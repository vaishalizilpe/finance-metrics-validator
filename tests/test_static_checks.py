from pathlib import Path
from revenue_validator.checks import run_static_checks

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "revenue_validator" / "sql"

def codes(sql_file: str) -> set[str]:
    sql = (SQL_DIR / sql_file).read_text()
    return {f.code for f in run_static_checks(sql)}

def test_good_model_has_no_findings():
    assert codes("revenue_model.sql") == set()

def test_missing_status_filter_flagged():
    assert "MISSING_STATUS_FILTER" in codes("revenue_model_bad_missing_status.sql")

def test_refunds_not_accounted_flagged():
    assert "REFUNDS_NOT_ACCOUNTED" in codes("revenue_model_bad_no_refunds.sql")

def test_missing_group_by_flagged():
    assert "MISSING_GROUP_BY" in codes("revenue_model_bad_no_groupby.sql")