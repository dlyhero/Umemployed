.PHONY: setup clean test lint format migrate run docker docker-down help

# Variables
PYTHON = python
PIP = pip
MANAGE = $(PYTHON) manage.py
PYTEST = pytest
FLAKE8 = flake8
BLACK = black
ISORT = isort

help:
	@echo "Available commands:"
	@echo "  make setup         - Install dependencies and set up database"
	@echo "  make clean         - Remove Python cache files"
	@echo "  make test          - Run test suite"
	@echo "  make lint          - Run code linting"
	@echo "  make format        - Format code with Black and isort"
	@echo "  make migrate       - Run database migrations"
	@echo "  make run           - Run development server"
	@echo "  make docker        - Run application with Docker"
	@echo "  make docker-down   - Stop Docker containers"

setup:
	$(PIP) install -r requirements.txt
	$(MANAGE) migrate

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".tox" -exec rm -rf {} +
	find . -type f -name ".coverage*" -delete
	rm -rf build/
	rm -rf dist/

test:
	$(PYTEST)

test-coverage:
	$(PYTEST) --cov=. --cov-report=html

lint:
	$(FLAKE8)

format:
	$(BLACK) .
	$(ISORT) .

migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

run:
	$(MANAGE) runserver

celery:
	celery -A umemployed worker -l info

docker:
	docker-compose up -d

docker-down:
	docker-compose down
