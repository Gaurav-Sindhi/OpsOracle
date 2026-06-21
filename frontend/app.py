import streamlit as st
import requests
import json
from datetime import datetime
from config import Config

# Page config
st.set_page_config(
    page_title="OpsOracle",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
    .main { padding: 2rem; }
    .metric-card { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .success { color: #10b981; font-weight: bold; }
    .error { color: #ef4444; font-weight: bold; }
    .warning { color: #f59e0b; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Backend URL
BACKEND_URL = f"http://localhost:{Config.API_PORT}"

# ============ SIDEBAR ============
st.sidebar.title("🤖 OpsOracle")
st.sidebar.write("AI-Powered Incident Response System")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Incidents", "RAG Knowledge Base", "Settings"]
)

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/",
            timeout=2
        )
        return response.status_code == 200

    except Exception:
        return False


st.sidebar.markdown("---")

st.sidebar.write(
    "**Status:** Connected ✅"
    if check_backend()
    else "**Status:** Disconnected ❌"
)

# ============ DASHBOARD PAGE ============
if page == "Dashboard":
    st.title("🎯 Incident Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Real-time Metrics")
        
        try:
            response = requests.get(f"{BACKEND_URL}/api/metrics/all")
            if response.status_code == 200:
                metrics = response.json()['metrics']
                
                # Display metrics
                for service, data in metrics.items():
                    if service != 'timestamp' and isinstance(data, dict):
                        st.write(f"**{service.upper()}**")
                        if 'datapoints' in data:
                            st.write(f"Data points: {len(data['datapoints'])}")
            else:
                st.error("Failed to fetch metrics")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with col2:
        st.subheader("🔍 Anomaly Detection")
        
        # Input metric values
        cpu = st.slider("CPU Utilization (%)", 0, 100, 50)
        memory = st.slider("Memory Utilization (%)", 0, 100, 60)
        latency = st.slider("Request Latency (ms)", 0, 5000, 200)
        
        if st.button("🔎 Check for Anomalies"):
            try:
                payload = {
                    "cpu_utilization": cpu,
                    "memory_utilization": memory,
                    "request_latency": latency
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/api/anomaly/predict",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()['prediction']
                    
                    if result['is_anomaly']:
                        st.error(f"🚨 **ANOMALY DETECTED**")
                        st.write(f"Score: {result['anomaly_score']:.3f}")
                        st.write(f"Confidence: {result['confidence']:.1%}")
                    else:
                        st.success(f"✅ **No Anomaly Detected**")
                        st.write(f"Score: {result['anomaly_score']:.3f}")
                else:
                    st.error("Failed to analyze")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Fetch logs section
    st.subheader("📋 Fetch CloudWatch Logs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        log_group = st.text_input("Log Group Name", "/aws/lambda/my-function")
    
    with col2:
        minutes = st.slider("Minutes Back", 1, 60, 10)
    
    if st.button("📥 Fetch Logs"):
        try:
            payload = {
                "log_group": log_group,
                "minutes_back": minutes
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/logs/fetch",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                parsed = data['parsed_logs']
                
                st.success(f"✅ Fetched {parsed['error_count']} errors, {parsed['warning_count']} warnings")
                
                # Show detailed logs
                with st.expander("📊 View Detailed Logs"):
                    st.json(parsed)
            else:
                st.error("Failed to fetch logs")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ============ INCIDENTS PAGE ============
elif page == "Incidents":
    st.title("🚨 Incidents")
    
    # Get incidents
    try:
        response = requests.get(f"{BACKEND_URL}/api/incidents?limit=20")
        
        if response.status_code == 200:
            data = response.json()
            incidents = data['incidents']
            stats = data['stats']
            
            # Stats
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Incidents", stats['total_incidents'])
            with col2:
                st.metric("Avg Duration", f"{stats['average_duration_minutes']:.1f} min")
            with col3:
                severities = stats.get('by_severity', {})
                st.metric("Critical", severities.get('CRITICAL', 0))
            with col4:
                st.metric("High", severities.get('HIGH', 0))
            
            st.markdown("---")
            
            # Incidents table
            st.subheader("📋 Recent Incidents")
            
            if incidents:
                for incident in incidents[:10]:
                    with st.expander(
                        f"🔴 {incident.get('id')} - {incident.get('error_type', 'Unknown')} "
                        f"({incident.get('duration_minutes', 0)} min)"
                    ):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**Severity:** {incident.get('severity', 'N/A')}")
                        with col2:
                            st.write(f"**Duration:** {incident.get('duration_minutes', 0)} minutes")
                        with col3:
                            st.write(f"**Services:** {len(incident.get('affected_services', []))}")
                        
                        st.write(f"**Root Cause:** {incident.get('analysis', {}).get('root_cause', 'N/A')}")
                        st.write(f"**Fix:** {incident.get('analysis', {}).get('recommended_fix', 'N/A')}")
            else:
                st.info("No incidents found")
                
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ============ RAG PAGE ============
elif page == "RAG Knowledge Base":
    st.title("📚 RAG Knowledge Base")
    
    # Get knowledge base stats
    try:
        response = requests.get(f"{BACKEND_URL}/api/rag/stats")
        
        if response.status_code == 200:
            stats = response.json()['stats']
            
            st.metric("Total Incidents in KB", stats['total_incidents'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 By Error Type")
                error_types = stats.get('error_types', {})
                st.bar_chart({k: v for k, v in list(error_types.items())[:5]})
            
            with col2:
                st.subheader("🔧 By Service")
                services = stats.get('services', {})
                st.bar_chart({k: v for k, v in list(services.items())[:5]})
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Search knowledge base
    st.subheader("🔍 Search Knowledge Base")
    
    query = st.text_input("Enter error description or query", "Lambda timeout error")
    
    if st.button("🔎 Search"):
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/rag/search",
                params={"query": query, "top_k": 3}
            )
            
            if response.status_code == 200:
                results = response.json()['results']
                
                st.success(f"Found {len(results)} similar incidents")
                
                for idx, result in enumerate(results, 1):
                    incident = result['incident']
                    similarity = result['similarity_score']
                    
                    st.write(f"**{idx}. {incident.get('id')}** (Similarity: {similarity:.1%})")
                    st.write(f"Root Cause: {incident.get('root_cause', 'N/A')}")
                    st.write(f"Fix: {incident.get('fix_applied', 'N/A')}")
                    st.divider()
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ============ SETTINGS PAGE ============
elif page == "Settings":
    st.title("⚙️ Settings")
    
    st.subheader("🔐 Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**API URL:** {BACKEND_URL}")
        st.write(f"**API Host:** {Config.API_HOST}")
        st.write(f"**API Port:** {Config.API_PORT}")
    
    with col2:
        st.write(f"**Region:** {Config.AWS_REGION}")
        st.write(f"**Log Level:** {Config.LOG_LEVEL}")
        st.write(f"**Auto Remediation:** {'Enabled' if Config.ENABLE_AUTO_REMEDIATION else 'Disabled'}")
    
    st.markdown("---")
    
    st.subheader("🔧 Remediation Settings")
    
    remediation_enabled = st.checkbox(
        "Enable Auto Remediation",
        Config.ENABLE_AUTO_REMEDIATION
    )
    
    remediation_level = st.selectbox(
        "Remediation Permission Level",
        options=[1, 2, 3],
        index=Config.AUTO_REMEDIATION_LEVEL - 1,
        format_func=lambda x: {
            1: "1 - Suggest Only",
            2: "2 - Ask Confirmation",
            3: "3 - Auto Execute"
        }[x]
    )
    
    if st.button("💾 Save Settings"):
        st.success("✅ Settings saved!")
    
    st.markdown("---")
    
    st.subheader("📊 System Status")
    
    if check_backend():
        st.success("✅ Backend is running")
    else:
        st.error("❌ Backend is not responding")
        st.write("Start the backend with: `python main.py`")

st.markdown("---")
st.caption("OpsOracle v1.0.0 - AI-Powered Incident Response System")