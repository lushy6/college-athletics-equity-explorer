"""Command-line entry point for user-downloaded EADA files."""

import argparse
from dataclasses import asdict
import json

from .build_db import build_database
from .import_eada import import_year


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local EADA comparison database")
    parser.add_argument("command", choices=["import"])
    parser.add_argument("--input", required=True, help="Extracted schools.xlsx or equivalent CSV")
    parser.add_argument("--year", required=True, type=int, help="EADA collection starting year")
    parser.add_argument("--db", default="data/processed/eada.sqlite")
    args = parser.parse_args()
    result = import_year(args.input, args.year)
    report = build_database(result, args.db)
    print(json.dumps({"database": args.db, **asdict(report)}, indent=2))
    if result.rejects:
        print(f"Review {len(result.rejects)} rejected source rows before using the figures.")


if __name__ == "__main__":
    main()
