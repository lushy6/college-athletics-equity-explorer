# College Athletics Equity Explorer

A local, read-only explorer of reported college sport participation and game-day operating expenses. It helps a student or reporter see a school/sport/category figure, compare peers from the same EADA collection, and trace every displayed number to a workbook row. It does not score Title IX compliance or measure an athletics department's entire budget.

## Run with the synthetic fixture

Install [uv](https://docs.astral.sh/uv/) and Python 3.12, then run:

```powershell
uv sync --group dev
uv run python -m athletics_etl.cli import --input tests/fixtures/eada_synthetic.csv --year 2024
uv run streamlit run app.py
```

The app opens on localhost. Choose **Example College → Basketball** to see why its men's zero participant count and women's blank participant cell make a calculated ratio undefined. The selected school values show source file and row; the peer table includes a source reference for every category.

## Run with the official 2023–24 file

Get `EADA_2023-2024.zip` from the [official EADA download page](https://ope.ed.gov/athletics/public/html/datafile/datafile.list.html). Compare its SHA-256 and byte count to [source_manifest.json](data/source_manifest.json). Extract `schools.xlsx` to `data/raw/2024/schools.xlsx`; raw files and the built database are gitignored. The direct official URL is in the manifest. Then run:

```powershell
uv run python -m athletics_etl.cli import --input data/raw/2024/schools.xlsx --year 2024
uv run streamlit run app.py
```

`EADA_DB_PATH` can point the app to another local SQLite snapshot. Each import replaces the snapshot atomically. The CLI prints source, normalized, rejected, and institution counts. A nonzero reject count needs review before relying on comparisons.

## Verify

```powershell
uv run python -m pytest -q
```

The [data dictionary](docs/data_dictionary.md) documents the mapped fields and denominator rules. [Validation notes](docs/validation.md) record source-row checks. The EADA download is a collection snapshot and may differ from later corrected portal views. Raw-file redistribution rights were not established, so this repository carries code and a synthetic fixture only.

## Next milestone

Add two more collection years with reviewed mappings, reconcile changed definitions, then audit 30 displayed cells and record a short demo. The [full project plan](../../../docs/project-ideas/01-college-athletics-equity-explorer.md) specifies the remaining acceptance gates.
