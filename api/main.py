from datetime import date
from os import getenv
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from luck_engine import (
    CAUTIONARY_DAYS,
    PROFILES,
    check_number,
    daily,
    lun_matrix,
    mulank as mulank_of,
    relation,
    today,
    week,
    worked_out,
)

app = FastAPI(title="Mulank Luck API", version="1.0.0")

_origins = [o.strip() for o in getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


class Profile(BaseModel):
    mulank: int
    planet: str
    lucky_numbers: list[int]
    lucky_colours: list[str]
    unlucky_numbers: list[int]
    unlucky_colours: list[str]


class DailyOut(BaseModel):
    mulank: int
    date: date
    weekday: str
    weekday_no: int
    date_no: int
    lucky_number: int
    lucky_colour: str
    rating: Literal["Lucky", "Neutral", "Unlucky"]
    score: int
    cautionary: bool
    explanation: str


class CheckOut(BaseModel):
    mulank: int
    value: int
    reduced: int
    relation: Literal["L", "N", "U"]


class CompatibilityOut(BaseModel):
    a: int
    b: int
    relation: Literal["L", "N", "U"]


class TableOut(BaseModel):
    rows: list[list[str]]
    cautionary_days: list[int]


class HealthOut(BaseModel):
    status: str
    today_ist: date


def _person(
    dob: Annotated[date | None, Query()] = None,
    mulank: Annotated[int | None, Query(ge=1, le=9)] = None,
) -> int:
    if dob is None and mulank is None:
        raise HTTPException(status_code=422, detail="Provide exactly one of dob or mulank")
    if dob is not None and mulank is not None:
        raise HTTPException(status_code=422, detail="Provide exactly one of dob or mulank")
    if dob is not None:
        if dob < date(1900, 1, 1) or dob > today():
            raise HTTPException(status_code=422, detail="dob must be between 1900-01-01 and today")
        return mulank_of(dob)
    return mulank


Person = Annotated[int, Depends(_person)]


def _daily_out(m: int, hit) -> DailyOut:
    return DailyOut(
        mulank=m,
        date=hit.day,
        weekday=hit.weekday,
        weekday_no=hit.weekday_no,
        date_no=hit.date_no,
        lucky_number=hit.lucky_number,
        lucky_colour=hit.lucky_colour,
        rating=hit.rating,
        score=hit.score,
        cautionary=hit.cautionary,
        explanation=worked_out(hit),
    )


@app.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok", today_ist=today())


@app.get("/mulank", response_model=Profile)
def get_mulank(m: Person) -> Profile:
    p = PROFILES[m]
    return Profile(
        mulank=m,
        planet=p["planet"],
        lucky_numbers=list(p["lucky"]),
        lucky_colours=list(p["lc"]),
        unlucky_numbers=list(p["unlucky"]),
        unlucky_colours=list(p["uc"]),
    )


@app.get("/daily", response_model=DailyOut)
def get_daily(
    m: Person,
    date: Annotated[date | None, Query()] = None,
) -> DailyOut:
    return _daily_out(m, daily(m, date))


@app.get("/week", response_model=list[DailyOut])
def get_week(
    m: Person,
    date: Annotated[date | None, Query()] = None,
) -> list[DailyOut]:
    return [_daily_out(m, hit) for hit in week(m, date)]


@app.get("/check", response_model=CheckOut)
def get_check(
    m: Person,
    value: Annotated[int, Query(ge=1)],
) -> CheckOut:
    reduced, tag = check_number(m, value)
    return CheckOut(mulank=m, value=value, reduced=reduced, relation=tag)


@app.get("/compatibility", response_model=CompatibilityOut)
def get_compatibility(
    a: Annotated[int, Query(ge=1, le=9)],
    b: Annotated[int, Query(ge=1, le=9)],
) -> CompatibilityOut:
    return CompatibilityOut(a=a, b=b, relation=relation(a, b))


@app.get("/table", response_model=TableOut)
def get_table() -> TableOut:
    return TableOut(rows=lun_matrix(), cautionary_days=sorted(CAUTIONARY_DAYS))
