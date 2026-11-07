from __future__ import annotations

import json
import logging
import re
from typing import Any

from ..llm_router import chat_completion
from .models import (
    Concept,
    Paper,
    PaperMap,
    ParentDelta,
    ParentInfo,
    Pass1,
    Prerequisite,
)
from .prompts import CARDS_PROMPT, PAPER_MAP_PROMPT
from .store import save_cards, save_map
from .models import FlashCard
import uuid
import time

logger = logging.getLogger(__name__)


def _strip_json(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text


def _sections_blob(paper: Paper, limit: int = 12000) -> str:
    parts: list[str] = []
    used = 0
    for s in paper.sections:
        chunk = f"[{s.id}] {s.heading}\n" + "\n".join(s.paragraphs[:3])
        if used + len(chunk) > limit:
            break
        parts.append(chunk)
        used += len(chunk)
    return "\n\n".join(parts)


def fallback_map(paper: Paper) -> PaperMap:
    title_l = (paper.title or "").lower()
    abstract_l = (paper.abstract or "").lower()
    parent = ParentInfo(title="unknown", one_liner="Could not auto-detect parent.")
    deltas: list[ParentDelta] = []
    prereqs = [
        Prerequisite(
            id="p_specdec",
            name="speculative decoding",
            why_needed="Common parent for draft-and-verify LLM speedups",
            check_question="What stays lossless in speculative decoding?",
            primer="A small draft model proposes tokens; the target verifies them in parallel. Accepted tokens stay identical to target-only decoding.",
        ),
        Prerequisite(
            id="p_kv",
            name="KV cache",
            why_needed="Attention reuse across decoding steps",
            check_question="What do K and V store in transformer decoding?",
            primer="Key/value tensors from past tokens are cached so new tokens attend without recomputing the full past.",
        ),
    ]
    if "diffusion" in title_l or "diffusion" in abstract_l or "dflash" in title_l:
        parent = ParentInfo(
            title="Fast Inference from Transformers via Speculative Decoding",
            arxiv_id="2211.17192",
            one_liner="Draft-then-verify decoding that keeps target-model quality.",
            deltas=[
                ParentDelta(
                    component="drafter",
                    before="Small autoregressive draft model (gamma sequential steps)",
                    after="Block-diffusion draft model that proposes a whole block in one forward pass",
                    why_it_matters="Draft cost becomes roughly parallel instead of gamma times a step",
                    section_id=paper.sections[0].id if paper.sections else "",
                ),
                ParentDelta(
                    component="conditioning",
                    before="Little or no target-feature fusion into the drafter",
                    after="Target hidden features injected as extra K/V into draft layers",
                    why_it_matters="Raises draft acceptance without changing target verification",
                ),
            ],
        )
        deltas = parent.deltas
        prereqs.insert(
            1,
            Prerequisite(
                id="p_diff",
                name="masked / block diffusion LMs",
                why_needed="Understands how a block can be drafted in parallel",
                check_question="Why can a diffusion drafter emit many tokens in one forward?",
                primer="Instead of left-to-right next-token prediction, a diffusion-style drafter denoises a block of positions together.",
            ),
        )
        prereqs.append(
            Prerequisite(
                id="p_accept",
                name="acceptance length",
                why_needed="Links draft quality to wall-clock speedup",
                check_question="What is tau (acceptance length) in speculative decoding?",
                primer="Acceptance length is the average number of drafted tokens kept per verification step. Higher tau usually means higher speedup.",
            ),
        )

    concepts = [
        Concept(
            id="c1",
            title="Pass-1: what problem and claim",
            section_ids=[paper.sections[0].id] if paper.sections else [],
            summary="Problem, claim, and why it matters",
        ),
        Concept(
            id="c2",
            title="Parent idea and the one big change",
            summary="Diff vs the parent method",
        ),
        Concept(
            id="c3",
            title="Core mechanism",
            section_ids=[s.id for s in paper.sections[1:3]],
            equation_ids=[e.id for e in paper.equations[:2]],
            summary="How the method actually runs",
        ),
        Concept(
            id="c4",
            title="Key equation / acceptance length",
            equation_ids=[e.id for e in paper.equations[:1]],
            summary="Math that drives the speedup",
        ),
        Concept(
            id="c5",
            title="Training or objective details",
            summary="What is optimized and why",
        ),
        Concept(
            id="c6",
            title="Results, limits, skepticism",
            summary="What the experiments really show",
        ),
    ]

    mermaid_parent = (
        "flowchart LR\n"
        "input[Input] --> draft[AR draft model]\n"
        "draft --> verify[Target verify]\n"
        "verify --> out[Output tokens]\n"
        "classDef changed fill:#f6c945,stroke:#333\n"
        "classDef added fill:#8fdb8f,stroke:#333\n"
        "classDef removed fill:#ccc,stroke-dasharray: 5 5\n"
    )
    mermaid_paper = (
        "flowchart LR\n"
        "input[Input] --> feats[Target hidden features]\n"
        "feats --> draft[Block diffusion draft]\n"
        "draft --> verify[Target verify]\n"
        "verify --> out[Output tokens]\n"
        "classDef changed fill:#f6c945,stroke:#333\n"
        "classDef added fill:#8fdb8f,stroke:#333\n"
        "class draft changed\n"
        "class feats added\n"
    )

    return PaperMap(
        pass1=Pass1(
            problem=paper.abstract[:280] or "See abstract",
            core_claim=paper.title,
            method_one_line="See method sections",
            main_results="See experiments",
            five_cs={
                "category": "systems / inference",
                "context": parent.title,
                "correctness": "unknown until deep read",
                "contributions": "; ".join(d.component for d in deltas) or "TBD",
                "clarity": "unknown",
            },
            worth_deep_read=True,
            verdict="Worth a deep read if the parent idea is familiar.",
        ),
        parent=parent,
        prerequisites=prereqs,
        concepts=concepts,
        glossary={
            "acceptance length": "Average number of drafted tokens accepted per verification step.",
            "KV cache": "Stored key/value tensors from past tokens for efficient attention.",
        },
        diagrams={
            "parent_mermaid": mermaid_parent,
            "paper_mermaid": mermaid_paper,
        },
    )


async def analyze_paper(paper: Paper, *, timeout_s: float = 45.0) -> PaperMap:
    import asyncio

    fallback = fallback_map(paper)

    async def _llm() -> PaperMap:
        prompt = PAPER_MAP_PROMPT.format(
            title=paper.title,
            arxiv_id=paper.arxiv_id or "",
            abstract=paper.abstract[:4000],
            sections_blob=_sections_blob(paper),
            equations_blob=json.dumps([e.model_dump() for e in paper.equations[:20]])[:3000],
            refs_blob="\n".join(r.raw for r in paper.references[:25])[:3000],
        )
        raw = await chat_completion(
            system="Return only valid PaperMap JSON.",
            history=[],
            user_text=prompt,
        )
        data = json.loads(_strip_json(raw))
        paper_map = PaperMap.model_validate(data)
        if not paper_map.concepts:
            return fallback
        if not paper_map.diagrams.get("parent_mermaid"):
            paper_map.diagrams = fallback.diagrams
        if paper_map.parent.title.lower() == "unknown" and fallback.parent.arxiv_id:
            paper_map.parent = fallback.parent
        if len(paper_map.prerequisites) < 3 and fallback.prerequisites:
            names = {p.name.lower() for p in paper_map.prerequisites}
            for p in fallback.prerequisites:
                if p.name.lower() not in names:
                    paper_map.prerequisites.append(p)
        return paper_map

    try:
        paper_map = await asyncio.wait_for(_llm(), timeout=timeout_s)
        save_map(paper.id, paper_map)
        return paper_map
    except Exception:
        logger.exception("paper map LLM failed/timed out; using fallback")
        save_map(paper.id, fallback)
        return fallback


async def generate_cards(
    paper: Paper, paper_map: PaperMap, *, timeout_s: float = 25.0
) -> list[FlashCard]:
    import asyncio

    cards: list[FlashCard] = []

    async def _llm() -> list[FlashCard]:
        prompt = CARDS_PROMPT.format(
            title=paper.title,
            concepts_json=json.dumps([c.model_dump() for c in paper_map.concepts])[:4000],
            pass1_json=paper_map.pass1.model_dump_json(),
            deltas_json=json.dumps([d.model_dump() for d in paper_map.parent.deltas]),
        )
        raw = await chat_completion(
            system="Return only JSON with cards array.",
            history=[],
            user_text=prompt,
        )
        data = json.loads(_strip_json(raw))
        out: list[FlashCard] = []
        for row in data.get("cards") or []:
            out.append(
                FlashCard(
                    id=str(uuid.uuid4()),
                    paper_id=paper.id,
                    concept_id=str(row.get("concept_id") or ""),
                    question=str(row.get("question") or ""),
                    answer=str(row.get("answer") or ""),
                    due_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                )
            )
        return out

    try:
        cards = await asyncio.wait_for(_llm(), timeout=timeout_s)
    except Exception:
        logger.exception("card gen failed/timed out")
    if not cards:
        for c in paper_map.concepts[:8]:
            cards.append(
                FlashCard(
                    id=str(uuid.uuid4()),
                    paper_id=paper.id,
                    concept_id=c.id,
                    question=f"In your own words, what is '{c.title}' doing in this paper?",
                    answer=c.summary or c.title,
                    due_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                )
            )
    return save_cards(paper.id, cards)


def concept_source(paper: Paper, paper_map: PaperMap, concept: Concept) -> str:
    chunks: list[str] = []
    wanted = set(concept.section_ids)
    for s in paper.sections:
        if not wanted or s.id in wanted:
            chunks.append(f"## {s.heading}\n" + "\n".join(s.paragraphs[:4]))
        if sum(len(x) for x in chunks) > 5000:
            break
    for e in paper.equations:
        if not concept.equation_ids or e.id in concept.equation_ids:
            chunks.append(f"Equation {e.id}: $${e.latex}$$\n{e.context}")
    if not chunks:
        chunks.append(paper.abstract)
    return "\n\n".join(chunks)[:7000]


def build_tutor_system(
    paper: Paper,
    paper_map: PaperMap,
    concept: Concept,
    *,
    mode: str,
    notes: str,
) -> str:
    from .prompts import PAPER_BUDDY_SYSTEM

    return PAPER_BUDDY_SYSTEM.format(
        learner_name="Riyaz",
        paper_title=paper.title,
        arxiv_id=paper.arxiv_id or "n/a",
        pass1_json=paper_map.pass1.model_dump_json(),
        parent_json=paper_map.parent.model_dump_json(),
        deltas_json=json.dumps([d.model_dump() for d in paper_map.parent.deltas]),
        prereq_status_json=json.dumps(
            [{"id": p.id, "name": p.name, "status": p.status} for p in paper_map.prerequisites]
        ),
        concepts_list=json.dumps(
            [{"id": c.id, "title": c.title, "state": c.state} for c in paper_map.concepts]
        ),
        current_concept_id=concept.id,
        current_concept_title=concept.title,
        current_concept_source=concept_source(paper, paper_map, concept),
        learner_notes=notes[:2000],
        mode=mode,
    )
