# Simple Makefile for sb-cli development
.PHONY: install test test-unit test-integration coverage lint type-check format clean help

# Development setup
install:
	pip install -e ".[dev]"

# Testing
test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

coverage:
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

# Code quality
lint:
	ruff check src/ tests/

lint-fix:
	ruff check --fix src/ tests/

check:
	mypy src/

format:
	ruff format src/ tests/

fmt: format lint-fix

# Combined checks
ci: lint check coverage
	@echo "✅ All checks passed!"

# Maintenance
clean:
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ htmlcov/ .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

help:
	@echo "Available commands:"
	@echo "  install        	- Install package in development mode"
	@echo "  test           	- Run all tests"
	@echo "  test-unit      	- Run unit tests only"
	@echo "  test-integration 	- Run integration tests only"
	@echo "  coverage       	- Run tests with coverage report"
	@echo "  lint           	- Run linting checks"
	@echo "  lint-fix       	- Auto-fix linting issues"
	@echo "  check			- Run type checking"
	@echo "  format         	- Format code"
	@echo "  fmt         		- Format code and fix linting issues"
	@echo "  ci			- Run all quality checks"
	@echo "  clean          	- Clean temporary files"
	@echo "  help           	- Show this help"
