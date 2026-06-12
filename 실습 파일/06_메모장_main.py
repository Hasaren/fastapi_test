# 간단한 메모장 만들기 --> DB 없이 메모리
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from datetime import datetime

app = FastAPI(title='메모장 API', 
              description='fastAPI 실습용 메모장 CRUD API', 
              version='1.0.0')

# 임시 데이터 저장소 (메모리)
memos = []

next_id = 1 # 자동 증가 ID를 직접 관리 (전역 변수)

# pydantic 모델 정의
# 메모 생성 / 수정 / 조회

class MemoCreate(BaseModel):
    """
    POST 요청 바디 - 메모 작성시 받는 데이터
    """
    content: str

class MemoUpdate(BaseModel):
    """
    PATCH 요청 바디 - None이 기본값 -> 보내지 않으면 기존 값 유지
    """
    content : str | None=None

class MemoResponse(BaseModel):
    """
    GET 응답으로 내보내는 메모 형태
    """
    id: int
    content : str
    create_at: str # 생성 시간
    update_at: str # 수정 시간


# helper 함수
def find_memo(memo_id: int):
    """
    ID로 메모를 검색, 없으면 None을 반환
    """
    return next((m for m in memos if m['id']==memo_id), None)

def now():
    """
    현재 시각을 보기 좋게 문자열로 변환
    """ 
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 엔드 포인트
@app.get('/')
def home():
    """
    API 안내
    """
    return {'message':'메모장 API 입니다. /docs에서 테스트'}

@app.get(
        '/memos',
        response_model=list[MemoResponse]
)
def get_memos():
    """
    전체 메모 조회-메모가 없으면 빈리스트 반환
    """
    return memos

@app.get(
        '/memos/{memo_id}',
        response_model=MemoResponse
)
def get_memo(memo_id: int):
    """
    특정 메모 조회-메모가 없으면 404에러 반환
    """
    memo = find_memo(memo_id)
    if memo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'{memo_id}번 메모를 찾을 수 없다.')
    return memo


@app.post(
    '/memos',
    response_model=MemoResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_memo(body: MemoCreate):
    """
    새로운 메모 생성
    """
    global next_id # 전역변수 불러오기
    new_memo = {
        'id': next_id,
        'content' : body.content,
        'create_at': now(), # 생성 시간
        'update_at': now(), # 수정 시간
    }

    memos.append(new_memo)
    next_id += 1
    return new_memo

@app.patch(
    '/memos/{memo_id}',
    response_model=MemoResponse,
    status_code=status.HTTP_200_OK
)
def update_memo(memo_id:int, body: MemoUpdate):
    """
    메모 수정 -> 없으면 404에러 반환
    """
    memo = find_memo(memo_id)
    if memo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'{memo_id}번 메모를 찾을 수 없다.')
    if body.content is not None:
        memo['content'] = body.content
        memo['update_at'] = now()
    
    return memo

@app.delete(
    '/memos/{memo_id}',
    response_model=MemoResponse
)
def delete_memo(memo_id: int):
    memo = find_memo(memo_id)
    if memo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'{memo_id}번 메모를 찾을 수 없다.')
    memos.remove(memo)
    # return memos
