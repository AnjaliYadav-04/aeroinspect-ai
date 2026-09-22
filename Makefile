.PHONY: build up down logs shell-ai shell-backend migrate train dev-backend dev-frontend

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down -v

logs:
	docker-compose logs -f

shell-ai:
	docker-compose exec ai-engine bash

shell-backend:
	docker-compose exec backend bash

migrate:
	docker-compose exec backend alembic upgrade head

train:
	docker-compose exec ai-engine python training/train_yolo.py

# Quick local dev (no Docker for backend/frontend)
dev-backend:
	cd backend && python -m uvicorn src.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

init:
	mkdir -p backend/data storage/uploads storage/processed storage/reports ai-engine/models
	cp .env.example .env
	echo "Edit .env, then run: make build && make up"
