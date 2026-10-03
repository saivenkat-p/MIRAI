/**
 * useProducts — fetches the product catalog and category list from the backend.
 *
 * Usage:
 *   const { categories, products, loading, error, selectCategory } = useProducts();
 */

import { useCallback, useEffect, useState } from 'react';
import type { Product, ProductCategory } from '../types/api';
import { fetchCategories, fetchProducts } from '../services/api';

export interface UseProductsReturn {
  categories: ProductCategory[];
  products: Product[];
  activeCategoryId: string | null;
  loading: boolean;
  error: string | null;
  selectCategory: (id: string | null) => void;
  retry: () => void;
}

export function useProducts(): UseProductsReturn {
  const [categories, setCategories] = useState<ProductCategory[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [activeCategoryId, setActiveCategoryId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchCategories()
      .then((cats) => {
        const sorted = [...cats].sort((a, b) => a.display_order - b.display_order);
        setCategories(sorted);
        const targetCatId = activeCategoryId || (sorted.length > 0 ? sorted[0].id : undefined);
        if (targetCatId && !activeCategoryId) {
          setActiveCategoryId(targetCatId);
        }
        return fetchProducts(targetCatId);
      })
      .then((prods) => {
        setProducts(prods);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message ?? 'Failed to load categories.');
        setLoading(false);
      });
  }, [activeCategoryId]);

  // Load categories and products once on mount
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Load products when active category changes
  useEffect(() => {
    if (!activeCategoryId) return;
    let cancelled = false;
    setLoading(true);
    fetchProducts(activeCategoryId)
      .then((prods) => {
        if (cancelled) return;
        setProducts(prods);
        setLoading(false);
      })
      .catch((err: Error) => {
        if (cancelled) return;
        setError(err.message ?? 'Failed to load products.');
        setLoading(false);
      });
    return () => { cancelled = true; };
  }, [activeCategoryId]);

  const selectCategory = useCallback((id: string | null) => {
    setActiveCategoryId(id);
  }, []);

  return { categories, products, activeCategoryId, loading, error, selectCategory, retry: loadData };
}
