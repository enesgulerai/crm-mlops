.PHONY: help up down test lint format

######################
# HELP MENU (DEFAULT)
######################
help:
	@echo "================================================================="
	@echo " CRM MLOps Project - Makefile Commands"
	@echo "================================================================="
	@echo " Docker Commands:"
	@echo "   make up      : Builds and starts the system (API, Redis)"
	@echo "   make down    : Stops and removes all running containers"
	@echo ""
	@echo " Testing Commands:"
	@echo "   make test    : Runs all tests using pytest"
	@echo ""
	@echo " Code Quality (Ruff):"
	@echo "   make lint    : Scans for errors and unused imports"
	@echo "   make format  : Formats code to industry standards"
	@echo "================================================================="

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