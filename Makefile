
.PHONY: lint type test check

lint:
	uv run ruff check .
	uv run ruff format --check .

type:
	uv run mypy

test:
	uv run pytest -q

check: lint type test


# we can directly run make check instead of running all commands again and again after every check
# Makefile is useful for Linux environments and CI pipelines if the roadmap expects it.