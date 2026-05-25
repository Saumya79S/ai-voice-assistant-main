"""
Vapi Webhook Controller
Handles Vapi webhook events: call.started, end-of-call-report, tool-calls
"""
import hmac
import hashlib
import json
import secrets
from datetime import date, datetime, time as dtime, timezone

from fastapi import Request
from sqlalchemy.orm import Session

from config import settings
from models.agent import Agent
from models.call_log import CallLog
from services.booking_service import book_appointment
from services.slot_service import generate_slots


def _parse_agent_date(value: str) -> date:
    s = value.strip().replace("/", "-")
    try:
        return date.fromisoformat(s)
    except ValueError:
        parts = s.split("-")
        if len(parts) == 3:
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            return date(y, m, d)
        raise


def _normalize_year(d: date) -> date:
    """If the agent passes a past year, advance to the nearest future occurrence."""
    today = date.today()
    if d < today:
        d = d.replace(year=today.year)
    if d < today:
        d = d.replace(year=today.year + 1)
    return d


def _parse_agent_time(value: str) -> dtime:
    s = value.strip().replace(".", ":")
    try:
        return dtime.fromisoformat(s)
    except ValueError:
        parts = [p for p in s.split(":") if p != ""]
        if not parts:
            raise ValueError("empty time") from None
        h = int(parts[0])
        mi = int(parts[1]) if len(parts) > 1 else 0
        sec = int(parts[2]) if len(parts) > 2 else 0
        return dtime(h, mi, sec)


def _webhook_secret_configured() -> bool:
    return bool(settings.VAPI_WEBHOOK_SECRET and settings.VAPI_WEBHOOK_SECRET.strip())


def verify_vapi_webhook(request: Request, body: bytes) -> bool:
    if not _webhook_secret_configured():
        return True
    expected = settings.VAPI_WEBHOOK_SECRET.strip()
    x_secret = request.headers.get("x-vapi-secret")
    if x_secret is not None and x_secret != "":
        return secrets.compare_digest(x_secret, expected)
    auth = request.headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
        if token:
            return secrets.compare_digest(token, expected)
    sig = (request.headers.get("x-vapi-signature") or "").strip()
    if sig:
        digest = hmac.new(expected.encode("utf-8"), body, hashlib.sha256).hexdigest()
        if sig.startswith("sha256="):
            sig = sig[7:]
        return hmac.compare_digest(sig, digest)
    return False


def _extract_call(payload: dict) -> dict:
    return payload.get("message", {}).get("call") or payload.get("call") or {}


def _resolve_assistant_name(call: dict, db: Session) -> str:
    name = (call.get("assistant") or {}).get("name")
    if name:
        return name
    assistant_id = call.get("assistantId")
    if assistant_id:
        agent = db.query(Agent).filter(Agent.vapi_assistant_id == assistant_id).first()
        if agent:
            return agent.name
    return "Alex"


def _resolve_assistant_phone(call: dict) -> str:
    number = (call.get("phoneNumber") or {}).get("number")
    if number:
        return number
    # VAPI_PHONE_NUMBER_ID maps to the provisioned number in settings
    if call.get("phoneNumberId") == settings.VAPI_PHONE_NUMBER_ID:
        return settings.VAPI_ASSISTANT_PHONE_NUMBER
    return None


def _make_call_log(call: dict, db: Session) -> CallLog:
    return CallLog(
        vapi_call_id=call.get("id", ""),
        assistant_name=_resolve_assistant_name(call, db),
        assistant_phone_number=_resolve_assistant_phone(call),
        customer_phone_number=(call.get("customer") or {}).get("number"),
        call_type=call.get("type"),
        start_time=datetime.now(timezone.utc),
    )


async def handle_call_started(payload: dict, db: Session) -> dict:
    call = _extract_call(payload)
    call_id = call.get("id", "")
    if not call_id:
        return {"status": "ok"}

    if db.query(CallLog).filter(CallLog.vapi_call_id == call_id).first():
        return {"status": "ok"}

    log = _make_call_log(call, db)
    db.add(log)
    db.commit()
    print(f"[CALL STARTED] id={call_id} phone={log.customer_phone_number}", flush=True)
    return {"status": "ok"}


async def handle_call_ended(payload: dict, db: Session) -> dict:
    call = _extract_call(payload)
    call_id = call.get("id", "")
    message = payload.get("message", payload)
    transcript = message.get("transcript", "") or (call.get("artifact") or {}).get("transcript", "")
    ended_reason = call.get("endedReason", "")
    analysis = call.get("analysis") or {}

    log = db.query(CallLog).filter(CallLog.vapi_call_id == call_id).first()
    if not log:
        log = _make_call_log(call, db)
        db.add(log)

    if log.start_time:
        start = log.start_time.replace(tzinfo=timezone.utc) if log.start_time.tzinfo is None else log.start_time
        log.duration_seconds = (datetime.now(timezone.utc) - start).total_seconds()

    log.ended_reason = ended_reason
    log.success_evaluation = analysis.get("successEvaluation")
    log.score = analysis.get("score")
    log.transcript = transcript[:10000] if transcript else None
    db.commit()
    print(f"[CALL ENDED] id={call_id} reason={ended_reason} duration={log.duration_seconds}s", flush=True)
    if transcript:
        print(f"[TRANSCRIPT]\n{transcript}", flush=True)
    return {"status": "ok"}


async def handle_tool_calls(payload: dict, db: Session) -> dict:
    message = payload.get("message", payload)
    tool_calls = message.get("toolCallList", message.get("toolCalls", []))
    results = []
    
    print(f"[TOOL CALLS] Received {len(tool_calls)} tool calls", flush=True)

    for tc in tool_calls:
        fn_name = tc.get("function", {}).get("name") or tc.get("name", "")
        args = tc.get("function", {}).get("arguments", tc.get("arguments", {}))
        tool_call_id = tc.get("id", "")
        
        print(f"[TOOL CALL] function={fn_name}, toolCallId={tool_call_id}, args={args}", flush=True)

        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception as e:
                print(f"[TOOL CALL ERROR] Failed to parse args: {e}", flush=True)
                args = {}

        result = await _execute_tool(fn_name, args, db)
        print(f"[TOOL RESULT] {fn_name} returned: {result[:200]}", flush=True)
        results.append({"toolCallId": tool_call_id, "result": result})

    return {"results": results}


async def _execute_tool(fn_name: str, args: dict, db: Session) -> str:
    try:
        if fn_name == "get_available_slots":
            try:
                target_date = _parse_agent_date(args["date"])
                target_date = _normalize_year(target_date)
                slots = generate_slots(db, target_date)
                if not slots:
                    return f"No availability found for {args['date']}. This day is not a working day."
                available = [s for s in slots if s.available]
                if not available:
                    return f"All slots on {args['date']} are booked. Please suggest another date."
                slot_list = ", ".join(f"{s.start_time}–{s.end_time}" for s in available[:10])
                return f"Available slots on {args['date']}: {slot_list}"
            except Exception as e:
                print(f"[TOOL ERROR] get_available_slots failed: {e}", flush=True)
                return f"Error getting slots for {args.get('date', 'unknown date')}: {str(e)}"

        elif fn_name == "book_appointment":
            try:
                appt_date = _normalize_year(_parse_agent_date(args["date"]))
                start_time = _parse_agent_time(args["time"])
                appt = book_appointment(
                    db,
                    name=args["name"],
                    phone=args["phone"],
                    appt_date=appt_date,
                    start_time=start_time,
                    notes=args.get("notes"),
                )
                return (
                    f"BOOKING_SUCCESS: Tell the caller exactly this: "
                    f"'Perfect! Your appointment is confirmed. {appt.name}, you're booked for "
                    f"{appt.date.strftime('%A, %B %d')} from {appt.start_time.strftime('%I:%M %p')} to "
                    f"{appt.end_time.strftime('%I:%M %p')}. Your confirmation number is {appt.id}. "
                    f"We look forward to seeing you at Sky AI Technologies!'"
                )
            except Exception as e:
                print(f"[TOOL ERROR] book_appointment failed: {e}", flush=True)
                return f"Error booking appointment: {str(e)}"

        elif fn_name == "transfer_to_human":
            reason = args.get("reason", "User requested human agent")
            return f"Transferring you to a human agent now. Reason: {reason}"

        else:
            return f"Unknown function: {fn_name}"

    except Exception as e:
        print(f"[TOOL EXCEPTION] {fn_name}: {type(e).__name__}: {e}", flush=True)
        return f"Error executing {fn_name}: {str(e)}"


async def handle_webhook_controller(request: Request, body: bytes, db: Session) -> dict:
    try:
        payload = json.loads(body)
        event_type = payload.get("message", {}).get("type") or payload.get("type", "")
        message = payload.get("message", payload)

        print(f"[VAPI WEBHOOK] event_type={event_type!r}", flush=True)

        if event_type in ("call.started", "call-start"):
            return await handle_call_started(payload, db)

        if event_type == "status-update":
            if message.get("status") == "in-progress":
                return await handle_call_started(payload, db)
            return {"status": "ok"}

        if event_type in ("call.ended", "end-of-call-report"):
            return await handle_call_ended(payload, db)

        if event_type in ("tool-calls", "tool.called"):
            return await handle_tool_calls(payload, db)

        return {"status": "ok", "type": event_type}
    except Exception as e:
        print(f"[WEBHOOK HANDLER ERROR] {type(e).__name__}: {e}", flush=True)
        import traceback
        print(f"[WEBHOOK HANDLER TRACEBACK]\n{traceback.format_exc()}", flush=True)
        return {"status": "error", "message": str(e)}
