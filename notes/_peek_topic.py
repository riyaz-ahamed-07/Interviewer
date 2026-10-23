from pathlib import Path
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
t = Path(__file__).parent.joinpath("ml-engineer-interview-notes.html").read_text(
    encoding="utf-8"
)
# Restore from downloads first? Check current topic 3 structure
bodies = re.findall(r'<article class="topic"[^>]*>(.*?)</article>', t, re.S)
b = bodies[3]
b2 = re.sub(r"<figure.*?</figure>", "\n[FIG]\n", b, flags=re.S)
# show structure markers
for m in re.finditer(r'<div class="(one|sec [^"]+|figs)"|</div>|<h4>[^<]+</h4>|<ul', b2):
    print(m.group(0)[:80])
print("--- snippet ---")
# print around secs without fig content
print(b2[:2500])
print("...")
print(b2[-1500:])
