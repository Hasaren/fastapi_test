# =============================================================
# database/db_connection.py
# 
# 역할 : PostgreSQL DB 연결 설정
#      - 연결 문자열(DATABASE_URL) 정의
#          --> 형식
#              postgresql+psycopg2://유저명:비밀번호@호스트:호스트번호/DB이름
#      - 엔진(engine) 생성
#          --> 엔진 : 데이터베이스와의 실제 연결을 관리하는 객체
#      - 세션 팩토리(SessionFactory) 생성
#          --> 세션 : ORM이 데이터베이스와 상호작용할 때 사용하는 작업 단위
#      - 흐름 : 1. 엔진을 생성하고, 그 엔진을 기반으로 세션을 생성한다.
#               2. 세션을 통해 데이터를 생성, 조회, 수정, 삭제하며, 이 과정에서 발생하는 모든 변경사항을 세션이 관리한다.
# ============================================================== 


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost:5432/tododb"

# 엔진 생성
# echo=True --> 실행되는 SQL을 터미널에 출력 (디버깅용)
# 실무:False 수업:True
engine = create_engine(DATABASE_URL, echo=True)

# 세션 팩토리 생성
SessionFactory = sessionmaker(
    autocommit= False, # sesstion.commit()을 직접 호출해야 DB에 반영
    autoflush=False, # flush : 커밋 전에 SQL을 실행하는 중간 단계
    expire_on_commit=False, # 커밋 후에도 데이터가 메모리에 유지된다. (True라면 db다시 조회 필요)
    bind=engine, # 위에서 만든 엔진과 세션을 연결
)

# get_session() : FastAPI Depends()를 주입해서 사용하는 세션 의존성 함수
# 최신 jwt버전에서 많이 사용한다.
# 패턴을 매 라우터마다 반복하지 않도록 함수 하나로 캡슐화 한 것 뿐이다.
def get_session():
    session = SessionFactory()
    # 함수 안에 yield가 있으면, yield 시점까지 실행한 뒤, 그 값(session)을
    # 라우터 함수의 매개변수로 전달한다. -> 라우터 함수 처리가 끝나면,
    # FastAPI가 yield 다음 줄(finally)을 실행해서 세션을 자동으로 닫아준다.
    # --> 언제 세션을 열고 언제 닫을지를 라우터마다 안써도 된다. (편리함)
    try:
        yield session
    finally:
        session.close()