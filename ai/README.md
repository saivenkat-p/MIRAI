# Role 1: AI / Computer Vision

**Domain Ownership**: `/ai/**`  
**Engineer**: Founding AI / Computer Vision Intern  

---

## Scope & Responsibilities
- Camera frame ingestion & preprocessing.
- 33-point human body pose estimation (MediaPipe / OpenCV).
- Coordinate normalization `[0.0, 1.0]`.
- Temporal landmark jitter smoothing (EMA / Kalman).
- Structured `TrackingFrame` serialization for local frontend consumption.

> **Ownership Boundary**: AI produces tracking data through the public `TrackingFrame` interface. AI does **not** render UI, edit `/frontend/`, or communicate with backend databases.

---

## Directory Structure
- `tracking/`: Telemetry data models and landmark definitions matching `/docs/INTEGRATION_CONTRACTS.md`.
- `pose/`: Pose estimator interfaces and implementation pipelines.
- `vision/`: Video capture abstraction and camera frame handlers.
- `tests/`: Contract validation and unit tests.
