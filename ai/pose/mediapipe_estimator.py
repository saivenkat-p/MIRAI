"""
MediaPipe Pose Estimation pipeline for MIRAI AI subsystem.
Extracts 33 normalized body landmarks, calculates confidence, applies EMA smoothing,
and outputs structured TrackingFrame packets.
"""
from typing import Any, List, Optional
import time

from .interface import BasePoseEstimator
from ..tracking.models import Landmark, TrackingFrame, TrackingState
from ..tracking.smoothing import LandmarkSmoother

# Canonical 33 MediaPipe pose landmark names
MEDIAPIPE_LANDMARK_NAMES = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear", "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_pinky", "right_pinky",
    "left_index", "right_index", "left_thumb", "right_thumb",
    "left_hip", "right_hip", "left_knee", "right_knee",
    "left_ankle", "right_ankle", "left_heel", "right_heel",
    "left_foot_index", "right_foot_index"
]

# Core torso landmarks used for overall pose confidence calculation
KEY_TORSO_LANDMARK_IDS = [11, 12, 23, 24]  # left/right shoulders & hips


class MediaPipePoseEstimator(BasePoseEstimator):
    """
    Production MediaPipe pose estimator pipeline.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        smoothing_alpha: float = 0.65,
        model_complexity: int = 1
    ):
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.model_complexity = model_complexity
        self.smoother = LandmarkSmoother(alpha=smoothing_alpha)
        self._mp_pose = None
        self._pose_instance = None
        self._previous_state = TrackingState.SEARCHING
        self._last_frame_time = time.time()
        self._fps = 30.0

    def initialize(self) -> bool:
        """Initialize the MediaPipe Pose solution."""
        try:
            import mediapipe as mp
            if hasattr(mp, "solutions") and hasattr(mp.solutions, "pose"):
                self._mp_pose = mp.solutions.pose
                self._pose_instance = self._mp_pose.Pose(
                    min_detection_confidence=self.min_detection_confidence,
                    min_tracking_confidence=self.min_tracking_confidence,
                    model_complexity=self.model_complexity,
                    smooth_landmarks=True
                )
                return True
            # MediaPipe 1.0+ Tasks mode or graceful fallback
            self._pose_instance = None
            return True
        except Exception:
            # Graceful initialization fallback
            self._pose_instance = None
            return False

    def process_frame(
        self,
        frame_bgr: Any,
        frame_id: int,
        timestamp_ms: int,
        frame_width: int = 1280,
        frame_height: int = 720
    ) -> TrackingFrame:
        """
        Process a single image frame and return a TrackingFrame.
        """
        now = time.time()
        elapsed = now - self._last_frame_time
        if elapsed > 0:
            self._fps = 0.9 * self._fps + 0.1 * (1.0 / elapsed)
        self._last_frame_time = now

        raw_landmarks: List[Landmark] = []

        if self._pose_instance is not None and frame_bgr is not None:
            try:
                import cv2
                # MediaPipe requires RGB format
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                results = self._pose_instance.process(frame_rgb)

                if results.pose_landmarks:
                    for idx, lm in enumerate(results.pose_landmarks.landmark):
                        name = MEDIAPIPE_LANDMARK_NAMES[idx] if idx < len(MEDIAPIPE_LANDMARK_NAMES) else f"point_{idx}"
                        # Normalize coordinates strictly within [0.0, 1.0]
                        norm_x = max(0.0, min(1.0, float(lm.x)))
                        norm_y = max(0.0, min(1.0, float(lm.y)))
                        raw_landmarks.append(Landmark(
                            id=idx,
                            name=name,
                            x=round(norm_x, 5),
                            y=round(norm_y, 5),
                            z=round(float(lm.z), 5),
                            visibility=round(max(0.0, min(1.0, float(lm.visibility))), 4)
                        ))
            except Exception:
                raw_landmarks = []

        # Calculate tracking confidence from core torso landmarks
        confidence = 0.0
        if raw_landmarks:
            torso_visibilities = [
                lm.visibility for lm in raw_landmarks if lm.id in KEY_TORSO_LANDMARK_IDS
            ]
            if torso_visibilities:
                confidence = sum(torso_visibilities) / len(torso_visibilities)
            else:
                confidence = sum(lm.visibility for lm in raw_landmarks) / len(raw_landmarks)

        # Determine Tracking State transition
        if confidence >= 0.5 and len(raw_landmarks) >= 15:
            current_state = TrackingState.TRACKED
            smoothed_landmarks = self.smoother.smooth(raw_landmarks)
        elif self._previous_state == TrackingState.TRACKED and confidence < 0.3:
            current_state = TrackingState.LOST
            self.smoother.reset()
            smoothed_landmarks = []
        else:
            current_state = TrackingState.SEARCHING
            smoothed_landmarks = []

        self._previous_state = current_state

        return TrackingFrame(
            timestamp=timestamp_ms,
            frame_id=frame_id,
            frame_width=frame_width,
            frame_height=frame_height,
            fps=round(self._fps, 2),
            confidence=round(confidence, 4),
            tracking_state=current_state,
            landmarks=smoothed_landmarks
        )

    def release(self) -> None:
        """Release underlying pose pipeline resources."""
        if self._pose_instance is not None:
            self._pose_instance.close()
            self._pose_instance = None
        self.smoother.reset()
