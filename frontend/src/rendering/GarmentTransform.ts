/**
 * Garment Transform Calculator.
 * Calculates 2D affine transformation (translation, scaling, rotation, and opacity)
 * for positioning virtual garments over the customer's reflection.
 */
import type { ResolvedAnchors } from './BodyAnchorResolver.ts';
import type { GarmentMetadata } from './GarmentAsset.ts';

export interface ComputedTransform {
  // Screen/Canvas coordinates in pixels
  centerX: number;
  centerY: number;
  width: number;
  height: number;
  rotationRad: number;
  rotationDeg: number;
  opacity: number;
  isValid: boolean;
}

export class GarmentTransformCalculator {
  private lastStableTransform: ComputedTransform | null = null;
  private holdFramesCount = 0;
  private static readonly MAX_HOLD_FRAMES = 8;

  /**
   * Computes garment transform from resolved body anchors and garment metadata.
   */
  public compute(
    anchors: ResolvedAnchors | null,
    garment: GarmentMetadata,
    canvasWidth: number,
    canvasHeight: number
  ): ComputedTransform {
    // 1. Handle tracking loss / null anchors
    if (!anchors || !anchors.isValid || anchors.shoulderWidth <= 0.01) {
      return this.handleTrackingLoss();
    }

    // 2. Base Translation: Anchor on mid-shoulder with vertical collar offset
    const calib = garment.calibration;
    const normX = anchors.midShoulder.x + calib.xOffset;
    const normY = anchors.midShoulder.y + calib.yOffset;

    // Map to canvas pixel space
    const centerX = normX * canvasWidth;
    const centerY = normY * canvasHeight;

    // 3. Scaling: Garment width proportional to shoulder width
    const targetWidth = anchors.shoulderWidth * calib.scaleMultiplier * canvasWidth;
    // Maintain 1:1 aspect ratio of garment bounding box
    const targetHeight = targetWidth;

    // 4. Rotation: Follows shoulder tilt angle
    const totalRotationDeg = anchors.shoulderAngleDeg + calib.rotationOffsetDeg;
    const totalRotationRad = (totalRotationDeg * Math.PI) / 180;

    // 5. Confidence-weighted opacity
    const opacity = Math.max(0.2, Math.min(1.0, anchors.confidence));

    // Guard against NaN or non-finite values
    if (!Number.isFinite(centerX) || !Number.isFinite(centerY) || !Number.isFinite(targetWidth)) {
      return this.handleTrackingLoss();
    }

    const transform: ComputedTransform = {
      centerX,
      centerY,
      width: Math.max(20, targetWidth),
      height: Math.max(20, targetHeight),
      rotationRad: totalRotationRad,
      rotationDeg: totalRotationDeg,
      opacity,
      isValid: true
    };

    // Cache stable transform
    this.lastStableTransform = transform;
    this.holdFramesCount = 0;

    return transform;
  }

  private handleTrackingLoss(): ComputedTransform {
    this.holdFramesCount++;

    // Hold last transform with smooth opacity decay during brief dropout
    if (this.lastStableTransform && this.holdFramesCount <= GarmentTransformCalculator.MAX_HOLD_FRAMES) {
      const decay = 1.0 - this.holdFramesCount / (GarmentTransformCalculator.MAX_HOLD_FRAMES + 1);
      return {
        ...this.lastStableTransform,
        opacity: Math.max(0, this.lastStableTransform.opacity * decay),
        isValid: false
      };
    }

    // Complete tracking loss
    this.lastStableTransform = null;
    return {
      centerX: 0,
      centerY: 0,
      width: 0,
      height: 0,
      rotationRad: 0,
      rotationDeg: 0,
      opacity: 0,
      isValid: false
    };
  }

  public reset(): void {
    this.lastStableTransform = null;
    this.holdFramesCount = 0;
  }
}
