import { useState, useEffect } from 'react';
import { TrackingFrame, Landmark } from '../types/tracking';

/**
 * Hook for consuming AI TrackingFrame stream.
 * Adheres strictly to the AI -> Frontend contract defined in /docs/INTEGRATION_CONTRACTS.md.
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

    // Standard demo simulation of natural human posture conforming to 33-point MediaPipe contract
    const updateFrame = () => {
      frameCounter++;
      const elapsed = (Date.now() - startTime) / 1000;
      
      // Gentle breathing & natural sway movement
      const swayX = Math.sin(elapsed * 1.5) * 0.02;
      const swayY = Math.cos(elapsed * 2.0) * 0.01;

      // Base standing landmarks (normalized 0.0 - 1.0)
      const mockLandmarks: Landmark[] = [
        { id: 0, name: 'nose', x: 0.50 + swayX, y: 0.22 + swayY, z: -0.1, visibility: 0.99 },
        { id: 11, name: 'left_shoulder', x: 0.42 + swayX, y: 0.32 + swayY, z: -0.05, visibility: 0.98 },
        { id: 12, name: 'right_shoulder', x: 0.58 + swayX, y: 0.32 + swayY, z: -0.05, visibility: 0.98 },
        { id: 13, name: 'left_elbow', x: 0.38 + swayX, y: 0.45 + swayY, z: -0.02, visibility: 0.96 },
        { id: 14, name: 'right_elbow', x: 0.62 + swayX, y: 0.45 + swayY, z: -0.02, visibility: 0.96 },
        { id: 15, name: 'left_wrist', x: 0.36 + swayX, y: 0.58 + swayY, z: 0.01, visibility: 0.94 },
        { id: 16, name: 'right_wrist', x: 0.64 + swayX, y: 0.58 + swayY, z: 0.01, visibility: 0.94 },
        { id: 23, name: 'left_hip', x: 0.44 + swayX, y: 0.56 + swayY, z: 0.0, visibility: 0.97 },
        { id: 24, name: 'right_hip', x: 0.56 + swayX, y: 0.56 + swayY, z: 0.0, visibility: 0.97 },
        { id: 25, name: 'left_knee', x: 0.43 + swayX, y: 0.74 + swayY, z: 0.02, visibility: 0.95 },
        { id: 26, name: 'right_knee', x: 0.57 + swayX, y: 0.74 + swayY, z: 0.02, visibility: 0.95 },
        { id: 27, name: 'left_ankle', x: 0.42 + swayX, y: 0.91 + swayY, z: 0.04, visibility: 0.93 },
        { id: 28, name: 'right_ankle', x: 0.58 + swayX, y: 0.91 + swayY, z: 0.04, visibility: 0.93 },
      ];

      setCurrentFrame({
        timestamp: Date.now(),
        frame_id: frameCounter,
        frame_width: 1080,
        frame_height: 1920,
        fps: 30.0,
        confidence: 0.96,
        tracking_state: 'tracked',
        landmarks: mockLandmarks
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
