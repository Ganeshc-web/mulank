"""Pure-logic Mulank engine (no UI). Single source of truth: PROFILES."""
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

PROFILES = {
    1: dict(planet="Sun", lucky=(1, 4, 5), lc=("Gold", "Yellow", "Orange"), unlucky=(6, 8), uc=("Black", "Dark blue")),
    2: dict(planet="Moon", lucky=(2, 7, 5), lc=("White", "Cream", "Green"), unlucky=(8,), uc=("Black", "Dark blue")),
    3: dict(planet="Jupiter", lucky=(3, 6, 9, 5), lc=("Violet", "Purple", "Mauve"), unlucky=(), uc=("Black", "Dark grey")),
    4: dict(planet="Rahu", lucky=(4, 1, 8, 5), lc=("Electric blue", "Grey"), unlucky=(9,), uc=("Red", "Crimson")),
    5: dict(planet="Mercury", lucky=tuple(range(1, 10)), lc=("Light green", "White", "Light grey"), unlucky=(), uc=("Very dark shades",)),
    6: dict(planet="Venus", lucky=(6, 3, 9, 5), lc=("Light blue", "Pink", "White"), unlucky=(1,), uc=("Black", "Gold", "Orange")),
    7: dict(planet="Ketu", lucky=(7, 2, 5), lc=("Green", "White", "Pale yellow"), unlucky=(), uc=("Black", "Dark shades")),
    8: dict(planet="Saturn", lucky=(8, 4, 5), lc=("Dark blue", "Black", "Dark grey"), unlucky=(1, 2, 9), uc=("Red", "Orange", "Bright yellow")),
    9: dict(planet="Mars", lucky=(9, 3, 6, 5), lc=("Red", "Crimson", "Pink"), unlucky=(4, 8), uc=("Black", "Dark blue", "Grey")),
}
# index = date.weekday() (Mon=0) -> (name, planet, number)
WEEKDAYS = [("Monday", "Moon", 2), ("Tuesday", "Mars", 9), ("Wednesday", "Mercury", 5),
            ("Thursday", "Jupiter", 3), ("Friday", "Venus", 6), ("Saturday", "Saturn", 8), ("Sunday", "Sun", 1)]
CAUTIONARY_DAYS = {11, 12, 16, 18, 22, 26, 28, 29}
SCORE = {"L": 1, "N": 0, "U": -1}

IST = ZoneInfo("Asia/Kolkata")


def today() -> date:
    return datetime.now(IST).date()


def reduce(n: int) -> int:
    """Digital root: 28 -> 1, 29 -> 2, 9 -> 9."""
    n = abs(int(n))
    return 1 + (n - 1) % 9 if n else 0


def mulank(birth: date) -> int:
    return reduce(birth.day)


def relation(m: int, n: int) -> str:
    """L / N / U from Mulank m vs. single digit n (matches the SOP table)."""
    p = PROFILES[m]
    return "L" if n in p["lucky"] else "U" if n in p["unlucky"] else "N"


def check_number(m: int, value: int) -> tuple[int, str]:
    d = reduce(value)
    return d, relation(m, d)


@dataclass
class Daily:
    day: date
    weekday: str
    weekday_no: int
    date_no: int
    lucky_number: int
    lucky_colour: str
    rating: str
    score: int
    cautionary: bool


def daily(m: int, day: date | None = None) -> Daily:
    day = day or today()
    wd_name, _, wd = WEEKDAYS[day.weekday()]
    dn = reduce(day.day)
    p = PROFILES[m]
    pool = p["lucky"] if m == 5 else tuple(x for x in p["lucky"] if x != 5)
    number = wd if wd in pool else dn if dn in pool else m
    colour = PROFILES[wd]["lc"][0] if relation(m, wd) == "L" else p["lc"][0]
    caution = day.day in CAUTIONARY_DAYS
    score = SCORE[relation(m, dn)] + SCORE[relation(m, wd)] - caution
    rating = "Lucky" if score >= 1 else "Neutral" if score == 0 else "Unlucky"
    return Daily(day, wd_name, wd, dn, number, colour, rating, score, caution)


def worked_out(hit: Daily) -> str:
    return (
        f"{hit.weekday} (no. {hit.weekday_no}), date no. {hit.date_no}. "
        "Rule 1 (weekday no. -> date no. -> Mulank) "
        f"=> lucky number {hit.lucky_number}. "
        f"Rule 2 => colour {hit.lucky_colour}. "
        f"Rule 3 score {hit.score} => {hit.rating}"
        f"{'; cautionary day -1' if hit.cautionary else ''}."
    )


def lun_matrix() -> list[list[str]]:
    return [[relation(i, j) for j in range(1, 10)] for i in range(1, 10)]


def week(m: int, start: date | None = None) -> list[Daily]:
    start = start or today()
    return [daily(m, start + timedelta(days=i)) for i in range(7)]


if __name__ == "__main__":
    exp = {(2026, 9, 28): (3, "Violet", "Unlucky"), (2026, 9, 29): (9, "Red", "Neutral"),
           (2026, 9, 30): (3, "Light green", "Lucky"), (2026, 10, 1): (3, "Violet", "Lucky"),
           (2026, 10, 2): (6, "Light blue", "Lucky"), (2026, 10, 3): (3, "Violet", "Lucky")}
    assert mulank(date(1990, 7, 3)) == 3
    for ymd, want in exp.items():
        r = daily(3, date(*ymd)); got = (r.lucky_number, r.lucky_colour, r.rating)
        assert got == want, (ymd, got, want)
    for a in PROFILES:
        for b in PROFILES:
            assert relation(a, b) == relation(b, a), (a, b)
    SOP_TABLE = ["LNNLLUNUN", "NLNNLNLUN", "NNLNLLNNL", "LNNLLNNLU", "LLLLLLLLL",
                 "UNLNLLNNL", "NLNNLNLNN", "UUNLLNNLU", "NNLULLNUL"]
    for a, row in enumerate(SOP_TABLE, 1):
        assert "".join(relation(a, b) for b in range(1, 10)) == row, ("table row", a)
    print("All SOP checks passed")
