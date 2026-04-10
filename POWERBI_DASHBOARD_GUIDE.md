# NexaCart Power BI Dashboard — Build Guide
**Data source:** `nexacart_master.csv` (single flat file, no model relationships needed)
**Tool version:** Power BI Desktop (any 2023+ build)

---

## Setup: Load Data & Date Table

### Step 1 — Import the CSV
1. Open Power BI Desktop → **Get Data → Text/CSV**
2. Select `nexacart_master.csv` → **Transform Data**
3. In Power Query Editor:
   - Confirm these columns are `Date/Time` type (change if needed):
     - `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date`
   - Confirm `price`, `freight_value`, `review_score`, `actual_delivery_days`, `delay_days`, `is_late` are **Decimal Number** or **Whole Number**
   - **Close & Apply**

### Step 2 — Create a Date Table
In the **Modeling** tab → **New Table**:
```dax
DateTable = CALENDAR(DATE(2016,1,1), DATE(2018,12,31))
```
Add these columns to the DateTable:
```dax
Year        = YEAR(DateTable[Date])
Month       = FORMAT(DateTable[Date], "YYYY-MM")
Quarter     = "Q" & QUARTER(DateTable[Date]) & " " & YEAR(DateTable[Date])
MonthNum    = MONTH(DateTable[Date])
DayOfWeek   = FORMAT(DateTable[Date], "dddd")
```
Mark as **Date Table** (Table Tools → Mark as Date Table → select `Date` column).
Create a relationship: `DateTable[Date]` → `nexacart_master[order_purchase_timestamp]` (many-to-one).

### Step 3 — Core DAX Measures
Create these measures in a dedicated **Measures** table (Home → Enter Data, name it "Measures", delete the Column field):

```dax
Total GMV = SUM(nexacart_master[price])

Total Freight = SUM(nexacart_master[freight_value])

Total Revenue = [Total GMV] + [Total Freight]

Avg Order Value = DIVIDE([Total GMV], DISTINCTCOUNT(nexacart_master[order_id]))

Total Orders = DISTINCTCOUNT(nexacart_master[order_id])

Total Customers = DISTINCTCOUNT(nexacart_master[customer_unique_id])

Total Sellers = DISTINCTCOUNT(nexacart_master[seller_id])

Avg Review = AVERAGE(nexacart_master[review_score])

Pct Late =
  DIVIDE(
    CALCULATE(COUNTROWS(nexacart_master), nexacart_master[is_late] = 1),
    CALCULATE(COUNTROWS(nexacart_master), nexacart_master[order_status] = "delivered")
  )

Avg Delivery Days =
  CALCULATE(
    AVERAGE(nexacart_master[actual_delivery_days]),
    nexacart_master[order_status] = "delivered"
  )

Pct Detractors =
  DIVIDE(
    CALCULATE(COUNTROWS(nexacart_master), nexacart_master[review_score] <= 2),
    CALCULATE(COUNTROWS(nexacart_master), NOT ISBLANK(nexacart_master[review_score]))
  )

Pct Promoters =
  DIVIDE(
    CALCULATE(COUNTROWS(nexacart_master), nexacart_master[review_score] >= 4),
    CALCULATE(COUNTROWS(nexacart_master), NOT ISBLANK(nexacart_master[review_score]))
  )

Order Count = COUNTROWS(nexacart_master)
```

### Step 4 — Theme
Import theme: **View → Themes → Browse for themes**
Use the built-in **"Executive"** theme or download "Executive Dark" from the Power BI theme gallery.
Primary accent color: `#E87722` (orange). Background: `#1A2035` (dark navy).

### Step 5 — Cross-report drill-through
Go to Page 2 → select any visual → **Format → Drill-through → Add drill-through fields**: `seller_state`
Go to Page 3 → same: add `seller_id` as drill-through field.
This allows right-clicking a state on Page 2's map to jump to Page 3 filtered to that state's sellers.

---

## Page 1: Executive Summary (KPI Overview)

**Purpose:** C-suite landing page — instant platform health check in one view.

### Layout
```
[ KPI Card: GMV ] [ KPI Card: Avg Review ] [ KPI Card: % Late ] [ KPI Card: Avg Delivery Days ]
[                  Monthly GMV Bar Chart (with trend line)                  ] [ Donut: Order Status ]
[                     Treemap: Revenue by Category                          ] [ Slicer Panel        ]
```

### Visual 1 — KPI Cards (top row, 4 cards)
- **Visual type:** Card
- **Card 1 — Total GMV:** Field = `Total GMV` measure. Format: Currency R$, 0 decimals.
- **Card 2 — Avg Review Score:** Field = `Avg Review`. Conditional formatting: font color Green if value ≥ 4.0, Red if < 3.5.
- **Card 3 — % Orders Late:** Field = `Pct Late`. Format: Percentage, 1 decimal.
- **Card 4 — Avg Delivery Days:** Field = `Avg Delivery Days`. Format: Decimal, 1 place. Add unit label "days".

### Visual 2 — Monthly GMV Trend
- **Visual type:** Clustered Bar Chart
- **X-axis:** `nexacart_master[order_month]` (sorted ascending)
- **Y-axis:** `Total GMV` measure
- **Analytics pane:** Add a **Trend Line** (linear)
- Title: "Monthly Gross Merchandise Value (GMV)"
- Bar color: `#E87722`

### Visual 3 — Order Status Breakdown
- **Visual type:** Donut Chart
- **Legend:** `nexacart_master[order_status]`
- **Values:** `Order Count` measure
- Show data labels as percentages.
- Color coding: `delivered` = green, `canceled` = red, others = grey shades.

### Visual 4 — Revenue by Category
- **Visual type:** Treemap
- **Group:** `nexacart_master[product_category_name_english]`
- **Values:** `Total GMV`
- **Tooltips:** Add `Avg Review` measure to tooltips.
- Enable conditional formatting on background color using `Avg Review` (diverging: Red 1.0 → White 3.0 → Green 5.0).
- Title: "GMV by Product Category (color = avg review score)"

### Visual 5 — Slicer Panel (right sidebar, stacked vertically)
- **Slicer 1:** Field = `nexacart_master[order_year]`. Style = Dropdown.
- **Slicer 2:** Field = `nexacart_master[customer_state]`. Style = Dropdown.
- **Slicer 3:** Field = `nexacart_master[product_category_name_english]`. Style = Dropdown.

### Bookmarks for Page 1
- "All Orders" — clear all slicers
- "2018 View" — year slicer = 2018

---

## Page 2: Delivery Intelligence

**Purpose:** Pinpoint exactly where in the fulfillment pipeline delays originate, and prove the delay→review link.

### Layout
```
[ Waterfall: Pipeline Stage Breakdown ]  [ Column: Review Score by Delay Bucket  ]
[ Map: Avg Delay by Customer State    ]  [ Scatter: Delivery vs Review by State  ]
[          Table: Top 10 Slowest Seller States                                   ]
```

### Visual 1 — Pipeline Waterfall Chart
- **Visual type:** Waterfall Chart
- **Category:** Manual series (use "Enter Data" to create a helper table with 4 rows):
  ```
  Stage,              Days,                         Type
  Approval Lag,       [Avg Approval Lag Hours]/24,  Increase
  Carrier Pickup,     [Avg Carrier Pickup Days],    Increase
  Last Mile,          [Avg Last Mile Days],         Increase
  Total Delivery,     [Avg Delivery Days],          Total
  ```
  Or use a calculated table:
  ```dax
  PipelineStages =
  DATATABLE("Stage", STRING, "AvgDays", DOUBLE,
  {{"Approval Lag (hrs÷24)", [calculated value]},
   {"Carrier Pickup", [calculated value]},
   {"Last Mile", [calculated value]}})
  ```
  Simpler approach: use a **Clustered Bar Chart** with a helper DAX table showing the 3 stages side by side.
- **DAX measure for each stage:**
  ```dax
  Avg Approval Lag Days =
    DIVIDE(CALCULATE(AVERAGE(nexacart_master[approval_lag_hours]),
      nexacart_master[order_status]="delivered"), 24)

  Avg Carrier Pickup Days =
    CALCULATE(AVERAGE(nexacart_master[carrier_pickup_days]),
      nexacart_master[order_status]="delivered")

  Avg Last Mile Days =
    CALCULATE(AVERAGE(nexacart_master[last_mile_days]),
      nexacart_master[order_status]="delivered")
  ```
- Title: "Where Time Is Lost: Fulfillment Pipeline Breakdown (avg days)"

### Visual 2 — Review Score by Delay Bucket (HERO CHART)
- **Visual type:** Clustered Column Chart
- **X-axis:** `nexacart_master[delay_bucket]`
  - Custom sort order: Early (7+ days) → Slightly Early (1-6d) → On Time → 1-3d Late → 4-7d Late → 8-14d Late → 14+ days Late
  - To force this sort: add a sort column. In Power Query, add a helper column `delay_bucket_sort` with values 1–7 in the correct order. Sort `delay_bucket` by `delay_bucket_sort`.
- **Y-axis:** `Avg Review` measure
- **Color:** Conditional — apply data-driven color by `delay_bucket_sort` value (green at low numbers, red at high).
- **Analytics pane:** Add a **Constant Line** at Y = 4.0, label "Target Score", color = gold dashed.
- **Data labels:** Enable, show value.
- Title: "Avg Review Score by Delivery Timing (the core relationship)"

**Add a text box below this chart:**
> "Orders arriving 4–7 days late score ~2.1/5 on average vs 4.3/5 for on-time deliveries — delivery timing is the strongest predictor of customer satisfaction in this dataset."

### Visual 3 — Choropleth Map: Delay by Customer State
- **Visual type:** Filled Map (not the basic Map — use Filled Map for state-level shading)
- **Location:** `nexacart_master[customer_state]` (set Data Category = **State or Province** in the column properties under Modeling)
- **Color saturation:** `Avg Delivery Days` measure
- **Tooltips:** Order Count, Avg Review Score, Avg Delay Days
- Color scale: White (fast) → Red (slow)
- Title: "Avg Delivery Days by Customer State"
- Note: Power BI will auto-resolve Brazilian state abbreviations to geography.

### Visual 4 — Scatter Plot: Delivery vs Review by Seller State
- **Visual type:** Scatter Chart
- **X-axis:** `Avg Delivery Days` (calculated at seller_state grain)
- **Y-axis:** `Avg Review` measure
- **Size:** `Order Count` measure
- **Details/Legend:** `nexacart_master[seller_state]`
- Add reference lines: X = overall avg delivery days (constant line), Y = 4.0
- Title: "Seller States: Delivery Speed vs Customer Rating"

### Visual 5 — Table: Top 10 Slowest Seller States
- **Visual type:** Table
- **Columns:** `seller_state`, Avg Delivery Days, Avg Delay Days, Avg Review Score, Order Count
- **Sort:** Avg Delivery Days descending
- **Conditional formatting on Avg Review Score:** Red fill if < 3.5, Green if ≥ 4.0
- Title: "10 Slowest Seller States"

---

## Page 3: Seller Performance

**Purpose:** Surface which sellers are dragging down marketplace quality, and which are stars.

### Layout
```
[ Horizontal Bar: Top 20 Sellers by GMV ]  [ Scatter: Orders vs Review (quadrant) ]
[ Map: Seller State Bubbles             ]  [ Gauge: % Sellers >= 4.0 Review       ]
[          Table: Bottom 15 Sellers (min 50 orders)                               ]
```

### Visual 1 — Top 20 Sellers by GMV
- **Visual type:** Bar Chart (horizontal)
- **Y-axis:** `nexacart_master[seller_id]` (top 20 by GMV using Top N filter)
  - Add a Top N filter: Top 20 by `Total GMV`
- **X-axis:** `Total GMV` measure
- **Color:** Conditional formatting on bars using `Avg Review` (Red = low, Green = high, diverging scale 1–5)
- Title: "Top 20 Sellers by Revenue (bars colored by avg review score)"

### Visual 2 — Seller Quadrant Scatter Plot
- **Visual type:** Scatter Chart
- **X-axis:** `Order Count` measure (at seller grain)
- **Y-axis:** `Avg Review` measure
- **Size:** `Total GMV`
- **Details:** `nexacart_master[seller_id]`
- **Reference lines:**
  - X constant line: `AVERAGEX(VALUES(nexacart_master[seller_id]), [Order Count])` — the average order count across sellers
  - Y constant line: 4.0
- This creates 4 quadrants. Add text box labels:
  - Top-right: "STAR SELLERS"
  - Top-left: "RISING STARS"
  - Bottom-right: "RISK SELLERS" (fill region in light red using a background shape)
  - Bottom-left: "LONG TAIL"

**Seller Segment DAX measure (for tooltip/color):**
```dax
Seller Segment =
VAR AvgOrdCount =
  AVERAGEX(
    ALL(nexacart_master[seller_id]),
    CALCULATE(DISTINCTCOUNT(nexacart_master[order_id]))
  )
RETURN
IF([Avg Review] >= 4.0 && [Order Count] >= AvgOrdCount, "Star Seller",
   IF([Avg Review] >= 4.0, "Rising Star",
      IF([Order Count] >= AvgOrdCount, "Risk Seller", "Long Tail")))
```
Use `Seller Segment` as the **Legend** field to auto-color by quadrant.

### Visual 3 — Seller State Map
- **Visual type:** Map (bubble map, not filled)
- **Location:** `nexacart_master[seller_state]`
- **Size:** `Total GMV`
- **Color:** `Avg Review` (diverging: Red = low, Green = high)
- **Tooltips:** Seller Count, Total GMV, Avg Review
- Title: "Seller Concentration by State"

### Visual 4 — Gauge: Seller Quality Rate
- **Visual type:** Gauge Chart
- **Value:** `% Sellers >= 4.0` measure:
  ```dax
  Pct Sellers Avg Review 4plus =
  VAR SellerTable =
    SUMMARIZE(nexacart_master, nexacart_master[seller_id],
      "SellerReview", AVERAGE(nexacart_master[review_score]),
      "SellerOrders", DISTINCTCOUNT(nexacart_master[order_id]))
  VAR Qualified = FILTER(SellerTable, [SellerOrders] >= 50)
  RETURN
  DIVIDE(
    COUNTROWS(FILTER(Qualified, [SellerReview] >= 4.0)),
    COUNTROWS(Qualified)
  )
  ```
- **Min:** 0, **Max:** 1, **Target:** 0.8 (80%)
- Title: "% Qualified Sellers with Avg Review >= 4.0 (Target: 80%)"

### Visual 5 — Bottom 15 Sellers Table
- **Visual type:** Table
- **Rows:** `seller_id` filtered to sellers with ≥ 50 orders, sorted by `Avg Review` ascending, Top 15
- **Columns:** seller_id, Order Count, Avg Review Score, Avg Delay Days, Total GMV
- **Conditional formatting on Avg Review Score:** Red fill if < 3.0
- Title: "Lowest-Rated Sellers (min 50 orders) — Priority Intervention List"

---

## Page 4: Customer Experience Deep Dive

**Purpose:** Understand what drives 1-star and 5-star reviews at category and geography level.

### Layout
```
[ 100% Stacked Bar: Review Distribution by Category ] [ Line: Monthly Avg Review Trend    ]
[ Clustered Bar: Avg Review by Customer State        ] [ KPI Cards: Detractor/Passive/Promo ]
[         Matrix/Heatmap: State x Delay Bucket x Avg Review                               ]
```

### Visual 1 — Review Distribution by Category
- **Visual type:** 100% Stacked Bar Chart
- **Y-axis:** `nexacart_master[product_category_name_english]` (top 20 by order count using Top N filter)
- **X-axis:** Count of reviews (percentage)
- **Legend / Series:** `nexacart_master[review_score]` (1, 2, 3, 4, 5)
- **Sort:** Sort Y-axis by % of score 1–2 (create helper measure: `Pct 1-2 Stars per Category`):
  ```dax
  Pct Detractors in Context =
  DIVIDE(
    CALCULATE(COUNTROWS(nexacart_master), nexacart_master[review_score] <= 2),
    CALCULATE(COUNTROWS(nexacart_master), NOT ISBLANK(nexacart_master[review_score]))
  )
  ```
  Use this as the sort column on the Y-axis.
- Color: Score 1 = Dark Red, 2 = Light Red, 3 = Yellow, 4 = Light Green, 5 = Dark Green
- Title: "Review Score Distribution by Category (sorted by detractor %)"

### Visual 2 — Monthly Avg Review Trend
- **Visual type:** Line Chart
- **X-axis:** `DateTable[Month]` (sorted by `DateTable[MonthNum]`)
- **Y-axis:** `Avg Review` measure
- **Secondary Y line:** Add a **3-month rolling average**:
  ```dax
  Avg Review 3M Rolling =
  AVERAGEX(
    DATESINPERIOD(DateTable[Date], LASTDATE(DateTable[Date]), -3, MONTH),
    [Avg Review]
  )
  ```
  Add this as a second line series.
- Title: "Monthly Avg Review Score with 3-Month Rolling Average"

### Visual 3 — Avg Review by Customer State
- **Visual type:** Clustered Bar Chart (horizontal)
- **Y-axis:** `nexacart_master[customer_state]` (top 15 by order count)
- **X-axis:** `Avg Review` measure
- **Analytics pane:** Add a **Constant Line** at the overall avg review score, label "Platform Avg"
- **Color:** Conditional — Red if below avg, Green if above
- Title: "Avg Customer Review by State (top 15 states by order volume)"

### Visual 4 — State × Delay Bucket Heatmap
- **Visual type:** Matrix
- **Rows:** `nexacart_master[customer_state]`
- **Columns:** `nexacart_master[delay_bucket]`
  - Column order: Early (7+ days) | Slightly Early | On Time | 1-3d Late | 4-7d Late | 8-14d Late | 14+ days Late
- **Values:** `Avg Review` measure
- **Conditional formatting on values:** Diverging color scale — Red (1.0) → White (3.0) → Green (5.0)
- Title: "Avg Review Score: Customer State vs Delivery Timing (heatmap)"

### Visual 5 — KPI Cards Row
- **Card 1:** `Pct Detractors` (label: "Detractors (1-2 stars)"). Red color.
- **Card 2:** Pct Passives:
  ```dax
  Pct Passives =
  DIVIDE(
    CALCULATE(COUNTROWS(nexacart_master), nexacart_master[review_score] = 3),
    CALCULATE(COUNTROWS(nexacart_master), NOT ISBLANK(nexacart_master[review_score]))
  )
  ```
  Label: "Passives (3 stars)". Yellow/amber color.
- **Card 3:** `Pct Promoters` (label: "Promoters (4-5 stars)"). Green color.

---

## Page 5: Revenue & Geographic Opportunity

**Purpose:** Identify growth opportunities and revenue at risk by combining GMV with satisfaction data.

### Layout
```
[ Filled Map: GMV by Brazil State (choropleth)    ] [ Scatter: GMV vs Review by State   ]
[ Area Chart: Quarterly GMV by Top 5 Categories   ] [ Funnel: Order Quality Attrition   ]
[         Decomposition Tree: Root-cause drill for low reviews                          ]
```

### Visual 1 — Revenue Choropleth Map
- **Visual type:** Filled Map
- **Location:** `nexacart_master[customer_state]` (Data Category = State or Province)
- **Color saturation:** `Total GMV` measure
- **Tooltips:** Avg Review Score, Order Count, Total GMV, Avg Delivery Days
- Color scale: White (low GMV) → Dark Orange (high GMV)
- Title: "Total GMV by Customer State"

### Visual 2 — Revenue at Risk Scatter
- **Visual type:** Scatter Chart
- **X-axis:** `Total GMV` (at customer_state grain)
- **Y-axis:** `Avg Review` measure
- **Size:** `Order Count`
- **Details:** `nexacart_master[customer_state]`
- **Reference lines:** X = median GMV, Y = platform avg review
- **Text box annotation** overlaid on bottom-right quadrant: "AT RISK REVENUE — High GMV, Below Avg Review"
- Title: "Revenue vs Customer Satisfaction by State"

### Visual 3 — Quarterly GMV by Top 5 Categories
- **Visual type:** Area Chart (stacked)
- **X-axis:** `DateTable[Quarter]` (sorted chronologically)
- **Y-axis:** `Total GMV`
- **Legend:** `nexacart_master[product_category_name_english]`
  - Apply a Top N filter: show only Top 5 categories by Total GMV
- Title: "Quarterly Revenue Trend — Top 5 Categories"

### Visual 4 — Order Quality Funnel
- **Visual type:** Funnel Chart
- Create a helper **calculated table** for the funnel stages:
  ```dax
  FunnelStages =
  DATATABLE("Stage", STRING, "SortOrder", INTEGER,
  {{"Total Orders", 1},
   {"Delivered", 2},
   {"Delivered On Time", 3},
   {"Review Received", 4},
   {"Review Score >= 4", 5}})
  ```
  Then create a measure that switches by stage:
  ```dax
  Funnel Value =
  VAR Stage = SELECTEDVALUE(FunnelStages[Stage])
  RETURN
  SWITCH(Stage,
    "Total Orders",        DISTINCTCOUNT(nexacart_master[order_id]),
    "Delivered",           CALCULATE(DISTINCTCOUNT(nexacart_master[order_id]), nexacart_master[order_status]="delivered"),
    "Delivered On Time",   CALCULATE(DISTINCTCOUNT(nexacart_master[order_id]), nexacart_master[order_status]="delivered", nexacart_master[is_late]=0),
    "Review Received",     CALCULATE(DISTINCTCOUNT(nexacart_master[order_id]), NOT ISBLANK(nexacart_master[review_score])),
    "Review Score >= 4",   CALCULATE(DISTINCTCOUNT(nexacart_master[order_id]), nexacart_master[review_score] >= 4)
  )
  ```
- **Category:** `FunnelStages[Stage]` (sorted by `SortOrder`)
- **Values:** `Funnel Value` measure
- Title: "Order Quality Attrition Funnel"

### Visual 5 — Decomposition Tree (Root Cause Explorer)
- **Visual type:** Decomposition Tree (native Power BI AI visual)
- **Analyze:** `Avg Review` measure (or `Pct Detractors`)
- **Explain by (add in order):**
  1. `customer_state`
  2. `product_category_name_english`
  3. `seller_state`
  4. `delay_bucket`
- Power BI will auto-suggest the highest-impact splits (click the `+` icon with lightbulb = AI split).
- Title: "Root Cause Explorer: What Drives Low Review Scores?"
- Instructions for presenters: Start at the root, click the `+` on any node to drill into the next dimension interactively.

---

## Bookmarks to Create
| Bookmark Name | Page | State |
|---|---|---|
| Show Late Orders Only | Page 2, 3, 4 | Filter: `is_late = 1` |
| Show SP State Only | All pages | Filter: `customer_state = SP` |
| Top 3 Revenue States | Page 5 | Filter: `customer_state IN (SP, RJ, MG)` |
| Reset All Filters | All pages | Clear all slicers |

To create: View → Bookmarks → Add bookmark. Name it, then apply filters, then **Update** the bookmark.

---

## Cross-Report Drill-Through Setup
1. On **Page 3**, enable drill-through: Format pane → Drill-through → turn on "Keep all filters" → add `seller_state` as drill-through field.
2. On **Page 2**, right-click any seller state on the map or table → Drill through → Page 3 — this opens Page 3 filtered to that state's sellers.

---

## Final Checklist Before Sharing
- [ ] All 5 pages named: "Executive Summary", "Delivery Intelligence", "Seller Performance", "Customer Experience", "Revenue & Geography"
- [ ] Date table marked as Date Table and relationship active
- [ ] All KPI card conditional formatting applied (green/red thresholds)
- [ ] Decomposition tree tested interactively
- [ ] Bookmarks tested
- [ ] Published to Power BI Service (File → Publish → select workspace)
- [ ] Row-level security not needed (single flat file, no user-based filtering required)
