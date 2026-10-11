from pathlib import Path

from athletics_etl.build_db import build_database
from athletics_etl.import_eada import import_year
from athletics_etl.metrics import compare_peers


FIXTURE = Path(__file__).parent / "fixtures" / "eada_synthetic.csv"


def test_comparison_keeps_numerator_denominator_status_and_source(tmp_path):
    db = tmp_path / "eada.sqlite"
    report = build_database(import_year(FIXTURE, 2024), db)
    assert (report.source_rows, report.normalized_rows, report.rejected_rows) == (5, 6, 2)
    assert report.institutions == 3

    rows = compare_peers(db, year=2024, sport_code="2", state="AL")
    assert len(rows) == 4
    first = next(r for r in rows if r.institution_id == "100001" and r.category == "men")
    assert (first.participants.value, first.team_expenses.value) == (10, 1000)
    assert (first.calculated_per_participant, first.undefined_reason) == (100, None)
    assert (first.source_file, first.source_row) == (FIXTURE.name, 2)

    zero = next(r for r in rows if r.institution_id == "100002" and r.category == "men")
    blank = next(r for r in rows if r.institution_id == "100002" and r.category == "women")
    assert (zero.calculated_per_participant, zero.undefined_reason) == (
        None, "zero participants"
    )
    assert (blank.calculated_per_participant, blank.undefined_reason) == (
        None, "participants blank"
    )

    assert len(compare_peers(db, year=2024, sport_code="2", state="GA")) == 2
    assert compare_peers(db, year=2024, sport_code="2", division="missing") == []


def test_repeat_build_is_deterministic_and_replaces_snapshot(tmp_path):
    db = tmp_path / "eada.sqlite"
    result = import_year(FIXTURE, 2024)
    report_a = build_database(result, db)
    first_bytes = db.read_bytes()
    report_b = build_database(result, db)
    assert report_a == report_b
    assert db.read_bytes() == first_bytes
