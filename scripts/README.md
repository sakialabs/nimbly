# Nimbly Scripts

Helper scripts for development, testing, and deployment.

## Setup Scripts

### Initial Setup

**Unix/Mac:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**Windows:**
```cmd
scripts\setup.bat
```

This script will:
- Check for required dependencies (Docker, Node.js)
- Create `.env` files
- Build and start Docker containers
- Seed the database with sample data
- Install web app dependencies
- Provide next steps

## Development Scripts

### Start Development Environment

**Unix/Mac:**
```bash
chmod +x scripts/dev.sh
./scripts/dev.sh
```

**Windows:**
```cmd
scripts\dev.bat
```

Starts the backend API and database. Start the web app separately with `cd web && npm run dev`.

### Run Tests

**Unix/Mac:**
```bash
chmod +x scripts/test.sh
./scripts/test.sh
```

**Windows:**
```cmd
scripts\test.bat
```

Runs the complete test suite with coverage reporting.

## Manual Testing

Located in `api/tests/`:

- `test_api_manual.py` - Manual API testing script

Run manually:
```bash
conda run -n nimbly python api/tests/test_api_manual.py
```

## Quick Reference

### Backend
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose build

# Seed database
docker-compose exec api python -m api.seed

# Run tests
docker-compose exec api pytest
```

### Web App
```bash
cd web

# Install dependencies
npm install

# Development
npm run dev

# Build
npm run build

# Production
npm start
```

### Mobile App
```bash
cd mobile

# Install dependencies
npm install

# Start Expo
npm start
```

## Contributing

Before submitting a PR:
1. Run `./scripts/test.sh` to ensure all tests pass
2. Check code formatting
3. Update documentation if needed
