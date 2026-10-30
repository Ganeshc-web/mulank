# Mulank Luck API

Stateless FastAPI wrapper around `luck_engine.py`. No database. **"Today" is India time (Asia/Kolkata).**

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Tests: `pip install pytest httpx && pytest -q`

## Docker

```bash
docker build -t mulank-api .
docker run --rm -p 8000:8000 -e PORT=8000 -e CORS_ORIGINS=* mulank-api
```

## Env

| Variable | Default | Meaning |
|---|---|---|
| `PORT` | `8000` | Listen port (Docker `CMD`) |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins; methods GET only |

## Endpoints (all GET)

Identify a person with **exactly one** of `dob` (`YYYY-MM-DD`, 1900-01-01 … today IST) or `mulank` (1–9).

| Path | Example |
|---|---|
| `/health` | `GET /health` → `{"status":"ok","today_ist":"2026-10-30"}` |
| `/mulank` | `GET /mulank?dob=1990-07-03` |
| `/daily` | `GET /daily?dob=1990-07-03&date=2026-09-28` → lucky number 3, Violet, Unlucky |
| `/week` | `GET /week?mulank=3&date=2026-09-28` (7 days) |
| `/check` | `GET /check?mulank=3&value=15` |
| `/compatibility` | `GET /compatibility?a=3&b=1` |
| `/table` | `GET /table` |
