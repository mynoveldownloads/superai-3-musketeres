"""
tools.py — shared tool definitions for the supermarket inventory ADK agent.

Tools:
- metadata_txt_exists(): checks whether agent/metadata.txt exists and returns its contents
- query_db(sql): executes read-only SQL against the FastAPI /query endpoint
- render_chart(sql, ...): fetches data via SQL and renders a deterministic matplotlib chart
"""

import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = os.getenv("DB_API_URL", "http://127.0.0.1:3000/query")
CHART_OUTPUT_DIR = os.getenv("CHART_OUTPUT_DIR", os.path.join(os.path.dirname(__file__), "charts"))
os.makedirs(CHART_OUTPUT_DIR, exist_ok=True)

_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
_METADATA_PATH = os.path.abspath(os.path.join(_TOOLS_DIR, "metadata.txt"))


def _run_sql(sql: str) -> dict:
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


def metadata_txt_exists() -> dict:
    """
    Checks whether agent/metadata.txt exists.

    Returns:
        {'exists': True, 'schema': <contents>} or {'exists': False, 'schema': None}
    """
    if os.path.exists(_METADATA_PATH):
        try:
            with open(_METADATA_PATH, "r", encoding="utf-8") as f:
                return {"exists": True, "schema": f.read()}
        except Exception as e:
            return {"exists": False, "schema": None, "warning": f"Could not read metadata.txt: {str(e)}"}
    return {"exists": False, "schema": None}


def query_db(sql: str) -> dict:
    """
    Executes a read-only SQL query through the FastAPI server.

    Returns only the first 5 rows to the LLM to reduce context bloat.
    """
    body = _run_sql(sql)
    if body.get("status") != "ok":
        return body

    body["data"] = body.get("data", [])[:5]
    body["note"] = f"Showing first 5 of {body.get('rows_returned', 0)} rows."
    return body


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
    Re-runs the verified SQL and renders a deterministic matplotlib chart.
    """
    if not os.access(CHART_OUTPUT_DIR, os.W_OK):
        return {"status": "error", "message": f"Chart output directory '{CHART_OUTPUT_DIR}' is not writable."}

    body = _run_sql(sql)
    if body.get("status") != "ok":
        return {"status": "error", "message": f"SQL re-execution failed: {body.get('message', 'unknown error')}"}

    columns = body["columns"]
    data = body["data"]

    if not data:
        return {"status": "error", "message": "SQL returned 0 rows. Nothing to render."}
    if x_col not in columns:
        return {"status": "error", "message": f"x_col '{x_col}' not found in query result. Available columns: {columns}"}
    if chart_type != "pie" and y_col not in columns:
        return {"status": "error", "message": f"y_col '{y_col}' not found in query result. Available columns: {columns}"}

    try:
        df = pd.DataFrame(data, columns=columns)
        fig, ax = plt.subplots(figsize=(12, 5))
        fig.patch.set_facecolor("#f9f9f9")
        ax.set_facecolor("#f9f9f9")

        if chart_type == "line":
            try:
                df[x_col] = pd.to_datetime(df[x_col])
                df = df.sort_values(x_col)
                ax.plot(df[x_col], pd.to_numeric(df[y_col], errors="coerce"), marker="o", linewidth=1.8, color="#2196F3")
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
                ax.xaxis.set_major_locator(mdates.MonthLocator())
                fig.autofmt_xdate()
            except Exception:
                ax.plot(df[x_col].astype(str), pd.to_numeric(df[y_col], errors="coerce"), marker="o", linewidth=1.8, color="#2196F3")
                plt.xticks(rotation=45, ha="right")

        elif chart_type == "bar":
            ax.bar(df[x_col].astype(str), pd.to_numeric(df[y_col], errors="coerce"), color="#4CAF50", edgecolor="white")
            plt.xticks(rotation=45, ha="right")

        elif chart_type == "pie":
            values = pd.to_numeric(df[y_col], errors="coerce").fillna(0)
            ax.pie(values, labels=df[x_col].astype(str), autopct="%1.1f%%", startangle=140, colors=plt.cm.Set3.colors)
            ax.axis("equal")

        else:
            plt.close(fig)
            return {"status": "error", "message": f"Unsupported chart_type '{chart_type}'."}

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

        result = {"status": "ok", "image_path": image_path, "rows_plotted": len(df)}
        return result
    except Exception as e:
        return {"status": "error", "message": f"render_chart failed: {str(e)}"}