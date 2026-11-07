# -*- coding: utf-8 -*-
"""Build AIML teaching notebook HTML."""
from pathlib import Path

OUT = Path(__file__).with_name("aiml-from-scratch-teaching.html")

CSS = r"""
:root{--paper:#fdfcf8;--ink:#1d2b4f;--ink2:#0f1a36;--blue:#1f4fa3;--red:#c62828;--green:#2e7d32;--orange:#d9822b;--faint:#8a8a8a;--hl:#fff1a8;--purple:#6a1b9a}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:16px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:"Patrick Hand","Comic Neue","Comic Sans MS",cursive;font-size:19px;line-height:1.55;
background-image:radial-gradient(circle at 20% 10%,rgba(0,0,0,.012),transparent 40%),radial-gradient(circle at 80% 90%,rgba(0,0,0,.015),transparent 45%)}
h1,h2,h3,h4{font-family:"Kalam","Patrick Hand",cursive;color:var(--ink2);margin:.25em 0}
a{color:var(--blue)}
b{color:var(--ink2);font-weight:700;background:linear-gradient(transparent 62%,rgba(255,226,120,.55) 62%)}
code{font-family:"IBM Plex Mono",Consolas,monospace;font-size:.82em;background:#f1efe6;padding:0 .3em;border-radius:4px}
.layout{display:grid;grid-template-columns:300px 1fr;min-height:100vh}
nav#toc{position:sticky;top:0;height:100vh;overflow:auto;padding:14px 12px 48px 14px;border-right:2px solid rgba(29,43,79,.22);background:var(--paper)}
nav#toc .brand{font-family:"Kalam",cursive;font-weight:700;font-size:19px;color:var(--red);margin-bottom:8px}
nav#toc a{display:block;text-decoration:none;color:var(--ink);padding:3px 6px;border-radius:6px;font-size:15px;line-height:1.3}
nav#toc a:hover{background:#f3f0e2}
nav#toc .g{font-family:"Kalam",cursive;font-weight:700;font-size:15px;color:var(--ink2);margin:10px 0 4px;padding-top:6px;border-top:1px dashed rgba(29,43,79,.2)}
main{padding:22px 40px 100px;max-width:1100px}
.hero{border-bottom:2px solid rgba(29,43,79,.25);padding-bottom:12px;margin-bottom:16px}
.hero h1{font-size:clamp(2rem,5vw,2.8rem);line-height:1.1;transform:rotate(-.5deg);display:inline-block}
.hero h1 span{color:var(--red)}
.hero .sub{font-size:1.25rem;color:var(--blue);margin:6px 0}
.hero .by{font-family:"Caveat",cursive;font-size:1.35rem;color:var(--faint)}
.howto{padding:12px 14px;border:2px solid var(--line,rgba(29,43,79,.45));border-radius:14px;background:#fff;margin:12px 0 22px}
.howto h3{color:var(--red);margin-top:0}
.part{margin-top:36px}
.ph{font-size:1.75rem;color:var(--red);border-bottom:3px solid var(--red);display:inline-block;padding-right:14px;transform:rotate(-.3deg)}
.psub{font-family:"Caveat",cursive;font-size:1.3rem;color:var(--faint);margin:2px 0 12px}
.topic{margin:18px 0;padding:14px 18px 12px;border:2px solid rgba(29,43,79,.5);border-radius:18px;background:rgba(255,255,255,.6)}
.topic h3{font-size:1.35rem;color:var(--ink2);margin:0 0 8px}
.one{margin:8px 0 12px;padding:10px 14px;border:2.5px solid var(--red);border-radius:12px;background:#fff;font-size:1.05rem}
.onelab{font-family:"Caveat",cursive;color:var(--red);font-weight:700;font-size:1.15rem}
.onelab::after{content:" → "}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:900px){.layout{grid-template-columns:1fr}nav#toc{position:relative;height:auto;max-height:40vh}.grid2{grid-template-columns:1fr}main{padding:16px 14px 80px}}
.card{padding:10px 12px;border:1.5px dashed rgba(29,43,79,.3);border-radius:10px;background:#fff;margin:6px 0}
.card h4{margin:0 0 4px;color:var(--blue);font-size:1.05rem}
.s-math{border-left:3px solid rgba(106,27,154,.4);padding-left:10px;margin:10px 0}
.s-why{border-left:3px solid rgba(46,125,50,.45);padding-left:10px;margin:10px 0}
.s-ex{border-left:3px solid rgba(31,79,163,.45);padding-left:10px;margin:10px 0}
.s-trap{border-left:3px dashed var(--red);padding-left:10px;margin:10px 0}
ul{margin:4px 0;padding-left:1.25rem}
li{margin:3px 0}
li::marker{color:var(--red)}
.steps{margin:12px 0;padding:10px;border:2px dashed rgba(29,43,79,.28);border-radius:12px;background:#fff}
.step-nav{display:flex;align-items:center;gap:10px;margin-bottom:8px;flex-wrap:wrap}
.step-nav button{font:inherit;cursor:pointer;border:2px solid var(--ink);background:var(--hl);border-radius:999px;padding:2px 12px}
.step-nav .lbl{font-family:"Caveat",cursive;font-size:1.25rem;color:var(--blue)}
.step-panel{display:none}
.step-panel.on{display:block}
.step-panel svg{width:100%;max-width:720px;height:auto;display:block;margin:6px auto}
.step-cap{font-family:"Caveat",cursive;font-size:1.2rem;color:var(--faint);text-align:center;margin-top:4px}
table.algo{width:100%;border-collapse:collapse;font-size:.95rem;margin:8px 0;background:#fff}
table.algo th,table.algo td{border:1px solid rgba(29,43,79,.25);padding:6px 8px;text-align:left;vertical-align:top}
table.algo th{background:#fff3c4;font-family:"Kalam",cursive}
.formula{font-family:"IBM Plex Mono",Consolas,monospace;background:#f6f3ea;padding:8px 10px;border-radius:8px;overflow-x:auto;margin:6px 0;font-size:.9rem}
.tag{display:inline-block;font-size:.75rem;padding:1px 8px;border-radius:999px;border:1.5px solid var(--line-soft,rgba(29,43,79,.3));margin-right:4px;color:var(--faint)}
"""

def step_block(sid: str, title: str, panels: list[tuple[str, str]]) -> str:
    """panels: list of (caption, svg_inner_or_html)"""
    n = len(panels)
    parts = [
        f'<div class="steps" data-steps id="{sid}">',
        f'<div class="step-nav"><button type="button" data-prev>← prev</button>',
        f'<span class="lbl" data-label>Step 1 / {n} — {title}</span>',
        f'<button type="button" data-next>next →</button></div>',
    ]
    for i, (cap, body) in enumerate(panels):
        on = " on" if i == 0 else ""
        parts.append(f'<div class="step-panel{on}" data-i="{i}">')
        parts.append(body)
        parts.append(f'<p class="step-cap">{cap}</p></div>')
    parts.append("</div>")
    return "\n".join(parts)


def svg_nn_full() -> str:
    return """<svg viewBox="0 0 640 280" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
  <text x="20" y="24" fill="#c62828" font-size="18">Full MLP — big picture</text>
  <text x="40" y="60" fill="#8a8a8a" font-size="14">input</text>
  <text x="200" y="60" fill="#8a8a8a" font-size="14">hidden</text>
  <text x="400" y="60" fill="#8a8a8a" font-size="14">hidden</text>
  <text x="560" y="60" fill="#8a8a8a" font-size="14">output</text>
  <circle cx="60" cy="110" r="14" fill="#fff" stroke="#1f4fa3" stroke-width="2"/><circle cx="60" cy="160" r="14" fill="#fff" stroke="#1f4fa3" stroke-width="2"/><circle cx="60" cy="210" r="14" fill="#fff" stroke="#1f4fa3" stroke-width="2"/>
  <circle cx="220" cy="100" r="14" fill="#fff" stroke="#2e7d32" stroke-width="2"/><circle cx="220" cy="150" r="14" fill="#fff" stroke="#2e7d32" stroke-width="2"/><circle cx="220" cy="200" r="14" fill="#fff" stroke="#2e7d32" stroke-width="2"/><circle cx="220" cy="240" r="14" fill="#fff" stroke="#2e7d32" stroke-width="2"/>
  <circle cx="420" cy="120" r="14" fill="#fff" stroke="#d9822b" stroke-width="2"/><circle cx="420" cy="180" r="14" fill="#fff" stroke="#d9822b" stroke-width="2"/>
  <circle cx="580" cy="150" r="16" fill="#fff1a8" stroke="#c62828" stroke-width="2.5"/>
  <path d="M74 110 L206 100 M74 110 L206 150 M74 160 L206 100 M74 160 L206 200 M74 210 L206 200 M74 210 L206 240" stroke="#1d2b4f" stroke-width="1" opacity=".35"/>
  <path d="M234 100 L406 120 M234 150 L406 120 M234 150 L406 180 M234 200 L406 180" stroke="#1d2b4f" stroke-width="1" opacity=".35"/>
  <path d="M434 120 L564 150 M434 180 L564 150" stroke="#1d2b4f" stroke-width="1.5" opacity=".5"/>
</svg>"""


def svg_nn_input() -> str:
    return """<svg viewBox="0 0 640 240" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
  <text x="20" y="24" fill="#c62828" font-size="18">Step focus: input layer only</text>
  <rect x="20" y="50" width="200" height="160" rx="12" fill="#eef4ff" stroke="#1f4fa3" stroke-width="2"/>
  <text x="40" y="78" fill="#1f4fa3" font-size="16">Raw features → numbers</text>
  <text x="40" y="110" fill="#1d2b4f" font-size="15">x₁ = house size (m²)</text>
  <text x="40" y="135" fill="#1d2b4f" font-size="15">x₂ = # bedrooms</text>
  <text x="40" y="160" fill="#1d2b4f" font-size="15">x₃ = age (years)</text>
  <text x="40" y="190" fill="#8a8a8a" font-size="14">Each becomes one input neuron</text>
  <circle cx="320" cy="100" r="18" fill="#fff" stroke="#1f4fa3" stroke-width="2.5"/><text x="312" y="106" font-size="14">x₁</text>
  <circle cx="320" cy="150" r="18" fill="#fff" stroke="#1f4fa3" stroke-width="2.5"/><text x="312" y="156" font-size="14">x₂</text>
  <circle cx="320" cy="200" r="18" fill="#fff" stroke="#1f4fa3" stroke-width="2.5"/><text x="312" y="206" font-size="14">x₃</text>
  <text x="400" y="150" fill="#8a8a8a" font-size="15">No learning yet — just hold values</text>
</svg>"""


def svg_neuron() -> str:
    return """<svg viewBox="0 0 720 260" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
  <text x="20" y="24" fill="#c62828" font-size="18">One neuron — the X-ray</text>
  <text x="30" y="80" fill="#1f4fa3" font-size="15">inputs</text>
  <circle cx="50" cy="120" r="12" fill="#fff" stroke="#1f4fa3" stroke-width="2"/><text x="42" y="125" font-size="12">x₁</text>
  <circle cx="50" cy="170" r="12" fill="#fff" stroke="#1f4fa3" stroke-width="2"/><text x="42" y="175" font-size="12">x₂</text>
  <text x="90" y="110" fill="#2e7d32" font-size="13">× w₁</text>
  <text x="90" y="160" fill="#2e7d32" font-size="13">× w₂</text>
  <path d="M62 120 L180 145 M62 170 L180 145" stroke="#1d2b4f" stroke-width="1.5"/>
  <rect x="180" y="115" width="150" height="60" rx="10" fill="#fff7d6" stroke="#d9822b" stroke-width="2"/>
  <text x="195" y="140" font-size="14">z = Σ xᵢwᵢ + b</text>
  <text x="195" y="162" font-size="13" fill="#8a8a8a">weighted sum + bias</text>
  <path d="M330 145 L400 145" stroke="#1d2b4f" stroke-width="2" marker-end="url(#a)"/>
  <rect x="400" y="115" width="140" height="60" rx="10" fill="#f3e5f5" stroke="#6a1b9a" stroke-width="2"/>
  <text x="415" y="140" font-size="14">a = σ(z)</text>
  <text x="415" y="162" font-size="13" fill="#8a8a8a">activation</text>
  <path d="M540 145 L600 145" stroke="#1d2b4f" stroke-width="2"/>
  <circle cx="630" cy="145" r="18" fill="#fff1a8" stroke="#c62828" stroke-width="2.5"/>
  <text x="620" y="150" font-size="12">out</text>
  <defs><marker id="a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#1d2b4f"/></marker></defs>
</svg>"""


def svg_forward_nums() -> str:
    return """<svg viewBox="0 0 720 300" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
  <text x="20" y="24" fill="#c62828" font-size="18">Worked numbers — one neuron</text>
  <text x="30" y="70" font-size="16">x = [2, 3]   w = [0.5, −0.2]   b = 0.1</text>
  <text x="30" y="110" font-size="16">z = 2·0.5 + 3·(−0.2) + 0.1 = 1 − 0.6 + 0.1 = <tspan fill="#c62828" font-weight="700">0.5</tspan></text>
  <text x="30" y="150" font-size="16">ReLU(z) = max(0, z) = <tspan fill="#2e7d32" font-weight="700">0.5</tspan></text>
  <text x="30" y="190" font-size="16">Sigmoid(z) = 1/(1+e^(−z)) ≈ <tspan fill="#6a1b9a" font-weight="700">0.62</tspan></text>
  <text x="30" y="240" fill="#8a8a8a" font-size="15">Same z, different activation → different “story” the neuron tells next layers</text>
  <text x="30" y="270" fill="#8a8a8a" font-size="15">If z were −1.2: ReLU→0 (silence). Sigmoid→~0.23 (still a small voice).</text>
</svg>"""


def svg_softmax() -> str:
    return """<svg viewBox="0 0 720 280" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
  <text x="20" y="24" fill="#c62828" font-size="18">Logits → probabilities (softmax)</text>
  <text x="40" y="70" font-size="15">logits z = [2.0, 1.0, 0.1]</text>
  <text x="40" y="100" font-size="15">e^z ≈ [7.39, 2.72, 1.11]</text>
  <text x="40" y="130" font-size="15">sum = 11.22</text>
  <text x="40" y="170" font-size="16">p = e^z / sum ≈ [<tspan fill="#c62828">0.66</tspan>, 0.24, 0.10]</text>
  <rect x="40" y="200" width="264" height="28" fill="#c62828" opacity=".85"/><text x="50" y="220" fill="#fff" font-size="14">cat 0.66</text>
  <rect x="314" y="200" width="96" height="28" fill="#1f4fa3" opacity=".7"/><text x="330" y="220" fill="#fff" font-size="14">dog 0.24</text>
  <rect x="420" y="200" width="48" height="28" fill="#8a8a8a" opacity=".7"/><text x="428" y="220" fill="#fff" font-size="14">bird</text>
  <text x="40" y="260" fill="#8a8a8a" font-size="14">All p ≥ 0 and sum to 1 — a real distribution you can sample or argmax</text>
</svg>"""


def svg_attn_steps() -> list[tuple[str, str]]:
    return [
        ("Q, K, V come from the same tokens (self-attention) via three learned matrices.",
         """<svg viewBox="0 0 700 220" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
         <text x="20" y="28" fill="#c62828" font-size="18">Attention step 1 — make Q, K, V</text>
         <rect x="40" y="60" width="120" height="100" rx="8" fill="#eef4ff" stroke="#1f4fa3" stroke-width="2"/><text x="60" y="115" font-size="15">tokens X</text>
         <text x="180" y="100" font-size="20">→</text>
         <rect x="220" y="50" width="70" height="40" rx="6" fill="#fff1a8" stroke="#c62828"/><text x="240" y="75" font-size="14">Q</text>
         <rect x="220" y="100" width="70" height="40" rx="6" fill="#e8f5e9" stroke="#2e7d32"/><text x="240" y="125" font-size="14">K</text>
         <rect x="220" y="150" width="70" height="40" rx="6" fill="#f3e5f5" stroke="#6a1b9a"/><text x="240" y="175" font-size="14">V</text>
         <text x="320" y="120" fill="#8a8a8a" font-size="14">Q = XW_Q · K = XW_K · V = XW_V</text>
         </svg>"""),
        ("Scores = how much each token should look at every other token (scaled dot product).",
         """<svg viewBox="0 0 700 240" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
         <text x="20" y="28" fill="#c62828" font-size="18">Attention step 2 — scores</text>
         <text x="40" y="80" font-size="16">score(i,j) = (qᵢ · kⱼ) / √d</text>
         <text x="40" y="120" font-size="15">Divide by √d so dots don’t explode as dimensions grow.</text>
         <text x="40" y="160" font-size="15">Causal mask (GPT-style): future tokens get −∞ → after softmax, weight 0.</text>
         <text x="40" y="200" fill="#8a8a8a" font-size="14">Softmax over j → attention weights that sum to 1 for each query i.</text>
         </svg>"""),
        ("Output = weighted mix of values — each token becomes a blend of what it attended to.",
         """<svg viewBox="0 0 700 220" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
         <text x="20" y="28" fill="#c62828" font-size="18">Attention step 3 — mix values</text>
         <text x="40" y="90" font-size="16">outᵢ = Σⱼ  αᵢⱼ · vⱼ</text>
         <text x="40" y="130" font-size="15">αᵢⱼ = softmax(scores)ᵢⱼ</text>
         <text x="40" y="170" fill="#8a8a8a" font-size="14">Multi-head: do this in parallel with different W_Q,W_K,W_V, then concat.</text>
         </svg>"""),
    ]


JS = r"""
document.querySelectorAll('[data-steps]').forEach(root=>{
  const panels=[...root.querySelectorAll('.step-panel')];
  const label=root.querySelector('[data-label]');
  let i=0;
  const show=()=>{
    panels.forEach((p,idx)=>p.classList.toggle('on', idx===i));
    if(label){
      const base=label.textContent.replace(/^Step \d+ \/ \d+ — /,'');
      const title=root.getAttribute('data-title')||base||'';
      label.textContent=`Step ${i+1} / ${panels.length}`+(title?` — ${title}`:'');
    }
  };
  root.querySelector('[data-prev]')?.addEventListener('click',()=>{i=(i-1+panels.length)%panels.length;show();});
  root.querySelector('[data-next]')?.addEventListener('click',()=>{i=(i+1)%panels.length;show();});
  const titleEl=root.querySelector('[data-label]');
  if(titleEl){const m=titleEl.textContent.match(/— (.+)$/); if(m) root.setAttribute('data-title', m[1]);}
  show();
});
if(window.renderMathInElement){
  renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]});
}
"""

def algo_row(name, how, data, out, best, solves):
    return f"<tr><td><b>{name}</b></td><td>{how}</td><td>{data}</td><td>{out}</td><td>{best}</td><td>{solves}</td></tr>"


body_parts = []

body_parts.append("""
<header class="hero">
  <h1>AIML From Scratch <span>→ Agents</span></h1>
  <p class="sub">Teaching notebook — chronological, diagram-heavy, X-ray intuition</p>
  <p class="by">For teaching a friend · use progressive steps like 3Blue1Brown · speak the “In short” first</p>
</header>

<section class="howto">
  <h3>How to teach from this book</h3>
  <ol>
    <li><b>Overview</b> — one sentence: what is this thing?</li>
    <li><b>Purpose</b> — why humans invented it / what pain it kills.</li>
    <li><b>Where it sits</b> — which stage of the pipeline (data → model → loss → deploy).</li>
    <li><b>How it works</b> — the X-ray (click Next on diagrams).</li>
    <li><b>Math</b> — formula + tiny numbers so she sees values move.</li>
    <li><b>Examples</b> — different settings (e.g. temperature 0.2 vs 1.5).</li>
    <li><b>Best for / not for</b> — so she can choose tools, not memorize names.</li>
  </ol>
  <p>Order is intentional: <b>ideas → classical ML → neural nets → sequence models → transformers → generative → alignment/fine-tuning → systems (RAG/agents)</b>.</p>
</section>
""")

# PART 0
body_parts.append("""
<section class="part" id="p0">
  <h2 class="ph">Part 0 — The map</h2>
  <p class="psub">Where everything sits before we zoom in</p>
  <div class="topic">
    <h3>0.1 Nested dolls</h3>
    <div class="one"><span class="onelab">In short</span> AI is the big dream (machines that act smart). ML is the main method (learn from data). DL is ML with deep neural nets. LLMs are deep nets trained as language models. Agents wrap LLMs with tools, memory, and a loop.</div>
""")

body_parts.append(step_block("map", "zoom from AI to agents", [
    ("AI = goal. Many roads (rules, search, ML…).",
     """<svg viewBox="0 0 640 200" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <rect x="120" y="40" width="400" height="120" rx="16" fill="#fff" stroke="#c62828" stroke-width="3"/>
     <text x="280" y="110" font-size="28" fill="#c62828">AI</text>
     </svg>"""),
    ("ML lives inside AI: instead of hand rules, fit a model to examples.",
     """<svg viewBox="0 0 640 220" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <rect x="80" y="30" width="480" height="160" rx="16" fill="#fff" stroke="#c62828" stroke-width="2"/>
     <text x="100" y="60" fill="#c62828" font-size="18">AI</text>
     <rect x="160" y="80" width="320" height="80" rx="12" fill="#eef4ff" stroke="#1f4fa3" stroke-width="2"/>
     <text x="280" y="128" fill="#1f4fa3" font-size="22">ML</text>
     </svg>"""),
    ("Deep learning = neural nets with many layers inside ML.",
     """<svg viewBox="0 0 640 240" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <rect x="60" y="20" width="520" height="200" rx="14" fill="#fff" stroke="#c62828" stroke-width="2"/>
     <text x="80" y="48" fill="#c62828" font-size="16">AI</text>
     <rect x="120" y="60" width="400" height="140" rx="12" fill="#eef4ff" stroke="#1f4fa3" stroke-width="2"/>
     <text x="140" y="88" fill="#1f4fa3" font-size="16">ML</text>
     <rect x="180" y="100" width="280" height="80" rx="10" fill="#e8f5e9" stroke="#2e7d32" stroke-width="2"/>
     <text x="250" y="148" fill="#2e7d32" font-size="20">Deep Learning</text>
     </svg>"""),
    ("LLM + tools + memory + loop = agent (uses everything below).",
     """<svg viewBox="0 0 640 260" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <rect x="40" y="16" width="560" height="228" rx="14" fill="#fff" stroke="#c62828" stroke-width="2"/>
     <text x="60" y="42" fill="#c62828" font-size="15">AI</text>
     <rect x="90" y="54" width="460" height="170" rx="12" fill="#eef4ff" stroke="#1f4fa3" stroke-width="2"/>
     <text x="110" y="78" fill="#1f4fa3" font-size="14">ML / DL / LLM</text>
     <rect x="150" y="100" width="340" height="100" rx="10" fill="#fff1a8" stroke="#d9822b" stroke-width="2.5"/>
     <text x="250" y="145" fill="#d9822b" font-size="22">Agent</text>
     <text x="190" y="175" fill="#8a8a8a" font-size="14">plan → act (tools) → observe → repeat</text>
     </svg>"""),
]))

body_parts.append("</div></section>")

# PART 1 AI
body_parts.append("""
<section class="part" id="p1">
  <h2 class="ph">Part 1 — What is AI?</h2>
  <p class="psub">Definitions without buzzwords</p>
  <div class="topic">
    <h3>1.1 Intelligence as a spectrum</h3>
    <div class="one"><span class="onelab">In short</span> AI systems take inputs from the world (or data), decide or predict, and act or output. Narrow AI does one job well. AGI (not here yet) would generalize like a human across jobs.</div>
    <div class="s-why"><h4>Purpose</h4><ul>
      <li>Automate judgment that used to need a human (spam, routing, translation, diagnosis support).</li>
      <li>Scale expertise: one model can serve millions of queries.</li>
    </ul></div>
    <div class="s-ex"><h4>Teach with</h4><ul>
      <li>Thermostat (rules) vs spam filter (learned) vs ChatGPT (learned language model) — same AI umbrella, different guts.</li>
    </ul></div>
  </div>
  <div class="topic">
    <h3>1.2 Symbolic AI vs learning</h3>
    <div class="one"><span class="onelab">In short</span> Old school: write rules/knowledge graphs. New school: show examples, let an optimizer find the rules as numbers (weights).</div>
    <div class="grid2">
      <div class="card"><h4>Symbolic</h4><p>IF fever AND cough THEN …</p><p>Pros: explainable. Cons: brittle, expensive to write.</p></div>
      <div class="card"><h4>Learning (ML)</h4><p>Data → model → predictions</p><p>Pros: scales. Cons: needs data, can fail silently.</p></div>
    </div>
  </div>
</section>
""")

# PART 2 ML
body_parts.append("""
<section class="part" id="p2">
  <h2 class="ph">Part 2 — Machine Learning landscape</h2>
  <p class="psub">Supervised · Unsupervised · Reinforcement</p>
  <div class="topic">
    <h3>2.1 The three learning styles</h3>
    <div class="one"><span class="onelab">In short</span> Supervised: labeled answers. Unsupervised: find structure with no labels. RL: learn by reward from actions in an environment.</div>
""")

body_parts.append(step_block("learn-styles", "three learning styles", [
    ("Supervised — teacher gave the answer key.",
     """<svg viewBox="0 0 640 200" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <rect x="40" y="50" width="160" height="100" rx="10" fill="#eef4ff" stroke="#1f4fa3" stroke-width="2"/><text x="70" y="105" font-size="16">emails X</text>
     <text x="220" y="105" font-size="22">→</text>
     <rect x="260" y="50" width="140" height="100" rx="10" fill="#fff1a8" stroke="#c62828" stroke-width="2"/><text x="290" y="105" font-size="16">model</text>
     <text x="420" y="105" font-size="22">→</text>
     <rect x="460" y="50" width="140" height="100" rx="10" fill="#e8f5e9" stroke="#2e7d32" stroke-width="2"/><text x="485" y="95" font-size="15">spam / ham</text><text x="490" y="120" font-size="13" fill="#8a8a8a">labels y</text>
     </svg>"""),
    ("Unsupervised — no labels; find clusters or compressions.",
     """<svg viewBox="0 0 640 200" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <circle cx="120" cy="80" r="8" fill="#1f4fa3"/><circle cx="140" cy="95" r="8" fill="#1f4fa3"/><circle cx="110" cy="110" r="8" fill="#1f4fa3"/>
     <circle cx="320" cy="70" r="8" fill="#c62828"/><circle cx="340" cy="90" r="8" fill="#c62828"/><circle cx="300" cy="100" r="8" fill="#c62828"/>
     <circle cx="500" cy="120" r="8" fill="#2e7d32"/><circle cx="520" cy="140" r="8" fill="#2e7d32"/>
     <text x="200" y="180" fill="#8a8a8a" font-size="15">Points group themselves — we never said “these are cluster A”</text>
     </svg>"""),
    ("Reinforcement — agent acts, environment rewards.",
     """<svg viewBox="0 0 640 200" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <rect x="60" y="60" width="120" height="70" rx="10" fill="#fff1a8" stroke="#d9822b" stroke-width="2"/><text x="85" y="100" font-size="16">Agent</text>
     <text x="200" y="95" font-size="14">action</text>
     <rect x="280" y="50" width="160" height="90" rx="10" fill="#eef4ff" stroke="#1f4fa3" stroke-width="2"/><text x="310" y="100" font-size="16">Environment</text>
     <text x="460" y="80" font-size="14">reward</text>
     <text x="460" y="110" font-size="14">new state</text>
     <path d="M180 95 L275 95 M440 95 L520 95 L520 130 L180 130 L180 110" fill="none" stroke="#1d2b4f" stroke-width="1.5"/>
     </svg>"""),
]))

body_parts.append("""
    <table class="algo">
      <tr><th>Style</th><th>Needs</th><th>Example</th><th>Success looks like</th></tr>
      <tr><td>Supervised</td><td>(x, y) pairs</td><td>Image → cat/dog</td><td>Low error on held-out y</td></tr>
      <tr><td>Unsupervised</td><td>only x</td><td>Customer segments</td><td>Useful structure / compression</td></tr>
      <tr><td>RL</td><td>env + reward</td><td>Game / robot / RLHF</td><td>High cumulative reward</td></tr>
    </table>
  </div>
</section>
""")

# PART 3 algorithms
body_parts.append("""
<section class="part" id="p3">
  <h2 class="ph">Part 3 — Classical algorithms</h2>
  <p class="psub">What each does · toy data · output · when to use</p>
  <div class="topic">
    <h3>3.1 Supervised menu</h3>
    <div class="one"><span class="onelab">In short</span> Start here before neural nets. Many business problems still win with these.</div>
    <table class="algo">
      <tr><th>Algorithm</th><th>How (intuition)</th><th>Toy dataset</th><th>Output</th><th>Best for</th><th>Solves</th></tr>
""")

body_parts.append(algo_row(
    "Linear regression",
    "Fit a line/plane: ŷ = w·x + b by minimizing squared error",
    "House size → price",
    "Continuous number",
    "Trends, baselines",
    "Predict a quantity",
))
body_parts.append(algo_row(
    "Logistic regression",
    "Linear score → sigmoid → probability of class",
    "Hours studied → pass/fail",
    "Probability / class",
    "Binary classification baseline",
    "Yes/no with calibrated probs",
))
body_parts.append(algo_row(
    "k-NN",
    "Look at k nearest training points; vote or average",
    "2D points with labels",
    "Class or average y",
    "Simple nonlinear boundaries",
    "Lazy learning, few assumptions",
))
body_parts.append(algo_row(
    "Decision tree",
    "Ask yes/no feature questions until a leaf",
    "Loan age, income → approve",
    "Class / value at leaf",
    "Explainable rules",
    "Interpretable decisions",
))
body_parts.append(algo_row(
    "Random forest",
    "Many trees on random subsets; average/vote",
    "Tabular features",
    "Class / number",
    "Strong tabular baseline",
    "Accuracy + robustness",
))
body_parts.append(algo_row(
    "Gradient boosting (XGBoost…)",
    "Add trees that fix previous trees’ errors",
    "Kaggle-style tables",
    "Class / number",
    "Best classic tabular ML",
    "Max accuracy on tables",
))
body_parts.append(algo_row(
    "SVM",
    "Find max-margin separator (kernel for curves)",
    "2-class blobs",
    "Class / side of margin",
    "Medium data, clear margin",
    "Separation with geometry",
))
body_parts.append(algo_row(
    "Naive Bayes",
    "Assume features independent; multiply likelihoods",
    "Word counts → spam",
    "Class probs",
    "Text baselines, speed",
    "Fast probabilistic classify",
))

body_parts.append("""
    </table>
  </div>
  <div class="topic">
    <h3>3.2 Unsupervised menu</h3>
    <table class="algo">
      <tr><th>Algorithm</th><th>How</th><th>Toy data</th><th>Output</th><th>Best for</th><th>Solves</th></tr>
""")
body_parts.append(algo_row("k-means", "Pick k centers; assign points; move centers; repeat", "2D blobs", "Cluster id + centers", "Segmentation", "Group similar items"))
body_parts.append(algo_row("Hierarchical clustering", "Merge closest clusters into a tree (dendrogram)", "Small distance matrix", "Tree of merges", "Taxonomies", "Multi-level grouping"))
body_parts.append(algo_row("PCA", "Find directions of most variance; project down", "Correlated features", "Lower-D coords", "Compression, viz", "Remove redundancy"))
body_parts.append(algo_row("t-SNE / UMAP", "Preserve local neighborhoods in 2D/3D", "Embeddings", "2D plot", "Visualization only", "See structure (not for downstream blindly)"))
body_parts.append("""
    </table>
  </div>
  <div class="topic">
    <h3>3.3 RL core ideas (before RLHF)</h3>
    <div class="one"><span class="onelab">In short</span> Policy π(a|s) chooses actions. Value tells expected future reward. Algorithms either learn values (Q-learning) or push the policy uphill (policy gradient / PPO).</div>
    <div class="s-ex"><ul>
      <li><b>State</b> — what the agent sees now.</li>
      <li><b>Action</b> — what it can do.</li>
      <li><b>Reward</b> — scalar feedback (can be sparse!).</li>
      <li><b>Episode</b> — one playthrough until done.</li>
    </ul></div>
  </div>
</section>
""")

# PART 4 NN - the big one
body_parts.append("""
<section class="part" id="p4">
  <h2 class="ph">Part 4 — Neural networks (X-ray)</h2>
  <p class="psub">Layers · neurons · activations · logits · softmax · loss · gradients · optimizers</p>

  <div class="topic">
    <h3>4.1 Big picture then zoom</h3>
    <div class="one"><span class="onelab">In short</span> A neural net is stacked differentiable functions. Data enters as numbers, each layer transforms them, the last layer outputs scores (logits). Training nudges millions of weights so the scores match reality.</div>
""")

body_parts.append(step_block("nn-zoom", "MLP layer by layer", [
    ("Whole network — don’t teach details yet; just the pipeline.", svg_nn_full()),
    ("Input layer only — features become neurons that hold values.", svg_nn_input()),
    ("Add first hidden layer — every input connects to every hidden neuron (dense).",
     """<svg viewBox="0 0 640 260" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <text x="20" y="24" fill="#c62828" font-size="18">Input → first hidden (fully connected)</text>
     <circle cx="80" cy="80" r="14" fill="#fff" stroke="#1f4fa3" stroke-width="2"/>
     <circle cx="80" cy="140" r="14" fill="#fff" stroke="#1f4fa3" stroke-width="2"/>
     <circle cx="80" cy="200" r="14" fill="#fff" stroke="#1f4fa3" stroke-width="2"/>
     <circle cx="320" cy="70" r="16" fill="#e8f5e9" stroke="#2e7d32" stroke-width="2.5"/>
     <circle cx="320" cy="130" r="16" fill="#e8f5e9" stroke="#2e7d32" stroke-width="2.5"/>
     <circle cx="320" cy="190" r="16" fill="#e8f5e9" stroke="#2e7d32" stroke-width="2.5"/>
     <path d="M94 80 L304 70 M94 80 L304 130 M94 80 L304 190 M94 140 L304 70 M94 140 L304 130 M94 140 L304 190 M94 200 L304 70 M94 200 L304 130 M94 200 L304 190" stroke="#1d2b4f" opacity=".35"/>
     <text x="400" y="140" fill="#8a8a8a" font-size="14">Each green neuron: its own w’s and b</text>
     </svg>"""),
    ("One neuron X-ray — weighted sum then activation.", svg_neuron()),
    ("Real numbers so she sees updates aren’t magic.", svg_forward_nums()),
]))

body_parts.append("""
  </div>

  <div class="topic">
    <h3>4.2 What is a neuron “firing”?</h3>
    <div class="one"><span class="onelab">In short</span> Biologically inspired metaphor: if the weighted sum is strong enough, the activation is large (“fires”). In ReLU, negative z → exact 0 (silent). In sigmoid, always a soft number between 0 and 1.</div>
    <div class="s-math"><h4>Math</h4>
      <div class="formula">z = w₁x₁ + w₂x₂ + … + b<br>a = f(z)</div>
      <ul>
        <li><b>Weights w</b> — strength of each incoming wire (learned).</li>
        <li><b>Bias b</b> — “default mood” of the neuron (learned).</li>
        <li><b>Activation f</b> — nonlinearity so stacked layers aren’t just one big linear map.</li>
      </ul>
    </div>
  </div>

  <div class="topic">
    <h3>4.3 Activation functions</h3>
    <div class="grid2">
      <div class="card"><h4>Sigmoid σ(z)=1/(1+e^(−z))</h4>
        <p><b>Purpose:</b> squash to (0,1) — classic for probabilities / gates.</p>
        <p><b>Effect:</b> saturates for |z| large → tiny gradients (vanishing).</p>
        <p><b>Example:</b> z=0 → 0.5; z=2 → ~0.88; z=−2 → ~0.12</p>
      </div>
      <div class="card"><h4>ReLU f(z)=max(0,z)</h4>
        <p><b>Purpose:</b> cheap nonlinearity for deep nets.</p>
        <p><b>Effect:</b> negative side off; positive side identity → sparse activations.</p>
        <p><b>Example:</b> z=0.5 → 0.5; z=−1.2 → 0</p>
      </div>
      <div class="card"><h4>Tanh</h4>
        <p>Like sigmoid but (−1,1); zero-centered.</p>
      </div>
      <div class="card"><h4>GELU / SiLU</h4>
        <p>Smooth ReLU cousins used in modern transformers.</p>
      </div>
    </div>
  </div>

  <div class="topic">
    <h3>4.4 Output layer → logits → probabilities → choice</h3>
    <div class="one"><span class="onelab">In short</span> Last layer usually outputs raw scores (logits). Softmax turns them into a probability distribution. Then we either take argmax (greedy) or sample (with temperature / top-k / top-p).</div>
""")

body_parts.append(step_block("decode", "from logits to a decision", [
    ("Logits are unbounded scores — not yet probabilities.",
     """<svg viewBox="0 0 640 180" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <text x="40" y="50" font-size="16">Class scores (logits): cat=2.0, dog=1.0, bird=0.1</text>
     <text x="40" y="90" fill="#8a8a8a" font-size="15">Bigger = model “likes” that class more — but not a %</text>
     <text x="40" y="130" fill="#8a8a8a" font-size="15">Same idea in LLMs: one logit per vocabulary token</text>
     </svg>"""),
    ("Softmax = exp then normalize so they sum to 1.", svg_softmax()),
    ("Choosing the next token / class — techniques",
     """<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <text x="20" y="28" fill="#c62828" font-size="18">Selection techniques</text>
     <text x="40" y="70" font-size="15"><tspan font-weight="700">Argmax / greedy</tspan> — always pick max p. Stable, dull, repetitive.</text>
     <text x="40" y="105" font-size="15"><tspan font-weight="700">Temperature T</tspan> — use softmax(z/T). T→0 sharper; T↑ flatter/random.</text>
     <text x="40" y="140" font-size="15"><tspan font-weight="700">Top-k</tspan> — keep k largest, renormalize, sample.</text>
     <text x="40" y="175" font-size="15"><tspan font-weight="700">Top-p (nucleus)</tspan> — keep smallest set with cumulative p≥p, sample.</text>
     <text x="40" y="220" fill="#8a8a8a" font-size="14">Teach temperature with same logits at T=0.2 vs T=1.5 — watch probs change.</text>
     </svg>"""),
]))

body_parts.append("""
    <div class="s-math"><h4>Temperature math (teach carefully)</h4>
      <div class="formula">pᵢ = exp(zᵢ / T) / Σⱼ exp(zⱼ / T)</div>
      <ul>
        <li><b>Does NOT update weights.</b> Temperature is inference-time only (unless you use it in distillation loss).</li>
        <li><b>Role:</b> reshape the distribution before sampling.</li>
        <li><b>T=1:</b> default softmax. <b>T&lt;1:</b> more confident/peaky. <b>T&gt;1:</b> more creative/chaotic.</li>
      </ul>
    </div>
    <div class="s-ex"><h4>Mini demo for her</h4>
      <p>Logits [2,1,0.1]:</p>
      <ul>
        <li>T=0.5 → probs ≈ even more peaked on first class</li>
        <li>T=2 → probs closer together → sampling jumps classes more</li>
      </ul>
    </div>
  </div>

  <div class="topic">
    <h3>4.5 Loss — how wrong are we?</h3>
    <div class="one"><span class="onelab">In short</span> Loss is a single number: “how unhappy is the model on this batch?” Training = change weights to make loss smaller.</div>
    <div class="grid2">
      <div class="card"><h4>MSE</h4><p>(ŷ−y)² — regression.</p></div>
      <div class="card"><h4>Binary cross-entropy</h4><p>−[y log p + (1−y)log(1−p)]</p></div>
      <div class="card"><h4>Cross-entropy (multi-class / LM)</h4><p>−log p<sub>correct</sub> — if true class has prob 0.66, loss = −log(0.66)≈0.42</p></div>
      <div class="card"><h4>NLL</h4><p>Same family; CE often = softmax + NLL fused.</p></div>
    </div>
    <div class="s-trap"><h4>Trap</h4><p>Never put softmax before <code>CrossEntropyLoss</code> in PyTorch — CE expects raw logits.</p></div>
  </div>

  <div class="topic">
    <h3>4.6 Gradients &amp; backpropagation</h3>
    <div class="one"><span class="onelab">In short</span> Gradient ∂L/∂w says: if I nudge this weight up a tiny bit, how does loss change? Backprop applies the chain rule from the loss backward through every layer so each weight gets its gradient.</div>
""")

body_parts.append(step_block("backprop", "forward then backward", [
    ("Forward: compute activations left → right, remember them.",
     """<svg viewBox="0 0 640 160" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <text x="40" y="50" font-size="16">x → h₁ → h₂ → logits → loss L</text>
     <text x="40" y="100" fill="#8a8a8a" font-size="15">Store h’s — backward will need them</text>
     </svg>"""),
    ("Backward: send error signal right → left; each w gets ∂L/∂w.",
     """<svg viewBox="0 0 640 160" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <text x="40" y="50" font-size="16">L → ∂L/∂logits → ∂L/∂h₂ → ∂L/∂h₁ → ∂L/∂w</text>
     <text x="40" y="100" fill="#8a8a8a" font-size="15">Chain rule: multiply local derivatives along the path</text>
     </svg>"""),
    ("Update: w ← w − η · ∂L/∂w (gradient descent).",
     """<svg viewBox="0 0 640 180" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <text x="40" y="50" font-size="16">η = learning rate (step size)</text>
     <text x="40" y="90" font-size="15">Too big η → overshoot / diverge. Too small → crawl.</text>
     <text x="40" y="130" fill="#8a8a8a" font-size="14">This is how weights actually “learn” from data</text>
     </svg>"""),
]))

body_parts.append("""
  </div>

  <div class="topic">
    <h3>4.7 Optimizers</h3>
    <div class="one"><span class="onelab">In short</span> Optimizers decide how to use gradients to update weights. SGD is the pure idea. Momentum remembers velocity. Adam adapts step size per parameter.</div>
    <table class="algo">
      <tr><th>Optimizer</th><th>Idea</th><th>Best for</th></tr>
      <tr><td>SGD</td><td>w ← w − η g</td><td>Simple, controllable; often + momentum</td></tr>
      <tr><td>SGD + momentum</td><td>Accumulate velocity in consistent directions</td><td>Vision classics</td></tr>
      <tr><td>Adam / AdamW</td><td>Per-weight adaptive rates + (AdamW) decoupled weight decay</td><td>Transformers, default fine-tunes</td></tr>
      <tr><td>RMSprop</td><td>Scale by running avg of squared grads</td><td>Some RNNs / older recipes</td></tr>
    </table>
    <div class="s-why"><h4>Related knobs</h4><ul>
      <li><b>Batch size</b> — how many examples per gradient estimate.</li>
      <li><b>Epoch</b> — one pass over the training set.</li>
      <li><b>Learning rate schedule</b> — warmup then decay.</li>
      <li><b>Weight decay</b> — penalize large weights (regularization).</li>
      <li><b>Gradient clipping</b> — cap huge gradients so training doesn’t explode.</li>
    </ul></div>
  </div>

  <div class="topic">
    <h3>4.8 Data ingestion by type</h3>
    <table class="algo">
      <tr><th>Data</th><th>Becomes numbers via</th><th>Typical first layer</th></tr>
      <tr><td>Tabular</td><td>Normalize / encode categories</td><td>Dense (Linear)</td></tr>
      <tr><td>Images</td><td>Pixels CHW floats 0–1</td><td>Conv2d</td></tr>
      <tr><td>Text</td><td>Tokenizer → token IDs → embedding vectors</td><td>Embedding lookup</td></tr>
      <tr><td>Audio</td><td>Waveform / spectrogram</td><td>Conv1d / spectrogram encoder</td></tr>
    </table>
  </div>
</section>
""")

# PART 5 CNN RNN
body_parts.append("""
<section class="part" id="p5">
  <h2 class="ph">Part 5 — CNN &amp; RNN</h2>
  <p class="psub">Spatial patterns · sequences before transformers</p>
  <div class="topic">
    <h3>5.1 CNN</h3>
    <div class="one"><span class="onelab">In short</span> Convolutions slide small filters over the image to detect local patterns (edges → textures → objects). Weight sharing = same filter reused everywhere.</div>
    <div class="s-why"><ul>
      <li><b>Solves:</b> vision where nearby pixels matter together.</li>
      <li><b>Key terms:</b> kernel, stride, padding, channel, pooling.</li>
    </ul></div>
  </div>
  <div class="topic">
    <h3>5.2 RNN / LSTM / GRU</h3>
    <div class="one"><span class="onelab">In short</span> RNNs read a sequence step by step, carrying a hidden state. LSTMs/GRUs add gates so memory can last longer. Transformers mostly replaced them for NLP, but the idea “state over time” still matters.</div>
    <div class="s-trap"><h4>Limits</h4><p>Sequential = slow to train; long-range memory is hard (vanishing gradients) — motivation for attention.</p></div>
  </div>
</section>
""")

# PART 6 Transformer
body_parts.append("""
<section class="part" id="p6">
  <h2 class="ph">Part 6 — Transformers &amp; attention</h2>
  <p class="psub">The architecture behind modern LLMs</p>
  <div class="topic">
    <h3>6.1 Why attention</h3>
    <div class="one"><span class="onelab">In short</span> Instead of compressing the whole past into one RNN state, each token can look at every other token (with weights) in parallel.</div>
""")

body_parts.append(step_block("attn", "attention mechanism", svg_attn_steps()))

body_parts.append("""
  </div>
  <div class="topic">
    <h3>6.2 Transformer block</h3>
    <div class="one"><span class="onelab">In short</span> Block ≈ Attention + MLP, each with residual connection and layer norm. Stack many blocks. Decoder-only (GPT) uses causal mask; encoder (BERT) can see both sides.</div>
    <ul>
      <li><b>Embeddings</b> + <b>positional</b> info (sin/cos, learned, or RoPE).</li>
      <li><b>Multi-head attention</b> — several attention “views” in parallel.</li>
      <li><b>FFN / MLP</b> — expands then shrinks features per token.</li>
      <li><b>Residuals</b> — add input to output so gradients flow.</li>
    </ul>
  </div>
  <div class="topic">
    <h3>6.3 Language modeling objective</h3>
    <div class="one"><span class="onelab">In short</span> Train by predicting the next token. Loss = cross-entropy of the true next token. Do this on trillions of tokens → a base LLM.</div>
  </div>
</section>
""")

# PART 7 diffusion
body_parts.append("""
<section class="part" id="p7">
  <h2 class="ph">Part 7 — Diffusion (generative beyond LLMs)</h2>
  <p class="psub">Images / audio — brief but clear</p>
  <div class="topic">
    <h3>7.1 Noise then denoise</h3>
    <div class="one"><span class="onelab">In short</span> Training: gradually add noise to real data, teach a net to predict the noise (or clean signal). Sampling: start from pure noise, iteratively denoise into an image.</div>
    <div class="s-why"><p><b>Role vs LLMs:</b> LLMs generate discrete tokens autoregressively. Diffusion generates continuous signals by reversing a noise process.</p></div>
  </div>
</section>
""")

# PART 8 fine-tuning
body_parts.append("""
<section class="part" id="p8">
  <h2 class="ph">Part 8 — Fine-tuning &amp; alignment</h2>
  <p class="psub">SFT · LoRA · QLoRA · RLHF / DPO</p>
  <div class="topic">
    <h3>8.1 Full fine-tune vs PEFT</h3>
    <div class="one"><span class="onelab">In short</span> Full FT updates all weights (expensive). PEFT freezes the base model and trains tiny adapters.</div>
  </div>
  <div class="topic">
    <h3>8.2 LoRA</h3>
    <div class="one"><span class="onelab">In short</span> For a weight matrix W, learn low-rank update ΔW = BA with rank r ≪ dimensions. Store/train only A and B.</div>
    <div class="s-math"><div class="formula">W' = W + (α/r) · B A</div>
    <ul>
      <li><b>Purpose:</b> cheap task adaptation, many adapters per base model.</li>
      <li><b>Does:</b> steer behavior without rewriting all of W.</li>
    </ul></div>
  </div>
  <div class="topic">
    <h3>8.3 QLoRA</h3>
    <div class="one"><span class="onelab">In short</span> Keep base weights 4-bit quantized in memory; train LoRA adapters in higher precision. Fits big models on one GPU.</div>
  </div>
  <div class="topic">
    <h3>8.4 SFT → preference optimization</h3>
    <ul>
      <li><b>SFT</b> — supervised fine-tune on instruction demos.</li>
      <li><b>RLHF</b> — reward model from preferences + RL (PPO) on the policy.</li>
      <li><b>DPO</b> — preference optimization without a separate RL loop (simpler).</li>
    </ul>
    <div class="s-ex"><p>Teach path: Base LM → SFT chatbot → (optional) preference stage so it prefers helpful/harmless answers.</p></div>
  </div>
</section>
""")

# PART 9 systems
body_parts.append("""
<section class="part" id="p9">
  <h2 class="ph">Part 9 — RAG, tools, agents</h2>
  <p class="psub">From model → product</p>
  <div class="topic">
    <h3>9.1 Embeddings &amp; RAG</h3>
    <div class="one"><span class="onelab">In short</span> Embed text as vectors; retrieve nearest chunks; stuff them into the prompt; generate. Grounds the LLM in your docs.</div>
""")

body_parts.append(step_block("rag", "RAG pipeline", [
    ("Index time: chunk docs → embed → store in vector DB.",
     """<svg viewBox="0 0 640 160" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <text x="40" y="70" font-size="16">Docs → chunks → embeddings → vector index</text>
     </svg>"""),
    ("Query time: embed question → nearest chunks → prompt → answer.",
     """<svg viewBox="0 0 640 180" xmlns="http://www.w3.org/2000/svg" font-family="Patrick Hand, Comic Sans MS, cursive">
     <text x="40" y="60" font-size="15">question → retrieve top-k → [context + question] → LLM → answer</text>
     <text x="40" y="110" fill="#8a8a8a" font-size="14">Failures: bad chunking, weak retrieve, ignored context, hallucination anyway</text>
     </svg>"""),
]))

body_parts.append("""
  </div>
  <div class="topic">
    <h3>9.2 Agents</h3>
    <div class="one"><span class="onelab">In short</span> An agent loops: think → call a tool (search, code, API) → observe result → repeat until done. The LLM is the brain; tools are hands.</div>
    <ul>
      <li><b>ReAct</b> — interleave reasoning traces and actions.</li>
      <li><b>Memory</b> — short-term chat vs long-term store.</li>
      <li><b>Guardrails</b> — allowlists, human approval, groundedness checks.</li>
    </ul>
  </div>
</section>
""")

# PART 10 teaching checklist
body_parts.append("""
<section class="part" id="p10">
  <h2 class="ph">Part 10 — Session plans for you</h2>
  <p class="psub">Suggested teaching order by week</p>
  <div class="topic">
    <ol>
      <li><b>Week 1:</b> Parts 0–2 + linear/logistic intuition with paper numbers.</li>
      <li><b>Week 2:</b> Trees/forests/boosting + unsupervised clustering/PCA.</li>
      <li><b>Week 3–4:</b> Part 4 entire NN X-ray with the worked neuron + CE + SGD vs Adam.</li>
      <li><b>Week 5:</b> CNN/RNN stories + why attention won.</li>
      <li><b>Week 6:</b> Transformer + LM loss + decoding (temperature lab).</li>
      <li><b>Week 7:</b> LoRA/QLoRA/RLHF map.</li>
      <li><b>Week 8:</b> RAG + agent loop on a tiny toy tool.</li>
    </ol>
    <p class="s-why">For every topic, force one <b>numeric toy example</b> on the whiteboard. If she can predict the next number, she owns it.</p>
  </div>
</section>
""")

toc = """
<nav id="toc">
  <div class="brand">AIML Teaching TOC</div>
  <div class="g">Start</div>
  <a href="#p0">0. The map</a>
  <a href="#p1">1. What is AI</a>
  <a href="#p2">2. ML landscape</a>
  <a href="#p3">3. Classical algorithms</a>
  <div class="g">Deep learning</div>
  <a href="#p4">4. Neural nets X-ray</a>
  <a href="#p5">5. CNN & RNN</a>
  <a href="#p6">6. Transformers</a>
  <a href="#p7">7. Diffusion</a>
  <div class="g">Modern stack</div>
  <a href="#p8">8. Fine-tuning</a>
  <a href="#p9">9. RAG & agents</a>
  <a href="#p10">10. Session plans</a>
</nav>
"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AIML From Scratch → Agents — Teaching Notebook</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;700&family=Kalam:wght@400;700&family=Patrick+Hand&family=IBM+Plex+Mono&display=swap">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="if(window.renderMathInElement)renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}]}});"></script>
<style>{CSS}</style>
</head>
<body>
<div class="layout">
{toc}
<main>
{''.join(body_parts)}
</main>
</div>
<script>{JS}</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print("Wrote", OUT, "bytes", OUT.stat().st_size)
