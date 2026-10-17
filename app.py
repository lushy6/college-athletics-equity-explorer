"""Read-only local explorer for one EADA collection year."""

import os
from pathlib import Path
import sqlite3
from contextlib import closing

import streamlit as st

from athletics_etl.metrics import compare_peers


st.set_page_config(page_title="College athletics equity explorer", layout="wide")
st.title("College athletics participation explorer")
st.markdown(
    "Compare reported participation and **game-day operating expenses** by school and sport. "
    "These survey figures are not total athletics spending or a Title IX compliance score."
)
db = Path(os.getenv("EADA_DB_PATH", "data/processed/eada.sqlite"))
if not db.is_file():
    st.info("Build the local database first: `uv run python -m athletics_etl.cli import ...`")
    st.stop()

with closing(sqlite3.connect(db)) as connection:
    years = [row[0] for row in connection.execute("SELECT DISTINCT year FROM eada ORDER BY year DESC")]
    institutions = connection.execute(
        "SELECT DISTINCT institution_id, institution_name FROM eada ORDER BY institution_name, institution_id"
    ).fetchall()
    sports = connection.execute(
        "SELECT DISTINCT sport_code, sport_name FROM eada ORDER BY sport_name, sport_code"
    ).fetchall()

if not years:
    st.info("The database has no accepted records. Import a valid EADA collection or the synthetic fixture first.")
    st.stop()

year = st.selectbox("Collection year", years)
institution = st.selectbox(
    "Institution", institutions, format_func=lambda row: f"{row[1]} ({row[0]})"
)
sport = st.selectbox("Sport", sports, format_func=lambda row: f"{row[1]} ({row[0]})")
all_rows = compare_peers(db, year=year, sport_code=sport[0])
selected = [row for row in all_rows if row.institution_id == institution[0]]
if not selected:
    st.warning("This institution has no row for the selected sport and year.")
    st.stop()


def show_number(cell):
    return str(cell.value) if cell.value is not None else f"{cell.status} (raw: {cell.raw or 'empty'})"


st.subheader("Selected institution")
for row in selected:
    st.markdown(f"### {row.category.title()}")
    st.write(f"Participants: {show_number(row.participants)}")
    st.write(f"Game-day team operating expenses: {show_number(row.team_expenses)}")
    if row.calculated_per_participant is None:
        st.write(f"Calculated per participant: undefined — {row.undefined_reason}")
    else:
        st.write(f"Calculated per participant: ${row.calculated_per_participant:,.2f}")
    st.write(f"Source-reported per participant: {show_number(row.reported_per_participant)}")
    st.markdown(f"**Source:** `{row.source_file}`, workbook row {row.source_row}; "
                f"year {row.year}, sport code {row.sport_code}, category {row.category}.")

st.subheader("Peers in the same collection year and sport")
states = sorted({row.state for row in all_rows if row.state})
divisions = sorted({row.division for row in all_rows if row.division})
types = sorted({row.institution_type for row in all_rows if row.institution_type})
state = st.selectbox("State", ["All", *states])
division = st.selectbox("Division", ["All", *divisions])
institution_type = st.selectbox("Institution type", ["All", *types])
peers = compare_peers(
    db, year=year, sport_code=sport[0],
    state=None if state == "All" else state,
    division=None if division == "All" else division,
    institution_type=None if institution_type == "All" else institution_type,
)
st.caption(f"{len({row.institution_id for row in peers})} institutions in this filtered view")
st.dataframe([
    {
        "Institution": row.institution_name, "ID": row.institution_id,
        "Category": row.category, "Participants": show_number(row.participants),
        "Team expenses": show_number(row.team_expenses),
        "Calculated per participant": (
            f"${row.calculated_per_participant:,.2f}"
            if row.calculated_per_participant is not None else f"undefined: {row.undefined_reason}"
        ),
        "Source": f"{row.source_file}:{row.source_row}",
    }
    for row in peers
], hide_index=True)
st.caption("A peer row is one reported category. Missing peer attributes are excluded when that filter is selected.")
