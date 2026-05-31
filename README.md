# DigiFortress
DigiFortress/
├── digifortress_env/          # (your virtual environment)
├── src/
│   ├── __init__.py
│   ├── core/                  # Core logic
│   │   ├── agent.py
│   │   ├── memory.py
│   │   └── defense.py
│   ├── attacks/               # Poisoning attack simulations
│   ├── defenses/              # Defense mechanisms
│   └── utils/
├── tests/
├── docs/
│   ├── architecture.md
│   ├── project_charter.md
│   └── threat_model.md
├── experiments/               # Jupyter notebooks for testing
├── notebooks/
├── data/                      # For memory database (will be created later)
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE

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
