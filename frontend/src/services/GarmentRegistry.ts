/**
 * MIRAI — Garment Registry
 *
 * Ground-truth product-to-garment reference mapping for Neural Realtime Virtual Try-On (Lucy V-TON).
 *
 * Strict Architectural Invariant:
 * Every product maps to its own authenticated garment reference or is marked explicitly as
 * `isLiveVTOReady: false`. NEVER fallback to the linen shirt for hoodies, jackets, or other items!
 */

import type { GarmentReference } from './vto/types';

export const GARMENT_REGISTRY: Record<string, GarmentReference> = {
  // ── Primary Test Target: Relaxed Camp-Collar Linen Shirt ──────────
  oct_sht_002: {
    productId: 'oct_sht_002',
    name: 'Relaxed Camp-Collar Linen Shirt',
    category: 'shirts',
    referenceImageUrl: '/garments/camp_collar_linen_shirt.png',
    vtonPrompt:
      'Relaxed camp-collar short-sleeve linen shirt in natural flax tan color, Cuban open collar, mother of pearl front buttons, breathable linen textile weave, relaxed tailored fit',
    isLiveVTOReady: true,
  },

  // ── Jackets & Outerwear (Marked false until high-res garment reference is verified) ──
  oct_jkt_001: {
    productId: 'oct_jkt_001',
    name: 'Cyber Techwear Bomber',
    category: 'jackets',
    referenceImageUrl: '',
    vtonPrompt: 'Matte black cyber techwear bomber jacket with tactical zips and ribbed collar',
    isLiveVTOReady: false,
  },
  oct_jkt_002: {
    productId: 'oct_jkt_002',
    name: 'Minimalist Wool Overcoat',
    category: 'jackets',
    referenceImageUrl: '',
    vtonPrompt: 'Oatmeal minimalist structured wool overcoat with tailored notch lapels',
    isLiveVTOReady: false,
  },

  // ── Hoodies & Sweatshirts ──
  oct_hod_001: {
    productId: 'oct_hod_001',
    name: 'Heavyweight French Terry Hoodie',
    category: 'hoodies',
    referenceImageUrl: '',
    vtonPrompt: 'Heather grey heavyweight French terry cotton hoodie with kangaroo pocket',
    isLiveVTOReady: false,
  },

  // ── Shirts & Tops ──
  oct_sht_001: {
    productId: 'oct_sht_001',
    name: 'Oxford Mercerized Cotton Shirt',
    category: 'shirts',
    referenceImageUrl: '',
    vtonPrompt: 'Crisp white Oxford mercerized button-down cotton shirt with long sleeves and barrel cuffs',
    isLiveVTOReady: false,
  },
};

/**
 * Normalizes product ID or SKU to registry key.
 * Handles both "oct_sht_002" and "OCT-SHT-002".
 */
export function normalizeProductId(idOrSku: string): string {
  return idOrSku.toLowerCase().replace(/[^a-z0-9]/g, '_');
}

/**
 * Retrieves the garment reference for a product, or null if unmapped.
 */
export function getGarmentReference(productIdOrSku: string): GarmentReference | null {
  const key = normalizeProductId(productIdOrSku);
  return GARMENT_REGISTRY[key] ?? null;
}

/**
 * Checks whether a product has a verified Live VTO reference ready.
 */
export function isLiveVTOAvailable(productIdOrSku: string): boolean {
  const ref = getGarmentReference(productIdOrSku);
  return ref ? ref.isLiveVTOReady : false;
}

/**
 * Returns all products verified for Live VTO.
 */
export function getLiveVTOGarments(): GarmentReference[] {
  return Object.values(GARMENT_REGISTRY).filter((g) => g.isLiveVTOReady);
}
