from pydantic import BaseModel

# 블로그 글 추가
class add_blog_request(BaseModel):
    title: str
    content: str | None=None

# 블로그 수정 요청
class update_blog_request(BaseModel):
    title: str | None=None
    content: str | None=None