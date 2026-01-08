#!/bin/bash
# Run all tests for Nimbly

set -e

echo "🧪 Running Nimbly Tests"
echo "======================="
echo ""

# Check if Docker containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️  Docker containers are not running. Starting them..."
    docker-compose up -d
    sleep 5
fi

echo "📦 Running backend tests..."
echo "---------------------------"

# Run pytest with coverage
docker-compose exec -T api pytest -v --cov=api --cov-report=term-missing

echo ""
echo "✓ All tests passed!"
echo ""
echo "To run specific tests:"
echo "  docker-compose exec api pytest api/tests/test_auth.py"
echo "  docker-compose exec api pytest api/tests/test_parser.py"
echo "  docker-compose exec api pytest api/tests/test_properties.py"
