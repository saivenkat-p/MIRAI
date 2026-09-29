/**
 * AI -> Frontend TrackingFrame contract.
 * Strictly mirrors /docs/INTEGRATION_CONTRACTS.md and ai/tracking/models.py
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

export interface TrackingFrame {
  timestamp: number;
  frame_id: number;
  frame_width: number;
  frame_height: number;
  fps: number;
  confidence: number;
  tracking_state: TrackingState;
  landmarks: Landmark[];
}
