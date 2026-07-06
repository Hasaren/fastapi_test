# system/loader.py

# 수집한 결과로 나온 파일 subway_long.csv 를
# 테이블에 적재

import os
import pandas as pd
from sqlalchemy.dialects.postgresql import insert as pg_insert
from database import engine
from models import SubwayRaw

# 경로 설정 및 기본값 설정

# 경로 설정 + DB URL 연결

BASE_DIR = os.getcwd()
INPUT_PATH = os.path.join(BASE_DIR,'input','subway_long.csv')
CHUNK_SIZE = 5000

# CSV -> DB 배치 적재

# 주말 여부 --> 주말이다/아니다
# 파이썬은 bool("False") --> 파이썬 입장에서는 비어있지 않아서 참

# 이런 문제를 예방하기 위하여 딕셔너리로 명시적 변환

WEEKEND_MAP = {
    True: True, False: False, # 이미 파이썬 bool 자료형인 경우
    "True": True, "False": False, # 문자열인 경우
    "TRUE": True, "FALSE": False, # 대문자인 경우
    "true": True, "false": False, # 소문자인 경우
    "1": True, "0":False, # 문자열 정수인 경우
    1:True, 0:False # 정수인 경우
}

# 함수 이름에 _가 붙어있다면
# 내부에서만 쓰는 헬퍼 함수
def _to_bool(value):
    """
    WEEKEND_MAP에 없는 값이 들어오면 에러를 내지 않고 False를 내보낸다.
    """
    return WEEKEND_MAP.get(value, False)

def _prepare_chunk(chunk: pd.DataFrame) -> list[dict]:
    """
    pandas로 읽어온 csv 를 DB에 바로 넣을 수 있는 딕셔너리 리스트 형태로 가공
    """

    chunk = chunk.copy() # 원본 chunk를 직접 건드리면 pandas에서 경고

    chunk['날짜'] = pd.to_datetime(chunk['날짜'], errors='coerce').dt.date
    chunk['주말여부'] = chunk['주말여부'].map(_to_bool)

    chunk = chunk.dropna(subset=['역번호', '날짜','시간대컬럼','승하차'])

    # 필요한 컬럼만 순서대로 골라, DB 삽입에 사용할 수 있는 딕셔너리 리스트로 변환
    return chunk[[
        '월','일','역번호','역명','승하차','시간대컬럼','인원수','시작시','날짜','요일코드','주말여부'
    ]].to_dict(orient='records')


# 함수정의
def load_from_csv(path: str=INPUT_PATH, chunksize: int=CHUNK_SIZE) -> dict:
    """
    CSV 파일을 배치 단위로 읽어 subway_raw 테이블에 적재하는 메인 함수
    """
    # 전체 적재 결과를 누적할 카운터들
    total_success = 0 # 새로 삽입된 건수
    total_skipped = 0 # UNIQUE 제약에 걸러 중복으로 스킵된 건수
    total_failed = 0 # 배치 자체가 에러로 실패한 건수
    
    for i, chunk in enumerate(pd.read_csv(INPUT_PATH, encoding='utf-8-sig', chunksize=CHUNK_SIZE)):
        try:
            # 이번 배치를 DB 삽입용 딕셔너리 리스트로 가공
            records = _prepare_chunk(chunk) # 함수 호출

            # 가공 후 남은 데이터가 없다면 이번 배치는 건너뛴다.
            if not records:
                continue

            with engine.begin() as conn:
                # PostgreSQL 전용 insert 구문 생성
                stmt = pg_insert(SubwayRaw).values(records)

                # UNIQUE 제약 위반 -> 에러 안내고 무시
                stmt = stmt.on_conflict_do_nothing(constraint='uq_subway_raw_key')

                # 실제 sql 실행
                result = conn.execute(stmt)

            # rowcount : 실제로 삽입된 행의 개수 (충돌로 스킵된 행은 포함하지 않는다.)
            inserted = result.rowcount if result.rowcount is not None else 0

            # 중복관련
            skipped = len(records) - inserted

            total_success += inserted
            total_skipped += skipped

            print(f'{i+1}번째 배치 - 신규 {inserted} / 중복 {skipped}')

        except Exception as e:
            # 예상치 못한 에러
            total_failed += len(chunk)
            print(f'{i+1}번째 배치 실패 : {e}')


    # 전체 배치 처리가 끝난 후 결과 요약
    # print(f'적재 완료 - 신규: {total_success:,} / 중복: {total_skipped:,} / 실패: {total_failed:,}')

    summary = {
        "success":total_success,
        "skipped_duplicate": total_skipped,
        "failed": total_failed
    }

    print(f'[loader] 전체 적재 완료 - 신규: {total_success:,} 중복: {total_skipped:,} 실패: {total_failed:,}')

    return summary

# 이 파일을 직접 실행 했을 때만 (python loader.py)
if __name__ == '__main__':
    load_from_csv()