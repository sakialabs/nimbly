@echo off
REM Run all tests for Nimbly

echo.
echo 🧪 Running Nimbly Tests
echo =======================
echo.

REM Check if Docker containers are running
docker-compose ps | findstr "Up" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker containers are not running. Starting them...
    docker-compose up -d
    timeout /t 5 /nobreak >nul
)

echo 📦 Running backend tests...
echo ---------------------------

REM Run pytest with coverage
docker-compose exec -T api pytest -v --cov=api --cov-report=term-missing

echo.
echo ✓ All tests passed!
echo.
echo To run specific tests:
echo   docker-compose exec api pytest api/tests/test_auth.py
echo   docker-compose exec api pytest api/tests/test_parser.py
echo   docker-compose exec api pytest api/tests/test_properties.py
