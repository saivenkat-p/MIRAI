"""
Product & Catalog API routes for MIRAI backend.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from ..schemas.product import ProductCategory, Product, InventoryStatus
from ..data.demo_store import (
    get_demo_categories,
    get_demo_products,
    get_demo_product_by_id,
    get_demo_inventory
)

router = APIRouter(prefix="/v1", tags=["Products & Catalog"])


@router.get("/categories", response_model=List[ProductCategory])
def list_categories():
    """List all garment categories available for virtual try-on."""
    return get_demo_categories()


@router.get("/products", response_model=List[Product])
def list_products(
    category_id: Optional[str] = Query(None, description="Filter products by category ID"),
    in_stock_only: bool = Query(False, description="Filter only in-stock items")
):
    """Retrieve catalog products, optionally filtered by category."""
    products = get_demo_products(category_id=category_id)
    if in_stock_only:
        products = [p for p in products if p.in_stock]
    return products


@router.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    """Retrieve detailed product information by ID or SKU."""
    product = get_demo_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/inventory/{product_id}", response_model=InventoryStatus)
def get_inventory(product_id: str):
    """Retrieve real-time in-store inventory and physical rack location."""
    return get_demo_inventory(product_id)
