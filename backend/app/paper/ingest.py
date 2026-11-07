from __future__ import annotations

import io
import re
import uuid
import xml.etree.ElementTree as ET
from typing import Any

import httpx

from .models import Paper, PaperEquation, PaperReference, PaperSection

ARXIV_API = "https://export.arxiv.org/api/query"
ARXIV_HTML = "https://arxiv.org/html/{id}"
ARXIV_ABS = "https://arxiv.org/abs/{id}"


def extract_arxiv_id(text: str) -> str | None:
    raw = (text or "").strip()
    if not raw:
        return None
    m = re.search(
        r"(?:arxiv\.org/(?:abs|pdf|html)/|arxiv:)?(\d{4}\.\d{4,5})(?:v\d+)?",
        raw,
        re.I,
    )
    return m.group(1) if m else None


async def fetch_arxiv_meta(arxiv_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(ARXIV_API, params={"id_list": arxiv_id})
        r.raise_for_status()
    root = ET.fromstring(r.text)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entry = root.find("a:entry", ns)
    if entry is None:
        return {"title": arxiv_id, "authors": [], "abstract": "", "arxiv_id": arxiv_id}
    title = (entry.findtext("a:title", default="", namespaces=ns) or "").strip()
    title = re.sub(r"\s+", " ", title)
    summary = (entry.findtext("a:summary", default="", namespaces=ns) or "").strip()
    authors = [
        (a.findtext("a:name", default="", namespaces=ns) or "").strip()
        for a in entry.findall("a:author", ns)
    ]
    return {
        "title": title or arxiv_id,
        "authors": [a for a in authors if a],
        "abstract": summary,
        "arxiv_id": arxiv_id,
    }


async def fetch_arxiv_html_text(arxiv_id: str) -> str:
    url = ARXIV_HTML.format(id=arxiv_id)
    try:
        async with httpx.AsyncClient(timeout=45.0, follow_redirects=True) as client:
            r = await client.get(url, headers={"User-Agent": "Interviewer-DrDelta/0.1"})
            if r.status_code >= 400:
                return ""
            html = r.text
    except Exception:
        return ""
    # Crude strip — enough for tutoring chunks
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?is)<[^>]+>", "\n", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_pdf_bytes(raw: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(raw))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n\n".join(parts).strip()


def _split_sections(text: str) -> list[PaperSection]:
    lines = [ln.strip() for ln in text.splitlines()]
    headings = {
        "abstract",
        "introduction",
        "related work",
        "background",
        "method",
        "methods",
        "approach",
        "model",
        "architecture",
        "experiments",
        "results",
        "discussion",
        "conclusion",
        "conclusions",
        "references",
        "appendix",
    }
    sections: list[PaperSection] = []
    current = PaperSection(id="s0", heading="Body", paragraphs=[])
    buf: list[str] = []
    idx = 1

    def flush() -> None:
        nonlocal buf, current
        para = " ".join(buf).strip()
        if para:
            current.paragraphs.append(para[:4000])
        buf = []

    for ln in lines:
        if not ln:
            flush()
            continue
        key = re.sub(r"^[\d.]+\s*", "", ln).strip().lower()
        if len(ln) < 80 and any(key.startswith(h) for h in headings):
            flush()
            if current.paragraphs or current.heading != "Body":
                sections.append(current)
            current = PaperSection(id=f"s{idx}", heading=ln[:120], paragraphs=[])
            idx += 1
            continue
        buf.append(ln)
    flush()
    if current.paragraphs:
        sections.append(current)
    if not sections:
        sections = [
            PaperSection(
                id="s0",
                heading="Body",
                paragraphs=[text[:6000]] if text else [],
            )
        ]
    return sections[:40]


def _find_equations(text: str) -> list[PaperEquation]:
    eqs: list[PaperEquation] = []
    for i, m in enumerate(re.finditer(r"\$\$(.+?)\$\$", text, re.S)):
        latex = m.group(1).strip()
        if latex:
            eqs.append(
                PaperEquation(
                    id=f"e{i+1}",
                    latex=latex[:500],
                    context=text[max(0, m.start() - 120) : m.end() + 120][:400],
                )
            )
        if len(eqs) >= 30:
            break
    if not eqs:
        # Heuristic lines that look like equations
        for i, ln in enumerate(text.splitlines()):
            if "=" in ln and len(ln) < 160 and re.search(r"[A-Za-z]\\_|\\frac|\\sum|L\s*=", ln):
                eqs.append(PaperEquation(id=f"e{i+1}", latex=ln.strip()[:500], context=ln))
            if len(eqs) >= 12:
                break
    return eqs


def _find_references(text: str) -> list[PaperReference]:
    refs: list[PaperReference] = []
    chunk = text
    m = re.search(r"(?im)^references\b", text)
    if m:
        chunk = text[m.end() : m.end() + 12000]
    for line in chunk.splitlines():
        line = line.strip()
        if len(line) < 20:
            continue
        if not re.match(r"^\[?\d+\]?\.?\s+", line) and "arXiv" not in line:
            continue
        arxiv = extract_arxiv_id(line)
        refs.append(PaperReference(raw=line[:500], arxiv_id=arxiv, title=line[:160]))
        if len(refs) >= 40:
            break
    return refs


def paper_from_text(
    text: str,
    *,
    title: str = "",
    authors: list[str] | None = None,
    abstract: str = "",
    arxiv_id: str | None = None,
    source_url: str = "",
) -> Paper:
    body = text.strip()
    if not abstract:
        am = re.search(r"(?is)abstract\s*(.+?)(?:\n\s*\n|1\s+introduction|introduction)", body)
        abstract = (am.group(1).strip() if am else body[:800])[:4000]
    if not title:
        title = (body.splitlines()[0] if body else "Untitled paper")[:200]
    return Paper(
        id=str(uuid.uuid4()),
        title=title,
        authors=authors or [],
        arxiv_id=arxiv_id,
        abstract=abstract,
        sections=_split_sections(body),
        equations=_find_equations(body),
        references=_find_references(body),
        source_url=source_url,
    )


async def ingest_arxiv(arxiv_id: str) -> Paper:
    try:
        meta = await fetch_arxiv_meta(arxiv_id)
    except Exception:
        meta = {
            "title": arxiv_id,
            "authors": [],
            "abstract": "",
            "arxiv_id": arxiv_id,
        }
    try:
        html_text = await fetch_arxiv_html_text(arxiv_id)
    except Exception:
        html_text = ""
    text = html_text or f"{meta['title']}\n\nAbstract\n{meta['abstract']}"
    return paper_from_text(
        text,
        title=meta["title"],
        authors=meta["authors"],
        abstract=meta["abstract"],
        arxiv_id=arxiv_id,
        source_url=ARXIV_ABS.format(id=arxiv_id),
    )


async def ingest_pdf(raw: bytes, filename: str = "") -> Paper:
    text = parse_pdf_bytes(raw)
    if not text:
        raise ValueError("No text extracted from PDF")
    title = filename.rsplit(".", 1)[0] if filename else ""
    return paper_from_text(text, title=title or "Uploaded PDF")


async def ingest_request(
    *,
    arxiv_url: str = "",
    arxiv_id: str = "",
    text: str = "",
) -> Paper:
    aid = extract_arxiv_id(arxiv_id or arxiv_url) or extract_arxiv_id(text[:500])
    if aid:
        return await ingest_arxiv(aid)
    if text.strip():
        return paper_from_text(text)
    raise ValueError("Provide an arXiv id/url, PDF, or pasted text")
