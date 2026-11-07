import type { Pillar, ForgeNode } from "./types";

const n = (
  id: string,
  title: string,
  children?: ForgeNode[],
  extra?: Partial<ForgeNode>,
): ForgeNode => ({
  id,
  title,
  xp: children?.length ? undefined : (extra?.xp ?? 12),
  phase: extra?.phase,
  children,
});

export const PILLARS: Pillar[] = [
  {
    id: "math",
    title: "Math & Numerical Foundations",
    blurb: "The language behind every model and optimizer.",
    accent: "#1f4fa3",
    roots: [
      n(
        "math.linalg",
        "Linear algebra",
        [
          n("math.linalg.vectors", "Vectors", [
            n("math.linalg.vectors.dot", "Dot product"),
            n("math.linalg.vectors.norm", "Norms (L1, L2, infinity)"),
            n("math.linalg.vectors.proj", "Projection"),
            n("math.linalg.vectors.ortho", "Orthogonality"),
          ]),
          n("math.linalg.matrices", "Matrices", [
            n("math.linalg.matrices.mul", "Matrix multiplication"),
            n("math.linalg.matrices.transpose", "Transpose"),
            n("math.linalg.matrices.inverse", "Inverse & singularity"),
            n("math.linalg.matrices.rank", "Rank & column space"),
            n("math.linalg.matrices.det", "Determinant"),
            n("math.linalg.matrices.trace", "Trace"),
          ]),
          n("math.linalg.eig", "Eigen stuff", [
            n("math.linalg.eig.values", "Eigenvalues / eigenvectors"),
            n("math.linalg.eig.diag", "Diagonalization"),
            n("math.linalg.eig.svd", "SVD"),
            n("math.linalg.eig.pca", "PCA link"),
          ]),
          n("math.linalg.shapes", "Broadcasting & tensor shapes"),
        ],
        { phase: 1 },
      ),
      n(
        "math.calc",
        "Calculus",
        [
          n("math.calc.deriv", "Derivatives", [
            n("math.calc.deriv.chain", "Chain rule"),
            n("math.calc.deriv.product", "Product / quotient"),
            n("math.calc.deriv.partial", "Partial derivatives"),
            n("math.calc.deriv.grad", "Gradient"),
            n("math.calc.deriv.jacobian", "Jacobian"),
            n("math.calc.deriv.hessian", "Hessian"),
          ]),
          n("math.calc.opt", "Optimization view", [
            n("math.calc.opt.gd", "Gradient descent intuition"),
            n("math.calc.opt.lr", "Learning rate geometry"),
            n("math.calc.opt.saddle", "Local minima / saddles"),
          ]),
        ],
        { phase: 1 },
      ),
      n(
        "math.prob",
        "Probability & statistics",
        [
          n("math.prob.basics", "Basics", [
            n("math.prob.basics.rv", "Random variables"),
            n("math.prob.basics.expect", "Expectation / variance"),
            n("math.prob.basics.cov", "Covariance / correlation"),
            n("math.prob.basics.bayes", "Bayes rule"),
            n("math.prob.basics.cond", "Conditional probability"),
          ]),
          n("math.prob.dist", "Distributions", [
            n("math.prob.dist.bernoulli", "Bernoulli / Binomial"),
            n("math.prob.dist.gauss", "Gaussian"),
            n("math.prob.dist.cat", "Categorical / Multinomial"),
            n("math.prob.dist.poisson", "Poisson"),
          ]),
          n("math.prob.stats", "Stats for ML", [
            n("math.prob.stats.mle", "MLE"),
            n("math.prob.stats.map", "MAP"),
            n("math.prob.stats.ci", "Confidence intervals"),
            n("math.prob.stats.hypothesis", "Hypothesis testing basics"),
            n("math.prob.stats.kl", "KL divergence"),
            n("math.prob.stats.entropy", "Entropy / cross-entropy"),
          ]),
        ],
        { phase: 1 },
      ),
      n(
        "math.num",
        "Numerical computing",
        [
          n("math.num.float", "Floating point & precision"),
          n("math.num.stability", "Numerical stability"),
          n("math.num.numpy", "NumPy fluency", [
            n("math.num.numpy.broadcast", "Broadcasting rules"),
            n("math.num.numpy.einsum", "einsum"),
            n("math.num.numpy.vectorize", "Vectorization vs loops"),
          ]),
        ],
        { phase: 1 },
      ),
    ],
  },
  {
    id: "ml",
    title: "Classical Machine Learning",
    blurb: "Before transformers — the algorithms that still ship.",
    accent: "#2e7d32",
    roots: [
      n(
        "ml.super",
        "Supervised learning",
        [
          n("ml.super.reg", "Regression", [
            n("ml.super.reg.linear", "Linear regression"),
            n("ml.super.reg.ridge", "Ridge / Lasso"),
            n("ml.super.reg.poly", "Polynomial features"),
            n("ml.super.reg.metrics", "MSE / MAE / R²"),
          ]),
          n("ml.super.clf", "Classification", [
            n("ml.super.clf.logistic", "Logistic regression"),
            n("ml.super.clf.svm", "SVM"),
            n("ml.super.clf.knn", "k-NN"),
            n("ml.super.clf.nb", "Naive Bayes"),
            n("ml.super.clf.metrics", "Precision / recall / F1 / ROC-AUC"),
          ]),
          n("ml.super.trees", "Trees & ensembles", [
            n("ml.super.trees.dt", "Decision trees"),
            n("ml.super.trees.bag", "Bagging"),
            n("ml.super.trees.rf", "Random Forest"),
            n("ml.super.trees.boost", "Boosting idea"),
            n("ml.super.trees.xgb", "XGBoost / LightGBM intuition"),
          ]),
        ],
        { phase: 1 },
      ),
      n(
        "ml.unsup",
        "Unsupervised",
        [
          n("ml.unsup.kmeans", "K-means"),
          n("ml.unsup.gmm", "GMM"),
          n("ml.unsup.pca", "PCA"),
          n("ml.unsup.iforest", "Isolation Forest"),
          n("ml.unsup.dbscan", "DBSCAN"),
        ],
        { phase: 1 },
      ),
      n(
        "ml.theory",
        "Learning theory practice",
        [
          n("ml.theory.biasvar", "Bias–variance"),
          n("ml.theory.overfit", "Overfitting / underfitting"),
          n("ml.theory.reg", "Regularization"),
          n("ml.theory.cv", "Cross-validation"),
          n("ml.theory.leak", "Data leakage"),
          n("ml.theory.features", "Feature engineering"),
          n("ml.theory.imbalance", "Class imbalance"),
        ],
        { phase: 1 },
      ),
    ],
  },
  {
    id: "dl",
    title: "Deep Learning & PyTorch",
    blurb: "Implement, train, debug — not just name the layers.",
    accent: "#c62828",
    roots: [
      n(
        "dl.nn",
        "Neural nets from scratch",
        [
          n("dl.nn.perceptron", "Perceptron"),
          n("dl.nn.mlp", "MLP"),
          n("dl.nn.forward", "Forward pass"),
          n("dl.nn.loss", "Loss surfaces"),
          n("dl.nn.backprop", "Backpropagation"),
          n("dl.nn.autograd", "Autograd mental model"),
        ],
        { phase: 1 },
      ),
      n(
        "dl.opt",
        "Optimizers & training",
        [
          n("dl.opt.sgd", "SGD"),
          n("dl.opt.momentum", "Momentum"),
          n("dl.opt.adam", "Adam / AdamW"),
          n("dl.opt.sched", "LR schedules"),
          n("dl.opt.init", "Weight init"),
          n("dl.opt.batchnorm", "BatchNorm / LayerNorm"),
          n("dl.opt.dropout", "Dropout"),
          n("dl.opt.gradclip", "Gradient clipping"),
          n("dl.opt.debug", "Training debugging checklist"),
        ],
        { phase: 2 },
      ),
      n(
        "dl.arch",
        "Architectures",
        [
          n("dl.arch.cnn", "CNNs", [
            n("dl.arch.cnn.conv", "Convolution"),
            n("dl.arch.cnn.pool", "Pooling"),
            n("dl.arch.cnn.res", "ResNet skip connections"),
            n("dl.arch.cnn.receptive", "Receptive field"),
          ]),
          n("dl.arch.seq", "Sequence models", [
            n("dl.arch.seq.rnn", "RNN"),
            n("dl.arch.seq.lstm", "LSTM / GRU"),
            n("dl.arch.seq.vanishing", "Vanishing gradients"),
          ]),
          n("dl.arch.attn", "Attention & Transformers", [
            n("dl.arch.attn.qkv", "Q / K / V"),
            n("dl.arch.attn.scaled", "Scaled dot-product"),
            n("dl.arch.attn.mha", "Multi-head attention"),
            n("dl.arch.attn.ffn", "FFN block"),
            n("dl.arch.attn.pos", "Positional encodings"),
            n("dl.arch.attn.encoder", "Encoder stack"),
            n("dl.arch.attn.decoder", "Decoder / causal mask"),
            n("dl.arch.attn.kvcache", "KV cache"),
          ]),
        ],
        { phase: 2 },
      ),
      n(
        "dl.torch",
        "PyTorch craft",
        [
          n("dl.torch.tensor", "Tensor API"),
          n("dl.torch.device", "CPU / CUDA device moves"),
          n("dl.torch.module", "nn.Module"),
          n("dl.torch.dataloader", "Dataset / DataLoader"),
          n("dl.torch.trainloop", "Training loop"),
          n("dl.torch.eval", "eval() vs train()"),
          n("dl.torch.amp", "AMP / autocast"),
          n("dl.torch.compile", "torch.compile intuition"),
          n("dl.torch.debug", "Common bug patterns"),
        ],
        { phase: 2 },
      ),
    ],
  },
  {
    id: "llm",
    title: "Modern AI · LLMs · Agents",
    blurb: "Fine-tune, serve, retrieve, and agentize with depth.",
    accent: "#6a1b9a",
    roots: [
      n(
        "llm.basics",
        "LLM building blocks",
        [
          n("llm.basics.tokenize", "Tokenization"),
          n("llm.basics.embed", "Embeddings"),
          n("llm.basics.pretrain", "Pretraining objectives"),
          n("llm.basics.sft", "SFT"),
          n("llm.basics.rlhf", "RLHF / preference tuning idea"),
          n("llm.basics.temp", "Temperature / top-p / top-k"),
          n("llm.basics.context", "Context window limits"),
        ],
        { phase: 3 },
      ),
      n(
        "llm.ft",
        "Fine-tuning",
        [
          n("llm.ft.full", "Full fine-tune tradeoffs"),
          n("llm.ft.lora", "LoRA", [
            n("llm.ft.lora.rank", "Rank / alpha"),
            n("llm.ft.lora.targets", "Target modules"),
            n("llm.ft.lora.merge", "Adapter merge"),
          ]),
          n("llm.ft.qlora", "QLoRA", [
            n("llm.ft.qlora.nf4", "NF4 / double quant"),
            n("llm.ft.qlora.memory", "Memory math"),
          ]),
          n("llm.ft.peft", "PEFT zoo overview"),
          n("llm.ft.eval", "Fine-tune evaluation"),
        ],
        { phase: 3 },
      ),
      n(
        "llm.compr",
        "Compression",
        [
          n("llm.compr.quant", "Quantization", [
            n("llm.compr.quant.ptq", "PTQ"),
            n("llm.compr.quant.qat", "QAT"),
            n("llm.compr.quant.int8", "INT8 / INT4"),
            n("llm.compr.quant.awq", "AWQ / GPTQ intuition"),
          ]),
          n("llm.compr.distill", "Distillation"),
          n("llm.compr.prune", "Pruning basics"),
        ],
        { phase: 3 },
      ),
      n(
        "llm.rag",
        "RAG",
        [
          n("llm.rag.chunk", "Chunking strategies"),
          n("llm.rag.index", "Indexes / vector DBs"),
          n("llm.rag.retrieve", "Retrieval quality"),
          n("llm.rag.rerank", "Reranking"),
          n("llm.rag.eval", "RAG evaluation"),
          n("llm.rag.failure", "Failure modes"),
        ],
        { phase: 3 },
      ),
      n(
        "llm.agents",
        "Agents",
        [
          n("llm.agents.loop", "Plan → act → observe"),
          n("llm.agents.tools", "Tool calling"),
          n("llm.agents.memory", "Memory"),
          n("llm.agents.multi", "Multi-agent patterns"),
          n("llm.agents.eval", "Agent evaluation"),
          n("llm.agents.safety", "Guardrails / sandboxing"),
        ],
        { phase: 3 },
      ),
      n(
        "llm.infer",
        "Inference engineering",
        [
          n("llm.infer.latency", "Latency vs throughput"),
          n("llm.infer.batch", "Continuous batching"),
          n("llm.infer.spec", "Speculative decoding"),
          n("llm.infer.paged", "PagedAttention idea"),
          n("llm.infer.serving", "vLLM / TensorRT-LLM awareness"),
          n("llm.infer.metrics", "Tokens/sec, TTFT, TPOT"),
        ],
        { phase: 3 },
      ),
    ],
  },
  {
    id: "systems",
    title: "Systems · GPU · CUDA Path",
    blurb: "How NVIDIA-shaped engineers think about silicon and speed.",
    accent: "#76b900",
    roots: [
      n(
        "sys.linux",
        "Linux fluency",
        [
          n("sys.linux.shell", "Shell & pipelines"),
          n("sys.linux.proc", "Processes / threads"),
          n("sys.linux.fs", "Filesystem & permissions"),
          n("sys.linux.perf", "top / htop / perf basics"),
          n("sys.linux.docker", "Containers overview"),
        ],
        { phase: 4 },
      ),
      n(
        "sys.cpp",
        "C++ fundamentals",
        [
          n("sys.cpp.types", "Types / memory ownership"),
          n("sys.cpp.pointers", "Pointers / references"),
          n("sys.cpp.raii", "RAII"),
          n("sys.cpp.stl", "STL containers"),
          n("sys.cpp.build", "Build / compile / link"),
        ],
        { phase: 4 },
      ),
      n(
        "sys.arch",
        "Computer architecture",
        [
          n("sys.arch.cpu", "CPU pipeline"),
          n("sys.arch.cache", "Cache hierarchy"),
          n("sys.arch.mem", "Memory bandwidth vs latency"),
          n("sys.arch.simd", "SIMD intuition"),
          n("sys.arch.gpu", "CPU vs GPU", [
            n("sys.arch.gpu.simt", "SIMT"),
            n("sys.arch.gpu.sm", "SMs / warps"),
            n("sys.arch.gpu.hbm", "HBM / VRAM"),
            n("sys.arch.gpu.occupancy", "Occupancy"),
          ]),
        ],
        { phase: 4 },
      ),
      n(
        "sys.cuda",
        "CUDA fundamentals",
        [
          n("sys.cuda.kernels", "Kernels"),
          n("sys.cuda.grid", "Grid / block / thread"),
          n("sys.cuda.mem", "Global / shared / registers"),
          n("sys.cuda.copy", "Host↔device copies"),
          n("sys.cuda.streams", "Streams"),
          n("sys.cuda.profile", "Nsight / profiling idea"),
        ],
        { phase: 4 },
      ),
      n(
        "sys.dist",
        "Distributed training basics",
        [
          n("sys.dist.dp", "Data parallel"),
          n("sys.dist.mp", "Model / pipeline parallel"),
          n("sys.dist.comm", "AllReduce intuition"),
          n("sys.dist.fsdp", "FSDP awareness"),
        ],
        { phase: 4 },
      ),
    ],
  },
  {
    id: "corecs",
    title: "Core CS",
    blurb: "OS · Networks · DBMS — Prime + interview bedrock.",
    accent: "#00838f",
    roots: [
      n(
        "cs.os",
        "Operating systems",
        [
          n("cs.os.process", "Process vs thread"),
          n("cs.os.sched", "Scheduling"),
          n("cs.os.sync", "Mutex / semaphore / deadlock"),
          n("cs.os.mem", "Virtual memory / paging"),
          n("cs.os.fs", "File systems"),
          n("cs.os.io", "I/O & interrupts"),
        ],
        { phase: 2 },
      ),
      n(
        "cs.cn",
        "Computer networks",
        [
          n("cs.cn.osi", "OSI / TCP-IP layers"),
          n("cs.cn.tcp", "TCP vs UDP"),
          n("cs.cn.http", "HTTP / HTTPS"),
          n("cs.cn.dns", "DNS"),
          n("cs.cn.tls", "TLS basics"),
          n("cs.cn.load", "Load balancing idea"),
        ],
        { phase: 2 },
      ),
      n(
        "cs.dbms",
        "DBMS",
        [
          n("cs.dbms.er", "ER modeling"),
          n("cs.dbms.norm", "Normalization"),
          n("cs.dbms.acid", "ACID"),
          n("cs.dbms.txn", "Transactions / isolation"),
          n("cs.dbms.index", "Indexes (B-tree / hash)"),
          n("cs.dbms.query", "Query planning intuition"),
        ],
        { phase: 2 },
      ),
      n(
        "cs.oop",
        "OOP & design basics",
        [
          n("cs.oop.solid", "SOLID skim"),
          n("cs.oop.patterns", "Common patterns"),
        ],
        { phase: 2 },
      ),
    ],
  },
  {
    id: "dsa",
    title: "DSA & Problem Solving",
    blurb: "Patterns you can invent under pressure — not mugged solutions.",
    accent: "#ef6c00",
    roots: [
      n(
        "dsa.comp",
        "Complexity",
        [
          n("dsa.comp.bigO", "Big-O / Theta / Omega"),
          n("dsa.comp.space", "Space tradeoffs"),
          n("dsa.comp.amort", "Amortized analysis skim"),
        ],
        { phase: 1 },
      ),
      n(
        "dsa.struct",
        "Data structures",
        [
          n("dsa.struct.array", "Arrays / strings"),
          n("dsa.struct.hash", "Hash maps / sets"),
          n("dsa.struct.ll", "Linked lists"),
          n("dsa.struct.stack", "Stack / queue / deque"),
          n("dsa.struct.heap", "Heap / priority queue"),
          n("dsa.struct.tree", "Trees / BST / Traversals"),
          n("dsa.struct.trie", "Trie"),
          n("dsa.struct.graph", "Graphs (adj list/matrix)"),
          n("dsa.struct.uf", "Union-Find"),
        ],
        { phase: 1 },
      ),
      n(
        "dsa.patterns",
        "Patterns",
        [
          n("dsa.patterns.two", "Two pointers"),
          n("dsa.patterns.slide", "Sliding window"),
          n("dsa.patterns.prefix", "Prefix sums"),
          n("dsa.patterns.binary", "Binary search variants"),
          n("dsa.patterns.dfs", "DFS / BFS"),
          n("dsa.patterns.topo", "Topological sort"),
          n("dsa.patterns.dij", "Dijkstra / shortest path"),
          n("dsa.patterns.dp1", "1D DP"),
          n("dsa.patterns.dp2", "2D DP / knapsack"),
          n("dsa.patterns.greedy", "Greedy proofs intuition"),
          n("dsa.patterns.backtrack", "Backtracking"),
          n("dsa.patterns.bit", "Bit manipulation"),
        ],
        { phase: 1 },
      ),
      n(
        "dsa.practice",
        "Practice cadence",
        [
          n("dsa.practice.easy", "Easy consistency"),
          n("dsa.practice.med", "Medium pattern coverage"),
          n("dsa.practice.hard", "Selective hard"),
          n("dsa.practice.explain", "Explain out loud"),
        ],
        { phase: 5 },
      ),
    ],
  },
  {
    id: "sql",
    title: "SQL & Data Questions",
    blurb: "Write queries that interviewers trust.",
    accent: "#455a64",
    roots: [
      n(
        "sql.core",
        "Core SQL",
        [
          n("sql.core.select", "SELECT / WHERE / ORDER"),
          n("sql.core.join", "JOINs (inner/left/right/full)"),
          n("sql.core.agg", "GROUP BY / HAVING"),
          n("sql.core.null", "NULL semantics"),
          n("sql.core.sub", "Subqueries"),
          n("sql.core.cte", "CTEs"),
          n("sql.core.window", "Window functions", [
            n("sql.core.window.rank", "ROW_NUMBER / RANK / DENSE_RANK"),
            n("sql.core.window.lag", "LAG / LEAD"),
            n("sql.core.window.frame", "Frames"),
          ]),
        ],
        { phase: 2 },
      ),
      n(
        "sql.adv",
        "Interview SQL",
        [
          n("sql.adv.dedupe", "Deduping rows"),
          n("sql.adv.gaps", "Gaps & islands"),
          n("sql.adv.running", "Running totals"),
          n("sql.adv.topn", "Top-N per group"),
          n("sql.adv.self", "Self joins"),
        ],
        { phase: 2 },
      ),
    ],
  },
  {
    id: "aptitude",
    title: "Aptitude",
    blurb: "Logical · quantitative · reasoning — keep Prime gains alive.",
    accent: "#5d4037",
    roots: [
      n(
        "apt.quant",
        "Quantitative",
        [
          n("apt.quant.pct", "Percentages"),
          n("apt.quant.ratio", "Ratios & proportions"),
          n("apt.quant.avg", "Averages"),
          n("apt.quant.profit", "Profit & loss"),
          n("apt.quant.si", "SI / CI"),
          n("apt.quant.time", "Time & work"),
          n("apt.quant.speed", "Time / speed / distance"),
          n("apt.quant.perm", "Permutations / combinations"),
          n("apt.quant.prob", "Probability aptitude"),
          n("apt.quant.di", "Data interpretation"),
        ],
        { phase: 1 },
      ),
      n(
        "apt.logical",
        "Logical reasoning",
        [
          n("apt.logical.series", "Number / letter series"),
          n("apt.logical.coding", "Coding–decoding"),
          n("apt.logical.blood", "Blood relations"),
          n("apt.logical.dir", "Directions"),
          n("apt.logical.syll", "Syllogisms"),
          n("apt.logical.puzzle", "Seating / puzzles"),
          n("apt.logical.venn", "Venn diagrams"),
        ],
        { phase: 1 },
      ),
      n(
        "apt.verbal",
        "Verbal reasoning",
        [
          n("apt.verbal.analogy", "Analogies"),
          n("apt.verbal.comp", "Reading comprehension"),
          n("apt.verbal.crit", "Critical reasoning skim"),
        ],
        { phase: 1 },
      ),
    ],
  },
  {
    id: "comms",
    title: "Communication",
    blurb: "Sound like an engineer who owns the room.",
    accent: "#ad1457",
    roots: [
      n(
        "com.intro",
        "Self introduction",
        [
          n("com.intro.story", "60s story arc"),
          n("com.intro.rap", "RAP / Cradle highlights"),
          n("com.intro.whyai", "Why AI / why NVIDIA"),
        ],
        { phase: 5 },
      ),
      n(
        "com.speak",
        "Speaking craft",
        [
          n("com.speak.fillers", "Kill fillers"),
          n("com.speak.structure", "PREP / STAR"),
          n("com.speak.whiteboard", "Explain while drawing"),
          n("com.speak.teach", "Teach-back a concept"),
        ],
        { phase: 5 },
      ),
      n(
        "com.write",
        "Writing",
        [
          n("com.write.resume", "Resume bullets (impact)"),
          n("com.write.readme", "Technical READMEs"),
          n("com.write.email", "Cold outreach notes"),
        ],
        { phase: 5 },
      ),
    ],
  },
  {
    id: "sysdesign",
    title: "System Design",
    blurb: "Ask the right questions. Draw the right boxes.",
    accent: "#283593",
    roots: [
      n(
        "sd.gen",
        "General systems",
        [
          n("sd.gen.req", "Requirements & clarifications"),
          n("sd.gen.cap", "Capacity estimation"),
          n("sd.gen.api", "API design"),
          n("sd.gen.storage", "SQL vs NoSQL choice"),
          n("sd.gen.cache", "Caching"),
          n("sd.gen.queue", "Queues / async"),
          n("sd.gen.consist", "Consistency models"),
          n("sd.gen.scale", "Horizontal scaling"),
          n("sd.gen.fail", "Failure modes"),
        ],
        { phase: 5 },
      ),
      n(
        "sd.ml",
        "ML system design",
        [
          n("sd.ml.pipeline", "Training vs serving split"),
          n("sd.ml.feature", "Feature store idea"),
          n("sd.ml.online", "Online vs batch inference"),
          n("sd.ml.monitor", "Drift / monitoring"),
          n("sd.ml.ab", "A/B & shadow deploy"),
          n("sd.ml.cost", "Cost / latency budgets"),
        ],
        { phase: 5 },
      ),
    ],
  },
  {
    id: "mlops",
    title: "MLOps & Production",
    blurb: "Ship models like software.",
    accent: "#37474f",
    roots: [
      n("ops.track", "Experiment tracking"),
      n("ops.version", "Data / model versioning"),
      n("ops.ci", "CI for ML"),
      n("ops.serve", "Serving patterns"),
      n("ops.obs", "Logging / metrics / traces"),
      n("ops.gpu", "GPU utilization basics"),
    ],
  },
  {
    id: "papers",
    title: "Research Papers · Build Loop",
    blurb: "One paper a week → concepts → implement the delta.",
    accent: "#bf360c",
    roots: [
      n(
        "paper.method",
        "How to read",
        [
          n("paper.method.pass1", "Pass 1 (Keshav)"),
          n("paper.method.parent", "Find the parent paper"),
          n("paper.method.delta", "Name the delta"),
          n("paper.method.math", "Derive key equations"),
          n("paper.method.repro", "Minimal reproduction"),
          n("paper.method.teach", "Teach Dr. Delta style"),
        ],
        { phase: 2 },
      ),
      n(
        "paper.track",
        "Paper themes to cover",
        [
          n("paper.track.spec", "Speculative decoding lineage"),
          n("paper.track.attn", "Efficient attention"),
          n("paper.track.moe", "MoE"),
          n("paper.track.rl", "Alignment / RL"),
          n("paper.track.vision", "Vision / multimodal"),
          n("paper.track.systems", "Systems papers (serving)"),
        ],
        { phase: 3 },
      ),
      n(
        "paper.projects",
        "Deep projects",
        [
          n("paper.projects.voltify", "Voltify depth pass"),
          n("paper.projects.dl", "Independent DL project"),
          n("paper.projects.infer", "Inference optimization project"),
          n("paper.projects.repro", "Paper reproduction project"),
        ],
        { phase: 3 },
      ),
    ],
  },
  {
    id: "career",
    title: "Career Ops · Off-campus",
    blurb: "Applications, network, NVIDIA pipeline — consistent motion.",
    accent: "#212121",
    roots: [
      n(
        "car.brand",
        "Personal brand",
        [
          n("car.brand.github", "GitHub hygiene"),
          n("car.brand.linkedin", "LinkedIn narrative"),
          n("car.brand.portfolio", "Portfolio site / demos"),
        ],
        { phase: 5 },
      ),
      n(
        "car.apply",
        "Applications",
        [
          n("car.apply.nvidia", "NVIDIA university / intern watch"),
          n("car.apply.list", "Target company list"),
          n("car.apply.tailor", "Tailor resume per role"),
          n("car.apply.track", "Application tracker habit"),
        ],
        { phase: 5 },
      ),
      n(
        "car.net",
        "Network",
        [
          n("car.net.meetup", "AI meetups"),
          n("car.net.outreach", "Warm / cold outreach"),
          n("car.net.refer", "Referral asks"),
        ],
        { phase: 5 },
      ),
      n(
        "car.mock",
        "Mocks",
        [
          n("car.mock.dsa", "DSA mocks"),
          n("car.mock.ml", "ML theory mocks"),
          n("car.mock.sd", "System design mocks"),
          n("car.mock.torch", "PyTorch debug mocks"),
        ],
        { phase: 5 },
      ),
    ],
  },
];

export function walk(
  nodes: ForgeNode[],
  fn: (node: ForgeNode, parents: ForgeNode[]) => void,
  parents: ForgeNode[] = [],
) {
  for (const node of nodes) {
    fn(node, parents);
    if (node.children?.length) walk(node.children, fn, [...parents, node]);
  }
}

export function allLeaves(): ForgeNode[] {
  const out: ForgeNode[] = [];
  for (const p of PILLARS) {
    walk(p.roots, (node) => {
      if (!node.children?.length) out.push(node);
    });
  }
  return out;
}

export function findNode(
  id: string,
): { pillar: Pillar; node: ForgeNode; path: string[] } | null {
  for (const pillar of PILLARS) {
    let hitNode: ForgeNode | null = null;
    let hitPath: string[] = [];
    walk(pillar.roots, (node, parents) => {
      if (node.id === id) {
        hitNode = node;
        hitPath = [...parents.map((p) => p.title), node.title];
      }
    });
    if (hitNode) return { pillar, node: hitNode, path: hitPath };
  }
  return null;
}

export function countLeaves(nodes: ForgeNode[]): number {
  let c = 0;
  walk(nodes, (n) => {
    if (!n.children?.length) c += 1;
  });
  return c;
}
