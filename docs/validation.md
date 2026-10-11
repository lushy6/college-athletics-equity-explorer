# First-year validation log

**Collection:** 2023–24 EADA `schools.xlsx`, downloaded October 11, 2026 from the official EADA portal. ZIP SHA-256 and size match `data/source_manifest.json`.

**Import:** 17,959 workbook data rows; 35,918 normalized category rows; 0 rejected source rows; 2,040 unique institutions. The importer creates a men's and women's category row for every source row while preserving blanks. This is a 2024-only checkpoint, not the three-year portfolio release.

**Five fixed source-cell checks:** `scripts/check_sample.py` reads the original workbook and SQLite app snapshot independently, selects source row and category, and asserts exact raw cell equality. It checks a participant count and expense for Alabama A & M baseball (workbook row 2), a participant count and expense for its basketball women (row 3), and one participant count for its combined track/cross-country men (row 4). These were selected at the start of this checkpoint as consecutive source rows, not based on agreement. The script must report five `PASS` lines; a mismatch raises an error.

```powershell
uv run python scripts/check_sample.py --input data/raw/2024/schools.xlsx --db data/processed/eada.sqlite
```

These five source checks establish the row/field path for this first slice only. They do not constitute the 30-cell, three-year audit in the full plan. The survey file is a post-collection snapshot; later portal corrections can differ.
