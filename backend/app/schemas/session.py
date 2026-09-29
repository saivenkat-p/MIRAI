"""
Pydantic schemas for Sessions, Saved Looks, and Analytics.
Strictly mirrors /docs/API_CONTRACT.md.
"""
from typing import List, Optional
from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    mirror_id: str
    client_timestamp: int


class SessionResponse(BaseModel):
    session_id: str
    mirror_id: str
    status: str
    created_at: str


class SaveLookRequest(BaseModel):
    session_id: str
    product_ids: List[str]
    look_name: str


class SaveLookResponse(BaseModel):
    look_id: str
    qr_url: str
    shareable_code: str


class AnalyticsEventRequest(BaseModel):
    session_id: str
    event_type: str
    product_id: Optional[str] = None
    dwell_time_seconds: Optional[int] = None
    timestamp: int
