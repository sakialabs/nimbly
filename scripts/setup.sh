#!/bin/bash
# Nimbly Setup Script (Unix/Mac)
# Automates the initial setup process for contributors

set -e

echo "🐇 Welcome to Nimbly Setup"
echo "=========================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✓ Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker Compose is installed"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is not installed. Web app setup will be skipped."
    echo "   Install Node.js from: https://nodejs.org/"
    SKIP_WEB=true
else
    echo "✓ Node.js $(node --version) is installed"
    SKIP_WEB=false
fi

echo ""
echo "📦 Setting up backend..."
echo "------------------------"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi

# Build and start Docker containers
echo "Building Docker containers (this may take a few minutes)..."
docker-compose build

echo "Starting Docker containers..."
docker-compose up -d

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 5

# Seed the database
echo "Seeding database with sample data..."
docker-compose exec -T api python -m api.seed

echo ""
echo "✓ Backend setup complete!"
echo "  API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"

if [ "$SKIP_WEB" = false ]; then
    echo ""
    echo "📦 Setting up web app..."
    echo "------------------------"
    
    cd web
    
    # Create .env.local if it doesn't exist
    if [ ! -f .env.local ]; then
        echo "Creating .env.local file..."
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
        echo "✓ .env.local file created"
    else
        echo "✓ .env.local file already exists"
    fi
    
    # Install dependencies
    echo "Installing web dependencies..."
    npm install
    
    echo ""
    echo "✓ Web app setup complete!"
    echo "  Run 'npm run dev' in the web/ directory to start"
    
    cd ..
fi

echo ""
echo "🎉 Setup complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "  1. Backend is running at http://localhost:8000"
echo "  2. Check API docs at http://localhost:8000/docs"
if [ "$SKIP_WEB" = false ]; then
    echo "  3. Start web app: cd web && npm run dev"
    echo "  4. Web app will be at http://localhost:3000"
fi
echo ""
echo "To stop the backend: docker-compose down"
echo "To view logs: docker-compose logs -f"
echo ""
echo "Happy coding! 🚀"
