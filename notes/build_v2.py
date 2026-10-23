# -*- coding: utf-8 -*-
"""Fuse Codex structure + Transformer Notebook aesthetic into one notes book."""
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "ml-engineer-interview-notes.html"
def _clean(s: str) -> str:
    return (
        s.replace("\ufeff", "")
        .replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2014", "—")
        .replace("\u2013", "-")
        .replace("\ufffd", "")
    )


def _escape_js_apostrophes(js: str) -> str:
    """Escape English possessives/contractions inside single-quoted JS strings."""
    import re

    return re.sub(r"(?<![\\])([A-Za-z])'([A-Za-z])", r"\1\\'\2", js)


CHAPTERS_JS = _escape_js_apostrophes(
    _clean((ROOT / "_codex_chapters.js").read_text(encoding="utf-8"))
)
DIAGRAMS_JS = _escape_js_apostrophes(
    _clean((ROOT / "_codex_diagrams.js").read_text(encoding="utf-8"))
)

# Extra deep diagrams (Transformer-Notebook style classes: s, fy, t, etc.)
EXPANSIONS_JS = r"""
const expansions = {
'Attention and transformers': `
<p>Walk one head slowly. Token <b>"slept"</b> builds a <em>query</em>. Every token builds a <em>key</em> and a <em>value</em>.
Dot products Q·K give similarity scores. Divide by √d so large dimensions do not explode the softmax.
Softmax turns scores into weights that sum to 1. The output is a weighted sum of values — so "slept" can borrow meaning from "cat".</p>
<p>Worked numbers: scores (0, 2, 1) → softmax ≈ (0.09, 0.67, 0.24). Context ≈ 0.09v₁ + 0.67v₂ + 0.24v₃.</p>
<ul class="hd">
<li><b>Multi-head</b>: several QKV projections in parallel — different relationship patterns.</li>
<li><b>Causal mask</b>: at generation time, no looking at future tokens.</li>
<li><b>GQA / MQA</b>: share K/V across query heads → much smaller KV cache.</li>
</ul>`,
'LoRA: low-rank adapters': `
<p>Think geometrically: full fine-tuning moves every entry of a giant matrix W. Empirically, the <em>useful update</em> for a new task often lives in a thin subspace.
So freeze W₀ and learn ΔW = BA with rank r ≪ d. Trainable count for one d×d layer: <span class="y">2dr</span> instead of d².</p>
<p>Forward: <b>h = W₀x + (α/r) BAx</b>. Initialize B=0 so the model starts unchanged. Typical injection points: attention Q/V projections.
At serve time you can keep adapters hot-swappable or merge BA into W.</p>
<ul class="hd">
<li><b>rank</b> = capacity of the adapter (too small underfits the task).</li>
<li><b>alpha</b> = scales the update strength.</li>
<li>Saves optimizer/grad memory for adapters — base weights still occupy VRAM unless quantized (→ QLoRA).</li>
</ul>`,
'QLoRA: quantized base plus LoRA': `
<p>Memory story: a 7B model at 16-bit is ~14GB of weights alone. At 4-bit ideal storage ~3.5GB before metadata.
QLoRA keeps that base <b>frozen + quantized</b>, and trains small LoRA adapters in higher precision.
Arithmetic usually dequantizes weights on the fly for matmuls — "4-bit model" ≠ "all math is 4-bit".</p>
<ul class="hd">
<li>Say precisely: what is quantized, what is trainable, what precision for compute.</li>
<li>Still need activation memory + adapter grads + optimizer states.</li>
</ul>`,
'Quantization: PTQ, QAT, calibration': `
<p>Quantization snaps continuous values onto a grid: q = round(x/s) + z, then reconstruct x̂ = s(q−z).
Fewer bits → less memory traffic → often faster on supporting hardware, with rounding error.</p>
<ul class="hd">
<li><b>PTQ</b>: after training; calibrate scales on a few batches.</li>
<li><b>QAT</b>: fake-quantize during training so the model adapts to noise.</li>
<li><b>GPTQ / AWQ</b>: strong LLM weight-only methods.</li>
<li>Measure accuracy + latency on the <em>target</em> GPU/CPU — do not assume smaller always means faster.</li>
</ul>`,
'LLM prefill, decode, TTFT, KV cache': `
<p><b>Prefill</b>: process the whole prompt in parallel; write K and V for every layer into a cache.
<b>Decode</b>: for each new token, compute only that token's Q and attend to cached K/V — then append new K/V.</p>
<ul class="hd">
<li><b>TTFT</b> = queue + prefill (time to first token).</li>
<li><b>Tok/s</b> ≈ decode speed under concurrency.</li>
<li>KV memory grows with batch × layers × heads × seq × dim × dtype bytes — why long context is expensive.</li>
<li><b>PagedAttention</b> + continuous batching (vLLM) fix fragmentation and idle GPUs.</li>
</ul>`,
'RAG and vector search': `
<p>Loop: query → (optional rewrite) → embed → ANN search / hybrid BM25 → rerank → pack citations into context → generate → verify grounding.</p>
<ul class="hd">
<li>Chunking decides the unit of truth; bad chunks → bad answers.</li>
<li>HyDE: invent a hypothetical answer doc, embed that, retrieve real docs.</li>
<li>Graph RAG: entities/edges for multi-hop / structured links (RAP-flavored).</li>
<li>Permissions before retrieval. Evaluate retrieval Recall@k separately from answer faithfulness.</li>
</ul>`,
'Agents and tool use': `
<p>Agent = model + tools + loop. <b>Harness</b> = the cage: schemas, max steps, timeouts, validation, logging, human gates.
Prefer a deterministic workflow when the steps are known; open-ended loops need budgets and kill switches.</p>
<ul class="hd">
<li>ReAct: observe → think → act → observe…</li>
<li>MCP: standard tool/resource wiring.</li>
<li>Treat tool output and retrieved text as untrusted (prompt injection).</li>
</ul>`,
'Language models and token prediction': `
<p>The model does not "know facts" as a database. It assigns P(next token | past). Generation is:
<span class="y">predict distribution → sample → append → repeat</span>.
Training maximizes likelihood (cross-entropy on the true next token). Softmax temperature reshapes the distribution at decode time — it is not a training hyperparameter unless you used it that way.</p>`
};
"""

EXTRA_DIAGRAMS = r"""
const extraDiagrams = {
'Attention deep': `<svg class="d" viewBox="0 0 640 320" role="img" aria-label="Query key value attention"><g filter="url(#rough)">
<rect x="20" y="40" width="80" height="50" rx="10" class="s fy"/><text x="60" y="72" class="t tb" text-anchor="middle">Q</text>
<rect x="20" y="130" width="80" height="50" rx="10" class="s fp"/><text x="60" y="162" class="t tb" text-anchor="middle">K</text>
<rect x="20" y="220" width="80" height="50" rx="10" class="s fg"/><text x="60" y="252" class="t tb" text-anchor="middle">V</text>
<line x1="100" y1="65" x2="180" y2="65" class="s sb" marker-end="url(#ahb)"/>
<line x1="100" y1="155" x2="180" y2="155" class="s sr" marker-end="url(#ahr)"/>
<rect x="180" y="40" width="160" height="180" rx="12" class="s fb"/>
<text x="260" y="90" class="t tb" text-anchor="middle">scores</text>
<text x="260" y="120" class="t sm" text-anchor="middle">QKᵀ / √d</text>
<text x="260" y="155" class="t tb" text-anchor="middle">softmax</text>
<text x="260" y="185" class="t sm mu" text-anchor="middle">weights sum to 1</text>
<line x1="340" y1="130" x2="400" y2="130" class="s" marker-end="url(#ah)"/>
<line x1="100" y1="245" x2="400" y2="245" class="s sg dash"/>
<rect x="400" y="100" width="200" height="80" rx="12" class="s fg"/>
<text x="500" y="135" class="t tb" text-anchor="middle">Σ wᵢ Vᵢ</text>
<text x="500" y="160" class="t sm" text-anchor="middle">new token vector</text>
</g></svg>`,
'Predict sample repeat': `<svg class="d" viewBox="0 0 600 280" role="img"><g filter="url(#rough)">
<rect x="20" y="90" width="130" height="60" rx="12" class="s fb"/><text x="85" y="125" class="t tb" text-anchor="middle">text so far</text>
<line x1="150" y1="120" x2="200" y2="120" class="s" marker-end="url(#ah)"/>
<rect x="200" y="90" width="150" height="60" rx="12" class="s fg"/><text x="275" y="125" class="t tb" text-anchor="middle">TRANSFORMER</text>
<line x1="350" y1="120" x2="400" y2="120" class="s" marker-end="url(#ah)"/>
<rect x="400" y="60" width="160" height="100" rx="12" class="s"/>
<rect x="420" y="100" width="16" height="48" class="s cell fy"/><rect x="445" y="120" width="16" height="28" class="s cell fy"/><rect x="470" y="132" width="16" height="16" class="s cell fy"/><rect x="495" y="140" width="16" height="8" class="s cell fy"/>
<text x="480" y="85" class="t sm" text-anchor="middle">probs</text>
<line x1="480" y1="160" x2="480" y2="195" class="s" marker-end="url(#ah)"/>
<rect x="400" y="195" width="160" height="45" rx="10" class="s fp"/><text x="480" y="223" class="t tb" text-anchor="middle">sample ONE</text>
<path d="M400 217 L85 217 L85 150" class="s sr" marker-end="url(#ahr)"/>
<text x="200" y="250" class="t r">append + repeat</text>
</g></svg>`,
'LoRA geometry': `<svg class="d" viewBox="0 0 620 200" role="img"><g filter="url(#rough)">
<rect x="30" y="40" width="130" height="120" rx="10" class="s fb"/><text x="95" y="105" class="t tb" text-anchor="middle">W₀</text><text x="95" y="128" class="t sm mu" text-anchor="middle">frozen</text>
<text x="180" y="105" class="t xl">+</text>
<rect x="220" y="30" width="50" height="140" rx="8" class="s fy"/><text x="245" y="105" class="t tb" text-anchor="middle">B</text>
<text x="290" y="105" class="t xl">×</text>
<rect x="320" y="70" width="140" height="50" rx="8" class="s fy"/><text x="390" y="102" class="t tb" text-anchor="middle">A</text>
<text x="490" y="90" class="t">→ ΔW = BA</text>
<text x="490" y="115" class="t sm r">rank r ≪ d</text>
<text x="30" y="185" class="t sm mu">h = W₀x + (α/r) B A x</text>
</g></svg>`,
'KV cache growth': `<svg class="d" viewBox="0 0 640 180" role="img"><g filter="url(#rough)">
<rect x="20" y="40" width="200" height="80" rx="10" class="s fb"/><text x="120" y="75" class="t tb" text-anchor="middle">prefill prompt</text><text x="120" y="100" class="t sm" text-anchor="middle">build full KV</text>
<line x1="220" y1="80" x2="270" y2="80" class="s" marker-end="url(#ah)"/>
<rect x="270" y="30" width="70" height="100" rx="8" class="s fg"/><text x="305" y="85" class="t" text-anchor="middle">t1</text>
<rect x="350" y="30" width="70" height="100" rx="8" class="s fg"/><text x="385" y="85" class="t" text-anchor="middle">t2</text>
<rect x="430" y="30" width="70" height="100" rx="8" class="s fg"/><text x="465" y="85" class="t" text-anchor="middle">t3</text>
<rect x="510" y="30" width="100" height="100" rx="8" class="s fy"/><text x="560" y="75" class="t tb" text-anchor="middle">KV</text><text x="560" y="100" class="t sm" text-anchor="middle">grows</text>
<text x="20" y="160" class="t sm mu">decode appends one token; reuse past K,V — memory ∝ seq length</text>
</g></svg>`
};
"""

HTML_HEAD = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<title>ML Engineer Interview Notebook</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;700&family=Courier+Prime:wght@400;700&family=Kalam:wght@300;400;700&display=swap"/>
<style>
:root{
  --desk:#dfe6f2; --paper:#fbfcff; --line:#d3e1f6; --margin:#ee9aa0;
  --ink:#1b2866; --ink-soft:#4b5693; --red:#c4303b; --blue:#1d5fcf; --green:#16764a;
  --hl-y:rgba(255,222,40,.6); --hl-p:rgba(255,130,185,.4); --hl-g:rgba(90,215,150,.45); --hl-b:rgba(110,170,255,.38);
  --wt:#a3c1f6; --data:#ccd1de; --sticky:#fff1a0; --sticky-ink:#4a3a00; --shadow:rgba(28,40,100,.22);
  --f-hand:"Kalam","Comic Sans MS","Segoe Print",cursive; --f-pen:"Caveat","Segoe Script",cursive; --f-mono:"Courier Prime","Courier New",monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --desk:#0e1220; --paper:#1b2136; --line:#2a3452; --margin:#8e4552;
  --ink:#dfe7ff; --ink-soft:#a5b3e8; --red:#ff8089; --blue:#82b3ff; --green:#62d89c;
  --hl-y:rgba(255,212,10,.3); --hl-p:rgba(255,120,180,.3); --hl-g:rgba(90,220,150,.28); --hl-b:rgba(110,170,255,.3);
  --wt:#3b62b6; --data:#505b79; --sticky:#4a4118; --sticky-ink:#ffeba3; --shadow:rgba(0,0,0,.5); color-scheme:dark}}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--desk);color:var(--ink);font-family:var(--f-hand);font-size:17px;line-height:30px;margin:0;padding:0 16px 64px}
.wrap{max-width:920px;margin:0 auto;display:flex;flex-direction:column;gap:36px;padding-top:18px}
.tabs{position:sticky;top:0;z-index:30;background:var(--desk);margin:0 -16px;padding:8px 16px;display:flex;gap:6px;overflow-x:auto;box-shadow:0 6px 10px -8px var(--shadow)}
.tabs a,.tabs button{flex:none;font-family:var(--f-pen);font-size:20px;line-height:26px;font-weight:700;color:var(--ink);text-decoration:none;padding:2px 10px;border:2px solid var(--ink-soft);border-radius:12px 8px 14px 6px;background:var(--paper);cursor:pointer}
.tabs a:hover,.tabs a.active{background:var(--hl-y)}
.searchrow{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.searchrow input{flex:1;min-width:180px;font-family:var(--f-hand);font-size:16px;padding:6px 12px;border:2px solid var(--ink-soft);border-radius:10px;background:var(--paper);color:var(--ink)}
.prog{font-family:var(--f-pen);font-size:18px;color:var(--ink-soft)}
.page{position:relative;scroll-margin-top:64px;background-color:var(--paper);background-image:repeating-linear-gradient(to bottom,transparent 0 29px,var(--line) 29px 30px);border-radius:6px;box-shadow:0 1px 0 var(--shadow),0 14px 30px -14px var(--shadow);padding:30px 26px 30px 82px}
.page::before{content:"";position:absolute;left:60px;top:0;bottom:0;width:2px;background:var(--margin);box-shadow:4px 0 0 var(--margin)}
.page::after{content:"";position:absolute;left:12px;top:0;bottom:0;width:26px;background-image:radial-gradient(circle at 50% 50%,var(--desk) 0 8px,transparent 9px);background-size:26px 90px;background-position:0 30px}
.page>*{margin:0;min-width:0}.page>*+*{margin-top:24px}
.pg-head{display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap}
h1,h2,h3{font-family:var(--f-pen);color:var(--ink);margin:0;font-weight:700;text-wrap:balance}
h1{font-size:48px;line-height:52px} h2{font-size:38px;line-height:44px}
h3{font-size:28px;line-height:32px;color:var(--blue);text-decoration:underline wavy var(--red);text-decoration-thickness:1.5px;text-underline-offset:6px;width:fit-content;max-width:100%}
.pgno{font-family:var(--f-pen);font-size:22px;color:var(--ink-soft)}
.sub{font-family:var(--f-pen);font-size:24px;color:var(--ink-soft);line-height:30px}
b{color:var(--red);font-weight:700}
em{font-style:normal;color:var(--blue);font-weight:700;border-bottom:2px dotted var(--blue)}
.gr{color:var(--green);font-weight:700}
.y{background:linear-gradient(transparent 36%,var(--hl-y) 36% 94%,transparent 94%);padding:0 3px;border-radius:3px}
.pk{background:linear-gradient(transparent 36%,var(--hl-p) 36% 94%,transparent 94%);padding:0 3px}
.mn{background:linear-gradient(transparent 36%,var(--hl-g) 36% 94%,transparent 94%);padding:0 3px}
ul.hd{list-style:none;padding:0} ul.hd>li{position:relative;padding-left:30px}
ul.hd>li::before{content:"→";position:absolute;left:2px;color:var(--red);font-family:var(--f-pen);font-size:26px;font-weight:700}
.box{border:2px solid var(--ink);border-radius:255px 18px 225px 18px/18px 225px 18px 255px;padding:13px 22px;background:var(--paper)}
.box.red{border-color:var(--red)} .box.blue{border-color:var(--blue)} .box.green{border-color:var(--green)}
.box .tag{font-family:var(--f-pen);font-weight:700;font-size:22px;color:var(--red)}
.box.blue .tag{color:var(--blue)} .box.green .tag{color:var(--green)}
.sticky{position:relative;background:var(--sticky);color:var(--sticky-ink);padding:15px 20px;box-shadow:0 8px 14px -8px var(--shadow);transform:rotate(-.6deg)}
.sticky::before{content:"";position:absolute;top:-10px;left:50%;width:84px;height:20px;margin-left:-42px;background:var(--hl-p);transform:rotate(2deg)}
.eq{font-family:var(--f-mono);font-size:17px;text-align:center;border:2px solid var(--blue);border-radius:255px 18px 225px 18px/18px 225px 18px 255px;padding:12px 14px;overflow-x:auto;background:var(--paper)}
.fig{background:var(--paper);border:1.5px dashed var(--line);border-radius:10px;overflow-x:auto;display:flex;align-items:center}
svg.d{display:block;width:100%;height:auto;min-width:520px;flex:none}
svg .t{font-family:var(--f-pen);font-weight:500;font-size:20px;fill:var(--ink)}
svg .tb{font-weight:700} svg .sm{font-size:15px} svg .lg{font-size:24px} svg .xl{font-size:32px;font-weight:700}
svg .r{fill:var(--red)} svg .bl{fill:var(--blue)} svg .g{fill:var(--green)} svg .mu{fill:var(--ink-soft)}
svg .s{fill:none;stroke:var(--ink);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
svg .sr{stroke:var(--red)} svg .sb{stroke:var(--blue)} svg .sg{stroke:var(--green)}
svg .fy{fill:var(--hl-y)} svg .fp{fill:var(--hl-p)} svg .fg{fill:var(--hl-g)} svg .fb{fill:var(--hl-b)} svg .fw{fill:var(--wt)} svg .fd{fill:var(--data)} svg .fr{fill:var(--red)}
svg .dash{stroke-dasharray:7 6} svg .thin{stroke-width:1;opacity:.5} svg .cell{stroke-width:1.4}
svg .mk{fill:none;stroke:var(--ink);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
svg .mkr{stroke:var(--red)} svg .mkb{stroke:var(--blue)} svg .mkg{stroke:var(--green)}
.topic{border-bottom:1px dashed var(--ink-soft);padding-bottom:18px}
.topic summary{cursor:pointer;list-style:none;font-family:var(--f-pen);font-weight:700;font-size:26px;color:var(--blue);position:relative;padding-left:28px}
.topic summary::-webkit-details-marker{display:none}
.topic summary::before{content:"▸";position:absolute;left:0;color:var(--red)}
.topic[open] summary::before{content:"▾"}
.badge{display:inline-block;font-family:var(--f-pen);font-size:16px;padding:0 8px;border:1.5px solid var(--red);border-radius:8px;color:var(--red);margin-left:8px;vertical-align:middle}
.badge.post{border-color:var(--green);color:var(--green)}
.label{font-family:var(--f-pen);font-size:20px;color:var(--red);font-weight:700;margin-top:12px}
.interview{border-left:3px solid var(--green);padding:8px 12px;background:color-mix(in srgb, var(--hl-g) 35%, transparent);margin-top:10px}
.widget{border:2px solid var(--green);border-radius:255px 18px 225px 18px/18px 225px 18px 255px;padding:13px 22px;background:var(--paper)}
.widget .wtop{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.widget input[type=range]{flex:1 1 180px;accent-color:var(--red)}
.brow{display:grid;grid-template-columns:110px 1fr 56px;gap:10px;align-items:center}
.brow .tok{font-family:var(--f-pen);font-size:20px;font-weight:700}
.brow .trk{height:16px;border-radius:8px;background:var(--line);overflow:hidden}
.brow .fill{height:100%;background:var(--hl-y);border-right:2px solid var(--red);min-width:2px}
.brow .pc{font-family:var(--f-mono);font-size:14px;text-align:right}
.mark{font-family:var(--f-pen);font-size:18px;border:2px solid var(--ink);background:var(--paper);border-radius:10px;padding:2px 12px;cursor:pointer;color:var(--ink)}
.mark.done{background:var(--hl-g);border-color:var(--green)}
.foot{display:flex;justify-content:space-between;gap:10px;font-family:var(--f-pen);font-size:20px;color:var(--ink-soft)}
.foot a{color:var(--blue);font-weight:700}
.hidden{display:none!important}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:0 28px}
.num{font-family:var(--f-pen);font-size:28px;color:var(--blue);font-weight:700}
details.qa{border-bottom:1px dashed var(--ink-soft)}
details.qa summary{cursor:pointer;font-family:var(--f-pen);font-weight:700;font-size:22px;color:var(--blue);list-style:none;padding-left:26px;position:relative}
details.qa summary::-webkit-details-marker{display:none}
details.qa summary::before{content:"?";position:absolute;left:2px;color:var(--red)}
details.qa[open] summary::before{content:"✓";color:var(--green)}
@media (max-width:600px){
  .page{padding:24px 12px 24px 46px}
  .page::before{left:34px}
  h1{font-size:36px} h2{font-size:30px}
}
</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<filter id="rough" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="4" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="2.4"/></filter>
<marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1 L9 5 L1 9" class="mk"/></marker>
<marker id="ahr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1 L9 5 L1 9" class="mk mkr"/></marker>
<marker id="ahb" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1 L9 5 L1 9" class="mk mkb"/></marker>
<marker id="ahg" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1 L9 5 L1 9" class="mk mkg"/></marker>
</defs></svg>

<nav class="tabs" id="tabs" aria-label="Chapters"></nav>
<div class="wrap">
<section class="page" id="cover">
<div class="pg-head"><h1>ML Engineer Interview Notebook</h1><span class="pgno">cover</span></div>
<p class="sub">Handwritten field notes · Codex structure · Transformer-Notebook diagrams &amp; labs</p>
<div class="box red"><span class="tag">How to use</span><br>
Work <b>in order</b> once. Open each card: read intuition → math → diagram → say the green interview line aloud.
Mark studied. Use the <span class="y">labs</span> (temperature, LoRA, quant) until the numbers feel obvious.
Post-training chapters (LoRA, QLoRA, quant, KV, RAG, agents) are marked <em>after training</em> — RAP loves these.</div>
<div class="searchrow">
<input id="q" type="search" placeholder="Search any concept…"/>
<span class="prog" id="prog">0 studied</span>
</div>
<div class="sticky"><b>Pen code:</b> <b>red</b> = key term · <em>blue</em> = idea · <span class="gr">green</span> = interview · <span class="y">yellow</span> = memorize</div>
<div class="cols">
<ul class="hd">
<li>Ch 0–2 foundations &amp; data</li>
<li>Ch 3–5 classical ML &amp; eval</li>
<li>Ch 6–7 neural nets &amp; architectures</li>
</ul>
<ul class="hd">
<li>Ch 8 RAG &amp; agents</li>
<li>Ch 9–10 ★ after training + inference</li>
<li>Ch 11–12 MLOps &amp; system design</li>
</ul>
</div>
<div class="foot"><span>sources: RAP topic list · Codex field notes · 3Blue1Brown-style transformer notebook</span><a href="#c00">start →</a></div>
</section>

<section class="page" id="xform">
<div class="pg-head"><h2>Transformer foundations (deep)</h2><span class="pgno">xform</span></div>
<p class="sub">From the interactive Transformer Notebook style — predict, sample, repeat · embeddings · softmax</p>
<div class="box red"><span class="tag">One breath</span><br>
A transformer chops text into <b>tokens</b>, turns each into a <b>vector</b>, lets vectors share info (<em>attention</em>) and think alone (<em>MLP</em>) many times, then turns the <span class="y">last vector</span> into a <b>probability distribution</b> over the next token. Sample one, append, repeat.</div>
<h3>Predict → sample → repeat</h3>
<figure class="fig"><svg class="d" viewBox="0 0 600 280" role="img"><g filter="url(#rough)">
<rect x="20" y="90" width="130" height="60" rx="12" class="s fb"/><text x="85" y="125" class="t tb" text-anchor="middle">text so far</text>
<line x1="150" y1="120" x2="200" y2="120" class="s" marker-end="url(#ah)"/>
<rect x="200" y="90" width="150" height="60" rx="12" class="s fg"/><text x="275" y="125" class="t tb" text-anchor="middle">TRANSFORMER</text>
<line x1="350" y1="120" x2="400" y2="120" class="s" marker-end="url(#ah)"/>
<rect x="400" y="60" width="160" height="100" rx="12" class="s"/>
<rect x="420" y="100" width="16" height="48" class="s cell fy"/><rect x="445" y="120" width="16" height="28" class="s cell fy"/><rect x="470" y="132" width="16" height="16" class="s cell fy"/>
<text x="480" y="85" class="t sm" text-anchor="middle">probabilities</text>
<line x1="480" y1="160" x2="480" y2="195" class="s" marker-end="url(#ah)"/>
<rect x="400" y="195" width="160" height="45" rx="10" class="s fp"/><text x="480" y="223" class="t tb" text-anchor="middle">sample ONE</text>
<path d="M400 217 L85 217 L85 150" class="s sr" marker-end="url(#ahr)"/>
<text x="200" y="250" class="t r">append + repeat</text>
</g></svg></figure>
<ol>
<li>Seed text in.</li>
<li>Model outputs a full distribution — not one word.</li>
<li>Sample (not always argmax).</li>
<li>Append; run again on the longer text.</li>
</ol>
<h3>Embeddings = directions with meaning</h3>
<p>Each token becomes a high-dimensional point via matrix <b>W<sub>E</sub></b>. Nearby directions ≈ related meaning. Dot product measures alignment (attention is built from this). Unembedding <b>W<sub>U</sub></b> turns the last vector into one logit per vocab entry, then softmax.</p>
<div class="eq">text → tokens → W<sub>E</sub> → vectors → [attention + MLP]×N → last vector → W<sub>U</sub> → logits → softmax(T) → sample</div>
<div class="sticky"><b>Study move:</b> cover this page and redraw the loop from memory. Then open Labs and drive temperature until you can predict the bars.</div>
<div class="foot"><a href="#cover">↑ cover</a><a href="#c00">ch 00 →</a></div>
</section>

<div id="book"></div>

<section class="page" id="labs">
<div class="pg-head"><h2>Interactive labs</h2><span class="pgno">labs</span></div>
<p class="sub">Move sliders. Predict. Check. This is how temperature / LoRA / bits become muscle memory.</p>

<h3>1 · Softmax temperature</h3>
<p>Logits for next-token candidates (toy): princess 3.2, little 2.9, king 2.1, dragon 1.4, web-artist −0.5.</p>
<div class="eq">softmax<sub>T</sub>(x<sub>i</sub>) = e<sup>x<sub>i</sub>/T</sup> / Σ<sub>j</sub> e<sup>x<sub>j</sub>/T</sup></div>
<div class="widget" id="wtemp">
<div class="wtop"><label>temperature T = <b id="tval">1.00</b></label><input type="range" id="temp" min="0" max="5" step="0.05" value="1"/></div>
<div id="tbars"></div>
<p class="sub" id="tnote"></p>
</div>
<div class="box blue"><span class="tag">Interview line</span><br>
Low T ≈ greedy / factual. High T ≈ creative then nonsense. T→0 puts all mass on the max logit.</div>

<h3>2 · Quantization memory (weights only)</h3>
<div class="widget">
<div class="wtop"><label>params <b id="paramv">7</b>B</label><input type="range" id="param" min="1" max="70" value="7"/></div>
<div class="wtop"><label>bits <b id="bitsv">4</b></label><input type="range" id="bits" min="4" max="16" step="4" value="4"/></div>
<p class="num" id="wmem">—</p>
<p class="sub">GB ≈ params_B × bits / 8. Ignores KV cache, activations, metadata.</p>
</div>

<h3>3 · LoRA trainable fraction (one square layer)</h3>
<div class="widget">
<div class="wtop"><label>d = <b id="dimv">4096</b></label><input type="range" id="dim" min="512" max="8192" step="512" value="4096"/></div>
<div class="wtop"><label>rank r = <b id="rankv">16</b></label><input type="range" id="rank" min="1" max="128" value="16"/></div>
<p class="num" id="loraout">—</p>
<div class="eq">full = d² &nbsp;|&nbsp; LoRA = 2dr &nbsp;|&nbsp; fraction = 2r/d</div>
</div>
<figure class="fig" id="lorafig"></figure>

<h3>4 · Precision vs recall</h3>
<div class="widget">
<div class="wtop"><label>TP <b id="tpv">70</b></label><input type="range" id="tp" min="0" max="100" value="70"/></div>
<div class="wtop"><label>FP <b id="fpv">20</b></label><input type="range" id="fp" min="0" max="100" value="20"/></div>
<div class="wtop"><label>FN <b id="fnv">30</b></label><input type="range" id="fn" min="0" max="100" value="30"/></div>
<p class="num" id="pr">—</p>
</div>

<div class="foot"><a href="#cover">↑ cover</a><a href="#drill">drills →</a></div>
</section>

<section class="page" id="drill">
<div class="pg-head"><h2>Say-aloud drills</h2><span class="pgno">drill</span></div>
<div id="quizzes"></div>
<div class="foot"><a href="#labs">↑ labs</a><span>end ✓</span></div>
</section>
</div>

<script>
'''

HTML_TAIL = r'''
const book = document.getElementById('book');
const tabs = document.getElementById('tabs');
const saved = new Set(JSON.parse(localStorage.getItem('mlnb-studied')||'[]'));
let total = 0;

// merge extra diagrams
Object.assign(diagrams, typeof extraDiagrams !== 'undefined' ? extraDiagrams : {});
diagrams['Attention and transformers'] = diagrams['Attention deep'] || diagrams['Attention and transformers'];
diagrams['LoRA: low-rank adapters'] = diagrams['LoRA geometry'] || diagrams['LoRA: low-rank adapters'];
diagrams['LLM prefill, decode, TTFT, KV cache'] = diagrams['KV cache growth'] || diagrams['LLM prefill, decode, TTFT, KV cache'];
diagrams['Language models and token prediction'] = diagrams['Predict sample repeat'] || diagrams['Language models and token prediction'];

function esc(s){return String(s).replace(/[&<>]/g,c=>({ '&':'&amp;','<':'&lt;','>':'&gt;' }[c]));}

tabs.innerHTML = '<a href="#cover" class="active">Cover</a><a href="#xform">Transformers</a>' +
  chapters.map(ch => `<a href="#c${ch.n}">${ch.n}</a>`).join('') +
  '<a href="#labs">Labs</a><a href="#drill">Drills</a>';

chapters.forEach((ch, ci) => {
  const page = document.createElement('section');
  page.className = 'page';
  page.id = 'c' + ch.n;
  page.innerHTML = `<div class="pg-head"><h2>${esc(ch.n)}. ${esc(ch.title)}</h2><span class="pgno">ch ${ch.n}</span></div>
    <p class="sub">${esc(ch.lead)}</p>`;
  ch.topics.forEach((t, ti) => {
    const [name, tag, intuition, math, inside, trade, question] = t;
    const id = `t-${ch.n}-${ti}`;
    total++;
    const dig = diagrams[name] ? `<figure class="fig">${diagrams[name]}</figure>` : '';
    const det = document.createElement('details');
    det.className = 'topic';
    det.dataset.text = t.join(' ').toLowerCase();
    det.id = id;
    if (ci === 0 && ti === 0) det.open = true;
    det.innerHTML = `<summary>${esc(name)}<span class="badge ${tag==='post'?'post':''}">${tag==='post'?'after training':'foundation'}</span></summary>
      <div class="label">Intuition</div><p>${intuition}</p>
      <div class="label">Math / geometry</div><div class="eq">${math}</div>
      <div class="label">Inside the machine</div><p>${inside}</p>
      ${expansions[name]||''}
      ${dig}
      <div class="label">Trade-off to defend</div><p>${trade}</p>
      <div class="interview"><strong>Interview — say aloud:</strong> ${question}</div>
      <p style="margin-top:12px"><button type="button" class="mark ${saved.has(id)?'done':''}" data-id="${id}">${saved.has(id)?'✓ Studied':'Mark studied'}</button></p>`;
    page.appendChild(det);
  });
  const next = chapters[ci+1];
  const foot = document.createElement('div');
  foot.className = 'foot';
  foot.innerHTML = `<a href="#${ci?('c'+chapters[ci-1].n):'cover'}">↑ prev</a><a href="#${next?('c'+next.n):'labs'}">next →</a>`;
  page.appendChild(foot);
  book.appendChild(page);
});

function prog(){
  document.getElementById('prog').textContent = `${saved.size} / ${total} studied`;
}
prog();

document.addEventListener('click', e => {
  if (e.target.classList.contains('mark')) {
    const id = e.target.dataset.id;
    if (saved.has(id)) saved.delete(id); else saved.add(id);
    localStorage.setItem('mlnb-studied', JSON.stringify([...saved]));
    e.target.classList.toggle('done', saved.has(id));
    e.target.textContent = saved.has(id) ? '✓ Studied' : 'Mark studied';
    prog();
  }
});

document.getElementById('q').addEventListener('input', e => {
  const q = e.target.value.trim().toLowerCase();
  document.querySelectorAll('.topic').forEach(t => {
    const ok = !q || t.dataset.text.includes(q);
    t.classList.toggle('hidden', !ok);
    if (q && ok) t.open = true;
  });
  document.querySelectorAll('.page[id^="c"]').forEach(p => {
    const vis = [...p.querySelectorAll('.topic')].some(t => !t.classList.contains('hidden'));
    p.classList.toggle('hidden', q && !vis);
  });
});

// drills
const drills = [
['Why isn’t a random forest a whole recommender?','Need candidate generation first, then rank, then diversity/policy. The forest is only the ranker over a few hundred pairs.'],
['LoRA vs QLoRA vs quantization in 30s','LoRA: freeze W, train low-rank BA. QLoRA: same adapters but frozen base stored 4-bit. Quantization: fewer bits for weights/activations to save memory/speed — measure accuracy on hardware.'],
['First thing in system design?','Who decides what, at what timestamp, with what data available then. Then baseline + metrics.'],
['Prefill vs decode','Prefill: parallel over prompt, build KV. Decode: one token at a time using cache. TTFT vs tok/s.'],
['RAG vs fine-tune','Fresh/private facts → RAG. Style/format/behavior → FT/LoRA. Often combine. Diagnose the error type first.'],
['Attention in one breath','softmax(QKᵀ/√d)V — soft weighted mix of values by query–key similarity.']
];
document.getElementById('quizzes').innerHTML = drills.map(([q,a],i) =>
  `<details class="qa"><summary>${i+1}. ${esc(q)}</summary><p>${esc(a)}</p></details>`
).join('');

// labs
(function(){
  const toks=["princess","little","king","dragon","web artist"], z=[3.2,2.9,2.1,1.4,-0.5];
  const rng=document.getElementById('temp'), out=document.getElementById('tval'), box=document.getElementById('tbars'), note=document.getElementById('tnote');
  function soft(T){
    const m=Math.max(...z);
    if(T<0.02) return z.map(v => v===m?1:0);
    const e=z.map(v => Math.exp((v-m)/T));
    const s=e.reduce((p,c)=>p+c,0);
    return e.map(v => v/s);
  }
  function drawT(){
    const T=+rng.value; const p=soft(T);
    out.textContent=T.toFixed(2);
    box.innerHTML=toks.map((t,i)=>`<div class="brow"><span class="tok">${t}</span><div class="trk"><div class="fill" style="width:${(p[i]*100).toFixed(1)}%"></div></div><span class="pc">${(p[i]*100).toFixed(1)}%</span></div>`).join('');
    note.textContent = T<0.02?'T≈0: always the top token.':T<0.7?'Low T: leader dominates (factual/code).':T<1.4?'Near 1: model’s own distribution.':T<2.5?'High T: flatter, riskier.':'Very high T: near random.';
  }
  rng.addEventListener('input', drawT); drawT();

  function lab(){
    const p=+document.getElementById('param').value, b=+document.getElementById('bits').value;
    const d=+document.getElementById('dim').value, r=+document.getElementById('rank').value;
    const tp=+document.getElementById('tp').value, fp=+document.getElementById('fp').value, fn=+document.getElementById('fn').value;
    document.getElementById('paramv').textContent=p;
    document.getElementById('bitsv').textContent=b;
    document.getElementById('wmem').textContent=(p*b/8).toFixed(2)+' GB approx. weights';
    document.getElementById('dimv').textContent=d;
    document.getElementById('rankv').textContent=r;
    document.getElementById('loraout').textContent=(100*2*d*r/(d*d)).toFixed(2)+'% trainable on this layer';
    document.getElementById('lorafig').innerHTML = diagrams['LoRA geometry'] || diagrams['LoRA: low-rank adapters'] || '';
    document.getElementById('tpv').textContent=tp; document.getElementById('fpv').textContent=fp; document.getElementById('fnv').textContent=fn;
    const P=tp/(tp+fp)||0, R=tp/(tp+fn)||0;
    document.getElementById('pr').textContent=`Precision ${(P*100).toFixed(0)}% · Recall ${(R*100).toFixed(0)}% · F1 ${((2*P*R)/((P+R)||1)*100).toFixed(0)}%`;
  }
  document.querySelectorAll('#labs input').forEach(x => x.addEventListener('input', lab));
  lab();
})();

// active tab highlight
const tabLinks=[...tabs.querySelectorAll('a')];
const obs=new IntersectionObserver(ents=>{
  ents.forEach(en=>{
    if(!en.isIntersecting) return;
    tabLinks.forEach(a=>a.classList.toggle('active', a.getAttribute('href')==='#'+en.target.id));
  });
},{rootMargin:'-30% 0px -60% 0px'});
['cover','xform',...chapters.map(c=>'c'+c.n),'labs','drill'].forEach(id=>{
  const el=document.getElementById(id); if(el) obs.observe(el);
});
</script>
</body></html>
'''

def main():
    chapters = CHAPTERS_JS.rstrip().rstrip(";")
    diagrams = DIAGRAMS_JS.rstrip().rstrip(";")
    html = (
        HTML_HEAD
        + "\n"
        + chapters
        + ";\n"
        + diagrams
        + ";\n"
        + EXPANSIONS_JS
        + "\n"
        + EXTRA_DIAGRAMS
        + "\n"
        + HTML_TAIL
    )
    OUT.write_text(html, encoding="utf-8")
    # sanity: chapters must parse as JS assignment when const→name
    import re

    start = html.index("const chapters=")
    end = html.index(";\nconst diagrams=", start)
    chunk = html[start:end]
    assert "];;" not in html[start : end + 5]
    assert not re.search(r"(?<![\\])([A-Za-z])'([A-Za-z])", chunk), "unescaped apostrophe"
    print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
