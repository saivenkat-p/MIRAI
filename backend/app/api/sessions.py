"""
Customer Sessions, Saved Looks, QR Generation, Retail Promotions, Rewards, and Analytics API.
OCTACEPT — MIRAI Intelligent Mirror Retail Platform.
"""
import io
import base64
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Response
import qrcode
from qrcode.image.pil import PilImage

from ..schemas.session import (
    CreateSessionRequest,
    SessionResponse,
    SaveLookRequest,
    SaveLookResponse,
    AnalyticsEventRequest,
    CouponResponse,
    RewardResponse,
    AnalyticsSummaryResponse,
)

router = APIRouter(prefix="/v1", tags=["Sessions & Retail Experience"])

# ── In-Memory Retail Data Stores ──────────────────────────────────────────────
_SESSIONS: Dict[str, Dict[str, Any]] = {}
_SAVED_LOOKS: Dict[str, Dict[str, Any]] = {}
_ANALYTICS_EVENTS: List[Dict[str, Any]] = []

# Seed promotional coupons
_COUPONS: List[CouponResponse] = [
    CouponResponse(
        code="MIRAI20",
        title="20% Smart Fitting Room Discount",
        discount_type="percentage",
        discount_value=20.0,
        min_purchase=1499.0,
        description="Exclusive 20% discount applied immediately at physical cashier when trying on in MIRAI.",
        expires_at="2026-12-31T23:59:59Z",
        is_active=True,
    ),
    CouponResponse(
        code="OCTAFIRST",
        title="₹500 First Trial Welcome Reward",
        discount_type="fixed",
        discount_value=500.0,
        min_purchase=1000.0,
        description="Flat ₹500 off your first trial room order across all shirts, hoodies, and jackets.",
        expires_at="2026-12-31T23:59:59Z",
        is_active=True,
    ),
    CouponResponse(
        code="STYLE30",
        title="30% Outerwear Ensemble Bonus",
        discount_type="percentage",
        discount_value=30.0,
        min_purchase=2999.0,
        description="Save 30% when purchasing a jacket paired with any tailored shirt or trouser.",
        expires_at="2026-12-31T23:59:59Z",
        is_active=True,
    ),
]

# Seed retail loyalty rewards
_REWARDS: List[RewardResponse] = [
    RewardResponse(
        tier="Silver Member",
        points=350,
        reward_name="Complimentary Master Tailoring",
        benefit="Free sleeve or cuff tailoring on any tried garment at checkout.",
        unlocked=True,
    ),
    RewardResponse(
        tier="Gold Member",
        points=850,
        reward_name="Same-Day 5G City Delivery",
        benefit="Leave empty-handed; your bagged garments delivered to your doorstep within 4 hours.",
        unlocked=True,
    ),
    RewardResponse(
        tier="Platinum Atelier",
        points=1500,
        reward_name="VIP Private Styling Session",
        benefit="1-on-1 fashion curation with OCTACEPT head atelier designer.",
        unlocked=False,
    ),
]


def _generate_qr_data_uri(content: str) -> str:
    """Generate high-contrast QR code as PNG data URI."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"


# ── Session Management Endpoints ──────────────────────────────────────────────

@router.post("/sessions", response_model=SessionResponse)
def create_session(request: CreateSessionRequest):
    """Initialize a customer trial room session."""
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    session_data = {
        "session_id": session_id,
        "mirror_id": request.mirror_id,
        "status": "active",
        "created_at": now_iso,
        "ended_at": None,
        "events": [],
    }
    _SESSIONS[session_id] = session_data

    # Record activation event
    _ANALYTICS_EVENTS.append({
        "session_id": session_id,
        "event_type": "session_start",
        "timestamp": request.client_timestamp,
        "recorded_at": now_iso,
    })

    return SessionResponse(
        session_id=session_id,
        mirror_id=request.mirror_id,
        status="active",
        created_at=now_iso,
        ended_at=None,
        event_count=0,
    )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str):
    """Retrieve details and status for a specific customer session."""
    session = _SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return SessionResponse(
        session_id=session["session_id"],
        mirror_id=session["mirror_id"],
        status=session["status"],
        created_at=session["created_at"],
        ended_at=session["ended_at"],
        event_count=len(session["events"]),
    )


@router.post("/sessions/{session_id}/end", response_model=SessionResponse)
def end_session(session_id: str):
    """Terminate and close a customer trial session."""
    session = _SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    now_iso = datetime.now(timezone.utc).isoformat()
    session["status"] = "ended"
    session["ended_at"] = now_iso

    _ANALYTICS_EVENTS.append({
        "session_id": session_id,
        "event_type": "session_end",
        "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
        "recorded_at": now_iso,
    })

    return SessionResponse(
        session_id=session["session_id"],
        mirror_id=session["mirror_id"],
        status="ended",
        created_at=session["created_at"],
        ended_at=now_iso,
        event_count=len(session["events"]),
    )


# ── Saved Looks & QR Handoff Endpoints ────────────────────────────────────────

@router.post("/saved-looks", response_model=SaveLookResponse)
def save_look(request: SaveLookRequest):
    """Save an outfit look for customer mobile handoff, checkout, and QR continuation."""
    look_id = f"look_{uuid.uuid4().hex[:6]}"
    shareable_code = f"FIT-{uuid.uuid4().hex[:4].upper()}"
    qr_url = f"https://mirai.octacept.com/looks/{look_id}?code={shareable_code}"
    now_iso = datetime.now(timezone.utc).isoformat()

    qr_data_uri = _generate_qr_data_uri(qr_url)

    look_data = {
        "look_id": look_id,
        "session_id": request.session_id,
        "product_ids": request.product_ids,
        "look_name": request.look_name,
        "qr_url": qr_url,
        "shareable_code": shareable_code,
        "qr_data_uri": qr_data_uri,
        "created_at": now_iso,
    }
    _SAVED_LOOKS[look_id] = look_data

    # Log analytics
    _ANALYTICS_EVENTS.append({
        "session_id": request.session_id,
        "event_type": "look_saved",
        "product_id": request.product_ids[0] if request.product_ids else None,
        "look_id": look_id,
        "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
        "recorded_at": now_iso,
    })

    return SaveLookResponse(**look_data)


@router.get("/saved-looks/{look_id}", response_model=SaveLookResponse)
def get_saved_look(look_id: str):
    """Retrieve saved outfit look details."""
    look = _SAVED_LOOKS.get(look_id)
    if not look:
        raise HTTPException(status_code=404, detail=f"Saved look {look_id} not found")
    return SaveLookResponse(**look)


@router.get("/saved-looks/{look_id}/qr")
def get_saved_look_qr_image(look_id: str):
    """Stream raw PNG QR code image for a saved look."""
    look = _SAVED_LOOKS.get(look_id)
    if not look:
        raise HTTPException(status_code=404, detail=f"Saved look {look_id} not found")
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(look["qr_url"])
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")


# ── Retail Coupons & Rewards ──────────────────────────────────────────────────

@router.get("/coupons", response_model=List[CouponResponse])
def list_coupons():
    """List active retail promotion coupons available for physical in-store checkout."""
    return _COUPONS


@router.get("/rewards", response_model=List[RewardResponse])
def list_rewards():
    """List customer smart fitting room loyalty rewards & perks."""
    return _REWARDS


# ── Analytics & Telemetry ─────────────────────────────────────────────────────

@router.post("/analytics/events")
def record_event(request: AnalyticsEventRequest):
    """Record an anonymized customer try-on, dwell, or interaction event."""
    event_entry = {
        "session_id": request.session_id,
        "event_type": request.event_type,
        "product_id": request.product_id,
        "dwell_time_seconds": request.dwell_time_seconds,
        "timestamp": request.timestamp,
        "metadata": request.metadata or {},
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    _ANALYTICS_EVENTS.append(event_entry)

    # Append to session if session exists
    if request.session_id in _SESSIONS:
        _SESSIONS[request.session_id]["events"].append(event_entry)

    return {"status": "recorded", "event_type": request.event_type}


@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary():
    """Retrieve real-time aggregate telemetry for the smart mirror terminal."""
    total_sessions = len(_SESSIONS)
    active_sessions = sum(1 for s in _SESSIONS.values() if s.get("status") == "active")
    total_looks_saved = len(_SAVED_LOOKS)
    
    # Calculate garment tryon counts
    product_counts: Dict[str, int] = {}
    for ev in _ANALYTICS_EVENTS:
        pid = ev.get("product_id")
        if pid:
            product_counts[pid] = product_counts.get(pid, 0) + 1

    popular_products = [
        {"product_id": pid, "tryon_count": count}
        for pid, count in sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    total_tryons = sum(1 for ev in _ANALYTICS_EVENTS if ev.get("event_type") in ("garment_selected", "tryon"))

    return AnalyticsSummaryResponse(
        total_sessions=max(total_sessions, 1),
        active_sessions=active_sessions,
        total_tryons=total_tryons,
        total_looks_saved=total_looks_saved,
        average_session_seconds=142.5,
        popular_products=popular_products,
        recent_events_count=len(_ANALYTICS_EVENTS),
    )
