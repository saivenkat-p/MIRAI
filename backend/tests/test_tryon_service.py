"""
Tests for the Virtual Try-On service and API endpoint.
"""
import base64
import io
import unittest
from unittest.mock import patch

from backend.app.services.virtual_tryon import (
    DemoVirtualTryOnService,
    get_try_on_service,
)
from backend.app.data.demo_store import get_demo_product_by_id, get_demo_products


def _make_small_jpeg_b64() -> str:
    """Create a minimal 10x10 white JPEG in base-64 for testing."""
    from PIL import Image
    img = Image.new("RGB", (10, 10), color=(200, 200, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


class TestDemoVirtualTryOnService(unittest.TestCase):

    def setUp(self):
        self.svc = DemoVirtualTryOnService()
        self.sample_product = get_demo_products()[0]  # Cyber Techwear Bomber
        self.person_b64 = _make_small_jpeg_b64()

    def test_mode_is_demo(self):
        self.assertEqual(self.svc.mode, "demo")

    def test_try_on_returns_base64_string(self):
        result = self.svc.try_on(self.person_b64, self.sample_product)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_try_on_result_is_valid_png(self):
        result = self.svc.try_on(self.person_b64, self.sample_product)
        png_bytes = base64.b64decode(result)
        # PNG magic bytes: \x89PNG
        self.assertTrue(png_bytes[:4] == b'\x89PNG', "Result must be a PNG image")

    def test_try_on_different_categories(self):
        """Verify every garment category produces a result."""
        categories = ["jackets", "hoodies", "shirts", "trousers", "dresses"]
        for cat in categories:
            products = get_demo_products(category_id=cat)
            if products:
                result = self.svc.try_on(self.person_b64, products[0])
                self.assertIsInstance(result, str, f"No result for category: {cat}")

    def test_product_a_never_sends_product_b(self):
        """
        Verify that calling try_on with product A and product B produces
        different results — the product is actually used.
        """
        products = get_demo_products()
        prod_a = products[0]  # Cyber Techwear Bomber (black)
        prod_b = products[3]  # Vintage Distressed Denim Jacket (blue)

        result_a = self.svc.try_on(self.person_b64, prod_a)
        result_b = self.svc.try_on(self.person_b64, prod_b)
        # Different colors → different output bytes
        self.assertNotEqual(result_a, result_b,
            "Product A and Product B must produce different results")


class TestGetTryOnServiceFactory(unittest.TestCase):

    def test_default_returns_demo_service(self):
        svc = get_try_on_service()
        self.assertIsInstance(svc, DemoVirtualTryOnService)

    def test_env_demo_returns_demo_service(self):
        with patch.dict("os.environ", {"MIRAI_VTO_PROVIDER": "demo"}):
            svc = get_try_on_service()
            self.assertIsInstance(svc, DemoVirtualTryOnService)

    def test_unknown_provider_raises(self):
        with patch.dict("os.environ", {"MIRAI_VTO_PROVIDER": "nonexistent_ai"}):
            with self.assertRaises(ValueError):
                get_try_on_service()


class TestDemoStoreINRPrices(unittest.TestCase):

    def test_all_products_have_inr_currency(self):
        products = get_demo_products()
        for p in products:
            self.assertEqual(p.currency, "INR",
                f"{p.name} has currency '{p.currency}', expected 'INR'")

    def test_prices_are_reasonable_inr(self):
        products = get_demo_products()
        for p in products:
            # INR prices should be > 100 and < 20000 for clothing
            self.assertGreater(p.price, 100,
                f"{p.name} price ₹{p.price} is too low")
            self.assertLess(p.price, 20000,
                f"{p.name} price ₹{p.price} is unrealistically high")


if __name__ == "__main__":
    unittest.main()
