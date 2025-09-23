from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Learning Path Generator API",
              description="Backend API for ML-powered course recommendations",
              version="1.0")

class Features(BaseModel):
    vector: list[float]

@app.post("/recommend")
def recommend(features: Features):
    # Mock prediction for now
    return {
        "recommendation": "Software Engineer",
        "confidence": 0.92,
        "input": features.vector
    }

@app.post("/explain")
def explain(features: Features):
    # Mock explanation
    return {
        "explanation": [
            {"feature_index": i, "contribution": round(val * 0.1, 3)}
            for i, val in enumerate(features.vector)
        ]
    }

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": False}
