"""
Test suite validating Backend API contracts and Demo Store seed data.
"""
import unittest
from backend.app.data.demo_store import (
    get_demo_categories,
    get_demo_products,
    get_demo_product_by_id,
    get_demo_inventory
)
from backend.app.schemas.product import Product, ProductCategory, InventoryStatus


class TestBackendContract(unittest.TestCase):

    def test_demo_categories_seeded(self):
        categories = get_demo_categories()
        self.assertGreaterEqual(len(categories), 5)
        category_ids = [c.id for c in categories]
        self.assertIn("jackets", category_ids)
        self.assertIn("hoodies", category_ids)
        self.assertIn("shirts", category_ids)
        self.assertIn("trousers", category_ids)
        self.assertIn("dresses", category_ids)

    def test_demo_products_count_and_schema(self):
        products = get_demo_products()
        # Prompt requirement: 30+ products for Demo Store
        self.assertGreaterEqual(len(products), 30, f"Expected at least 30 products, got {len(products)}")
        
        # Verify first product integrity
        p = products[0]
        self.assertIsInstance(p, Product)
        self.assertTrue(len(p.id) > 0)
        self.assertTrue(len(p.sku) > 0)
        self.assertGreater(p.price, 0)
        self.assertTrue(p.in_stock)
        self.assertTrue(len(p.sizes) > 0)
        self.assertTrue(len(p.colors) > 0)
        self.assertTrue(p.asset_2d_overlay.startswith("/assets/"))

    def test_product_filter_by_category(self):
        jackets = get_demo_products(category_id="jackets")
        self.assertGreaterEqual(len(jackets), 5)
        for j in jackets:
            self.assertEqual(j.category_id, "jackets")

    def test_inventory_lookup(self):
        products = get_demo_products()
        sample_prod = products[0]
        inv = get_demo_inventory(sample_prod.id)
        self.assertIsInstance(inv, InventoryStatus)
        self.assertEqual(inv.product_id, sample_prod.id)
        self.assertGreater(inv.total_stock, 0)
        self.assertTrue(len(inv.rack_location) > 0)


if __name__ == "__main__":
    unittest.main()
