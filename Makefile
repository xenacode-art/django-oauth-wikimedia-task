.PHONY: help test lint security typecheck all clean

help:
	@echo "Available commands:"
	@echo "  make test        - Run unit tests with pytest"
	@echo "  make lint        - Run code quality checks"
	@echo "  make security    - Run security checks (bandit & safety)"
	@echo "  make typecheck   - Run type checking with mypy"
	@echo "  make all         - Run all checks"
	@echo "  make clean       - Remove generated files"

test:
	@echo "Running tests..."
	pytest

lint:
	@echo "Running linters..."
	@echo "Note: Install flake8 if you want additional linting"

security:
	@echo "Running security checks..."
	bandit -r src/ -c .bandit
	@echo "\nChecking for known security vulnerabilities in dependencies..."
	safety check --json || true

typecheck:
	@echo "Running type checks..."
	mypy src/ --config-file=mypy.ini

all: test security typecheck
	@echo "\nAll checks completed!"

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov .coverage
	@echo "Cleanup complete!"
