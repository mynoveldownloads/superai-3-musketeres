"""
agent.py — standardized ADK agent for supermarket inventory tasks.

Uses LiteLlm with the same OpenRouter model as the teammate's agent.
This agent can:
- check metadata.txt schema cache
- query the FastAPI SQL endpoint
- render deterministic matplotlib charts
"""

import os
import ssl
import urllib3
import requests
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from tools import metadata_txt_exists, query_db, render_chart

load_dotenv()

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_original_session_init = requests.Session.__init__


def _patched_session_init(self, *args, **kwargs):
    _original_session_init(self, *args, **kwargs)
    self.verify = False


requests.Session.__init__ = _patched_session_init

MODEL = LiteLlm(
    model="openrouter/google/gemini-3.1-flash-lite",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    api_base="https://openrouter.ai/api/v1",
)

SYSTEM_PROMPT = """
You are an intelligent supermarket assistant.

You have three tools:
1. metadata_txt_exists — check whether schema cache exists and read it
2. query_db — execute read-only SQL against the inventory database
3. render_chart — render a deterministic chart from the final SQL

Rules:
- Your first action must always be metadata_txt_exists.
- If metadata.txt exists, use it to reason about the schema and skip exploratory LIMIT 5 probes.
- If metadata.txt does not exist, probe relevant tables with SELECT * FROM <table> LIMIT 5 before building the final query.
- Use query_db to inspect sample rows and verify columns before the final query.
- Use render_chart only after you have a correct final SQL statement.
- Never pass raw data rows to render_chart. Pass the SQL string only.
- Call render_chart exactly once as the final action.
- Only use SELECT queries.
- For debugging, explain your reasoning briefly before each tool call.
"""

root_agent = LlmAgent(
    name="inventory_data_visual_agent",
    model=MODEL,
    instruction=SYSTEM_PROMPT,
    description=(
        "Supermarket inventory agent that checks metadata.txt, queries the SQL API, "
        "and renders charts deterministically."
    ),
    tools=[metadata_txt_exists, query_db, render_chart],
)

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

        print(f"\n{'=' * 60}")
        print(f"Query: {user_message}")
        print(f"{'=' * 60}")

        async for event in runner.run_async(
            user_id="dev",
            session_id="test-session-01",
            new_message=content,
        ):
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        print(f"\n[Tool Call] {part.function_call.name}({dict(part.function_call.args)})")
                    if hasattr(part, "function_response") and part.function_response:
                        print(f"[Tool Result] {str(part.function_response.response)[:500]}")
                    if part.text:
                        print(f"\n[Agent] {part.text}")

    asyncio.run(run_query("Give me the sales performance of all HappySnacks Potato Chips products over time"))