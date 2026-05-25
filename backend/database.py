from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from config import settings

engine = create_engine(settings.resolved_database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def _safe_database_target() -> str:
    try:
        url = make_url(settings.resolved_database_url)
        host = url.host or "localhost"
        port = f":{url.port}" if url.port else ""
        db_name = url.database or "<unknown-db>"
        return f"{url.drivername}://{host}{port}/{db_name}"
    except Exception:
        return "configured DATABASE_URL"


def assert_database_connection() -> None:
    """Fail fast with a clear message if Postgres is unreachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        target = _safe_database_target()
        raise RuntimeError(
            "Database connection failed during startup. "
            f"Target: {target}. "
            "Ensure PostgreSQL is running and DB settings are correct."
        ) from exc


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()