-- ------------------------------------------------------------
-- FlexiMart Data Warehouse Sample Data (Task 3.2)
-- ------------------------------------------------------------

USE fleximart_dw;

-- -------------------------
-- dim_date (30 rows)
-- Jan 15, 2024 to Feb 13, 2024 (includes weekends)
-- -------------------------
INSERT INTO dim_date
(date_key, full_date, day_of_week, day_of_month, month, month_name, quarter, year, is_weekend)
VALUES
(20240115,'2024-01-15','Monday',15,1,'January','Q1',2024,0),
(20240116,'2024-01-16','Tuesday',16,1,'January','Q1',2024,0),
(20240117,'2024-01-17','Wednesday',17,1,'January','Q1',2024,0),
(20240118,'2024-01-18','Thursday',18,1,'January','Q1',2024,0),
(20240119,'2024-01-19','Friday',19,1,'January','Q1',2024,0),
(20240120,'2024-01-20','Saturday',20,1,'January','Q1',2024,1),
(20240121,'2024-01-21','Sunday',21,1,'January','Q1',2024,1),
(20240122,'2024-01-22','Monday',22,1,'January','Q1',2024,0),
(20240123,'2024-01-23','Tuesday',23,1,'January','Q1',2024,0),
(20240124,'2024-01-24','Wednesday',24,1,'January','Q1',2024,0),
(20240125,'2024-01-25','Thursday',25,1,'January','Q1',2024,0),
(20240126,'2024-01-26','Friday',26,1,'January','Q1',2024,0),
(20240127,'2024-01-27','Saturday',27,1,'January','Q1',2024,1),
(20240128,'2024-01-28','Sunday',28,1,'January','Q1',2024,1),
(20240129,'2024-01-29','Monday',29,1,'January','Q1',2024,0),
(20240130,'2024-01-30','Tuesday',30,1,'January','Q1',2024,0),
(20240131,'2024-01-31','Wednesday',31,1,'January','Q1',2024,0),
(20240201,'2024-02-01','Thursday',1,2,'February','Q1',2024,0),
(20240202,'2024-02-02','Friday',2,2,'February','Q1',2024,0),
(20240203,'2024-02-03','Saturday',3,2,'February','Q1',2024,1),
(20240204,'2024-02-04','Sunday',4,2,'February','Q1',2024,1),
(20240205,'2024-02-05','Monday',5,2,'February','Q1',2024,0),
(20240206,'2024-02-06','Tuesday',6,2,'February','Q1',2024,0),
(20240207,'2024-02-07','Wednesday',7,2,'February','Q1',2024,0),
(20240208,'2024-02-08','Thursday',8,2,'February','Q1',2024,0),
(20240209,'2024-02-09','Friday',9,2,'February','Q1',2024,0),
(20240210,'2024-02-10','Saturday',10,2,'February','Q1',2024,1),
(20240211,'2024-02-11','Sunday',11,2,'February','Q1',2024,1),
(20240212,'2024-02-12','Monday',12,2,'February','Q1',2024,0),
(20240213,'2024-02-13','Tuesday',13,2,'February','Q1',2024,0);

-- -------------------------
-- dim_product (15 rows, 3 categories)
-- product_key will be 1..15 in insert order
-- -------------------------
INSERT INTO dim_product
(product_id, product_name, category, subcategory, unit_price)
VALUES
('P001','Samsung Galaxy S21','Electronics','Smartphones',45999.00),
('P002','Apple MacBook Pro 14','Electronics','Laptops',99999.00),
('P003','Dell 27-inch 4K Monitor','Electronics','Monitors',32999.00),
('P004','Sony WH-1000XM5 Headphones','Electronics','Audio',29990.00),
('P005','iPhone 13','Electronics','Smartphones',69999.00),

('P006','Nike Running Shoes','Fashion','Footwear',3499.00),
('P007','Levi''s 511 Jeans','Fashion','Apparel',2999.00),
('P008','Adidas T-Shirt','Fashion','Apparel',1299.00),
('P009','Puma Sneakers','Fashion','Footwear',4599.00),
('P010','Reebok Trackpants','Fashion','Apparel',1899.00),

('P011','Organic Almonds 1kg','Groceries','Dry Fruits',899.00),
('P012','Basmati Rice 5kg','Groceries','Grains',650.00),
('P013','Masoor Dal 1kg','Groceries','Pulses',120.00),
('P014','Organic Honey 500g','Groceries','Condiments',450.00),
('P015','Masala Tea 500g','Groceries','Beverages',320.00);

-- -------------------------
-- dim_customer (12 rows)
-- customer_key will be 1..12 in insert order
-- -------------------------
INSERT INTO dim_customer
(customer_id, customer_name, city, state, customer_segment)
VALUES
('C001','Rahul Sharma','Bangalore','Karnataka','Consumer'),
('C002','Priya Patel','Mumbai','Maharashtra','Consumer'),
('C003','Sneha Reddy','Hyderabad','Telangana','Corporate'),
('C004','Karthik Nair','Delhi','Delhi','Consumer'),
('C005','Arjun Rao','Hyderabad','Telangana','Home Office'),
('C006','Anjali Mehta','Bangalore','Karnataka','Corporate'),
('C007','Suresh Patel','Mumbai','Maharashtra','Consumer'),
('C008','Swati Desai','Pune','Maharashtra','Consumer'),
('C009','Neha Shah','Ahmedabad','Gujarat','Corporate'),
('C010','Rajesh Kumar','Delhi','Delhi','Consumer'),
('C011','Divya Menon','Bangalore','Karnataka','Home Office'),
('C012','Manish Joshi','Mumbai','Maharashtra','Consumer');

-- -------------------------
-- fact_sales (40 rows)
-- IMPORTANT: product_key and customer_key reference the auto-increment keys
-- total_amount = (quantity_sold * unit_price) - discount_amount
-- -------------------------
INSERT INTO fact_sales
(date_key, product_key, customer_key, quantity_sold, unit_price, discount_amount, total_amount)
VALUES
(20240204, 2, 1, 8, 99999.00, 4999.95, 794992.05),
(20240122, 3, 12, 1, 32999.00, 0.00, 32999.00),
(20240212, 9, 2, 4, 4599.00, 459.90, 17936.10),
(20240118, 2, 4, 1, 99999.00, 0.00, 99999.00),
(20240130, 12, 1, 1, 650.00, 0.00, 650.00),
(20240117, 2, 9, 1, 99999.00, 0.00, 99999.00),
(20240121, 9, 8, 6, 4599.00, 459.90, 27134.10),
(20240202, 9, 12, 2, 4599.00, 0.00, 9198.00),
(20240212, 9, 4, 1, 4599.00, 0.00, 4599.00),
(20240120, 4, 3, 8, 29990.00, 0.00, 239920.00),

(20240120, 7, 5, 6, 2999.00, 0.00, 17994.00),
(20240204, 1, 4, 3, 45999.00, 2299.95, 135697.05),
(20240207, 6, 3, 1, 3499.00, 0.00, 3499.00),
(20240123, 2, 12, 3, 99999.00, 0.00, 299997.00),
(20240205, 5, 8, 3, 69999.00, 3499.95, 206497.05),
(20240131, 15, 12, 1, 320.00, 0.00, 320.00),
(20240126, 5, 7, 4, 69999.00, 0.00, 279996.00),
(20240208, 13, 10, 2, 120.00, 0.00, 240.00),
(20240128, 4, 2, 7, 29990.00, 1499.50, 208430.50),
(20240128, 11, 4, 8, 899.00, 0.00, 7192.00),

(20240125, 1, 9, 2, 45999.00, 0.00, 91998.00),
(20240124, 9, 4, 3, 4599.00, 0.00, 13797.00),
(20240202, 2, 6, 1, 99999.00, 4999.95, 9500.00),
(20240211, 14, 9, 7, 450.00, 0.00, 3150.00),
(20240211, 2, 11, 7, 99999.00, 0.00, 699993.00),
(20240129, 3, 5, 2, 32999.00, 0.00, 65998.00),
(20240119, 10, 3, 2, 1899.00, 0.00, 3798.00),
(20240203, 5, 12, 5, 69999.00, 3499.95, 346495.05),
(20240115, 12, 7, 2, 650.00, 0.00, 1300.00),
(20240121, 3, 2, 6, 32999.00, 0.00, 197994.00),

(20240122, 14, 1, 1, 450.00, 0.00, 450.00),
(20240210, 2, 5, 6, 99999.00, 4999.95, 594994.05),
(20240127, 8, 9, 7, 1299.00, 0.00, 9093.00),
(20240206, 1, 12, 2, 45999.00, 0.00, 91998.00),
(20240116, 13, 8, 1, 120.00, 0.00, 120.00),
(20240209, 6, 10, 3, 3499.00, 349.90, 10147.10),
(20240123, 4, 6, 1, 29990.00, 0.00, 29990.00),
(20240213, 15, 3, 2, 320.00, 0.00, 640.00),
(20240118, 11, 2, 1, 899.00, 0.00, 899.00),
(20240201, 9, 7, 1, 4599.00, 0.00, 4599.00);
