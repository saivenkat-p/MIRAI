import React, { useRef, useEffect } from 'react';
import { TrackingFrame, Landmark } from '../types/tracking';

interface SkeletonCanvasProps {
  trackingFrame: TrackingFrame;
  visible?: boolean;
}

// Canonical MediaPipe connections between landmark pairs
const POSE_CONNECTIONS: [number, number][] = [
  // Torso
  [11, 12], // shoulders
  [11, 23], // left shoulder to left hip
  [12, 24], // right shoulder to right hip
  [23, 24], // hips
  // Left arm
  [11, 13], [13, 15],
  // Right arm
  [12, 14], [14, 16],
  // Left leg
  [23, 25], [25, 27],
  // Right leg
  [24, 26], [26, 28]
];

export const SkeletonCanvas: React.FC<SkeletonCanvasProps> = ({ trackingFrame, visible = true }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Resize canvas internal buffer to container display size
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
    }

    ctx.clearRect(0, 0, width, height);

    if (!visible || trackingFrame.tracking_state !== 'tracked' || !trackingFrame.landmarks.length) {
      return;
    }

    // Map landmark IDs for fast lookup
    const lmMap = new Map<number, Landmark>();
    trackingFrame.landmarks.forEach((lm) => lmMap.set(lm.id, lm));

    // Draw skeletal connection bones
    ctx.lineWidth = 3;
    ctx.strokeStyle = '#06b6d4'; // cyan
    ctx.shadowColor = '#22d3ee';
    ctx.shadowBlur = 8;

    POSE_CONNECTIONS.forEach(([startId, endId]) => {
      const start = lmMap.get(startId);
      const end = lmMap.get(endId);
      if (start && end && start.visibility > 0.5 && end.visibility > 0.5) {
        ctx.beginPath();
        ctx.moveTo(start.x * width, start.y * height);
        ctx.lineTo(end.x * width, end.y * height);
        ctx.stroke();
      }
    });

    // Draw landmark joint nodes
    trackingFrame.landmarks.forEach((lm) => {
      if (lm.visibility > 0.5) {
        const px = lm.x * width;
        const py = lm.y * height;

        ctx.beginPath();
        ctx.arc(px, py, 5, 0, 2 * Math.PI);
        // Distinguish shoulders and hips with emerald highlight
        if ([11, 12, 23, 24].includes(lm.id)) {
          ctx.fillStyle = '#10b981'; // emerald-500
          ctx.shadowColor = '#34d399';
        } else {
          ctx.fillStyle = '#38bdf8'; // sky-400
          ctx.shadowColor = '#0284c7';
        }
        ctx.shadowBlur = 10;
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = '#ffffff';
        ctx.stroke();
      }
    });
  }, [trackingFrame, visible]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none z-10"
      style={{ transform: 'scaleX(-1)' }} // Mirror flip
    />
  );
};
