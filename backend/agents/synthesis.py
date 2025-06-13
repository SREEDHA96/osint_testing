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
        # Fallback if no articles retrieved
        if not articles:
            return f"""
# OSINT Intelligence Report: {entity}

## Executive Summary
- No articles or content chunks were retrieved, leading to a lack of data for analysis.
- The investigation was unable to provide insights into {entity}'s social, professional, or political activities.
- There are significant gaps in the information due to the absence of retrieved data.
- Further investigation is required to fulfill the objectives outlined in the collection plan.

## Investigation Objectives
{json.dumps(plan.get('objectives', []), indent=2)}

## Information Sources & Retrieval Log
_No data retrieved._

## Key Findings
_No key findings could be reported due to lack of data._

## Inconsistencies or Gaps
The investigation encountered a significant gap due to missing content chunks.

## Follow-Up Queries
1. "{entity} biography and career"
2. "{entity} recent news coverage"
3. "Social media activity of {entity}"

## Appendix: Retrieved Snippets
_No content snippets were available._

## Entity Relationship Graph
_No relationships extracted._

## Confidence & Attribution
**Confidence Rating: Low**

- **Number of Sources Used**: 0
- **Credibility of Sources**: Not applicable
- **Recency**: Not applicable
- **Coverage of Goals**: Not met
"""

        # Ensure all articles have "used_in" field
        for article in articles:
            if "used_in" not in article:
                article["used_in"] = ["synthesis"]

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
