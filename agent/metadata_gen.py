import os
import ssl
import json
import httpx
import urllib3
import requests
from dotenv import load_dotenv
from openai import OpenAI
from exa_py import Exa

load_dotenv()

# ==============================================================================
# SSL FIX — Bypass SSL certificate verification globally.
# Your antivirus or school network proxy performs HTTPS/TLS inspection,
# replacing certificates with its own. Python doesn't trust these certs.
# This disables verification for ALL Python HTTP libraries.
# WARNING: Development only. Remove for production.
# ==============================================================================

# 1. Patch Python's built-in SSL so all new contexts skip verification
ssl._create_default_https_context = ssl._create_unverified_context

# 2. Suppress urllib3 InsecureRequestWarning spam
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 3. Monkey-patch requests.Session so ALL requests calls use verify=False
_original_session_init = requests.Session.__init__

def _patched_session_init(self, *args, **kwargs):
    _original_session_init(self, *args, **kwargs)
    self.verify = False

requests.Session.__init__ = _patched_session_init

# Now import exa_py AFTER the patch so it picks up the patched Session
from exa_py import Exa

# --- OpenRouter Client Setup ---
http_client = httpx.Client(verify=False)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    http_client=http_client,
)

MODEL = "google/gemini-3.1-flash-lite"

##

large_json = {}

for i in ['orders', 'inventory', 'sales_items', 'suppliers', 'products']:
    resp = requests.post(
        "http://sql-backend:3000/api/sql/query",
        json={"sql": f"SELECT * FROM {i} LIMIT 10;"}
    )
    large_json[i] = resp.json()

print(large_json)

system_prompt = (
    "You are an intelligent metadata inference tool. Your job is to infer the metadata "
    "(that would otherwise reside in the INFORMATION_SCHEMA) of 5 tables in a database.\n\n"
    "You will be provided a subsample of 10 rows for each table. The context of the 5 tables will be given below.\n"
    "The data is data from a supermarket, and pertains to the data of products, sale records, order records from inventory department, etc.\n\n"
    "You must return an inferred metadata schema of EACH column in the 5 tables.\n"
    "In detail, you will return the table name, column name, data type, primary key, foreign key & references, nullable, and description of each column.\n\n"
    "You are to return as a JSON. Ensure that you follow this JSON structure EXACTLY:\n\n"
    "{\n"
    '  "table_name": {\n'
    '    "description": "A brief description of what this table stores",\n'
    '    "columns": {\n'
    '      "column_name": {\n'
    '        "type": "DATA_TYPE (e.g. INTEGER, VARCHAR(255), DECIMAL(10,2), DATE, BOOLEAN)",\n'
    '        "primary_key": true or false,\n'
    '        "nullable": true or false,\n'
    '        "foreign_key": "referenced_table.referenced_column or null if not a FK",\n'
    '        "description": "A clear description of what this column represents",\n'
    '        "example": "An example value from the sample data provided"\n'
    '      }\n'
    '    }\n'
    '  }\n'
    "}\n\n"
    "RULES:\n"
    "1. Infer data types from the sample values (e.g., if all values are integers, use INTEGER; if they have decimals, use DECIMAL; if they are dates, use DATE).\n"
    "2. Infer primary keys by looking for columns with unique, sequential, or ID-like values.\n"
    "3. Infer foreign keys by matching column names and values across tables (e.g., if 'product_id' in sales matches 'product_id' in products, it is a FK).\n"
    "4. Infer nullable by checking if any NULL/empty values appear in the sample, or if the column logically could be empty.\n"
    "5. Write descriptions that explain the business meaning, not just the technical definition.\n"
    "6. Include one representative example value from the sample data for each column.\n"
    "7. If a column has a limited set of repeating values (e.g., status fields), add a 'valid_values' field listing all observed distinct values.\n\n"
    "Return ONLY the JSON object. No markdown, no explanation, no extra text."
)

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(large_json)},
    ],
)

# --- Step 1: Convert LLM response to JSON ---
raw_content = response.choices[0].message.content.strip()

# Strip markdown code fences if the LLM wraps it in ```json ... ```
if raw_content.startswith("```"):
    raw_content = raw_content.split("\n", 1)[1]  # Remove first line (```json)
    raw_content = raw_content.rsplit("```", 1)[0]  # Remove closing ```

inferred_schema = json.loads(raw_content)

print("\n=== Inferred Schema (Pass 1) ===")
print(json.dumps(inferred_schema, indent=2))

# --- Step 2: Refinement & Verification Pass ---

large_json2 = {}

for i in ['orders', 'inventory', 'sales_items', 'suppliers', 'products']:
    resp = requests.post(
        "http://sql-backend:3000/api/sql/query",
        json={"sql": f"SELECT * FROM {i} LIMIT 10 OFFSET 20;"}
    )
    large_json2[i] = resp.json()

print(large_json2)

refinement_prompt = (
    "You are a database schema verification tool. You have been given an inferred metadata schema "
    "for 5 supermarket database tables, along with a SECOND sample of 10 rows from each table.\n\n"
    "Your job is to validate the inferred schema against this new sample data and refine it.\n\n"
    "Check for and fix the following:\n"
    "1. FOREIGN KEYS: Verify that all foreign key references point to valid tables and columns in the schema. "
    "Fix any incorrect or missing foreign key relationships.\n"
    "2. DATA TYPES: Cross-check against the new sample. Verify data types are precise "
    "(e.g., don't use VARCHAR if it should be INTEGER, use DATE not VARCHAR for date columns). "
    "If the new sample reveals a different format, correct the type.\n"
    "3. PRIMARY KEYS: Ensure every table has exactly one primary key identified. "
    "Verify uniqueness holds in the new sample.\n"
    "4. DESCRIPTIONS: Improve any vague descriptions to be more specific to supermarket context.\n"
    "5. NULLABLE: Check the new sample for NULL values. Verify nullable makes sense "
    "(e.g., primary keys should never be nullable, foreign keys in required relationships should not be nullable).\n"
    "6. CONSISTENCY: Ensure column names referenced as foreign keys match exactly across tables.\n"
    "7. VALID VALUES: If you see enum-like columns (status, category), check the new sample for "
    "additional distinct values and update valid_values accordingly.\n"
    "8. EXAMPLE VALUES: Update example values if the new sample reveals more representative ones.\n\n"
    "Return the CORRECTED and REFINED JSON schema in the exact same structure. "
    "Return ONLY the JSON object. No markdown, no explanation, no extra text."
)

refinement_response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": refinement_prompt},
        {"role": "user", "content": json.dumps({
            "inferred_schema": inferred_schema,
            "validation_sample": large_json2
        })},
    ],
)

# --- Parse refined response ---
refined_content = refinement_response.choices[0].message.content.strip()

if refined_content.startswith("```"):
    refined_content = refined_content.split("\n", 1)[1]
    refined_content = refined_content.rsplit("```", 1)[0]

refined_schema = json.loads(refined_content)

print("\n=== Refined Schema (Pass 2 - Verified) ===")
print(json.dumps(refined_schema, indent=2))

# --- Step 3: Write refined schema to JSON file ---
output_path = os.path.join(os.path.dirname(__file__), "db_schema.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(refined_schema, f, indent=2)

print(f"\n✅ Schema written to: {output_path}")