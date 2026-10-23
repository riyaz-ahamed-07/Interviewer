# -*- coding: utf-8 -*-
"""Build self-contained interactive ML interview notes HTML."""
from pathlib import Path

OUT = Path(__file__).parent / "ml-engineer-interview-notes.html"

HEAD = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>ML Engineer Interview Notes — Handwritten Book</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;600;700&family=Kalam:wght@300;400;700&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&display=swap" rel="stylesheet" />
<style>
:root {
  --paper: #f4efe4;
  --paper2: #ebe4d4;
  --ink: #1c1914;
  --ink-soft: #3d3830;
  --blue: #1a4f8c;
  --red: #a83228;
  --green: #2a5c3a;
  --fade: #8a8274;
  --rule: rgba(28,25,20,.08);
  --shadow: rgba(40,30,10,.12);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background:
    radial-gradient(ellipse at 20% 0%, #ddd4c0 0%, transparent 50%),
    radial-gradient(ellipse at 90% 40%, #d6cbb5 0%, transparent 40%),
    #cfc5b0;
  color: var(--ink);
  font-family: "Literata", Georgia, serif;
  font-size: 1.05rem;
  line-height: 1.65;
}
.desk {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 0;
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
}
@media (max-width: 900px) {
  .desk { grid-template-columns: 1fr; }
  .toc { position: static !important; max-height: none !important; border-right: none; }
}
.toc {
  position: sticky;
  top: 0;
  align-self: start;
  max-height: 100vh;
  overflow: auto;
  padding: 1.25rem 1rem 2rem;
  background: color-mix(in srgb, var(--paper2) 92%, #000 2%);
  border-right: 1px solid var(--rule);
  font-family: "Kalam", cursive;
}
.toc h1 {
  font-family: "Caveat", cursive;
  font-size: 1.9rem;
  margin: 0 0 .25rem;
  color: var(--blue);
  line-height: 1.1;
}
.toc .sub { font-size: .85rem; color: var(--fade); margin-bottom: 1rem; }
.toc input {
  width: 100%;
  padding: .45rem .6rem;
  border: 1.5px solid #b8ae9a;
  background: var(--paper);
  font-family: "Kalam", cursive;
  margin-bottom: .75rem;
}
.toc nav a {
  display: block;
  text-decoration: none;
  color: var(--ink-soft);
  padding: .2rem 0 .2rem .4rem;
  border-left: 2px solid transparent;
  font-size: .92rem;
  line-height: 1.3;
}
.toc nav a:hover, .toc nav a.active {
  border-left-color: var(--red);
  color: var(--red);
}
.toc nav .ch { font-weight: 700; margin-top: .65rem; color: var(--ink); }
.toc nav .sec { padding-left: 1rem; font-size: .86rem; }
.book {
  padding: 1.5rem 1.25rem 4rem;
}
.sheet {
  background:
    linear-gradient(90deg, transparent 0, transparent 2.2rem, rgba(200,80,80,.15) 2.2rem, rgba(200,80,80,.15) 2.28rem, transparent 2.28rem),
    var(--paper);
  box-shadow: 0 12px 40px var(--shadow), 0 1px 0 #fff inset;
  border: 1px solid #d4c9b4;
  padding: 1.75rem 1.75rem 1.75rem 2.75rem;
  margin-bottom: 1.5rem;
  position: relative;
  transform: rotate(var(--tilt, 0deg));
}
.sheet::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  opacity: .5;
  mix-blend-mode: multiply;
}
.sheet h2 {
  font-family: "Caveat", cursive;
  font-size: 2.4rem;
  margin: 0 0 .5rem;
  color: var(--blue);
  font-weight: 700;
}
.sheet h3 {
  font-family: "Caveat", cursive;
  font-size: 1.65rem;
  margin: 1.4rem 0 .4rem;
  color: var(--red);
}
.sheet h4 {
  font-family: "Kalam", cursive;
  font-size: 1.15rem;
  margin: 1rem 0 .3rem;
  color: var(--green);
}
.lead { font-family: "Kalam", cursive; font-size: 1.15rem; color: var(--ink-soft); }
.margin-note {
  float: right;
  width: 11rem;
  margin: 0 0 1rem 1rem;
  padding: .5rem .65rem;
  border: 1.5px dashed var(--blue);
  font-family: "Caveat", cursive;
  font-size: 1.15rem;
  color: var(--blue);
  transform: rotate(2deg);
  background: color-mix(in srgb, var(--paper) 80%, #cde);
}
.ink-red { color: var(--red); }
.ink-blue { color: var(--blue); }
.formula {
  display: block;
  margin: .85rem 0;
  padding: .75rem 1rem;
  background: #fffaf0;
  border-left: 3px solid var(--blue);
  font-family: "Literata", serif;
  overflow-x: auto;
}
.card {
  border: 1.5px solid #c9bfaa;
  background: #fffdf8;
  padding: .85rem 1rem;
  margin: .75rem 0;
}
.card summary {
  font-family: "Kalam", cursive;
  font-weight: 700;
  cursor: pointer;
  color: var(--ink);
}
.ask {
  margin: .75rem 0;
  padding: .6rem .8rem;
  background: color-mix(in srgb, #a83228 8%, var(--paper));
  border-left: 3px solid var(--red);
  font-family: "Kalam", cursive;
}
.ask::before { content: "Interview ask → "; color: var(--red); font-weight: 700; }
.diagram {
  margin: 1rem 0;
  padding: .75rem;
  background: #fff;
  border: 1px solid #d0c6b2;
  overflow-x: auto;
}
.diagram svg { display: block; margin: 0 auto; max-width: 100%; height: auto; }
.diagram figcaption {
  font-family: "Caveat", cursive;
  font-size: 1.2rem;
  text-align: center;
  color: var(--fade);
  margin-top: .35rem;
}
ul.tight li { margin: .25rem 0; }
.tag {
  display: inline-block;
  font-family: "Kalam", cursive;
  font-size: .8rem;
  padding: .1rem .45rem;
  border: 1px solid var(--fade);
  color: var(--fade);
  margin-right: .25rem;
}
.hidden { display: none !important; }
.progress {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  height: 4px;
  background: transparent;
  z-index: 20;
}
.progress > i {
  display: block;
  height: 100%;
  width: 0;
  background: var(--red);
}
.hero-sheet { --tilt: -0.4deg; }
</style>
</head>
<body>
<div class="desk">
<aside class="toc">
  <h1>ML Interview<br/>Notes</h1>
  <div class="sub">Handwritten · unruled · RAP prep<br/>From 0% → interview-ready</div>
  <input id="q" type="search" placeholder="Search concepts…" />
  <nav id="tocnav"></nav>
</aside>
<main class="book" id="book">
"""

FOOT = r"""
</main>
</div>
<div class="progress"><i id="bar"></i></div>
<script>
(function(){
  const book = document.getElementById('book');
  const nav = document.getElementById('tocnav');
  const sheets = [...book.querySelectorAll('.sheet[id]')];
  sheets.forEach(s => {
    const a = document.createElement('a');
    a.href = '#' + s.id;
    a.textContent = s.dataset.title || s.querySelector('h2')?.textContent || s.id;
    a.className = s.dataset.level === 'sec' ? 'sec' : 'ch';
    nav.appendChild(a);
  });
  const links = [...nav.querySelectorAll('a')];
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      links.forEach(l => l.classList.toggle('active', l.getAttribute('href') === '#' + e.target.id));
    });
  }, { rootMargin: '-20% 0px -70% 0px' });
  sheets.forEach(s => io.observe(s));
  document.getElementById('q').addEventListener('input', (e) => {
    const q = e.target.value.trim().toLowerCase();
    sheets.forEach(s => {
      const hit = !q || s.textContent.toLowerCase().includes(q);
      s.classList.toggle('hidden', !hit);
    });
  });
  window.addEventListener('scroll', () => {
    const h = document.documentElement;
    const p = h.scrollTop / (h.scrollHeight - h.clientHeight || 1);
    document.getElementById('bar').style.width = (p * 100) + '%';
  });
})();
</script>
</body>
</html>
"""


def sheet(sid: str, title: str, body: str, *, level: str = "ch", tilt: str = "0deg") -> str:
    return f'''<article class="sheet" id="{sid}" data-title="{title}" data-level="{level}" style="--tilt:{tilt}">
<h2>{title}</h2>
{body}
</article>
'''


def svg_box_flow(pairs, w=640, h=120):
    """Simple left-to-right boxes."""
    n = len(pairs)
    bw = min(110, (w - 40) // n - 20)
    gap = (w - 40 - n * bw) // max(n - 1, 1)
    parts = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Kalam, cursive">']
    for i, (label, color) in enumerate(pairs):
        x = 20 + i * (bw + gap)
        y = 30
        parts.append(
            f'<rect x="{x}" y="{y}" width="{bw}" height="48" rx="4" fill="none" stroke="{color}" stroke-width="2"/>'
        )
        parts.append(
            f'<text x="{x + bw/2}" y="{y + 30}" text-anchor="middle" font-size="13" fill="#1c1914">{label}</text>'
        )
        if i < n - 1:
            x2 = x + bw
            parts.append(
                f'<line x1="{x2}" y1="{y+24}" x2="{x2+gap}" y2="{y+24}" stroke="#1a4f8c" stroke-width="2" marker-end="url(#arrow)"/>'
            )
    parts.insert(
        1,
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#1a4f8c"/></marker></defs>',
    )
    parts.append("</svg>")
    return '<figure class="diagram">' + "".join(parts) + "</figure>"


def content() -> str:
    parts: list[str] = []

    parts.append(
        sheet(
            "cover",
            "0 · How to read this book",
            f'''
<p class="lead">One page. Unruled paper. Built for a RAP-style ML Engineer Intern interview:
crisp definitions, intuition, and the <span class="ink-red">why</span> behind each technique —
especially everything that happens <em>after</em> a model is trained.</p>
<div class="margin-note">Exclude Python syntax, LeetCode tricks, and “how to import torch”. Keep the science.</div>
<p>Sources woven in: RAP topic list PDF, RAPFlow / AIStudio / agent harness notes from your prep chat,
plus the interview bank (LoRA, QLoRA, quantization, RAG, agents, vLLM…).</p>
{svg_box_flow([
    ("Basics", "#1a4f8c"),
    ("Nets", "#2a5c3a"),
    ("Transformers", "#a83228"),
    ("Post-train ★", "#1a4f8c"),
    ("RAG/Agents", "#2a5c3a"),
])}
<p><span class="tag">search above</span> <span class="tag">click headings in TOC</span> <span class="tag">open &lt;details&gt; for depth</span></p>
''',
            tilt="-0.5deg",
        )
    )

    parts.append(
        sheet(
            "map",
            "1 · The map: AI → ML → DL → LLM → Agents",
            f'''
<p>Imagine intelligence as nested dolls:</p>
<ul class="tight">
<li><b>AI</b> — any system that acts intelligently (rules, search, ML…).</li>
<li><b>ML</b> — learn patterns from data instead of hand-writing rules.</li>
<li><b>DL</b> — ML with multi-layer neural nets that learn features themselves.</li>
<li><b>LLM</b> — a deep net trained to predict the next token in text (a language model at huge scale).</li>
<li><b>Agent</b> — an LLM plus a <em>harness</em>: tools, memory, loops, guardrails.</li>
</ul>
{svg_box_flow([
    ("Data", "#1a4f8c"),
    ("Train", "#1a4f8c"),
    ("Adapt", "#a83228"),
    ("Serve", "#2a5c3a"),
    ("Observe", "#2a5c3a"),
])}
<p class="lead ink-blue">RAP mindset (from AIStudio notes): an enterprise pipeline may mix LLM + classifier + OCR/CV + deterministic code. Agent ≠ “only an LLM”.</p>
<details class="card"><summary>Official RAP prep topics (from PDF)</summary>
<ol>
<li>Train a basic LLM + fast inference frameworks</li>
<li>LLM parameters for training &amp; inferencing</li>
<li>Agent harness, context &amp; tools <em>without</em> heavy frameworks</li>
<li>Prompt writing for any task</li>
<li>Basic ML system architecture</li>
<li>Flask+Gunicorn / FastAPI+Uvicorn</li>
<li>Docker (+ compose)</li>
<li>Streamlit or Gradio</li>
<li>Debug without ChatGPT</li>
<li>LeetCode arrays/dicts (out of scope for these notes)</li>
</ol>
</details>
''',
        )
    )

    # Classical ML
    parts.append(
        sheet(
            "learning-types",
            "2 · Types of learning",
            '''
<h3>Supervised</h3>
<p>You have inputs <b>X</b> and labels <b>y</b>. The model learns a function <span class="formula">f(X) ≈ y</span>.
Like a student with an answer key.</p>
<ul class="tight">
<li><b>Regression</b> — y is continuous (price, temperature).</li>
<li><b>Classification</b> — y is a class (spam/ham, digit 0–9).</li>
</ul>
<h3>Unsupervised</h3>
<p>Only X. Find structure: clusters, density, dimensions. No answer key.</p>
<h3>Reinforcement learning</h3>
<p>An agent takes actions, gets rewards. Learns a policy. (RLHF for LLMs borrows this idea.)</p>
<div class="ask">“Supervised vs unsupervised — one sentence each, with an example.”</div>
<details class="card"><summary>Bias–variance, over/underfitting</summary>
<p><b>Bias</b>: systematic error from a too-simple model (underfit).<br/>
<b>Variance</b>: sensitivity to training sample (overfit).<br/>
Goal: sweet spot. Regularization, more data, simpler models, early stopping help.</p>
<figure class="diagram">
<svg viewBox="0 0 520 180" xmlns="http://www.w3.org/2000/svg" font-family="Kalam, cursive">
  <text x="40" y="24" font-size="16" fill="#a83228">underfit</text>
  <text x="220" y="24" font-size="16" fill="#2a5c3a">sweet spot</text>
  <text x="400" y="24" font-size="16" fill="#a83228">overfit</text>
  <path d="M40,140 Q140,40 260,90 T480,50" fill="none" stroke="#1a4f8c" stroke-width="2"/>
  <path d="M40,100 Q200,110 480,130" fill="none" stroke="#8a8274" stroke-width="1.5" stroke-dasharray="4 3"/>
  <text x="40" y="170" font-size="13" fill="#8a8274">model complexity →</text>
</svg>
<figcaption>Solid = train error · dashed = test error (sketch)</figcaption>
</figure>
</details>
''',
        )
    )

    parts.append(
        sheet(
            "linear-regression",
            "3 · Linear & logistic regression",
            '''
<h3>Linear regression — geometry first</h3>
<p>Imagine points on a plane. You draw the straight line that misses them the least.</p>
<p class="formula">ŷ = w·x + b &nbsp;&nbsp;|&nbsp;&nbsp; Loss = (1/n) Σ (ŷᵢ − yᵢ)² &nbsp;(MSE)</p>
<p><b>Intuition:</b> w is the slope (how much y changes when x grows). b is the intercept.
Gradient descent nudges w,b downhill on the loss bowl.</p>
<figure class="diagram">
<svg viewBox="0 0 420 200" xmlns="http://www.w3.org/2000/svg" font-family="Kalam, cursive">
  <line x1="40" y1="170" x2="390" y2="170" stroke="#1c1914"/>
  <line x1="40" y1="170" x2="40" y2="20" stroke="#1c1914"/>
  <line x1="60" y1="150" x2="360" y2="40" stroke="#1a4f8c" stroke-width="2"/>
  <circle cx="100" cy="130" r="4" fill="#a83228"/><circle cx="160" cy="100" r="4" fill="#a83228"/>
  <circle cx="220" cy="95" r="4" fill="#a83228"/><circle cx="280" cy="60" r="4" fill="#a83228"/>
  <circle cx="320" cy="70" r="4" fill="#a83228"/>
  <text x="300" y="35" font-size="14" fill="#1a4f8c">ŷ = wx+b</text>
</svg>
<figcaption>Best-fit line through noisy points</figcaption>
</figure>
<details class="card"><summary>Ridge vs Lasso (regularization)</summary>
<p>Add a penalty so weights don’t explode (fight overfitting).</p>
<p class="formula">Ridge: + λ‖w‖₂² &nbsp;(shrinks weights, keeps all features)<br/>
Lasso: + λ‖w‖₁ &nbsp;(can zero weights → feature selection)</p>
</details>
<h3>Logistic regression — classification</h3>
<p>Still a linear score z = w·x + b, but squash through a <b>sigmoid</b> to get a probability:</p>
<p class="formula">σ(z) = 1 / (1 + e^(−z)) &nbsp;∈ (0,1)</p>
<p>Train with <b>binary cross-entropy</b>, not MSE. Decision: if σ(z) &gt; 0.5 → class 1.</p>
<div class="ask">“Why not use MSE with sigmoid?” → gradients saturate; CE matches Bernoulli likelihood.</div>
''',
            tilt="0.3deg",
        )
    )

    parts.append(
        sheet(
            "classical-ml",
            "4 · Classical ML algorithms (interview set)",
            '''
<details class="card" open><summary>Decision tree</summary>
<p>Ask yes/no questions that split data to purify labels (info gain / Gini). Easy to visualize; overfits if deep.
<b>Random Forest</b>: many trees on bootstrap samples + random features → bagging → lower variance.
<b>Boosting</b> (AdaBoost, Gradient Boosting, <b>XGBoost</b>): trees correct previous trees’ mistakes sequentially.</p>
</details>
<details class="card"><summary>k-NN</summary>
<p>No training really — store points. Predict by vote/average of k nearest neighbors.
Curse of dimensionality: distances become meaningless in high-d.</p>
</details>
<details class="card"><summary>Naive Bayes</summary>
<p>Bayes rule + assume features independent given class. Fast text baseline. “Naive” = independence assumption.</p>
</details>
<details class="card"><summary>SVM</summary>
<p>Find the hyperplane with maximum margin between classes. Kernels map to higher dimensions for non-linear borders.</p>
<figure class="diagram">
<svg viewBox="0 0 400 160" xmlns="http://www.w3.org/2000/svg" font-family="Kalam, cursive">
  <line x1="50" y1="130" x2="350" y2="30" stroke="#1a4f8c" stroke-width="2"/>
  <line x1="70" y1="140" x2="370" y2="40" stroke="#1a4f8c" stroke-width="1" stroke-dasharray="4 3"/>
  <line x1="30" y1="120" x2="330" y2="20" stroke="#1a4f8c" stroke-width="1" stroke-dasharray="4 3"/>
  <circle cx="90" cy="50" r="5" fill="#2a5c3a"/><circle cx="120" cy="70" r="5" fill="#2a5c3a"/>
  <circle cx="280" cy="110" r="5" fill="#a83228"/><circle cx="310" cy="90" r="5" fill="#a83228"/>
  <text x="200" y="155" font-size="14" fill="#8a8274">margin</text>
</svg>
<figcaption>Max-margin separator + support vectors on the dashed edges</figcaption>
</figure>
</details>
<details class="card"><summary>Clustering: K-Means, Hierarchical, DBSCAN</summary>
<p><b>K-Means</b>: pick k centers, assign points, move centers to mean, repeat.<br/>
<b>Hierarchical</b>: build a dendrogram of merges/splits.<br/>
<b>DBSCAN</b>: density-based; finds arbitrary shapes; marks noise; needs ε and minPts.</p>
</details>
<div class="ask">Bagging vs boosting? RF vs single tree? When DBSCAN over K-Means?</div>
''',
        )
    )

    parts.append(
        sheet(
            "gradients",
            "4.5 · Gradients & loss bowls (must-have intuition)",
            '''
<p>Training = stand on a hilly landscape (loss). Each weight is a coordinate. The <b>gradient</b> points uphill;
we step downhill: <span class="formula">w ← w − η ∇_w L</span></p>
<ul class="tight">
<li><b>η learning rate</b>: step size. Too big → bounce. Too small → crawl.</li>
<li><b>Mini-batch</b>: estimate gradient from a subset — noisy but efficient.</li>
<li><b>Local minima / saddle points</b>: Adam helps navigate flatter regions.</li>
</ul>
<figure class="diagram">
<svg viewBox="0 0 480 160" xmlns="http://www.w3.org/2000/svg" font-family="Kalam, cursive">
  <path d="M40,40 Q120,140 200,70 T360,90 T460,50" fill="none" stroke="#1a4f8c" stroke-width="2"/>
  <circle cx="200" cy="70" r="5" fill="#a83228"/>
  <line x1="200" y1="70" x2="170" y2="100" stroke="#a83228" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="210" y="65" font-size="13" fill="#a83228">you are here</text>
  <text x="40" y="150" font-size="13" fill="#8a8274">weight → &nbsp;&nbsp; height = loss</text>
</svg>
<figcaption>Loss surface sketch — follow the negative gradient</figcaption>
</figure>
<details class="card"><summary>Softmax + cross-entropy (LLM training loss)</summary>
<p>Logits z → probs p_i = e^{z_i}/Σ e^{z_j}. For true class y:
L = −log p_y. Intuition: punish low probability on the correct next token.
Never apply softmax <em>before</em> CE in frameworks that already include it (classic PyTorch bug).</p>
</details>
''',
            level="sec",
        )
    )

    parts.append(
        sheet(
            "embeddings",
            "4.6 · Embeddings &amp; vector geometry",
            '''
<p>An embedding maps discrete things (words, docs) to vectors so <b>geometry ≈ meaning</b>:
similar items have high cosine similarity.</p>
<p class="formula">cos(a,b) = (a·b) / (‖a‖ ‖b‖)</p>
<figure class="diagram">
<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg" font-family="Kalam, cursive">
  <line x1="40" y1="150" x2="380" y2="150" stroke="#1c1914"/>
  <line x1="40" y1="150" x2="40" y2="20" stroke="#1c1914"/>
  <line x1="40" y1="150" x2="200" y2="40" stroke="#1a4f8c" stroke-width="2"/>
  <line x1="40" y1="150" x2="280" y2="60" stroke="#2a5c3a" stroke-width="2"/>
  <line x1="40" y1="150" x2="120" y2="90" stroke="#a83228" stroke-width="2"/>
  <text x="205" y="35" font-size="13" fill="#1a4f8c">king</text>
  <text x="285" y="55" font-size="13" fill="#2a5c3a">queen</text>
  <text x="125" y="85" font-size="13" fill="#a83228">car</text>
</svg>
<figcaption>Nearby angles ≈ related meanings (cartoon 2D)</figcaption>
</figure>
<p>Used in: Word2Vec/legacy NLP, modern sentence transformers, <b>RAG retrieval</b>, clustering.</p>
''',
            level="sec",
            tilt="0.25deg",
        )
    )

    parts.append(
        sheet(
            "neural-nets",
            "5 · Neural nets from zero (ANN)",
            f'''
<p class="lead">A neuron: weighted sum → nonlinearity. A network: stack them so they compose complex functions.</p>
<p class="formula">z = W x + b &nbsp;&nbsp;→&nbsp;&nbsp; a = φ(z) &nbsp;&nbsp;(ReLU, sigmoid, tanh…)</p>
{svg_box_flow([
    ("input x", "#1a4f8c"),
    ("hidden", "#2a5c3a"),
    ("hidden", "#2a5c3a"),
    ("output", "#a83228"),
])}
<details class="card" open><summary>Backpropagation (intuition)</summary>
<p>Forward: compute prediction &amp; loss.<br/>
Backward: use chain rule to see how much each weight contributed to the error; nudge weights opposite the gradient.
It’s “blame assignment” flowing backwards.</p>
</details>
<details class="card"><summary>Key training knobs</summary>
<ul class="tight">
<li><b>Loss</b>: MSE (regression), Cross-Entropy (classification / next-token).</li>
<li><b>Optimizer</b>: SGD, Adam, AdamW (decoupled weight decay).</li>
<li><b>LR schedule</b>: warmup + cosine decay common for transformers.</li>
<li><b>Batch size</b>: noisier grads if small; memory if large.</li>
<li><b>Regularization</b>: dropout, weight decay, early stopping, data aug.</li>
</ul>
</details>
<div class="ask">What does ReLU do geometrically? Why is CE used with softmax?</div>
''',
        )
    )

    parts.append(
        sheet(
            "cnn-rnn",
            "6 · CNN &amp; RNN / LSTM",
            '''
<h3>CNN — vision’s inductive bias</h3>
<p>Images have local structure. <b>Convolution</b> slides small filters that detect edges → textures → parts.
Weight sharing = same filter everywhere → translation-friendly &amp; fewer params than a giant dense net.</p>
<figure class="diagram">
<svg viewBox="0 0 520 150" xmlns="http://www.w3.org/2000/svg" font-family="Kalam, cursive">
  <rect x="20" y="30" width="90" height="90" fill="none" stroke="#1c1914" stroke-width="1.5"/>
  <text x="65" y="80" text-anchor="middle" font-size="14">image</text>
  <rect x="140" y="50" width="40" height="40" fill="none" stroke="#a83228" stroke-width="2"/>
  <text x="160" y="130" text-anchor="middle" font-size="13" fill="#a83228">filter</text>
  <text x="210" y="75" font-size="22" fill="#1a4f8c">→</text>
  <rect x="250" y="40" width="70" height="70" fill="none" stroke="#1a4f8c" stroke-width="1.5"/>
  <text x="285" y="80" text-anchor="middle" font-size="13">feature map</text>
  <text x="350" y="75" font-size="22" fill="#1a4f8c">→</text>
  <text x="400" y="70" font-size="14">pool / more</text>
  <text x="400" y="90" font-size="14">conv layers</text>
</svg>
<figcaption>Local receptive field → feature map</figcaption>
</figure>
<h3>RNN / LSTM — sequences before transformers</h3>
<p>RNNs read tokens one-by-one, hidden state carries memory. Hard to train far back (vanishing grads).
<b>LSTM/GRU</b> add gates to keep/forget information longer. Transformers largely replaced them for NLP via attention.</p>
<div class="ask">CNN vs MLP on images? Why LSTM gates?</div>
''',
            tilt="-0.25deg",
        )
    )

    parts.append(
        sheet(
            "transformers",
            "7 · Transformers &amp; attention (core)",
            '''
<div class="margin-note">Karpathy “Let’s build GPT” is the gold video for this chapter.</div>
<p>A transformer block = <b>self-attention</b> + <b>MLP</b>, with residuals &amp; layer-norm.</p>
<h3>Self-attention — geometric story</h3>
<p>Each token makes three vectors from itself: <b>Query</b> (what I’m looking for), <b>Key</b> (what I contain), <b>Value</b> (what I pass along).</p>
<p class="formula">Attention(Q,K,V) = softmax(QKᵀ / √d<sub>k</sub>) V</p>
<ul class="tight">
<li>Dot Q·K = relevance score between tokens.</li>
<li>/√d<sub>k</sub> keeps scores from exploding.</li>
<li>softmax → weights that sum to 1.</li>
<li>Weighted sum of V = new representation.</li>
</ul>
<figure class="diagram">
<svg viewBox="0 0 560 200" xmlns="http://www.w3.org/2000/svg" font-family="Kalam, cursive">
  <text x="30" y="30" font-size="15">tokens: The cat sat</text>
  <rect x="30" y="50" width="70" height="36" rx="4" fill="none" stroke="#1a4f8c" stroke-width="2"/><text x="65" y="73" text-anchor="middle" font-size="13">The</text>
  <rect x="120" y="50" width="70" height="36" rx="4" fill="none" stroke="#1a4f8c" stroke-width="2"/><text x="155" y="73" text-anchor="middle" font-size="13">cat</text>
  <rect x="210" y="50" width="70" height="36" rx="4" fill="none" stroke="#1a4f8c" stroke-width="2"/><text x="245" y="73" text-anchor="middle" font-size="13">sat</text>
  <path d="M155,86 Q155,120 245,86" fill="none" stroke="#a83228" stroke-width="1.5"/>
  <path d="M65,86 Q100,130 245,86" fill="none" stroke="#2a5c3a" stroke-width="1.5"/>
  <text x="30" y="160" font-size="14" fill="#a83228">“sat” attends strongly to “cat”</text>
  <text x="30" y="180" font-size="13" fill="#8a8274">multi-head = several such views in parallel</text>
</svg>
<figcaption>Attention as soft lookup between tokens</figcaption>
</figure>
<details class="card"><summary>Causal mask, MHA, GQA, MQA</summary>
<p><b>Causal LM</b>: token i may only attend to ≤ i (no peeking at the future).<br/>
<b>Multi-Head Attention</b>: several QKV projections → richer patterns.<br/>
<b>MQA / GQA</b>: share K/V across heads → much smaller KV cache at decode time (interview favorite).</p>
</details>
<details class="card"><summary>Positional info</summary>
<p>Attention alone is permutation-invariant. Add positions: sinusoidal, learned, <b>RoPE</b> (rotate Q/K by position), ALiBi…</p>
</details>
<details class="card"><summary>Encoder vs decoder vs encoder–decoder</summary>
<p>BERT-style encoder (bidirectional), GPT-style decoder (causal), T5-style both (seq2seq).</p>
</details>
<div class="ask">Write the attention formula and explain each symbol. What is GQA?</div>
''',
        )
    )

    parts.append(
        sheet(
            "lms-decoding",
            "8 · Language models &amp; decoding",
            '''
<p>An LM assigns P(next token | previous tokens). Training = maximize likelihood of real text (CE on next token).</p>
<h3>Decoding — how we sample answers</h3>
<ul class="tight">
<li><b>Greedy</b>: always pick argmax. Deterministic, can be dull/repetitive.</li>
<li><b>Temperature T</b>: divide logits by T before softmax. T→0 ≈ greedy; T↑ = flatter, more random.</li>
<li><b>Top-k</b>: sample only from k highest logits.</li>
<li><b>Top-p (nucleus)</b>: smallest set whose probs sum to ≥ p.</li>
<li><b>Beam search</b>: keep top-B partial hypotheses (classic MT; less common for chatty LLMs).</li>
</ul>
<p class="formula">softmax(logits / T)</p>
<div class="ask">Exact defs: temperature, top-k, top-p, greedy. Trade-offs?</div>
<details class="card"><summary>Prompting (interview list item #4)</summary>
<p>Zero-shot / few-shot / CoT / ReAct / roles / delimiters. Prompt injection = hostile instructions in data.
Structure beats poetry: role, task, constraints, output schema, examples.</p>
</details>
''',
        )
    )

    parts.append(
        sheet(
            "tokenization",
            "8.5 · Tokenization (BPE intuition)",
            '''
<p>Models don’t see letters; they see <b>token IDs</b>. BPE merges frequent pairs (“ing”, “tion”) into subwords.
Trade-off: vocab size vs sequence length vs rare-word handling. Special tokens: BOS/EOS/PAD.</p>
<div class="ask">Why subwords instead of whole words?</div>
''',
            level="sec",
        )
    )

    parts.append(
        sheet(
            "train-llm",
            "9 · Training a basic LLM (pretrain → SFT)",
            f'''
<p class="lead ink-red">Fine-tuning ≠ training from scratch.</p>
{svg_box_flow([
    ("Pretrain", "#1a4f8c"),
    ("SFT", "#2a5c3a"),
    ("Prefer/Align", "#a83228"),
    ("Deploy", "#1a4f8c"),
])}
<ul class="tight">
<li><b>Pretraining</b>: next-token on huge corpora — expensive, foundation model.</li>
<li><b>SFT (instruction tuning)</b>: supervised examples of (prompt → ideal answer).</li>
<li><b>Preference / RLHF / DPO</b>: steer toward human-preferred style &amp; safety.</li>
</ul>
<details class="card"><summary>Practical training knobs</summary>
<p>Mixed precision (fp16/bf16), gradient accumulation, grad checkpointing (trade compute for memory),
packing sequences, LoRA instead of full FT when you lack GPUs.</p>
</details>
<div class="ask">Outline how you’d train a small LM, then serve it fast.</div>
''',
        )
    )

    # POST TRAINING - the star section
    parts.append(
        sheet(
            "post-train",
            "10 · ★ After the model is trained",
            '''
<p class="lead">This is where RAP interviews live: you have weights — now make them <b>cheap, fast, and task-fit</b>
without always retraining everything.</p>
<figure class="diagram">
<svg viewBox="0 0 640 160" xmlns="http://www.w3.org/2000/svg" font-family="Kalam, cursive">
  <rect x="20" y="40" width="120" height="70" rx="6" fill="none" stroke="#1a4f8c" stroke-width="2"/>
  <text x="80" y="80" text-anchor="middle" font-size="14">Base model</text>
  <text x="160" y="75" font-size="22" fill="#1a4f8c">→</text>
  <rect x="190" y="20" width="100" height="50" rx="4" fill="none" stroke="#a83228" stroke-width="2"/>
  <text x="240" y="50" text-anchor="middle" font-size="13">LoRA/SFT</text>
  <rect x="190" y="85" width="100" height="50" rx="4" fill="none" stroke="#a83228" stroke-width="2"/>
  <text x="240" y="115" text-anchor="middle" font-size="13">Quantize</text>
  <text x="310" y="75" font-size="22" fill="#1a4f8c">→</text>
  <rect x="340" y="40" width="120" height="70" rx="6" fill="none" stroke="#2a5c3a" stroke-width="2"/>
  <text x="400" y="70" text-anchor="middle" font-size="13">KV / batching</text>
  <text x="400" y="90" text-anchor="middle" font-size="13">vLLM / TGI</text>
  <text x="480" y="75" font-size="22" fill="#1a4f8c">→</text>
  <rect x="510" y="40" width="110" height="70" rx="6" fill="none" stroke="#1c1914" stroke-width="2"/>
  <text x="565" y="80" text-anchor="middle" font-size="14">API</text>
</svg>
<figcaption>Adapt → compress → accelerate → serve</figcaption>
</figure>
''',
        )
    )

    parts.append(
        sheet(
            "lora",
            "10.1 · LoRA &amp; QLoRA (PEFT)",
            '''
<div class="margin-note">Demand an exact definition in interviews.</div>
<h3>LoRA — Low-Rank Adaptation</h3>
<p><b>Definition:</b> Freeze the pretrained weights W₀. For selected layers, learn a low-rank update
ΔW = B A where A is r×d_in, B is d_out×r, with rank r ≪ min(d_in,d_out). Forward becomes:</p>
<p class="formula">h = W₀ x + (α/r) B A x</p>
<p><b>Why it works (geometry):</b> Task change often lives in a low-dimensional subspace of weight-space.
Instead of moving the whole matrix, you learn a thin “side road” of adapters.</p>
<ul class="tight">
<li>Few trainable params → less VRAM, faster FT, easy to swap adapters.</li>
<li><b>rank r</b> &amp; <b>alpha</b>: capacity vs stability; targets often q/v projections.</li>
<li>Can merge adapters into W for serving.</li>
</ul>
<figure class="diagram">
<svg viewBox="0 0 520 180" xmlns="http://www.w3.org/2000/svg" font-family="Kalam, cursive">
  <rect x="40" y="40" width="100" height="100" fill="none" stroke="#1a4f8c" stroke-width="2"/>
  <text x="90" y="95" text-anchor="middle" font-size="14">W₀ frozen</text>
  <text x="170" y="90" font-size="20">+</text>
  <rect x="200" y="55" width="40" height="70" fill="none" stroke="#a83228" stroke-width="2"/>
  <text x="220" y="95" text-anchor="middle" font-size="12">B</text>
  <rect x="260" y="70" width="70" height="40" fill="none" stroke="#a83228" stroke-width="2"/>
  <text x="295" y="95" text-anchor="middle" font-size="12">A</text>
  <text x="360" y="90" font-size="16">→ ΔW low-rank</text>
</svg>
<figcaption>Big frozen W + skinny BA update</figcaption>
</figure>
<h3>QLoRA</h3>
<p><b>Definition:</b> Load the base model in <b>4-bit quantized</b> form (e.g. NF4) to save memory,
keep a small set of <b>fp16/bf16 LoRA adapters</b> trainable. Backprop through frozen quantized weights into adapters.</p>
<p>Result: fine-tune big models on much smaller GPUs.</p>
<div class="ask">LoRA vs full FT? What does rank mean? How is QLoRA different from LoRA?</div>
<details class="card"><summary>When NOT to fine-tune</summary>
<p>If knowledge changes often or is private/docs → prefer <b>RAG</b>.
If you only need format/style → prompting or light SFT/LoRA.
Full FT when you must deeply change behavior and have data+compute.</p>
</details>
''',
            level="sec",
            tilt="0.35deg",
        )
    )

    parts.append(
        sheet(
            "quantization",
            "10.2 · Quantization",
            '''
<p><b>Definition:</b> Store/compute weights (and sometimes activations) with fewer bits
(fp32→fp16/bf16→INT8→INT4), trading a bit of accuracy for memory &amp; speed.</p>
<p class="formula">q = round(w / scale) + zero_point &nbsp;&nbsp;|&nbsp;&nbsp; ŵ = scale · (q − zero_point)</p>
<ul class="tight">
<li><b>PTQ</b> — quantize after training (calibrate on a few batches).</li>
<li><b>QAT</b> — simulate quantization during training; usually more accurate.</li>
<li><b>GPTQ / AWQ</b> — strong weight-only PTQ methods for LLMs.</li>
<li><b>Weight-only vs activation quant</b> — activations harder (outliers).</li>
</ul>
<figure class="diagram">
<svg viewBox="0 0 480 140" xmlns="http://www.w3.org/2000/svg" font-family="Kalam, cursive">
  <text x="30" y="40" font-size="14">fp16 continuous-ish values</text>
  <line x1="30" y1="60" x2="450" y2="60" stroke="#1a4f8c" stroke-width="2"/>
  <text x="30" y="100" font-size="14" fill="#a83228">INT4 staircase (16 levels)</text>
  <path d="M30,110 H60 V90 H90 V110 H120 V90 H150 V110 H180 V90 H210 V110 H240 V90 H270 V110 H300 V90 H330 V110 H360 V90 H390 V110 H420 V90 H450"
        fill="none" stroke="#a83228" stroke-width="2"/>
</svg>
<figcaption>Continuous weights snapped to discrete bins</figcaption>
</figure>
<div class="ask">INT8 vs INT4 trade-off? PTQ vs QAT? Why calibrate?</div>
''',
            level="sec",
        )
    )

    parts.append(
        sheet(
            "inference",
            "10.3 · Inference optimization (KV, batching, engines)",
            '''
<h3>KV cache</h3>
<p>During autoregressive decode, K and V for past tokens are reused. Cache them so you don’t recompute the whole prompt every step.
Memory grows with <b>batch × layers × heads × seq × dim</b> — why long context is expensive.</p>
<h3>PagedAttention &amp; continuous batching (vLLM)</h3>
<p><b>PagedAttention:</b> manage KV memory like OS virtual memory (pages) → less fragmentation, higher GPU utilization.<br/>
<b>Continuous batching:</b> add/remove sequences as they finish instead of waiting for the slowest in a static batch.</p>
<ul class="tight">
<li><b>TTFT</b> — time to first token (prefill).</li>
<li><b>Tok/s</b> — decode throughput.</li>
<li><b>FlashAttention</b> — IO-aware exact attention; faster &amp; less memory.</li>
<li><b>Speculative decoding</b> — draft model proposes, big model verifies.</li>
</ul>
<details class="card"><summary>Engines to name</summary>
<p>vLLM, TGI, TensorRT-LLM, llama.cpp, Triton. RAP cares that you know <em>why</em> an engine is fast (batching + KV memory), not just the brand.</p>
</details>
<div class="ask">What is a KV cache? PagedAttention in one sentence? Prefill vs decode?</div>
''',
            level="sec",
            tilt="-0.3deg",
        )
    )

    parts.append(
        sheet(
            "alignment",
            "10.4 · Alignment: RLHF &amp; DPO",
            '''
<p><b>RLHF:</b> SFT → train a <b>reward model</b> on human preferences → optimize policy (often PPO) with a KL penalty to stay near the SFT model.</p>
<p><b>DPO:</b> Direct Preference Optimization — skip the explicit RL loop; optimize a closed-form loss on preferred vs rejected answers relative to a reference model.</p>
<div class="ask">RLHF stages? DPO vs PPO-RLHF?</div>
''',
            level="sec",
        )
    )

    parts.append(
        sheet(
            "rag",
            "11 · RAG, HyDE, Graph RAG",
            f'''
<p><b>RAG</b> = retrieve relevant docs → stuff into context → generate. Grounds answers; helps private/fresh knowledge without FT.</p>
{svg_box_flow([
    ("Query", "#1a4f8c"),
    ("Retrieve", "#2a5c3a"),
    ("Augment", "#2a5c3a"),
    ("Generate", "#a83228"),
])}
<ul class="tight">
<li>Chunking, embeddings, hybrid BM25+dense, rerankers.</li>
<li><b>HyDE</b>: generate a hypothetical answer doc, embed that to retrieve better.</li>
<li><b>Graph RAG</b>: entities/relations in a graph + vectors — multi-hop &amp; structured links (RAP-flavored).</li>
<li>OCR / Image RAG for scanned manuals &amp; screenshots.</li>
</ul>
<div class="ask">RAG vs fine-tuning — when each? Failure modes of naive RAG?</div>
''',
        )
    )

    parts.append(
        sheet(
            "agents",
            "12 · Agents, harness, MCP",
            '''
<p class="lead">Agent = model + tools + loop. <b>Harness</b> = the software cage around it.</p>
<figure class="diagram">
<svg viewBox="0 0 560 170" xmlns="http://www.w3.org/2000/svg" font-family="Kalam, cursive">
  <rect x="20" y="50" width="90" height="50" rx="4" fill="none" stroke="#1a4f8c" stroke-width="2"/><text x="65" y="80" text-anchor="middle" font-size="13">Observe</text>
  <text x="120" y="80" font-size="18">→</text>
  <rect x="150" y="50" width="90" height="50" rx="4" fill="none" stroke="#1a4f8c" stroke-width="2"/><text x="195" y="80" text-anchor="middle" font-size="13">Decide</text>
  <text x="250" y="80" font-size="18">→</text>
  <rect x="280" y="50" width="90" height="50" rx="4" fill="none" stroke="#a83228" stroke-width="2"/><text x="325" y="80" text-anchor="middle" font-size="13">Act/Tool</text>
  <text x="380" y="80" font-size="18">→</text>
  <rect x="410" y="50" width="110" height="50" rx="4" fill="none" stroke="#2a5c3a" stroke-width="2"/><text x="465" y="80" text-anchor="middle" font-size="13">Record</text>
  <path d="M465,100 Q280,160 65,100" fill="none" stroke="#8a8274" stroke-width="1.5" stroke-dasharray="4 3"/>
  <text x="200" y="155" font-size="13" fill="#8a8274">harness: limits, validation, retries, logs</text>
</svg>
<figcaption>ReAct-style loop inside a harness</figcaption>
</figure>
<ul class="tight">
<li>Tool schemas (JSON), timeouts, max steps, sandboxing.</li>
<li>Context management: what stays in the window vs memory store.</li>
<li><b>MCP</b> (Model Context Protocol): standard way to expose tools/resources to models.</li>
<li>Multi-agent: supervisor + specialists; human-in-the-loop gates for high stakes.</li>
</ul>
<p class="ink-blue">RAP VerifyMe / guardrails: don’t trust free-form model output for enterprise actions — verify, redact PII, audit.</p>
<div class="ask">Define agent harness. How do you stop infinite tool loops?</div>
''',
            tilt="0.2deg",
        )
    )

    parts.append(
        sheet(
            "diffusion",
            "13 · Diffusion models (brief)",
            '''
<p>Generative vision (and more): gradually add noise to data (forward), train a net to <b>denoize</b> step-by-step (reverse).
Sampling starts from noise and walks back to an image. Different family from autoregressive LLMs, but same “deep generative model” family tree.</p>
<div class="ask">One-sentence diffusion vs one-sentence GPT.</div>
''',
        )
    )

    parts.append(
        sheet(
            "systems",
            "14 · ML system design, serving, Docker",
            f'''
{svg_box_flow([
    ("Ingest", "#1a4f8c"),
    ("Train", "#1a4f8c"),
    ("Registry", "#2a5c3a"),
    ("Serve", "#a83228"),
    ("Monitor", "#a83228"),
])}
<ul class="tight">
<li>Online vs batch inference; latency budgets; queues; autoscaling.</li>
<li><b>FastAPI + Uvicorn</b> (async APIs); Flask + Gunicorn (classic WSGI).</li>
<li><b>Docker</b>: image = app + deps; compose for multi-service; non-root, healthchecks, GPU notes.</li>
<li>Streamlit/Gradio for demos.</li>
<li>Drift monitoring, rollbacks, shadow/canary deploys.</li>
</ul>
<details class="card"><summary>RAPFlow intuition</summary>
<p>Orchestrator as control plane; AIStudio for models/pipelines; AgenticStudio for agent workflows;
deterministic bots where LLMs shouldn’t decide; deploy in customer VPC; observability + guardrails.</p>
</details>
''',
        )
    )

    parts.append(
        sheet(
            "eval-metrics",
            "14.5 · Evaluation metrics you’ll be asked",
            '''
<ul class="tight">
<li><b>Accuracy / Precision / Recall / F1</b> — classification; know imbalance traps.</li>
<li><b>ROC-AUC</b> — ranking quality across thresholds.</li>
<li><b>Perplexity</b> — exp(average CE); lower → model less “surprised” by text (limited as quality metric).</li>
<li><b>LLM-as-judge / rubrics</b> — score answers with another model + human spot checks.</li>
<li><b>RAG</b>: retrieval Recall@k, faithfulness/groundedness, answer relevance.</li>
</ul>
<div class="ask">Precision vs recall with a medical false-negative example.</div>
''',
            level="sec",
        )
    )

    parts.append(
        sheet(
            "pytorch-debug",
            "14.6 · PyTorch mental model (debug round)",
            '''
<p>Not syntax — failure modes interviewers plant:</p>
<ul class="tight">
<li>shape / <code>view</code> / <code>Linear in_features</code> mismatch</li>
<li>device CPU vs CUDA</li>
<li>CE wants <b>logits</b> + Long targets — not softmax probs, not float labels</li>
<li><code>train()</code> vs <code>eval()</code> for dropout/BatchNorm</li>
<li>forgotten <code>zero_grad</code> (silent wrong training — still know the concept)</li>
</ul>
<p class="lead">Read the traceback. Fix the crash. Re-run. Cascades are normal.</p>
''',
            level="sec",
        )
    )

    parts.append(
        sheet(
            "flashcards",
            "15 · Definition flashcards (say these out loud)",
            '''
<details class="card"><summary>LoRA</summary><p>Freeze base weights; train low-rank matrices A,B so ΔW=BA adapts the model with few parameters.</p></details>
<details class="card"><summary>QLoRA</summary><p>Quantize base to 4-bit for memory; train LoRA adapters in higher precision on top.</p></details>
<details class="card"><summary>Quantization</summary><p>Represent numbers with fewer bits via scales/zero-points to cut memory and often speed.</p></details>
<details class="card"><summary>KV cache</summary><p>Store past keys/values during decode to avoid recomputing attention over the full prefix each token.</p></details>
<details class="card"><summary>GQA</summary><p>Grouped-Query Attention: groups of query heads share K/V → smaller KV cache.</p></details>
<details class="card"><summary>Temperature</summary><p>Softmax temperature scales logits; lower → peakier/greedy; higher → more random.</p></details>
<details class="card"><summary>Top-p</summary><p>Sample from the smallest token set whose cumulative probability ≥ p.</p></details>
<details class="card"><summary>RAG</summary><p>Retrieve external evidence, add to prompt, then generate — improves grounding &amp; freshness.</p></details>
<details class="card"><summary>Agent harness</summary><p>Control software around an LLM: tools, limits, validation, logging, retries, stopping rules.</p></details>
<details class="card"><summary>Attention</summary><p>softmax(QKᵀ/√d)V — soft weighted combination of values by query-key similarity.</p></details>
<details class="card"><summary>Cross-entropy (LM)</summary><p>Loss = −log pθ(correct next token); training pushes probability mass onto true tokens.</p></details>
<details class="card"><summary>Overfitting</summary><p>Memorizes train set; poor generalization — high variance symptom.</p></details>
''',
            tilt="-0.4deg",
        )
    )

    parts.append(
        sheet(
            "study-plan",
            "16 · 48-hour drill order",
            '''
<ol>
<li>Ch 1–5 skim + flashcards for classical ML asks.</li>
<li>Ch 7–8 attention + decoding — write formulas from memory.</li>
<li>Ch 10 ★ LoRA/QLoRA/quant/KV/vLLM — exact defs aloud.</li>
<li>Ch 11–12 RAG + agent harness story with a box diagram.</li>
<li>Ch 14 serving/Docker one-liners.</li>
<li>Run the mock interviewer hardcore mode; fix every failed def.</li>
</ol>
<p class="lead">If you can teach each red “Interview ask” to a friend without notes, you’re ready.</p>
''',
        )
    )

    return "\n".join(parts)


def main() -> None:
    html = HEAD + content() + FOOT
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
