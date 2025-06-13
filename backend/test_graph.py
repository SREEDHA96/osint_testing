# backend/test_graph.py

import sys, os, json
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.graph import build_langgraph

async def main():
    query = "Investigate Ali Khaledi Nasab’s social and professional background across public records."

    try:
        result = await build_langgraph(query)
    except Exception as e:
        print(f"❌ LangGraph pipeline failed: {str(e)}")
        return

    print("\n🎯 Final Graph State:\n")
    for key, val in result.items():
        print(f"--- {key.upper()} ---")
        if isinstance(val, (dict, list)):
            print(json.dumps(val, indent=2), "\n")
        else:
            print(val, "\n")

    # Optional: Print final report separately
    print("\n📄 Intelligence Report:\n")
    print(result.get("final_report", "⚠️ No report generated."))

if __name__ == "__main__":
    asyncio.run(main())
