from pathlib import Path
import re

html = Path(__file__).parent.joinpath("ml-engineer-interview-notes.html").read_text(
    encoding="utf-8"
)
start = html.index("const chapters=")
end = html.index(";\nconst diagrams=", start)
chunk = html[start : end + 1]
assert "];;" not in html[start : end + 10], "double semicolon still present"
left = list(re.finditer(r"(?<![\\])([A-Za-z])'([A-Za-z])", chunk))
assert not left, left
py = chunk.replace("const chapters=", "chapters =", 1)
compile(py, "<c>", "exec")
print("VERIFY OK")
for line in chunk.splitlines():
    if "Classical supervised" in line:
        print(line[:130])
        break
print("ending:", repr(chunk[-12:]))
