# Business Strategy Review: Royals Concession Intelligence Platform PRD
## VP of Business Strategy Analysis -- Hackathon MVP

**Reviewer:** Business Strategy Advisor
**Date:** 2026-02-27
**Time Remaining:** ~2.5 hours to build

---

## 1. Value Assessment: Business Impact Score

**Rating: 7.5 / 10**

**What is working well:**

- The PRD is grounded in real data (239K transactions, 67 games, 2 seasons). This is not a toy demo with fake data -- judges will immediately recognize the difference. The fact that you are working with actual SOFMC POS exports gives every insight credibility.
- The platform covers all three business impact levers the judges care about: revenue growth (combos, forecasting, upselling), cost reduction (demand prediction, staffing optimization), and customer experience (intermission bottleneck, advisor recommendations).
- The Claude-powered Concession Advisor with 7 tools is genuine product differentiation. This is not a ChatGPT wrapper -- it is an AI agent that can query a real database, run ML predictions, and generate actionable prep sheets. That is a real product concept.
- The demo flow is well-sequenced, ending with the "wow moment" of live AI conversation.

**What is holding this back from a 9 or 10:**

- The PRD is technically comprehensive but **business-narrative thin**. It reads like an engineering spec, not a business case. Judges score on Business Impact first. The PRD never explicitly states the headline revenue number. It never says: "This platform enables $X in incremental annual revenue." That single sentence needs to be baked into every page of the dashboard.
- The Stripe mock data (US-1.5) is clever engineering but adds limited business value relative to its build complexity. Judges do not care whether you simulated Stripe transactions. They care whether you can show that Phillips Bar is leaving $18K/year on the table by not selling food.
- The anomaly detection model (US-2.2) is technically interesting but has no clear business story. "This game was anomalous" -- so what? What does the GM do differently? Without a recommended action, anomaly detection is academic.
- Revenue Analytics (page 6) based on mock Stripe data is risky. If judges probe, you are showing revenue charts built on synthetic data generated from data that already lacked prices. That is two layers of estimation. Better to own the estimation openly than hide it behind a "Stripe" facade.

---

## 2. Revenue Story Gaps

### Gap 1: No explicit "Per-Cap Gap to Benchmark" visualization

This is your single most powerful business argument. You have the data to show:
- Current per-cap: $11.77
- WHL peer benchmark: $14-$16
- Gap: $2.23-$4.23 per fan per game
- At 2,600 avg attendance x 31 games = **$180K-$342K left on the table annually**

This needs to be front and center on the Season KPIs page -- not buried in a report. A simple gauge chart showing "Where We Are vs. Where We Should Be" is worth more than any ML model.

### Gap 2: The intermission bottleneck is mentioned but not quantified in the dashboard

The PRD describes an Intermission Analysis page (US-3.5) with a heatmap and a "lost revenue estimator" slider. Good. But the business story needs to hit harder:
- Show the exact 18-minute window where transaction velocity spikes and then crashes
- Calculate the gap between demand (fans wanting to buy) and throughput (transactions completed)
- Put a dollar figure on it: **$80K-$120K lost per season**
- Then show the AI-recommended solution: "If you add one express grab-and-go station, you recover $50K-$80K"

The slider is nice. But judges want you to tell them the answer, not ask them to find it.

### Gap 3: Phillips Bar cross-sell opportunity is invisible

Your research reports identify Phillips Bar as selling 19K+ beers with virtually zero food. That is arguably the single most actionable, lowest-cost insight in the entire dataset. The Stand Performance page (US-3.4) will show category mix per stand, but the PRD does not call out a specific "Missed Upsell Alert" feature.

The advisor could answer this if asked, but you should not rely on the judge asking the right question. Bake it into the Stand Performance page as a callout box: "Phillips Bar: 19,000 beer transactions, <5% food attach rate. Adding simple food items could generate $18K-$25K/season."

### Gap 4: No cost-savings narrative

The judges listed "Decreasing Cost" as a success metric. The PRD's ML models support this (demand forecasting for inventory prep, attendance-based staffing), but the dashboard pages do not surface a cost-savings number. The Forecasting page (US-3.6) shows a prep sheet, but it does not say: "Using this model instead of guessing saves you $15K-$25K in food waste and $20K-$35K in labor costs."

### Gap 5: $1 Dog Night is an unsung hero

Your data shows $1 Dog Night generated 1,167 hot dog transactions -- 30% of all transactions that night. That is a promotional ROI story begging to be told. It proves promotional pricing drives massive volume. The dashboard should have this as a callout somewhere: proof that data-driven promotions work.

---

## 3. Differentiation: What Makes This Stand Out

### Current "Wow Factor" Assessment: Strong, but fragile

**Strong differentiators:**
1. **Real data, real venue.** Most hackathon teams use synthetic datasets. You have 239K real transactions from the actual arena the judges manage. This is powerful.
2. **Claude Advisor with tool use.** An AI agent that can query the database, run forecasts, and generate prep sheets in natural language is genuinely impressive. If it works live, this wins the demo.
3. **Actionable outputs (prep sheets, staffing recommendations).** This goes beyond dashboards into decision-support. The "print this and hand it to the stand manager" use case is tangible.

**Weak differentiators (things that do NOT set you apart):**
1. **Generic dashboard charts.** Bar charts of category breakdown, donut charts of revenue mix -- every team with a data analyst will have these. These are table stakes, not differentiators.
2. **ML model names.** Saying "GradientBoostingRegressor" or "IsolationForest" does not impress business judges. They care about what the model DOES ("predicts how many hot dogs to prep for Friday's game"), not what it IS.
3. **Mock Stripe data.** This sounds impressive technically but actually weakens credibility. You are generating fake payment data from real POS data that already lacks prices. Judges will probe this.

### What would make this a 10/10 on differentiation:

- **The "One Question" demo:** Start the Claude Advisor demo with: "We just learned Vancouver is coming on Friday, expected attendance 4,200. What should we do?" Then watch Claude call 3-4 tools and return a complete game-day operations plan: prep quantities, staffing levels, recommended combos to push, expected revenue. THAT is a wow moment that no dashboard alone can deliver.
- **Before/After framing:** Show a split screen -- "Here is what the GM does today (guesses based on experience)" vs. "Here is what the platform recommends (data-driven, with confidence intervals)." Make the pain of the current state visceral.

---

## 4. Scope Risks for 2.5 Hours: What to Cut

### CRITICAL: You have 2.5 hours and 4 agents. Scope must be ruthless.

### CUT or drastically simplify:

| Item | Reason to Cut | Time Saved |
|------|--------------|------------|
| **US-1.5: Mock Stripe data generation** | High complexity, low business value. Generating 90-110K synthetic payment transactions is engineering busywork. Revenue estimation from POS data is sufficient. If you need dollar figures, use estimated_revenue directly -- do not build a fake Stripe layer. | 30-45 min |
| **US-3.7: Revenue Analytics page (Stripe-based)** | If you cut Stripe mock data, this page becomes simpler. Replace it with a "Revenue Estimation" page that uses your price lookup directly. Same charts, no Stripe fiction. | 15-20 min |
| **US-2.2: Anomaly detection model** | Lowest business value of the 4 ML models. No clear "so what" action for the GM. The anomaly badge on Game Explorer is a nice-to-have. If it works, great; if not, skip it. | 20-30 min |
| **7 Claude tools down to 4-5** | `get_anomalies` can be cut if anomaly model is cut. `get_revenue_analysis` can be simplified if Stripe data is cut. Focus on: `query_database`, `get_forecast`, `get_game_summary`, `get_prep_sheet`, `get_product_recommendations`. | 15-20 min |
| **Custom CSS/branding polish** | Purple/gold theme is nice but do not spend more than 10 minutes on it. Streamlit's default theme with a logo in the sidebar is fine. | 15-20 min |

### Total time recovered: ~90-120 minutes of buffer

### DO NOT CUT:

| Item | Why It Must Stay |
|------|-----------------|
| **US-1.2: CSV ingestion + price estimation** | This is the foundation. Everything depends on it. |
| **US-1.3: Games table** | Attendance data drives the entire business story. |
| **US-2.1: Demand forecasting** | This is the core ML value proposition. |
| **US-2.4: Product affinity** | Directly supports the combo/upsell revenue story. |
| **US-3.2: Season KPIs** | The opening slide of the demo. Must be polished. |
| **US-3.5: Intermission Analysis** | The $80-120K lost revenue story. High impact. |
| **US-3.6: Forecasting page** | The "predict Friday's game" demo moment. |
| **US-3.8: Concession Advisor** | The wow moment. Must work live. |
| **US-4.1-4.4: Claude advisor core** | The entire technical differentiator. |

---

## 5. Must-Have Business Features (The 5 That Must Work)

These are the 5 features that, if they work in the demo, sell the business story. If any of these fail, the pitch weakens significantly.

### 1. Season KPI Page with Per-Cap Benchmark Gap

**What judges see:** "Your per-cap is $11.77. The WHL average is $14-$16. That is $180K-$342K in annual upside."
**Why it matters:** This is the opening hook. It frames every subsequent page as "here is how we close that gap."
**Technical requirement:** KPI cards with delta indicators, one gauge or comparison chart showing current vs. benchmark.

### 2. Intermission Bottleneck Visualization with Dollar Impact

**What judges see:** A heatmap or timeline showing the exact intermission crunch, and a number: "$80K-$120K in lost sales per season."
**Why it matters:** This is the most visceral, relatable insight. Every arena operator has watched fans leave the line. Now they see the cost.
**Technical requirement:** Transaction timeline with game_period shading, aggregated intermission metrics, one big number.

### 3. Demand Forecasting with Prep Sheet Output

**What judges see:** "Friday vs. Vancouver, 4,200 expected fans. Prep 480 hot dogs, 800 beers, 215 pizzas. Staff 28 people across 5 stands."
**Why it matters:** This is where ML becomes tangible. It is not a prediction chart -- it is a printable operations document.
**Technical requirement:** Input widgets (opponent, day, attendance), demand model output, formatted prep table.

### 4. Stand-Level Insights with Actionable Callouts

**What judges see:** "Phillips Bar: 19K beers, <5% food. Adding food = $18K-$25K/year. Island Canteen handles 41% of transactions -- it is the bottleneck."
**Why it matters:** This turns data into decisions. Not just "here is what happened" but "here is what to do about it."
**Technical requirement:** Stand comparison charts with annotation/callout boxes for key insights.

### 5. Claude Advisor Live Demo (The Closer)

**What judges see:** A live conversation where someone asks "What should we prepare for Friday's Vancouver game?" and the AI responds with a complete, data-backed game-day plan.
**Why it matters:** This is the "future of arena operations" moment. It turns a dashboard into an intelligent assistant. It is the reason this is not just another BI tool.
**Technical requirement:** Chat UI, Claude API with tool use working, at least 3 tools executing successfully (query_database, get_forecast, get_prep_sheet).

---

## 6. Recommended Changes to the PRD

### Change 1: Add a "Business Impact Summary" to every dashboard page

Every page should end with a callout box or card that answers: "So what? How much money does this insight represent?" Examples:
- Season KPIs: "Closing the per-cap gap to $14.50 = +$220K/year"
- Stand Performance: "Adding food to Phillips Bar = +$18K-$25K/year"
- Intermission Analysis: "Solving the bottleneck = +$80K-$120K/year"
- Forecasting: "Accurate demand prediction = -$35K-$60K in waste + labor"

This turns every page into a business case, not a data report.

### Change 2: Replace mock Stripe data with direct revenue estimation

Delete US-1.5 (stripe_generator.py) entirely. Instead, enhance the `estimated_revenue` column already in US-1.2. Use your KNOWN_PRICES and CATEGORY_PRICES to compute revenue directly. Label it "Estimated Revenue" throughout the dashboard -- be transparent about the estimation. This is more honest and saves massive build time.

If you want payment method breakdowns for visual interest, hardcode industry-standard splits (Visa 40%, MC 25%, Debit 15%, Apple Pay 12%, Google Pay 8%) as a single static chart. Do not build a data pipeline for it.

### Change 3: Restructure the demo flow to lead with the business problem

Current demo flow starts with Season KPIs. Better flow:

1. **The Problem (30 sec):** "SOFMC generates ~$950K/season in concessions. Per-cap spend is $11.77 -- 25% below WHL average. We built a platform to find and close that gap."
2. **The Data (1 min):** Season KPIs -- "239K real transactions, 67 games, 2 seasons. Here is the baseline."
3. **The Bottleneck (2 min):** Intermission Analysis -- "18-minute windows where you are losing $80-120K/year."
4. **The Missed Opportunities (2 min):** Stand Performance -- "Phillips Bar: 19K beers, no food. Island Canteen: 41% of all traffic."
5. **The Prediction (2 min):** Forecasting -- "Friday vs Vancouver. Here is your prep sheet."
6. **The Advisor (3 min):** Claude live demo -- "Ask it anything. It queries the data, runs the models, gives you the answer."
7. **The Number (30 sec):** "This platform identifies $150K-$250K in actionable revenue opportunities. Phase 1 initiatives require under $10K in investment."

### Change 4: Pre-script 3 Claude Advisor questions

Do not rely on improvisation during the demo. Pre-test these exact prompts:

1. **"What should we prepare for Friday's game against Vancouver with 4,200 expected fans?"** -- triggers get_forecast + get_prep_sheet. This is the operational value demo.
2. **"Which stand has the biggest missed opportunity and what should we do about it?"** -- triggers query_database. This surfaces the Phillips Bar insight.
3. **"What combo deals would you recommend based on our sales data?"** -- triggers get_product_recommendations. This is the revenue-growth demo.

Test these before the demo. If Claude's answers are weak, refine the system prompt to ensure it cites specific numbers.

### Change 5: Add a "$1 Dog Night" callout to prove promotional ROI

Somewhere in the dashboard (Game Explorer or Season KPIs), highlight the $1 Dog Night case study:
- 1,167 hot dog transactions (30% of all that night)
- Proof that data-driven promotions drive volume
- The platform enables identifying which promotions to run and when

This is a one-card addition. It proves the platform's value with a real historical example, not a hypothetical.

### Change 6: Cut the anomaly detection model scope

If time allows, keep it. But do not let it block more important work. The anomaly detection model is the weakest link in the business story. "This game was unusual" is analytically interesting but not actionable unless paired with a recommendation engine. That recommendation engine is a post-hackathon feature.

If you keep it, frame it as: "The platform automatically flags games that deviated from predicted patterns, so ops teams can investigate and learn." That is a reasonable 15-second demo moment, not a 3-minute deep dive.

---

## 7. The "$X Revenue" Slide

### The Number: **$250,000 in identified annual revenue opportunity**

### How to present it:

"This platform identifies **$250,000 in incremental annual revenue** from concession optimization at SOFMC, achievable with under $10,000 in Phase 1 investment."

### How to justify it (build-up for the judges):

| Opportunity | Annual Impact | Data Source |
|-------------|---------------|-------------|
| Close per-cap gap (from $11.77 to $14.00) | +$180,000 | Benchmark comparison vs. WHL peers |
| Intermission bottleneck recovery (express lanes, pre-ordering) | +$80,000-$120,000 | Transaction velocity analysis showing demand exceeding throughput |
| Combo/bundle strategy (25% adoption) | +$72,000 | Product affinity analysis + industry combo adoption rates |
| Phillips Bar food cross-sell | +$18,000-$25,000 | Stand-level analysis showing 19K beer transactions with <5% food |
| Attendance-based staffing + prep optimization (cost savings) | -$35,000-$60,000 | Demand forecast model reducing waste and overstaffing |
| **Total identified opportunity** | **$385,000-$457,000** | |
| **Conservative capture rate (60%)** | **~$250,000** | |

### Why $250K and not $350K+:

- $250K is credible. You can defend it without looking like you are inflating numbers.
- It accounts for overlap between initiatives (combo strategy and per-cap improvement are not fully additive).
- It assumes conservative adoption rates and execution.
- If a judge pushes back, you can say: "Even at half that, $125K on a $10K investment is 12x ROI in year one."

### The one-liner for the final slide:

> **"This platform turns 239,000 real transactions into a $250K annual revenue roadmap -- with a 25x ROI on Phase 1 implementation."**

---

## Final Assessment

### Strengths of this PRD:
- Real data, real venue, real business problem
- AI advisor is a genuine differentiator
- Technical architecture is sound for a hackathon scope
- Demo flow is logical

### Critical risks in the next 2.5 hours:
1. **Scope creep from Stripe mock data** -- cut it now, save 45+ minutes
2. **Claude API reliability** -- if the advisor crashes during the demo, you lose your biggest differentiator. Test it early and often.
3. **Business narrative is buried under technical detail** -- add dollar figures to every page, lead every insight with "this means $X"
4. **7 pages is a lot for a 10-minute demo** -- you will spend ~90 seconds per page. Focus on making 4 pages excellent rather than 7 pages mediocre.

### If I were the team lead, here is what I would do right now:
1. **Kill Stripe mock data generation.** Use estimated_revenue from price lookup.
2. **Tell Agent C to add "business impact" callout cards to every dashboard page.**
3. **Tell Agent D to pre-test the 3 scripted Claude questions and tune the system prompt until the answers are crisp.**
4. **Write the final slide with the $250K number and the justification table.**
5. **Practice the demo flow once before the final hour.**

You have a strong foundation. The risk is not that the idea is bad -- it is that you over-build the technology and under-deliver the business story. Judges remember the dollar figure and the AI demo. Everything else is supporting evidence.

---

*Analysis prepared for the Victoria Royals Hackathon Team*
*Time of review: 2.5 hours remaining in build window*
