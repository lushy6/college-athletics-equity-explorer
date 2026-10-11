"""Read-only peer queries and guarded per-participant calculation."""

from dataclasses import dataclass
from decimal import Decimal
from contextlib import closing
from pathlib import Path
import sqlite3

from .schema import NumericCell


@dataclass(frozen=True)
class Comparison:
    year: int
    institution_id: str
    institution_name: str
    state: str
    division: str
    institution_type: str
    sport_code: str
    sport_name: str
    category: str
    participants: NumericCell
    team_expenses: NumericCell
    reported_per_participant: NumericCell
    calculated_per_participant: Decimal | None
    undefined_reason: str | None
    source_file: str
    source_row: int


def _cell(row: sqlite3.Row, prefix: str) -> NumericCell:
    number = row[f"{prefix}_value"]
    return NumericCell(
        row[f"{prefix}_raw"], Decimal(number) if number is not None else None,
        row[f"{prefix}_status"],
    )


def compare_peers(
    path: str | Path, *, year: int, sport_code: str,
    state: str | None = None, division: str | None = None,
    institution_type: str | None = None, institution_id: str | None = None,
) -> list[Comparison]:
    clauses = ["year = ?", "sport_code = ?"]
    parameters: list[int | str] = [year, sport_code]
    for name, value in (
        ("state", state), ("division", division),
        ("institution_type", institution_type), ("institution_id", institution_id),
    ):
        if value is not None:
            clauses.append(f"{name} = ?")
            parameters.append(value)
    query = "SELECT * FROM eada WHERE " + " AND ".join(clauses) + (
        " ORDER BY institution_name, institution_id, category"
    )
    with closing(sqlite3.connect(path)) as connection:
        connection.row_factory = sqlite3.Row
        source_rows = connection.execute(query, parameters).fetchall()
    results = []
    for row in source_rows:
        participants = _cell(row, "participants")
        expenses = _cell(row, "team_expenses")
        reported = _cell(row, "reported_per_participant")
        if participants.value is None:
            calculated, reason = None, f"participants {participants.status}"
        elif participants.value == 0:
            calculated, reason = None, "zero participants"
        elif expenses.value is None:
            calculated, reason = None, f"team expenses {expenses.status}"
        else:
            calculated, reason = expenses.value / participants.value, None
        results.append(Comparison(
            year=row["year"], institution_id=row["institution_id"],
            institution_name=row["institution_name"], state=row["state"],
            division=row["division"], institution_type=row["institution_type"],
            sport_code=row["sport_code"], sport_name=row["sport_name"],
            category=row["category"], participants=participants,
            team_expenses=expenses, reported_per_participant=reported,
            calculated_per_participant=calculated, undefined_reason=reason,
            source_file=row["source_file"], source_row=row["source_row"],
        ))
    return results
