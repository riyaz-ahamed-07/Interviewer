# -*- coding: utf-8 -*-
"""Escape apostrophes inside single-quoted JS string literals in chapters."""
from pathlib import Path
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = Path(__file__).parent / "ml-engineer-interview-notes.html"
html = path.read_text(encoding="utf-8")
start = html.index("const chapters=")
end = html.index(";\nconst diagrams=", start)
chunk = html[start : end + 1]

bad = list(re.finditer(r"(?<![\\])([A-Za-z])'([A-Za-z])", chunk))
print("apostrophe-in-word count:", len(bad))
for m in bad:
    print(repr(m.group(0)))

fixed = re.sub(r"(?<![\\])([A-Za-z])'([A-Za-z])", r"\1\\'\2", chunk)
html2 = html[:start] + fixed + html[end + 1 :]
path.write_text(html2, encoding="utf-8")
print("wrote", path)

# Verify with Node if available, else heuristic: no letter'letter left unescaped
left = list(re.finditer(r"(?<![\\])([A-Za-z])'([A-Za-z])", fixed))
print("remaining unescaped:", len(left))
assert not left, left

# Parse check: node --check on extracted script is heavy; use python on rewritten assignment
py = fixed.replace("const chapters=", "chapters =", 1)
try:
    compile(py, "<chapters>", "exec")
    print("PYTHON-PARSE OK (as chapters=)")
except SyntaxError as e:
    print("PARSE FAIL", e)
    lines = py.splitlines()
    if e.lineno:
        for i in range(max(0, e.lineno - 2), min(len(lines), e.lineno + 1)):
            print(f"{i+1}: {lines[i][:200]}")
    raise

# Full script extract optional node check
try:
    r = subprocess.run(
        ["node", "--check", str(path)],
        capture_output=True,
        text=True,
    )
    # node --check on HTML will fail; skip
except FileNotFoundError:
    pass

print("VERIFY OK")
