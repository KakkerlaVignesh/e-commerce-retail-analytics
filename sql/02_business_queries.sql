-- ============================================================================
-- BUSINESS ANALYTICS QUERY SUITE
-- Project: Retail E-Commerce Analytics Portfolio (Olist Dataset Schema)
-- Engine: SQLite / ANSI SQL
-- Description: 7 production-grade business queries utilizing CTEs, Window Functions,
--              Multi-table Joins, and Conditional Aggregations.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: Monthly Revenue Trend & Month-over-Month (MoM) Growth Rate
-- Business Question: What is the overall monthly revenue trend, total order volume,
--                    and month-over-month (MoM) growth percentage?
-- Technical Skills: CTE, Window Function LAG(), DATE functions, Rounding
-- ----------------------------------------------------------------------------
WITH monthly_sales AS (
    SELECT 
        STRFTIME('%Y-%m', o.order_purchase_timestamp) AS year_month,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(i.price + i.freight_value), 2) AS monthly_revenue
    FROM clean_orders o
    JOIN clean_order_items i ON o.order_id = i.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY STRFTIME('%Y-%m', o.order_purchase_timestamp)
)
SELECT 
    year_month,
    total_orders,
    monthly_revenue,
    LAG(monthly_revenue, 1) OVER (ORDER BY year_month) AS prev_month_revenue,
    ROUND(
        (monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY year_month)) 
        / LAG(monthly_revenue, 1) OVER (ORDER BY year_month) * 100.0, 2
    ) AS mom_growth_pct
FROM monthly_sales
ORDER BY year_month;


-- ----------------------------------------------------------------------------
-- QUERY 2: Top & Bottom Product Categories by Sales Revenue and Volume
-- Business Question: Which product categories drive the highest revenue, sales volume,
--                    and average price point?
-- Technical Skills: Multi-table JOIN, DENSE_RANK() Window Function, GROUP BY
-- ----------------------------------------------------------------------------
WITH category_metrics AS (
    SELECT 
        p.product_category_name,
        COUNT(DISTINCT i.order_id) AS total_orders,
        COUNT(i.order_item_id) AS total_items_sold,
        ROUND(SUM(i.price), 2) AS gross_merchandise_revenue,
        ROUND(AVG(i.price), 2) AS avg_item_price
    FROM clean_order_items i
    JOIN clean_products p ON i.product_id = p.product_id
    JOIN clean_orders o ON i.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.product_category_name
)
SELECT 
    product_category_name,
    total_orders,
    total_items_sold,
    gross_merchandise_revenue,
    avg_item_price,
    DENSE_RANK() OVER (ORDER BY gross_merchandise_revenue DESC) AS revenue_rank
FROM category_metrics
ORDER BY revenue_rank ASC;


-- ----------------------------------------------------------------------------
-- QUERY 3: Customer Repeat Purchase Rate & Buyer Frequency Distribution
-- Business Question: What percentage of customers return to place multiple orders,
--                    and what is the breakdown of order frequency per buyer?
-- Technical Skills: Nested CTEs, Conditional Aggregation, Distinct Customer Counts
-- ----------------------------------------------------------------------------
WITH customer_order_counts AS (
    SELECT 
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM clean_customers c
    JOIN clean_orders o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
customer_segments AS (
    SELECT 
        COUNT(customer_unique_id) AS total_customers,
        SUM(CASE WHEN order_count = 1 THEN 1 ELSE 0 END) AS single_order_customers,
        SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers
    FROM customer_order_counts
)
SELECT 
    total_customers,
    single_order_customers,
    repeat_customers,
    ROUND((repeat_customers * 100.0 / total_customers), 2) AS repeat_purchase_rate_pct
FROM customer_segments;


-- ----------------------------------------------------------------------------
-- QUERY 4: Regional Revenue, Order Volume, & Freight Cost Breakdown by State
-- Business Question: Which Brazilian states generate the highest revenue and order volume,
--                    and how do average order values and freight costs vary regionally?
-- Technical Skills: JOIN across 3 tables, SUM OVER() Window Function for % Share
-- ----------------------------------------------------------------------------
WITH state_summary AS (
    SELECT 
        c.customer_state,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(i.price + i.freight_value), 2) AS total_state_revenue,
        ROUND(SUM(i.price + i.freight_value) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value,
        ROUND(AVG(i.freight_value), 2) AS avg_freight_cost
    FROM clean_customers c
    JOIN clean_orders o ON c.customer_id = o.customer_id
    JOIN clean_order_items i ON o.order_id = i.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_state
)
SELECT 
    customer_state,
    total_orders,
    total_state_revenue,
    avg_order_value,
    avg_freight_cost,
    ROUND(
        (total_state_revenue * 100.0 / SUM(total_state_revenue) OVER ()), 2
    ) AS revenue_share_pct
FROM state_summary
ORDER BY total_state_revenue DESC;


-- ----------------------------------------------------------------------------
-- QUERY 5: Fulfillment Efficiency & State-Level Delivery Delay Anomalies
-- Business Question: What is the average order delivery time versus estimated time,
--                    and which states suffer from the highest delivery delay rate?
-- Technical Skills: JULIANDAY Date Difference, Conditional Aggregation, Percentage Rates
-- ----------------------------------------------------------------------------
WITH delivery_performance AS (
    SELECT 
        c.customer_state,
        o.order_id,
        JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp) AS actual_delivery_days,
        JULIANDAY(o.order_estimated_delivery_date) - JULIANDAY(o.order_purchase_timestamp) AS estimated_delivery_days,
        CASE 
            WHEN JULIANDAY(o.order_delivered_customer_date) > JULIANDAY(o.order_estimated_delivery_date) THEN 1 
            ELSE 0 
        END AS is_delayed
    FROM clean_orders o
    JOIN clean_customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered' 
      AND o.order_delivered_customer_date IS NOT NULL
)
SELECT 
    customer_state,
    COUNT(order_id) AS total_delivered_orders,
    ROUND(AVG(actual_delivery_days), 1) AS avg_actual_delivery_days,
    ROUND(AVG(estimated_delivery_days), 1) AS avg_estimated_delivery_days,
    SUM(is_delayed) AS total_delayed_orders,
    ROUND((SUM(is_delayed) * 100.0 / COUNT(order_id)), 2) AS delay_rate_pct
FROM delivery_performance
GROUP BY customer_state
ORDER BY delay_rate_pct DESC;


-- ----------------------------------------------------------------------------
-- QUERY 6: Payment Method Breakdown & Installment Usage Preferences
-- Business Question: What payment methods do customers prefer, and how do payment
--                    installments correlate with total purchase value?
-- Technical Skills: GROUP BY, SUM OVER(), Aggregations
-- ----------------------------------------------------------------------------
WITH payment_summary AS (
    SELECT 
        p.payment_type,
        COUNT(DISTINCT p.order_id) AS total_orders,
        ROUND(SUM(p.payment_value), 2) AS total_payment_value,
        ROUND(AVG(p.payment_value), 2) AS avg_transaction_value,
        ROUND(AVG(p.payment_installments), 1) AS avg_installments
    FROM clean_order_payments p
    JOIN clean_orders o ON p.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.payment_type
)
SELECT 
    payment_type,
    total_orders,
    total_payment_value,
    avg_transaction_value,
    avg_installments,
    ROUND(
        (total_payment_value * 100.0 / SUM(total_payment_value) OVER ()), 2
    ) AS market_share_pct
FROM payment_summary
ORDER BY total_payment_value DESC;


-- ----------------------------------------------------------------------------
-- QUERY 7: Delivery Delay Impact on Customer Satisfaction Review Scores
-- Business Question: How significantly does late delivery impact overall review scores
--                    and 1-star ratings compared to on-time deliveries?
-- Technical Skills: Multi-table JOIN, Case Statements, Conditional Rating % Metrics
-- ----------------------------------------------------------------------------
WITH delivery_reviews AS (
    SELECT 
        r.review_score,
        CASE 
            WHEN JULIANDAY(o.order_delivered_customer_date) > JULIANDAY(o.order_estimated_delivery_date) THEN 'Late Delivery'
            ELSE 'On-Time / Early'
        END AS delivery_status
    FROM clean_orders o
    JOIN clean_order_reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered' 
      AND o.order_delivered_customer_date IS NOT NULL
)
SELECT 
    delivery_status,
    COUNT(*) AS total_reviews,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    SUM(CASE WHEN review_score = 5 THEN 1 ELSE 0 END) AS five_star_count,
    ROUND(SUM(CASE WHEN review_score = 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS five_star_pct,
    SUM(CASE WHEN review_score = 1 THEN 1 ELSE 0 END) AS one_star_count,
    ROUND(SUM(CASE WHEN review_score = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS one_star_pct
FROM delivery_reviews
GROUP BY delivery_status;
