from sqlalchemy import Column, Integer, BigInteger, Text, TIMESTAMP, JSON, func, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from app.db import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(Text, unique=True, nullable=True)
    phone_hash = Column(Text, unique=True, nullable=True)
    name = Column(Text, nullable=True)
    locale = Column(Text, nullable=True)
    region = Column(Text, nullable=True)
    role = Column(Text, default="learner")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    profile = relationship("Profile", uselist=False, back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    nsqf_level_est = Column(Integer, nullable=True)
    learner_vector_json = Column(JSONB, nullable=True)
    constraints_json = Column(JSONB, nullable=True)
    points = Column(Integer, default=0)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")
