"""
tools.py — ADK tool definitions for the supermarket inventory agent.

Two tools exposed to the LLM:
  - query_db(sql)      : POST to FastAPI /query, returns schema/data for inspection
  - render_chart(...)  : Re-runs the SAME sql internally, then renders chart from result
                         The LLM never touches the data values — fully deterministic.
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
CHART_OUTPUT_DIR = os.getenv("CHART_OUTPUT_DIR", "./charts")
os.makedirs(CHART_OUTPUT_DIR, exist_ok=True)


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


# ── Tool 1: query_db ───────────────────────────────────────────────────────────

def query_db(sql: str) -> dict:
    """
    Executes a read-only SELECT query against the supermarket inventory SQLite
    database via the internal FastAPI server at http://127.0.0.1:3000/query.

    Use this tool to:
    1. EXPLORE schema: run 'SELECT * FROM <table> LIMIT 5' for each of the
       available tables to discover column names and data types before building
       any JOIN query. Available tables: inventory, orders, products,
       sales_items, suppliers.
    2. RETRIEVE data: after understanding the schema, craft a precise SELECT
       with the necessary JOINs, filters (WHERE), and aggregations (GROUP BY)
       to fetch exactly the data needed to answer the user's question.
    3. VERIFY results: inspect the returned rows to confirm the data shape is
       correct before passing the sql to render_chart.

    Only SELECT statements are allowed. No semicolons. No write operations.
    If a query is malformed or blocked, the returned dict will contain a
    'status' of 'error' or 'rejected' — read the message and retry.

    Args:
        sql: A valid SELECT statement targeting the inventory database.

    Returns:
        On success: {'status': 'ok', 'rows_returned': int,
                     'columns': [str, ...], 'data': [dict, ...]}
        On failure: {'status': 'error'|'rejected', 'message': str}
    """
    return _run_sql(sql)


# ── Tool 2: render_chart ───────────────────────────────────────────────────────

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
    Re-executes a verified SQL query and renders the result as a static
    matplotlib chart saved as a PNG. The data is fetched directly from the
    database — you do NOT pass any data values to this tool.

    Call this tool ONLY after you have already called query_db with the same
    sql and confirmed the returned rows and columns look correct. Pass the
    EXACT same sql string you used in that final query_db call.

    Supported chart_type values:
      'line' — trend over time; x_col should be a date/time column.
      'bar'  — comparison across categories; x_col should be a label column.
      'pie'  — proportional breakdown; x_col = label col, y_col = value col.

    Args:
        sql:        The EXACT same verified SELECT statement used in query_db.
                    This is re-executed to fetch fresh, authoritative data.
        chart_type: One of 'line', 'bar', 'pie'.
        x_col:      Column name for the x-axis (must exist in the sql result).
        y_col:      Column name for the y-axis (must exist in the sql result).
        title:      Descriptive chart title shown at the top of the image.
        x_label:    Optional human-readable label for the x-axis.
        y_label:    Optional human-readable label for the y-axis.

    Returns:
        On success: {'status': 'ok', 'image_path': str, 'rows_plotted': int}
        On failure: {'status': 'error', 'message': str}
    """
    # Step 1: Re-fetch data directly from DB — LLM never supplies values
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

    # Step 2: Validate column references before touching matplotlib
    if x_col not in columns:
        return {"status": "error", "message": f"x_col '{x_col}' not found in query result columns: {columns}"}
    if chart_type != "pie" and y_col not in columns:
        return {"status": "error", "message": f"y_col '{y_col}' not found in query result columns: {columns}"}

    # Step 3: Build DataFrame and render
    try:
        df = pd.DataFrame(data, columns=columns)

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

        return {
            "status": "ok",
            "image_path": image_path,
            "rows_plotted": len(df),
        }

    except Exception as e:
        return {"status": "error", "message": f"render_chart failed: {str(e)}"}