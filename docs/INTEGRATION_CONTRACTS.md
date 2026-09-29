# MIRAI — Integration Contracts

This document formalizes the public interfaces between the four engineering domains.  
**No role may alter these interfaces without an approved RFC and documentation update.**

---

## 1. AI → Frontend Contract: `TrackingFrame`

The AI subsystem produces a continuous stream of structured pose tracking data. The Frontend consumes this stream to position virtual garments over the live mirrored view.

### 1.1 JSON Packet Schema

```json
{
  "timestamp": 1727625600123,
  "frame_id": 4120,
  "frame_width": 1280,
  "frame_height": 720,
  "fps": 30.0,
  "confidence": 0.94,
  "tracking_state": "tracked",
  "landmarks": [
    {
      "id": 0,
      "name": "nose",
      "x": 0.521,
      "y": 0.214,
      "z": -0.125,
      "visibility": 0.99
    }
  ]
}
```

### 1.2 Data Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `timestamp` | `integer` (epoch ms) | Monotonic capture timestamp. |
| `frame_id` | `integer` | Monotonically increasing sequential frame counter. |
| `frame_width` | `integer` | Source camera frame width in pixels (e.g., 1280 or 1920). |
| `frame_height` | `integer` | Source camera frame height in pixels (e.g., 720 or 1080). |
| `fps` | `float` | Instantaneous rolling frame rate of the tracking loop. |
| `confidence` | `float` | Mean pose estimation confidence `[0.0, 1.0]`. |
| `tracking_state` | `string` | One of: `"searching"`, `"tracked"`, `"lost"`, `"calibrating"`. |
| `landmarks` | `array[Landmark]` | Array of 33 normalized body landmark objects. |

### 1.3 Landmark Object

| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | `integer` | `0` to `32` | Standard MediaPipe landmark identifier. |
| `name` | `string` | Human-readable | Standard name (e.g. `left_shoulder`, `right_shoulder`, `left_hip`). |
| `x` | `float` | `0.0` – `1.0` | Normalized horizontal position (0 = left, 1 = right). |
| `y` | `float` | `0.0` – `1.0` | Normalized vertical position (0 = top, 1 = bottom). |
| `z` | `float` | Relative depth | Estimated depth relative to mid-hip reference plane. |
| `visibility` | `float` | `0.0` – `1.0` | Probability that the landmark is visible and not occluded. |

### 1.4 Primary Garment Anchors
- **Upper Body (Shirts, Jackets, Tops)**:
  - Left Shoulder (`id: 11`)
  - Right Shoulder (`id: 12`)
  - Left Hip (`id: 23`)
  - Right Hip (`id: 24`)
- **Lower Body (Trousers, Skirts, Pants)**:
  - Left Hip (`id: 23`)
  - Right Hip (`id: 24`)
  - Left Knee (`id: 25`), Right Knee (`id: 26`)
  - Left Ankle (`id: 27`), Right Ankle (`id: 28`)

---

## 2. Frontend → Backend Contract (REST API)

The Frontend requests store and product metadata asynchronously. Full endpoint specs are defined in [`API_CONTRACT.md`](./API_CONTRACT.md).

- Base URL: `http://localhost:8000/api`
- Content Type: `application/json`
- Key interactions:
  - Fetch catalog and categories for garment browser.
  - Check real-time inventory and sizes.
  - Save customer outfit looks.
  - Publish aggregated UI interaction events.

---

## 3. Hardware → Software Interface

Physical devices provide standard driver-level OS abstractions so software remains decoupled from hardware manufacturers:

### 3.1 Camera Interface
- **Protocol**: USB Video Class (UVC 1.1 / 1.5).
- **Format**: YUY2 / MJPEG at 1080p @ 30fps or 720p @ 60fps.
- **Mounting**: Top-center bezel, downward tilt of 6°–8° calibrated for full-height standing user capture at 1.8m distance.
- **Software Access**: Accessible via OpenCV `cv2.VideoCapture(index)` or Browser `navigator.mediaDevices.getUserMedia()`.

### 3.2 Display Interface
- **Format**: HDMI 2.0 / DisplayPort.
- **Resolution**: 1080 x 1920 (Vertical Portrait Orientation, 9:16 aspect ratio).
- **Brightness**: Minimum 700 nits (to achieve >350 nits after 50% beamsplitter mirror transmission).

### 3.3 Touch Interface
- **Protocol**: USB HID multi-touch digitizer (standard plug-and-play).
- **Overlay**: Optical IR Touch Frame (10-point or 20-point touch).
- **Software Access**: Standard DOM pointer events (`pointerdown`, `pointermove`, `pointerup`).

### 3.4 Audio / Speech (Phase 4 Ready)
- **Input**: USB omnidirectional microphone array with hardware noise suppression.
- **Output**: 3.5mm / HDMI integrated stereo speakers.
