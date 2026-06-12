from blog.schema.respone import blog_respone
from blog.schema.request import add_blog_request, update_blog_request
from fastapi import FastAPI, status, HTTPException

app = FastAPI()

all_blog = []

# 전체 게시글 조회
@app.get(
        '/',
        response_model=list[blog_respone],
        )
def all_blog_respone_handler():
    return all_blog

# 단일 게시글 조회
@app.get(
    '/{blog_id}',
    response_model=blog_respone
)
def blog_respone_handler(blog_id: int):
    for blog in all_blog:
        if blog_id == blog['id']:
            return blog
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

# 블로그 글 추가
@app.post(
    '/',
    response_model=blog_respone,
    status_code=status.HTTP_201_CREATED
)
def add_blog_handler(body: add_blog_request):
    new_blog = {'id':len(all_blog)+1,
                'title':body.title,
                'content':body.content}
    all_blog.append(new_blog)
    return new_blog

# 블로그 글 수정
@app.patch(
        '/{blog_id}',
        response_model=blog_respone
)
def update_blog_handler(blog_id:int, body:update_blog_request):
    for blog in all_blog:
        if blog_id == blog['id']:
            if body.title is not None:
                blog['title'] = body.title
            if body.content is not None:
                blog['content'] = body.content
            return blog
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='blog not found')

# 블로그 글 삭제
@app.delete(
    '/{blog_id}',
    response_model=blog_respone,
)
def delete_blog_handler(blog_id: int):
    for blog in all_blog:
        if blog_id == blog['id']:
            all_blog.remove(blog)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='blog not found')