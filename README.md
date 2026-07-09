# CrackIT — AI-Driven Job Aggregator & Interview Prep

A smart job aggregator that scrapes the latest job postings, extracts requirements via LLM agents, and instantly matches them with curated preparation resources to create a tailored study dashboard.

Built with a 100% free, local-first stack:
- **FastAPI + Streamlit** for the API and Dashboard.
- **httpx + BeautifulSoup + Playwright** for robust job scraping.
- **LangGraph** for multi-agent orchestration.
- **DuckDuckGo Search** for live job and resource aggregation.
- **Groq API** for ultra-fast LLM processing.

## Quick Start

1. **Environment Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configuration**
   Copy `.env.example` to `.env` and add your Groq API key:
   ```bash
   cp .env.example .env
   # Edit .env and set GROQ_API_KEY
   ```

3. **Run the Application**
   ```bash
   # Terminal 1: Start the FastAPI backend
   uvicorn src.api.main:app --reload
   
   # Terminal 2: Start the Streamlit dashboard
   streamlit run src/dashboard/app.py
   ```
