# system/pipeline.py
# 대구 지하철 csv 수집 데이터를 저장하는 파이프라인 통합 실행
#   --> 처리단계 지정

from database import init_db
from loader import load_from_csv
# 검증 함수 모듈

def main():
    print('1. 저장 구조 재설계 (기본키 + UNIQUE 제약 적용)')
    init_db()

    print()
    print('2. 결과(subway_long.csv) 배치 적재')
    load_from_csv()

    print()
    print('3. 검증 함수')

if __name__ == '__main__':
    main()