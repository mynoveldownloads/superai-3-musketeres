"""
api_server.py — FastAPI SQL Query Server for database.db
---------------------------------------------------------
Port    : 3000
Endpoint: POST /query
DB      : Resolved to ../init_db/database.db relative to this script file.
          Uses os.path.abspath to ensure correct resolution regardless of
          the working directory the server is launched from.

Whitelisting Rules:
  - Only SELECT statements are permitted.
  - The following SQL keywords are explicitly BLOCKED and will return a 403:
      DROP, DELETE, INSERT, UPDATE, REPLACE, ALTER, TRUNCATE,
      CREATE, ATTACH, DETACH, PRAGMA, VACUUM, REINDEX, ANALYZE
  - Semicolons are stripped to prevent statement stacking (e.g. SELECT 1; DROP TABLE ...)
  - Empty or non-string inputs return a 422 validation error.
  - Any SQL that raises a sqlite3 exception returns a 400 with the error detail.
  - If the database file does not exist at startup, the server will raise an error
    immediately rather than silently creating a blank database.

JSON Response Format (success):
  {
    "status": "ok",
    "rows_returned": <int>,
    "columns": [<str>, ...],
    "data": [ { <col>: <value>, ... }, ... ]
  }

JSON Response Format (rejected/error):
  {
    "status": "rejected" | "error",
    "message": "<reason>"
  }
"""

import re
import os
import sqlite3
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# ── DB path resolution ─────────────────────────────────────────────────────────
# Always resolve relative to THIS script file, not the working directory.
# This prevents sqlite3 from silently creating a blank database in whichever
# directory the server happens to be launched from.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(_SCRIPT_DIR, "../init_db/database.db"))

# Fail fast at import time if the database file doesn't exist.
if not os.path.exists(DB_PATH):
    raise FileNotFoundError(
        f"database.db not found at resolved path: {DB_PATH}\n"
        "Ensure init_db/database.db has been created before starting the server."
    )

print(f"✅ Database resolved at: {DB_PATH}")

# ── App init ───────────────────────────────────────────────────────────────────

app = FastAPI(
    title="database.db Query API",
    description="Read-only SQL query interface for database.db. Only SELECT statements are permitted.",
    version="1.0.0",
)

# ── Whitelist / Blacklist config ───────────────────────────────────────────────

# Keywords that indicate a write, destructive, or administrative operation.
# Matched as whole words (case-insensitive) to avoid false positives
# e.g. a column alias containing the word "update".
BLOCKED_KEYWORDS = [
    "DROP", "DELETE", "INSERT", "UPDATE", "REPLACE",
    "ALTER", "TRUNCATE", "CREATE", "ATTACH", "DETACH",
    "PRAGMA", "VACUUM", "REINDEX", "ANALYZE",
]

BLOCKED_PATTERN = re.compile(
    r"\b(" + "|".join(BLOCKED_KEYWORDS) + r")\b",
    re.IGNORECASE,
)


def is_safe_query(sql: str) -> tuple[bool, str]:
    """
    Validate a SQL string against the whitelist rules.

    Rules (in order):
      1. Must be a non-empty string.
      2. Must start with SELECT (after stripping whitespace).
      3. Must not contain any BLOCKED_KEYWORDS as whole words.
      4. Semicolons are stripped before execution to prevent stacking.

    Returns:
      (True, cleaned_sql)  — if query passes all checks
      (False, reason_str)  — if query is rejected
    """
    sql = sql.strip()

    # Rule 1: non-empty
    if not sql:
        return False, "Query is empty."

    # Rule 2: must start with SELECT
    if not re.match(r"^SELECT\b", sql, re.IGNORECASE):
        return False, (
            "Only SELECT statements are permitted. "
            "Data manipulation and schema modification queries are not allowed."
        )

    # Rule 3: blocked keyword check
    match = BLOCKED_PATTERN.search(sql)
    if match:
        return False, (
            f"Query contains a blocked keyword: '{match.group().upper()}'. "
            "Destructive or write operations are not permitted."
        )

    # Rule 4: strip semicolons to prevent statement stacking
    cleaned = sql.replace(";", "")

    return True, cleaned


# ── Request model ──────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    """
    Request body for POST /query.

    Fields:
      sql (str): A SQL SELECT statement to execute against database.db.

    Example:
      { "sql": "SELECT * FROM suppliers LIMIT 5" }
    """
    sql: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/", summary="Health check")
def root():
    """Returns a simple health-check confirming the server is running and which DB is in use."""
    return {
        "status": "ok",
        "message": "database.db Query API is running. POST /query to execute a SELECT statement.",
        "database": DB_PATH,
    }


@app.post("/query", summary="Execute a SELECT query")
async def execute_query(body: QueryRequest):
    """
    Execute a read-only SQL SELECT query against database.db.

    - **Allowed**: Any valid SELECT statement.
    - **Blocked**: DROP, DELETE, INSERT, UPDATE, REPLACE, ALTER, TRUNCATE,
      CREATE, ATTACH, DETACH, PRAGMA, VACUUM, REINDEX, ANALYZE.
    - **Stacking prevention**: Semicolons are stripped before execution.
    - **Malformed SQL**: Returns HTTP 400 with the sqlite3 error detail.
    - **Blocked query**: Returns HTTP 403 with a rejection reason.
    """

    # Input guard
    if not isinstance(body.sql, str) or not body.sql.strip():
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "message": "Invalid input: 'sql' must be a non-empty string.",
            },
        )

    # Whitelist validation
    safe, result = is_safe_query(body.sql)
    if not safe:
        return JSONResponse(
            status_code=403,
            content={"status": "rejected", "message": result},
        )

    cleaned_sql = result

    # Execute against the resolved DB_PATH (never creates a new file)
    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(cleaned_sql)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description] if cur.description else []
        conn.close()

    except sqlite3.OperationalError as e:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": f"SQL execution error: {str(e)}"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Unexpected server error: {str(e)}"},
        )

    data = [dict(row) for row in rows]

    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "rows_returned": len(data),
            "columns": columns,
            "data": data,
        },
    )


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="127.0.0.1", port=3000, reload=False)
