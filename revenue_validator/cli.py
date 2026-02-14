from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb
from rich import print
import sys

from .checks import run_static_checks
from .schemas import Report
from .utils import load_ledger
from .main import reconcile

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser(description="Validate finance revenue SQL and reconcile against ledger.")
    p.add_argument("--model", default="revenue_model", help="SQL model name without .sql (in revenue_validator/sql/)")
    p.add_argument("--tolerance-pct", type=float, default=0.5, help="Reconciliation tolerance percent (default: 0.5)")
    p.add_argument("--ledger", default=str(ROOT / "revenue_validator" / "data" / "ledger.csv"), help="Path to ledger CSV")
    p.add_argument("--out", default=None, help="Output report path (json). Default: revenue_validator/output/<model>_report.json")
    args = p.parse_args()

    if args.tolerance_pct < 0:
        raise ValueError("tolerance-pct must be >= 0")

    model_sql_path = ROOT / "revenue_validator" / "sql" / f"{args.model}.sql"
    if not model_sql_path.exists():
        raise FileNotFoundError(f"Model SQL not found: {model_sql_path}")

    model_sql = model_sql_path.read_text()
    findings = run_static_checks(model_sql)

    con = duckdb.connect(database=":memory:")
    load_ledger(con, Path(args.ledger))

    rec = reconcile(con, model_sql, tolerance_pct=args.tolerance_pct)
    report = Report(model_name=args.model, findings=findings, reconciliation=rec)

    out_path = Path(args.out) if args.out else (ROOT / "revenue_validator" / "output" / f"{args.model}_report.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report.model_dump(), indent=2))
    

    print(f"[bold cyan]Model:[/bold cyan] {args.model}")
    print(f"[bold cyan]Tolerance:[/bold cyan] {args.tolerance_pct}%")
    print(json.dumps(report.model_dump(), indent=2))

    if not rec.within_tolerance:
        sys.exit(1)
if __name__ == "__main__":
    main()