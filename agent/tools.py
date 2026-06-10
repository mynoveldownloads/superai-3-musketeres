"""
tools.py — ADK tool definitions for the supermarket inventory agent.

Three tools exposed to the LLM:
  - metadata_txt_exists() : Check + read agent/metadata.txt schema cache
  - query_db(sql)         : POST to FastAPI /query, returns trimmed schema/data
  - render_chart(...)     : Re-runs verified SQL internally, renders matplotlib PNG
                            LLM never touches data values — fully deterministic.
"""

import os
import requests
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

API_URL = os.getenv("DB_API_URL", "http://127.0.0.1:3000/query")
# CHART_OUTPUT_DIR = os.getenv("CHART_OUTPUT_DIR", "./charts")
# NEW — always saves next to tools.py regardless of launch directory
CHART_OUTPUT_DIR = os.getenv(
    "CHART_OUTPUT_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "charts")
)
os.makedirs(CHART_OUTPUT_DIR, exist_ok=True)

# Resolved once at import time — tools.py lives in agent/agent2/
# so metadata.txt is one level up at agent/metadata.txt
_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
_METADATA_PATH = os.path.abspath(os.path.join(_TOOLS_DIR, "metadata.txt"))


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
    database via the internal FastAPI server at http://127.0.0.1:3000/query.

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
    matplotlib chart saved as a PNG. Data is fetched directly from the database
    — you do NOT pass any data values to this tool. This makes chart rendering
    fully deterministic and immune to LLM data hallucination.

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
        On success: {'status': 'ok', 'image_path': str, 'rows_plotted': int}
        On failure: {'status': 'error', 'message': str}
    """
    # Fix W7: validate output dir is writable before touching matplotlib
    if not os.access(CHART_OUTPUT_DIR, os.W_OK):
        return {
            "status": "error",
            "message": f"Chart output directory '{CHART_OUTPUT_DIR}' is not writable.",
        }

    # Re-fetch full dataset directly from DB — LLM never supplies values
    body = _run_sql(sql)
    if body.get("status") != "ok":
        return {
            "status": "error",
            "message": f"SQL re-execution failed: {body.get('message', 'unknown error')}",
        }

    columns = body["columns"]
    data = body["data"]

    if not data:
        return {"status": "error", "message": "SQL returned 0 rows. Nothing to render."}

    # Validate column references before touching matplotlib
    if x_col not in columns:
        return {
            "status": "error",
            "message": (
                f"x_col '{x_col}' not found in query result. "
                f"Available columns are: {columns}"
            ),
        }
    if chart_type != "pie" and y_col not in columns:
        return {
            "status": "error",
            "message": (
                f"y_col '{y_col}' not found in query result. "
                f"Available columns are: {columns}"
            ),
        }

    try:
        df = pd.DataFrame(data, columns=columns)
        datetime_fallback = False

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
                # Fix W6: flag fallback instead of silently degrading
                datetime_fallback = True
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
                "status": "error",
                "message": f"Unsupported chart_type '{chart_type}'. Use 'line', 'bar', or 'pie'.",
            }

        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
        if chart_type != "pie":
            ax.set_xlabel(x_label or x_col, fontsize=11)
            ax.set_ylabel(y_label or y_col, fontsize=11)
            ax.grid(axis="y", linestyle="--", alpha=0.4)

        plt.tight_layout()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in "_-" else "_" for c in title)[:40]
        filename = f"{safe_title}_{timestamp}.png"
        image_path = os.path.join(CHART_OUTPUT_DIR, filename)
        plt.savefig(image_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        result = {
            "status": "ok",
            "image_path": image_path,
            "rows_plotted": len(df),
        }
        if datetime_fallback:
            result["warning"] = (
                f"x_col '{x_col}' could not be parsed as datetime. "
                "X-axis rendered as string labels. Check date format in your SQL."
            )
        return result

    except Exception as e:
        return {"status": "error", "message": f"render_chart failed: {str(e)}"}