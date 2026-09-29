# Role 1: AI / Computer Vision

**Domain Ownership**: `/ai/**`  
**Engineer**: Founding AI / Computer Vision Intern  

---

## Scope & Responsibilities
- Camera frame ingestion & preprocessing.
- 33-point human body pose estimation (MediaPipe / OpenCV).
- Coordinate normalization `[0.0, 1.0]`.
- Temporal landmark jitter smoothing (EMA filter).
- **Phase 2 Body Geometry Extraction**: deriving garment anchor points, torso center, shoulder/hip widths, and rotation angles.
- Structured `TrackingFrame` serialization for local frontend AR garment fitting.

> **Ownership Boundary**: AI produces tracking data through the public `TrackingFrame` interface and `BodyAnchors` geometry. AI does **not** render clothing, does **not** modify `/frontend/**`, and does **not** communicate with the backend database.

---

## Coordinate System Conventions (Phase 2)
- **Coordinate Space**: Normalized $[0.0, 1.0]$ in both horizontal ($X$) and vertical ($Y$) axes.
- **Origin $(0.0, 0.0)$**: Top-left corner of the video frame.
- **$X$ Axis**: Left to Right ($0.0 \to 1.0$).
- **$Y$ Axis**: Top to Bottom ($0.0 \to 1.0$).
- **$Z$ Axis**: Estimated relative depth from mid-hip reference plane (negative = closer to camera).
- **Shoulder Angle**: Angle in degrees and radians of the line from Left Shoulder to Right Shoulder. $0.0^\circ$ corresponds to horizontal; positive values indicate clockwise tilt.
- **Torso Angle**: Angle of the mid-shoulder to mid-hip spine line relative to vertical. $0.0^\circ$ indicates upright standing posture.
- **Mirroring Convention**: Landmarks are extracted directly from the camera frame. The Frontend mirrors the display horizontally via CSS `transform: scaleX(-1)`.
- **Frame Timestamps**: Monotonic epoch milliseconds integer.

---

## Confidence & Dropout Handling
- **High Confidence ($\ge 0.65$)**: Full real-time update using EMA-smoothed landmark coordinates.
- **Degraded Confidence ($0.35 \le c < 0.65$)**: Anchors computed from available visible landmarks; decay factor applied to confidence.
- **Temporary Dropout ($< 0.35$ or missing landmarks)**: `BodyAnchorExtractor` holds previous valid anchor geometry for up to **5 frames** with confidence decay to prevent sudden visual jumping or flickering during fast user movement.
- **Tracking Lost**: Cache resets and `is_valid` is set to `False`.

---

## Directory Structure
- `tracking/`:
  - `models.py`: Telemetry data models (`TrackingFrame`, `Landmark`, `TrackingState`).
  - `anchors.py`: `BodyAnchors`, `BodyAnchorExtractor`, `Point2D`, `BoundingBox`.
  - `smoothing.py`: `LandmarkSmoother` (Exponential Moving Average filter).
- `pose/`:
  - `interface.py`: `BasePoseEstimator` abstract base class.
  - `mediapipe_estimator.py`: MediaPipe Pose estimator pipeline with 33 canonical landmark extraction and body anchor derivation.
- `vision/`:
  - `camera_interface.py`: `BaseCameraCapture` interface.
  - `streamer.py`: `WebcamCapture` and `PoseStreamer`.
  - `segmentation_interface.py`: `BaseBodySegmenter` interface for future segmentation masks.
- `tests/`:
  - `test_tracking_contract.py`: Contract and schema serialization tests.
  - `test_pose_pipeline.py`: Pipeline and smoothing unit tests.
  - `test_body_anchors.py`: Body anchor extraction, geometry math, confidence, and stability tests.
