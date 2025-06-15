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
```

### 2. Set Up Environment

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Add a `.env` File

Create a `.env` file in the root with the following content:

```env
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_API_KEY=your-google-gemini-key
SERPAPI_KEY=your-serpapi-key
```

> ✅ You can use `.env.example` as a template.

🛠️ Execution Details
🧠 Backend (LangGraph + FastAPI)
To run the OSINT agent and serve the API:

bash
Copy
Edit
# Activate virtual environment
.\.venv\Scripts\activate   # Windows
# or
source .venv/bin/activate  # macOS/Linux

# Start the FastAPI server
uvicorn backend.main:app --reload
Endpoint: POST /query

Accepts: { "query": "Your OSINT investigation query" }

Returns: { "report": "...", "evaluation": {...} }

Optional:

GET /history — fetches past investigations from the database

The backend also serves the React frontend statically at http://localhost:8000

💻 Frontend (React + Vite)
To run the frontend in development mode:

bash
Copy
Edit
cd frontend
npm install
npm run dev
Dev URL: http://localhost:5173

Interacts with FastAPI backend at http://localhost:8000/query

To build for production:

bash
Copy
Edit
npm run build
Output is generated in frontend/dist/

FastAPI automatically serves these static files in production mode

🧪 Running a Local Investigation (CLI Mode)
If you prefer testing the pipeline without the UI:

bash
Copy
Edit
python backend/graph.py
This executes the pipeline once for a hardcoded or test query and prints the structured report.

## 👨‍💻 Author

**Sreedha Bhakthavalsalan**  
GitHub: [@SREEDHA96](https://github.com/SREEDHA96)

