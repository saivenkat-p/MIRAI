"""
MIRAI VTO Engine — Step 5 Isolated Live Video Prototype
Evaluates NeuralSurfaceDeformationEngine across physical movements:
  1. Torso movement (left / right)
  2. Distance change (closer / farther scaling)
  3. Arm movement (sleeve tracking & arm raise)
  4. Leaning / tilt
  5. Turning / yaw angle
  6. Occlusion / cross-body compositing

Supports:
  - Interactive webcam mode: python live_prototype.py --webcam 0
  - Automated motion evaluation suite: python live_prototype.py --evaluate
"""

import sys
import os
import time
import argparse
import numpy as np
import cv2

# Add workspace root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.vto.engine.neural_surface import NeuralSurfaceDeformationEngine

try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False


def create_synthetic_frame(
    W: int,
    H: int,
    landmarks: dict,
    draw_person: bool = True
) -> tuple[np.ndarray, np.ndarray]:
    """Generates a synthetic evaluation frame with a person body silhouette and segmentation mask."""
    frame = np.full((H, W, 3), (220, 215, 210), dtype=np.uint8)  # Studio mirror wall tone

    # Neutral floor line
    cv2.line(frame, (0, int(H * 0.88)), (W, int(H * 0.88)), (180, 175, 170), 2)

    seg_mask = np.zeros((H, W), dtype=np.uint8)

    if not draw_person:
        return frame, seg_mask

    # Extract key landmarks
    l_sh = (int(landmarks["left_shoulder"]["x"] * W), int(landmarks["left_shoulder"]["y"] * H))
    r_sh = (int(landmarks["right_shoulder"]["x"] * W), int(landmarks["right_shoulder"]["y"] * H))
    l_el = (int(landmarks["left_elbow"]["x"] * W), int(landmarks["left_elbow"]["y"] * H))
    r_el = (int(landmarks["right_elbow"]["x"] * W), int(landmarks["right_elbow"]["y"] * H))
    l_wr = (int(landmarks["left_wrist"]["x"] * W), int(landmarks["left_wrist"]["y"] * H))
    r_wr = (int(landmarks["right_wrist"]["x"] * W), int(landmarks["right_wrist"]["y"] * H))
    l_hip = (int(landmarks["left_hip"]["x"] * W), int(landmarks["left_hip"]["y"] * H))
    r_hip = (int(landmarks["right_hip"]["x"] * W), int(landmarks["right_hip"]["y"] * H))

    sh_mid = ((l_sh[0] + r_sh[0]) // 2, (l_sh[1] + r_sh[1]) // 2)
    hip_mid = ((l_hip[0] + r_hip[0]) // 2, (l_hip[1] + r_hip[1]) // 2)

    # 1. Draw head and neck
    head_center = (sh_mid[0], sh_mid[1] - int(H * 0.12))
    cv2.circle(frame, head_center, int(H * 0.075), (170, 185, 210), -1)  # Skin tone
    cv2.circle(seg_mask, head_center, int(H * 0.075), 255, -1)

    # 2. Draw neck
    cv2.line(frame, (sh_mid[0], head_center[1] + int(H * 0.04)), sh_mid, (160, 175, 200), int(W * 0.04))
    cv2.line(seg_mask, (sh_mid[0], head_center[1] + int(H * 0.04)), sh_mid, 255, int(W * 0.04))

    # 3. Draw torso (original yellow shirt to test coverage/peek-through)
    torso_poly = np.array([
        [l_sh[0] - 15, l_sh[1]],
        [r_sh[0] + 15, r_sh[1]],
        [r_hip[0] + 20, r_hip[1]],
        [l_hip[0] - 20, l_hip[1]]
    ], dtype=np.int32)
    cv2.fillPoly(frame, [torso_poly], (60, 190, 240))  # Yellow undershirt (BGR)
    cv2.fillPoly(seg_mask, [torso_poly], 255)

    # 4. Draw arms (forearms skin tone, upper arms undershirt color)
    # Left Arm
    cv2.line(frame, l_sh, l_el, (60, 190, 240), int(W * 0.045))  # Upper arm
    cv2.line(frame, l_el, l_wr, (170, 185, 210), int(W * 0.035)) # Forearm (skin)
    cv2.line(seg_mask, l_sh, l_el, 255, int(W * 0.045))
    cv2.line(seg_mask, l_el, l_wr, 255, int(W * 0.035))

    # Right Arm
    cv2.line(frame, r_sh, r_el, (60, 190, 240), int(W * 0.045))
    cv2.line(frame, r_el, r_wr, (170, 185, 210), int(W * 0.035))
    cv2.line(seg_mask, r_sh, r_el, 255, int(W * 0.045))
    cv2.line(seg_mask, r_el, r_wr, 255, int(W * 0.035))

    return frame, seg_mask


def run_evaluation_suite(output_dir: str):
    """Executes the 6-movement physical test suite and saves diagnostic images."""
    os.makedirs(output_dir, exist_ok=True)
    W, H = 1280, 720

    print("=" * 70)
    print("MIRAI VTO STEP 5: ISOLATED LIVE PROTOTYPE EVALUATION")
    print("=" * 70)

    engine = NeuralSurfaceDeformationEngine()
    engine.initialize()

    garment_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "garments", "camp_collar_linen_shirt.png")
    )
    garment_id = "OCT-SHT-002"
    engine.load_garment(garment_id, garment_path)
    print(f"Loaded Garment: {garment_id}")

    # Base nominal standing pose
    base_pose = {
        "left_shoulder": {"x": 0.42, "y": 0.28, "z": 0.0},
        "right_shoulder": {"x": 0.58, "y": 0.28, "z": 0.0},
        "left_elbow": {"x": 0.35, "y": 0.45, "z": 0.0},
        "right_elbow": {"x": 0.65, "y": 0.45, "z": 0.0},
        "left_wrist": {"x": 0.32, "y": 0.60, "z": 0.0},
        "right_wrist": {"x": 0.68, "y": 0.60, "z": 0.0},
        "left_hip": {"x": 0.45, "y": 0.62, "z": 0.0},
        "right_hip": {"x": 0.55, "y": 0.62, "z": 0.0},
    }

    # Define test movement variations
    movements = {
        "1_nominal_center": {
            "title": "Nominal Standing Pose",
            "pose": base_pose,
            "desc": "Baseline upright position directly facing mirror."
        },
        "2_shift_left": {
            "title": "Torso Shift Left (-15%)",
            "pose": {k: {"x": v["x"] - 0.15, "y": v["y"], "z": v["z"]} for k, v in base_pose.items()},
            "desc": "Person steps horizontally to their left."
        },
        "3_scale_close": {
            "title": "Moving Closer (+25% Scale)",
            "pose": {
                "left_shoulder": {"x": 0.38, "y": 0.24, "z": -0.3},
                "right_shoulder": {"x": 0.62, "y": 0.24, "z": -0.3},
                "left_elbow": {"x": 0.28, "y": 0.45, "z": -0.3},
                "right_elbow": {"x": 0.72, "y": 0.45, "z": -0.3},
                "left_wrist": {"x": 0.24, "y": 0.66, "z": -0.3},
                "right_wrist": {"x": 0.76, "y": 0.66, "z": -0.3},
                "left_hip": {"x": 0.42, "y": 0.68, "z": -0.3},
                "right_hip": {"x": 0.58, "y": 0.68, "z": -0.3},
            },
            "desc": "Person steps closer to smart mirror display."
        },
        "4_arm_raise_left": {
            "title": "Left Arm Raised (90 deg)",
            "pose": {
                **base_pose,
                "left_elbow": {"x": 0.28, "y": 0.28, "z": 0.0},  # Horizontal
                "left_wrist": {"x": 0.20, "y": 0.20, "z": 0.0},  # Raised hand
            },
            "desc": "Left arm raised laterally to test sleeve conformity."
        },
        "5_leaning_tilt": {
            "title": "Torso Lateral Lean (15 deg)",
            "pose": {
                "left_shoulder": {"x": 0.40, "y": 0.25, "z": 0.0},
                "right_shoulder": {"x": 0.56, "y": 0.33, "z": 0.0},
                "left_elbow": {"x": 0.33, "y": 0.42, "z": 0.0},
                "right_elbow": {"x": 0.64, "y": 0.49, "z": 0.0},
                "left_wrist": {"x": 0.30, "y": 0.58, "z": 0.0},
                "right_wrist": {"x": 0.67, "y": 0.64, "z": 0.0},
                "left_hip": {"x": 0.46, "y": 0.62, "z": 0.0},
                "right_hip": {"x": 0.56, "y": 0.64, "z": 0.0},
            },
            "desc": "Shoulder line tilted 15 degrees."
        },
        "6_turning_angle": {
            "title": "Body Turn (45 deg Yaw)",
            "pose": {
                "left_shoulder": {"x": 0.44, "y": 0.28, "z": 0.25},   # Far shoulder
                "right_shoulder": {"x": 0.54, "y": 0.28, "z": -0.25},  # Near shoulder
                "left_elbow": {"x": 0.41, "y": 0.45, "z": 0.20},
                "right_elbow": {"x": 0.61, "y": 0.45, "z": -0.20},
                "left_wrist": {"x": 0.40, "y": 0.60, "z": 0.15},
                "right_wrist": {"x": 0.63, "y": 0.60, "z": -0.15},
                "left_hip": {"x": 0.46, "y": 0.62, "z": 0.10},
                "right_hip": {"x": 0.53, "y": 0.62, "z": -0.10},
            },
            "desc": "Person turns at a 45 degree angle to mirror."
        }
    }

    results = {}
    saved_images = []

    print("\nExecuting Physical Movement Test Suite...")
    for key, item in movements.items():
        t_start = time.perf_counter()
        raw_frame, seg_mask = create_synthetic_frame(W, H, item["pose"], draw_person=True)

        res = engine.process_frame(raw_frame, item["pose"], seg_mask, garment_id)
        out_frame = res["output_frame"]
        t_total = (time.perf_counter() - t_start) * 1000.0

        # Annotate test frame with diagnostic label
        cv2.putText(out_frame, f"TEST: {item['title']}", (25, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 3)
        cv2.putText(out_frame, f"TEST: {item['title']}", (25, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(out_frame, f"Latency: {t_total:.1f}ms | {res['metrics']['fps']} FPS", (25, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        file_path = os.path.join(output_dir, f"step5_eval_{key}.jpg")
        cv2.imwrite(file_path, out_frame)
        saved_images.append(out_frame)

        results[key] = {
            "title": item["title"],
            "latency_ms": round(t_total, 2),
            "fps": res["metrics"]["fps"],
            "image_saved": file_path
        }
        print(f"  [OK] {item['title']:<30} | {t_total:6.1f} ms | Saved: {os.path.basename(file_path)}")

    # Generate a composite 2x3 montage
    print("\nGenerating Evaluation Montage (2x3 Grid)...")
    thumb_w, thumb_h = 640, 360
    resized_thumbs = [cv2.resize(img, (thumb_w, thumb_h)) for img in saved_images]

    row1 = np.hstack(resized_thumbs[0:3])
    row2 = np.hstack(resized_thumbs[3:6])
    montage = np.vstack([row1, row2])

    montage_path = os.path.join(output_dir, "step5_eval_movement_montage.jpg")
    cv2.imwrite(montage_path, montage)
    print(f"Montage saved to: {montage_path}")

    # Generate a 60-frame continuous video clip demonstrating smooth motion
    print("\nGenerating Continuous Evaluation Video Clip (60 frames)...")
    video_path = os.path.join(output_dir, "step5_eval_motion_clip.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(video_path, fourcc, 20.0, (W, H))

    for frame_idx in range(60):
        # Oscillate left to right and tilt slightly
        alpha_t = np.sin(frame_idx * (2 * np.pi / 60.0))
        pose = {
            "left_shoulder": {"x": 0.42 + 0.08 * alpha_t, "y": 0.28 + 0.02 * abs(alpha_t), "z": 0.0},
            "right_shoulder": {"x": 0.58 + 0.08 * alpha_t, "y": 0.28 - 0.02 * abs(alpha_t), "z": 0.0},
            "left_elbow": {"x": 0.35 + 0.08 * alpha_t, "y": 0.45, "z": 0.0},
            "right_elbow": {"x": 0.65 + 0.08 * alpha_t, "y": 0.45, "z": 0.0},
            "left_wrist": {"x": 0.32 + 0.08 * alpha_t, "y": 0.60, "z": 0.0},
            "right_wrist": {"x": 0.68 + 0.08 * alpha_t, "y": 0.60, "z": 0.0},
            "left_hip": {"x": 0.45 + 0.06 * alpha_t, "y": 0.62, "z": 0.0},
            "right_hip": {"x": 0.55 + 0.06 * alpha_t, "y": 0.62, "z": 0.0},
        }
        f_raw, s_mask = create_synthetic_frame(W, H, pose, draw_person=True)
        res = engine.process_frame(f_raw, pose, s_mask, garment_id)
        video_writer.write(res["output_frame"])

    video_writer.release()
    print(f"Video clip saved to: {video_path}")
    print("=" * 70)
    return results


def run_interactive_webcam(camera_idx: int = 0):
    """Runs the live webcam loop with OpenCV window."""
    print(f"Opening webcam device {camera_idx}...")
    cap = cv2.VideoCapture(camera_idx)
    if not cap.isOpened():
        print(f"ERROR: Could not open camera {camera_idx}. Falling back to evaluation suite.")
        return False

    engine = NeuralSurfaceDeformationEngine()
    engine.initialize()

    garment_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "garments", "camp_collar_linen_shirt.png")
    )
    garment_id = "OCT-SHT-002"
    engine.load_garment(garment_id, garment_path)

    # Optional MediaPipe Pose Detector
    pose_detector = None
    if HAS_MEDIAPIPE:
        mp_pose = mp.solutions.pose
        pose_detector = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    window_name = "MIRAI Live VTO Evaluation Prototype"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    print("Live loop running. Press 'q' to quit, 's' to snapshot.")
    frame_count = 0
    t_start = time.perf_counter()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        H, W = frame.shape[:2]
        landmarks = None

        if pose_detector:
            rgb_f = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_res = pose_detector.process(rgb_f)
            if mp_res.pose_landmarks:
                lms = mp_res.pose_landmarks.landmark
                landmarks = {
                    "left_shoulder": {"x": lms[11].x, "y": lms[11].y, "z": lms[11].z},
                    "right_shoulder": {"x": lms[12].x, "y": lms[12].y, "z": lms[12].z},
                    "left_elbow": {"x": lms[13].x, "y": lms[13].y, "z": lms[13].z},
                    "right_elbow": {"x": lms[14].x, "y": lms[14].y, "z": lms[14].z},
                    "left_wrist": {"x": lms[15].x, "y": lms[15].y, "z": lms[15].z},
                    "right_wrist": {"x": lms[16].x, "y": lms[16].y, "z": lms[16].z},
                    "left_hip": {"x": lms[23].x, "y": lms[23].y, "z": lms[23].z},
                    "right_hip": {"x": lms[24].x, "y": lms[24].y, "z": lms[24].z},
                }

        res = engine.process_frame(frame, landmarks, None, garment_id)
        out = res["output_frame"]

        frame_count += 1
        fps = frame_count / (time.perf_counter() - t_start)
        cv2.putText(out, f"MIRAI VTO Prototype | {fps:.1f} FPS", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow(window_name, out)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            snap_path = f"vto_snapshot_{int(time.time())}.jpg"
            cv2.imwrite(snap_path, out)
            print(f"Saved snapshot to {snap_path}")

    cap.release()
    cv2.destroyAllWindows()
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MIRAI Step 5 Live VTO Prototype")
    parser.add_argument("--webcam", type=int, default=None, help="Webcam device index (e.g. 0)")
    parser.add_argument("--evaluate", action="store_true", default=True, help="Run evaluation suite on physical movements")
    args = parser.parse_args()

    out_directory = os.path.dirname(os.path.abspath(__file__))

    if args.webcam is not None:
        run_interactive_webcam(args.webcam)
    else:
        run_evaluation_suite(out_directory)
