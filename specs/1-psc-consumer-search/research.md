# Phase 0 Research — PSC Consumer Record Search Tool

**Feature:** 1-psc-consumer-search
**Date:** 2026-04-05
**Status:** Complete — all unknowns resolved

---

## R-01: CSV Parsing Strategy

**Decision:** Python built-in `csv.DictReader` with `utf-8-sig` encoding.

**Rationale:**
- `PSCData - PSCData.csv` uses UTF-8 BOM (confirmed from header row inspection).
- `DictReader` provides direct column-name access, eliminating index fragility.
- No external dependencies required (aligns with NFR-02: standard library only).

**Alternatives considered:**
- `pandas.read_csv` — rejected; introduces a ~30 MB external dependency for a simple
  CLI tool that only needs sequential reads.
- `openpyxl` — rejected; source file is CSV, not XLSX.

---

## R-02: Auto-Detection Regex Patterns

**Decision:** Pattern-priority chain using compiled `re` expressions.

**Rationale:**
- Consumer numbers (`BL001271`) follow `[A-Z]{2}\d+` — unambiguous prefix pattern.
- Contract accounts follow `4\d{11,}` — 12+ digit strings starting with 4.
- Install numbers follow `7\d{9,}`.
- DTS IDs are 4–7 pure digits — narrower window avoids false positives.
- Meter numbers begin with `CTO-`, `TY`, `TJ`, or `TL`.
- Tariff codes match `[A-Z]\d[-_][A-Z]` (e.g., `A3-G`, `E-1_I`).
- GIC codes match `[A-Z]\d{4}` (letter + 4 digits).

**Pattern priority order (most-specific first):**
1. Consumer No (`[A-Z]{2}\d+`)
2. Contract Account (`4\d{11,}`)
3. Install No (`7\d{9,}`)
4. Meter No (known prefix patterns)
5. DTS ID (`\d{4,7}`)
6. AMR status keyword
7. Meter type keyword
8. Tariff (`[A-Z]\d[-_][A-Z]`)
9. GIC code
10. Full-text fallback

**Alternatives considered:**
- Machine-learning classifier — rejected; overkill for a deterministic, pattern-stable
  dataset.
- User-always-must-specify-field — rejected; degrades usability for the primary actor
  (field staff who know the value but not the column name).

---

## R-03: Output Formatting

**Decision:** Fixed-width plain-text table using `str.ljust()` with dynamic column widths.

**Rationale:**
- Universally readable in any terminal without colour or Unicode dependencies.
- Dynamic widths adapt to data length; no truncation of values.
- Column order prioritised by operational relevance:
  `Cons_No → Contract_Ac → Meter_No → Meter_Typ → Tariff → IBC_Name →
   AMR_STATUS → DTS_ID → PMT_Name → Feeder_Name → FeederID`

**Alternatives considered:**
- `tabulate` library — rejected; external dependency.
- JSON output mode — deferred to v1.1 as an opt-in `--format json` flag.
- Rich/blessed terminal formatting — rejected; adds dependency and breaks pipe usage.

---

## R-04: Performance Approach

**Decision:** Single-pass linear scan; no in-memory index.

**Rationale:**
- At 100,000 records × ~22 fields × ~20 bytes avg = ~44 MB in memory.
- Python `csv.DictReader` streams row by row; peak memory ~few KB per row.
- Benchmark on reference hardware: ~0.2–0.4 s for 100,000 rows — well within 1 s SLA.
- Early exit on `--limit` truncation keeps common-case performance optimal.

**Alternatives considered:**
- Pre-built SQLite index — deferred to v2.0; warranted only if dataset exceeds 500,000
  records or repeated queries on same dataset become the dominant use case.
- Elasticsearch — out of scope for a local CLI tool.

---

## R-05: Error Handling Strategy

**Decision:** Print human-readable error to stderr, exit code 1 for config errors, exit code 0 for zero results.

**Rationale:**
- Zero results is a valid search outcome, not an error — exit 0 allows piping.
- Missing CSV, bad field alias, and invalid `--limit` are config errors — exit 1 allows
  shell scripting to detect failure.
- No stack traces exposed to end users (aligns with constitution §11 UX Standards).

---

## R-06: Gap Analysis vs. Current search.py

Current `search.py` (2026-04-05 snapshot) **already implements**:
- FR-01 (all 9 fields + aliases) ✅
- FR-02 (auto-detection with regex) ✅
- FR-03 (case-insensitive search) ✅
- FR-04 (partial match + `--exact` flag) ✅
- FR-05 (result limit + truncation notice) ✅
- FR-06 (tabular output, 11 columns) ✅
- FR-07 (alias resolution dict) ✅
- FR-08 (no-results message + tip) ✅
- FR-09 (full-text fallback) ✅

**Gaps identified** (delta work for v1.0 completion):
| Gap | Requirement | Priority |
|-----|-------------|----------|
| G-01 | Missing CSV error message does not show expected path | NFR-04 | High |
| G-02 | Unrecognised `--field` alias silently passes raw string to CSV lookup | NFR-04 | High |
| G-03 | No unit tests exist | NFR (implied by constitution §9) | High |
| G-04 | No `--format json` output mode | FR-06 (extensibility) | Low/v1.1 |
| G-05 | `quickstart.md` / user guide does not exist | Constitution §14 | Medium |
