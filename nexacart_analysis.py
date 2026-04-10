"""
nexacart_analysis.py
NexaCart BI Audit -- Step 2: KPI Analysis & JSON Export
"""

import sys
import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings("ignore")

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

FILE = "nexacart_master.csv"

print("=" * 60)
print("NexaCart BI Audit -- KPI Analysis")
print("=" * 60)

# ---- LOAD --------------------------------------------------------
print("\n[LOAD] Reading nexacart_master.csv...")
df = pd.read_csv(FILE, low_memory=False)
print(f"  Shape: {df.shape[0]:,} rows x {df.shape[1]} cols")

# Restore dtypes
date_cols = [
    "order_purchase_timestamp", "order_approved_at",
    "order_delivered_carrier_date", "order_delivered_customer_date",
    "order_estimated_delivery_date",
]
for c in date_cols:
    if c in df.columns:
        df[c] = pd.to_datetime(df[c], errors="coerce")

for c in ["price", "freight_value", "review_score", "actual_delivery_days",
          "delay_days", "approval_lag_hours", "carrier_pickup_days",
          "last_mile_days", "total_payment_value", "is_late"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Delivered-only subset
delivered = df[df["order_status"] == "delivered"].copy()
print(f"  Delivered orders subset: {delivered.shape[0]:,} rows")

kpis = {}

# ==================================================================
# SECTION 1: REVENUE & VOLUME
# ==================================================================
print("\n[1/5] Computing Revenue & Volume KPIs...")

total_gmv       = float(df["price"].sum())
total_freight   = float(df["freight_value"].sum())
total_revenue   = total_gmv + total_freight
total_orders    = int(df["order_id"].nunique())
total_customers = (int(df["customer_unique_id"].nunique())
                   if "customer_unique_id" in df.columns
                   else int(df["customer_id"].nunique()))
total_sellers   = int(df["seller_id"].nunique())
avg_order_value = float(df.groupby("order_id")["price"].sum().mean())

print(f"  Total GMV:         R$ {total_gmv:,.2f}")
print(f"  Total Freight:     R$ {total_freight:,.2f}")
print(f"  Total Revenue:     R$ {total_revenue:,.2f}")
print(f"  Avg Order Value:   R$ {avg_order_value:,.2f}")
print(f"  Total Orders:      {total_orders:,}")
print(f"  Total Customers:   {total_customers:,}")
print(f"  Total Sellers:     {total_sellers:,}")

monthly_gmv = (
    df.groupby("order_month")["price"]
    .sum()
    .reset_index()
    .sort_values("order_month")
    .rename(columns={"order_month": "month", "price": "gmv"})
)
monthly_gmv_list = monthly_gmv.to_dict(orient="records")

top_cat_gmv = (
    df.groupby("product_category_name_english")["price"]
    .sum()
    .sort_values(ascending=False)
    .head(15)
    .reset_index()
    .rename(columns={"product_category_name_english": "category", "price": "gmv"})
)

top_cat_orders = (
    df.groupby("product_category_name_english")["order_id"]
    .nunique()
    .sort_values(ascending=False)
    .head(15)
    .reset_index()
    .rename(columns={"product_category_name_english": "category", "order_id": "order_count"})
)

kpis["revenue_volume"] = {
    "total_gmv": round(total_gmv, 2),
    "total_freight": round(total_freight, 2),
    "total_revenue": round(total_revenue, 2),
    "avg_order_value": round(avg_order_value, 2),
    "total_orders": total_orders,
    "total_customers": total_customers,
    "total_sellers": total_sellers,
    "monthly_gmv_trend": monthly_gmv_list,
    "top15_categories_by_gmv": top_cat_gmv.to_dict(orient="records"),
    "top15_categories_by_order_count": top_cat_orders.to_dict(orient="records"),
}

# ==================================================================
# SECTION 2: DELIVERY PERFORMANCE
# ==================================================================
print("\n[2/5] Computing Delivery Performance KPIs...")

pct_late = float(
    delivered["is_late"].sum() / delivered["is_late"].notna().sum() * 100
)
avg_delivery_days   = float(delivered["actual_delivery_days"].mean())
avg_delay_days_all  = float(delivered["delay_days"].mean())
avg_approval_lag_h  = float(delivered["approval_lag_hours"].mean())
avg_carrier_pickup  = float(delivered["carrier_pickup_days"].mean())
avg_last_mile       = float(delivered["last_mile_days"].mean())

print(f"  % Orders Late:          {pct_late:.1f}%")
print(f"  Avg Actual Delivery:    {avg_delivery_days:.2f} days")
print(f"  Avg Delay Days:         {avg_delay_days_all:.2f} days")
print(f"  Avg Approval Lag:       {avg_approval_lag_h:.2f} hours")
print(f"  Avg Carrier Pickup:     {avg_carrier_pickup:.2f} days")
print(f"  Avg Last Mile:          {avg_last_mile:.2f} days")

delay_bucket_stats = (
    delivered.groupby("delay_bucket")
    .agg(
        count=("order_id", "count"),
        avg_delay_days=("delay_days", "mean"),
        avg_review_score=("review_score", "mean"),
    )
    .reset_index()
)
delay_bucket_stats["pct"] = (
    delay_bucket_stats["count"] / delay_bucket_stats["count"].sum() * 100
).round(2)
delay_bucket_stats = delay_bucket_stats.round(3)

delivery_by_seller_state = (
    delivered.groupby("seller_state")
    .agg(
        avg_delivery_days=("actual_delivery_days", "mean"),
        avg_delay_days=("delay_days", "mean"),
        avg_review_score=("review_score", "mean"),
        order_count=("order_id", "count"),
    )
    .reset_index()
    .sort_values("avg_delivery_days")
    .round(3)
)

delivery_by_customer_state = (
    delivered.groupby("customer_state")
    .agg(
        avg_delivery_days=("actual_delivery_days", "mean"),
        avg_delay_days=("delay_days", "mean"),
        avg_review_score=("review_score", "mean"),
        order_count=("order_id", "count"),
    )
    .reset_index()
    .sort_values("avg_delivery_days")
    .round(3)
)

kpis["delivery_performance"] = {
    "pct_orders_late": round(pct_late, 2),
    "avg_actual_delivery_days": round(avg_delivery_days, 3),
    "avg_delay_days": round(avg_delay_days_all, 3),
    "avg_approval_lag_hours": round(avg_approval_lag_h, 3),
    "avg_carrier_pickup_days": round(avg_carrier_pickup, 3),
    "avg_last_mile_days": round(avg_last_mile, 3),
    "delay_bucket_breakdown": delay_bucket_stats.to_dict(orient="records"),
    "top10_fastest_seller_states": delivery_by_seller_state.head(10).to_dict(orient="records"),
    "top10_slowest_seller_states": delivery_by_seller_state.tail(10).to_dict(orient="records"),
    "delivery_by_customer_state": delivery_by_customer_state.to_dict(orient="records"),
}

# ==================================================================
# SECTION 3: REVIEW SCORE INTELLIGENCE
# ==================================================================
print("\n[3/5] Computing Review Score KPIs...")

avg_review_overall = float(df["review_score"].mean())
pct_detractors     = float((df["review_score"] <= 2).sum() / df["review_score"].notna().sum() * 100)
pct_passives       = float((df["review_score"] == 3).sum() / df["review_score"].notna().sum() * 100)
pct_promoters      = float((df["review_score"] >= 4).sum() / df["review_score"].notna().sum() * 100)

on_time_review = float(delivered[delivered["is_late"] == 0]["review_score"].mean())
late_review    = float(delivered[delivered["is_late"] == 1]["review_score"].mean())

print(f"  Avg Review Score:       {avg_review_overall:.3f}")
print(f"  % Detractors (1-2):     {pct_detractors:.1f}%")
print(f"  % Promoters (4-5):      {pct_promoters:.1f}%")
print(f"  Avg Review On-Time:     {on_time_review:.3f}")
print(f"  Avg Review Late:        {late_review:.3f}")

# THE MONEY TABLE
review_by_delay = (
    delivered.dropna(subset=["review_score"])
    .groupby("delay_bucket")
    .agg(
        avg_review_score=("review_score", "mean"),
        order_count=("order_id", "count"),
    )
    .reset_index()
    .round(3)
)

print("\n  *** MONEY TABLE: Review Score by Delay Bucket ***")
for _, row in review_by_delay.iterrows():
    print(f"    {row['delay_bucket']:<25} avg={row['avg_review_score']:.3f}  n={row['order_count']:,}")

review_by_category = (
    df.dropna(subset=["review_score"])
    .groupby("product_category_name_english")
    .agg(avg_review_score=("review_score", "mean"), order_count=("order_id", "count"))
    .reset_index()
    .sort_values("avg_review_score")
    .round(3)
)

review_by_seller_state = (
    df.dropna(subset=["review_score"])
    .groupby("seller_state")
    .agg(avg_review_score=("review_score", "mean"), order_count=("order_id", "count"))
    .reset_index().round(3)
)

review_by_customer_state = (
    df.dropna(subset=["review_score"])
    .groupby("customer_state")
    .agg(avg_review_score=("review_score", "mean"), order_count=("order_id", "count"))
    .reset_index().round(3)
)

corr_cols = ["delay_days", "freight_value", "actual_delivery_days", "price", "review_score"]
corr_cols_present = [c for c in corr_cols if c in df.columns]
corr_matrix = df[corr_cols_present].corr().round(4).to_dict()

# Per-bucket late-specific averages
bucket_47 = review_by_delay[review_by_delay["delay_bucket"] == "4-7d Late"]
review_47  = float(bucket_47["avg_review_score"].iloc[0]) if len(bucket_47) > 0 else None
bucket_14p = review_by_delay[review_by_delay["delay_bucket"] == "14+ days Late"]
review_14p = float(bucket_14p["avg_review_score"].iloc[0]) if len(bucket_14p) > 0 else None

kpis["review_score_intelligence"] = {
    "avg_review_overall": round(avg_review_overall, 3),
    "pct_detractors": round(pct_detractors, 2),
    "pct_passives": round(pct_passives, 2),
    "pct_promoters": round(pct_promoters, 2),
    "avg_review_ontime": round(on_time_review, 3),
    "avg_review_late": round(late_review, 3),
    "avg_review_4_7d_late": round(review_47, 3) if review_47 else None,
    "avg_review_14plus_late": round(review_14p, 3) if review_14p else None,
    "review_by_delay_bucket": review_by_delay.to_dict(orient="records"),
    "review_by_category_worst10": review_by_category.head(10).to_dict(orient="records"),
    "review_by_category_best10": review_by_category.tail(10).to_dict(orient="records"),
    "review_by_seller_state": review_by_seller_state.to_dict(orient="records"),
    "review_by_customer_state": review_by_customer_state.to_dict(orient="records"),
    "correlation_matrix": corr_matrix,
}

# ==================================================================
# SECTION 4: SELLER PERFORMANCE
# ==================================================================
print("\n[4/5] Computing Seller Performance KPIs...")

revenue_per_seller = (
    df.groupby("seller_id")
    .agg(
        total_gmv=("price", "sum"),
        order_count=("order_id", "nunique"),
        avg_review_score=("review_score", "mean"),
        avg_delay_days=("delay_days", "mean"),
    )
    .reset_index()
    .sort_values("total_gmv", ascending=False)
    .round(3)
)

qualified_sellers = revenue_per_seller[revenue_per_seller["order_count"] >= 50].copy()
pct_bad_sellers   = float((qualified_sellers["avg_review_score"] < 3.0).sum() / len(qualified_sellers) * 100)
worst_sellers     = qualified_sellers.sort_values("avg_review_score").head(15)
print(f"  Qualified sellers (>=50 orders): {len(qualified_sellers)}")
print(f"  % with avg review < 3.0:         {pct_bad_sellers:.1f}%")

# Bottom 15% sellers impact
bottom_15pct_count  = max(1, int(len(qualified_sellers) * 0.15))
bottom_sellers      = qualified_sellers.nsmallest(bottom_15pct_count, "avg_review_score")
seller_ids_bottom   = set(bottom_sellers["seller_id"])

bottom_del          = delivered[delivered["seller_id"].isin(seller_ids_bottom)]
all_late_count      = int(delivered["is_late"].sum())
bottom_late_count   = int(bottom_del["is_late"].sum())
bottom_pct_late     = float(bottom_late_count / all_late_count * 100) if all_late_count > 0 else 0

all_1star           = int((df["review_score"] == 1).sum())
bottom_1star        = int((df[df["seller_id"].isin(seller_ids_bottom)]["review_score"] == 1).sum())
bottom_pct_1star    = float(bottom_1star / all_1star * 100) if all_1star > 0 else 0

print(f"  Bottom 15% sellers -> {bottom_pct_late:.1f}% of all late deliveries")
print(f"  Bottom 15% sellers -> {bottom_pct_1star:.1f}% of all 1-star reviews")

seller_state_stats = (
    df.groupby("seller_state")
    .agg(
        seller_count=("seller_id", "nunique"),
        total_gmv=("price", "sum"),
        avg_review=("review_score", "mean"),
    )
    .reset_index()
    .sort_values("total_gmv", ascending=False)
    .round(3)
)

kpis["seller_performance"] = {
    "top20_sellers_by_revenue": revenue_per_seller.head(20).to_dict(orient="records"),
    "bottom15_sellers_by_review": worst_sellers.to_dict(orient="records"),
    "pct_sellers_below_3_review": round(pct_bad_sellers, 2),
    "seller_state_concentration": seller_state_stats.to_dict(orient="records"),
    "bottom15pct_sellers_pct_late_deliveries": round(bottom_pct_late, 2),
    "bottom15pct_sellers_pct_1star_reviews": round(bottom_pct_1star, 2),
}

# ==================================================================
# SECTION 5: CUSTOMER GEOGRAPHY
# ==================================================================
print("\n[5/5] Computing Customer Geography KPIs...")

customer_state_stats = (
    df.groupby("customer_state")
    .agg(
        order_count=("order_id", "nunique"),
        total_gmv=("price", "sum"),
        avg_review_score=("review_score", "mean"),
        avg_delivery_days=("actual_delivery_days", "mean"),
    )
    .reset_index()
    .sort_values("order_count", ascending=False)
    .round(3)
)

median_orders  = customer_state_stats["order_count"].median()
high_risk      = customer_state_stats[
    (customer_state_stats["order_count"] > median_orders) &
    (customer_state_stats["avg_review_score"] < avg_review_overall)
].sort_values("avg_review_score")

print(f"  High-risk states (high volume, below-avg review): {list(high_risk['customer_state'])}")

kpis["customer_geography"] = {
    "orders_by_customer_state_top10": customer_state_stats.head(10).to_dict(orient="records"),
    "customer_state_full": customer_state_stats.to_dict(orient="records"),
    "high_risk_states": high_risk.to_dict(orient="records"),
}

# ==================================================================
# SUMMARY PRINT
# ==================================================================
print("\n" + "=" * 60)
print("KPI SUMMARY")
print("=" * 60)
print(f"  Total GMV:                 R$ {total_gmv:>15,.2f}")
print(f"  Total Revenue:             R$ {total_revenue:>15,.2f}")
print(f"  Avg Order Value:           R$ {avg_order_value:>12,.2f}")
print(f"  Total Orders:              {total_orders:>15,}")
print(f"  Total Customers:           {total_customers:>15,}")
print(f"  Total Sellers:             {total_sellers:>15,}")
print(f"  Avg Review Score:          {avg_review_overall:>15.3f} / 5.0")
print(f"  pct Orders Late:           {pct_late:>14.1f}%")
print(f"  Avg Delivery Days:         {avg_delivery_days:>15.2f}")
print(f"  Avg Review On-Time:        {on_time_review:>15.3f}")
print(f"  Avg Review Late:           {late_review:>15.3f}")
print(f"  pct Detractors (1-2):      {pct_detractors:>14.1f}%")

top_cat = top_cat_gmv.iloc[0]
print(f"  Top Revenue Category:      {top_cat['category']} (R$ {top_cat['gmv']:,.0f})")

worst_state_row = review_by_customer_state.sort_values("avg_review_score").iloc[0]
print(f"  Highest Risk State:        {worst_state_row['customer_state']} (avg review {worst_state_row['avg_review_score']:.3f})")
print("=" * 60)

# ==================================================================
# SAVE JSON
# ==================================================================
def convert(obj):
    if isinstance(obj, (np.integer,)):  return int(obj)
    if isinstance(obj, (np.floating,)): return float(obj)
    if isinstance(obj, np.ndarray):     return obj.tolist()
    try:
        if pd.isna(obj): return None
    except Exception:
        pass
    return obj

with open("nexacart_kpis.json", "w", encoding="utf-8") as f:
    json.dump(kpis, f, indent=2, default=convert, ensure_ascii=False)

print("\n[OK] Saved nexacart_kpis.json")
print("\nAnalysis complete.")
