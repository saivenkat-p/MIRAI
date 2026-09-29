"""
Abstract interface for Pose Estimation implementations.
Defines contracts for MediaPipe/ONNX pose estimators without locking into specific implementations.
"""
from abc import ABC, abstractmethod
from typing import Any
from ..tracking.models import TrackingFrame


class BasePoseEstimator(ABC):
    """Abstract base class for MIRAI pose estimation engines."""

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the model and prepare GPU/CPU inference pipelines."""
        pass

    @abstractmethod
    def process_frame(self, frame_bgr: Any, frame_id: int, timestamp_ms: int) -> TrackingFrame:
        """
        Process an individual RGB/BGR video frame and extract 33 landmarks.
        Returns a normalized TrackingFrame object.
        """
        pass

    @abstractmethod
    def release(self) -> None:
        """Cleanly release hardware/model resources."""
        pass
