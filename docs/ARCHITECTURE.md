# MIRAI — System Architecture

**OCTACEPT** — *Observe • Perceive • Imagine • Create*  
**MIRAI** — *The Intelligent Mirror: "Try Beyond Reality"*

---

## 1. High-Level Architecture Overview

MIRAI is an intelligent smart mirror and digital trial-room platform designed for retail store environments. The system blends physical mirror hardware, high-frame-rate local computer vision, real-time client-side AR garment rendering, and a decoupled server backend for product catalog and inventory.

```
                          PHYSICAL WORLD
                   ┌───────────────────────────┐
                   │  Customer in Trial Room   │
                   └─────────────┬─────────────┘
                                 │
                                 ▼
                     HARDWARE LAYER (/hardware)
              Camera (USB)      Touch Frame (USB)     Display (HDMI)
                   │                     │                  ▲
                   ▼                     │                  │
        AI / COMPUTER VISION (/ai)       │                  │
      - Local Frame Processing           │                  │
      - 33-point Pose & Landmarks        │                  │
      - Smoothing & Normalization        │                  │
                   │                     │                  │
                   ▼ (TrackingFrame)     ▼ (Pointer Events) │
        FRONTEND / AR LAYER (/frontend)  ───────────────────┘
      - Client-Side WebGL/Canvas Rendering
      - Garment Dynamic Fitting & Follow
      - Smart Mirror Portrait UI (1080x1920)
                   ▲
                   │ REST API (JSON)
                   ▼
          BACKEND LAYER (/backend)
      - Catalog & 30+ Demo Products
      - Inventory & Store Availability
      - Customer Sessions & Saved Looks
      - Analytics & POS Integrations (FastAPI / PostgreSQL)
```

---

## 2. Core Architectural Principles

### Principle 1: Zero-Video Cloud Upload (Privacy by Design)
- **Hard Rule**: Camera frames are processed strictly locally in memory on the mirror's compute unit.
- Video streams are **never** transmitted to the cloud, backend server, or stored persistently.
- No facial recognition is performed.
- Only anonymized, aggregated event data (e.g., product try-on counter) is sent to the backend.

### Principle 2: Local Real-Time Loop
- Computer vision tracking and AR garment visualization run locally at 30+ FPS.
- The backend is **completely bypassed** for real-time video/tracking frames.
- Backend interaction occurs strictly asynchronously for catalog lookups, product switching, and session saves.

### Principle 3: Absolute Decoupling Across 4 Roles
- AI emits structured telemetry packets (`TrackingFrame`).
- Frontend consumes `TrackingFrame` and renders visual overlays.
- Backend serves structured REST APIs over HTTP.
- Hardware provides certified physical interfaces (USB video, HDMI display, USB HID touch).

---

## 3. Data Flow

1. **Capture**: Physical wide-angle camera captures user standing 1.5m–2.5m in front of mirror at 1080p/720p @ 30–60 FPS.
2. **Pose Extraction**: AI module extracts 33 standard human landmarks, filters sensor noise via exponential moving average (EMA), and normalizes coordinates `[0.0, 1.0]`.
3. **Local Stream**: AI sends `TrackingFrame` packets to Frontend via local socket/IPC/BroadcastChannel.
4. **AR Rendering**: Frontend aligns virtual garment anchor points (shoulders, chest, hips, waist) over the user's reflection in real time.
5. **Catalog Queries**: When customer selects garments or categories via touch, Frontend fetches metadata from Backend REST API.
