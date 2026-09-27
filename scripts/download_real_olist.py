import os
import urllib.request
import pandas as pd

RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

# Sources for authentic Kaggle Olist Dataset files
urls = {
    "orders": "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets/olist_orders_dataset.csv",
    "customers": "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets/olist_customers_dataset.csv",
    "order_items": "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets/olist_order_items_dataset.csv",
    "products": "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets/olist_products_dataset.csv",
    "order_payments": "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets/olist_order_payments_dataset.csv",
    "order_reviews": "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets/olist_order_reviews_dataset.csv",
    "category_translation": "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets/product_category_name_translation.csv"
}

print("--- Downloading Authentic Kaggle Olist Dataset ---")

for name, url in urls.items():
    dest_path = os.path.join(RAW_DIR, f"{name}.csv")
    print(f"Downloading {name} from {url}...")
    urllib.request.urlretrieve(url, dest_path)
    df = pd.read_csv(dest_path)
    print(f"  -> Saved {dest_path}: {len(df):,} rows, {len(df.columns)} columns.")

print("\nAll authentic Kaggle Olist dataset CSV files downloaded successfully into data/raw/")
