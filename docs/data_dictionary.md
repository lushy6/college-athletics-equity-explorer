# 2023–24 EADA schools workbook mapping

This first slice uses `schools.xlsx` from the official `EADA_2023-2024.zip` download. The CLI's `--year 2024` labels the collection period ending in 2024. The [2024 EADA survey guide](https://surveys.ope.ed.gov/athletics2024/wwwroot/documents/2024_EADA_Users_Guide.pdf) and bundled `SchoolsDoc2024.doc` define the fields. This adapter refuses a missing or duplicated required column; later years need their own reviewed mapping.

| Normalized field | Source column | Meaning |
| --- | --- | --- |
| institution ID | `unitid` | Six-digit federal institution ID; invalid IDs are rejected. |
| school, state, division, type | `institution_name`, `state_cd`, `classification_name`, `sector_name` | Peer labels from the same source row. |
| sport code, name | `SPORTSCODE`, `Sports` | Source sport classification. |
| men/women participants | `PARTIC_MEN`, `PARTIC_WOMEN` | Reported participant counts for that category. |
| men/women team expense | `OPEXPPERTEAM_MEN`, `OPEXPPERTEAM_WOMEN` | Reported game-day operating expenses per team, the numerator shown in the app. |
| men/women reported per participant | `OPEXPPERPART_MEN`, `OPEXPPERPART_WOMEN` | Source-reported per-participant expense, shown separately from our calculation. |

The local calculation divides reported team expense by reported participants only when both are valid and participants exceed zero. The source's per-participant value may be rounded differently. It is never substituted for an invalid calculation. Each numeric cell retains raw text, parsed value, and one of `observed`, `blank`, `suppressed`, `undefined`, or `invalid`. A reported zero is `observed`, unlike a blank. A code's presence does not mean both men's and women's teams participated.

Operating expenses are tied to games and practice, including travel, lodging, meals, uniforms and equipment, as described by the survey guide. They are not total athletics budgets. The explorer reports survey data and makes no Title IX or discrimination determination.
