/**
 * useCamera — manages webcam access and frame capture for MIRAI.
 *
 * Usage:
 *   const { videoRef, isReady, error, startCamera, stopCamera, captureFrame } = useCamera();
 *
 * captureFrame() returns a base-64 JPEG string (no data-URI prefix)
 * suitable for sending directly to POST /api/v1/try-on as person_image_b64.
 *
 * Frame capture only happens when explicitly called — we do NOT stream every
 * frame to the backend. The webcam video runs locally in a <video> element.
 */

import { useCallback, useRef, useState } from 'react';

export type CameraError =
  | 'permission_denied'
  | 'not_found'
  | 'overconstrained'
  | 'unknown';

export interface UseCameraReturn {
  videoRef: React.RefObject<HTMLVideoElement>;
  canvasRef: React.RefObject<HTMLCanvasElement>;
  isReady: boolean;
  error: CameraError | null;
  startCamera: () => Promise<void>;
  stopCamera: () => void;
  captureFrame: () => string | null;
}

export function useCamera(): UseCameraReturn {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<CameraError | null>(null);

  const startCamera = useCallback(async () => {
    setError(null);
    setIsReady(false);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user',
        },
        audio: false,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        // Wait for video metadata to load before marking ready
        await new Promise<void>((resolve) => {
          const v = videoRef.current!;
          const handler = () => { resolve(); v.removeEventListener('loadedmetadata', handler); };
          v.addEventListener('loadedmetadata', handler);
        });
        await videoRef.current.play();
        setIsReady(true);
      }
    } catch (err: unknown) {
      const domErr = err as { name?: string };
      if (domErr.name === 'NotAllowedError' || domErr.name === 'PermissionDeniedError') {
        setError('permission_denied');
      } else if (domErr.name === 'NotFoundError' || domErr.name === 'DevicesNotFoundError') {
        setError('not_found');
      } else if (domErr.name === 'OverconstrainedError') {
        setError('overconstrained');
      } else {
        setError('unknown');
      }
    }
  }, []);

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setIsReady(false);
  }, []);

  /**
   * Capture a single frame from the live video feed.
   * Returns a base-64 JPEG string (WITHOUT the data-URI prefix).
   * Returns null if camera is not ready.
   */
  const captureFrame = useCallback((): string | null => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || !isReady) return null;

    const w = video.videoWidth || 640;
    const h = video.videoHeight || 480;
    canvas.width = w;
    canvas.height = h;

    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    // Mirror the frame horizontally (selfie/mirror convention)
    ctx.save();
    ctx.scale(-1, 1);
    ctx.drawImage(video, -w, 0, w, h);
    ctx.restore();

    // dataURL → strip the prefix, return raw base-64
    const dataUrl = canvas.toDataURL('image/jpeg', 0.90);
    return dataUrl.split(',')[1] ?? null;
  }, [isReady]);

  return { videoRef, canvasRef, isReady, error, startCamera, stopCamera, captureFrame };
}
