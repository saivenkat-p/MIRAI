/**
 * AI -> Frontend TrackingFrame contract.
 * Strictly mirrors /docs/INTEGRATION_CONTRACTS.md and ai/tracking/models.py / ai/tracking/anchors.py.
 */

export type TrackingState = 'searching' | 'tracked' | 'lost' | 'calibrating';

export interface Landmark {
  id: number;
  name: string;
  x: number;          // Normalized 0.0 - 1.0 (left to right)
  y: number;          // Normalized 0.0 - 1.0 (top to bottom)
  z: number;          // Relative depth
  visibility: number; // 0.0 - 1.0 confidence/visibility
}

export interface Point2D {
  x: number;
  y: number;
}

export interface BoundingBox {
  min_x: number;
  min_y: number;
  max_x: number;
  max_y: number;
  width: number;
  height: number;
}

export interface BodyAnchors {
  left_shoulder: Point2D | null;
  right_shoulder: Point2D | null;
  left_hip: Point2D | null;
  right_hip: Point2D | null;
  left_elbow: Point2D | null;
  right_elbow: Point2D | null;
  left_wrist: Point2D | null;
  right_wrist: Point2D | null;
  shoulder_width: number;
  hip_width: number;
  torso_center: Point2D;
  torso_height: number;
  shoulder_angle_deg: number;
  shoulder_angle_rad: number;
  torso_angle_deg: number;
  torso_angle_rad: number;
  bounding_box: BoundingBox;
  confidence: number;
  is_valid: boolean;
}

export interface TrackingFrame {
  timestamp: number;
  frame_id: number;
  frame_width: number;
  frame_height: number;
  fps: number;
  confidence: number;
  tracking_state: TrackingState;
  landmarks: Landmark[];
  body_anchors?: BodyAnchors | null;
}
