-- =========================================================
-- Task 3.3: OLAP Analytics Queries (fleximart_dw)
-- =========================================================

USE fleximart_dw;

-- =========================================================
-- Query 1: Monthly Sales Drill-Down Analysis (5 marks)
-- Business Scenario:
-- "The CEO wants to see sales performance broken down by time periods.
--  Start with yearly total, then quarterly, then monthly sales for 2024."
--
-- Demonstrates: Drill-down (Year → Quarter → Month)
-- Requirements:
-- - Show: year, quarter, month_name, total_sales, total_quantity
-- - Group by year, quarter, month
-- - Order chronologically
-- =========================================================

SELECT
    d.year AS year,
    d.quarter AS quarter,
    d.month_name AS month_name,
    ROUND(SUM(f.total_amount), 2) AS total_sales,
    SUM(f.quantity_sold) AS total_quantity
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
WHERE d.year = 2024
GROUP BY
    d.year,
    d.quarter,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.quarter,
    d.month;


-- =========================================================
-- Query 2: Product Performance Analysis (5 marks)
-- Business Scenario:
-- "Show the top 10 products by revenue, along with their category,
--  total units sold, and revenue contribution percentage."
--
-- Requirements:
-- - Join fact_sales with dim_product
-- - Calculate total revenue and total quantity per product
-- - Calculate revenue percentage of overall revenue
-- - Order by revenue DESC, limit 10
-- Hint: Use window function or subquery
-- =========================================================

WITH product_revenue AS (
    SELECT
        p.product_name,
        p.category,
        SUM(f.quantity_sold) AS units_sold,
        SUM(f.total_amount) AS revenue
    FROM fact_sales f
    JOIN dim_product p
        ON f.product_key = p.product_key
    GROUP BY
        p.product_name,
        p.category
)
SELECT
    product_name,
    category,
    units_sold,
    ROUND(revenue, 2) AS revenue,
    ROUND((revenue / SUM(revenue) OVER ()) * 100, 2) AS revenue_percentage
FROM product_revenue
ORDER BY
    revenue DESC
LIMIT 10;


-- =========================================================
-- Query 3: Customer Segmentation Analysis (5 marks)
-- Business Scenario:
-- "Segment customers into High Value (>₹50,000 spent),
--  Medium Value (₹20,000–₹50,000), and Low Value (<₹20,000).
--  Show count of customers and total revenue in each segment."
--
-- Requirements:
-- - Calculate total spending per customer
-- - Use CASE to create segments
-- - Group by segment
-- - Show: segment, customer_count, total_revenue, avg_revenue_per_customer
-- Hint: Use CTE/nested query recommended
-- =========================================================

WITH customer_totals AS (
    SELECT
        c.customer_key,
        c.customer_name,
        SUM(f.total_amount) AS total_spent
    FROM fact_sales f
    JOIN dim_customer c
        ON f.customer_key = c.customer_key
    GROUP BY
        c.customer_key,
        c.customer_name
),
segmented AS (
    SELECT
        customer_key,
        customer_name,
        total_spent,
        CASE
            WHEN total_spent > 50000 THEN 'High Value'
            WHEN total_spent >= 20000 AND total_spent <= 50000 THEN 'Medium Value'
            ELSE 'Low Value'
        END AS customer_segment
    FROM customer_totals
)
SELECT
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(SUM(total_spent), 2) AS total_revenue,
    ROUND(AVG(total_spent), 2) AS avg_revenue_per_customer
FROM segmented
GROUP BY
    customer_segment
ORDER BY
    FIELD(customer_segment, 'High Value', 'Medium Value', 'Low Value');
