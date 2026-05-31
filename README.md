# DigiFortress
DigiFortress/
├── venv/                       # (your virtual environment)
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── memory/
│   │   ├── __init__.py
│   │   └── memory_manager.py
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedder.py
│   ├── llm/
│   │   ├── __init__.py
│   │   └── llm_handler.py
│   └── utils/
│       └── helpers.py
├── data/
│   └── chroma_db/              # Chroma DB persistent storage
├── tests/
│   └── test_memory.py
├── docs/
│   ├── project_charter.md
│   └── phase1_design.md
├── requirements.txt
├── README.md
├── .gitignore
└── main.py


Architecture Basic

User
  │
  ▼
Agent
  │
  ├── Memory Retrieval
  │
  ▼
Memory Store
  │
  ▼
Relevant Memories
  │
  ▼
LLM
  │
  ▼
Response
