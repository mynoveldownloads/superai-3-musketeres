"""
tools.py — ADK tool definitions for the supermarket inventory agent.

Two tools exposed to the LLM:
  - query_db(sql)      : POST to FastAPI /query, returns schema/data
  - render_chart(...)  : Build matplotlib PNG from query result data
"""

import os
import requests
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend, safe for server use
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

API_URL = os.getenv("DB_API_URL", "http://127.0.0.1:3000/query")
CHART_OUTPUT_DIR = os.getenv("CHART_OUTPUT_DIR", "./charts")
os.makedirs(CHART_OUTPUT_DIR, exist_ok=True)


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

    Only SELECT statements are allowed. No semicolons. No write operations.
    If a query is malformed or blocked, the returned dict will contain an
    'error' key — read the message and try a corrected query.

    Args:
        sql: A valid SELECT statement targeting the inventory database.

    Returns:
        On success: {'status': 'ok', 'rows_returned': int,
                     'columns': [str, ...], 'data': [dict, ...]}
        On failure: {'status': 'error'|'rejected', 'message': str}
    """
    try:
        resp = requests.post(API_URL, json={"sql": sql}, timeout=15)
        body = resp.json()
        return body
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": f"Could not connect to DB API at {API_URL}. Is the FastAPI server running?",
        }
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error calling DB API: {str(e)}"}


def render_chart(
    columns: list[str],
    data: list[dict],
    chart_type: str,
    x_col: str,
    y_col: str,
    title: str,
    x_label: str = "",
    y_label: str = "",
) -> dict:
    """
    Renders a static matplotlib chart from a query result and saves it as a PNG.

    Call this tool ONLY after query_db has returned the final, correctly shaped
    result set that directly answers the user's question. Do NOT call this with
    raw schema-exploration results (e.g. LIMIT 5 probes).

    Supported chart_type values:
      'line' — trend over time; x_col should be a date/time column.
      'bar'  — comparison across categories; x_col should be a label column.
      'pie'  — proportional breakdown; x_col = label col, y_col = value col.

    Args:
        columns:    Column names from the query_db result (the 'columns' field).
        data:       Row dicts from the query_db result (the 'data' field).
        chart_type: One of 'line', 'bar', 'pie'.
        x_col:      Column name to use as x-axis values (or pie slice labels).
        y_col:      Column name to use as y-axis values (or pie slice sizes).
        title:      Descriptive chart title shown at the top of the image.
        x_label:    Optional label for the x-axis.
        y_label:    Optional label for the y-axis.

    Returns:
        On success: {'status': 'ok', 'image_path': str, 'message': str}
        On failure: {'status': 'error', 'message': str}
    """
    if not data:
        return {"status": "error", "message": "No data provided to render_chart. Query returned 0 rows."}
    if x_col not in columns:
        return {"status": "error", "message": f"x_col '{x_col}' not found in columns: {columns}"}
    if chart_type != "pie" and y_col not in columns:
        return {"status": "error", "message": f"y_col '{y_col}' not found in columns: {columns}"}

    try:
        df = pd.DataFrame(data, columns=columns)

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor("#f9f9f9")
        ax.set_facecolor("#f9f9f9")

        if chart_type == "line":
            # Attempt to parse x_col as datetime for proper time-series axis
            try:
                df[x_col] = pd.to_datetime(df[x_col])
                df = df.sort_values(x_col)
                ax.plot(df[x_col], pd.to_numeric(df[y_col], errors="coerce"),
                        marker="o", linewidth=2, color="#2196F3")
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
                fig.autofmt_xdate()
            except Exception:
                ax.plot(df[x_col].astype(str), pd.to_numeric(df[y_col], errors="coerce"),
                        marker="o", linewidth=2, color="#2196F3")
                plt.xticks(rotation=45, ha="right")

        elif chart_type == "bar":
            ax.bar(df[x_col].astype(str), pd.to_numeric(df[y_col], errors="coerce"),
                   color="#4CAF50", edgecolor="white")
            plt.xticks(rotation=45, ha="right")

        elif chart_type == "pie":
            values = pd.to_numeric(df[y_col], errors="coerce").fillna(0)
            ax.pie(values, labels=df[x_col].astype(str), autopct="%1.1f%%",
                   startangle=140, colors=plt.cm.Set3.colors)
            ax.axis("equal")

        else:
            plt.close(fig)
            return {"status": "error", "message": f"Unsupported chart_type '{chart_type}'. Use 'line', 'bar', or 'pie'."}

        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
        if chart_type != "pie":
            ax.set_xlabel(x_label or x_col, fontsize=11)
            ax.set_ylabel(y_label or y_col, fontsize=11)
            ax.grid(axis="y", linestyle="--", alpha=0.5)

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
            "message": f"Chart saved to {image_path}",
        }

    except Exception as e:
        return {"status": "error", "message": f"render_chart failed: {str(e)}"}