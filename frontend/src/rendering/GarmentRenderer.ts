/**
 * Real-time 2D Canvas Garment Renderer.
 * Renders virtual clothing overlays anchored to tracked body geometry.
 */
import { ComputedTransform } from './GarmentTransform';
import { GarmentMetadata, GarmentAssetCache } from './GarmentAsset';

export class GarmentRenderer {
  private canvas: HTMLCanvasElement | null = null;
  private ctx: CanvasRenderingContext2D | null = null;
  private currentAssetUrl: string | null = null;
  private currentImage: HTMLImageElement | null = null;
  private loadError: string | null = null;

  public initialize(canvas: HTMLCanvasElement): void {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
  }

  public setGarment(garment: GarmentMetadata): void {
    if (this.currentAssetUrl === garment.assetUrl && this.currentImage) {
      return;
    }

    this.currentAssetUrl = garment.assetUrl;
    this.loadError = null;

    // Check synchronous cache first
    const cached = GarmentAssetCache.getSync(garment.assetUrl);
    if (cached) {
      this.currentImage = cached;
      return;
    }

    // Load asynchronously and cache
    GarmentAssetCache.loadAsset(garment.assetUrl)
      .then((img) => {
        if (this.currentAssetUrl === garment.assetUrl) {
          this.currentImage = img;
        }
      })
      .catch((err) => {
        this.loadError = err?.message || 'Failed to load garment image';
        this.currentImage = null;
      });
  }

  public render(transform: ComputedTransform, garment: GarmentMetadata): void {
    if (!this.canvas || !this.ctx) return;

    const width = this.canvas.clientWidth;
    const height = this.canvas.clientHeight;
    if (this.canvas.width !== width || this.canvas.height !== height) {
      this.canvas.width = width;
      this.canvas.height = height;
    }

    this.ctx.clearRect(0, 0, width, height);

    if (transform.opacity <= 0.01 || !transform.width || !this.currentImage) {
      return;
    }

    const { ctx } = this;
    ctx.save();

    // 1. Move to garment anchor center (mid-shoulder with collar offset)
    ctx.translate(transform.centerX, transform.centerY);

    // 2. Rotate with shoulder tilt
    ctx.rotate(transform.rotationRad);

    // 3. Set confidence-weighted opacity
    ctx.globalAlpha = Math.max(0, Math.min(1, transform.opacity));

    // 4. Align based on anchor config (e.g. anchorX: 0.5, anchorY: 0.28)
    const drawX = -transform.width * garment.anchorConfig.anchorX;
    const drawY = -transform.height * garment.anchorConfig.anchorY;

    // 5. Draw cached garment image
    try {
      ctx.drawImage(this.currentImage, drawX, drawY, transform.width, transform.height);
    } catch (e) {
      // Silently guard against unexpected canvas draw errors
    }

    ctx.restore();
  }

  public clear(): void {
    if (this.canvas && this.ctx) {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
  }

  public getLoadError(): string | null {
    return this.loadError;
  }
}
