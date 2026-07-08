# LineWatch BE

LineWatch의 제조 품질 이벤트를 제공하는 FastAPI REST API입니다. 센서 이벤트와 검사 결과를 작업자용 품질 이벤트로 정규화하는 흐름을 구현했습니다.

## 주요 기능

- 로그인, refresh token, 로그아웃
- 생산 라인/설비/센서 이벤트 모델
- 품질 이벤트 목록, 상세, 상태 변경
- 센서 시계열 조회
- 이벤트 ingest API
- 로컬 검증용 seed 데이터

## 기술 스택

- FastAPI
- Tortoise ORM
- Python REST API
- SQLite local demo, PostgreSQL/TimescaleDB 확장 가능 구조

## 실행

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

OpenAPI:

```text
http://127.0.0.1:8000/docs
```

## 검증

```bash
python scripts/verify_api.py
```

## API

- `POST /api/v1/auth/signin`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/lines`
- `GET /api/v1/quality-events`
- `GET /api/v1/quality-events/{id}`
- `PATCH /api/v1/quality-events/{id}/status`
- `POST /api/v1/events/ingest`
- `GET /api/v1/machines/{id}/sensor-series`

## 포트폴리오 포인트

FastAPI와 Tortoise ORM으로 제조 도메인 모델을 빠르게 구성하고, refresh token 해시 저장과 device 단위 로그아웃을 포함했습니다. REST API만 사용합니다.
