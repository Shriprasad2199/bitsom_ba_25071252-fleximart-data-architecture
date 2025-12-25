"""
FlexiMart ETL Pipeline (Part 1)

- Extract: reads CSVs from ../data/
- Transform: fixes duplicates, missing values, phone/date/category standardisation
- Load: inserts into MySQL using the provided schema
- Output: writes data_quality_report.txt (in this same folder)

Assumptions (documented):
1) Customers with missing email are dropped because customers.email is UNIQUE NOT NULL.
2) Each transaction_id in sales_raw.csv represents one order with one order_item.
3) Products with missing price are imputed from sales unit_price (median per product_id).
   If a product has missing price and never appears in sales, it is dropped.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
load_dotenv()


# -----------------------------
# Configuration (edit if needed)
# -----------------------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "fleximart"),
    "port": int(os.getenv("DB_PORT", 3306)),
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

CUSTOMERS_CSV = DATA_DIR / "customers_raw.csv"
PRODUCTS_CSV = DATA_DIR / "products_raw.csv"
SALES_CSV = DATA_DIR / "sales_raw.csv"

REPORT_PATH = Path(__file__).resolve().parent / "data_quality_report.txt"


# -----------------------------
# Utilities: standardisation
# -----------------------------
DATE_FORMATS = [
    "%Y-%m-%d",   # 2024-01-15
    "%d/%m/%Y",   # 15/01/2024
    "%m-%d-%Y",   # 01-22-2024 or 08-15-2023
    "%m/%d/%Y",   # 03/12/2024
    "%d-%m-%Y",   # 15-01-2024 (just in case)
]


def parse_date(value: Any) -> Optional[date]:
    """Parse multiple common date formats and return a datetime.date."""
    if value is None:
        return None
    s = str(value).strip()
    if s == "" or s.lower() in {"nan", "none", "null"}:
        return None

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass

    # Fallback: pandas parser (handles many formats), but keep it conservative
    try:
        dt = pd.to_datetime(s, errors="coerce", dayfirst=False)
        if pd.notna(dt):
            return dt.date()
    except Exception:
        pass

    try:
        dt = pd.to_datetime(s, errors="coerce", dayfirst=True)
        if pd.notna(dt):
            return dt.date()
    except Exception:
        pass

    return None


def normalise_phone(phone: Any) -> Optional[str]:
    """
    Standardise phone to +91-XXXXXXXXXX using last 10 digits.
    Returns None if phone cannot be normalised.
    """
    if phone is None:
        return None
    s = str(phone).strip()
    if s == "" or s.lower() in {"nan", "none", "null"}:
        return None

    digits = "".join(ch for ch in s if ch.isdigit())
    if len(digits) < 10:
        return None
    last10 = digits[-10:]
    return f"+91-{last10}"


def normalise_city(city: Any) -> Optional[str]:
    if city is None:
        return None
    s = str(city).strip()
    if s == "" or s.lower() in {"nan", "none", "null"}:
        return None
    return s.title()


CATEGORY_MAP = {
    "electronics": "Electronics",
    "fashion": "Fashion",
    "groceries": "Groceries",
}


def normalise_category(cat: Any) -> str:
    s = "" if cat is None else str(cat).strip()
    key = s.lower()
    return CATEGORY_MAP.get(key, s.title() if s else "Unknown")


# -----------------------------
# Reporting structure
# -----------------------------
@dataclass
class QualityCounts:
    rows_read: int = 0
    duplicates_removed: int = 0
    rows_dropped: int = 0
    missing_filled: int = 0
    loaded: int = 0
    notes: List[str] = None

    def __post_init__(self) -> None:
        if self.notes is None:
            self.notes = []


# -----------------------------
# DB schema (exact tables)
# -----------------------------
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    city VARCHAR(50),
    registration_date DATE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB;
"""


def connect_db() -> mysql.connector.connection.MySQLConnection:
    return mysql.connector.connect(**DB_CONFIG)


def ensure_schema(conn: mysql.connector.connection.MySQLConnection) -> None:
    cur = conn.cursor()
    for statement in SCHEMA_SQL.strip().split(";"):
        stmt = statement.strip()
        if stmt:
            cur.execute(stmt)
    conn.commit()
    cur.close()


def truncate_tables(conn: mysql.connector.connection.MySQLConnection) -> None:
    """
    Makes the pipeline re-runnable.
    We disable FK checks temporarily to truncate in dependency order safely.
    """
    cur = conn.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS=0;")
    cur.execute("TRUNCATE TABLE order_items;")
    cur.execute("TRUNCATE TABLE orders;")
    cur.execute("TRUNCATE TABLE products;")
    cur.execute("TRUNCATE TABLE customers;")
    cur.execute("SET FOREIGN_KEY_CHECKS=1;")
    conn.commit()
    cur.close()


# -----------------------------
# Extract
# -----------------------------
def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return pd.read_csv(path, dtype=str).copy()


# -----------------------------
# Transform: customers
# -----------------------------
def transform_customers(df: pd.DataFrame) -> Tuple[pd.DataFrame, QualityCounts, Dict[str, str]]:
    qc = QualityCounts(rows_read=len(df))

    # Trim spaces in all string cells
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # Standardise fields
    df["email"] = df["email"].replace({"": None})
    df["phone"] = df["phone"].apply(normalise_phone)
    df["city"] = df["city"].apply(normalise_city)
    df["registration_date"] = df["registration_date"].apply(parse_date)

    # Drop rows missing required email
    before = len(df)
    df = df[df["email"].notna()].copy()
    dropped_missing_email = before - len(df)
    qc.rows_dropped += dropped_missing_email
    if dropped_missing_email:
        qc.notes.append(f"Dropped {dropped_missing_email} customer rows due to missing email (NOT NULL constraint).")

    # Deduplicate by email (unique constraint)
    before = len(df)
    df = df.drop_duplicates(subset=["email"], keep="first").copy()
    qc.duplicates_removed += (before - len(df))

    # Build raw_id map (raw customer_code -> email). Keep for sales mapping.
    # We will map sales customer_id like "C001" to email first, then to db id later.
    raw_to_email = {}
    if "customer_id" in df.columns:
        for _, row in df.iterrows():
            raw_to_email[str(row["customer_id"]).strip()] = row["email"]

    # Keep only columns needed for insertion (db has auto customer_id)
    cleaned = df[["first_name", "last_name", "email", "phone", "city", "registration_date"]].copy()

    return cleaned, qc, raw_to_email


# -----------------------------
# Transform: products
# -----------------------------
def transform_products(df_products: pd.DataFrame, df_sales: pd.DataFrame) -> Tuple[pd.DataFrame, QualityCounts, Dict[str, str]]:
    qc = QualityCounts(rows_read=len(df_products))

    df_products = df_products.map(lambda x: x.strip() if isinstance(x, str) else x)
    df_products["product_name"] = df_products["product_name"].astype(str).str.strip()
    df_products["category"] = df_products["category"].apply(normalise_category)

    # Stock: missing -> 0
    before_missing_stock = df_products["stock_quantity"].isna().sum() + (df_products["stock_quantity"] == "").sum()
    df_products["stock_quantity"] = df_products["stock_quantity"].replace({"": None})
    df_products["stock_quantity"] = df_products["stock_quantity"].fillna("0")
    qc.missing_filled += int(before_missing_stock)

    # Prices: fill from sales (median per product_id), else drop
    df_products["price"] = df_products["price"].replace({"": None})

    # Build median unit_price per product_id from sales
    sales_prices = df_sales.copy()
    sales_prices = sales_prices.map(lambda x: x.strip() if isinstance(x, str) else x)
    sales_prices = sales_prices[sales_prices["product_id"].notna() & (sales_prices["product_id"] != "")]
    sales_prices["unit_price_num"] = pd.to_numeric(sales_prices["unit_price"], errors="coerce")
    median_by_pid = sales_prices.groupby("product_id")["unit_price_num"].median().to_dict()

    missing_price_mask = df_products["price"].isna()
    filled = 0
    for idx, row in df_products[missing_price_mask].iterrows():
        pid = str(row["product_id"]).strip()
        med = median_by_pid.get(pid)
        if med is not None and pd.notna(med):
            df_products.at[idx, "price"] = f"{float(med):.2f}"
            filled += 1

    qc.missing_filled += filled

    # Drop remaining missing prices (cannot insert due to NOT NULL)
    before = len(df_products)
    df_products = df_products[df_products["price"].notna()].copy()
    dropped_missing_price = before - len(df_products)
    qc.rows_dropped += dropped_missing_price
    if dropped_missing_price:
        qc.notes.append(
            f"Dropped {dropped_missing_price} product rows due to missing price not recoverable from sales."
        )

    # Deduplicate by product_id (raw id)
    before = len(df_products)
    df_products = df_products.drop_duplicates(subset=["product_id"], keep="first").copy()
    qc.duplicates_removed += (before - len(df_products))

    # Raw mapping: raw product_code -> product_name
    raw_to_name = {}
    for _, row in df_products.iterrows():
        raw_to_name[str(row["product_id"]).strip()] = row["product_name"]

    cleaned = df_products[["product_name", "category", "price", "stock_quantity"]].copy()

    # Convert numerics
    cleaned["price"] = pd.to_numeric(cleaned["price"], errors="coerce")
    cleaned["stock_quantity"] = pd.to_numeric(cleaned["stock_quantity"], errors="coerce").fillna(0).astype(int)

    return cleaned, qc, raw_to_name


# -----------------------------
# Transform: sales -> orders + order_items
# -----------------------------
def transform_sales(df_sales: pd.DataFrame) -> Tuple[pd.DataFrame, QualityCounts]:
    qc = QualityCounts(rows_read=len(df_sales))

    df_sales = df_sales.map(lambda x: x.strip() if isinstance(x, str) else x)

    # Deduplicate by transaction_id
    before = len(df_sales)
    df_sales = df_sales.drop_duplicates(subset=["transaction_id"], keep="first").copy()
    qc.duplicates_removed += (before - len(df_sales))

    # Parse date
    df_sales["order_date"] = df_sales["transaction_date"].apply(parse_date)

    # Drop rows with missing customer_id or product_id (cannot satisfy FKs)
    before = len(df_sales)
    df_sales["customer_id"] = df_sales["customer_id"].replace({"": None})
    df_sales["product_id"] = df_sales["product_id"].replace({"": None})
    df_sales = df_sales[df_sales["customer_id"].notna() & df_sales["product_id"].notna()].copy()
    dropped_missing_ids = before - len(df_sales)
    qc.rows_dropped += dropped_missing_ids
    if dropped_missing_ids:
        qc.notes.append(f"Dropped {dropped_missing_ids} sales rows due to missing customer_id/product_id.")

    # Quantity and unit_price numeric
    df_sales["quantity_num"] = pd.to_numeric(df_sales["quantity"], errors="coerce")
    df_sales["unit_price_num"] = pd.to_numeric(df_sales["unit_price"], errors="coerce")

    # Drop invalid quantity/price or missing parsed date
    before = len(df_sales)
    df_sales = df_sales[
        df_sales["order_date"].notna()
        & df_sales["quantity_num"].notna()
        & (df_sales["quantity_num"] > 0)
        & df_sales["unit_price_num"].notna()
        & (df_sales["unit_price_num"] >= 0)
    ].copy()
    dropped_invalid = before - len(df_sales)
    qc.rows_dropped += dropped_invalid
    if dropped_invalid:
        qc.notes.append(f"Dropped {dropped_invalid} sales rows due to invalid date/quantity/unit_price.")

    # Compute subtotal and total_amount (one line per transaction)
    df_sales["subtotal"] = (df_sales["quantity_num"] * df_sales["unit_price_num"]).round(2)
    df_sales["total_amount"] = df_sales["subtotal"]

    cleaned = df_sales[
        ["transaction_id", "customer_id", "product_id", "order_date", "status", "quantity_num", "unit_price_num", "subtotal", "total_amount"]
    ].copy()

    cleaned = cleaned.rename(
        columns={
            "quantity_num": "quantity",
            "unit_price_num": "unit_price",
        }
    )

    return cleaned, qc


# -----------------------------
# Load helpers
# -----------------------------
def insert_customers(conn, df: pd.DataFrame) -> int:
    sql = """
        INSERT INTO customers (first_name, last_name, email, phone, city, registration_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cur = conn.cursor()
    rows = 0
    for _, r in df.iterrows():
        cur.execute(sql, (r["first_name"], r["last_name"], r["email"], r["phone"], r["city"], r["registration_date"]))
        rows += 1
    conn.commit()
    cur.close()
    return rows


def insert_products(conn, df: pd.DataFrame) -> int:
    sql = """
        INSERT INTO products (product_name, category, price, stock_quantity)
        VALUES (%s, %s, %s, %s)
    """
    cur = conn.cursor()
    rows = 0
    for _, r in df.iterrows():
        cur.execute(sql, (r["product_name"], r["category"], float(r["price"]), int(r["stock_quantity"])))
        rows += 1
    conn.commit()
    cur.close()
    return rows


def fetch_customer_email_to_dbid(conn) -> Dict[str, int]:
    cur = conn.cursor()
    cur.execute("SELECT customer_id, email FROM customers;")
    mapping = {email: int(cid) for (cid, email) in cur.fetchall()}
    cur.close()
    return mapping


def fetch_product_name_to_dbid(conn) -> Dict[str, int]:
    cur = conn.cursor()
    cur.execute("SELECT product_id, product_name FROM products;")
    mapping = {name: int(pid) for (pid, name) in cur.fetchall()}
    cur.close()
    return mapping


def insert_orders_and_items(
    conn,
    sales: pd.DataFrame,
    raw_customer_to_email: Dict[str, str],
    email_to_db_customer_id: Dict[str, int],
    raw_product_to_name: Dict[str, str],
    name_to_db_product_id: Dict[str, int],
) -> Tuple[int, int, int]:
    """
    Returns:
      orders_inserted, order_items_inserted, sales_rows_dropped_due_to_fk
    """
    order_sql = """
        INSERT INTO orders (customer_id, order_date, total_amount, status)
        VALUES (%s, %s, %s, %s)
    """
    item_sql = """
        INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
        VALUES (%s, %s, %s, %s, %s)
    """

    cur = conn.cursor()
    orders = 0
    items = 0
    dropped_fk = 0

    for _, r in sales.iterrows():
        raw_cid = str(r["customer_id"]).strip()
        raw_pid = str(r["product_id"]).strip()

        email = raw_customer_to_email.get(raw_cid)
        prod_name = raw_product_to_name.get(raw_pid)

        if not email or email not in email_to_db_customer_id:
            dropped_fk += 1
            continue
        if not prod_name or prod_name not in name_to_db_product_id:
            dropped_fk += 1
            continue

        db_cid = email_to_db_customer_id[email]
        db_pid = name_to_db_product_id[prod_name]

        # Insert order
        cur.execute(order_sql, (db_cid, r["order_date"], float(r["total_amount"]), r["status"] or "Pending"))
        order_id = cur.lastrowid
        orders += 1

        # Insert order item
        cur.execute(item_sql, (order_id, db_pid, int(r["quantity"]), float(r["unit_price"]), float(r["subtotal"])))
        items += 1

    conn.commit()
    cur.close()
    return orders, items, dropped_fk


# -----------------------------
# Report writer
# -----------------------------
def write_report(
    customer_qc: QualityCounts,
    product_qc: QualityCounts,
    sales_qc: QualityCounts,
    extra_notes: List[str],
) -> None:
    lines = []
    lines.append("FlexiMart ETL Data Quality Report")
    lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    def section(title: str, qc: QualityCounts) -> None:
        lines.append(f"== {title} ==")
        lines.append(f"Rows read: {qc.rows_read}")
        lines.append(f"Duplicates removed: {qc.duplicates_removed}")
        lines.append(f"Missing values filled: {qc.missing_filled}")
        lines.append(f"Rows dropped: {qc.rows_dropped}")
        lines.append(f"Rows loaded: {qc.loaded}")
        if qc.notes:
            lines.append("Notes:")
            for n in qc.notes:
                lines.append(f"- {n}")
        lines.append("")

    section("customers_raw.csv", customer_qc)
    section("products_raw.csv", product_qc)
    section("sales_raw.csv", sales_qc)

    if extra_notes:
        lines.append("== Additional Notes ==")
        for n in extra_notes:
            lines.append(f"- {n}")
        lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    extra_notes: List[str] = []

    # Extract
    customers_raw = read_csv(CUSTOMERS_CSV)
    products_raw = read_csv(PRODUCTS_CSV)
    sales_raw = read_csv(SALES_CSV)

    # Transform
    sales_clean, sales_qc = transform_sales(sales_raw)
    customers_clean, customer_qc, raw_customer_to_email = transform_customers(customers_raw)
    products_clean, product_qc, raw_product_to_name = transform_products(products_raw, sales_raw)

    # Load
    try:
        conn = connect_db()
        ensure_schema(conn)

        # Re-runnable ETL
        truncate_tables(conn)

        customer_qc.loaded = insert_customers(conn, customers_clean)
        product_qc.loaded = insert_products(conn, products_clean)

        email_to_db_customer_id = fetch_customer_email_to_dbid(conn)
        name_to_db_product_id = fetch_product_name_to_dbid(conn)

        orders_loaded, items_loaded, dropped_fk = insert_orders_and_items(
            conn,
            sales_clean,
            raw_customer_to_email,
            email_to_db_customer_id,
            raw_product_to_name,
            name_to_db_product_id,
        )

        sales_qc.loaded = len(sales_clean) - dropped_fk
        if dropped_fk:
            sales_qc.rows_dropped += dropped_fk
            extra_notes.append(
                f"Dropped {dropped_fk} sales rows during load because customer/product could not be mapped "
                f"(e.g., customers dropped due to missing email)."
            )

        extra_notes.append(f"Orders inserted: {orders_loaded}")
        extra_notes.append(f"Order items inserted: {items_loaded}")

        conn.close()

    except Error as e:
        # Write a report even if DB load fails (useful for marking)
        extra_notes.append(f"MySQL Error: {str(e)}")

    # Report
    write_report(customer_qc, product_qc, sales_qc, extra_notes)


if __name__ == "__main__":
    main()
