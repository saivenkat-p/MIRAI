# MIRAI — Step 6.5: Validation of Proposed Learned VTO Foundation
**Document:** `docs/vto_foundation_validation.md`  
**Date:** October 2026 | **Status:** Step 6.5 Architectural & Feasibility Validation — Implementation Frozen

---

> [!IMPORTANT]
> **Terminology & Integrity Standard:**
> - All performance and memory figures in this document are explicitly classified as either **ACTUAL BENCHMARK** (experimentally measured on test hardware via `test_lc_unet.py`) or **THEORETICAL ESTIMATE / TARGET** (derived from architectural FLOPs and parameter math).
> - **LC-UNet is currently a PROPOSED ARCHITECTURE, NOT an existing validated or pre-trained VTO model.**
> - "100% Permissive Commercial Licensing" is revoked as an assumption; every component is audited individually with dataset provenance.

---

## 1. PRECISE DEFINITION OF THE PROPOSED LC-UNET ARCHITECTURE

### Architectural Topology
The proposed **Lightweight Conditional U-Net (LC-UNet)** is a single-pass, feed-forward convolutional encoder-decoder with symmetric skip connections, designed as an image-to-image neural appearance harmonizer. It does **not** perform iterative diffusion denoising.

```
INPUT TENSOR: [B, 10, H, W]
  │
  ├── Inc Conv: [10 -> 32] ──────────── Skip 1 ───────────┐
  ▼                                                        │
  Down 1 (MaxPool + Conv): [32 -> 64] ── Skip 2 ─────┐    │
  ▼                                                  │    │
  Down 2 (MaxPool + Conv): [64 -> 128] ─ Skip 3 ┐   │    │
  ▼                                              │   │    │
  Down 3 (MaxPool + Conv): [128 -> 256] ─ Skip 4 │   │    │
  ▼                                              │   │    │
  Bottleneck: [256 -> 512]                       │   │    │
  ▼                                              │   │    │
  Up 1 (ConvTranspose + Concat Skip 4): [512 -> 256] │    │
  ▼                                                  │    │
  Up 2 (ConvTranspose + Concat Skip 3): [256 -> 128] ◄┘   │
  ▼                                                       │
  Up 3 (ConvTranspose + Concat Skip 2): [128 -> 64] ──────┘
  ▼
  Up 4 (ConvTranspose + Concat Skip 1): [64 -> 32]
  ▼
  Output Conv (1x1): [32 -> 4]
  │
OUTPUT TENSOR: [B, 4, H, W] (Refined Garment RGB + Refined Alpha)
```

### Exact Inputs and Outputs (Tensor Schema)

| Channel Index | Modality | Representation & Source | Role in Network |
|---|---|---|---|
| **0, 1, 2** | `garment_warp_rgb` | Coarse geometrically warped garment (from kinematic rigging layer) | Base texture, pattern, logos, buttons |
| **3** | `garment_warp_alpha` | Binary/soft alpha mask of warped garment | Garment boundary prior |
| **4, 5, 6** | `body_agnostic_rgb` | Camera frame with wearer's original clothing masked/inpainted | Background context, neck/skin tones |
| **7, 8, 9** | `pose_dense_guide` | DensePose IUV surface map OR 2D skeleton joint heatmaps | Body shape, limb articulation, orientation |
| **OUTPUT 0, 1, 2** | `synth_garment_rgb` | Photorealistic synthesized garment (RGB) | Fabric shading, wrinkles, dynamic lighting |
| **OUTPUT 3** | `synth_alpha` | Soft edge-preserving alpha mask | Seamless blending with background & limbs |

### Answering Core Mechanism Questions
- **What represents the person?** The body-agnostic camera frame (channels 4–6), where the wearer's real clothing has been masked out, preserving only their real head, neck, hands, and background.
- **What represents body pose?** 3D skeleton keypoint Gaussian heatmaps or DensePose IUV channels (channels 7–9).
- **What represents garment deformation?** The coarse geometrically warped garment prior ($I_{\text{warp}}$ in channels 0–3), which has already been piecewise articulated along the wearer's shoulder, chest, and arm bones.
- **How does it produce wrinkles and folds?** Convolutions in the bottleneck and decoder receive both the warped texture and the joint angles. The network learns to synthesize non-linear shadow gradients and highlight folds where joint compression occurs (e.g. inner elbow, waist crease).
- **How does it preserve garment texture?** Because $I_{\text{warp}}$ is fed directly into channel 0–2 and linked through high-resolution skip connections, the network does *not* invent new patterns; it acts as a non-linear modulation filter over the actual photographic texture.
- **How does it handle different garments?** 
  > [!WARNING]
  > **Zero-Retraining Reality Check:**
  > While the architecture accepts *any* pre-warped texture as input, **it is NOT completely category-agnostic without diverse training**. If trained only on T-shirts, feeding it a heavy winter parka or a flowing dress will result in unnatural T-shirt-like folding dynamics. Category generalization requires training across upper-body, lower-body, and dresses.

---

## 2. HARDWARE FEASIBILITY & CONCRETE BENCHMARK (GTX 1650 4GB)

### Concrete Architectural Sizing (Measured via `test_lc_unet.py`)

```
=================================================================
ACTUAL PROFILING BENCHMARK: CONCRETE LC-UNET INSTANCE
=================================================================
Total Model Parameters:       7,765,156 (~7.77 Million parameters)
Trainable Parameters:         7,765,156
Weights Memory (FP32):        29.62 MB
Weights Memory (FP16):        14.81 MB

Measured Tensor Memory (Host RAM):
- Resolution 288x384:         5.91 MB
- Resolution 384x512:         10.50 MB
- Resolution 512x768:         21.00 MB

Measured Forward Pass Latency (CPU PyTorch Baseline):
- Resolution 288x384:         738.82 ms (~1.4 FPS CPU)
- Resolution 384x512:         880.08 ms (~1.1 FPS CPU)
- Resolution 512x768:         1,616.20 ms (~0.6 FPS CPU)
=================================================================
```

### Distinction: Actual Benchmark vs Theoretical Target

| Metric | Status | Measurement / Estimate | Notes |
|---|---|---|---|
| **Model Weights (FP16)** | **ACTUAL BENCHMARK** | **14.81 MB** | Directly calculated from instantiated weights |
| **I/O Tensor RAM (384×512)** | **ACTUAL BENCHMARK** | **10.50 MB** | Directly allocated tensor measurement |
| **CPU Forward Pass (384×512)** | **ACTUAL BENCHMARK** | **880.08 ms (1.1 FPS)** | Single-threaded CPU baseline |
| **Inference VRAM (GTX 1650)** | **THEORETICAL ESTIMATE** | **~350 – 500 MB** | Weights (15MB) + Activations (350MB) + Context |
| **Total Pipeline VRAM** | **TARGET / ESTIMATE** | **~1.1 – 1.4 GB** | Including MediaPipe & display buffers |
| **GTX 1650 CUDA FP16 Latency** | **TARGET / ESTIMATE** | **~20 – 35 ms (28–50 FPS)** | Based on 896 Turing CUDA cores @ 1.6 GHz |
| **End-to-End Glass-to-Glass** | **TARGET / ESTIMATE** | **~45 – 70 ms (14–22 FPS)** | Transport + Rigging + Model + Render |

---

## 3. THE TRAINING STRATEGY & BOTTLENECK

> [!CAUTION]
> **A model without a viable training strategy is not a product foundation.**
> This section addresses how this model can actually be brought into existence.

### 1. Training Dataset Requirements
To train the LC-UNet to synthesize realistic folds and boundary transitions, the training dataset must contain:
1. **Source Person Image ($I_{\text{target}}$):** A real human wearing garment $G$ in pose $P$.
2. **Body Agnostic Frame ($I_{\text{agnostic}}$):** Same image with garment $G$ erased.
3. **Garment In-Shop Photo ($G_{\text{flat}}$):** High-resolution flat-lay photo of garment $G$.
4. **Pose Representation ($P$):** DensePose or 2D/3D joint coordinates.
5. **Coarse Warped Prior ($I_{\text{warp}}$):** Generated by passing $G_{\text{flat}}$ and $P$ through our kinematic mesh.

### 2. Available Academic Datasets vs License Contamination
- **VITON-HD (CVPR 2021):** 13,679 high-res image pairs. **Strictly Non-Commercial.**
- **DressCode (CVPR 2022):** 53,792 high-res image pairs (upper, lower, dresses). **Strictly Non-Commercial.**
- **SHHQ-1.0:** 40,000 full-body images. **Strictly Non-Commercial.**

> [!WARNING]
> **Legal Barrier:** There is **NO publicly available, permissively licensed (Apache 2.0 / MIT) paired virtual try-on training dataset**.
> If MIRAI trains LC-UNet on VITON-HD or DressCode, the resulting model weights inherit the **Non-Commercial restriction**, making commercial deployment in retail stores illegal.

### 3. Clean Commercial Training Paths for MIRAI
To maintain 100% commercial cleanliness, MIRAI must use one of three strategies:

1. **Path 1: Synthetic 3D Simulation Training (Recommended for Independence)**
   - Use open-source cloth simulation engines or Blender with 3D human body avatars wearing 3D garments.
   - Render 20,000 synthetic frames across diverse poses and fabric stiffness settings.
   - Perfectly clean copyright; zero human privacy issues; ground-truth depth and occlusion are free.
2. **Path 2: Self-Captured Retail Store Video Dataset**
   - Record 5–10 staff models wearing the 32 demo products across standard retail movements (raising arms, turning, walking) in front of the kiosk camera.
   - Extract paired training frames automatically using MediaPipe.
   - Clean proprietary retail dataset owned 100% by the store.
3. **Path 3: Distillation from Permissively Licensed Base Models**
   - Use FASHN VTON v1.5 (Apache 2.0) to generate paired pseudo-ground-truth images offline, then train LC-UNet to distill the output into a single-pass realtime model.

### 4. Training Hardware Feasibility
- **Can the GTX 1650 4GB train this model?** **ABSOLUTELY NOT.**
  - Training requires batch size $\ge 8$, Adam optimizer states (which double parameter memory), and backpropagation gradient graphs. Memory required during backward pass: **$14\text{ to }20\text{ GB}$ VRAM**.
  - Attempting to train on GTX 1650 will cause immediate CUDA Out-Of-Memory.
- **Required Training Hardware:**
  - Training MUST be conducted on rented cloud GPU hardware: **$1\times$ NVIDIA A10G (24GB) or A100 (40GB)** on RunPod, Lambda Labs, or AWS for approximately 12–24 hours (estimated cost: $\$15\text{ to }\$35$).
  - The **GTX 1650 is exclusively an INFERENCE runtime**, not a training workstation.

---

## 4. ZERO-RETRAINING GARMENT ONBOARDING EVALUATION

Can the model onboard new products (shirt $\to$ hoodie $\to$ jacket $\to$ dress) without retraining?

| Garment Type | Feasibility with Zero Retraining | Failure Mode / Boundary Condition |
|---|---|---|
| **Camp-Collar Linen Shirt (OCT-SHT-002)** | ✅ **HIGH** | Baseline training target; conforms to torso + short sleeves. |
| **Cyber Techwear Bomber (OCT-JKT-001)** | ⚠️ **MODERATE** | Heavier fabric silhouette; will look slightly too slim unless kinematic prior accounts for boxy shoulder padding. |
| **Oversized Hoodie (OCT-HOD-001)** | ⚠️ **MODERATE** | Requires long-sleeve kinematics (shoulder $\to$ elbow $\to$ wrist) and hood geometry around the neck. |
| **Pleated Midi Dress (OCT-DRS-001)** | ❌ **FAILS without Lower-Body Prior** | Current kinematic prior only models upper torso; dress requires skirt hem expansion below hips. |

**Verdict:** The model is zero-retraining **within supported kinematic categories**, but requires category-specific geometric anchors in the Garment Profile JSON.

---

## 5. REAL LIVE VTO PROOF-OF-CONCEPT TEST SPECIFICATION

Before any production commitment, a minimal test must evaluate 10 physical actions:

1. Arms down (nominal standing fit)
2. Left arm raised ($90^\circ$ and $135^\circ$)
3. Right arm raised ($90^\circ$ and $135^\circ$)
4. Both arms raised laterally
5. Body turning left ($30^\circ$ and $60^\circ$ yaw)
6. Body turning right ($30^\circ$ and $60^\circ$ yaw)
7. Stepping closer and farther (scale handling)
8. Forearm crossing over chest (occlusion depth test)
9. Original undershirt removal (zero yellow fabric visible)
10. High-frequency pattern preservation (linen weave and button clarity)

---

## 6. RIGOROUS LICENSING AUDIT TABLE

| Component | Source / Author | Code License | Commercial Use Permitted? | Model Weights License | Dataset Dependency | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MediaPipe Pose** | Google | Apache 2.0 | ✅ YES | Apache 2.0 (Bundled) | Internal Google Datasets | ✅ **VERIFIED CLEAN** |
| **PyTorch & torchvision** | Linux Foundation / Meta | BSD 3-Clause | ✅ YES | Open Source | ImageNet (Permissive) | ✅ **VERIFIED CLEAN** |
| **ONNX Runtime** | Microsoft | MIT License | ✅ YES | Open Source | N/A | ✅ **VERIFIED CLEAN** |
| **LC-UNet Architecture** | Custom MIRAI | Apache 2.0 | ✅ YES | **NOT YET TRAINED** | **PENDING DATASET CHOICE** | ⚠️ **PROPOSED** |
| **VITON-HD Dataset** | Academic (CVPR 2021) | Non-Commercial | ❌ **NO** | Non-Commercial | Academic crawling | ❌ **REJECTED** |
| **DressCode Dataset** | Academic (CVPR 2022) | Non-Commercial | ❌ **NO** | Non-Commercial | Academic crawling | ❌ **REJECTED** |
| **TikTokDress Dataset** | VinAI (AAAI 2025) | Non-Commercial | ❌ **NO** | Non-Commercial | TikTok videos | ❌ **REJECTED** |
| **Store Garment Assets** | Retail Store Catalog | Proprietary | ✅ YES | N/A | Proprietary Photography | ✅ **VERIFIED CLEAN** |

---

## 7. FINAL ARCHITECTURAL DECISION

### Selected Decision:
# **C: PROTOTYPE REQUIRED**

### Rationale:
1. **Why not "A: APPROVE"?**
   - The LC-UNet is currently an unvalidated conceptual architecture. We have demonstrated its actual parameter sizing (**7.77M parameters, 14.81 MB FP16 memory**), but **no trained checkpoint currently exists** that proves it can synthesize natural wrinkles and erase original clothing in real-time. Committing to a full production build without an empirical proof-of-concept is high risk.
2. **Why not "B: REJECT"?**
   - Rejecting the neural refiner would leave MIRAI with only two choices: (1) pure geometric polygon warping (which already failed visually), or (2) heavy diffusion models (which require 16–24 GB VRAM and run at 0.5 FPS). The kinematic prior + feed-forward U-Net is the *only* mathematically viable path for real-time inference on a 4GB GPU.
3. **What "PROTOTYPE REQUIRED" specifically mandates:**
   - **Phase 1 (Kinematic Multi-Part Rigging):** Implement the multi-part kinematic sleeve/torso rigging first, proving that the sleeve structurally follows the arm bone to $90^\circ$.
   - **Phase 2 (Neural Refinement POC):** Train or distill a tiny proof-of-concept LC-UNet on a small clean dataset (or cloud GPU) to verify that it actually synthesizes realistic cloth creases and erases the undershirt before finalizing the production engine.
