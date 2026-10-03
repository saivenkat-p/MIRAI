/**
 * ProductCatalog — Collapsible Right-Side Wardrobe Panel.
 *
 * Positions the product selection cleanly on the right side of the screen,
 * leaving the entire center of the mirror (head, shoulders, torso, arms, waist)
 * completely unobstructed for live AR try-on testing and movement inspection.
 */

import React, { useState } from 'react';
import {
  Sparkles,
  Camera,
  Check,
  X,
  ChevronRight,
  ChevronLeft,
  Shirt,
} from 'lucide-react';
import type { Product, ProductCategory } from '../types/api';
import { isLiveVTOAvailable } from '../services/GarmentRegistry';

interface ProductCatalogProps {
  categories: ProductCategory[];
  products: Product[];
  activeCategoryId: string | null;
  selectedProduct: Product | null;
  loading: boolean;
  error?: string | null;
  onRetry?: () => void;
  isARActive: boolean;
  onSelectCategory: (id: string) => void;
  onSelectProduct: (product: Product) => void;
  onToggleAR: () => void;
  onPhotoTryOn: () => void;
  onClearSelection: () => void;
}

/** Format price as ₹1,499 */
function formatPrice(price: number, currency: string): string {
  if (currency === 'INR') {
    return `₹${price.toLocaleString('en-IN')}`;
  }
  return `${currency} ${price.toFixed(2)}`;
}

const CATEGORY_ICONS: Record<string, string> = {
  jackets: '🧥',
  hoodies: '👕',
  shirts: '👔',
  trousers: '👖',
  dresses: '👗',
};

export const ProductCatalog: React.FC<ProductCatalogProps> = ({
  categories,
  products,
  activeCategoryId,
  selectedProduct,
  loading,
  error,
  onRetry,
  isARActive,
  onSelectCategory,
  onSelectProduct,
  onToggleAR,
  onPhotoTryOn,
  onClearSelection,
}) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);

  // If collapsed, render a sleek floating toggle tab on the right edge
  if (isCollapsed) {
    return (
      <div className="absolute right-4 top-24 z-20 pointer-events-auto">
        <button
          onClick={() => setIsCollapsed(false)}
          className="flex items-center gap-2 px-4 py-3 rounded-2xl
                     bg-black/85 backdrop-blur-xl border border-white/20
                     text-white shadow-2xl hover:bg-black/95 hover:border-violet-500/50
                     transition-all duration-200 active:scale-95 group"
          title="Open Wardrobe / Catalog"
        >
          <ChevronLeft size={18} className="text-violet-400 group-hover:-translate-x-0.5 transition-transform" />
          <Shirt size={16} className="text-violet-300" />
          <span className="font-bold text-xs tracking-wider">WARDROBE</span>
          {selectedProduct && (
            <span className="w-2 h-2 rounded-full bg-violet-400 animate-ping ml-1" />
          )}
        </button>
      </div>
    );
  }

  return (
    <aside
      className="absolute right-4 top-20 bottom-4 z-20 pointer-events-auto
                 w-80 sm:w-88 md:w-92 flex flex-col
                 bg-black/85 backdrop-blur-2xl border border-white/15
                 rounded-3xl shadow-2xl overflow-hidden transition-all duration-300"
    >
      {/* ── Top Panel Header ── */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-white/[0.02]">
        <div className="flex items-center gap-2">
          <Shirt size={16} className="text-violet-400" />
          <span className="font-bold text-sm text-white tracking-wider">WARDROBE</span>
          <span className="px-2 py-0.5 rounded-full bg-white/10 text-neutral-300 text-[10px] font-mono">
            {products.length}
          </span>
        </div>

        {/* Collapse Button */}
        <button
          onClick={() => setIsCollapsed(true)}
          className="p-1.5 rounded-xl bg-white/5 hover:bg-white/15 text-neutral-300 hover:text-white transition-colors"
          title="Minimize catalog to view full mirror"
        >
          <ChevronRight size={18} />
        </button>
      </div>

      {/* ── Active / Selected Garment Hero Card ── */}
      {selectedProduct && (
        <div className="p-3 border-b border-white/10 bg-violet-950/20">
          <div className="bg-black/60 border border-violet-500/30 rounded-2xl p-3.5 shadow-lg">
            <div className="flex items-start justify-between gap-2 mb-2.5">
              <div className="min-w-0">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <p className="text-white font-bold text-sm leading-tight truncate">
                    {selectedProduct.name}
                  </p>
                  {isLiveVTOAvailable(selectedProduct.id) ? (
                    isARActive ? (
                      <span className="px-2 py-0.2 rounded-full bg-emerald-500/25 border border-emerald-400/50 text-emerald-300 text-[9px] font-bold tracking-wider animate-pulse">
                        LUCY V-TON ACTIVE
                      </span>
                    ) : (
                      <span className="px-2 py-0.2 rounded-full bg-violet-500/20 border border-violet-400/40 text-violet-300 text-[9px] font-bold tracking-wider">
                        LIVE VTO READY
                      </span>
                    )
                  ) : (
                    <span className="px-2 py-0.2 rounded-full bg-amber-500/20 border border-amber-400/40 text-amber-300 text-[9px] font-bold tracking-wider">
                      PHOTO AI ONLY
                    </span>
                  )}
                </div>
                <p className="text-emerald-400 font-bold text-sm mt-0.5">
                  {formatPrice(selectedProduct.price, selectedProduct.currency)}
                </p>
                <p className="text-neutral-400 text-[11px]">{selectedProduct.brand}</p>
              </div>

              <div className="flex items-center gap-1.5 flex-shrink-0">
                {/* Color swatches */}
                <div className="flex gap-1">
                  {selectedProduct.colors.map((c) => (
                    <div
                      key={c.name}
                      title={c.name}
                      className="w-4 h-4 rounded-full border border-white/30"
                      style={{ backgroundColor: c.hex }}
                    />
                  ))}
                </div>
                {/* Unselect / remove */}
                <button
                  onClick={onClearSelection}
                  className="p-1 rounded-full bg-white/10 hover:bg-white/20 text-neutral-300 transition-colors"
                  title="Remove garment"
                >
                  <X size={12} />
                </button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={onToggleAR}
                disabled={!isLiveVTOAvailable(selectedProduct.id)}
                title={
                  isLiveVTOAvailable(selectedProduct.id)
                    ? 'Start live real-time try-on with Decart Lucy V-TON'
                    : 'Live VTO reference asset in preparation. Please use AI Photo Try-On.'
                }
                className={`flex-1 py-2 px-3 rounded-xl font-bold text-xs tracking-wide
                           transition-all duration-200 active:scale-95 flex items-center justify-center gap-1.5 shadow-md
                           ${
                             !isLiveVTOAvailable(selectedProduct.id)
                               ? 'bg-neutral-800 text-neutral-500 border border-neutral-700 cursor-not-allowed'
                               : isARActive
                               ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white ring-1 ring-emerald-400/50'
                               : 'bg-white text-black hover:bg-neutral-100'
                           }`}
              >
                <Sparkles size={13} className={isARActive ? 'animate-spin' : ''} />
                <span>
                  {!isLiveVTOAvailable(selectedProduct.id)
                    ? 'LIVE VTO PENDING'
                    : isARActive
                    ? 'LUCY V-TON: ON'
                    : 'TRY ON (LUCY VTO)'}
                </span>
              </button>

              <button
                onClick={onPhotoTryOn}
                title="Generate high-res AI photo snapshot"
                className="px-3 py-2 rounded-xl font-semibold text-[11px]
                           bg-white/10 hover:bg-white/15 text-neutral-200 border border-white/15
                           transition-all active:scale-95 flex items-center gap-1 whitespace-nowrap"
              >
                <Camera size={12} />
                <span>AI Photo</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Category Filter Pills ── */}
      <div className="flex overflow-x-auto no-scrollbar gap-1.5 px-3 py-2.5 border-b border-white/5 bg-white/[0.01]">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => onSelectCategory(cat.id)}
            className={`flex-shrink-0 flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-semibold
                        transition-all duration-150 whitespace-nowrap
                        ${
                          activeCategoryId === cat.id
                            ? 'bg-white text-black shadow-md'
                            : 'bg-white/10 text-neutral-300 hover:bg-white/20'
                        }`}
          >
            <span>{CATEGORY_ICONS[cat.id] ?? '🏷️'}</span>
            <span>{cat.name.split('&')[0].trim()}</span>
          </button>
        ))}
      </div>

      {/* ── Scrollable Product List (Vertical) ── */}
      <div className="flex-1 overflow-y-auto no-scrollbar p-3 space-y-2.5">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="h-20 rounded-2xl bg-white/5 animate-pulse"
            />
          ))
        ) : error && products.length === 0 ? (
          <div className="py-8 px-4 text-center">
            <p className="text-amber-400 text-xs font-semibold mb-1">Backend Connection Issue</p>
            <p className="text-neutral-400 text-[11px] mb-3">{error}</p>
            {onRetry && (
              <button
                onClick={onRetry}
                className="px-3 py-1.5 bg-violet-600 hover:bg-violet-500 text-white rounded-xl text-xs font-semibold transition-all active:scale-95"
              >
                Reconnect Catalog
              </button>
            )}
          </div>
        ) : products.length === 0 ? (
          <p className="text-neutral-500 text-xs py-8 text-center">No products found in this category.</p>
        ) : (
          products.map((product) => {
            const isSelected = selectedProduct?.id === product.id;
            const primaryColor = product.colors[0];

            return (
              <button
                key={product.id}
                onClick={() => onSelectProduct(product)}
                className={`w-full p-2.5 rounded-2xl border transition-all duration-150
                            text-left flex items-center gap-3 relative group
                            ${
                              isSelected
                                ? 'border-violet-500 bg-violet-950/70 shadow-lg shadow-violet-900/40 ring-1 ring-violet-400/50'
                                : 'border-white/10 bg-white/5 hover:border-white/25 hover:bg-white/10'
                            }`}
              >
                {/* Thumbnail / Swatch */}
                <div
                  className="w-14 h-14 rounded-xl flex-shrink-0 relative flex items-center justify-center overflow-hidden"
                  style={{
                    background: primaryColor
                      ? `linear-gradient(135deg, ${primaryColor.hex}dd 0%, ${primaryColor.hex}66 100%)`
                      : '#1e1e1e',
                  }}
                >
                  <span className="text-xl opacity-80 select-none group-hover:scale-110 transition-transform">
                    {CATEGORY_ICONS[product.category_id] ?? '🏷️'}
                  </span>
                  {isSelected && (
                    <div className="absolute top-1 right-1 w-4 h-4 bg-violet-500 rounded-full flex items-center justify-center shadow">
                      <Check size={10} className="text-white" />
                    </div>
                  )}
                </div>

                {/* Details */}
                <div className="min-w-0 flex-1">
                  <p className="text-white text-xs font-semibold leading-snug line-clamp-1">
                    {product.name}
                  </p>
                  <p className="text-emerald-400 text-xs font-bold mt-0.5">
                    {formatPrice(product.price, product.currency)}
                  </p>
                  <div className="flex items-center gap-2 mt-0.5">
                    {primaryColor && (
                      <span className="text-neutral-400 text-[11px] truncate">
                        {primaryColor.name}
                      </span>
                    )}
                    <span className="text-neutral-600 text-[10px]">•</span>
                    <span className="text-neutral-400 text-[10px] font-mono">
                      {product.sizes.join(', ')}
                    </span>
                  </div>
                </div>
              </button>
            );
          })
        )}
      </div>

      {/* ── Bottom Footer Hint ── */}
      <div className="px-4 py-2 border-t border-white/5 bg-white/[0.01] text-center">
        <p className="text-[10px] text-neutral-500">
          Tap garment to try on • Click <span className="text-neutral-400 font-bold">&gt;</span> to minimize
        </p>
      </div>
    </aside>
  );
};
