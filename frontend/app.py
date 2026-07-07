"""OpsOracle — Autonomous Incident Response Dashboard"""

import streamlit as st
import requests
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OpsOracle",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "http://localhost:8000"

# ── Design system ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@300;400;500;600&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080B10 !important;
    color: #C8D0DC !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: #0C1017 !important;
    border-right: 1px solid #1C2333 !important;
}

[data-testid="stSidebar"] * { color: #C8D0DC !important; }

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1400px !important; }

/* ── Typography ── */
h1, h2, h3, h4 { font-family: 'Inter', sans-serif !important; letter-spacing: -0.02em; }

/* ── Cards ── */
.oc-card {
    background: #0C1017;
    border: 1px solid #1C2333;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}

.oc-card-glow {
    background: #0C1017;
    border: 1px solid #1C2333;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 0 0 1px #1C2333, 0 4px 24px rgba(255,59,48,0.06);
}

/* ── Metric cards ── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 1.5rem;
}

.metric-card {
    background: #0C1017;
    border: 1px solid #1C2333;
    border-radius: 8px;
    padding: 1.1rem 1.3rem;
}

.metric-card .label {
    font-size: 11px;
    font-family: 'IBM Plex Mono', monospace;
    color: #4A5568;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
}

.metric-card .value {
    font-size: 28px;
    font-weight: 600;
    letter-spacing: -0.03em;
    line-height: 1;
    color: #E8EDF5;
}

.metric-card .sub {
    font-size: 11px;
    color: #4A5568;
    margin-top: 6px;
    font-family: 'IBM Plex Mono', monospace;
}

.metric-card.danger  { border-color: rgba(255,59,48,0.35); }
.metric-card.warning { border-color: rgba(255,165,0,0.35); }
.metric-card.success { border-color: rgba(52,199,89,0.35); }
.metric-card.info    { border-color: rgba(0,122,255,0.35); }

.metric-card.danger  .value { color: #FF3B30; }
.metric-card.warning .value { color: #FF9500; }
.metric-card.success .value { color: #34C759; }
.metric-card.info    .value { color: #007AFF; }

/* ── Status badges ── */
.badge {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    padding: 3px 8px;
    border-radius: 4px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.badge-critical { background: rgba(255,59,48,0.15);  color: #FF3B30; border: 1px solid rgba(255,59,48,0.3); }
.badge-high     { background: rgba(255,149,0,0.15);  color: #FF9500; border: 1px solid rgba(255,149,0,0.3); }
.badge-medium   { background: rgba(0,122,255,0.15);  color: #007AFF; border: 1px solid rgba(0,122,255,0.3); }
.badge-low      { background: rgba(52,199,89,0.15);  color: #34C759; border: 1px solid rgba(52,199,89,0.3); }
.badge-aws      { background: rgba(255,153,0,0.12);  color: #FF9900; border: 1px solid rgba(255,153,0,0.3); }

/* ── Incident cards ── */
.incident-card {
    background: #0C1017;
    border: 1px solid #1C2333;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 10px;
    transition: border-color 0.15s;
}

.incident-card:hover { border-color: #2D3748; }

.incident-card.aws-source {
    border-left: 3px solid #FF9900;
}

.incident-card.manual-source {
    border-left: 3px solid #007AFF;
}

.incident-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.incident-id {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: #E8EDF5;
    font-weight: 500;
}

.incident-time {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #4A5568;
}

.incident-cause {
    font-size: 13px;
    color: #8A95A5;
    line-height: 1.5;
    margin-bottom: 10px;
}

.incident-footer {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
}

.tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #4A5568;
    background: #141920;
    border: 1px solid #1C2333;
    border-radius: 4px;
    padding: 2px 7px;
}

/* ── Live indicator ── */
.live-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #34C759;
    margin-right: 6px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

/* ── Section headers ── */
.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
    padding-bottom: 8px;
    border-bottom: 1px solid #1C2333;
}

.section-title {
    font-size: 12px;
    font-family: 'IBM Plex Mono', monospace;
    color: #4A5568;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── Buttons ── */
.stButton > button {
    background: #141920 !important;
    color: #C8D0DC !important;
    border: 1px solid #1C2333 !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important;
    padding: 0.4rem 1rem !important;
    transition: all 0.15s !important;
}

.stButton > button:hover {
    background: #1C2333 !important;
    border-color: #2D3748 !important;
    color: #E8EDF5 !important;
}

/* AWS trigger buttons */
.aws-btn > button {
    border-color: rgba(255,153,0,0.35) !important;
    color: #FF9900 !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0C1017 !important;
    border: 1px solid #1C2333 !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
}

[data-testid="stExpander"] summary {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important;
    color: #C8D0DC !important;
}

/* ── Divider ── */
hr { border-color: #1C2333 !important; }

/* ── Code blocks ── */
code, pre {
    font-family: 'IBM Plex Mono', monospace !important;
    background: #141920 !important;
    color: #7DD3FC !important;
    border-radius: 4px !important;
    font-size: 12px !important;
}

/* ── Selectbox / radio ── */
[data-testid="stRadio"] label { font-size: 13px !important; }

/* ── Charts ── */
[data-testid="stVegaLiteChart"] { border-radius: 8px; overflow: hidden; }

/* ── Sidebar nav ── */
.sidebar-logo {
    font-size: 18px;
    font-weight: 600;
    letter-spacing: -0.03em;
    color: #E8EDF5 !important;
    margin-bottom: 4px;
}

.sidebar-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #4A5568;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 1.5rem;
}

/* ── Timeline ── */
.timeline-item {
    display: flex;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px solid #1C2333;
    align-items: flex-start;
}

.timeline-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-top: 4px;
    flex-shrink: 0;
}

.timeline-content { flex: 1; }

.timeline-title {
    font-size: 13px;
    color: #C8D0DC;
    font-weight: 500;
    margin-bottom: 2px;
}

.timeline-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #4A5568;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #4A5568;
}

.empty-state .icon { font-size: 2rem; margin-bottom: 0.75rem; }
.empty-state .title { font-size: 14px; color: #8A95A5; margin-bottom: 6px; }
.empty-state .desc { font-size: 12px; font-family: 'IBM Plex Mono', monospace; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def check_backend():
    try:
        r = requests.get(f"{BACKEND_URL}/", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def get_incidents():
    try:
        r = requests.get(f"{BACKEND_URL}/api/incidents/", timeout=5)
        return r.json().get("incidents", []) if r.status_code == 200 else []
    except Exception:
        return []


def trigger_test(failure_type="timeout"):
    payload = {
        "logs": {
            "summary": f"Lambda {failure_type} error detected",
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
        r = requests.post(f"{BACKEND_URL}/api/incidents/analyze", json=payload, timeout=30)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def trigger_aws(failure_type="timeout"):
    try:
        r = requests.post(
            f"{BACKEND_URL}/api/incidents/trigger-aws-incident",
            params={"failure_type": failure_type},
            timeout=60
        )
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def sev_badge(sev):
    sev = (sev or "MEDIUM").upper()
    cls = {"CRITICAL": "critical", "HIGH": "high", "MEDIUM": "medium", "LOW": "low"}.get(sev, "medium")
    return f'<span class="badge badge-{cls}">{sev}</span>'


def fmt_time(ts):
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%d %b %H:%M:%S")
    except Exception:
        return ts or "—"


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="sidebar-logo">OpsOracle</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Incident Response Platform</div>', unsafe_allow_html=True)

    backend_ok = check_backend()
    if backend_ok:
        st.markdown('<span class="live-dot"></span><span style="font-size:12px;color:#34C759;">Backend online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="font-size:12px;color:#FF3B30;">⬤ Backend offline</span>', unsafe_allow_html=True)

    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;margin-top:4px;margin-bottom:1.5rem;">LLM · Llama 3.3 70B (Groq)</div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["Dashboard", "Incidents", "Analytics", "AWS Trigger", "Settings"],
        label_visibility="collapsed"
    )

    incidents = get_incidents() if backend_ok else []

    st.markdown("---")
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;">TOTAL INCIDENTS</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:22px;font-weight:600;color:#E8EDF5;">{len(incidents)}</div>', unsafe_allow_html=True)

    critical_count = sum(1 for i in incidents if i.get("analysis", {}).get("severity", "").upper() == "CRITICAL")
    aws_count = sum(1 for i in incidents if i.get("source") == "REAL AWS")

    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#FF3B30;margin-top:8px;">CRITICAL: {critical_count}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#FF9900;margin-top:4px;">FROM AWS: {aws_count}</div>', unsafe_allow_html=True)


if not backend_ok:
    st.markdown("""
    <div class="oc-card" style="border-color:rgba(255,59,48,0.3);text-align:center;padding:3rem;">
        <div style="font-size:2rem;margin-bottom:1rem;">⚠️</div>
        <div style="font-size:15px;color:#FF3B30;margin-bottom:8px;">Backend Offline</div>
        <div style="font-family:IBM Plex Mono,monospace;font-size:12px;color:#4A5568;">
            Run: python -m backend.main
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

if page == "Dashboard":

    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown('<h1 style="font-size:24px;font-weight:600;color:#E8EDF5;margin:0;">Command Centre</h1>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;margin-top:4px;">Real-time incident detection and autonomous response</div>', unsafe_allow_html=True)
    with col_h2:
        if st.button("+ Trigger Test Incident", use_container_width=True):
            with st.spinner("Running pipeline..."):
                r = trigger_test()
            if r:
                st.success(f"Created {r['incident_id']}")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Metrics row
    total = len(incidents)
    critical = sum(1 for i in incidents if i.get("analysis", {}).get("severity", "").upper() == "CRITICAL")
    high = sum(1 for i in incidents if i.get("analysis", {}).get("severity", "").upper() == "HIGH")
    aws_real = sum(1 for i in incidents if i.get("source") == "REAL AWS")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card info">
            <div class="label">Total Incidents</div>
            <div class="value">{total}</div>
            <div class="sub">all time</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card danger">
            <div class="label">Critical</div>
            <div class="value">{critical}</div>
            <div class="sub">blast radius</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card warning">
            <div class="label">High Severity</div>
            <div class="value">{high}</div>
            <div class="sub">needs attention</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card success">
            <div class="label">From Real AWS</div>
            <div class="value">{aws_real}</div>
            <div class="sub">live cloudwatch</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not incidents:
        st.markdown("""
        <div class="oc-card" style="text-align:center;padding:3rem;">
            <div class="empty-state">
                <div class="icon">📡</div>
                <div class="title">No incidents detected</div>
                <div class="desc">Click "Trigger Test Incident" to run the full pipeline</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown('<div class="section-title">Recent Incidents</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            for inc in list(reversed(incidents))[:5]:
                analysis = inc.get("analysis", {})
                cascade = inc.get("cascade", {})
                sev = analysis.get("severity", "MEDIUM").upper()
                source = inc.get("source", "manual")
                src_class = "aws-source" if source == "REAL AWS" else "manual-source"
                src_badge = '<span class="badge badge-aws">AWS</span>' if source == "REAL AWS" else '<span class="badge badge-medium">TEST</span>'
                affected = cascade.get("total_affected", 0)
                blast = cascade.get("blast_radius_level", "unknown").upper()
                root = analysis.get("root_cause", "No analysis available")
                root_short = root[:120] + "..." if len(root) > 120 else root

                st.markdown(f"""
                <div class="incident-card {src_class}">
                    <div class="incident-header">
                        <span class="incident-id">{inc.get('id', '—')}</span>
                        <div style="display:flex;gap:6px;align-items:center;">
                            {src_badge}
                            {sev_badge(sev)}
                        </div>
                    </div>
                    <div class="incident-cause">{root_short}</div>
                    <div class="incident-footer">
                        <span class="tag">{blast} blast</span>
                        <span class="tag">{affected} services</span>
                        <span class="incident-time">{fmt_time(inc.get('timestamp', ''))}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="section-title">Latest Analysis</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            latest = incidents[-1]
            analysis = latest.get("analysis", {})
            cascade = latest.get("cascade", {})

            st.markdown(f"""
            <div class="oc-card-glow">
                <div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.1em;">Root Cause</div>
                <div style="font-size:13px;color:#C8D0DC;line-height:1.6;margin-bottom:1rem;">{analysis.get('root_cause','—')}</div>

                <div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.1em;">Recommended Fix</div>
                <div style="font-size:12px;color:#8A95A5;line-height:1.5;margin-bottom:1rem;">{str(analysis.get('recommended_fix','—'))[:200]}...</div>

                <div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.1em;">Blast Radius</div>
                <div style="display:flex;flex-wrap:wrap;gap:6px;">
                    {"".join(f'<span class="tag">{s}</span>' for s in cascade.get("all_affected_services", []))}
                </div>

                <div style="margin-top:1rem;padding-top:1rem;border-top:1px solid #1C2333;font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;">
                    MODEL · {analysis.get('model','—').upper()}
                </div>
            </div>""", unsafe_allow_html=True)

            # Severity breakdown mini chart
            if len(incidents) >= 2:
                st.markdown('<div class="section-title" style="margin-top:1rem;">Severity Breakdown</div>', unsafe_allow_html=True)
                sev_map = {}
                for i in incidents:
                    s = i.get("analysis", {}).get("severity", "MEDIUM").upper()
                    sev_map[s] = sev_map.get(s, 0) + 1
                st.bar_chart(sev_map, height=140, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: INCIDENTS
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
                st.success(f"Created")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if not incidents:
        st.markdown("""
        <div class="oc-card" style="text-align:center;padding:3rem;">
            <div class="empty-state">
                <div class="icon">🗂️</div>
                <div class="title">No incidents yet</div>
                <div class="desc">Trigger a test incident or connect real AWS</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        for inc in reversed(incidents):
            analysis = inc.get("analysis", {})
            cascade = inc.get("cascade", {})
            sev = analysis.get("severity", "MEDIUM").upper()
            source = inc.get("source", "manual")
            src_label = "🟠 REAL AWS" if source == "REAL AWS" else "🔵 TEST"
            affected_svcs = cascade.get("all_affected_services", [])

            with st.expander(f"{inc.get('id','—')}  ·  {sev}  ·  {src_label}  ·  {fmt_time(inc.get('timestamp',''))}"):
                c1, c2 = st.columns(2)

                with c1:
                    st.markdown("**Root Cause**")
                    st.markdown(f'<div style="font-size:13px;color:#C8D0DC;line-height:1.6;">{analysis.get("root_cause","—")}</div>', unsafe_allow_html=True)

                    st.markdown("<br>**Recommended Fix**")
                    st.markdown(f'<div style="font-size:13px;color:#8A95A5;line-height:1.6;">{analysis.get("recommended_fix","—")}</div>', unsafe_allow_html=True)

                    st.markdown("<br>**Remediation Steps**")
                    for step in analysis.get("remediation_steps", []):
                        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:12px;color:#7DD3FC;padding:3px 0;">→ {step}</div>', unsafe_allow_html=True)

                with c2:
                    st.markdown("**Blast Radius**")
                    blast_level = cascade.get("blast_radius_level", "unknown").upper()
                    blast_color = {"CRITICAL": "#FF3B30", "HIGH": "#FF9500", "MEDIUM": "#007AFF", "LOW": "#34C759"}.get(blast_level, "#4A5568")
                    st.markdown(f'<div style="font-size:18px;font-weight:600;color:{blast_color};margin-bottom:8px;">{blast_level}</div>', unsafe_allow_html=True)
                    st.markdown('<div style="display:flex;flex-wrap:wrap;gap:6px;">' + "".join(f'<span class="tag">{s}</span>' for s in affected_svcs) + '</div>', unsafe_allow_html=True)

                    st.markdown("<br>**Metrics at Incident Time**")
                    metrics = inc.get("metrics", {})
                    for k, v in metrics.items():
                        if k not in ("timestamp", "function_name"):
                            st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;padding:2px 0;">{k}: <span style="color:#C8D0DC;">{v}</span></div>', unsafe_allow_html=True)

                    st.markdown("<br>")
                    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;">MODEL · {analysis.get("model","—").upper()}<br>CONFIDENCE · {analysis.get("confidence",0):.0%}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Analytics":

    st.markdown('<h1 style="font-size:24px;font-weight:600;color:#E8EDF5;margin:0;">Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;margin-top:4px;margin-bottom:1.5rem;">Patterns across all incidents</div>', unsafe_allow_html=True)

    if not incidents:
        st.markdown("""
        <div class="oc-card" style="text-align:center;padding:3rem;">
            <div class="empty-state">
                <div class="icon">📊</div>
                <div class="title">No data yet</div>
                <div class="desc">Trigger at least 3 incidents to see analytics</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        sev_counts = {}
        service_counts = {}
        source_counts = {"REAL AWS": 0, "TEST": 0}
        blast_counts = {}

        for i in incidents:
            sev = i.get("analysis", {}).get("severity", "MEDIUM").upper()
            sev_counts[sev] = sev_counts.get(sev, 0) + 1

            for svc in i.get("cascade", {}).get("all_affected_services", []):
                service_counts[svc] = service_counts.get(svc, 0) + 1

            src = i.get("source", "manual")
            if src == "REAL AWS":
                source_counts["REAL AWS"] += 1
            else:
                source_counts["TEST"] += 1

            bl = i.get("cascade", {}).get("blast_radius_level", "unknown").upper()
            blast_counts[bl] = blast_counts.get(bl, 0) + 1

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-title">Incidents by Severity</div>', unsafe_allow_html=True)
            st.bar_chart(sev_counts, height=200, use_container_width=True)

            st.markdown('<br><div class="section-title">Incident Source</div>', unsafe_allow_html=True)
            st.bar_chart(source_counts, height=200, use_container_width=True)

        with col2:
            st.markdown('<div class="section-title">Most Affected Services</div>', unsafe_allow_html=True)
            st.bar_chart(service_counts, height=200, use_container_width=True)

            st.markdown('<br><div class="section-title">Blast Radius Levels</div>', unsafe_allow_html=True)
            st.bar_chart(blast_counts, height=200, use_container_width=True)

        # Summary stats
        st.markdown("<br>")
        st.markdown('<div class="section-title">Summary</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            most_sev = max(sev_counts, key=sev_counts.get) if sev_counts else "—"
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">Most Common Severity</div>
                <div class="value" style="font-size:18px;">{most_sev}</div>
            </div>""", unsafe_allow_html=True)
        with s2:
            most_svc = max(service_counts, key=service_counts.get) if service_counts else "—"
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">Most Affected Service</div>
                <div class="value" style="font-size:18px;">{most_svc.upper()}</div>
            </div>""", unsafe_allow_html=True)
        with s3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">Real AWS Incidents</div>
                <div class="value" style="font-size:18px;">{source_counts['REAL AWS']}</div>
            </div>""", unsafe_allow_html=True)
        with s4:
            most_blast = max(blast_counts, key=blast_counts.get) if blast_counts else "—"
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">Most Common Blast Level</div>
                <div class="value" style="font-size:18px;">{most_blast}</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AWS TRIGGER
# ══════════════════════════════════════════════════════════════════════════════

elif page == "AWS Trigger":

    st.markdown('<h1 style="font-size:24px;font-weight:600;color:#E8EDF5;margin:0;">AWS Live Trigger</h1>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;margin-top:4px;margin-bottom:1.5rem;">Trigger real Lambda failures → read real CloudWatch logs → full pipeline</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="oc-card" style="border-color:rgba(255,153,0,0.25);margin-bottom:1.5rem;">
        <div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#FF9900;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">Live AWS Integration</div>
        <div style="font-size:13px;color:#8A95A5;line-height:1.6;">
            These buttons trigger the <code>opsoracle-demo-failure</code> Lambda function in your AWS account (ap-south-1).
            OpsOracle reads the real CloudWatch logs, fetches real metrics, and runs the full incident response pipeline.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("""
        <div class="oc-card" style="border-color:rgba(255,59,48,0.25);text-align:center;margin-bottom:10px;">
            <div style="font-size:1.5rem;margin-bottom:8px;">⚡</div>
            <div style="font-size:13px;font-weight:500;color:#E8EDF5;margin-bottom:4px;">Lambda Timeout</div>
            <div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;">Simulates execution timeout</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Trigger Timeout", use_container_width=True, key="aws_timeout"):
            with st.spinner("Invoking Lambda... reading CloudWatch..."):
                r = trigger_aws("timeout")
            if r and r.get("status") == "success":
                st.success(f"Incident created: {r['incident_id']}")
                st.rerun()
            else:
                st.error("Failed — check Lambda is deployed in ap-south-1")

    with col_b:
        st.markdown("""
        <div class="oc-card" style="border-color:rgba(255,149,0,0.25);text-align:center;margin-bottom:10px;">
            <div style="font-size:1.5rem;margin-bottom:8px;">💾</div>
            <div style="font-size:13px;font-weight:500;color:#E8EDF5;margin-bottom:4px;">Memory Error</div>
            <div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;">Simulates OOM crash</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Trigger Memory Error", use_container_width=True, key="aws_memory"):
            with st.spinner("Invoking Lambda... reading CloudWatch..."):
                r = trigger_aws("memory")
            if r and r.get("status") == "success":
                st.success(f"Incident created: {r['incident_id']}")
                st.rerun()
            else:
                st.error("Failed — check Lambda is deployed in ap-south-1")

    with col_c:
        st.markdown("""
        <div class="oc-card" style="border-color:rgba(0,122,255,0.25);text-align:center;margin-bottom:10px;">
            <div style="font-size:1.5rem;margin-bottom:8px;">🔌</div>
            <div style="font-size:13px;font-weight:500;color:#E8EDF5;margin-bottom:4px;">DB Connection</div>
            <div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;">Simulates RDS pool exhaustion</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Trigger DB Error", use_container_width=True, key="aws_db"):
            with st.spinner("Invoking Lambda... reading CloudWatch..."):
                r = trigger_aws("connection")
            if r and r.get("status") == "success":
                st.success(f"Incident created: {r['incident_id']}")
                st.rerun()
            else:
                st.error("Failed — check Lambda is deployed in ap-south-1")

    st.markdown("<br>")
    st.markdown('<div class="section-title">Recent AWS Incidents</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    aws_incidents = [i for i in incidents if i.get("source") == "REAL AWS"]

    if not aws_incidents:
        st.markdown("""
        <div class="oc-card" style="text-align:center;padding:2rem;">
            <div class="empty-state">
                <div class="icon">☁️</div>
                <div class="title">No real AWS incidents yet</div>
                <div class="desc">Use the buttons above to trigger your first real AWS incident</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        for inc in reversed(aws_incidents):
            analysis = inc.get("analysis", {})
            sev = analysis.get("severity", "HIGH").upper()
            st.markdown(f"""
            <div class="incident-card aws-source">
                <div class="incident-header">
                    <span class="incident-id">{inc.get('id','—')}</span>
                    <div style="display:flex;gap:6px;">
                        <span class="badge badge-aws">AWS</span>
                        {sev_badge(sev)}
                    </div>
                </div>
                <div class="incident-cause">{analysis.get('root_cause','—')[:150]}...</div>
                <div class="incident-footer">
                    <span class="tag">{inc.get('failure_type','unknown')}</span>
                    <span class="tag">{inc.get('function_name','—')}</span>
                    <span class="incident-time">{fmt_time(inc.get('timestamp',''))}</span>
                </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Settings":

    st.markdown('<h1 style="font-size:24px;font-weight:600;color:#E8EDF5;margin:0;">Settings</h1>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;margin-top:4px;margin-bottom:1.5rem;">System configuration and status</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="oc-card">
        <div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px;">System</div>
    """, unsafe_allow_html=True)

    rows = [
        ("Backend URL", BACKEND_URL),
        ("LLM Provider", "Groq API"),
        ("LLM Model", "Llama 3.3 70B (llama-3.3-70b-versatile)"),
        ("AWS Region", "ap-south-1 (Mumbai)"),
        ("Lambda Function", "opsoracle-demo-failure"),
        ("Embeddings Model", "all-MiniLM-L6-v2"),
        ("Anomaly Detection", "Isolation Forest (scikit-learn)"),
        ("RAG Storage", "In-memory (Pinecone-ready)"),
        ("Version", "OpsOracle v1.1.0"),
    ]

    for label, value in rows:
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #1C2333;">
            <span style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;">{label}</span>
            <span style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#C8D0DC;">{value}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="oc-card">
        <div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4A5568;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">Built by</div>
        <div style="font-size:14px;font-weight:500;color:#E8EDF5;">Gaurav Sindhi</div>
        <div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;margin-top:4px;">B.Tech AI/ML · R.C. Patel Institute of Technology</div>
    </div>
    """, unsafe_allow_html=True)