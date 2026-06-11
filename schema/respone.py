from pydantic import BaseModel

# 게시글 조회
class blog_respone(BaseModel):
    id: int
    title: str
    content: str