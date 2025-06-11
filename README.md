# 🕵️‍♂️ OSINT AI Agent

**LangGraph-based OSINT Intelligence Agent** for investigating public figures, organizations, or topics by retrieving and synthesizing information from multiple open sources using LLMs like Claude, GPT-4o, and Gemini.

---

## 📌 Features

- 🔎 **Query Analysis** — Breaks down natural language queries into structured OSINT tasks
- 🧭 **Planning Agent** — Chooses relevant sources (news, social, academic, gov, etc.)
- 📡 **Multi-source Retrieval** — From Google News, LinkedIn (stub), Twitter (stub), OpenCorporates, and more
- 🔄 **Pivoting Agent** — Extracts related entities and builds a simple entity graph
- 🧠 **LLM Synthesis** — Uses Gemini or GPT-4o to generate a professional intelligence report
- 🧾 **Structured Output** — Final report with confidence scoring, retrieval logs, and source links
- 🗃️ **Persistent Storage** — Saves each investigation with metadata and source traceability
- 🧪 **Evaluation-ready** — Supports credibility scoring, follow-up queries, and entity mapping

---

## 🚀 Quickstart

### 1. Clone the Repo

```bash
git clone https://github.com/SREEDHA96/osint-ai-agent_new.git
cd osint-ai-agent_new
2. Set Up Environment
bash
Copy
Edit
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
3. Add a .env File
Create a .env file in the project root using:

env
Copy
Edit
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=your_google_gemini_key
SERPAPI_KEY=your_serpapi_key
✅ You can use .env.example as a reference.

4. Run an Example Investigation
bash
Copy
Edit
python backend/graph.py
🧠 Architecture
text
Copy
Edit
+--------------------+
|  Query Analysis    | ← Claude (structured parsing)
+--------------------+
          ↓
+--------------------+
|    Planning Agent   | ← Claude (source selection)
+--------------------+
          ↓
+--------------------+
| Multi-Source Fetch | ← SerpAPI, stubs (Twitter, LinkedIn), OpenCorporates
+--------------------+
          ↓
+--------------------+
|   Pivoting Agent    | ← Claude (related entities, graph)
+--------------------+
          ↓
+--------------------+
|  Synthesis Agent    | ← Gemini 1.5 Pro or GPT-4o
+--------------------+
          ↓
+--------------------+
|   Final Report + DB |
+--------------------+
📦 File Structure
bash
Copy
Edit
osint-ai-agent_new/
├── backend/
│   ├── agents/              # All agent logic (query, planner, retriever, pivot, synthesis)
│   ├── retrieval/           # Source-specific retrieval modules
│   ├── database/            # SQLite + SQLAlchemy schema and save logic
│   ├── graph.py             # LangGraph pipeline orchestrator
│   └── test_retrieval_*.py  # Test scripts for retrieval modules
├── .gitignore
├── .env.example
├── requirements.txt
└── README.md
📥 Sources Integrated
Source	Type	Status
Google News	News	✅ Real (SerpAPI)
Twitter/X	Social Media	🔁 Stub
LinkedIn	Professional Net	🔁 Stub
OpenCorporates	Public Records	🔁 Stub
Academic Sources	Research	⏳ Planned

🔐 Secrets & Safety
✅ .env is ignored and never committed

✅ .venv/ removed from history and excluded

🛡️ GitHub push protection configured

📈 Roadmap
 Entity graph + relationship extraction

 Source credibility scoring

 Timeline of key events

 Risk scoring system

 RAG-based citation-backed answers

👨‍💻 Author
Sreedha Bhakthavalsalan
GitHub: @SREEDHA96

📄 License
MIT License

yaml
Copy
Edit

---

### ✅ Then:

1. Save the file.
2. Stage and commit:
   ```bash
   git add README.md
   git commit -m "Add full project README"
   git push
