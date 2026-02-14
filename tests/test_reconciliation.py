from pathlib import Path
import duckdb

from revenue_validator.main import reconcile
from revenue_validator.utils import load_ledger

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "revenue_validator" / "sql"
DATA_DIR = ROOT / "revenue_validator" / "data"

def read_sql(name: str) -> str:
    return (SQL_DIR / name).read_text()

def setup_con():
    con = duckdb.connect(database=":memory:")
    load_ledger(con, DATA_DIR / "ledger.csv")
    return con

def test_good_model_reconciles():
    con = setup_con()
    rec = reconcile(con, read_sql("revenue_model.sql"), tolerance_pct=0.5)
    assert rec.within_tolerance is True
    assert rec.delta == 0.0

def test_missing_status_fails_reconciliation():
    con = setup_con()
    rec = reconcile(con, read_sql("revenue_model_bad_missing_status.sql"), tolerance_pct=0.5)
    # includes void invoice, should overstate revenue
    assert rec.within_tolerance is False
    assert rec.delta > 0

def test_no_refunds_fails_reconciliation():
    con = setup_con()
    rec = reconcile(con, read_sql("revenue_model_bad_no_refunds.sql"), tolerance_pct=0.5)
    # ignores refunds, should overstate revenue
    assert rec.within_tolerance is False
    assert rec.delta > 0

def test_alias_model_reconciles():
    con = setup_con()
    rec = reconcile(con, read_sql("revenue_model_alias.sql"), tolerance_pct=0.5)
    assert rec.within_tolerance is True
    assert rec.delta == 0.0