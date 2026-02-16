#!/bin/bash

cd "$(dirname "$0")/backend"

echo "🚀 Starting Fraud Detection RLM System..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Start Streamlit dashboard
echo "📊 Starting Streamlit Dashboard on http://localhost:8501"
streamlit run app/ui/streamlit_dashboard.py --server.port=8501 --server.address=0.0.0.0
