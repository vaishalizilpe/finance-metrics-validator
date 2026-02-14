from __future__ import annotations
from typing import List
import sqlglot
from sqlglot import exp
from .schemas import Finding

def _has_where_filter(ast: exp.Expression, column: str) -> bool:
    where = ast.find(exp.Where)
    if not where:
        return False
    # crude but effective for MVP: look for column name in WHERE
    where_sql = where.sql(dialect="duckdb").lower()
    return column.lower() in where_sql

def _has_group_by(ast: exp.Expression) -> bool:
    return ast.find(exp.Group) is not None

def _references_table(ast: exp.Expression, table: str) -> bool:
    for t in ast.find_all(exp.Table):
        if t.name.lower() == table.lower():
            return True
    return False

def _uses_sum(ast: exp.Expression) -> bool:
    for fn in ast.find_all(exp.Anonymous):
        if fn.name.lower() == "sum":
            return True
    for fn in ast.find_all(exp.Sum):
        return True
    return False

def run_static_checks(sql: str) -> List[Finding]:
    findings: List[Finding] = []

    try:
        ast = sqlglot.parse_one(sql, read="duckdb")
    except Exception as e:
        return [Finding(code="SQL_PARSE_ERROR", severity="high", message="SQL failed to parse", evidence=str(e))]

    # 1) Must reference ledger (for this MVP)
    if not _references_table(ast, "ledger"):
        findings.append(Finding(
            code="MISSING_LEDGER_TABLE",
            severity="high",
            message="Model does not reference required table: ledger",
        ))

    # 2) Must aggregate with SUM
    if not _uses_sum(ast):
        findings.append(Finding(
            code="MISSING_SUM_AGG",
            severity="high",
            message="Model does not appear to aggregate using SUM(). Revenue models typically require aggregation.",
        ))

    # 3) Should group by month if selecting service_month
    # MVP heuristic: if service_month appears, require GROUP BY
    sql_lower = sql.lower()
    if "service_month" in sql_lower and not _has_group_by(ast):
        findings.append(Finding(
            code="MISSING_GROUP_BY",
            severity="high",
            message="Model references service_month but has no GROUP BY. High risk of wrong totals.",
        ))

    # 4) Should filter out void/canceled using status
    if not _has_where_filter(ast, "status"):
        findings.append(Finding(
            code="MISSING_STATUS_FILTER",
            severity="medium",
            message="No obvious status filter found. Finance revenue models usually exclude void/canceled invoices.",
            evidence="Expected something like WHERE status = 'paid'."
        ))

    # 5) Should net out refunds
    if "refund_amount" not in sql_lower:
        findings.append(Finding(
            code="REFUNDS_NOT_ACCOUNTED",
            severity="medium",
            message="refund_amount not found in SQL. Revenue may be overstated if refunds exist.",
        ))

    return findings