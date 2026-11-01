.PHONY: setup lint test test-network run db-up db-reset

# NOTE (R5.2): `npm --prefix apps/web install` resolves package.json from the repo root on
# Windows, which broke `make setup` on a clean clone. Always `cd` into apps/web instead.

setup:
	uv sync
	cd apps/web && npm ci

lint:
	uv run ruff check .
	uv run mypy apps/api/src packages/geo/src packages/ml/src packages/rag/src
	cd apps/web && npm run lint
	cd apps/web && npm run typecheck
	cd apps/web && npm run format:check

test:
	uv run pytest -m "not network"
	cd apps/web && npm run test

test-network:
	uv run pytest -m "network" -v

run:
	docker compose -f infra/docker/docker-compose.yml up -d --build

db-up:
	docker compose -f infra/docker/docker-compose.yml up -d db

db-reset:
	docker compose -f infra/docker/docker-compose.yml down -v
	docker compose -f infra/docker/docker-compose.yml up -d db
