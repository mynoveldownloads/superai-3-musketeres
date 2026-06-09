# API Server Initialisation & Usage Documentation

**File:** `api_server.py`  
**Framework:** FastAPI  
**Default Port:** `3000`  
**Database:** `../init_db/database.db` (resolved relative to `api_server.py`)  
**Access:** Read-only — only `SELECT` statements are permitted.

---

## Table of Contents

1. [Windows Setup (Teammates — Local)](#1-windows-setup-teammates--local)
2. [API Reference](#2-api-reference)
   - [Health Check](#get-)
   - [Execute Query](#post-query)
   - [Whitelisting Rules](#whitelisting-rules)
   - [Blocked Commands](#blocked-commands)
   - [Response Formats](#response-formats)
   - [Error Codes](#error-codes)
3. [Calling the API — Python Examples](#3-calling-the-api--python-examples)
4. [Ubuntu Developer Setup (SSH + Tailscale) -> Infra only](#4-ubuntu-developer-setup-ssh--tailscale)

---

## 1. Windows Setup (Teammates — Local)

Follow these steps to run the API server locally on your Windows machine.

### Prerequisites

- Python 3.10 or later installed — download from [python.org](https://www.python.org/downloads/)
- `pip` available in your terminal (bundled with Python)

### Step 1 — Install dependencies

Open **Command Prompt** or **PowerShell** and run:

```powershell
pip install fastapi uvicorn requests pandas
```

### Step 2 — Navigate to the server directory

```powershell
cd path\to\backend\init_server
```

### Step 3 — Start the API server

```powershell
python api_server.py
```

Expected output:

```
✅ Database resolved at: ...\backend\init_db\database.db
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:3000 (Press CTRL+C to quit)
```

The server is now accessible at `http://127.0.0.1:3000`.

### Step 4 — Stop the server

Press `CTRL+C` in the terminal window.

> **Note:** The server must be running before you call any API endpoints.
> The `database.db` file must exist at `../init_db/database.db` relative to `api_server.py`.
> If it is missing, the server will refuse to start with a `FileNotFoundError`.

---

## 2. API Reference

### Base URL

```
http://127.0.0.1:3000
```

---

### GET `/`

Health check endpoint. Confirms the server is running and shows the resolved database path.

**Request**

No body required.

```http
GET http://127.0.0.1:3000/
```

**Response (200 OK)**

```json
{
  "status": "ok",
  "message": "database.db Query API is running. POST /query to execute a SELECT statement.",
  "database": "/absolute/path/to/backend/init_db/database.db"
}
```

---

### POST `/query`

Execute a read-only SQL `SELECT` statement against `database.db`.

**Request Headers**

```
Content-Type: application/json
```

**Request Body**

| Field | Type   | Required | Description                              |
|-------|--------|----------|------------------------------------------|
| `sql` | string | ✅ Yes   | A valid SQL `SELECT` statement to execute |

**Example payload:**

```json
{
  "sql": "SELECT * FROM suppliers LIMIT 5"
}
```

**Response (200 OK — success)**

```json
{
  "status": "ok",
  "rows_returned": 5,
  "columns": ["supplier_id", "supplier_code", "supplier_name", "contact_name", "contact_email", "contact_phone", "address", "is_active", "created_at"],
  "data": [
    {
      "supplier_id": 1,
      "supplier_code": "LIONCI-001",
      "supplier_name": "Lion City Foods Pte Ltd",
      "contact_name": "Lion Contact",
      "contact_email": "info@lioncityfoods.example.com",
      "contact_phone": "+65 60010001",
      "address": "11 Market Street, Singapore",
      "is_active": 1,
      "created_at": "2024-04-12T00:00:00Z"
    }
  ]
}
```

---

### Whitelisting Rules

The API enforces the following rules **in order** before any query is executed:

| # | Rule | Behaviour on Violation |
|---|------|------------------------|
| 1 | `sql` field must be a non-empty string | HTTP 422 — validation error |
| 2 | Query must begin with `SELECT` | HTTP 403 — rejected |
| 3 | Query must not contain any blocked keyword (see below) | HTTP 403 — rejected |
| 4 | Semicolons (`;`) are stripped to prevent statement stacking | Silently sanitised before execution |
| 5 | Database is opened in **read-only mode** at the sqlite3 level | Write operations fail even if they bypass checks 1–4 |

---

### Blocked Commands

The following SQL keywords are **always rejected**, matched as whole words (case-insensitive):

| Keyword | Reason Blocked |
|---------|----------------|
| `DROP` | Destroys tables or the database |
| `DELETE` | Removes rows from a table |
| `INSERT` | Adds new rows to a table |
| `UPDATE` | Modifies existing row values |
| `REPLACE` | Inserts or replaces rows |
| `ALTER` | Modifies table structure |
| `TRUNCATE` | Removes all rows from a table |
| `CREATE` | Creates new tables or indexes |
| `ATTACH` | Attaches an external database file |
| `DETACH` | Detaches an attached database |
| `PRAGMA` | Can modify SQLite configuration |
| `VACUUM` | Rewrites the database file |
| `REINDEX` | Rebuilds indexes |
| `ANALYZE` | Writes query statistics |

**Example rejected query:**

```json
{ "sql": "DROP TABLE suppliers" }
```

**Response (403 Forbidden):**

```json
{
  "status": "rejected",
  "message": "Query contains a blocked keyword: 'DROP'. Destructive or write operations are not permitted."
}
```

---

### Response Formats

#### Success

```json
{
  "status": "ok",
  "rows_returned": <integer>,
  "columns": ["col1", "col2", "..."],
  "data": [
    { "col1": <value>, "col2": <value>, "...": "..." },
    "..."
  ]
}
```

#### Rejected (blocked query)

```json
{
  "status": "rejected",
  "message": "<reason for rejection>"
}
```

#### Error (malformed SQL or server issue)

```json
{
  "status": "error",
  "message": "<error detail>"
}
```

---

### Error Codes

| HTTP Status | `status` value | Cause |
|-------------|----------------|-------|
| `200 OK` | `ok` | Query executed successfully |
| `400 Bad Request` | `error` | SQL syntax error or references a non-existent table/column |
| `403 Forbidden` | `rejected` | Query blocked by whitelist (non-SELECT or blocked keyword) |
| `422 Unprocessable Entity` | `error` | Missing or empty `sql` field in request body |
| `500 Internal Server Error` | `error` | Unexpected server-side failure |

---

## 3. Calling the API — Python Examples

Install the required library if not already installed:

```bash
pip install requests pandas
```

### Health check

```python
import requests

resp = requests.get("http://127.0.0.1:3000/")
print(resp.json())
```

### Execute a SELECT query

```python
import requests
import pandas as pd

resp = requests.post(
    "http://127.0.0.1:3000/query",
    json={"sql": "SELECT * FROM products LIMIT 10"}
)
body = resp.json()

if body["status"] == "ok":
    df = pd.DataFrame(body["data"], columns=body["columns"])
    print(f"Rows returned: {body['rows_returned']}")
    print(df)
else:
    print(f"[{body['status'].upper()}] {body['message']}")
```

### Reusable query helper

```python
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:3000"

def query(sql: str) -> pd.DataFrame | dict:
    resp = requests.post(f"{BASE_URL}/query", json={"sql": sql})
    body = resp.json()
    if body["status"] == "ok":
        return pd.DataFrame(body["data"], columns=body["columns"])
    else:
        print(f"[{body['status'].upper()}] {body['message']}")
        return body

# Usage
df = query("SELECT category, COUNT(*) AS count FROM products GROUP BY category")
print(df)
```

### Available tables

| Table | Description |
|-------|-------------|
| `suppliers` | Supplier master data |
| `products` | Product catalogue |
| `inventory` | Stock levels and reorder thresholds |
| `orders` | Purchase orders placed with suppliers |
| `sales_items` | Individual sales transaction line items |

### Example queries

```python
# All suppliers
query("SELECT * FROM suppliers")

# Products below reorder point
query("""
    SELECT i.product_id, p.product_name, i.quantity_on_hand, i.reorder_point
    FROM inventory i
    JOIN products p ON i.product_id = p.product_id
    WHERE i.quantity_on_hand < i.reorder_point
    ORDER BY i.quantity_on_hand ASC
""")

# Revenue per supplier
query("""
    SELECT s.supplier_name,
           COUNT(DISTINCT p.product_id) AS products,
           ROUND(SUM(si.line_sale_amount), 2) AS total_revenue
    FROM suppliers s
    JOIN products p     ON s.supplier_id = p.supplier_id
    JOIN sales_items si ON p.product_id  = si.product_id
    GROUP BY s.supplier_id
    ORDER BY total_revenue DESC
""")
```

---

## 4. Ubuntu Developer Setup (SSH + Tailscale) -> Infra only

This section is for the developer maintaining the server on the Ubuntu machine accessed via Tailscale.

### Environment

| Item | Value |
|------|-------|
| OS | Ubuntu (remote, accessed via SSH) |
| Package manager | `uv` |
| Project root | `~/local_jupyter/superai-2026/` |
| Server location | `backend/init_server/api_server.py` |
| Database location | `backend/init_db/database.db` |
| Tailscale IP | `100.101.98.26` |

### Step 1 — Sync project dependencies

```bash
cd ~/local_jupyter/superai-2026
uv sync
```

To add new dependencies:

```bash
uv add fastapi uvicorn requests pandas
```

### Step 2 — Start the API server

```bash
cd ~/local_jupyter/superai-2026/backend/init_server
uv run api_server.py
```

Expected output:

```
✅ Database resolved at: /root/local_jupyter/superai-2026/backend/init_db/database.db
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:3000 (Press CTRL+C to quit)
```

### Step 3 — Access the API remotely via Tailscale

The server binds to `127.0.0.1:3000` by default (localhost only).
To access it from your Windows machine over Tailscale, use SSH local port forwarding.

**Option A — SSH config (persistent, recommended):**

Add to `~/.ssh/config` on your **Windows machine**:

```
Host dev
    HostName 100.101.98.26
    User root
    LocalForward 3000 127.0.0.1:3000
```

Then connect normally:

```powershell
ssh dev
```

Port `3000` on your Windows machine will be tunnelled to port `3000` on the Ubuntu server.
Use `http://127.0.0.1:3000` in your notebook on Windows.

**Option B — Bind to all interfaces (simpler, Tailscale network only):**

Change the last line of `api_server.py`:

```python
# From:
uvicorn.run("api_server:app", host="127.0.0.1", port=3000, reload=False)

# To:
uvicorn.run("api_server:app", host="0.0.0.0", port=3000, reload=False)
```

Then access the API directly via the Tailscale IP from any device on your tailnet:

```python
BASE_URL = "http://100.101.98.26:3000"
```

> This is safe because Tailscale is a private VPN mesh — `100.101.98.26` is not reachable from the public internet.

### Step 4 — Verify the database path

If the server fails to start with a `FileNotFoundError`, confirm the database exists:

```bash
find ~/local_jupyter/superai-2026 -name "database.db"
```

Expected output:

```
/root/local_jupyter/superai-2026/backend/init_db/database.db
```

If a stray `database.db` exists in `init_server/`, remove it:

```bash
rm ~/local_jupyter/superai-2026/backend/init_server/database.db
```

### Step 5 — Confirm which Python environment is in use

```bash
uv run python -c "import sys; print(sys.executable)"
```

Should point to:

```
/root/local_jupyter/superai-2026/.venv/bin/python
```
