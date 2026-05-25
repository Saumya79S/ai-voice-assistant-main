# AI Voice Receptionist — MVP

A production-ready AI voice calling agent that answers inbound calls, books appointments, and provides a management dashboard.

## Architecture

```
Caller → Vapi (voice) → OpenAI GPT-4o (AI) → FastAPI (logic) → PostgreSQL (data)
Dashboard → React/Vite → FastAPI → PostgreSQL
```

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + SQLAlchemy |
| Database | PostgreSQL |
| Frontend | React + Vite + Tailwind |
| AI | OpenAI GPT-4o (tool calling) |
| Voice | Vapi |
| Deployment | Docker + docker-compose |

## Quick Start

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required keys:
- `OPENAI_API_KEY` — from platform.openai.com
- `VAPI_API_KEY` — from dashboard.vapi.ai
- `SECRET_KEY` — random 32-char string for JWT
- `BACKEND_URL` — public URL (use ngrok for local dev)

### 2. Start with Docker

```bash
docker-compose up -d
```

Services:
- Backend: http://localhost:8000
- Frontend: http://localhost:80
- API Docs: http://localhost:8000/docs

### 3. Local development (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 4. Dashboard Setup

1. Open http://localhost:5173
2. Register an account at `/login`
3. Go to **Agent Settings** → configure prompt and voice → Save
4. Go to **Availability** → set working days and hours
5. Your Vapi webhook is at: `{BACKEND_URL}/vapi-webhook`

### 5. Vapi Configuration

1. Log into dashboard.vapi.ai
2. Create an assistant (the backend does this automatically on first agent save)
3. Or manually configure using `vapi_setup_example.json`
4. Set webhook URL to: `https://your-domain.com/vapi-webhook`
5. Assign a phone number to the assistant

### 6. Local webhook tunnel (development)

```bash
ngrok http 8000
# Copy the https URL → set as BACKEND_URL in .env
```

## API Reference

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/user/register` | Create account | No |
| POST | `/user/login` | Get JWT token | No |
| GET/POST | `/availability` | Manage working hours | Yes |
| GET | `/availability/slots?target_date=YYYY-MM-DD` | Get slots | No |
| GET/POST | `/appointments` | Manage bookings | Mixed |
| GET/PATCH/DELETE | `/appointments/{id}` | Single appointment | Yes |
| GET/POST | `/agents` | AI agent config | Yes |
| GET | `/call-logs` | Call history | Yes |
| POST | `/vapi-webhook` | Vapi events (no auth) | No |

## AI Tool Calling Flow

```
1. Caller asks about availability
2. AI calls get_available_slots(date) → backend returns real slots
3. AI presents options to caller
4. Caller picks a slot, provides name/phone
5. AI confirms with caller verbally
6. AI calls book_appointment(name, phone, date, time)
7. Backend creates booking, prevents double-booking
8. AI reads back confirmation ID
```

## Database Schema

- **users** — dashboard login accounts
- **agents** — AI assistant configuration (prompt, voice)
- **availability_rules** — per-day working hours + slot duration
- **appointments** — confirmed bookings
- **call_logs** — per-call records with outcome + transcript

## Project Structure

```
voice_bot_basic/
├── backend/
│   ├── main.py                  # FastAPI app + startup
│   ├── config.py                # Settings (env vars)
│   ├── database.py              # SQLAlchemy engine
│   ├── system_prompt.py         # Default AI prompt
│   ├── models/                  # DB models
│   ├── schemas/                 # Pydantic schemas
│   ├── routers/                 # API routes
│   ├── services/                # Business logic
│   ├── auth/                    # JWT auth
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api/client.js        # Axios + JWT interceptor
│   │   ├── components/          # Dashboard pages
│   │   └── pages/               # Login + Dashboard
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── vapi_setup_example.json
```
