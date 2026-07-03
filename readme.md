# OpsOracle — Autonomous AI Incident Response System

> Detects, diagnoses, and remediates cloud infrastructure failures in under 60 seconds.
> Human engineers take 45 minutes. OpsOracle does it autonomously.

---

## What It Does

OpsOracle is a production-grade AI SRE (Site Reliability Engineering) platform. When a cloud service fails, it:

1. **Detects** anomalies in real-time using ML (Isolation Forest)
2. **Maps blast radius** — identifies all cascading service failures
3. **Searches memory** — RAG pipeline retrieves similar past incidents
4. **Analyses** root cause using Groq LLM (Llama 3.3 70B)
5. **Remediates** automatically with 3 permission levels
6. **Writes post-mortem** report without human input

**Simulated MTTR: 45 minutes → under 60 seconds.**

---

## Demo

```
Incident triggered → Anomaly detected (8s) → Blast radius mapped (15s)
→ RAG search (20s) → Root cause analysis (35s) → Fix applied (47s)
→ Post-mortem generated (60s)
```

Test it yourself using the built-in "Trigger test incident" button on the dashboard.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Python 3.12 |
| Frontend | Streamlit |
| LLM | Groq API — Llama 3.3 70B (free) |
| Anomaly Detection | Scikit-learn Isolation Forest |
| RAG Pipeline | LangChain + Sentence Transformers |
| Vector Search | Cosine similarity (Pinecone-ready) |
| Cloud | AWS (CloudWatch, Lambda, EC2, X-Ray, RDS) |
| Embeddings | all-MiniLM-L6-v2 |
| PDF Reports | ReportLab |

---

## Architecture

```
OpsOracle/
├── backend/
│   ├── agents/
│   │   ├── llm_agent.py          # Groq LLM reasoning
│   │   └── remediation_agent.py  # Autonomous fix execution
│   ├── services/
│   │   ├── aws_manager.py        # CloudWatch, Lambda, EC2
│   │   ├── log_parser.py         # Log parsing + blast radius
│   │   ├── rag_service.py        # Semantic search pipeline
│   │   ├── blast_radius_service.py
│   │   └── alert_service.py      # Incident intake + triage
│   ├── ml/
│   │   └── anomaly_detector.py   # Isolation Forest model
│   ├── routers/
│   │   ├── incidents.py          # POST /api/incidents/analyze
│   │   ├── metrics.py
│   │   ├── remediation.py
│   │   └── postmortem.py
│   ├── models/schemas.py
│   ├── utils/
│   ├── main.py                   # FastAPI entry point
│   └── config.py
├── frontend/
│   └── app.py                    # Streamlit dashboard
├── ml_models/
├── data/
├── tests/
├── .env
└── requirements.txt
```

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/OpsOracle.git
cd OpsOracle
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add:

```env
GROQ_API_KEY=gsk_your_key_from_console.groq.com
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
```

Get your **free** Groq API key (no credit card) at: https://console.groq.com/keys

### 4. Run backend

```bash
python -m backend.main
```

Backend runs at: `http://localhost:8000`
Interactive API docs: `http://localhost:8000/docs`

### 5. Run frontend

```bash
streamlit run frontend/app.py
```

Dashboard opens at: `http://localhost:8501`

---

## Test the Full Pipeline

Go to `http://localhost:8000/docs`, find `POST /api/incidents/analyze` and send:

```json
{
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
```

Or click **"Trigger test incident"** directly from the Streamlit dashboard.

---

## API Endpoints

### Incidents
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/incidents/` | List all incidents |
| POST | `/api/incidents/analyze` | Full pipeline — analyze and store |
| GET | `/api/incidents/stats/overview` | Stats summary |

### Remediation
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/remediation/execute` | Execute fix |
| GET | `/api/remediation/history` | Remediation history |

### Post-Mortem
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/postmortem/generate` | Generate report |
| GET | `/api/postmortem/{id}` | Get report |

---

## Key Features

### Multi-service blast radius detection
When Lambda fails, OpsOracle automatically maps the full cascade — API Gateway, RDS, EC2, DynamoDB — and prioritizes which service to fix first.

### RAG-powered incident memory
Every incident is embedded and stored. New incidents are matched against historical ones, giving the LLM context from your own infrastructure history — not generic advice.

### Isolation Forest anomaly detection
Detects abnormal server metrics (CPU, memory, latency, error rate) before they escalate. Falls back to threshold-based detection if model is not yet trained.

### Autonomous remediation (3 levels)
- **Level 1** — Suggest only (show what fix would be applied)
- **Level 2** — Ask confirmation, then execute
- **Level 3** — Fully autonomous, no human needed

### Auto post-mortem generation
After every incident, the LLM writes a structured post-mortem with timeline, root cause, impact, resolution, lessons learned, and action items.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Free from console.groq.com/keys |
| `AWS_ACCESS_KEY_ID` | Yes | AWS IAM credentials |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS IAM credentials |
| `AWS_REGION` | No | Default: us-east-1 |
| `PINECONE_API_KEY` | No | For production vector storage |
| `FASTAPI_PORT` | No | Default: 8000 |
| `STREAMLIT_PORT` | No | Default: 8501 |

---

## Production Upgrade Path

| Component | Current (demo) | Production |
|---|---|---|
| Incident storage | In-memory | AWS DynamoDB |
| Vector store | In-memory cosine similarity | Pinecone |
| LLM | Groq (free) | Anthropic Claude API |
| Logs | CloudWatch (mocked) | Real CloudWatch integration |

---

## Security

- All API keys stored in `.env` — never committed to git
- `.gitignore` excludes `.env`, `venv/`, `__pycache__/`, `*.pkl`
- AWS credentials via environment variables only

---

## Built By

**Gaurav Sindhi** — B.Tech AI/ML, R.C. Patel Institute of Technology

- LinkedIn: [/gaurav-sindhi](https://linkedin.com/in/gaurav-sindhi)
- GitHub: [/GauravSindhi](https://github.com/GauravSindhi)

---

## License

Built for portfolio and educational purposes.

---

*OpsOracle v1.1.0 — LLM: Groq Llama 3.3 70B — Updated: July 2026*