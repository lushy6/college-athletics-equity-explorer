"""Small, explicit contracts for source values and their lineage."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


ValueStatus = Literal["observed", "blank", "suppressed", "undefined", "invalid"]


@dataclass(frozen=True)
class NumericCell:
    raw: str
    value: Decimal | None
    status: ValueStatus


@dataclass(frozen=True)
class Record:
    year: int
    institution_id: str
    institution_name: str
    state: str
    division: str
    institution_type: str
    sport_code: str
    sport_name: str
    category: Literal["men", "women"]
    participants: NumericCell
    team_expenses: NumericCell
    reported_per_participant: NumericCell
    source_file: str
    source_row: int


@dataclass(frozen=True)
class RejectedRow:
    source_file: str
    source_row: int
    reason: str


@dataclass(frozen=True)
class ImportResult:
    records: list[Record]
    rejects: list[RejectedRow]
    source_rows: int
