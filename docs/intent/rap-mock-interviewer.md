# RAP Mock Interviewer — Statement of Intent

Confirmed: 2026-10-23

## Outcome

Voice-first solo RAP mock coach for one realistic ML Intern interview loop:

1. **PyTorch debug** — AI drops a broken snippet (like chat); candidate pastes into real Colab; candidate dictates issues/fixes and pastes snippets as they debug; AI follows and interrupts.
2. **System design** — candidate draws architecture on an embedded OSS whiteboard (Excalidraw or similar); AI can read the diagram so the round feels real.
3. **LLM techniques** — crisp definitions under pressure; interrupt waffle; RAP-flavored follow-ups.

Modes: soft / medium / strict / hardcore (skeptical). Adaptive follow-ups, not a fixed question bank.

## User

Only the candidate (you), practicing alone — not multi-person video conferencing.

## Why now

RAP ML Engineer Intern interview on **Monday 26 Oct 2026**. Near 0% prepared; friend’s debrief showed interrupt-y timing (~10m debug → ~5m design stop → ~30m LLM defs) and zero patience for essays when a definition was asked.

## Success

By Sunday night: one full timed mock in a chosen mode that feels interrupt-y like the real loop and forces crisp answers under time pressure.

## Constraint

- Weekend MVP only.
- Gemini (+ Grok) API keys via LiteLLM for rate-limit rerouting.
- Voice is primary; text is a side channel (paste code/snippets, optional transcript).
- Voice aim: as close as practical to ChatGPT voice mode while staying free / OSS-leaning (exact STT/TTS stack TBD in spike).
- System design: integrate free OSS diagram tool (prefer Excalidraw embed); do not build a canvas from scratch. AI consumes export (JSON / SVG / PNG) to “see” the diagram.

## Out of scope (this weekend)

- Multi-person video / Zoom clone
- Screen share or Colab page watching
- In-app Colab / IDE / code runner
- Custom diagram editor from scratch
- Post-Monday product polish / multi-role expansion

## Context anchors (for interviewer persona & content)

- Interviewer resumes: Deepanshu Dashora, Vishwanath (RAP) — agent harness, RAG, Graph RAG, OCR/doc intel, Unsloth/SFT, vLLM, HyDE, MCP, etc.
- Friend’s loop: debug → design (notepad) → LLM techniques (quantization, greedy/GQA/etc., demand exact defs).
- Prep flashcards already drafted (decoding, KV cache, LoRA, RAG vs FT, agent harness, MCP, …).

## Next decisions (not locked)

- STT/TTS providers that maximize realism under free/OSS constraints
- Exact Excalidraw (or alternative) embed + how diagram state is sent to the LLM each turn
- Round timers and interruption policy per mode
