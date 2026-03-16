.PHONY: up down restart logs logs-be logs-fe restart-be restart-fe format lint test-be migrate-up migrate-down migrate-create migrate-history shell-be shell-fe clean

up:
	docker compose up -d

down:
	docker compose down

restart: down up

logs:
	docker compose logs -f

logs-be:
	docker compose logs -f backend

logs-fe:
	docker compose logs -f frontend

logs-db:
	docker compose logs -f db

logs-keycloak:
	docker compose logs -f keycloak

restart-be:
	docker compose restart backend

restart-fe:
	docker compose restart frontend

format:
	cd backend && black app/ && isort app/
	cd frontend && npm run format

lint:
	cd backend && ruff check app/
	cd frontend && npm run lint

test-be:
	cd backend && pytest

migrate-up:
	docker compose exec backend alembic upgrade head

migrate-down:
	docker compose exec backend alembic downgrade -1

migrate-create:
	@if [ -z "$(MSG)" ]; then \
		echo "Usage: make migrate-create MSG='your message'"; \
		exit 1; \
	fi
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"

migrate-history:
	docker compose exec backend alembic history

shell-be:
	docker compose exec backend bash

shell-fe:
	docker compose exec frontend sh

shell-db:
	docker compose exec db psql -U atlas -d atlas_db

clean:
	docker compose down -v
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/.next frontend/node_modules

help:
	@echo "Available commands:"
	@echo "  make up              - Start all services"
	@echo "  make down            - Stop all services"
	@echo "  make logs            - View all logs"
	@echo "  make logs-be         - View backend logs"
	@echo "  make logs-fe         - View frontend logs"
	@echo "  make restart-be      - Restart backend"
	@echo "  make restart-fe      - Restart frontend"
	@echo "  make format          - Format all code"
	@echo "  make lint            - Lint all code"
	@echo "  make test-be         - Run backend tests"
	@echo "  make migrate-up      - Apply pending migrations"
	@echo "  make migrate-down    - Rollback one migration"
	@echo "  make migrate-create  - Create new migration (use MSG='...')"
	@echo "  make migrate-history - View migration history"
	@echo "  make shell-be        - Open backend shell"
	@echo "  make shell-fe        - Open frontend shell"
	@echo "  make shell-db        - Open database shell"
	@echo "  make clean           - Clean all containers and volumes"
