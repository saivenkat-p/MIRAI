/**
 * MIRAI — MirrorView
 *
 * The Main MIRAI Intelligent Mirror Experience.
 *
 * Self-Hosted Virtual Try-On Pipeline:
 *   Hardware Camera Feed (HTMLVideoElement, scaleX(-1))
 *         │
 *         ├───► MediaPipe Pose Landmarker (WASM/GPU, runs locally in browser)
 *         │            │
 *         │            ▼
 *         │     Live Normalized Landmarks & Segmentation Mask
 *         │            │
 *         └───► Kinematic Volumetric Garment Engine (GarmentRenderer2D)
 *                      │
 *                      ▼
 *               Deformable 32-Triangle Fabric Mesh
 *               + 3D Cylindrical Ambient Shading
 *               + Dynamic Flexion Creasing
 *               + Throat & Forearm Occlusion
 *               (Canvas2D, Full 60 FPS Local Rendering)
 *
 * Retail Systems Integrated:
 *   • Multi-Garment Wardrobe Catalog
 *   • Real-Time Sizing & Store Inventory (Rack Locations)
 *   • Saved Looks with Real QR Code Mobile Handoff
 *   • In-Store Promotional Coupons & Loyalty Rewards
 *   • Anonymized Customer Telemetry & Session Management
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useCamera } from '../hooks/useCamera';
import { useProducts } from '../hooks/useProducts';
import { useLiveAR } from '../hooks/useLiveAR';
import { useTryOn } from '../hooks/useTryOn';
import { ProductCatalog } from './ProductCatalog';
import { ProductDetailCard } from './ProductDetailCard';
import { SaveLookModal } from './SaveLookModal';
import { CouponsModal } from './CouponsModal';
import { TryOnOverlay } from './TryOnOverlay';
import type { Product } from '../types/api';
import { Activity, Eye, EyeOff, Tag, LogOut } from 'lucide-react';

export const MirrorView: React.FC = () => {
  // ── Hardware Camera Feed ───────────────────────────────────────────────────
  const {
    videoRef,
    canvasRef,
    isReady: cameraReady,
    error: cameraError,
    startCamera,
    captureFrame,
  } = useCamera();

  // ── Session State & Telemetry ──────────────────────────────────────────────
  const [sessionId, setSessionId] = useState<string>(() => `sess_${Math.random().toString(36).substring(2, 9)}`);

  // Initialize session on mount
  useEffect(() => {
    fetch('http://localhost:8000/api/v1/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mirror_id: 'MIRAI-SMART-MIRROR-01',
        client_timestamp: Date.now(),
      }),
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.session_id) {
          setSessionId(data.session_id);
        }
      })
      .catch((err) => console.warn('[MIRAI] Backend session init notice:', err));
  }, []);

  // ── Product Catalog ────────────────────────────────────────────────────────
  const {
    categories,
    products,
    activeCategoryId,
    loading: catalogLoading,
    selectCategory,
  } = useProducts();

  // ── Live AR Virtual Try-On Engine ──────────────────────────────────────────
  const arCanvasRef = useRef<HTMLCanvasElement>(null);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [selectedSize, setSelectedSize] = useState<string>('M');
  const [isARActive, setIsARActive] = useState<boolean>(true);
  const [showSkeleton, setShowSkeleton] = useState<boolean>(false);

  // Drive self-hosted Kinematic Volumetric Garment Engine (60 FPS local canvas)
  const { fps: realFPS } = useLiveAR(
    videoRef,
    arCanvasRef,
    selectedProduct,
    isARActive,
    showSkeleton
  );

  // ── Modals & Dialogs ───────────────────────────────────────────────────────
  const [isSaveLookOpen, setIsSaveLookOpen] = useState<boolean>(false);
  const [isCouponsOpen, setIsCouponsOpen] = useState<boolean>(false);

  // ── AI Photo Snapshot Try-On (Secondary Feature) ───────────────────────────
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

  // Record telemetry on product selection
  const handleSelectProduct = useCallback(
    (product: Product) => {
      setSelectedProduct(product);
      setSelectedSize(product.sizes[0] || 'M');
      setIsARActive(true);

      // Record selection event with backend
      fetch('http://localhost:8000/api/v1/analytics/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          event_type: 'garment_selected',
          product_id: product.id,
          dwell_time_seconds: 0,
          timestamp: Date.now(),
        }),
      }).catch(() => {});
    },
    [sessionId]
  );

  const handleToggleAR = useCallback(() => {
    setIsARActive((v) => !v);
  }, []);

  const handleClearSelection = useCallback(() => {
    setSelectedProduct(null);
  }, []);

  const handleEndSession = useCallback(() => {
    fetch(`http://localhost:8000/api/v1/sessions/${sessionId}/end`, {
      method: 'POST',
    }).catch(() => {});

    setSelectedProduct(null);
    setIsARActive(true);
    setSessionId(`sess_${Math.random().toString(36).substring(2, 9)}`);
  }, [sessionId]);

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

  const isPhotoOverlayOpen = photoState !== 'idle';

  return (
    <div className="relative w-full h-full bg-neutral-950 overflow-hidden select-none">
      {/* ── Layer 1: Hardware Mirror Camera Viewport ── */}
      <div className="absolute inset-0">
        <canvas ref={canvasRef} className="hidden" />

        {cameraError ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-8">
            <div className="text-5xl mb-4">📷</div>
            <p className="text-white font-semibold text-lg">Camera Access Required</p>
            <p className="text-neutral-400 text-sm mt-2 max-w-sm">
              {cameraError === 'permission_denied'
                ? 'Please allow camera access in your browser settings to activate the mirror.'
                : cameraError === 'not_found'
                ? 'No camera found. Please connect an HD webcam.'
                : 'Could not start mirror camera stream.'}
            </p>
            <button
              onClick={startCamera}
              className="mt-6 px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm font-semibold transition-all shadow-lg shadow-violet-900/40"
            >
              Retry Camera
            </button>
          </div>
        ) : (
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

      {/* ── Layer 2: Self-Hosted Kinematic Volumetric Garment Canvas ── */}
      <canvas
        ref={arCanvasRef}
        className="absolute inset-0 w-full h-full pointer-events-none z-10"
      />

      {/* ── Layer 3: Enterprise Retail HUD Header Bar ── */}
      {!isPhotoOverlayOpen && (
        <header className="absolute top-0 left-0 right-0 z-20 flex justify-between items-center mx-4 mt-4 px-5 py-3 bg-black/80 backdrop-blur-2xl rounded-2xl border border-white/10 shadow-2xl">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-black tracking-widest text-white">MIRAI</h1>
              <span className="px-2 py-0.5 rounded-full bg-violet-500/20 border border-violet-500/40 text-violet-300 text-[10px] font-bold">
                5G SMART TRIAL ROOM
              </span>
            </div>
            <p className="text-[11px] text-neutral-400 tracking-wider">OCTACEPT • Intelligent Mirror</p>
          </div>

          {/* Engine & Retail Control Badges */}
          <div className="flex items-center gap-2.5">
            {/* Self-Hosted VTO Engine Status */}
            {selectedProduct && isARActive ? (
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-xs font-semibold shadow-sm shadow-emerald-900/30">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="font-mono">KVGE VTO: ACTIVE</span>
              </div>
            ) : (
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-neutral-900/80 border border-white/10 text-neutral-400 text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-neutral-500" />
                <span className="font-mono">KVGE: STANDBY</span>
              </div>
            )}

            {/* Real Measured FPS */}
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

            {/* In-Store Promotions & Coupons Button */}
            <button
              onClick={() => setIsCouponsOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 transition-all shadow-sm active:scale-95"
            >
              <Tag size={13} />
              <span>Coupons & Rewards</span>
            </button>

            {/* Hardware Camera Indicator */}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-neutral-300 text-xs font-mono">
              <span className={`w-2 h-2 rounded-full ${cameraReady ? 'bg-emerald-400' : 'bg-neutral-600'}`} />
              <span>{cameraReady ? 'CAM' : 'OFF'}</span>
            </div>

            {/* End Session Button */}
            <button
              onClick={handleEndSession}
              title="End session and reset mirror for next customer"
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-white/5 hover:bg-red-500/20 text-neutral-400 hover:text-red-300 border border-white/10 hover:border-red-500/30 transition-all active:scale-95"
            >
              <LogOut size={13} />
              <span>Reset</span>
            </button>
          </div>
        </header>
      )}

      {/* ── Layer 4: Contextual Product Details, Sizes & In-Store Inventory ── */}
      {!isPhotoOverlayOpen && selectedProduct && (
        <ProductDetailCard
          product={selectedProduct}
          selectedSize={selectedSize}
          onSelectSize={setSelectedSize}
          onSaveLook={() => setIsSaveLookOpen(true)}
          onOpenCoupons={() => setIsCouponsOpen(true)}
          onClear={handleClearSelection}
        />
      )}

      {/* ── Layer 5: Interactive Wardrobe & Garment Catalog (Right Drawer) ── */}
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

      {/* ── Layer 6: Save Look & Real QR Code Handoff Modal ── */}
      <SaveLookModal
        isOpen={isSaveLookOpen}
        onClose={() => setIsSaveLookOpen(false)}
        product={selectedProduct}
        selectedSize={selectedSize}
        sessionId={sessionId}
      />

      {/* ── Layer 7: In-Store Promotional Coupons & Rewards Modal ── */}
      <CouponsModal
        isOpen={isCouponsOpen}
        onClose={() => setIsCouponsOpen(false)}
      />

      {/* ── Layer 8: Secondary AI Photo Snapshot Try-On Overlay ── */}
      <TryOnOverlay
        state={photoState}
        resultImage={photoResultImage}
        resultMode={photoResultMode}
        processingMs={photoProcessingMs}
        error={photoError}
        product={selectedProduct}
        capturedPersonB64={capturedB64}
        onTryAnother={() => {
          resetPhotoTryOn();
          setCapturedB64(null);
        }}
        onRetry={handlePhotoTryOn}
        onSaveLook={() => setIsSaveLookOpen(true)}
      />
    </div>
  );
};
