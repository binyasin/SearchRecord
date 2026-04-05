# Quickstart Guide — PSC Consumer Record Search Tool

**Version:** 1.0.0 | **Date:** 2026-04-05

---

## Prerequisites

- Python 3.8 or later installed
- `PSCData - PSCData.csv` in the same directory as `search.py`

Verify Python:

```bash
python --version
# Python 3.8.x or higher
```

---

## Running a Search

```bash
python search.py <query>
```

### Common Examples

| Goal | Command |
|------|---------|
| Find a consumer by number | `python search.py BL001271` |
| Find all consumers in an IBC | `python search.py JOHAR` |
| Find by DTS ID | `python search.py 508214` |
| Find by feeder name | `python search.py "A.D.B.P S/S" --field feeder` |
| Find by AMR status | `python search.py AMR --field amr` |
| Find by tariff code | `python search.py A3-G --field tariff` |
| Find by PMT name | `python search.py "HAROON JAFFAR" --field pmt` |
| Exact match only | `python search.py CTO --field meter_type --exact` |
| See more results | `python search.py JOHAR --limit 200` |

---

## Field Shortcuts

You don't need to know the exact column name. Use these shortcuts with `--field`:

| Shortcut | Searches in |
|----------|------------|
| `cons` | Consumer Number |
| `dts` | DTS ID |
| `feeder` | Feeder Name |
| `feeder_id` | Feeder ID |
| `ibc` | IBC Name |
| `amr` | AMR Status |
| `meter_type` | Meter Type |
| `tariff` | Tariff Code |
| `pmt` | PMT Name |
| `meter` | Meter Number |
| `account` | Contract Account |

---

## Auto-Detection

If you omit `--field`, the tool guesses the right field automatically:

| Query pattern | Detected field |
|--------------|----------------|
| `BL001271` (2 letters + digits) | Consumer Number |
| `508214` (4–7 digits) | DTS ID |
| `AMR` or `NON AMR` | AMR Status |
| `A3-G` (letter + digit + dash) | Tariff |
| `CTO-40295` (starts with CTO-) | Meter Number |
| Anything else | Searches all fields |

---

## Understanding the Output

```
  Query   : JOHAR
  Field   : IBC_Name
  Results : 3+ record(s) (showing first 50)

  Cons_No    Contract_Ac     Meter_No   Meter_Typ  Tariff  IBC_Name  AMR_STATUS  DTS_ID  ...
  -------------------------------------------------------------------------------------------
  BL001271   400002018827    CTO-40295  CTO        A3-G    JOHAR     AMR         508214  ...
```

- **Results: 3+** means 3 or more records exist; use `--limit 200` to see more.
- Columns auto-size to fit the widest value.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ERROR: Data file not found` | Ensure `PSCData - PSCData.csv` is in the same folder as `search.py` |
| `ERROR: Unknown field` | Run `python search.py --help` to see valid field names |
| No results found | Try a shorter partial value; check spelling |
| Too many results | Add `--field` to narrow the search, or use `--exact` |
