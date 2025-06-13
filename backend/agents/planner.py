from anthropic import Anthropic
import os
from dotenv import load_dotenv
import json
import traceback
from ..prompts.planner import PLANNER_SYSTEM_PROMPT

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def osint_planning_agent(parsed_json: dict) -> str:
    try:
        print("\n🧠 [Planner] Parsed Input:\n", json.dumps(parsed_json, indent=2))

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=PLANNER_SYSTEM_PROMPT.strip(),
            messages=[
                {
                    "role": "user",
                    "content": json.dumps(parsed_json, indent=2)
                }
            ]
        )

        content = response.content[0].text.strip()
        print("\n🧠 [Planner] Claude Response:\n", content[:300], "..." if len(content) > 300 else "")

        # ✅ Strip code block formatting if present
        if content.startswith("```json"):
            content = content.removeprefix("```json").removesuffix("```").strip()

        if not content or not content.startswith("{"):
            raise ValueError("Claude returned non-JSON content")

        return content

    except Exception as e:
        traceback.print_exc()
        print("⚠️ [Planner] Falling back to default minimal OSINT plan.")
        return json.dumps({
            "plan": [
                {"source": "google news", "goal": "Find recent articles"},
                {"source": "linkedin", "goal": "Check professional background"},
                {"source": "twitter", "goal": "Monitor social presence"}
            ]
        }, indent=2)
