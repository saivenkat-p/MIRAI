import React from 'react';
import { TrackingFrame } from '../types/tracking';
import { Product } from '../types/api';

interface MirrorViewProps {
  currentFrame?: TrackingFrame;
  selectedProduct?: Product;
}

export const MirrorView: React.FC<MirrorViewProps> = ({ currentFrame, selectedProduct }) => {
  return (
    <div className="relative w-full h-full bg-neutral-950 flex flex-col justify-between p-6 select-none overflow-hidden">
      {/* Top Header / Telemetry Bar */}
      <header className="flex justify-between items-center z-10 bg-black/60 backdrop-blur-md px-6 py-4 rounded-2xl border border-white/10">
        <div>
          <h1 className="text-xl font-bold tracking-widest text-white">MIRAI</h1>
          <p className="text-xs text-neutral-400">OCTACEPT • Try Beyond Reality</p>
        </div>
        <div className="flex items-center space-x-6 text-xs text-neutral-300">
          <div>
            FPS: <span className="font-mono text-emerald-400">{currentFrame?.fps?.toFixed(0) ?? '--'}</span>
          </div>
          <div>
            Tracking: <span className="font-mono text-cyan-400">{currentFrame?.tracking_state ?? 'searching'}</span>
          </div>
        </div>
      </header>

      {/* Center AR / Mirrored Viewport Area */}
      <main className="absolute inset-0 flex items-center justify-center">
        <div className="text-center text-neutral-500">
          <p className="text-sm font-medium">PHASE 0 MIRROR VIEWPORT</p>
          <p className="text-xs mt-1">Portrait Mode 1080x1920 • Camera / AR Scaffolding Active</p>
        </div>
      </main>

      {/* Bottom Product Selection Bar Placeholder */}
      <footer className="z-10 bg-black/60 backdrop-blur-md p-4 rounded-2xl border border-white/10 flex items-center justify-between">
        <div className="text-xs text-neutral-400">
          Selected Product: <span className="text-white font-semibold">{selectedProduct?.name ?? 'None'}</span>
        </div>
        <div className="text-xs text-neutral-500">
          Touch to browse catalog
        </div>
      </footer>
    </div>
  );
};
