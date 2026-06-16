from pydantic import BaseModel

# 할 일 생성 요청
class TodoCreateRequest(BaseModel):
    title: str
    is_done: bool = False

#할일 수정 요청
class TodoUpdateRequest(BaseModel):
    title: str | None=None
    is_done: bool | None=None