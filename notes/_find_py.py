from pathlib import Path
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
t = Path(__file__).parent.joinpath("ml-engineer-interview-notes.html").read_text(
    encoding="utf-8"
)
bodies = re.findall(r'<article class="topic"[^>]*>(.*?)</article>', t, re.S)
pat = re.compile(r".{0,60}(torch\.|nn\.|requires_grad|CrossEntropyLoss|batch_first|pickle).{0,60}", re.I)
for i, b in enumerate(bodies):
    b2 = re.sub(r"<figure.*?</figure>", "", b, flags=re.S)
    hits = pat.findall(b2)
    if hits:
        print(i, hits)
        for m in pat.finditer(b2):
            print(" ", m.group(0).replace("\n", " ")[:140])
print("--- memorise contexts ---")
for m in re.finditer(r".{0,40}memorise.{0,40}", t, re.I):
    print(m.group(0).replace("\n", " "))
