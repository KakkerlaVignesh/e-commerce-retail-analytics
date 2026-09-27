# 🛒 Authentic Kaggle Olist E-Commerce Data Analytics Portfolio Project

> **End-to-End Data Analyst Portfolio Project** analyzing 96,478 delivered orders, R$ 15.42M in Gross Merchandise Revenue, and customer satisfaction metrics using the **Authentic Kaggle Olist Dataset**, **SQL (SQLite)**, **Python**, and **Power BI**.

[![SQL](https://img.shields.io/badge/SQL-SQLite%20%2F%20ANSI-blue?logo=sqlite)](sql/)
[![Python](https://img.shields.io/badge/Python-3.13-green?logo=python)](scripts/)
[![Power BI](https://img.shields.io/badge/Power_BI-Desktop_Dashboard-yellow?logo=powerbi)](dashboard/)

---

## 📌 Project Overview & Structure

```
├── README.md                          # Main Repository Documentation & Showcase
├── executive_summary.md               # 1-Page Executive Business Report
├── resume_bullets.md                  # Copy-Paste Resume Paragraph & Bullets
├── data/
│   ├── raw/                           # Raw Authentic Kaggle CSV Datasets
│   └── cleaned/                       # Cleaned & Normalized CSV Datasets
├── db/
│   ├── retail_analytics_raw.db        # Raw SQLite Database
│   └── retail_analytics.db            # Cleaned SQLite Relational Database
├── scripts/
│   ├── download_real_olist.py         # Authentic Kaggle Dataset Downloader
│   └── run_analysis.py                # Data Pipeline & SQL Execution Engine
├── sql/
│   ├── 01_data_cleaning.sql           # Data Cleaning & Standardization Queries
│   └── 02_business_queries.sql        # 7 Business Queries (CTEs & Window Functions)
├── dashboard/
│   ├── powerbi_guide.md               # Wireframe Diagram & Step-by-Step Build Guide
│   └── dax_measures.dax               # Production DAX Formulas File
└── results/                           # Exported Query Output CSVs
```

---

## 1. 📊 Dataset Selection & Business Justification

**Dataset Source**: [Official Kaggle Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (99,441 orders, 112,650 items spanning 2016–2018).

### Why this dataset fits a Retail Analytics Portfolio Project:
1. **Authentic Multi-Table Relational Schema**: Features 7 interconnected tables (`customers`, `orders`, `order_items`, `products`, `payments`, `reviews`, `sellers`, `category_translation`).
2. **Real-World Complexity**: Contains messy real-world challenges such as duplicate line items, unstandardized timestamps, Portuguese category names, missing review scores, and freight variations.
3. **End-to-End E-Commerce Metrics**: Enables holistic analysis across sales revenue trends, customer lifetime value (LTV), logistics delivery latency, payment installments, and customer review scores.

---

## 2. ❓ 7 Core Business Questions Answered

1. **Monthly Revenue & MoM Growth**: What is the overall monthly revenue trend, total order volume, and month-over-month (MoM) revenue growth rate?
2. **Top & Bottom Product Categories**: Which product categories generate the highest total sales volume, revenue, and average unit price point?
3. **Customer Repeat Purchase Rate**: What percentage of customers return to place repeat purchases, and how is purchase frequency distributed?
4. **Regional & State Sales Performance**: Which Brazilian states generate the highest total revenue, order count, and average freight costs per order?
5. **Order Fulfillment Latency & Delay Anomalies**: What is the average order delivery time versus estimated delivery time, and which states experience the highest delivery delay rate?
6. **Payment Preferences & Installments**: How do customers pay for orders (Credit Card, Boleto, Voucher, Debit Card), and how do installments relate to purchase values?
7. **Delivery Delay Impact on Customer Reviews**: How severely do fulfillment delays degrade customer review ratings and increase 1-star reviews?

---

## 3. 🧹 Data Cleaning & Preprocessing Audit

The raw dataset contained several data quality flaws handled by our Python cleaning pipeline (`scripts/run_analysis.py`) and SQL cleaning script (`sql/01_data_cleaning.sql`):

| Data Issue Identified | Affected Table & Column | Solution / Cleaning Action Taken | Audit Metric |
| :--- | :--- | :--- | :--- |
| **Duplicate Records** | `order_items` | Deduplicated using `ROW_NUMBER() OVER(PARTITION BY order_id, item_id...)` | Identifies exact duplicate rows |
| **Missing Review Scores** | `order_reviews.review_score` | Imputed NULL ratings with cohort median rating (3.0) | Imputed missing review entries |
| **Non-Standard Timestamps** | `orders.order_purchase_timestamp` | Replaced slash dates (`YYYY/MM/DD`) with standard SQL `YYYY-MM-DD HH:MM:SS` | Standardized 100% of order timestamps |
| **Portuguese Categories** | `products.product_category_name` | Joined with translation table & mapped unstandardized strings | 100% mapped to English titles |
| **Text Casing & Whitespace**| `customers` & `products` | Applied `UPPER()`, `LOWER()`, and `TRIM()` functions | Text attributes standardized |

---

## 4. 💻 Advanced SQL Query Suite & Authentic Results

All queries were executed against the live SQLite database (`db/retail_analytics.db`). Below are the exact SQL code blocks and output tables from the authentic Kaggle dataset.

### Query 1: Monthly Revenue Trend & Month-over-Month (MoM) Growth Rate
```sql
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
```
#### Output Results (Sample):
| year_month | total_orders | monthly_revenue | prev_month_revenue | mom_growth_pct |
| :--- | :--- | :--- | :--- | :--- |
| **2017-01** | 750 | R$ 137,364.53 | R$ 19.40 | +707964% |
| **2017-02** | 1,634 | R$ 285,429.98 | R$ 137,364.53 | +107.79% |
| **2017-03** | 2,514 | R$ 430,307.72 | R$ 285,429.98 | +50.76% |
| **2017-11** | 7,289 | R$ 1,177,755.73 | R$ 760,202.93 | +54.93% |
| **2018-08** | 6,351 | R$ 1,004,136.21 | R$ 1,027,861.94 | -2.31% |

---

### Query 2: Product Category Performance & Revenue Ranking
```sql
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
```
#### Output Results (Top 5):
| product_category_name | total_orders | total_items_sold | gross_merchandise_revenue | avg_item_price | revenue_rank |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **beleza_saude** (health_beauty) | 8,836 | 9,670 | **R$ 1,258,681.34** | R$ 130.16 | 1 |
| **relogios_presentes** (watches) | 5,624 | 5,991 | **R$ 1,205,005.68** | R$ 201.14 | 2 |
| **cama_mesa_banho** (bed_bath) | 9,417 | 11,115 | **R$ 1,036,988.03** | R$ 93.30 | 3 |
| **esporte_lazer** (sports) | 7,720 | 8,641 | **R$ 988,048.97** | R$ 114.34 | 4 |
| **informatica_acessorios** | 6,689 | 7,827 | **R$ 911,954.32** | R$ 116.51 | 5 |

---

### Query 3: Customer Repeat Purchase Rate
```sql
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
```
#### Output Results:
| total_customers | single_order_customers | repeat_customers | repeat_purchase_rate_pct |
| :--- | :--- | :--- | :--- |
| **93,358** | 90,557 | **2,801** | **3.00%** |

---

### Query 4: Regional Revenue & Shipping Cost Breakdown by State
```sql
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
    ROUND((total_state_revenue * 100.0 / SUM(total_state_revenue) OVER ()), 2) AS revenue_share_pct
FROM state_summary
ORDER BY total_state_revenue DESC;
```
#### Output Results (Top 5 States):
| customer_state | total_orders | total_state_revenue | avg_order_value | avg_freight_cost | revenue_share_pct |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SP** (São Paulo) | 40,501 | **R$ 5,771,713.93** | **R$ 142.51** | R$ 15.16 | **37.42%** |
| **RJ** (Rio de Janeiro)| 12,350 | **R$ 2,055,636.12** | **R$ 166.45** | R$ 20.93 | **13.33%** |
| **MG** (Minas Gerais) | 11,354 | **R$ 1,819,357.56** | **R$ 160.24** | R$ 20.66 | **11.80%** |
| **RS** (Rio Grande) | 5,345 | **R$ 861,734.99** | **R$ 161.22** | R$ 21.66 | **5.59%** |
| **PR** (Paraná) | 4,923 | **R$ 781,851.01** | **R$ 158.82** | R$ 20.50 | **5.07%** |

---

### Query 5: Order Fulfillment Latency & Delivery Delay Anomalies
```sql
WITH delivery_performance AS (
    SELECT 
        c.customer_state,
        o.order_id,
        JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp) AS actual_delivery_days,
        JULIANDAY(o.order_estimated_delivery_date) - JULIANDAY(o.order_purchase_timestamp) AS estimated_delivery_days,
        CASE WHEN JULIANDAY(o.order_delivered_customer_date) > JULIANDAY(o.order_estimated_delivery_date) THEN 1 ELSE 0 END AS is_delayed
    FROM clean_orders o
    JOIN clean_customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
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
```
#### Output Results (Sample):
| customer_state | total_delivered_orders | avg_actual_delivery_days | avg_estimated_delivery_days | total_delayed_orders | delay_rate_pct |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AL** (Alagoas) | 397 | 24.5 | 32.6 | 95 | **23.93%** |
| **MA** (Maranhão) | 717 | 21.6 | 30.5 | 141 | **19.67%** |
| **PI** (Piauí) | 476 | 19.5 | 30.1 | 76 | **15.97%** |
| **CE** (Ceará) | 1,279 | 21.3 | 31.4 | 196 | **15.32%** |
| **SP** (São Paulo) | 40,494 | 8.8 | 19.1 | 2,387 | **5.89%** |

---

### Query 6: Payment Method Share & Installment Analysis
```sql
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
    ROUND((total_payment_value * 100.0 / SUM(total_payment_value) OVER ()), 2) AS market_share_pct
FROM payment_summary
ORDER BY total_payment_value DESC;
```
#### Output Results:
| payment_type | total_orders | total_payment_value | avg_transaction_value | avg_installments | market_share_pct |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **credit_card** | 74,304 | **R$ 12,101,094.88** | R$ 162.24 | 3.5 | **78.46%** |
| **boleto** | 19,191 | **R$ 2,769,932.58** | R$ 144.33 | 1.0 | **17.96%** |
| **voucher** | 3,679 | **R$ 343,013.19** | R$ 62.45 | 1.0 | **2.22%** |
| **debit_card** | 1,485 | **R$ 208,421.12** | R$ 140.26 | 1.0 | **1.35%** |

---

### Query 7: Delivery Delay Impact on Customer Review Satisfaction
```sql
WITH delivery_reviews AS (
    SELECT 
        r.review_score,
        CASE 
            WHEN JULIANDAY(o.order_delivered_customer_date) > JULIANDAY(o.order_estimated_delivery_date) THEN 'Late Delivery'
            ELSE 'On-Time / Early'
        END AS delivery_status
    FROM clean_orders o
    JOIN clean_order_reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
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
```
#### Output Results:
| delivery_status | total_reviews | avg_review_score | 5-Star Count | 5-Star % | 1-Star Count | 1-Star % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **On-Time / Early** | 88,653 | **4.29 / 5.0** | 55,348 | **62.43%** | 5,851 | **6.60%** |
| **Late Delivery** | 7,700 | **2.57 / 5.0** | 1,711 | **22.22%** | 3,554 | **46.16%** |

---

## 5. 🎨 Power BI Dashboard Layout & DAX Specification

For full build instructions, wireframe diagrams, and DAX measures, view [`dashboard/powerbi_guide.md`](dashboard/powerbi_guide.md).

---

## 6. 📄 Executive Summary & Strategic Recommendations

Read the 1-page business report in [`executive_summary.md`](executive_summary.md).

---

> End-to-end retail analytics project evaluating R$ 15.42M in gross merchandise revenue across 96,478 delivered orders from the authentic Kaggle Olist dataset. Engineered an automated Python/SQLite data pipeline to clean 112,000+ transactional records, deduplicate item entries, and handle missing attributes. Wrote advanced SQL queries utilizing CTEs and Window Functions (`LAG`, `DENSE_RANK`, `SUM OVER`) to analyze monthly revenue trends, customer repeat purchase rate (3.0%), average order value (R$ 159.85), and regional logistics bottlenecks. Built an interactive 2-page Power BI executive dashboard with DAX measures, revealing that delivery delays cause a 1.72-point drop in customer review ratings and surge 1-star reviews from 6.6% to 46.2%.
