# Database Initialisation Documentation

**File:** `database.db`  
**Engine:** SQLite3  
**Foreign Keys:** Enabled (`PRAGMA foreign_keys = ON`)  
**Generated:** 2026-06-09  

---

## Overview

This document describes the database schema created in `database.db`, including table definitions, constraints, and data loading notes for each corresponding CSV source file.

Five tables are defined and populated:

| Table | Source CSV | Rows Loaded |
|---|---|---|
| `suppliers` | `suppliers.csv` | 10 |
| `products` | `products.csv` | 150 |
| `inventory` | `inventory.csv` | 150 |
| `orders` | `orders.csv` | 1,500 |
| `sales_items` | `sales_transaction_lines.csv` | 19,862 |

---

## Table Schemas

### `suppliers`

Stores supplier master data.

| Column | Type | Not Null | Default | Constraints |
|---|---|---|---|---|
| `supplier_id` | INTEGER | — | — | PRIMARY KEY AUTOINCREMENT |
| `supplier_code` | TEXT | ✅ | — | UNIQUE |
| `supplier_name` | TEXT | ✅ | — | — |
| `contact_name` | TEXT | — | — | — |
| `contact_email` | TEXT | — | — | — |
| `contact_phone` | TEXT | — | — | — |
| `address` | TEXT | — | — | — |
| `is_active` | INTEGER | ✅ | `1` | CHECK (is_active IN (0, 1)) |
| `created_at` | TEXT | ✅ | `strftime('%Y-%m-%dT%H:%M:%SZ', 'now')` | — |

**Foreign Keys:** None  
**CSV Columns Ignored:** None  
**Data Transformations Applied:**
- `is_active`: `True`/`False` string → `1`/`0` integer
- `contact_email`: Markdown link syntax `[email](mailto:email)` stripped to raw email address
- `created_at`: Normalised to ISO 8601 format `YYYY-MM-DDTHH:MM:SSZ`

---

### `products`

Stores product catalogue with supplier linkage.

| Column | Type | Not Null | Default | Constraints |
|---|---|---|---|---|
| `product_id` | INTEGER | — | — | PRIMARY KEY AUTOINCREMENT |
| `product_sku` | TEXT | ✅ | — | UNIQUE |
| `product_name` | TEXT | ✅ | — | — |
| `brand` | TEXT | — | — | — |
| `category` | TEXT | — | — | — |
| `supplier_id` | INTEGER | ✅ | — | FOREIGN KEY → `suppliers(supplier_id)` |
| `unit_of_measure` | TEXT | — | — | — |
| `pack_size` | TEXT | — | — | — |
| `base_cost` | REAL | ✅ | `0.00` | — |
| `base_retail_price` | REAL | ✅ | `0.00` | — |
| `tax_rate_pct` | REAL | ✅ | `0.00` | — |
| `is_discontinued` | INTEGER | ✅ | `0` | CHECK (is_discontinued IN (0, 1)) |
| `created_at` | TEXT | ✅ | `strftime('%Y-%m-%dT%H:%M:%SZ', 'now')` | — |

**Foreign Keys:** `supplier_id` → `suppliers(supplier_id)`  
**CSV Columns Ignored:** None  
**Data Transformations Applied:**
- `is_discontinued`: `True`/`False` string → `1`/`0` integer
- `created_at`: Normalised to ISO 8601 format `YYYY-MM-DDTHH:MM:SSZ`

---

### `inventory`

Stores stock levels and reorder thresholds per product. Each product has at most one inventory record (UNIQUE constraint on `product_id`).

| Column | Type | Not Null | Default | Constraints |
|---|---|---|---|---|
| `inventory_id` | INTEGER | — | — | PRIMARY KEY AUTOINCREMENT |
| `product_id` | INTEGER | ✅ | — | UNIQUE, FOREIGN KEY → `products(product_id)` |
| `quantity_on_hand` | REAL | ✅ | `0.000` | — |
| `reorder_point` | REAL | — | `0.000` | — |
| `reorder_qty` | REAL | — | `0.000` | — |
| `last_updated_at` | TEXT | ✅ | `strftime('%Y-%m-%dT%H:%M:%SZ', 'now')` | — |

**Foreign Keys:** `product_id` → `products(product_id)`  
**CSV Columns Ignored:**
- Trailing blank/unnamed columns (columns with no header) present in the source CSV were dropped before insert

**Data Transformations Applied:**
- `last_updated_at`: Normalised to ISO 8601 format `YYYY-MM-DDTHH:MM:SSZ`

---

### `orders`

Stores purchase orders placed with suppliers.

| Column | Type | Not Null | Default | Constraints |
|---|---|---|---|---|
| `order_id` | INTEGER | — | — | PRIMARY KEY AUTOINCREMENT |
| `order_number` | TEXT | ✅ | — | — |
| `order_date` | TEXT | ✅ | — | — |
| `supplier_id` | INTEGER | ✅ | — | FOREIGN KEY → `suppliers(supplier_id)` |
| `product_id` | INTEGER | ✅ | — | FOREIGN KEY → `products(product_id)` |
| `ordered_qty` | REAL | ✅ | `0.000` | — |
| `received_qty` | REAL | — | `0.000` | — |
| `unit_cost` | REAL | ✅ | `0.00` | — |
| `line_base_cost` | REAL | — | `0.00` | — |
| `discount_pct` | REAL | — | `0.00` | — |
| `tax_rate_pct` | REAL | — | `0.00` | — |
| `status` | TEXT | ✅ | `'CREATED'` | CHECK (status IN ('CREATED', 'RECEIVED', 'CANCELLED')) |
| `created_at` | TEXT | ✅ | `strftime('%Y-%m-%dT%H:%M:%SZ', 'now')` | — |

**Foreign Keys:** `supplier_id` → `suppliers(supplier_id)`, `product_id` → `products(product_id)`  
**CSV Columns Ignored:**
- `expected_delivery_date` — not present in schema; dropped on load
- `actual_delivery_date` — not present in schema; dropped on load

**Data Transformations Applied:**
- `status`: Values not permitted by the CHECK constraint were remapped as follows:

  | CSV Value | Mapped To | Rationale |
  |---|---|---|
  | `SENT` | `CREATED` | Order dispatched but not yet confirmed received |
  | `PENDING` | `CREATED` | Order initiated but not yet actioned |
  | `DELIVERED` | `RECEIVED` | Order fulfilled |
  | `CLOSED` | `RECEIVED` | Order completed |

- `order_date`, `created_at`: Normalised to ISO 8601 format `YYYY-MM-DDTHH:MM:SSZ`

---

### `sales_items`

Stores individual line items for each sales transaction.

> **Note:** A `sales` (transaction header) table was considered but removed by team agreement as it is not part of the current data model. As a result, `sale_id` is retained as a plain grouping reference column with no foreign key enforcement.

| Column | Type | Not Null | Default | Constraints |
|---|---|---|---|---|
| `sale_item_id` | INTEGER | — | — | PRIMARY KEY AUTOINCREMENT |
| `sale_id` | INTEGER | ✅ | — | Plain column — no FK (parent `sales` table not in schema) |
| `product_id` | INTEGER | ✅ | — | FOREIGN KEY → `products(product_id)` |
| `line_number` | INTEGER | ✅ | `1` | — |
| `base_unit_price` | REAL | ✅ | `0.00` | — |
| `sale_unit_price` | REAL | ✅ | `0.00` | — |
| `quantity` | REAL | ✅ | `0.000` | — |
| `line_base_amount` | REAL | ✅ | `0.00` | — |
| `line_sale_amount` | REAL | ✅ | `0.00` | — |
| `line_discount_amount` | REAL | ✅ | `0.00` | — |
| `tax_rate_pct` | REAL | ✅ | `0.00` | — |
| `tax_amount` | REAL | ✅ | `0.00` | — |
| `promotion_code` | TEXT | — | — | — |
| `created_at` | TEXT | ✅ | `strftime('%Y-%m-%dT%H:%M:%SZ', 'now')` | — |

**Foreign Keys:** `product_id` → `products(product_id)`  
**CSV Columns Ignored:** None  
**Data Transformations Applied:**
- `created_at`: Normalised to ISO 8601 format `YYYY-MM-DDTHH:MM:SSZ`

---

## General Data Transformation Notes

The following transformations were applied globally across all CSV files during loading:

| Issue | Transformation |
|---|---|
| Boolean strings (`True`/`False`) in integer columns | Converted to `1`/`0` |
| Inconsistent date formats (`DD/MM/YYYY`, `MM/DD/YYYY HH:MM`, `YYYY-MM-DD HH:MM:SS`) | Normalised to `YYYY-MM-DDTHH:MM:SSZ` (ISO 8601) |
| Markdown email syntax `[email](mailto:email)` | Stripped to raw email string |
| Trailing unnamed/blank columns in CSV | Dropped before insert |
| `status` values outside schema CHECK constraint | Remapped to nearest valid value (see `orders` section) |

---

## Entity Relationship Summary

```
suppliers
    └── products         (supplier_id → suppliers.supplier_id)
            └── inventory    (product_id → products.product_id)
            └── orders       (product_id → products.product_id)
            └── sales_items  (product_id → products.product_id)

orders
    └── suppliers        (supplier_id → suppliers.supplier_id)
```
