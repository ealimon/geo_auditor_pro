import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="GEO Auditor Pro (Gemini Edition)", page_icon="🌐")

# --- API Setup ---
# This looks for "GOOGLE_API_KEY" in your Streamlit Secrets
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Google API Key not found in Secrets. Please add 'GOOGLE_API_KEY' to your Streamlit settings.")

def scrape_website(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = " ".join([p.get_text() for p in soup.find_all('p')[:15]])
        headings = [h.get_text() for h in soup.find_all(['h1', 'h2'])]
        return {"content": text, "headings": headings, "url": url}
    except Exception as e:
        return {"error": str(e)}

def run_gemini_audit(data):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    You are a GEO (Generative Engine Optimization) expert. 
    Audit this website content to see how well AI engines (like Gemini/Perplexity) can cite it.
    
    URL: {data['url']}
    Headings: {data['headings']}
    Content Snippet: {data['content']}
    
    Provide:
    1. GEO Citability Score (0-100)
    2. Analysis of Factual Density
    3. Recommendations to improve 'AI visibility'
    """
    response = model.generate_content(prompt)
    return response.text

# --- UI ---
st.title("🌐 GEO Auditor Professional")
st.subheader("Powered by Google Gemini")

target_url = st.text_input("Enter URL to Audit:", placeholder="https://example.com")

if st.button("Run Audit"):
    if target_url:
        with st.spinner("Scraping and analyzing..."):
            site_data = scrape_website(target_url)
            if "error" in site_data:
                st.error(f"Error: {site_data['error']}")
            else:
                report = run_gemini_audit(site_data)
                st.markdown("### 📊 Audit Report")
                st.write(report)
    else:
        st.warning("Please enter a URL.")
