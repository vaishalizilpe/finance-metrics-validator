.PHONY: install test demo clean

install:
	pip install -e .
	pip install pytest

test:
	pytest -q

demo:
	finance-validate --model revenue_model
	finance-validate --model revenue_model_bad_no_refunds || true

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -rf .pytest_cache