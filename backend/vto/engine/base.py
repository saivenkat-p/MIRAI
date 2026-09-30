from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np

class IVTOEngine(ABC):
    """
    Standardized Hardware Abstraction Layer (HAL) for MIRAI VTO Engines.
    GPU-agnostic: implemented by lightweight edge engines (GTX 1650 / RTX 4050),
    high-end kiosk engines (RTX 4090/5090), and cloud workers.
    """

    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize models, configure device, allocate execution buffers."""
        pass

    @abstractmethod
    def load_garment(self, garment_id: str, garment_path: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Load and cache garment texture, alpha mask, and anchor points."""
        pass

    @abstractmethod
    def process_frame(
        self,
        frame_bgr: np.ndarray,
        pose_landmarks: Optional[Dict[str, Any]] = None,
        segmentation_mask: Optional[np.ndarray] = None,
        garment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single input frame through the VTO pipeline.
        Returns dict containing:
          - 'output_frame': np.ndarray (H, W, 3) BGR
          - 'latency_breakdown_ms': dict of stage timings
          - 'metrics': FPS, VRAM usage, device info
        """
        pass

    @abstractmethod
    def get_hardware_info(self) -> Dict[str, Any]:
        """Return detected hardware details (GPU, VRAM, compute device)."""
        pass
