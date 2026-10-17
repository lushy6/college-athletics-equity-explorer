from pathlib import Path

import pytest
from openpyxl import Workbook


FIXTURE = Path(__file__).parent / "fixtures" / "eada_synthetic.csv"


@pytest.mark.parametrize("change", ["extra", "missing"])
def test_irregular_csv_rows_are_rejected_instead_of_losing_columns(tmp_path, change):
    import csv
    from athletics_etl.import_eada import SchemaError, import_year

    with FIXTURE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    rows[1] = rows[1] + ["unexpected"] if change == "extra" else rows[1][:-1]
    path = tmp_path / "malformed.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows[:2])
    with pytest.raises(SchemaError, match="column count"):
        import_year(path, 2024)


def test_import_keeps_source_rows_and_distinguishes_numeric_states():
    from athletics_etl.import_eada import import_year

    result = import_year(FIXTURE, 2024)

    assert result.source_rows == 5
    assert len(result.records) == 6  # three accepted source rows, two categories each
    assert [(reject.source_row, reject.reason) for reject in result.rejects] == [
        (5, "duplicate institution/sport/year"),
        (6, "invalid institution ID"),
    ]
    men = next(r for r in result.records if r.institution_id == "100001" and r.category == "men")
    assert (men.source_file, men.source_row, men.sport_name) == (FIXTURE.name, 2, "Basketball")
    assert (men.participants.raw, men.participants.value, men.participants.status) == (
        "10", 10, "observed"
    )
    assert (men.team_expenses.raw, men.team_expenses.value) == ("1000", 1000)

    zero = next(r for r in result.records if r.institution_id == "100002" and r.category == "men")
    blank = next(r for r in result.records if r.institution_id == "100002" and r.category == "women")
    assert (zero.participants.value, zero.participants.status) == (0, "observed")
    assert (blank.participants.value, blank.participants.status) == (None, "blank")

    invalid = next(r for r in result.records if r.institution_id == "100003" and r.category == "men")
    assert (invalid.participants.value, invalid.participants.status) == (None, "invalid")
    assert (invalid.team_expenses.value, invalid.team_expenses.status) == (None, "suppressed")
    assert invalid.reported_per_participant.status == "undefined"


def test_missing_header_fails_before_import(tmp_path):
    from athletics_etl.import_eada import SchemaError, import_year

    path = tmp_path / "changed.csv"
    path.write_text("unitid,SPORTSCODE,PARTIC_MALE\n100001,2,10\n", encoding="utf-8")
    with pytest.raises(SchemaError, match="missing columns.*PARTIC_MEN"):
        import_year(path, 2024)


def test_xlsx_uses_the_same_field_contract_and_excel_row_numbers(tmp_path):
    from athletics_etl.import_eada import import_year

    path = tmp_path / "schools.xlsx"
    wb = Workbook()
    sheet = wb.active
    sheet.append(
        [
            "unitid", "institution_name", "state_cd", "classification_name", "sector_name",
            "SPORTSCODE", "Sports", "PARTIC_MEN", "PARTIC_WOMEN", "OPEXPPERPART_MEN",
            "OPEXPPERTEAM_MEN", "OPEXPPERPART_WOMEN", "OPEXPPERTEAM_WOMEN",
        ]
    )
    sheet.append([100001, "Example University", "AL", "Division I", "Public", 2, "Basketball", 10, 12, 100, 1000, 150, 1800])
    wb.save(path)

    result = import_year(path, 2024)
    assert result.rejects == []
    assert len(result.records) == 2
    assert result.records[0].source_row == 2
    assert result.records[0].institution_id == "100001"
