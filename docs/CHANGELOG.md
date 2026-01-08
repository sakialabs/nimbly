# Changelog

All notable changes to Nimbly will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete requirements documentation
- System design and architecture documentation
- Implementation task breakdown (18 tasks)
- Savvy voice and tone guidelines
- Key product and technical decisions documentation
- Deal intelligence constraints and ethical data practices
- FastAPI project structure with SQLAlchemy models
- Magic link authentication with JWT tokens
- Receipt upload endpoint with file validation
- Receipt listing and detail endpoints with pagination
- Receipt parser with OCR, PDF extraction, and regex patterns
- Store and product normalization utilities
- Automatic price history tracking
- Insight generation system with 4 insight types
- Comprehensive error handling with global exception handlers
- Structured logging infrastructure with request IDs
- Database seed script with sample data
- Docker and docker-compose configuration
- Enhanced README with setup instructions

### Implemented
- **Task 1:** Project foundation and database setup ✅
- **Task 2:** Magic link authentication system ✅
- **Task 3:** Receipt upload endpoint ✅
- **Task 4:** Receipt listing and detail endpoints ✅
- **Task 5:** Receipt parser implementation ✅
- **Task 6:** Store and product normalization ✅
- **Task 7:** Price history tracking ✅
- **Task 8:** Savvy insight generation logic ✅
- **Task 9:** Insights API endpoint ✅
- **Task 10:** Comprehensive error handling ✅
- **Task 11:** Logging infrastructure ✅
- **Task 12:** Docker and local development setup ✅
- **Task 13:** Database seed script ✅
- **Task 14:** Integration tests ✅
- **Task 15:** API documentation ✅
- **Task 16:** Property-based tests ✅
- **Task 17:** Performance optimization ✅

### Backend Features Complete
- Magic link authentication with console logging in dev mode
- Receipt upload supporting JPEG, PNG, PDF, and TXT formats
- OCR-based receipt parsing with Tesseract
- Store name and product name normalization
- Automatic price history generation
- Four insight types: purchase frequency, price trends, common purchases, store patterns
- Minimum data thresholds enforced for all insights
- Transparent data display with confidence levels
- Pagination support for receipt listing
- User authorization enforced on all endpoints
- Consistent error responses with proper HTTP status codes
- Structured logging with request IDs and context
- Health check endpoint
- Auto-generated OpenAPI documentation at /docs

### Infrastructure
- Docker Compose setup with PostgreSQL and FastAPI
- Environment variable configuration
- Automatic database table creation on startup
- Volume mounts for development
- Health checks for database service
- Seed script for testing with 2 users and 10 receipts

### Configuration
- pytest.ini moved to api/ directory (best practice)
- Enhanced .env.example with comments
- All environment variables documented

### Testing
- Comprehensive integration tests for all workflows
- Property-based tests with Hypothesis (100+ iterations per test)
- Tests for authentication flow, receipt upload/parsing, and insights
- Multi-user isolation tests
- Authorization enforcement tests
- Predictive language detection tests
- Referential integrity tests
- Normalization consistency tests
- Test coverage with pytest-cov

### Documentation
- Requirements document with MUST/SHOULD/COULD prioritization
- Design document with 29 correctness properties for property-based testing
- Task list with clear acceptance criteria and dependencies
- Tone guide with examples of Savvy's voice
- Decisions document explaining key tradeoffs
- Comprehensive README with quick start guide
- API documentation auto-generated via FastAPI with enhanced docstrings
- TESTING.md guide for contributors

## [0.0.0] - 2026-01-07

### Project Initialized
- Repository created
- Documentation foundation established
- Ready for v0 backend implementation
