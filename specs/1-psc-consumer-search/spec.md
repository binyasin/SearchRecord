# Feature Specification: PSC Consumer Record Search Tool

**Feature ID:** 1-psc-consumer-search
**Version:** 1.0.0
**Date:** 2026-04-05
**Status:** Draft
**Author:** binyasin

---

## 1. Overview

### 1.1 Problem Statement

Field staff, billing officers, and operations teams at PSC (Power Supply Company) need to
quickly locate consumer records from a large dataset. Currently this requires manually
scanning a CSV file or using spreadsheet tools, which is slow, error-prone, and inaccessible
from the command line or automated workflows.

### 1.2 Feature Summary

A command-line search tool that allows users to find PSC consumer records by one or more
searchable fields — including Consumer Number, DTS ID, Feeder, IBC, AMR status, Meter type,
Tariff, and PMT Name — with intelligent auto-detection of the search field and a clean,
readable output.

### 1.3 Goals

* Enable fast, single-command lookup of any PSC consumer record.
* Support all major searchable fields without requiring users to remember exact column names.
* Provide readable tabular output suitable for terminal use.
* Return results in under 1 second for datasets up to 100,000 records.

### 1.4 Non-Goals

* This tool does not modify, add, or delete records.
* This tool does not provide a graphical or web-based interface (CLI only).
* This tool does not synchronise with live billing systems.
* Bulk export or reporting is out of scope.

---

## 2. Actors & Stakeholders

| Actor | Description | Primary Use |
|-------|-------------|-------------|
| Field Staff | Technicians performing on-site work | Look up meter and DTS details |
| Billing Officer | Office staff processing consumer accounts | Verify consumer number, tariff, IBC |
| Operations Analyst | Reviews feeder and PMT assignments | Search by Feeder, DTS, PMT |
| System Integrator | Embeds search in scripts or pipelines | Machine-readable output |

---

## 3. User Scenarios & Acceptance Tests

### Scenario 1 — Search by Consumer Number (Primary Path)

**Given** a user knows a consumer number (e.g., `BL001271`)
**When** they run `search BL001271`
**Then** the tool returns the matching consumer record(s) with all key fields displayed
**And** results appear within 1 second

**Acceptance criteria:**
- Exact consumer number returns the correct record.
- Partial consumer number (e.g., `BL001`) returns all matching records.
- Search is case-insensitive.

---

### Scenario 2 — Search by DTS ID

**Given** a user knows a DTS ID (e.g., `508214`)
**When** they run `search 508214`
**Then** all consumers on that DTS are returned
**And** the output shows Feeder, IBC, and AMR status for each consumer

**Acceptance criteria:**
- All records matching the DTS ID are returned (up to configured limit).
- Result count is shown; user is notified when results are truncated.

---

### Scenario 3 — Search by Feeder Name or ID

**Given** a user wants all consumers on a feeder
**When** they run `search "A.D.B.P S/S" --field feeder`
**Then** all consumers on that feeder are listed

**Acceptance criteria:**
- Partial feeder name match is supported.
- Both `Feeder_Name` and `FeederID` are searchable.

---

### Scenario 4 — Search by IBC Name

**Given** a user wants to see all consumers under an IBC (e.g., `JOHAR`)
**When** they run `search JOHAR`
**Then** all consumers in the JOHAR IBC are returned

**Acceptance criteria:**
- Case-insensitive partial match on IBC name works.

---

### Scenario 5 — Filter by AMR Status

**Given** a user needs to identify non-AMR consumers
**When** they run `search "NON AMR" --field amr`
**Then** all consumers with that AMR status are listed

**Acceptance criteria:**
- Supports values: `AMR`, `NON AMR`, `Inactive`, `Active`.
- Status matching is case-insensitive.

---

### Scenario 6 — Filter by Meter Type

**Given** a billing officer wants all CTO meters
**When** they run `search CTO --field meter_type`
**Then** all consumers with Meter_Typ = CTO are returned

**Acceptance criteria:**
- Supports exact and partial match on meter type values.

---

### Scenario 7 — Search by Tariff

**Given** a user wants consumers on a specific tariff (e.g., `A3-G`)
**When** they run `search A3-G --field tariff`
**Then** all A3-G tariff consumers are listed

**Acceptance criteria:**
- Tariff codes are matched exactly by default; partial match supported without `--exact`.

---

### Scenario 8 — Search by PMT Name

**Given** a user knows a PMT name
**When** they run `search "HAROON JAFFAR"`
**Then** all consumers under that PMT are returned

**Acceptance criteria:**
- Multi-word PMT names work with or without quotes.

---

### Scenario 9 — No Results Found

**Given** a user searches for a value that does not exist
**When** they run `search UNKNOWN_VALUE`
**Then** the tool displays a clear "no results" message
**And** provides at least one tip for refining the search

**Acceptance criteria:**
- Zero-result state is clearly communicated.
- No error or stack trace is shown.

---

### Scenario 10 — Limit Control

**Given** a search returns more than the default result count
**When** the user runs `search JOHAR --limit 200`
**Then** up to 200 records are shown
**And** if results were truncated at the default limit, the user is told how to see more

---

## 4. Functional Requirements

### FR-01: Multi-Field Search Support

The tool MUST support searching across all of the following fields:

| Field | Aliases | Description |
|-------|---------|-------------|
| Cons_No | cons, consumer, consno | Consumer number |
| DTS_ID | dts, dts_id | Distribution transformer station ID |
| Feeder_Name | feeder, feeder_name | Feeder name |
| FeederID | feeder_id, feederid | Feeder numeric ID |
| IBC_Name | ibc, ibc_name | Independent Billing Cell name |
| AMR_STATUS | amr, amr_status, status | AMR meter status |
| Meter_Typ | meter_type, meter_typ, cto, type | Meter type |
| Tariff | tariff | Consumer tariff code |
| PMT_Name | pmt, pmt_name | Primary Metering Terminal name |

### FR-02: Automatic Field Detection

When no `--field` flag is provided, the tool MUST auto-detect the most likely field based
on the query pattern (e.g., `BL001271` → `Cons_No`, `508214` → `DTS_ID`).

### FR-03: Case-Insensitive Search

All text searches MUST be case-insensitive by default.

### FR-04: Partial Match

Searches MUST return partial matches by default. An `--exact` flag MUST be available to
restrict to exact-value matches.

### FR-05: Result Limit

The tool MUST enforce a configurable result limit (default: 50). When results are truncated,
the user MUST be informed. The limit MUST be adjustable via `--limit N`.

### FR-06: Tabular Output

Results MUST be displayed in a fixed-width tabular format showing at minimum:
`Cons_No`, `Contract_Ac`, `Meter_No`, `Meter_Typ`, `Tariff`, `IBC_Name`, `AMR_STATUS`,
`DTS_ID`, `PMT_Name`, `Feeder_Name`, `FeederID`.

### FR-07: Field Alias Resolution

Short-form aliases (e.g., `cons`, `ibc`, `amr`, `dts`, `pmt`, `feeder`) MUST resolve to
their canonical CSV column names automatically.

### FR-08: No-Results Feedback

When a query returns zero records, the tool MUST print a user-friendly message and at
least one actionable suggestion for refining the search.

### FR-09: Fallback to Full-Text Search

When field auto-detection produces no match and no `--field` is specified, the tool MUST
fall back to searching all text fields.

---

## 5. Non-Functional Requirements

### NFR-01: Performance

* Search across a dataset of up to 100,000 records MUST complete in under 1 second
  on standard hardware.

### NFR-02: Portability

* The tool MUST run on Windows, macOS, and Linux without modification.
* No external dependencies beyond the Python standard library are required.

### NFR-03: Data Safety

* The tool MUST be read-only; it MUST NOT write to, modify, or delete any record.

### NFR-04: Error Handling

* Missing CSV file: MUST print a clear error with the expected file path.
* Unrecognised field alias: MUST list valid aliases.
* Invalid `--limit` value: MUST print usage hint.

---

## 6. Key Entities

| Entity | Key Fields | Notes |
|--------|------------|-------|
| Consumer Record | Cons_No, Contract_Ac, Install_No | Unique identifier: Cons_No |
| Meter | Meter_No, Meter_Typ | Linked to consumer |
| Distribution Station | DTS_ID | One DTS serves many consumers |
| Feeder | FeederID, Feeder_Name | One feeder serves many DTS |
| IBC | IBC_Name, PSC_Cons_IBC | Billing zone |
| PMT | PMT_Name | Primary metering terminal |

---

## 7. Assumptions

1. The data source is a single CSV file (`PSCData - PSCData.csv`) co-located with the script.
2. The CSV uses UTF-8 BOM encoding and comma delimiters.
3. Dataset size is expected to remain under 500,000 records for CLI usage.
4. Users run the tool from a terminal with Python 3.8+ installed.
5. No authentication or access control is needed at this stage (local file access only).
6. The `search-record` Claude Code skill (`.claude/skills/search-record/`) is the primary
   integration surface; this spec governs the underlying `search.py` implementation.

---

## 8. Success Criteria

| # | Criterion | Measure |
|---|-----------|---------|
| SC-01 | Search returns correct results | 100% of known consumer numbers found in < 1 s |
| SC-02 | Auto-detection accuracy | Correct field detected for > 95% of structured query patterns |
| SC-03 | Usability | User can find a consumer record with a single command and zero prior knowledge of column names |
| SC-04 | No-result guidance | Every zero-result response includes at least one actionable tip |
| SC-05 | Stability | Tool exits with code 0 for all valid queries; non-zero only on configuration errors |

---

## 9. Dependencies

* `PSCData - PSCData.csv` — must be present and readable at runtime.
* Python 3.8+ standard library (`csv`, `argparse`, `re`, `os`, `sys`).
* Claude Code `search-record` skill (`.claude/skills/search-record/skill.md`) — optional
  integration for in-session use.

---

## 10. Out of Scope / Future Considerations

* Web or GUI interface
* Live database connection or API backend
* Multi-file / multi-dataset search
* Export to JSON / CSV output format
* Authentication or user roles
* Pagination (replaced by `--limit` for CLI simplicity)
