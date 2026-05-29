# GasMap — Gas Dispersion Visualizer

[![CI](https://github.com/arienug20/gasmap/actions/workflows/ci.yml/badge.svg)](https://github.com/arienug20/gasmap/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Aplikasi web interaktif untuk visualisasi dispersi gas berbahaya dengan calculation engine yang tervalidasi, chemical database komprehensif, dan peta interaktif. Dirancang untuk process safety engineers sebagai tool harian untuk QRA, HAZOP support, dan emergency planning.

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
git clone https://github.com/arienug20/gasmap.git
cd gasmap
docker compose up --build
```

Akses aplikasi di http://localhost:3000

### Manual Setup

**Backend (FastAPI):**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m src.database.init_db  # Initialize database with seed data
uvicorn src.main:app --reload --port 8000
```

**Frontend (React + Vite):**

```bash
cd frontend
npm install
npm run dev
```

Akses aplikasi di http://localhost:5173

## 📋 Features

- **Chemical Database** — 200+ chemicals dengan emergency exposure limits (ERPG, IDLH, AEGL) dan physical properties
- **Dispersion Models** — Gaussian Plume (continuous), Gaussian Puff (instantaneous), Heavy Gas (Britter-McQuaid), Pool Evaporation, Jet Release
- **Interactive Map** — MapLibre GL dengan contour layers, threshold rings, dan multiple base layers (OSM, satellite, terrain)
- **Visualization** — Heat maps, time animations, concentration vs distance charts, cross-section plots
- **GIS Export** — KML (Google Earth), GeoJSON, PNG snapshot, CSV grid data
- **Scenario Management** — Template-based scenario creation, duplication for what-if analysis, multi-scenario comparison
- **Weather System** — Pasquill stability classification, weather presets, wind rose analysis

## 🏗️ Architecture

```
Frontend (React 18 + TypeScript + Vite + MapLibre GL + Deck.gl)
            ↓ HTTPS/JSON
Backend (FastAPI + Python 3.11+)
            ↓ NumPy/SciPy
Calculation Engine (Gaussian Plume/Puff/Heavy Gas)
            ↓
Database (SQLite + 200+ chemicals seed data)
```

## 📚 Documentation

- [User Guide](docs/user-guide.md)
- [Tutorial](docs/tutorial.md)
- [API Reference](http://localhost:8000/docs) (FastAPI auto-generated)
- [Development Plan](../plans/03-gasmap.md)

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=src

# Frontend tests
cd frontend
npm test
npm run lint

# E2E tests
npx playwright test
```

## 🐳 Docker

```bash
# Build and run all services
docker compose up --build

# Run backend only
docker compose up backend

# Run frontend only
docker compose up frontend

# Stop all services
docker compose down

# Remove volumes (wipe database)
docker compose down -v
```

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, MapLibre GL JS, Deck.gl, Recharts |
| Backend | FastAPI, Python 3.11+, NumPy, SciPy, SQLAlchemy, Pydantic |
| Database | SQLite with chemical seed data |
| Testing | pytest, Vitest, Playwright |
| CI/CD | GitHub Actions |
| Deployment | Docker Compose, Docker |

## 📊 Dispersion Models

### Gaussian Plume (Continuous Release)
Standard Pasquill-Gifford model untuk continuous release dari elevated atau ground-level source. Tervalidasi terhadap CCPS Guidelines, TNO Yellow Book, dan literatur peer-reviewed.

### Gaussian Puff (Instantaneous Release)
Time-dependent model untuk instantaneous release (e.g., vessel rupture, BLEVE). Menggunakan σx = σy untuk puff symmetry.

### Heavy Gas (Britter-McQuaid)
Dense gas dispersion model untuk gases heavier than air (e.g., chlorine, LPG, HF). Menggunakan nomogram Britter-McQuaid (1988) dengan dimensionless analysis.

### Pool Evaporation
Menghitung evaporasi rate dari liquid pool (HSSC model + Mackay & Matsugu) dan dispersi ke atmosfer.

### Jet Release
Model untuk pressurized gas release through an orifice/pipe leak dengan choked/subsonic flow calculation dan far-field transition ke Gaussian.

## 🎯 Use Cases

- **QRA (Quantitative Risk Assessment)** — Calculate affected zones for process safety studies
- **HAZOP Support** — Visualize dispersion scenarios during hazard analysis
- **Emergency Planning** — Determine evacuation zones and safe distances
- **Incident Investigation** — Reconstruct dispersion patterns for post-incident analysis
- **Regulatory Compliance** — Generate exportable data for permits and reports

## 📈 Performance Targets

- 200×200 grid Gaussian Plume: <500ms
- 200×200 grid Gaussian Puff (50 timesteps): <5s
- Heavy Gas 200×200 grid: <1s
- Full simulation API call: <2s

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests to `develop` branch.

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 👥 Authors

- Arie Nugraha (@arienug20) — Initial development

## 🙏 Acknowledgments

- CCPS (Center for Chemical Process Safety) — Validation examples and methodologies
- TNO Yellow Book — Heavy gas dispersion methodologies
- Briggs (1973, 1988) — Dispersion coefficients and plume rise formulas
- Britter & McQuaid (1988) — Heavy gas dispersion nomograms
- Hanna, Briggs, Hosker (1982) — Atmospheric dispersion handbook