from fastapi import FastAPI, Depends, Request
from app.auth_router import router as auth_router
from app.profile_router import router as profile_router
from app.db import engine, Base
import asyncio

app = FastAPI(title="Learner Backend (Sprint1)")

app.include_router(auth_router)
app.include_router(profile_router)

@app.on_event("startup")
async def on_startup():
    # create tables if not exist (dev convenience)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
