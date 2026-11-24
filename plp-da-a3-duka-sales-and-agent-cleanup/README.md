# PLP Data Analysis Assignment 3 — Duka Sales and Agent Cleanup

**Required repository name:** `plp-da-a3-duka-sales-and-agent-cleanup`

This repository contains two engagements:
1. Duka Electronics sales exploration for January–June 2026.
2. Mobile-money agent transaction data-quality audit, cleaning and county analysis.

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Regenerate agent data and run its notebook

```bash
python generate_data.py
```

This creates `agents.csv` and `agent_transactions.csv` using the assignment's seed 44 generator. Then open `agent_cleanup.ipynb` in VS Code/Jupyter and run all cells from top to bottom.

## Duka data

Place the original practical-generated `duka_sales.csv` in the repository root and run `duka_sales_exploration.ipynb`. The original Duka generator (seed 2026) still needs to be added unchanged to `generate_data.py`; it was not part of the supplied assignment excerpt.

## Outputs

- `outputs/agent_transactions_clean.csv`
- `outputs/premium_online_coast_capital.csv`
- `excel/duka_branch_summary.xlsx`

The notebooks create these outputs when run. Do not commit the raw generated CSV files.

## Duka Executive Summary

**Pending execution against the original Duka dataset.** The five quantified findings must be populated from the real 1,000-order dataset; no sales figures have been fabricated.

## Agent row-count record

- Raw generated transactions: 600 original rows + 12 appended duplicate rows = **612 rows**.
- After duplicate removal: **600 rows**, before subsequent validity/type filtering.
- Final cleaned row count and unknown-agent transaction count are calculated and displayed by `agent_cleanup.ipynb`.

## Submission checklist

- [ ] Add the original Duka seed-2026 generator unchanged.
- [ ] Run both notebooks from a restarted kernel, top to bottom.
- [ ] Verify the Excel SUMIFS/XLOOKUP/PivotTable results against notebook totals.
- [ ] Confirm output CSVs exist and commit only files under `outputs/` and `excel/` as data.
- [ ] Push this folder to the exact public GitHub repository name and submit its URL on PLP LMS.
