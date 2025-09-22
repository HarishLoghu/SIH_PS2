from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class OTPRequest(BaseModel):
    identifier: str  # email or phone

class OTPVerify(BaseModel):
    identifier: str
    otp: str
    name: Optional[str] = None  # optional for new user

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class QuizAnswers(BaseModel):
    user_id: int
    answers: Dict[str, Any]   # structure per your quiz (academics, skills, constraints...)

class ProfileOut(BaseModel):
    user_id: int
    nsqf_level_est: Optional[int]
    learner_vector_json: Optional[Dict[str, Any]]
    constraints_json: Optional[Dict[str, Any]]
    points: int
