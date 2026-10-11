"""Create a deterministic, replaceable local SQLite snapshot."""

from dataclasses import dataclass
from pathlib import Path
import os
import sqlite3

from .schema import ImportResult, NumericCell


@dataclass(frozen=True)
class BuildReport:
    source_rows: int
    normalized_rows: int
    rejected_rows: int
    institutions: int


DDL = """
CREATE TABLE eada (
    year INTEGER NOT NULL, institution_id TEXT NOT NULL,
    institution_name TEXT NOT NULL, state TEXT NOT NULL,
    division TEXT NOT NULL, institution_type TEXT NOT NULL,
    sport_code TEXT NOT NULL, sport_name TEXT NOT NULL,
    category TEXT NOT NULL,
    participants_raw TEXT NOT NULL, participants_value TEXT,
    participants_status TEXT NOT NULL,
    team_expenses_raw TEXT NOT NULL, team_expenses_value TEXT,
    team_expenses_status TEXT NOT NULL,
    reported_per_participant_raw TEXT NOT NULL,
    reported_per_participant_value TEXT,
    reported_per_participant_status TEXT NOT NULL,
    source_file TEXT NOT NULL, source_row INTEGER NOT NULL,
    PRIMARY KEY (year, institution_id, sport_code, category)
);
CREATE TABLE rejected_rows (
    source_file TEXT NOT NULL, source_row INTEGER NOT NULL, reason TEXT NOT NULL
);
CREATE INDEX eada_peers ON eada(year, sport_code, state, division, institution_type);
"""


def _cell(cell: NumericCell) -> tuple[str, str | None, str]:
    return cell.raw, str(cell.value) if cell.value is not None else None, cell.status


def build_database(result: ImportResult, path: str | Path) -> BuildReport:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    try:
        connection = sqlite3.connect(temporary)
        try:
            connection.executescript(DDL)
            rows = sorted(result.records, key=lambda r: (
                r.year, r.institution_id, r.sport_code, r.category
            ))
            connection.executemany(
                "INSERT INTO eada VALUES (" + ",".join("?" for _ in range(20)) + ")",
                [
                    (
                        r.year, r.institution_id, r.institution_name, r.state,
                        r.division, r.institution_type, r.sport_code, r.sport_name,
                        r.category, *_cell(r.participants), *_cell(r.team_expenses),
                        *_cell(r.reported_per_participant), r.source_file, r.source_row,
                    )
                    for r in rows
                ],
            )
            connection.executemany(
                "INSERT INTO rejected_rows VALUES (?, ?, ?)",
                [(r.source_file, r.source_row, r.reason) for r in result.rejects],
            )
            connection.commit()
        finally:
            connection.close()
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return BuildReport(
        source_rows=result.source_rows,
        normalized_rows=len(result.records),
        rejected_rows=len(result.rejects),
        institutions=len({r.institution_id for r in result.records}),
    )
