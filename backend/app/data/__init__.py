"""
Data and seed module for backend catalog.
"""
from .demo_store import (
    get_demo_categories,
    get_demo_products,
    get_demo_product_by_id,
    get_demo_inventory
)

__all__ = [
    "get_demo_categories",
    "get_demo_products",
    "get_demo_product_by_id",
    "get_demo_inventory"
]
