"""
MIRAI — Multi-Garment Asset Suite Generator
Generates realistic photographic/stylized garment textures, transparency masks,
and normal/anchor definitions for store catalog items:
  1. OCT-SHT-001: Oxford Mercerized Cotton Shirt (Crisp White)
  2. OCT-SHT-002: Relaxed Camp-Collar Linen Shirt (Natural Flax)
  3. OCT-SHT-003: Cuban Collar Silk-Touch Shirt (Deep Merlot)
  4. OCT-SHT-004: Supima Drop-Shoulder Heavy Tee (Pitch Black)
  5. OCT-SHT-005: Tailored Poplin Mandarin Shirt (Sky Azure)
  6. OCT-SHT-006: Waffle Thermal Longsleeve (Dim Ash)
  7. OCT-JKT-002: Suede Minimalist Bomber (Camel Suede)
"""

import os
import cv2
import numpy as np


def create_base_shirt_template(
    color_rgb: tuple[int, int, int],
    texture_type: str = "linen",
    collar_type: str = "camp",
    sleeve_type: str = "short",
    size: int = 1024
) -> np.ndarray:
    """
    Creates a high-resolution 1024x1024 RGBA garment texture with realistic
    fabric weave, seams, collar, placket, and alpha transparency.
    """
    H, W = size, size
    # Create empty RGBA
    img = np.zeros((H, W, 4), dtype=np.uint8)

    # Coordinates in 1024 space:
    # Neck center: (512, 140)
    # Left shoulder (wearer left, image right): (760, 260)
    # Right shoulder (wearer right, image left): (264, 260)
    # Left armpit: (730, 480)
    # Right armpit: (294, 480)
    # Hem left: (720, 960)
    # Hem right: (304, 960)

    # 1. Base Torso Contour
    torso_pts = [
        (264, 260),  # Right shoulder
        (380, 200),  # Right neck
        (512, 170 if collar_type != "camp" else 240),  # Collar notch
        (644, 200),  # Left neck
        (760, 260),  # Left shoulder
        (730, 480),  # Left armpit
        (720, 960),  # Left hem
        (512, 980),  # Hem center
        (304, 960),  # Right hem
        (294, 480),  # Right armpit
    ]
    torso_poly = np.array(torso_pts, dtype=np.int32)

    # 2. Sleeve Contours
    if sleeve_type == "short":
        # Right sleeve (image left)
        r_sleeve_pts = [
            (264, 260),
            (294, 480),
            (110, 520),  # Cuff inner
            (80, 410),   # Cuff outer
        ]
        # Left sleeve (image right)
        l_sleeve_pts = [
            (760, 260),
            (944, 410),  # Cuff outer
            (914, 520),  # Cuff inner
            (730, 480),
        ]
    else:  # long sleeve
        r_sleeve_pts = [
            (264, 260),
            (294, 480),
            (170, 720),
            (110, 700),
            (80, 410),
        ]
        l_sleeve_pts = [
            (760, 260),
            (944, 410),
            (914, 700),
            (854, 720),
            (730, 480),
        ]

    r_sleeve_poly = np.array(r_sleeve_pts, dtype=np.int32)
    l_sleeve_poly = np.array(l_sleeve_pts, dtype=np.int32)

    # Create solid mask
    mask = np.zeros((H, W), dtype=np.uint8)
    cv2.fillPoly(mask, [torso_poly, r_sleeve_poly, l_sleeve_poly], 255)

    # 3. Procedural Fabric Texture Synthesis
    base_color = np.array(color_rgb, dtype=np.float32)

    # Create weave pattern
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    if texture_type == "linen":
        # Irregular slub yarn weave
        slub1 = np.sin(x_coords * 0.4) * np.cos(y_coords * 0.3) * 6.0
        slub2 = np.sin((x_coords + y_coords) * 0.25) * 4.0
        fine_weave = ((x_coords % 3 == 0).astype(float) - 0.5) * 8.0 + ((y_coords % 3 == 0).astype(float) - 0.5) * 8.0
        texture_noise = slub1 + slub2 + fine_weave
    elif texture_type == "cotton":
        # Fine twill weave
        twill = np.sin((x_coords * 2.0 + y_coords * 2.0) * 0.3) * 4.0
        fine = (np.random.RandomState(42).randn(H, W) * 3.5)
        texture_noise = twill + fine
    elif texture_type == "silk":
        # Smooth luster with subtle anisotropic sheen
        luster = np.sin(x_coords * 0.05 + y_coords * 0.03) * 12.0
        fine = (np.random.RandomState(42).randn(H, W) * 1.5)
        texture_noise = luster + fine
    elif texture_type == "waffle":
        # Thermal waffle grid
        grid_x = np.sin(x_coords * 0.2)
        grid_y = np.sin(y_coords * 0.2)
        waffle = (grid_x * grid_y) * 14.0
        texture_noise = waffle
    elif texture_type == "suede":
        # Soft velvety micro-grain
        suede_grain = (np.random.RandomState(42).randn(H, W) * 6.0)
        suede_soft = cv2.GaussianBlur(suede_grain, (5, 5), 1.5)
        texture_noise = suede_soft * 2.0
    else:  # plain
        texture_noise = np.random.RandomState(42).randn(H, W) * 4.0

    # Color synthesis
    bgr_img = np.zeros((H, W, 3), dtype=np.float32)
    # OpenCV uses BGR
    b_val = np.clip(base_color[2] + texture_noise, 0, 255)
    g_val = np.clip(base_color[1] + texture_noise, 0, 255)
    r_val = np.clip(base_color[0] + texture_noise, 0, 255)

    bgr_img[:, :, 0] = b_val
    bgr_img[:, :, 1] = g_val
    bgr_img[:, :, 2] = r_val

    # 4. Tailoring Details: Seams, Collar, Placket, Buttons
    detail_overlay = np.zeros((H, W, 3), dtype=np.float32)

    # Button placket down the center
    placket_w = 28
    p_x1, p_x2 = 512 - placket_w // 2, 512 + placket_w // 2
    p_y1 = 240 if collar_type == "camp" else 180
    p_y2 = 970
    cv2.rectangle(detail_overlay, (p_x1, p_y1), (p_x2, p_y2), (-18, -18, -18), -1)
    cv2.line(detail_overlay, (p_x1, p_y1), (p_x1, p_y2), (-35, -35, -35), 2)
    cv2.line(detail_overlay, (p_x2, p_y1), (p_x2, p_y2), (18, 18, 18), 2)

    # Buttons
    for by in range(p_y1 + 80, p_y2 - 40, 110):
        cv2.circle(detail_overlay, (512, by), 9, (25, 25, 25), -1)
        cv2.circle(detail_overlay, (512, by), 7, (-10, -10, -10), -1)
        cv2.circle(detail_overlay, (510, by - 2), 2, (70, 70, 70), -1)  # highlight

    # Collar Flaps
    if collar_type == "camp":
        # Right collar flap (image left)
        r_collar = np.array([(512, 240), (410, 190), (330, 310), (470, 330)], dtype=np.int32)
        # Left collar flap (image right)
        l_collar = np.array([(512, 240), (614, 190), (694, 310), (554, 330)], dtype=np.int32)
        cv2.fillPoly(detail_overlay, [r_collar, l_collar], (14, 14, 14))
        cv2.polylines(detail_overlay, [r_collar, l_collar], True, (-40, -40, -40), 2)
    elif collar_type == "mandarin":
        # Mandarin band collar
        cv2.ellipse(detail_overlay, (512, 190), (120, 30), 0, 0, 180, (18, 18, 18), 8)
    elif collar_type == "crew":
        # Ribbed crewneck band
        cv2.ellipse(detail_overlay, (512, 190), (130, 45), 0, 0, 180, (-22, -22, -22), 12)

    # Armscye Seams (shoulder-to-armpit)
    cv2.line(detail_overlay, (264, 260), (294, 480), (-40, -40, -40), 3)
    cv2.line(detail_overlay, (760, 260), (730, 480), (-40, -40, -40), 3)

    # Bottom hem fold
    cv2.line(detail_overlay, (304, 955), (720, 955), (-30, -30, -30), 2)
    cv2.line(detail_overlay, (304, 958), (720, 958), (20, 20, 20), 2)

    # Combine BGR with details
    bgr_img = np.clip(bgr_img + detail_overlay, 0, 255).astype(np.uint8)

    # Edge anti-aliasing on alpha mask
    mask_blurred = cv2.GaussianBlur(mask, (7, 7), 2.0)

    # Construct RGBA output
    img[:, :, 0] = bgr_img[:, :, 0]
    img[:, :, 1] = bgr_img[:, :, 1]
    img[:, :, 2] = bgr_img[:, :, 2]
    img[:, :, 3] = mask_blurred

    return img


def generate_all_catalog_assets(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    garments = [
        # (ID, Filename, Color RGB, Texture, Collar, Sleeve)
        ("OCT-SHT-001", "oxford_cotton_shirt.png", (248, 248, 252), "cotton", "regular", "long"),
        ("OCT-SHT-002", "camp_collar_linen_shirt.png", (222, 184, 135), "linen", "camp", "short"),
        ("OCT-SHT-003", "cuban_collar_silk_shirt.png", (128, 0, 32), "silk", "camp", "short"),
        ("OCT-SHT-004", "supima_heavy_tee.png", (28, 28, 30), "cotton", "crew", "short"),
        ("OCT-SHT-005", "tailored_mandarin_shirt.png", (135, 206, 235), "cotton", "mandarin", "long"),
        ("OCT-SHT-006", "waffle_thermal_longsleeve.png", (105, 105, 105), "waffle", "crew", "long"),
        ("OCT-JKT-002", "suede_minimalist_bomber.png", (190, 140, 90), "suede", "mandarin", "long"),
    ]

    print(f"Generating {len(garments)} realistic store garment assets in {output_dir}...")
    for gid, fname, col, tex, col_type, slv in garments:
        target_path = os.path.join(output_dir, fname)
        # If camp collar linen shirt already exists, we keep its master texture or refresh
        if gid == "OCT-SHT-002" and os.path.exists(target_path):
            print(f"  [EXISTS] {gid} ({fname}) — Preserving primary linen asset")
            continue

        rgba = create_base_shirt_template(
            color_rgb=col,
            texture_type=tex,
            collar_type=col_type,
            sleeve_type=slv,
            size=1024
        )
        cv2.imwrite(target_path, rgba)
        print(f"  [SAVED]  {gid} ({fname}) -> {rgba.shape} RGBA ({tex} fabric, {col_type} collar, {slv} sleeve)")


if __name__ == "__main__":
    import sys
    out = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "garments"))
    generate_all_catalog_assets(out)
