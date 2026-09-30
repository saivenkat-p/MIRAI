"""
MIRAI VTO Engine — Step 4 Standalone Benchmarking Suite
Measures actual latency, FPS, VRAM, and GPU utilization for Tier-1 NeuralSurfaceDeformationEngine.
Saves results to backend/vto/benchmark_results.json and renders a sample output frame.
"""

import sys
import os
import time
import json
import numpy as np
import cv2

# Add parent directory to path to enable relative imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.vto.engine.neural_surface import NeuralSurfaceDeformationEngine


def run_benchmark(iterations: int = 100, frame_size=(1280, 720)):
    W, H = frame_size
    print("=" * 70)
    print("MIRAI VTO STEP 4: STANDALONE ENGINE BENCHMARK")
    print("=" * 70)

    # 1. Hardware & System Inspection
    print("[1/5] Inspecting System & Hardware...")
    engine = NeuralSurfaceDeformationEngine()
    engine.initialize()
    hw_info = engine.get_hardware_info()
    print(f"  Python Version:     {sys.version.split()[0]}")
    print(f"  PyTorch Version:    {hw_info.get('pytorch_version')}")
    print(f"  CUDA Available:     {hw_info.get('is_cuda')}")
    print(f"  Device Name:        {hw_info.get('device_name')}")
    print(f"  Total VRAM (MB):    {hw_info.get('total_vram_mb')} MB")

    # 2. Garment Asset Loading
    print("\n[2/5] Loading Primary Retail Garment Asset...")
    garment_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "garments", "camp_collar_linen_shirt.png")
    )
    if not os.path.exists(garment_path):
        print(f"ERROR: Garment asset not found at {garment_path}")
        return False

    garment_id = "OCT-SHT-002"
    engine.load_garment(garment_id, garment_path)
    print(f"  Loaded Garment:     {garment_id} (Relaxed Camp-Collar Linen Shirt)")
    print(f"  Asset File:         {garment_path}")

    # 3. Controlled Input Generation
    print("\n[3/5] Generating Controlled Test Input (1280x720)...")
    # Synthetic realistic person backdrop (neutral room tone)
    test_frame = np.full((H, W, 3), (210, 200, 190), dtype=np.uint8)

    # Simulated MediaPipe 3D pose landmarks for standing person in front of mirror
    test_landmarks = {
        "left_shoulder": {"x": 0.42, "y": 0.28, "z": -0.05},
        "right_shoulder": {"x": 0.58, "y": 0.28, "z": 0.05},
        "left_elbow": {"x": 0.35, "y": 0.45, "z": -0.10},
        "right_elbow": {"x": 0.65, "y": 0.45, "z": 0.10},
        "left_wrist": {"x": 0.32, "y": 0.60, "z": -0.15},
        "right_wrist": {"x": 0.68, "y": 0.60, "z": 0.15},
        "left_hip": {"x": 0.45, "y": 0.62, "z": 0.0},
        "right_hip": {"x": 0.55, "y": 0.62, "z": 0.0},
    }

    # Synthetic body segmentation mask (torso + arms region)
    seg_mask = np.zeros((H, W), dtype=np.uint8)
    cv2.ellipse(seg_mask, (int(W * 0.50), int(H * 0.45)), (int(W * 0.18), int(H * 0.30)), 0, 0, 360, 255, -1)

    # 4. Warmup Loop (10 iterations)
    print("\n[4/5] Priming GPU & Caches (10 warmup iterations)...")
    for _ in range(10):
        _ = engine.process_frame(test_frame, test_landmarks, seg_mask, garment_id)

    # 5. Timed Benchmark Loop
    print(f"\n[5/5] Executing {iterations} Timed Iterations...")
    pre_times = []
    inf_times = []
    post_times = []
    total_times = []

    last_result = None
    for i in range(iterations):
        res = engine.process_frame(test_frame, test_landmarks, seg_mask, garment_id)
        timings = res["metrics"]["timings_ms"]
        pre_times.append(timings["preprocessing_ms"])
        inf_times.append(timings["inference_ms"])
        post_times.append(timings["postprocessing_ms"])
        total_times.append(timings["total_pipeline_ms"])
        last_result = res

    # Compute Statistical Metrics
    def stats(arr):
        return {
            "mean": round(float(np.mean(arr)), 2),
            "median": round(float(np.median(arr)), 2),
            "min": round(float(np.min(arr)), 2),
            "max": round(float(np.max(arr)), 2),
            "p95": round(float(np.percentile(arr, 95)), 2),
        }

    summary = {
        "hardware": engine.get_hardware_info(),
        "iterations": iterations,
        "input_resolution": f"{W}x{H}",
        "garment_tested": garment_id,
        "metrics": {
            "preprocessing_ms": stats(pre_times),
            "inference_ms": stats(inf_times),
            "postprocessing_ms": stats(post_times),
            "total_pipeline_ms": stats(total_times),
            "measured_fps": round(1000.0 / float(np.mean(total_times)), 1),
        },
        "architectural_status": {
            "pytorch_gpu_grid_sample": "VERIFIED & MEASURED",
            "pose_to_surface_mapping": "VERIFIED & MEASURED",
            "densepose_checkpoint": "NOT IMPLEMENTED — ARCHITECTURAL PLACEHOLDER",
            "tensorrt_fp16": "NOT IMPLEMENTED — ARCHITECTURAL PLACEHOLDER",
            "cloth_physics_wrinkle_synthesis": "NOT IMPLEMENTED — ARCHITECTURAL PLACEHOLDER",
        }
    }

    # Save output benchmark image
    output_dir = os.path.dirname(os.path.abspath(__file__))
    sample_img_path = os.path.join(output_dir, "benchmark_output.jpg")
    cv2.imwrite(sample_img_path, last_result["output_frame"])

    # Save JSON results
    results_json_path = os.path.join(output_dir, "benchmark_results.json")
    with open(results_json_path, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 70)
    print("BENCHMARK RESULTS SUMMARY")
    print("=" * 70)
    print(f"Device:                 {summary['hardware']['device_name']}")
    print(f"Is CUDA:                {summary['hardware']['is_cuda']}")
    print(f"Preprocessing:          {summary['metrics']['preprocessing_ms']['mean']} ms (p95: {summary['metrics']['preprocessing_ms']['p95']} ms)")
    print(f"GPU Inference:          {summary['metrics']['inference_ms']['mean']} ms (p95: {summary['metrics']['inference_ms']['p95']} ms)")
    print(f"Postprocessing/Blend:   {summary['metrics']['postprocessing_ms']['mean']} ms (p95: {summary['metrics']['postprocessing_ms']['p95']} ms)")
    print(f"Total Pipeline Latency: {summary['metrics']['total_pipeline_ms']['mean']} ms (p95: {summary['metrics']['total_pipeline_ms']['p95']} ms)")
    print(f"Measured FPS:           {summary['metrics']['measured_fps']} FPS")
    if summary['hardware']['is_cuda']:
        print(f"VRAM Allocated:         {summary['hardware'].get('vram_allocated_mb', 0)} MB")
        print(f"VRAM Reserved:          {summary['hardware'].get('vram_reserved_mb', 0)} MB")
    print(f"Output Sample Saved:    {sample_img_path}")
    print(f"Results JSON Saved:     {results_json_path}")
    print("=" * 70)

    return True


if __name__ == "__main__":
    run_benchmark(iterations=50)
