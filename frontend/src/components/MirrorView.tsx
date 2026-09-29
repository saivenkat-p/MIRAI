import React, { useState, useMemo } from 'react';
import { CameraBackdrop } from './CameraBackdrop';
import { SkeletonCanvas } from './SkeletonCanvas';
import { GarmentCanvas } from './GarmentCanvas';
import { ProductCatalogDrawer } from './ProductCatalogDrawer';
import { useCamera } from '../hooks/useCamera';
import { usePoseStream } from '../hooks/usePoseStream';
import { useCatalog } from '../hooks/useCatalog';
import { DEFAULT_GARMENTS, GarmentMetadata } from '../rendering/GarmentAsset';

export const MirrorView: React.FC = () => {
  const { videoRef, isActive: isCameraActive, error: cameraError } = useCamera();
  const trackingFrame = usePoseStream();
  const {
    categories,
    products,
    selectedCategory,
    selectedProduct,
    isLoading: isCatalogLoading,
    error: catalogError,
    setSelectedCategory,
    setSelectedProduct,
    refreshCatalog
  } = useCatalog();

  const [showSkeleton, setShowSkeleton] = useState<boolean>(false);
  const [showGarment, setShowGarment] = useState<boolean>(true);

  // Map selected product to garment metadata with fallback
  const activeGarment: GarmentMetadata | null = useMemo(() => {
    if (!selectedProduct) return DEFAULT_GARMENTS.oct_jkt_001;

    // Check if customized metadata exists for this product ID
    if (DEFAULT_GARMENTS[selectedProduct.id]) {
      return DEFAULT_GARMENTS[selectedProduct.id];
    }

    // Default garment dynamic adapter for jacket/outerwear categories
    return {
      id: selectedProduct.id,
      name: selectedProduct.name,
      category: selectedProduct.category_id,
      assetUrl: DEFAULT_GARMENTS.oct_jkt_001.assetUrl, // Reuses front-facing clean bomber silhouette
      anchorConfig: { anchorX: 0.5, anchorY: 0.28 },
      calibration: { scaleMultiplier: 2.2, xOffset: 0.0, yOffset: -0.02, rotationOffsetDeg: 0.0 }
    };
  }, [selectedProduct]);

  // Status badge styling
  const stateBadgeColor =
    trackingFrame.tracking_state === 'tracked'
      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
      : trackingFrame.tracking_state === 'lost'
      ? 'bg-rose-500/20 text-rose-400 border-rose-500/40'
      : 'bg-amber-500/20 text-amber-400 border-amber-500/40';

  return (
    <div className="relative w-full h-full bg-black flex flex-col justify-between p-6 select-none overflow-hidden font-sans">
      {/* 1. Live Camera Feed Layer */}
      <CameraBackdrop videoRef={videoRef} isActive={isCameraActive} error={cameraError} />

      {/* 2. Phase 2 Real-Time AR Virtual Garment Fitting Layer */}
      <GarmentCanvas
        trackingFrame={trackingFrame}
        garment={activeGarment}
        visible={showGarment}
      />

      {/* 3. Real-time Skeleton Overlay Layer (Optional debug mode) */}
      <SkeletonCanvas trackingFrame={trackingFrame} visible={showSkeleton} />

      {/* 4. Top Header & Telemetry Layer */}
      <header className="z-20 flex justify-between items-center bg-black/60 backdrop-blur-md px-6 py-4 rounded-3xl border border-white/10 shadow-xl">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-black tracking-widest text-white">MIRAI</h1>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              Phase 2 AR Live
            </span>
          </div>
          <p className="text-[11px] text-neutral-400 mt-0.5">
            {activeGarment ? `Wearing: ${activeGarment.name}` : 'OCTACEPT • Try Beyond Reality'}
          </p>
        </div>

        {/* Telemetry & toggle controls */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowGarment((prev) => !prev)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-all ${
              showGarment
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-400/50'
                : 'bg-white/5 text-neutral-400 border-white/10'
            }`}
          >
            Garment: {showGarment ? 'ON' : 'OFF'}
          </button>

          <button
            onClick={() => setShowSkeleton((prev) => !prev)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-all ${
              showSkeleton
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400/50'
                : 'bg-white/5 text-neutral-400 border-white/10'
            }`}
          >
            Skeleton: {showSkeleton ? 'ON' : 'OFF'}
          </button>

          <div className="hidden sm:flex items-center space-x-4 text-xs font-mono text-neutral-300 bg-white/5 px-4 py-1.5 rounded-full border border-white/10">
            <div>
              FPS: <span className="text-emerald-400 font-bold">{trackingFrame.fps.toFixed(0)}</span>
            </div>
            <div>
              Conf: <span className="text-cyan-400 font-bold">{(trackingFrame.confidence * 100).toFixed(0)}%</span>
            </div>
            {trackingFrame.body_anchors && (
              <div>
                Tilt: <span className="text-amber-400 font-bold">{trackingFrame.body_anchors.shoulder_angle_deg.toFixed(1)}°</span>
              </div>
            )}
          </div>

          <div
            className={`text-xs px-3 py-1 rounded-full uppercase font-bold tracking-wider border ${stateBadgeColor}`}
          >
            {trackingFrame.tracking_state}
          </div>
        </div>
      </header>

      {/* 5. Bottom Product Catalog Drawer */}
      <ProductCatalogDrawer
        categories={categories}
        products={products}
        selectedCategory={selectedCategory}
        selectedProduct={selectedProduct}
        isLoading={isCatalogLoading}
        error={catalogError}
        onSelectCategory={setSelectedCategory}
        onSelectProduct={setSelectedProduct}
        onRetry={refreshCatalog}
      />
    </div>
  );
};
