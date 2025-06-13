import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic
from ..prompts.query_analysis import QUERY_ANALYSIS_PROMPT_TEMPLATE


# Load environment variables from repository root
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# ✅ Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def query_analysis_agent(user_query: str) -> str:
    # ✅ Inject user query into template
    prompt = QUERY_ANALYSIS_PROMPT_TEMPLATE.replace("{{query}}", user_query)


    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.content[0].text
