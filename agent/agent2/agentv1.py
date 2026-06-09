"""
agent.py — ADK LlmAgent for supermarket inventory data visualization.

Uses LiteLlm to route through OpenRouter (same API key + model as the
teammate's non-ADK agent), but hands orchestration to ADK's agent loop.

The agent freely calls query_db() to explore schema and retrieve data,
then calls render_chart() once it has the final result set.
The ONLY hard stop is max_iterations (token/step budget).
"""

import os
import ssl
import urllib3
import requests
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from tools import query_db, render_chart

load_dotenv()

# ==============================================================================
# SSL FIX — same as teammate's agent.py (dev only, remove for production)
# ==============================================================================
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_original_session_init = requests.Session.__init__

def _patched_session_init(self, *args, **kwargs):
    _original_session_init(self, *args, **kwargs)
    self.verify = False

requests.Session.__init__ = _patched_session_init

# ==============================================================================
# Model — identical OpenRouter API key + model name as teammate's agent
# LiteLlm bridges ADK ↔ OpenRouter using the 'openrouter/' prefix
# ==============================================================================
MODEL = LiteLlm(
    model="openrouter/google/gemini-3.1-flash-lite",   # same model string as teammate
    api_key=os.getenv("OPENROUTER_API_KEY"),
    api_base="https://openrouter.ai/api/v1",
)

# ==============================================================================
# System prompt
# ==============================================================================
SYSTEM_PROMPT = """
You are an intelligent data analyst agent for a supermarket inventory management system.
You have access to a SQLite database through the query_db tool, and can render charts
with the render_chart tool.

Available tables: inventory, orders, products, sales_items, suppliers.
You do NOT know the column names in advance.

Your reasoning process MUST follow these steps:

STEP 1 — SCHEMA DISCOVERY
Before writing any JOIN or filtered query, run:
  SELECT * FROM <table> LIMIT 5
for EVERY table that is likely relevant to the user's question.
This reveals column names, data types, and foreign key patterns.

STEP 2 — PLAN THE FINAL QUERY
After inspecting sample rows, identify:
  - Which tables need to be JOINed and on which keys
  - Which column holds the metric the user wants (e.g. quantity, revenue)
  - Which column holds the time dimension or category for the x-axis
  - What WHERE / GROUP BY / ORDER BY clauses are needed

STEP 3 — EXECUTE THE FINAL QUERY
Call query_db with the precise SELECT + JOIN + WHERE + GROUP BY query.
If the result is empty or malformed, revisit your schema understanding and retry.

STEP 4 — RENDER THE CHART
Call render_chart ONLY once you have a clean, correctly shaped result set.
Choose chart_type based on the user's question:
  - 'line' for trends over time
  - 'bar'  for comparisons across products/categories
  - 'pie'  for proportional breakdowns

IMPORTANT RULES:
- Never guess column names. Always discover them via LIMIT 5 probes first.
- Only SELECT statements are allowed. Never attempt INSERT, UPDATE, DROP, etc.
- If query_db returns an error, read the message and correct your SQL before retrying.
- Call render_chart exactly once as your final action. After it succeeds, stop.
""".strip()

# ==============================================================================
# ADK Agent definition
# root_agent is the required name for ADK's runner to auto-discover this agent
# ==============================================================================
root_agent = LlmAgent(
    name="inventory_data_visual_agent",
    model=MODEL,
    instruction=SYSTEM_PROMPT,
    description=(
        "Answers supermarket inventory questions by querying the SQLite database "
        "and rendering a matplotlib chart. Discovers schema dynamically before "
        "building JOIN queries."
    ),
    tools=[query_db, render_chart],
    # max_steps=12,
)


# # ==============================================================================
# # Local test runner (bypasses ADK web UI)
# # ==============================================================================
# if __name__ == "__main__":
#     import asyncio
#     import json
#     from google.adk.runners import Runner
#     from google.adk.sessions import InMemorySessionService
#     from google.genai import types

#     async def run_query(user_message: str):
#         session_service = InMemorySessionService()
#         session = await session_service.create_session(
#             app_name="inventory_agent",
#             user_id="dev",
#             session_id="test-session-01",
#         )
#         runner = Runner(
#             agent=root_agent,
#             app_name="inventory_agent",
#             session_service=session_service,
#         )
#         content = types.Content(
#             role="user",
#             parts=[types.Part(text=user_message)],
#         )
#         print(f"\n{'='*60}")
#         print(f"Query: {user_message}")
#         print(f"{'='*60}")

#         async for event in runner.run_async(
#             user_id="dev",
#             session_id="test-session-01",
#             new_message=content,
#         ):
#             if event.is_final_response():
#                 for part in event.content.parts:
#                     if part.text:
#                         print(f"\n[Agent Final Response]\n{part.text}")

#     asyncio.run(run_query("How is the performance of milk sales this month?"))



# ==============================================================================
# Local test runner
# ==============================================================================
if __name__ == "__main__":
    import asyncio
    import json
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    async def run_query(user_message: str):
        session_service = InMemorySessionService()
        session = await session_service.create_session(
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
            # Print every tool call and response so you can follow the loop
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        print(f"\n[Tool Call] {part.function_call.name}({dict(part.function_call.args)})")
                    if hasattr(part, "function_response") and part.function_response:
                        print(f"[Tool Result] {str(part.function_response.response)[:300]}")
                    if part.text:
                        print(f"\n[Agent] {part.text}")

    asyncio.run(run_query("Give me the sales performance of all HappySnacks Potato Chips products over time"))