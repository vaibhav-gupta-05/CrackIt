#!/usr/bin/env bash
# start.sh - Launch script for Render

# Start the FastAPI backend in the background
# (We use uvicorn with the host 0.0.0.0 so the cloud platform can route to it)
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &

# Start the Streamlit dashboard in the foreground
# Streamlit will run on port 8501 by default, or whatever port Render assigns
python -m streamlit run src/dashboard/app.py --server.address 0.0.0.0 --server.port 8501
