"""
Camera capture and real-time pose streaming pipeline.
Connects camera frame ingestion with pose estimation to emit TrackingFrame stream.
"""
from typing import Tuple, Any, Optional, Iterator
import time
from .camera_interface import BaseCameraCapture
from ..pose.interface import BasePoseEstimator
from ..tracking.models import TrackingFrame, TrackingState


class WebcamCapture(BaseCameraCapture):
    """OpenCV UVC webcam capture implementation."""

    def __init__(self, device_index: int = 0):
        self.device_index = device_index
        self._cap = None
        self._width = 1280
        self._height = 720
        self._fps = 30

    def open(self, device_index: int = 0, width: int = 1280, height: int = 720, fps: int = 30) -> bool:
        self.device_index = device_index
        self._width = width
        self._height = height
        self._fps = fps
        try:
            import cv2
            self._cap = cv2.VideoCapture(self.device_index)
            if not self._cap.isOpened():
                return False
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
            self._cap.set(cv2.CAP_PROP_FPS, self._fps)
            return True
        except ImportError:
            return False

    def read_frame(self) -> Tuple[bool, Optional[Any]]:
        if self._cap is None or not self._cap.isOpened():
            return False, None
        return self._cap.read()

    def is_opened(self) -> bool:
        return self._cap is not None and self._cap.isOpened()

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None


class PoseStreamer:
    """
    Coordinates camera capture and pose estimation pipeline to emit a stream of TrackingFrames.
    """

    def __init__(self, camera: BaseCameraCapture, estimator: BasePoseEstimator):
        self.camera = camera
        self.estimator = estimator
        self._running = False
        self._frame_id = 0

    def start(self) -> bool:
        """Initialize camera and estimator."""
        cam_ok = self.camera.open()
        est_ok = self.estimator.initialize()
        self._running = True
        return cam_ok

    def step(self) -> TrackingFrame:
        """Process one single frame and return the resulting TrackingFrame."""
        self._frame_id += 1
        now_ms = int(time.time() * 1000)

        ret, frame = self.camera.read_frame()
        if not ret or frame is None:
            return TrackingFrame(
                timestamp=now_ms,
                frame_id=self._frame_id,
                frame_width=1280,
                frame_height=720,
                fps=0.0,
                confidence=0.0,
                tracking_state=TrackingState.SEARCHING,
                landmarks=[]
            )

        return self.estimator.process_frame(
            frame_bgr=frame,
            frame_id=self._frame_id,
            timestamp_ms=now_ms
        )

    def stop(self) -> None:
        """Release camera and estimator resources."""
        self._running = False
        self.camera.release()
        self.estimator.release()
