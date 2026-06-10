# fastAPI 클래스 불러오기

from fastapi import FastAPI

app = FastAPI()

# 서버 실행
@app.get('/') # /경로로 get 요청이 오면 아래 함수를 실행
def root_hander():
    # 딕셔너리를 반환하면 FastAPI가 자동으로 json으로 변환
    return {'message':'hello, FastAPI'}