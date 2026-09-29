import { useState, useEffect } from 'react';
import { TrackingFrame, Landmark, BodyAnchors, Point2D, BoundingBox } from '../types/tracking';

/**
 * Hook for consuming AI TrackingFrame stream.
 * Adheres strictly to the AI -> Frontend contract defined in /docs/INTEGRATION_CONTRACTS.md
 * and Phase 2 Body Geometry extensions.
 */
export function usePoseStream(streamUrl?: string) {
  const [currentFrame, setCurrentFrame] = useState<TrackingFrame>({
    timestamp: Date.now(),
    frame_id: 0,
    frame_width: 1080,
    frame_height: 1920,
    fps: 30,
    confidence: 0.95,
    tracking_state: 'tracked',
    landmarks: []
  });

  useEffect(() => {
    let animationFrameId: number;
    let startTime = Date.now();
    let frameCounter = 0;

    // Simulation of natural human posture conforming to AI Phase 2 BodyAnchors contract
    const updateFrame = () => {
      frameCounter++;
      const elapsed = (Date.now() - startTime) / 1000;

      // Gentle natural breathing & slight lateral swaying
      const swayX = Math.sin(elapsed * 1.5) * 0.02;
      const swayY = Math.cos(elapsed * 2.0) * 0.01;
      const shoulderTiltDeg = Math.sin(elapsed * 1.2) * 3.5; // Natural +-3.5 deg shoulder tilt
      const shoulderTiltRad = (shoulderTiltDeg * Math.PI) / 180;
      const tiltDeltaY = Math.tan(shoulderTiltRad) * 0.08;

      const lsPt: Point2D = { x: 0.42 + swayX, y: 0.32 + swayY - tiltDeltaY };
      const rsPt: Point2D = { x: 0.58 + swayX, y: 0.32 + swayY + tiltDeltaY };
      const lhPt: Point2D = { x: 0.44 + swayX, y: 0.56 + swayY };
      const rhPt: Point2D = { x: 0.56 + swayX, y: 0.56 + swayY };

      const lePt: Point2D = { x: 0.38 + swayX, y: 0.45 + swayY };
      const rePt: Point2D = { x: 0.62 + swayX, y: 0.45 + swayY };
      const lwPt: Point2D = { x: 0.36 + swayX, y: 0.58 + swayY };
      const rwPt: Point2D = { x: 0.64 + swayX, y: 0.58 + swayY };

      // Base standing landmarks (normalized 0.0 - 1.0)
      const mockLandmarks: Landmark[] = [
        { id: 0, name: 'nose', x: 0.50 + swayX, y: 0.22 + swayY, z: -0.1, visibility: 0.99 },
        { id: 11, name: 'left_shoulder', x: lsPt.x, y: lsPt.y, z: -0.05, visibility: 0.98 },
        { id: 12, name: 'right_shoulder', x: rsPt.x, y: rsPt.y, z: -0.05, visibility: 0.98 },
        { id: 13, name: 'left_elbow', x: lePt.x, y: lePt.y, z: -0.02, visibility: 0.96 },
        { id: 14, name: 'right_elbow', x: rePt.x, y: rePt.y, z: -0.02, visibility: 0.96 },
        { id: 15, name: 'left_wrist', x: lwPt.x, y: lwPt.y, z: 0.01, visibility: 0.94 },
        { id: 16, name: 'right_wrist', x: rwPt.x, y: rwPt.y, z: 0.01, visibility: 0.94 },
        { id: 23, name: 'left_hip', x: lhPt.x, y: lhPt.y, z: 0.0, visibility: 0.97 },
        { id: 24, name: 'right_hip', x: rhPt.x, y: rhPt.y, z: 0.0, visibility: 0.97 },
        { id: 25, name: 'left_knee', x: 0.43 + swayX, y: 0.74 + swayY, z: 0.02, visibility: 0.95 },
        { id: 26, name: 'right_knee', x: 0.57 + swayX, y: 0.74 + swayY, z: 0.02, visibility: 0.95 },
        { id: 27, name: 'left_ankle', x: 0.42 + swayX, y: 0.91 + swayY, z: 0.04, visibility: 0.93 },
        { id: 28, name: 'right_ankle', x: 0.58 + swayX, y: 0.91 + swayY, z: 0.04, visibility: 0.93 },
      ];

      const dxS = rsPt.x - lsPt.x;
      const dyS = rsPt.y - lsPt.y;
      const shoulderWidth = Math.hypot(dxS, dyS);
      const shoulderAngleRad = Math.atan2(dyS, dxS);
      const shoulderAngleDeg = (shoulderAngleRad * 180) / Math.PI;

      const midShoulder: Point2D = { x: (lsPt.x + rsPt.x) * 0.5, y: (lsPt.y + rsPt.y) * 0.5 };
      const midHip: Point2D = { x: (lhPt.x + rhPt.x) * 0.5, y: (lhPt.y + rhPt.y) * 0.5 };
      const torsoCenter: Point2D = { x: (midShoulder.x + midHip.x) * 0.5, y: (midShoulder.y + midHip.y) * 0.5 };
      const torsoHeight = Math.hypot(midHip.x - midShoulder.x, midHip.y - midShoulder.y);

      const boundingBox: BoundingBox = {
        min_x: lwPt.x,
        min_y: lsPt.y,
        max_x: rwPt.x,
        max_y: lhPt.y,
        width: rwPt.x - lwPt.x,
        height: lhPt.y - lsPt.y
      };

      const bodyAnchors: BodyAnchors = {
        left_shoulder: lsPt,
        right_shoulder: rsPt,
        left_hip: lhPt,
        right_hip: rhPt,
        left_elbow: lePt,
        right_elbow: rePt,
        left_wrist: lwPt,
        right_wrist: rwPt,
        shoulder_width: shoulderWidth,
        hip_width: Math.hypot(rhPt.x - lhPt.x, rhPt.y - lhPt.y),
        torso_center: torsoCenter,
        torso_height: torsoHeight,
        shoulder_angle_deg: shoulderAngleDeg,
        shoulder_angle_rad: shoulderAngleRad,
        torso_angle_deg: 0.0,
        torso_angle_rad: 0.0,
        bounding_box: boundingBox,
        confidence: 0.96,
        is_valid: true
      };

      setCurrentFrame({
        timestamp: Date.now(),
        frame_id: frameCounter,
        frame_width: 1080,
        frame_height: 1920,
        fps: 30.0,
        confidence: 0.96,
        tracking_state: 'tracked',
        landmarks: mockLandmarks,
        body_anchors: bodyAnchors
      });

      animationFrameId = requestAnimationFrame(updateFrame);
    };

    animationFrameId = requestAnimationFrame(updateFrame);

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [streamUrl]);

  return currentFrame;
}
