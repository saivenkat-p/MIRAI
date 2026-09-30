"""
Kinematic Multi-Part Garment Rig (Sub-phase 1 POC)
Implements IVTOEngine with decoupled kinematic articulation:
  1. Torso Core (anchored to shoulders and spine)
  2. Left Sleeve (articulates along Left Shoulder -> Elbow -> Wrist)
  3. Right Sleeve (articulates along Right Shoulder -> Elbow -> Wrist)
Driven by body landmarks, bone vectors, joint angles, and local coordinate frames.
"""

import os
import time
import math
from typing import Dict, Any, Optional, Tuple
import cv2
import numpy as np

try:
    import torch
    import torch.nn.functional as F
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

from backend.vto.engine.base import IVTOEngine


class KinematicGarmentRig(IVTOEngine):
    """
    Sub-phase 1: 3-Part Kinematic Garment Rigging Engine.
    Decomposes garment texture into local torso and sleeve regions,
    transforming each according to body skeletal kinematics.
    """

    def __init__(self):
        self.device = None
        self.is_cuda = False
        self.device_name = "Not Initialized"
        self.total_vram_mb = 0.0
        self.initialized = False
        self.active_garment_id = None
        self.garment_data: Dict[str, Any] = {}

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        if not HAS_TORCH:
            raise RuntimeError("PyTorch is required for KinematicGarmentRig.")

        if torch.cuda.is_available():
            self.device = torch.device("cuda:0")
            self.device_name = torch.cuda.get_device_name(0)
            self.total_vram_mb = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
            self.is_cuda = True
        else:
            self.device = torch.device("cpu")
            self.device_name = "CPU Fallback"
            self.total_vram_mb = 0.0
            self.is_cuda = False

        self.initialized = True
        return True

    def get_hardware_info(self) -> Dict[str, Any]:
        info = {
            "device": str(self.device),
            "device_name": self.device_name,
            "is_cuda": self.is_cuda,
            "total_vram_mb": round(self.total_vram_mb, 2),
            "pytorch_version": torch.__version__ if HAS_TORCH else "N/A",
        }
        if self.is_cuda:
            info["vram_allocated_mb"] = round(torch.cuda.memory_allocated(self.device) / (1024 * 1024), 2)
            info["vram_reserved_mb"] = round(torch.cuda.memory_reserved(self.device) / (1024 * 1024), 2)
        return info

    def load_garment(self, garment_id: str, garment_path: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        if not os.path.exists(garment_path):
            raise FileNotFoundError(f"Garment not found at {garment_path}")

        img_rgba = cv2.imread(garment_path, cv2.IMREAD_UNCHANGED)
        if img_rgba is None:
            raise ValueError(f"Failed to load image from {garment_path}")

        if img_rgba.shape[2] == 3:
            alpha = np.ones((img_rgba.shape[0], img_rgba.shape[1], 1), dtype=img_rgba.dtype) * 255
            img_rgba = np.concatenate([img_rgba, alpha], axis=2)

        H_g, W_g = img_rgba.shape[:2]

        # Convert to RGB and keep Alpha
        img_rgb = cv2.cvtColor(img_rgba[:, :, :3], cv2.COLOR_BGR2RGB)
        alpha = img_rgba[:, :, 3:4]
        combined = np.concatenate([img_rgb, alpha], axis=2)  # H x W x 4 (RGBA)

        # Decompose into 3 kinematic sub-parts in normalized UV texture coordinates
        # In camp_collar_linen_shirt.png (1024x1024):
        # Wearer Left is image right (X: 740 to 966)
        # Wearer Right is image left (X: 58 to 284)
        # Torso center is X: 240 to 784, Y: 180 to 966
        
        # 1. Torso Mask & Cutout
        torso_mask = np.zeros((H_g, W_g, 1), dtype=np.float32)
        torso_mask[:, 240:784] = 1.0
        # Feather the armpit boundaries for seamless blend
        torso_mask[:, 240:280] = np.linspace(0.0, 1.0, 40).reshape(1, 40, 1)
        torso_mask[:, 744:784] = np.linspace(1.0, 0.0, 40).reshape(1, 40, 1)

        # 2. Wearer Left Sleeve Mask (Image Right: X 740 to 966)
        left_sleeve_mask = np.zeros((H_g, W_g, 1), dtype=np.float32)
        left_sleeve_mask[180:600, 740:] = 1.0
        left_sleeve_mask[180:600, 740:780] = np.linspace(0.0, 1.0, 40).reshape(1, 40, 1)

        # 3. Wearer Right Sleeve Mask (Image Left: X 58 to 284)
        right_sleeve_mask = np.zeros((H_g, W_g, 1), dtype=np.float32)
        right_sleeve_mask[180:600, :284] = 1.0
        right_sleeve_mask[180:600, 244:284] = np.linspace(1.0, 0.0, 40).reshape(1, 40, 1)

        torso_rgba = combined.astype(np.float32) / 255.0
        torso_rgba[:, :, 3:4] *= torso_mask

        left_sleeve_rgba = combined.astype(np.float32) / 255.0
        left_sleeve_rgba[:, :, 3:4] *= left_sleeve_mask

        right_sleeve_rgba = combined.astype(np.float32) / 255.0
        right_sleeve_rgba[:, :, 3:4] *= right_sleeve_mask

        # Move to PyTorch tensors on device (1, 4, H_g, W_g)
        t_torso = torch.from_numpy(torso_rgba.transpose(2, 0, 1)).unsqueeze(0).to(self.device)
        t_lsleeve = torch.from_numpy(left_sleeve_rgba.transpose(2, 0, 1)).unsqueeze(0).to(self.device)
        t_rsleeve = torch.from_numpy(right_sleeve_rgba.transpose(2, 0, 1)).unsqueeze(0).to(self.device)

        # Canonical rest geometric anchors (normalized in [0, 1])
        anchors = {
            "collar_center": (0.50, 0.28),
            "left_shoulder": (0.72, 0.31),   # Wearer Left (image right)
            "right_shoulder": (0.28, 0.31),  # Wearer Right (image left)
            "left_elbow_rest": (0.88, 0.44), # Wearer Left sleeve rest direction
            "right_elbow_rest": (0.12, 0.44),# Wearer Right sleeve rest direction
            "left_armpit": (0.75, 0.52),
            "right_armpit": (0.25, 0.52),
            "hem_center": (0.50, 0.94),
        }

        self.garment_data[garment_id] = {
            "torso_tensor": t_torso,
            "left_sleeve_tensor": t_lsleeve,
            "right_sleeve_tensor": t_rsleeve,
            "anchors": anchors,
            "texture_size": (W_g, H_g)
        }
        self.active_garment_id = garment_id
        return True

    def _build_torso_grid(self, H: int, W: int, landmarks: Dict[str, Any], anchors: Dict[str, Any]) -> torch.Tensor:
        """Constructs sampling grid for Torso core."""
        l_sh = landmarks.get("left_shoulder", {"x": 0.42, "y": 0.28, "z": 0.0})
        r_sh = landmarks.get("right_shoulder", {"x": 0.58, "y": 0.28, "z": 0.0})
        l_hip = landmarks.get("left_hip", {"x": 0.45, "y": 0.62, "z": 0.0})
        r_hip = landmarks.get("right_hip", {"x": 0.55, "y": 0.62, "z": 0.0})

        sh_cx = (l_sh["x"] + r_sh["x"]) / 2.0
        sh_cy = (l_sh["y"] + r_sh["y"]) / 2.0
        hip_cx = (l_hip["x"] + r_hip["x"]) / 2.0
        hip_cy = (l_hip["y"] + r_hip["y"]) / 2.0

        sh_width = math.hypot(r_sh["x"] - l_sh["x"], r_sh["y"] - l_sh["y"])
        sh_width = max(sh_width, 0.08)
        torso_len = math.hypot(hip_cx - sh_cx, hip_cy - sh_cy) * 1.35
        torso_len = max(torso_len, 0.12)

        # Torso tilt angle
        tilt_rad = math.atan2(r_sh["y"] - l_sh["y"], r_sh["x"] - l_sh["x"])

        # Grid coordinates in [-1, 1]
        y_c = torch.linspace(-1.0, 1.0, H, device=self.device)
        x_c = torch.linspace(-1.0, 1.0, W, device=self.device)
        gy, gx = torch.meshgrid(y_c, x_c, indexing="ij")

        # Torso center in grid coords
        center_gx = sh_cx * 2.0 - 1.0
        center_gy = (sh_cy + torso_len * 0.40) * 2.0 - 1.0

        dx = gx - center_gx
        dy = gy - center_gy

        # Rotate grid to align with torso tilt
        cos_t = math.cos(-tilt_rad)
        sin_t = math.sin(-tilt_rad)
        rx = dx * cos_t - dy * sin_t
        ry = dx * sin_t + dy * cos_t

        scale_x = sh_width * 1.25
        scale_y = torso_len * 1.05

        u = rx / max(scale_x, 0.05)
        v = ry / max(scale_y, 0.05)

        # Cylindrical curvature
        curv = 0.10 * (u ** 2)
        u = u * (1.0 + curv)

        grid = torch.stack([u, v], dim=-1).unsqueeze(0)
        return grid

    def _build_sleeve_grid(
        self,
        H: int,
        W: int,
        sh_lm: Dict[str, Any],
        el_lm: Dict[str, Any],
        wr_lm: Dict[str, Any],
        is_left_arm: bool,
        anchors: Dict[str, Any]
    ) -> torch.Tensor:
        """
        Constructs sampling grid for an independently articulated sleeve.
        Sleeve origin: Shoulder joint.
        Bone vector: Shoulder -> Elbow.
        Forearm direction: Elbow -> Wrist.
        """
        sx, sy = sh_lm["x"], sh_lm["y"]
        ex, ey = el_lm["x"], el_lm["y"]
        wx, wy = wr_lm["x"], wr_lm["y"]

        # Upper arm vector and length
        v_upper_x = ex - sx
        v_upper_y = ey - sy
        upper_len = math.hypot(v_upper_x, v_upper_y)
        upper_len = max(upper_len, 0.06)

        current_angle = math.atan2(v_upper_y, v_upper_x)

        # Rest angle in reference garment photo
        # Wearer Left (image right): rest vector goes down-right (+X, +Y)
        # Wearer Right (image left): rest vector goes down-left (-X, +Y)
        if is_left_arm:
            # Wearer left sleeve rest angle (~55 degrees down-right)
            rest_angle = math.atan2(anchors["left_elbow_rest"][1] - anchors["left_shoulder"][1],
                                    anchors["left_elbow_rest"][0] - anchors["left_shoulder"][0])
            anchor_u = anchors["left_shoulder"][0] * 2.0 - 1.0
            anchor_v = anchors["left_shoulder"][1] * 2.0 - 1.0
        else:
            # Wearer right sleeve rest angle (~125 degrees down-left)
            rest_angle = math.atan2(anchors["right_elbow_rest"][1] - anchors["right_shoulder"][1],
                                    anchors["right_elbow_rest"][0] - anchors["right_shoulder"][0])
            anchor_u = anchors["right_shoulder"][0] * 2.0 - 1.0
            anchor_v = anchors["right_shoulder"][1] * 2.0 - 1.0

        delta_angle = current_angle - rest_angle

        # Elbow articulation: angle difference to forearm
        v_fore_x = wx - ex
        v_fore_y = wy - ey
        fore_angle = math.atan2(v_fore_y, v_fore_x)
        elbow_flex = (fore_angle - current_angle) * 0.35  # partial sleeve deformation toward forearm

        total_rot = delta_angle + elbow_flex

        y_c = torch.linspace(-1.0, 1.0, H, device=self.device)
        x_c = torch.linspace(-1.0, 1.0, W, device=self.device)
        gy, gx = torch.meshgrid(y_c, x_c, indexing="ij")

        # Screen coordinates relative to shoulder joint in [-1, 1] grid space
        sh_gx = sx * 2.0 - 1.0
        sh_gy = sy * 2.0 - 1.0

        dx = gx - sh_gx
        dy = gy - sh_gy

        # Inverse rotation back into garment texture coordinate space
        cos_r = math.cos(-total_rot)
        sin_r = math.sin(-total_rot)
        rx = dx * cos_r - dy * sin_r
        ry = dx * sin_r + dy * cos_r

        # Scale relative to nominal upper-arm bone length
        nominal_upper = 0.18
        scale_bone = upper_len / nominal_upper
        scale_bone = max(scale_bone, 0.5)

        sleeve_u = (rx / (0.28 * scale_bone)) + anchor_u
        sleeve_v = (ry / (0.28 * scale_bone)) + anchor_v

        grid = torch.stack([sleeve_u, sleeve_v], dim=-1).unsqueeze(0)
        return grid

    def process_frame(
        self,
        frame_bgr: np.ndarray,
        pose_landmarks: Optional[Dict[str, Any]] = None,
        segmentation_mask: Optional[np.ndarray] = None,
        garment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.initialized:
            raise RuntimeError("Rig not initialized. Call initialize() first.")

        target_id = garment_id or self.active_garment_id
        if target_id not in self.garment_data:
            raise ValueError(f"Garment '{target_id}' not loaded.")

        g_data = self.garment_data[target_id]
        t_torso = g_data["torso_tensor"]
        t_lsleeve = g_data["left_sleeve_tensor"]
        t_rsleeve = g_data["right_sleeve_tensor"]
        anchors = g_data["anchors"]

        H, W = frame_bgr.shape[:2]
        timings = {}

        t0 = time.perf_counter()
        lms = pose_landmarks or {}
        l_sh = lms.get("left_shoulder", {"x": 0.42, "y": 0.28, "z": 0.0})
        r_sh = lms.get("right_shoulder", {"x": 0.58, "y": 0.28, "z": 0.0})
        l_el = lms.get("left_elbow", {"x": 0.35, "y": 0.45, "z": 0.0})
        r_el = lms.get("right_elbow", {"x": 0.65, "y": 0.45, "z": 0.0})
        l_wr = lms.get("left_wrist", {"x": 0.32, "y": 0.60, "z": 0.0})
        r_wr = lms.get("right_wrist", {"x": 0.68, "y": 0.60, "z": 0.0})
        t1 = time.perf_counter()
        timings["preprocessing_ms"] = (t1 - t0) * 1000.0

        # Kinematic Transformations & Grid Sampling (Inference)
        t_inf_start = time.perf_counter()

        # 1. Torso Grid
        torso_grid = self._build_torso_grid(H, W, lms, anchors)
        sampled_torso = F.grid_sample(t_torso, torso_grid, mode="bilinear", padding_mode="zeros", align_corners=True)

        # 2. Wearer Left Sleeve Grid (Shoulder_L -> Elbow_L -> Wrist_L)
        # Note: Wearer Left is l_sh, l_el, l_wr
        lsleeve_grid = self._build_sleeve_grid(H, W, l_sh, l_el, l_wr, is_left_arm=True, anchors=anchors)
        sampled_lsleeve = F.grid_sample(t_lsleeve, lsleeve_grid, mode="bilinear", padding_mode="zeros", align_corners=True)

        # 3. Wearer Right Sleeve Grid (Shoulder_R -> Elbow_R -> Wrist_R)
        rsleeve_grid = self._build_sleeve_grid(H, W, r_sh, r_el, r_wr, is_left_arm=False, anchors=anchors)
        sampled_rsleeve = F.grid_sample(t_rsleeve, rsleeve_grid, mode="bilinear", padding_mode="zeros", align_corners=True)

        # Composite the 3 garment parts in PyTorch:
        # Combined RGB = sum(part_rgb * part_alpha) / sum(part_alpha + eps)
        # Combined Alpha = clamp(torso_alpha + lsleeve_alpha + rsleeve_alpha, 0, 1)
        torso_rgb = sampled_torso[:, :3]
        torso_a = sampled_torso[:, 3:4]

        lsleeve_rgb = sampled_lsleeve[:, :3]
        lsleeve_a = sampled_lsleeve[:, 3:4]

        rsleeve_rgb = sampled_rsleeve[:, :3]
        rsleeve_a = sampled_rsleeve[:, 3:4]

        total_a = (torso_a + lsleeve_a + rsleeve_a).clamp(0.0, 1.0)
        denom = (torso_a + lsleeve_a + rsleeve_a).clamp(min=1e-5)

        combined_rgb = (torso_rgb * torso_a + lsleeve_rgb * lsleeve_a + rsleeve_rgb * rsleeve_a) / denom

        t_inf_end = time.perf_counter()
        timings["kinematic_inference_ms"] = (t_inf_end - t_inf_start) * 1000.0

        # Postprocessing: Alpha compositing over input frame
        t_post_start = time.perf_counter()

        # RGB to BGR in PyTorch
        garment_bgr = combined_rgb[:, [2, 1, 0], :, :]

        frame_t = torch.from_numpy(frame_bgr.transpose(2, 0, 1)).unsqueeze(0).to(self.device).float() / 255.0

        # Forearm / hand skin occlusion: ensure skin in front of cuffs
        if segmentation_mask is not None:
            seg_t = torch.from_numpy(segmentation_mask).unsqueeze(0).unsqueeze(0).to(self.device).float()
            if seg_t.max() > 1.0:
                seg_t = seg_t / 255.0
            # Garment only renders where body is present
            total_a = total_a * seg_t

        blended_t = garment_bgr * total_a + frame_t * (1.0 - total_a)

        out_bgr = np.ascontiguousarray(
            (blended_t[0].permute(1, 2, 0).clamp(0.0, 1.0) * 255.0).byte().cpu().numpy()
        )

        t_post_end = time.perf_counter()
        timings["postprocessing_ms"] = (t_post_end - t_post_start) * 1000.0

        total_ms = timings["preprocessing_ms"] + timings["kinematic_inference_ms"] + timings["postprocessing_ms"]
        timings["total_pipeline_ms"] = total_ms

        fps = 1000.0 / max(total_ms, 0.001)

        metrics = {
            "fps": round(fps, 1),
            "timings_ms": {k: round(v, 2) for k, v in timings.items()},
            "hardware": self.get_hardware_info(),
            "articulation": {
                "left_sleeve_angle_deg": round(math.degrees(math.atan2(l_el["y"] - l_sh["y"], l_el["x"] - l_sh["x"])), 1),
                "right_sleeve_angle_deg": round(math.degrees(math.atan2(r_el["y"] - r_sh["y"], r_el["x"] - r_sh["x"])), 1),
            }
        }

        return {
            "output_frame": out_bgr,
            "metrics": metrics
        }
