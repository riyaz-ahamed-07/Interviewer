"""Generate RAP-style short PyTorch debug drills (like real Wed/Thu/Fri screens).

Not giant model code — tiny Linear/CE scripts with 2–4 loud, chained bugs.
"""

from __future__ import annotations

import json
import logging
import random
import re
from typing import Any

from .llm_router import chat_completion_groq

logger = logging.getLogger(__name__)

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

# Real RAP screens were ~15–30 lines: device, Linear in_features, CE target dtype,
# CUDA→numpy. Generate NEW snippets at that difficulty — never copy these verbatim.
_STYLE_EXAMPLES = """
STYLE EXAMPLES (do NOT copy; invent different numbers / names / order):

Example A — device + dtype flavor:
```python
import torch
import torch.nn as nn

device = "cuda"
model = nn.Linear(10, 3).to(device)
x = torch.randn(32, 10)
y = torch.randint(0, 3, (32,)).int()
loss = nn.CrossEntropyLoss()(model(x), y)
loss.backward()
print(loss.item())
```

Example B — shape + float targets + .numpy() on CUDA flavor:
```python
import torch
import torch.nn as nn

device = "cuda"
x = torch.randn(32, 3).to(device)
y = torch.randint(0, 2, (32,)).float().to(device)
model = nn.Linear(4, 2).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
for epoch in range(5):
    optimizer.zero_grad()
    out = model(x)
    loss = criterion(out, y)
    loss.backward()
    optimizer.step()
preds = out.argmax(1)
print("Predictions:", preds.numpy())
```

Example C — shape + CUDA numpy flavor (cleaner loop):
```python
import torch
import torch.nn as nn

device = "cuda"
x = torch.rand(32, 3).to(device)
y = torch.randint(0, 2, (32,)).to(device)
model = nn.Linear(4, 2).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
for epoch in range(5):
    optimizer.zero_grad()
    out = model(x)
    loss = criterion(out, y)
    loss.backward()
    optimizer.step()
preds = out.argmax(1)
print("Predictions:", preds.numpy())
```
"""

GEN_SYSTEM = f"""You generate ORIGINAL PyTorch debugging interview snippets for RAP ML intern screens.
Return ONLY valid JSON (no markdown fences) with keys:
- title: short title (must NOT spoil the bugs)
- code: full runnable Python script (broken on purpose)
- hidden_bugs: array of brief bug descriptions in discovery order (PRIVATE)
- cascade_note: one sentence on how early fixes reveal later errors (PRIVATE)

{_STYLE_EXAMPLES}

HARD STYLE RULES (match real RAP interviews):
- Keep it SHORT: about 12–35 lines. Tiny Linear (+ optional short train loop). NO CNN, NO custom Module classes unless tiny, NO transformers.
- Plant 2–4 CHAINED bugs that RAISE (RuntimeError / TypeError / ValueError / AttributeError).
- Allowed bug families ONLY (mix 2–4):
  1) device mismatch (model/x/y not all on same device)
  2) Linear in_features ≠ x last dim
  3) CrossEntropyLoss targets wrong dtype (float / int32 instead of long)
  4) CE class count / target range mismatch
  5) .numpy() or similar on a CUDA tensor
  6) batch-size mismatch between logits and targets
- EVERY bug must raise when that stage runs. No silent wrong-answer bugs.
- FORBIDDEN: softmax-before-CE, forgotten zero_grad as the "main" bug, train/eval,
  wrong LR, giant models, file I/O, comments/docstrings, spoiler words in code.
- CRITICAL: code must contain ZERO comments and ZERO docstrings.
- Use torch / torch.nn only. Prefer device="cuda" like Colab interviews (still valid if CUDA missing — device bugs still raise).
- Vary batch sizes, feature dims, class counts, and bug ORDER each time so it is not a copy of the examples.
"""


async def generate_debug_drill(difficulty: str = "rap") -> dict[str, Any]:
    """difficulty is ignored for selection — RAP screens are one band. Kept for API compat."""
    _ = difficulty
    seed = random.randint(1000, 9999)
    user = (
        f"Invent a NEW RAP-style short snippet now (seed={seed}). "
        "Different dims and bug order from the style examples. "
        "NO comments. EVERY bug must RAISE."
    )
    drill = await _generate_once(user)
    if drill and not _has_silent_signals(drill) and _looks_rap_short(drill):
        return drill

    if drill and (_has_silent_signals(drill) or not _looks_rap_short(drill)):
        logger.warning("Drill rejected (silent or too complex); regenerating")
        retry = (
            user
            + "\nREJECTED DRAFT: keep under ~35 lines, only Linear+CE style, "
            "only raising device/shape/dtype/numpy bugs. No CNN / custom nets."
        )
        drill = await _generate_once(retry)
        if drill and not _has_silent_signals(drill) and _looks_rap_short(drill):
            return drill

    logger.warning("Using RAP emergency drill")
    return _emergency_drill()


def _looks_rap_short(drill: dict[str, Any]) -> bool:
    code = drill.get("code") or ""
    lines = [ln for ln in code.splitlines() if ln.strip()]
    if len(lines) > 45:
        return False
    if re.search(r"Conv2d|Transformer|MultiheadAttention|nn\.Sequential", code):
        return False
    return "nn.Linear" in code or "Linear(" in code


async def _generate_once(user: str) -> dict[str, Any] | None:
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
    drill["difficulty"] = "rap"
    return drill


def _has_silent_signals(drill: dict[str, Any]) -> bool:
    meta = " ".join(
        [
            " ".join(str(b) for b in (drill.get("hidden_bugs") or [])),
            str(drill.get("cascade_note") or ""),
        ]
    )
    if _SILENT_BUG_RE.search(meta):
        return True
    code = drill.get("code") or ""
    if re.search(r"softmax\s*\(", code) and re.search(
        r"CrossEntropyLoss\s*\(", code
    ):
        return True
    return False


def strip_comments(code: str) -> str:
    code = re.sub(
        r'^\s*("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')\s*', "", code, flags=re.M
    )
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


def _emergency_drill() -> dict[str, Any]:
    """Fallback patterned on real RAP screens (new dims)."""
    variants = [
        {
            "title": "RAP Linear device/dtype",
            "code": """import torch
import torch.nn as nn

device = "cuda"
model = nn.Linear(8, 4).to(device)
x = torch.randn(16, 8)
y = torch.randint(0, 4, (16,)).int()
loss = nn.CrossEntropyLoss()(model(x), y)
loss.backward()
print(loss.item())
""",
            "hidden_bugs": [
                "x (and y) on CPU while model on CUDA → device RuntimeError",
                "CE targets are int32; need long/int64 → TypeError/RuntimeError",
            ],
            "cascade_note": "Device fix reveals float/int target dtype crash.",
        },
        {
            "title": "RAP Linear shape + CUDA numpy",
            "code": """import torch
import torch.nn as nn

device = "cuda"
x = torch.randn(24, 5).to(device)
y = torch.randint(0, 3, (24,)).float().to(device)
model = nn.Linear(7, 3).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.05)
for epoch in range(3):
    optimizer.zero_grad()
    out = model(x)
    loss = criterion(out, y)
    loss.backward()
    optimizer.step()
preds = out.argmax(1)
print(preds.numpy())
""",
            "hidden_bugs": [
                "Linear expects 7 features but x has 5 → shape RuntimeError",
                "CE targets are float → dtype RuntimeError",
                "preds.numpy() on CUDA tensor → TypeError",
            ],
            "cascade_note": "Shape then dtype then CUDA numpy.",
        },
    ]
    pick = random.choice(variants)
    return {
        "title": pick["title"],
        "code": strip_comments(pick["code"]),
        "hidden_bugs": pick["hidden_bugs"],
        "cascade_note": pick["cascade_note"],
        "difficulty": "rap",
    }
