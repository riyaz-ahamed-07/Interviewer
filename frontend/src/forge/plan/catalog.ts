import { buildPlanWeek, type DaySeed } from "./buildWeek";
import type { PlanWeek } from "./types";

function seeds(
  rows: [
    number,
    string,
    string,
    string?,
    number?,
  ][],
): DaySeed[] {
  return rows.map(([dow, topic, conceptTitle, conceptId, conceptMin]) => ({
    dow,
    topic,
    conceptTitle,
    conceptId,
    conceptMin,
  }));
}

export const MAX_PLANNED_WEEK = 12;

export const PLAN_WEEKS: PlanWeek[] = [
  buildPlanWeek(
    1,
    "Kickoff · DSA basics + OS intro + TrenTorch Python",
    seeds([
      [1, "DSA", "Striver Step 1 · Learn the basics", "dsa.s1"],
      [2, "DBMS", "What is DBMS? (video block)", "cs.dbms.what"],
      [3, "OS", "What is an OS? (video block)", "cs.os.intro", 90],
      [4, "CN", "How networking started", "cs.cn.start"],
      [5, "AIML", "Python for ML — data structures & NumPy mindset", "tt.python"],
      [6, "Paper", "How to read a paper · Pass 1", "paper.method.pass1", 50],
      [0, "OS", "OS types + multitasking vs multithreading", "cs.os.types", 140],
    ]),
  ),
  buildPlanWeek(
    2,
    "Arrays + OS process/scheduling + Math/NumPy",
    seeds([
      [1, "DSA", "Striver Step 3 · Arrays (easy set)", "dsa.s3"],
      [2, "DBMS", "DBMS architecture & DBA", "cs.dbms.arch"],
      [3, "OS", "OS components + system calls", "cs.os.components", 90],
      [4, "CN", "Client–server + IP + ports", "cs.cn.cs"],
      [5, "AIML", "Linear algebra · vectors & matrices (implement)", "math.linalg.vectors"],
      [6, "Paper", "Find the parent paper of your pick", "paper.method.parent", 50],
      [0, "OS", "How OS creates a process + process states", "cs.os.create", 140],
    ]),
  ),
  buildPlanWeek(
    3,
    "Sorting + OS sync start + TrenTorch Math",
    seeds([
      [1, "DSA", "Striver Step 2 · Sorting techniques", "dsa.s2"],
      [2, "DBMS", "ER model fundamentals", "cs.dbms.er"],
      [3, "OS", "Context switching + convoy effect", "cs.os.ctx", 90],
      [4, "CN", "LAN/MAN/WAN + topologies", "cs.cn.lan"],
      [5, "AIML", "TrenTorch · Mathematics for ML module", "tt.math"],
      [6, "Paper", "Name the paper delta in one sentence", "paper.method.delta", 50],
      [0, "OS", "CPU scheduling · SJF / Priority / RR", "cs.os.sched.basic", 150],
    ]),
  ),
  buildPlanWeek(
    4,
    "Binary search + OS memory + Data Science practice",
    seeds([
      [1, "DSA", "Striver Step 4 · Binary search", "dsa.s4"],
      [2, "DBMS", "Extended ER + ER thinking", "cs.dbms.eer"],
      [3, "OS", "Concurrency + critical section", "cs.os.conc", 90],
      [4, "CN", "OSI 7 layers (study + redraw)", "cs.cn.osi", 90],
      [5, "AIML", "TrenTorch · Data Science module", "tt.ds"],
      [6, "Paper", "Derive one key equation from the paper", "paper.method.math", 50],
      [0, "OS", "Semaphores + producer–consumer", "cs.os.sync", 150],
    ]),
  ),
  buildPlanWeek(
    5,
    "LL/Recursion + DBMS relational + SQL emphasis",
    seeds([
      [1, "DSA", "Striver Step 6 · Linked list", "dsa.s6"],
      [2, "DBMS", "Relational model + ER→relational", "cs.dbms.rel"],
      [3, "OS", "Deadlock basics", "cs.os.deadlock", 90],
      [4, "CN", "TCP/IP model + HTTP verbs", "cs.cn.tcpip"],
      [5, "AIML", "Calculus for ML · derivatives & chain rule", "math.calc.deriv"],
      [6, "Paper", "Minimal reproduction sketch", "paper.method.repro", 50],
      [0, "DBMS", "Normalisation deep block", "cs.dbms.norm", 150],
    ]),
  ),
  buildPlanWeek(
    6,
    "Stack/Queue/SW + ACID/index + SysDesign foundations",
    seeds([
      [1, "DSA", "Striver Step 9 · Stack & queue", "dsa.s9"],
      [2, "DBMS", "ACID & transactions", "cs.dbms.acid"],
      [3, "OS", "Deadlock avoidance / detection", "cs.os.deadlock.recover", 90],
      [4, "CN", "DNS + cookies + status codes", "cs.cn.dns"],
      [5, "AIML", "SysDesign foundations · approach + latency/throughput", "sd.intro.approach"],
      [6, "Paper", "Teach the paper out loud (5 min)", "paper.method.teach", 50],
      [0, "DBMS", "Indexing deep block", "cs.dbms.index", 150],
    ]),
  ),
  buildPlanWeek(
    7,
    "Trees start + CN transport + Classical ML practice",
    seeds([
      [1, "DSA", "Striver Step 13 · Binary trees (traversals)", "dsa.s13"],
      [2, "DBMS", "NoSQL vs SQL + DB types", "cs.dbms.nosql"],
      [3, "OS", "Memory management overview", "cs.os.mem", 90],
      [4, "CN", "UDP vs TCP + 3-way handshake", "cs.cn.tcp"],
      [5, "AIML", "TrenTorch · Classical ML module", "tt.cml"],
      [6, "Paper", "Pick this week’s paper title", undefined, 50],
      [0, "CN", "Transport layer deep + checksum/timers", "cs.cn.transport", 140],
    ]),
  ),
  buildPlanWeek(
    8,
    "BST + CN IP/NAT + SysDesign edge/LB",
    seeds([
      [1, "DSA", "Striver Step 14 · BST", "dsa.s14"],
      [2, "DBMS", "Clustering / replication / sharding", "cs.dbms.cluster"],
      [3, "OS", "Paging + segmentation", "cs.os.paging", 90],
      [4, "CN", "IPv4 vs IPv6 + NAT", "cs.cn.ipv46"],
      [5, "AIML", "SysDesign · DNS / CDN / load balancers", "sd.edge.lb"],
      [6, "Paper", "Annotate abstract + contributions", undefined, 50],
      [0, "OS", "Virtual memory + page replacement", "cs.os.vm", 150],
    ]),
  ),
  buildPlanWeek(
    9,
    "Graphs start + CN wrap + Classical ML concepts",
    seeds([
      [1, "DSA", "Striver Step 15 · Graphs (BFS/DFS)", "dsa.s15"],
      [2, "DBMS", "CAP theorem + master–slave", "cs.dbms.cap"],
      [3, "OS", "Thrashing + free-space mgmt", "cs.os.thrash", 80],
      [4, "CN", "Data link layer wrap-up", "cs.cn.datalink"],
      [5, "AIML", "Supervised vs unsupervised + train/val/test", undefined],
      [6, "Paper", "Map paper → one TrenTorch question", undefined, 50],
      [0, "AIML", "Linear + logistic regression from scratch plan", undefined, 150],
    ]),
  ),
  buildPlanWeek(
    10,
    "Graphs/DP intro + paper habit + TrenTorch DL",
    seeds([
      [1, "DSA", "Striver Step 15 · Graphs (shortest path intro)", "dsa.s15"],
      [2, "DBMS", "Review ACID + indexing flashcards", "cs.dbms.acid", 60],
      [3, "OS", "LC concurrency set 1 (guided)", "cs.os.lc.conc1", 90],
      [4, "CN", "HTTP deep review + status codes drill", "cs.cn.http"],
      [5, "AIML", "TrenTorch · Deep Learning module start", "tt.dl"],
      [6, "Paper", "Neural net foundations paper track", "paper.track.attn", 50],
      [0, "AIML", "NN fundamentals · forward + loss intuition", undefined, 150],
    ]),
  ),
  buildPlanWeek(
    11,
    "DP patterns + DL fundamentals + agents preview only",
    seeds([
      [1, "DSA", "Striver Step 16 · DP patterns intro", "dsa.s16"],
      [2, "DBMS", "ER of a familiar product (sketch)", "cs.dbms.erthink"],
      [3, "OS", "LC concurrency set 2", "cs.os.lc.conc2", 90],
      [4, "CN", "Redraw OSI + TCP/IP from memory", "cs.cn.osi", 70],
      [5, "AIML", "Backprop intuition + PyTorch autograd sketch", undefined],
      [6, "Paper", "Agents preview · what NOT to build yet", "agents.core.tools", 40],
      [0, "AIML", "Train a tiny NN in PyTorch (pipeline)", undefined, 160],
    ]),
  ),
  buildPlanWeek(
    12,
    "Review + continue DL (agents only if Transformers ready)",
    seeds([
      [1, "DSA", "Striver catch-up · weakest step revision", "dsa.s1"],
      [2, "DBMS", "Full DBMS video map recap", "cs.dbms.what", 70],
      [3, "OS", "Full OS video map recap", "cs.os.intro", 90],
      [4, "CN", "Full CN video map recap", "cs.cn.start", 80],
      [5, "AIML", "TrenTorch DL continue · activations & training loop", "tt.dl"],
      [6, "Paper", "Week review notes → next 4-week goals", undefined, 50],
      [
        0,
        "AIML",
        "Continue DL OR first Krish LangChain block (only if Transformers done)",
        "agents.krish.lc",
        160,
      ],
    ]),
  ),
];

export function getMaxPlannedWeek() {
  return MAX_PLANNED_WEEK;
}
