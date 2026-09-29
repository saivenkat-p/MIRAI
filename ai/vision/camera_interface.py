"""
Camera hardware abstraction interface for AI video ingestion.
"""
from abc import ABC, abstractmethod
from typing import Tuple, Any, Optional


class BaseCameraCapture(ABC):
    """Abstract interface defining camera hardware connection contracts."""

    @abstractmethod
    def open(self, device_index: int = 0, width: int = 1280, height: int = 720, fps: int = 30) -> bool:
        """Open physical USB camera device or synthetic video stream."""
        pass

    @abstractmethod
    def read_frame(self) -> Tuple[bool, Optional[Any]]:
        """Read latest video frame. Returns (success, frame_data)."""
        pass

    @abstractmethod
    def is_opened(self) -> bool:
        """Check if camera device is actively streaming."""
        pass

    @abstractmethod
    def release(self) -> None:
        """Release camera hardware handle."""
        pass
