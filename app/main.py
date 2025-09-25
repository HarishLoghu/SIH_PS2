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
    return {
        "recommendation": "Software Engineer",
        "confidence": 0.92,
        "input": features.vector
    }

@app.post("/explain")
def explain(features: Features):
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

        data = resp.json()

        # ✅ Clean response
        cleaned = []
        for course in data.get("courses", []):
            cleaned.append({
                "title": course.get("name"),
                "category": course.get("category"),
                "image": course.get("image"),
                "original_price": course.get("actual_price_usd"),
                "discounted_price": course.get("sale_price_usd"),
                "offer_expires": course.get("sale_end"),
                "description": course.get("description"),
                "url": course.get("url"),
                "clean_url": course.get("clean_url")
            })

        return {
            "total_courses": data.get("total", 0),
            "results": cleaned
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- Adzuna Job Search API ----------------
ADZUNA_APP_ID = "41124aed"   # 👈 your real App ID
ADZUNA_APP_KEY = "e1f63054c16f5fd19fd5b0532e92d1c6"   # 👈 your real App Key

@app.get("/external-jobs/adzuna")
def get_adzuna_jobs(query: str = "python developer", country: str = "gb", page: int = 1, results_per_page: int = 10):
    """
    Fetch jobs from Adzuna API.
    Example: /external-jobs/adzuna?query=python&country=gb&page=1&results_per_page=10
    """
    url = f"http://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": query,
        "content-type": "application/json"
    }

    try:
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)

        data = resp.json()
        jobs = []
        for job in data.get("results", []):
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company", {}).get("display_name"),
                "location": job.get("location", {}).get("display_name"),
                "posted": job.get("created"),
                "url": job.get("redirect_url"),
                "description": job.get("description")
            })

        return {"total": len(jobs), "jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
