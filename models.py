# ==========================================================
# models.py
#  - SQLAlchemy ORM
#  - 파이썬 클래스 -> DB 테이블 --> mapping하는 부분
#  - Todo(할 일) 1개는 User(회원) 1명에게 속할 수 있다. --> 1:N 관계
#  - (한 명의 회원이 여러개의 할 일을 가질 수있다.)

# 기본키(Primary Key, PK)
#  - 테이블에서 각 행을 고유하게 식별하기 위한 컬럼
#  - 기본키 값은 절대 중복될 수 없다.
#  - 반드시 하나의 값이 존재해야 한다.
#  - 테이블 내부에서 데이터를 구분하기 위한 기준

# 외래키(Foreign Key, FK)
#  - 다른 테이블의 기본 키를 참조하는 컬럼
#  - 한 테이블의 데이터가 다른 테이블의 어떤 데이터와 연결되어있는지를 표현하기 위해 사용된다.
#  - 이를 통해 각 할 일이 어떤 사용자에게 속해있는지 알 수 있다.
#  - 테이블과 테이블 사이 관계를 표현하기 위한 연결 고리
# ==========================================================

from datetime import datetime
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.orm import Base

# ---- Todo 모델 (할 일 테이블)
class Todo(Base):
    __tablename__ = 'todo' # 실제 DB에 생성할 테이블 이름

    id: Mapped[int] =mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_done: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'), # user 테이블의 id컬럼을 참조하는 외래키
        nullable=True, # 담당 회원을 지정하지 않고도 할 일 생성 가능 (선택 사항)
    )

    # 관계(relationship) 설정 - todo.user로 연결된 User 객체에 바로 접근 가능해진다.
    user: Mapped['User'] = relationship(
        back_populates='todos', # User쪽의 todos 속성과 서로 짝지어진다. (양방향 관계)
    )


# ---- User 모델 (회원 테이블)
class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True, # 같은 이메일로 중복 가입 불가.
        index=True, # 이메일로 조회가 자주 일어날 것이므로 검색 속도 향상을 위한 인덱스
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False, # 비밀번호는 평문이 아닌 '해시된 값'으로 저장
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(), # 오늘 날짜 시간 추출
        nullable=False,
    )
    # 한명의 회원은 여러개의 todo를 받을 수있다. -> list
    todos: Mapped[list['Todo']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan', # 회원이 삭제되면 그 회원의 todo들도 함께 자동 삭제
    )
