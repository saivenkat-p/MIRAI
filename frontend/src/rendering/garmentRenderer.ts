/**
 * Garment Renderer interface for AR overlay.
 * Phase 0 Foundation Scaffolding.
 */
import { TrackingFrame } from '../types/tracking';
import { Product } from '../types/api';

export interface GarmentRenderAnchor {
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
}

export interface IGarmentRenderer {
  initialize(canvas: HTMLCanvasElement): void;
  renderFrame(
    tracking: TrackingFrame,
    selectedGarment?: Product,
    videoElement?: HTMLVideoElement,
    maskCanvas?: HTMLCanvasElement | OffscreenCanvas
  ): void;
  clear(): void;
  dispose(): void;
}
