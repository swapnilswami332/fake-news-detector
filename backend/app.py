import asyncio
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .fact_checker import FactChecker
from .predict import NewsClassifier
from .train import train_model
from .utils import calculate_trust_score


class PredictionRequest(BaseModel):
    text: str = Field(min_length=20, max_length=20_000)


class Source(BaseModel):
    title: str
    url: str


class PredictionResponse(BaseModel):
    prediction: str
    confidence: int
    trust_score: int
    model_reason: str
    ai_fact_check: str
    sources: list[Source]
    processing_time_ms: int


@asynccontextmanager
async def lifespan(_: FastAPI):
    model_path = Path(__file__).parent / "models" / "model.pkl"
    if not model_path.exists():
        train_model()
    app.state.classifier = NewsClassifier()
    app.state.fact_checker = FactChecker()
    yield


app = FastAPI(title="TruthLens API", version="0.1.0", lifespan=lifespan)
_cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest) -> PredictionResponse:
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Please provide an article or headline.")

    started_at = time.perf_counter()
    model_result = app.state.classifier.analyze(text)
    fact_check, sources = await asyncio.to_thread(app.state.fact_checker.check, text)
    trust_score = calculate_trust_score(
        str(model_result["prediction"]),
        int(model_result["confidence"]),
        sources,
    )
    elapsed_ms = round((time.perf_counter() - started_at) * 1_000)

    return PredictionResponse(
        prediction=str(model_result["prediction"]),
        confidence=int(model_result["confidence"]),
        trust_score=trust_score,
        model_reason=str(model_result["model_reason"]),
        ai_fact_check=fact_check,
        sources=[Source(**source) for source in sources],
        processing_time_ms=elapsed_ms,
    )
