from pydantic import BaseModel
from datetime import datetime
import re

class TodoResponse(BaseModel):
    id: int
    title: str
    is_done: bool

# 회원 가입 응답 모델
class UserSignUpResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
