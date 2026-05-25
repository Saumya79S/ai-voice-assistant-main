"""
Tests for POST /vapi-webhook

Covers:
  - call.started  → creates a CallLog
  - call.ended    → updates the CallLog (duration, transcript, outcome)
  - tool-calls    → get_available_slots / book_appointment / transfer_to_human / unknown
  - unhandled event type
  - 403 when VAPI_WEBHOOK_SECRET is set and request has no / wrong auth header
"""
import json
from datetime import date, time, datetime, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ── in-memory SQLite DB (no Postgres needed) ──────────────────────────────────
# StaticPool ensures all sessions share the same in-memory database.
from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite://"  # in-memory

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    # Disable webhook secret so non-auth tests don't get 403
    with patch("controllers.vapi_webhook_controller.settings") as mock_settings:
        mock_settings.VAPI_WEBHOOK_SECRET = ""
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c
    app.dependency_overrides.clear()


# ── helpers ───────────────────────────────────────────────────────────────────

def post_webhook(client, payload: dict, headers: dict | None = None):
    return client.post(
        "/vapi-webhook",
        content=json.dumps(payload),
        headers={"Content-Type": "application/json", **(headers or {})},
    )


# ── call.started ──────────────────────────────────────────────────────────────

def test_call_started_returns_ok(client):
    payload = {
        "message": {
            "type": "call.started",
            "call": {"id": "call-abc", "customer": {"number": "+15550001111"}},
        }
    }
    resp = post_webhook(client, payload)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_call_started_creates_call_log(client, db):
    from models.call_log import CallLog

    payload = {
        "message": {
            "type": "call.started",
            "call": {"id": "call-xyz", "customer": {"number": "+15559998888"}},
        }
    }
    post_webhook(client, payload)

    log = db.query(CallLog).filter(CallLog.vapi_call_id == "call-xyz").first()
    assert log is not None
    assert log.phone == "+15559998888"
    assert log.outcome.value == "abandoned"


def test_call_start_alias(client):
    """'call-start' is an accepted alias for call.started."""
    payload = {"message": {"type": "call-start", "call": {"id": "c1", "customer": {"number": "+1"}}}}
    resp = post_webhook(client, payload)
    assert resp.status_code == 200


# ── call.ended ────────────────────────────────────────────────────────────────

def test_call_ended_updates_log(client, db):
    from models.call_log import CallLog, CallOutcome

    # Seed an existing CallLog
    log = CallLog(
        phone="+15550001111",
        vapi_call_id="call-end-test",
        start_time=datetime(2026, 3, 29, 10, 0, 0),  # naive — SQLite strips tzinfo
        outcome=CallOutcome.abandoned,
    )
    db.add(log)
    db.commit()

    payload = {
        "message": {
            "type": "call.ended",
            "call": {"id": "call-end-test"},
            "transcript": "Hello, I'd like to book an appointment.",
        }
    }
    resp = post_webhook(client, payload)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

    db.refresh(log)
    assert log.end_time is not None
    assert log.duration_seconds is not None
    assert "appointment" in log.transcript


def test_end_of_call_report_alias(client):
    payload = {"message": {"type": "end-of-call-report", "call": {"id": "no-log"}, "transcript": ""}}
    resp = post_webhook(client, payload)
    assert resp.status_code == 200


# ── tool-calls: get_available_slots ───────────────────────────────────────────

def test_get_available_slots_no_availability(client):
    payload = {
        "message": {
            "type": "tool-calls",
            "toolCallList": [
                {
                    "id": "tc-1",
                    "function": {
                        "name": "get_available_slots",
                        "arguments": {"date": "2026-03-30"},
                    },
                }
            ],
        }
    }
    resp = post_webhook(client, payload)
    assert resp.status_code == 200
    result = resp.json()["results"][0]["result"]
    assert "No availability" in result or "not a working day" in result


def test_get_available_slots_with_rules(client, db):
    from models.availability import AvailabilityRule

    # 2026-03-30 is a Monday (weekday 0)
    db.add(AvailabilityRule(day_of_week=0, start_time=time(9, 0), end_time=time(11, 0), slot_duration=30, is_active=True))
    db.commit()

    payload = {
        "message": {
            "type": "tool-calls",
            "toolCallList": [
                {"id": "tc-2", "function": {"name": "get_available_slots", "arguments": {"date": "2026-03-30"}}}
            ],
        }
    }
    resp = post_webhook(client, payload)
    assert resp.status_code == 200
    result = resp.json()["results"][0]["result"]
    assert "Available slots" in result


# ── tool-calls: book_appointment ─────────────────────────────────────────────

def test_book_appointment_success(client, db):
    from models.availability import AvailabilityRule

    # 2026-03-30 is Monday
    db.add(AvailabilityRule(day_of_week=0, start_time=time(9, 0), end_time=time(11, 0), slot_duration=30, is_active=True))
    db.commit()

    payload = {
        "message": {
            "type": "tool-calls",
            "toolCallList": [
                {
                    "id": "tc-3",
                    "function": {
                        "name": "book_appointment",
                        "arguments": {
                            "name": "Alice Smith",
                            "phone": "+15550001111",
                            "date": "2026-03-30",
                            "time": "09:00",
                        },
                    },
                }
            ],
        }
    }
    resp = post_webhook(client, payload)
    assert resp.status_code == 200
    result = resp.json()["results"][0]["result"]
    assert "confirmed" in result.lower()
    assert "Alice Smith" in result


def test_book_appointment_updates_call_log_outcome(client, db):
    from models.availability import AvailabilityRule
    from models.call_log import CallLog, CallOutcome

    db.add(AvailabilityRule(day_of_week=0, start_time=time(9, 0), end_time=time(11, 0), slot_duration=30, is_active=True))
    log = CallLog(phone="+1", vapi_call_id="call-book", start_time=datetime.utcnow(), outcome=CallOutcome.abandoned)
    db.add(log)
    db.commit()

    payload = {
        "message": {
            "type": "tool-calls",
            "call": {"id": "call-book"},
            "toolCallList": [
                {
                    "id": "tc-4",
                    "function": {
                        "name": "book_appointment",
                        "arguments": {"name": "Bob", "phone": "+1", "date": "2026-03-30", "time": "09:00"},
                    },
                }
            ],
        }
    }
    post_webhook(client, payload)
    db.refresh(log)
    assert log.outcome == CallOutcome.booked


# ── tool-calls: transfer_to_human ────────────────────────────────────────────

def test_transfer_to_human(client, db):
    from models.call_log import CallLog, CallOutcome

    log = CallLog(phone="+1", vapi_call_id="call-transfer", start_time=datetime.utcnow(), outcome=CallOutcome.abandoned)
    db.add(log)
    db.commit()

    payload = {
        "message": {
            "type": "tool-calls",
            "call": {"id": "call-transfer"},
            "toolCallList": [
                {
                    "id": "tc-5",
                    "function": {"name": "transfer_to_human", "arguments": {"reason": "Complex query"}},
                }
            ],
        }
    }
    resp = post_webhook(client, payload)
    assert resp.status_code == 200
    result = resp.json()["results"][0]["result"]
    assert "human agent" in result.lower()

    db.refresh(log)
    assert log.outcome == CallOutcome.transferred


def test_unknown_tool_name(client):
    payload = {
        "message": {
            "type": "tool-calls",
            "toolCallList": [{"id": "tc-6", "function": {"name": "fly_to_moon", "arguments": {}}}],
        }
    }
    resp = post_webhook(client, payload)
    assert resp.status_code == 200
    result = resp.json()["results"][0]["result"]
    assert "Unknown function" in result


# ── unhandled event ───────────────────────────────────────────────────────────

def test_unhandled_event_type(client):
    payload = {"message": {"type": "some.other.event"}}
    resp = post_webhook(client, payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "unhandled"
    assert resp.json()["type"] == "some.other.event"


# ── authentication ────────────────────────────────────────────────────────────

def test_valid_x_vapi_secret_passes(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with patch("controllers.vapi_webhook_controller.settings") as mock_settings:
        mock_settings.VAPI_WEBHOOK_SECRET = "mysecret"
        payload = {"message": {"type": "some.event"}}
        with TestClient(app, raise_server_exceptions=True) as c:
            resp = post_webhook(c, payload, headers={"x-vapi-secret": "mysecret"})
    app.dependency_overrides.clear()
    assert resp.status_code == 200


def test_wrong_x_vapi_secret_returns_403(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with patch("controllers.vapi_webhook_controller.settings") as mock_settings:
        mock_settings.VAPI_WEBHOOK_SECRET = "mysecret"
        payload = {"message": {"type": "some.event"}}
        with TestClient(app, raise_server_exceptions=True) as c:
            resp = post_webhook(c, payload, headers={"x-vapi-secret": "wrongsecret"})
    app.dependency_overrides.clear()
    assert resp.status_code == 403


def test_no_auth_header_with_secret_returns_403(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with patch("controllers.vapi_webhook_controller.settings") as mock_settings:
        mock_settings.VAPI_WEBHOOK_SECRET = "mysecret"
        payload = {"message": {"type": "some.event"}}
        with TestClient(app, raise_server_exceptions=True) as c:
            resp = post_webhook(c, payload)
    app.dependency_overrides.clear()
    assert resp.status_code == 403
