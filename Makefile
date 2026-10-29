.PHONY: setup lint test run db-up db-reset

setup:
	uv sync
	npm --prefix apps/web install

lint:
	uv run ruff check .
	uv run mypy apps/api/src packages/geo/src packages/ml/src packages/rag/src
	npm --prefix apps/web run lint
	npm --prefix apps/web run typecheck
	npm --prefix apps/web run format:check

test:
	uv run pytest -m "not network"
	npm --prefix apps/web run test

run:
	docker compose -f infra/docker/docker-compose.yml up -d --build

db-up:
	docker compose -f infra/docker/docker-compose.yml up -d db

db-reset:
	docker compose -f infra/docker/docker-compose.yml down -v
	docker compose -f infra/docker/docker-compose.yml up -d db
