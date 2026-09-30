/**
 * TryOnOverlay — full-screen overlay showing the try-on flow states.
 *
 * States:
 *   capturing   — "Capturing your image..."
 *   processing  — "Creating your look..." with progress animation
 *   success     — Generated result image + product info + action buttons
 *   error       — User-friendly error message + retry button
 *
 * The DEMO badge is always visible when mode === 'demo' to clearly
 * communicate this is NOT real AI virtual try-on.
 */

import React from 'react';
import { RotateCcw, Plus, Bookmark, AlertCircle, Camera, Sparkles } from 'lucide-react';
import type { Product } from '../types/api';
import type { TryOnState } from '../hooks/useTryOn';

interface TryOnOverlayProps {
  state: TryOnState;
  resultImage: string | null;
  resultMode: 'demo' | 'ai' | null;
  processingMs: number | null;
  error: string | null;
  product: Product | null;
  capturedPersonB64: string | null;
  onTryAnother: () => void;
  onRetry: () => void;
  onSaveLook: () => void;
}

function formatPrice(price: number, currency: string): string {
  if (currency === 'INR') return `₹${price.toLocaleString('en-IN')}`;
  return `${currency} ${price.toFixed(2)}`;
}

// ── Capturing state ──────────────────────────────────────────────────────────

const CapturingView: React.FC = () => (
  <div className="flex flex-col items-center justify-center h-full gap-6 px-8">
    <div className="w-20 h-20 rounded-full border-2 border-violet-500/60 flex items-center justify-center animate-pulse">
      <Camera size={36} className="text-violet-400" />
    </div>
    <div className="text-center">
      <p className="text-white text-xl font-semibold">Capturing your image</p>
      <p className="text-neutral-400 text-sm mt-1">Hold still for a moment...</p>
    </div>
  </div>
);

// ── Processing state ─────────────────────────────────────────────────────────

const ProcessingView: React.FC<{ product: Product | null; capturedB64: string | null }> = ({
  product,
  capturedB64,
}) => (
  <div className="flex flex-col items-center justify-center h-full gap-6 px-8">
    {/* Person + garment preview */}
    <div className="flex items-center gap-4">
      <div className="w-24 h-24 rounded-2xl overflow-hidden border border-white/20 bg-white/5">
        {capturedB64 ? (
          <img
            src={`data:image/jpeg;base64,${capturedB64}`}
            alt="Your image"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Camera size={24} className="text-neutral-500" />
          </div>
        )}
      </div>
      <div className="text-neutral-400 text-xl">+</div>
      <div
        className="w-24 h-24 rounded-2xl border border-white/20 flex items-center justify-center"
        style={{
          background: product?.colors[0]
            ? `linear-gradient(135deg, ${product.colors[0].hex}bb, ${product.colors[0].hex}44)`
            : '#1a1a1a',
        }}
      >
        <span className="text-3xl">🧥</span>
      </div>
    </div>

    {/* Progress ring */}
    <div className="relative w-16 h-16">
      <svg className="w-16 h-16 -rotate-90" viewBox="0 0 64 64">
        <circle cx="32" cy="32" r="28" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="4" />
        <circle
          cx="32" cy="32" r="28"
          fill="none"
          stroke="url(#vtoGrad)"
          strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray="175"
          strokeDashoffset="35"
          className="animate-spin"
          style={{ animationDuration: '1.4s' }}
        />
        <defs>
          <linearGradient id="vtoGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#7c3aed" />
            <stop offset="100%" stopColor="#4f46e5" />
          </linearGradient>
        </defs>
      </svg>
    </div>

    <div className="text-center">
      <p className="text-white text-xl font-semibold flex items-center gap-2">
        <Sparkles size={18} className="text-violet-400" />
        Creating your look...
      </p>
      {product && (
        <p className="text-neutral-400 text-sm mt-1">
          Fitting {product.name}
        </p>
      )}
      <p className="text-neutral-600 text-xs mt-3">This may take a few seconds</p>
    </div>

    {/* Step indicators */}
    <div className="flex items-center gap-3 text-xs text-neutral-500">
      <span className="flex items-center gap-1.5">
        <span className="w-2 h-2 bg-emerald-500 rounded-full" />
        Captured
      </span>
      <span className="w-6 h-px bg-neutral-700" />
      <span className="flex items-center gap-1.5">
        <span className="w-2 h-2 bg-violet-500 rounded-full animate-pulse" />
        Generating
      </span>
      <span className="w-6 h-px bg-neutral-700" />
      <span className="flex items-center gap-1.5">
        <span className="w-2 h-2 bg-neutral-700 rounded-full" />
        Finalise
      </span>
    </div>
  </div>
);

// ── Success state ────────────────────────────────────────────────────────────

const SuccessView: React.FC<{
  resultImage: string;
  mode: 'demo' | 'ai';
  product: Product | null;
  processingMs: number | null;
  onTryAnother: () => void;
  onSaveLook: () => void;
}> = ({ resultImage, mode, product, processingMs, onTryAnother, onSaveLook }) => (
  <div className="flex flex-col h-full">
    {/* Result image — main focus */}
    <div className="relative flex-1 overflow-hidden">
      <img
        src={`data:image/png;base64,${resultImage}`}
        alt="Your virtual try-on result"
        className="w-full h-full object-cover"
      />

      {/* DEMO badge — always shown when mode is demo */}
      {mode === 'demo' && (
        <div className="absolute top-4 left-4 flex items-center gap-1.5 bg-red-600/90 backdrop-blur-sm
                        text-white text-xs font-bold px-3 py-1.5 rounded-full border border-red-500/50">
          ⚡ DEMO MODE
          <span className="font-normal opacity-80">— Not real AI VTO</span>
        </div>
      )}

      {processingMs !== null && (
        <div className="absolute top-4 right-4 bg-black/60 backdrop-blur-sm text-neutral-400
                        text-xs px-2.5 py-1 rounded-full">
          {processingMs}ms
        </div>
      )}

      {/* Gradient fade at bottom */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-neutral-950 to-transparent" />
    </div>

    {/* Product info + actions */}
    <div className="bg-neutral-950 px-5 pb-6 pt-4">
      {product && (
        <div className="mb-4">
          <p className="text-white font-bold text-lg">{product.name}</p>
          <p className="text-emerald-400 font-bold text-base">
            {formatPrice(product.price, product.currency)}
          </p>
          <p className="text-neutral-500 text-xs mt-0.5">{product.brand}</p>
        </div>
      )}

      <div className="flex flex-col gap-2.5">
        <button
          onClick={onTryAnother}
          className="w-full py-3 rounded-xl bg-violet-600 hover:bg-violet-500
                     text-white font-bold text-sm tracking-wide transition-all
                     active:scale-95 flex items-center justify-center gap-2"
        >
          <RotateCcw size={16} />
          TRY ANOTHER
        </button>

        <div className="flex gap-2.5">
          <button
            onClick={onTryAnother}
            className="flex-1 py-3 rounded-xl bg-white/10 hover:bg-white/20
                       text-white text-sm font-semibold transition-all
                       active:scale-95 flex items-center justify-center gap-2 border border-white/10"
          >
            <Plus size={15} />
            ADD TO LOOK
          </button>
          <button
            onClick={onSaveLook}
            className="flex-1 py-3 rounded-xl bg-white/10 hover:bg-white/20
                       text-white text-sm font-semibold transition-all
                       active:scale-95 flex items-center justify-center gap-2 border border-white/10"
          >
            <Bookmark size={15} />
            SAVE LOOK
          </button>
        </div>
      </div>
    </div>
  </div>
);

// ── Error state ──────────────────────────────────────────────────────────────

const ErrorView: React.FC<{
  message: string;
  onRetry: () => void;
  onBack: () => void;
}> = ({ message, onRetry, onBack }) => (
  <div className="flex flex-col items-center justify-center h-full gap-6 px-8 text-center">
    <div className="w-16 h-16 rounded-full bg-red-900/30 border border-red-700/50 flex items-center justify-center">
      <AlertCircle size={28} className="text-red-400" />
    </div>
    <div>
      <p className="text-white text-lg font-semibold">Unable to create your look</p>
      <p className="text-neutral-400 text-sm mt-2 leading-relaxed">{message}</p>
    </div>
    <div className="flex flex-col gap-3 w-full">
      <button
        onClick={onRetry}
        className="w-full py-3 rounded-xl bg-violet-600 hover:bg-violet-500
                   text-white font-bold text-sm tracking-wide transition-all
                   active:scale-95 flex items-center justify-center gap-2"
      >
        <RotateCcw size={16} />
        TRY AGAIN
      </button>
      <button
        onClick={onBack}
        className="w-full py-3 rounded-xl bg-white/10 hover:bg-white/20
                   text-white text-sm font-semibold transition-all
                   active:scale-95 border border-white/10"
      >
        Back to catalog
      </button>
    </div>
  </div>
);

// ── Main overlay component ───────────────────────────────────────────────────

export const TryOnOverlay: React.FC<TryOnOverlayProps> = ({
  state,
  resultImage,
  resultMode,
  processingMs,
  error,
  product,
  capturedPersonB64,
  onTryAnother,
  onRetry,
  onSaveLook,
}) => {
  if (state === 'idle') return null;

  return (
    <div className="absolute inset-0 z-30 bg-neutral-950 flex flex-col">
      {/* Header */}
      <header className="flex-shrink-0 flex items-center justify-between px-5 pt-5 pb-3">
        <div>
          <h1 className="text-white font-bold text-lg tracking-widest">MIRAI</h1>
          <p className="text-neutral-500 text-xs">OCTACEPT • Try Beyond Reality</p>
        </div>
        {state === 'success' && (
          <div className="bg-emerald-900/40 border border-emerald-700/50 px-3 py-1.5 rounded-full">
            <p className="text-emerald-400 text-xs font-semibold">YOUR LOOK</p>
          </div>
        )}
      </header>

      {/* Content area */}
      <div className="flex-1 overflow-hidden">
        {state === 'capturing' && <CapturingView />}

        {state === 'processing' && (
          <ProcessingView product={product} capturedB64={capturedPersonB64} />
        )}

        {state === 'success' && resultImage && (
          <SuccessView
            resultImage={resultImage}
            mode={resultMode ?? 'demo'}
            product={product}
            processingMs={processingMs}
            onTryAnother={onTryAnother}
            onSaveLook={onSaveLook}
          />
        )}

        {state === 'error' && (
          <ErrorView
            message={error ?? 'Something went wrong.'}
            onRetry={onRetry}
            onBack={onTryAnother}
          />
        )}
      </div>
    </div>
  );
};
