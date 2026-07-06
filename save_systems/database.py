# ==============================
# save_systems
# PostgreSQL 연결 및 세션 관리
# (DB subwaydb, pw 1234)
# 
# 
# 수집 과정에서 다 했는데 왜 다시 만드는가
# --> 원본은 임시 적재, 지금이 정식 저장 모델 설계 단계
# ==============================

# 라이브러리 불러오기
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# DB URL 연결
DB_URL = 'postgresql://postgres:1234@localhost:5432/subwaydb'

# PostgreSQL 과 연결할 엔진 생성
engine = create_engine(DB_URL, echo=False)

# 세션 팩토리 생성
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 테이블 재설계를 위한 함수 정의
def init_db(drop_existing:bool = True):
    """
    subway_raw 테이블을 초기화 하는 함수

    매개변수(파라미터)
    drop_existing : bool, 기본값 = True

        True = 기본 테이블을 먼저 삭제하고 새로 만든다.
        False = 기존 테이블이 있으면 두고 없을 때만 새로 만든다.

    """

    if drop_existing:
        Base.metadata.drop_all(bind=engine)
        print('[database] 기존 subway_raw테이블 삭제')

    Base.metadata.create_all(bind=engine)
    print('[database] subway_raw 테이블 준비 완료')


def get_session():
    """
    SubwayRaw 등 모델을 다루기 위한 새로운 세션을 하나 생성해서 반환
    실제로 사용 가능한 세션 객체가 생성되도록 한다.

    1. 호출부를 단순하게 유지
    2. 나중에 세션 생성 시 로깅을 추가하거나, 그 외 기능을 수정 및 추가할 때 get_session() 내부만 수정하면 된다.
    """

    return SessionLocal()