"""
클라이언트가 서버로 보내는 데이터의 형태를 정의하는 파일
pydantic BaseModel을 상속하면 FastAPI가 요층 body를 자동으로 검증해준다.
--> 타입이 안맞거나 필수값이 없으면 자동으로 422 에러 응답
"""

import re # 정규표현식 라이브러리
from pydantic import BaseModel, EmailStr, Field, field_validator

# 할일 생성 요청
class TodoCreateRequest(BaseModel):
    title: str # 할 일의 제목, 문자열 (필수)
    is_done: bool = False # 할 일을 했다 안했다 --> 기본값 False

# 할일 수정 요청
class TodoUpdateRequest(BaseModel):
    title: str | None = None
    is_done: bool | None = None

# 회원 가입 요청
class UserSignUpRequest(BaseModel):
    # Field(...) --> ...은 "필수"라는 뜻의 파이썬 문법
    # 이메일 같은 경우는 description을 같이 쓰려면 Field() 형태가 필요하다.
    # --> description : 코드 실행에는 영향이 없고, /docs 화면에서만 표시되는 문서용 문자열
    email: EmailStr = Field(..., description="사용자 이메일 주소")
    password: str = Field(..., min_length=8, description="사용자 비밀번호(평문 입력)")

    # field_validator : Pydantic 기본 검증 통과 후 추가로 실행되는 커스텀 규칙 (데코레이터) 
    @field_validator("password")
    def validate_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("비밀번호에는 대문자가 최소 1개 포함되어야 합니다.")
        if not re.search(r"[a-z]", value):
            raise ValueError("비밀번호에는 소문자가 최소 1개 포함되어야 합니다.")
        if not re.search(r"[0-9]", value):
            raise ValueError("비밀번호에는 숫자가 최소 1개 포함되어야 합니다.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError("비밀번호에는 특수문자가 최소 1개 포함되어야 합니다.")
        return value

# 회원 로그인 요청
class UserLoginRequest(BaseModel):
    # 회원가입과 로그인을 분리한 이유 : 로그인에는 회원가입 때의 복잡한 비밀번호 규칙 검증이
    # 필요가 없다. 로그인은 "이미 만들어진 비밀번호가 맞는지"만 확인하면 된다.
    email: EmailStr = Field(..., description="사용자 이메일 주소")
    password: str = Field(..., min_length=8, description="사용자 비밀번호(평문 입력)")

# accescc Token 재발급 요청 모델
# 로그인 때 받은 refresh_token을 그대로 같이 보내는 용도, 필드는 하나
class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="로그인 시 발급받은 refresh token")

# --- ML 요청 ---
class CategoryUpdateRequest(BaseModel):
    # PATCH /todos/{id}/category 요청 body
    # 여기서 넘어온 값이 Todo.final_category에 저장되고,
    # 나중에 ml/retrain.py가 재학습 데이터로 사용한다.
    category: str = Field(..., description='사용자가 직접 확정한 카테고리 (업무/개인/긴급)')