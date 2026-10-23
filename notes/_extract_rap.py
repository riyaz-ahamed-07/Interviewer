from pathlib import Path
import re

text = open(r"C:\Users\thahs\Downloads\# RAP.txt", encoding="utf-8", errors="ignore").read()
out = Path(__file__).parent
for label, pat in [
    ("rapflow", r"# 2\. RAPFlow's anatomy.*?(?=\n# 3\. )"),
    ("aistudio", r"# 3\. AIStudio.*?(?=\n# 4\. )"),
    ("agentic", r"# 4\. AgenticStudio.*?(?=\n# 5\. )"),
    ("verify", r"# 7\. VerifyMe.*?(?=\n# 8\. )"),
    ("security", r"# 8\. RAP's security philosophy.*?(?=\n# 9\. )"),
]:
    m = re.search(pat, text, re.S)
    (out / f"_extract_{label}.txt").write_text(
        (m.group(0)[:12000] if m else "MISSING"), encoding="utf-8"
    )
    print(label, "ok" if m else "missing", len(m.group(0)) if m else 0)

# Grab a dense response about quantization/LoRA if present
for m in re.finditer(r"(## Response:.*?)(?=\n## Prompt:|\Z)", text, re.S):
    block = m.group(1)
    if "QLoRA" in block and "quantization" in block.lower() and len(block) > 800:
        (out / "_extract_qlora_block.txt").write_text(block[:15000], encoding="utf-8")
        print("qlora_block", len(block))
        break
