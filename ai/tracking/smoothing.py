"""
Landmark temporal smoothing filter using Exponential Moving Average (EMA).
Reduces high-frequency jitter in pose landmark coordinates for stable AR tracking.
"""
from typing import Dict, List, Optional
from .models import Landmark


class LandmarkSmoother:
    """
    Applies exponential moving average smoothing across consecutive video frames.
    smoothed = alpha * current + (1 - alpha) * previous
    """

    def __init__(self, alpha: float = 0.65):
        """
        :param alpha: Smoothing factor between 0.0 (maximum lag, infinite smoothing)
                      and 1.0 (no smoothing, raw sensor coordinates).
        """
        self.alpha = max(0.01, min(1.0, alpha))
        self._prev_landmarks: Dict[int, Landmark] = {}

    def smooth(self, raw_landmarks: List[Landmark]) -> List[Landmark]:
        """Smooth a list of raw landmarks using previous frame state."""
        smoothed_list: List[Landmark] = []

        for current in raw_landmarks:
            prev = self._prev_landmarks.get(current.id)

            if prev is None or current.visibility < 0.2:
                # First time seeing landmark or low visibility: use raw value
                smoothed_list.append(current)
                if current.visibility >= 0.2:
                    self._prev_landmarks[current.id] = current
            else:
                # Apply EMA filter to x, y, z
                sm_x = self.alpha * current.x + (1.0 - self.alpha) * prev.x
                sm_y = self.alpha * current.y + (1.0 - self.alpha) * prev.y
                sm_z = self.alpha * current.z + (1.0 - self.alpha) * prev.z
                # Visibility is tracked with higher weight on recent frame
                sm_vis = 0.8 * current.visibility + 0.2 * prev.visibility

                smoothed_lm = Landmark(
                    id=current.id,
                    name=current.name,
                    x=round(sm_x, 5),
                    y=round(sm_y, 5),
                    z=round(sm_z, 5),
                    visibility=round(sm_vis, 4)
                )
                smoothed_list.append(smoothed_lm)
                self._prev_landmarks[current.id] = smoothed_lm

        return smoothed_list

    def reset(self) -> None:
        """Clear filter history (e.g. when track is lost or new person enters)."""
        self._prev_landmarks.clear()
