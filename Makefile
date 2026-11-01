.PHONY: setup lint test test-network run db-up db-reset fetch-legal stack-up stack-down stack-status

# NOTE (R5.2): `npm --prefix apps/web install` resolves package.json from the repo root on
# Windows, which broke `make setup` on a clean clone. Always `cd` into apps/web instead.

setup:
	uv sync
	cd apps/web && npm ci

fetch-legal:
	uv run python -m eriwatch_rag.corpus_manifest --download --verify

lint:
	uv run ruff check .
	uv run mypy apps/api/src packages/geo/src packages/ml/src packages/rag/src
	cd apps/web && npm run lint
	cd apps/web && npm run typecheck
	cd apps/web && npm run format:check

test:
	uv run pytest --cov=apps/api/src --cov=packages/geo/src --cov=packages/ml/src --cov=packages/rag/src --cov-report=term-missing -m "not network"
	cd apps/web && npm run test

test-network:
	uv run pytest -m "network" -v

run: stack-up

stack-up:
	docker compose -f infra/docker/docker-compose.yml up -d --build

stack-down:
	docker compose -f infra/docker/docker-compose.yml down

stack-status:
	docker compose -f infra/docker/docker-compose.yml ps
	curl -s http://localhost:8000/health
	curl -s -I http://localhost:3000/
	curl -s http://localhost:5678/healthz

db-up:
	docker compose -f infra/docker/docker-compose.yml up -d db

db-reset:
	docker compose -f infra/docker/docker-compose.yml down -v
	docker compose -f infra/docker/docker-compose.yml up -d db
