.PHONY: mock mock-test mock-lint env up obs down dev-backend dev-frontend test-backend lint-backend lint-frontend migrate accept demo

DEMO_OUT ?= /opt/cursor/artifacts

env:
	bash scripts/write-env-from-keychain.sh

up:
	bash scripts/ensure-env.sh
	docker compose up --build -d --wait postgres mock-severholod backend frontend

obs:
	bash scripts/ensure-env.sh
	docker compose up --build -d --wait

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
	docker compose exec -T \
		-e ACCEPT_BASE=http://127.0.0.1:8000 \
		-e ACCEPT_REPORT=/tmp/accept-s1-s4.json \
		backend python /app/scripts/accept_s1_s4.py

demo:
	@out="$(DEMO_OUT)"; \
	if ! mkdir -p "$$out" 2>/dev/null; then \
		out=/tmp/reflex-interview-demo; \
		mkdir -p "$$out"; \
		echo "DEMO_OUT fallback: $$out"; \
	fi; \
	cd frontend && PATH="$(HOME)/.local/bin:$$PATH" DEMO_OUT="$$out" node scripts/interview-demo.mjs; \
	cp "$$out/interview-demo.mp4" docs/sprints/sprint-08-agent-voice/demo.mp4
