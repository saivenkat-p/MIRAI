"""
Step 7A: Automated Motion Evaluation Test Suite for Kinematic Garment Rig.
Executes 10 required physical movement tests:
  TEST 1:  Standing, arms down
  TEST 2:  Left arm raised ~45 deg
  TEST 3:  Left arm raised ~90 deg
  TEST 4:  Right arm raised ~90 deg
  TEST 5:  Both arms raised
  TEST 6:  Left arm bent at elbow
  TEST 7:  Right arm bent at elbow
  TEST 8:  Both elbows bent
  TEST 9:  Torso rotated left (yaw)
  TEST 10: Torso rotated right (yaw)

Generates:
  - docs/step7a_kinematic_montage.png (2x5 grid)
  - docs/step7a_kinematic_motion.mp4 (continuous animation)
  - Detailed diagnostic metrics report
"""

import sys
import os
import time
import math
import numpy as np
import cv2

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.vto.kinematic_rig import KinematicGarmentRig


def draw_body_with_skeleton(
    W: int, H: int, landmarks: dict, draw_undershirt: bool = True
) -> tuple[np.ndarray, np.ndarray]:
    """Renders a controlled test human figure with yellow undershirt and joint skeleton lines."""
    frame = np.full((H, W, 3), (225, 220, 215), dtype=np.uint8)  # Studio backdrop
    seg_mask = np.zeros((H, W), dtype=np.uint8)

    l_sh = (int(landmarks["left_shoulder"]["x"] * W), int(landmarks["left_shoulder"]["y"] * H))
    r_sh = (int(landmarks["right_shoulder"]["x"] * W), int(landmarks["right_shoulder"]["y"] * H))
    l_el = (int(landmarks["left_elbow"]["x"] * W), int(landmarks["left_elbow"]["y"] * H))
    r_el = (int(landmarks["right_elbow"]["x"] * W), int(landmarks["right_elbow"]["y"] * H))
    l_wr = (int(landmarks["left_wrist"]["x"] * W), int(landmarks["left_wrist"]["y"] * H))
    r_wr = (int(landmarks["right_wrist"]["x"] * W), int(landmarks["right_wrist"]["y"] * H))
    l_hip = (int(landmarks["left_hip"]["x"] * W), int(landmarks["left_hip"]["y"] * H))
    r_hip = (int(landmarks["right_hip"]["x"] * W), int(landmarks["right_hip"]["y"] * H))

    sh_mid = ((l_sh[0] + r_sh[0]) // 2, (l_sh[1] + r_sh[1]) // 2)

    # 1. Head & Neck
    head_c = (sh_mid[0], sh_mid[1] - int(H * 0.12))
    cv2.circle(frame, head_c, int(H * 0.075), (170, 185, 210), -1)
    cv2.circle(seg_mask, head_c, int(H * 0.075), 255, -1)

    cv2.line(frame, (sh_mid[0], head_c[1] + int(H * 0.04)), sh_mid, (160, 175, 200), int(W * 0.04))
    cv2.line(seg_mask, (sh_mid[0], head_c[1] + int(H * 0.04)), sh_mid, 255, int(W * 0.04))

    # 2. Torso (Yellow undershirt to test coverage)
    torso_poly = np.array([
        [l_sh[0] - 10, l_sh[1]],
        [r_sh[0] + 10, r_sh[1]],
        [r_hip[0] + 15, r_hip[1]],
        [l_hip[0] - 15, l_hip[1]]
    ], dtype=np.int32)
    if draw_undershirt:
        cv2.fillPoly(frame, [torso_poly], (60, 190, 240))  # Yellow
    cv2.fillPoly(seg_mask, [torso_poly], 255)

    # 3. Arms (Upper arms yellow, forearms skin)
    arm_w = int(W * 0.04)
    # Left Arm
    cv2.line(frame, l_sh, l_el, (60, 190, 240), arm_w)
    cv2.line(frame, l_el, l_wr, (170, 185, 210), int(arm_w * 0.85))
    cv2.line(seg_mask, l_sh, l_el, 255, arm_w)
    cv2.line(seg_mask, l_el, l_wr, 255, int(arm_w * 0.85))

    # Right Arm
    cv2.line(frame, r_sh, r_el, (60, 190, 240), arm_w)
    cv2.line(frame, r_el, r_wr, (170, 185, 210), int(arm_w * 0.85))
    cv2.line(seg_mask, r_sh, r_el, 255, arm_w)
    cv2.line(seg_mask, r_el, r_wr, 255, int(arm_w * 0.85))

    return frame, seg_mask


def run_10_motion_tests():
    print("=" * 70)
    print("MIRAI STEP 7A: KINEMATIC MULTI-PART GARMENT RIGGING POC")
    print("=" * 70)

    W, H = 1280, 720
    rig = KinematicGarmentRig()
    rig.initialize()

    garment_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "garments", "camp_collar_linen_shirt.png")
    )
    garment_id = "OCT-SHT-002"
    rig.load_garment(garment_id, garment_path)
    print(f"Loaded Primary Garment: {garment_id} (Relaxed Camp-Collar Linen Shirt)")

    # 10 Test Poses Specification
    tests = {
        "test1_arms_down": {
            "title": "TEST 1: Standing, arms down",
            "pose": {
                "left_shoulder": {"x": 0.42, "y": 0.28, "z": 0.0},
                "right_shoulder": {"x": 0.58, "y": 0.28, "z": 0.0},
                "left_elbow": {"x": 0.36, "y": 0.44, "z": 0.0},
                "right_elbow": {"x": 0.64, "y": 0.44, "z": 0.0},
                "left_wrist": {"x": 0.34, "y": 0.60, "z": 0.0},
                "right_wrist": {"x": 0.66, "y": 0.60, "z": 0.0},
                "left_hip": {"x": 0.45, "y": 0.62, "z": 0.0},
                "right_hip": {"x": 0.55, "y": 0.62, "z": 0.0},
            }
        },
        "test2_left_arm_45": {
            "title": "TEST 2: Left arm raised ~45 deg",
            "pose": {
                "left_shoulder": {"x": 0.42, "y": 0.28, "z": 0.0},
                "right_shoulder": {"x": 0.58, "y": 0.28, "z": 0.0},
                "left_elbow": {"x": 0.32, "y": 0.36, "z": 0.0},
                "right_elbow": {"x": 0.64, "y": 0.44, "z": 0.0},
                "left_wrist": {"x": 0.25, "y": 0.44, "z": 0.0},
                "right_wrist": {"x": 0.66, "y": 0.60, "z": 0.0},
                "left_hip": {"x": 0.45, "y": 0.62, "z": 0.0},
                "right_hip": {"x": 0.55, "y": 0.62, "z": 0.0},
            }
        },
        "test3_left_arm_90": {
            "title": "TEST 3: Left arm raised ~90 deg",
            "pose": {
                "left_shoulder": {"x": 0.42, "y": 0.28, "z": 0.0},
                "right_shoulder": {"x": 0.58, "y": 0.28, "z": 0.0},
                "left_elbow": {"x": 0.27, "y": 0.28, "z": 0.0},
                "right_elbow": {"x": 0.64, "y": 0.44, "z": 0.0},
                "left_wrist": {"x": 0.16, "y": 0.28, "z": 0.0},
                "right_wrist": {"x": 0.66, "y": 0.60, "z": 0.0},
                "left_hip": {"x": 0.45, "y": 0.62, "z": 0.0},
                "right_hip": {"x": 0.55, "y": 0.62, "z": 0.0},
            }
        },
        "test4_right_arm_90": {
            "title": "TEST 4: Right arm raised ~90 deg",
            "pose": {
                "left_shoulder": {"x": 0.42, "y": 0.28, "z": 0.0},
                "right_shoulder": {"x": 0.58, "y": 0.28, "z": 0.0},
                "left_elbow": {"x": 0.36, "y": 0.44, "z": 0.0},
                "right_elbow": {"x": 0.73, "y": 0.28, "z": 0.0},
                "left_wrist": {"x": 0.34, "y": 0.60, "z": 0.0},
                "right_wrist": {"x": 0.84, "y": 0.28, "z": 0.0},
                "left_hip": {"x": 0.45, "y": 0.62, "z": 0.0},
                "right_hip": {"x": 0.55, "y": 0.62, "z": 0.0},
            }
        },
        "test5_both_arms_raised": {
            "title": "TEST 5: Both arms raised",
            "pose": {
                "left_shoulder": {"x": 0.42, "y": 0.28, "z": 0.0},
                "right_shoulder": {"x": 0.58, "y": 0.28, "z": 0.0},
                "left_elbow": {"x": 0.30, "y": 0.20, "z": 0.0},
                "right_elbow": {"x": 0.70, "y": 0.20, "z": 0.0},
                "left_wrist": {"x": 0.22, "y": 0.12, "z": 0.0},
                "right_wrist": {"x": 0.78, "y": 0.12, "z": 0.0},
                "left_hip": {"x": 0.45, "y": 0.62, "z": 0.0},
                "right_hip": {"x": 0.55, "y": 0.62, "z": 0.0},
            }
        },
        "test6_left_elbow_bent": {
            "title": "TEST 6: Left arm bent at elbow",
            "pose": {
                "left_shoulder": {"x": 0.42, "y": 0.28, "z": 0.0},
                "right_shoulder": {"x": 0.58, "y": 0.28, "z": 0.0},
                "left_elbow": {"x": 0.34, "y": 0.44, "z": 0.0},
                "right_elbow": {"x": 0.64, "y": 0.44, "z": 0.0},
                "left_wrist": {"x": 0.44, "y": 0.38, "z": 0.0},  # Hand in front of chest
                "right_wrist": {"x": 0.66, "y": 0.60, "z": 0.0},
                "left_hip": {"x": 0.45, "y": 0.62, "z": 0.0},
                "right_hip": {"x": 0.55, "y": 0.62, "z": 0.0},
            }
        },
        "test7_right_elbow_bent": {
            "title": "TEST 7: Right arm bent at elbow",
            "pose": {
                "left_shoulder": {"x": 0.42, "y": 0.28, "z": 0.0},
                "right_shoulder": {"x": 0.58, "y": 0.28, "z": 0.0},
                "left_elbow": {"x": 0.36, "y": 0.44, "z": 0.0},
                "right_elbow": {"x": 0.66, "y": 0.44, "z": 0.0},
                "left_wrist": {"x": 0.34, "y": 0.60, "z": 0.0},
                "right_wrist": {"x": 0.56, "y": 0.38, "z": 0.0},  # Hand in front of chest
                "left_hip": {"x": 0.45, "y": 0.62, "z": 0.0},
                "right_hip": {"x": 0.55, "y": 0.62, "z": 0.0},
            }
        },
        "test8_both_elbows_bent": {
            "title": "TEST 8: Both elbows bent",
            "pose": {
                "left_shoulder": {"x": 0.42, "y": 0.28, "z": 0.0},
                "right_shoulder": {"x": 0.58, "y": 0.28, "z": 0.0},
                "left_elbow": {"x": 0.33, "y": 0.42, "z": 0.0},
                "right_elbow": {"x": 0.67, "y": 0.42, "z": 0.0},
                "left_wrist": {"x": 0.43, "y": 0.35, "z": 0.0},
                "right_wrist": {"x": 0.57, "y": 0.35, "z": 0.0},
                "left_hip": {"x": 0.45, "y": 0.62, "z": 0.0},
                "right_hip": {"x": 0.55, "y": 0.62, "z": 0.0},
            }
        },
        "test9_torso_rot_left": {
            "title": "TEST 9: Torso rotated left",
            "pose": {
                "left_shoulder": {"x": 0.45, "y": 0.28, "z": 0.15},
                "right_shoulder": {"x": 0.55, "y": 0.28, "z": -0.15},
                "left_elbow": {"x": 0.41, "y": 0.44, "z": 0.12},
                "right_elbow": {"x": 0.62, "y": 0.44, "z": -0.12},
                "left_wrist": {"x": 0.39, "y": 0.60, "z": 0.10},
                "right_wrist": {"x": 0.64, "y": 0.60, "z": -0.10},
                "left_hip": {"x": 0.47, "y": 0.62, "z": 0.10},
                "right_hip": {"x": 0.53, "y": 0.62, "z": -0.10},
            }
        },
        "test10_torso_rot_right": {
            "title": "TEST 10: Torso rotated right",
            "pose": {
                "left_shoulder": {"x": 0.45, "y": 0.28, "z": -0.15},
                "right_shoulder": {"x": 0.55, "y": 0.28, "z": 0.15},
                "left_elbow": {"x": 0.38, "y": 0.44, "z": -0.12},
                "right_elbow": {"x": 0.59, "y": 0.44, "z": 0.12},
                "left_wrist": {"x": 0.36, "y": 0.60, "z": -0.10},
                "right_wrist": {"x": 0.61, "y": 0.60, "z": 0.10},
                "left_hip": {"x": 0.47, "y": 0.62, "z": -0.10},
                "right_hip": {"x": 0.53, "y": 0.62, "z": 0.10},
            }
        },
    }

    test_outputs = []
    print("\nExecuting 10 Movement Tests...")
    for key, item in tests.items():
        pose = item["pose"]
        raw_frame, seg_mask = draw_body_with_skeleton(W, H, pose, draw_undershirt=True)

        t_start = time.perf_counter()
        res = rig.process_frame(raw_frame, pose, seg_mask, garment_id)
        t_total = (time.perf_counter() - t_start) * 1000.0

        out_frame = res["output_frame"].copy()

        # Draw skeletal bones on output for clear visual verification
        l_sh = (int(pose["left_shoulder"]["x"] * W), int(pose["left_shoulder"]["y"] * H))
        l_el = (int(pose["left_elbow"]["x"] * W), int(pose["left_elbow"]["y"] * H))
        l_wr = (int(pose["left_wrist"]["x"] * W), int(pose["left_wrist"]["y"] * H))
        r_sh = (int(pose["right_shoulder"]["x"] * W), int(pose["right_shoulder"]["y"] * H))
        r_el = (int(pose["right_elbow"]["x"] * W), int(pose["right_elbow"]["y"] * H))
        r_wr = (int(pose["right_wrist"]["x"] * W), int(pose["right_wrist"]["y"] * H))

        # Thin cyan skeleton lines
        cv2.line(out_frame, l_sh, l_el, (255, 255, 0), 2)
        cv2.line(out_frame, l_el, l_wr, (255, 255, 0), 2)
        cv2.line(out_frame, r_sh, r_el, (255, 255, 0), 2)
        cv2.line(out_frame, r_el, r_wr, (255, 255, 0), 2)
        for pt in [l_sh, l_el, l_wr, r_sh, r_el, r_wr]:
            cv2.circle(out_frame, pt, 4, (0, 0, 255), -1)

        # Diagnostic HUD
        cv2.putText(out_frame, item["title"], (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 0), 3)
        cv2.putText(out_frame, item["title"], (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
        fps = res["metrics"]["fps"]
        l_ang = res["metrics"]["articulation"]["left_sleeve_angle_deg"]
        r_ang = res["metrics"]["articulation"]["right_sleeve_angle_deg"]
        cv2.putText(out_frame, f"{t_total:.1f}ms | {fps} FPS | L-Angle: {l_ang} deg | R-Angle: {r_ang} deg",
                    (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)

        test_outputs.append(out_frame)
        print(f"  [OK] {item['title']:<35} | {t_total:5.1f} ms | L-Arm: {l_ang:5.1f} deg | R-Arm: {r_ang:5.1f} deg")

    # Generate 2x5 composite montage
    print("\nGenerating Diagnostic Montage (2x5 Grid)...")
    thumb_w, thumb_h = 480, 270
    thumbs = [cv2.resize(img, (thumb_w, thumb_h)) for img in test_outputs]
    row1 = np.hstack(thumbs[0:5])
    row2 = np.hstack(thumbs[5:10])
    montage = np.vstack([row1, row2])

    # Save to docs in both directories
    montage_path1 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "step7a_kinematic_montage.png"))
    cv2.imwrite(montage_path1, montage)
    print(f"Montage saved to: {montage_path1}")

    proj_dir = "C:\\Projects\\5G-Smart-Trial-Room\\docs"
    if os.path.exists(proj_dir):
        cv2.imwrite(os.path.join(proj_dir, "step7a_kinematic_montage.png"), montage)

    # Generate 100-frame continuous animation video
    print("\nGenerating Continuous Kinematic Motion Clip (100 frames)...")
    video_path1 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "step7a_kinematic_motion.mp4"))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(video_path1, fourcc, 25.0, (W, H))

    for f_idx in range(100):
        # Phase 1: Left arm raises from 0 to 90 degrees and back
        angle_l = math.sin(f_idx * (2 * math.pi / 50.0)) * 0.5 + 0.5  # 0 to 1
        arm_rad = -angle_l * math.pi * 0.55  # raises upward
        base_l_sh = (0.42, 0.28)
        upper_l = 0.18
        fore_l = 0.16

        el_x = base_l_sh[0] - upper_l * math.cos(arm_rad)
        el_y = base_l_sh[1] + upper_l * math.sin(arm_rad)
        wr_x = el_x - fore_l * math.cos(arm_rad)
        wr_y = el_y + fore_l * math.sin(arm_rad)

        pose = {
            "left_shoulder": {"x": base_l_sh[0], "y": base_l_sh[1], "z": 0.0},
            "right_shoulder": {"x": 0.58, "y": 0.28, "z": 0.0},
            "left_elbow": {"x": el_x, "y": el_y, "z": 0.0},
            "right_elbow": {"x": 0.64, "y": 0.44, "z": 0.0},
            "left_wrist": {"x": wr_x, "y": wr_y, "z": 0.0},
            "right_wrist": {"x": 0.66, "y": 0.60, "z": 0.0},
            "left_hip": {"x": 0.45, "y": 0.62, "z": 0.0},
            "right_hip": {"x": 0.55, "y": 0.62, "z": 0.0},
        }
        f_raw, s_mask = draw_body_with_skeleton(W, H, pose, draw_undershirt=True)
        res = rig.process_frame(f_raw, pose, s_mask, garment_id)
        writer.write(res["output_frame"])

    writer.release()
    if os.path.exists(proj_dir) and os.path.abspath(video_path1) != os.path.abspath(os.path.join(proj_dir, "step7a_kinematic_motion.mp4")):
        import shutil
        shutil.copyfile(video_path1, os.path.join(proj_dir, "step7a_kinematic_motion.mp4"))

    print("=" * 70)
    print("STEP 7A KINEMATIC POC TESTING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run_10_motion_tests()
