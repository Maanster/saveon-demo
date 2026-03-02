# Royals Concession Intelligence Platform

A demo for how **Save-on Foods Memorial Centre** in Victoria can make use of an unutilized concession dataset.

Built during a **2-person, 4-hour hackathon** as a proof of concept for the Victoria Royals (WHL) venue.

## What It Does

The platform turns 239,000+ concession transactions into actionable intelligence:

- **Season KPIs** — Per-cap revenue, WHL benchmark gap, attendance trends
- **Game Explorer** — Drill into any game by stand, period, and category
- **Stand Performance** — Cross-sell insights, Phillips Bar optimization
- **Intermission Analysis** — Heatmaps, lost revenue modeling
- **ML Forecasting** — Demand prediction and prep sheets for kitchen handoff
- **Revenue Estimation** — Game-level and season-level projections
- **Claude Advisor** — Ask questions in plain English, get AI-powered recommendations
- **Game Simulator** — Period-by-period demand simulation

## Quick Start

```bash
cd royals-concession-intel
pip install -r requirements.txt
streamlit run dashboard/app.py
```

Then open [http://localhost:8501](http://localhost:8501).

Use the **View Slides** / **View Demo** toggle at the top to switch between the pitch deck and the live dashboard.

## Live Demo

[Deploy to Streamlit Community Cloud and add your URL here]

## Tech Stack

Python, Streamlit, pandas, plotly, scikit-learn, Claude AI
