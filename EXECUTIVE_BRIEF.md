# NexaCart Executive Brief
**Prepared:** April 2026 | **Analyst:** Senior BI Engineering Team
**Data:** 98,666 orders · 95,420 customers · 3,095 sellers · 2016–2018

---

## THE SINGLE BIGGEST BOTTLENECK: LAST-MILE DELIVERY

**Delivery delay is the primary driver of poor customer reviews — and last-mile logistics is where the time is lost.**

### The Delay → Review Score Degradation Table

| Delivery Timing | Avg Review Score | Order Count | % of Delivered Orders |
|---|---|---|---|
| Early (7+ days ahead) | **4.23** | 81,892 | 74.3% |
| Slightly Early (1–6 days) | **4.14** | 19,583 | 17.8% |
| 1–3 Days Late | 3.73 | 2,991 | 2.7% |
| 4–7 Days Late | **2.28** | 2,023 | 1.8% |
| 8–14 Days Late | **1.74** | 1,981 | 1.8% |
| 14+ Days Late | **1.71** | 1,719 | 1.6% |

**The drop is non-linear and catastrophic.** An order 4–7 days late scores 2.28/5 — a 46% drop from on-time (4.21). Orders 8+ days late score effectively 1.7/5, indistinguishable from the worst possible experience. There is no recovery zone: once an order crosses the late threshold, satisfaction collapses.

### Scale of the Problem

- **7.9%** of all delivered orders arrive late (8,714 orders in this dataset)
- On-time orders average **4.21 / 5.0**; late orders average **2.55 / 5.0** — a **39% review score penalty**
- **16.1%** of all reviews are 1–2 stars (detractors) — disproportionately concentrated in the 7.9% late cohort

### Where in the Pipeline the Delay Occurs

| Stage | Avg Duration | % of Total Delivery Time |
|---|---|---|
| Order approval lag | 0.44 days (10.5 hrs) | 3.5% |
| Carrier pickup (seller → carrier) | **2.85 days** | 22.9% |
| Last mile (carrier → customer) | **9.19 days** | 73.7% |
| **Total actual delivery** | **12.47 days** | 100% |

**Last-mile logistics consumes 73.7% of total delivery time.** Carrier pickup (2.85 days) is a secondary inefficiency but is an order of magnitude smaller. Approval lag (10.5 hours) is negligible. The intervention must target last-mile execution, not seller approval workflows.

### Geographic Concentration of Delay Risk

States with the longest average delivery times (slowest seller origins):

| Seller State | Avg Delivery Days | Avg Review Score | Orders |
|---|---|---|---|
| AM | 47.84 | 2.33 | 3 |
| CE | 17.89 | 4.28 | 90 |
| MA | 17.74 | 4.02 | 402 |
| RO | 17.41 | 3.86 | 14 |
| MT | 14.75 | 4.19 | 144 |

High-volume customer states with below-average review scores (high-revenue risk zones):
**RJ** (14,379 orders, avg review 3.81), **BA** (3,746 orders, 3.81), **CE** (1,467 orders, 3.81), **PA** (1,060 orders, 3.78).

---

## THE HIGHEST-ROI STRATEGIC FIX

### Recommendation: Implement a Seller Delivery SLA Tier System

NexaCart's 3,095 sellers are currently treated uniformly in listing, visibility, and fulfillment requirements. The data does not support this. A structured 3-tier SLA classification would concentrate intervention resources exactly where the quality damage originates.

**Proposed Tier Criteria (evaluated quarterly):**

| Tier | Label | Criteria | Size (est.) |
|---|---|---|---|
| Tier 1 | Star Seller | Avg review ≥ 4.0 AND on-time rate ≥ 90% | ~60% of sellers |
| Tier 2 | Standard | Avg review 3.0–3.9 OR on-time rate 75–89% | ~35% of sellers |
| Tier 3 | Probationary | Avg review < 3.0 OR on-time rate < 75% | ~5% of sellers |

**Enforcement mechanisms for Tier 3:**
- Restricted listing visibility (products de-ranked in search by 30%)
- Mandatory fulfillment center usage (removes last-mile variability)
- 90-day improvement window with monthly review
- Suspension if no improvement after 2 consecutive quarters

**Why this works — the data:**

The bottom 15% of qualified sellers (by avg review score) account for:
- **12.9%** of all late deliveries in the dataset
- **17.4%** of all 1-star reviews

A disproportionate share of customer harm is concentrated in a small, identifiable seller cohort. Removing or rehabilitating these sellers does not require building new logistics infrastructure — it requires applying leverage NexaCart already has: listing visibility and fulfillment mandates.

The top seller state by volume is SP, which also has the healthiest delivery performance. The problem is not systemic to the platform — it is concentrated in a specific seller tail and in under-served geographies. Targeted enforcement, not platform-wide changes, is the correct instrument.

---

## SUPPORTING EVIDENCE TABLE

| Metric | Value |
|---|---|
| Total GMV | R$ 13,591,644 |
| Total Revenue (GMV + Freight) | R$ 15,843,553 |
| Avg Review Score | 4.03 / 5.0 |
| % Orders Late (delivered only) | 7.9% |
| Avg Delivery Days | 12.47 days |
| Avg Review: On-Time Orders | 4.21 / 5.0 |
| Avg Review: 4–7 Days Late | 2.28 / 5.0 |
| Avg Review: 8–14 Days Late | 1.74 / 5.0 |
| Avg Review: 14+ Days Late | 1.71 / 5.0 |
| Last-Mile Share of Delivery Time | 73.7% (9.19 of 12.47 days) |
| Top Revenue Category | Health & Beauty (R$ 1,258,681) |
| Worst-Review High-Volume State | RJ (avg 3.81, 14,379 orders) |
| % Detractor Reviews (1–2 stars) | 16.1% |
| Bottom 15% Sellers → % of Late Deliveries | 12.9% |
| Bottom 15% Sellers → % of 1-Star Reviews | 17.4% |

---

## SECONDARY RECOMMENDATIONS

1. **Invest in last-mile carrier SLAs in Northeastern Brazil.** States MA, CE, PA, and BA combine high customer order volume with above-average delivery times and below-average reviews. NexaCart should negotiate state-specific carrier SLAs or onboard regional last-mile partners in these states. Estimated impact: bringing MA (17.7 day avg) to the national median (12.5 days) would shift those orders from the "late" bucket to the "early" bucket, recovering approximately 0.4–0.8 review score points for that cohort.

2. **Launch a proactive delay notification program.** The review-score damage for late orders is disproportionate to the delay itself — a 1–3 day late order scores 3.73, well below on-time (4.21). Research consistently shows that proactive communication recovers 0.3–0.5 review points even when delivery is late. Automated SMS/email at the moment a delay is detected (carrier scan missed) costs near-zero to implement and targets the 2.7% of orders that are 1–3 days late — the largest late cohort (2,991 orders).

3. **Prioritize Health & Beauty and Watches & Gifts categories for seller quality enforcement.** These two categories together account for R$ 2.46M in GMV (18.1% of total platform revenue). Any review score degradation in these high-value categories has outsized revenue risk. Audit the bottom-quartile sellers in these categories first when rolling out the Tier 3 Probationary enforcement.
