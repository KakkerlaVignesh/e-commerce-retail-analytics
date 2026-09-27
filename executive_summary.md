# Executive Summary: E-Commerce Retail Analytics & Customer Satisfaction Drivers

**Project**: Authentic Kaggle Olist Brazilian E-Commerce Sales & Fulfillment Analytics  
**Author**: Data Analytics Specialist  
**Dataset Analyzed**: Authentic Kaggle Dataset | 96,478 Delivered Orders | R$ 15.42M Gross Revenue | 2016–2018  

---

## 1. Executive Business Problem Statement

As e-commerce marketplaces scale, balancing revenue growth, customer retention, and fulfillment efficiency becomes critical to long-term profitability. Olist, a major Brazilian marketplace operating across 27 state regions, faces operational complexity in managing regional shipping logistics, payment options, and category expansion.

This analysis was conducted on the **authentic Kaggle Olist dataset** to evaluate key revenue growth drivers, assess regional sales concentration, measure customer repeat purchase dynamics, and quantify the direct impact of fulfillment delays on customer satisfaction and review ratings.

---

## 2. Methodology & Analytical Approach

- **Data Ingestion & Cleaning**: Cleaned, standardized, and normalized 7 raw relational tables (99,441 orders, 112,650 order items) using Python (`pandas`, `sqlite3`) and ANSI SQL. Deduplicated order item entries, imputed missing review scores, standardized ISO timestamps, and resolved category translation mappings.
- **Database Engine**: Deployed an SQLite database (`retail_analytics.db`) to write complex multi-table SQL queries utilizing Common Table Expressions (CTEs), Window Functions (`LAG()`, `DENSE_RANK()`, `SUM() OVER()`), date metrics (`JULIANDAY`), and conditional aggregations.
- **Business Intelligence**: Visualized insights through an interactive 2-page Power BI dashboard featuring dynamic DAX measures (`MoM Revenue Growth %`, `On-Time Delivery Rate %`, `Repeat Customer Rate %`).

---

## 3. Key Findings & Authentic Data Insights

### Insight 1: Revenue Concentration in Health & Beauty and Watches Categories
- Gross merchandise revenue reached **R$ 15,422,461.77** across 96,478 delivered orders, with an Average Order Value (AOV) of **R$ 159.85**.
- Revenue is heavily concentrated in top-tier product categories. **Health & Beauty** (beleza_saude) ranked #1, generating **R$ 1,258,681.34** (8,836 orders, 9,670 items sold, avg unit price R$ 130.16). 
- **Watches & Gifts** (#2) generated **R$ 1,205,005.68** (5,624 orders, avg unit price R$ 201.14), while **Bed Bath & Table** (#3) contributed **R$ 1,036,988.03**. Together, the top 5 categories generate over 35% of total merchandise revenue.

### Insight 2: Low E-Commerce Retention Rate (3.00% Repeat Purchase Rate)
- Across 93,358 unique delivered buyers (`customer_unique_id`), **90,557 customers bought once** while **2,801 customers made 2 or more purchases**, yielding a **3.00% Repeat Purchase Rate**.
- This reveals that Olist operates primarily as a top-of-funnel customer acquisition marketplace where customer retention is low, highlighting an urgent strategic need for re-engagement marketing and loyalty incentive programs.

### Insight 3: Massive Regional Revenue Concentration in São Paulo (37.42% Revenue Share)
- **São Paulo (SP)** is the dominant market leader, generating **R$ 5,771,713.93** (**37.42% of total national revenue**) across 40,501 orders with an Average Order Value of **R$ 142.51** and low average freight cost of R$ 15.16.
- **Rio de Janeiro (RJ)** ranked 2nd with **R$ 2,055,636.12** (13.33% share, AOV R$ 166.45), followed by **Minas Gerais (MG)** at **R$ 1,819,357.56** (11.80% share, AOV R$ 160.24). These top 3 states account for **62.55% of total marketplace revenue**.
- Northeastern states experience severe logistics fulfillment delays: **Alagoas (AL)** recorded a **23.93% delay rate** (avg delivery 24.5 days), **Maranhão (MA)** recorded **19.67%**, and **Piauí (PI)** recorded **15.97%**, compared to 5.89% in SP (avg delivery 8.8 days).

### Insight 4: Severe Satisfaction Penalty for Delayed Deliveries (1.72 Point Rating Drop)
- Analysis revealed a major drop in review scores due to fulfillment delays across 96,353 order reviews:
  - **On-Time / Early Deliveries** (88,653 reviews): Achieved an average review rating of **4.29 / 5.0**, with **62.43% 5-star ratings** and **6.60% 1-star ratings**.
  - **Late Deliveries** (7,700 reviews): Suffered an average review rating of **2.57 / 5.0**, representing a **1.72 point drop** in customer rating. 
  - **1-Star Surge**: Delayed deliveries caused 1-star negative reviews to jump **from 6.60% to 46.16% (a 7x increase)**.

---

## 4. Strategic Business Recommendations

1. **Establish Regional Fulfillment Centers in Northeastern Brazil**:
   - Build distribution centers in Alagoas, Maranhão, and Ceará to cut shipping latency from 24+ days down to under 10 days, reducing regional delay rates below 8%.

2. **Promote Credit Card Installments for High-Value Categories**:
   - Credit Card transactions account for **78.46% of total payments (R$ 12.10M)** with an average of 3.5 installments. Introduce zero-interest installment promos for high-value categories like Watches & Gifts (R$ 201.14 avg price) to increase basket size.

3. **Deploy Proactive Delay Notifications & Automated Account Credits**:
   - Implement real-time tracking alerts and issue automated R$ 15 account credits prior to the estimated delivery window passing to mitigate the 46.16% 1-star review penalty on late orders.

4. **Launch Repeat Buyer Loyalty & Subscription Programs**:
   - With repeat purchase rate at 3.00%, introducing a subscription membership (free shipping & cash-back rewards) could double 2nd-purchase conversion rates.
