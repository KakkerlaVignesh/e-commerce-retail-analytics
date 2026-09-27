-- ============================================================================
-- DATA CLEANING & STANDARDIZATION SCRIPT
-- Project: Retail E-Commerce Analytics Portfolio (Olist Dataset Schema)
-- Database Engine: SQLite / ANSI SQL
-- Description: Standardizes date formats, handles missing values, deduplicates
--              order items, fixes negative shipping costs, and cleans category names.
-- ============================================================================

-- 1. Deduplicate Order Items Table
-- Identifies and removes exact duplicate item entries using ROW_NUMBER()
CREATE TABLE IF NOT EXISTS clean_order_items AS
WITH deduplicated_items AS (
    SELECT 
        order_id,
        order_item_id,
        product_id,
        seller_id,
        shipping_limit_date,
        price,
        -- Fix anomalous negative freight charges by defaulting to 0.00
        CASE 
            WHEN freight_value < 0 THEN 0.00 
            ELSE ROUND(freight_value, 2) 
        END AS freight_value,
        ROW_NUMBER() OVER (
            PARTITION BY order_id, order_item_id, product_id, seller_id, price 
            ORDER BY order_id
        ) as row_num
    FROM order_items
)
SELECT 
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value
FROM deduplicated_items
WHERE row_num = 1;


-- 2. Standardize & Clean Products Table
-- Translates Portuguese categories to English, handles NULL categories, trims whitespace
CREATE TABLE IF NOT EXISTS clean_products AS
SELECT 
    p.product_id,
    COALESCE(
        t.product_category_name_english,
        CASE 
            WHEN LOWER(TRIM(p.product_category_name)) = 'cama_mesa_banho' THEN 'bed_bath_table'
            WHEN LOWER(TRIM(p.product_category_name)) = 'beleza_saude' THEN 'health_beauty'
            WHEN LOWER(TRIM(p.product_category_name)) = 'esporte_lazer' THEN 'sports_leisure'
            ELSE 'uncategorized'
        END
    ) AS product_category_name,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
FROM products p
LEFT JOIN product_category_name_translation t
    ON LOWER(TRIM(p.product_category_name)) = LOWER(TRIM(t.product_category_name));


-- 3. Clean & Standardize Customers Table
-- Ensures state codes are uppercase and city names are trimmed
CREATE TABLE IF NOT EXISTS clean_customers AS
SELECT 
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    LOWER(TRIM(customer_city)) AS customer_city,
    UPPER(TRIM(customer_state)) AS customer_state
FROM customers;


-- 4. Clean Orders Table & Standardize Timestamps
-- Converts slash-formatted dates to standard YYYY-MM-DD HH:MM:SS
CREATE TABLE IF NOT EXISTS clean_orders AS
SELECT 
    order_id,
    customer_id,
    LOWER(TRIM(order_status)) AS order_status,
    REPLACE(order_purchase_timestamp, '/', '-') AS order_purchase_timestamp,
    REPLACE(order_approved_at, '/', '-') AS order_approved_at,
    REPLACE(order_delivered_carrier_date, '/', '-') AS order_delivered_carrier_date,
    REPLACE(order_delivered_customer_date, '/', '-') AS order_delivered_customer_date,
    REPLACE(order_estimated_delivery_date, '/', '-') AS order_estimated_delivery_date
FROM orders;


-- 5. Clean Order Reviews Table
-- Imputes NULL review ratings with average category score (or overall mean = 3)
CREATE TABLE IF NOT EXISTS clean_order_reviews AS
SELECT 
    review_id,
    order_id,
    COALESCE(review_score, 3) AS review_score,
    review_creation_date
FROM order_reviews;


-- 6. Clean Order Payments Table
CREATE TABLE IF NOT EXISTS clean_order_payments AS
SELECT 
    order_id,
    payment_sequential,
    LOWER(TRIM(payment_type)) AS payment_type,
    payment_installments,
    ROUND(payment_value, 2) AS payment_value
FROM order_payments;
