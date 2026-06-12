# 업그레이드 버전 --> id 중복 문제, 등 해결 버전
#  오늘 점심

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, field_validator

import random
from enum import Enum # 허용할 값을 미리 정해두는 것


app = FastAPI(
    title='점심 메뉴 추천 API',
    description='오늘 뭐 먹을 지 고민될때 사용하는 메뉴 추천 API',
    version='1.0.1',
)



# Enum 카테고리 허용값 제한
# str 응답에서 문자열로 출력된다.
class CategoryEnum(str, Enum):
    한식 = "한식"
    일식 = "일식"
    중식 = "중식"
    양식 = "양식"

# pydantic 모델: 저장소(DB 역할)에 사용할 메뉴 schema
# 요청과 응답 모두 동일한 구조로 일관성 유지
class Menu(BaseModel):
    id: int
    name: str
    category: CategoryEnum
    price: int
    like: int = 0

# 요청 바디 schema
class MenuCreateRequest(BaseModel):
    """
    메뉴 생성 시 클라이언트가 내보내는 데이터 구조
    """
    name: str
    category: CategoryEnum
    price: int

    #field_validator: 추가 유효성 검사 -> price 0이하이면 의미 없는 데이터이므로 차단
    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('가격은 0보다 커야 합니다.')
        return v

class MenuUpdateRequest(BaseModel):
    name: str|None=None
    category: CategoryEnum|None=None
    price: int|None=None

    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('가격은 0보다 커야 합니다.')
        return v



# 임시 데이터 장소 --> pydantic 모델로 저장 (타입 일관성 유지)
menus: list[Menu] = [
    Menu(id=1, name='김치찌개', category=CategoryEnum.한식, price=9000, like=0),
    Menu(id=2, name='돈까스', category=CategoryEnum.일식, price=11000, like=0),
    Menu(id=3, name='마라탕', category=CategoryEnum.중식, price=13000, like=0),
    Menu(id=4, name='햄버거', category=CategoryEnum.양식, price=8500,  like=0)
]

# 헬퍼 함수 : 다음 id 계산
def get_next_id():
    if not menus:
        return 1 # 메뉴가 하나도 없으면 1부터 시작
    return max(menu.id for menu in menus)+1

# 엔드포인트 정의
@app.get('/')
def home():
    """
    루트 경로 - API 안내 메시지 반환
    """
    return {'message':'오늘 뭐 먹지 메뉴 추천 API'}

@app.get('/menus', response_model=list[Menu])
def get_menus():
    """
    전체 메뉴 목록 반환
    GET /menus
    응답: 메뉴 리스트 전체
    """
    return menus

@app.get(
    '/menus/random', response_model=Menu
)
def random_menu():
    """
    랜덤 메뉴 1개 반환
    GET /menus/random
    응답: 랜덤 메뉴 1개
    주의: 반드시 특정 id 메뉴 반환 보다 위에 정의되어야 한다.
    """
    return random.choice(menus)

@app.get('/menus/{menu_id}', response_model=Menu)
def get_menu(menu_id: int):
    """
    특정 id의 메뉴 1개 반환

    GET /menus/1
    없는 아이디라면 404 반환
    """
    for menu in menus:
        if menu.id==menu_id:
            return menu
        
    raise HTTPException(status_code=404, detail='메뉴를 찾을 수 없습니다.')

@app.post(
    '/menus/',
    status_code=201, response_model=Menu
)
def create_menu(body:MenuCreateRequest):
    """
    새 메뉴 등록

    POST /menus
    body: name, category, price 전달
    id: 자동 부여
    like: 생성시 항상 0으로 초기화
    """
    new_menu = Menu(
        id=get_next_id(),
        name=body.name,
        category=body.category,
        price=body.price,
        like=0,
    )
    menus.append(new_menu)
    return new_menu

@app.patch('/menus/{menu_id}', response_model=Menu)
def update_menu(menu_id: int, body:MenuUpdateRequest):
    """
    메뉴 수정

    POST /menus/1
    전달된 필드만 수정, 나머지는 기존 값 유지
    """

    for menu in menus:
        if menu.id==menu_id:
            if body.name is not None:
                menu.name = body.name
            if body.category is not None:
                menu.category = body.category
            if body.price is not None:
                menu.price = body.price

            return menu
    
    raise HTTPException(status_code=404)

@app.patch('/menus/{menu_id}/like', response_model=Menu)
def like_menu(menu_id: int):
    """
    메뉴 좋아요 +1
    
    PATCH /menus/1/like
    요청 바디가 없다. url만으로 동작
    like 필드를 1증가시키고, 수정된 메뉴 반환
    """

    for menu in menus:
        if menu.id==menu_id:
            menu.like += 1
            return menu

    raise HTTPException(status_code=404)

@app.delete('/menus/{menu_id}')
def delete_menu(menu_id: int):
    """
    특정 메뉴 삭제

    DELETE /menus/1
    """

    for menu in menus:
        if menu.id==menu_id:
            menus.remove(menu)
            return
    
    raise HTTPException(status_code=404)