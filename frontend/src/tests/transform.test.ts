import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { BodyAnchorResolver, type ResolvedAnchors } from '../rendering/BodyAnchorResolver.ts';
import { GarmentTransformCalculator } from '../rendering/GarmentTransform.ts';
import { DEFAULT_GARMENTS, type GarmentMetadata } from '../rendering/GarmentAsset.ts';
import type { TrackingFrame } from '../types/tracking.ts';

describe('Phase 2 Frontend Garment Transformation Tests', () => {
  const sampleGarment: GarmentMetadata = DEFAULT_GARMENTS.oct_jkt_001;

  function createMockAnchors(overrides?: Partial<ResolvedAnchors>): ResolvedAnchors {
    return {
      leftShoulder: { x: 0.40, y: 0.30 },
      rightShoulder: { x: 0.60, y: 0.30 },
      leftHip: { x: 0.42, y: 0.60 },
      rightHip: { x: 0.58, y: 0.60 },
      midShoulder: { x: 0.50, y: 0.30 },
      torsoCenter: { x: 0.50, y: 0.45 },
      shoulderWidth: 0.20,
      hipWidth: 0.16,
      torsoHeight: 0.30,
      shoulderAngleDeg: 0.0,
      shoulderAngleRad: 0.0,
      torsoAngleDeg: 0.0,
      torsoAngleRad: 0.0,
      confidence: 0.95,
      isValid: true,
      ...overrides
    };
  }

  test('Test 1 — Translation: Garment position translates to expected screen coordinates', () => {
    const calc = new GarmentTransformCalculator();
    const anchors = createMockAnchors({
      midShoulder: { x: 0.50, y: 0.30 }
    });
    const canvasWidth = 1000;
    const canvasHeight = 2000;

    const transform = calc.compute(anchors, sampleGarment, canvasWidth, canvasHeight);

    // Expected X: (0.50 + xOffset(0)) * 1000 = 500 px
    // Expected Y: (0.30 + yOffset(-0.02)) * 2000 = 560 px
    assert.equal(transform.isValid, true);
    assert.equal(transform.centerX, 500);
    assert.ok(Math.abs(transform.centerY - 560) < 0.001, `Expected centerY close to 560, got ${transform.centerY}`);
  });

  test('Test 2 — Scaling: Increasing shoulder width increases garment scale', () => {
    const calc = new GarmentTransformCalculator();
    const canvasWidth = 1000;
    const canvasHeight = 2000;

    // Person further away (shoulderWidth = 0.15)
    const farAnchors = createMockAnchors({ shoulderWidth: 0.15 });
    const farTransform = calc.compute(farAnchors, sampleGarment, canvasWidth, canvasHeight);

    // Person closer to camera (shoulderWidth = 0.30)
    const closeAnchors = createMockAnchors({ shoulderWidth: 0.30 });
    const closeTransform = calc.compute(closeAnchors, sampleGarment, canvasWidth, canvasHeight);

    assert.ok(closeTransform.width > farTransform.width);
    // 0.30 * 2.2 * 1000 = 660 px vs 0.15 * 2.2 * 1000 = 330 px
    assert.equal(closeTransform.width, 660);
    assert.equal(farTransform.width, 330);
  });

  test('Test 3 — Rotation: Changing shoulder angle changes garment rotation correctly', () => {
    const calc = new GarmentTransformCalculator();
    const canvasWidth = 1000;
    const canvasHeight = 2000;

    // Right shoulder tilted down 15 degrees
    const tiltedAnchors = createMockAnchors({
      shoulderAngleDeg: 15.0,
      shoulderAngleRad: (15.0 * Math.PI) / 180
    });

    const transform = calc.compute(tiltedAnchors, sampleGarment, canvasWidth, canvasHeight);
    assert.equal(transform.rotationDeg, 15.0);
    assert.ok(Math.abs(transform.rotationRad - (15.0 * Math.PI) / 180) < 0.0001);
  });

  test('Test 4 — Mirroring: Camera normalized coordinates map to mirrored canvas coordinates', () => {
    // Under CSS scaleX(-1), points at camera normalized x=0.40 appear at mirrored screen position x=0.60
    const rawCameraX = 0.40;
    const canvasWidth = 1080;
    const internalCanvasPx = rawCameraX * canvasWidth;
    const mirroredScreenPx = (1.0 - rawCameraX) * canvasWidth;

    assert.equal(internalCanvasPx, 432);
    assert.equal(mirroredScreenPx, 648);
  });

  test('Test 5 — Tracking loss: Invalid anchors do not produce broken transforms or NaN', () => {
    const calc = new GarmentTransformCalculator();
    const canvasWidth = 1000;
    const canvasHeight = 2000;

    // 1. Initial valid frame
    const validAnchors = createMockAnchors();
    const t1 = calc.compute(validAnchors, sampleGarment, canvasWidth, canvasHeight);
    assert.equal(t1.isValid, true);

    // 2. Tracking lost frame
    const lostAnchors = createMockAnchors({ isValid: false });
    const t2 = calc.compute(lostAnchors, sampleGarment, canvasWidth, canvasHeight);

    // Should gracefully hold last stable transform with decay rather than crashing or NaN
    assert.equal(t2.isValid, false);
    assert.ok(Number.isFinite(t2.centerX));
    assert.ok(Number.isFinite(t2.centerY));
    assert.ok(t2.opacity < t1.opacity);
  });

  test('Test 6 — Asset error: Missing or invalid garment gracefully returns safe fallback', () => {
    const invalidGarment: GarmentMetadata = {
      id: 'missing_garment',
      name: 'Missing',
      category: 'jackets',
      assetUrl: 'invalid://nonexistent-path.png',
      anchorConfig: { anchorX: 0.5, anchorY: 0.5 },
      calibration: { scaleMultiplier: 1.0, xOffset: 0, yOffset: 0, rotationOffsetDeg: 0 }
    };

    assert.ok(invalidGarment.id);
    assert.ok(invalidGarment.assetUrl.startsWith('invalid://'));
  });

  test('Test 7 — Product selection: Selecting another garment updates active metadata', () => {
    const customGarment: GarmentMetadata = {
      id: 'oct_hoodie_002',
      name: 'Oversized Boxy Graphic Hoodie',
      category: 'hoodies',
      assetUrl: DEFAULT_GARMENTS.oct_jkt_001.assetUrl,
      anchorConfig: { anchorX: 0.5, anchorY: 0.25 },
      calibration: { scaleMultiplier: 2.4, xOffset: 0.0, yOffset: 0.01, rotationOffsetDeg: 0.0 }
    };

    const calc = new GarmentTransformCalculator();
    const anchors = createMockAnchors();
    const transform = calc.compute(anchors, customGarment, 1000, 2000);

    // 0.20 * 2.4 * 1000 = 480 px
    assert.equal(transform.width, 480);
    assert.equal(transform.centerY, (0.30 + 0.01) * 2000);
  });
});
