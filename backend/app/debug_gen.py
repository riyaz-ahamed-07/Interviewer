"""Generate unique chained PyTorch debug drills (no fixed bank).

Every planted bug must FAIL LOUDLY (raise) when that stage is reached —
no silent wrong-answer / train-wrong bugs.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from .llm_router import chat_completion_groq

logger = logging.getLogger(__name__)

# Match against hidden_bugs / cascade notes only (not raw code boilerplate).
_SILENT_BUG_RE = re.compile(
    r"softmax|"
    r"forgot(?:ten)?\s+zero[_\s-]?grad|missing\s+zero[_\s-]?grad|no\s+zero[_\s-]?grad|"
    r"train\s*/\s*eval|train\s+vs\s+eval|forgot\s+\.eval|forgot\s+\.train|"
    r"batchnorm\s+train|batch[_\s-]?norm\s+eval|"
    r"wrong\s+learning\s+rate|bad\s+learning\s+rate|"
    r"wrong\s+(loss|result|output|answer|grad)|silent|"
    r"train\s+wrong|incorrect\s+output|no\s+error|doesn.?t\s+crash|"
    r"wrong\s+reduction|forgot\s+detach|\.item\(\)\s+mid",
    re.I,
)

DIFFICULTY_SPEC = {
    "easy": (
        "Exactly 2 bugs. BOTH must raise RuntimeError/TypeError/ValueError "
        "when reached (never silent wrong math). Typical pair: (1) tensor "
        "device mismatch CPU vs CUDA, (2) after device fix, Linear in_features "
        "or view/flatten shape mismatch. Code ~25-40 lines."
    ),
    "medium": (
        "3-4 CHAINED bugs. EACH must raise when that stage is hit. Allowed "
        "families only: device mismatch, shape/view/flatten vs Linear/"
        "Conv channels, CrossEntropy target dtype (float vs long), CE batch "
        "size mismatch, non-contiguous .view that errors, wrong ndim for "
        "matmul/bmm, indexing out of range. Fixing A must reveal B. "
        "Code ~40-70 lines. No softmax-before-CE, no forgotten zero_grad, "
        "no train/eval."
    ),
    "hard": (
        "4-6 deeply chained bugs; EVERY one raises. Mix device, shapes, "
        "dtype, contiguous views, broadcast that errors, parameter not "
        "registered then used in a way that blows up, wrong Conv/Linear "
        "channel math. Cascades: fixing step-1 surfaces step-3. "
        "Code ~60-100 lines. Still ZERO silent logic bugs."
    ),
}


GEN_SYSTEM = """You generate ORIGINAL PyTorch debugging interview snippets.
Return ONLY valid JSON (no markdown fences) with keys:
- title: short title (must NOT spoil the bugs)
- code: full runnable Python script (broken on purpose)
- hidden_bugs: array of brief bug descriptions in intended discovery order (PRIVATE — never appear in code)
- cascade_note: one sentence on how early fixes interact with later errors (PRIVATE)

Rules for code:
- Must be self-contained: imports, model, fake batch, loss, backward/step.
- CRITICAL — EXPLICIT FAILURES ONLY:
  Every planted bug MUST raise an exception (RuntimeError, TypeError, ValueError,
  IndexError, etc.) when that line/stage executes. The candidate discovers bugs
  by reading TRACEBACKS after each fix+rerun.
- FORBIDDEN (silent / implicit bugs that run but give wrong answers):
  softmax before CrossEntropyLoss, forgotten zero_grad, train vs eval,
  wrong but runnable loss math, wrong learning rate, wrong reduction,
  BatchNorm train/eval, detach mistakes that still print a number, any
  "trains wrong with no crash".
- Prefer device mismatch, shape/view/Linear in_features, CE target dtype,
  batch-size mismatch, illegal views, matmul rank errors.
- Bugs must CHAIN: fixing an early crash reveals the next crash.
- Prefer realistic ML-intern mistakes, not trivia syntax typos.
- Use torch / torch.nn only (no internet, no files).
- CRITICAL: code must contain ZERO comments and ZERO docstrings.
  No # lines, no \"\"\" ... \"\"\", no spoiler words like bug/fix/wrong/TODO/FIXME/should/missing.
- Vary architecture each time (MLP, tiny CNN, embedding+linear, etc.).
- End of script may print a loss only after a path that would have crashed
  if any planted bug remained — do not add assert checks that spoil bugs.
"""


async def generate_debug_drill(difficulty: str) -> dict[str, Any]:
    level = difficulty if difficulty in DIFFICULTY_SPEC else "medium"
    user = (
        f"Difficulty: {level}\n"
        f"Spec: {DIFFICULTY_SPEC[level]}\n"
        "Invent a NEW snippet now. Different from common MNIST Linear(784) demos if possible.\n"
        "Again: NO comments. EVERY bug must RAISE — no silent wrong-output bugs."
    )
    drill = await _generate_once(level, user)
    if drill and not _has_silent_signals(drill):
        return drill

    if drill and _has_silent_signals(drill):
        logger.warning("Drill had silent-bug signals; regenerating once")
        retry_user = (
            user
            + "\nPREVIOUS DRAFT REJECTED: it included silent/logic bugs "
            "(e.g. softmax-before-CE, zero_grad, train/eval). "
            "Rewrite with ONLY raising bugs (device/shape/dtype/batch)."
        )
        drill = await _generate_once(level, retry_user)
        if drill and not _has_silent_signals(drill):
            return drill

    logger.warning("Using emergency loud-fail drill")
    return _emergency_drill(level)


async def _generate_once(level: str, user: str) -> dict[str, Any] | None:
    try:
        raw = await chat_completion_groq(GEN_SYSTEM, user)
    except Exception:
        logger.exception("Drill gen threw")
        return None

    if raw.startswith("[LLM error"):
        logger.warning("Drill gen LLM error: %s", raw[:200])
        return None

    drill = _parse_drill(raw)
    if not drill.get("code") or "torch" not in drill["code"]:
        logger.warning("Drill gen parse weak")
        return None
    drill["code"] = strip_comments(drill["code"])
    drill["difficulty"] = level
    return drill


def _has_silent_signals(drill: dict[str, Any]) -> bool:
    """Reject drills that describe or plant classic silent bugs."""
    meta = " ".join(
        [
            " ".join(str(b) for b in (drill.get("hidden_bugs") or [])),
            str(drill.get("cascade_note") or ""),
        ]
    )
    if _SILENT_BUG_RE.search(meta):
        return True
    # softmax(...) into CrossEntropyLoss is the classic silent CE bug
    code = drill.get("code") or ""
    if re.search(r"softmax\s*\(", code) and re.search(
        r"CrossEntropyLoss\s*\(", code
    ):
        return True
    return False


def strip_comments(code: str) -> str:
    """Remove comments/docstrings so bugs are not spoiled."""
    code = re.sub(r'^\s*("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')\s*', "", code, flags=re.M)
    out_lines: list[str] = []
    for line in code.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        cleaned = _strip_inline_comment(line)
        if cleaned.strip():
            out_lines.append(cleaned.rstrip())
    return "\n".join(out_lines).strip() + "\n"


def _strip_inline_comment(line: str) -> str:
    in_single = False
    in_double = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return line[:i].rstrip()
        i += 1
    return line


def _parse_drill(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return {
                "title": str(data.get("title") or "Generated debug"),
                "code": str(data.get("code") or "").strip(),
                "hidden_bugs": data.get("hidden_bugs") or [],
                "cascade_note": str(data.get("cascade_note") or ""),
            }
    except json.JSONDecodeError:
        pass
    m = re.search(r"```python\n(.*?)```", raw, re.DOTALL)
    if m:
        return {
            "title": "Generated debug",
            "code": m.group(1).strip(),
            "hidden_bugs": [],
            "cascade_note": "",
        }
    return {}


def _emergency_drill(level: str) -> dict[str, Any]:
    # Both bugs always raise (CPU or CUDA): wrong Linear in_features first,
    # then float CE targets after the shape fix.
    code = '''import torch
import torch.nn as nn

class TinyCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(1, 8, 3, padding=1)
        self.fc = nn.Linear(8 * 14 * 14, 10)

    def forward(self, x):
        x = torch.relu(self.conv(x))
        x = x.view(x.size(0), -1)
        return self.fc(x)

model = TinyCNN()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
crit = nn.CrossEntropyLoss()
xb = torch.randn(16, 1, 28, 28)
yb = torch.randint(0, 10, (16,)).float()
opt.zero_grad()
out = model(xb)
loss = crit(out, yb)
loss.backward()
opt.step()
print(loss.item())
'''
    return {
        "title": f"Emergency TinyCNN ({level})",
        "code": strip_comments(code),
        "hidden_bugs": [
            "fc expects 8*14*14 but flattened conv is 8*28*28 → shape RuntimeError",
            "CE targets are float; must be long/int64 → TypeError/RuntimeError",
        ],
        "cascade_note": "Shape fix reveals float-target CE crash.",
        "difficulty": level,
    }
