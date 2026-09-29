"""
Unit tests validating AI TrackingFrame contract against /docs/INTEGRATION_CONTRACTS.md.
"""
import unittest
import json
from ai.tracking.models import TrackingFrame, Landmark, TrackingState


class TestTrackingContract(unittest.TestCase):

    def test_landmark_serialization(self):
        lm = Landmark(id=11, name="left_shoulder", x=0.45, y=0.32, z=-0.05, visibility=0.98)
        d = lm.to_dict()
        self.assertEqual(d["id"], 11)
        self.assertEqual(d["name"], "left_shoulder")
        self.assertEqual(d["x"], 0.45)
        self.assertEqual(d["y"], 0.32)
        self.assertEqual(d["z"], -0.05)
        self.assertEqual(d["visibility"], 0.98)

    def test_tracking_frame_contract(self):
        lm1 = Landmark(id=11, name="left_shoulder", x=0.45, y=0.32, z=-0.05, visibility=0.98)
        lm2 = Landmark(id=12, name="right_shoulder", x=0.55, y=0.32, z=-0.05, visibility=0.98)
        frame = TrackingFrame(
            timestamp=1727625600000,
            frame_id=1,
            frame_width=1280,
            frame_height=720,
            fps=30.0,
            confidence=0.96,
            tracking_state=TrackingState.TRACKED,
            landmarks=[lm1, lm2]
        )

        serialized = frame.to_dict()
        self.assertEqual(serialized["timestamp"], 1727625600000)
        self.assertEqual(serialized["fps"], 30.0)
        self.assertEqual(serialized["confidence"], 0.96)
        self.assertEqual(serialized["tracking_state"], "tracked")
        self.assertEqual(len(serialized["landmarks"]), 2)

        # Test JSON round-trip
        json_str = frame.to_json()
        loaded = json.loads(json_str)
        self.assertIn("landmarks", loaded)
        self.assertEqual(loaded["tracking_state"], "tracked")

        # Test reconstruction
        reconstructed = TrackingFrame.from_dict(loaded)
        self.assertEqual(reconstructed.frame_id, 1)
        self.assertEqual(len(reconstructed.landmarks), 2)
        self.assertEqual(reconstructed.landmarks[0].name, "left_shoulder")


if __name__ == "__main__":
    unittest.main()
