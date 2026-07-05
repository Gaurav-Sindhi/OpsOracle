"""OpsOracle Frontend - Real Streamlit Dashboard"""

import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="OpsOracle", page_icon="🤖", layout="wide")

BACKEND_URL = "http://localhost:8000"


def check_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def get_incidents():
    try:
        response = requests.get(f"{BACKEND_URL}/api/incidents/", timeout=5)
        if response.status_code == 200:
            return response.json().get("incidents", [])
        return []
    except Exception:
        return []


def trigger_test_incident():
    payload = {
        "logs": {
            "summary": "Lambda function timeout error detected",
            "error_count": 15,
            "warning_count": 3
        },
        "metrics": {
            "cpu_utilization": 92,
            "memory_utilization": 88,
            "request_latency": 850,
            "error_rate": 0.35,
            "request_count": 1200
        },
        "service": "lambda"
    }
    try:
        response = requests.post(f"{BACKEND_URL}/api/incidents/analyze", json=payload, timeout=30)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None


# ---------- Sidebar ----------
st.sidebar.title("OpsOracle")
st.sidebar.caption("Autonomous incident response")

backend_ok = check_backend()
status_label = "Connected" if backend_ok else "Disconnected"
status_color = "green" if backend_ok else "red"
st.sidebar.markdown(f":{status_color}[●] Backend {status_label}")
st.sidebar.caption("LLM: Llama 3.3 70B (Groq)")

page = st.sidebar.radio("Navigate", ["Dashboard", "Incidents", "Analytics", "Settings"])

if not backend_ok:
    st.error("Backend is not reachable at " + BACKEND_URL + ". Start it with: python -m backend.main")
    st.stop()

incidents = get_incidents()

# ---------- Dashboard ----------
if page == "Dashboard":
    st.title("Dashboard")
    st.caption("Real-time incident monitoring and metrics")

    total = len(incidents)
    critical = sum(1 for i in incidents if i.get("cascade", {}).get("blast_radius_level") == "critical")
    severities = [i.get("severity", "MEDIUM") for i in incidents]
    high_or_critical = sum(1 for s in severities if s in ("HIGH", "CRITICAL"))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total incidents", total)
    col2.metric("Critical blast radius", critical)
    col3.metric("High/Critical severity", high_or_critical)
    col4.metric("Resolution time", "under 60s" if total > 0 else "—")

    st.divider()

    if total == 0:
        st.info("No incidents yet. Trigger a test incident below or send a real one via the API.")
        if st.button("Trigger test incident"):
            with st.spinner("Running full pipeline..."):
                result = trigger_test_incident()
            if result:
                st.success(f"Incident {result['incident_id']} created")
                st.rerun()
    else:
        st.subheader("Latest incident")
        latest = incidents[-1]
        analysis = latest.get("analysis", {})
        cascade = latest.get("cascade", {})

        sev = analysis.get("severity", "MEDIUM")
        sev_color = {"CRITICAL": "red", "HIGH": "orange", "MEDIUM": "blue", "LOW": "green"}.get(sev, "gray")

        st.markdown(f"**{latest.get('id')}** — :{sev_color}[{sev} severity]")
        st.write(analysis.get("root_cause", "No analysis available"))

        c1, c2 = st.columns(2)
        with c1:
            st.caption("Blast radius")
            st.write(f"{cascade.get('blast_radius_level', 'unknown').upper()} — {cascade.get('total_affected', 0)} services affected")
        with c2:
            st.caption("Recommended fix")
            st.write(analysis.get("recommended_fix", "N/A")[:150] + "...")


# ---------- Incidents ----------
elif page == "Incidents":
    st.title("Incidents")
    st.caption("Browse and analyze incidents")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Trigger test incident", use_container_width=True):
            with st.spinner("Running full pipeline..."):
                result = trigger_test_incident()
            if result:
                st.success("Created")
                st.rerun()

    if not incidents:
        st.info("No incidents found. Use the button above to generate a test incident.")
    else:
        st.write(f"**{len(incidents)} incident(s) found**")
        for incident in reversed(incidents):
            analysis = incident.get("analysis", {})
            cascade = incident.get("cascade", {})
            sev = analysis.get("severity", "MEDIUM")
            sev_color = {"CRITICAL": "red", "HIGH": "orange", "MEDIUM": "blue", "LOW": "green"}.get(sev, "gray")

            with st.expander(f"{incident.get('id')} — :{sev_color}[{sev}]"):
                st.markdown("**Root cause**")
                st.write(analysis.get("root_cause", "N/A"))

                st.markdown("**Recommended fix**")
                st.write(analysis.get("recommended_fix", "N/A"))

                st.markdown("**Remediation steps**")
                for step in analysis.get("remediation_steps", []):
                    st.write(f"- {step}")

                st.markdown("**Blast radius**")
                st.write(f"{cascade.get('blast_radius_level', 'unknown').upper()} — "
                          f"{', '.join(cascade.get('all_affected_services', []))}")

                st.caption(f"Model: {analysis.get('model', 'unknown')} · "
                           f"Timestamp: {analysis.get('timestamp', 'N/A')}")

    st.markdown("---")
    st.subheader("🔴 Real AWS Incidents")
    st.caption("Triggers actual Lambda failure → reads real CloudWatch logs → full pipeline")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button("⚡ Lambda Timeout", use_container_width=True):
            with st.spinner("Triggering real AWS Lambda... reading CloudWatch..."):
                r = requests.post(
                    f"{BACKEND_URL}/api/incidents/trigger-aws-incident",
                    params={"failure_type": "timeout"},
                    timeout=60
                )
                if r.status_code == 200:
                    data = r.json()
                    st.success(f"Real AWS incident: {data['incident_id']}")
                    st.rerun()
                else:
                    st.error(f"Failed: {r.text}")

    with col_b:
        if st.button("💾 Memory Error", use_container_width=True):
            with st.spinner("Triggering real AWS Lambda... reading CloudWatch..."):
                r = requests.post(
                    f"{BACKEND_URL}/api/incidents/trigger-aws-incident",
                    params={"failure_type": "memory"},
                    timeout=60
                )
                if r.status_code == 200:
                    data = r.json()
                    st.success(f"Real AWS incident: {data['incident_id']}")
                    st.rerun()
                else:
                    st.error(f"Failed: {r.text}")

    with col_c:
        if st.button("🔌 DB Connection", use_container_width=True):
            with st.spinner("Triggering real AWS Lambda... reading CloudWatch..."):
                r = requests.post(
                    f"{BACKEND_URL}/api/incidents/trigger-aws-incident",
                    params={"failure_type": "connection"},
                    timeout=60
                )
                if r.status_code == 200:
                    data = r.json()
                    st.success(f"Real AWS incident: {data['incident_id']}")
                    st.rerun()
                else:
                    st.error(f"Failed: {r.text}")

# ---------- Analytics ----------
elif page == "Analytics":
    st.title("Analytics")
    st.caption("Trends across all incidents")

    if not incidents:
        st.info("No data yet. Trigger an incident first to see analytics.")
    else:
        sev_counts = {}
        service_counts = {}
        for i in incidents:
            sev = i.get("analysis", {}).get("severity", "MEDIUM")
            sev_counts[sev] = sev_counts.get(sev, 0) + 1
            for svc in i.get("cascade", {}).get("all_affected_services", []):
                service_counts[svc] = service_counts.get(svc, 0) + 1

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Incidents by severity")
            st.bar_chart(sev_counts)
        with col2:
            st.subheader("Most affected services")
            st.bar_chart(service_counts)


# ---------- Settings ----------
elif page == "Settings":
    st.title("Settings")

    st.markdown("**Backend URL**")
    st.code(BACKEND_URL)

    st.markdown("**LLM Provider**")
    st.write("Groq API — Llama 3.3 70B (free tier, no card required)")

    st.markdown("**Connection status**")
    if check_backend():
        st.success("Backend is reachable")
    else:
        st.error("Backend is not reachable")

    st.divider()
    st.caption("OpsOracle v1.0.0 — built by Gaurav Sindhi")       