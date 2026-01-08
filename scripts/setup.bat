@echo off
REM Nimbly Setup Script (Windows)
REM Automates the initial setup process for contributors

echo.
echo 🐇 Welcome to Nimbly Setup
echo ==========================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first:
    echo    https://docs.docker.com/desktop/install/windows-install/
    exit /b 1
)
echo ✓ Docker is installed

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop first:
    echo    https://docs.docker.com/desktop/install/windows-install/
    exit /b 1
)
echo ✓ Docker Compose is installed

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Node.js is not installed. Web app setup will be skipped.
    echo    Install Node.js from: https://nodejs.org/
    set SKIP_WEB=true
) else (
    for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
    echo ✓ Node.js %NODE_VERSION% is installed
    set SKIP_WEB=false
)

echo.
echo 📦 Setting up backend...
echo ------------------------

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env >nul
    echo ✓ .env file created
) else (
    echo ✓ .env file already exists
)

REM Build and start Docker containers
echo Building Docker containers (this may take a few minutes)...
docker-compose build

echo Starting Docker containers...
docker-compose up -d

REM Wait for database to be ready
echo Waiting for database to be ready...
timeout /t 5 /nobreak >nul

REM Seed the database
echo Seeding database with sample data...
docker-compose exec -T api python -m api.seed

echo.
echo ✓ Backend setup complete!
echo   API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs

if "%SKIP_WEB%"=="false" (
    echo.
    echo 📦 Setting up web app...
    echo ------------------------
    
    cd web
    
    REM Create .env.local if it doesn't exist
    if not exist .env.local (
        echo Creating .env.local file...
        echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
        echo ✓ .env.local file created
    ) else (
        echo ✓ .env.local file already exists
    )
    
    REM Install dependencies
    echo Installing web dependencies...
    call npm install
    
    echo.
    echo ✓ Web app setup complete!
    echo   Run 'npm run dev' in the web\ directory to start
    
    cd ..
)

echo.
echo 🎉 Setup complete!
echo ==================
echo.
echo Next steps:
echo   1. Backend is running at http://localhost:8000
echo   2. Check API docs at http://localhost:8000/docs
if "%SKIP_WEB%"=="false" (
    echo   3. Start web app: cd web ^&^& npm run dev
    echo   4. Web app will be at http://localhost:3000
)
echo.
echo To stop the backend: docker-compose down
echo To view logs: docker-compose logs -f
echo.
echo Happy coding! 🚀
