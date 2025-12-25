# FlexiMart Database Schema Documentation (Part 1.2)

## 1) Entity-Relationship Description (Text Format)

### ENTITY: customers  
**Purpose:** Stores customer master data for FlexiMart.  
**Attributes:**  
- **customer_id (PK):** Surrogate key, auto-increment unique identifier for each customer.  
- **first_name:** Customer’s first name.  
- **last_name:** Customer’s last name.  
- **email (UNIQUE, NOT NULL):** Customer’s email address; used as a unique business identifier.  
- **phone:** Standardised contact number (e.g., +91-9876543210).  
- **city:** Customer’s city of residence.  
- **registration_date:** Date the customer registered on the platform.

**Relationships:**  
- One **customer** can place **many orders** (1:M relationship with `orders`).  
- Each **order** belongs to exactly one **customer** (M:1 from `orders` to `customers`).

---

### ENTITY: products  
**Purpose:** Stores product master data used for sales and inventory tracking.  
**Attributes:**  
- **product_id (PK):** Surrogate key, auto-increment unique identifier for each product.  
- **product_name:** Descriptive product name.  
- **category:** Standardised category name (e.g., Electronics, Fashion, Groceries).  
- **price (NOT NULL):** Current product list price (decimal).  
- **stock_quantity (DEFAULT 0):** Current inventory quantity on hand.

**Relationships:**  
- One **product** can appear in **many order_items** (1:M relationship with `order_items`).  
- Each **order_item** references exactly one **product** (M:1 from `order_items` to `products`).

---

### ENTITY: orders  
**Purpose:** Stores order header information (who ordered, when, and the overall total).  
**Attributes:**  
- **order_id (PK):** Surrogate key, auto-increment unique identifier for each order.  
- **customer_id (FK):** References `customers.customer_id`.  
- **order_date (NOT NULL):** Date the order was placed.  
- **total_amount (NOT NULL):** Total amount for the whole order (sum of item subtotals).  
- **status (DEFAULT 'Pending'):** Order status (e.g., Completed, Pending, Cancelled).

**Relationships:**  
- One **order** can contain **many order_items** (1:M relationship with `order_items`).  
- Each **order_item** belongs to exactly one **order** (M:1 from `order_items` to `orders`).  
- Each **order** belongs to exactly one **customer** (M:1 from `orders` to `customers`).

---

### ENTITY: order_items  
**Purpose:** Stores line-item details for each order (what product, quantity, and pricing).  
**Attributes:**  
- **order_item_id (PK):** Surrogate key, auto-increment unique identifier for each line item.  
- **order_id (FK):** References `orders.order_id`.  
- **product_id (FK):** References `products.product_id`.  
- **quantity (NOT NULL):** Number of units purchased for the product.  
- **unit_price (NOT NULL):** Unit price at time of purchase.  
- **subtotal (NOT NULL):** `quantity * unit_price` for the line item.

**Relationships:**  
- Each **order_item** links one **order** to one **product**, implementing a many-to-many relationship between `orders` and `products` through this junction table.

---

## 2) Normalization Explanation (3NF Justification)

This schema is designed to satisfy Third Normal Form (3NF) by separating customer, product, and transactional data into distinct relations and ensuring attributes depend on keys, the whole key, and nothing but the key. Key functional dependencies include: `customer_id → {first_name, last_name, email, phone, city, registration_date}` in `customers`, `product_id → {product_name, category, price, stock_quantity}` in `products`, `order_id → {customer_id, order_date, total_amount, status}` in `orders`, and `order_item_id → {order_id, product_id, quantity, unit_price, subtotal}` in `order_items`. Non-key attributes in each table depend only on the primary key, and there are no transitive dependencies (for example, customer contact fields are not stored in `orders`, and product descriptive fields are not stored in `order_items`). This prevents update anomalies (changing a customer email requires updating only one row in `customers`, not many rows across orders), insert anomalies (a new product can be inserted into `products` without requiring an order), and delete anomalies (deleting an order does not delete the product master data). The design also preserves referential integrity through foreign keys, so each order references a valid customer, and each line item references a valid order and product.

---

## 3) Sample Data Representation (Illustrative)

> Note: The following examples demonstrate the intended structure. Actual IDs may differ due to auto-increment behavior.

### customers (sample)
| customer_id | first_name | last_name | email                    | phone           | city      | registration_date |
|------------:|------------|-----------|--------------------------|-----------------|-----------|-------------------|
| 1           | Rahul      | Sharma    | rahul.sharma@gmail.com   | +91-9876543210  | Bangalore | 2023-01-15        |
| 2           | Priya      | Patel     | priya.patel@yahoo.com    | +91-9988776655  | Mumbai    | 2023-02-20        |
| 3           | Sneha      | Reddy     | sneha.reddy@gmail.com    | +91-9123456789  | Hyderabad | 2023-04-15        |

### products (sample)
| product_id | product_name         | category     | price    | stock_quantity |
|-----------:|----------------------|--------------|---------:|---------------:|
| 1          | Samsung Galaxy S21   | Electronics  | 45999.00 | 150            |
| 2          | Nike Running Shoes   | Fashion      | 3499.00  | 80             |
| 3          | Organic Almonds      | Groceries    | 899.00   | 0              |

### orders (sample)
| order_id | customer_id | order_date  | total_amount | status     |
|---------:|------------:|-------------|-------------:|------------|
| 1        | 1           | 2024-01-15  | 45999.00     | Completed  |
| 2        | 2           | 2024-01-16  | 5998.00      | Completed  |
| 3        | 5           | 2024-01-20  | 1950.00      | Completed  |

### order_items (sample)
| order_item_id | order_id | product_id | quantity | unit_price | subtotal  |
|--------------:|---------:|-----------:|---------:|-----------:|----------:|
| 1             | 1        | 1          | 1        | 45999.00   | 45999.00  |
| 2             | 2        | 4          | 2        | 2999.00    | 5998.00   |
| 3             | 3        | 9          | 3        | 650.00     | 1950.00   |
