# Finance Metrics Validator

A finance-focused SQL validation and reconciliation tool that detects
common revenue-model risks and verifies totals against a ledger
baseline.

Built to demonstrate production-ready analytics engineering discipline
in financial reporting environments.

------------------------------------------------------------------------

## What This Project Does

Given: - A revenue model SQL file - A ledger dataset (CSV)

The tool:

-   Performs static SQL risk checks
-   Executes reconciliation using DuckDB
-   Compares model output to ledger baseline
-   Returns structured JSON output
-   Exits non-zero if reconciliation fails (CI-ready)

------------------------------------------------------------------------

## Why This Matters

Revenue misstatements often happen due to:

-   Missing refund logic
-   Including void/canceled invoices
-   Incorrect aggregation
-   Silent KPI definition drift

This project introduces validation + reconciliation controls to prevent
those issues before models reach production dashboards.

------------------------------------------------------------------------

## Tech Stack

-   Python
-   DuckDB
-   sqlglot (SQL parsing)
-   Pydantic (structured schemas)
-   pytest (automated testing)

------------------------------------------------------------------------

## Installation

``` bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Or:

``` bash
make install
```

------------------------------------------------------------------------

## Usage

Validate a correct model:

``` bash
finance-validate --model revenue_model
```

Demo a failure (refunds ignored):

``` bash
finance-validate --model revenue_model_bad_no_refunds
```

If reconciliation fails, the CLI exits with status code `1`.

------------------------------------------------------------------------

## Run Tests

``` bash
make test
```

or

``` bash
pytest -q
```

------------------------------------------------------------------------

## How It Works

### Static SQL Checks

Using `sqlglot`, the tool detects:

-   Missing status filters
-   Refund logic omission
-   Missing GROUP BY
-   Missing aggregation

### Reconciliation Engine

-   Loads ledger into in-memory DuckDB
-   Executes the revenue model
-   Compares totals
-   Applies configurable tolerance threshold

### Structured Reporting

Outputs deterministic JSON with:

-   Findings
-   Ledger total
-   Model total
-   Delta and delta %
-   Reconciliation status

------------------------------------------------------------------------

## Project Structure

    revenue_validator/
      cli.py
      main.py
      checks.py
      schemas.py
      utils.py
      data/
      sql/

    tests/
    docs/

------------------------------------------------------------------------

## What This Demonstrates

-   Strong SQL fluency
-   Finance-aware analytics engineering
-   Risk-based validation mindset
-   CI/CD gating via exit codes
-   Structured, test-driven development

------------------------------------------------------------------------

## Interview Pitch

I built a finance-focused SQL validation and reconciliation engine that
identifies common revenue-model risks and verifies totals against a
ledger baseline. It enforces structured output, automated tests, and
CI-compatible failure handling to reduce financial reporting risk.
