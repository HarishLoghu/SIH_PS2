from fastapi import APIRouter, Depends, HTTPException
from app.schemas import QuizAnswers, ProfileOut
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session
from app.models import Profile, User
from sqlalchemy import select, insert, update

router = APIRouter(prefix="/profile", tags=["profile"])

def compute_learner_vector(answers: dict):
    # Simple mapping example. Expand this based on quiz schema.
    skills = []
    interests = []
    constraints = {}
    nsqf = 1

    # academics -> bump nsqf
    acad = answers.get("academics", {}).get("highest_qualification", "").lower()
    if "phd" in acad or "post" in acad:
        nsqf = 8
    elif "bachelor" in acad:
        nsqf = 6
    elif "diploma" in acad:
        nsqf = 5
    else:
        nsqf = 3

    # prior skills list
    prior = answers.get("prior_skills", [])
    if isinstance(prior, list):
        skills.extend(prior)

    # learning pace
    pace = answers.get("learning_pace", "moderate")
    constraints["pace"] = pace

    # time/budget
    constraints["time_per_week"] = answers.get("time_per_week", 5)
    constraints["budget"] = answers.get("budget", "low")

    # interests
    ints = answers.get("interests", [])
    if isinstance(ints, list):
        interests.extend(ints)

    learner_vector = {
        "skills": list(set(skills)),
        "interests": list(set(interests)),
        "constraints": constraints,
        "nsqf_level_est": nsqf
    }
    return learner_vector, nsqf

@router.post("/quiz")
async def submit_quiz(q: QuizAnswers, session: AsyncSession = Depends(get_session)):
    # validate user exists
    stmt = select(User).where(User.id == q.user_id)
    res = await session.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    learner_vector, nsqf = compute_learner_vector(q.answers)
    # upsert profile
    stmt = select(Profile).where(Profile.user_id == q.user_id)
    res = await session.execute(stmt)
    prof = res.scalars().first()
    if prof:
        prof.learner_vector_json = learner_vector
        prof.nsqf_level_est = nsqf
        await session.commit()
    else:
        prof = Profile(user_id=q.user_id, learner_vector_json=learner_vector, nsqf_level_est=nsqf)
        session.add(prof)
        await session.commit()

    return {"status": "ok", "learner_vector": learner_vector, "nsqf_level_est": nsqf}

@router.get("/")
async def get_profile(user_id: int, session: AsyncSession = Depends(get_session)) -> ProfileOut:
    stmt = select(Profile).where(Profile.user_id == user_id)
    res = await session.execute(stmt)
    prof = res.scalars().first()
    if not prof:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "user_id": prof.user_id,
        "nsqf_level_est": prof.nsqf_level_est,
        "learner_vector_json": prof.learner_vector_json,
        "constraints_json": prof.constraints_json,
        "points": prof.points or 0
    }
