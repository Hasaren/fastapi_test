from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()

@app.get('/')
def root_handler():
    # 리턴되는 자료형은 dict -> 변환 자동으로 json으로
    return {'message':'hello'}

@app.get('/login')
def login_handler():
    # 리턴되는 자료형은 dict -> 변환 자동으로 json으로
    return {'message':'login'}

@app.get('/users/{user_id}')
def read_user_handler(user_id: int):
    # 리턴되는 자료형은 dict -> 변환 자동으로 json으로
    return {'user_id':user_id,'message':f'user {user_id} 정보'}


# 쿼리 파라미터
@app.get('/items')
def read_item_handler(max_price: int|None=None):
    # 리턴되는 자료형은 dict -> 변환 자동으로 json으로
    return {'max_price':max_price,'message':f'item {max_price} 정보'}


# pydantic 모델
class Item(BaseModel):
    name: str
    price: int
    is_stock: bool = True

# 요청 본문 수신
@app.post(path='/items',
          response_model=Item, #응답 구조를 Item으로 고정
          status_code=status.HTTP_201_CREATED
          )
def create_item_handlear(item: Item):
    return item

# 경로 변수 + 쿼리 파라미터 + 요청 본문 혼합
@app.put('/items/{item_id}')
def update_item_handler(item_id,assignee, item):
    return {'item_id':item_id,
            'assignee':assignee,
            'item':item}

# 응답 모델
class OrderResponse(BaseModel):
    order_id: int
    pickup: bool|None=None

@app.get('/orders/{order_id}',response_model=OrderResponse)
def get_order_handler(order_id: int, pickup: bool|None=None):
    return {'order_id':order_id,
            'pickup':pickup}