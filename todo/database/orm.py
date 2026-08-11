# ===============================================================
# database/orm.py
# 역할: 모든 ORM 모델(테이블 클래스)의 부모가 되는 Base 클래스를 정의
# ORM : Object Relational Mapping
#  - SQL을 직접 작성하지 않고 파이썬 클래스로 db 테이블을 다루는 방식
#  - 예: Todo 클래스 -> Todo 테이블 자동 생성
# ===============================================================

from sqlalchemy.orm import DeclarativeBase

# Base 클래스 : 이 클래스를 상속 받는 모든 클래스는 데이터 베이스테이블로 취급한다는 기준점 역할
class Base(DeclarativeBase):
    pass