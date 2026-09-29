# MIRAI — MVP Development Roadmap

**OCTACEPT — Try Beyond Reality**

---

## Roadmap Overview

```
[ Phase 0: Foundation ]  <-- CURRENT PHASE
          │
          ▼
[ Phase 1: First Working MIRAI (Pose Tracking + Visual Overlay) ]
          │
          ▼
[ Phase 2: Virtual Garment Fitting (2D/3D Follows Movement) ]
          │
          ▼
[ Phase 3: Interactive Mirror (Touch UI, Lookbook, Mix & Match) ]
          │
          ▼
[ Phase 4: Smart Retail Features (QR, Analytics, Voice, Inventory) ]
          │
          ▼
[ Phase 5: Retail Pilot (In-Store Deployment, POS Integration) ]
```

---

## Detailed Phases

### Phase 0 — Foundation (CURRENT PHASE)
- **Scope**: Repository setup, directory boundaries, governance documents, integration contracts, minimal scaffolding, demo seed schema.
- **Rules**:
  - No complex model implementations.
  - No premature feature bloat.
  - Verification of 4-role independent environments.
- **Deliverables**:
  - `CODEOWNERS`, `.gitignore`, `.env.example`, `README.md`.
  - Architecture, team roles, contracts, roadmap documentation.
  - `/ai/`, `/frontend/`, `/backend/`, `/hardware/` directory scaffolding.
  - Demo store seed schema and initial 30+ product definitions.

---

### Phase 1 — First Working MIRAI
- **Objective**: Establish the live real-time camera-to-display loop with pose telemetry.
- **Success Condition**: A person stands in front of the mirror, the camera detects their body, and 33 landmarks are rendered smoothly in real time.
- **Role Deliverables**:
  - **AI**: Local MediaPipe Pose pipeline, landmark normalization, exponential moving average smoothing filter, and `TrackingFrame` generation at 30 FPS.
  - **Frontend**: Camera view backdrop, canvas overlay rendering tracked skeletal landmarks.
  - **Hardware**: USB camera mount test, display portrait mode configuration.
  - **Backend**: Basic health and product listing endpoints.

---

### Phase 2 — Virtual Garment
- **Objective**: Virtual garment overlay dynamically anchored to shoulders/torso following user motion.
- **Success Condition**: Garment scales, rotates, and translates in sync with user body movement without jitter.

---

### Phase 3 — Interactive Mirror
- **Objective**: Customer touch interaction and garment switching.
- **Success Condition**: User taps product catalog cards on touch mirror to swap garments, select sizes, and view details.

---

### Phase 4 — Smart Retail Features
- **Objective**: Save looks via QR code, real-time inventory queries, try-on dwell analytics.

---

### Phase 5 — Retail Pilot
- **Objective**: Physical store integration, store POS connectivity, hardened uptime and kiosk lock.
