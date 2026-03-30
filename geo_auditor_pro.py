import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# --- Page Configuration ---
st.set_page_config(page_title="GEO Auditor Pro", page_icon="🌐", layout="wide")

# --- API Setup with Diagnostics ---
def initialize_gemini():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("Missing GOOGLE_API_KEY in Streamlit Secrets.")
        return None

    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    try:
        # Check which models are actually available to your key
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority list: Use Flash if available, otherwise Pro, otherwise whatever is first
        if 'models/gemini-1.5-flash' in available_models:
            return genai.GenerativeModel('models/gemini-1.5-flash')
        elif 'models/gemini-1.5-pro' in available_models:
            return genai.GenerativeModel('models/gemini-1.5-pro')
        elif available_models:
            return genai.GenerativeModel(available_models[0])
        else:
            st.error("Your API key doesn't have access to any Generative models.")
            return None
    except Exception as e:
        st.error(f"Failed to connect to Google AI: {e}")
        return None

def scrape_website(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Clean text extraction
        for script in soup(["script", "style"]):
            script.extract()
        
        text = " ".join([p.get_text() for p in soup.find_all('p')[:15]])
        headings = [h.get_text() for h in soup.find_all(['h1', 'h2'])]
        return {"content": text, "headings": headings, "url": url}
    except Exception as e:
        return {"error": str(e)}

# --- UI ---
st.title("🌐 GEO Auditor Professional")
st.caption("Analyzing for Generative Engine Optimization (AI Search Visibility)")

model = initialize_gemini()

target_url = st.text_input("Enter URL to Audit:", placeholder="https://newfrontier.us/")

if st.button("Run Audit"):
    if not model:
        st.error("Model initialization failed. Check your API key.")
    elif target_url:
        with st.spinner("Step 1: Scrapping website content..."):
            site_data = scrape_website(target_url)
            
        if "error" in site_data:
            st.error(f"Scraping Error: {site_data['error']}")
        else:
            with st.spinner("Step 2: AI Analyzing for GEO factors..."):
                try:
                    prompt = f"""
                    You are a GEO (Generative Engine Optimization) expert. 
                    Perform a professional audit on this content:
                    
                    URL: {site_data['url']}
                    Headings: {site_data['headings']}
                    Content: {site_data['content']}
                    
                    Structure your response with:
                    1. GEO Citability Score (0-100)
                    2. Factual Density Analysis (Is the content too vague for AI?)
                    3. Optimization Checklist (What to change to get cited by Perplexity/Gemini)
                    """
                    response = model.generate_content(prompt)
                    st.success("Audit Complete!")
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI Analysis Error: {e}")
    else:
        st.warning("Please enter a URL.")
