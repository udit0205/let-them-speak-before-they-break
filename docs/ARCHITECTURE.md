# Architecture

```text
Browser (React + Vite)
        |
        | REST/JSON + X-User-ID
        v
FastAPI API
  |      |        |
  |      |        +--> Safety detector (deterministic)
  |      |
  |      +----------> Conversation memory (last 20 messages)
  |
  +-----------------> SQLModel / SQLite
  |
  +-----------------> AI provider
                       |-- Ollama (local default)
                       |-- OpenAI-compatible endpoint (optional)
                       +-- Safe scripted fallback
```

## Request lifecycle

1. A browser gets a stable anonymous UUID stored in localStorage.
2. Selecting Red / Blue / Yellow / Green creates a conversation row and an opening assistant message.
3. A user message is stored immediately in the database.
4. The safety layer checks the new message for coarse high-risk signals.
5. Immediate danger bypasses the LLM and returns an emergency-support response.
6. Otherwise, the last 20 messages plus the mode-specific system prompt go to the AI provider.
7. The assistant response is stored and returned with safety/provider metadata.

## Data model

- `User`: anonymous device identity.
- `Conversation`: selected emotional mode, title, timestamps.
- `Message`: role, content, safety flag, timestamp.

For a real public deployment, replace the anonymous header-based identity with authenticated sessions and authorization, use PostgreSQL + migrations, and establish a formal retention/deletion policy.
