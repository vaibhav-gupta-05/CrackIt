import streamlit as st


def inject_custom_css():
    """
    Injects custom CSS to override Streamlit's default styling,
    achieving a premium, modern dark aesthetic.
    """
    custom_css = """<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

/* Global Typography */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    letter-spacing: -0.01em;
}

/* Dark Background */
.stApp {
    background-color: #0A0A0C;
}

/* Headings */
h1, h2, h3 {
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    color: #FFFFFF !important;
}

h1 { font-size: 2rem !important; }

/* Body text */
p, .stMarkdown p {
    color: rgba(255,255,255,0.7) !important;
    font-weight: 300 !important;
    line-height: 1.6 !important;
}

/* Captions / labels */
[data-testid="stCaptionContainer"] {
    letter-spacing: 0.08em !important;
    text-transform: uppercase;
    font-size: 0.7rem !important;
    color: rgba(255,255,255,0.35) !important;
}

/* Input Fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    color: #FFF !important;
    font-weight: 300 !important;
    padding: 0.75rem 1rem !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #5A657A !important;
    box-shadow: 0 0 0 1px #5A657A !important;
}

/* Select boxes */
.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
}

/* Buttons: default (secondary) */
.stButton > button {
    background: rgba(90, 101, 122, 0.08) !important;
    border: 1px solid rgba(90, 101, 122, 0.25) !important;
    color: #C8CCD4 !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.25rem !important;
    font-weight: 400 !important;
    font-size: 0.875rem !important;
    transition: all 0.15s ease !important;
}

.stButton > button:hover {
    background: rgba(90, 101, 122, 0.18) !important;
    border-color: rgba(90, 101, 122, 0.5) !important;
}

/* Primary Button */
[data-testid="stBaseButton-primary"] {
    background: #5A657A !important;
    color: #FFF !important;
    border: 1px solid #6E7B94 !important;
    font-weight: 500 !important;
}

[data-testid="stBaseButton-primary"]:hover {
    background: #6E7B94 !important;
}

/* Link buttons */
[data-testid="stBaseLinkButton-primary"] a,
[data-testid="stBaseLinkButton-secondary"] a {
    color: #8B9DC3 !important;
    text-decoration: none !important;
}

/* Containers with border */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.015) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 10px !important;
    transition: border-color 0.2s ease !important;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(255, 255, 255, 0.12) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #07070A !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}

/* Sidebar expand button — always visible */
[data-testid="collapsedControl"] {
    visibility: visible !important;
    display: flex !important;
    z-index: 1000000 !important;
    color: #FFF !important;
}

/* Metric styling */
[data-testid="stMetricValue"] {
    font-size: 1.1rem !important;
    font-weight: 500 !important;
    color: #FFF !important;
}
[data-testid="stMetricLabel"] {
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    font-size: 0.65rem !important;
    color: rgba(255,255,255,0.35) !important;
}

/* Expander styling */
[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.015) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 10px !important;
}

/* Divider */
hr {
    border-color: rgba(255, 255, 255, 0.06) !important;
}

/* Inline code (used for skill chips) */
code {
    background: rgba(90, 101, 122, 0.15) !important;
    color: #C8CCD4 !important;
    padding: 0.15rem 0.5rem !important;
    border-radius: 4px !important;
    font-size: 0.8rem !important;
    font-family: 'Inter', sans-serif !important;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Success/info/warning/error alerts */
[data-testid="stAlert"] {
    border-radius: 8px !important;
}
</style>"""
    st.html(custom_css)
