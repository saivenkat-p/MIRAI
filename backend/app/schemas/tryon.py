"""
Pydantic schemas for the Virtual Try-On API.
"""
import time
from typing import Literal, Optional
from pydantic import BaseModel, Field


class TryOnRequest(BaseModel):
    """
    POST /api/v1/try-on request body.

    person_image_b64: Base-64 encoded JPEG captured from the customer's camera.
    product_id:       The product ID or SKU to try on.
    session_id:       Optional session identifier for analytics.
    """
    person_image_b64: str = Field(
        ...,
        description="Base-64 encoded JPEG of the customer, captured from webcam."
    )
    product_id: str = Field(
        ...,
        description="Product ID or SKU to be tried on."
    )
    session_id: Optional[str] = Field(
        None,
        description="Optional customer session ID for analytics tracking."
    )


class TryOnResponse(BaseModel):
    """
    POST /api/v1/try-on response body.

    result_image_b64: Base-64 encoded PNG of the try-on result.
    product_id:       Echo of the product ID that was tried on.
    mode:             'demo' (Pillow composite) or 'ai' (real VTO provider).
    processing_time_ms: Server-side processing duration.
    """
    result_image_b64: str = Field(
        ...,
        description="Base-64 encoded PNG of the try-on result image."
    )
    product_id: str = Field(
        ...,
        description="The product ID that was processed."
    )
    mode: Literal["demo", "ai"] = Field(
        ...,
        description="'demo' = Pillow composite (NOT real AI). 'ai' = real VTO provider."
    )
    processing_time_ms: int = Field(
        ...,
        description="Server-side processing time in milliseconds."
    )
