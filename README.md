# TruthLens

TruthLens is a small fake-news analysis project that combines a local text classifier with an optional AI-assisted source review. Paste a headline or article, then get a language-pattern prediction, the words that influenced it, relevant search links, and a cautious credibility score.
**Introduction**
TruthLens is a two-tier analyzer: (1) lightweight sklearn fake/real stylistic classifier with explainability, plus (2) optional retrieval-augmented narrative via DuckDuckGo and local Mistral through Ollama. The React app is a polished single-page demo with dark mode and session history. The project is optimized for local full-stack demo (Ollama + Vite proxy) and documented cloud split (ML + search on Docker API, static UI elsewhere, often without working LLM). Any work that claims accuracy, adds authority language, or commits secrets would contradict the project's stated scope.
## Architecture

```text
Browser
  │ POST /predict
  ▼
FastAPI
  ├── TF-IDF + Logistic Regression ──> Fake/Real, confidence, word explanation
  └── DuckDuckGo search ──> semantic ranking ──> Ollama Mistral summary
                                                │
                                                ▼
                                 combined response and credibility score
```

## Tech stack

- **API:** Python, FastAPI, Pydantic
- **ML:** scikit-learn, TF-IDF, Logistic Regression, SHAP
- **Retrieval:** DuckDuckGo Search, Sentence Transformers, FAISS
- **AI review:** LangChain Ollama with local Mistral
- **UI:** React, TypeScript, Tailwind CSS, Axios

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.com/) for the AI fact-check summary (optional)

### Backend

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m backend.train
uvicorn backend.app:app --reload
```

The API runs at `http://localhost:8000`. `backend.train` saves `model.pkl` and `vectorizer.pkl` under `backend/models/`. The API also trains them on first launch if they do not exist.

For AI summaries, install Ollama and download Mistral:

```bash
ollama pull mistral
ollama serve
```

The prediction endpoint still works if Ollama is unavailable. It returns the source links and a message asking the user to review them directly. To skip external search and Ollama entirely, set `ENABLE_FACT_CHECKING=false` before starting the API.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, usually `http://localhost:5173`.

## API

`POST /predict`

```json
{ "text": "Scientists publish a peer reviewed study on coastal erosion trends." }
```

Example response shape:

```json
{
  "prediction": "Real",
  "confidence": 78,
  "trust_score": 62,
  "model_reason": "The reporting-style language around “peer reviewed, study” influenced this result.",
  "ai_fact_check": "Relevant sources were found...",
  "sources": [{ "title": "Example source", "url": "https://example.com" }],
  "processing_time_ms": 824
}
```

`GET /health` returns `{"status":"ok"}`.

## How it works

1. The text is lightly normalized, then scored by a TF-IDF and Logistic Regression model.
2. SHAP identifies the token contributions for the chosen class. If SHAP cannot run in the local environment, a coefficient-based equivalent is used.
3. The longest sentence is used as the central claim for DuckDuckGo search.
4. Search results are ranked with MiniLM embeddings and FAISS when available. Trusted public-interest domains receive a small boost.
5. Ollama Mistral is instructed to describe whether the links are supportive, contradictory, or insufficient. It is told to preserve uncertainty.
6. The response combines those signals into a credibility score. The score is a UI aid, not a probability of truth.

## Project notes

The included training corpus in `backend/train.py` is deliberately small and transparent. It is a demo baseline made of illustrative examples, not a benchmark dataset. Replace it with a labeled, licensed dataset and evaluate on a held-out test set before making claims about accuracy.

## Known limitations

- The ML model detects linguistic patterns; it cannot determine whether factual claims are true.
- Search results can be incomplete, biased, outdated, or manipulated.
- The LLM may misunderstand a source or produce an incorrect summary.
- A high confidence score reflects this model's certainty, not verified truth.
- Predictions should never replace professional journalism, domain experts, or established fact-checking organizations.

## Future improvements

- Add dataset versioning, train/validation metrics, and threshold calibration.
- Extract multiple claims instead of using one representative sentence.
- Show source snippets and publication dates alongside links.
- Add automated tests for API responses and text preprocessing.
- Support a hosted LLM provider for deployments where local Ollama is unsuitable.

## Docker

```bash
docker build -t truthlens-api .
docker run -p 8000:8000 truthlens-api
```

This image runs the API, but does not bundle Ollama. Configure an accessible Ollama service or set `ENABLE_FACT_CHECKING=false` for a self-contained ML-only container.
