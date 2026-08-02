# TruthLens

**Repository:** [github.com/swapnilswami332/fake-news-detector](https://github.com/swapnilswami332/fake-news-detector)

TruthLens is a fake-news analysis demo that combines a **language-pattern classifier** with an **optional source-aware review** (search + local LLM). Paste a headline or article to see a Fake/Real label, confidence, word-level reasoning, linked sources, and a credibility score.

This is a portfolio project — not a fact-checking authority.

---

## Table of contents

- [Features](#features)
- [How it works](#how-it-works)
- [Project layout](#project-layout)
- [Quick start](#quick-start)
- [API](#api)
- [Deployment](#deployment)
- [Limitations](#limitations)
- [Docker](#docker)

---

## Features

| Layer | What you get |
|--------|----------------|
| **ML** | TF-IDF + Logistic Regression, SHAP-style word explanations |
| **Retrieval** | DuckDuckGo search, semantic ranking (MiniLM + FAISS) |
| **AI review** | Optional summary via **Ollama + Mistral** (local only) |
| **UI** | React single page — dark mode, session history, copy result |

---

## How it works

```text
Browser  →  POST /predict  →  FastAPI
                                ├─ normalize text → classify (Fake/Real)
                                ├─ explain influential terms (SHAP or coefficients)
                                └─ extract claim → search → rank sources → LLM summary
                                        ↓
                              JSON response + credibility score
```

1. Text is normalized and scored by the sklearn pipeline.
2. Important tokens are surfaced for the chosen class.
3. The longest sentence drives a web search for related sources.
4. Sources are ranked; Mistral (via Ollama) summarizes support/contradiction when available.
5. Scores are combined into a **credibility score** for the UI — not a guarantee of truth.

Training data lives in `backend/train.py`: a small, transparent demo corpus. Swap it for a real labeled dataset before claiming production accuracy.

---

## Project layout

```text
fake-news-detector/
├── backend/
│   ├── app.py           # FastAPI routes (/predict, /health)
│   ├── predict.py       # Model load + SHAP explanations
│   ├── fact_checker.py  # Search, FAISS ranking, Ollama
│   ├── train.py         # Train and save model artifacts
│   └── models/          # model.pkl, vectorizer.pkl (generated locally)
├── frontend/
│   └── src/             # React UI (Vite + Tailwind)
├── Dockerfile           # API container (trains model at build)
├── requirements.txt
├── DEPLOY.md            # Host API + UI in production
└── README.md
```

---

## Quick start

### Clone

```bash
git clone https://github.com/swapnilswami332/fake-news-detector.git
cd fake-news-detector
```

### Prerequisites

- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.com/) + `mistral` (optional, for AI summaries)

### Backend

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m backend.train
uvicorn backend.app:app --reload
```

API: **http://localhost:8000** · Health: **http://localhost:8000/health**

Optional Ollama:

```bash
ollama pull mistral
ollama serve
```

Set `ENABLE_FACT_CHECKING=false` to skip search/LLM and use ML-only responses.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** (Vite proxies API calls in dev).

---

## API

**`POST /predict`**

```json
{ "text": "Scientists publish a peer reviewed study on coastal erosion trends." }
```

**`GET /health`** → `{"status":"ok"}`

Example response fields: `prediction`, `confidence`, `trust_score`, `model_reason`, `ai_fact_check`, `sources[]`, `processing_time_ms`.

---

## Deployment

Public hosting needs a deployed API URL and CORS configuration. Step-by-step guide:

**[DEPLOY.md](DEPLOY.md)** — Render/Railway (API) + Vercel/Netlify (UI), env vars `VITE_API_URL` and `CORS_ORIGINS`.

---

## Limitations

- The model detects **writing style**, not ground truth.
- Search and LLM outputs can be incomplete or wrong.
- High confidence ≠ verified fact.
- Not a substitute for professional journalism or established fact-checkers.

---

## Docker

```bash
docker build -t truthlens-api .
docker run -p 8000:8000 truthlens-api
```

Ollama is not included in the image. Use a reachable Ollama host or `ENABLE_FACT_CHECKING=false` for ML-only mode.

---

## Tech stack

Python · FastAPI · scikit-learn · SHAP · DuckDuckGo Search · Sentence Transformers · FAISS · LangChain Ollama · React · TypeScript · Tailwind · Axios
