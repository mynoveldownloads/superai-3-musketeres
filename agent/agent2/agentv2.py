"""
agent.py — ADK LlmAgent for supermarket inventory data visualization.

Uses LiteLlm to route through OpenRouter (same API key + model as the
teammate's non-ADK agent), but hands orchestration to ADK's agent loop.

Improvements over v1:
  - metadata_txt_exists() as mandatory first tool call
  - Fast path skips schema probes when metadata.txt is present
  - Mandatory intermediate reasoning after every tool call
  - query_db returns only 5 sample rows to LLM (full data fetched in render_chart)
  - render_chart validates output dir writability and flags datetime fallback
"""

import os
import ssl
import urllib3
import requests
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from tools import query_db, render_chart, metadata_txt_exists

load_dotenv()

# ==============================================================================
# SSL FIX — dev only, remove for production
# ==============================================================================
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_original_session_init = requests.Session.__init__

def _patched_session_init(self, *args, **kwargs):
    _original_session_init(self, *args, **kwargs)
    self.verify = False

requests.Session.__init__ = _patched_session_init

# ==============================================================================
# Model
# ==============================================================================
MODEL = LiteLlm(
    model="openrouter/google/gemini-3.1-flash-lite",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    api_base="https://openrouter.ai/api/v1",
)

# ==============================================================================
# System prompt
# ==============================================================================
SYSTEM_PROMPT = """
You are an intelligent data analyst agent for a supermarket inventory management system.
You have access to a SQLite database via query_db, a schema cache via metadata_txt_exists,
and a chart renderer via render_chart.

Available tables: inventory, orders, products, sales_items, suppliers.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY REASONING RULE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
After EVERY tool call, before invoking the next tool, you MUST write a short
reasoning block using this format:

  [Reasoning]
  Observed: <what the tool returned>
  Concluded: <what this tells you>
  Next action: <what you will do next and why>

This is required for every step without exception.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0 — METADATA CHECK (always first)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Your FIRST action must always be to call metadata_txt_exists().

  If exists=True (FAST PATH):
    The 'schema' field contains full table definitions, column names, data
    types, and foreign key relationships. Use this directly.
    → Skip all SELECT * LIMIT 5 probes entirely.
    → Proceed immediately to STEP 2 (query planning).

  If exists=False (SLOW PATH):
    No schema cache. You must explore the database manually.
    → Proceed to STEP 1 (schema discovery).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — SCHEMA DISCOVERY (slow path only)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For every table likely relevant to the user's question, run:
  SELECT * FROM <table> LIMIT 5

This reveals column names, data types, and FK patterns.
After all probes, write a [Reasoning] block summarising what you learned:
which FK keys link which tables, which column holds the metric, which holds
the time dimension or category.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — QUERY PLANNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Before calling query_db with your final SQL, write a [Reasoning] block stating:
  - Which tables you will JOIN and on which FK keys
  - Which column is the metric (y-axis)
  - Which column is the time dimension or category (x-axis)
  - What WHERE / GROUP BY / ORDER BY clauses you need
  - What chart_type you plan to use and why

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3 — EXECUTE FINAL QUERY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Call query_db with your planned SELECT + JOIN + WHERE + GROUP BY query.
You will receive back the column names and a 5-row sample.
Write a [Reasoning] block after receiving the result:
  - Confirm columns match your plan
  - Confirm rows_returned > 0
  - Confirm x_col and y_col values look sensible
  - If something is wrong, explain what and how you will fix it, then retry.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4 — RENDER CHART
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Call render_chart with:
  - sql: the EXACT same SQL string from your final query_db call
  - chart_type, x_col, y_col, title, x_label, y_label

Do NOT pass any data values. The tool re-fetches data from the DB directly.
After render_chart succeeds, write a final [Reasoning] block summarising:
  - How many rows were plotted
  - The key trend or insight visible in the chart
  - Any warnings returned (e.g. datetime fallback)
Then stop. Do not call any more tools.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HARD RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Never guess column names. Always verify from metadata.txt or LIMIT 5 probes.
- Only SELECT statements. Never INSERT, UPDATE, DROP, ALTER, TRUNCATE, etc.
- If query_db returns an error, read the message, explain what went wrong in
  [Reasoning], correct your SQL, and retry.
- Call render_chart exactly once as your final tool action.
- Never pass raw data rows to render_chart — only the sql string.
""".strip()

# ==============================================================================
# ADK Agent
# ==============================================================================
root_agent = LlmAgent(
    name="inventory_data_visual_agent",
    model=MODEL,
    instruction=SYSTEM_PROMPT,
    description=(
        "Answers supermarket inventory questions by querying a SQLite database "
        "and rendering a matplotlib chart. Uses metadata.txt schema cache when "
        "available to skip schema discovery and go directly to query planning."
    ),
    tools=[metadata_txt_exists, query_db, render_chart],
)

# ==============================================================================
# Local test runner
# ==============================================================================
if __name__ == "__main__":
    import asyncio
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    async def run_query(user_message: str):
        session_service = InMemorySessionService()
        await session_service.create_session(
            app_name="inventory_agent",
            user_id="dev",
            session_id="test-session-01",
        )
        runner = Runner(
            agent=root_agent,
            app_name="inventory_agent",
            session_service=session_service,
        )
        content = types.Content(
            role="user",
            parts=[types.Part(text=user_message)],
        )
        print(f"\n{'='*60}")
        print(f"Query: {user_message}")
        print(f"{'='*60}")

        async for event in runner.run_async(
            user_id="dev",
            session_id="test-session-01",
            new_message=content,
        ):
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        # Show tool name but truncate args to avoid terminal flood
                        args_preview = str(dict(part.function_call.args))[:200]
                        print(f"\n[Tool Call] {part.function_call.name}({args_preview})")
                    if hasattr(part, "function_response") and part.function_response:
                        print(f"[Tool Result] {str(part.function_response.response)[:400]}")
                    if part.text:
                        print(f"\n[Agent] {part.text}")

    asyncio.run(run_query(
        "Give me the sales performance of all HappySnacks Potato Chips products over time"
    ))