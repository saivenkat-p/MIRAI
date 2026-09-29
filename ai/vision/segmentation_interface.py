"""
Abstract interface for Optional Body / Clothing Segmentation.
Prepares the architectural contract for future Phase 4/5 occlusion handling and background matting
without implementing expensive models prematurely.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple


class BaseBodySegmenter(ABC):
    """
    Abstract interface for body and clothing segmentation pipelines.
    Reserved for future occlusion mask generation.
    """

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize segmentation model/engine."""
        pass

    @abstractmethod
    def generate_mask(self, frame_bgr: Any) -> Optional[Any]:
        """
        Generate a binary or multi-class segmentation mask.
        Returns 2D NumPy array / mask buffer normalized [0, 255] or None.
        """
        pass

    @abstractmethod
    def release(self) -> None:
        """Release segmentation resources."""
        pass
