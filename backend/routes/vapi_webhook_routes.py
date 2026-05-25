from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
import json
import traceback

from controllers.vapi_webhook_controller import handle_webhook_controller
from database import get_db

router = APIRouter(prefix="/vapi-webhook", tags=["vapi-webhook"])


@router.post("")
async def vapi_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.body()
        print(f"[WEBHOOK RECEIVED] Content-Length: {len(body)}", flush=True)
        print(f"[WEBHOOK HEADERS] {dict(request.headers)}", flush=True)
        
        try:
            payload = json.loads(body)
            event_type = payload.get("message", {}).get("type") or payload.get("type", "UNKNOWN")
            print(f"[WEBHOOK] Event Type: {event_type}", flush=True)
            print(f"[WEBHOOK] Full Payload: {json.dumps(payload, indent=2)[:500]}", flush=True)
        except Exception as parse_err:
            print(f"[WEBHOOK] Could not parse JSON: {parse_err}", flush=True)
        
        result = await handle_webhook_controller(request, body, db)
        print(f"[WEBHOOK RESPONSE] {result}", flush=True)
        return result
    except Exception as e:
        print(f"[WEBHOOK ERROR] {type(e).__name__}: {e}", flush=True)
        print(f"[WEBHOOK TRACEBACK]\n{traceback.format_exc()}", flush=True)
        return {"status": "error", "message": str(e)}
