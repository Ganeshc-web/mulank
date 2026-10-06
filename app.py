from datetime import date

import pandas as pd
import streamlit as st

from luck_engine import (PROFILES, caution_for, check_number, daily, lun_matrix, mulank, relation,
                         week_rows, worked_out)
from ui_helpers import swatch_html

st.set_page_config(page_title="Mulank", layout="wide")


@st.cache_data
def _week_table(mulank_n: int, start: date) -> pd.DataFrame:
    return pd.DataFrame(week_rows(mulank_n, start))


# --- Sidebar: wide DOB range (Streamlit defaults to only today +/- 10 years) ---
dob = st.sidebar.date_input("DOB", value=date(1990, 7, 3),
                            min_value=date(1900, 1, 1), max_value=date.today(),
                            format="DD/MM/YYYY")
check_day = st.sidebar.date_input("Date to check (blank = today)", value=None,
                                  min_value=date(1900, 1, 1), max_value=date(2100, 12, 31),
                                  format="DD/MM/YYYY")

if dob is None:                                    # user cleared the box
    st.info("Enter a date of birth in the sidebar.")
    st.stop()

m = mulank(dob)
profile = PROFILES[m]
hit = daily(m, check_day)                          # None -> today (handled in engine)

_BADGE = {"Lucky": "🟢", "Neutral": "🟡", "Unlucky": "🔴"}
_CELL = {"L": "#c8e6c9", "N": "#eeeeee", "U": "#ffcdd2"}

c1, c2, c3 = st.columns(3)
c1.metric("Mulank", f"{m} · {profile['planet']}")
c2.metric("Date", hit.day.strftime("%d %b %Y"), hit.weekday, delta_color="off")
c3.metric("Rating", f"{_BADGE[hit.rating]} {hit.rating}", f"score {hit.score:+d}", delta_color="off")

tab_daily, tab_week, tab_profile, tab_check = st.tabs(["Daily", "Next 7 days", "Profile", "Number checker"])

with tab_daily:
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Lucky number", hit.lucky_number)
    with d2:
        st.metric("Colour", hit.lucky_colour)
        st.markdown(swatch_html(hit.lucky_colour), unsafe_allow_html=True)
    d3.metric("Weekday no.", f"{hit.weekday_no} ({relation(m, hit.weekday_no)})")
    d4.metric("Date no.", f"{hit.date_no} ({relation(m, hit.date_no)})")
    if (warning := caution_for(hit)):
        st.warning(warning)
    with st.expander("How it was worked out"):
        st.write(worked_out(hit))

with tab_week:
    st.dataframe(_week_table(m, hit.day), hide_index=True)

with tab_profile:
    a, b = st.columns(2)
    with a:
        st.subheader("Lucky")
        st.write("Numbers:", ", ".join(map(str, profile["lucky"])))
        st.markdown(swatch_html(profile["lc"]), unsafe_allow_html=True)
    with b:
        st.subheader("Unlucky")
        st.write("Numbers:", ", ".join(map(str, profile["unlucky"])) or "None hostile")
        st.markdown(swatch_html(profile["uc"]), unsafe_allow_html=True)
    grid = pd.DataFrame(lun_matrix(), index=range(1, 10), columns=range(1, 10))
    grid.index.name = "Mulank ↓ / Number →"
    st.dataframe(grid.style.map(lambda v: f"background-color: {_CELL[v]}"))

with tab_check:
    value = st.number_input("Any number (house no., phone total...)", min_value=1, step=1, value=15)
    reduced, tag = check_number(m, int(value))
    st.write(f"{value} reduces to {reduced} → **{tag}** for Mulank {m}")
    left, right = st.columns(2)
    ma = left.selectbox("Mulank A", range(1, 10), index=m - 1)
    mb = right.selectbox("Mulank B", range(1, 10), index=0)
    st.write(f"Mulank {ma} vs Mulank {mb} → **{relation(int(ma), int(mb))}**")
