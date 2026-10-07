# LET THEM SPEAK BEFORE THEY BREAK

A full-stack, local-first emotional-support AI web app.

## Stack
- Frontend: React 19.3 + Vite 8.1
- Backend: FastAPI 0.142.2 + SQLModel
- Database: SQLite by default (easy local development; PostgreSQL can be used later)
- AI: Ollama by default, with an optional OpenAI-compatible provider and a safe scripted fallback
- Safety: deterministic high-risk signal layer + AI prompt guardrails + India emergency resources configurable via environment variables

## What is included
- Four color-coded emotional modes: Red, Blue, Yellow, Green
- Dedicated mode-specific conversation personality
- Animated CSS robotic AI companion
- Conversation context stored in DB and sent back to the AI model
- Conversation history panel
- REST APIs for health, modes, sessions, messages
- Anonymous device ID (no account required)
- High-risk safety detector that bypasses the LLM for immediate-danger messages
- Fallback mode so the UI remains usable when the AI provider is unavailable
- Responsive premium glassmorphism/futuristic UI

## 1. Prerequisites
- Windows + VS Code
- Python 3.12+ recommended
- Node.js 20.19+ (Vite 8 requirement) or Node.js 22.12+
- Ollama installed if you want local model responses

## 2. Backend
Open a terminal in `backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python run.py
```

The API will run at `http://127.0.0.1:8000`.
Swagger docs: `http://127.0.0.1:8000/docs`

### Ollama
Install/pull a model, then keep Ollama running. Example:

```powershell
ollama pull gemma3:4b
```

The default config expects:
- base URL: `http://127.0.0.1:11434`
- model: `gemma3:4b`

Change `OLLAMA_MODEL` in `.env` to any compatible chat model you have installed.

### No Ollama?
Set:

```env
AI_PROVIDER=fallback
```

The app still works with contextual scripted replies, but it is no longer a real LLM experience.

## 3. Frontend
Open another terminal in `frontend`:

```powershell
npm install
copy .env.example .env
npm run dev
```

Open the URL shown by Vite, normally `http://localhost:5173`.

## 4. API overview
- `GET /api/health` — service health/provider
- `GET /api/modes` — emotional modes
- `POST /api/sessions` — start a new conversation
- `GET /api/sessions/{user_id}` — list conversation history
- `GET /api/sessions/{conversation_id}/messages` — load messages
- `POST /api/sessions/{conversation_id}/messages` — send message + receive AI response + safety metadata

## 5. Deploy publicly (Render)

This repository includes a `render.yaml` Blueprint that creates:
- a React/Vite static frontend
- a FastAPI web service
- a PostgreSQL database

The deployed frontend receives the backend URL automatically at build time. The backend uses an OpenAI-compatible provider so the public deployment does not depend on Ollama running on your laptop. The included configuration uses OpenRouter's `openrouter/free` router for free-model inference; availability and limits can change.

### Render setup
1. Push this repository to GitHub.
2. In Render, choose **New → Blueprint** and connect the GitHub repository.
3. Render reads `render.yaml` and creates the frontend, API, and Postgres resources.
4. During the initial setup, Render asks for `OPENAI_COMPATIBLE_API_KEY`. Create an OpenRouter key and paste it there. Keep API keys in Render environment variables; never commit them.
5. After deployment, open the frontend service URL on your phone.

Render provides public `onrender.com` URLs for web services/static sites. Free web services can spin down after inactivity, and free Render Postgres databases currently expire after 30 days, so use the free tier for testing rather than a production promise.

## 6. Production hardening before public launch
This project is designed as a strong development/demo foundation, not as a regulated clinical product. Before public deployment, add:
- Authentication and session authorization
- HTTPS, secure cookies/JWT and CSRF protections where applicable
- PostgreSQL + migrations
- Rate limiting and abuse protection
- Server-side structured logging without storing unnecessary sensitive chat content
- Encryption and a documented retention/deletion policy
- A stronger safety evaluation/red-team process, human escalation, and region-specific crisis resource configuration
- Privacy/consent UX reviewed for the exact jurisdiction and audience
- Observability, backups, and model/provider monitoring

Do not market the AI as a therapist or as a crisis-response service.
