import random, hashlib
from app.config import settings
from jose import jwt
import aioredis
import asyncio

async def get_redis():
    return await aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

def generate_otp():
    # 6 digits
    return f"{random.randint(0, 999999):06d}"

def hash_str(s: str):
    return hashlib.sha256(s.encode()).hexdigest()

def create_access_token(data: dict):
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
