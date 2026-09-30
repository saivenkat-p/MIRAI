/**
 * MIRAI API Client — typed fetch wrappers for all backend endpoints.
 * Uses VITE_API_BASE_URL from env (defaults to http://127.0.0.1:8000).
 */

import type {
  Product,
  ProductCategory,
  TryOnRequest,
  TryOnResponse,
} from '../types/api';

const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://127.0.0.1:8000';

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body?.detail ?? `API error ${res.status}`);
  }
  return res.json() as Promise<T>;
}

/** Fetch all product categories. */
export async function fetchCategories(): Promise<ProductCategory[]> {
  return apiFetch<ProductCategory[]>('/api/v1/categories');
}

/** Fetch products, optionally filtered by category ID. */
export async function fetchProducts(categoryId?: string): Promise<Product[]> {
  const qs = categoryId ? `?category_id=${encodeURIComponent(categoryId)}` : '';
  return apiFetch<Product[]>(`/api/v1/products${qs}`);
}

/**
 * POST /api/v1/try-on
 *
 * Sends the captured person image (base-64 JPEG) and the selected product ID
 * to the backend VirtualTryOnService.
 *
 * Returns TryOnResponse with result_image_b64 (PNG) and mode ('demo' | 'ai').
 * The caller should display mode prominently — 'demo' is NOT real AI VTO.
 */
export async function postTryOn(payload: TryOnRequest): Promise<TryOnResponse> {
  return apiFetch<TryOnResponse>('/api/v1/try-on', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
