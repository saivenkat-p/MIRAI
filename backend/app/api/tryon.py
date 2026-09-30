"""
Virtual Try-On API route for MIRAI backend.

POST /api/v1/try-on

Accepts a base-64 encoded customer photo and a product ID.
Returns a base-64 encoded result image produced by VirtualTryOnService.

Current mode: DEMO (Pillow composite — NOT real AI virtual try-on).
"""
import time
from fastapi import APIRouter, HTTPException, status

from ..schemas.tryon import TryOnRequest, TryOnResponse
from ..data.demo_store import get_demo_product_by_id
from ..services.virtual_tryon import get_try_on_service

router = APIRouter(prefix="/v1", tags=["Virtual Try-On"])


@router.post(
    "/try-on",
    response_model=TryOnResponse,
    summary="Virtual Try-On",
    description=(
        "Submit a customer photo (base-64 JPEG) and a product ID. "
        "Returns a result image (base-64 PNG) showing the try-on output. "
        "Current mode: DEMO — produced by DemoVirtualTryOnService (Pillow composite), "
        "NOT real AI virtual try-on."
    ),
)
def try_on(request: TryOnRequest) -> TryOnResponse:
    """
    POST /api/v1/try-on

    Errors returned (never exposes raw Python tracebacks to the frontend):
        400 — missing or empty person image / product_id
        404 — product not found in catalog
        422 — base-64 decode failure (corrupted image)
        503 — VTO service failure (Pillow error, etc.)
    """
    # ── Validate inputs ──────────────────────────────────────────────────
    if not request.person_image_b64 or not request.person_image_b64.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="person_image_b64 is required and cannot be empty.",
        )

    if not request.product_id or not request.product_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="product_id is required and cannot be empty.",
        )

    # ── Lookup product ───────────────────────────────────────────────────
    product = get_demo_product_by_id(request.product_id.strip())
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{request.product_id}' not found in catalog.",
        )

    if not product.in_stock:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product '{product.name}' is currently out of stock.",
        )

    # ── Validate base-64 image ───────────────────────────────────────────
    import base64 as b64_module
    try:
        # Strip data-URI prefix if the frontend sends it (data:image/jpeg;base64,...)
        image_data = request.person_image_b64
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]
        b64_module.b64decode(image_data, validate=True)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="person_image_b64 is not valid base-64 data.",
        )

    # ── Run virtual try-on ───────────────────────────────────────────────
    t_start = time.monotonic()
    try:
        service = get_try_on_service()
        result_b64 = service.try_on(image_data, product)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Try-on service error: {exc}",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to create your look right now. Please try again.",
        )

    processing_ms = int((time.monotonic() - t_start) * 1000)

    return TryOnResponse(
        result_image_b64=result_b64,
        product_id=product.id,
        mode=service.mode,
        processing_time_ms=processing_ms,
    )
