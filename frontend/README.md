# Role 2: Frontend / AR

**Domain Ownership**: `/frontend/**`  
**Engineer**: Founding Frontend / AR Intern  

---

## Scope & Responsibilities
- Smart Mirror UI optimized for vertical portrait displays (1080x1920, 9:16).
- Real-time client-side AR garment overlay rendering (Canvas / WebGL / Three.js).
- Customer touch interactions (garment browsing, category filters, size/color selectors).
- Consuming AI tracking packets (`TrackingFrame`) via WebSocket / local transport.
- Consuming Backend REST APIs for catalog and inventory.

> **Ownership Boundary**: Frontend consumes the AI `TrackingFrame` contract and Backend REST APIs. Frontend does **not** implement pose detection, does **not** alter the database, and does **not** modify `/ai/**` or `/backend/**`.

---

## Directory Scaffolding
- `src/components/`: Modular UI widgets (Camera preview backdrop, Product Drawer, Telemetry overlay).
- `src/rendering/`: Garment positioning and AR alignment canvas.
- `src/types/`: Interfaces matching `/docs/INTEGRATION_CONTRACTS.md` and `/docs/API_CONTRACT.md`.
- `src/hooks/`: Reactive hooks for tracking streams and API data fetching.
