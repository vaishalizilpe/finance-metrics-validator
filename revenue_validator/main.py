from __future__ import annotations
import json
from pathlib import Path
import duckdb
from rich import print

from .checks import run_static_checks
from .schemas import Report, ReconciliationResult
from .utils import load_ledger

ROOT = Path(__file__).resolve().parents[1]

def reconcile(con: duckdb.DuckDBPyConnection, model_sql: str, tolerance_pct: float = 0.5) -> ReconciliationResult:
    # Ledger “ground truth” for MVP: paid net of refunds
    ledger_total = con.execute("""
        SELECT COALESCE(SUM(invoice_amount - refund_amount), 0)::DOUBLE AS total
        FROM ledger
        WHERE status = 'paid';
    """).fetchone()[0]

    # Model total: sum of recognized_revenue over months (assumes column name exists)
    # remove trailing semicolon if present
	    # Model total: sum of recognized_revenue over months (assumes column name exists)
    # remove trailing semicolon if present
    model_sql_clean = model_sql.strip().rstrip(";")

    # Run model once to inspect columns
    model_df = con.execute(f"""
        WITH model AS (
            {model_sql_clean}
        )
        SELECT * FROM model
        LIMIT 1
    """).df()

    if model_df.empty:
        # No rows: model_total is 0, but still compute safely
        model_total = 0.0
    else:
        # Prefer a column named recognized_revenue if present
        cols = list(model_df.columns)
        preferred = "recognized_revenue" if "recognized_revenue" in cols else None

        # Otherwise pick the first numeric column
        numeric_cols = [c for c in cols if str(model_df[c].dtype).startswith(("int", "float"))]
        target_col = preferred or (numeric_cols[0] if numeric_cols else None)

        if target_col is None:
            raise ValueError(
                f"Model output has no numeric columns to sum. Columns={cols}. "
                "Ensure the model outputs a numeric revenue column."
            )

        model_total = con.execute(f"""
            WITH model AS (
                {model_sql_clean}
            )
            SELECT COALESCE(SUM({target_col}), 0)::DOUBLE
            FROM model
        """).fetchone()[0]

    delta = model_total - ledger_total
    delta_pct = 0.0 if ledger_total == 0 else (abs(delta) / abs(ledger_total)) * 100.0
    within = delta_pct <= tolerance_pct

    return ReconciliationResult(
        ledger_total=float(ledger_total),
        model_total=float(model_total),
        delta=float(delta),
        delta_pct=float(delta_pct),
        within_tolerance=bool(within),
        tolerance_pct=float(tolerance_pct),
    )

def run(model_name: str = "revenue_model") -> None:
    ledger_csv = ROOT / "revenue_validator" / "data" / "ledger.csv"
    model_sql_path = ROOT / "revenue_validator" / "sql" / f"{model_name}.sql"
    out_path = ROOT / "revenue_validator" / "output" / f"{model_name}_report.json"

    model_sql = model_sql_path.read_text()

    findings = run_static_checks(model_sql)

    con = duckdb.connect(database=":memory:")
    load_ledger(con, ledger_csv)

    rec = reconcile(con, model_sql, tolerance_pct=0.5)

    report = Report(model_name=model_name, findings=findings, reconciliation=rec)

    out_path.write_text(json.dumps(report.model_dump(), indent=2))
    print(f"[green]Wrote report:[/green] {out_path}")
    print(report.model_dump())

if __name__ == "__main__":
    run()