"""OpsOracle — Autonomous Incident Response Dashboard v1.2"""

import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="OpsOracle", page_icon="🔴", layout="wide", initial_sidebar_state="expanded")

BACKEND_URL = "http://localhost:8000"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@300;400;500;600&display=swap');
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] { background: #080B10 !important; color: #C8D0DC !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stSidebar"] { background: #0C1017 !important; border-right: 1px solid #1C2333 !important; }
[data-testid="stSidebar"] * { color: #C8D0DC !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1400px !important; }
h1, h2, h3 { font-family: 'Inter', sans-serif !important; letter-spacing: -0.02em; }
.oc-card { background: #0C1017; border: 1px solid #1C2333; border-radius: 8px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; }
.oc-glow { background: #0C1017; border: 1px solid #1C2333; border-radius: 8px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 24px rgba(255,59,48,0.06); }
.metric-card { background: #0C1017; border: 1px solid #1C2333; border-radius: 8px; padding: 1.1rem 1.3rem; }
.metric-card .lbl { font-size: 10px; font-family: 'IBM Plex Mono',monospace; color: #4A5568; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }
.metric-card .val { font-size: 28px; font-weight: 600; letter-spacing: -0.03em; line-height: 1; color: #E8EDF5; }
.metric-card .sub { font-size: 10px; color: #4A5568; margin-top: 6px; font-family: 'IBM Plex Mono',monospace; }
.metric-card.danger { border-color: rgba(255,59,48,0.35); } .metric-card.danger .val { color: #FF3B30; }
.metric-card.warning { border-color: rgba(255,149,0,0.35); } .metric-card.warning .val { color: #FF9500; }
.metric-card.success { border-color: rgba(52,199,89,0.35); } .metric-card.success .val { color: #34C759; }
.metric-card.info { border-color: rgba(0,122,255,0.35); } .metric-card.info .val { color: #007AFF; }
.badge { display:inline-block; font-family:'IBM Plex Mono',monospace; font-size:10px; font-weight:500; padding:3px 8px; border-radius:4px; letter-spacing:0.06em; text-transform:uppercase; }
.badge-critical { background:rgba(255,59,48,0.15); color:#FF3B30; border:1px solid rgba(255,59,48,0.3); }
.badge-high { background:rgba(255,149,0,0.15); color:#FF9500; border:1px solid rgba(255,149,0,0.3); }
.badge-medium { background:rgba(0,122,255,0.15); color:#007AFF; border:1px solid rgba(0,122,255,0.3); }
.badge-low { background:rgba(52,199,89,0.15); color:#34C759; border:1px solid rgba(52,199,89,0.3); }
.badge-aws { background:rgba(255,153,0,0.12); color:#FF9900; border:1px solid rgba(255,153,0,0.3); }
.inc-card { background:#0C1017; border:1px solid #1C2333; border-radius:8px; padding:1rem 1.25rem; margin-bottom:10px; }
.inc-card.aws-src { border-left:3px solid #FF9900; }
.inc-card.manual-src { border-left:3px solid #007AFF; }
.inc-hdr { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }
.inc-id { font-family:'IBM Plex Mono',monospace; font-size:12px; color:#E8EDF5; font-weight:500; }
.inc-time { font-family:'IBM Plex Mono',monospace; font-size:11px; color:#4A5568; }
.inc-cause { font-size:13px; color:#8A95A5; line-height:1.5; margin-bottom:10px; }
.inc-footer { display:flex; gap:8px; flex-wrap:wrap; align-items:center; }
.tag { font-family:'IBM Plex Mono',monospace; font-size:10px; color:#4A5568; background:#141920; border:1px solid #1C2333; border-radius:4px; padding:2px 7px; }
.live-dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:#34C759; margin-right:6px; animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
.sec-title { font-size:11px; font-family:'IBM Plex Mono',monospace; color:#4A5568; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.75rem; padding-bottom:6px; border-bottom:1px solid #1C2333; }
.stButton > button { background:#141920 !important; color:#C8D0DC !important; border:1px solid #1C2333 !important; border-radius:6px !important; font-family:'IBM Plex Mono',monospace !important; font-size:12px !important; transition:all 0.15s !important; }
.stButton > button:hover { background:#1C2333 !important; border-color:#2D3748 !important; color:#E8EDF5 !important; }
[data-testid="stExpander"] { background:#0C1017 !important; border:1px solid #1C2333 !important; border-radius:8px !important; margin-bottom:8px !important; }
hr { border-color:#1C2333 !important; }
code, pre { font-family:'IBM Plex Mono',monospace !important; background:#141920 !important; color:#7DD3FC !important; border-radius:4px !important; font-size:12px !important; }
.anomaly-positive { background:rgba(255,59,48,0.1); border:1px solid rgba(255,59,48,0.3); border-radius:6px; padding:8px 12px; font-family:'IBM Plex Mono',monospace; font-size:11px; color:#FF3B30; }
.anomaly-negative { background:rgba(52,199,89,0.1); border:1px solid rgba(52,199,89,0.3); border-radius:6px; padding:8px 12px; font-family:'IBM Plex Mono',monospace; font-size:11px; color:#34C759; }
.rag-item { background:#141920; border:1px solid #1C2333; border-radius:6px; padding:8px 12px; margin-bottom:6px; font-size:12px; color:#8A95A5; }
.rag-score { font-family:'IBM Plex Mono',monospace; font-size:10px; color:#4A5568; margin-bottom:3px; }
.postmortem-box { background:#0D1117; border:1px solid #1C2333; border-radius:8px; padding:1.25rem; font-size:13px; color:#C8D0DC; line-height:1.8; white-space:pre-wrap; font-family:'Inter',sans-serif; max-height:500px; overflow-y:auto; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def check_backend():
    try:
        return requests.get(f"{BACKEND_URL}/", timeout=2).status_code == 200
    except Exception:
        return False

def get_incidents():
    try:
        r = requests.get(f"{BACKEND_URL}/api/incidents/", timeout=5)
        return r.json().get("incidents", []) if r.status_code == 200 else []
    except Exception:
        return []

def trigger_test():
    payload = {"logs": {"summary": "Lambda timeout error detected", "error_count": 15, "warning_count": 3},
               "metrics": {"cpu_utilization": 92, "memory_utilization": 88, "request_latency": 850, "error_rate": 0.35, "request_count": 1200},
               "service": "lambda"}
    try:
        r = requests.post(f"{BACKEND_URL}/api/incidents/analyze", json=payload, timeout=60)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def trigger_aws(failure_type="timeout"):
    try:
        r = requests.post(f"{BACKEND_URL}/api/incidents/trigger-aws-incident",
                         params={"failure_type": failure_type}, timeout=60)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def get_postmortem_pdf(incident_id):
    try:
        r = requests.get(f"{BACKEND_URL}/api/incidents/{incident_id}/postmortem/pdf", timeout=30)
        return r.content if r.status_code == 200 else None
    except Exception:
        return None

def sev_badge(sev):
    sev = (sev or "MEDIUM").upper()
    cls = {"CRITICAL":"critical","HIGH":"high","MEDIUM":"medium","LOW":"low"}.get(sev,"medium")
    return f'<span class="badge badge-{cls}">{sev}</span>'

def fmt_time(ts):
    try:
        return datetime.fromisoformat(ts).strftime("%d %b %H:%M:%S")
    except Exception:
        return ts or "—"


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-size:18px;font-weight:600;letter-spacing:-0.03em;color:#E8EDF5;">OpsOracle</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;">Incident Response Platform</div>', unsafe_allow_html=True)

    backend_ok = check_backend()
    if backend_ok:
        st.markdown('<span class="live-dot"></span><span style="font-size:12px;color:#34C759;">Backend online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="font-size:12px;color:#FF3B30;">⬤ Backend offline</span>', unsafe_allow_html=True)

    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;margin-top:4px;margin-bottom:1.5rem;">LLM · Llama 3.3 70B (Groq)</div>', unsafe_allow_html=True)

    page = st.radio("Navigate", ["Dashboard", "Incidents", "Analytics", "AWS Trigger", "Settings"], label_visibility="collapsed")

    incidents = get_incidents() if backend_ok else []

    st.markdown("---")
    total = len(incidents)
    critical = sum(1 for i in incidents if i.get("analysis", {}).get("severity", "").upper() == "CRITICAL")
    aws_real = sum(1 for i in incidents if i.get("source") == "REAL AWS")
    anomalies = sum(1 for i in incidents if i.get("anomaly", {}).get("is_anomaly"))

    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;">INCIDENTS</div><div style="font-size:22px;font-weight:600;color:#E8EDF5;">{total}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#FF3B30;margin-top:8px;">CRITICAL: {critical}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#FF9900;margin-top:4px;">FROM AWS: {aws_real}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#FF6B6B;margin-top:4px;">ANOMALIES: {anomalies}</div>', unsafe_allow_html=True)

if not backend_ok:
    st.error("Backend offline. Run: python -m backend.main")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    col_h, col_btn = st.columns([4, 1])
    with col_h:
        st.markdown('<h1 style="font-size:24px;font-weight:600;color:#E8EDF5;margin:0;">Command Centre</h1>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;margin-top:4px;">Real-time incident detection · Isolation Forest · RAG · Groq LLM</div>', unsafe_allow_html=True)
    with col_btn:
        if st.button("+ Trigger Test", use_container_width=True):
            with st.spinner("Running full pipeline..."):
                r = trigger_test()
            if r:
                st.success(f"Created {r['incident_id']}")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    high = sum(1 for i in incidents if i.get("analysis", {}).get("severity", "").upper() == "HIGH")
    rag_kb = max((i.get("rag_context", {}).get("knowledge_base_size", 0) for i in incidents), default=0)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card info"><div class="lbl">Total Incidents</div><div class="val">{total}</div><div class="sub">all time</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card danger"><div class="lbl">Critical</div><div class="val">{critical}</div><div class="sub">blast radius</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card warning"><div class="lbl">Anomalies Detected</div><div class="val">{anomalies}</div><div class="sub">isolation forest</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card success"><div class="lbl">RAG Knowledge Base</div><div class="val">{rag_kb}</div><div class="sub">incidents stored</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not incidents:
        st.markdown('<div class="oc-card" style="text-align:center;padding:3rem;"><div style="font-size:2rem;margin-bottom:1rem;">📡</div><div style="font-size:14px;color:#8A95A5;">No incidents yet — click Trigger Test to run the full pipeline</div></div>', unsafe_allow_html=True)
    else:
        left, right = st.columns([3, 2])

        with left:
            st.markdown('<div class="sec-title">Recent Incidents</div>', unsafe_allow_html=True)
            for inc in list(reversed(incidents))[:5]:
                analysis = inc.get("analysis", {})
                cascade = inc.get("cascade", {})
                sev = analysis.get("severity", "MEDIUM").upper()
                source = inc.get("source", "manual")
                src_cls = "aws-src" if source == "REAL AWS" else "manual-src"
                src_badge = '<span class="badge badge-aws">AWS</span>' if source == "REAL AWS" else '<span class="badge badge-medium">TEST</span>'
                root = analysis.get("root_cause", "—")
                root_short = root[:110] + "..." if len(root) > 110 else root
                affected = cascade.get("total_affected", 0)
                blast = cascade.get("blast_radius_level", "unknown").upper()
                is_anomaly = inc.get("anomaly", {}).get("is_anomaly", False)
                anomaly_badge = '<span class="badge badge-critical">⚠ ANOMALY</span>' if is_anomaly else ''

                st.markdown(f"""
                <div class="inc-card {src_cls}">
                    <div class="inc-hdr">
                        <span class="inc-id">{inc.get('id','—')[:28]}...</span>
                        <div style="display:flex;gap:5px;align-items:center;">{anomaly_badge}{src_badge}{sev_badge(sev)}</div>
                    </div>
                    <div class="inc-cause">{root_short}</div>
                    <div class="inc-footer">
                        <span class="tag">{blast} blast</span>
                        <span class="tag">{affected} services</span>
                        <span class="inc-time">{fmt_time(inc.get('timestamp',''))}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

        with right:
            latest = incidents[-1]
            analysis = latest.get("analysis", {})
            cascade = latest.get("cascade", {})
            anomaly = latest.get("anomaly", {})
            rag_ctx = latest.get("rag_context", {})

            st.markdown('<div class="sec-title">Latest Analysis</div>', unsafe_allow_html=True)

            root_cause_text = analysis.get('root_cause', '—')
            recommended_fix_text = str(analysis.get('recommended_fix', '—'))[:200]
            model_name = analysis.get('model', '—').upper()
            confidence = int(analysis.get('confidence', 0) * 100)
            anomaly_score = anomaly.get('anomaly_score', 0)
            is_anomaly = anomaly.get('is_anomaly', False)
            similar_count = rag_ctx.get('similar_count', 0)
            anomaly_color = '#FF3B30' if is_anomaly else '#34C759'
            anomaly_label = '⚠ ANOMALY DETECTED' if is_anomaly else '✓ NORMAL'
            services_html = "".join(f'<span class="tag">{s}</span>' for s in cascade.get("all_affected_services", []))

            latest_html = f"""<div class="oc-glow">
                <div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.1em;">Root Cause</div>
                <div style="font-size:13px;color:#C8D0DC;line-height:1.6;margin-bottom:12px;">{root_cause_text}</div>
                <div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.1em;">Recommended Fix</div>
                <div style="font-size:12px;color:#8A95A5;line-height:1.5;margin-bottom:12px;">{recommended_fix_text}...</div>
                <div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.1em;">Blast Radius</div>
                <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;">{services_html}</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px;">
                    <div style="background:#141920;border-radius:6px;padding:8px;font-family:IBM Plex Mono,monospace;font-size:10px;">
                        <div style="color:#4A5568;margin-bottom:3px;">ANOMALY SCORE</div>
                        <div style="color:{anomaly_color};font-size:14px;font-weight:500;">{anomaly_score}</div>
                        <div style="color:#4A5568;font-size:9px;">{anomaly_label}</div>
                    </div>
                    <div style="background:#141920;border-radius:6px;padding:8px;font-family:IBM Plex Mono,monospace;font-size:10px;">
                        <div style="color:#4A5568;margin-bottom:3px;">RAG CONTEXT</div>
                        <div style="color:#007AFF;font-size:14px;font-weight:500;">{similar_count}</div>
                        <div style="color:#4A5568;font-size:9px;">similar past incidents</div>
                    </div>
                </div>
                <div style="padding-top:10px;border-top:1px solid #1C2333;font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;">
                    MODEL · {model_name} · CONFIDENCE · {confidence}%
                </div>
            </div>"""

            st.markdown(latest_html, unsafe_allow_html=True)

            if len(incidents) >= 2:
                st.markdown('<div class="sec-title" style="margin-top:1rem;">Severity Breakdown</div>', unsafe_allow_html=True)
                sev_map = {}
                for i in incidents:
                    s = i.get("analysis", {}).get("severity", "MEDIUM").upper()
                    sev_map[s] = sev_map.get(s, 0) + 1
                st.bar_chart(sev_map, height=130, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# INCIDENTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Incidents":
    col_t, col_b = st.columns([3, 1])
    with col_t:
        st.markdown('<h1 style="font-size:24px;font-weight:600;color:#E8EDF5;margin:0;">Incident Log</h1>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;margin-top:4px;">{len(incidents)} incidents recorded</div>', unsafe_allow_html=True)
    with col_b:
        if st.button("+ New Test Incident", use_container_width=True):
            with st.spinner("Running pipeline..."):
                r = trigger_test()
            if r:
                st.success("Created")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if not incidents:
        st.markdown('<div class="oc-card" style="text-align:center;padding:3rem;"><div style="font-size:2rem;">🗂️</div><div style="font-size:14px;color:#8A95A5;margin-top:0.5rem;">No incidents yet</div></div>', unsafe_allow_html=True)
    else:
        for inc in reversed(incidents):
            analysis = inc.get("analysis", {})
            cascade = inc.get("cascade", {})
            anomaly = inc.get("anomaly", {})
            rag_ctx = inc.get("rag_context", {})
            sev = analysis.get("severity", "MEDIUM").upper()
            source = inc.get("source", "manual")
            src_label = "🟠 REAL AWS" if source == "REAL AWS" else "🔵 TEST"
            is_anomaly = anomaly.get("is_anomaly", False)
            anomaly_str = f"⚠ YES (score: {anomaly.get('anomaly_score', 0)})" if is_anomaly else f"✓ NO (score: {anomaly.get('anomaly_score', 0)})"
            inc_id = inc.get('id', '—')

            with st.expander(f"{inc_id[:35]}...  ·  {sev}  ·  {src_label}  ·  {fmt_time(inc.get('timestamp',''))}"):

                tab1, tab2, tab3, tab4 = st.tabs(["📋 Analysis", "🔍 Anomaly & RAG", "📝 Post-Mortem", "📊 Metrics"])

                with tab1:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Root Cause**")
                        st.markdown(f'<div style="font-size:13px;color:#C8D0DC;line-height:1.6;background:#141920;padding:10px;border-radius:6px;">{analysis.get("root_cause","—")}</div>', unsafe_allow_html=True)
                        st.markdown("**Recommended Fix**")
                        st.markdown(f'<div style="font-size:13px;color:#8A95A5;line-height:1.6;background:#141920;padding:10px;border-radius:6px;">{analysis.get("recommended_fix","—")}</div>', unsafe_allow_html=True)
                        st.markdown("**Remediation Steps**")
                        for step in analysis.get("remediation_steps", []):
                            clean_step = step.replace("**", "").replace("*", "")
                            st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:12px;color:#7DD3FC;padding:3px 0;line-height:1.6;">→ {clean_step}</div>', unsafe_allow_html=True)
                    with c2:
                        st.markdown("**Blast Radius**")
                        blast_level = cascade.get("blast_radius_level","unknown").upper()
                        blast_color = {"CRITICAL":"#FF3B30","HIGH":"#FF9500","MEDIUM":"#007AFF","LOW":"#34C759"}.get(blast_level,"#4A5568")
                        st.markdown(f'<div style="font-size:20px;font-weight:600;color:{blast_color};margin-bottom:8px;">{blast_level}</div>', unsafe_allow_html=True)
                        services_tags = "".join(f'<span class="tag">{s}</span> ' for s in cascade.get("all_affected_services",[]))
                        st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:6px;">{services_tags}</div>', unsafe_allow_html=True)
                        st.markdown("**Confidence & Model**")
                        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;">MODEL: {analysis.get("model","—").upper()}<br>CONFIDENCE: {int(analysis.get("confidence",0)*100)}%</div>', unsafe_allow_html=True)

                with tab2:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Isolation Forest — Anomaly Detection**")
                        anomaly_cls = "anomaly-positive" if is_anomaly else "anomaly-negative"
                        st.markdown(f"""
                        <div class="{anomaly_cls}" style="margin-bottom:10px;">
                            {'⚠ ANOMALY DETECTED' if is_anomaly else '✓ NO ANOMALY'}
                        </div>""", unsafe_allow_html=True)
                        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;">SCORE: <span style="color:#C8D0DC;">{anomaly.get("anomaly_score","—")}</span><br>METHOD: <span style="color:#C8D0DC;">{anomaly.get("detection_method","isolation_forest")}</span></div>', unsafe_allow_html=True)

                        breaches = anomaly.get("threshold_breaches", [])
                        if breaches:
                            st.markdown("**Threshold Breaches**")
                            for b in breaches:
                                st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#FF9500;">⚠ {b}</div>', unsafe_allow_html=True)

                    with c2:
                        st.markdown("**RAG — Similar Past Incidents**")
                        similar_incidents = rag_ctx.get("similar_incidents", [])
                        kb_size = rag_ctx.get("knowledge_base_size", 0)
                        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;margin-bottom:8px;">KB SIZE: {kb_size} incidents | FOUND: {rag_ctx.get("similar_count",0)}</div>', unsafe_allow_html=True)

                        if similar_incidents:
                            for sim in similar_incidents:
                                score = sim.get("similarity_score", 0)
                                root = sim.get("root_cause", "—")[:80]
                                st.markdown(f"""
                                <div class="rag-item">
                                    <div class="rag-score">SIMILARITY: {score:.3f}</div>
                                    <div>{root}...</div>
                                </div>""", unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;">No similar incidents found in knowledge base yet.<br>Generate more incidents to build the RAG memory.</div>', unsafe_allow_html=True)

                with tab3:
                    st.markdown("**Auto-Generated Post-Mortem Report**")
                    postmortem = inc.get("postmortem", "")
                    if postmortem:
                        st.markdown(f'<div class="postmortem-box">{postmortem}</div>', unsafe_allow_html=True)
                        st.markdown("<br>")

                        # PDF download
                        pdf_bytes = get_postmortem_pdf(inc_id)
                        if pdf_bytes:
                            st.download_button(
                                label="⬇ Download Post-Mortem PDF",
                                data=pdf_bytes,
                                file_name=f"postmortem_{inc_id[:20]}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                key=f"pdf_{inc_id}"
                            )
                        else:
                            st.warning("PDF generation failed — check backend logs")
                    else:
                        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:12px;color:#4A5568;">Post-mortem not available for this incident.<br>Re-trigger the incident to generate one.</div>', unsafe_allow_html=True)

                with tab4:
                    st.markdown("**Metrics at Incident Time**")
                    metrics = inc.get("metrics", {})
                    metric_cols = st.columns(3)
                    metric_items = [(k, v) for k, v in metrics.items() if k not in ("timestamp", "function_name")]
                    for idx, (k, v) in enumerate(metric_items):
                        with metric_cols[idx % 3]:
                            st.metric(k.replace("_", " ").title(), v)


# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Analytics":
    st.markdown('<h1 style="font-size:24px;font-weight:600;color:#E8EDF5;margin:0;">Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;margin-top:4px;margin-bottom:1.5rem;">Patterns across all incidents</div>', unsafe_allow_html=True)

    if not incidents:
        st.markdown('<div class="oc-card" style="text-align:center;padding:3rem;"><div style="font-size:2rem;">📊</div><div style="font-size:14px;color:#8A95A5;margin-top:0.5rem;">Trigger at least 3 incidents to see analytics</div></div>', unsafe_allow_html=True)
    else:
        sev_counts = {}
        service_counts = {}
        source_counts = {"REAL AWS": 0, "TEST": 0}
        blast_counts = {}
        anomaly_scores = []

        for i in incidents:
            sev = i.get("analysis", {}).get("severity", "MEDIUM").upper()
            sev_counts[sev] = sev_counts.get(sev, 0) + 1
            for svc in i.get("cascade", {}).get("all_affected_services", []):
                service_counts[svc] = service_counts.get(svc, 0) + 1
            src = i.get("source", "manual")
            source_counts["REAL AWS" if src == "REAL AWS" else "TEST"] += 1
            bl = i.get("cascade", {}).get("blast_radius_level", "unknown").upper()
            blast_counts[bl] = blast_counts.get(bl, 0) + 1
            score = i.get("anomaly", {}).get("anomaly_score", 0)
            if score:
                anomaly_scores.append(score)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="sec-title">Incidents by Severity</div>', unsafe_allow_html=True)
            st.bar_chart(sev_counts, height=200)
            st.markdown('<div class="sec-title" style="margin-top:1rem;">Incident Source</div>', unsafe_allow_html=True)
            st.bar_chart(source_counts, height=200)
        with c2:
            st.markdown('<div class="sec-title">Most Affected Services</div>', unsafe_allow_html=True)
            st.bar_chart(service_counts, height=200)
            st.markdown('<div class="sec-title" style="margin-top:1rem;">Blast Radius Levels</div>', unsafe_allow_html=True)
            st.bar_chart(blast_counts, height=200)

        st.markdown('<div class="sec-title">Summary Stats</div>', unsafe_allow_html=True)
        s1, s2, s3, s4 = st.columns(4)
        most_sev = max(sev_counts, key=sev_counts.get) if sev_counts else "—"
        most_svc = max(service_counts, key=service_counts.get) if service_counts else "—"
        avg_score = round(sum(anomaly_scores)/len(anomaly_scores), 3) if anomaly_scores else 0

        s1.markdown(f'<div class="metric-card"><div class="lbl">Most Common Severity</div><div class="val" style="font-size:18px;">{most_sev}</div></div>', unsafe_allow_html=True)
        s2.markdown(f'<div class="metric-card"><div class="lbl">Most Affected Service</div><div class="val" style="font-size:18px;">{most_svc.upper()}</div></div>', unsafe_allow_html=True)
        s3.markdown(f'<div class="metric-card"><div class="lbl">Avg Anomaly Score</div><div class="val" style="font-size:18px;">{avg_score}</div></div>', unsafe_allow_html=True)
        s4.markdown(f'<div class="metric-card"><div class="lbl">Real AWS Incidents</div><div class="val" style="font-size:18px;">{source_counts["REAL AWS"]}</div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# AWS TRIGGER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "AWS Trigger":
    st.markdown('<h1 style="font-size:24px;font-weight:600;color:#E8EDF5;margin:0;">AWS Live Trigger</h1>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;margin-top:4px;margin-bottom:1.5rem;">Trigger real Lambda failures → CloudWatch logs → full pipeline → postmortem PDF</div>', unsafe_allow_html=True)

    st.markdown('<div class="oc-card" style="border-color:rgba(255,153,0,0.25);margin-bottom:1.5rem;"><div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#FF9900;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">Live AWS Integration</div><div style="font-size:13px;color:#8A95A5;line-height:1.6;">Triggers <code>opsoracle-demo-failure</code> Lambda in ap-south-1. OpsOracle reads real CloudWatch logs, runs Isolation Forest, RAG search, Groq LLM analysis, and generates a downloadable post-mortem PDF.</div></div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown('<div class="oc-card" style="border-color:rgba(255,59,48,0.25);text-align:center;"><div style="font-size:1.5rem;margin-bottom:8px;">⚡</div><div style="font-size:13px;font-weight:500;color:#E8EDF5;margin-bottom:4px;">Lambda Timeout</div><div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;">Simulates execution timeout</div></div>', unsafe_allow_html=True)
        if st.button("Trigger Timeout", use_container_width=True, key="aws_t"):
            with st.spinner("Invoking Lambda... reading CloudWatch... running pipeline..."):
                r = trigger_aws("timeout")
            if r and r.get("status") == "success":
                st.success(f"{r['incident_id']}")
                st.rerun()
            else:
                st.error("Failed — ensure Lambda is deployed in ap-south-1")

    with col_b:
        st.markdown('<div class="oc-card" style="border-color:rgba(255,149,0,0.25);text-align:center;"><div style="font-size:1.5rem;margin-bottom:8px;">💾</div><div style="font-size:13px;font-weight:500;color:#E8EDF5;margin-bottom:4px;">Memory Error</div><div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;">Simulates OOM crash</div></div>', unsafe_allow_html=True)
        if st.button("Trigger Memory Error", use_container_width=True, key="aws_m"):
            with st.spinner("Invoking Lambda... reading CloudWatch... running pipeline..."):
                r = trigger_aws("memory")
            if r and r.get("status") == "success":
                st.success(f"{r['incident_id']}")
                st.rerun()
            else:
                st.error("Failed — ensure Lambda is deployed in ap-south-1")

    with col_c:
        st.markdown('<div class="oc-card" style="border-color:rgba(0,122,255,0.25);text-align:center;"><div style="font-size:1.5rem;margin-bottom:8px;">🔌</div><div style="font-size:13px;font-weight:500;color:#E8EDF5;margin-bottom:4px;">DB Connection</div><div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;">Simulates RDS pool exhaustion</div></div>', unsafe_allow_html=True)
        if st.button("Trigger DB Error", use_container_width=True, key="aws_d"):
            with st.spinner("Invoking Lambda... reading CloudWatch... running pipeline..."):
                r = trigger_aws("connection")
            if r and r.get("status") == "success":
                st.success(f"{r['incident_id']}")
                st.rerun()
            else:
                st.error("Failed — ensure Lambda is deployed in ap-south-1")

    
    st.markdown('<div class="sec-title">Recent AWS Incidents</div>', unsafe_allow_html=True)
    aws_incidents = [i for i in incidents if i.get("source") == "REAL AWS"]

    if not aws_incidents:
        st.markdown('<div class="oc-card" style="text-align:center;padding:2rem;"><div style="font-size:2rem;">☁️</div><div style="font-size:14px;color:#8A95A5;margin-top:0.5rem;">No real AWS incidents yet</div></div>', unsafe_allow_html=True)
    else:
        for inc in reversed(aws_incidents):
            analysis = inc.get("analysis", {})
            sev = analysis.get("severity", "HIGH").upper()
            inc_id = inc.get("id", "—")
            postmortem_available = bool(inc.get("postmortem"))

            st.markdown(f"""
            <div class="inc-card aws-src">
                <div class="inc-hdr">
                    <span class="inc-id">{inc_id[:30]}...</span>
                    <div style="display:flex;gap:5px;">
                        <span class="badge badge-aws">AWS</span>
                        {sev_badge(sev)}
                        {'<span class="badge badge-low">📝 POST-MORTEM</span>' if postmortem_available else ''}
                    </div>
                </div>
                <div class="inc-cause">{analysis.get('root_cause','—')[:150]}...</div>
                <div class="inc-footer">
                    <span class="tag">{inc.get('failure_type','unknown')}</span>
                    <span class="tag">{inc.get('function_name','—')}</span>
                    <span class="inc-time">{fmt_time(inc.get('timestamp',''))}</span>
                </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Settings":
    st.markdown('<h1 style="font-size:24px;font-weight:600;color:#E8EDF5;margin:0;">Settings</h1>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;margin-top:4px;margin-bottom:1.5rem;">System configuration and status</div>', unsafe_allow_html=True)

    rows = [
        ("Backend URL", BACKEND_URL),
        ("LLM Provider", "Groq API (free tier)"),
        ("LLM Model", "llama-3.3-70b-versatile"),
        ("Anomaly Detection", "Isolation Forest — scikit-learn"),
        ("Anomaly Trees", "100 estimators, contamination=0.1"),
        ("Embeddings", "all-MiniLM-L6-v2 (384 dimensions)"),
        ("Vector Search", "Cosine similarity (Pinecone-ready)"),
        ("RAG Framework", "LangChain + Sentence Transformers"),
        ("AWS Region", "ap-south-1 (Mumbai)"),
        ("Lambda Function", "opsoracle-demo-failure"),
        ("PDF Generator", "ReportLab"),
        ("Version", "OpsOracle v1.2.0"),
    ]

    st.markdown('<div class="oc-card">', unsafe_allow_html=True)
    for label, value in rows:
        st.markdown(f'<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #1C2333;"><span style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;">{label}</span><span style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#C8D0DC;">{value}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

  
    st.markdown('<div class="oc-card"><div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">Built by</div><div style="font-size:14px;font-weight:500;color:#E8EDF5;">Gaurav Sindhi</div><div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;margin-top:4px;">B.Tech AI/ML · R.C. Patel Institute of Technology · 2026</div></div>', unsafe_allow_html=True)