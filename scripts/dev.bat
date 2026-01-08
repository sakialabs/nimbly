@echo off
REM Start Nimbly development environment

echo.
echo 🚀 Starting Nimbly Development Environment
echo ==========================================
echo.

REM Start backend
echo Starting backend...
docker-compose up -d

echo.
echo ✓ Backend started!
echo   API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo To view logs: docker-compose logs -f
echo To stop: docker-compose down
echo.
echo Start web app separately:
echo   cd web ^&^& npm run dev
