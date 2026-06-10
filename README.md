# Musketeers Mart — AI-Powered Supermarket Inventory Management System

An intelligent supermarket inventory management system that combines a traditional web dashboard with an AI chatbot agent. The chatbot assists store managers with stock replenishment decisions using machine learning predictions, real-time data insights, and automated chart generation.

Built for **SuperAI NEXT Hackathon 2026** by Alena, Caden, Raphael.

---

## Architecture

```
User (Browser @ port 8000) → Frontend (HTML/JS/CSS)
                       ↓ API calls
           ┌────────────────────────────────────┐
           │   Backend (2 FastAPI servers)       │
           │                                    │
           │  Port 3000: DB API Server          │ ← Read-only SQL query interface
           │  Port 5000: Chatbot API Server     │ ← AI agent wrapper
           └────────────────────────────────────┘
                       ↓                ↓
               SQLite DB         AI Agent (Python)
             (database.db)       ├── Safety Gate
                                 ├── Intent Router
                                 ├── Stock Order (ML + LLM)
                                 └── Data Visual (Google ADK)
                                            ↓
                                 OpenRouter API (Gemini 3.1 Flash Lite)
```

---

## Features

### Feature 1: AI Stock Order Recommendations
The agent recommends how many units to reorder for a given product:
1. Extracts the product name from natural language input
2. Queries historical sales data from the database
3. Runs a pre-trained Random Forest Regression model to predict demand
4. LLM generates additional trend insight queries
5. Final LLM synthesizes all data into a recommendation with reasoning

### Feature 2: AI Data Visualization
The agent generates charts from natural language queries using Google ADK:
1. Reads the database schema from a metadata cache
2. Generates and validates SQL queries
3. Renders matplotlib charts as base64-encoded PNG images
4. Returns the chart inline in the chatbot UI

### Feature 3: Web Dashboard & Inventory Management
- KPI cards (revenue, orders, products, low stock alerts)
- Revenue charts by product and category
- Product inventory table with search and filter
- Purchase order form with supplier-product linking

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla HTML/CSS/JS, Chart.js |
| Backend API | FastAPI, Uvicorn, SQLite3 |
| AI/ML | Google ADK, LiteLLM, OpenRouter (Gemini 3.1 Flash Lite), scikit-learn |
| Data Viz | Matplotlib, Pandas |
| Database | SQLite3 (150 products, 10 suppliers, 1500 orders, ~20K sales) |
| Python | 3.12 |

---

## Project Structure

```
├── agent/                      # AI agent system
│   ├── agent.py                # Main orchestrator (safety → intent → routing)
│   ├── stock_retrieval.py      # Stock order recommendation workflow
│   ├── tools.py                # ADK tools (query_db, render_chart, metadata_txt_exists)
│   ├── metadata_gen.py         # LLM-based schema inference utility
│   ├── data_visual.py          # Data visualization handler
│   ├── db_schema.json          # Inferred database metadata
│   └── ml_model/
│       ├── model_training.ipynb
│       └── rfr_order_model.joblib
│
├── backend/
│   ├── init_server/            # Port 3000 — DB API server
│   │   ├── api_server.py
│   │   └── SQL_Queries.py
│   ├── init_adk_server/        # Port 5000 — Chatbot API server
│   │   └── fastapi_server.py
│   └── init_db/                # Database initialization
│       ├── main.ipynb
│       ├── database.db
│       ├── orders.csv
│       ├── products.csv
│       ├── suppliers.csv
│       ├── inventory.csv
│       └── sales_transaction_lines.csv
│
├── Frontend/                   # Web interface
│   ├── index.html              # Login page
│   ├── MainPage.html           # Dashboard
│   ├── Inventory.html          # Product inventory
│   ├── OrderForm.html          # Purchase order form
│   ├── OrderHistory.html       # Order history
│   └── OrderSummary.html       # Order detail view
│
├── docs/                       # Team documentation
├── .env.example                # Environment variable template
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.12+
- An [OpenRouter](https://openrouter.ai/) API key

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd NextHackathon

# Install Python dependencies
pip install fastapi uvicorn openai python-dotenv httpx pandas numpy scikit-learn joblib matplotlib google-adk litellm aiohttp

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

### Running

Start all three servers (each in a separate terminal):

```bash
# Terminal 1 — Database API Server (port 3000)
python backend/init_server/api_server.py

# Terminal 2 — Chatbot API Server (port 5000)
python backend/init_adk_server/fastapi_server.py

# Terminal 3 — Frontend Web Server (port 8000)
cd Frontend
python -m http.server 8000
```

Then open `http://localhost:8000` in your browser. Demo credentials:
- Username: `user1`, Password: `1234`
- Username: `user2`, Password: `9907`

---

## API Response Format

All chatbot responses follow this unified structure:

```json
{
  "message": "Human-readable response text",
  "recommendation": {
    "product_name": "MeadowFresh Yogurt",
    "supplier_name": "Lion City Foods Pte Ltd",
    "qty": 75
  },
  "base64": "iVBORw0KGgoAAAA..."
}
```

| Field | Present When |
|-------|-------------|
| `message` | Always |
| `recommendation` | Stock order queries only (null otherwise) |
| `base64` | Data visualization queries only (null otherwise) |

---

## Database

SQLite3 database with 5 tables:

| Table | Records | Description |
|-------|---------|-------------|
| `suppliers` | 10 | Supplier master data |
| `products` | 150 | Product catalogue |
| `inventory` | 150 | Current stock levels |
| `orders` | 1,500 | Purchase order history |
| `sales_items` | 19,862 | Sales transaction line items |

---

## AI Agent Workflow

```
User Input
    │
    ├── Safety Check (LLM) ──→ Block if harmful
    │
    ├── Intent Classification (LLM)
    │       │
    │       ├── STOCK_ORDER → stock_retrieval.py
    │       │       ├── Product extraction (LLM)
    │       │       ├── Sales query (SQL)
    │       │       ├── ML prediction (Random Forest)
    │       │       ├── Trend insight queries (LLM + SQL)
    │       │       ├── Inventory check (SQL)
    │       │       └── Final recommendation (LLM)
    │       │
    │       ├── DATA_VISUAL → Google ADK Agent
    │       │       ├── Schema discovery
    │       │       ├── SQL generation + validation
    │       │       └── Chart rendering (matplotlib → base64)
    │       │
    │       └── GENERAL → Direct LLM response
    │
    └── Return unified JSON response
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | API key for OpenRouter (Gemini 3.1 Flash Lite) |
| `DB_API_URL` | No | Defaults to `http://127.0.0.1:3000/query` |

---

## Team

Built by the 3 Musketeers team — SuperAI NEXT Hackathon 2026.
