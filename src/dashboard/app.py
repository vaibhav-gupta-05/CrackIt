import sys
from pathlib import Path
# Ensure project root is in sys.path so 'config' and 'src' modules can be imported
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import httpx
import streamlit as st

from config import get_settings
from src.dashboard.theme import inject_custom_css

# Must be the very first Streamlit command
st.set_page_config(
    page_title="CrackIT — Interview Prep",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "current_view" not in st.session_state:
    st.session_state.current_view = "workspace"
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None
if "job_results" not in st.session_state:
    st.session_state.job_results = []
if "api_url" not in st.session_state:
    settings = get_settings()
    host = "127.0.0.1" if settings.api_host == "0.0.0.0" else settings.api_host
    st.session_state.api_url = f"http://{host}:{settings.api_port}/api"


def set_view(view_name: str):
    st.session_state.current_view = view_name


def call_match_api(jd_text: str):
    """Calls the FastAPI backend to parse JD and match resources."""
    try:
        response = httpx.post(
            f"{st.session_state.api_url}/resources/match",
            json={"jd_text": jd_text},
            timeout=60.0
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to connect to backend API: {e}")
        return None


# --- Navigation Sidebar ---
def render_sidebar():
    with st.sidebar:
        st.markdown("## CrackIT.")
        st.caption("AI Interview Intelligence")
        st.divider()
        
        nav_items = [
            ("🔍  Live Job Search", "job_search"),
            ("📋  Extraction Workspace", "workspace"),
            ("📚  Practice Arena", "arena"),
        ]
        
        for label, view_key in nav_items:
            btn_type = "primary" if st.session_state.current_view == view_key else "secondary"
            st.button(label, key=f"nav_{view_key}", type=btn_type, use_container_width=True, on_click=set_view, args=(view_key,))
        
        st.divider()
        
        # Show current extraction summary in sidebar if available
        if st.session_state.extracted_data:
            data = st.session_state.extracted_data
            st.caption("LAST EXTRACTION")
            st.markdown(f"**{data.get('job_title', 'Unknown')}**")
            st.markdown(f"_{data.get('company', 'Unknown')}_")
            skills = data.get("extracted_skills", [])
            st.markdown(f"`{len(skills)} skills` · `{len(data.get('round_types', []))} rounds`")


# --- View 1: Extraction Workspace ---
def view_workspace():
    st.markdown("# 📋 Extraction Workspace")
    st.markdown("Paste a job description to extract skills, predict interview rounds, and find prep resources.")
    
    st.write("")
    
    col1, col2 = st.columns([0.4, 0.6], gap="large")
    
    with col1:
        st.caption("INPUT")
        jd_input = st.text_area(
            "Job Description", 
            height=400, 
            placeholder="Paste the full job description text here...",
            label_visibility="collapsed"
        )
        
        if st.button("Extract Insights", type="primary", use_container_width=True):
            if len(jd_input) > 50:
                with st.spinner("Extracting skills & matching resources..."):
                    data = call_match_api(jd_input)
                    if data:
                        st.session_state.extracted_data = data
                        st.rerun()
            else:
                st.warning("Please paste a longer job description (at least 50 characters).")
                
    with col2:
        st.caption("EXTRACTED INSIGHTS")
        data = st.session_state.extracted_data
        
        if not data:
            st.markdown(
                "<div style='display:flex; height:400px; align-items:center; justify-content:center; color:rgba(255,255,255,0.2); font-weight:300;'>Awaiting input...</div>", 
                unsafe_allow_html=True
            )
        else:
            # Metrics row
            m1, m2, m3 = st.columns(3)
            m1.metric("Role", data.get("job_title", "Unknown"))
            m2.metric("Company", data.get("company", "Unknown"))
            m3.metric("Level", data.get("experience_level", "Unknown"))
            
            st.write("")
            
            # Skills
            st.caption("REQUIRED SKILLS")
            skills = data.get("extracted_skills", [])
            if skills:
                # Render as pill-like chips using markdown
                chips = " ".join([f"`{s}`" for s in skills])
                st.markdown(chips)
            
            st.write("")
            
            # Rounds
            st.caption("PREDICTED INTERVIEW ROUNDS")
            rounds = data.get("round_types", [])
            if rounds:
                chips = " ".join([f"`{r.replace('_', ' ').title()}`" for r in rounds])
                st.markdown(chips)
            
            st.write("")
            
            # Cache status
            if data.get("cache_hit"):
                st.success("⚡ Instant result (cached)")
            else:
                st.info("🧠 Fresh analysis via Groq API")


# --- View 2: Practice Arena ---
def view_arena():
    st.markdown("# 📚 Practice Arena")
    
    data = st.session_state.extracted_data
    if not data:
        st.info("👈 Extract a Job Description in the **Workspace** first to see matched resources here.")
        return
    
    st.markdown(f"Curated resources for **{data.get('job_title', 'this role')}** at **{data.get('company', 'Unknown')}**")
    st.write("")
    
    resources = data.get("matched_resources", [])
    
    if not resources:
        st.warning("No matching resources were found. Try extracting a different JD with more specific skills.")
        return
    
    st.caption(f"MATCHED RESOURCES ({len(resources)})")
    
    for res_dict in resources:
        r = res_dict["resource"]
        
        # Platform icon
        icon = "🌐"
        if r["platform"] == "youtube":
            icon = "▶️"
        elif r["platform"] == "gfg":
            icon = "📗"
        elif r["platform"] == "leetcode":
            icon = "💻"
        
        with st.container(border=True):
            title_col, link_col = st.columns([0.8, 0.2])
            with title_col:
                st.markdown(f"**{icon} {r['title']}**")
                st.caption(f"Skill: {r['topic']}  ·  Platform: {r['platform'].upper()}")
            with link_col:
                st.link_button("Open →", r["url"], use_container_width=True)
            
            if r.get("description"):
                st.markdown(f"<small style='color:rgba(255,255,255,0.5);'>{r['description'][:200]}</small>", unsafe_allow_html=True)


# --- View 3: Live Job Search ---
def view_job_search():
    st.markdown("# 🔍 Live Job Search")
    st.markdown("Search across major job portals (Greenhouse, Lever, Workday) using search engine dorking.")
    
    st.write("")
    
    col_search, col_location, col_time = st.columns([0.5, 0.25, 0.25])
    
    with col_search:
        query = st.text_input("Role", placeholder="e.g. Python Developer, AI Engineer...", label_visibility="collapsed")
    with col_location:
        location = st.selectbox("Location", ["India", "Remote", "USA", "Global (Any)"], label_visibility="collapsed")
    with col_time:
        time_filter = st.selectbox("Posted", ["Past Week", "Past Day", "Past Month"], label_visibility="collapsed")
    
    time_map = {"Past Week": "w", "Past Day": "d", "Past Month": "m"}
    
    if st.button("Search Jobs", type="primary"):
        if not query:
            st.warning("Please enter a search query.")
        else:
            with st.spinner(f"Searching for '{query}' jobs..."):
                try:
                    from ddgs import DDGS
                    with DDGS() as ddgs:
                        # Build the dork query
                        location_str = "" if location == "Global (Any)" else f" {location}"
                        dork_query = f'"{query}"{location_str} (site:myworkdayjobs.com OR site:greenhouse.io OR site:jobs.lever.co OR site:icims.com)'
                        
                        results = list(ddgs.text(dork_query, timelimit=time_map[time_filter], max_results=10))
                        
                        if results:
                            st.session_state.job_results = results
                            st.success(f"Found {len(results)} jobs!")
                        else:
                            st.session_state.job_results = []
                            st.warning("No jobs found. Try broadening your search or changing the time filter.")
                except Exception as e:
                    st.error(f"Search failed: {e}")

    # Render results (persisted in session_state so buttons work)
    if st.session_state.job_results:
        st.write("")
        st.caption(f"SEARCH RESULTS ({len(st.session_state.job_results)})")
        
        for idx, job in enumerate(st.session_state.job_results):
            with st.container(border=True):
                title_col, action_col = st.columns([0.75, 0.25])
                
                with title_col:
                    st.markdown(f"**{job.get('title', 'Job Opening')}**")
                    body = job.get('body', '')
                    if body:
                        st.markdown(f"<small style='color:rgba(255,255,255,0.5);'>{body[:200]}</small>", unsafe_allow_html=True)
                
                with action_col:
                    st.link_button("Apply →", job.get("href", "#"), use_container_width=True)
                    
                    if st.button("Analyze", key=f"analyze_{idx}", use_container_width=True):
                        with st.spinner("Fetching & analyzing JD..."):
                            try:
                                resp = httpx.post(
                                    f"{st.session_state.api_url}/jobs/scrape_url",
                                    json={"url": job.get("href")},
                                    timeout=60.0
                                )
                                if resp.status_code == 200:
                                    clean_text = resp.json().get("text", "")
                                    if len(clean_text) > 50:
                                        data = call_match_api(clean_text)
                                        if data:
                                            st.session_state.extracted_data = data
                                            set_view("workspace")
                                            st.rerun()
                                    else:
                                        st.error("Could not extract enough text from the page.")
                                else:
                                    st.error(f"Failed to fetch: {resp.text}")
                            except Exception as e:
                                st.error(f"Error: {e}")


# --- Main Application Loop ---
def main():
    inject_custom_css()
    render_sidebar()
    
    if st.session_state.current_view == "workspace":
        view_workspace()
    elif st.session_state.current_view == "arena":
        view_arena()
    elif st.session_state.current_view == "job_search":
        view_job_search()

if __name__ == "__main__":
    main()
