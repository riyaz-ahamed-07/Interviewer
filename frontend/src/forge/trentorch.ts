export type TrenTorchModule = {
  id: string;
  title: string;
  slug: string;
  count: number;
  phase: 1 | 2 | 3 | 4 | 5 | 6;
  aimlPhase: string;
};

export const TRENTORCH_MODULES: TrenTorchModule[] = [
  {
    id: "tt.python",
    title: "Python for Engineers",
    slug: "part-python",
    count: 121,
    phase: 1,
    aimlPhase: "Phase 1 · Programming",
  },
  {
    id: "tt.math",
    title: "Mathematics for ML",
    slug: "part-mathematics",
    count: 64,
    phase: 1,
    aimlPhase: "Phase 1 · Math",
  },
  {
    id: "tt.ds",
    title: "Data Science",
    slug: "part-data-science",
    count: 135,
    phase: 1,
    aimlPhase: "Phase 1 · Data",
  },
  {
    id: "tt.cml",
    title: "Classical ML",
    slug: "part-classical-ml",
    count: 165,
    phase: 2,
    aimlPhase: "Phase 2 · Classical ML",
  },
  {
    id: "tt.dl",
    title: "Deep Learning",
    slug: "part-deep-learning",
    count: 152,
    phase: 3,
    aimlPhase: "Phase 3–4 · DL",
  },
  {
    id: "tt.llm",
    title: "Language Modelling, Attention & LLMs",
    slug: "part-language-modelling-attention-llms",
    count: 137,
    phase: 4,
    aimlPhase: "Phase 4–6 · Transformers / LLMs",
  },
  {
    id: "tt.rl",
    title: "Reinforcement Learning",
    slug: "part-reinforcement-learning",
    count: 61,
    phase: 5,
    aimlPhase: "Phase 6 · RL / Alignment",
  },
  {
    id: "tt.cv",
    title: "Computer Vision",
    slug: "part-computer-vision",
    count: 67,
    phase: 4,
    aimlPhase: "Phase 5 · CV",
  },
  {
    id: "tt.agents",
    title: "Agentic & GenAI",
    slug: "part-agentic-systems",
    count: 55,
    phase: 5,
    aimlPhase: "Phase 6 · Agents",
  },
  {
    id: "tt.dist",
    title: "Distributed Systems",
    slug: "part-distributed-systems",
    count: 48,
    phase: 5,
    aimlPhase: "Phase 7–8 · Systems",
  },
  {
    id: "tt.prod",
    title: "Production & Reliability",
    slug: "part-production-reliability",
    count: 32,
    phase: 5,
    aimlPhase: "Phase 7 · MLOps",
  },
  {
    id: "tt.papers",
    title: "Research Papers",
    slug: "part-research-papers",
    count: 360,
    phase: 6,
    aimlPhase: "Phase 9 · Papers",
  },
];

export function trentorchUrl(slug: string) {
  return `https://trentorch.com/questions/${slug}`;
}
