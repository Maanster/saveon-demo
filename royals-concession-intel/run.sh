#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Activate venv
source .venv/bin/activate

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "WARNING: ANTHROPIC_API_KEY not set. Claude Advisor will not work."
fi

# Build data (skip if DB exists)
if [ ! -f db/royals.db ]; then
    echo "Building database..."
    python3 data_foundation/build_all.py
fi

# Train models (skip if models exist)
if [ ! -f models/demand_forecast.joblib ]; then
    echo "Training ML models..."
    python3 ml/train_demand.py
    python3 ml/train_revenue.py
    python3 ml/train_affinity.py
fi

echo "Launching dashboard..."
streamlit run dashboard/app.py --server.port 8501
