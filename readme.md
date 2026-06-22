    # 🤖 OpsOracle - AI-Powered Incident Response System

**Powered by Claude API (Anthropic)**

---

## 📋 Overview

OpsOracle is a professional-grade, AI-powered incident response system that detects, analyzes, remediates, and learns from cloud infrastructure incidents using Claude API for intelligent reasoning and analysis.

**Key Features:**
- ✅ Real-time anomaly detection (ML)
- ✅ Multi-service blast radius analysis
- ✅ Claude AI-powered root cause analysis
- ✅ Autonomous remediation (3 permission levels)
- ✅ RAG semantic search over incident history
- ✅ Auto-generated post-mortem reports
- ✅ Beautiful Streamlit dashboard
- ✅ Production-ready FastAPI backend

---

## 🏗️ Architecture

```
OpsOracle/
├── backend/
│   ├── agents/              # LLM & Remediation agents
│   ├── services/            # AWS, RAG, Alert services
│   ├── ml/                  # Anomaly detection
│   ├── routers/             # FastAPI endpoints
│   ├── models/              # Pydantic schemas
│   ├── utils/               # Utilities (PDF, embeddings)
│   ├── main.py              # FastAPI app
│   └── config.py            # Configuration
│
├── frontend/
│   ├── app.py               # Streamlit dashboard
│   └── pages/               # Multi-page app
│
├── ml_models/               # Trained ML models
├── data/                    # Sample data
├── tests/                   # Unit tests
├── .env                     # Environment variables
├── requirements.txt         # Dependencies
└── README.md               # This file
```

---

## 🚀 Quick Start

### Step 1: Setup
```bash
# Clone/download OpsOracle
cd OpsOracle

# Create directories
mkdir -p ml_models data logs tests

# Create ml_models subdirectories
mkdir -p ml_models
```

### Step 2: Install Dependencies
```bash
pip install -r requirements_CLAUDE.txt
```

### Step 3: Configure Environment
```bash
# Copy .env template
cp .env_CLAUDE .env

# Edit .env with your keys:
# - CLAUDE_API_KEY from console.anthropic.com
# - AWS credentials from AWS Console
# - AWS_REGION (default: us-east-1)
```

### Step 4: Validate Configuration
```bash
python backend/config.py
```

Expected output: `✅ Configuration loaded successfully (Claude API enabled)`

### Step 5: Run Backend
```bash
# Terminal 1
python -m backend.main
```

Backend starts on: `http://localhost:8000`

### Step 6: Run Frontend
```bash
# Terminal 2
streamlit run frontend/app.py
```

Frontend opens at: `http://localhost:8501`

---

## 📊 API Endpoints

### Health & Status
- `GET /` — Health check

### Incidents
- `GET /api/incidents` — List incidents
- `GET /api/incidents/{id}` — Get specific incident
- `POST /api/incidents` — Create incident
- `POST /api/incidents/analyze` — Full analysis pipeline

### Metrics
- `GET /api/metrics/all` — Get all metrics
- `GET /api/metrics/{namespace}/{metric_name}` — Get specific metric
- `GET /api/metrics/xray/traces` — Get X-Ray traces

### Remediation
- `POST /api/remediation/execute` — Execute fix
- `GET /api/remediation/history` — Get history
- `GET /api/remediation/cascade/{incident_id}` — Get cascade plan

### Post-Mortem
- `POST /api/postmortem/generate` — Generate postmortem
- `GET /api/postmortem/{id}` — Get postmortem
- `POST /api/postmortem/{id}/export/pdf` — Export as PDF

---

## 🧠 Claude API Integration

OpsOracle uses Claude API for intelligent analysis:

### Incident Analysis
Claude analyzes logs, metrics, and historical incidents to:
- ✅ Identify root causes
- ✅ Suggest specific fixes
- ✅ Assess severity (CRITICAL/HIGH/MEDIUM/LOW)
- ✅ Generate step-by-step remediation
- ✅ Write professional post-mortems

### Configuration
All Claude calls use **claude-3-5-sonnet-20241022** model with optimized prompts for infrastructure analysis.

---

## 🔧 Core Components

### 1. **Agents** (`backend/agents/`)
- `llm_agent.py` — Claude-powered analysis
- `remediation_agent.py` — Autonomous fixes

### 2. **Services** (`backend/services/`)
- `aws_manager.py` — AWS CloudWatch, Lambda, EC2
- `log_parser.py` — Parse & structure logs
- `rag_service.py` — Semantic search
- `blast_radius_service.py` — Multi-service detection
- `alert_service.py` — Alert ingestion & triage

### 3. **ML** (`backend/ml/`)
- `anomaly_detector.py` — Isolation Forest model

### 4. **Routers** (`backend/routers/`)
- `incidents.py` — Incident endpoints
- `metrics.py` — Metrics endpoints
- `remediation.py` — Remediation endpoints
- `postmortem.py` — Post-mortem endpoints

---

## 📝 Sample Usage

### Test Anomaly Detection
```bash
curl -X POST http://localhost:8000/api/anomaly/predict \
  -H "Content-Type: application/json" \
  -d '{
    "cpu_utilization": 95,
    "memory_utilization": 92,
    "request_latency": 450,
    "error_rate": 0.15,
    "request_count": 1200
  }'
```

### Test Incident Analysis
```bash
curl -X POST http://localhost:8000/api/incidents/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "logs": {"summary": "Lambda timeout", "error_count": 3},
    "metrics": {"cpu": 85, "memory": 90},
    "service": "lambda"
  }'
```

---

## 🏆 Key Differentiators

| Feature | OpsOracle |
|---------|-----------|
| **LLM** | Claude API (Anthropic) |
| **Anomaly Detection** | Isolation Forest ML |
| **RAG Pipeline** | Semantic search with embeddings |
| **Blast Radius** | Multi-service cascade detection |
| **Autonomy Levels** | 3 permission levels |
| **Auto Post-Mortems** | Claude-generated narratives |
| **Database** | DynamoDB-ready |
| **Deployment** | AWS-native |

---

## 📚 File Organization

### Backend Files
- `backend_main.py` → `backend/main.py`
- `backend_config_CLAUDE.py` → `backend/config.py`
- `agents_llm_agent_CLAUDE.py` → `backend/agents/llm_agent.py`
- `agents_remediation_agent.py` → `backend/agents/remediation_agent.py`
- All services → `backend/services/`
- All routers → `backend/routers/`
- `ml_anomaly_detector.py` → `backend/ml/anomaly_detector.py`

### Frontend Files
- `frontend_app.py` → `frontend/app.py`

### Config Files
- `.env_CLAUDE` → `.env`
- `requirements_CLAUDE.txt` → `requirements.txt`

---

## 🔐 Security

- All API keys in `.env` (never commit)
- AWS credentials via environment
- Claude API key in `.env`
- No sensitive data in logs

---

## 📈 Production Deployment

### Database
Replace in-memory stores with:
- DynamoDB for incidents
- Pinecone for RAG vectors
- CloudWatch Logs Insights for logs

### Monitoring
- CloudWatch alarms
- X-Ray tracing
- Application insights

### Scaling
- Lambda auto-scaling
- RDS multi-AZ
- CloudFront CDN

---

## 🧪 Testing

```bash
# Run tests
python tests/test_anomaly.py
python tests/test_rag.py
python tests/test_agents.py

# Check backend
curl http://localhost:8000/

# Check frontend
curl http://localhost:8501/
```

---

## 📞 Support & Resources

- **Claude API Docs:** https://docs.anthropic.com
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Streamlit Docs:** https://docs.streamlit.io/
- **AWS SDK:** https://boto3.amazonaws.com/

---

## 📄 License

Built for portfolio/educational purposes.

---

**Version:** 1.0.0  
**Status:** Production Ready  
**LLM:** Claude API (Anthropic)  
**Updated:** January 2026