import { useState, useEffect, useCallback } from 'react';
import { Product, ProductCategory } from '../types/api';

const API_BASE = 'http://localhost:8000/api/v1';

export interface UseCatalogResult {
  categories: ProductCategory[];
  products: Product[];
  selectedCategory: string | null;
  selectedProduct: Product | null;
  isLoading: boolean;
  error: string | null;
  setSelectedCategory: (catId: string | null) => void;
  setSelectedProduct: (prod: Product | null) => void;
  refreshCatalog: () => Promise<void>;
}

export function useCatalog(): UseCatalogResult {
  const [categories, setCategories] = useState<ProductCategory[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCategories = async () => {
    const res = await fetch(`${API_BASE}/categories`);
    if (!res.ok) throw new Error(`Failed to fetch categories: ${res.statusText}`);
    return (await res.json()) as ProductCategory[];
  };

  const fetchProducts = async (catId: string | null) => {
    const url = catId
      ? `${API_BASE}/products?category_id=${encodeURIComponent(catId)}`
      : `${API_BASE}/products`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to fetch products: ${res.statusText}`);
    return (await res.json()) as Product[];
  };

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [cats, prods] = await Promise.all([
        fetchCategories(),
        fetchProducts(selectedCategory)
      ]);
      setCategories(cats);
      setProducts(prods);
      if (prods.length > 0 && !selectedProduct) {
        setSelectedProduct(prods[0]);
      }
    } catch (err: any) {
      setError(err?.message || 'Unable to connect to MIRAI backend catalog service.');
    } finally {
      setIsLoading(false);
    }
  }, [selectedCategory]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return {
    categories,
    products,
    selectedCategory,
    selectedProduct,
    isLoading,
    error,
    setSelectedCategory,
    setSelectedProduct,
    refreshCatalog: loadData
  };
}
