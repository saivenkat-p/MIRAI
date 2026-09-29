# MIRAI — The Intelligent Mirror

> **OCTACEPT**  
> *Observe • Perceive • Imagine • Create*  
> **"Try Beyond Reality"**

MIRAI is an intelligent physical smart mirror and smart trial-room platform for retail stores, delivering real-time zero-latency virtual garment try-ons through localized computer vision and augmented reality.

---

## 4-Role Team Architecture & Ownership

The project enforces an **absolute ownership rule** across four distinct domains:

| Role | Authorized Directory | Ownership Scope |
| :--- | :--- | :--- |
| **Role 1: AI / Computer Vision** | `/ai/**` | Camera ingestion, pose estimation, landmark tracking, smoothing |
| **Role 2: Frontend / AR** | `/frontend/**` | Portrait mirror UI, WebGL/Canvas rendering, touch interaction |
| **Role 3: Backend** | `/backend/**` | Catalog, inventory, sessions, analytics, FastAPI server |
| **Role 4: Hardware / Embedded** | `/hardware/**` | Mirror glass, display mounting, camera FOV, IR touch frame, BOM |

> **Strict Rule**: Read Access ≠ Write Access. No role may modify files in another role's directory. Review [docs/TEAM_ROLES.md](docs/TEAM_ROLES.md) and [.github/CODEOWNERS](.github/CODEOWNERS).

---

## Repository Structure & Team Ownership

```text
MIRAI/
├── frontend/  → Frontend / AR
│   ├── src/
│   ├── package.json
│   └── ...
├── backend/   → Backend / API
│   ├── app/
│   ├── tests/
│   └── ...
├── ai/        → AI / Computer Vision
│   ├── pose/
│   ├── tracking/
│   ├── vision/
│   └── tests/
├── hardware/  → Hardware / Embedded
│   ├── bom/
│   ├── diagrams/
│   ├── mechanical/
│   └── tests/
├── docs/      → Shared Documentation
│   ├── ARCHITECTURE.md
│   ├── TEAM_ROLES.md
│   ├── INTEGRATION_CONTRACTS.md
│   ├── API_CONTRACT.md
│   └── MVP_ROADMAP.md
├── .github/
│   └── CODEOWNERS              # Explicit team code review ownership
├── .env.example                # Shared environment configuration template
├── .gitignore                  # Global Git ignore rules
└── README.md                   # Project documentation & setup guide
```

---

## Getting Started (Phase 0 Foundation)

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Swagger API docs available at: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Mirror UI available at: `http://localhost:5173`

### 3. AI / Tracking Setup
```bash
cd ai
python -m venv .venv
# On Windows:
.venv\Scripts\activate
pip install -r requirements.txt
python -m tracking.models
```

### 4. Hardware Documentation
Explore `hardware/bom/` for Bill of Materials and `hardware/diagrams/` for connection schematics.

---

## Core Contracts & Specifications
- Pose Tracking Contract: [`docs/INTEGRATION_CONTRACTS.md`](docs/INTEGRATION_CONTRACTS.md)
- REST API Contract: [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md)
- System Architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
