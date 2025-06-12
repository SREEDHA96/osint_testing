from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.agents.evaluator import evaluate_report
from backend.llm_judge import call_claude_opus
from backend.graph import build_langgraph
from backend.database import insert_investigation, get_all_investigations

app = FastAPI()

# ✅ CORS settings (Updated)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use ["http://127.0.0.1:8000"] if you want to restrict it
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ History API
@app.get("/history")
def fetch_history():
    investigations = get_all_investigations()
    return [
        {
            "id": inv.id,
            "query": inv.query,
            "report": inv.final_report,
            "created_at": inv.created_at.isoformat()
        }
        for inv in investigations
    ]

# ✅ Query request model
class QueryRequest(BaseModel):
    query: str

# ✅ Main OSINT endpoint
@app.post("/query")
async def query_osint(req: QueryRequest):
    try:
        print("📥 [API] Received query:", req.query)

        final_state = await build_langgraph(req.query)
        print("✅ [LangGraph] Pipeline execution finished")

        report = final_state.get("final_report")
        if not report:
            print("⚠️ No report returned from synthesis_node.")
            return {"report": "No report generated."}

        print("📝 Report:", report[:300], "..." if len(report) > 300 else "")

        # Evaluate the report
        evaluation = await call_claude_opus(report)
        print("🧠 Evaluation complete")

        # Store in DB
        insert_investigation(
            query=req.query,
            final_report=report,
            evaluation=evaluation
        )
        print("💾 Report saved to DB")

        return {"report": report, "evaluation": evaluation}

    except Exception as e:
        import traceback
        print("❌ [ERROR] Exception in /query:", e)
        traceback.print_exc()
        return {"report": f"Error occurred: {str(e)}"}

# ✅ Serve React Frontend (dist build)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

# ✅ Fallback to index.html for SPA routing
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    index_path = os.path.join(frontend_path, "index.html")
    return FileResponse(index_path)
