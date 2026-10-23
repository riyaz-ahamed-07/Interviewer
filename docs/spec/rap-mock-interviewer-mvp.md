# SPEC: RAP Mock Interviewer MVP (weekend)

Status: **approved** (2026-10-23) — voice: Gemini Live + fallback; stack: Vite/React + FastAPI; timers: ~10m debug / **10–15m design** / ~25m LLM  
Based on: `docs/intent/rap-mock-interviewer.md`  
Spike date: 2026-10-23

---

## Assumptions (correct me now)

1. Local web app on your Windows machine is fine (no cloud deploy this weekend).
2. You already have **4 Gemini** + **2 Grok** keys; free-tier Gemini Live audio is acceptable (Google may use free-tier data to improve products).
3. “ChatGPT-like voice” means **barge-in + natural spoken interviewer**, not identical timbre to ChatGPT.
4. System-design round: you draw; AI critiques from **PNG + text labels** of the diagram (not pixel-perfect layout scoring).
5. One user, one session at a time; no auth.

---

## Spike findings

### 1) Diagram — **Excalidraw (recommended)**

| Option                       | License                     | Embed?      | AI can read?                                                                      | Weekend fit                 |
| ---------------------------- | --------------------------- | ----------- | --------------------------------------------------------------------------------- | --------------------------- |
| **`@excalidraw/excalidraw`** | MIT                         | Yes (React) | `exportToBlob` → PNG; `getSceneElements` / `serializeAsJSON` → labels + structure | **Best**                    |
| tldraw                       | Custom / commercial caveats | Yes         | Similar export                                                                    | Skip — Excalidraw is enough |
| Build our own boxes/lines    | —                           | —           | —                                                                                 | Out of scope                |

**How AI “sees” the board (v1):**

1. On demand (button **“I’ve drawn — ask me”**) or on each spoken turn in the design round:
2. Client calls `exportToBlob({ mimeType: "image/png", ... })` + extracts text from labeled elements.
3. Backend (or Live session) sends **image + short text inventory** of boxes/arrows to the model with the interviewer system prompt.

Docs: [Excalidraw embed](https://docs.excalidraw.com), `excalidrawAPI`, `exportToBlob`.

### 2) Voice — options ranked for _your_ constraints

| Approach                                                       | Feels like ChatGPT voice?                            | Free / OSS                                | Weekend risk                   | Notes                             |
| -------------------------------------------------------------- | ---------------------------------------------------- | ----------------------------------------- | ------------------------------ | --------------------------------- |
| **A. Gemini Live API** (speech↔speech WebSocket)               | **Highest** — barge-in, affective audio, transcripts | Free tier on Gemini keys you already have | Medium (audio PCM plumbing)    | **Recommended primary**           |
| B. Mic → Whisper (local/API) → LiteLLM text → Edge-TTS / Piper | Medium                                               | Mostly free/OSS                           | Low–medium                     | Solid **fallback** if Live flakes |
| C. Full local S2S (HF speech-to-speech, Kokoro, Skadoosh)      | High if tuned                                        | True OSS                                  | **High** (GPU/deps on Windows) | Defer post-Monday                 |

**Recommendation:** **A primary, B fallback.**  
Pure OSS local voice is real, but installing/tuning it this weekend burns the practice time the tool is for. Gemini Live is the closest free path to ChatGPT Voice using keys you already have. LiteLLM still fronts **text + vision** (diagram, paste snippets, mode prompts) with multi-key load balance; Live is a separate WebSocket path (not the same as `completion()`).

Live API facts (official): PCM in 16 kHz / out 24 kHz, WSS, barge-in, tool use, audio transcriptions. Prefer **server proxy** or **ephemeral tokens** so keys stay off the browser long-term; for solo weekend MVP, server-side WebSocket proxy with key rotation is enough.

### 3) LLM routing (your 6 keys)

LiteLLM `Router`: same `model_name` (e.g. `interviewer`) mapped to multiple Gemini deployments (one key each) + Grok fallbacks; `simple-shuffle` / usage-based routing; retries + fallbacks on rate limit.

Live voice: rotate among Gemini keys on session start / reconnect (simple round-robin in our proxy) — LiteLLM may not cover Live the same way.

---

## Capability map

| Module id        | Responsibility                                                             | Depends on                         |
| ---------------- | -------------------------------------------------------------------------- | ---------------------------------- |
| `session`        | Mode select, round timers, phase machine (debug → design → llm → feedback) | —                                  |
| `llm-router`     | LiteLLM multi-key chat + vision for text/diagram turns                     | —                                  |
| `voice-live`     | Mic ↔ Gemini Live ↔ speaker; transcripts; barge-in                         | `session`                          |
| `voice-fallback` | STT → text LLM → TTS if Live unavailable                                   | `llm-router`, `session`            |
| `debug-round`    | Paste broken PyTorch; accept snippet pastes; interrupt-y follow-ups        | `session`, `voice-*`, `llm-router` |
| `design-round`   | Excalidraw embed; export PNG+labels to model                               | `session`, `voice-*`, `llm-router` |
| `llm-round`      | Flashcard-style defs; stop waffle; RAP-flavored techniques                 | `session`, `voice-*`, `llm-router` |
| `feedback`       | Short end debrief (like friend’s ask)                                      | `session`, `llm-router`            |

**Build order:** `llm-router` → `session` → `voice-live` (+ `voice-fallback` stub) → `debug-round` → `design-round` → `llm-round` → `feedback`.

---

## Product behavior

### Lobby

- Pick mode: soft | medium | strict | hardcore (skeptical).
- Start → mic permission → enter **debug**.

### Round 1 — PyTorch debug (~10 min hard cap)

- AI speaks + shows broken snippet in a code panel (copy button for Colab).
- You work in Colab; you **speak** findings and **paste** intermediate snippets into a text box.
- AI interrupts / asks next bug; does not essay.
- Timer visible; at cap → force transition (like friend’s interview).

### Round 2 — System design (10–15 min)

- AI reads aloud a short RAP-shaped problem (or shows compact prompt).
- Excalidraw panel opens; you draw boxes/arrows/labels.
- “Submit board” / each turn: PNG + label list → AI questions architecture (why / fail / scale).
- Timer; hard stop → next round.

### Round 3 — LLM techniques (~20–30 min)

- Demand **definition first, then stop** (friend failure mode).
- Topics pool: greedy, temperature, top-k/p, beam, quantization, KV cache, PagedAttention/continuous batching, grad checkpointing, GQA, LoRA/QLoRA, RAG vs FT, agent harness, MCP, HyDE, vLLM — RAP-flavored follow-ups from intent anchors.
- Mode controls skepticism / follow-up depth.

### End

- 60–90s spoken (+ text) feedback: what was solid, what to drill before Monday.

### Mode dial (system prompt + interrupt policy)

| Mode     | Behavior                                    |
| -------- | ------------------------------------------- |
| soft     | Hints allowed; longer answers OK            |
| medium   | Crisp; one follow-up                        |
| strict   | Exact defs; cut waffle fast                 |
| hardcore | Skeptical; “prove it”; interrupt mid-ramble |

---

## Technical shape (MVP)

- **Frontend:** Vite + React + TypeScript; `@excalidraw/excalidraw`; Web Audio for mic/playback.
- **Backend:** FastAPI; LiteLLM Router; WebSocket proxy for Gemini Live; REST for session + diagram upload + text turns.
- **Config:** `.env` with `GEMINI_API_KEY_1..N`, `GROK_API_KEY_1..N` — never commit.
- **State:** In-memory session (enough for one laptop user).

---

## Success criteria (done = ship)

- [ ] One full timed mock completes without crashing.
- [ ] Voice: you can interrupt the AI mid-sentence (Live barge-in) **or** fallback path works with push-to-talk.
- [ ] Debug: copy snippet → paste replies → AI tracks fixes.
- [ ] Design: Excalidraw → AI references your boxes in a follow-up.
- [ ] LLM round: asks for exact defs and cuts off essays in strict/hardcore.
- [ ] Mode switch changes interviewer tone.
- [ ] Keys rotate / fallback when one Gemini key rate-limits (text path).

---

## Explicitly not building this weekend

- Screen share / Colab watcher
- In-app code runner
- Multi-user / auth / deploy
- Perfect local OSS voice stack
- Custom canvas
- Mobile polish

---

## Decisions (locked)

1. **Voice:** Gemini Live primary; Whisper → LiteLLM text → TTS fallback.
2. **Stack:** Vite/React + FastAPI.
3. **Timers (defaults):** ~10 min debug / **10–15 min design** / ~25 min LLM (hard caps; mode may cut early).
