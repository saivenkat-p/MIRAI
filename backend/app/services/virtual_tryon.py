"""
MIRAI — Virtual Try-On Service Layer.

Architecture:
    Frontend → FastAPI → VirtualTryOnService → DemoVirtualTryOnService | RealVTOProvider → result

VirtualTryOnService is the abstract interface.
DemoVirtualTryOnService is the current implementation — it uses Pillow to produce
a clearly labeled DEMO composite. It is NOT a real AI virtual try-on.

To integrate a real VTO provider (e.g. Fashn.ai, IDM-VTON via Replicate):
  1. Create a class that inherits VirtualTryOnService and implements try_on().
  2. Set MIRAI_VTO_PROVIDER=real in .env
  3. Update get_try_on_service() to return it.
  Zero frontend changes required.
"""

import abc
import base64
import io
import os
import time
from typing import Optional

from ..schemas.product import Product


# ---------------------------------------------------------------------------
# Abstract interface — the contract every VTO provider must satisfy
# ---------------------------------------------------------------------------

class VirtualTryOnService(abc.ABC):
    """Abstract base class for all virtual try-on service providers."""

    @abc.abstractmethod
    def try_on(
        self,
        person_image_b64: str,
        product: Product,
    ) -> str:
        """
        Perform virtual try-on.

        Args:
            person_image_b64: Base-64 encoded JPEG of the customer captured from camera.
            product:          The selected Product object (used for color, name, category).

        Returns:
            Base-64 encoded PNG of the result image.
        """

    @property
    @abc.abstractmethod
    def mode(self) -> str:
        """Return 'demo' or 'ai' to identify the provider in the API response."""


# ---------------------------------------------------------------------------
# Demo implementation — Pillow composite. CLEARLY LABELED DEMO.
# This is NOT real AI virtual try-on. It composites the person photo with
# a garment color panel to demonstrate the full pipeline works end-to-end.
# ---------------------------------------------------------------------------

class DemoVirtualTryOnService(VirtualTryOnService):
    """
    DEMO VTO using Pillow image compositing.

    ⚠️  NOT real AI virtual try-on.
    The result shows the person photo with a garment-colored shape composited
    on the upper body, with a DEMO watermark. Used only to verify the full
    pipeline: camera → FastAPI → service → result → frontend.

    Replace with a real provider (Fashn.ai, IDM-VTON, etc.) without changing
    any frontend or API code.
    """

    @property
    def mode(self) -> str:
        return "demo"

    def try_on(self, person_image_b64: str, product: Product) -> str:
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError as e:
            raise RuntimeError(
                "Pillow is not installed. Run: pip install Pillow>=10.0.0"
            ) from e

        # ── Decode person image ──────────────────────────────────────────
        person_bytes = base64.b64decode(person_image_b64)
        person_img = Image.open(io.BytesIO(person_bytes)).convert("RGBA")

        # Standardize canvas size (portrait)
        TARGET_W, TARGET_H = 480, 640
        person_img = person_img.resize((TARGET_W, TARGET_H), Image.LANCZOS)

        # ── Prepare composite layer ──────────────────────────────────────
        # Convert product hex color → RGBA
        hex_color = product.colors[0].hex if product.colors else "#333333"
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        garment_rgba = (r, g, b, 190)   # semi-transparent overlay

        # Build garment shape based on category
        overlay = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        cat = product.category_id.lower()
        if cat in ("jackets", "hoodies", "shirts"):
            # Upper-body trapezoid (shoulders → waist)
            shape = [
                (TARGET_W * 0.10, TARGET_H * 0.22),   # left shoulder
                (TARGET_W * 0.90, TARGET_H * 0.22),   # right shoulder
                (TARGET_W * 0.85, TARGET_H * 0.58),   # right waist
                (TARGET_W * 0.15, TARGET_H * 0.58),   # left waist
            ]
        elif cat == "trousers":
            # Lower-body rectangle (hips → ankles)
            shape = [
                (TARGET_W * 0.20, TARGET_H * 0.52),
                (TARGET_W * 0.80, TARGET_H * 0.52),
                (TARGET_W * 0.80, TARGET_H * 0.97),
                (TARGET_W * 0.20, TARGET_H * 0.97),
            ]
        else:
            # Dresses / skirts — full body
            shape = [
                (TARGET_W * 0.15, TARGET_H * 0.22),
                (TARGET_W * 0.85, TARGET_H * 0.22),
                (TARGET_W * 0.90, TARGET_H * 0.97),
                (TARGET_W * 0.10, TARGET_H * 0.97),
            ]

        draw.polygon(shape, fill=garment_rgba)

        # Subtle border on the garment shape
        draw.polygon(shape, outline=(255, 255, 255, 120))

        # ── Composite onto person ────────────────────────────────────────
        composite = Image.alpha_composite(person_img, overlay)
        result = composite.convert("RGB")
        result_draw = ImageDraw.Draw(result)

        # ── DEMO badge (top-right corner) ────────────────────────────────
        badge_x, badge_y = TARGET_W - 10, 10
        badge_w, badge_h = 90, 28
        result_draw.rectangle(
            [badge_x - badge_w, badge_y, badge_x, badge_y + badge_h],
            fill=(220, 50, 50),
        )
        result_draw.text(
            (badge_x - badge_w + 10, badge_y + 6),
            "⚡ DEMO",
            fill=(255, 255, 255),
        )

        # ── Product label (bottom) ────────────────────────────────────────
        label_bg_y = TARGET_H - 50
        result_draw.rectangle(
            [0, label_bg_y, TARGET_W, TARGET_H],
            fill=(0, 0, 0, 200),
        )
        result_draw.text(
            (12, label_bg_y + 8),
            f"{product.name}",
            fill=(255, 255, 255),
        )
        result_draw.text(
            (12, label_bg_y + 28),
            f"₹{int(product.price):,}  •  {product.brand}",
            fill=(160, 160, 160),
        )

        # ── Encode result ────────────────────────────────────────────────
        buf = io.BytesIO()
        result.save(buf, format="PNG", optimize=True)
        return base64.b64encode(buf.getvalue()).decode("utf-8")


# ---------------------------------------------------------------------------
# Factory — returns the configured service
# ---------------------------------------------------------------------------

_PROVIDER_ENV_KEY = "MIRAI_VTO_PROVIDER"

def get_try_on_service() -> VirtualTryOnService:
    """
    Return the configured VirtualTryOnService.

    Set MIRAI_VTO_PROVIDER=real in .env to use a real AI provider.
    Defaults to DemoVirtualTryOnService (Pillow composite, NOT real AI).
    """
    provider = os.getenv(_PROVIDER_ENV_KEY, "demo").lower()
    if provider == "demo":
        return DemoVirtualTryOnService()
    # Future: load real provider here
    # elif provider == "fashn":
    #     return FashnVirtualTryOnService(api_key=os.environ["FASHN_API_KEY"])
    raise ValueError(
        f"Unknown MIRAI_VTO_PROVIDER '{provider}'. "
        "Supported: 'demo'. Set MIRAI_VTO_PROVIDER=demo in .env."
    )
