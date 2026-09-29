# Role 3: Backend & Catalog Services

**Domain Ownership**: `/backend/**`  
**Engineer**: Founding Backend Intern  

---

## Scope & Responsibilities
- Product catalog, garment metadata, and category management.
- Real-time stock queries and in-store rack locations.
- Customer session management and saved look generation (QR/mobile handoff).
- Anonymous analytics event collection (dwell times, garment try-on frequencies).
- REST API service (FastAPI).

> **Ownership Boundary & Critical Rule**: Backend **never** processes video frames, runs pose estimation, or handles WebGL rendering. Backend serves asynchronous metadata to the local mirror UI over REST. Backend does **not** edit `/ai/**`, `/frontend/**`, or `/hardware/**`.

---

## Directory Scaffolding
- `app/api/`: Versioned API routers (`products`, `sessions`).
- `app/schemas/`: Pydantic data schemas mirroring `/docs/API_CONTRACT.md`.
- `app/data/`: In-memory demo store and catalog seed mechanism (30+ products).
- `tests/`: API contract test suite.
