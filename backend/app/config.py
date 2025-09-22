from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    OTP_TTL_SECONDS: int = 300
    OTP_RATE_LIMIT_PER_HOUR: int = 5

    class Config:
        env_file = ".env"

settings = Settings()
