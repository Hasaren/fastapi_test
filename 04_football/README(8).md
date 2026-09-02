# 🏈 Sports World Central 판타지 풋볼 API

> 선수·주간 성적·리그·팀 데이터를 PostgreSQL에 관계형으로 저장하고, 필터·페이지네이션·중첩 관계 응답을 제공하는 FastAPI 기반 읽기 전용 API입니다.

## 1. 프로젝트 개요

판타지 풋볼 데이터를 단순 CSV 목록으로 조회하는 데서 나아가, 선수와 성적의 1:N 관계, 리그와 팀의 1:N 관계, 팀과 선수의 N:M 관계를 SQLAlchemy ORM으로 모델링했습니다. FastAPI에서는 선수·성적·리그·팀 조회와 전체 건수 API를 제공하고, Swagger UI에서 각 경로와 매개변수를 이해할 수 있도록 OpenAPI 설명을 작성했습니다.

| 구분 | 내용 |
| --- | --- |
| 프로젝트 유형 | PostgreSQL 기반 판타지 풋볼 조회 API |
| API 버전 | `0.1.1` |
| 주요 기술 | Python, FastAPI, Pydantic, SQLAlchemy 2.0, PostgreSQL, pytest |
| 데이터 구성 | 선수, 주간 성적, 리그, 팀, 팀–선수 연결 |
| 제공 기능 | 조건 검색, 날짜 기반 증분 조회, 페이지네이션, 관계 데이터 포함 응답, 건수 집계 |
| 테스트 구성 | CRUD 테스트 13개, API 테스트 11개 |

현재 구현은 **GET 기반 읽기 전용 API**입니다. 사용자 인증, 판타지 팀 생성·수정, 선수 영입·방출, 점수 계산 규칙 및 외부 NFL 데이터 실시간 동기화는 포함되어 있지 않습니다.

## 2. 핵심 기능

### 선수 조회

- 전체 선수 목록을 `skip`, `limit`으로 나누어 조회
- 이름과 성의 정확한 문자열 일치 검색
- `minimum_last_changed_date` 이상으로 변경된 선수만 조회
- `player_id`로 단건 조회하고 없는 경우 HTTP 404 반환
- 단건·목록 응답에 선수별 성적 목록 포함

### 주간 성적 조회

- 여러 선수의 주간 성적 목록 조회
- `skip`, `limit` 페이지네이션
- 변경일 기준 증분 조회
- 선수 ID, 주차, 판타지 포인트 및 마지막 변경일 반환

### 리그·팀 조회

- 리그 목록과 리그 단건 조회
- 리그 이름과 변경일 필터
- 리그 응답에 소속 팀 목록 포함
- 팀 이름·리그 ID·변경일 필터
- 팀 응답에 소속 선수 목록 포함

### 집계 API

리그·팀·선수 전체 건수를 한 번에 반환하여 대시보드 요약이나 페이지네이션 범위 확인에 활용할 수 있습니다.

## 3. API 목록

| Method | 경로 | 주요 매개변수 | 응답 |
| --- | --- | --- | --- |
| GET | `/` | 없음 | API 상태 메시지 |
| GET | `/v0/players/` | `skip`, `limit`, `minimum_last_changed_date`, `first_name`, `last_name` | 성적을 포함한 선수 목록 |
| GET | `/v0/players/{player_id}` | `player_id` | 성적을 포함한 선수 1명 |
| GET | `/v0/performances/` | `skip`, `limit`, `minimum_last_changed_date` | 주간 성적 목록 |
| GET | `/v0/leagues/` | `skip`, `limit`, `minimum_last_changed_date`, `league_name` | 팀 목록을 포함한 리그 목록 |
| GET | `/v0/leagues/{league_id}` | `league_id` | 팀 목록을 포함한 리그 1개 |
| GET | `/v0/teams/` | `skip`, `limit`, `minimum_last_changed_date`, `team_name`, `league_id` | 선수 목록을 포함한 팀 목록 |
| GET | `/v0/counts/` | 없음 | 리그·팀·선수 전체 건수 |

`minimum_last_changed_date` 조건은 코드에서 `>=`로 비교하므로 입력한 날짜 당일의 레코드도 포함합니다. 이름·팀명·리그명 필터는 부분 검색이나 대소문자 무시 검색이 아니라 정확히 일치하는 값을 조회합니다.

`skip`과 `limit`에는 설명과 기본값이 있지만 최소·최대 범위 제약은 별도로 지정되어 있지 않습니다. 조회 정렬 기준도 명시되어 있지 않으므로 안정적인 페이지네이션이 필요하면 `ORDER BY`와 매개변수 범위 검증을 추가해야 합니다.

## 4. 데이터 모델

```mermaid
erDiagram
    LEAGUE ||--o{ TEAM : contains
    TEAM ||--o{ TEAM_PLAYER : has
    PLAYER ||--o{ TEAM_PLAYER : joins
    PLAYER ||--o{ PERFORMANCE : records

    LEAGUE {
        int league_id PK
        string league_name
        string scoring_type
        date last_changed_date
    }
    TEAM {
        int team_id PK
        int league_id FK
        string team_name
        date last_changed_date
    }
    PLAYER {
        int player_id PK
        string gsis_id
        string first_name
        string last_name
        string position
        date last_changed_date
    }
    TEAM_PLAYER {
        int team_id PK,FK
        int player_id PK,FK
        date last_changed_date
    }
    PERFORMANCE {
        int performance_id PK
        int player_id FK
        string week_number
        float fantasy_points
        date last_changed_date
    }
```

### 관계 설계

| 관계 | 구현 |
| --- | --- |
| 리그 1 : N 팀 | `Team.league_id` 외래키와 양방향 `relationship` |
| 선수 1 : N 성적 | `Performance.player_id` 외래키와 양방향 `relationship` |
| 팀 N : M 선수 | `TeamPlayer` 연결 모델과 복합 기본키 |

`TeamPlayer`는 단순 연결 테이블이 아니라 `last_changed_date`를 가진 Association Object입니다. `association_proxy`를 사용해 `team.players`와 `player.teams`처럼 중간 모델을 거치지 않고 관계 객체에 접근할 수 있도록 구성했습니다.

Player 또는 Team에서 연결 관계가 제거되면 관련 `TeamPlayer`가 정리되도록 `delete-orphan` cascade를 사용합니다. DB 외래키의 `ON DELETE CASCADE`를 지정한 구성은 아니므로 ORM 외부에서 삭제할 때의 동작은 별도로 확인해야 합니다.

## 5. 관계 데이터 조회 전략

응답 직렬화 시 관계별 추가 쿼리가 반복되는 N+1 문제를 줄이기 위해 조회 특성에 따라 로딩 전략을 구분했습니다.

| 대상 | 로딩 전략 | 적용 이유 |
| --- | --- | --- |
| 리그 목록 → 팀 | `joinedload` | 리그와 소속 팀을 JOIN으로 함께 조회 |
| 팀 목록 → TeamPlayer | `selectinload` | 팀 목록 조회 후 연결 행을 별도 IN 쿼리로 일괄 조회 |
| TeamPlayer → 선수 | 체이닝한 `joinedload` | 연결 행을 조회하는 쿼리에서 선수도 함께 로드 |

리그 목록의 JOIN 결과에서 같은 리그 객체가 중복되는 문제는 `unique()`로 정리합니다. 실제 쿼리 수나 응답 시간의 개선 효과는 측정 자료가 없으므로 성능 향상 수치를 주장하지 않습니다.

선수 목록의 `performances` 관계에는 명시적인 eager loading 옵션이 없습니다. 여러 선수 응답을 직렬화할 때 추가 쿼리가 발생할 수 있으므로 쿼리 로그나 프로파일링으로 확인할 필요가 있습니다.

## 6. 제공 데이터 분석

CSV 5개를 직접 확인한 결과입니다.

| 파일 | 행 수 | 주요 컬럼 | 날짜 범위 |
| --- | ---: | --- | --- |
| `player_data.csv` | 1,018 | 선수 ID, GSIS ID, 이름, 성, 포지션, 변경일 | 2024-04-18 |
| `league_data.csv` | 5 | 리그 ID, 이름, 득점 방식, 변경일 | 2024-04-25 |
| `team_data.csv` | 20 | 팀 ID, 이름, 리그 ID, 변경일 | 2024-04-23 |
| `team_player_data.csv` | 140 | 팀 ID, 선수 ID, 변경일 | 2024-04-17 |
| `performance_data.csv` | 17,306 | 성적 ID, 주차, 포인트, 선수 ID, 변경일 | 2024-03-01 ~ 2024-05-30 |

### 데이터 점검 결과

| 점검 항목 | 결과 |
| --- | ---: |
| 완전히 동일한 중복 행 | 0건 |
| 빈 셀 | 0건 |
| 존재하지 않는 리그를 참조하는 팀 | 0건 |
| 존재하지 않는 선수를 참조하는 성적 | 0건 |
| 존재하지 않는 팀·선수를 참조하는 연결 행 | 0건 |

### 선수 포지션 구성

| 포지션 | 선수 수 |
| --- | ---: |
| WR | 415 |
| RB | 229 |
| TE | 206 |
| QB | 123 |
| K | 45 |
| **합계** | **1,018** |

판타지 포인트는 제공 데이터에서 최소 1.0, 최대 25.0이며 전체 합계는 225,313.0입니다. 이 수치는 데이터 파일의 기술적 확인 결과로, 시즌 성과나 리그 순위를 분석한 결과는 아닙니다.

## 7. 초기 데이터 적재

`seed_postgres_basic.py`는 다음 순서로 PostgreSQL에 데이터를 넣습니다.

```mermaid
flowchart LR
    P["Player"] --> TP["TeamPlayer"]
    P --> PF["Performance"]
    L["League"] --> T["Team"]
    T --> TP
```

실제 적재 순서는 다음과 같습니다.

1. 기존 ORM 테이블 삭제 후 재생성
2. Player와 League 추가 후 `flush()`
3. Team 추가 후 `flush()`
4. TeamPlayer와 Performance 추가
5. 전체 트랜잭션 커밋

부모 데이터를 먼저 flush하여 같은 트랜잭션 안에서 후속 외래키가 참조할 수 있게 합니다. CSV의 날짜 문자열은 `date.fromisoformat()`으로 변환하고 ID·점수도 모델 타입에 맞게 변환합니다.

> ⚠️ **주의:** 초기화 스크립트는 `Base.metadata.drop_all()`을 실행합니다. 연결된 DB의 해당 테이블과 기존 데이터를 삭제하므로 반드시 실습용·초기화 대상 DB인지 확인한 뒤 실행해야 합니다. 삭제된 데이터는 별도 백업 없이는 복구할 수 없습니다.

## 8. 프로젝트 구조

업로드 파일의 `(1)`, `(5)`, `(6)`, `(8)` 등의 접미사를 제거하고 다음과 같이 배치합니다.

```text
football/
├── data/
│   ├── league_data.csv
│   ├── performance_data.csv
│   ├── player_data.csv
│   ├── team_data.csv
│   └── team_player_data.csv
├── crud.py
├── database.py
├── main.py
├── models.py
├── schemas.py
├── seed_postgres_basic.py
├── test_crud.py
└── test_main.py
```

| 파일 | 역할 |
| --- | --- |
| `database.py` | DB URL, Engine, 세션 팩토리, SQLAlchemy Base |
| `models.py` | 5개 ORM 모델과 관계 정의 |
| `schemas.py` | Pydantic 응답 모델과 중첩 응답 구조 |
| `crud.py` | 필터·페이지네이션·관계 로딩·집계 조회 함수 |
| `main.py` | FastAPI 엔드포인트와 OpenAPI 문서 설정 |
| `seed_postgres_basic.py` | CSV를 PostgreSQL에 초기 적재 |
| `test_crud.py` | DB 조회 함수 테스트 13개 |
| `test_main.py` | TestClient 기반 HTTP API 테스트 11개 |

## 9. 실행 방법

### 1. 환경 준비

Python 3.10 이상과 PostgreSQL을 준비합니다. 제공 자료에는 의존성 버전 파일이 포함되어 있지 않으므로 아래는 설치 예시입니다.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi "uvicorn[standard]" sqlalchemy psycopg2-binary pydantic pytest httpx
```

macOS·Linux:

```bash
source .venv/bin/activate
python -m pip install fastapi "uvicorn[standard]" sqlalchemy psycopg2-binary pydantic pytest httpx
```

`fastapi.testclient.TestClient` 실행에는 사용 중인 FastAPI·Starlette와 호환되는 `httpx` 버전이 필요합니다. 실제 확인한 패키지 버전을 `requirements.txt` 또는 `pyproject.toml`에 고정하는 것이 좋습니다.

### 2. DB 연결 설정

코드는 `DATABASE_URL` 환경변수를 우선 사용합니다. 설정하지 않으면 소스에 지정된 로컬 기본 연결 문자열을 사용합니다. 공개 전 기본 자격증명을 제거하고 환경변수를 필수화하는 것이 안전합니다.

예시 형식:

```text
postgresql://USER:PASSWORD@HOST:5432/DB_NAME
```

Windows PowerShell:

```powershell
$env:DATABASE_URL = "postgresql://USER:PASSWORD@HOST:5432/DB_NAME"
```

macOS·Linux:

```bash
export DATABASE_URL='postgresql://USER:PASSWORD@HOST:5432/DB_NAME'
```

DB 자체는 미리 생성되어 있어야 하며, 초기 적재 계정에는 테이블 삭제·생성·삽입 권한이 필요합니다.

### 3. 초기 데이터 적재

데이터가 삭제되어도 되는 대상 DB인지 다시 확인한 뒤 프로젝트 루트에서 실행합니다.

```bash
python seed_postgres_basic.py
```

정상 완료 시 테이블별 적재 건수를 출력합니다.

### 4. API 실행

```bash
uvicorn main:app --reload
```

| 문서 | 주소 |
| --- | --- |
| Swagger UI | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| ReDoc | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) |

### 5. 테스트 실행

테스트는 임시 DB나 mock이 아니라 `DATABASE_URL`이 가리키는 PostgreSQL의 seed 데이터를 조회합니다. 먼저 초기 적재를 완료한 뒤 실행합니다.

```bash
pytest -v
```

테스트가 데이터를 수정하지는 않지만 운영 DB와 분리된 테스트 DB 사용을 권장합니다.

## 10. 테스트 범위

| 구분 | 테스트 수 | 확인 내용 |
| --- | ---: | --- |
| CRUD | 13 | 단건·목록, 이름·날짜·리그 필터, 관계 탐색, 전체 건수 |
| API | 11 | 상태코드, 응답 개수·구조, 경로·쿼리 매개변수, 중첩 팀 목록 |
| **합계** | **24** | DB 조회와 HTTP 계층 |

테스트는 seed 데이터의 정확한 건수와 특정 ID를 기준으로 하므로 데이터셋이 달라지면 기대값도 수정해야 합니다. 각 테스트마다 DB 세션을 새로 열어 닫지만, 트랜잭션 롤백으로 DB 상태를 격리하는 fixture는 아닙니다.

이번 README 작성 과정에서는 소스 문법과 CSV 구조·행 수·외래키 참조를 확인했습니다. PostgreSQL 서버를 연결하지 않았으므로 24개 테스트의 실제 통과 여부는 검증하지 않았습니다.

## 11. 기술적 설계 포인트

| 설계 요소 | 적용 내용 |
| --- | --- |
| ORM 관계 모델링 | 1:N과 N:M 관계를 타입이 지정된 SQLAlchemy 2.0 모델로 표현 |
| Association Object | 연결 시점 정보를 가진 TeamPlayer를 독립 모델로 관리 |
| 응답 모델 분리 | ORM 테이블과 외부 JSON 구조를 Pydantic 모델로 구분 |
| 중첩 직렬화 | 선수–성적, 리그–팀, 팀–선수 관계를 응답에 포함 |
| 조회 조건 | 페이지네이션, 변경일, 이름, 리그 ID 필터 제공 |
| 관계 로딩 | `joinedload`, `selectinload`, `unique()`를 조회 구조에 맞게 적용 |
| API 문서화 | 제목·설명·태그·operation ID·매개변수 설명 구성 |
| 자동 테스트 | CRUD 계층과 HTTP 계층을 분리해 기대 데이터 검증 |

## 12. 현재 한계와 개선 방향

| 현재 상태 | 개선 방향 |
| --- | --- |
| 읽기 전용 기능 | 요구사항에 따라 생성·수정·삭제 API와 입력 스키마 추가 |
| 기본 DB URL에 자격증명 포함 | 기본값 제거, 환경변수·비밀 관리 적용 및 노출된 값 교체 |
| 데이터 전체 삭제 방식의 seed | 테스트 DB 전용 보호 장치, upsert 또는 마이그레이션 기반 적재 추가 |
| 페이지네이션 정렬 없음 | 기본키 등 고정 정렬과 `skip`·`limit` 범위 제한 적용 |
| 선수 목록의 성적 관계 로딩 미지정 | SQL 로그·프로파일링 후 `selectinload` 적용 검토 |
| 성적 API의 선수 필터 없음 | `player_id`, 주차 등 실사용 조회 조건 추가 |
| TeamPlayer 날짜가 API 응답에 없음 | 팀 가입 이력이 필요하면 전용 응답 스키마와 엔드포인트 제공 |
| 테스트가 실제 seed DB에 결합 | 테스트 전용 DB·트랜잭션 롤백 fixture 또는 컨테이너 환경 구성 |
| DB 스키마 버전 관리 없음 | Alembic을 이용한 마이그레이션 도입 |
| 오류·운영 설정 부족 | DB 예외 처리, 구조화 로그, 헬스체크와 배포 설정 추가 |

## 13. 검증 범위와 포트폴리오 보완

이 README는 제공된 8개 Python 파일과 CSV 5개를 기준으로 작성했습니다. 데이터 행 수, 빈 셀, 동일 행 중복, 외래키 참조, 포지션 구성과 포인트 범위를 직접 확인했습니다. API 서버 실행, 실제 DB 적재, Swagger 렌더링 및 pytest 실행은 수행하지 않았습니다.

포트폴리오에는 다음 자료를 추가하면 구현 결과와 본인 기여가 더 명확해집니다.

- 프로젝트 진행 기간, 참여 인원과 본인 담당 범위
- 데이터 출처와 사용 조건
- ERD 및 Swagger UI 실행 화면
- `pytest -v` 전체 통과 결과
- eager loading 전후 SQL 쿼리 수나 응답 시간 비교
- 테스트 DB 구성과 패키지 버전

---

**프로젝트 요약:** 판타지 풋볼의 선수·성적·리그·팀 관계를 SQLAlchemy 2.0으로 모델링하고, 필터·페이지네이션·관계 데이터 응답·OpenAPI 문서·자동 테스트를 구성한 PostgreSQL 기반 읽기 전용 FastAPI 서비스입니다.
