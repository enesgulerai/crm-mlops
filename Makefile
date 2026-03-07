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
	@echo " Kubernetes Commands:"
	@echo "   make k8s-up  : Applies all manifests in the k8s directory"
	@echo "   make k8s-down: Deletes all resources defined in the k8s directory"
	@echo "   make k8s-status: Shows the current status of pods, services, and deployments"
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

######################
# KUBERNETES
######################
k8s-build:
	docker build -t crm-mlops-api:latest -f docker/backend/Dockerfile .
	docker build -t crm-mlops-ui:latest -f docker/frontend/Dockerfile .

######################
# HELM
######################
helm-up: k8s-build
	helm upgrade --install crm-mlops-release ./crm-mlops-chart

helm-down:
	helm uninstall crm-mlops-release

helm-status:
	helm list
	kubectl get pods,svc,deployments