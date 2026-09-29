"""
Body Anchor Extraction for Virtual Garment Alignment.
Derives torso center, shoulder/hip widths, rotation angles, and garment anchor points
from normalized pose landmarks with confidence-weighted stability.

Coordinate System Specification:
--------------------------------
- Normalized Range: [0.0, 1.0] for X and Y coordinates.
- Origin (0.0, 0.0): Top-Left corner of the frame.
- X Axis: Left to Right (0.0 = Left edge, 1.0 = Right edge).
- Y Axis: Top to Bottom (0.0 = Top edge, 1.0 = Bottom edge).
- Z Axis: Relative depth from mid-hip reference plane (negative = closer to camera).
- Angle Conventions:
    - 0 radians (0 deg): Horizontal line pointing from Left Shoulder to Right Shoulder.
    - Positive angles: Clockwise rotation in image space.
"""
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import math
from .models import Landmark, TrackingState


@dataclass
class Point2D:
    x: float
    y: float

    def to_dict(self) -> dict:
        return {"x": round(self.x, 5), "y": round(self.y, 5)}


@dataclass
class BoundingBox:
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    width: float
    height: float

    def to_dict(self) -> dict:
        return {
            "min_x": round(self.min_x, 5),
            "min_y": round(self.min_y, 5),
            "max_x": round(self.max_x, 5),
            "max_y": round(self.max_y, 5),
            "width": round(self.width, 5),
            "height": round(self.height, 5)
        }


@dataclass
class BodyAnchors:
    """Garment-relevant body geometry and rotation angles."""
    # Key Anchor Joints
    left_shoulder: Optional[Point2D]
    right_shoulder: Optional[Point2D]
    left_hip: Optional[Point2D]
    right_hip: Optional[Point2D]
    left_elbow: Optional[Point2D]
    right_elbow: Optional[Point2D]
    left_wrist: Optional[Point2D]
    right_wrist: Optional[Point2D]

    # Derived Metrics
    shoulder_width: float
    hip_width: float
    torso_center: Point2D
    torso_height: float
    shoulder_angle_deg: float
    shoulder_angle_rad: float
    torso_angle_deg: float
    torso_angle_rad: float
    bounding_box: BoundingBox
    confidence: float
    is_valid: bool

    def to_dict(self) -> dict:
        return {
            "left_shoulder": self.left_shoulder.to_dict() if self.left_shoulder else None,
            "right_shoulder": self.right_shoulder.to_dict() if self.right_shoulder else None,
            "left_hip": self.left_hip.to_dict() if self.left_hip else None,
            "right_hip": self.right_hip.to_dict() if self.right_hip else None,
            "left_elbow": self.left_elbow.to_dict() if self.left_elbow else None,
            "right_elbow": self.right_elbow.to_dict() if self.right_elbow else None,
            "left_wrist": self.left_wrist.to_dict() if self.left_wrist else None,
            "right_wrist": self.right_wrist.to_dict() if self.right_wrist else None,
            "shoulder_width": round(self.shoulder_width, 5),
            "hip_width": round(self.hip_width, 5),
            "torso_center": self.torso_center.to_dict(),
            "torso_height": round(self.torso_height, 5),
            "shoulder_angle_deg": round(self.shoulder_angle_deg, 2),
            "shoulder_angle_rad": round(self.shoulder_angle_rad, 4),
            "torso_angle_deg": round(self.torso_angle_deg, 2),
            "torso_angle_rad": round(self.torso_angle_rad, 4),
            "bounding_box": self.bounding_box.to_dict(),
            "confidence": round(self.confidence, 4),
            "is_valid": self.is_valid
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BodyAnchors":
        def _to_pt(d):
            return Point2D(x=d["x"], y=d["y"]) if d else None

        bb_data = data.get("bounding_box", {})
        bb = BoundingBox(
            min_x=bb_data.get("min_x", 0.0),
            min_y=bb_data.get("min_y", 0.0),
            max_x=bb_data.get("max_x", 0.0),
            max_y=bb_data.get("max_y", 0.0),
            width=bb_data.get("width", 0.0),
            height=bb_data.get("height", 0.0)
        )

        return cls(
            left_shoulder=_to_pt(data.get("left_shoulder")),
            right_shoulder=_to_pt(data.get("right_shoulder")),
            left_hip=_to_pt(data.get("left_hip")),
            right_hip=_to_pt(data.get("right_hip")),
            left_elbow=_to_pt(data.get("left_elbow")),
            right_elbow=_to_pt(data.get("right_elbow")),
            left_wrist=_to_pt(data.get("left_wrist")),
            right_wrist=_to_pt(data.get("right_wrist")),
            shoulder_width=float(data.get("shoulder_width", 0.0)),
            hip_width=float(data.get("hip_width", 0.0)),
            torso_center=Point2D(x=data.get("torso_center", {}).get("x", 0.5), y=data.get("torso_center", {}).get("y", 0.5)),
            torso_height=float(data.get("torso_height", 0.0)),
            shoulder_angle_deg=float(data.get("shoulder_angle_deg", 0.0)),
            shoulder_angle_rad=float(data.get("shoulder_angle_rad", 0.0)),
            torso_angle_deg=float(data.get("torso_angle_deg", 0.0)),
            torso_angle_rad=float(data.get("torso_angle_rad", 0.0)),
            bounding_box=bb,
            confidence=float(data.get("confidence", 0.0)),
            is_valid=bool(data.get("is_valid", False))
        )


class BodyAnchorExtractor:
    """
    Extracts garment anchor points and geometric measurements from pose landmarks.
    Handles degraded confidence and brief landmark dropouts gracefully to avoid visual snapping.
    """

    MIN_CONFIDENCE_THRESHOLD = 0.35
    MAX_HOLD_FRAMES = 5

    def __init__(self):
        self._last_valid_anchors: Optional[BodyAnchors] = None
        self._dropout_frames = 0

    def extract(self, landmarks: List[Landmark]) -> Optional[BodyAnchors]:
        """
        Derives BodyAnchors from a list of 33 MediaPipe landmarks.
        Returns BodyAnchors or None if tracking is unavailable.
        """
        if not landmarks:
            return self._handle_dropout()

        lm_map: Dict[int, Landmark] = {lm.id: lm for lm in landmarks}

        # Check required torso anchor landmarks (11: L_shoulder, 12: R_shoulder, 23: L_hip, 24: R_hip)
        ls = lm_map.get(11)
        rs = lm_map.get(12)
        lh = lm_map.get(23)
        rh = lm_map.get(24)

        if not ls or not rs or not lh or not rh:
            return self._handle_dropout()

        # Check visibility threshold for core anchors
        core_vis = [ls.visibility, rs.visibility, lh.visibility, rh.visibility]
        mean_confidence = sum(core_vis) / len(core_vis)

        if mean_confidence < self.MIN_CONFIDENCE_THRESHOLD:
            return self._handle_dropout()

        # Extract optional arm anchors (13: L_elbow, 14: R_elbow, 15: L_wrist, 16: R_wrist)
        le = lm_map.get(13)
        re = lm_map.get(14)
        lw = lm_map.get(15)
        rw = lm_map.get(16)

        def _get_pt(lm: Optional[Landmark]) -> Optional[Point2D]:
            if lm and lm.visibility >= self.MIN_CONFIDENCE_THRESHOLD:
                return Point2D(x=lm.x, y=lm.y)
            return None

        left_shoulder_pt = Point2D(x=ls.x, y=ls.y)
        right_shoulder_pt = Point2D(x=rs.x, y=rs.y)
        left_hip_pt = Point2D(x=lh.x, y=lh.y)
        right_hip_pt = Point2D(x=rh.x, y=rh.y)

        # 1. Shoulder width & angle
        dx_s = right_shoulder_pt.x - left_shoulder_pt.x
        dy_s = right_shoulder_pt.y - left_shoulder_pt.y
        shoulder_width = math.hypot(dx_s, dy_s)
        shoulder_angle_rad = math.atan2(dy_s, dx_s)
        shoulder_angle_deg = math.degrees(shoulder_angle_rad)

        # 2. Hip width
        dx_h = right_hip_pt.x - left_hip_pt.x
        dy_h = right_hip_pt.y - left_hip_pt.y
        hip_width = math.hypot(dx_h, dy_h)

        # 3. Torso Center & Torso Height
        mid_shoulder = Point2D(
            x=(left_shoulder_pt.x + right_shoulder_pt.x) * 0.5,
            y=(left_shoulder_pt.y + right_shoulder_pt.y) * 0.5
        )
        mid_hip = Point2D(
            x=(left_hip_pt.x + right_hip_pt.x) * 0.5,
            y=(left_hip_pt.y + right_hip_pt.y) * 0.5
        )
        torso_center = Point2D(
            x=(mid_shoulder.x + mid_hip.x) * 0.5,
            y=(mid_shoulder.y + mid_hip.y) * 0.5
        )

        dx_t = mid_hip.x - mid_shoulder.x
        dy_t = mid_hip.y - mid_shoulder.y
        torso_height = math.hypot(dx_t, dy_t)

        # Torso angle relative to vertical (0 deg = upright standing)
        torso_angle_rad = math.atan2(dx_t, dy_t)
        torso_angle_deg = math.degrees(torso_angle_rad)

        # 4. Upper body bounding region
        pts_to_bound = [left_shoulder_pt, right_shoulder_pt, left_hip_pt, right_hip_pt]
        for opt_pt in [_get_pt(le), _get_pt(re), _get_pt(lw), _get_pt(rw)]:
            if opt_pt:
                pts_to_bound.append(opt_pt)

        xs = [p.x for p in pts_to_bound]
        ys = [p.y for p in pts_to_bound]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        bounding_box = BoundingBox(
            min_x=min_x,
            min_y=min_y,
            max_x=max_x,
            max_y=max_y,
            width=max_x - min_x,
            height=max_y - min_y
        )

        anchors = BodyAnchors(
            left_shoulder=left_shoulder_pt,
            right_shoulder=right_shoulder_pt,
            left_hip=left_hip_pt,
            right_hip=right_hip_pt,
            left_elbow=_get_pt(le),
            right_elbow=_get_pt(re),
            left_wrist=_get_pt(lw),
            right_wrist=_get_pt(rw),
            shoulder_width=shoulder_width,
            hip_width=hip_width,
            torso_center=torso_center,
            torso_height=torso_height,
            shoulder_angle_deg=shoulder_angle_deg,
            shoulder_angle_rad=shoulder_angle_rad,
            torso_angle_deg=torso_angle_deg,
            torso_angle_rad=torso_angle_rad,
            bounding_box=bounding_box,
            confidence=mean_confidence,
            is_valid=True
        )

        self._last_valid_anchors = anchors
        self._dropout_frames = 0
        return anchors

    def _handle_dropout(self) -> Optional[BodyAnchors]:
        """Holds previous valid anchor state during brief dropout (up to MAX_HOLD_FRAMES)."""
        self._dropout_frames += 1
        if self._last_valid_anchors is not None and self._dropout_frames <= self.MAX_HOLD_FRAMES:
            # Return cached anchors with degraded confidence flag
            decay = max(0.1, 1.0 - (self._dropout_frames / (self.MAX_HOLD_FRAMES + 1)))
            return BodyAnchors(
                left_shoulder=self._last_valid_anchors.left_shoulder,
                right_shoulder=self._last_valid_anchors.right_shoulder,
                left_hip=self._last_valid_anchors.left_hip,
                right_hip=self._last_valid_anchors.right_hip,
                left_elbow=self._last_valid_anchors.left_elbow,
                right_elbow=self._last_valid_anchors.right_elbow,
                left_wrist=self._last_valid_anchors.left_wrist,
                right_wrist=self._last_valid_anchors.right_wrist,
                shoulder_width=self._last_valid_anchors.shoulder_width,
                hip_width=self._last_valid_anchors.hip_width,
                torso_center=self._last_valid_anchors.torso_center,
                torso_height=self._last_valid_anchors.torso_height,
                shoulder_angle_deg=self._last_valid_anchors.shoulder_angle_deg,
                shoulder_angle_rad=self._last_valid_anchors.shoulder_angle_rad,
                torso_angle_deg=self._last_valid_anchors.torso_angle_deg,
                torso_angle_rad=self._last_valid_anchors.torso_angle_rad,
                bounding_box=self._last_valid_anchors.bounding_box,
                confidence=self._last_valid_anchors.confidence * decay,
                is_valid=False  # Marked invalid to signal hold state
            )

        self.reset()
        return None

    def reset(self) -> None:
        """Resets cached state on tracking loss."""
        self._last_valid_anchors = None
        self._dropout_frames = 0
