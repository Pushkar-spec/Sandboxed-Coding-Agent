$ErrorActionPreference = "Stop"

Write-Host "`n=== Lint ===" -ForegroundColor Cyan
uv run ruff check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== Type check ===" -ForegroundColor Cyan
uv run mypy
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== Tests ===" -ForegroundColor Cyan
uv run pytest -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`nAll checks passed!" -ForegroundColor Green