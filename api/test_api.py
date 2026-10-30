from datetime import date, timedelta

from fastapi.testclient import TestClient

from luck_engine import today
from main import app

client = TestClient(app)
DOB = "1990-07-03"

SOP_DAILY = {
    "2026-09-28": (3, "Violet", "Unlucky"),
    "2026-09-29": (9, "Red", "Neutral"),
    "2026-09-30": (3, "Light green", "Lucky"),
    "2026-10-01": (3, "Violet", "Lucky"),
    "2026-10-02": (6, "Light blue", "Lucky"),
    "2026-10-03": (3, "Violet", "Lucky"),
}


def test_sop_daily_week():
    for day, want in SOP_DAILY.items():
        r = client.get("/daily", params={"dob": DOB, "date": day})
        assert r.status_code == 200, r.text
        body = r.json()
        assert (body["lucky_number"], body["lucky_colour"], body["rating"]) == want


def test_daily_default_is_health_today():
    health = client.get("/health").json()
    daily = client.get("/daily", params={"dob": DOB}).json()
    assert daily["date"] == health["today_ist"]


def test_week_length():
    r = client.get("/week", params={"dob": DOB, "date": "2026-09-28"})
    assert r.status_code == 200
    assert len(r.json()) == 7


def test_table_rows():
    rows = client.get("/table").json()["rows"]
    assert "".join(rows[2]) == "NNLNLLNNL"
    assert "".join(rows[7]) == "UUNLLNNLU"


def test_check_and_compatibility():
    r = client.get("/check", params={"mulank": 3, "value": 15})
    assert r.status_code == 200
    assert r.json()["relation"] == "L"
    r = client.get("/compatibility", params={"a": 3, "b": 1})
    assert r.status_code == 200
    assert r.json()["relation"] == "N"


def test_422_identity_and_bounds():
    assert client.get("/daily").status_code == 422
    assert client.get("/daily", params={"dob": DOB, "mulank": 3}).status_code == 422
    future = (today() + timedelta(days=1)).isoformat()
    assert client.get("/daily", params={"dob": future}).status_code == 422
    assert client.get("/daily", params={"mulank": 10}).status_code == 422
    assert client.get("/check", params={"mulank": 3, "value": 0}).status_code == 422
