# RAP Mock Interviewer

Voice-first solo mock interview for the RAP ML Engineer Intern loop:

1. **PyTorch debug** (~10 min) — copy snippet → Colab → talk + paste fixes
2. **System design** (10–15 min) — Excalidraw board → AI critiques
3. **LLM techniques** (~25 min) — crisp definitions, interrupt waffle

Modes: soft / medium / strict / hardcore.

## Setup

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# edit .env — paste GEMINI_API_KEYS=key1,key2,...
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Voice

- **Primary:** Gemini Live (mic ↔ spoken interviewer, barge-in). Needs `GEMINI_API_KEYS`.
- **Fallback:** uncheck Live on lobby, or automatic if Live fails — text turns + Edge-TTS.

## Keys

Put numbered keys in `backend/.env` (never commit):

```
GEMINI_API_KEY_1=...
GEMINI_API_KEY_2=...
GROQ_API_KEY_1=...   # optional text fallback (console.groq.com)
```

LiteLLM load-balances text/vision across Gemini + Groq; Live rotates Gemini keys per connection.
