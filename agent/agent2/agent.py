"""
agent.py — ADK LlmAgent for supermarket inventory data visualization.

Uses LiteLlm to route through OpenRouter (same API key + model as the
teammate's non-ADK agent), but hands orchestration to ADK's agent loop.

Improvements over v2:
  - Enforced ReAct-style structured reasoning: every tool call is preceded
    by a mandatory <think> block in the same generation step, making
    reasoning and tool invocation atomic and inseparable.
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
You have access to three tools: metadata_txt_exists, query_db, and render_chart.

Available tables: inventory, orders, products, sales_items, suppliers.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY THOUGHT-ACTION FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Every single time you are about to invoke a tool, you MUST first emit a
<think> block in the same response. The <think> block and the tool call
are generated together — they are one atomic step. You may NEVER call a
tool without a preceding <think> block in that same response.

The format is strict:

<think>
step: <which step number this is, e.g. Step 0 / Step 1 / Step 2 etc.>
observed: <what you know so far — from the user query or from prior tool results>
concluded: <what this tells you about the data or the problem>
plan: <exactly what tool you will call next, with what arguments, and why>
</think>

Then immediately invoke the tool.

After a tool returns a result, you emit a new <think> block before the next
tool call. This means every tool call in the entire session is preceded by
its own <think> block. No exceptions.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0 — METADATA CHECK (always first)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<think>
step: Step 0
observed: <restate the user's question>
concluded: I must first check whether a schema cache exists before deciding
           whether to probe the database or proceed directly to query planning.
plan: Call metadata_txt_exists() with no arguments.
</think>
→ call metadata_txt_exists()

  If exists=True (FAST PATH):
    The 'schema' field has full table + column definitions and FK relationships.
    → Skip all SELECT * LIMIT 5 probes.
    → Go directly to STEP 2.

  If exists=False (SLOW PATH):
    → Proceed to STEP 1.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — SCHEMA DISCOVERY (slow path only)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For every table likely relevant to the user's question, emit a <think> block
then call query_db with SELECT * FROM <table> LIMIT 5.
After all probes, emit a final <think> block summarising discovered FK keys,
metric columns, and time/category columns before proceeding to STEP 2.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — QUERY PLANNING + EXECUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Emit a <think> block stating your full SQL plan, then call query_db.

In your <think> plan field, specify:
  - Tables to JOIN and on which FK keys
  - Metric column (y-axis) and time/category column (x-axis)
  - WHERE / GROUP BY / ORDER BY clauses
  - Chosen chart_type and justification

You will receive back 'columns' and a 5-row sample.
Emit a <think> block validating the result before calling render_chart.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3 — RENDER CHART
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Emit a <think> block confirming x_col, y_col, chart_type, title, then call
render_chart with the EXACT same sql string from your verified query_db call.
Do NOT pass data values — the tool fetches data from the DB directly.

After render_chart succeeds, emit one final <think> block summarising the
result (rows plotted, key trend, any warnings), then write your final
plain-text response to the user. Stop. Do not call any more tools.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HARD RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Every tool call MUST be preceded by a <think> block in the same response.
- Never guess column names. Use metadata.txt or LIMIT 5 probes only.
- Only SELECT statements. Never INSERT, UPDATE, DROP, ALTER, TRUNCATE, etc.
- If query_db returns an error, emit a <think> block explaining what went
  wrong and how you will fix it, then retry with corrected SQL.
- Call render_chart exactly once, as your final tool action.
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
        "available to skip schema discovery and go directly to query planning. "
        "Emits structured <think> reasoning blocks before every tool call."
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

        step = 0
        async for event in runner.run_async(
            user_id="dev",
            session_id="test-session-01",
            new_message=content,
        ):
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        step += 1
                        args_preview = str(dict(part.function_call.args))[:300]
                        print(f"\n{'─'*60}")
                        print(f"[Step {step} — Tool Call] {part.function_call.name}")
                        print(f"[Args] {args_preview}")
                    if hasattr(part, "function_response") and part.function_response:
                        print(f"[Tool Result] {str(part.function_response.response)[:400]}")
                    if part.text:
                        # Highlight <think> blocks vs regular agent text
                        text = part.text
                        if "<think>" in text:
                            print(f"\n[🧠 Think]\n{text}")
                        else:
                            print(f"\n[Agent] {text}")

    asyncio.run(run_query(
        "Give me the sales performance of all HappySnacks Potato Chips products in 2024 in each month"
    ))