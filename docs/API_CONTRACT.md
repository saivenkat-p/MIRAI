# MIRAI — Backend API Contract

This document defines the REST API endpoints exposed by the Backend (`/backend/**`) and consumed by the Frontend (`/frontend/**`).

---

## 1. General Specifications
- **Base URL**: `/api/v1`
- **Default Port**: `8000`
- **Format**: JSON (`Content-Type: application/json`)
- **Authentication**: Bearer Token / API Key (Optional for local store prototype, required for admin).

---

## 2. Product & Catalog Endpoints

### 2.1 List Categories
- **Endpoint**: `GET /api/v1/categories`
- **Description**: Returns all garment categories available for display.
- **Response**:
```json
[
  {
    "id": "jackets",
    "name": "Jackets & Outerwear",
    "display_order": 1,
    "icon": "jacket"
  },
  {
    "id": "hoodies",
    "name": "Hoodies & Sweatshirts",
    "display_order": 2,
    "icon": "hoodie"
  },
  {
    "id": "shirts",
    "name": "Shirts & Tops",
    "display_order": 3,
    "icon": "shirt"
  },
  {
    "id": "trousers",
    "name": "Pants & Trousers",
    "display_order": 4,
    "icon": "pants"
  },
  {
    "id": "dresses",
    "name": "Dresses & Skirts",
    "display_order": 5,
    "icon": "dress"
  }
]
```

### 2.2 List Products
- **Endpoint**: `GET /api/v1/products`
- **Query Parameters**:
  - `category_id` (optional, string)
  - `in_stock_only` (optional, boolean, default `false`)
- **Response**:
```json
[
  {
    "id": "prod_001",
    "sku": "OCT-JKT-01",
    "name": "Cyber Techwear Bomber",
    "category_id": "jackets",
    "brand": "OCTACEPT Atelier",
    "price": 129.99,
    "currency": "USD",
    "description": "Weatherproof matte black bomber with reflective accents.",
    "colors": [
      { "name": "Matte Black", "hex": "#1a1a1a" },
      { "name": "Slate Grey", "hex": "#708090" }
    ],
    "sizes": ["S", "M", "L", "XL"],
    "asset_2d_overlay": "/assets/garments/bomber_black.png",
    "asset_thumbnail": "/assets/thumbnails/bomber_black_thumb.png",
    "in_stock": true
  }
]
```

### 2.3 Get Product Details
- **Endpoint**: `GET /api/v1/products/{id}`
- **Response**: Single `Product` object matching schema above.

### 2.4 Inventory Status
- **Endpoint**: `GET /api/v1/inventory/{product_id}`
- **Response**:
```json
{
  "product_id": "prod_001",
  "total_stock": 14,
  "size_breakdown": {
    "S": 3,
    "M": 5,
    "L": 4,
    "XL": 2
  },
  "rack_location": "Rack A-04 (Trial Room Left)"
}
```

---

## 3. Session & Customer Look Endpoints

### 3.1 Create Customer Session
- **Endpoint**: `POST /api/v1/sessions`
- **Request Body**:
```json
{
  "mirror_id": "MIRAI-STORE-01-ROOM-3",
  "client_timestamp": 1727625600000
}
```
- **Response**:
```json
{
  "session_id": "sess_89a12c4f",
  "mirror_id": "MIRAI-STORE-01-ROOM-3",
  "status": "active",
  "created_at": "2026-09-29T15:30:00Z"
}
```

### 3.2 Save Look / Wishlist
- **Endpoint**: `POST /api/v1/saved-looks`
- **Request Body**:
```json
{
  "session_id": "sess_89a12c4f",
  "product_ids": ["prod_001", "prod_004"],
  "look_name": "Autumn Streetwear Fit"
}
```
- **Response**:
```json
{
  "look_id": "look_99e1b",
  "qr_url": "https://mirai.octacept.com/looks/look_99e1b",
  "shareable_code": "FIT-492"
}
```

---

## 4. Analytics Endpoints

### 4.1 Record Event (Privacy-Preserving UI & Try-On Metrics)
- **Endpoint**: `POST /api/v1/analytics/events`
- **Request Body**:
```json
{
  "session_id": "sess_89a12c4f",
  "event_type": "garment_try_on",
  "product_id": "prod_001",
  "dwell_time_seconds": 24,
  "timestamp": 1727625624000
}
```
- **Response**:
```json
{ "status": "recorded" }
```
