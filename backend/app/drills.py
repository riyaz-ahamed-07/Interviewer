"""PyTorch debug drills and RAP-flavored design prompts."""

from __future__ import annotations

from .technique_bank import LLM_TOPICS, MASTER_TECHNIQUE_BANK, sample_session_topics

__all__ = [
    "DEBUG_DRILLS",
    "DESIGN_PROMPTS",
    "LLM_TOPICS",
    "MASTER_TECHNIQUE_BANK",
    "sample_session_topics",
]

DEBUG_DRILLS: list[dict] = [
    {
        "id": "mnist_shape_softmax",
        "title": "MNIST MLP - shape + loss",
        "hint": "Two bugs: input shape into Linear, and softmax before CrossEntropy.",
        "code": '''import torch
import torch.nn as nn

class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return torch.softmax(x, dim=1)

model = Net()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
crit = nn.CrossEntropyLoss()
xb = torch.randn(32, 1, 28, 28)
yb = torch.randint(0, 10, (32,))
opt.zero_grad()
logits = model(xb)
loss = crit(logits, yb)
loss.backward()
opt.step()
print(loss.item())
''',
    },
    {
        "id": "device_mismatch",
        "title": "Device mismatch",
        "hint": "Model on CUDA (if available), batch on CPU - classic trap.",
        "code": '''import torch
import torch.nn as nn

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = nn.Linear(16, 4).to(device)
xb = torch.randn(8, 16)
yb = torch.randint(0, 4, (8,))
crit = nn.CrossEntropyLoss()
opt = torch.optim.SGD(model.parameters(), lr=0.1)
opt.zero_grad()
out = model(xb)
loss = crit(out, yb)
loss.backward()
opt.step()
''',
    },
    {
        "id": "train_eval_dropout",
        "title": "train() vs eval() + wrong CrossEntropy target",
        "hint": "Dropout left in train mode at inference; targets wrong dtype/shape.",
        "code": '''import torch
import torch.nn as nn

class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 3)
        self.drop = nn.Dropout(0.5)

    def forward(self, x):
        return self.fc(self.drop(x))

model = Net()
model.train()
xb = torch.randn(4, 10)
# bug: float targets + wrong shape for CE
yb = torch.randn(4, 3)
with torch.no_grad():
    logits = model(xb)
    loss = nn.CrossEntropyLoss()(logits, yb)
print(loss)
''',
    },
    {
        "id": "forgotten_zero_grad",
        "title": "Forgotten zero_grad + .item() mid-graph",
        "hint": "Gradients accumulate; also watch for breaking the graph.",
        "code": '''import torch
import torch.nn as nn

model = nn.Linear(8, 2)
opt = torch.optim.Adam(model.parameters(), lr=1e-2)
crit = nn.MSELoss()
for step in range(3):
    xb = torch.randn(16, 8)
    yb = torch.randn(16, 2)
    pred = model(xb)
    loss = crit(pred, yb)
    # accidentally take .item() then try backward on scalar float
    val = loss.item()
    val.backward()
    opt.step()
print("done")
''',
    },
]

DESIGN_PROMPTS: list[dict] = [
    {
        "id": "enterprise_pdf_qa",
        "title": "Enterprise PDF / manual Q&A",
        "summary": (
            "Build an architecture for employees asking questions over large "
            "manufacturing PDFs and Word manuals (tables, diagrams, scanned pages). "
            "Must support RAG, optional Image/HyDE retrieval, human review for "
            "high-stakes answers, and FastAPI serving inside the customer VPC."
        ),
        "ask": (
            "Draw boxes for ingest → understand/OCR → chunk/embed → retrieve → "
            "agent/tools/memory → guardrails → human-in-loop → API. "
            "Be ready to defend every box: why, alternative, failure, metric."
        ),
    },
    {
        "id": "rfp_bid_agent",
        "title": "Government RFP bid agent workgroup",
        "summary": (
            "Design a multi-agent workgroup that reads RFPs, plans bid sections, "
            "and drafts responses. Graph RAG (e.g. Neo4j) + document store. "
            "Include document-understanding, bid-planning, and section-generator agents."
        ),
        "ask": (
            "Draw the workgroup, shared memory, tools, and where humans approve "
            "before submission. Call out Graph RAG vs plain vector search."
        ),
    },
]
