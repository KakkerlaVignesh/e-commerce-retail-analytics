# Power BI Dashboard Specification & Build Guide
**Project**: E-Commerce Retail Analytics Dashboard  
**Dataset**: Authentic Kaggle Olist Brazilian E-Commerce Dataset (99,441 Orders)  

---

## 1. Executive Dashboard Layout & Wireframe

The dashboard is structured into **2 interactive pages** optimized for 16:9 canvas ratio (1920 x 1080 px) with a modern dark theme background (`#1A1D24`), navy card containers (`#242832`), teal primary accents (`#00D1C1`), and high-contrast typography (`#FFFFFF`). All financial values are formatted in **Brazilian Real (R$)**.

### Page 1: Executive Sales & Revenue Overview

```
+---------------------------------------------------------------------------------------------------+
|  [LOGO] E-COMMERCE EXECUTIVE REVENUE & SALES OVERVIEW                  [Slicers: Year | State | Category]  |
+---------------------------------------------------------------------------------------------------+
|  +------------------+  +------------------+  +------------------+  +------------------+  +-------------+  |
|  | TOTAL REVENUE    |  | TOTAL ORDERS     |  | AVG ORDER VALUE  |  | REPEAT RATE      |  | ON-TIME RATE|  |
|  |   R$ 15.42M      |  |   96,478         |  |   R$ 159.85      |  |   3.00%          |  |   92.01%    |  |
|  +------------------+  +------------------+  +------------------+  +------------------+  +-------------+  |
+---------------------------------------------------------------------------------------------------+
|  +------------------------------------------------------+  +------------------------------------------+  |
|  | VISUAL 1: Monthly Revenue Trend & MoM Growth %       |  | VISUAL 2: Top 10 Product Categories      |  |
|  | (Line & Stacked Bar Chart: Revenue R$ vs MoM % Line)   |  | (Horizontal Clustered Bar Chart)         |  |
|  |                                                      |  | Health & Beauty | R$ 1.26M               |  |
|  | R$ 1.2M |=======\                                    |  | Watches Gifts   | R$ 1.21M               |  |
|  | R$ 1.0M |       \=====\                              |  | Bed Bath Table  | R$ 1.04M               |  |
|  | R$ 800k |              \=======                      |  | Sports Leisure  | R$ 988K                |  |
|  +------------------------------------------------------+  +------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
|  +------------------------------------------------------+  +------------------------------------------+  |
|  | VISUAL 3: Revenue & Orders Share by State            |  | VISUAL 4: Payment Method Market Share    |  |
|  | (Filled Map / Clustered Bar: SP 37.4%, RJ 13.3%)     |  | (Donut Chart: Credit Card 78.5%, Boleto) |  |
|  +------------------------------------------------------+  +------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Step-by-Step Power BI Desktop Build Instructions

### Step 1: Data Import
1. Open **Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV**.
3. Load the 6 cleaned CSV files from `data/cleaned/`:
   - `clean_orders.csv`
   - `clean_customers.csv`
   - `clean_products.csv`
   - `clean_order_items.csv`
   - `clean_order_payments.csv`
   - `clean_order_reviews.csv`
4. Set currency format for `price`, `freight_value`, and `payment_value` to **Currency ($ / R$)** -> Select **Portuguese (Brazil) R$**.

### Step 2: Create Calendar / DimDate Table
```dax
DimDate = 
ADDCOLUMNS(
    CALENDAR(DATE(2016, 1, 1), DATE(2018, 12, 31)),
    "Year", YEAR([Date]),
    "Month", FORMAT([Date], "MMM"),
    "MonthNo", MONTH([Date]),
    "YearMonth", FORMAT([Date], "YYYY-MM"),
    "Quarter", "Q" & FORMAT([Date], "Q")
)
```

### Step 3: Visual Configuration & Placement
1. **KPI Header Cards**:
   - Card 1: `[Total Revenue]` -> Format as Currency (R$ 15.42M)
   - Card 2: `[Total Orders]` -> Whole Number (96,478)
   - Card 3: `[Average Order Value]` -> Currency (R$ 159.85)
   - Card 4: `[Repeat Customer Rate %]` -> Percentage (3.00%)
   - Card 5: `[On-Time Delivery Rate %]` -> Percentage (92.01%)
2. **Visual 1 (Line & Stacked Column Chart)**: Monthly Revenue (R$) & MoM Growth %.
3. **Visual 2 (Horizontal Clustered Bar Chart)**: Top 10 Product Categories by Revenue (R$).
4. **Visual 3 (Clustered Bar Chart / Map)**: Gross Revenue Share by State (SP R$ 5.77M, RJ R$ 2.06M, MG R$ 1.82M).
5. **Visual 4 (Donut Chart)**: Payment Method Distribution (Credit Card R$ 12.10M / 78.5%).
