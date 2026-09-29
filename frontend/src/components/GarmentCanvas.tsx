import React, { useRef, useEffect } from 'react';
import { TrackingFrame } from '../types/tracking';
import { GarmentMetadata } from '../rendering/GarmentAsset';
import { BodyAnchorResolver } from '../rendering/BodyAnchorResolver';
import { GarmentTransformCalculator } from '../rendering/GarmentTransform';
import { GarmentRenderer } from '../rendering/GarmentRenderer';

interface GarmentCanvasProps {
  trackingFrame: TrackingFrame;
  garment: GarmentMetadata | null;
  visible?: boolean;
}

export const GarmentCanvas: React.FC<GarmentCanvasProps> = ({ trackingFrame, garment, visible = true }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rendererRef = useRef<GarmentRenderer>(new GarmentRenderer());
  const calculatorRef = useRef<GarmentTransformCalculator>(new GarmentTransformCalculator());

  // Initialize canvas
  useEffect(() => {
    if (canvasRef.current) {
      rendererRef.current.initialize(canvasRef.current);
    }
  }, []);

  // Update active garment asset
  useEffect(() => {
    if (garment) {
      rendererRef.current.setGarment(garment);
    } else {
      rendererRef.current.clear();
      calculatorRef.current.reset();
    }
  }, [garment]);

  // Main rendering loop driven by incoming TrackingFrame
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !garment || !visible) {
      rendererRef.current.clear();
      return;
    }

    const width = canvas.clientWidth || 1080;
    const height = canvas.clientHeight || 1920;

    // 1. Resolve body anchors from AI TrackingFrame
    const resolvedAnchors = BodyAnchorResolver.resolve(trackingFrame);

    // 2. Compute 2D affine transform
    const transform = calculatorRef.current.compute(resolvedAnchors, garment, width, height);

    // 3. Render virtual garment
    rendererRef.current.render(transform, garment);
  }, [trackingFrame, garment, visible]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none z-10"
      style={{ transform: 'scaleX(-1)' }} // Mirror flip
    />
  );
};
