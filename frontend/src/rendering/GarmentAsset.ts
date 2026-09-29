/**
 * Garment Asset definitions and image caching manager.
 * Supports configurable garment anchors, scaling multipliers, and offsets.
 */
export interface GarmentAnchorConfig {
  // Anchor ratio relative to garment image dimensions (0.0 to 1.0)
  anchorX: number; // default: 0.5 (center)
  anchorY: number; // default: 0.28 (collar/shoulder line)
}

export interface GarmentCalibration {
  scaleMultiplier: number; // Relative to shoulder width
  xOffset: number;         // Normalized translation offset
  yOffset: number;         // Normalized vertical offset
  rotationOffsetDeg: number;
}

export interface GarmentMetadata {
  id: string;
  name: string;
  category: string;
  assetUrl: string;
  anchorConfig: GarmentAnchorConfig;
  calibration: GarmentCalibration;
}

// Embedded high-fidelity SVG graphic for offline demo of Cyber Techwear Bomber (OCT-JKT-001)
const TECHWEAR_BOMBER_SVG = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500">
  <defs>
    <linearGradient id="jacketGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="%231a1a1a"/>
      <stop offset="50%" stop-color="%23262626"/>
      <stop offset="100%" stop-color="%230f0f0f"/>
    </linearGradient>
    <linearGradient id="zipperGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="%2300ffff"/>
      <stop offset="100%" stop-color="%230088cc"/>
    </linearGradient>
  </defs>
  <!-- Torso & Sleeves -->
  <path d="M170 120 L250 145 L330 120 L440 220 L390 270 L340 210 L340 380 L160 380 L160 210 L110 270 L60 220 Z" fill="url(%23jacketGrad)" stroke="%23333333" stroke-width="4"/>
  <!-- Collar -->
  <path d="M190 120 Q250 160 310 120 L290 100 Q250 130 210 100 Z" fill="%23111111" stroke="%23444444" stroke-width="2"/>
  <!-- Neon Cyan Accent Piping -->
  <path d="M170 120 L160 380" stroke="%2300f3ff" stroke-width="3" stroke-dasharray="10,5" opacity="0.8"/>
  <path d="M330 120 L340 380" stroke="%2300f3ff" stroke-width="3" stroke-dasharray="10,5" opacity="0.8"/>
  <!-- Front Zipper -->
  <line x1="250" y1="145" x2="250" y2="380" stroke="url(%23zipperGrad)" stroke-width="5"/>
  <!-- Chest Utility Pockets -->
  <rect x="180" y="200" width="50" height="55" rx="6" fill="%23141414" stroke="%2300f3ff" stroke-width="1.5" opacity="0.9"/>
  <rect x="270" y="200" width="50" height="55" rx="6" fill="%23141414" stroke="%23444444" stroke-width="1.5"/>
  <!-- Hem Cuffs -->
  <rect x="160" y="375" width="180" height="15" rx="4" fill="%23111111" stroke="%23222222" stroke-width="1"/>
</svg>`;

export const DEFAULT_GARMENTS: Record<string, GarmentMetadata> = {
  oct_jkt_001: {
    id: 'oct_jkt_001',
    name: 'Cyber Techwear Bomber',
    category: 'jackets',
    assetUrl: TECHWEAR_BOMBER_SVG,
    anchorConfig: {
      anchorX: 0.5,
      anchorY: 0.28 // Aligns with shoulder neckline
    },
    calibration: {
      scaleMultiplier: 2.2, // Scales jacket width to 2.2x shoulder-to-shoulder distance
      xOffset: 0.0,
      yOffset: -0.02,
      rotationOffsetDeg: 0.0
    }
  }
};

export class GarmentAssetCache {
  private static cache: Map<string, HTMLImageElement> = new Map();
  private static loadingPromises: Map<string, Promise<HTMLImageElement>> = new Map();

  /**
   * Preloads or retrieves cached image element.
   * Guarantees images are loaded once and reused across frame renders.
   */
  public static async loadAsset(assetUrl: string): Promise<HTMLImageElement> {
    const cached = this.cache.get(assetUrl);
    if (cached && cached.complete) {
      return cached;
    }

    const pending = this.loadingPromises.get(assetUrl);
    if (pending) {
      return pending;
    }

    const promise = new Promise<HTMLImageElement>((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        this.cache.set(assetUrl, img);
        this.loadingPromises.delete(assetUrl);
        resolve(img);
      };
      img.onerror = (err) => {
        this.loadingPromises.delete(assetUrl);
        reject(new Error(`Failed to load garment asset from ${assetUrl}: ${err}`));
      };
      img.src = assetUrl;
    });

    this.loadingPromises.set(assetUrl, promise);
    return promise;
  }

  public static getSync(assetUrl: string): HTMLImageElement | null {
    const img = this.cache.get(assetUrl);
    return img && img.complete && img.naturalWidth > 0 ? img : null;
  }

  public static clear(): void {
    this.cache.clear();
    this.loadingPromises.clear();
  }
}
