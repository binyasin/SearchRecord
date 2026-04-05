# Tasks — PSC Consumer Record Search Tool

**Feature:** 1-psc-consumer-search
**Branch:** 1-psc-consumer-search
**Plan:** [plan.md](plan.md) | **Spec:** [spec.md](spec.md)
**Generated:** 2026-04-05
**Total tasks:** 28
**Status:** Ready for execution

---

## Implementation Strategy

Most core functionality already exists in `search.py`. This task list focuses on:
1. **Closing gaps** (G-01, G-02) — error messages per NFR-04 and cli-schema.md contract
2. **Test coverage** (G-03) — test suite from zero to ≥90% line coverage
3. **Documentation** (G-05) — CLAUDE.md onboarding

**MVP scope:** Phase 1 + Phase 2 + US1/US9/US10 tests (T001–T016) → fully tested, production-ready core.

---

## Phase 1: Setup — Test Infrastructure

**Goal:** Establish the test harness and fixture data needed by all subsequent test phases.

| # | Task | Effort | Role | Priority | Milestone |
|---|------|--------|------|----------|-----------|
| T001 | Create `tests/` directory and `tests/__init__.py` | 15 min | Developer | High | M-02 |
| T002 | Create `tests/fixtures/sample.csv` — 10-row deterministic fixture | 30 min | Developer | High | M-02 |
| T003 | Verify `pytest` available or document install step in CLAUDE.md | 15 min | Developer | High | M-02 |

### Tasks

- [x] T001 Create test package structure: `tests/__init__.py` and `tests/fixtures/` directory
- [x] T002 Create `tests/fixtures/sample.csv` — 10 rows covering all searchable field types (Consumer No, DTS, Feeder, IBC, AMR, Meter, Tariff, PMT)
- [x] T003 [P] Confirm `pytest` is available; add `pip install pytest` note to `CLAUDE.md` under "Running Tests"

**Phase 1 completion gate:** `python -m pytest tests/ --collect-only` lists test file(s) without error.

---

## Phase 2: Foundational — Bug Fixes (Gap G-01 & G-02)

**Goal:** Harden error handling to match the cli-schema.md contract before writing tests that assert on error behaviour.

**Prerequisite:** Phase 1 complete.

| # | Task | Effort | Role | Priority | Milestone | Risk |
|---|------|--------|------|----------|-----------|------|
| T004 | Fix missing-CSV error (G-01) | 30 min | Developer | High | M-01 | none |
| T005 | Fix unknown-field-alias error (G-02) | 30 min | Developer | High | M-01 | none |

### Tasks

- [x] T004 Fix `search()` in `search.py`: wrap `open(CSV_FILE)` in `try/except FileNotFoundError`; print `ERROR: Data file not found: <absolute_path>` to stderr and `sys.exit(1)`
- [x] T005 Fix `main()` in `search.py`: after alias resolution, check resolved field against `reader.fieldnames`; if not found print `ERROR: Unknown field '<alias>'. Valid aliases: cons, meter, ibc, amr, dts, pmt, feeder, feeder_id, tariff, gic, contract, account, install` to stderr and `sys.exit(1)`

**Phase 2 completion gate:**
- `python search.py BL001` with CSV renamed → prints `ERROR: Data file not found:` + exits 1
- `python search.py X --field badname` → prints `ERROR: Unknown field` + exits 1

---

## Phase 3: User Story 1 — Consumer Number Search (P1 Core)

**User story:** As a field technician, I can search by consumer number so that I can quickly
locate a consumer record without knowing exact column names.
**Spec reference:** Scenario 1 (spec.md §3)
**FR covered:** FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-07, FR-09

**Independent test criteria:**
- `search('BL001271')` returns exactly the BL001271 fixture row
- `search('bl001')` returns all rows where Cons_No starts with 'BL001' (case-insensitive)
- `search('BL001271', exact=True)` returns only the exact match

| # | Task | Effort | Role | Priority | Milestone |
|---|------|--------|------|----------|-----------|
| T006 | Write US1 unit test: exact consumer number | 20 min | QA | High | M-02 |
| T007 | Write US1 unit test: partial consumer number | 20 min | QA | High | M-02 |
| T008 | Write US1 unit test: case-insensitive match | 20 min | QA | High | M-02 |
| T009 | Write US1 unit test: --exact flag restricts results | 20 min | QA | High | M-02 |
| T010 | Write US1 unit test: auto-detect Cons_No pattern | 20 min | QA | High | M-02 |
| T011 | Write US1 integration test: tabular output contains all 11 required columns | 20 min | QA | High | M-02 |

### Tasks

- [x] T006 [US1] Write `test_search_by_exact_consumer_no()` in `tests/test_search.py`: `search('BL001271')` returns 1 row with correct Cons_No
- [x] T007 [US1] Write `test_search_by_partial_consumer_no()` in `tests/test_search.py`: `search('BL001')` returns all fixture rows with Cons_No starting 'BL001'
- [x] T008 [US1] Write `test_search_case_insensitive()` in `tests/test_search.py`: `search('bl001271')` returns same result as `search('BL001271')`
- [x] T009 [P] [US1] Write `test_search_exact_flag()` in `tests/test_search.py`: `search('BL001', exact=True)` returns 0 rows (no exact match); `search('BL001271', exact=True)` returns 1 row
- [x] T010 [P] [US1] Write `test_detect_field_consumer_no()` in `tests/test_search.py`: `detect_field('BL001271')` returns `'Cons_No'`
- [x] T011 [P] [US1] Write `test_output_columns()` in `tests/test_search.py`: result dict keys include all 11 display columns from FR-06

**Phase 3 completion gate:** `python -m pytest tests/test_search.py -k "US1 or consumer" -v` — all pass.

---

## Phase 4: User Story 9 — No Results Feedback (P1)

**User story:** As any user, I receive a clear message and actionable tip when my search
returns no results, so I know how to refine my query.
**Spec reference:** Scenario 9 (spec.md §3)
**FR covered:** FR-08

**Independent test criteria:**
- `search('ZZZNOMATCH')` returns empty list, exit code 0
- Print output contains "No results found" and at least one tip line

| # | Task | Effort | Role | Priority | Milestone |
|---|------|--------|------|----------|-----------|
| T012 | Write US9 test: zero results returns empty list | 20 min | QA | High | M-02 |
| T013 | Write US9 test: no-results message includes tip | 20 min | QA | High | M-02 |

### Tasks

- [x] T012 [US9] Write `test_no_results_returns_empty()` in `tests/test_search.py`: `search('ZZZNOMATCH')` returns `([], None, headers)` — empty list, exit 0
- [x] T013 [US9] Write `test_no_results_message()` in `tests/test_search.py`: capture stdout from `print_results([], None, headers, 'ZZZNOMATCH', 50)` and assert it contains "No results" and "Tips:"

**Phase 4 completion gate:** `python -m pytest tests/test_search.py -k "no_result" -v` — all pass.

---

## Phase 5: User Story 10 — Limit Control (P1)

**User story:** As any user, I can control how many results are shown, so that I can see
more than the default or avoid information overload.
**Spec reference:** Scenario 10 (spec.md §3)
**FR covered:** FR-05

**Independent test criteria:**
- `search('...', limit=2)` returns at most 2 rows even if more match
- Output contains truncation notice when limit reached

| # | Task | Effort | Role | Priority | Milestone |
|---|------|--------|------|----------|-----------|
| T014 | Write US10 test: limit truncates results | 20 min | QA | High | M-02 |
| T015 | Write US10 test: truncation notice in output | 20 min | QA | High | M-02 |

### Tasks

- [x] T014 [US10] Write `test_limit_truncates_results()` in `tests/test_search.py`: add ≥3 rows with same IBC in fixture; `search('TESTBC', limit=2)` returns exactly 2 rows
- [x] T015 [US10] Write `test_truncation_notice()` in `tests/test_search.py`: capture stdout from `print_results` with `limited=True`; assert output contains `--limit`

**Phase 5 completion gate:** `python -m pytest tests/test_search.py -k "limit" -v` — all pass.

---

## Phase 6: User Story 2 — DTS ID Search (P1)

**User story:** As an operations analyst, I can search by DTS ID to see all consumers on
a distribution transformer station.
**Spec reference:** Scenario 2 (spec.md §3)
**FR covered:** FR-01, FR-02

### Tasks

- [x] T016 [US2] Write `test_detect_field_dts()` in `tests/test_search.py`: `detect_field('508214')` returns `'DTS_ID'`
- [x] T017 [P] [US2] Write `test_search_by_dts()` in `tests/test_search.py`: `search('508214', field='dts')` returns all fixture rows with DTS_ID = '508214'

**Phase 6 completion gate:** `python -m pytest tests/test_search.py -k "dts" -v` — all pass.

---

## Phase 7: User Stories 3–8 — Field-Specific Search (P2)

**User stories:** Feeder, IBC, AMR, Meter Type, Tariff, PMT Name searches.
**Spec reference:** Scenarios 3–8 (spec.md §3)
**FR covered:** FR-01, FR-03, FR-04

These tests are independent of each other and can be written in parallel ([P]).

### Tasks

- [x] T018 [P] [US3] Write `test_search_by_feeder()` in `tests/test_search.py`: `search('A.D.B.P', field='feeder')` returns rows matching Feeder_Name partial
- [x] T019 [P] [US4] Write `test_search_by_ibc()` in `tests/test_search.py`: `search('JOHAR', field='ibc')` returns all fixture rows with IBC_Name = 'JOHAR'
- [x] T020 [P] [US4] Write `test_search_ibc_auto_detect()` in `tests/test_search.py`: `search('JOHAR')` auto-routes to IBC_Name (full-text fallback since no pattern)
- [x] T021 [P] [US5] Write `test_search_by_amr_status()` in `tests/test_search.py`: `search('AMR', field='amr')` returns only AMR rows
- [x] T022 [P] [US5] Write `test_detect_field_amr_keyword()` in `tests/test_search.py`: `detect_field('AMR')` returns `'AMR_STATUS'`
- [x] T023 [P] [US6] Write `test_search_by_meter_type()` in `tests/test_search.py`: `search('CTO', field='meter_type')` returns CTO meter rows
- [x] T024 [P] [US7] Write `test_search_by_tariff()` in `tests/test_search.py`: `search('A3-G', field='tariff')` returns A3-G tariff rows
- [x] T025 [P] [US7] Write `test_detect_field_tariff()` in `tests/test_search.py`: `detect_field('A3-G')` returns `'Tariff'`
- [x] T026 [P] [US8] Write `test_search_by_pmt()` in `tests/test_search.py`: `search('HAROON JAFFAR', field='pmt')` returns matching PMT rows

**Phase 7 completion gate:** `python -m pytest tests/test_search.py -k "feeder or ibc or amr or meter or tariff or pmt" -v` — all pass.

---

## Phase 8: Error Handling Tests (NFR-04)

**Goal:** Verify all three error conditions from cli-schema.md after Phase 2 fixes.

### Tasks

- [x] T027 Write `test_missing_csv_error()` in `tests/test_search.py`: temporarily rename CSV_FILE path; assert `FileNotFoundError` path triggers stderr message and `SystemExit(1)`
- [x] T027 [P] Write `test_unknown_field_alias_error()` in `tests/test_search.py`: call search with `field='nonexistent_xyz'`; assert `SystemExit(1)` is raised

**Phase 8 completion gate:** `python -m pytest tests/test_search.py -k "error" -v` — all pass.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Goal:** Documentation, coverage report, PR readiness.

| # | Task | Effort | Role | Priority | Milestone |
|---|------|--------|------|----------|-----------|
| T028 | Validate all quickstart.md examples | 30 min | Technical Writer | Medium | M-03 |

### Tasks

- [x] T028 Run every command in `specs/1-psc-consumer-search/quickstart.md` against real `PSCData - PSCData.csv`; confirm output format matches documented format; fix any discrepancies in quickstart.md or search.py

**Coverage gate:** `python -m pytest tests/ --cov=search --cov-report=term-missing` → line coverage ≥ 90%.

**Final PR gate:** All QC-01 through QC-06 checkpoints from plan.md pass.

---

## Dependency Graph

```
Phase 1 (T001–T003)
    └── Phase 2 (T004–T005)   ← must complete before error-handling tests
            └── Phase 8 (T027) ← depends on G-01/G-02 fixes

Phase 1 (T001–T003)
    ├── Phase 3 (T006–T011)   ← US1 core tests
    ├── Phase 4 (T012–T013)   ← US9 no-results tests
    ├── Phase 5 (T014–T015)   ← US10 limit tests
    ├── Phase 6 (T016–T017)   ← US2 DTS tests
    └── Phase 7 (T018–T026)   ← US3–US8 field tests (all parallel within phase)

All phases → Phase 9 (T028) → PR
```

---

## Parallel Execution Opportunities

Within each phase, tasks marked `[P]` can run concurrently:

| Phase | Parallel group | Tasks |
|-------|---------------|-------|
| 3 | Auto-detect + column + exact flag | T009, T010, T011 |
| 6 | DTS detect + search | T016, T017 |
| 7 | All field-specific tests | T018–T026 (9 tasks, fully independent) |
| 8 | Both error tests | T027 (both subtasks) |

---

## Full Task Summary

| Phase | Task ID | Description | Role | Effort | Priority | Milestone |
|-------|---------|-------------|------|--------|----------|-----------|
| 1 | T001 | Create test package | Developer | 15 min | High | M-02 |
| 1 | T002 | Create fixture CSV | Developer | 30 min | High | M-02 |
| 1 | T003 | Verify pytest | Developer | 15 min | High | M-02 |
| 2 | T004 | Fix CSV error message | Developer | 30 min | High | M-01 |
| 2 | T005 | Fix alias validation | Developer | 30 min | High | M-01 |
| 3 | T006 | Test: exact consumer no | QA | 20 min | High | M-02 |
| 3 | T007 | Test: partial consumer no | QA | 20 min | High | M-02 |
| 3 | T008 | Test: case-insensitive | QA | 20 min | High | M-02 |
| 3 | T009 | Test: --exact flag | QA | 20 min | High | M-02 |
| 3 | T010 | Test: auto-detect Cons_No | QA | 20 min | High | M-02 |
| 3 | T011 | Test: 11 output columns | QA | 20 min | High | M-02 |
| 4 | T012 | Test: zero results list | QA | 20 min | High | M-02 |
| 4 | T013 | Test: no-results message | QA | 20 min | High | M-02 |
| 5 | T014 | Test: limit truncation | QA | 20 min | High | M-02 |
| 5 | T015 | Test: truncation notice | QA | 20 min | High | M-02 |
| 6 | T016 | Test: detect DTS pattern | QA | 20 min | High | M-02 |
| 6 | T017 | Test: search by DTS | QA | 20 min | High | M-02 |
| 7 | T018 | Test: search by feeder | QA | 20 min | Medium | M-02 |
| 7 | T019 | Test: search by IBC | QA | 20 min | Medium | M-02 |
| 7 | T020 | Test: IBC auto-detect | QA | 20 min | Medium | M-02 |
| 7 | T021 | Test: search by AMR | QA | 20 min | Medium | M-02 |
| 7 | T022 | Test: detect AMR keyword | QA | 20 min | Medium | M-02 |
| 7 | T023 | Test: search by meter type | QA | 20 min | Medium | M-02 |
| 7 | T024 | Test: search by tariff | QA | 20 min | Medium | M-02 |
| 7 | T025 | Test: detect tariff pattern | QA | 20 min | Medium | M-02 |
| 7 | T026 | Test: search by PMT | QA | 20 min | Medium | M-02 |
| 8 | T027 | Test: missing CSV error | QA | 20 min | High | M-02 |
| 8 | T027 | Test: unknown alias error | QA | 20 min | High | M-02 |
| 9 | T028 | Validate quickstart.md | Technical Writer | 30 min | Medium | M-03 |

**Total estimated effort: ~7.25 hours**
**Total task count: 28**

---

## Blockers & Risks

| Task | Blocker | Risk | Mitigation |
|------|---------|------|------------|
| T002 | None | Fixture CSV schema drifts from real CSV | Derive fixture from first 10 rows of real CSV using `head -11 "PSCData - PSCData.csv"` |
| T005 | T004 (same function) | Alias check must happen after CSV open | Ensure `fieldnames` read after successful file open; use same reader for both checks |
| T027 | T004, T005 | Test must isolate the actual CSV path | Use `monkeypatch` or `unittest.mock.patch` to override `CSV_FILE` constant |
| T018–T026 | T002 | All require fixture rows covering each field | Fixture must include rows with non-null Feeder, IBC, AMR, Meter, Tariff, PMT values |
