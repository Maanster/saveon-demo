# Operations Manager PRD Review
## Victoria Royals Concession Intelligence Platform -- SOFMC
### Reviewer: Operations Manager Perspective (6 stands, 25-35 staff, 67 game nights/season)

---

## 1. Practical Value Assessment

**Rating: 6.5 / 10**

Let me be honest. This platform solves some of my problems, but it is built more like a retrospective analytics tool for a GM reviewing the season than an operational tool for someone running game night. Most of what I see here is "look at what happened" rather than "here is what to do next."

**What it actually solves for me:**

- **Pre-game prep planning.** If the forecasting page works as described -- I pick Friday, Vancouver, 4,000 expected fans, and it tells me how many kegs of Phillips to tap, how many pizza doughs to prep, and how many hot dogs to thaw -- that is genuinely valuable. I currently do this on gut feel and a notebook. A data-backed version would reduce my Thursday night anxiety.
- **Staffing decisions for low-attendance games.** Right now I staff roughly the same for a Tuesday Kamloops game (1,300 fans) as I do for a Friday Vancouver game (4,900 fans). That is money I am burning. If this tool tells me "for 1,500 expected, open Island Canteen, Phillips Bar, and one Portable -- shut down Island Slice and TacoTacoTaco" then I save real labor dollars.
- **Post-game analysis.** The Game Explorer and Stand Performance pages would help me have better conversations with Matt Cooke about what worked and what did not. Currently I have no data to back up my hunches.

**What it does NOT solve:**

- Nothing here helps me during the game. Once puck drops, this platform is closed on my laptop and I am running between stands with a radio. I need real-time tools, not dashboards.
- No inventory tracking. I know what I should have prepped, but there is nothing tracking what I have actually sold through during the game or what I am running low on.
- No staff communication or deployment tool. The staffing "suggestion" is a number on a page. I need something that tells me "move 2 staff from TacoTacoTaco to Island Canteen NOW -- the line is 40 deep."

**Bottom line:** Good for pre-game planning and post-game review. Useless once the doors open. For a hackathon demo, that is probably fine. For real-world adoption, it needs a game-day operational layer.

---

## 2. The Prep Sheet is Everything

The forecasting page with the prep sheet is the single most valuable feature in this entire PRD. If you nail this one page, the rest is window dressing. An ops manager would open this page every Thursday afternoon to plan for the weekend.

**What the PRD gets right:**

- Input widgets for opponent, day, attendance, month, and playoff toggle -- these are exactly the variables I think about when planning.
- Predicted units by category -- useful directionally.
- Staffing suggestion per stand -- critical if done well.

**What the prep sheet MUST include that is missing:**

1. **Item-level quantities, not just category-level.** "You need 450 Beer units" is useless. I need "Tap 3 kegs of Phillips IPA, 2 kegs of Stanley Park, stock 180 cans of Bud, 90 cans of Coors Light." Category-level forecasting does not translate to purchase orders. The data has item-level granularity -- use it.

2. **Stand-level breakdown.** Do not just tell me total predicted units. Tell me: Island Canteen needs X hot dogs, Phillips Bar needs Y kegs, Island Slice needs Z pizza doughs. I prep each stand independently. A single aggregate number means I still have to do the math myself.

3. **Buffer recommendations with reasoning.** The PRD mentions a 20% buffer, but it should be context-dependent. A Friday playoff game against Vancouver with 5,000 expected needs a 25-30% buffer because upside risk is enormous and running out of beer at a playoff game is a fireable offense. A Tuesday Kamloops game with 1,300 expected needs a 10% buffer because over-prepping costs more than a brief stockout on a slow night.

4. **"Do not prep" items for low-attendance games.** For a 1,500-attendance Tuesday, I should not be prepping tequila slushie mix at TacoTacoTaco. The prep sheet should explicitly say "Skip these items / Close these stands" for small games.

5. **Perishable vs. non-perishable distinction.** Over-prepping canned beer is low risk -- it keeps. Over-prepping pizza dough or thawing too many hot dog buns is real waste. The prep sheet should flag high-waste-risk items differently from shelf-stable items.

6. **Historical comparison.** Show me: "Last time you had a Friday Vancouver game with similar attendance (March 14, 2025, 4,942 fans), you sold X of Y at each stand." Let me see the actual comparable game, not just a model output. I trust data from a real game more than a model prediction.

7. **Printable format.** This needs to export as a one-page PDF I can hand to each stand lead at 4 PM when they arrive for setup. They are not opening Streamlit on their phones. A "Print Prep Sheet" button that generates a clean PDF per stand is worth more than every chart in this platform combined.

**Recommended change for the hackathon:** Even if you cannot build all of this, at minimum make the prep sheet item-level (not category-level) and stand-level (not aggregate). That alone turns it from a toy into a tool.

---

## 3. Intermission Analysis Reality Check

The intermission heatmap is the most visually impressive feature in the PRD and the most likely to wow hackathon judges. As an ops manager, here is my honest take on actionability.

**What the heatmap tells me that I already know:**

- Intermissions are insane. I am there. I can see the lines. I do not need a heatmap to tell me that the first 8 minutes of first intermission is a war zone. I have lived it 67 times.

**What the heatmap could tell me that I do NOT know:**

- Which specific games had unusually high or low intermission velocity. If I can see that the Jan 31 Red Deer game (4,217 fans) had a worse intermission crunch than the Mar 14 Vancouver game (4,942 fans) despite lower attendance, that is interesting. It might tell me something about opponent-driven crowd behavior or promotional effects.
- Whether second intermission velocity is declining faster than first intermission -- which would tell me fans are giving up on concessions by the 2nd break.
- Whether specific stands are chokepoints during intermissions that others are not. If Phillips Bar clears its queue in 6 minutes but Island Canteen is still slammed at minute 14, that tells me where to redeploy staff.

**What operational decisions this actually drives:**

1. **Pre-intermission staging.** If I know the first 8 minutes account for 70% of intermission transactions, I need all hands on deck the moment the buzzer sounds. No bathroom breaks for staff at period end. Pre-pour beers starting 2 minutes before the period ends.
2. **Stand-specific intermission staffing.** The stand-level intermission comparison (mentioned in US-3.5) is the real gold. If Island Canteen does 3x the intermission volume of TacoTacoTaco, I should be pulling a TacoTacoTaco staff member to Island Canteen at each intermission. This is a concrete, game-day-actionable decision.
3. **Express station placement.** If the data shows that 200-700 transactions are being lost per intermission, that justifies deploying a grab-and-go station. The heatmap data gives me the evidence to present to Matt when I ask for budget to set up express stations.

**The "lost revenue estimator" slider:** This is a great demo feature for judges and for convincing Matt Cooke to invest. It is not something I would use regularly. I would use it once to build a business case, then never open it again. That is fine for a hackathon -- just know that it is a pitch tool, not an operations tool.

**What would make the intermission page actually operational:** Add a "Pre-Intermission Checklist" output. Based on the expected attendance and historical patterns, generate: "5 minutes before 1st intermission: pre-pour 40 Phillips drafts, stage 20 bags of popcorn at Island Canteen, move 2 staff from Portable to Island Canteen, announce mobile ordering on PA." That is actionable. A heatmap is informative.

---

## 4. Stand Performance Gaps

The Stand Performance page (US-3.4) gives me stacked bars and revenue comparisons. These are fine for a season review meeting. Here are the operational questions I am actually asking that this page does not answer:

**Questions I ask every game day:**

1. **"Which stands should I open tonight?"** For a 1,500-fan Tuesday, I need to open 2-3 stands, not 6. The data should tell me: for attendance under 2,000, the optimal configuration is Island Canteen + Phillips Bar + 1 Portable. For 2,000-3,500, add Island Slice. Over 3,500, open everything. This is a simple lookup table derived from the data, and it would save me $15K-$25K/season in labor. The PRD does not explicitly build this.

2. **"Where should I put my extra staff?"** On a 4,500-fan night I might have 32 staff. The stand performance data should generate a recommended staffing split. Something like: Island Canteen: 10, Phillips Bar: 5, Island Slice: 5, ReMax: 4, TacoTacoTaco: 4, Portable: 4. Right now I eyeball it.

3. **"Is a stand underperforming because of low demand or slow service?"** If TacoTacoTaco does fewer transactions per staff-hour than Island Slice, is that because tacos take longer to make, or because fewer people want tacos? The stand performance page shows volume but not efficiency. Transactions per staff-hour would be the real metric, but we probably do not have staff-hour data.

4. **"Which stand should get the promotional item?"** If we are doing a Dollar Dog Night, where do I push the volume? Island Canteen handles food well, but it is already overloaded. Maybe the promo should be routed through a dedicated Portable Station to avoid crushing Island Canteen. The stand data should inform promotional stand assignment.

5. **"What is the revenue-per-square-foot or revenue-per-staff-hour by stand?"** Phillips Bar does 19K+ beer units with minimal food -- it is probably the most efficient revenue generator per labor hour. Island Canteen does 41% of volume but probably requires 40%+ of staff. Are they proportional? The stand comparison should reveal efficiency, not just volume.

**What the PRD should add:** A simple "Stand Opening Recommendation" widget on the Forecasting page. Input expected attendance, output which stands to open and suggested headcount per stand. This is a 10-line lookup table, not a machine learning problem, and it would be the most used feature on game day.

---

## 5. What's Missing for Game Day

The PRD is designed as a pre-game and post-game tool. Here is what an ops manager actually needs that is entirely absent:

**Critical gaps:**

1. **Game-day countdown dashboard.** A single screen showing: time until puck drop, time until next intermission, current period, and a pre-intermission checklist. This would run on a tablet behind the main concourse. It keeps my stand leads synchronized.

2. **"Express Prep" alerts.** 5 minutes before intermission, push a notification or display: "INTERMISSION IN 5 MINUTES -- Pre-pour 40 drafts, stage grab-and-go items." This is the most operationally impactful feature you could build, and it is not in the PRD.

3. **Inventory depletion estimates.** If I prepped 200 hot dogs based on the forecast and I have sold 140 by second intermission, am I going to run out? A simple burn-rate tracker (even estimated from the forecast model) would tell me "at current pace, hot dogs will sell out with 25 minutes remaining -- consider pulling stock from Island Slice."

4. **Post-game reconciliation.** After the game, I want to compare forecast vs. actual. Did we over-prep or under-prep? By how much? This feedback loop is how the model gets better and how I build trust in it. The PRD has no mention of forecast-vs-actual comparison.

5. **Stand-specific checklists.** Each stand lead needs a game-day checklist: items to prep, quantities, setup tasks, break schedule, intermission protocol. The prep sheet is the start, but it should flow into a per-stand operational checklist that the lead can check off as they work through setup.

6. **Weather integration.** A cold rainy Wednesday vs. a warm sunny Saturday dramatically changes what sells. Hot chocolate and coffee spike in cold weather. Beer consumption goes up on warm evenings. The PRD includes month as a feature but not weather. Even a simple temperature input on the forecasting page would improve predictions.

7. **Promotional event flag.** Dollar Dog Night changes everything about demand patterns. The forecasting model needs a "special promotion" input, or at minimum a flag for known high-impact promotions. The $1 Dog Night drove transactions per capita to 1.73 -- nearly 40% above normal. If the model does not account for this, its predictions will be wrong on promo nights.

**Realistic for the hackathon (2.5 hours left):** Items 4 (post-game reconciliation) and 7 (promo flag) could be added quickly. Item 6 (weather) is a simple text input. Items 1-3 and 5 are future roadmap.

---

## 6. Anomaly Detection Reality

The IsolationForest anomaly detection model (US-2.2) uses features like units_per_cap, beer_share, food_share, snack_share, avg_basket_size, and pct_intermission_sales. Here is when an ops manager would actually care about unusual patterns:

**Scenarios where anomaly detection is useful:**

1. **"Something weird happened and I need to know what."** After a game where revenue was 20% below forecast despite good attendance, the anomaly detector could flag "beer share was unusually low, food share was unusually high." Maybe it was a family night I forgot about, or maybe there was a keg issue at Phillips Bar that I did not notice. This is useful for post-game diagnosis.

2. **"Is this promotional night actually performing differently?"** When Matt asks "did Dollar Dog Night change the sales mix?" the anomaly detector can quantify exactly how different the pattern was from normal. It shifts the conversation from "I think it went well" to "the food share jumped from 18% to 35% and the basket size dropped by $3, but total transactions were up 40%."

3. **"Identifying POS issues or theft."** If a stand shows anomalously low revenue relative to foot traffic or attendance, that could indicate a POS malfunction, a training issue, or a more serious problem. This is a low-probability but high-impact use case.

**Scenarios where it is NOT useful:**

- "Unusual patterns" on a random Tuesday do not drive any operational decision. If the model flags a game from two months ago as anomalous, I probably already knew something was off that night and I have moved on. Anomaly detection on historical data is interesting for analysis but does not change what I do tomorrow.

**Honest assessment:** Anomaly detection is a nice-to-have for the Claude Advisor ("Hey Claude, were there any weird games this season?") and a good demo feature. It is not something I would check regularly. It adds technical sophistication to the hackathon submission, which matters for judges scoring Technical Execution and Innovation. Keep it, but do not spend precious build time perfecting it. A basic version that flags the 3-5 most unusual games with a one-sentence explanation is sufficient.

---

## 7. Feasibility Concerns

With 2.5 hours left, here is what I think is realistic and what is not:

**Realistic to build well:**

- Season KPIs page (straightforward SQL aggregations, 30 minutes)
- Game Explorer page (dropdown + queries, 45 minutes)
- Forecasting page with basic prep sheet (the model is simple, the UI is straightforward, 60 minutes)
- Claude Advisor with 3-4 working tools (the wow factor, worth investing in, 60 minutes)

**Realistic to build adequately:**

- Stand Performance page (bar charts from SQL, 30 minutes, but keep it simple)
- Revenue Analytics from Stripe mock data (if the Stripe generator is already working, 30 minutes)

**At risk of being half-baked:**

- Intermission Analysis heatmap. Plotly heatmaps with proper time bucketing, game-date axes, and color scaling take time to get right. A broken or ugly heatmap hurts the demo more than a missing page. If this is not 80% done already, simplify it to a bar chart showing transaction volume by period. You can still tell the intermission story with a bar chart.
- The "lost revenue estimator" slider. Cool idea, but it is a nice-to-have on top of the intermission page. If the heatmap is not solid, skip the slider entirely.

**Should be simplified or cut:**

- Affinity mining (US-2.4). Product co-occurrence is computationally interesting but operationally marginal. "People who buy beer also buy popcorn" is not a revelation. Cut this model if you are behind schedule. The Claude Advisor can answer affinity questions directly from SQL queries without a trained model.
- Anomaly detection (US-2.2). As discussed above, useful for demo flair but not operationally critical. Train a basic model, display a green/red badge on the Game Explorer, and move on. Do not spend time tuning hyperparameters.
- Revenue Analytics page (US-3.7). This is entirely based on mock Stripe data. It looks professional, but judges who know the data is fake may not be impressed. If you are running short, this page can show 2-3 KPI cards instead of full charts.

**What to protect at all costs:**

- The Forecasting page with prep sheet. This is your operational differentiator. If this page works well in the demo -- someone types in "Friday, Vancouver, 4,500 fans" and gets a credible prep sheet with item quantities, staffing suggestions, and revenue prediction -- that alone wins the Feasibility and Business Impact categories.
- The Claude Advisor. This is your Innovation differentiator. A live conversation with the data where someone asks "What should I order for next Friday's game?" and gets a data-backed answer is the wow moment. Protect the 3 minutes of demo time allocated to this.

---

## 8. The "I Would Actually Use This" Features

Ranked from "I would open this every game day" to "I would look at it once and forget about it":

### Tier 1: Would use before every game (weekly)

1. **Forecasting page + prep sheet** -- This is the tool. Every Thursday I would plug in the weekend games and generate prep sheets. If it produces stand-level, item-level quantities with a print button, I would use it 34+ times per season.
2. **Stand opening / staffing recommendation** -- Currently NOT in the PRD as a standalone feature, but embedded in the forecasting page. If you surface "open these 4 stands, staff them 8/5/4/3" as a prominent output, this saves me a phone call and a spreadsheet every game.

### Tier 2: Would use monthly or for specific situations

3. **Game Explorer** -- Useful when Matt asks "how did the Spokane playoff game go?" or when I want to compare two similar games. I would use this 5-10 times per season, mostly for post-game review and reporting.
4. **Claude Advisor** -- I would use this when I have a specific question I cannot easily answer from the other pages. "Which item has the highest margin at TacoTacoTaco?" or "What happened the last time we played Kelowna on a Wednesday?" This is a power-user feature. I would probably use it 10-15 times per season once I learned what it can do.
5. **Stand Performance** -- Useful for the mid-season and end-of-season review meeting with Matt. I would pull this up 2-3 times per season to make the case for operational changes.

### Tier 3: Would look at once or twice, then rarely again

6. **Intermission Analysis** -- I would use this once to build the business case for express stations or mobile ordering expansion. After that, the intermission pattern does not change game to game. It is always the same crunch. Useful as a persuasion tool, not an operational tool.
7. **Season KPIs** -- Nice summary for the start-of-season or end-of-season presentation. Not something I need on game day.
8. **Revenue Analytics (Stripe)** -- This is the GM's page, not mine. I care about units, not dollars. Matt Cooke would use this for board reporting. I would not open it.
9. **Anomaly Detection badges** -- Mildly interesting when they appear on the Game Explorer. I would never go looking for anomalies proactively.
10. **Product Affinity / Bundle suggestions** -- Nice for a menu planning meeting once a year. Not operationally relevant on a game-by-game basis.

---

## 9. Recommended Changes (Top 5)

These are the five changes that would turn this from a hackathon demo into a tool I would actually open before every game:

### Change 1: Make the Prep Sheet the Hero Feature

Restructure the Forecasting page so the prep sheet is the primary output, not a secondary display. When I input game parameters, the first thing I should see is a printable, stand-by-stand, item-by-item prep sheet with quantities. The forecast charts and revenue predictions should be below it, not above it. Flip the hierarchy: operational output first, analytical charts second.

**Specific addition:** Add a "Print Prep Sheet" button that generates a clean, one-page-per-stand PDF. This costs almost nothing to build (Streamlit has PDF export libraries) and makes the difference between a demo feature and a real tool.

### Change 2: Add a Stand Opening Recommendation

On the Forecasting page, add a prominent section that says: "For [X] expected attendance, recommended configuration: Open [these stands], close [these stands]. Suggested staffing: [breakdown]." This can be a simple rules-based lookup (attendance < 2,000: open 3 stands; 2,000-3,500: open 4; 3,500+: open all 6) derived from the historical data. No ML required. This single widget saves $15K-$25K/season in labor costs and is the easiest business impact to quantify for judges.

### Change 3: Add Forecast vs. Actual Comparison

On the Game Explorer page, add a toggle: "Compare to Forecast." Show the predicted values next to the actual values for any historical game. This does two things: (a) it builds my trust in the model by showing me where it was right and where it was wrong, and (b) it demonstrates to judges that the team understands model validation, which scores well on Technical Execution.

### Change 4: Add a Promotional Event Input to Forecasting

Add a dropdown or checkbox on the Forecasting page for known promotional events: Dollar Dog Night, Family Night, School Night, Playoff, etc. The $1 Dog Night drove a 1.73 transactions-per-cap rate versus a typical 1.30. If the model does not account for this, it will be wildly wrong on promo nights, and I will stop trusting it after the first bad prediction. Even a simple multiplier adjustment ("if Dollar Dog Night, multiply hot dog forecast by 3x and reduce beer forecast by 10%") would dramatically improve accuracy for these games.

### Change 5: Surface Comparable Historical Games

On the Forecasting page, below the model prediction, show: "Most similar historical games:" with 3-5 past games that match the input parameters (same opponent, similar attendance, same day of week). Show what actually sold at each of those games. This gives me a sanity check on the model output and is often more trusted by operations people than a black-box prediction. If the model says I need 400 hot dogs but every comparable game sold 250, I am going to prep 275 and ignore the model. Showing the comparables makes the tool collaborative rather than prescriptive.

---

## Summary

This PRD describes a solid analytics platform that would impress hackathon judges on Technical Execution and Innovation. It has the right data foundation, reasonable ML models, and a strong demo story. The Claude Advisor is a genuine differentiator.

Where it falls short is in operational empathy. It is built by data people for data people. An ops manager does not think in heatmaps and donut charts. I think in prep sheets, staffing counts, and stand assignments. The gap between "here is an insight" and "here is what to do" is where this platform lives right now, and closing that gap is what would make it a real product instead of a demo.

**The single most impactful change with 2.5 hours remaining:** Make the Forecasting page prep sheet item-level and stand-level instead of category-level aggregate. Everything else is polish. That one change turns a dashboard into a decision-making tool.

**If you have extra time after that:** Add the stand opening recommendation, the comparable historical games, and the promotional event input. These are all small features with outsized operational impact.

The bones are good. The data is real. The architecture is sound. Just shift 20% of the focus from "what happened" analytics to "what to do" recommendations, and this tool has genuine real-world adoption potential.
