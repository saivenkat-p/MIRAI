"""
NeuralSurfaceDeformationEngine — Tier-1 Standalone VTO Inference Engine for MIRAI
Implements the IVTOEngine Hardware Abstraction Layer.
Uses PyTorch GPU grid sampling to compute non-linear cloth deformation flows.
"""

import time
import json
import os
from typing import Dict, Any, Optional, Tuple
import cv2
import numpy as np

try:
    import torch
    import torch.nn.functional as F
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


from .base import IVTOEngine


class NeuralSurfaceDeformationEngine(IVTOEngine):
    """
    Tier-1 Engine: GPU-accelerated continuous surface deformation field.
    Bridges 3D pose landmarks and photographic garment texture via
    bilinear GPU grid-sampling.
    """

    def __init__(self):
        self.device = None
        self.device_name = "Not Initialized"
        self.total_vram_mb = 0.0
        self.is_cuda = False
        self.cached_garments: Dict[str, Dict[str, Any]] = {}
        self.active_garment_id = None
        self.initialized = False

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        if not HAS_TORCH:
            raise RuntimeError("PyTorch is required for NeuralSurfaceDeformationEngine.")

        if torch.cuda.is_available():
            self.device = torch.device("cuda:0")
            self.device_name = torch.cuda.get_device_name(0)
            self.total_vram_mb = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
            self.is_cuda = True
            # Warm up CUDA context
            _ = torch.zeros((1, 3, 256, 256), device=self.device)
            torch.cuda.synchronize()
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
            raise FileNotFoundError(f"Garment asset not found at {garment_path}")

        img_rgba = cv2.imread(garment_path, cv2.IMREAD_UNCHANGED)
        if img_rgba is None:
            raise ValueError(f"Failed to decode image from {garment_path}")

        # Ensure 4-channel RGBA
        if img_rgba.shape[2] == 3:
            alpha = np.ones((img_rgba.shape[0], img_rgba.shape[1], 1), dtype=img_rgba.dtype) * 255
            img_rgba = np.concatenate([img_rgba, alpha], axis=2)

        h, w = img_rgba.shape[:2]

        # Convert to RGB (from BGR) and keep Alpha
        img_rgb = cv2.cvtColor(img_rgba[:, :, :3], cv2.COLOR_BGR2RGB)
        alpha = img_rgba[:, :, 3:4]
        combined = np.concatenate([img_rgb, alpha], axis=2)  # H x W x 4 (RGBA)

        # PyTorch Tensor: (1, 4, H, W) normalized to [0, 1]
        tensor = torch.from_numpy(combined.transpose(2, 0, 1)).float() / 255.0
        tensor = tensor.unsqueeze(0).to(self.device)

        default_anchors = {
            "collar_center": (0.50, 0.30),
            "left_shoulder": (0.30, 0.31),
            "right_shoulder": (0.70, 0.31),
            "left_sleeve_tip": (0.06, 0.39),
            "right_sleeve_tip": (0.94, 0.39),
            "hem_center": (0.50, 0.92),
        }

        self.cached_garments[garment_id] = {
            "tensor": tensor,
            "orig_size": (w, h),
            "anchors": metadata.get("anchors", default_anchors) if metadata else default_anchors,
        }
        self.active_garment_id = garment_id
        return True

    def _compute_surface_grid(
        self,
        frame_shape: Tuple[int, int],
        landmarks: Dict[str, Any],
        anchors: Dict[str, Any]
    ) -> torch.Tensor:
        """
        Builds a GPU tensor grid [-1, 1] mapping each output screen pixel
        to corresponding coordinates in garment texture UV space.
        """
        H, W = frame_shape

        # Extract normalized pose landmarks (default to nominal standing pose if missing)
        l_sh = landmarks.get("left_shoulder", {"x": 0.40, "y": 0.30, "z": 0.0})
        r_sh = landmarks.get("right_shoulder", {"x": 0.60, "y": 0.30, "z": 0.0})
        l_hip = landmarks.get("left_hip", {"x": 0.43, "y": 0.65, "z": 0.0})
        r_hip = landmarks.get("right_hip", {"x": 0.57, "y": 0.65, "z": 0.0})
        l_el = landmarks.get("left_elbow", {"x": 0.32, "y": 0.45, "z": 0.0})
        r_el = landmarks.get("right_elbow", {"x": 0.68, "y": 0.45, "z": 0.0})

        # Body center and dimensions in screen space [0, 1]
        sh_center_x = (l_sh["x"] + r_sh["x"]) / 2.0
        sh_center_y = (l_sh["y"] + r_sh["y"]) / 2.0
        hip_center_x = (l_hip["x"] + r_hip["x"]) / 2.0
        hip_center_y = (l_hip["y"] + r_hip["y"]) / 2.0

        sh_width = np.hypot(r_sh["x"] - l_sh["x"], r_sh["y"] - l_sh["y"])
        torso_height = np.hypot(hip_center_x - sh_center_x, hip_center_y - sh_center_y) * 1.35
        sh_width = max(sh_width, 0.10)
        torso_height = max(torso_height, 0.15)

        # Generate base coordinate meshgrid on target device
        # Normalised screen coordinates in [-1, 1]
        y_coords = torch.linspace(-1.0, 1.0, H, device=self.device, dtype=torch.float32)
        x_coords = torch.linspace(-1.0, 1.0, W, device=self.device, dtype=torch.float32)
        grid_y, grid_x = torch.meshgrid(y_coords, x_coords, indexing="ij")

        # Convert normalized pose coordinates from [0, 1] to [-1, 1] grid space
        c_x = sh_center_x * 2.0 - 1.0
        c_y = sh_center_y * 2.0 - 1.0 + (torso_height * 0.4) * 2.0

        scale_x = sh_width * 1.55
        scale_y = torso_height * 1.05

        # Compute displacement in grid units
        dx = (grid_x - c_x) / max(scale_x, 0.05)
        dy = (grid_y - c_y) / max(scale_y, 0.05)

        # 3D Cylindrical Perspective Compensation:
        # Warp x based on distance from center line to simulate chest curvature
        curvature = 0.12 * (dx ** 2)
        u = dx * (1.0 + curvature)
        v = dy

        # Stack into (1, H, W, 2) grid expected by grid_sample
        grid = torch.stack([u, v], dim=-1).unsqueeze(0)
        return grid

    def process_frame(
        self,
        frame_bgr: np.ndarray,
        pose_landmarks: Optional[Dict[str, Any]] = None,
        segmentation_mask: Optional[np.ndarray] = None,
        garment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.initialized:
            raise RuntimeError("Engine not initialized. Call initialize() first.")

        target_garment_id = garment_id or self.active_garment_id
        if target_garment_id not in self.cached_garments:
            raise ValueError(f"Garment '{target_garment_id}' is not loaded.")

        garment_entry = self.cached_garments[target_garment_id]
        garment_tensor = garment_entry["tensor"]
        anchors = garment_entry["anchors"]

        H, W = frame_bgr.shape[:2]
        timings = {}

        # 1. Preprocessing Stage
        t0 = time.perf_counter()
        landmarks = pose_landmarks or {}
        t1 = time.perf_counter()
        timings["preprocessing_ms"] = (t1 - t0) * 1000.0

        # 2. Neural Surface Deformation Inference Stage (PyTorch GPU)
        if self.is_cuda:
            start_event = torch.cuda.Event(enable_timing=True)
            end_event = torch.cuda.Event(enable_timing=True)
            start_event.record()
        else:
            t_inf_start = time.perf_counter()

        flow_grid = self._compute_surface_grid((H, W), landmarks, anchors)

        # Bilinear texture sampling on GPU
        # garment_tensor is (1, 4, Gh, Gw), flow_grid is (1, H, W, 2)
        sampled_rgba = F.grid_sample(
            garment_tensor,
            flow_grid,
            mode="bilinear",
            padding_mode="zeros",
            align_corners=True
        )

        if self.is_cuda:
            end_event.record()
            torch.cuda.synchronize()
            timings["inference_ms"] = start_event.elapsed_time(end_event)
        else:
            t_inf_end = time.perf_counter()
            timings["inference_ms"] = (t_inf_end - t_inf_start) * 1000.0

        # 3. Postprocessing & Compositing Stage
        t_post_start = time.perf_counter()

        # sampled_rgba is (1, 4, H, W) in RGB + A on self.device
        # We store garment in RGB; let's convert frame_bgr to tensor or blend efficiently
        garment_rgb = sampled_rgba[:, :3, :, :]   # (1, 3, H, W) in RGB
        garment_alpha = sampled_rgba[:, 3:4, :, :] # (1, 1, H, W) in [0, 1]

        # Convert garment_rgb from RGB to BGR in PyTorch by swapping channels 0 and 2
        garment_bgr = garment_rgb[:, [2, 1, 0], :, :]

        # Frame tensor on self.device
        frame_tensor = torch.from_numpy(frame_bgr.transpose(2, 0, 1)).unsqueeze(0).to(self.device).float() / 255.0

        if segmentation_mask is not None:
            mask_t = torch.from_numpy(segmentation_mask).unsqueeze(0).unsqueeze(0).to(self.device).float()
            if mask_t.max() > 1.0:
                mask_t = mask_t / 255.0
            garment_alpha = garment_alpha * mask_t

        # Fast vectorized alpha blend directly in PyTorch
        blended_t = garment_bgr * garment_alpha + frame_tensor * (1.0 - garment_alpha)

        # Output uint8 BGR (ensuring contiguous memory layout for OpenCV)
        output_bgr = np.ascontiguousarray(
            (blended_t[0].permute(1, 2, 0).clamp(0.0, 1.0) * 255.0).byte().cpu().numpy()
        )

        t_post_end = time.perf_counter()
        timings["postprocessing_ms"] = (t_post_end - t_post_start) * 1000.0

        total_ms = timings["preprocessing_ms"] + timings["inference_ms"] + timings["postprocessing_ms"]
        timings["total_pipeline_ms"] = total_ms

        fps = 1000.0 / max(total_ms, 0.001)

        metrics = {
            "fps": round(fps, 1),
            "timings_ms": {k: round(v, 2) for k, v in timings.items()},
            "hardware": self.get_hardware_info(),
        }

        return {
            "output_frame": output_bgr,
            "metrics": metrics
        }
