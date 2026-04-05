#!/usr/bin/env python3
"""
PSC Data Search Tool
Usage: python search.py <query> [--field <fieldname>] [--limit <n>]
"""

import csv
import sys
import os
import re
import argparse

CSV_FILE = os.path.join(os.path.dirname(__file__), "PSCData - PSCData.csv")

# Field aliases for easy access
FIELD_ALIASES = {
    "cons":        "Cons_No",
    "consumer":    "Cons_No",
    "cons_no":     "Cons_No",
    "consno":      "Cons_No",

    "contract":    "Contract",
    "contract_ac": "Contract_Ac",
    "account":     "Contract_Ac",

    "install":     "Install_No",
    "install_no":  "Install_No",

    "gic":         "GIC_Code",
    "gic_code":    "GIC_Code",

    "sch":         "Sch_No.",
    "schedule":    "Sch_No.",

    "leg":         "Leg_Ac_No",
    "legacy":      "Leg_Ac_No",

    "meter":       "Meter_No",
    "meter_no":    "Meter_No",
    "meter_type":  "Meter_Typ",
    "meter_typ":   "Meter_Typ",
    "type":        "Meter_Typ",
    "cto":         "Meter_Typ",

    "tariff":      "Tariff",

    "ibc":         "IBC_Name",
    "ibc_name":    "IBC_Name",

    "amr":         "AMR_STATUS",
    "amr_status":  "AMR_STATUS",
    "status":      "AMR_STATUS",

    "lat":         "Actual_Latitude",
    "latitude":    "Actual_Latitude",
    "lon":         "Actual_Longitude",
    "longitude":   "Actual_Longitude",

    "dts":         "DTS_ID",
    "dts_id":      "DTS_ID",

    "pmt":         "PMT_Name",
    "pmt_name":    "PMT_Name",

    "feeder":      "Feeder_Name",
    "feeder_name": "Feeder_Name",
    "feeder_id":   "FeederID",
    "feederid":    "FeederID",

    "feeder_bh":   "Feeder_Name_(BH)",
    "feeder_id_bh":"FeederID_(BH)",

    "cm":          "CM_No",
    "cm_no":       "CM_No",
}

def detect_field(query):
    """Auto-detect the most likely field based on query pattern."""
    q = query.strip().upper()

    # Consumer number patterns: starts with 2 letters + digits (e.g. BL001271, AL135711, DP002726)
    if re.match(r'^[A-Z]{2}\d+$', q):
        return "Cons_No"

    # Contract account: long numeric (12+ digits starting with 4)
    if re.match(r'^4\d{11,}$', q):
        return "Contract_Ac"

    # Installation number: starts with 7 + digits
    if re.match(r'^7\d{9,}$', q):
        return "Install_No"

    # Meter number patterns
    if re.match(r'^(CTO-|TY|TJ|TL)\w+', q, re.IGNORECASE):
        return "Meter_No"

    # DTS ID: purely numeric, typically 4-7 digits
    if re.match(r'^\d{4,7}$', q):
        return "DTS_ID"

    # AMR status keywords
    if q in ("AMR", "NON AMR", "NONAMR", "INACTIVE", "ACTIVE"):
        return "AMR_STATUS"

    # Meter type keywords
    if q in ("CTO", "THREE", "HOOK", "INACTIVE"):
        return "Meter_Typ"

    # Tariff patterns: A1-R, A3-G, E-1_I, etc.
    if re.match(r'^[A-Z]\d[-_][A-Z]', q):
        return "Tariff"

    # GIC code: letter + 4 digits
    if re.match(r'^[A-Z]\d{4}$', q):
        return "GIC_Code"

    # Default: search all text fields
    return None

def search(query, field=None, limit=50, exact=False):
    query_lower = query.strip().lower()

    # Resolve alias
    resolved_field = None
    if field:
        resolved_field = FIELD_ALIASES.get(field.lower(), field)

    # Auto-detect if no field given
    if not resolved_field:
        resolved_field = detect_field(query)

    results = []
    # T004: Explicit error for missing CSV (G-01)
    if not os.path.isfile(CSV_FILE):
        print(f"ERROR: Data file not found: {os.path.abspath(CSV_FILE)}", file=sys.stderr)
        sys.exit(1)

    with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        # T005: Validate resolved field against actual CSV columns (G-02)
        if resolved_field and resolved_field not in headers:
            valid = ", ".join(sorted(FIELD_ALIASES.keys()))
            print(
                f"ERROR: Unknown field '{field or resolved_field}'. "
                f"Valid aliases: {valid}",
                file=sys.stderr,
            )
            sys.exit(1)

        for row in reader:
            if resolved_field:
                cell = row.get(resolved_field, "")
                match = (
                    cell.strip().lower() == query_lower if exact
                    else query_lower in cell.strip().lower()
                )
            else:
                # Search all fields
                match = any(query_lower in v.lower() for v in row.values() if v)

            if match:
                results.append(row)
                if len(results) >= limit:
                    break

    return results, resolved_field, headers

def print_results(results, field_searched, headers, query, limit):
    if not results:
        print(f"\n  No results found for: '{query}'")
        if field_searched:
            print(f"  Searched in field: {field_searched}")
        print("\n  Tips:")
        print("  - Try a partial match: python search.py JOHAR")
        print("  - Specify a field:     python search.py AMR --field amr_status")
        return

    total = len(results)
    limited = total >= limit

    print(f"\n  Query   : {query}")
    if field_searched:
        print(f"  Field   : {field_searched}")
    print(f"  Results : {total}{'+' if limited else ''} record(s){' (showing first ' + str(limit) + ')' if limited else ''}")
    print()

    # Determine columns to display (skip empty/zero columns for brevity)
    display_cols = [
        "Cons_No", "Contract_Ac", "Meter_No", "Meter_Typ", "Tariff",
        "IBC_Name", "AMR_STATUS", "DTS_ID", "PMT_Name", "Feeder_Name", "FeederID"
    ]

    # Column widths
    col_widths = {col: len(col) for col in display_cols}
    for row in results:
        for col in display_cols:
            col_widths[col] = max(col_widths[col], len(row.get(col, "")))

    # Header
    header_line = "  " + "  ".join(col.ljust(col_widths[col]) for col in display_cols)
    print(header_line)
    print("  " + "-" * (sum(col_widths[c] + 2 for c in display_cols)))

    for row in results:
        line = "  " + "  ".join(row.get(col, "").ljust(col_widths[col]) for col in display_cols)
        print(line)

    if limited:
        print(f"\n  ... use --limit <n> to see more (e.g. --limit 200)")

def main():
    parser = argparse.ArgumentParser(
        description="Search PSC consumer records",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python search.py BL001271               # Search by consumer number
  python search.py JOHAR                  # Search by IBC name
  python search.py AMR                    # Search AMR status
  python search.py CTO --field meter_type # Search CTO meters
  python search.py 508214 --field dts     # Search by DTS ID
  python search.py 3067 --field feeder_id # Search by Feeder ID
  python search.py "HAROON JAFFAR"        # Search PMT name
  python search.py A3-G --field tariff    # Search by tariff

Available field shortcuts:
  cons, consumer, meter, meter_type, ibc, amr, dts, pmt,
  feeder, feeder_id, tariff, gic, contract, account, install
        """
    )
    parser.add_argument("query", nargs="+", help="Search term(s)")
    parser.add_argument("--field", "-f", help="Field to search in (e.g. ibc, amr, dts, feeder)")
    parser.add_argument("--limit", "-l", type=int, default=50, help="Max results to show (default: 50)")
    parser.add_argument("--exact", "-e", action="store_true", help="Exact match only")

    args = parser.parse_args()
    query = " ".join(args.query)

    results, field_searched, headers = search(query, args.field, args.limit, args.exact)
    print_results(results, field_searched, headers, query, args.limit)

if __name__ == "__main__":
    main()
