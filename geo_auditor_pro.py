import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="GEO Auditor Professional",
    page_icon="🤖",
    layout="wide"
)

# --- Custom CSS for Stability & Style ---
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar: API Keys & Settings ---
with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.info("This app audits your site for 'Generative Engine Optimization' (GEO) to help you rank in AI search results.")

# --- Helper Functions ---
def scrape_robust(url):
    """Scrapes a website with professional headers to prevent blocks."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Trigger error for 403/404/500
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract meaningful data
        page_text = [p.get_text() for p in soup.find_all('p')]
        headings = [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])]
        schema = soup.find_all('script', type='application/ld+json')
        
        return {
            "content": " ".join(page_text[:15]), # Top 15 paragraphs
            "headings": headings,
            "has_schema": len(schema) > 0,
            "char_count": len(response.text)
        }
    except Exception as e:
        return {"error": str(e)}

def analyze_geo(data, api_key):
    """Uses GPT-4o to perform the GEO Audit."""
    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""
    Analyze the following website data for Generative Engine Optimization (GEO). 
    GEO focuses on how likely an LLM (like ChatGPT or Perplexity) is to cite this content.
    
    Data:
    Content: {data['content'][:3000]}
    Headings: {data['headings']}
    Schema Present: {data['has_schema']}
    
    Provide a professional audit:
    1. **Factual Density Score (0-100)**: Does it provide hard data or just fluff?
    2. **Citatability**: Are there specific "nuggets" or quotes an AI can cite?
    3. **Structural Clarity**: Are headings optimized for 'Natural Language Queries'?
    4. **The 'GEO Gap'**: What is missing that would make an AI prefer this site?
    5. **3 Critical Recommendations**: Immediate changes.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a senior GEO strategist."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- Main UI ---
st.title("🌐 GEO Auditor Pro")
st.caption("Optimize your website for the Age of AI Search (Perplexity, SearchGPT, Gemini)")

target_url = st.text_input("Enter Website URL to Audit:", placeholder="https://example.com")

if st.button("Start Professional Audit"):
    if not api_key:
        st.error("Please enter an OpenAI API Key in the sidebar.")
    elif not target_url:
        st.warning("Please enter a URL.")
    else:
        # Progress Tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Scrape
        status_text.text("Connecting to website and bypassing firewalls...")
        progress_bar.progress(25)
        site_data = scrape_robust(target_url)
        
        if "error" in site_data:
            st.error(f"Audit Failed: {site_data['error']}")
            st.info("Tip: Some sites (like LinkedIn/Amazon) block basic scrapers. Try a blog post or a service page.")
        else:
            # Step 2: Analyze
            status_text.text("Analyzing content for LLM-citatability...")
            progress_bar.progress(60)
            
            try:
                report = analyze_geo(site_data, api_key)
                progress_bar.progress(100)
                status_text.text("Audit Complete!")
                
                # Step 3: Display Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Technical Readiness", "Pass" if site_data['has_schema'] else "Fail")
                with col2:
                    st.metric("Content Depth", f"{len(site_data['headings'])} Sections")
                with col3:
                    st.metric("Status", "Analyzed")
                
                # Step 4: Display Report
                st.divider()
                st.markdown("### 📊 GEO Professional Audit Report")
                st.markdown(report)
                
                # Step 5: Download Option
                st.download_button("Download Audit Report", report, file_name="geo_audit.txt")
                
            except Exception as e:
                st.error(f"AI Analysis Error: {e}")

# --- Footer ---
st.divider()
st.caption("Built for Generative Engine Optimization Testing | Professional Grade")
