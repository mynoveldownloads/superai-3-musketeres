"""
tools.py — ADK tool definitions for the supermarket inventory agent.

Three tools exposed to the LLM:
  - metadata_txt_exists() : Check + read agent/metadata.txt schema cache
  - query_db(sql)         : POST to FastAPI /query, returns trimmed schema/data
  - render_chart(...)     : Re-runs verified SQL internally, renders matplotlib PNG
                            as base64. LLM never touches data values — fully deterministic.
"""

import os
import io
import base64
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
matplotlib.use("Agg")
from datetime import datetime

import ssl
import json
import httpx
import urllib3
import requests
from dotenv import load_dotenv

load_dotenv()

# ==============================================================================
# SSL FIX
# ==============================================================================
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_original_session_init = requests.Session.__init__

def _patched_session_init(self, *args, **kwargs):
    _original_session_init(self, *args, **kwargs)
    self.verify = False

requests.Session.__init__ = _patched_session_init

# --- OpenRouter Client Setup ---
http_client = httpx.Client(verify=False)

API_URL = os.getenv("DB_API_URL", "http://sql-backend:3000/api/sql/query")

# Resolved once at import time — tools.py lives in agent/
_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
_METADATA_PATH = os.path.abspath(os.path.join(_TOOLS_DIR, "metadata.txt"))

# Module-level store for the last rendered chart base64
last_chart_base64 = None


# ── Shared internal helper ─────────────────────────────────────────────────────

def _run_sql(sql: str) -> dict:
    """Internal helper — not exposed as an ADK tool. Calls the FastAPI server."""
    try:
        resp = requests.post(API_URL, json={"sql": sql}, timeout=15)
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": f"Could not connect to DB API at {API_URL}. Is the FastAPI server running?",
        }
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error calling DB API: {str(e)}"}


# ── Tool 1: metadata_txt_exists ────────────────────────────────────────────────

def metadata_txt_exists() -> dict:
    """
    Checks whether the pre-built database schema metadata file exists at
    agent/metadata.txt. You MUST call this as your very first action before
    any other tool call.

    If the file exists, its full contents are returned in the 'schema' field.
    Use this schema to understand all table names, column names, data types,
    and foreign key relationships WITHOUT needing to run any SELECT * LIMIT 5
    probes. You can proceed directly to building your JOIN query.

    If the file does not exist, 'schema' will be None. In that case you MUST
    fall back to schema discovery by calling query_db with SELECT * LIMIT 5
    for every relevant table before building any JOIN query.

    Returns:
        {'exists': True,  'schema': <full metadata.txt contents as string>}
        {'exists': False, 'schema': None}
    """
    if os.path.exists(_METADATA_PATH):
        try:
            with open(_METADATA_PATH, "r", encoding="utf-8") as f:
                contents = f.read()
            return {"exists": True, "schema": contents}
        except Exception as e:
            return {
                "exists": False,
                "schema": None,
                "warning": f"metadata.txt found but could not be read: {str(e)}",
            }
    return {"exists": False, "schema": None}


# ── Tool 2: query_db ───────────────────────────────────────────────────────────

def query_db(sql: str) -> dict:
    """
    Executes a read-only SELECT query against the supermarket inventory SQLite
    database via the internal FastAPI server at http://sql-backend:3000/api/sql/query.

    Use this tool to:
    1. EXPLORE schema (only if metadata_txt_exists returned exists=False):
       run 'SELECT * FROM <table> LIMIT 5' for each relevant table to discover
       column names and FK patterns. Available tables: inventory, orders,
       products, sales_items, suppliers.
    2. RETRIEVE data: craft a precise SELECT with JOINs, WHERE, and GROUP BY
       to fetch exactly the data needed to answer the user's question.
    3. VERIFY results: inspect 'columns' and the first few rows of 'data' to
       confirm the result shape is correct before calling render_chart.

    Only SELECT statements are allowed. No semicolons. No write operations.
    If a query fails, the returned dict will have status 'error' or 'rejected'
    with a 'message' explaining why — correct your SQL and retry.

    IMPORTANT: To keep your context window clean, only the first 5 rows of
    'data' are returned to you for inspection. The full dataset is fetched
    fresh inside render_chart when you pass the same sql string.

    Args:
        sql: A valid SELECT statement targeting the inventory database.

    Returns:
        On success: {'status': 'ok', 'rows_returned': int,
                     'columns': [str, ...], 'data': [first 5 row dicts]}
        On failure: {'status': 'error'|'rejected', 'message': str}
    """
    body = _run_sql(sql)
    if body.get("status") != "ok":
        return body

    # Fix W8: return only first 5 rows to LLM to avoid context bloat.
    # Full data is re-fetched inside render_chart via _run_sql.
    trimmed = dict(body)
    trimmed["data"] = body["data"][:5]
    trimmed["note"] = (
        f"Showing first 5 of {body['rows_returned']} rows. "
        "Full dataset will be used when you call render_chart with this sql."
    )
    return trimmed


# ── Tool 3: render_chart ───────────────────────────────────────────────────────

def render_chart(
    sql: str,
    chart_type: str,
    x_col: str,
    y_col: str,
    title: str,
    x_label: str = "",
    y_label: str = "",
) -> dict:
    """
    Re-executes a verified SQL query and renders the full result as a static
    matplotlib chart, returned as a base64-encoded PNG string.

    Call this tool ONLY after:
    1. You have called query_db with this exact sql.
    2. You have confirmed the returned columns and sample rows look correct.
    3. You have stated your reasoning for chart_type, x_col, y_col choices.

    Pass the EXACT same sql string from your final verified query_db call.

    Supported chart_type values:
      'line' — trend over time; x_col should be a date/time column.
      'bar'  — comparison across categories; x_col is a label column.
      'pie'  — proportional breakdown; x_col = labels, y_col = values.

    Args:
        sql:        The EXACT verified SELECT used in your final query_db call.
        chart_type: One of 'line', 'bar', 'pie'.
        x_col:      Column name for x-axis (must exist in sql result columns).
        y_col:      Column name for y-axis (must exist in sql result columns).
        title:      Descriptive chart title shown at the top of the image.
        x_label:    Optional human-readable x-axis label.
        y_label:    Optional human-readable y-axis label.

    Returns:
        On success: {'message': str, 'base64': str}
        On failure: {'message': str, 'base64': ''}
    """
    # Re-fetch full dataset directly from DB — LLM never supplies values
    body = _run_sql(sql)
    if body.get("status") != "ok":
        return {
            "message": f"SQL re-execution failed: {body.get('message', 'unknown error')}",
            "base64": "",
        }

    columns = body["columns"]
    data = body["data"]

    if not data:
        return {"message": "SQL returned 0 rows. Nothing to render.", "base64": ""}

    # Validate column references
    if x_col not in columns:
        return {
            "message": f"x_col '{x_col}' not found in query result. Available columns: {columns}",
            "base64": "",
        }
    if chart_type != "pie" and y_col not in columns:
        return {
            "message": f"y_col '{y_col}' not found in query result. Available columns: {columns}",
            "base64": "",
        }

    try:
        df = pd.DataFrame(data, columns=columns)
        warning_msg = ""

        fig, ax = plt.subplots(figsize=(12, 5))
        fig.patch.set_facecolor("#f9f9f9")
        ax.set_facecolor("#f9f9f9")

        if chart_type == "line":
            try:
                df[x_col] = pd.to_datetime(df[x_col])
                df = df.sort_values(x_col)
                ax.plot(
                    df[x_col],
                    pd.to_numeric(df[y_col], errors="coerce"),
                    marker="o", markersize=3, linewidth=1.8, color="#2196F3",
                )
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
                ax.xaxis.set_major_locator(mdates.MonthLocator())
                fig.autofmt_xdate()
            except Exception:
                warning_msg = f" (Note: x_col '{x_col}' could not be parsed as datetime, rendered as string labels.)"
                ax.plot(
                    df[x_col].astype(str),
                    pd.to_numeric(df[y_col], errors="coerce"),
                    marker="o", linewidth=1.8, color="#2196F3",
                )
                plt.xticks(rotation=45, ha="right")

        elif chart_type == "bar":
            ax.bar(
                df[x_col].astype(str),
                pd.to_numeric(df[y_col], errors="coerce"),
                color="#4CAF50", edgecolor="white",
            )
            plt.xticks(rotation=45, ha="right")

        elif chart_type == "pie":
            values = pd.to_numeric(df[y_col], errors="coerce").fillna(0)
            ax.pie(
                values, labels=df[x_col].astype(str),
                autopct="%1.1f%%", startangle=140,
                colors=plt.cm.Set3.colors,
            )
            ax.axis("equal")

        else:
            plt.close(fig)
            return {
                "message": f"Unsupported chart_type '{chart_type}'. Use 'line', 'bar', or 'pie'.",
                "base64": "",
            }

        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
        if chart_type != "pie":
            ax.set_xlabel(x_label or x_col, fontsize=11)
            ax.set_ylabel(y_label or y_col, fontsize=11)
            ax.grid(axis="y", linestyle="--", alpha=0.4)

        plt.tight_layout()

        # Render to base64 instead of saving to disk
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        # Store in module-level variable for external access
        global last_chart_base64
        last_chart_base64 = img_base64

        message = f"Chart rendered successfully: '{title}' ({chart_type} chart, {len(df)} data points).{warning_msg}"

        return {
            "message": message,
            "base64": img_base64,
        }

    except Exception as e:
        return {"message": f"render_chart failed: {str(e)}", "base64": ""}