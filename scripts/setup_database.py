import sqlite3
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

DB_PATH = "db/retail_analytics_raw.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Generating raw e-commerce retail dataset (Olist Schema)...")

# 1. Product Categories & Translation
categories = [
    ("cama_mesa_banho", "bed_bath_table"),
    ("beleza_saude", "health_beauty"),
    ("esporte_lazer", "sports_leisure"),
    ("informatica_acessorios", "computers_accessories"),
    ("utilidades_domesticas", "housewares"),
    ("relogios_presentes", "watches_gifts"),
    ("telefonia", "telephony"),
    ("ferramentas_jardim", "garden_tools"),
    ("automotivo", "auto"),
    ("brinquedos", "toys"),
    ("eletronicos", "electronics"),
    ("perfumaria", "perfumery"),
    ("moveis_decoracao", "furniture_decor"),
    ("bebes", "baby"),
    ("papelaria", "stationery")
]

df_cat_trans = pd.DataFrame(categories, columns=["product_category_name", "product_category_name_english"])
df_cat_trans.to_sql("product_category_name_translation", conn, index=False, if_exists="replace")

# 2. Products Table (with some missing category names & unstandardized casing)
n_products = 500
product_ids = [f"prod_{i:04d}" for i in range(1, n_products + 1)]
product_cats = [random.choice([c[0] for c in categories] + [None, "cama_mesa_banho", "BELEZA_SAUDE", "  esporte_lazer  "]) for _ in range(n_products)]
product_prices = np.random.exponential(scale=120, size=n_products) + 10

products_data = []
for pid, cat in zip(product_ids, product_cats):
    weight = random.randint(100, 10000)
    length = random.randint(10, 80)
    height = random.randint(5, 50)
    width = random.randint(10, 60)
    products_data.append((pid, cat, weight, length, height, width))

df_products = pd.DataFrame(products_data, columns=[
    "product_id", "product_category_name", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"
])
df_products.to_sql("products", conn, index=False, if_exists="replace")

# 3. Customers Table (~15,000 customers with ~10,000 unique customer_unique_ids to enable repeat purchase analysis)
n_customers = 15000
unique_customer_ids = [f"unique_cust_{i:05d}" for i in range(1, 10000 + 1)]

states = ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "PE", "DF", "CE", "GO", "ES"]
state_weights = [0.42, 0.14, 0.12, 0.06, 0.05, 0.04, 0.04, 0.03, 0.03, 0.03, 0.02, 0.02]

cities = {
    "SP": ["sao paulo", "campinas", "guarulhos", "santo andre"],
    "RJ": ["rio de janeiro", "niteroi", "duque de caxias"],
    "MG": ["belo horizonte", "uberlandia", "juiz de fora"],
    "RS": ["porto alegre", "caxias do sul"],
    "PR": ["curitiba", "londrina"],
    "SC": ["florianopolis", "joinville"],
    "BA": ["salvador", "feira de santana"],
    "PE": ["recife", "olinda"],
    "DF": ["brasilia"],
    "CE": ["fortaleza"],
    "GO": ["goiania"],
    "ES": ["vitoria"]
}

customers_data = []
for i in range(1, n_customers + 1):
    c_id = f"cust_{i:05d}"
    u_id = random.choice(unique_customer_ids[:8000]) if i > 8000 else unique_customer_ids[i-1]
    st = np.random.choice(states, p=state_weights)
    ct = random.choice(cities[st])
    zip_code = random.randint(1000, 99999)
    customers_data.append((c_id, u_id, zip_code, ct, st))

df_customers = pd.DataFrame(customers_data, columns=[
    "customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"
])
df_customers.to_sql("customers", conn, index=False, if_exists="replace")

# 4. Orders Table (Date range: Jan 2017 - Dec 2018, ~22,000 orders)
start_date = datetime(2017, 1, 1)
end_date = datetime(2018, 12, 31)
time_delta_days = (end_date - start_date).days

n_orders = 22000
order_statuses = ["delivered"] * 20500 + ["shipped"] * 600 + ["canceled"] * 500 + ["invoiced"] * 400

orders_data = []
for i in range(1, n_orders + 1):
    o_id = f"ord_{i:05d}"
    c_id = f"cust_{random.randint(1, n_customers):05d}"
    status = random.choice(order_statuses)
    
    rand_days = random.randint(0, time_delta_days)
    purchase_dt = start_date + timedelta(days=rand_days, hours=random.randint(0, 23), minutes=random.randint(0, 59))
    
    # Date formatting issue demo: mix ISO strings and slashes
    purchase_str = purchase_dt.strftime("%Y-%m-%d %H:%M:%S") if random.random() > 0.02 else purchase_dt.strftime("%Y/%m/%d %H:%M:%S")
    
    approved_dt = purchase_dt + timedelta(hours=random.randint(1, 48))
    approved_str = approved_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    est_delivery_dt = purchase_dt + timedelta(days=random.randint(10, 25))
    est_delivery_str = est_delivery_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    if status == "delivered":
        delay_days = random.randint(-5, 12) if random.random() < 0.15 else random.randint(-8, 0)
        delivered_dt = est_delivery_dt + timedelta(days=delay_days)
        delivered_str = delivered_dt.strftime("%Y-%m-%d %H:%M:%S")
        carrier_dt = purchase_dt + timedelta(days=random.randint(1, 4))
        carrier_str = carrier_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        delivered_str = None
        carrier_str = None if status == "canceled" else (purchase_dt + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        
    orders_data.append((o_id, c_id, status, purchase_str, approved_str, carrier_str, delivered_str, est_delivery_str))

df_orders = pd.DataFrame(orders_data, columns=[
    "order_id", "customer_id", "order_status", "order_purchase_timestamp",
    "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"
])
df_orders.to_sql("orders", conn, index=False, if_exists="replace")

# 5. Order Items Table (~30,000 item rows, including some duplicate rows and invalid negative freight values)
order_items_data = []
sellers = [f"seller_{i:03d}" for i in range(1, 150)]

for o_id in df_orders["order_id"]:
    num_items = random.choices([1, 2, 3, 4], weights=[0.75, 0.15, 0.07, 0.03])[0]
    for item_seq in range(1, num_items + 1):
        p_idx = random.randint(0, n_products - 1)
        p_id = product_ids[p_idx]
        price = round(float(product_prices[p_idx]), 2)
        freight = round(random.uniform(8.5, 45.0), 2)
        
        if random.random() < 0.005:
            freight = -15.00
            
        seller = random.choice(sellers)
        shipping_limit = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
        order_items_data.append((o_id, item_seq, p_id, seller, shipping_limit, price, freight))

# Add 250 duplicate rows
duplicates = random.sample(order_items_data, 250)
order_items_data.extend(duplicates)

df_order_items = pd.DataFrame(order_items_data, columns=[
    "order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value"
])
df_order_items.to_sql("order_items", conn, index=False, if_exists="replace")

# 6. Order Payments Table
payment_types = ["credit_card", "boleto", "voucher", "debit_card"]
payment_weights = [0.74, 0.19, 0.05, 0.02]

payments_data = []
order_totals = df_order_items.groupby("order_id").apply(lambda g: (g["price"] + np.maximum(g["freight_value"], 0)).sum()).to_dict()

for o_id in df_orders["order_id"]:
    tot_val = order_totals.get(o_id, 50.0)
    ptype = np.random.choice(payment_types, p=payment_weights)
    
    if ptype == "credit_card":
        installments = random.choices([1, 2, 3, 4, 5, 6, 10, 12], weights=[0.50, 0.15, 0.12, 0.08, 0.05, 0.05, 0.03, 0.02])[0]
    else:
        installments = 1
        
    payments_data.append((o_id, 1, ptype, installments, round(tot_val, 2)))

df_payments = pd.DataFrame(payments_data, columns=[
    "order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"
])
df_payments.to_sql("order_payments", conn, index=False, if_exists="replace")

# 7. Order Reviews Table
reviews_data = []
for idx, row in df_orders.iterrows():
    o_id = row["order_id"]
    status = row["order_status"]
    deliv_str = row["order_delivered_customer_date"]
    est_str = row["order_estimated_delivery_date"]
    
    r_id = f"rev_{idx+1:05d}"
    
    if status == "delivered" and deliv_str and est_str:
        deliv_dt = datetime.strptime(deliv_str, "%Y-%m-%d %H:%M:%S")
        est_dt = datetime.strptime(est_str, "%Y-%m-%d %H:%M:%S")
        
        if deliv_dt > est_dt:
            score = np.random.choice([1, 2, 3, 4, 5], p=[0.45, 0.25, 0.15, 0.10, 0.05])
        else:
            score = np.random.choice([1, 2, 3, 4, 5], p=[0.02, 0.03, 0.10, 0.25, 0.60])
    else:
        score = np.random.choice([1, 2, 3, 4, 5], p=[0.50, 0.20, 0.15, 0.10, 0.05])
        
    if random.random() < 0.015:
        score = None
        
    crea_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reviews_data.append((r_id, o_id, score, crea_dt))

df_reviews = pd.DataFrame(reviews_data, columns=["review_id", "order_id", "review_score", "review_creation_date"])
df_reviews.to_sql("order_reviews", conn, index=False, if_exists="replace")

# Save CSVs to data/raw/
for name, df in [
    ("products", df_products),
    ("customers", df_customers),
    ("orders", df_orders),
    ("order_items", df_order_items),
    ("order_payments", df_payments),
    ("order_reviews", df_reviews),
    ("category_translation", df_cat_trans)
]:
    df.to_csv(f"data/raw/{name}.csv", index=False)

conn.close()
print("Raw database and CSV files created successfully in db/retail_analytics_raw.db and data/raw/")
