# MIRAI — Temporary Decart Live VTO Prototype Integration Guide

> **Notice**: Decart Lucy V-TON (`lucy-vton-3.5`) is integrated as a **temporary external inference provider** for funding and investor validation demonstrations. MIRAI's proprietary self-hosted **Kinematic Volumetric Garment Engine (KVGE)** remains fully intact as the core edge architecture.

---

## 1. Architectural Overview

```
                      ┌──────────────────────────────────────────────┐
                      │             USB Webcam / Camera              │
                      └──────────────────────┬───────────────────────┘
                                             │ Local MediaStream
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │             MIRAI Smart Mirror               │
                      │               (MirrorView)                   │
                      └───────┬──────────────────────────────┬───────┘
                              │                              │
         [Engine Mode: Decart Prototype]        [Engine Mode: Mirai KVGE]
                              │                              │
                              ▼                              ▼
                 ┌─────────────────────────┐   ┌───────────────────────────┐
                 │  DecartLucyVTOProvider  │   │     MiraiVTOProvider      │
                 │   (WebRTC Client SDK)   │   │  (MediaPipe + Mesh 2D)    │
                 └────────────┬────────────┘   └─────────────┬─────────────┘
                              │                              │
         Sub-60ms Streaming   │                              │ Continuous 60 FPS
         Neural World Model   │                              │ Deformable Canvas Mesh
                              ▼                              ▼
                 ┌─────────────────────────┐   ┌───────────────────────────┐
                 │  Remote MediaStream     │   │ 32-Triangle Fabric Mesh   │
                 │  (HTMLVideoElement)     │   │ + Cylindrical Shading     │
                 └────────────┬────────────┘   └─────────────┬─────────────┘
                              │                              │
                              └──────────────┬───────────────┘
                                             │
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │         Digital Mirror Display (HUD)         │
                      │    • Live Garment Try-On (scaleX(-1))        │
                      │    • Dynamic Sizing & Rack Inventory         │
                      │    • Save Look & Mobile QR Handoff           │
                      │    • Coupons & Loyalty Rewards               │
                      └──────────────────────────────────────────────┘
```

---

## 2. Pluggable Provider Interface

The VTO layer is abstracted through `IVTOProvider` (`frontend/src/services/vto/types.ts`):

```typescript
export type VTOProviderType = 'decart' | 'mirai_kvge';

export interface IVTOProvider {
  readonly id: VTOProviderType | string;
  readonly name: string;
  readonly modelName: string;
  readonly isTemporaryPrototype: boolean;
  readonly renderMode: 'stream' | 'canvas';
  readonly description: string;

  connect(cameraStream: MediaStream, initialGarment?: GarmentReference): Promise<void>;
  setGarment(garment: GarmentReference): Promise<void>;
  getRemoteStream(): MediaStream | null;
  getConnectionState(): VTOConnectionState;
  disconnect(): void;

  on<K extends keyof VTOEventMap>(event: K, listener: (data: VTOEventMap[K]) => void): void;
  off<K extends keyof VTOEventMap>(event: K, listener: (data: VTOEventMap[K]) => void): void;
}
```

### Registered Providers

| Provider ID | Provider Name | Role | Render Mode | Model Target |
| :--- | :--- | :--- | :--- | :--- |
| `decart` | **Decart Lucy V-TON** | Temporary External Prototype | `stream` (Remote WebRTC) | `lucy-vton-3.5` |
| `mirai_kvge` | **Mirai KVGE** | Self-Hosted Core Architecture | `canvas` (Edge GPU/WASM) | `kvge-deformable-mesh-v1` |

---

## 3. API Key & Security Configuration

The Decart API key is **never committed to Git** and **never hard-coded**.

### Option A: Backend Environment Variable (Recommended for Kiosk)
Launch the backend service with the environment variable set:

```powershell
$env:DECART_API_KEY = "decart_sk_your_actual_key_here"
& "backend\.venv\Scripts\python.exe" -m uvicorn backend.app.main:app --port 8000
```

The frontend automatically discovers this key upon loading via the protected local endpoint `GET /api/v1/vto/credentials`.

### Option B: Local Frontend Environment
Create a local `.env.local` file (already ignored by `.gitignore`):

```bash
# frontend/.env.local
VITE_DECART_API_KEY=decart_sk_your_actual_key_here
```

### Option C: Runtime Presenter Input
Click the **Engine** button on the mirror's top HUD to open the **VTO Inference Engine Architecture** modal. Enter or update your API key directly on screen.

---

## 4. Live Operational Controls

- **Engine Toggle Badge**: Located on the top-left of the HUD header bar:
  - `⚡ DECART VTO: ACTIVE (TEMP)` indicates live neural video streaming from Decart.
  - `🛡️ MIRAI KVGE: ACTIVE (SELF-HOSTED)` indicates local edge mesh rendering.
- **Instant Fallback**: If Decart is selected without a valid API key or encounters network disruption, the UI alerts the presenter and permits immediate fallback to Mirai KVGE without interrupting the customer.
- **Skeleton HUD**: Can be toggled on/off in both modes. MediaPipe pose landmarks track user movements simultaneously.
- **Seamless Garment Swapping**: Swapping garments via the right-side catalog invokes `provider.setGarment(garment)` without terminating or re-establishing the WebRTC session.
- **Retail Continuity**: In-store inventory rack locations, sizes, saved looks with QR mobile handoff, and discount coupons remain active across both engines.

---

## 5. Verification Checklist

1. **Backend Tests**: 32/32 passed (`pytest ai/tests backend/tests`).
2. **KVGE Movement Tests**: 10/10 passed (`backend/vto/test_kvge.py`).
3. **TypeScript Compilation**: 0 errors (`npx tsc --noEmit`).
4. **Production Build**: Clean bundle generated (`npm run build`).
