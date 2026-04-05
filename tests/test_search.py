"""
PSC Consumer Record Search Tool — Test Suite
============================================
Covers all functional requirements (FR-01 through FR-09), NFR-04 error handling,
and all 10 user scenarios from spec.md.

Run with:
    python -m pytest tests/ -v
    python -m pytest tests/ --cov=search --cov-report=term-missing
"""

import csv
import io
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Ensure repo root is on sys.path so 'search' module can be imported
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

import search as search_module
from search import FIELD_ALIASES, detect_field, print_results, search

FIXTURE_CSV = str(REPO_ROOT / "tests" / "fixtures" / "sample.csv")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_search(query, field=None, limit=50, exact=False):
    """Run search() against the fixture CSV."""
    with patch.object(search_module, "CSV_FILE", FIXTURE_CSV):
        return search(query, field=field, limit=limit, exact=exact)


def capture_print_results(results, field_searched, headers, query, limit):
    """Capture stdout from print_results()."""
    buf = io.StringIO()
    with patch("sys.stdout", buf):
        print_results(results, field_searched, headers, query, limit)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Phase 3 — US1: Consumer Number Search
# ---------------------------------------------------------------------------

class TestConsumerNumberSearch:
    """US1 — Scenario 1: Search by Consumer Number (FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-07)"""

    def test_exact_consumer_no(self):
        """T006 — Exact consumer number returns the correct single record."""
        results, field, _ = make_search("BL001271")
        assert len(results) == 1
        assert results[0]["Cons_No"] == "BL001271"
        assert field == "Cons_No"

    def test_partial_consumer_no(self):
        """T007 — Partial consumer number returns all matching records."""
        results, field, _ = make_search("BL00")
        # Fixture has BL001271, BL002500, BL003999
        cons_nos = [r["Cons_No"] for r in results]
        assert "BL001271" in cons_nos
        assert "BL002500" in cons_nos
        assert "BL003999" in cons_nos
        assert field == "Cons_No"

    def test_search_case_insensitive(self):
        """T008 — Search is case-insensitive."""
        results_upper, _, _ = make_search("BL001271")
        results_lower, _, _ = make_search("bl001271")
        assert len(results_upper) == len(results_lower)
        assert results_upper[0]["Cons_No"] == results_lower[0]["Cons_No"]

    def test_exact_flag_restricts_results(self):
        """T009 — --exact flag returns only exact-value matches."""
        # Partial 'BL00' without --exact finds multiple BL rows (BL001271, BL002500, BL003999)
        results_partial, _, _ = make_search("BL00", exact=False)
        assert len(results_partial) > 1

        # With --exact, 'BL00' matches nothing (no Cons_No is exactly 'BL00')
        results_exact_partial, _, _ = make_search("BL00", exact=True)
        assert len(results_exact_partial) == 0

        # Exact full consumer number matches exactly one
        results_exact_full, _, _ = make_search("BL001271", exact=True)
        assert len(results_exact_full) == 1

    def test_auto_detect_consumer_no_pattern(self):
        """T010 — detect_field correctly identifies consumer number pattern."""
        assert detect_field("BL001271") == "Cons_No"
        assert detect_field("DP002726") == "Cons_No"
        assert detect_field("KH001001") == "Cons_No"
        assert detect_field("ML005000") == "Cons_No"

    def test_output_contains_required_columns(self):
        """T011 — Search result dicts contain all 11 required display columns."""
        required_cols = [
            "Cons_No", "Contract_Ac", "Meter_No", "Meter_Typ", "Tariff",
            "IBC_Name", "AMR_STATUS", "DTS_ID", "PMT_Name", "Feeder_Name", "FeederID"
        ]
        results, _, _ = make_search("BL001271")
        assert len(results) >= 1
        for col in required_cols:
            assert col in results[0], f"Missing column: {col}"


# ---------------------------------------------------------------------------
# Phase 4 — US9: No Results Feedback (FR-08)
# ---------------------------------------------------------------------------

class TestNoResultsFeedback:
    """US9 — Scenario 9: No results found state."""

    def test_no_results_returns_empty_list(self):
        """T012 — Search for non-existent value returns empty list, not an error."""
        results, field, headers = make_search("ZZZNOMATCH_XYZABC")
        assert results == []
        assert headers is not None  # headers still returned

    def test_no_results_message_contains_tip(self):
        """T013 — Zero-result output includes 'No results' text and at least one tip."""
        results, field, headers = make_search("ZZZNOMATCH_XYZABC")
        output = capture_print_results(results, field, headers, "ZZZNOMATCH_XYZABC", 50)
        assert "No results" in output or "no results" in output.lower()
        assert "Tips" in output or "tips" in output.lower() or "--field" in output


# ---------------------------------------------------------------------------
# Phase 5 — US10: Limit Control (FR-05)
# ---------------------------------------------------------------------------

class TestLimitControl:
    """US10 — Scenario 10: Result limit and truncation notice."""

    def test_limit_truncates_results(self):
        """T014 — --limit 2 returns at most 2 rows even when more match."""
        # JOHAR IBC has BL001271, BL002500, BL003999, LY009999 — 4 rows
        results, _, _ = make_search("JOHAR", field="ibc", limit=2)
        assert len(results) == 2

    def test_truncation_notice_in_output(self):
        """T015 — Output contains --limit hint when results were truncated."""
        results, field, headers = make_search("JOHAR", field="ibc", limit=2)
        output = capture_print_results(results, field, headers, "JOHAR", 2)
        assert "--limit" in output or "limit" in output.lower()


# ---------------------------------------------------------------------------
# Phase 6 — US2: DTS ID Search (FR-01, FR-02)
# ---------------------------------------------------------------------------

class TestDTSSearch:
    """US2 — Scenario 2: Search by DTS ID."""

    def test_detect_field_dts_pattern(self):
        """T016 — detect_field identifies 4–7 digit strings as DTS_ID."""
        assert detect_field("508214") == "DTS_ID"
        assert detect_field("526271") == "DTS_ID"
        assert detect_field("530000") == "DTS_ID"

    def test_search_by_dts_field(self):
        """T017 — Searching by DTS ID returns all consumers on that DTS."""
        results, field, _ = make_search("508214", field="dts")
        assert field == "DTS_ID"
        # Fixture: BL001271, BL002500, LY009999 all share DTS 508214
        assert len(results) >= 2
        for r in results:
            assert r["DTS_ID"].strip() == "508214"


# ---------------------------------------------------------------------------
# Phase 7 — US3–US8: Field-Specific Searches (FR-01, FR-03, FR-04)
# ---------------------------------------------------------------------------

class TestFeederSearch:
    """US3 — Scenario 3: Search by Feeder Name or ID."""

    def test_search_by_feeder_partial(self):
        """T018 — Partial feeder name match returns matching rows."""
        results, field, _ = make_search("A.D.B.P", field="feeder")
        assert field == "Feeder_Name"
        assert len(results) >= 1
        for r in results:
            assert "A.D.B.P" in r["Feeder_Name"]


class TestIBCSearch:
    """US4 — Scenario 4: Search by IBC Name."""

    def test_search_by_ibc_exact_field(self):
        """T019 — Searching by IBC field returns all consumers in that IBC."""
        results, field, _ = make_search("JOHAR", field="ibc")
        assert field == "IBC_Name"
        assert len(results) >= 3
        for r in results:
            assert r["IBC_Name"].strip().upper() == "JOHAR"

    def test_search_ibc_full_text_fallback(self):
        """T020 — 'JOHAR' with no --field falls back to full-text and finds IBC matches."""
        results, field, _ = make_search("JOHAR")
        # field may be None (full-text) — results should still include JOHAR rows
        johar_rows = [r for r in results if "JOHAR" in r.get("IBC_Name", "").upper()]
        assert len(johar_rows) >= 1


class TestAMRSearch:
    """US5 — Scenario 5: Filter by AMR Status."""

    def test_search_by_amr_status(self):
        """T021 — Filtering by AMR status returns only matching rows."""
        results, field, _ = make_search("AMR", field="amr")
        assert field == "AMR_STATUS"
        for r in results:
            assert "AMR" in r["AMR_STATUS"].upper()

    def test_detect_field_amr_keyword(self):
        """T022 — detect_field recognises AMR keyword."""
        assert detect_field("AMR") == "AMR_STATUS"
        assert detect_field("INACTIVE") in ("AMR_STATUS", "Meter_Typ")  # dual keyword


class TestMeterTypeSearch:
    """US6 — Scenario 6: Filter by Meter Type."""

    def test_search_by_meter_type(self):
        """T023 — Filtering by meter_type returns CTO meter rows."""
        results, field, _ = make_search("CTO", field="meter_type")
        assert field == "Meter_Typ"
        assert len(results) >= 1
        for r in results:
            assert r["Meter_Typ"].strip().upper() == "CTO"


class TestTariffSearch:
    """US7 — Scenario 7: Search by Tariff."""

    def test_search_by_tariff(self):
        """T024 — Filtering by tariff returns matching rows."""
        results, field, _ = make_search("A3-G", field="tariff")
        assert field == "Tariff"
        assert len(results) >= 1
        for r in results:
            assert r["Tariff"].strip() == "A3-G"

    def test_detect_field_tariff_pattern(self):
        """T025 — detect_field identifies tariff pattern (letter + digit + separator + letter).
        Matches: A3-G, A1-R, C1-G format.  E-1_I does not match this pattern (no leading digit).
        """
        assert detect_field("A3-G") == "Tariff"
        assert detect_field("A1-R") == "Tariff"
        assert detect_field("C1-G") == "Tariff"
        # E-1_I starts with letter-separator (no digit in position 1); returns None (full-text)
        assert detect_field("E-1_I") is None


class TestPMTSearch:
    """US8 — Scenario 8: Search by PMT Name."""

    def test_search_by_pmt_name(self):
        """T026 — Searching by PMT name returns matching rows."""
        results, field, _ = make_search("HAROON JAFFAR", field="pmt")
        assert field == "PMT_Name"
        assert len(results) >= 1
        for r in results:
            assert "HAROON JAFFAR" in r["PMT_Name"].upper()


# ---------------------------------------------------------------------------
# Phase 8 — Error Handling Tests (NFR-04)
# ---------------------------------------------------------------------------

class TestErrorHandling:
    """T027 — NFR-04: Error conditions map to correct stderr messages and exit codes."""

    def test_missing_csv_triggers_exit_1(self):
        """Missing CSV file prints error to stderr and exits with code 1."""
        nonexistent = str(REPO_ROOT / "tests" / "fixtures" / "DOES_NOT_EXIST.csv")
        with patch.object(search_module, "CSV_FILE", nonexistent):
            with patch("sys.stderr", io.StringIO()) as mock_err:
                try:
                    search("BL001271")
                    assert False, "Expected SystemExit"
                except SystemExit as e:
                    assert e.code == 1
                    mock_err.seek(0)
                    err_text = mock_err.read()
                    assert "ERROR" in err_text
                    assert "not found" in err_text.lower() or "DOES_NOT_EXIST" in err_text

    def test_unknown_field_alias_triggers_exit_1(self):
        """Unknown field alias prints error to stderr and exits with code 1."""
        with patch.object(search_module, "CSV_FILE", FIXTURE_CSV):
            with patch("sys.stderr", io.StringIO()) as mock_err:
                try:
                    search("test", field="nonexistent_field_xyz")
                    assert False, "Expected SystemExit"
                except SystemExit as e:
                    assert e.code == 1
                    mock_err.seek(0)
                    err_text = mock_err.read()
                    assert "ERROR" in err_text
                    assert "Unknown field" in err_text or "unknown" in err_text.lower()


# ---------------------------------------------------------------------------
# Alias Resolution (FR-07)
# ---------------------------------------------------------------------------

class TestAliasResolution:
    """T005 — FR-07: All field aliases resolve to canonical column names."""

    ALIAS_MAP = {
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
        "dts":         "DTS_ID",
        "dts_id":      "DTS_ID",
        "pmt":         "PMT_Name",
        "pmt_name":    "PMT_Name",
        "feeder":      "Feeder_Name",
        "feeder_name": "Feeder_Name",
        "feeder_id":   "FeederID",
        "feederid":    "FeederID",
        "cm":          "CM_No",
        "cm_no":       "CM_No",
    }

    def test_all_aliases_resolve_correctly(self):
        """T005 — Every alias in FIELD_ALIASES maps to its documented canonical column."""
        for alias, expected_col in self.ALIAS_MAP.items():
            resolved = FIELD_ALIASES.get(alias.lower())
            assert resolved == expected_col, (
                f"Alias '{alias}' should resolve to '{expected_col}', got '{resolved}'"
            )


# ---------------------------------------------------------------------------
# Auto-Detection — Extended (FR-02)
# ---------------------------------------------------------------------------

class TestAutoDetection:
    """Extended auto-detect tests beyond US1/US2 coverage."""

    def test_detect_contract_account(self):
        assert detect_field("400002018827") == "Contract_Ac"

    def test_detect_install_no(self):
        assert detect_field("7000203015") == "Install_No"

    def test_detect_meter_no_cto_prefix(self):
        assert detect_field("CTO-40295") == "Meter_No"

    def test_detect_gic_code(self):
        assert detect_field("D0701") == "GIC_Code"

    def test_detect_amr_keyword_non_amr(self):
        assert detect_field("NON AMR") == "AMR_STATUS"

    def test_detect_unknown_returns_none(self):
        """Unknown patterns return None → full-text fallback."""
        assert detect_field("JOHAR") is None
        assert detect_field("HAROON JAFFAR") is None
        assert detect_field("A.D.B.P S/S") is None


# ---------------------------------------------------------------------------
# Full-Text Fallback (FR-09)
# ---------------------------------------------------------------------------

class TestFullTextFallback:
    """FR-09 — When no field detected and no --field given, all fields are searched."""

    def test_full_text_finds_pmt_name(self):
        results, field, _ = make_search("HAROON JAFFAR")
        assert field is None  # no specific field detected
        assert len(results) >= 1
        pmt_rows = [r for r in results if "HAROON JAFFAR" in r.get("PMT_Name", "").upper()]
        assert len(pmt_rows) >= 1

    def test_full_text_zero_results(self):
        results, _, _ = make_search("ZZZNOMATCH999XYZ")
        assert results == []


# ---------------------------------------------------------------------------
# Coverage gap closers (lines 107, 174, 214-242)
# ---------------------------------------------------------------------------

class TestCoverageGaps:
    """Close coverage gaps identified from first run."""

    def test_detect_field_meter_typ_keywords(self):
        """Line 107 — Meter_Typ keyword detection for HOOK and THREE."""
        assert detect_field("HOOK") == "Meter_Typ"
        assert detect_field("THREE") == "Meter_Typ"

    def test_no_results_with_field_prints_field_name(self):
        """Line 174 — When zero results and a field was searched, that field name is printed."""
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            print_results([], "IBC_Name", ["Cons_No", "IBC_Name"], "ZZZNOMATCH", 50)
        output = buf.getvalue()
        assert "IBC_Name" in output

    def test_main_cli_via_subprocess(self):
        """Lines 214-242 — main() runs end-to-end via CLI subprocess."""
        import subprocess
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "search.py"), "BL001271"],
            env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
            capture_output=True,
            text=True,
        )
        # Should exit 0 and print the consumer record
        assert result.returncode == 0
        assert "BL001271" in result.stdout

    def test_main_cli_no_results(self):
        """main() exits 0 for a valid query that returns no results."""
        import subprocess
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "search.py"), "ZZZNOMATCH999XYZ"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "No results" in result.stdout or "no results" in result.stdout.lower()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
