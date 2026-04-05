# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Project: PSC Consumer Record Search Tool

A command-line Python tool for searching PSC (Power Supply Company) consumer records
stored in a local CSV file.

---

## Tech Stack

- **Language:** Python 3.8+ (standard library only — no external packages)
- **Data source:** `PSCData - PSCData.csv` (UTF-8 BOM, comma-delimited, ~22 columns)
- **Entry point:** `search.py`

---

## Running the Tool

```bash
python search.py <query> [--field <alias>] [--limit <n>] [--exact]
```

Examples:
```bash
python search.py BL001271              # by consumer number (auto-detect)
python search.py JOHAR                 # by IBC name (auto-detect)
python search.py 508214 --field dts    # by DTS ID
python search.py A3-G --field tariff   # by tariff code
```

See `specs/1-psc-consumer-search/quickstart.md` for full usage guide.

---

## Running Tests

Install pytest first (one-time):
```bash
pip install pytest pytest-cov
```

Run tests:
```bash
python -m pytest tests/ -v
python -m pytest tests/ --cov=search --cov-report=term-missing
```

Test fixture CSV is at `tests/fixtures/sample.csv` (10-row subset of real data).

---

## Project Structure

```
search.py                    # Main CLI entry point
PSCData - PSCData.csv        # Production data (read-only)
CLAUDE.md                    # This file
.specify/memory/constitution.md   # Project governance
specs/1-psc-consumer-search/ # Feature spec, plan, research, contracts
  spec.md
  plan.md
  research.md
  data-model.md
  quickstart.md
  contracts/cli-schema.md
  checklists/requirements.md
tests/
  test_search.py
  fixtures/sample.csv
history/prompts/             # Prompt History Records (PHRs)
```

---

## Key Design Decisions

- **No external dependencies** — `csv`, `argparse`, `re`, `os`, `sys` only.
- **Read-only** — the tool never writes to the CSV file.
- **Auto-detection** — field is inferred from query pattern; see `detect_field()` in `search.py`.
- **Alias resolution** — short names (cons, ibc, amr, dts, pmt) map to CSV column names
  via `FIELD_ALIASES` dict.

---

## SDD Artifacts

This project uses Specification-Driven Development (SDD):
- Constitution: `.specify/memory/constitution.md`
- Feature spec: `specs/1-psc-consumer-search/spec.md`
- Implementation plan: `specs/1-psc-consumer-search/plan.md`
- CLI contract: `specs/1-psc-consumer-search/contracts/cli-schema.md`
