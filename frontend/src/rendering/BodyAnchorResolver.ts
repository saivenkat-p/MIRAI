/**
 * Body Anchor Resolver.
 * Adapts AI TrackingFrame and BodyAnchors into frontend garment rendering parameters.
 * Does NOT duplicate pose estimation; consumes public AI contract directly.
 */
import type { TrackingFrame, BodyAnchors, Point2D, Landmark } from '../types/tracking.ts';

export interface ResolvedAnchors {
  leftShoulder: Point2D;
  rightShoulder: Point2D;
  leftHip: Point2D;
  rightHip: Point2D;
  midShoulder: Point2D;
  torsoCenter: Point2D;
  shoulderWidth: number;
  hipWidth: number;
  torsoHeight: number;
  shoulderAngleDeg: number;
  shoulderAngleRad: number;
  torsoAngleDeg: number;
  torsoAngleRad: number;
  confidence: number;
  isValid: boolean;
}

export class BodyAnchorResolver {
  /**
   * Resolves garment alignment anchors from TrackingFrame.
   * Prioritizes AI-provided body_anchors; falls back to raw landmarks if necessary.
   */
  public static resolve(frame: TrackingFrame): ResolvedAnchors | null {
    if (!frame || frame.tracking_state === 'lost') {
      return null;
    }

    // 1. If AI contract provides precomputed body_anchors
    if (frame.body_anchors) {
      return this.fromBodyAnchors(frame.body_anchors);
    }

    // 2. Fallback: extract from raw landmarks if body_anchors was omitted
    if (frame.landmarks && frame.landmarks.length > 0) {
      return this.fromLandmarks(frame.landmarks, frame.confidence);
    }

    return null;
  }

  private static fromBodyAnchors(anchors: BodyAnchors): ResolvedAnchors | null {
    if (!anchors.left_shoulder || !anchors.right_shoulder || !anchors.left_hip || !anchors.right_hip) {
      if (!anchors.is_valid) return null;
    }

    const ls = anchors.left_shoulder || { x: 0.4, y: 0.3 };
    const rs = anchors.right_shoulder || { x: 0.6, y: 0.3 };
    const lh = anchors.left_hip || { x: 0.42, y: 0.6 };
    const rh = anchors.right_hip || { x: 0.58, y: 0.6 };

    const midShoulder: Point2D = {
      x: (ls.x + rs.x) * 0.5,
      y: (ls.y + rs.y) * 0.5
    };

    return {
      leftShoulder: ls,
      rightShoulder: rs,
      leftHip: lh,
      rightHip: rh,
      midShoulder,
      torsoCenter: anchors.torso_center,
      shoulderWidth: anchors.shoulder_width,
      hipWidth: anchors.hip_width,
      torsoHeight: anchors.torso_height,
      shoulderAngleDeg: anchors.shoulder_angle_deg,
      shoulderAngleRad: anchors.shoulder_angle_rad,
      torsoAngleDeg: anchors.torso_angle_deg,
      torsoAngleRad: anchors.torso_angle_rad,
      confidence: anchors.confidence,
      isValid: anchors.is_valid
    };
  }

  private static fromLandmarks(landmarks: Landmark[], frameConfidence: number): ResolvedAnchors | null {
    const lmMap = new Map<number, Landmark>();
    landmarks.forEach((lm) => lmMap.set(lm.id, lm));

    const ls = lmMap.get(11);
    const rs = lmMap.get(12);
    const lh = lmMap.get(23);
    const rh = lmMap.get(24);

    if (!ls || !rs || !lh || !rh) {
      return null;
    }

    const minVis = Math.min(ls.visibility, rs.visibility, lh.visibility, rh.visibility);
    const isValid = minVis >= 0.35;

    const leftShoulder: Point2D = { x: ls.x, y: ls.y };
    const rightShoulder: Point2D = { x: rs.x, y: rs.y };
    const leftHip: Point2D = { x: lh.x, y: lh.y };
    const rightHip: Point2D = { x: rh.x, y: rh.y };

    const dxS = rightShoulder.x - leftShoulder.x;
    const dyS = rightShoulder.y - leftShoulder.y;
    const shoulderWidth = Math.hypot(dxS, dyS);
    const shoulderAngleRad = Math.atan2(dyS, dxS);
    const shoulderAngleDeg = (shoulderAngleRad * 180) / Math.PI;

    const dxH = rightHip.x - leftHip.x;
    const dyH = rightHip.y - leftHip.y;
    const hipWidth = Math.hypot(dxH, dyH);

    const midShoulder: Point2D = {
      x: (leftShoulder.x + rightShoulder.x) * 0.5,
      y: (leftShoulder.y + rightShoulder.y) * 0.5
    };
    const midHip: Point2D = {
      x: (leftHip.x + rightHip.x) * 0.5,
      y: (leftHip.y + rightHip.y) * 0.5
    };
    const torsoCenter: Point2D = {
      x: (midShoulder.x + midHip.x) * 0.5,
      y: (midShoulder.y + midHip.y) * 0.5
    };

    const dxT = midHip.x - midShoulder.x;
    const dyT = midHip.y - midShoulder.y;
    const torsoHeight = Math.hypot(dxT, dyT);
    const torsoAngleRad = Math.atan2(dxT, dyT);
    const torsoAngleDeg = (torsoAngleRad * 180) / Math.PI;

    return {
      leftShoulder,
      rightShoulder,
      leftHip,
      rightHip,
      midShoulder,
      torsoCenter,
      shoulderWidth,
      hipWidth,
      torsoHeight,
      shoulderAngleDeg,
      shoulderAngleRad,
      torsoAngleDeg,
      torsoAngleRad,
      confidence: frameConfidence,
      isValid
    };
  }
}
