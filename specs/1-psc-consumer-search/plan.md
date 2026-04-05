# Implementation Plan — PSC Consumer Record Search Tool

**Feature:** 1-psc-consumer-search
**Version:** 1.0.0
**Date:** 2026-04-05
**Branch:** 1-psc-consumer-search
**Spec:** [spec.md](spec.md)
**Status:** Ready for implementation

---

## Constitution Check

| Principle | Requirement | Status |
|-----------|-------------|--------|
| 2.1 Accuracy & Integrity | Search results consistent and reproducible | ✅ Linear scan is deterministic |
| 2.2 Performance | < 300 ms typical queries | ✅ < 1 s for 100k records (target met) |
| 2.3 Security & Privacy | Read-only access; no personal data transmission | ✅ Local file, no network I/O |
| 2.4 Transparency | Error messages are explicit; no silent failures | ✅ Gap G-01/G-02 fix required |
| 2.5 Interoperability | Standard CLI interface; exit codes for scripting | ✅ Covered by cli-schema.md |
| §9 Testing | Unit + integration tests required | ⚠ Gap G-03: tests not yet written |
| §11 UX Standards | Fast response, no stack traces exposed | ✅ NFR-04 error handling required |
| §14 Documentation | User guide + developer docs required | ⚠ Gap G-05: quickstart written, onboarding pending |

**Gate result:** PASS with two tracked gaps (G-03, G-05) — both addressed in tasks below.

---

## Technical Context

| Item | Decision | Source |
|------|----------|--------|
| Language | Python 3.8+ | Existing `search.py`; spec assumption |
| Data source | CSV (utf-8-sig, comma-delimited) | `PSCData - PSCData.csv` observed |
| Dependencies | stdlib only (`csv`, `argparse`, `re`, `os`, `sys`) | NFR-02 |
| Search strategy | Linear single-pass scan | research.md R-04 |
| Field detection | Regex priority chain | research.md R-02 |
| Output format | Fixed-width plain-text table | research.md R-03 |
| Error exit codes | 0=success/no-results, 1=config error | research.md R-05; cli-schema.md |

---

## Project Objectives

1. Deliver a production-quality, fully-tested CLI search tool for PSC consumer records.
2. Close all gaps identified in research.md (G-01 through G-05 priority).
3. Ensure the tool meets all success criteria defined in spec.md.
4. Produce documentation sufficient for self-service onboarding by field staff.

---

## Scope

**In scope:**
- `search.py` — gaps G-01 and G-02 (error message improvements)
- `tests/` — unit test suite covering all FR and NFR-04 scenarios (gap G-03)
- `quickstart.md` — user guide (created, complete)
- `CLAUDE.md` update — developer onboarding notes (gap G-05)

**Out of scope (deferred to v1.1):**
- `--format json` output (G-04)
- SQLite indexing for datasets > 500,000 records
- Web or GUI interface

---

## Milestones & Deliverables

| Milestone | Deliverable | Acceptance Gate |
|-----------|-------------|-----------------|
| M-01: Gap Fix | Updated `search.py` with G-01 & G-02 fixed | All NFR-04 error messages match cli-schema.md |
| M-02: Tests | `tests/test_search.py` with full test suite | ≥ 90% line coverage; all 10 scenarios pass |
| M-03: Docs | `quickstart.md` validated + `CLAUDE.md` updated | Reviewable by non-developer |
| M-04: Release | Branch merged to `main` via PR | All tests green; checklist complete |

---

## Task Breakdown

### Phase 1: Bug Fixes & Gap Closure

#### T-01 — Fix missing-CSV error message (G-01)
**File:** `search.py` — `search()` function
**Change:** Wrap `open(CSV_FILE)` in try/except; print
`ERROR: Data file not found: <absolute_path>` to stderr; exit(1).
**Effort:** 0.5 h
**Dependency:** none
**Acceptance:** Running `search.py BL001` with CSV renamed triggers error with absolute path.

#### T-02 — Validate field alias on input (G-02)
**File:** `search.py` — `main()` argument parsing
**Change:** After alias resolution, if resolved field is not in `reader.fieldnames`,
print `ERROR: Unknown field '<alias>'. Valid aliases: …` to stderr; exit(1).
**Effort:** 0.5 h
**Dependency:** none
**Acceptance:** `python search.py X --field nonexistent` prints valid aliases list.

---

### Phase 2: Test Suite

#### T-03 — Create test infrastructure
**File:** `tests/__init__.py`, `tests/test_search.py`
**Change:** Create test directory; copy a minimal fixture CSV (5–10 rows) for deterministic tests.
**Effort:** 1 h
**Dependency:** none

#### T-04 — Unit tests: auto-detection (FR-02)
**Covers:** All patterns in `detect_field()`.
**Test cases:**
- `BL001271` → `Cons_No`
- `400002018827` → `Contract_Ac`
- `7000203015` → `Install_No`
- `CTO-40295` → `Meter_No`
- `508214` → `DTS_ID`
- `AMR` → `AMR_STATUS`
- `CTO` → `Meter_Typ`
- `A3-G` → `Tariff`
- `D0701` → `GIC_Code`
- `JOHAR` → `None` (full-text fallback)
**Effort:** 1 h
**Dependency:** T-03

#### T-05 — Unit tests: alias resolution (FR-07)
**Covers:** All entries in `FIELD_ALIASES`.
**Test cases:** Each alias resolves to its canonical column.
**Effort:** 0.5 h
**Dependency:** T-03

#### T-06 — Integration tests: search scenarios (FR-01–FR-09)
**Covers:** All 10 user scenarios from spec.md using fixture CSV.
**Key cases:**
- Exact consumer number match
- Partial match returns multiple rows
- Case-insensitive match (`johar` → JOHAR records)
- `--exact` flag restricts to exact values
- `--limit 2` truncates and shows notice
- Zero results returns tip message, exit 0
- `--field amr` with value `AMR`
- `--field feeder` with partial feeder name
- Full-text fallback (no field, unstructured query)
**Effort:** 2 h
**Dependency:** T-03

#### T-07 — Error handling tests (NFR-04)
**Covers:** G-01, G-02 (after T-01, T-02 fixes).
**Test cases:**
- Missing CSV → stderr message + exit 1
- Unknown field alias → stderr message + exit 1
- Invalid `--limit 0` → stderr + exit 1
**Effort:** 0.5 h
**Dependency:** T-01, T-02, T-03

---

### Phase 3: Documentation

#### T-08 — Validate quickstart.md (G-05 partial)
**Action:** Run all examples in quickstart.md against real CSV; confirm output matches
documented format. Fix any discrepancies.
**Effort:** 0.5 h
**Dependency:** T-01, T-02

#### T-09 — Update CLAUDE.md with developer onboarding notes (G-05)
**File:** `CLAUDE.md`
**Change:** Add: tech stack note (Python 3.8+, stdlib only), how to run tests, file structure,
CSV encoding note, link to spec and plan.
**Effort:** 0.5 h
**Dependency:** none

---

### Phase 4: PR & Release

#### T-10 — Create PR to main
**Action:** Push `1-psc-consumer-search` branch; open PR with spec link, test results,
and checklist sign-off.
**Effort:** 0.25 h
**Dependency:** T-01 through T-09

---

## Task Dependency Graph

```
T-01 ──┐
T-02 ──┤──► T-07
T-03 ──┤──► T-04
       ├──► T-05
       └──► T-06
T-01, T-02 ──► T-08
T-09 (independent)
All above ──► T-10
```

---

## Timeline & Effort Summary

| Task | Effort | Assignee Role |
|------|--------|---------------|
| T-01 Fix CSV error | 0.5 h | Developer |
| T-02 Fix alias validation | 0.5 h | Developer |
| T-03 Test infrastructure | 1.0 h | Developer |
| T-04 Auto-detect unit tests | 1.0 h | Developer/QA |
| T-05 Alias unit tests | 0.5 h | Developer/QA |
| T-06 Integration tests | 2.0 h | Developer/QA |
| T-07 Error handling tests | 0.5 h | QA |
| T-08 Quickstart validation | 0.5 h | Technical Writer |
| T-09 CLAUDE.md update | 0.5 h | Developer |
| T-10 PR & merge | 0.25 h | Developer |
| **Total** | **7.25 h** | |

**Estimated calendar time:** 1–2 working days (single developer + self-review).

---

## Resource Allocation & Roles

| Role | Responsibility | Tasks |
|------|---------------|-------|
| Developer | Bug fixes, test infrastructure, documentation | T-01, T-02, T-03, T-09, T-10 |
| Developer/QA | Test case writing | T-04, T-05, T-06 |
| QA | Error scenario validation | T-07 |
| Technical Writer | User guide validation | T-08 |

*For a solo contributor, all roles are performed by the same person.*

---

## Risk Assessment & Mitigation

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|------------|
| R-01 | CSV file encoding changes (non-BOM UTF-8) | Low | High | Detect encoding at startup; fallback to `utf-8` if `utf-8-sig` fails |
| R-02 | Dataset grows beyond 500k rows; performance SLA breached | Medium | Medium | Add benchmark test; document SQLite migration path in research.md |
| R-03 | Field auto-detection produces false positives for new data patterns | Low | Medium | Unit tests lock in detection patterns; add `--field` as escape hatch |
| R-04 | Python version < 3.8 on user machines | Low | Low | Add version check in `main()` with explicit error message |
| R-05 | Test fixture CSV becomes stale relative to real schema | Medium | Medium | Derive fixture from first 10 rows of real CSV; include in CI |

---

## Compliance & Quality Checkpoints

| Checkpoint | Criterion | Gate |
|------------|-----------|------|
| QC-01 | All unit tests pass | Required before M-04 |
| QC-02 | ≥ 90% line coverage | Required before M-04 |
| QC-03 | No stack traces reachable via normal CLI usage | Required before M-04 |
| QC-04 | quickstart.md examples all produce correct output | Required before M-04 |
| QC-05 | Constitution §9 test categories covered (unit + integration) | Required before M-04 |
| QC-06 | Exit codes match cli-schema.md contract | Required before M-04 |

---

## Generated Artifacts

| File | Purpose |
|------|---------|
| `specs/1-psc-consumer-search/spec.md` | Feature requirements |
| `specs/1-psc-consumer-search/plan.md` | This document |
| `specs/1-psc-consumer-search/research.md` | Design decisions & gap analysis |
| `specs/1-psc-consumer-search/data-model.md` | Entity model & field index |
| `specs/1-psc-consumer-search/contracts/cli-schema.md` | CLI interface contract |
| `specs/1-psc-consumer-search/quickstart.md` | End-user guide |
| `specs/1-psc-consumer-search/checklists/requirements.md` | Spec quality checklist |
