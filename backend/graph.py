from langgraph.graph import StateGraph
from typing import TypedDict
import json
from datetime import datetime
from dateutil import parser as date_parser

from .agents.query_analysis import query_analysis_agent
from .agents.planner import osint_planning_agent
from .agents.retriever_orchestrator import multi_source_retrieval
from .agents.pivot import pivot_agent
from .agents.synthesis import synthesis_agent
from .agents.deduplication import deduplicate_chunks
from .database import save_investigation

# Define the shared state schema for LangGraph
class GraphState(TypedDict):
    input: str
    parsed_query: dict
    task_plan: dict
    retrieved_chunks: list
    pivot_insights: dict
    retrieval_log: list
    final_report: str
    sources: list

# Credibility scoring map
CREDIBILITY_MAP = {
    "Reuters": 0.95,
    "Bloomberg": 0.9,
    "Google News": 0.8,
    "LinkedIn": 0.75,
    "Twitter/X": 0.4,
    "OpenCorporates": 0.7,
    "TechCrunch": 0.6,
    "Forbes": 0.65
}

# Apply time decay to a publication date
def apply_time_decay(published: str) -> float:
    try:
        pub_date = date_parser.parse(published)
        days_old = (datetime.utcnow() - pub_date).days
        return max(0.1, 1.0 - (days_old / 365.0))  # decay over 1 year
    except Exception:
        return 0.5  # fallback if date is bad

# Node 1: Query Analysis
def query_node(state: GraphState) -> dict:
    parsed = query_analysis_agent(state["input"])
    print("\n📤 DEBUG: Raw Claude response:", parsed)

    if parsed.strip().startswith("```json"):
        parsed = parsed.strip().removeprefix("```json").removesuffix("```")

    parsed = parsed.strip()
    print("🧪 Cleaned Claude response:\n", parsed)

    if not parsed or not parsed.startswith("{"):
        raise ValueError("query_analysis_agent returned invalid or empty response")

    return {"parsed_query": json.loads(parsed)}

# Node 2: Planning
def planner_node(state: GraphState) -> dict:
    parsed_query = state["parsed_query"]
    plan = osint_planning_agent(parsed_query)
    print("🧭 DEBUG: Raw Plan Output:", repr(plan))

    if plan.startswith("```"):
        plan = plan.strip("`").strip()
        if "\n" in plan:
            plan = plan.split("\n", 1)[1]
        if plan.endswith("```"):
            plan = plan.rsplit("````", 1)[0]

    print("🧪 Cleaned Plan Output:\n", plan)

    if not plan or not plan.strip().startswith("{"):
        raise ValueError("osint_planning_agent returned invalid or empty response")

    return {"task_plan": json.loads(plan)}

# Node 3: Retrieval
def retriever_node(state: GraphState) -> dict:
    entity = state["parsed_query"]["entity"]
    plan = state["task_plan"].get("plan", [])

    results = multi_source_retrieval(entity, plan)
    print(f"📚 Retrieved {len(results)} chunks from all sources.")

    # Enrich with credibility and decay
    enriched = []
    for item in results:
        credibility = CREDIBILITY_MAP.get(item.get("source"), 0.5)
        published = item.get("published", "")
        decay = apply_time_decay(published)
        item["credibility_score"] = credibility
        item["decay_factor"] = decay
        item["final_score"] = round(credibility * decay, 3)
        enriched.append(item)

    deduped = deduplicate_chunks(enriched)

    # ✅ Add the required "used_in" field for synthesis_agent
    for chunk in deduped:
        chunk["used_in"] = ["synthesis"]

    if not deduped:
        print("❌ No deduplicated chunks available — downstream synthesis will receive empty input.")
    else:
        print(f"✅ {len(deduped)} chunks ready to pass to synthesis.")

    # Build structured log
    source_log = {}
    for item in deduped:
        source = item["source"]
        source_log[source] = source_log.get(source, 0) + 1

    structured_log = [
        {"type": source, "count": count} for source, count in source_log.items()
    ]

    return {
        "retrieved_chunks": deduped,
        "retrieval_log": structured_log,
        "sources": deduped
    }



# Node 4: Pivoting
def pivot_node(state: GraphState) -> dict:
    insights_raw = pivot_agent(state["retrieved_chunks"], state["parsed_query"]["entity"])
    print("\n🧠 Pivot Agent Output:\n", insights_raw)

    insights = insights_raw.strip()
    if insights.startswith("```json"):
        insights = insights.removeprefix("```json").removesuffix("```").strip()

    try:
        parsed = json.loads(insights)
    except json.JSONDecodeError as e:
        print("❌ Failed to parse pivot agent output:", e)
        raise ValueError("pivot_agent returned invalid JSON")

    # Extract entity graph triples
    entity_graph = []
    for rel in parsed.get("related_entities", []):
        entity_graph.append({
            "subject": state["parsed_query"]["entity"],
            "relation": rel.get("relation", "related to"),
            "object": rel.get("name", "Unknown"),
            "context": rel.get("event", ""),
            "confidence": 0.85
        })
    print("\n🧩 Extracted Entity Graph:")
    for e in entity_graph:
        print(f"→ ({e['subject']}) —[{e['relation']} @ {e['confidence']}]→ ({e['object']})")
    return {
        "pivot_insights": {
            **parsed,
            "entity_graph": entity_graph
        }
    }

# Node 5: Synthesis
def synthesis_node(state: GraphState) -> dict:
    report = synthesis_agent(
        entity=state["parsed_query"]["entity"],
        plan=state["task_plan"],
        articles=state["retrieved_chunks"],
        pivots=state["pivot_insights"]
    )
    print("\n📄 Final Report Generated.\n")

    save_investigation({
        **state,
        "final_report": report
    })

    return {"final_report": report}

# Build LangGraph pipeline
async def build_langgraph(query: str):
    builder = StateGraph(GraphState)

    builder.add_node("QueryAnalysis", query_node)
    builder.add_node("Planner", planner_node)
    builder.add_node("Retriever", retriever_node)
    builder.add_node("Pivot", pivot_node)
    builder.add_node("Synthesis", synthesis_node)

    builder.set_entry_point("QueryAnalysis")
    builder.add_edge("QueryAnalysis", "Planner")
    builder.add_edge("Planner", "Retriever")
    builder.add_edge("Retriever", "Pivot")
    builder.add_edge("Pivot", "Synthesis")

    builder.set_finish_point("Synthesis")

    graph = builder.compile()
    result = await graph.ainvoke({"input": query})
    return result

if __name__ == "__main__":
    import asyncio
    query = "Investigate Ali Khaledi Nasab’s social and professional background across public records."
    result = asyncio.run(build_langgraph(query))

    print("\n🎯 Final Graph State:\n")
    for key, val in result.items():
        print(f"--- {key.upper()} ---")
        if isinstance(val, (dict, list)):
            print(json.dumps(val, indent=2), "\n")
        else:
            print(val, "\n")
