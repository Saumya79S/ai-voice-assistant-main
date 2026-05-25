import logging
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.exceptions import ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import settings
from database import assert_database_connection, SessionLocal
from models.agent import Agent
from routes.api_router import router as api_router

logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).resolve().parent


async def _sync_webhook_to_vapi():
    # In dev: try ngrok first. In prod: fall back to BACKEND_URL from .env
    webhook_url = None

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get("http://127.0.0.1:4040/api/tunnels")
            tunnels = resp.json().get("tunnels", [])
            ngrok_url = next((t["public_url"] for t in tunnels if t["public_url"].startswith("https")), None)
            if ngrok_url:
                webhook_url = f"{ngrok_url}/vapi-webhook"
                print(f"ngrok tunnel detected: {webhook_url}")
    except Exception:
        pass  # ngrok not running — use BACKEND_URL instead

    if not webhook_url:
        backend_url = (settings.BACKEND_URL or "").strip().rstrip("/")
        if backend_url and "localhost" not in backend_url and "127.0.0.1" not in backend_url:
            webhook_url = f"{backend_url}/vapi-webhook"
            print(f"Production URL: {webhook_url}")

    if not webhook_url:
        print("No public webhook URL found. Set BACKEND_URL in .env for production.")
        return

    db = SessionLocal()
    try:
        agents = db.query(Agent).filter(
            Agent.vapi_assistant_id.isnot(None), Agent.is_active
        ).all()
    finally:
        db.close()

    async with httpx.AsyncClient(timeout=10) as client:
        for agent in agents:
            r = await client.patch(
                f"https://api.vapi.ai/assistant/{agent.vapi_assistant_id}",
                headers={"Authorization": f"Bearer {settings.VAPI_API_KEY}", "Content-Type": "application/json"},
                json={"serverUrl": webhook_url},
            )
            if r.status_code == 200:
                print(f"VAPI assistant '{agent.name}' serverUrl → {webhook_url}")
            else:
                print(f"VAPI sync failed for '{agent.name}': {r.status_code} {r.text[:100]}")


# ── Startup ────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(_: FastAPI):
    print("Checking database connection...")
    assert_database_connection()
    print("Database connection OK.")

    print("Running database migrations...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            str(_BASE_DIR / "alembic.ini"),
            "upgrade",
            "head",
        ],
        cwd=str(_BASE_DIR),
        check=True,
    )
    print("Migrations complete.")

    await _sync_webhook_to_vapi()

    yield


# ── Rate limiter ───────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Voice Receptionist API",
    version="1.0.0",
    description="Backend for AI-powered inbound call + appointment booking system",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(ResponseValidationError)
async def response_validation_error_handler(request: Request, exc: ResponseValidationError):
    logger.error("Response validation error on %s: %s", request.url, exc.errors())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error: response data is invalid."},
    )

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(api_router)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/")
def root():
    return {"message": "AI Voice Receptionist API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
    # uvicorn.run(app, host="127.0.0.1", port=8001)
