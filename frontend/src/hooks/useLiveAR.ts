/**
 * MIRAI — useLiveAR
 *
 * The main Live AR orchestration hook.
 *
 * Responsibilities:
 *   • Initialize MediaPipe Pose Landmarker (WASM, runs in browser)
 *   • Run pose detection every frame via requestAnimationFrame
 *   • Drive GarmentRenderer2D to draw garment anchored to body
 *   • Optionally render real-time skeleton overlay
 *   • Sync canvas dimensions to video element each frame
 *   • Throttle React state updates (fps, trackingState) to ~8/s
 *     so the rAF loop does NOT cause 30 React re-renders/second
 *   • Apply EMA smoothing (inside GarmentRenderer2D)
 *   • Handle tracking loss / fade
 *
 * Returns reactive state for the UI (header badges, FPS counter).
 * Does NOT return raw landmarks — those flow imperatively to the renderer.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import type { RefObject } from 'react';
import type { Product } from '../types/api';
import type { TrackingFrame } from '../types/tracking';
import { GarmentRenderer2D } from '../rendering/GarmentRenderer2D';

// ── MediaPipe CDN URLs ────────────────────────────────────────────────────────
const WASM_URL =
  'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm';
const MODEL_URL =
  'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task';

// UI state update throttle — React re-renders max this often
const UI_UPDATE_INTERVAL_MS = 120;

// Tracking confidence thresholds
const PRESENCE_THRESHOLD  = 0.50;
const TRACKING_THRESHOLD  = 0.50;
const DETECTION_THRESHOLD = 0.50;

// ── Types ────────────────────────────────────────────────────────────────────

export type ARTrackingState = 'initializing' | 'ready' | 'searching' | 'tracked' | 'lost' | 'error';

export interface LiveARState {
  trackingState: ARTrackingState;
  fps: number;
  confidence: number;
  isLoading: boolean;
  loadError: string | null;
  /** true once PoseLandmarker is initialized and ready */
  isReady: boolean;
}

// ── Hook ─────────────────────────────────────────────────────────────────────

export function useLiveAR(
  videoRef: RefObject<HTMLVideoElement>,
  arCanvasRef: RefObject<HTMLCanvasElement>,
  selectedProduct: Product | null,
  isARActive: boolean,
  showSkeleton: boolean = true,
): LiveARState {
  const [state, setState] = useState<LiveARState>({
    trackingState: 'initializing',
    fps: 0,
    confidence: 0,
    isLoading: true,
    loadError: null,
    isReady: false,
  });

  // ── Imperative refs (never trigger re-renders) ───────────────────────
  const rendererRef = useRef<GarmentRenderer2D | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const landmarkerRef = useRef<any>(null);  // PoseLandmarker (dynamic import)
  const rafRef   = useRef<number>(0);
  const runningRef = useRef(false);

  // fps accounting
  const frameTimesRef = useRef<number[]>([]);
  const lastUIUpdateRef = useRef(0);
  const lastTrackedAtRef = useRef(0);

  // Track the last loaded product id to avoid reloading the same product
  const loadedProductIdRef = useRef<string | null>(null);

  // ── Initialize renderer once ─────────────────────────────────────────
  useEffect(() => {
    rendererRef.current = new GarmentRenderer2D();
    rendererRef.current.setShowSkeleton(showSkeleton);
    return () => {
      rendererRef.current?.dispose();
      rendererRef.current = null;
    };
  }, []);

  // ── Sync showSkeleton changes to renderer ────────────────────────────
  useEffect(() => {
    rendererRef.current?.setShowSkeleton(showSkeleton);
  }, [showSkeleton]);

  // ── Initialize renderer on canvas ────────────────────────────────────
  useEffect(() => {
    const canvas = arCanvasRef.current;
    if (!canvas || !rendererRef.current) return;
    rendererRef.current.initialize(canvas);
  }, [arCanvasRef]);

  // ── Initialize MediaPipe PoseLandmarker ───────────────────────────────
  useEffect(() => {
    let cancelled = false;

    async function initMediaPipe() {
      try {
        const { FilesetResolver, PoseLandmarker } =
          await import('@mediapipe/tasks-vision');

        const vision = await FilesetResolver.forVisionTasks(WASM_URL);
        if (cancelled) return;

        const landmarker = await PoseLandmarker.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath: MODEL_URL,
            delegate: 'GPU',
          },
          runningMode: 'VIDEO',
          numPoses: 1,
          minPoseDetectionConfidence:  DETECTION_THRESHOLD,
          minPosePresenceConfidence:   PRESENCE_THRESHOLD,
          minTrackingConfidence:       TRACKING_THRESHOLD,
          outputSegmentationMasks:     true,
        });

        if (cancelled) {
          landmarker.close();
          return;
        }

        landmarkerRef.current = landmarker;
        setState(s => ({
          ...s,
          isLoading: false,
          isReady: true,
          trackingState: 'searching',
        }));
      } catch (err) {
        if (cancelled) return;
        console.error('[MIRAI] MediaPipe init failed:', err);
        setState(s => ({
          ...s,
          isLoading: false,
          isReady: false,
          loadError: 'Pose tracking unavailable. Check internet connection.',
          trackingState: 'error',
        }));
      }
    }

    initMediaPipe();
    return () => { cancelled = true; };
  }, []);

  // ── Load garment when selected product changes ────────────────────────
  useEffect(() => {
    const renderer = rendererRef.current;
    if (!renderer) return;

    if (!selectedProduct || !isARActive) {
      renderer.unloadGarment?.();
      loadedProductIdRef.current = null;
      return;
    }

    if (selectedProduct.id === loadedProductIdRef.current) return;
    loadedProductIdRef.current = selectedProduct.id;
    renderer.loadProduct(selectedProduct).catch(err => {
      console.error('[MIRAI] Garment load failed:', err);
    });
  }, [selectedProduct, isARActive]);

  // ── Main rAF tracking + render loop ──────────────────────────────────
  const startLoop = useCallback(() => {
    if (runningRef.current) return;
    runningRef.current = true;

    function tick(timestamp: number) {
      if (!runningRef.current) return;

      const video  = videoRef.current;
      const canvas = arCanvasRef.current;
      const landmarker = landmarkerRef.current;
      const renderer   = rendererRef.current;

      // Always re-request the next frame first so loop keeps going even on error
      rafRef.current = requestAnimationFrame(tick);

      if (!video || !canvas || !landmarker || !renderer) return;
      if (video.readyState < 2) return; // HAVE_CURRENT_DATA

      // ── Sync canvas size to video element ──────────────────────────
      const rect = video.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0) {
        if (canvas.width  !== Math.round(rect.width) ||
            canvas.height !== Math.round(rect.height)) {
          canvas.width  = Math.round(rect.width);
          canvas.height = Math.round(rect.height);
        }
      }

      // ── Pose detection ─────────────────────────────────────────────
      let trackingFrame: TrackingFrame = {
        timestamp,
        frame_id: 0,
        frame_width:  video.videoWidth  || 1280,
        frame_height: video.videoHeight || 720,
        fps: 0,
        confidence: 0,
        tracking_state: 'searching',
        landmarks: [],
      };

      let maskCanvas: HTMLCanvasElement | OffscreenCanvas | undefined;
      try {
        const result = landmarker.detectForVideo(video, timestamp);

        if (result.segmentationMasks && result.segmentationMasks.length > 0) {
          maskCanvas = result.segmentationMasks[0].canvas;
        }

        if (result.landmarks && result.landmarks.length > 0) {
          const rawLandmarks = result.landmarks[0];
          // Convert MediaPipe NormalizedLandmark[] to our Landmark[] schema
          const landmarks = rawLandmarks.map(
            (lm: { x: number; y: number; z: number; visibility?: number }, i: number) => ({
              id: i,
              name: LANDMARK_NAMES[i] ?? `landmark_${i}`,
              x: lm.x,
              y: lm.y,
              z: lm.z,
              visibility: lm.visibility ?? 1.0,
            })
          );

          // Compute mean confidence of the primary garment anchor landmarks
          const anchorIds = [11, 12, 23, 24];
          const anchorVis = anchorIds
            .map(id => landmarks[id]?.visibility ?? 0)
            .filter(v => v > 0);
          const confidence = anchorVis.length
            ? anchorVis.reduce((a, b) => a + b, 0) / anchorVis.length
            : 0;

          trackingFrame = {
            ...trackingFrame,
            tracking_state: confidence > TRACKING_THRESHOLD ? 'tracked' : 'searching',
            confidence,
            landmarks,
          };
          lastTrackedAtRef.current = Date.now();
        } else {
          const elapsed = Date.now() - lastTrackedAtRef.current;
          trackingFrame.tracking_state = elapsed > 1500 ? 'lost' : 'searching';
        }

        // ── Render garment / skeleton ──────────────────────────────────
        if (isARActive) {
          renderer.renderFrame(trackingFrame, selectedProduct ?? undefined, video, maskCanvas);
        } else if (showSkeleton) {
          renderer.renderFrame(trackingFrame, undefined, video, maskCanvas);
        } else {
          renderer.clear();
        }

        // Close MPMasks to release WebGL resources
        if (result.segmentationMasks) {
          for (const m of result.segmentationMasks) {
            try { m.close(); } catch { /* ignore */ }
          }
        }
      } catch {
        // Detection errors are non-fatal — just skip this frame
      }

      // ── Throttled UI state update ──────────────────────────────────
      frameTimesRef.current.push(timestamp);
      // Keep only last 30 frames for FPS rolling average
      if (frameTimesRef.current.length > 30) frameTimesRef.current.shift();

      if (timestamp - lastUIUpdateRef.current >= UI_UPDATE_INTERVAL_MS) {
        lastUIUpdateRef.current = timestamp;

        const times = frameTimesRef.current;
        const fps = times.length > 1
          ? Math.round(1000 * (times.length - 1) /
              (times[times.length - 1] - times[0]))
          : 0;

        setState(s => ({
          ...s,
          trackingState: trackingFrame.tracking_state as ARTrackingState,
          fps,
          confidence: Math.round(trackingFrame.confidence * 100) / 100,
        }));
      }
    }

    rafRef.current = requestAnimationFrame(tick);
  }, [videoRef, arCanvasRef, isARActive, selectedProduct, showSkeleton]);

  const stopLoop = useCallback(() => {
    runningRef.current = false;
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = 0;
    }
    rendererRef.current?.clear();
  }, []);

  // ── Start/stop loop based on readiness ───────────────────────────────
  useEffect(() => {
    if (state.isReady) {
      startLoop();
    }
    return () => stopLoop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.isReady]);

  // ── Restart loop on dependency change ────────────────────────────────
  useEffect(() => {
    if (!state.isReady) return;
    stopLoop();
    startLoop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isARActive, selectedProduct?.id, showSkeleton]);

  return state;
}

// ── MediaPipe landmark name lookup ──────────────────────────────────────────
const LANDMARK_NAMES: Record<number, string> = {
  0: 'nose', 1: 'left_eye_inner', 2: 'left_eye', 3: 'left_eye_outer',
  4: 'right_eye_inner', 5: 'right_eye', 6: 'right_eye_outer',
  7: 'left_ear', 8: 'right_ear', 9: 'mouth_left', 10: 'mouth_right',
  11: 'left_shoulder', 12: 'right_shoulder',
  13: 'left_elbow', 14: 'right_elbow',
  15: 'left_wrist', 16: 'right_wrist',
  17: 'left_pinky', 18: 'right_pinky', 19: 'left_index', 20: 'right_index',
  21: 'left_thumb', 22: 'right_thumb',
  23: 'left_hip', 24: 'right_hip',
  25: 'left_knee', 26: 'right_knee',
  27: 'left_ankle', 28: 'right_ankle',
  29: 'left_heel', 30: 'right_heel',
  31: 'left_foot_index', 32: 'right_foot_index',
};
