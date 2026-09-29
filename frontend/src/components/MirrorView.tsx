import React, { useState } from 'react';
import { CameraBackdrop } from './CameraBackdrop';
import { SkeletonCanvas } from './SkeletonCanvas';
import { ProductCatalogDrawer } from './ProductCatalogDrawer';
import { useCamera } from '../hooks/useCamera';
import { usePoseStream } from '../hooks/usePoseStream';
import { useCatalog } from '../hooks/useCatalog';

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

  const [showSkeleton, setShowSkeleton] = useState<boolean>(true);

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

      {/* 2. Real-time Skeleton Overlay Layer */}
      <SkeletonCanvas trackingFrame={trackingFrame} visible={showSkeleton} />

      {/* 3. Top Header & Telemetry Layer */}
      <header className="z-20 flex justify-between items-center bg-black/60 backdrop-blur-md px-6 py-4 rounded-3xl border border-white/10 shadow-xl">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-black tracking-widest text-white">MIRAI</h1>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              Phase 1 Live
            </span>
          </div>
          <p className="text-[11px] text-neutral-400 mt-0.5">OCTACEPT • Try Beyond Reality</p>
        </div>

        {/* Telemetry metrics bar */}
        <div className="flex items-center space-x-4">
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
          </div>

          <div
            className={`text-xs px-3 py-1 rounded-full uppercase font-bold tracking-wider border ${stateBadgeColor}`}
          >
            {trackingFrame.tracking_state}
          </div>
        </div>
      </header>

      {/* 4. Bottom Product Catalog Drawer */}
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
