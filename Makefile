.PHONY: up down test lint format

######################
# DOCKER
######################
up:
	docker-compose up -d --build

down:
	docker-compose down

######################
# TEST
######################
test:
	pytest tests/ -v

######################
# FORMAT
######################
lint:
	ruff check .

format:
	ruff format .
