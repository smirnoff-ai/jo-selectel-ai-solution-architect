.PHONY: mock mock-test mock-lint env up down dev-backend dev-frontend test-backend lint-backend lint-frontend migrate accept

env:
	bash scripts/write-env-from-keychain.sh

up: env
	docker compose up --build

down:
	docker compose down

mock:
	cd mock-severholod && uv run uvicorn mock_severholod.app:app --host 0.0.0.0 --port 8080

mock-test:
	cd mock-severholod && uv run pytest

mock-lint:
	cd mock-severholod && uv run ruff check src tests && uv run ruff format --check src tests

dev-backend:
	bash scripts/write-env-from-keychain.sh local
	cd backend && uv run uvicorn backend.app:create_app --factory --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && BACKEND_URL=http://127.0.0.1:8000 pnpm dev --port 3000

migrate:
	cd backend && PYTHONPATH=src uv run alembic upgrade head

test-backend:
	cd backend && uv run pytest

lint-backend:
	cd backend && uv run ruff check src tests && uv run ruff format --check src tests

lint-frontend:
	cd frontend && pnpm lint

accept:
	cd backend && uv run python ../scripts/accept_s1_s4.py
