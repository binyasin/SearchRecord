# CLI Command Schema — PSC Consumer Record Search Tool

**Feature:** 1-psc-consumer-search
**Date:** 2026-04-05

This document defines the command-line interface contract (analogous to an API contract
for a CLI tool). All consumers of `search.py` MUST conform to this schema.

---

## Command: search

```
python search.py <query> [OPTIONS]
```

### Positional Arguments

| Argument | Required | Type | Description |
|----------|----------|------|-------------|
| query | Yes | string (one or more tokens) | Search term(s); multiple tokens joined with space |

### Options

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--field` | `-f` | string | auto-detect | Field alias or canonical column name to search in |
| `--limit` | `-l` | int | 50 | Maximum number of results to return (1–10000) |
| `--exact` | `-e` | flag | false | Require exact value match instead of partial |

### Field Alias Map (contract)

All aliases below MUST resolve to the stated canonical column:

```
cons, consumer, consno, cons_no    → Cons_No
contract, contract_ac, account     → Contract_Ac
install, install_no                → Install_No
gic, gic_code                      → GIC_Code
sch, schedule                      → Sch_No.
leg, legacy                        → Leg_Ac_No
meter, meter_no                    → Meter_No
meter_type, meter_typ, type, cto   → Meter_Typ
tariff                             → Tariff
ibc, ibc_name                      → IBC_Name
amr, amr_status, status            → AMR_STATUS
lat, latitude                      → Actual_Latitude
lon, longitude                     → Actual_Longitude
dts, dts_id                        → DTS_ID
pmt, pmt_name                      → PMT_Name
feeder, feeder_name                → Feeder_Name
feeder_id, feederid                → FeederID
feeder_bh                          → Feeder_Name_(BH)
feeder_id_bh                       → FeederID_(BH)
cm, cm_no                          → CM_No
```

---

## Output Contract

### Standard output (stdout) — results found

```
  Query   : <query>
  Field   : <resolved_field_or_blank>
  Results : <N>[+] record(s)[( showing first <limit>)]

  <COL1>  <COL2>  ... <COL11>
  -----------------------------------------------
  <val>   <val>   ... <val>
  ...
```

Columns displayed (fixed order, dynamic widths):
1. Cons_No
2. Contract_Ac
3. Meter_No
4. Meter_Typ
5. Tariff
6. IBC_Name
7. AMR_STATUS
8. DTS_ID
9. PMT_Name
10. Feeder_Name
11. FeederID

### Standard output (stdout) — no results

```
  No results found for: '<query>'
  Searched in field: <field>

  Tips:
  - Try a partial match: python search.py <example>
  - Specify a field:     python search.py <value> --field <field>
```

### Standard error (stderr)

| Condition | Message format |
|-----------|---------------|
| CSV file not found | `ERROR: Data file not found: <absolute_path>` |
| Unrecognised field alias | `ERROR: Unknown field '<alias>'. Valid aliases: cons, meter, ibc, amr, dts, ...` |
| Invalid --limit value | `ERROR: --limit must be a positive integer` |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Successful query (including zero results) |
| 1 | Configuration error (missing file, bad argument) |
| 2 | Unexpected runtime error |

---

## Usage Examples (normative)

```bash
# By consumer number (auto-detect)
python search.py BL001271

# By IBC name (partial, auto-detect)
python search.py JOHAR

# By DTS ID (auto-detect)
python search.py 508214

# By feeder (explicit field)
python search.py "A.D.B.P S/S" --field feeder

# By AMR status
python search.py AMR --field amr

# By tariff (exact)
python search.py A3-G --field tariff --exact

# By PMT name (multi-word)
python search.py "HAROON JAFFAR" --field pmt

# Increase result limit
python search.py JOHAR --limit 200
```
