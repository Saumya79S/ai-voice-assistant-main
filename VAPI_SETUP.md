# VAPI Setup & Configuration Log

## Architecture

```
Caller (Phone/Browser)
      ↓ voice
   VAPI (handles call + STT via Deepgram)
      ↓ text
   OpenAI GPT-4.1 (LLM — called directly by VAPI)
      ↓ tool call needed
   Your Backend /vapi-webhook (executes tools, saves to DB)
      ↓ result
   OpenAI GPT-4.1 (feeds result back)
      ↓ text
   VAPI TTS (speaks response to caller)
```

---

## VAPI Credentials

| Key | Value |
|-----|-------|
| VAPI_API_KEY | `38b125d8-e2e2-4e7c-8e08-b94e0ba07ec4` |
| VAPI_PHONE_NUMBER_ID | `0724c1ec-57e2-4157-a4a3-0ba6fd933954` |
| Phone Number | `+1 (507) 999 8532` |

---

## Assistants

| Name | ID | Notes |
|------|----|-------|
| Alex | `4c80407c-7edb-4658-b8c6-c21eed988ec8` | Main assistant, assigned to phone number |
| Riley | `b335ab38-7174-4839-93b4-c75927b9d1a0` | Secondary assistant |

### Alex Configuration
- **Model**: GPT-4.1 (called by VAPI directly)
- **Voice**: Elliot (Vapi provider)
- **First Message**: "Hi there, this is Alex from Skyai customer support. How can I help you today?"
- **Server URL**: set to ngrok webhook URL (see below)

---

## Webhook URL Setup

### How the serverUrl was set
The `serverUrl` on the Alex assistant was set via VAPI REST API:

```bash
curl -X PATCH https://api.vapi.ai/assistant/4c80407c-7edb-4658-b8c6-c21eed988ec8 \
  -H "Authorization: Bearer 38b125d8-e2e2-4e7c-8e08-b94e0ba07ec4" \
  -H "Content-Type: application/json" \
  -d '{"serverUrl": "https://<your-ngrok-url>/vapi-webhook"}'
```

### Current ngrok URL (changes every restart)
```
https://janessa-stomatous-ingratiatingly.ngrok-free.dev/vapi-webhook
```

> **Important:** ngrok free plan generates a new URL every time you restart.
> After restarting ngrok, update the assistant serverUrl using the PATCH command above.

### ngrok must forward to port 8000
```bash
ngrok http 8000
```
Previous mistake: ngrok was forwarding to port 5000 (macOS AirPlay) causing 403 errors.

---

## Webhook Endpoint

**Route:** `POST /vapi-webhook`
**File:** `backend/routes/vapi_webhook_routes.py`
**Controller:** `backend/controllers/vapi_webhook_controller.py`

### Event Types Handled

| VAPI Event | Handler |
|------------|---------|
| `call.started` / `call-start` | Creates CallLog in DB |
| `end-of-call-report` / `call.ended` | Updates CallLog with duration + transcript |
| `tool-calls` / `tool.called` | Executes tool and returns result |

### Tools Available to Alex

| Tool | Description |
|------|-------------|
| `get_available_slots` | Returns available appointment slots for a given date |
| `book_appointment` | Books an appointment and saves to DB |
| `transfer_to_human` | Transfers call and logs outcome |

---

## Database Tables (created via migration `a1b2c3d4e5f6`)

- `users` — registered users
- `verification_code` — email verification tokens
- `availability_rules` — working hours per day of week
- `appointments` — booked appointments
- `call_logs` — VAPI call history with transcripts
- `agents` — VAPI assistant config (name, prompt, voice, vapi_assistant_id)

---

## Testing

### Trigger outbound call (VAPI calls your phone)
> Note: Free VAPI plan does NOT support international calls (India numbers blocked)

```bash
curl -X POST https://api.vapi.ai/call/phone \
  -H "Authorization: Bearer 38b125d8-e2e2-4e7c-8e08-b94e0ba07ec4" \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumberId": "0724c1ec-57e2-4157-a4a3-0ba6fd933954",
    "customer": { "number": "+91XXXXXXXXXX" },
    "assistantId": "4c80407c-7edb-4658-b8c6-c21eed988ec8"
  }'
```

### Test via browser (free, works immediately)
1. Go to https://dashboard.vapi.ai
2. Assistants → Alex → click the call button (top right)
3. Talk to Alex from browser

### Test webhook locally
```bash
# call.started
curl -X POST http://localhost:8000/vapi-webhook \
  -H "Content-Type: application/json" \
  -d '{"message": {"type": "call.started", "call": {"id": "test-123", "customer": {"number": "+919876543210"}}}}'

# get_available_slots
curl -X POST http://localhost:8000/vapi-webhook \
  -H "Content-Type: application/json" \
  -d '{"message": {"type": "tool-calls", "call": {"id": "test-123"}, "toolCallList": [{"id": "tc1", "function": {"name": "get_available_slots", "arguments": {"date": "2026-04-01"}}}]}}'

# book_appointment
curl -X POST http://localhost:8000/vapi-webhook \
  -H "Content-Type: application/json" \
  -d '{"message": {"type": "tool-calls", "call": {"id": "test-123"}, "toolCallList": [{"id": "tc2", "function": {"name": "book_appointment", "arguments": {"name": "Raj Singh", "phone": "+919876543210", "date": "2026-04-01", "time": "10:00"}}}]}}'
```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| 403 on ngrok URL | ngrok forwarding to wrong port (5000 = AirPlay) | Run `ngrok http 8000` |
| No webhook logs on call end | `serverUrl` was `null` on assistant | PATCH assistant with serverUrl |
| `availability_rules` table missing | Migration only created users table | Created migration `a1b2c3d4e5f6` |
| Free plan international call blocked | VAPI free plan restriction | Use browser call from dashboard instead |

---

## Update serverUrl After ngrok Restart

Every time ngrok restarts, run this with the new URL:

```bash
NEW_URL="https://<new-ngrok-subdomain>.ngrok-free.app"

curl -X PATCH https://api.vapi.ai/assistant/4c80407c-7edb-4658-b8c6-c21eed988ec8 \
  -H "Authorization: Bearer 38b125d8-e2e2-4e7c-8e08-b94e0ba07ec4" \
  -H "Content-Type: application/json" \
  -d "{\"serverUrl\": \"${NEW_URL}/vapi-webhook\"}"
```
