"""
Pydantic schemas for Sessions, Saved Looks, Retail Coupons, Rewards, and Analytics.
Strictly mirrors /docs/API_CONTRACT.md and enterprise retail store standards.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    mirror_id: str
    client_timestamp: int


class SessionResponse(BaseModel):
    session_id: str
    mirror_id: str
    status: str
    created_at: str
    ended_at: Optional[str] = None
    event_count: int = 0


class SaveLookRequest(BaseModel):
    session_id: str
    product_ids: List[str]
    look_name: str


class SaveLookResponse(BaseModel):
    look_id: str
    session_id: str
    product_ids: List[str]
    look_name: str
    qr_url: str
    shareable_code: str
    qr_data_uri: Optional[str] = None
    created_at: str


class AnalyticsEventRequest(BaseModel):
    session_id: str
    event_type: str
    product_id: Optional[str] = None
    dwell_time_seconds: Optional[int] = None
    timestamp: int
    metadata: Optional[Dict[str, Any]] = None


class CouponResponse(BaseModel):
    code: str
    title: str
    discount_type: str  # 'percentage' | 'fixed'
    discount_value: float
    min_purchase: float
    description: str
    expires_at: str
    is_active: bool


class RewardResponse(BaseModel):
    tier: str
    points: int
    reward_name: str
    benefit: str
    unlocked: bool


class AnalyticsSummaryResponse(BaseModel):
    total_sessions: int
    active_sessions: int
    total_tryons: int
    total_looks_saved: int
    average_session_seconds: float
    popular_products: List[Dict[str, Any]]
    recent_events_count: int
