"""
Unit tests validating Phase 1 AI pose estimation pipeline, smoothing, and streaming.
"""
import unittest
from ai.tracking.models import Landmark, TrackingFrame, TrackingState
from ai.tracking.smoothing import LandmarkSmoother
from ai.pose.mediapipe_estimator import MediaPipePoseEstimator, MEDIAPIPE_LANDMARK_NAMES
from ai.vision.camera_interface import BaseCameraCapture
from ai.vision.streamer import PoseStreamer


class MockCamera(BaseCameraCapture):
    """Mock camera for headless pipeline testing."""

    def __init__(self, produce_frames: bool = True):
        self.produce_frames = produce_frames
        self._opened = False

    def open(self, device_index: int = 0, width: int = 1280, height: int = 720, fps: int = 30) -> bool:
        self._opened = True
        return True

    def read_frame(self):
        if not self._opened or not self.produce_frames:
            return False, None
        # Return mock 10x10 dummy image array or marker
        return True, "mock_frame_data"

    def is_opened(self) -> bool:
        return self._opened

    def release(self) -> None:
        self._opened = False


class TestPosePipeline(unittest.TestCase):

    def test_landmark_smoother(self):
        smoother = LandmarkSmoother(alpha=0.5)

        # Frame 1: Initial position at 0.0
        raw_f1 = [Landmark(id=11, name="left_shoulder", x=0.0, y=0.0, z=0.0, visibility=1.0)]
        smoothed_f1 = smoother.smooth(raw_f1)
        self.assertEqual(smoothed_f1[0].x, 0.0)

        # Frame 2: Sudden jitter jump to 1.0 -> smoothed value should be 0.5 * 1.0 + 0.5 * 0.0 = 0.5
        raw_f2 = [Landmark(id=11, name="left_shoulder", x=1.0, y=0.0, z=0.0, visibility=1.0)]
        smoothed_f2 = smoother.smooth(raw_f2)
        self.assertAlmostEqual(smoothed_f2[0].x, 0.5, places=2)

        # Frame 3: Stays at 1.0 -> smoothed value: 0.5 * 1.0 + 0.5 * 0.5 = 0.75
        raw_f3 = [Landmark(id=11, name="left_shoulder", x=1.0, y=0.0, z=0.0, visibility=1.0)]
        smoothed_f3 = smoother.smooth(raw_f3)
        self.assertAlmostEqual(smoothed_f3[0].x, 0.75, places=2)

        # Reset filter
        smoother.reset()
        self.assertEqual(len(smoother._prev_landmarks), 0)

    def test_mediapipe_canonical_names_count(self):
        self.assertEqual(len(MEDIAPIPE_LANDMARK_NAMES), 33)
        self.assertEqual(MEDIAPIPE_LANDMARK_NAMES[0], "nose")
        self.assertEqual(MEDIAPIPE_LANDMARK_NAMES[11], "left_shoulder")
        self.assertEqual(MEDIAPIPE_LANDMARK_NAMES[12], "right_shoulder")
        self.assertEqual(MEDIAPIPE_LANDMARK_NAMES[23], "left_hip")
        self.assertEqual(MEDIAPIPE_LANDMARK_NAMES[24], "right_hip")

    def test_pose_estimator_empty_frame(self):
        estimator = MediaPipePoseEstimator()
        frame = estimator.process_frame(
            frame_bgr=None,
            frame_id=1,
            timestamp_ms=1000,
            frame_width=1280,
            frame_height=720
        )
        self.assertIsInstance(frame, TrackingFrame)
        self.assertEqual(frame.frame_id, 1)
        self.assertEqual(frame.tracking_state, TrackingState.SEARCHING)
        self.assertEqual(frame.confidence, 0.0)
        self.assertEqual(len(frame.landmarks), 0)

    def test_pose_streamer_pipeline(self):
        camera = MockCamera(produce_frames=False)
        estimator = MediaPipePoseEstimator()
        streamer = PoseStreamer(camera, estimator)

        streamer.start()
        frame = streamer.step()
        self.assertEqual(frame.tracking_state, TrackingState.SEARCHING)
        self.assertEqual(frame.confidence, 0.0)
        streamer.stop()
        self.assertFalse(camera.is_opened())


if __name__ == "__main__":
    unittest.main()
