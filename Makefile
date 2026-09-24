.PHONY: dev build test lint migrate migration down

dev:
	docker compose up --build

build:
	docker compose build

test:
	docker compose run --rm backend pytest tests/ -v

lint:
	docker compose run --rm backend ruff check app/ tests/
	docker compose run --rm backend mypy app/
	cd frontend && npx tsc --noEmit

migrate:
	docker compose run --rm backend alembic upgrade head

migration:
	@read -p "Enter migration message: " MSG; \
	docker compose run --rm backend alembic revision --autogenerate -m "$$MSG"

down:
	docker compose down -v
