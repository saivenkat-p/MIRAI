"""
Demo Store seed data and query interface.
Provides 30+ demo garments across 5 categories for investor & retail store demonstration.
"""
from typing import List, Optional
from ..schemas.product import ProductCategory, Product, ProductColor, InventoryStatus

DEMO_CATEGORIES: List[ProductCategory] = [
    ProductCategory(id="jackets", name="Jackets & Outerwear", display_order=1, icon="jacket"),
    ProductCategory(id="hoodies", name="Hoodies & Sweatshirts", display_order=2, icon="hoodie"),
    ProductCategory(id="shirts", name="Shirts & Tops", display_order=3, icon="shirt"),
    ProductCategory(id="trousers", name="Pants & Trousers", display_order=4, icon="pants"),
    ProductCategory(id="dresses", name="Dresses & Skirts", display_order=5, icon="dress"),
]

def _generate_demo_products() -> List[Product]:
    products = []
    
    # 1. Jackets & Outerwear (7 items)
    jacket_names = [
        ("Cyber Techwear Bomber", 149.99, "OCT-JKT-001", "#111111", "Matte Black"),
        ("Minimalist Wool Overcoat", 219.00, "OCT-JKT-002", "#e5e5e5", "Oatmeal"),
        ("Urban Utility Windbreaker", 119.50, "OCT-JKT-003", "#2f4f4f", "Dark Slate"),
        ("Vintage Distressed Denim Jacket", 95.00, "OCT-JKT-004", "#4682b4", "Washed Indigo"),
        ("Structured Leather Moto Jacket", 280.00, "OCT-JKT-005", "#1c1c1c", "Midnight Black"),
        ("Puffer Thermore Vest", 89.99, "OCT-JKT-006", "#d2b48c", "Desert Sand"),
        ("Sartorial Peak-Lapel Blazer", 175.00, "OCT-JKT-007", "#000080", "Navy Blue"),
    ]
    for name, price, sku, hex_c, col_name in jacket_names:
        products.append(Product(
            id=sku.lower().replace("-", "_"),
            sku=sku,
            name=name,
            category_id="jackets",
            brand="OCTACEPT Atelier",
            price=price,
            description=f"Premium {name.lower()} crafted for physical trial and smart AR fitting.",
            colors=[ProductColor(name=col_name, hex=hex_c)],
            sizes=["S", "M", "L", "XL"],
            asset_2d_overlay=f"/assets/garments/{sku.lower()}_overlay.png",
            asset_thumbnail=f"/assets/thumbnails/{sku.lower()}_thumb.png",
            in_stock=True
        ))

    # 2. Hoodies & Sweatshirts (6 items)
    hoodie_names = [
        ("Heavyweight French Terry Hoodie", 85.00, "OCT-HOD-001", "#808080", "Heather Grey"),
        ("Oversized Boxy Graphic Hoodie", 92.00, "OCT-HOD-002", "#000000", "Obsidian"),
        ("Acid Wash Vintage Crewneck", 78.00, "OCT-HOD-003", "#708090", "Slate Wash"),
        ("Cashmere-Blend Zip Hoodie", 145.00, "OCT-HOD-004", "#f5f5dc", "Cream Beige"),
        ("Reflective Pipeline Pullover", 99.00, "OCT-HOD-005", "#ff4500", "Signal Neon"),
        ("Thermal Knit Quarter-Zip", 88.00, "OCT-HOD-006", "#2e8b57", "Forest Green"),
    ]
    for name, price, sku, hex_c, col_name in hoodie_names:
        products.append(Product(
            id=sku.lower().replace("-", "_"),
            sku=sku,
            name=name,
            category_id="hoodies",
            brand="OCTACEPT Originals",
            price=price,
            description=f"Signature {name.lower()} engineered with tailored silhouette tracking.",
            colors=[ProductColor(name=col_name, hex=hex_c)],
            sizes=["XS", "S", "M", "L", "XL"],
            asset_2d_overlay=f"/assets/garments/{sku.lower()}_overlay.png",
            asset_thumbnail=f"/assets/thumbnails/{sku.lower()}_thumb.png",
            in_stock=True
        ))

    # 3. Shirts & Tops (7 items)
    shirt_names = [
        ("Oxford Mercerized Cotton Shirt", 68.00, "OCT-SHT-001", "#ffffff", "Crisp White"),
        ("Relaxed Camp-Collar Linen Shirt", 74.00, "OCT-SHT-002", "#deb887", "Natural Flax"),
        ("Cuban Collar Silk-Touch Shirt", 89.00, "OCT-SHT-003", "#800020", "Deep Merlot"),
        ("Supima Drop-Shoulder Heavy Tee", 45.00, "OCT-SHT-004", "#000000", "Pitch Black"),
        ("Tailored Poplin Mandarin Shirt", 72.00, "OCT-SHT-005", "#87ceeb", "Sky Azure"),
        ("Waffle Thermal Longsleeve", 52.00, "OCT-SHT-006", "#696969", "Dim Ash"),
        ("Striped Breton Knit Top", 58.00, "OCT-SHT-007", "#00008b", "Dark Marine"),
    ]
    for name, price, sku, hex_c, col_name in shirt_names:
        products.append(Product(
            id=sku.lower().replace("-", "_"),
            sku=sku,
            name=name,
            category_id="shirts",
            brand="OCTACEPT Essentials",
            price=price,
            description=f"Essential {name.lower()} offering breathable luxury.",
            colors=[ProductColor(name=col_name, hex=hex_c)],
            sizes=["S", "M", "L", "XL"],
            asset_2d_overlay=f"/assets/garments/{sku.lower()}_overlay.png",
            asset_thumbnail=f"/assets/thumbnails/{sku.lower()}_thumb.png",
            in_stock=True
        ))

    # 4. Pants & Trousers (6 items)
    trouser_names = [
        ("Pleated Wide-Leg Wool Trousers", 130.00, "OCT-TRS-001", "#36454f", "Charcoal"),
        ("Technical Cargo Tapered Pants", 110.00, "OCT-TRS-002", "#556b2f", "Olive Drab"),
        ("Relaxed Drawstring Linen Pants", 85.00, "OCT-TRS-003", "#fdf5e6", "Ecru"),
        ("Selvedge Japanese Denim Jeans", 165.00, "OCT-TRS-004", "#191970", "Raw Indigo"),
        ("Cropped Tailored Chinos", 79.00, "OCT-TRS-005", "#c2b280", "Khaki Sand"),
        ("Athletic Comfort Track Trousers", 75.00, "OCT-TRS-006", "#000000", "Solid Black"),
    ]
    for name, price, sku, hex_c, col_name in trouser_names:
        products.append(Product(
            id=sku.lower().replace("-", "_"),
            sku=sku,
            name=name,
            category_id="trousers",
            brand="OCTACEPT Atelier",
            price=price,
            description=f"Contemporary {name.lower()} with precision drape.",
            colors=[ProductColor(name=col_name, hex=hex_c)],
            sizes=["28", "30", "32", "34", "36"],
            asset_2d_overlay=f"/assets/garments/{sku.lower()}_overlay.png",
            asset_thumbnail=f"/assets/thumbnails/{sku.lower()}_thumb.png",
            in_stock=True
        ))

    # 5. Dresses & Skirts (6 items)
    dress_names = [
        ("Bias-Cut Silk Slip Dress", 175.00, "OCT-DRS-001", "#2e0854", "Royal Violet"),
        ("Pleated Georgette Midi Dress", 155.00, "OCT-DRS-002", "#ffb6c1", "Blush Pink"),
        ("Sculptural Knit Maxi Dress", 140.00, "OCT-DRS-003", "#a0522d", "Sienna Clay"),
        ("Structured A-Line Linen Sundress", 115.00, "OCT-DRS-004", "#ffffe0", "Buttercream"),
        ("Asymmetrical Wrap Dress", 160.00, "OCT-DRS-005", "#008080", "Emerald Teal"),
        ("High-Waisted Knife-Pleat Skirt", 95.00, "OCT-DRS-006", "#778899", "Muted Steel"),
    ]
    for name, price, sku, hex_c, col_name in dress_names:
        products.append(Product(
            id=sku.lower().replace("-", "_"),
            sku=sku,
            name=name,
            category_id="dresses",
            brand="OCTACEPT Atelier",
            price=price,
            description=f"Fluid {name.lower()} modeled for movement simulation.",
            colors=[ProductColor(name=col_name, hex=hex_c)],
            sizes=["XS", "S", "M", "L"],
            asset_2d_overlay=f"/assets/garments/{sku.lower()}_overlay.png",
            asset_thumbnail=f"/assets/thumbnails/{sku.lower()}_thumb.png",
            in_stock=True
        ))

    return products

DEMO_PRODUCTS: List[Product] = _generate_demo_products()

def get_demo_categories() -> List[ProductCategory]:
    return DEMO_CATEGORIES

def get_demo_products(category_id: Optional[str] = None) -> List[Product]:
    if category_id:
        return [p for p in DEMO_PRODUCTS if p.category_id == category_id]
    return DEMO_PRODUCTS

def get_demo_product_by_id(product_id: str) -> Optional[Product]:
    for p in DEMO_PRODUCTS:
        if p.id == product_id or p.sku.lower() == product_id.lower():
            return p
    return None

def get_demo_inventory(product_id: str) -> InventoryStatus:
    prod = get_demo_product_by_id(product_id)
    if not prod:
        return InventoryStatus(
            product_id=product_id,
            total_stock=0,
            size_breakdown={},
            rack_location="Not Found"
        )
    breakdown = {s: 3 for s in prod.sizes}
    return InventoryStatus(
        product_id=product_id,
        total_stock=sum(breakdown.values()),
        size_breakdown=breakdown,
        rack_location=f"Rack {prod.category_id[:3].upper()}-0{len(prod.sizes)}"
    )
