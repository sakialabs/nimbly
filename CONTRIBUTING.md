# Contributing to Nimbly

Thank you for your interest in contributing to Nimbly! This guide will help you get started.

## Quick Start

### Prerequisites

- **Docker & Docker Compose** (required for backend)
- **Node.js 20+** (required for web app)
- **Python 3.11+** with conda (optional, for local development)

### Setup

**Unix/Mac:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**Windows:**
```cmd
scripts\setup.bat
```

This automated script will:
1. Check dependencies
2. Create environment files
3. Build and start Docker containers
4. Seed the database
5. Install web dependencies

### Development

**Start backend:**
```bash
docker-compose up -d
```

**Start web app:**
```bash
cd web
npm run dev
```

**Run tests:**
```bash
./scripts/test.sh  # Unix/Mac
scripts\test.bat   # Windows
```

## Project Structure

```
nimbly/
├── api/              # FastAPI backend
│   ├── tests/        # Backend tests
│   ├── models.py     # Database models
│   ├── parser.py     # Receipt parsing
│   └── insights.py   # Insight generation
├── web/              # Next.js web app
│   ├── app/          # Pages and routes
│   ├── components/   # React components
│   └── lib/          # Utilities and API client
├── mobile/           # React Native mobile app
├── docs/             # Documentation
└── scripts/          # Helper scripts
```

## Development Workflow

### 1. Pick an Issue

- Check [open issues](https://github.com/sakialabs/nimbly/issues)
- Comment on the issue to claim it
- Ask questions if anything is unclear

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Changes

- Follow existing code style
- Write tests for new features
- Update documentation as needed
- Keep commits focused and atomic

### 4. Test Your Changes

```bash
# Run all tests
./scripts/test.sh

# Run specific tests
docker-compose exec api pytest api/tests/test_auth.py

# Check web app builds
cd web && npm run build
```

### 5. Commit

Use clear, descriptive commit messages:

```bash
git commit -m "Add feature: magic link authentication

- Implement request and verify endpoints
- Add session token management
- Update navigation with auth state
"
```

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Link to related issue
- Screenshots (if UI changes)
- Test results

## Code Guidelines

### Backend (Python)

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions
- Keep functions focused and small
- Use meaningful variable names

**Example:**
```python
def extract_store_name(text: str) -> Tuple[Optional[str], float]:
    """
    Extract store name from receipt text with confidence score.
    
    Args:
        text: Raw receipt text
        
    Returns:
        Tuple of (store_name, confidence) where confidence is 0.0-1.0
    """
    # Implementation
```

### Frontend (TypeScript/React)

- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Keep components small and focused
- Follow existing naming conventions

**Example:**
```typescript
interface ButtonProps {
  variant?: "primary" | "secondary";
  disabled?: boolean;
  children: React.ReactNode;
}

export function Button({ variant = "primary", disabled, children }: ButtonProps) {
  // Implementation
}
```

### Design System

- Follow `docs/visuals.md` strictly
- Use Sage (#5F7D73) for primary actions
- Use Amber (#D9A441) for deals/highlights only
- Support both light and dark mode
- Keep animations subtle and purposeful

### Copy and Tone

- Follow `docs/tone.md` for all user-facing text
- Be calm, clear, and non-judgmental
- Avoid jargon and technical terms
- Use simple, global language
- Never predict or recommend

## Testing

### Backend Tests

```bash
# All tests
docker-compose exec api pytest

# With coverage
docker-compose exec api pytest --cov=api

# Specific test file
docker-compose exec api pytest api/tests/test_parser.py

# Specific test
docker-compose exec api pytest api/tests/test_parser.py::test_extract_store_name
```

### Property-Based Tests

We use Hypothesis for property-based testing:

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_normalization_is_idempotent(text):
    """Normalizing twice should give same result"""
    once = normalize_product_name(text)
    twice = normalize_product_name(once)
    assert once == twice
```

### Manual Testing

```bash
# API testing
conda run -n nimbly python api/tests/test_api_manual.py

# Parser testing
conda run -n nimbly python api/tests/test_parser_enhanced.py
```

## Documentation

Update documentation when:
- Adding new features
- Changing APIs
- Modifying setup process
- Adding dependencies

Key docs:
- `README.md` - Project overview
- `docs/requirements.md` - Feature requirements
- `docs/design.md` - System design
- `docs/tasks.md` - Implementation tasks
- `docs/CHANGELOG.md` - Version history

## Common Tasks

### Add a New API Endpoint

1. Define route in appropriate file (`api/auth.py`, `api/receipts.py`, etc.)
2. Add Pydantic schemas in `api/schemas.py`
3. Write tests in `api/tests/`
4. Update API client in `web/lib/api.ts`
5. Document in `docs/`

### Add a New UI Component

1. Create component in `web/components/`
2. Follow design system (`docs/visuals.md`)
3. Add to Storybook (if applicable)
4. Use in pages
5. Test responsiveness

### Improve Receipt Parsing

1. Update patterns in `api/parser.py`
2. Add test cases in `api/tests/test_parser.py`
3. Test with real receipts
4. Document improvements in `docs/parser_enhancements.md`

## Getting Help

- **Questions?** Open a [discussion](https://github.com/sakialabs/nimbly/discussions)
- **Bug?** Open an [issue](https://github.com/sakialabs/nimbly/issues)
- **Stuck?** Comment on your PR or issue

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

Thank you for contributing to Nimbly! 🐇
