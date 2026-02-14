import duckdb
from pathlib import Path

def load_ledger(con: duckdb.DuckDBPyConnection, ledger_csv_path: Path) -> None:
    con.execute("""
        CREATE OR REPLACE TABLE ledger AS
        SELECT * FROM read_csv_auto(?, header=True);
    """, [str(ledger_csv_path)])