Section 1: Schema Overview

FACT TABLE: fact_sales
Grain: One row per product per order line item
Business Process: Sales transactions

Measures (Numeric Facts):
- quantity_sold: Number of units sold
- unit_price: Price per unit at time of sale
- discount_amount: Discount applied
- total_amount: Final amount (quantity × unit_price - discount)

Foreign Keys:
- date_key → dim_date
- product_key → dim_product
- customer_key → dim_customer

DIMENSION TABLE: dim_date
Purpose: Date dimension for time-based analysis
Type: Conformed dimension
Attributes:
- date_key (PK): Surrogate key (integer, format: YYYYMMDD)
- full_date: Actual date
- day_of_week: Monday, Tuesday, etc.
- month: 1-12
- month_name: January, February, etc.
- quarter: Q1, Q2, Q3, Q4
- year: 2023, 2024, etc.
- is_weekend: Boolean

DIMENSION TABLE: dim_product
Purpose: Product master dimension for slicing sales by product and category.
Attributes:
- product_key (PK): Surrogate key (auto-increment integer)
- product_id: Natural/business key from source (e.g., P001)
- product_name: Product name
- category: Standardized category (e.g., Electronics, Fashion, Groceries)
- current_price: Current listed price (optional for reference; transactional price belongs in fact)
- current_stock_quantity: Current stock (optional; operational snapshot)

DIMENSION TABLE: dim_customer
Purpose: Customer dimension for analyzing sales by customer demographics and location.
Attributes:
- customer_key (PK): Surrogate key (auto-increment integer)
- customer_id: Natural/business key from source (e.g., C001)
- customer_name: Full name (first_name + last_name)
- email: Email address (unique identifier at business level)
- phone: Standardized phone number (if available)
- city: Customer city
- registration_date: Date the customer registered (optional for cohort analysis)

Section 2: Design Decisions

This warehouse uses a line-item level grain in fact_sales because it preserves the most detailed representation of sales activity. With line items, analysts can drill down from monthly revenue into specific categories, products, and customers without losing detail. This granularity supports multiple analytical questions such as product performance, customer purchasing patterns, and category contribution to revenue, while still allowing roll-ups to daily, monthly, or quarterly totals through dim_date.

Surrogate keys are used in dimensions to ensure stable joins and improve performance. Natural keys such as customer_id or product_id may change format, contain duplicates, or differ across systems. Surrogate keys also simplify handling slowly changing dimensions, where attributes like city or product category might change over time. Finally, the star schema structure (fact table with descriptive dimensions) is optimized for OLAP-style queries, enabling efficient aggregations and supporting drill-down and roll-up operations across time, product, and customer dimensions.

Section 3: Sample Data Flow

Source Transaction 

Order#101
Customer: John Doe (City: Mumbai)
Product: Laptop (Category: Electronics)
Qty: 2
Unit Price: 50000
Discount: 0
Order Date: 2024-01-15

Transformed into Data Warehouse

dim_date
- date_key: 20240115
- full_date: 2024-01-15
- month: 1
- month_name: January
- quarter: Q1
- year: 2024
- day_of_week: Monday
- is_weekend: 0

dim_product
- product_key: 5
- product_name: Laptop
- category: Electronics
- dim_customer
- customer_key: 12
- customer_name: John Doe
- city: Mumbai

fact_sales
- date_key: 20240115
- product_key: 5
- customer_key: 12
- quantity_sold: 2
- unit_price: 50000
- discount_amount: 0
- total_amount: 100000