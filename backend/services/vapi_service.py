"""
Vapi assistant management service.
Creates / updates the Vapi assistant via REST API.
"""
import httpx
from datetime import date
from typing import Optional
from config import settings
from services.openai_tools import TOOL_DEFINITIONS

VAPI_BASE = "https://api.vapi.ai"
REQUEST_TIMEOUT = 60.0


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.VAPI_API_KEY}",
        "Content-Type": "application/json",
    }


def _voice_config(voice: str) -> dict:
    v = (voice or "nova").strip().lower()
    return {"provider": "openai", "voiceId": v}


def _build_assistant_payload(name: str, prompt: str, voice: str) -> dict:
    today = date.today().strftime("%A, %B %d, %Y")
    full_prompt = f"Today's date is {today}.\n\n{prompt}"
    return {
        "name": name,
        "model": {
            "provider": "openai",
            "model": settings.OPENAI_MODEL,
            "systemPrompt": full_prompt,
            "tools": TOOL_DEFINITIONS,
            "temperature": 0.7,
        },
        "voice": _voice_config(voice),
        "firstMessage": "Hello! Thank you for calling Sky AI Technologies. I'm your AI receptionist. How can I help you today?",
        "endCallMessage": "Thank you for calling Sky AI Technologies. Have a great day!",
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en-US",
        },
        "serverUrl": f"{settings.BACKEND_URL}/vapi-webhook",
        # "serverUrlSecret": settings.VAPI_WEBHOOK_SECRET,
        "silenceTimeoutSeconds": 30,
        "maxDurationSeconds": 600,
        "backgroundDenoisingEnabled": True,
    }


def _vapi_http_error(resp: httpx.Response) -> str:
    text = (resp.text or "").strip()
    if len(text) > 800:
        text = text[:800] + "…"
    return f"Vapi HTTP {resp.status_code}: {text or resp.reason_phrase}"


async def create_vapi_assistant(name: str, prompt: str, voice: str) -> Optional[str]:
    if not settings.VAPI_API_KEY:
        return None
    payload = _build_assistant_payload(name, prompt, voice)
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        resp = await client.post(f"{VAPI_BASE}/assistant", json=payload, headers=_headers())
    if resp.status_code not in (200, 201):
        raise RuntimeError(_vapi_http_error(resp))
    data = resp.json()
    aid = data.get("id")
    if not aid:
        raise RuntimeError(f"Vapi response missing id: {data!r}")
    return str(aid)


async def update_vapi_assistant(
    assistant_id: str, name: str, prompt: str, voice: str
) -> None:
    if not settings.VAPI_API_KEY or not assistant_id:
        raise RuntimeError("Missing VAPI_API_KEY or vapi_assistant_id")
    payload = _build_assistant_payload(name, prompt, voice)
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        resp = await client.patch(
            f"{VAPI_BASE}/assistant/{assistant_id}", json=payload, headers=_headers()
        )
    if resp.status_code != 200:
        raise RuntimeError(_vapi_http_error(resp))
