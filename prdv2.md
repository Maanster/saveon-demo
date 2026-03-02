# PRD v2: Royals Concession Intelligence Platform
## Post-GM Meeting Sprint — Parallel Agent Build

---

## What Changed from v1

| # | Change | Source |
|---|--------|--------|
| 1 | **[REFRAMED] 24-Hour Advance Prediction is THE feature** — GM confirmed: predict the day before, hand prep sheet to cooks at 4 PM. Not real-time. | GM meeting |
| 2 | **[NEW] Kitchen Production Planner** — food production is the bottleneck. Predict cook times, prep sequences, pre-production quantities for grab-and-go items. | GM: "greatest bottleneck is how fast they can produce food" |
| 3 | **[NEW] Order Velocity Prediction** — predict not just WHAT but HOW FAST orders come in, by period. "How fast are they going to order" per stand per period. | GM meeting |
| 4 | **[NEW] Weather Integration** — real OpenWeatherMap API call for Victoria BC. Cold = hot chocolate/coffee spike. Rain = covered stand preference. | Innovation differentiator |
| 5 | **[NEW] Dynamic Pricing Engine page** — surge/discount modeling for intermission demand redistribution. | Innovation differentiator |
| 6 | **[NEW] Fan Mobile Pre-Order Mock** — phone-styled UI showing "order from your seat". Shows full ecosystem vision. | Innovation + CMO feedback: missing fan perspective |
| 7 | **[NEW] Predictive Alerts System** — stockout warnings, staffing redeployment, revenue milestones during simulated games. | Innovation differentiator |
| 8 | **[UPGRADED] Forecasting Page** — add "Email/Export Prep Sheet" with PDF-style output, kitchen production timeline, food prep sequence. | GM: "handed off to the cooks in the back house" |
| 9 | **[UPGRADED] Game Simulator** — add live predictive alerts overlay, command center feel with real-time KPIs. | Innovation differentiator |
| 10 | **[UPGRADED] Slides** — expand from 5 to 8-10 slides covering innovation story, GM validation, and live demo screenshots. | Presentation improvement |
| 11 | **[UPGRADED] Claude Advisor** — add weather-aware tool, dynamic pricing tool, velocity prediction tool. Expand from 5 to 8 tools. | Innovation + richer advisor |

---

## GM Meeting Key Quotes (Design Constraints)

These quotes drive every design decision in v2:

1. **"Goal would be to predict the day before — handed off to the cooks in the back house"**
   - Prep sheet must be exportable as a kitchen-ready document
   - Must include food production timelines (when to start cooking what)

2. **"We are not looking for real time prediction, we are looking to inform decisions 24 hours in advance for staffing decisions"**
   - 24-hour advance is the sweet spot. Not real-time, not weekly.
   - Staffing + prep are the two key outputs

3. **"Greatest bottleneck is how fast they can produce food"**
   - Food production capacity is the constraint, not demand
   - Need to model: if we know 480 hot dogs will sell, start grilling at 5:30 PM, batch 1 ready by 6:00 PM

4. **"We want to be able to grab and go — get the chicken tenders ahead if we know they are going to sell out"**
   - Pre-production is the goal. Cook BEFORE demand hits.
   - Identify items that sell out and pre-stage them

5. **"How fast are they going to order / how many are they going to order"**
   - Two predictions: quantity AND velocity
   - Velocity by period matters for kitchen staging

6. **"Seems very predictable but haven't taken the time to predict"**
   - GM validates the model concept — they KNOW it's predictable, they just don't have the tool
   - This is a credibility win for our pitch

---

## Current State (What's Already Shipped)

All 9 pages working with dark Royals theme, inline filters, horizontal nav:

| Page | Status | Key Features Working |
|------|--------|---------------------|
| Home | Done | KPIs, feature lists, $250K callout |
| Season KPIs | Done | Per-cap hero, WHL benchmark gap gauge, donut chart, $1 Dog Night |
| Game Explorer | Done | Game selector, category/stand filters, forecast vs actual, timeline |
| Stand Performance | Done | Stacked bar, Phillips Bar cross-sell alert, drill-down |
| Intermission | Done | Heatmap with gold boundaries, lost revenue slider, period bars |
| Forecasting | Done | Inline form, ML-powered prep sheet, comparable games, download |
| Revenue | Done | KPIs, line charts, scatter plot, WHL benchmark line |
| Advisor | Done | Settings expander, 3 starter prompts, chat with tool display |
| Simulator | Done | Period clock, stand cards, cumulative charts, transaction stream |

ML models trained: demand_forecast.joblib (7MB), revenue_predictor.joblib (1.4KB), affinity_rules.json (6.1KB)

Claude advisor: 5 tools working (query_database, get_forecast, get_game_summary, get_prep_sheet, get_product_recommendations)

---

## New Features to Build

### Feature 1: Kitchen Production Planner (on Forecasting page)
**Priority: CRITICAL — This is the GM's #1 ask**

Add a new section below the existing prep sheet on the Forecasting page:

**Kitchen Production Timeline:**
A visual timeline showing WHEN to start cooking each food item based on predicted demand velocity.

```
KITCHEN PRODUCTION SCHEDULE — Friday vs Vancouver, 4,200 fans

Pre-Game Prep (3:00 PM - 5:30 PM):
  [===] Thaw 480 hot dogs (start 3:00 PM)
  [===] Prep 120 chicken tender batches (start 3:30 PM)
  [===] Pre-roll 200 pretzels (start 4:00 PM)
  [===] Prep pizza dough x 80 (start 4:30 PM)

Pre-Game Service (5:30 PM - 7:00 PM):
  [==] Grill batch 1: 120 hot dogs (ready by 5:45 PM)
  [==] Fryer batch 1: 40 chicken tenders (ready by 5:50 PM)
  [==] Oven batch 1: 30 pretzels (ready by 6:00 PM)

1st Intermission Rush (predicted 7:45-8:05 PM):
  [!] HIGH DEMAND WINDOW — pre-stage grab-and-go items by 7:30 PM
  [==] Grill batch 2: 160 hot dogs (start 7:15 PM, ready 7:35 PM)
  [==] Fryer batch 2: 60 chicken tenders (start 7:20 PM, ready 7:40 PM)
  [!] SELLOUT RISK: Hot dogs at Island Canteen — transfer 40 units from Portable

2nd Intermission Rush (predicted 9:00-9:20 PM):
  [==] Grill batch 3: 100 hot dogs (start 8:40 PM)
  [==] Fryer batch 3: 30 chicken tenders (start 8:45 PM)
```

**Implementation:**
- Use the existing demand forecast (by_item dict from predict.py)
- Distribute predicted quantities across game periods using historical period proportions (already in DB)
- Add FOOD_PREP_TIMES to config.py: {"Hot Dog": 15, "Chicken Tenders": 20, "Pretzel": 25, "Pizza": 18, ...} (minutes)
- Add BATCH_SIZES to config.py: {"Hot Dog": 40, "Chicken Tenders": 20, "Pretzel": 15, "Pizza": 10}
- Calculate: if 160 hot dogs needed for 1st intermission at 7:45 PM, and batch = 40, cook time = 15 min → start 4 batches at 7:15 PM
- Render as a Streamlit timeline using plotly gantt chart or custom HTML
- Add "Print Kitchen Schedule" button (separate from prep sheet download)

**Acceptance Criteria:**
- [ ] Timeline shows food items with start times, ready times, and batch quantities
- [ ] Pre-intermission staging alerts ("have X ready by Y:ZZ PM")
- [ ] Sellout risk warnings for high-demand items
- [ ] Exportable as text/PDF alongside prep sheet

---

### Feature 2: Order Velocity Prediction
**Priority: HIGH — Answers "how fast are they going to order"**

Add to both the Forecasting page and the Advisor tools:

**What it predicts:** Units per 5-minute window, by stand, across the game timeline.

**Visualization on Forecasting page:**
- Predicted transaction velocity chart (same style as intermission heatmap but for a FUTURE game)
- X-axis: time (5:30 PM - 10:00 PM), Y-axis: predicted transactions per 5 min
- Overlay: period boundaries, intermission peaks highlighted
- Per-stand breakdown available via tabs

**Implementation:**
- Query historical transaction velocity: GROUP BY game_period, 5-min bucket, stand
- Weight by attendance similarity to predicted game
- Scale velocity proportionally to predicted total demand
- Output: dict of {time_bucket: {stand: predicted_units}}

**New predict.py function:**
```python
def get_velocity_forecast(attendance, day_of_week, is_playoff=False, promo_event="Regular"):
    """Returns predicted units per 5-min bucket per stand."""
    # Use historical velocity profile scaled to predicted total demand
    return {
        "total_by_bucket": {"17:30": 12, "17:35": 15, ...},
        "by_stand": {
            "SOFMC Island Canteen": {"17:30": 5, ...},
            ...
        },
        "peak_periods": [
            {"time": "19:45-20:05", "label": "1st Intermission", "predicted_units": 340},
            ...
        ]
    }
```

**New advisor tool:**
```python
get_velocity_forecast(attendance, day_of_week, is_playoff, promo_event)
```

---

### Feature 3: Weather Integration
**Priority: HIGH — Easy win, strong innovation signal**

**Data source:** OpenWeatherMap API (free tier, 1000 calls/day)
- Endpoint: `api.openweathermap.org/data/2.5/forecast?q=Victoria,CA&appid={KEY}`
- Returns 5-day forecast with temp, conditions, wind, humidity

**Integration points:**

1. **Forecasting page:** Auto-populate weather for selected game date (if within 5-day window)
   - Display weather card: temp, conditions, icon
   - Adjust predictions: cold weather modifier (+15% hot beverages, -10% cold beverages), rain modifier (+5% covered stands, -20% outdoor stands like Portable)

2. **Config.py additions:**
```python
WEATHER_MODIFIERS = {
    "cold": {"threshold_c": 5, "hot_bev_boost": 0.15, "cold_bev_drop": -0.10},
    "rain": {"outdoor_drop": -0.20, "covered_boost": 0.05},
    "warm": {"threshold_c": 20, "cold_bev_boost": 0.10, "hot_bev_drop": -0.05},
}
```

3. **Advisor tool:**
```python
get_weather_forecast(date)  # Returns Victoria BC weather for game date
```

4. **Prep sheet enhancement:** Weather-adjusted quantities with note: "Weather adjustment: +15% hot beverages (forecast: 3C, rain)"

**Fallback:** If no API key or API fails, skip weather — don't break the page. Show "Weather data unavailable" gracefully.

---

### Feature 4: Dynamic Pricing Engine (New Page)
**Priority: MEDIUM — Strong innovation differentiator for judges**

New page between Revenue and Advisor: **"Pricing Intelligence"**

**Concept:** Model the impact of price changes on demand distribution across game periods.

**Sections:**

1. **Current Pricing Overview**
   - Table of top 20 items with current prices
   - Revenue contribution per item

2. **Intermission Demand Redistribution Simulator**
   - Interactive: "If we drop beer price by $X during 2nd period..."
   - Sliders: discount amount ($0.50 - $3.00), target period (2nd period, pre-game)
   - Output: predicted demand shift (% moving from intermission to target period), queue reduction estimate, net revenue impact
   - Based on price elasticity assumptions from literature (beer elasticity -0.3 to -0.7)

3. **Promotional ROI Calculator**
   - Input: promotional price (e.g., $1 hot dog, $5 beer)
   - Compare: $1 Dog Night actual data vs normal game
   - Model: "At $2 hot dogs, we predict X% of the $1 Dog Night volume lift at Y% higher margin"
   - Show breakeven analysis

4. **Combo Pricing Optimizer**
   - Uses affinity data to suggest bundles
   - Interactive: adjust combo discount %, see predicted adoption and revenue impact
   - Already have affinity_rules.json — enhance with pricing sensitivity

**Business Impact Callout:** "Strategic pricing can redistribute 15-20% of intermission demand to off-peak periods, recovering $40K-$60K in lost queue-abandonment revenue annually."

---

### Feature 5: Fan Mobile Pre-Order Mock (New Page)
**Priority: MEDIUM — Completes the ecosystem story**

New page: **"Fan Experience"** — styled as a phone screen mockup

**Layout:** Center-aligned, max-width 375px container styled like an iPhone, dark background.

**Mock Screens (tabs or stepper):**

1. **Browse Menu** — items grouped by stand, with prices and photos (placeholder icons)
2. **Select Stand & Pickup Time** — "Pick up at Phillips Bar during 1st intermission"
3. **Order Confirmation** — "Your chicken tenders + beer will be ready at 7:50 PM at Window B"
4. **Order Status** — "Preparing... Ready for pickup!"

**Data connection:** Use real menu items and prices from config.py/price_lookup table.

**Business Impact Callout:** "Mobile pre-ordering shifts 20-30% of intermission demand to pre-game prep windows, reducing peak queue length by 35% and recovering $60K-$80K in abandoned sales annually."

**Note:** This is a MOCK. No backend. Pure UI demonstration of the vision.

---

### Feature 6: Predictive Alerts on Game Simulator
**Priority: MEDIUM — Makes the simulator a command center**

Enhance the existing game_simulator.py with an alerts panel:

**Alert Types:**
1. **Stockout Warning** — "Hot Dogs at Island Canteen: 45 remaining, burn rate 12/min. Stockout in 3.7 min."
2. **Staffing Redeployment** — "2nd intermission in 90 seconds. Deploy +2 staff to Island Canteen."
3. **Revenue Milestone** — "Game revenue hit $12,000 — tracking for top-5 game this season."
4. **Velocity Spike** — "Phillips Bar orders 40% above forecast. Investigate: visiting team fan effect?"
5. **Pre-Intermission Prep** — "1st intermission in 5 min. Pre-stage 80 hot dogs, 40 pretzels at Island Canteen."

**Implementation:**
- Add alerts list to session state
- During simulation loop, evaluate alert conditions each tick
- Display as a scrolling feed alongside the existing stand cards
- Color-code: red (stockout), orange (staffing), green (milestone), blue (info)

---

### Feature 7: Expanded Claude Advisor (8 tools)
**Priority: HIGH — Core differentiator gets richer**

Add 3 new tools to the existing 5:

**Tool 6: `get_velocity_forecast(attendance, day_of_week, is_playoff, promo_event)`**
- Returns predicted transaction velocity by 5-min bucket and by stand
- Enables questions like "When will the biggest rush hit Phillips Bar on Friday?"

**Tool 7: `get_weather_impact(game_date)`**
- Returns weather forecast for Victoria BC + predicted impact on concession categories
- Enables: "How will Friday's weather affect beer sales?"
- Falls back gracefully if no API key

**Tool 8: `get_pricing_analysis(item, current_price, proposed_price)`**
- Returns elasticity estimate, demand change prediction, revenue impact
- Enables: "What happens if we drop beer to $7.99 during 2nd period?"

**Updated pre-scripted demo questions (5 total):**

1. **The Operational Question:** "What should we prepare for Friday's game against Vancouver with 4,200 expected fans and 3C rain forecast?"
   - Triggers: get_forecast + get_prep_sheet + get_weather_impact
   - Shows: Weather-adjusted prep with kitchen timeline

2. **The Discovery Question:** "Which stand has the biggest missed opportunity and what should we do about it?"
   - Triggers: query_database
   - Shows: Phillips Bar insight with dollar figures

3. **The Velocity Question:** "When will the biggest rush hit on Friday night and how should we pre-stage food?"
   - Triggers: get_velocity_forecast
   - Shows: Period-by-period velocity with pre-staging recommendations

4. **The Pricing Question:** "What would happen if we offered a $12.99 beer and pretzel combo?"
   - Triggers: get_pricing_analysis + get_product_recommendations
   - Shows: Adoption estimate, revenue impact, margin analysis

5. **The Revenue Question:** "What combo deals would you recommend based on our sales data?"
   - Triggers: get_product_recommendations
   - Shows: Specific bundles with revenue projections

---

## Updated Slide Deck (slides.html)

Expand from 5 to 10 slides:

| Slide | Title | Content |
|-------|-------|---------|
| 1 | Title | "Royals Concession Intelligence Platform" + tagline + team name |
| 2 | The Problem | Per-cap gap visual: $11.77 vs $14-$16 WHL = $180K-$342K gap |
| 3 | The Opportunity | $250K revenue roadmap table (5 levers) |
| 4 | GM Validation | Quote: "Seems very predictable but haven't taken the time to predict" + "The goal is to predict the day before" |
| 5 | The Platform | Screenshot placeholder + 6 feature cards (KPIs, Explorer, Forecasting, Advisor, Pricing, Fan Experience) |
| 6 | Innovation: 24-Hour Prediction | Kitchen production timeline mockup + "Predict → Prep → Profit" |
| 7 | Innovation: Intelligence Layer | Weather integration + dynamic pricing + velocity forecasting |
| 8 | Innovation: Fan Experience | Mobile pre-order mock + "The future of arena concessions" |
| 9 | Live Demo | "Let's show you" — transition slide |
| 10 | Close | "239K transactions. $250K opportunity. Runs on a laptop. A GM could use this tomorrow." + tech stack |

---

## Agent Build Plan (Parallel Execution)

```
AGENT A: Kitchen & Forecasting Upgrades
  ├── Add FOOD_PREP_TIMES + BATCH_SIZES to config.py
  ├── Add kitchen production timeline to Forecasting page
  ├── Add velocity prediction to predict.py (get_velocity_forecast)
  ├── Add velocity chart to Forecasting page
  └── Enhance prep sheet download with kitchen schedule

AGENT B: Innovation Pages
  ├── Build Dynamic Pricing Engine page (new page)
  ├── Build Fan Mobile Pre-Order mock page (new page)
  ├── Add pages to app.py navigation
  └── Business impact callouts on both new pages

AGENT C: Weather + Simulator Upgrades
  ├── Add weather API integration (utils/weather.py)
  ├── Add weather card to Forecasting page
  ├── Add weather-adjusted prep quantities
  ├── Upgrade Game Simulator with predictive alerts overlay
  └── Add alert conditions + scrolling feed to simulator

AGENT D: Advisor + Slides
  ├── Add 3 new tools to advisor/tools.py (velocity, weather, pricing)
  ├── Update tool schemas in advisor/claude_advisor.py
  ├── Update system prompt in advisor/prompts.py
  ├── Update 5 pre-scripted demo questions on Advisor page
  └── Rebuild slides.html (10 slides with GM quotes + innovation story)

AGENT E: Polish & Integration
  ├── Run full app and fix any import/runtime errors
  ├── Test all 5 advisor demo questions end-to-end
  ├── Verify all page navigation works
  ├── Screenshot best pages for slides
  └── Final theme/styling pass
```

**Dependency graph:**
- Agents A, B, C, D can start in parallel (independent pages/features)
- Agent E starts after A, B, C, D complete (integration testing)
- Agent D's advisor tools depend on Agent A's velocity function and Agent C's weather function (but can stub initially)

---

## Integration Contracts (v2 additions)

### Contract 5: Weather API (Agent C creates, A/D consume)
```python
# utils/weather.py or similar
def get_victoria_weather(date_str: str = None) -> dict:
    """Returns weather for Victoria BC. Needs OPENWEATHER_API_KEY env var."""
    return {
        "temperature_c": 3.0,
        "conditions": "Rain",
        "wind_kph": 15,
        "humidity": 85,
        "icon": "rain",
        "forecast_available": True,
        "modifiers": {
            "hot_bev_boost": 0.15,
            "cold_bev_drop": -0.10,
            "outdoor_stand_drop": -0.20
        }
    }
```

### Contract 6: Velocity Forecast (Agent A creates, D consumes)
```python
from ml.predict import get_velocity_forecast

result = get_velocity_forecast(attendance=4200, day_of_week="Friday")
# Returns:
# {
#     "total_by_bucket": {"17:30": 12, "17:35": 18, ...},
#     "by_stand": {"SOFMC Island Canteen": {"17:30": 5, ...}, ...},
#     "peak_periods": [{"time": "19:45", "label": "1st Intermission", "predicted_units": 340}]
# }
```

### Contract 7: Pricing Analysis (Agent B creates, D consumes)
```python
# Can live in advisor/tools.py or separate module
def get_pricing_analysis(item, current_price, proposed_price):
    return {
        "item": "Beer",
        "current_price": 9.49,
        "proposed_price": 7.99,
        "price_change_pct": -15.8,
        "estimated_demand_change_pct": 8.5,  # Based on elasticity
        "estimated_revenue_impact": -2400,  # Per season
        "demand_redistribution": {"from_intermission": -12, "to_2nd_period": +8},
        "notes": "Beer elasticity estimated at -0.5. Lower price during off-peak shifts demand but reduces per-unit margin."
    }
```

---

## Config.py Additions

```python
# Food production parameters (for kitchen timeline)
FOOD_PREP_TIMES = {
    "Hot Dog": {"cook_minutes": 15, "batch_size": 40, "prep_type": "grill"},
    "Chicken Tenders": {"cook_minutes": 20, "batch_size": 20, "prep_type": "fryer"},
    "Pretzel": {"cook_minutes": 25, "batch_size": 15, "prep_type": "oven"},
    "Pizza": {"cook_minutes": 18, "batch_size": 10, "prep_type": "oven"},
    "Nachos": {"cook_minutes": 8, "batch_size": 25, "prep_type": "assembly"},
    "Taco": {"cook_minutes": 12, "batch_size": 15, "prep_type": "grill"},
    "Fries": {"cook_minutes": 10, "batch_size": 30, "prep_type": "fryer"},
    "Popcorn": {"cook_minutes": 5, "batch_size": 50, "prep_type": "machine"},
}

FOOD_ITEMS = list(FOOD_PREP_TIMES.keys())

# Price elasticity estimates (from sports venue literature)
PRICE_ELASTICITY = {
    "Beer": -0.5,
    "Cocktail": -0.4,
    "Wine": -0.3,
    "NA Bev": -0.8,
    "Food": -0.6,
    "Snacks": -0.7,
}

# Weather API
OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/forecast"
WEATHER_MODIFIERS = {
    "cold": {"threshold_c": 5, "hot_bev_boost": 0.15, "cold_bev_drop": -0.10},
    "rain": {"outdoor_drop": -0.20, "covered_boost": 0.05},
    "warm": {"threshold_c": 20, "cold_bev_boost": 0.10, "hot_bev_drop": -0.05},
}
```

---

## Acceptance Criteria (v2)

Carried from v1 (all already passing):
- [x] `run.sh` builds everything and launches Streamlit
- [x] All dashboard pages load without errors
- [x] SQLite database contains 239K+ transactions and ~67 games
- [x] ML demand model trained with item-level + stand-level predictions
- [x] Forecasting prep sheet shows item-level quantities with stand breakdown
- [x] Per-cap benchmark gap visualization on Season KPIs page
- [x] Business Impact Callout on every page
- [x] Claude advisor answers questions using real data via tools
- [x] Demo runs entirely on laptop

New for v2:
- [ ] Kitchen production timeline on Forecasting page with cook times and batch scheduling
- [ ] Velocity prediction chart showing orders per 5-min bucket
- [ ] Weather integration on Forecasting page (with graceful fallback)
- [ ] Dynamic Pricing Engine page with intermission redistribution simulator
- [ ] Fan Mobile Pre-Order mock page with phone-styled UI
- [ ] Game Simulator has predictive alerts overlay (stockout, staffing, revenue)
- [ ] Claude advisor has 8 tools (added: velocity, weather, pricing)
- [ ] 5 pre-scripted advisor demo questions tested and working
- [ ] Slides updated to 10 slides with GM quotes and innovation story
- [ ] All new pages accessible from horizontal nav bar
