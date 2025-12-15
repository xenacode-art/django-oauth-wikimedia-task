@echo off
REM Run all checks on Windows

echo ========================================
echo Running Tests
echo ========================================
pytest

echo.
echo ========================================
echo Running Security Checks
echo ========================================
bandit -r src/ -c .bandit
safety check --json 2>nul

echo.
echo ========================================
echo Running Type Checks
echo ========================================
mypy src/ --config-file=mypy.ini

echo.
echo ========================================
echo All checks completed!
echo ========================================
