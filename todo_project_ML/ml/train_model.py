"""
ml/train_model.py
------------------
- Todo 제목 텍스트로 카테고리(업무/개인/긴급)를 분류하는 모델을 학습한다.
- FastAPI서버와 완전히 분리된 별도 스크립트 (서버 안에서 학습하지 않는다.)

- FastAPI 앱(main.py) 코드와 물리적으로 완전히 분리되어 있다.
    - 학습(train)과 서빙(serving)을 분리하는 것이 MLOps의 가장 기본이 되는 개념이다.
    - 학습은 몇 초~몇 분 씩 걸릴 수 있는 무거운 작업이라, 만약 API 요청 처리 흐름 안에 학습 코드를
        넣으면 그동안 서버 전체가 멈춰버린다.
"""
import json
from datetime import datetime
from pathlib import Path
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline

# __file__.resolve().parent : 이 스크립트가 어느 폴더에 있든 항상 스크립트 자신의 위치를 기준으로
#                             경로를 계산한다. (실행 위치에 흔들리지 않는다.)
BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / 'artifacts' # 학습 결과물(모델, 메타데이터)이 쌓이는 곳
DATA_PATH = BASE_DIR / 'sample_labeled_data.csv' # 학습에 사용할 원본 라벨 데이터

def load_data(csv_path: Path) -> pd.DataFrame:
    """
    csv 파일이 있는 경로를 읽어서 csv 파일을 판다스의 데이터프레임으로 반환

    - title이나 category중 하나라도 비어있는 행은 학습에서 제외
    """
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['title','category'])
    return df

def build_pipeline() -> Pipeline:
    """
    TfidVectorizer(텍스트 -> 숫자 벡터로 변환)
    로지스틱 회귀를 하나의 Pipeline객체로 묶는다.
    --> 왜 묶는가?
        서빙(FastAPI) 쪽에서 TfidVectorizer, 예측도 해야하고 단계를 직접 호출 해야 한다.
        두 객체를 각각 파일로 저장/로드 해야한다.
        파이프라인으로 묶으면 한 줄로 벡터화+분류가 한번에 처리되고, 저장/로드 도 파일 하나로 끝난다.
    
    TfidVectorizer(ngram_range(1, 2)) : 단어 하나(unigram)뿐 아니라 연속된 두 단어(bigram)까지
                                        특징으로 사용한다.
                                        ex) "회의 자료" --> "회의", "자료", "회의 자료"
                                        짧은 한국어 제목에서 문맥 정보를 조금 더 살릴 수 있다.
    """
    return Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1,2), max_df=1)),
        ('clf', LogisticRegression(max_iter=1000)),
    ])

def get_next_version(artifacts_dir: Path) -> int:
    """
    artifacts 폴더 안에 model_v1.pkl, ... 파일명을 스캔해서 다음에 저장할 버전 번호를 계산
    "파일명 + 숫자"만으로 최소한의 버전 관리를 구현한 가벼운 방식
    --> 버전이 쌓인다는 개념을 이해하기 좋은 예제
    """
    existing = list(artifacts_dir.glob('model_v*.pkl'))
    if not existing: # 학습한 압축 모델이 없다. --> 처음이므로 버전 1로 한다.
        return 1
    versions = [int(p.stem.split('_v')[-1]) for p in existing]
    return max(versions) + 1

def main():
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data(DATA_PATH)
    print(f'[INFO] 학습 데이터 {len(df)}건 로드 완료')
    print(df['category'].value_counts()) # 카테고리별 데이터 개수

    # 입력(피쳐, 독립변수) --> df['title']
    # 결과(타겟, 종속변수) --> df['category']
    # 전체 데이터를 "학습용" "평가용"으로 나눈다.
    X_train, X_test, y_train, y_test = train_test_split(
        df['title'],df['category'],test_size=0.2, random_state=42, stratify=df['category']
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train) # 학습

    # 학습에 사용되지 않은 X_test로 예측, 진짜 정답 y_test와 비교
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f'[INFO] 테스트 정확도: {accuracy:.3f}')

    # 카테고리별 정밀도 / 재현율 까지 자세히 보여준다.
    # 전체 정확도는 괜찮은데 특정 카테고리만 유독 잘 못 맞힌다 같은 문제를 여기서 발견할 수 있다.
    print(classification_report(y_test, y_pred))

    version = get_next_version(ARTIFACTS_DIR)
    model_path = ARTIFACTS_DIR / f'model_v{version}.pkl'

    # joblib.dump() : 학습된 파이썬 객체(pipeline)를 파일 그대로 저장
    #                 pickle과 비슷하지만, numpy 배열이 많은 sklearn 객체 저장에 더 최적화 되어 있다.
    joblib.dump(pipeline, model_path)

    # 모델 파일만 저장하면 "언제, 얼마나 정확했는지" 기록이 안남는다.
    # 최소한의 버전 관리로 메타데이터를 JSON으로 남긴다.
    metadata = {
        "version": version,
        "trained_at" : datetime.now().isoformat(timespec='seconds'),
        "n_samples": len(df),
        "accuracy": round(accuracy, 4),
        "categories": sorted(df['category'].unique().tolist()),
        "source_data": DATA_PATH.name,
    }
    metadata_path = ARTIFACTS_DIR / f'model_v{version}_metadata.json'
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # main.py 의 lifespan은 항상 'latest.pkl'이라는 고정된 이름만 찾는다.
    # 버전이 올라갈 때 마다 main.py코드를 수정할 필요없이, 이 파일 하나만 최신모델로 덮어쓰기하면
    # 서버가 자동으로 최신 버전을 로드하게 된다.
    latest_path = ARTIFACTS_DIR / 'latest.pkl'
    joblib.dump(pipeline, latest_path)

    print(f'[INFO] 모델 저장 완료: {model_path.name} (버전 {version})')
    print(f'[INFO] latest.pkl 갱신 완료 (FastAPI가 여기서 로드함)')


if __name__ == '__main__':
    main()
