"""
Unit & Integration tests for MIRAI Retail Features:
- Saved Looks with QR generation
- Promotional Coupons
- Store Loyalty Rewards
- Session Lifecycle & Analytics Summary
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_session_lifecycle():
    # 1. Create Session
    create_res = client.post("/api/v1/sessions", json={
        "mirror_id": "MIRAI-DEV-01",
        "client_timestamp": 1700000000000
    })
    assert create_res.status_code == 200
    data = create_res.json()
    assert "sess_" in data["session_id"]
    assert data["status"] == "active"
    sess_id = data["session_id"]

    # 2. Get Session
    get_res = client.get(f"/api/v1/sessions/{sess_id}")
    assert get_res.status_code == 200
    assert get_res.json()["session_id"] == sess_id

    # 3. End Session
    end_res = client.post(f"/api/v1/sessions/{sess_id}/end")
    assert end_res.status_code == 200
    assert end_res.json()["status"] == "ended"


def test_saved_look_and_qr():
    # 1. Save Look
    res = client.post("/api/v1/saved-looks", json={
        "session_id": "sess_test123",
        "product_ids": ["oct_sht_002"],
        "look_name": "Summer Linen Fit"
    })
    assert res.status_code == 200
    data = res.json()
    assert "look_" in data["look_id"]
    assert "data:image/png;base64," in data["qr_data_uri"]
    assert "https://mirai.octacept.com" in data["qr_url"]
    look_id = data["look_id"]

    # 2. Get Saved Look
    get_res = client.get(f"/api/v1/saved-looks/{look_id}")
    assert get_res.status_code == 200
    assert get_res.json()["look_name"] == "Summer Linen Fit"

    # 3. Stream QR Image
    qr_res = client.get(f"/api/v1/saved-looks/{look_id}/qr")
    assert qr_res.status_code == 200
    assert qr_res.headers["content-type"] == "image/png"
    assert len(qr_res.content) > 100


def test_coupons_and_rewards():
    # 1. Coupons
    c_res = client.get("/api/v1/coupons")
    assert c_res.status_code == 200
    coupons = c_res.json()
    assert len(coupons) >= 3
    codes = [c["code"] for c in coupons]
    assert "MIRAI20" in codes

    # 2. Rewards
    r_res = client.get("/api/v1/rewards")
    assert r_res.status_code == 200
    rewards = r_res.json()
    assert len(rewards) >= 2


def test_analytics_summary():
    # Record an event
    client.post("/api/v1/analytics/events", json={
        "session_id": "sess_test123",
        "event_type": "garment_selected",
        "product_id": "oct_sht_002",
        "dwell_time_seconds": 45,
        "timestamp": 1700000005000
    })

    # Summary
    res = client.get("/api/v1/analytics/summary")
    assert res.status_code == 200
    summary = res.json()
    assert summary["total_sessions"] >= 1
    assert "popular_products" in summary
