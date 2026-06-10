"""
Stock Retrieval Module.

Handles stock order recommendations by:
1. Extracting the product from user input.
2. Querying SQL for sales figures (latest months).
3. Running the pre-trained RFR model to predict next order quantity.
4. LLM generates insight SQL queries based on db_schema.json.
5. Executes insight queries and retrieves inventory levels.
6. Final LLM evaluates all data and produces recommendation with reasoning.
"""

import os
import ssl
import json
import httpx
import urllib3
import requests
import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

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

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    http_client=http_client,
)

MODEL = "google/gemini-3.1-flash-lite"

# --- Load the pre-trained Random Forest Regression model ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml_model", "rfr_order_model.joblib")
rfr_model = joblib.load(MODEL_PATH)


def load_db_schema() -> dict:
    """Load the inferred database schema from db_schema.json."""
    schema_path = os.path.join(os.path.dirname(__file__), "db_schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def execute_sql_function(sql: str) -> dict:
    """Execute a SQL query against the database."""
    resp = requests.post(
        "http://127.0.0.1:3000/query",
        json={"sql": sql}
    )
    return resp.json()


def extract_data(result: dict) -> list:
    """Extract the 'data' list from API response dict."""
    if isinstance(result, dict):
        return result.get("data", [])
    return result if isinstance(result, list) else []


def product_extraction(user_input: str) -> str:
    """Use LLM to match user's product mention to an actual product in the database."""
    product_list = execute_sql_function("SELECT DISTINCT product_name FROM products;")
    product_list_data = extract_data(product_list)

    product_prompt = (
        "You are a product detector for an AI agent that handles inventory for a supermarket.\n"
        "You are provided a list of products and a user prompt.\n"
        "Match the product the user is asking for with a product on the list.\n"
        "Return only the product name as a string. No other text.\n"
        "Example input: im looking for sparklePro lanudry detergent\n"
        "Example output: SparklePro Laundry Detergent"
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": product_prompt},
            {"role": "user", "content": json.dumps({
                "product_line": product_list_data,
                "user_input": user_input
            })},
        ],
    )

    return response.choices[0].message.content.strip()


def get_product_id(product_name: str) -> int:
    """Get the product_id for a given product_name."""
    sql = f"SELECT product_id FROM products WHERE product_name = '{product_name}' LIMIT 1;"
    result = execute_sql_function(sql)
    data = extract_data(result)
    if data:
        return int(data[0].get("product_id", 0))
    return 0


def get_sales_figures(product_id: int) -> list:
    """Query sales figures for Apr & May 2025 (ISO 8601 dates: 2025-04-xxTxx:xx:xxZ)."""
    sql = f"""
        SELECT 
            product_id,
            CAST(SUBSTR(created_at, 6, 2) AS INTEGER) AS mth,
            CAST(SUBSTR(created_at, 1, 4) AS INTEGER) AS year,
            SUM(quantity) AS sales_qty
        FROM sales_items
        WHERE product_id = {product_id}
        AND SUBSTR(created_at, 1, 4) = '2025'
        AND SUBSTR(created_at, 6, 2) IN ('04', '05')
        GROUP BY product_id, mth
        ORDER BY mth;
    """
    result = execute_sql_function(sql)
    return extract_data(result)


def predict_order_quantity(product_id: int, sales_data: list) -> list:
    """
    Use the pre-trained RFR model to predict the next order quantity.
    Model expects one-hot encoded product_id, mth, and sales_qty as features.
    """
    feature_names = rfr_model.feature_names_in_
    predictions = []

    for row in sales_data:
        mth = int(row["mth"])
        sales_qty = int(row["sales_qty"])

        input_data = pd.DataFrame(np.zeros((1, len(feature_names))), columns=feature_names)

        if "sales_qty" in input_data.columns:
            input_data["sales_qty"] = float(sales_qty)

        product_col = f"product_id_{product_id}"
        if product_col in input_data.columns:
            input_data[product_col] = 1.0

        mth_col = f"mth_{mth}"
        if mth_col in input_data.columns:
            input_data[mth_col] = 1.0

        predicted_qty = rfr_model.predict(input_data)[0]

        predictions.append({
            "product_id": product_id,
            "month": mth,
            "year": 2025,
            "sales_qty": sales_qty,
            "predicted_order_qty": round(predicted_qty),
        })

    return predictions


def generate_insight_queries(product_id: int, product_name: str, db_schema: dict) -> list:
    """
    Use LLM to generate SQL queries that reveal trends/insights about the product.
    Returns a list of SQL query strings.
    """
    prompt = (
        "You are a SQL query generator for a supermarket inventory management system.\n"
        "Given the database schema below and a specific product, generate exactly 3 SQL queries "
        "that will provide useful TREND insights for deciding how much stock to order.\n\n"
        "Focus on:\n"
        "1. Monthly sales trend for this product over the past 12 months (quantity sold per month).\n"
        "2. Monthly order history for this product over the past 12 months (quantity ordered per month).\n"
        "3. Average order fulfillment rate (received_qty vs ordered_qty) for this product.\n\n"
        "IMPORTANT NOTES:\n"
        "- The created_at columns are in ISO 8601 format: '2025-05-12T15:47:00Z'\n"
        "- Use SUBSTR(created_at, 1, 7) to get 'YYYY-MM' for monthly grouping.\n"
        "- The sales table is called 'sales_items' and uses 'quantity' column.\n"
        "- The orders table is called 'orders' and uses 'ordered_qty' and 'received_qty' columns.\n"
        f"- Filter by product_id = {product_id}\n\n"
        "Return ONLY a JSON array of 3 SQL query strings. No markdown, no explanation.\n"
        'Example: ["SELECT ...", "SELECT ...", "SELECT ..."]'
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(db_schema)},
        ],
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    return json.loads(raw)


def get_inventory_level(product_id: int) -> dict:
    """Get current inventory information for the product."""
    sql = f"SELECT * FROM inventory WHERE product_id = {product_id};"
    result = execute_sql_function(sql)
    data = extract_data(result)
    return data[0] if data else {}


def final_recommendation(
    product_name: str,
    product_id: int,
    ml_predictions: list,
    insight_results: list,
    inventory_info: dict,
) -> dict:
    """
    Final LLM call that evaluates all data and produces a stock order recommendation.
    """
    prompt = (
        "You are a senior inventory analyst for a supermarket. You are given:\n"
        "1. ML model predictions for next order quantity (based on recent sales).\n"
        "2. Trend insights from SQL queries (sales trends, order history, fulfillment rates).\n"
        "3. Current inventory stock level information.\n\n"
        "Your job is to recommend how many units to order for the next restocking cycle.\n"
        "Consider:\n"
        "- The ML prediction as a baseline.\n"
        "- Sales trends (increasing/decreasing demand).\n"
        "- Current stock on hand vs reorder point.\n"
        "- Historical order fulfillment rate (suppliers may short-deliver).\n"
        "- Reorder quantity guidelines from inventory settings.\n\n"
        "Return your response in this EXACT JSON format:\n"
        "{\n"
        '  "message": "<A full, human-readable message for the user. Must include ALL of the following sections clearly labeled:\\n'
        '\\n📊 DATA INSIGHTS:\\n- Insight 1 title: summary of the trend\\n- Insight 2 title: summary of the trend\\n- Insight 3 title: summary of the trend\\n'
        '\\n🤖 ML MODEL SUGGESTION:\\n- The ML model recommends X units, based on [explanation].\\n'
        '\\n✅ FINAL RECOMMENDATION:\\n- Order X units of [product name].\\n'
        '\\n💡 REASONING:\\n- [3-5 sentences explaining why you adjusted or agreed with the ML suggestion, referencing trends, inventory, and fulfillment rates.]>",\n'
        '  "reports": [\n'
        '    {"title": "<short title for insight 1>", "summary": "<1-2 sentence interpretation of the trend data>"},\n'
        '    {"title": "<short title for insight 2>", "summary": "<1-2 sentence interpretation>"},\n'
        '    {"title": "<short title for insight 3>", "summary": "<1-2 sentence interpretation>"}\n'
        "  ],\n"
        '  "ml_suggestion": {\n'
        '    "qty": <the ML predicted quantity>,\n'
        '    "explanation": "<1 sentence explaining what the ML model based its prediction on>"\n'
        "  },\n"
        '  "recommendation": {\n'
        f'    "product": "{product_name}",\n'
        '    "qty": <your final recommended integer quantity to order>\n'
        "  },\n"
        '  "reasoning": "<Your detailed reasoning in 3-5 sentences>"\n'
        "}\n\n"
        "The 'message' field is what the user will read directly. It MUST contain all the transparency info: "
        "the data insights, the ML suggestion, the final recommendation, and the reasoning. "
        "Make it clear, professional, and easy to understand.\n\n"
        "Return ONLY the JSON. No markdown, no extra text."
    )

    user_content = json.dumps({
        "product_name": product_name,
        "product_id": product_id,
        "ml_predictions": ml_predictions,
        "trend_insights": insight_results,
        "current_inventory": inventory_info,
    })

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content},
        ],
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    return json.loads(raw)


def handle_stock_order(user_input: str) -> dict:
    """
    Entry point for stock order processing.
    Called by agent.py when intent is classified as STOCK_ORDER.
    """
    # Step 1: Extract product name from user input
    product_name = product_extraction(user_input)

    # Step 2: Get product_id
    product_id = get_product_id(product_name)
    if product_id == 0:
        return {
            "message": f"Could not find product '{product_name}' in the database.",
            "recommendation": None,
            "base64": None,
        }

    # Step 3: Query sales figures for Apr/May 2025
    sales_data = get_sales_figures(product_id)
    if not sales_data:
        return {
            "message": f"No sales data found for product '{product_name}' (ID: {product_id}) in Apr/May 2025.",
            "recommendation": None,
            "base64": None,
        }

    # Step 4: Run RFR model prediction
    ml_predictions = predict_order_quantity(product_id, sales_data)

    # Step 5: LLM generates insight SQL queries
    db_schema = load_db_schema()
    insight_queries = generate_insight_queries(product_id, product_name, db_schema)

    # Step 6: Execute insight queries and collect results
    insight_results = []
    for i, sql in enumerate(insight_queries):
        result = execute_sql_function(sql)
        insight_results.append({
            "query_index": i + 1,
            "sql": sql,
            "data": extract_data(result),
        })

    # Step 7: Get current inventory level
    inventory_info = get_inventory_level(product_id)

    # Step 8: Get supplier name
    supplier_sql = f"SELECT s.supplier_name FROM suppliers s INNER JOIN products p ON s.supplier_id=p.supplier_id WHERE p.product_id={product_id};"
    supplier_result = execute_sql_function(supplier_sql)
    supplier_data = extract_data(supplier_result)
    supplier_name = supplier_data[0].get("supplier_name", "Unknown") if supplier_data else "Unknown"

    # Step 9: Final LLM recommendation
    recommendation = final_recommendation(
        product_name=product_name,
        product_id=product_id,
        ml_predictions=ml_predictions,
        insight_results=insight_results,
        inventory_info=inventory_info,
    )

    # Build final output — only qty, product_name, supplier_name
    rec = recommendation.get("recommendation", {})
    final_rec = {
        "product_name": product_name,
        "supplier_name": supplier_name,
        "qty": rec.get("qty", 0),
    }

    return {
        "message": recommendation.get("message", ""),
        "recommendation": final_rec,
        "base64": None,
    }
