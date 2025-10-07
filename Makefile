.PHONY: install install-dev test lint format clean help

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package in production mode
	. .venv/bin/activate && uv pip install -e .

install-dev:  ## Install the package with development dependencies
	. .venv/bin/activate && uv pip install -e ".[dev]"

sync:  ## Sync dependencies (create/update venv)
	uv venv
	. .venv/bin/activate && uv pip install -e ".[dev]"

test:  ## Run tests
	. .venv/bin/activate && pytest tests/ -v

test-cov:  ## Run tests with coverage
	. .venv/bin/activate && pytest tests/ -v --cov=src/command_line_agent --cov-report=html --cov-report=term

lint:  ## Run linting checks
	. .venv/bin/activate && ruff check src/ tests/

lint-fix:  ## Fix linting issues automatically
	. .venv/bin/activate && ruff check --fix src/ tests/

format:  ## Format code with black
	. .venv/bin/activate && black src/ tests/

format-check:  ## Check code formatting
	. .venv/bin/activate && black --check src/ tests/

clean:  ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:  ## Run the agent in interactive mode
	. .venv/bin/activate && python command_line_agent.py

run-query:  ## Run a single query (use QUERY="your question")
	. .venv/bin/activate && python command_line_agent.py "$(QUERY)"

venv:  ## Create virtual environment with uv
	uv venv

upgrade:  ## Upgrade all dependencies
	. .venv/bin/activate && uv pip install --upgrade -e ".[dev]"
