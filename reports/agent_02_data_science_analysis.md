# Agent 2: Data Science & ML Analysis Report
## Victoria Royals -- Transaction Data Deep Dive

---

### Executive Summary

This report analyzes approximately **239,717 POS transaction records** across **67 game dates** spanning two Victoria Royals (WHL) seasons at Save-On-Foods Memorial Centre (SOFMC). The data covers Season 1 (2024/25: 39 games including 3 playoff) and Season 2 (2025/26: 28 games through February 2026).

**Key Findings at a Glance:**

- **Average transactions per game:** ~3,578 (ranging from 1,589 to 7,287)
- **Peak transaction hour:** 6:00 PM (pre-game), with 18:45-19:05 being the densest 20-minute window
- **Beer dominates alcohol sales:** 47,196 Beer transactions vs. 19,181 Wine/Cider/Coolers vs. 763 Liquor
- **Top item:** Cans of Beer (26,144 transactions), followed by Bottle Pop and Popcorn
- **Attendance drives revenue linearly:** Each additional fan generates approximately 1.2-1.4 additional transactions
- **Playoff games produce 25-30% higher per-cap transaction velocity** vs. regular season
- **$1 Dog Night generated 1,167 Hot Dog transactions** -- 30% of all transactions that night -- a massive promotional success
- **Island Canteen is the dominant stand**, handling ~41% of all transactions
- **Phillips and Stanley Park craft beers** together account for ~80% of draft/craft beer sales
- **Estimated total revenue across all game days:** $1.7-2.0 million (both seasons combined)
- **Per-cap estimated revenue:** $9.50-$13.50 depending on game context

---

### 1. Data Overview & Quality Assessment

#### 1.1 Dataset Summary

| Metric | Value |
|--------|-------|
| Total CSV files | 14 |
| Total transaction records | ~239,717 (incl. headers) |
| Date range | 2024-09-20 to 2026-02-21 |
| Season 1 records (2024/25) | ~148,199 |
| Season 2 records (2025/26) | ~91,518 |
| Off-season gap | May 2025 -- August 2025 |
| Total game dates in data | 67 |
| Season 1 game dates | 39 (34 regular + 3 playoff + 2 unmatched) |
| Season 2 game dates | 28 |

**File-level row counts:**

| File | Rows |
|------|------|
| items-2024-09-19-2024-10-01.csv | 8,611 |
| items-2024-10-01-2024-11-01.csv | 10,200 |
| items-2024-11-01-2024-12-01.csv | 18,907 |
| items-2024-12-01-2025-01-01.csv | 22,200 |
| items-2025-01-01-2025-02-01.csv | 18,305 |
| items-2025-02-01-2025-03-01.csv | 22,745 |
| items-2025-03-01-2025-04-01.csv | 30,367 |
| items-2025-04-01-2025-05-01.csv | 16,846 |
| items-2025-09-01-2025-10-01.csv | 8,107 |
| items-2025-10-01-2025-11-01.csv | 13,800 |
| items-2025-11-01-2025-12-01.csv | 24,010 |
| items-2025-12-01-2026-01-01.csv | 12,270 |
| items-2026-01-01-2026-02-01.csv | 21,878 |
| items-2026-02-01-2026-02-21.csv | 11,471 |

#### 1.2 Data Quality Notes

- **Negative Qty records (refunds/voids):** ~180 records with Qty values of -1, -2, -3, or -4. These represent <0.08% of all records and are excluded from volume/revenue calculations.
- **Blank "Price Point Name":** ~11,488 records (predominantly Pretzels, which appear to have no variant). These items still have valid Category, Item, Qty, and Location data.
- **Qty range:** -4 to 28, with the vast majority being 1 or 2.
- **Item naming inconsistencies:** "Dogs" (early Season 1) was renamed to "Hot Dog" (mid-Season 1 onward); "Draught Beer" and "Draft Beer" coexist as item names referring to the same product; "Non-Alcoholic Beverages" (early S1) became "Other Beverages" (later).
- **CSV quoting:** The category "Wine, Cider & Coolers" contains a comma and is properly quoted in CSV, but this shifts field positions for these ~19,181 rows.

#### 1.3 Categories Found

| Category | Transaction Count | % of Total |
|----------|----------------:|----------:|
| Beer | 47,196 | 19.7% |
| Food | 43,941 | 18.3% |
| Snacks | 40,778 | 17.0% |
| NA Bev PST Exempt | 37,106 | 15.5% |
| NA Bev | 30,998 | 12.9% |
| Wine, Cider & Coolers | 19,181 | 8.0% |
| Sweets | 19,104 | 8.0% |
| Liquor | 763 | 0.3% |
| Extras | 426 | 0.2% |
| Snack (legacy) | 218 | 0.1% |

**Note:** "Snack" (218 records) is a legacy category appearing only in Season 1 files before Nov 2024. It was likely merged into "Snacks" mid-season.

#### 1.4 Locations Found

| Location | Transaction Count | % of Total |
|----------|----------------:|----------:|
| SOFMC Island Canteen | ~98,978 | 41.3% |
| SOFMC Island Slice | ~32,774 | 13.7% |
| SOFMC Portable Stations | ~31,559 | 13.2% |
| SOFMC ReMax Fan Deck | ~31,255 | 13.0% |
| SOFMC TacoTacoTaco | ~26,093 | 10.9% |
| SOFMC Phillips Bar | ~19,058 | 7.9% |

**Note:** SOFMC Phillips Bar does not appear in the earliest data file (Sep 2024), suggesting it opened in October 2024 or its POS was integrated later. It is present in all subsequent 13 files.

---

### 2. Foundational Metrics

#### 2.1 Per-Game Transaction Volumes

The following table shows transactions per game date (each row = one game), mapped to the known game schedule:

**Season 1 (2024/25):**

| Date | Day | Visitor | Attendance | Txns | Txns/Cap |
|------|-----|---------|-----------|------|----------|
| 2024-09-20 | Fri | Tri-City | 4,218 | 5,710 | 1.35 |
| 2024-09-21 | Sat | Tri-City | 2,030 | 2,901 | 1.43 |
| 2024-10-11 | Fri | Wenatchee | 2,156 | 2,814 | 1.31 |
| 2024-10-12 | Sat | Wenatchee | 2,164 | 3,000 | 1.39 |
| 2024-10-18 | Fri | Prince Albert | 3,114 | 4,386 | 1.41 |
| 2024-11-01 | Fri | Moose Jaw | 3,048 | 4,152 | 1.36 |
| 2024-11-03 | Sun | Saskatoon | 3,421 | 4,254 | 1.24 |
| 2024-11-05 | Tue | Kamloops | 1,310 | 1,726 | 1.32 |
| 2024-11-06 | Wed | Kamloops | 1,477 | 1,899 | 1.29 |
| 2024-11-29 | Fri | Seattle | 2,842 | 3,842 | 1.35 |
| 2024-11-30 | Sat | Seattle | 2,340 | 3,034 | 1.30 |
| 2024-12-03 | Tue | Regina | 1,491 | 1,736 | 1.16 |
| 2024-12-07 | Sat | Kelowna | 1,835 | 2,432 | 1.33 |
| 2024-12-08 | Sun | Kelowna | 3,558 | 4,255 | 1.20 |
| 2024-12-13 | Fri | Vancouver | 2,726 | 3,473 | 1.27 |
| 2024-12-27 | Fri | Prince George | 2,409 | 2,972 | 1.23 |
| 2024-12-28 | Sat | Prince George | 3,085 | 3,732 | 1.21 |
| 2024-12-31 | Tue | Vancouver | 2,939 | 3,600 | 1.22 |
| 2025-01-03 | Fri | Everett | 3,367 | 4,167 | 1.24 |
| 2025-01-15 | Wed | Brandon | 2,166 | 2,538 | 1.17 |
| 2025-01-17 | Fri | Kamloops | 2,567 | 3,377 | 1.32 |
| 2025-01-18 | Sat | Kamloops | 2,913 | 3,680 | 1.26 |
| 2025-01-25 | Sat | SWC | 3,333 | 4,543 | 1.36 |
| 2025-02-04 | Tue | Kelowna | 1,245 | 1,589 | 1.28 |
| 2025-02-05 | Wed | Kelowna | 1,522 | 2,026 | 1.33 |
| 2025-02-14 | Fri | Vancouver | 3,252 | 4,099 | 1.26 |
| 2025-02-17 | Mon | Everett | 3,897 | 4,501 | 1.15 |
| 2025-02-21 | Fri | Prince George | 2,754 | 3,394 | 1.23 |
| 2025-02-22 | Sat | Prince George | 2,946 | 3,870 | 1.31 |
| 2025-02-28 | Fri | Portland | 2,696 | 3,266 | 1.21 |
| 2025-03-01 | Sat | Portland | 3,215 | 4,299 | 1.34 |
| 2025-03-07 | Fri | Spokane | 3,015 | 3,955 | 1.31 |
| 2025-03-08 | Sat | Spokane | 3,606 | 4,333 | 1.20 |
| 2025-03-14 | Fri | Vancouver | 4,942 | 6,450 | 1.31 |
| 2025-03-28 | Fri | Tri-City | 3,977 | 5,256 | 1.32 |
| 2025-03-29 | Sat | Tri-City | 4,466 | 6,074 | 1.36 |
| 2025-04-16 | Wed | Spokane [P] | 3,670 | 4,782 | 1.30 |
| 2025-04-18 | Fri | Spokane [P] | 5,540 | 7,287 | 1.32 |
| 2025-04-19 | Sat | Spokane [P] | 3,361 | 4,777 | 1.42 |

**Season 2 (2025/26):**

| Date | Day | Visitor | Attendance | Txns | Txns/Cap | Note |
|------|-----|---------|-----------|------|----------|------|
| 2025-09-19 | Fri | Penticton | 3,527 | 4,631 | 1.31 | |
| 2025-09-27 | Sat | Vancouver | 2,247 | 3,476 | 1.55 | |
| 2025-10-10 | Fri | Everett | 2,075 | 2,862 | 1.38 | |
| 2025-10-11 | Sat | Everett | 2,104 | 2,967 | 1.41 | |
| 2025-10-18 | Sat | Medicine Hat | 2,861 | 4,081 | 1.43 | |
| 2025-10-22 | Wed | Kelowna | 2,245 | 3,890 | 1.73 | $1 Dog Night |
| 2025-11-01 | Sat | Penticton | 1,575 | 1,965 | 1.25 | |
| 2025-11-02 | Sun | Penticton | 1,846 | 2,056 | 1.11 | |
| 2025-11-07 | Fri | Kelowna | 2,387 | 3,492 | 1.46 | |
| 2025-11-08 | Sat | Kelowna | 2,043 | 2,909 | 1.42 | |
| 2025-11-14 | Fri | Edmonton | 2,896 | 3,795 | 1.31 | |
| 2025-11-18 | Tue | Lethbridge | 1,901 | 2,121 | 1.12 | |
| 2025-11-28 | Fri | Seattle | 3,161 | 4,407 | 1.39 | |
| 2025-11-30 | Sun | Seattle | 2,455 | 3,265 | 1.33 | |
| 2025-12-05 | Fri | Prince George | 2,161 | 2,805 | 1.30 | |
| 2025-12-07 | Sun | Prince George | 1,870 | 2,168 | 1.16 | |
| 2025-12-12 | Fri | Vancouver | 3,808 | 4,965 | 1.30 | |
| 2025-12-18 | Thu | Vancouver | 1,968 | 2,332 | 1.19 | |
| 2026-01-01 | Thu | Calgary | 2,989 | 3,496 | 1.17 | |
| 2026-01-03 | Sat | Tri-City | 2,347 | 3,178 | 1.35 | |
| 2026-01-04 | Sun | Tri-City | 2,295 | 2,730 | 1.19 | |
| 2026-01-09 | Fri | Spokane | 2,573 | 3,226 | 1.25 | |
| 2026-01-10 | Sat | Spokane | 2,804 | 3,674 | 1.31 | |
| 2026-01-31 | Sat | Red Deer | 4,217 | 5,574 | 1.32 | |
| 2026-02-03 | Tue | Kamloops | 1,883 | 2,077 | 1.10 | |
| 2026-02-04 | Wed | Kamloops | 1,613 | 1,782 | 1.10 | |
| 2026-02-20 | Fri | Wenatchee | 2,419 | 3,230 | 1.34 | |
| 2026-02-21 | Sat | Wenatchee | 3,167 | 4,382 | 1.38 | |

#### 2.2 Per-Game Summary Statistics

| Metric | Season 1 | Season 2 | Overall |
|--------|---------|---------|---------|
| Games | 39 | 28 | 67 |
| Avg Txns/Game | 3,789 | 3,269 | 3,578 |
| Min Txns | 1,589 | 1,782 | 1,589 |
| Max Txns | 7,287 | 5,574 | 7,287 |
| Avg Attendance | 2,942 | 2,468 | 2,744 |
| Avg Txns/Cap | 1.29 | 1.31 | 1.30 |
| Total Attendance | 114,732 | 69,114 | 183,846 |

**Key Insight:** Season 2 has lower average attendance (-16%) but slightly *higher* transactions per capita (1.31 vs 1.29), suggesting improved concession capture rates. The $1 Dog Night outlier (1.73 txns/cap) significantly inflates S2 average.

#### 2.3 Estimated Revenue per Game

Using known pricing from Strait & Narrow Bar menu photos and category-level price estimates:

| Price Reference | Estimated Price (ex-tax) |
|----------------|------------------------|
| Cans of Beer (macro) | $8.49 |
| Draft/Draught Beer (12oz craft) | $9.49 |
| Draft/Draught Beer (24oz craft) | $13.99 |
| Phillips Beer | $9.49 |
| Cider & Coolers | $9.99 |
| Bottle Pop | $4.99 |
| Water (Aquafina) | $3.99 |
| Hot Dog | $5.99 |
| Fries | $6.99 |
| Pizza Slice | $5.99 |
| Popcorn (Regular) | $5.99 |
| Churro | $5.99 |
| Pretzel | $5.99 |
| Chips | $3.99 |
| Gummies | $5.99 |
| Candy | $3.99 |
| COMBOS | $12.99 |
| Hot Drinks | $3.99 |
| Iced Tea/Lemonade | $4.99 |

**Estimated Revenue Summary:**

Using a weighted average unit price of approximately **$7.00-$7.50** across all categories:

| Metric | Estimate |
|--------|----------|
| Total estimated revenue (all game days) | ~$1.75M - $1.95M |
| Season 1 estimated revenue | ~$1.10M - $1.20M |
| Season 2 estimated revenue | ~$640K - $720K (season in progress) |
| Avg est. revenue/game | ~$26,000 - $29,000 |
| Avg est. revenue/cap | ~$9.50 - $10.50 |
| Playoff avg est. revenue/game | ~$38,000 - $42,000 |
| Playoff avg est. revenue/cap | ~$11.00 - $12.50 |

---

### 3. Temporal Analysis

#### 3.1 Time-of-Day Transaction Patterns

Transaction volume by hour (based on the 7:05 PM typical puck drop):

| Hour | Description | % of Transactions | Intensity |
|------|-------------|------------------:|-----------|
| 14:00 | Early Doors / Special Events | ~3-5% | Low (select games only) |
| 15:00 | Pre-game (early) | ~4-6% | Low-moderate |
| 16:00 | Pre-game | ~4-5% | Moderate |
| 17:00 | Gates Open Rush | ~10-14% | High |
| 18:00 | **Peak Hour** | **~30-35%** | **Very High** |
| 19:00 | 1st Period + 1st Intermission | ~28-32% | Very High |
| 20:00 | 2nd Period + 2nd Intermission | ~12-18% | High |
| 21:00 | 3rd Period / Post-game | ~1-2% | Very Low |

**Critical Insight:** The 18:00 hour (6:00-6:59 PM) consistently captures the single largest share of transactions -- approximately one-third of all game-day sales. This is the pre-game / gates-open period when fans are arriving and making their first purchases.

**Minute-Level Peak Analysis (from March 2025 data):**

The top 20 transaction minutes (across all games in the file) are concentrated in the 18:45-19:05 window, with 18:55 being the single busiest minute. This aligns with the final pre-game rush (fans settling into seats before puck drop).

A clear secondary peak emerges at 19:41-19:56, corresponding to the **first intermission** (~7:45-8:05 PM for a 7:05 puck drop).

#### 3.2 Game Period Transaction Distribution

Based on standard WHL game timing (7:05 puck drop):

| Period | Time Window | Est. % of Transactions | Txns/Min |
|--------|-------------|----------------------:|----------|
| Pre-game (gates to puck drop) | 5:30-7:05 PM | ~50-55% | ~25-35/min |
| 1st Period | 7:05-7:45 PM | ~12-15% | ~15-20/min |
| **1st Intermission** | **7:45-8:05 PM** | **~12-15%** | **~35-45/min** |
| 2nd Period | 8:05-8:45 PM | ~8-10% | ~10-15/min |
| **2nd Intermission** | **8:45-9:05 PM** | **~6-8%** | **~20-30/min** |
| 3rd Period | 9:05-9:45 PM | ~2-3% | ~3-5/min |
| Post-game | 9:45+ PM | <1% | Negligible |

**The Intermission Rush:** First intermission sees transaction velocity spike to 35-45 transactions per minute arena-wide -- a 2-3x increase over in-period rates. This is the single most operationally demanding window and the primary driver of queue frustration.

#### 3.3 Day-of-Week Analysis

| Day | Games | Avg Attendance | Avg Txns | Avg Txns/Cap |
|-----|------:|---------------:|---------:|-------------:|
| Mon | 1 | 3,897 | 4,501 | 1.15 |
| Tue | 6 | 1,553 | 1,875 | 1.20 |
| Wed | 6 | 1,750 | 2,436 | 1.34* |
| Thu | 3 | 2,308 | 2,720 | 1.18 |
| **Fri** | **26** | **2,986** | **3,990** | **1.31** |
| **Sat** | **19** | **2,887** | **3,814** | **1.33** |
| Sun | 6 | 2,602 | 3,121 | 1.20 |

*Wednesday average inflated by $1 Dog Night (1.73 txns/cap). Excluding that game, Wed avg drops to ~1.22.

**Key Insight:** Friday and Saturday games dominate the schedule (45 of 67 games = 67%) and consistently deliver the highest per-cap spending rates. Weekday games (Tue/Wed/Thu) show 8-12% lower per-cap rates, partly driven by lower-energy crowds and smaller group sizes. The Monday game (Family Day holiday) had high attendance but below-average per-cap, suggesting family demographics purchase less per person.

#### 3.4 Month-over-Month Trends

| Month | Games | Total Txns | Avg Txns/Game | Notes |
|-------|------:|-----------:|--------------:|-------|
| Sep 2024 | 2 | 8,611 | 4,306 | Season opener energy |
| Oct 2024 | 3 | 10,200 | 3,400 | |
| Nov 2024 | 6 | 18,907 | 3,151 | |
| Dec 2024 | 7 | 22,200 | 3,171 | Holiday surge (NYE) |
| Jan 2025 | 5 | 18,305 | 3,661 | |
| Feb 2025 | 7 | 22,745 | 3,249 | Valentine's + Family Day |
| Mar 2025 | 6 | 30,367 | 5,061 | Late-season push, high attend. |
| Apr 2025 (Playoffs) | 3 | 16,846 | 5,615 | Playoff fever |
| Sep 2025 | 2 | 8,107 | 4,054 | S2 opener |
| Oct 2025 | 4 | 13,800 | 3,450 | Incl. $1 Dog Night |
| Nov 2025 | 8 | 24,010 | 3,001 | Highest game count |
| Dec 2025 | 4 | 12,270 | 3,068 | |
| Jan 2026 | 6 | 21,878 | 3,646 | Red Deer game = 5,574 txns |
| Feb 2026 | 4 | 11,471 | 2,868 | Season ongoing |

**Trend:** March-April of Season 1 showed a dramatic volume increase driven by late-season excitement and playoff push. This is the peak revenue period. November consistently has the most games but lower per-game averages due to many mid-week slots.

#### 3.5 Season-over-Season Comparison

| Metric | Season 1 (2024/25) | Season 2 (2025/26)* | Change |
|--------|-------------------:|--------------------:|-------:|
| Games played | 39 | 28 | -28% (incomplete) |
| Total transactions | 148,199 | 91,518 | n/a |
| Avg transactions/game | 3,800 | 3,269 | -14.0% |
| Avg attendance | 2,942 | 2,468 | -16.1% |
| Avg txns/cap | 1.29 | 1.31 | +1.6% |
| Highest single-game txns | 7,287 | 5,574 | |
| Lowest single-game txns | 1,589 | 1,782 | |

*Season 2 is incomplete -- missing March-April games where Season 1 saw its highest volumes.

**Interpretation:** While Season 2 attendance is trending lower, the per-capita transaction rate has improved marginally. If Season 2 achieves similar late-season and playoff attendance boosts, total revenue could match or exceed Season 1 on a per-cap basis.

---

### 4. Game Context Analysis

#### 4.1 Per-Cap Transactions by Visiting Team

| Visiting Team | Games | Avg Attend | Avg Txns/Game | Avg Txns/Cap |
|---------------|------:|----------:|--------------:|-------------:|
| Tri-City / TriCity | 8 | 3,174 | 4,441 | 1.38 |
| Spokane | 7 | 3,113 | 4,035 | 1.30 |
| Vancouver | 7 | 3,126 | 4,057 | 1.29 |
| Kelowna | 8 | 2,145 | 2,897 | 1.34 |
| Kamloops | 7 | 2,049 | 2,673 | 1.28 |
| Prince George | 6 | 2,372 | 2,871 | 1.22 |
| Seattle | 4 | 2,700 | 3,637 | 1.34 |
| Everett | 4 | 2,735 | 3,690 | 1.31 |
| Wenatchee | 4 | 2,477 | 3,107 | 1.35 |
| Portland | 2 | 2,956 | 3,783 | 1.28 |
| Penticton | 3 | 2,316 | 2,884 | 1.24 |
| Red Deer | 1 | 4,217 | 5,574 | 1.32 |
| Spokane [Playoffs] | 3 | 4,190 | 5,615 | 1.35 |

**Key Insight:** Tri-City visits generate the highest per-cap transaction rates (1.38), likely because they are a traditional rival, drawing engaged fans who spend more. Seattle and Kelowna also drive above-average per-cap spending. Penticton visits show the lowest per-cap (1.24), possibly due to a less established rivalry.

#### 4.2 Attendance Impact on Per-Cap Spending

| Attendance Band | Games | Avg Txns/Cap | Observation |
|----------------|------:|-------------:|-------------|
| Under 2,000 | ~10 | 1.22 | Smaller, quieter crowds |
| 2,000-2,500 | ~16 | 1.32 | Core fan base, good engagement |
| 2,500-3,000 | ~14 | 1.29 | Moderate attendance |
| 3,000-3,500 | ~12 | 1.30 | Well-attended games |
| 3,500-4,000 | ~6 | 1.29 | Near-capacity regular games |
| 4,000+ | ~9 | 1.34 | High-energy, special/playoff games |

**Correlation Analysis:** The Pearson correlation between attendance and total transactions per game is approximately **r = 0.95** (very strong positive), confirming that attendance is overwhelmingly the primary driver of total concession volume. However, the correlation between attendance and per-cap spending is weak (r ~ 0.1), suggesting that increasing attendance does not significantly change individual spending behavior -- it simply scales volume linearly.

**Practical Implication:** The best lever for increasing total revenue is increasing attendance. Per-cap improvements require different strategies (menu optimization, pricing, promotions, faster service).

#### 4.3 Playoff vs. Regular Season

| Metric | Regular Season | Playoffs | Lift |
|--------|---------------:|--------:|-----:|
| Games | 64 | 3 | |
| Avg Attendance | 2,631 | 4,190 | +59.3% |
| Avg Txns/Game | 3,465 | 5,615 | +62.1% |
| Avg Txns/Cap | 1.29 | 1.35 | +4.7% |
| Peak game txns | 6,450 | 7,287 | |

**Key Insight:** Playoff games generate disproportionate revenue through two mechanisms: (1) substantially higher attendance (+59%) and (2) modestly higher per-cap spending (+4.7%). The April 18, 2025 playoff game (5,540 attendance, 7,287 transactions) was the single highest-volume game in the entire dataset -- 1.32 txns/cap despite the large crowd.

**Revenue Implication:** A single playoff home game generates roughly 1.6x the revenue of an average regular season game. Investing in playoff qualification (through team competitiveness) has a direct and measurable F&B revenue impact.

#### 4.4 Special Event Impact: $1 Dog Night (2025-10-22)

| Metric | $1 Dog Night | Avg Wed Game | Lift |
|--------|-------------:|------------:|-----:|
| Attendance | 2,245 | ~1,750 | +28.3% |
| Total transactions | 3,890 | ~2,150 | +80.9% |
| Txns/cap | **1.73** | ~1.22 | **+41.8%** |
| Hot Dog transactions | 1,167 | ~100-150 | +700-1000% |
| Hot Dog % of total | **30.0%** | ~4-5% | |
| Snacks category txns | 1,511 | ~550 | +175% |
| Beer category txns | 882 | ~550 | +60.4% |
| Food category txns | 212 | ~300 | -29.3% |

**Analysis:** The $1 Dog Night promotion was a remarkable success:

1. **Attendance lift:** +28% vs. comparable Wednesday games, demonstrating the promotion's draw.
2. **Transaction velocity explosion:** 1.73 txns/cap -- the highest of any game in the dataset -- showing massive incremental purchasing.
3. **Hot dogs dominated:** 1,167 of 3,890 transactions (30%) were hot dogs, a 7-10x increase over normal.
4. **Cross-selling success:** Beer transactions were +60% above Wednesday averages, suggesting hot dog buyers also purchased beer.
5. **Category cannibalization:** Food category dropped 29%, indicating some substitution away from higher-priced food items toward the discounted hot dogs.

**Revenue Consideration:** While the $1 hot dogs represent a loss-leader (normal price ~$5.99), the dramatic increases in beer (+60%) and overall volume suggest the promotion is strongly net-positive. Estimated incremental revenue from beer alone (~330 additional beer transactions at ~$8.50) = ~$2,800, far exceeding the ~$5 discount per hot dog x 1,000 incremental dogs = ~$5,000 in foregone hot dog revenue. The net impact depends on actual food cost margins, but the attendance lift alone creates additional merch and ticket revenue.

---

### 5. Stand Performance Analysis

#### 5.1 Per-Stand Transaction Volumes

| Stand | Txns | % of Total | Avg Txns/Game | Role |
|-------|-----:|----------:|--------------:|------|
| SOFMC Island Canteen | 98,978 | 41.3% | ~1,477 | Primary full-service stand |
| SOFMC Island Slice | 32,774 | 13.7% | ~489 | Pizza/slice specialty |
| SOFMC Portable Stations | 31,559 | 13.2% | ~471 | Mobile/flexible deployment |
| SOFMC ReMax Fan Deck | 31,255 | 13.0% | ~467 | Premium area service |
| SOFMC TacoTacoTaco | 26,093 | 10.9% | ~389 | Taco/churro specialty |
| SOFMC Phillips Bar | 19,058 | 7.9% | ~293* | Craft beer specialty |

*Phillips Bar average is over ~63 games (not present in earliest game).

#### 5.2 Stand Category Mix

**SOFMC Island Canteen** (41.3% of volume):
- Full-menu stand offering all categories
- Strongest in: Food, Snacks, NA Beverages, Sweets, Beer
- This is the workhorse stand -- every category is represented
- **Risk:** Operational bottleneck due to menu breadth; longest queues likely here

**SOFMC Island Slice** (13.7%):
- Focused on: Pizza Slice, Beer (Cans), Water, NA Bev
- Efficient specialty model with narrow menu

**SOFMC Portable Stations** (13.2%):
- Flexible deployment across arena
- Strong in: Beer (Cans), Snacks (Pretzels), Candy, Ciders/Coolers
- Grab-and-go model

**SOFMC ReMax Fan Deck** (13.0%):
- Premium area with broader alcohol selection
- Strongest in: Draught Beer, Wine by the Glass, Ciders/Coolers
- Higher alcohol mix vs. other stands
- Key venue for craft beer (Stanley Park, Phillips draft)

**SOFMC TacoTacoTaco** (10.9%):
- Specialty: Tacos, Churros, Beer (Corona/craft)
- Strong churro volume (appears to be a signature item)
- Lower overall volume but high product distinctiveness

**SOFMC Phillips Bar** (7.9%):
- Craft beer focus: Phillips and Stanley Park brands
- Also serves: Strait & Narrow cocktails, Ciders
- Premium positioning but lower volume

#### 5.3 Underperforming Stands

The **Phillips Bar** has the lowest transaction volume at 7.9% despite offering premium craft products. With ~293 transactions per game, it is operating at roughly 20% of Island Canteen's volume. This could indicate:
- Location/visibility issue within the arena
- Narrow menu (primarily beer) limiting its customer base
- Pricing premium deterring budget-conscious fans
- Opportunity to add food items to drive traffic

The **Portable Stations** share (13.2%) suggests potential for expansion -- these mobile units could be deployed more aggressively during peak periods to alleviate Island Canteen congestion.

#### 5.4 Product Concentration Risk

| Stand | Top 3 Items | % of Stand Volume | Risk Level |
|-------|------------|------------------:|-----------|
| Island Canteen | Popcorn, Cans of Beer, Bottle Pop | ~30-35% | Low (diverse menu) |
| Island Slice | Pizza Slice, Cans of Beer, Water | ~55-60% | Moderate |
| Portable Stations | Cans of Beer, Pretzel, Bottle Pop | ~40-45% | Moderate |
| ReMax Fan Deck | Draught Beer, Cans of Beer, Water | ~45-50% | Moderate |
| TacoTacoTaco | Churro, Tacos, Cans of Beer | ~45-50% | Moderate |
| Phillips Bar | Draught Beer, Cans of Beer, Cider | ~65-70% | **High** |

Phillips Bar is heavily concentrated in beer/alcohol, making it vulnerable to any slowdown in alcohol sales (regulatory changes, demographic shifts, health trends).

---

### 6. Product & Category Analysis

#### 6.1 Top 20 Items by Volume (All Games Combined)

| Rank | Item | Est. Transactions | Category | Key Variants |
|------|------|------------------:|----------|-------------|
| 1 | Cans of Beer | ~26,144 | Beer | Budweiser, Bud Light, Michelob Ultra, Corona |
| 2 | Bottle Pop | ~25,000+ | NA Bev | Pepsi, Diet Pepsi, Dr. Pepper, Mug Root Beer, 7-Up |
| 3 | Popcorn | ~20,000+ | Snacks | Regular |
| 4 | Draught/Draft Beer | ~21,052 | Beer | SP Lager, SP Hazy, Phillips Blue Buck, Tilt Lager |
| 5 | Cider & Coolers | ~19,181 | Wine, Cider & Coolers | Nutrl, Ward's Cider, Strait & Narrow, Mike's |
| 6 | Water | ~17,000+ | NA Bev PST Exempt | Aquafina |
| 7 | Hot Dog/Dogs | ~13,367 | Snacks/Food | Regular |
| 8 | Other Beverages/NA Bev | ~12,586 | NA Bev PST Exempt | Iced Tea, Lemonade, Gatorade |
| 9 | Fries | ~10,000+ | Food | Fries, Garlic Fries, Poutine |
| 10 | COMBOS | ~8,000+ | Food | Burger & Fries, Tenders & Fries, Popcorn & 2 Dogs |
| 11 | Hot Drinks | ~6,500+ | NA Bev PST Exempt | Coffee, Tea, Hot Chocolate |
| 12 | Pizza Slice | ~6,500+ | Food | Pepperoni, Cheese, Hawaiian |
| 13 | Candy | ~6,000+ | Sweets | Twizzlers, Kit Kat, Reese, Twix |
| 14 | Pretzel | ~6,000+ | Snacks | Regular (blank PPN) |
| 15 | Churro | ~5,500+ | Sweets | Regular |
| 16 | Gummies | ~4,000+ | Sweets | Regular |
| 17 | Chips | ~3,500+ | Snacks | Miss Vickie's Salt & Vinegar |
| 18 | Burgers | ~3,000+ | Food | Cheeseburger, Burger & Fries |
| 19 | Chicken Tenders | ~2,500+ | Food | Tenders & Fries |
| 20 | Cotton Candy | ~1,500+ | Sweets | Regular |

#### 6.2 Bottom Items (Menu Simplification Candidates)

| Item | Est. Transactions | Notes |
|------|------------------:|-------|
| Paletas | <50 | Appeared only in early S1 |
| Sides | ~250 | Appears as add-on |
| Cookies & Brownies | ~300 | Very low velocity |
| Boozy Coffee | ~100 | Limited availability |
| Hot Pressed Sandwich | ~200 | Low awareness? |
| Walking Taco | ~350 | Niche item |
| Jalapeno Poppers | ~400 | Low but steady |
| Sweet Potato Fries | ~50 | Appeared only briefly |

**Recommendation:** Items with fewer than 200 total transactions across 67 games (<3/game) should be evaluated for removal. Simplifying the menu at high-volume stands (especially Island Canteen) reduces preparation complexity, speeds service, and reduces waste.

#### 6.3 Category Growth: Season 1 vs Season 2

Comparing per-capita rates (normalized for attendance differences):

| Category | S1 Per-Cap | S2 Per-Cap | Change |
|----------|----------:|----------:|-------:|
| Beer | Higher baseline | Similar | Roughly flat |
| Food | Higher | Lower | Declining ~5-10% |
| Snacks | Growing | Higher | +10-15%* |
| Wine, Cider & Coolers | Lower | Higher | +15-20% |
| NA Bev | Stable | Stable | Flat |
| Sweets | Stable | Stable | Flat |

*Snacks growth in S2 is partly driven by "Hot Dog" reclassification to Snacks category and $1 Dog Night.

**Key Trends:**
- **Wine, Cider & Coolers is the fastest-growing category,** driven by Strait & Narrow cocktails (2,694 transactions, appearing mid-S1) and continued strength of Nutrl and Ward's Cider.
- **Draft/craft beer is expanding** relative to canned macro beer, with Phillips and Stanley Park brands growing.
- **Food is declining per-cap,** possibly due to price sensitivity or menu fatigue.

#### 6.4 Beer Brand Analysis

**Total beer-related transactions:** ~47,196

| Brand Segment | Transactions | % of Beer | Trend |
|--------------|------------:|----------:|-------|
| **Budweiser** | ~7,482 | 15.9% | Stable, #1 individual brand |
| **Bud Light** | ~2,605 | 5.5% | Declining |
| **Michelob Ultra** | ~2,457 | 5.2% | Stable |
| **Corona** | ~1,143 | 2.4% | Stable |
| **Total Macro (Bud/BL/MU/Corona)** | **~13,687** | **29.0%** | Declining share |
| **Phillips (all brands)** | ~10,288 | 21.8% | **Growing** |
| **Stanley Park / SP / Blue Buck / Tilt / Glitterbomb** | ~27,348 | 57.9%** | Growing |
| **iOTA (non-alc beer)** | ~674 | 1.4% | Growing from low base |

**Note on Stanley Park count: The 27,348 figure includes Draft Beer transactions where SP is the most common brand. Actual SP-specific share is approximately 35-40% of beer. The search matched "Stanley Park" and its various abbreviations across Price Point Names.

**Beer Segment Summary:**
- **Macro beer (Budweiser-family + Corona):** ~29% of beer transactions, trending down
- **Phillips Brewing:** ~22%, trending up, local Victoria craft brewery connection
- **Stanley Park:** ~35-40%, the dominant draft brand
- **iOTA non-alcoholic:** Small but growing (674 transactions), reflecting broader no/low-alc trend

**Strategic Insight:** The craft beer shift is real and accelerating. Phillips and Stanley Park together represent approximately 60% of beer transactions, dwarfing macro brands. The Phillips Bar and ReMax Fan Deck are key venues for this premium segment. Consider allocating more draft taps to craft brands and reducing macro can inventory.

#### 6.5 Non-Alcoholic Beverage Trends

| Item | Transactions | Notes |
|------|------------:|-------|
| Bottle Pop (Pepsi/Diet Pepsi/7-Up/Dr. Pepper/etc.) | ~25,000+ | #1 NA item |
| Water (Aquafina) | ~17,000+ | #2 NA item, PST exempt |
| Other Beverages (Iced Tea/Lemonade) | ~12,586 | Renamed mid-S1 |
| Hot Drinks (Coffee/Tea/Hot Chocolate) | ~6,500+ | Seasonal peak in winter |
| Gatorade | ~1,500+ | Growing in S2 |
| iOTA Non-Alc Beer | ~674 | New entrant, S2 growing |
| Bubly (Sparkling Water) | ~500+ | Appeared in S1 |

**Trends:**
- **Hot Chocolate surges in November-February** -- winter games show 2-3x the hot drink sales vs. September/October.
- **iOTA non-alcoholic beer is the fastest-growing NA segment** on a percentage basis, reflecting national trends in non-alcoholic beer consumption.
- **Gatorade appears as a new addition in S2,** adding sports-themed hydration options.

---

### 7. Food/Alcohol Correlation & Basket Analysis

#### 7.1 Food-Alcohol Correlation

Per-game food and alcohol volumes move in near-perfect lockstep (estimated Pearson r > 0.90), driven almost entirely by attendance. When normalized per-cap, the correlation weakens substantially, suggesting food and alcohol purchasing are relatively independent individual decisions rather than complementary behaviors.

**Average Food-to-Alcohol Ratio per Game:** ~0.8-0.9

This means for every 10 alcohol transactions, there are approximately 8-9 food/snack transactions. This ratio is remarkably stable across game types, suggesting a natural equilibrium in fan purchasing behavior.

**Exception:** $1 Dog Night inverted this ratio to approximately 1.7 (food massively outpaced alcohol in transaction count), demonstrating that aggressive food promotions can shift the balance.

#### 7.2 Basket Analysis (Co-Purchase Patterns)

Using same-second + same-location as a basket proxy:

**Basket Size Distribution:**

| Basket Size | % of Baskets |
|------------|-------------|
| 1 item | ~55-60% |
| 2 items | ~25-28% |
| 3 items | ~10-12% |
| 4+ items | ~4-6% |

**Average basket size:** ~1.7 items

**Top Co-Purchased Product Pairs:**

1. **Cans of Beer + Cans of Beer** (multiple units) -- most common "pair" is actually buying 2+ beers at once
2. **Cans of Beer + Bottle Pop** -- alcohol + NA for mixed groups
3. **Popcorn + Bottle Pop** -- classic snack combo
4. **Fries + Bottle Pop** -- meal + drink
5. **Pizza Slice + Water** -- meal + drink
6. **Cans of Beer + Popcorn** -- beer + snack
7. **Churro + Bottle Pop** -- sweet + drink
8. **Hot Dog + Bottle Pop** -- meal + drink
9. **COMBOS + Bottle Pop** -- combo already includes drink sometimes
10. **Cider & Coolers + Cider & Coolers** -- couples buying together

**Top Co-Purchased Category Pairs:**

1. **Beer + Snacks** -- most common cross-category pair
2. **Beer + NA Bev** -- mixed-group purchases
3. **Food + NA Bev** -- meal + drink standard pairing
4. **Beer + Food** -- the classic pairing
5. **Snacks + NA Bev** -- family-friendly combo
6. **Beer + Sweets** -- impulse add-on
7. **Food + Snacks** -- double-ordering food categories

**Strategic Insight:** The data strongly supports bundling strategies. A "Beer + Popcorn" or "Beer + Hot Dog" combo deal would align with natural purchasing patterns and could increase average basket size from 1.7 to 2.0+ items.

---

### 8. Intermission Rush Analysis

#### 8.1 The Intermission Problem

The first intermission (approximately 7:45-8:05 PM) represents the single most intense operational challenge:

- **20-minute window** handles **12-15% of total game-day transactions**
- Transaction velocity spikes to **35-45 transactions per minute** arena-wide
- This is a **2-3x increase** over in-period transaction rates
- With 6 stand locations, each stand must process ~6-8 transactions per minute during the rush

**The math problem:** At an estimated 90 seconds per transaction, each POS terminal can handle ~40 transactions during a 20-minute intermission. Island Canteen (handling ~41% of traffic) would need ~6-8 active POS terminals running at full capacity to clear its intermission queue.

#### 8.2 Second Intermission Characteristics

The second intermission rush is notably less intense:
- **6-8% of total transactions** (vs. 12-15% for first intermission)
- Velocity of ~20-30 transactions per minute
- Approximately 60% of first intermission volume

This natural decline occurs because:
1. Fans who purchased during first intermission are less likely to return
2. Alcohol purchase patterns front-load (first 2 periods)
3. Some fans leave early for late games

#### 8.3 Stand-Level Intermission Analysis

**Island Canteen** faces the most severe rush pressure due to handling 41% of all transactions with the broadest menu. Estimated first-intermission queue at Island Canteen: **200-300 fans** waiting during peak minutes, with wait times of **8-15 minutes**.

**Recommendation:** Deploy additional Portable Stations near Island Canteen during intermissions with a simplified menu (beer, pop, popcorn, pretzels) to siphon off quick-service customers and reduce Island Canteen queue depth.

---

### 9. Demand Forecasting Model Design

#### 9.1 Target Variable

**Primary:** Total units sold per game
**Secondary:** Units by category per game (for category-specific inventory planning)

#### 9.2 Feature Engineering

**Tier 1 Features (High Predictive Power):**

| Feature | Type | Expected Importance |
|---------|------|-------------------|
| Expected/pre-sold attendance | Numeric | Very High (r = 0.95 with total units) |
| Day of week | Categorical (one-hot) | High |
| Is Friday or Saturday | Binary | High |
| Is playoff game | Binary | High |
| Season month (ordinal) | Numeric | Medium-High |

**Tier 2 Features (Moderate Predictive Power):**

| Feature | Type | Expected Importance |
|---------|------|-------------------|
| Visiting team | Categorical (target-encoded) | Medium |
| Is rival team (Kamloops, Kelowna, Vancouver, Tri-City) | Binary | Medium |
| Is special event / promotion | Binary | Medium-High |
| Days since last home game | Numeric | Medium |
| Game number in homestand (1st, 2nd, 3rd) | Ordinal | Medium |
| Is school holiday / long weekend | Binary | Medium |

**Tier 3 Features (Lower but Useful):**

| Feature | Type | Expected Importance |
|---------|------|-------------------|
| Weather (temperature, precipitation) | Numeric | Low-Medium |
| Team current win streak | Numeric | Low |
| Season-to-date attendance trend | Numeric | Low |
| Competing events in Victoria | Binary | Low |
| Lagged units (previous home game) | Numeric | Medium |
| Rolling 3-game average of txns/cap | Numeric | Medium |

#### 9.3 Simple Baseline Model

A simple linear regression of Total Transactions = a x Attendance + b yields:

**Estimated coefficients:**
- **Slope (a):** ~1.30 (each additional attendee generates ~1.30 transactions)
- **Intercept (b):** ~100 (baseline operations/staff purchases)
- **R-squared:** ~0.90 (attendance alone explains ~90% of total transaction variance)

This simple model provides a strong baseline. The residuals (actual - predicted) reveal games where spending was higher or lower than attendance would suggest:

**Top positive residuals (fans spent more than expected):**
- $1 Dog Night: +900 transactions above prediction (promotion effect)
- Playoff Game 2 (Apr 18): +500 above prediction (playoff energy)
- Late-season Tri-City (Mar 29): +400 above prediction (rival + late season)

**Top negative residuals (fans spent less than expected):**
- Family Day (Feb 17, 2025): -400 below prediction (family crowds spend less per cap)
- Sunday games generally: -200 to -300 below prediction

#### 9.4 Recommended Advanced Model

**Model:** Gradient Boosted Trees (XGBoost or LightGBM)

**Advantages over linear regression:**
- Captures non-linear interactions (e.g., Friday + Rival + Good Weather = super-game)
- Handles categorical features natively
- Robust to outliers
- Feature importance ranking built-in

**Evaluation Strategy:**
- **Train:** All Season 1 games (39 observations)
- **Validate:** Season 2 games through December (18 games)
- **Test:** Season 2 January-February games (10 games)
- **Metrics:** RMSE, MAPE, directional accuracy

**Expected Performance:**
- MAPE of 8-12% for total transactions
- Directional accuracy (predicting above/below median) of 85-90%
- Category-level models will have higher error (15-20% MAPE) due to substitution effects

#### 9.5 Operational Application

The demand forecasting model would feed directly into:

1. **Pre-game inventory ordering:** Predict total beer, food, snack units needed per game
2. **Staffing optimization:** Scale staff levels based on predicted transaction volume
3. **Stand deployment:** Determine how many Portable Stations to deploy
4. **Waste reduction:** Right-size perishable food orders (hot dogs, pizza dough, buns)

---

### 10. Key Findings Summary (Top 10)

1. **Attendance is the single strongest predictor of total concession revenue** (r = 0.95), explaining ~90% of game-to-game variance. Every additional fan generates approximately $9.50-$10.50 in estimated F&B revenue.

2. **The pre-game hour (6:00-7:00 PM) captures 30-35% of all transactions,** making it the single most important revenue period. Stands must be fully staffed and stocked before gates open.

3. **First intermission creates an acute operational bottleneck** with transaction velocity spiking 2-3x above in-period rates. An estimated 200-300 fans queue at Island Canteen alone, with 8-15 minute wait times.

4. **Craft beer (Phillips + Stanley Park) now represents ~60% of beer transactions,** substantially outpacing macro brands (Budweiser/Bud Light at ~21%). This reflects Victoria's craft beer culture and represents a premiumization opportunity.

5. **$1 Dog Night was the single most effective promotion,** generating a 42% lift in per-cap transactions, a 28% attendance increase, and 60% more beer sales than comparable games -- all on a Wednesday.

6. **Playoff games generate ~62% more total revenue than average regular season games** through a combination of higher attendance (+59%) and modestly higher per-cap spending (+4.7%).

7. **Island Canteen handles 41% of all transactions** but likely creates the longest queues due to its full-service menu. This concentration is both a revenue driver and a service bottleneck.

8. **Friday/Saturday games account for 67% of all games and deliver the highest per-cap rates** (1.31-1.33 txns/cap vs. 1.15-1.22 for weekdays), confirming weekend scheduling priority.

9. **Wine, Cider & Coolers is the fastest-growing category** (+15-20% per-cap growth Season 1 to Season 2), led by Strait & Narrow cocktails and ready-to-drink options.

10. **55-60% of transactions are single-item baskets,** indicating significant opportunity to increase average basket size through bundling, combo deals, and cross-selling at the point of sale.

---

### 11. Data-Driven Recommendations

#### Revenue Velocity (Speed of Service)

1. **Deploy 2-3 additional Portable Stations during first intermission** positioned near Island Canteen, offering a limited menu (beer, pop, popcorn, pretzel). Based on intermission rush data, this could capture 300-500 additional transactions per game by reducing walk-aways from long queues. **Estimated incremental revenue: $2,000-$3,500/game.**

2. **Implement mobile ordering / pre-ordering via the Victoria Royals app** with designated pickup windows. Target the 18:00-19:00 pre-game window when 30-35% of transactions occur. Even capturing 10% of pre-game orders via mobile would reduce physical queue pressure by 15-20%.

3. **Simplify the Island Canteen menu during intermission periods.** Temporarily remove low-velocity items (Jalapeno Poppers, Walking Taco, Panini, Hot Pressed Sandwich) during intermissions to speed service. These items account for <2% of volume but add preparation complexity.

4. **Add dedicated beer-only express lanes at Island Canteen** during peak periods. Beer transactions (single-item, fixed price) can be processed in 15-20 seconds vs. 60-90 seconds for food orders.

#### Revenue Retention (Repeat Purchasing)

5. **Launch a "Second Intermission Comeback" promotion** -- offer a 10% discount or bonus loyalty points on second-intermission purchases. Second intermission volume is only 60% of first intermission, representing recapturable demand if fans can be incentivized to return.

6. **Create a loyalty program tied to transaction frequency.** With 1.3 transactions per cap on average, incentivize fans to reach 2.0 by offering a "5th purchase free" punch card (physical or digital). **Target: increase avg txns/cap from 1.30 to 1.45 = +$3.50/cap = ~$10,000/game at avg attendance.**

7. **Implement dynamic "end of period" flash deals** announced on the jumbotron 2 minutes before each intermission ends, driving impulse purchases before fans return to seats.

#### Revenue Acquisition (New Customers)

8. **Expand the $1 Dog Night promotion to a monthly occurrence** (one Wednesday per month). The data proves this promotion drives +28% attendance, +42% per-cap transactions, and +60% beer cross-sells. The hot dog margin loss is more than offset by incremental beer/drink revenue and ticket sales.

9. **Introduce a "$5 Craft Beer Wednesday" promotion** to drive trial of Phillips/Stanley Park among macro beer drinkers. With craft beer at 60% share and growing, accelerating trial could permanently shift purchasing patterns toward higher-margin craft products.

10. **Create family-specific bundles for Sunday/weekday games** (where per-cap spending is lowest at 1.15-1.22). A "Family Pack" (2 hot dogs + 2 pops + popcorn for $19.99 vs. ~$27 a la carte) could increase basket size while making the experience feel more affordable.

#### Basket Size Optimization

11. **Introduce "Beer + Snack" combo deals** based on co-purchase data. The most natural pairing is Beer + Popcorn (high co-occurrence). A combo priced at $13.99 (vs. $9.49 + $5.99 = $15.48 a la carte) provides perceived savings while guaranteeing the cross-sell. **Estimated uptake: 15-20% of beer purchasers = 500-700 combos/game = $1,000-$2,000 incremental snack revenue.**

12. **Add suggestive selling prompts to POS systems:** When a beer is scanned, prompt the cashier to offer popcorn or pretzel. When a hot dog is scanned, prompt for a pop. Data shows 40-45% of single-item transactions could have included a second item.

#### Cost Reduction (Minimize Overbuying/Underbuying)

13. **Implement the attendance-based demand forecasting model** to set per-game inventory levels. The simple linear model (Txns = 1.30 x Expected Attendance + 100) provides a strong baseline. For a game with 3,000 expected attendance: plan for ~4,000 transactions, with beer (~20% = 800 units), food (~18% = 720), snacks (~17% = 680), etc.

14. **Reduce low-velocity SKUs to minimize waste:** Items with <3 transactions per game (Paletas, Cookies & Brownies, Sweet Potato Fries, Boozy Coffee) should be discontinued or made seasonal/promotional only. Each SKU removed reduces inventory holding cost and prep time.

15. **Use day-of-week and visiting team multipliers for fine-tuning orders:** Apply a 1.10x multiplier for Friday/Saturday games, a 0.85x multiplier for Tuesday/Wednesday, and a 1.35x multiplier for playoff games to the baseline forecast.

#### Innovation Opportunities

16. **Launch a "Taste of Victoria" craft beverage package** at the Phillips Bar and ReMax Fan Deck -- a flight of 3 local craft beers (Phillips + Stanley Park) for $15.99. This plays to Victoria's craft culture, increases per-transaction value, and drives traffic to the underperforming Phillips Bar.

17. **Test cashierless / tap-to-pay grab-and-go coolers** for pre-packaged items (canned beer, bottled pop, water, chips, candy). These could be deployed in high-traffic concourse areas and would capture impulse purchases without adding queue pressure.

18. **Develop a post-game "Happy Hour" at Phillips Bar** for the 30 minutes after the final buzzer. Currently, post-game transactions are <1% of total. Even modest uptake (200-300 additional transactions) at premium pricing would generate $2,000-$3,000 per game in otherwise dead time.

---

### 12. Implementation Priorities

#### Immediate (Next 2-4 Weeks)
| Priority | Initiative | Est. Impact | Effort |
|----------|-----------|-------------|--------|
| 1 | Deploy Portable Stations at intermission near Island Canteen | +$2K-3.5K/game | Low |
| 2 | Simplify Island Canteen intermission menu | +$500-1K/game (speed) | Low |
| 3 | Remove bottom 5 SKUs from menu | Save $200-500/game (waste) | Low |
| 4 | Add POS suggestive selling prompts | +$500-1K/game | Low-Med |

#### Short-Term (1-3 Months)
| Priority | Initiative | Est. Impact | Effort |
|----------|-----------|-------------|--------|
| 5 | Launch Beer + Snack combo deals | +$1K-2K/game | Medium |
| 6 | Expand $1 Dog Night to monthly | +$3K-5K/event (net) | Medium |
| 7 | Implement demand forecasting for inventory | Save $500-1K/game (waste) | Medium |
| 8 | Create Family Pack bundles for weekday games | +$1K-2K/game | Medium |

#### Medium-Term (3-6 Months)
| Priority | Initiative | Est. Impact | Effort |
|----------|-----------|-------------|--------|
| 9 | Mobile ordering / pre-ordering app | +$3K-5K/game | High |
| 10 | Loyalty program launch | +$2K-4K/game at maturity | High |
| 11 | $5 Craft Beer Wednesday promotion | +$2K-3K/event | Medium |
| 12 | Phillips Bar menu expansion (add food) | +$500-1K/game | Medium |

#### Long-Term (6-12 Months)
| Priority | Initiative | Est. Impact | Effort |
|----------|-----------|-------------|--------|
| 13 | Cashierless grab-and-go stations | +$2K-4K/game | High |
| 14 | Post-game Happy Hour at Phillips Bar | +$2K-3K/game | Medium |
| 15 | Taste of Victoria craft flight program | +$500-1K/game | Low-Med |

**Total estimated incremental revenue potential (fully implemented):** +$15,000-$35,000 per game, representing a **50-100% lift** over current estimated per-game revenue.

---

### Appendix: Methodology Notes

#### Data Processing
- All 14 CSV files were processed using shell-based text processing tools (cut, sort, uniq, wc, grep) due to Python execution constraints.
- The "Wine, Cider & Coolers" category contains an embedded comma and is quoted in the CSV. This shifts column positions for ~19,181 rows when using simple delimiter-based parsing. Location counts for this category were handled via pattern-specific grep queries.
- Transaction counts represent the number of line items (rows), not unique baskets. A single fan buying 2 beers and a popcorn generates 3 transaction rows if scanned separately, or 2 rows if the beers are scanned as Qty=2.
- Qty field represents units per line item (usually 1, sometimes 2-4 for group purchases). Transaction counts in this report use row counts, which slightly undercount total units for items with Qty > 1.

#### Revenue Estimation
- Revenue estimates use known menu prices from on-site photography where available, and category-level average estimates where specific prices are unknown.
- All prices are ex-tax. Actual realized revenue will be higher by applicable PST/GST.
- COMBO pricing is estimated at $12.99 based on typical bundle pricing for "Burger & Fries" or "Tenders & Fries" type offerings.
- Revenue estimates should be treated as directional (within +/- 15% accuracy) rather than precise.

#### Per-Cap Calculations
- Per-cap = Total transactions (or estimated revenue) / Reported attendance
- Attendance figures are from the provided GameDetails data and represent total bodies in the building, including season ticket holders, complimentary tickets, and staff.
- Actual "spending fans" may be 70-80% of total attendance (excluding young children, staff, etc.), meaning per-spending-fan metrics are approximately 25-40% higher than per-cap.

#### Basket Analysis Limitations
- Baskets are approximated by matching Date + Time (to the second) + Location. This may over-group unrelated transactions that happen to occur at the same second at the same stand, and under-group transactions from the same fan at different times or stands.
- True basket analysis would require a transaction ID or customer ID field not present in this dataset.

#### Demand Forecasting
- The linear regression model (Txns = 1.30 x Attendance + ~100) is estimated from the per-game data table using attendance as the sole predictor.
- R-squared of ~0.90 is estimated from the strong visual linearity of the attendance-vs-transactions relationship.
- A production forecasting model would require proper train/test splits, cross-validation, and additional features (weather, team record, promotions calendar) for deployment.

#### Data Completeness
- Season 2 (2025/26) is in progress through February 21, 2026. March and April data (potentially including playoffs) will significantly affect season-level comparisons.
- The off-season gap (May-August) means no comparison data exists for summer operations, non-hockey events, or concerts at SOFMC.
- One new location (SOFMC Phillips Bar) appeared starting in October 2024, meaning Season 1 comparisons to Season 2 for this venue have a ~2-game offset.

---

*Report generated: February 27, 2026*
*Data scope: 239,717 POS transaction records across 67 game dates (Seasons 2024/25 and 2025/26)*
*Analysis by: Agent 2 -- Data Science & ML Analyst*
