import sqlite3
import pandas as pd
import os

RAW_DB = "db/retail_analytics_raw.db"
CLEAN_DB = "db/retail_analytics.db"

if os.path.exists(CLEAN_DB):
    os.remove(CLEAN_DB)

print("--- STEP 1: Loading Authentic Kaggle Dataset & Running Data Cleaning Pipeline ---")
raw_conn = sqlite3.connect(RAW_DB)
clean_conn = sqlite3.connect(CLEAN_DB)

# Ensure raw database has the latest authentic raw CSVs
tables = {
    "orders": "data/raw/orders.csv",
    "customers": "data/raw/customers.csv",
    "order_items": "data/raw/order_items.csv",
    "products": "data/raw/products.csv",
    "order_payments": "data/raw/order_payments.csv",
    "order_reviews": "data/raw/order_reviews.csv",
    "product_category_name_translation": "data/raw/category_translation.csv"
}

for tbl, path in tables.items():
    df = pd.read_csv(path)
    df.to_sql(tbl, raw_conn, index=False, if_exists="replace")
    df.to_sql(tbl, clean_conn, index=False, if_exists="replace")

# Read and execute 01_data_cleaning.sql
with open("sql/01_data_cleaning.sql", "r") as f:
    cleaning_sql = f.read()

clean_conn.executescript(cleaning_sql)

# Audit metrics
raw_items_cnt = pd.read_sql("SELECT COUNT(*) AS cnt FROM order_items", raw_conn).iloc[0]["cnt"]
clean_items_cnt = pd.read_sql("SELECT COUNT(*) AS cnt FROM clean_order_items", clean_conn).iloc[0]["cnt"]

print(f"Data Cleaning Audit on Authentic Dataset:")
print(f"  - Order Items Raw Rows: {raw_items_cnt:,}")
print(f"  - Order Items Clean Rows: {clean_items_cnt:,} (Deduplicated {raw_items_cnt - clean_items_cnt:,} duplicate rows)")

# Save clean tables to data/cleaned/
clean_tables = ["clean_products", "clean_customers", "clean_orders", "clean_order_items", "clean_order_payments", "clean_order_reviews"]
for tbl in clean_tables:
    df = pd.read_sql(f"SELECT * FROM {tbl}", clean_conn)
    df.to_csv(f"data/cleaned/{tbl}.csv", index=False)

print("\n--- STEP 2: Executing Business Queries Suite on Authentic Data ---")

os.makedirs("results", exist_ok=True)

queries = [
    ("Query 1: Monthly Revenue Trend & MoM Growth", """
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
    """),
    ("Query 2: Top & Bottom Product Categories", """
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
    """),
    ("Query 3: Customer Repeat Purchase Rate", """
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
    """),
    ("Query 4: Regional Revenue & Shipping Cost Breakdown", """
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
    """),
    ("Query 5: Fulfillment Efficiency & Delivery Delay Anomalies", """
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
    """),
    ("Query 6: Payment Method & Installment Breakdown", """
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
    """),
    ("Query 7: Delivery Delay Impact on Customer Satisfaction", """
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
    """)
]

for idx, (title, sql_code) in enumerate(queries, 1):
    df_res = pd.read_sql(sql_code, clean_conn)
    out_path = f"results/query_{idx}_results.csv"
    df_res.to_csv(out_path, index=False)
    print(f"\n=======================================================")
    print(f"QUERY {idx}: {title}")
    print(f"=======================================================")
    print(df_res.to_string(index=False))

raw_conn.close()
clean_conn.close()
print("\nAll 7 queries executed successfully on the authentic dataset!")
