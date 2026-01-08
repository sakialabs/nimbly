# 🐇 Nimbly

Move lighter. Spend smarter.

**Nimbly** is a people-first app for **smarter everyday spending**, starting with groceries.  
It highlights deals, surfaces clearances, and nudges you toward better timing without guilt, pressure, or finance jargon.

Nimbly isn't about extreme budgeting.  
It's about **moving smart, consistently**.

---

## 🤖 Meet Savvy

**Savvy** is your in-app guide.

Savvy keeps an eye on prices, notices patterns, and gives you a heads-up when there's a better move to make.

No lectures.  
No judgment.  
Just the right info at the right time.

---

## ✨ What Nimbly does

- Surfaces grocery deals and clearances  
- Helps you spot better buying opportunities  
- Encourages smarter timing on everyday purchases  
- Keeps the experience fast, light, and human  

---

## 🚀 Quick Start

### Automated Setup (Recommended)

**Unix/Mac:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**Windows:**
```cmd
scripts\setup.bat
```

This will automatically:
- Check dependencies (Docker, Node.js)
- Set up environment files
- Build and start containers
- Seed the database
- Install web dependencies

### Manual Setup

If you prefer manual setup:

```bash
# 1. Start backend
docker-compose up -d

# 2. Seed database
docker-compose exec api python -m api.seed

# 3. Install web dependencies
cd web && npm install

# 4. Start web app
npm run dev
```

### Access

- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Web App:** http://localhost:3000 (after running `npm run dev`)

See `api/README.md` for detailed backend setup and `docs/testing.md` for testing guide.

---

## 📁 Project Structure

```
nimbly/
├── api/                    # FastAPI backend
│   ├── tests/              # Backend test suite
│   ├── auth.py             # Authentication endpoints
│   ├── receipts.py         # Receipt endpoints
│   ├── insights.py         # Insight generation
│   ├── parser.py           # Receipt parsing (OCR, extraction)
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   ├── database.py         # Database configuration
│   ├── config.py           # App configuration
│   ├── utils.py            # Utility functions
│   └── seed.py             # Database seeding
│
├── web/                    # Next.js web app
│   ├── app/                # Pages and routes
│   │   ├── page.tsx        # Home page
│   │   ├── auth/           # Authentication
│   │   ├── receipts/       # Receipts view
│   │   ├── about/          # About page
│   │   ├── savvy/          # Savvy page
│   │   └── ...
│   ├── components/         # React components
│   │   ├── ui/             # Base UI components
│   │   ├── navigation.tsx  # Navigation bar
│   │   ├── footer.tsx      # Footer
│   │   └── ...
│   └── lib/                # Utilities
│       ├── api.ts          # API client
│       ├── auth.ts         # Auth utilities
│       └── utils.ts        # Helper functions
│
├── mobile/                 # React Native mobile app
│   ├── src/
│   │   ├── components/     # Mobile components
│   │   ├── theme/          # Theme configuration
│   │   └── context/        # React context
│   └── App.tsx             # Main app component
│
├── docs/                   # Documentation
│   ├── requirements.md     # Feature requirements
│   ├── design.md           # System design
│   ├── tasks.md            # Implementation tasks
│   ├── phases.md           # Development phases
│   ├── visuals.md          # Visual design system
│   ├── tone.md             # Voice and tone guide
│   ├── testing.md          # Testing guide
│   └── CHANGELOG.md        # Version history
│
├── scripts/                # Helper scripts
│   ├── setup.sh/.bat       # Automated setup
│   ├── dev.sh/.bat         # Start dev environment
│   ├── test.sh/.bat        # Run tests
│   └── README.md           # Scripts documentation
│
├── uploads/                # Receipt file storage
├── docker-compose.yml      # Docker configuration
├── Dockerfile              # API container definition
├── .env.example            # Environment variables template
├── CONTRIBUTING.md         # Contribution guidelines
└── README.md               # This file
```

---

## 🌱 Why Nimbly exists

Groceries are getting expensive.  
Everyday spending decisions are getting harder.  
Most tools either shame you or overwhelm you.

Nimbly exists to help everyday people:
- spend smarter on essentials  
- make better decisions without stress  
- build healthier money habits over time  

Small wins. Real relief.

---

## 🎯 Goals

- Help people spend less on everyday groceries  
- Reduce decision fatigue around shopping  
- Build clarity instead of guilt  
- Turn small savings into long-term stability over time  

Small, repeatable wins. Long game.

---

## 🚧 Project status

**Phase 0 (Backend Foundation):** Complete ✅
- Magic link authentication
- Receipt upload and parsing (OCR)
- Price history tracking
- Insight generation
- Comprehensive error handling
- Structured logging
- Docker deployment
- Test suite

**Phase 1 (UI Foundation):** Complete ✅
- Next.js web app with professional pages
- React Native mobile app
- Design system (Sage/Amber colors, light/dark mode)
- Framer Motion animations
- Netlify deployment ready

**Phase 2 (Understanding):** In Progress 🚧
- ✅ Enhanced OCR preprocessing (OpenCV)
- ✅ Improved store detection (fuzzy matching)
- ✅ Smarter line item extraction (quantities, unit prices)
- ✅ Granular confidence scoring
- 🔄 New insight types (coming soon)

See `docs/` for complete requirements, design, and implementation plan.

---

## 🛠️ Tech stack

- **API:** FastAPI  
- **Database:** PostgreSQL  
- **Web app:** Next.js (shadcn/ui + Framer Motion)  
- **Mobile app:** React Native  
- **Infra:** Docker  

---

## 🧠 Philosophy

> Move fast. Stay aware. Don't get played.

That's Nimbly.

---

## 📬 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

Built with 💖 for everyday people trying to get by.
