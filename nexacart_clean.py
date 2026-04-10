"""
nexacart_clean.py
NexaCart BI Audit -- Step 1: Data Cleaning & Master CSV Generation
"""

import sys
import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# Force UTF-8 stdout on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

FILE = "NexaCart Data.xlsx"

print("=" * 60)
print("NexaCart BI Audit -- Data Cleaning Pipeline")
print("=" * 60)

# ---- 1. LOAD ALL SHEETS ------------------------------------------
print("\n[1/9] Loading Excel sheets...")
xl = pd.ExcelFile(FILE)
print(f"      Sheets found: {xl.sheet_names}")

orders       = xl.parse("orders_dataset")
order_items  = xl.parse("order_items_dataset")
payments     = xl.parse("order_payments_dataset")
reviews      = xl.parse("order_reviews_dataset")
customers    = xl.parse("customers_dataset")
sellers      = xl.parse("sellers_dataset")
products     = xl.parse("products_dataset")
cat_trans    = xl.parse("product_category_name_translati", header=1)
geolocation  = xl.parse("geolocation_dataset")

print(f"      orders:       {orders.shape}")
print(f"      order_items:  {order_items.shape}")
print(f"      payments:     {payments.shape}")
print(f"      reviews:      {reviews.shape}")
print(f"      customers:    {customers.shape}")
print(f"      sellers:      {sellers.shape}")
print(f"      products:     {products.shape}")
print(f"      cat_trans:    {cat_trans.shape}")
print(f"      geolocation:  {geolocation.shape}")


# ---- HELPER: strip all string columns ----------------------------
def strip_strings(df):
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df


# ---- 2. CLEAN ORDERS ---------------------------------------------
print("\n[2/9] Cleaning orders_dataset...")
orders = strip_strings(orders)

ts_cols = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]
for col in ts_cols:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")

print(f"      Null approved_at:            {orders['order_approved_at'].isna().sum()}")
print(f"      Null delivered_carrier_date: {orders['order_delivered_carrier_date'].isna().sum()}")
print(f"      Null delivered_customer_date:{orders['order_delivered_customer_date'].isna().sum()}")
print("      [OK] Keeping nulls (non-delivered orders) -- NOT imputing")


# ---- 3. FEATURE ENGINEERING --------------------------------------
print("\n[3/9] Engineering computed columns on orders_dataset...")

orders["actual_delivery_days"] = (
    (orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"])
    .dt.total_seconds() / 86400
)

orders["approval_lag_hours"] = (
    (orders["order_approved_at"] - orders["order_purchase_timestamp"])
    .dt.total_seconds() / 3600
)

orders["carrier_pickup_days"] = (
    (orders["order_delivered_carrier_date"] - orders["order_approved_at"])
    .dt.total_seconds() / 86400
)

orders["last_mile_days"] = (
    (orders["order_delivered_customer_date"] - orders["order_delivered_carrier_date"])
    .dt.total_seconds() / 86400
)

orders["delay_days"] = (
    (orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"])
    .dt.total_seconds() / 86400
)

orders["is_late"] = (orders["delay_days"] > 0).astype("Int64")

def assign_delay_bucket(d):
    if pd.isna(d):
        return "Unknown"
    if d <= -7:
        return "Early (7+ days)"
    elif d < 0:
        return "Slightly Early (1-6d)"
    elif d == 0:
        return "On Time"
    elif d <= 3:
        return "1-3d Late"
    elif d <= 7:
        return "4-7d Late"
    elif d <= 14:
        return "8-14d Late"
    else:
        return "14+ days Late"

orders["delay_bucket"] = orders["delay_days"].apply(assign_delay_bucket)
orders["order_month"]     = orders["order_purchase_timestamp"].dt.to_period("M").astype(str)
orders["order_quarter"]   = orders["order_purchase_timestamp"].dt.to_period("Q").astype(str)
orders["order_year"]      = orders["order_purchase_timestamp"].dt.year
orders["order_dayofweek"] = orders["order_purchase_timestamp"].dt.day_name()

print("      [OK] actual_delivery_days, approval_lag_hours, carrier_pickup_days")
print("      [OK] last_mile_days, delay_days, is_late, delay_bucket")
print("      [OK] order_month, order_quarter, order_year, order_dayofweek")


# ---- 4. CLEAN ORDER ITEMS ----------------------------------------
print("\n[4/9] Cleaning order_items_dataset...")
order_items = strip_strings(order_items)
order_items["shipping_limit_date"] = pd.to_datetime(
    order_items["shipping_limit_date"], errors="coerce"
)
order_items["price"]         = pd.to_numeric(order_items["price"],         errors="coerce")
order_items["freight_value"] = pd.to_numeric(order_items["freight_value"], errors="coerce")
print(f"      [OK] {order_items.shape[0]:,} rows -- price & freight cast to float")


# ---- 5. CLEAN REVIEWS --------------------------------------------
print("\n[5/9] Cleaning order_reviews_dataset...")
reviews = strip_strings(reviews)
reviews["review_creation_date"]    = pd.to_datetime(reviews["review_creation_date"],    errors="coerce")
reviews["review_answer_timestamp"] = pd.to_datetime(reviews["review_answer_timestamp"], errors="coerce")
reviews["review_score"] = pd.to_numeric(reviews["review_score"], errors="coerce")

# Keep only first review per order
reviews_dedup = reviews.sort_values("review_creation_date").drop_duplicates(
    subset="order_id", keep="first"
)
print(f"      [OK] Reviews before dedup: {reviews.shape[0]:,} -> after: {reviews_dedup.shape[0]:,}")


# ---- 6. AGGREGATE PAYMENTS ---------------------------------------
print("\n[6/9] Aggregating order_payments_dataset...")
payments = strip_strings(payments)
payments["payment_value"] = pd.to_numeric(payments["payment_value"], errors="coerce")

def mode_first(s):
    m = s.mode()
    return m.iloc[0] if len(m) > 0 else np.nan

payments_agg = (
    payments.groupby("order_id")
    .agg(
        total_payment_value=("payment_value", "sum"),
        payment_installments=("payment_installments", "max"),
        payment_type=("payment_type", mode_first),
    )
    .reset_index()
)
print(f"      [OK] Aggregated to {payments_agg.shape[0]:,} order-level rows")


# ---- 7. CLEAN CUSTOMERS ------------------------------------------
print("\n[7/9] Cleaning customers_dataset...")
customers = strip_strings(customers)
customers["customer_city"]  = customers["customer_city"].str.title()
customers["customer_state"] = customers["customer_state"].str.upper().str.strip()
print(f"      [OK] {customers.shape[0]:,} customers -- city title-cased, state uppercased")


# ---- 8. CLEAN SELLERS --------------------------------------------
print("\n[8/9] Cleaning sellers_dataset...")
sellers = strip_strings(sellers)
sellers["seller_city"]  = sellers["seller_city"].str.title()
sellers["seller_state"] = sellers["seller_state"].str.upper().str.strip()
print(f"      [OK] {sellers.shape[0]:,} sellers -- city title-cased, state uppercased")


# ---- 9. CLEAN PRODUCTS -------------------------------------------
print("\n[9/9] Cleaning products & category translation...")
products = strip_strings(products)

null_cat = products["product_category_name"].isna().sum()
products["product_category_name"] = products["product_category_name"].fillna("unknown")
print(f"      [OK] Filled {null_cat} null category names with 'unknown'")

dim_cols = [
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]
for col in dim_cols:
    products[col] = pd.to_numeric(products[col], errors="coerce")
    null_cnt = products[col].isna().sum()
    if null_cnt > 0:
        med = products[col].median()
        products[col] = products[col].fillna(med)
        print(f"      [OK] Filled {null_cnt} nulls in '{col}' with median {med:.1f}")

cat_trans = strip_strings(cat_trans)
cat_trans.columns = cat_trans.columns.str.strip()
print(f"      [OK] Category translation: {cat_trans.shape[0]} rows")


# ---- DEDUPLICATE GEOLOCATION -------------------------------------
print("\n[+] Deduplicating geolocation_dataset...")
geolocation = strip_strings(geolocation)
# Columns are: geolocation_zip_code_prefix, geolocation_lat, geolocation_lng, geolocation_city, geolocation_state
geolocation.rename(columns={
    "geolocation_zip_code_prefix": "zip_code_prefix",
    "geolocation_state": "geo_state",
}, inplace=True)
geo_dedup = geolocation.drop_duplicates(subset="zip_code_prefix", keep="first").copy()
print(f"      Geolocation before dedup: {geolocation.shape[0]:,} -> after: {geo_dedup.shape[0]:,}")

# Only keep zip + state (drop lat/lng to keep master CSV lean)
geo_state = geo_dedup[["zip_code_prefix", "geo_state"]].copy()


# ---- BUILD MASTER MERGED DATAFRAME --------------------------------
print("\n" + "=" * 60)
print("Building master merged DataFrame...")
print("=" * 60)

# Step 1: Start with order_items
print("  [1] Start with order_items_dataset")
master = order_items.copy()

# Step 2: Merge orders
print("  [2] Merge orders_dataset")
master = master.merge(orders, on="order_id", how="left")

# Step 3: Merge reviews (deduplicated, first review per order)
print("  [3] Merge order_reviews (deduplicated)")
review_cols = ["order_id", "review_score", "review_creation_date", "review_answer_timestamp"]
master = master.merge(reviews_dedup[review_cols], on="order_id", how="left")

# Step 4: Merge aggregated payments
print("  [4] Merge aggregated payments")
master = master.merge(payments_agg, on="order_id", how="left")

# Step 5: Merge customers
print("  [5] Merge customers_dataset")
master = master.merge(customers, on="customer_id", how="left")

# Step 6: Merge sellers
print("  [6] Merge sellers_dataset")
master = master.merge(sellers, on="seller_id", how="left")

# Step 7: Merge products
print("  [7] Merge products_dataset")
master = master.merge(products, on="product_id", how="left")

# Step 8: Merge category translation
print("  [8] Merge product_category_name_translati")
pt_col  = [c for c in cat_trans.columns if "category_name" in c.lower() and "english" not in c.lower()][0]
eng_col = [c for c in cat_trans.columns if "english" in c.lower()][0]
cat_trans_clean = cat_trans[[pt_col, eng_col]].copy()
cat_trans_clean.columns = ["product_category_name", "product_category_name_english"]
master = master.merge(cat_trans_clean, on="product_category_name", how="left")
master["product_category_name_english"] = master["product_category_name_english"].fillna(
    master["product_category_name"]
)

# Step 9: Merge geolocation on customer zip code
print("  [9] Merge geolocation on customer zip_code_prefix")
geo_state_merge = geo_state.rename(columns={"zip_code_prefix": "customer_zip_code_prefix"})
master = master.merge(geo_state_merge, on="customer_zip_code_prefix", how="left")

print(f"\n  [OK] Master DataFrame shape: {master.shape}")
print(f"  [OK] Columns ({len(master.columns)}): {list(master.columns)}")


# ---- EXPORT MASTER CSV -------------------------------------------
print("\n[EXPORT] Saving nexacart_master.csv...")
master.to_csv("nexacart_master.csv", index=False, encoding="utf-8")

size_mb = os.path.getsize("nexacart_master.csv") / (1024 * 1024)
print(f"  [OK] Saved nexacart_master.csv -- {size_mb:.1f} MB, {master.shape[0]:,} rows x {master.shape[1]} cols")

print("\n" + "=" * 60)
print("Data cleaning pipeline COMPLETE.")
print("=" * 60)
