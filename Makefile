.PHONY: mock mock-test mock-lint

mock:
	cd mock-severholod && uv run uvicorn mock_severholod.app:app --host 0.0.0.0 --port 8080

mock-test:
	cd mock-severholod && uv run pytest

mock-lint:
	cd mock-severholod && uv run ruff check src tests && uv run ruff format --check src tests
