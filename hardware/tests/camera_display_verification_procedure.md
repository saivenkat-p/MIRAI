# MIRAI — Camera & Display Verification Procedure

**Scope**: Protocols for validating optical geometry, display alignment, and trial-room physical parameters.

---

## 1. Physical Hardware Verification Protocol (When Assembling Physical Prototype)

### Step 1: Laser Level & Height Check
1. Mount aluminum mirror chassis vertically against test rig.
2. Verify chassis is plumb ($0.0^\circ \pm 0.2^\circ$ vertical tilt).
3. Using a laser measuring tape, measure from the ground to the camera lens optical center:
   - Target: $1650\text{ mm} \pm 10\text{ mm}$.

### Step 2: Mechanical Inclinometer Tilt Calibration
1. Attach digital inclinometer to camera mounting bracket.
2. Adjust micro-tilt screw until inclinometer reads **$7.0^\circ$ downward**.
3. Tighten bracket locknuts with Loctite 243 threadlocker to prevent vibration drift.

### Step 3: Standing FOV Boundary Test
1. Mark floor lines at $1.5\text{ m}$, $1.8\text{ m}$, and $2.2\text{ m}$ from mirror surface.
2. Test subject ($1.75\text{ m} \pm 0.1\text{ m}$) stands on the $1.8\text{ m}$ target line.
3. Verify video stream frame in preview:
   - Crown of head must have $\ge 50\text{ px}$ margin from top border.
   - Shoes/feet must be clearly visible with $\ge 30\text{ px}$ margin from bottom border.
   - Arms extended laterally must fit within the frame width.

---

## 2. Hardware Simulation & Synthetic Verification Procedure (Pre-Assembly / Software Testing)

When physical aluminum mirror chassis or commercial display hardware is not yet in hand:

### Step 1: Standard Webcam Angle Simulation
1. Mount a standard UVC webcam on a monitor top bezel or tripod at approximately eye height ($1.5\text{ m}–1.6\text{ m}$).
2. Manually pitch webcam downward approximately $7^\circ$.
3. Stand $1.8\text{ m}$ back and verify in the frontend mirror viewport that your shoulders, hips, and knees remain in frame.

### Step 2: Headless Synthetic Telemetry Validation
1. If no webcam is attached to the workstation, execute `python -m unittest discover -s ai/tests`.
2. The AI module's `MockCamera` and `test_pose_pipeline.py` simulate frame ingestion and verify `TrackingFrame` serialization without requiring physical camera drivers.

---

## 3. Physical Test Execution Status Note
- **Current Status**: **SIMULATION / SPECIFICATION ONLY**.
- In accordance with team engineering ethics, **no physical workshop testing is claimed as completed** until the physical chassis, beamsplitter glass, and camera bracket are physically mounted and measured in the lab.
