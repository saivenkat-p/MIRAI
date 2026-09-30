/**
 * MirrorView — the main MIRAI Intelligent Mirror experience.
 *
 * Architecture:
 *   Hardware Camera Feed (HTMLVideoElement, scaleX(-1))
 *         │
 *         ├───► Decart Lucy V-TON Realtime Session (@decartai/sdk WebRTC)
 *         │            │
 *         │            ▼
 *         │     Transformed Neural Video Stream (MediaStream)
 *         │            │
 *         │            ▼
 *         │     Primary Viewport Video Element (Live Neural Try-On)
 *         │
 *         └───► MediaPipe Pose Landmarker (Telemetry & Skeleton HUD overlay only)
 *
 * NOTE: The old 2D canvas polygon/mesh garment renderer is PERMANENTLY DISABLED.
 * Garments are synthesized in real-time by the neural video model.
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useCamera } from '../hooks/useCamera';
import { useProducts } from '../hooks/useProducts';
import { useLiveAR } from '../hooks/useLiveAR';
import { useTryOn } from '../hooks/useTryOn';
import { useDecartVTO } from '../hooks/useDecartVTO';
import { ProductCatalog } from './ProductCatalog';
import { TryOnOverlay } from './TryOnOverlay';
import { DecartVTOProofModal } from './DecartVTOProofModal';
import { isLiveVTOAvailable } from '../services/GarmentRegistry';
import type { Product } from '../types/api';
import { Activity, Eye, EyeOff, Zap } from 'lucide-react';

export const MirrorView: React.FC = () => {
  // ── Hardware Camera ────────────────────────────────────────────────────────
  const {
    videoRef,
    canvasRef,
    isReady: cameraReady,
    error: cameraError,
    startCamera,
    captureFrame,
  } = useCamera();

  // ── Decart Lucy V-TON Realtime Provider ─────────────────────────────────────
  const {
    remoteStream,
    connectionState: vtoState,
    isStreaming: isVTOStreaming,
    error: vtoError,
    startSession: startVTOSession,
    stopSession: stopVTOSession,
    changeGarment: changeVTOGarment,
  } = useDecartVTO();

  const vtoVideoRef = useRef<HTMLVideoElement>(null);
  const [isBenchmarkOpen, setIsBenchmarkOpen] = useState<boolean>(false);
  const [vtoNotice, setVTONotice] = useState<string | null>(null);

  // Bind remote transformed stream to VTO video element
  useEffect(() => {
    if (vtoVideoRef.current && remoteStream) {
      vtoVideoRef.current.srcObject = remoteStream;
      vtoVideoRef.current.play().catch((e) => console.warn('[MIRAI] VTO video play error:', e));
    }
  }, [remoteStream]);

  // ── Product Catalog ────────────────────────────────────────────────────────
  const {
    categories,
    products,
    activeCategoryId,
    loading: catalogLoading,
    selectCategory,
  } = useProducts();

  // ── Live Pose Telemetry & Skeleton HUD ──────────────────────────────────────
  const arCanvasRef = useRef<HTMLCanvasElement>(null);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isARActive, setIsARActive] = useState<boolean>(false);
  const [showSkeleton, setShowSkeleton] = useState<boolean>(false);

  // Pose detection for skeleton and telemetry HUD (garment rendering disabled)
  const { fps: realFPS } = useLiveAR(videoRef, arCanvasRef, null, false, showSkeleton);

  // ── Optional Feature B: AI Photo Snapshot Modal ────────────────────────────
  const {
    state: photoState,
    resultImage: photoResultImage,
    resultMode: photoResultMode,
    processingMs: photoProcessingMs,
    error: photoError,
    triggerTryOn: triggerPhotoTryOn,
    reset: resetPhotoTryOn,
  } = useTryOn();

  const [capturedB64, setCapturedB64] = useState<string | null>(null);

  // Start hardware camera on mount
  useEffect(() => {
    startCamera();
  }, [startCamera]);

  // ── Product Selection & Live VTO Handlers ──────────────────────────────────
  const handleSelectProduct = useCallback(
    async (product: Product) => {
      setSelectedProduct(product);
      setVTONotice(null);

      // Check if product has a verified Live VTO reference
      const isReady = isLiveVTOAvailable(product.id);
      if (isReady) {
        setIsARActive(true);
        const cameraStream = videoRef.current?.srcObject as MediaStream | null;
        if (cameraStream) {
          if (isVTOStreaming) {
            await changeVTOGarment(product);
          } else {
            await startVTOSession(cameraStream, product);
          }
        }
      } else {
        setIsARActive(false);
        stopVTOSession();
        setVTONotice(
          `Live VTO reference for "${product.name}" is pending. Use AI Photo Try-On.`
        );
      }
    },
    [videoRef, isVTOStreaming, changeVTOGarment, startVTOSession, stopVTOSession]
  );

  const handleToggleAR = useCallback(async () => {
    if (!selectedProduct) return;

    if (isARActive) {
      setIsARActive(false);
      stopVTOSession();
    } else {
      if (isLiveVTOAvailable(selectedProduct.id)) {
        setIsARActive(true);
        const cameraStream = videoRef.current?.srcObject as MediaStream | null;
        if (cameraStream) {
          await startVTOSession(cameraStream, selectedProduct);
        }
      } else {
        setVTONotice(
          `Live VTO reference for "${selectedProduct.name}" is pending. Use AI Photo Try-On.`
        );
      }
    }
  }, [selectedProduct, isARActive, stopVTOSession, startVTOSession, videoRef]);

  const handleClearSelection = useCallback(() => {
    setSelectedProduct(null);
    setIsARActive(false);
    stopVTOSession();
    setVTONotice(null);
  }, [stopVTOSession]);

  // ── AI Photo Try-On Handlers ───────────────────────────────────────────────
  const handlePhotoTryOn = useCallback(async () => {
    if (!selectedProduct) return;
    setCapturedB64(null);

    await triggerPhotoTryOn(selectedProduct, () => {
      const frame = captureFrame();
      setCapturedB64(frame);
      return frame;
    });
  }, [selectedProduct, triggerPhotoTryOn, captureFrame]);

  const handleTryAnotherPhoto = useCallback(() => {
    resetPhotoTryOn();
    setCapturedB64(null);
  }, [resetPhotoTryOn]);

  const handleRetryPhoto = useCallback(() => {
    if (selectedProduct) {
      handlePhotoTryOn();
    }
  }, [selectedProduct, handlePhotoTryOn]);

  const isPhotoOverlayOpen = photoState !== 'idle';
  const localCameraStream = (videoRef.current?.srcObject as MediaStream | null) ?? null;

  return (
    <div className="relative w-full h-full bg-neutral-950 overflow-hidden select-none">
      {/* ── Layer 1: Mirror Viewport (Live Neural VTO or Hardware Camera) ── */}
      <div className="absolute inset-0">
        {/* Hidden scratch canvas for photo snapshots */}
        <canvas ref={canvasRef} className="hidden" />

        {cameraError ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-8">
            <div className="text-5xl mb-4">📷</div>
            <p className="text-white font-semibold text-lg">Camera Access Required</p>
            <p className="text-neutral-400 text-sm mt-2 max-w-sm">
              {cameraError === 'permission_denied'
                ? 'Please allow camera access in your browser settings to use the smart mirror.'
                : cameraError === 'not_found'
                ? 'No camera found. Please connect a webcam.'
                : 'Could not start camera stream.'}
            </p>
            <button
              onClick={startCamera}
              className="mt-6 px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm font-semibold transition-all shadow-lg shadow-violet-900/40"
            >
              Retry Camera
            </button>
          </div>
        ) : isVTOStreaming && remoteStream ? (
          /* Live Neural Transformed Video Stream (Decart Lucy V-TON) */
          <video
            ref={vtoVideoRef}
            autoPlay
            playsInline
            className="w-full h-full object-cover"
            style={{ transform: 'scaleX(-1)' }}
          />
        ) : (
          /* Default Hardware Camera Feed */
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
            style={{ transform: 'scaleX(-1)' }}
          />
        )}
      </div>

      {/* ── Layer 2: Optional Diagnostic Skeleton Overlay ── */}
      <canvas
        ref={arCanvasRef}
        className="absolute inset-0 w-full h-full pointer-events-none z-10"
      />

      {/* ── Layer 3: HUD Header Bar ── */}
      {!isPhotoOverlayOpen && (
        <header className="absolute top-0 left-0 right-0 z-20 flex justify-between items-center mx-4 mt-4 px-5 py-3 bg-black/75 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-black tracking-widest text-white">MIRAI</h1>
              <span className="px-2 py-0.5 rounded-full bg-violet-500/20 border border-violet-500/40 text-violet-300 text-[10px] font-bold">
                SMART TRIAL ROOM
              </span>
            </div>
            <p className="text-[11px] text-neutral-400 tracking-wider">OCTACEPT • Intelligent Mirror</p>
          </div>

          {/* Telemetry & Provider Badges */}
          <div className="flex items-center gap-2.5">
            {/* Realtime Neural Model Status */}
            {isVTOStreaming ? (
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-xs font-semibold shadow-sm shadow-emerald-900/30">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="font-mono">LUCY V-TON 3.5: STREAMING</span>
              </div>
            ) : vtoState === 'connecting' ? (
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-950/80 border border-amber-500/30 text-amber-300 text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
                <span className="font-mono">CONNECTING VTO...</span>
              </div>
            ) : (
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-neutral-900/80 border border-white/10 text-neutral-400 text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-neutral-600" />
                <span className="font-mono">NEURAL VTO: STANDBY</span>
              </div>
            )}

            {/* Benchmark Suite Launcher Button */}
            <button
              onClick={() => setIsBenchmarkOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-violet-600/30 hover:bg-violet-600/50 text-violet-200 border border-violet-500/40 transition-all shadow-md active:scale-95"
            >
              <Zap size={13} className="text-violet-300" />
              <span>Lucy V-TON Benchmark</span>
            </button>

            {/* Real FPS */}
            <div className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-neutral-300 text-xs font-mono">
              <Activity size={12} className="text-violet-400" />
              <span>{realFPS > 0 ? `${realFPS} FPS` : '-- FPS'}</span>
            </div>

            {/* Skeleton Overlay Toggle */}
            <button
              onClick={() => setShowSkeleton((v) => !v)}
              title={showSkeleton ? 'Hide body skeleton lines' : 'Show body skeleton lines'}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                showSkeleton
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                  : 'bg-white/5 text-neutral-400 border border-white/10 hover:text-white'
              }`}
            >
              {showSkeleton ? <Eye size={13} /> : <EyeOff size={13} />}
              <span>Skeleton</span>
            </button>

            {/* Hardware Camera Indicator */}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-neutral-300 text-xs font-mono">
              <span className={`w-2 h-2 rounded-full ${cameraReady ? 'bg-emerald-400' : 'bg-neutral-600'}`} />
              <span>{cameraReady ? 'CAM' : 'OFF'}</span>
            </div>
          </div>
        </header>
      )}

      {/* ── Notice Banner (e.g. Garment in preparation or VTO error) ── */}
      {(vtoNotice || vtoError) && !isPhotoOverlayOpen && (
        <div className="absolute top-20 left-4 z-20 max-w-md p-3.5 rounded-2xl bg-amber-950/90 backdrop-blur-xl border border-amber-500/40 text-amber-200 text-xs shadow-2xl flex items-center justify-between gap-3">
          <span className="leading-snug">{vtoError ? `Lucy V-TON: ${vtoError}` : vtoNotice}</span>
          <button
            onClick={() => setVTONotice(null)}
            className="text-amber-400 hover:text-white font-bold text-xs"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* ── Layer 4: Interactive Product Catalog (Right Side Wardrobe Panel) ── */}
      {!isPhotoOverlayOpen && (
        <ProductCatalog
          categories={categories}
          products={products}
          activeCategoryId={activeCategoryId}
          selectedProduct={selectedProduct}
          loading={catalogLoading}
          isARActive={isARActive}
          onSelectCategory={selectCategory}
          onSelectProduct={handleSelectProduct}
          onToggleAR={handleToggleAR}
          onPhotoTryOn={handlePhotoTryOn}
          onClearSelection={handleClearSelection}
        />
      )}

      {/* ── Layer 5: Optional Feature B (AI Photo Snapshot Modal) ── */}
      <TryOnOverlay
        state={photoState}
        resultImage={photoResultImage}
        resultMode={photoResultMode}
        processingMs={photoProcessingMs}
        error={photoError}
        product={selectedProduct}
        capturedPersonB64={capturedB64}
        onTryAnother={handleTryAnotherPhoto}
        onRetry={handleRetryPhoto}
        onSaveLook={() => alert('Look saved to your fitting session!')}
      />

      {/* ── Layer 6: Phase 1 Decart Lucy V-TON Proof of Concept & Benchmark Modal ── */}
      <DecartVTOProofModal
        isOpen={isBenchmarkOpen}
        onClose={() => setIsBenchmarkOpen(false)}
        localStream={localCameraStream}
      />
    </div>
  );
};
