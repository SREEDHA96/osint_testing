# backend/agents/planner.py

from anthropic import Anthropic
import os
from pathlib import Path
from dotenv import load_dotenv
import json
from ..prompts.planner import PLANNER_SYSTEM_PROMPT



ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def osint_planning_agent(parsed_json: dict) -> str:
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
    return response.content[0].text
