import os
import json
import openai
from openai import OpenAI
from dotenv import load_dotenv
import traceback

# Load .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def synthesis_agent(entity: str, plan: dict, articles: list, pivots: dict) -> str:
    try:
        prompt = f"""
You are an OSINT Synthesis Agent.

Your job is to generate a comprehensive, structured OSINT intelligence report based on multi-agent investigation data.
You will receive:
1. The entity and investigation goal
2. A prioritized OSINT collection plan
3. A list of retrieved articles or content chunks (with metadata: source, credibility, time-decay score, published date, and used_in)
4. Pivot analysis insights (related entities, entity graph, new queries, inconsistencies, notes)

Return the final intelligence report as structured Markdown with the following sections:

# OSINT Intelligence Report: {entity}

## Executive Summary
Summarize key findings in 3–5 bullet points.

## Investigation Objectives
List the investigation goals.

## Information Sources & Retrieval Log
Group sources by type (Web, Social Media, Public Records, etc.) and list how many results were retrieved per source.

## Key Findings
Summarize the most relevant findings in these categories:
- Social & Professional Background
- Business or Academic Affiliations
- Public Appearances & Events
- Related People/Organizations
- Potential Risks

## Inconsistencies or Gaps
Mention any contradictory data, disinformation, missing sources, or ambiguity found during the investigation.

## Follow-Up Queries
Suggest 3–5 specific follow-up search queries based on gaps or new leads.

## Appendix: Retrieved Snippets
For each content chunk retrieved, include:
- **Source**: The name of the source (e.g., Google News, LinkedIn)
- **Title**: The article or post title
- **Published**: Date in YYYY-MM-DD
- **Credibility Score**: Float value (0.0–1.0)
- **Time-Decay Score**: Float value (0.0–1.0)
- **Used In**: Which agents used this chunk (e.g., ["pivot", "synthesis"])
- **Link**: URL if available
- **Snippet**: A brief excerpt from the content

## Entity Relationship Graph
Include confidence-weighted triples showing the subject–relation–object structure:
Format:
→ (subject) —[relation @ confidence]→ (object)

## Confidence & Attribution
Rate your confidence (High, Medium, Low) in the overall report. Justify the rating based on:
- Number of sources used
- Credibility of sources
- Recency (via time-decay)
- Presence of inconsistencies
- Coverage of goals

---

OSINT Collection Plan:
{json.dumps(plan, indent=2)}

Retrieved Articles:
{json.dumps(articles, indent=2)}

Pivot Insights:
{json.dumps(pivots, indent=2)}
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt.strip()}],
            temperature=0.3,
            max_tokens=3000,
        )
        print("🚀 Using GPT-4o synthesis agent")
        return response.choices[0].message.content.strip()

    except Exception as e:
        traceback.print_exc()
        return f"❌ Error during synthesis:\n\n{str(e)}"
