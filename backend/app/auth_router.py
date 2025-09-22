from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import OTPRequest, OTPVerify, Token
from app.utils import generate_otp, hash_str, get_redis, create_access_token
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session
from app.models import User, Profile
from sqlalchemy import select
import asyncio

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/otp")
async def request_otp(body: OTPRequest):
    identifier = body.identifier.strip().lower()
    redis = await get_redis()

    # rate limit per identifier
    rate_key = f"otp_rate:{identifier}"
    cnt = await redis.get(rate_key) or "0"
    if int(cnt) >= settings.OTP_RATE_LIMIT_PER_HOUR:
        raise HTTPException(status_code=429, detail="Too many OTP requests. Try later.")
    await redis.incr(rate_key)
    await redis.expire(rate_key, 3600)

    otp = generate_otp()
    otp_h = hash_str(otp + identifier)  # simple salting with identifier
    key = f"otp:{identifier}"
    await redis.set(key, otp_h, ex=settings.OTP_TTL_SECONDS)

    # TODO: integrate SMS/email provider. For now, log/print
    print(f"[DEV] OTP for {identifier} is {otp}")  # dev: console output

    return {"status": "ok", "message": "OTP sent (dev: printed to console)."}

@router.post("/verify", response_model=Token)
async def verify_otp(body: OTPVerify, session: AsyncSession = Depends(get_session)):
    identifier = body.identifier.strip().lower()
    redis = await get_redis()
    key = f"otp:{identifier}"
    stored = await redis.get(key)
    if not stored:
        raise HTTPException(status_code=400, detail="OTP expired or not requested")

    if stored != hash_str(body.otp + identifier):
        raise HTTPException(status_code=401, detail="Invalid OTP")

    # OTP OK -> create or fetch user
    stmt = select(User).where((User.email == identifier) | (User.phone_hash == identifier))
    res = await session.execute(stmt)
    user = res.scalars().first()
    if not user:
        # create user
        user = User(email=identifier if "@" in identifier else None,
                    phone_hash=identifier if "@" not in identifier else None,
                    name=body.name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        # create empty profile
        profile = Profile(user_id=user.id, learner_vector_json={}, constraints_json={})
        session.add(profile)
        await session.commit()

    # remove OTP so it cannot be reused
    await redis.delete(key)

    token = create_access_token({"user_id": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
  