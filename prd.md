# PRD: Royals Concession Intelligence Platform
## Hackathon MVP -- 2.5-Hour Build (v2)

---

## Changes from v1

This section summarizes every material change so the build team can quickly see what shifted.

| # | Change | Rationale |
|---|--------|-----------|
| 1 | **[CUT] US-1.5 Mock Stripe data generation** -- deleted entirely. Revenue uses `estimated_revenue` from price lookup. `stripe_generator.py` removed from project structure. | Saves 30-45 min. Two layers of estimation (POS -> prices -> Stripe) weakens credibility. |
| 2 | **[CUT] `stripe_transactions` table** -- removed from DB schema and integration contracts. | Follows from #1. |
| 3 | **[SIMPLIFIED] US-2.2 Anomaly detection** -- moved to optional/nice-to-have. Basic version only if time permits. | Lowest business value of the ML models. No clear actionable recommendation for the GM. |
| 4 | **[RENAMED] US-3.7 Revenue Analytics -> Revenue Estimation** -- uses `estimated_revenue` directly; all Stripe references removed. Simplified to 3-4 KPI cards + 2 charts. | Honest estimation > fake Stripe facade. |
| 5 | **[UPGRADED] US-3.6 Forecasting page** -- prep sheet is now the PRIMARY output. Added: item-level quantities, stand-level breakdown, stand opening recommendation, staffing per stand, historical comparable games, promotional event dropdown, "Print Prep Sheet" button. | Ops Manager feedback: this is the single most valuable feature. |
| 6 | **[ADDED] Business Impact Callout on every dashboard page** -- each page gets a callout card with specific dollar figures. | Business Strategy feedback: turns every page into a business case. |
| 7 | **[ADDED] Per-Cap Benchmark Gap** to Season KPIs -- gauge/comparison: $11.77 current vs $14-16 WHL benchmark = $180K-$342K gap. | Single most powerful business argument. |
| 8 | **[ADDED] $1 Dog Night callout** to Game Explorer or Season KPIs. | Promotional ROI proof point. |
| 9 | **[ADDED] Forecast vs. Actual toggle** on Game Explorer for historical games. | Builds trust in model; demonstrates model validation to judges. |
| 10 | **[REDUCED] Claude tools from 7 to 5** -- cut `get_anomalies`, simplified `get_revenue_analysis`. | Scope cut follows from Stripe and anomaly cuts. |
| 11 | **[RESTRUCTURED] Demo flow** -- from 7-page tour to problem-solution narrative arc. | CMO feedback: judges score narrative, not software tours. |
| 12 | **[ADDED] Pre-scripted Claude Advisor questions** -- 3 tested questions for live demo. | Do not rely on improvisation during 10-min demo. |
| 13 | **[ADDED] Business Case section** with $250K headline and breakdown table. | Business Strategy: judges score Business Impact first. |
| 14 | **[ADDED] Presentation Headlines section** with 2 options. | CMO: first impressions are formed in 5 seconds. |
| 15 | **[UPDATED] Build Order** -- realistic for 2.5 hours with scope cuts. | Reflects actual scope. |
| 16 | **[UPDATED] Acceptance Criteria** -- removed Stripe references, added new features. | Reflects actual scope. |

---

## Business Case

**Headline: $250K in identified annual revenue opportunity**

| Opportunity | Annual Impact | Data Source |
|-------------|---------------|-------------|
| Close per-cap gap ($11.77 -> $14.00) | +$180,000 | Benchmark comparison vs. WHL peers |
| Intermission bottleneck recovery (express lanes, pre-ordering) | +$80,000-$120,000 | Transaction velocity analysis: demand exceeding throughput |
| Combo/bundle strategy (25% adoption) | +$72,000 | Product affinity analysis + industry combo adoption rates |
| Phillips Bar food cross-sell | +$18,000-$25,000 | Stand-level analysis: 19K beer txns with <5% food |
| Staffing + prep optimization (cost savings) | -$35,000-$60,000 | Demand forecast reducing waste and overstaffing |
| **Total identified opportunity** | **$385,000-$457,000** | |
| **Conservative capture rate (60%)** | **~$250,000** | |

**One-liner:** "This platform turns 239,000 real transactions into a $250K annual revenue roadmap."

**Defensibility:** Even at half capture, $125K on a $10K Phase 1 investment = 12x ROI in year one.

---

## Presentation Headlines

Choose one for the opening slide:

- **Aggressive:** "Your arena is leaving $120K on the table every season. We found it."
- **Alternative:** "Turning 239,000 transactions into the smartest concession stand in the WHL."

---

## Overview

A Streamlit-based analytics platform for Victoria Royals concession operations at SOFMC. Powered by real POS data (239K transactions across 67 games and 2 seasons), ML forecasting models, and a Claude API-powered "Concession Advisor" that lets arena staff ask questions in natural language and get data-backed answers with specific dollar figures.

**Demo environment:** Single laptop, Python + Streamlit, no cloud dependencies.

## Tech Stack
- Python 3.10+
- Streamlit (dashboard UI)
- SQLite (data storage)
- scikit-learn (ML models)
- Plotly (charts)
- Anthropic Claude API with tool use (AI advisor)
- pandas, openpyxl, joblib

## Project Structure
```
royals-concession-intel/
├── config.py                    # Shared constants, prices, DB path
├── requirements.txt
├── run.sh                       # One-click build + launch
├── data/                        # Symlinked CSVs + GameDetails.xlsx
├── db/
│   └── royals.db                # SQLite (generated)
├── models/
│   ├── demand_forecast.joblib
│   ├── anomaly_detector.joblib  # [OPTIONAL] Only if time permits
│   ├── revenue_predictor.joblib
│   └── affinity_rules.json
├── data_foundation/
│   ├── load_data.py             # CSV -> SQLite ingestion
│   ├── price_lookup.py          # Item -> price mapping
│   └── build_all.py             # Master build script
├── ml/
│   ├── train_demand.py          # Demand forecasting model
│   ├── train_anomaly.py         # [OPTIONAL] Anomaly detection
│   ├── train_revenue.py         # Revenue predictor
│   ├── train_affinity.py        # Product affinity mining
│   └── predict.py               # Unified prediction API
├── dashboard/
│   ├── app.py                   # Streamlit main entrypoint
│   ├── pages/
│   │   ├── 1_Season_KPIs.py
│   │   ├── 2_Game_Explorer.py
│   │   ├── 3_Stand_Performance.py
│   │   ├── 4_Intermission_Analysis.py
│   │   ├── 5_Forecasting.py
│   │   ├── 6_Revenue_Estimation.py    # [RENAMED] was Revenue_Analytics
│   │   └── 7_Concession_Advisor.py
│   └── components/
│       ├── charts.py
│       ├── filters.py
│       └── kpi_cards.py
└── advisor/
    ├── claude_advisor.py        # Claude API + tool orchestration
    ├── tools.py                 # Tool implementations
    └── prompts.py               # System prompt
```

**Removed from v1:** `data_foundation/stripe_generator.py` -- no longer needed.

---

## User Stories

### Epic 1: Data Foundation (Agent A)

**US-1.1: Config file**
As a developer, I need a shared config.py at project root so all modules use the same constants.
- Exports: DB_PATH, MODELS_DIR, DATA_DIR, KNOWN_PRICES, CATEGORY_PRICES, LOCATIONS, CATEGORIES, GAME_PERIODS, TAX_RATE, LIQUOR_TAX_RATE
- KNOWN_PRICES maps (item, price_point_name) -> price using confirmed menu pricing: Beer $9.49, Cocktails $9.99, Water $3.99, Pop $4.99, Pretzel $5.99, etc.
- CATEGORY_PRICES provides fallback pricing by category
- NEW: Add STAND_OPENING_RULES dict mapping attendance ranges to recommended stands (see US-3.6)
- NEW: Add PROMO_EVENTS list: ["Dollar Dog Night", "Family Night", "School Night", "Taco Tuesday", "Playoff", "Regular"]

**US-1.2: CSV ingestion into SQLite**
As the system, I need all 14 CSV files loaded into a SQLite `transactions` table with enriched columns.
- Table schema: id, date, time, category, item, qty, price_point_name, location, estimated_price, estimated_revenue, hour, minute, game_period, season
- Derive `estimated_price` using price_lookup.py (exact match -> category fallback)
- Derive `estimated_revenue` = estimated_price * qty
- Derive `hour`, `minute` from time column
- Derive `game_period` from time (pre-game, 1st period, 1st intermission, etc.)
- Derive `season` (1 = 2024/25, 2 = 2025/26)
- Handle negative qty (refunds) -- keep them, they're valid
- Create indexes on date, category, location, game_period

**US-1.3: Game details table**
As the system, I need a `games` table with all ~67 home games from both seasons.
- Schema: id, date, opponent, day_of_week, attendance, season, is_playoff, promo_event, note
- Parse GameDetails.xlsx (or hardcode the pre-parsed data from the plan)
- NEW: `promo_event` column -- flag known promotional games (Dollar Dog Night, etc.) from the notes/data
- After transactions are loaded, compute: total_units, total_transactions, total_estimated_revenue, units_per_cap, revenue_per_cap per game

**US-1.4: Price lookup table**
As the system, I need a `price_lookup` table populated from KNOWN_PRICES.
- Schema: id, item, price_point_name, category, estimated_price
- Used by the advisor tools for reference

**[CUT] ~~US-1.5: Mock Stripe data generation~~**
~~As the system, I need a `stripe_transactions` table with realistic payment data.~~
**REMOVED.** Revenue analysis uses `estimated_revenue` from price lookup directly. No Stripe simulation needed. This saves 30-45 minutes of build time.

**US-1.5: Build script** (renumbered from US-1.6)
As a user, I need `build_all.py` to run the full data pipeline in sequence: load CSVs -> create games table -> compute game metrics.

### Epic 2: ML Models (Agent B)

**US-2.1: Demand forecasting model**
As the forecasting page, I need to predict units by category AND by item for any game scenario.
- Algorithm: GradientBoostingRegressor
- Features: opponent (encoded), day_of_week (encoded), month, attendance, is_playoff, promo_event (encoded)
- Target: units per game, per category, AND per top item (top 20-30 items by volume)
- NEW: Include `promo_event` as a feature -- Dollar Dog Night drives 1.73 txns/cap vs ~1.30 normal
- Train on all ~67 games
- Save as models/demand_forecast.joblib (dict with model, encoders, feature_names)
- Validate: print MAPE and R-squared
- NEW: The model must support item-level and stand-level predictions for the prep sheet

**US-2.2: Anomaly detection model [OPTIONAL -- Nice-to-have]**
As the game explorer and advisor, I need to flag unusual game-day patterns.
- Algorithm: IsolationForest
- Features per game: units_per_cap, beer_share, food_share, snack_share, avg_basket_size, pct_intermission_sales
- Save as models/anomaly_detector.joblib (dict with model, scaler, feature_names)
- Returns: is_anomaly (bool), anomaly_score (float), flagged_features (list)
- **Build this ONLY after US-2.1, US-2.3, and US-2.4 are complete.** If time is short, skip it.
- Basic version sufficient: flag the 3-5 most unusual games with a one-sentence explanation.

**US-2.3: Revenue predictor**
As the forecasting page, I need to predict total estimated revenue for a game.
- Algorithm: LinearRegression (attendance has r=0.95 correlation)
- Features: attendance, day_of_week_encoded, is_playoff, month, promo_event_encoded
- Save as models/revenue_predictor.joblib

**US-2.4: Product affinity mining**
As the advisor and combo recommendations, I need to know what items are bought together.
- Group transactions by (date, time, location) as basket proxy
- Compute co-occurrence matrix and lift scores for item pairs and category pairs
- Save as models/affinity_rules.json with top 20 item pairs, top 10 category pairs, suggested bundle names

**US-2.5: Unified prediction API (predict.py)**
As the dashboard and advisor, I need a clean Python API for all model predictions.
- Functions: get_demand_forecast(), get_revenue_prediction(), get_affinity_recommendations()
- NEW: get_demand_forecast() must return item-level AND stand-level breakdowns
- NEW: get_comparable_games(opponent, day_of_week, attendance) -- returns 3-5 most similar historical games
- OPTIONAL: get_anomalies() -- only if US-2.2 is built
- All return Python dicts
- Handles model loading (lazy, cached)
- Imports from config.py for paths

### Epic 3: Streamlit Dashboard (Agent C)

**US-3.1: App shell and navigation**
As a user, I see a multi-page Streamlit app with sidebar navigation, Royals branding (purple/gold theme), and responsive layout.
- Main app.py with page config, custom CSS
- Sidebar with Victoria Royals logo/title and page links
- Each page is a separate file in dashboard/pages/
- Keep CSS simple -- max 10 minutes on theming. Streamlit defaults with a logo in sidebar is fine.

**US-3.2: Season KPIs page**
As a GM, I want to see season-level metrics at a glance.
- KPI cards: total estimated revenue, total transactions, avg attendance, avg per-cap revenue, total games
- Season 1 vs Season 2 comparison with deltas
- **NEW: Per-Cap Benchmark Gap visualization** -- gauge chart or large comparison showing:
  - Current per-cap: $11.77
  - WHL peer benchmark: $14-$16
  - Gap: $2.23-$4.23 per fan per game
  - Annual opportunity: $180K-$342K (at 2,600 avg attendance x 31 games)
  - This should be PROMINENT -- large fonts, visible from the back of the room
- Category breakdown donut chart
- Top 10 items by volume (horizontal bar)
- Monthly revenue trend line
- **NEW: $1 Dog Night callout card** -- "1,167 hot dog transactions. 30% of all sales that night. Proof that data-driven promotions work." (can also go on Game Explorer -- builder's choice)
- **NEW: Business Impact Callout** -- "Closing the per-cap gap to $14.50 = +$220K/year in additional revenue"

**US-3.3: Game Explorer page**
As a GM, I want to drill into any specific game's performance.
- Dropdown: select game by date + opponent + attendance
- Game metadata card (opponent, day, attendance, revenue, units)
- Units by category (horizontal bar)
- Transaction timeline (line chart, 5-min buckets from 6pm-10pm)
- Top 10 items for that game
- Stand breakdown (pie chart)
- Anomaly flag indicator (green/red badge) -- only if US-2.2 is built; otherwise skip
- **NEW: Forecast vs. Actual toggle** -- for historical games, show predicted values next to actual values. Demonstrates model validation and builds trust.
- **NEW: $1 Dog Night callout** -- if the selected game is Dollar Dog Night, display a prominent callout card with the promotional ROI story
- **NEW: Business Impact Callout** -- contextual per game (e.g., "This game's per-cap was $X below benchmark. At scale, this pattern represents $Y annually.")

**US-3.4: Stand Performance page**
As ops manager, I want to compare stand performance.
- Stacked bar chart: units by stand by category
- Revenue by stand
- Stand ranking table (units, revenue, categories served)
- Category mix comparison per stand
- **NEW: Phillips Bar Cross-Sell Alert** -- callout box: "Phillips Bar: 19,000+ beer transactions, <5% food attach rate. Adding simple food items could generate $18K-$25K/season."
- **NEW: Business Impact Callout** -- "Adding food to Phillips Bar = +$18K-$25K/year. Rebalancing stand traffic = +$15K-$25K/year in labor savings."

**US-3.5: Intermission Analysis page**
As ops manager, I want to understand the intermission rush.
- Transaction velocity heatmap: X=time (5-min buckets), Y=game dates, color=transaction count
  - Color scale must be dramatic: cool blues for quiet periods, hot reds/oranges for intermission crush
  - This is the visual hero of the demo -- invest in making it look good
- Period summary bars (Pre-game / 1st Period / 1st Intermission / etc.)
- Stand-level intermission comparison
- "Lost revenue estimator": slider for % improvement -> shows additional revenue
- **NEW: Business Impact Callout** -- "Solving the intermission bottleneck = +$80K-$120K/year. 350+ estimated fans abandon the queue per intermission = ~$2,800 lost per game."

**US-3.6: Forecasting page [UPGRADED -- Primary operational tool]**
As ops manager, I want to predict demand for an upcoming game and get a complete prep plan.

**Input widgets:**
- Opponent dropdown
- Day of week dropdown
- Attendance slider (1,000-6,000)
- Month picker
- Playoff toggle
- **NEW: Promotional event dropdown** -- Dollar Dog Night, Family Night, School Night, Taco Tuesday, Playoff, Regular

**PRIMARY OUTPUT: The Prep Sheet** (show this FIRST, above all charts)
The prep sheet is the hero feature. It must include:
1. **Item-level quantities** -- not just categories. "Tap 3 kegs Phillips IPA, stock 180 cans Bud, thaw 480 hot dogs" -- not "450 Beer units."
2. **Stand-level breakdown** -- what each stand needs. Island Canteen gets X, Phillips Bar gets Y, Island Slice gets Z.
3. **Stand opening recommendation** -- "For 1,500 expected attendance: Open Island Canteen + Phillips Bar + 1 Portable. Close Island Slice, TacoTacoTaco, ReMax Fan Deck." Based on rules in config.py:
   - Under 2,000: open 3 stands
   - 2,000-3,500: open 4 stands
   - Over 3,500: open all 6
4. **Suggested staffing per stand** -- headcount per stand based on attendance and historical patterns.
5. **Buffer recommendations** -- context-dependent: 25-30% for playoff/high-attendance, 10-15% for low-attendance Tuesday games.
6. **Historical comparable games** -- show 3-5 most similar past games (same opponent, similar attendance, same day of week) with what actually sold. Displayed below the forecast so ops can sanity-check the model.
7. **"Print Prep Sheet" button** -- generates a clean, printable format (use st.download_button with CSV or formatted text). Stand leads need a physical sheet at 4 PM setup.

**SECONDARY OUTPUT: Charts and predictions** (below the prep sheet)
- Predicted units by category (bar chart)
- Predicted revenue (gauge/big number)

**Business Impact Callout:** "Accurate demand prediction saves $35K-$60K annually in food waste and labor costs."

**US-3.7: Revenue Estimation page [RENAMED from Revenue Analytics]**
As a GM, I want to see dollar-figure revenue analysis using estimated revenue.
- Total estimated revenue with trend line
- Average transaction value over time
- Revenue by stand
- Revenue per cap scatter (X=attendance, Y=revenue/cap)
- **REMOVED:** Revenue by payment method (was based on mock Stripe data). If desired for visual interest, hardcode industry-standard splits as a single static chart (Visa 40%, MC 25%, Debit 15%, Apple Pay 12%, Google Pay 8%) -- do NOT build a pipeline for it.
- Label all figures as "Estimated Revenue" -- be transparent about the estimation methodology.
- **Business Impact Callout:** "Revenue estimation enables tracking the $180K per-cap gap closure over time."

**US-3.8: Concession Advisor page (chat UI)**
As a GM, I want to ask questions in natural language and get data-backed answers.
- Chat interface using st.chat_message / st.chat_input
- Suggested starter prompts displayed as buttons -- use the 3 pre-scripted questions (see below)
- Tool calls shown in expandable sections
- Integrates with advisor/claude_advisor.py
- Maintains conversation history in session state
- **NEW: Give the Advisor page a distinct visual identity** -- different layout from chart pages, possibly darker background. It should feel like stepping into a different mode of interaction.

### Epic 4: Claude API Advisor (Agent D)

**US-4.1: System prompt**
As Claude, I need context about SOFMC, the 6 stands, product categories, attendance patterns, and my role as a concession analytics advisor.
- **NEW:** System prompt must instruct Claude to always cite specific dollar figures in responses.
- **NEW:** System prompt must include context about the $250K revenue opportunity, per-cap benchmark gap, and key insights (Phillips Bar cross-sell, intermission bottleneck, $1 Dog Night).
- **NEW:** System prompt must instruct Claude to frame answers operationally: "here is what to do" not just "here is what happened."

**US-4.2: Tool definitions (5 tools)** [REDUCED from 7]
As Claude, I have 5 tools available:
1. `query_database(sql)` -- Run SELECT queries against SQLite
2. `get_forecast(opponent, day, attendance, month, is_playoff, promo_event)` -- Demand prediction with item-level and stand-level detail
3. `get_game_summary(game_date)` -- Post-game executive summary with forecast vs. actual comparison
4. `get_prep_sheet(opponent, day, attendance, promo_event)` -- Full inventory prep with stand-level breakdown, staffing, and comparable games
5. `get_product_recommendations()` -- Affinity/bundle suggestions with estimated revenue impact

**[CUT]** ~~`get_anomalies(game_date)`~~ -- removed (anomaly model is optional)
**[CUT]** ~~`get_revenue_analysis(start_date, end_date)`~~ -- removed (no Stripe data; advisor can query estimated_revenue directly via query_database)

**US-4.3: Tool implementations**
As the system, each tool function executes against real SQLite data and ML models.
- query_database: Only allows SELECT, returns JSON with columns and rows
- get_forecast: Calls ml/predict.py, returns category-level AND item-level predictions with stand breakdown
- get_game_summary: Queries all metrics for a game, includes forecast vs. actual if forecast data available, formats as structured summary
- get_prep_sheet: Uses demand forecast + historical comparable games + context-dependent buffer. Returns stand-by-stand, item-by-item prep quantities with staffing recommendation.
- get_product_recommendations: Returns affinity_rules.json top items with estimated revenue impact of bundle adoption

**US-4.4: Multi-turn tool orchestration**
As the chat system, I handle Claude's tool-use loop: send message -> receive tool calls -> execute tools -> return results -> get final response. Max 5 tool rounds per message.

**US-4.5: Pre-scripted demo questions** [NEW]
Three pre-tested questions for the live demo. Test these before the demo and tune system prompt until answers are crisp, specific, and cite dollar figures.

1. **The Operational Question:** "What should we prepare for Friday's game against Vancouver with 4,200 expected fans?"
   - Should trigger: get_forecast + get_prep_sheet
   - Expected output: item-level prep quantities, stand assignments, staffing count, revenue prediction

2. **The Discovery Question:** "Which stand has the biggest missed opportunity and what should we do about it?"
   - Should trigger: query_database (stand-level analysis)
   - Expected output: Phillips Bar insight -- 19K beers, <5% food, $18-25K annual opportunity

3. **The Revenue Question:** "What combo deals would you recommend based on our sales data?"
   - Should trigger: get_product_recommendations
   - Expected output: specific bundle suggestions with estimated revenue uplift and adoption projections

**Backup questions** (if time permits, test these too):
- "How much revenue are we losing during intermissions, and what is the single highest-impact change we could make?"
- "Show me the full impact of Dollar Dog Night -- did it cannibalize other sales or lift the entire game?"
- "If we could only make three changes before next season to close the per-cap gap, what should they be?"

---

## Integration Contracts

### Contract 1: config.py (Agent A creates, all import)
```python
from config import (
    DB_PATH, MODELS_DIR, KNOWN_PRICES, CATEGORY_PRICES,
    LOCATIONS, CATEGORIES, STAND_OPENING_RULES, PROMO_EVENTS
)
```

### Contract 2: SQLite database (Agent A creates, B/C/D query)
```python
import sqlite3
from config import DB_PATH
conn = sqlite3.connect(DB_PATH)
```
Tables: transactions, games, price_lookup
**Removed:** ~~stripe_transactions~~

### Contract 3: ML predict API (Agent B creates, C/D import)
```python
from ml.predict import (
    load_models,
    get_demand_forecast,      # Returns item-level + stand-level predictions
    get_revenue_prediction,
    get_affinity_recommendations,
    get_comparable_games       # NEW: returns 3-5 similar historical games
)
# OPTIONAL: get_anomalies -- only if anomaly model is built
```

### Contract 4: Claude advisor (Agent D creates, C's page 7 imports)
```python
from advisor.claude_advisor import chat
response_text, updated_messages = chat(messages_list)
```

---

## Build Order

```
Phase 1 (0:00 - 0:50) -- All 4 agents work in parallel:
  Agent A: config.py + data_foundation/*.py (load_data, price_lookup, build_all)
  Agent B: ml/train_demand.py + train_revenue.py + train_affinity.py
           (can use raw CSVs initially; skip anomaly model for now)
  Agent C: dashboard/app.py + all page scaffolds with placeholder data
           Focus on: Season KPIs, Game Explorer, Forecasting page layout
  Agent D: advisor/*.py (system prompt, tool definitions, stubs)

Phase 2 (0:50 - 1:10) -- Data pipeline:
  Agent A: Run build_all.py -> creates royals.db with transactions + games + price_lookup
  Agent B: Run training scripts against DB -> creates .joblib files + affinity_rules.json
  Agent C: Continue building pages -- Intermission Analysis heatmap, Stand Performance
  Agent D: Continue system prompt tuning, implement tool function bodies

Phase 3 (1:10 - 1:50) -- Integration:
  Agent B: Implement predict.py with real model loading, get_comparable_games()
           If time permits: train_anomaly.py (optional)
  Agent C: Replace placeholders with real DB queries and model outputs
           Wire up: per-cap benchmark gap, business impact callouts, prep sheet UI
  Agent D: Implement all 5 tool function bodies against real data
           Test the 3 pre-scripted demo questions

Phase 4 (1:50 - 2:20) -- Polish & Integration:
  All: Fix integration bugs
  Agent C: Add forecast vs. actual toggle, $1 Dog Night callout, print prep sheet button
  Agent D: Tune Claude responses -- ensure dollar figures, actionable recommendations
  All: Test full demo flow end to end

Phase 5 (2:20 - 2:30) -- Demo prep:
  Test the 10-minute demo narrative
  Verify Claude API works with all 3 scripted questions
  Screenshot backup of best advisor responses (in case of API failure)
  Pre-type the 3 demo questions in a notes app for quick paste
```

---

## Demo Flow (10 minutes) -- Problem-Solution Narrative

This is NOT a dashboard tour. This is a story about finding $250K in revenue.

| Time | Beat | What to Show | What to Say |
|------|------|-------------|-------------|
| 0:00-0:30 | **The Hook** | Title slide (team name, platform name, headline) | "Every intermission at SOFMC, hundreds of fans walk away from the concession line empty-handed. That is $80K-$120K walking back to their seats every season. We built a platform to find that money -- and every other dollar being left on the table." |
| 0:30-1:30 | **The Data** | Season KPIs page -- hit the per-cap benchmark gap hard | "This is real data. 239,000 transactions. 67 games. Two full seasons from Matt Cooke. Per-cap spend is $11.77. The WHL average is $14-16. That gap? That is $180K-$342K per year." |
| 1:30-3:00 | **The Discovery** | Intermission Analysis heatmap + Game Explorer on $1 Dog Night or playoff game | "This heatmap is the smoking gun. Every bright band is a traffic jam. Every gap is money left on the table. And look at this -- Dollar Dog Night: 1,167 hot dog transactions. 30% of all sales. Proof that data-driven promotions work." |
| 3:00-4:30 | **The Operations** | Stand Performance -- Phillips Bar callout. Quick Game Explorer drill-down. | "Phillips Bar sold 19,000 beers with virtually zero food. That is $18-25K in annual cross-sell revenue just waiting to happen. The platform identifies these opportunities automatically." |
| 4:30-6:00 | **The Prediction** | Forecasting page -- input Friday, Vancouver, 4,200 fans -- show prep sheet | "Friday night. Vancouver is in town. 4,200 fans expected. Here is EXACTLY what to stock, where to staff, and how much revenue to expect. This prep sheet goes to stand leads at 4 PM." |
| 6:00-6:30 | **The Bridge** | Transition moment | "But a GM does not want to click through dashboards. A GM wants to ask questions and get answers. So we built an advisor." |
| 6:30-9:30 | **The Advisor** | Claude Advisor -- 3 pre-scripted questions, live | Q1: "What should we prepare for Friday's game against Vancouver with 4,200 expected fans?" Q2: "Which stand has the biggest missed opportunity?" Q3: "What combo deals would you recommend?" |
| 9:30-10:00 | **The Close** | Summary | "This platform identifies $250K in annual revenue opportunity. It runs on a laptop. No cloud. No setup. A GM could use this tomorrow. This is what happens when you turn 239,000 transactions into intelligence." |

**Presenter must-say lines:**
1. "This is real data. 239,000 transactions. 67 games. Two full seasons. Given to us by the GM."
2. "The per-cap spend at SOFMC is $11.77. The WHL average is $14-16. That gap is why we are here."
3. "This runs on a laptop. No cloud. No setup. A GM could use this tomorrow."

---

## Pre-Scripted Claude Advisor Questions

These questions MUST be tested before the demo. Have them pre-typed in a notes app for quick paste.

**Question 1 -- The Operational Question:**
> "What should we prepare for Friday's game against Vancouver with 4,200 expected fans?"

Expected behavior: Triggers get_forecast + get_prep_sheet. Returns item-level prep quantities, stand assignments, staffing, revenue prediction. Should feel like a complete game-day operations plan.

**Question 2 -- The Discovery Question:**
> "Which stand has the biggest missed opportunity and what should we do about it?"

Expected behavior: Triggers query_database. Surfaces Phillips Bar insight with specific dollar figures. Should recommend adding food items and estimate the revenue impact.

**Question 3 -- The Revenue Question:**
> "What combo deals would you recommend based on our sales data?"

Expected behavior: Triggers get_product_recommendations. Returns specific bundles (e.g., "Beer + Pretzel combo at $13.99"), estimated adoption rate, and projected revenue uplift.

**Demo execution tips:**
- Pre-load conversation history so responses are fast (no cold start).
- If a response is long, narrate over it: "Look -- it is pulling from our demand model AND the transaction database to give a compound answer."
- If something breaks, have a backup screenshot of a successful response ready.

---

## Acceptance Criteria

- [ ] `run.sh` builds everything and launches Streamlit in one command
- [ ] All 7 dashboard pages load without errors
- [ ] SQLite database contains 239K+ transactions and ~67 games
- [ ] Estimated revenue computed for all transactions using price lookup (no Stripe dependency)
- [ ] ML demand model trains and produces item-level + stand-level predictions
- [ ] Forecasting prep sheet shows item-level quantities with stand breakdown
- [ ] Forecasting page includes stand opening recommendation and staffing suggestion
- [ ] Per-cap benchmark gap visualization on Season KPIs page ($11.77 vs $14-16)
- [ ] Business Impact Callout card on every dashboard page with specific dollar figures
- [ ] Claude advisor answers the 3 pre-scripted questions using real data via tools
- [ ] Forecast vs. actual toggle works on Game Explorer for historical games
- [ ] Demo runs entirely on laptop, no cloud dependencies
- [ ] ANTHROPIC_API_KEY env var is the only external dependency
