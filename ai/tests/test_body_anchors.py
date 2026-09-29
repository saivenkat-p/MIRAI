"""
Comprehensive unit tests for Phase 2 Body Anchor Extraction, confidence handling,
and geometric derivations for virtual garment fitting.
"""
import unittest
import math
import json
from ai.tracking.models import Landmark, TrackingFrame, TrackingState
from ai.tracking.anchors import BodyAnchors, BodyAnchorExtractor, Point2D, BoundingBox
from ai.tracking.smoothing import LandmarkSmoother


class TestBodyAnchors(unittest.TestCase):

    def _create_standard_torso_landmarks(self, confidence: float = 0.95):
        """Creates standard normalized landmarks for an upright standing subject."""
        return [
            Landmark(id=11, name="left_shoulder", x=0.40, y=0.30, z=0.0, visibility=confidence),
            Landmark(id=12, name="right_shoulder", x=0.60, y=0.30, z=0.0, visibility=confidence),
            Landmark(id=23, name="left_hip", x=0.42, y=0.60, z=0.0, visibility=confidence),
            Landmark(id=24, name="right_hip", x=0.58, y=0.60, z=0.0, visibility=confidence),
            Landmark(id=13, name="left_elbow", x=0.35, y=0.45, z=0.0, visibility=confidence),
            Landmark(id=14, name="right_elbow", x=0.65, y=0.45, z=0.0, visibility=confidence),
            Landmark(id=15, name="left_wrist", x=0.32, y=0.58, z=0.0, visibility=confidence),
            Landmark(id=16, name="right_wrist", x=0.68, y=0.58, z=0.0, visibility=confidence),
        ]

    def test_anchor_extraction_and_geometry(self):
        extractor = BodyAnchorExtractor()
        landmarks = self._create_standard_torso_landmarks(confidence=0.95)

        anchors = extractor.extract(landmarks)
        self.assertIsNotNone(anchors)
        self.assertTrue(anchors.is_valid)

        # 1. Shoulder width: |0.60 - 0.40| = 0.20
        self.assertAlmostEqual(anchors.shoulder_width, 0.20, places=4)

        # 2. Hip width: |0.58 - 0.42| = 0.16
        self.assertAlmostEqual(anchors.hip_width, 0.16, places=4)

        # 3. Torso center:
        # mid_shoulder = (0.50, 0.30)
        # mid_hip = (0.50, 0.60)
        # torso_center = (0.50, 0.45)
        self.assertAlmostEqual(anchors.torso_center.x, 0.50, places=4)
        self.assertAlmostEqual(anchors.torso_center.y, 0.45, places=4)

        # 4. Torso height: |0.60 - 0.30| = 0.30
        self.assertAlmostEqual(anchors.torso_height, 0.30, places=4)

        # 5. Shoulder angle: horizontal shoulders -> dy = 0 -> angle = 0.0 deg
        self.assertAlmostEqual(anchors.shoulder_angle_deg, 0.0, places=2)

        # 6. Upper body bounding region
        self.assertAlmostEqual(anchors.bounding_box.min_x, 0.32, places=2)
        self.assertAlmostEqual(anchors.bounding_box.max_x, 0.68, places=2)
        self.assertAlmostEqual(anchors.bounding_box.min_y, 0.30, places=2)
        self.assertAlmostEqual(anchors.bounding_box.max_y, 0.60, places=2)

    def test_shoulder_angle_tilt(self):
        extractor = BodyAnchorExtractor()
        # Right shoulder slightly lower (y=0.35) than left (y=0.25)
        landmarks = [
            Landmark(id=11, name="left_shoulder", x=0.40, y=0.25, z=0.0, visibility=0.9),
            Landmark(id=12, name="right_shoulder", x=0.60, y=0.35, z=0.0, visibility=0.9),
            Landmark(id=23, name="left_hip", x=0.42, y=0.55, z=0.0, visibility=0.9),
            Landmark(id=24, name="right_hip", x=0.58, y=0.65, z=0.0, visibility=0.9),
        ]
        anchors = extractor.extract(landmarks)
        self.assertIsNotNone(anchors)
        # dx = 0.20, dy = 0.10 -> angle = atan2(0.1, 0.2) = 26.56 deg
        expected_angle = math.degrees(math.atan2(0.10, 0.20))
        self.assertAlmostEqual(anchors.shoulder_angle_deg, expected_angle, places=1)

    def test_low_confidence_and_dropout_handling(self):
        extractor = BodyAnchorExtractor()

        # Step 1: Valid initial detection
        landmarks = self._create_standard_torso_landmarks(confidence=0.9)
        anchors1 = extractor.extract(landmarks)
        self.assertIsNotNone(anchors1)
        self.assertTrue(anchors1.is_valid)

        # Step 2: Temporary missing landmark / dropout (frame 2)
        # Should gracefully hold previous valid anchors without crashing or sudden jump
        anchors2 = extractor.extract([])
        self.assertIsNotNone(anchors2)
        self.assertFalse(anchors2.is_valid)  # Held state marked invalid
        self.assertAlmostEqual(anchors2.shoulder_width, anchors1.shoulder_width, places=4)
        self.assertLess(anchors2.confidence, anchors1.confidence)  # Decayed confidence

        # Step 3: Sustained dropout exceeds MAX_HOLD_FRAMES (6 frames) -> returns None
        for _ in range(BodyAnchorExtractor.MAX_HOLD_FRAMES):
            extractor.extract([])
        anchors_dropped = extractor.extract([])
        self.assertIsNone(anchors_dropped)

    def test_low_confidence_rejection(self):
        extractor = BodyAnchorExtractor()
        # Landmarks with visibility below threshold (0.2 < 0.35)
        landmarks = self._create_standard_torso_landmarks(confidence=0.2)
        anchors = extractor.extract(landmarks)
        self.assertIsNone(anchors)

    def test_smoothing_temporal_stability(self):
        smoother = LandmarkSmoother(alpha=0.6)
        extractor = BodyAnchorExtractor()

        # Stationary subject across 10 frames with slight jitter (+-0.005)
        raw_x_values = [0.40, 0.405, 0.395, 0.402, 0.398, 0.401, 0.404, 0.397, 0.403, 0.400]
        recorded_shoulder_widths = []

        for x in raw_x_values:
            frame_lms = [
                Landmark(id=11, name="left_shoulder", x=x, y=0.30, z=0.0, visibility=0.95),
                Landmark(id=12, name="right_shoulder", x=0.60, y=0.30, z=0.0, visibility=0.95),
                Landmark(id=23, name="left_hip", x=0.42, y=0.60, z=0.0, visibility=0.95),
                Landmark(id=24, name="right_hip", x=0.58, y=0.60, z=0.0, visibility=0.95),
            ]
            smoothed = smoother.smooth(frame_lms)
            anchors = extractor.extract(smoothed)
            self.assertIsNotNone(anchors)
            recorded_shoulder_widths.append(anchors.shoulder_width)

        # Standard deviation of smoothed shoulder width should be significantly dampened
        variance = sum((w - 0.20) ** 2 for w in recorded_shoulder_widths) / len(recorded_shoulder_widths)
        std_dev = math.sqrt(variance)
        self.assertLess(std_dev, 0.005)

    def test_tracking_frame_serialization_with_anchors(self):
        landmarks = self._create_standard_torso_landmarks()
        extractor = BodyAnchorExtractor()
        anchors = extractor.extract(landmarks)

        frame = TrackingFrame(
            timestamp=1727625600000,
            frame_id=101,
            frame_width=1080,
            frame_height=1920,
            fps=30.0,
            confidence=0.95,
            tracking_state=TrackingState.TRACKED,
            landmarks=landmarks,
            body_anchors=anchors
        )

        d = frame.to_dict()
        self.assertIn("body_anchors", d)
        self.assertEqual(d["body_anchors"]["shoulder_angle_deg"], 0.0)
        self.assertAlmostEqual(d["body_anchors"]["shoulder_width"], 0.20, places=4)

        # JSON serialization round trip
        json_str = frame.to_json()
        reconstructed = TrackingFrame.from_dict(json.loads(json_str))
        self.assertIsNotNone(reconstructed.body_anchors)
        self.assertEqual(reconstructed.body_anchors.shoulder_angle_deg, 0.0)


if __name__ == "__main__":
    import json
    unittest.main()
