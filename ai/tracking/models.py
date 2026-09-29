"""
Data models defining the AI -> Frontend TrackingFrame contract.
Matches specifications in /docs/INTEGRATION_CONTRACTS.md.
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional
import json


class TrackingState(str, Enum):
    SEARCHING = "searching"
    TRACKED = "tracked"
    LOST = "lost"
    CALIBRATING = "calibrating"


@dataclass
class Landmark:
    """Normalized 3D body landmark."""
    id: int
    name: str
    x: float
    y: float
    z: float = 0.0
    visibility: float = 1.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TrackingFrame:
    """Structured telemetry frame emitted by AI and consumed by Frontend."""
    timestamp: int
    frame_id: int
    frame_width: int
    frame_height: int
    fps: float
    confidence: float
    tracking_state: TrackingState
    landmarks: List[Landmark] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "frame_id": self.frame_id,
            "frame_width": self.frame_width,
            "frame_height": self.frame_height,
            "fps": round(self.fps, 2),
            "confidence": round(self.confidence, 4),
            "tracking_state": self.tracking_state.value if isinstance(self.tracking_state, TrackingState) else str(self.tracking_state),
            "landmarks": [lm.to_dict() for lm in self.landmarks]
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> "TrackingFrame":
        landmarks = [
            Landmark(
                id=lm["id"],
                name=lm.get("name", f"landmark_{lm['id']}"),
                x=lm["x"],
                y=lm["y"],
                z=lm.get("z", 0.0),
                visibility=lm.get("visibility", 1.0)
            )
            for lm in data.get("landmarks", [])
        ]
        return cls(
            timestamp=data["timestamp"],
            frame_id=data.get("frame_id", 0),
            frame_width=data.get("frame_width", 1280),
            frame_height=data.get("frame_height", 720),
            fps=float(data.get("fps", 30.0)),
            confidence=float(data.get("confidence", 0.0)),
            tracking_state=TrackingState(data.get("tracking_state", "searching")),
            landmarks=landmarks
        )
