"""
SQL_Queries.py — Centralised SQL query strings for database.db
---------------------------------------------------------------
All queries used by the API endpoints live here.
Import this module in api_server.py and reference these constants
so SQL never needs to be written in the frontend or scattered
across multiple files.

Each constant is a plain SQL SELECT string.
They are executed read-only via sqlite3 in api_server.py.
"""

# ── Inventory page ─────────────────────────────────────────────────────────────

# All active (non-discontinued) products joined with their current stock level.
# Used by: GET /inventory
INVENTORY_LIST = """
    SELECT
        p.product_id,
        p.product_sku,
        p.product_name,
        p.brand,
        p.category,
        p.unit_of_measure,
        p.base_retail_price,
        COALESCE(i.quantity_on_hand, 0)  AS quantity_on_hand,
        COALESCE(i.reorder_point,    0)  AS reorder_point,
        COALESCE(i.reorder_qty,      0)  AS reorder_qty
    FROM products p
    LEFT JOIN inventory i ON p.product_id = i.product_id
    WHERE p.is_discontinued = 0
    ORDER BY p.product_name
"""

# Products belonging to a specific supplier — used to populate the Item dropdown
# in OrderForm when a supplier is selected. Filtered server-side by supplier_id.
# Used by: GET /products-by-supplier?supplier_id=<id>
PRODUCTS_BY_SUPPLIER = """
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.brand,
        p.unit_of_measure,
        p.pack_size,
        p.base_cost
    FROM products p
    WHERE p.supplier_id = {supplier_id}
      AND p.is_discontinued = 0
    ORDER BY p.category, p.product_name
"""

# ── Suppliers ──────────────────────────────────────────────────────────────────

# All active suppliers — used to populate the supplier dropdown in OrderForm.
# Used by: GET /suppliers
SUPPLIERS_ACTIVE = """
    SELECT
        supplier_id,
        supplier_code,
        supplier_name,
        contact_name,
        contact_email,
        contact_phone
    FROM suppliers
    WHERE is_active = 1
    ORDER BY supplier_name
"""

# ── Order History page ─────────────────────────────────────────────────────────

# Summary of all purchase orders grouped by order number.
# Shows one row per order_number with aggregated cost and item count.
# Used by: GET /orders
ORDERS_SUMMARY = """
    SELECT
        o.order_number,
        o.order_date,
        s.supplier_name,
        COUNT(o.order_id)                        AS item_count,
        ROUND(SUM(o.line_base_cost), 2)          AS total_cost,
        o.status
    FROM orders o
    JOIN suppliers s ON o.supplier_id = s.supplier_id
    GROUP BY o.order_number, o.order_date, s.supplier_name, o.status
    ORDER BY o.order_date DESC
    LIMIT 200
"""

# ── Dashboard / MainPage ───────────────────────────────────────────────────────

# KPI: total number of active (non-discontinued) products.
# Used by: GET /dashboard
DASHBOARD_TOTAL_PRODUCTS = """
    SELECT COUNT(*) AS total_products
    FROM products
    WHERE is_discontinued = 0
"""

# KPI: number of products whose stock is at or below reorder point.
# Used by: GET /dashboard
DASHBOARD_LOW_STOCK_COUNT = """
    SELECT COUNT(*) AS low_stock_count
    FROM inventory i
    JOIN products p ON i.product_id = p.product_id
    WHERE p.is_discontinued = 0
      AND i.quantity_on_hand <= i.reorder_point
"""

# KPI: total number of purchase orders in the system.
# Used by: GET /dashboard
DASHBOARD_TOTAL_ORDERS = """
    SELECT COUNT(DISTINCT order_number) AS total_orders
    FROM orders
"""

# KPI: total revenue from all sales transactions.
# Used by: GET /dashboard
DASHBOARD_TOTAL_REVENUE = """
    SELECT ROUND(SUM(line_sale_amount), 2) AS total_revenue
    FROM sales_items
"""

# Recent orders for the dashboard activity feed (latest 5).
# Used by: GET /dashboard
DASHBOARD_RECENT_ORDERS = """
    SELECT
        o.order_number,
        o.order_date,
        s.supplier_name,
        ROUND(SUM(o.line_base_cost), 2) AS total_cost,
        o.status
    FROM orders o
    JOIN suppliers s ON o.supplier_id = s.supplier_id
    GROUP BY o.order_number, o.order_date, s.supplier_name, o.status
    ORDER BY o.order_date DESC
    LIMIT 5
"""

# Top 10 best-selling products by total sale revenue.
# Replaces the monthly line chart — no date filter, always has data.
# Used by: GET /dashboard  (main chart)
DASHBOARD_TOP_PRODUCTS = """
    SELECT
        p.product_name,
        p.category,
        ROUND(SUM(si.line_sale_amount), 2)  AS revenue,
        ROUND(SUM(si.quantity), 0)          AS units_sold
    FROM sales_items si
    JOIN products p ON si.product_id = p.product_id
    GROUP BY p.product_id, p.product_name, p.category
    ORDER BY revenue DESC
    LIMIT 10
"""

# Top 15 products closest to or below their reorder point (lowest stock ratio).
# Used by: GET /dashboard  (low-stock table)
DASHBOARD_LOW_STOCK_ITEMS = """
    SELECT
        p.product_name,
        p.category,
        ROUND(i.quantity_on_hand, 0)  AS quantity_on_hand,
        ROUND(i.reorder_point, 0)     AS reorder_point
    FROM inventory i
    JOIN products p ON i.product_id = p.product_id
    WHERE p.is_discontinued = 0
    ORDER BY (i.quantity_on_hand - i.reorder_point) ASC
    LIMIT 15
"""

# Sales revenue and units sold broken down by product category.
# Used by: GET /dashboard  (bar chart)
DASHBOARD_SALES_BY_CATEGORY = """
    SELECT
        p.category,
        ROUND(SUM(si.line_sale_amount), 2)  AS revenue,
        ROUND(SUM(si.quantity), 0)          AS units_sold
    FROM sales_items si
    JOIN products p ON si.product_id = p.product_id
    WHERE p.category IS NOT NULL
    GROUP BY p.category
    ORDER BY revenue DESC
    LIMIT 10
"""
