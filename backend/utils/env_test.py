from dotenv import load_dotenv
from pathlib import Path
import os

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

print("Anthropic:", os.getenv("ANTHROPIC_API_KEY")[:10])
print("OpenAI:", os.getenv("OPENAI_API_KEY")[:10])
print("Gemini:", os.getenv("GOOGLE_API_KEY")[:10])
