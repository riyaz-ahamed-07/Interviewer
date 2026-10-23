"""Merge STE100 content banks into the diagram-rich notes HTML."""
from __future__ import annotations

import html as html_lib
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
HTML_PATH = ROOT / "ml-engineer-interview-notes.html"

TITLE_OVERRIDES = {
    0: "Interview map — what they actually test",
    2: "Debug round — the ideas behind every bug",
    84: "Scenario answer templates",
}


def esc(text: str) -> str:
    return html_lib.escape(text, quote=False)


def bullets(items: list[str]) -> str:
    return "".join(f"<li>{esc(x)}</li>" for x in items)


def load_content() -> dict:
    merged: dict = {}
    for name in (
        "_content_part1.json",
        "_content_part2.json",
        "_content_part3.json",
        "_content_part4.json",
    ):
        merged.update(json.loads((ROOT / name).read_text(encoding="utf-8")))
    assert len(merged) == 85, len(merged)
    return merged


def extract_figs(tb_inner: str) -> str:
    start = tb_inner.find('<div class="figs">')
    assert start >= 0, "missing figs block"
    # Walk nested divs until figs closes (figures use <figure>, not nested topic divs).
    i = start + len('<div class="figs">')
    depth = 1
    while i < len(tb_inner) and depth:
        next_open = tb_inner.find("<div", i)
        next_close = tb_inner.find("</div>", i)
        assert next_close >= 0, "unclosed figs"
        if next_open >= 0 and next_open < next_close:
            depth += 1
            i = next_open + 4
        else:
            depth -= 1
            i = next_close + len("</div>")
    return tb_inner[start:i]


def rewrite_topic(body: str, data: dict, title_override: str | None) -> str:
    # Split header vs tb
    m = re.search(r'(.*?)(<div class="tb">)(.*)(</div>\s*)$', body, re.S)
    assert m, "missing tb"
    head, tb_open, tb_inner, tb_close_tail = m.group(1), m.group(2), m.group(3), m.group(4)

    if title_override:
        head = re.sub(
            r"(<h3>)(.*?)(</h3>)",
            lambda mm: mm.group(1) + esc(title_override) + mm.group(3),
            head,
            count=1,
        )

    figs = extract_figs(tb_inner)
    short = " ".join(data["short"])
    new_tb = (
        tb_open
        + f'<div class="one"><span class="onelab">In short</span> {esc(short)}</div>'
        + f'<div class="sec s-int"><h4>Picture it</h4><ul>{bullets(data["picture"])}</ul></div>'
        + f'<div class="sec s-math"><h4>How it works</h4><ul>{bullets(data["inside"])}</ul></div>'
        + figs
        + f'<div class="sec s-why"><h4>When it matters</h4><ul>{bullets(data["matters"])}</ul></div>'
        + f'<div class="sec s-trap"><h4>Watch out</h4><ul>{bullets(data["watch"])}</ul></div>'
        + tb_close_tail
    )
    return head + new_tb


def polish_shell(doc: str) -> str:
    doc = doc.replace(
        "<title>RAP ML Intern — Master Notes</title>",
        "<title>ML Interview Master Notes</title>",
    )
    doc = doc.replace(
        '<div class="brand">✎ Contents</div>',
        '<div class="brand">ML Interview Notes</div>',
    )
    doc = re.sub(
        r"<header class=\"hero\">.*?</header>",
        lambda _m: """<header class="hero">
<h1>ML Interview <span>Master Notes</span></h1>
<p class="sub">Diagrams stay. Words teach. One careful read should be enough.</p>
<p class="by">Plain English · real examples · low-level mechanism · interview ready</p>
<p class="howto">How to use: open a topic → read <b>In short</b> → study the diagram → walk <b>Picture it</b> and <b>How it works</b> → check <b>Watch out</b>. Mark Understood when you can explain it aloud without the page.</p>
</header>""",
        doc,
        count=1,
        flags=re.S,
    )

    replacements = [
        (
            "Part 0 — How to use these notes + RAP interview map",
            "Part 0 — How to use these notes + interview map",
        ),
        (
            "Part 1 — After the model is built (P0: memorise the one-liners)",
            "Part 1 — After the model is built (serve, tune, and ship)",
        ),
        (
            "Part 3 — RAG, agents, tools (RAP-heavy)",
            "Part 3 — RAG, agents, and tools",
        ),
        ("read once, then jump to Part 1", "Start here, then jump to Part 1"),
        ("AgenticStudio-style thinking", "Design answers that fit real products"),
        (
            "Last morning: open “Rapid-fire revision” in Part 1 and say every line aloud. No new topics. You've got this. ✎",
            "Before the interview: pick ten hard topics, close the page, and explain each aloud. No new topics that morning.",
        ),
        (
            "RAP interview map — what they actually test",
            "Interview map — what they actually test",
        ),
        (
            "PyTorch debug round — the concepts behind every bug",
            "Debug round — the ideas behind every bug",
        ),
        ("79. RAP-style scenario templates", "79. Scenario answer templates"),
        ("RAP-style scenario templates", "Scenario answer templates"),
    ]
    for a, b in replacements:
        doc = doc.replace(a, b)

    doc = re.sub(r'\s*<span class="wc">\(.*?words?\)</span>', "", doc)
    return doc


def rebuild_flash_table(doc: str, content: dict) -> str:
    m = re.search(
        r'<details class="flash">.*?<table class="ftab">(.*?)</table>.*?</details>',
        doc,
        re.S,
    )
    if not m:
        return doc
    old_rows = re.findall(
        r"<tr><td><a href=\"#([^\"]+)\">(.*?)</a></td><td>.*?</td></tr>",
        m.group(1),
        re.S,
    )
    rows = []
    for idx, (href, label) in enumerate(old_rows, start=3):
        short = " ".join(content[str(idx)]["short"])
        rows.append(
            f'<tr><td><a href="#{href}">{label}</a></td><td>{esc(short)}</td></tr>'
        )
    new_block = (
        '<details class="flash"><summary>⚡ Quick revision: Part 1 core ideas '
        "(explain each aloud; do not recite a slogan)</summary>"
        '<table class="ftab"><tr><th>Topic</th><th>Core idea</th></tr>'
        + "".join(rows)
        + "</table></details>"
    )
    return re.sub(
        r'<details class="flash">.*?</details>',
        lambda _m: new_block,
        doc,
        count=1,
        flags=re.S,
    )


def main() -> None:
    content = load_content()
    doc = HTML_PATH.read_text(encoding="utf-8")
    doc = polish_shell(doc)

    articles = list(
        re.finditer(r'(<article class="topic"[^>]*>)(.*?)(</article>)', doc, re.S)
    )
    assert len(articles) == 85, len(articles)

    out: list[str] = []
    last = 0
    fig_total = 0
    for i, m in enumerate(articles):
        out.append(doc[last : m.start()])
        open_tag, body, close = m.group(1), m.group(2), m.group(3)
        data = content[str(i)]
        for field in ("short", "picture", "inside", "matters", "watch"):
            assert field in data and data[field], (i, field)
        fb = len(re.findall(r"<figure", body))
        new_body = rewrite_topic(body, data, TITLE_OVERRIDES.get(i))
        fa = len(re.findall(r"<figure", new_body))
        assert fb == fa, f"figure loss at topic {i}: {fb}->{fa}"
        # all four sections present
        for key in ("s-int", "s-math", "s-why", "s-trap"):
            assert f'class="sec {key}"' in new_body, (i, key)
        assert ">How it works<" in new_body
        assert ">Watch out<" in new_body
        fig_total += fa
        out.append(open_tag + new_body + close)
        last = m.end()
    out.append(doc[last:])
    new_doc = "".join(out)
    new_doc = rebuild_flash_table(new_doc, content)

    assert "Interview one-liner" not in new_doc
    assert "memorise the one-liners" not in new_doc

    HTML_PATH.write_text(new_doc, encoding="utf-8")
    print("OK wrote", HTML_PATH)
    print("size", HTML_PATH.stat().st_size)
    print(
        "topics",
        len(articles),
        "figures",
        fig_total,
        "svgs",
        len(re.findall(r"<svg\b", new_doc)),
        "how-it-works",
        new_doc.count(">How it works<"),
        "watch-out",
        new_doc.count(">Watch out<"),
    )


if __name__ == "__main__":
    main()
