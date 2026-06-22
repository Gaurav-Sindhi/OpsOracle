"""OpsOracle Frontend - Streamlit Dashboard"""
import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)
import streamlit as st
import requests
import json
from datetime import datetime
from backend.config import Config

st.set_page_config(page_title="OpsOracle", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    .main { padding: 2rem; }
    .metric-card { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px; border-radius: 10px; color: white;
    }
</style>
""", unsafe_allow_html=True)

BACKEND_URL = f"http://localhost:{Config.API_PORT}"

st.sidebar.title("🤖 OpsOracle")
st.sidebar.write("AI-Powered Incident Response System")

page = st.sidebar.radio("Navigation", ["Dashboard", "Incidents", "Analytics", "Settings"])

def check_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False

st.sidebar.markdown("---")
st.sidebar.write("✅ Connected" if check_backend() else "❌ Disconnected")

if page == "Dashboard":
    st.title("🎯 Dashboard")
    st.write("Real-time incident monitoring and metrics")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Incidents", 3)
    with col2:
        st.metric("MTTR (min)", 15)

elif page == "Incidents":
    st.title("🚨 Incidents")
    st.write("Browse and analyze incidents")
    
    if st.button("Fetch Recent Incidents"):
        try:
            response = requests.get(f"{BACKEND_URL}/api/incidents")
            if response.status_code == 200:
                data = response.json()
                st.success(f"Found {data.get('total', 0)} incidents")
            else:
                st.error("Failed to fetch incidents")
        except Exception as e:
            st.error(f"Error: {str(e)}")

elif page == "Analytics":
    st.title("📊 Analytics")
    st.write("View analytics and metrics")

elif page == "Settings":
    st.title("⚙️ Settings")
    st.write(f"Backend URL: {BACKEND_URL}")
    st.write(f"Using Claude API (Anthropic)")
    
    if st.button("Test Backend"):
        if check_backend():
            st.success("✅ Backend is running!")
        else:
            st.error("❌ Backend is not responding")

st.markdown("---")
st.caption("OpsOracle v1.0.0 - Powered by Claude (Anthropic)")