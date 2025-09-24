from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI(
    title="Learning Path Generator API",
    description="Backend API for ML-powered course recommendations + external courses",
    version="1.0"
)

# ---------------- Root Route ----------------
@app.get("/")
def root():
    return {"message": "Welcome to the Learning Path Generator API 🚀"}

# ---------------- Mock ML Endpoints ----------------
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

# ---------------- Udemy External Courses (RapidAPI) ----------------
RAPIDAPI_KEY = "df33adf040msh36b5b205dbf09e4p188dedjsn2b364664a015"

@app.get("/external-courses/udemy")
def get_udemy_courses(query: str = "python", page: int = 1, page_size: int = 10):
    """
    Fetch free Udemy courses from RapidAPI.
    Example: /external-courses/udemy?query=python&page=1&page_size=10
    """
    url = "https://udemy-paid-courses-for-free-api.p.rapidapi.com/rapidapi/courses/search"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "udemy-paid-courses-for-free-api.p.rapidapi.com"
    }

    try:
        resp = requests.get(url, headers=headers, params={
            "query": query,
            "page": page,
            "page_size": page_size
        })
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        
        # 🔹 Debug Mode: return the raw response from RapidAPI
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
