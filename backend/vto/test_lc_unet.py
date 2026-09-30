"""
Step 6.5 Architectural Verification: Concrete LC-UNet Profiling Script
Measures actual parameter count, FP32/FP16 tensor memory, and forward-pass latency.
"""

import time
import torch
import torch.nn as nn
import torch.nn.functional as F

class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )
    def forward(self, x):
        return self.net(x)

class LightweightConditionalUNet(nn.Module):
    """
    Proposed LC-UNet Architecture for Garment Refinement.
    Input Channels (10 total):
      - 3 channels: Coarse geometrically warped garment prior (RGB)
      - 1 channel:  Warped garment alpha mask
      - 3 channels: Body-agnostic camera frame (wearer shirt masked/erased)
      - 3 channels: DensePose / Pose joint heatmap / edge representation
    Output Channels (4 total):
      - 3 channels: Refined garment appearance (RGB) with dynamic wrinkles/folds
      - 1 channel:  Refined alpha mask
    """
    def __init__(self, in_channels=10, out_channels=4, base_ch=32):
        super().__init__()
        # Encoder (Downsampling)
        self.inc = DoubleConv(in_channels, base_ch)            # 32
        self.down1 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(base_ch, base_ch * 2))       # 64
        self.down2 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(base_ch * 2, base_ch * 4))   # 128
        self.down3 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(base_ch * 4, base_ch * 8))   # 256
        
        # Bottleneck
        self.bot = nn.Sequential(nn.MaxPool2d(2), DoubleConv(base_ch * 8, base_ch * 16))    # 512

        # Decoder (Upsampling with Skip Connections)
        self.up1 = nn.ConvTranspose2d(base_ch * 16, base_ch * 8, kernel_size=2, stride=2)
        self.conv1 = DoubleConv(base_ch * 16, base_ch * 8)

        self.up2 = nn.ConvTranspose2d(base_ch * 8, base_ch * 4, kernel_size=2, stride=2)
        self.conv2 = DoubleConv(base_ch * 8, base_ch * 4)

        self.up3 = nn.ConvTranspose2d(base_ch * 4, base_ch * 2, kernel_size=2, stride=2)
        self.conv3 = DoubleConv(base_ch * 4, base_ch * 2)

        self.up4 = nn.ConvTranspose2d(base_ch * 2, base_ch, kernel_size=2, stride=2)
        self.conv4 = DoubleConv(base_ch * 2, base_ch)

        self.outc = nn.Conv2d(base_ch, out_channels, kernel_size=1)

    def forward(self, x):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.bot(x4)

        x = self.up1(x5)
        x = self.conv1(torch.cat([x, x4], dim=1))
        x = self.up2(x)
        x = self.conv2(torch.cat([x, x3], dim=1))
        x = self.up3(x)
        x = self.conv3(torch.cat([x, x2], dim=1))
        x = self.up4(x)
        x = self.conv4(torch.cat([x, x1], dim=1))
        return self.outc(x)

def profile_model():
    print("=" * 65)
    print("STEP 6.5: PROFILING CONCRETE LC-UNET ARCHITECTURE")
    print("=" * 65)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Profiling Device: {device}")

    model = LightweightConditionalUNet(in_channels=10, out_channels=4, base_ch=32).to(device)
    model.eval()

    # 1. Parameter Count
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    weight_mem_fp32_mb = total_params * 4 / (1024 * 1024)
    weight_mem_fp16_mb = total_params * 2 / (1024 * 1024)

    print(f"\n[1] Parameter Count:")
    print(f"    Total Parameters:      {total_params:,} ({total_params/1e6:.2f} Million)")
    print(f"    Trainable Parameters:  {trainable_params:,}")
    print(f"    Weights Memory (FP32): {weight_mem_fp32_mb:.2f} MB")
    print(f"    Weights Memory (FP16): {weight_mem_fp16_mb:.2f} MB")

    # 2. Forward Pass at Target Resolutions
    resolutions = [
        (384, 288),  # Low-res real-time proxy (4:3)
        (512, 384),  # Standard proposed resolution
        (768, 512),  # High-fidelity target
    ]

    print("\n[2] Forward Pass Latency & Memory Profiling:")
    for H, W in resolutions:
        dummy_input = torch.randn(1, 10, H, W, device=device)
        
        # Warmup
        for _ in range(5):
            with torch.no_grad():
                _ = model(dummy_input)

        # Timed Loop (20 iterations)
        timings = []
        for _ in range(20):
            t0 = time.perf_counter()
            with torch.no_grad():
                out = model(dummy_input)
            t1 = time.perf_counter()
            timings.append((t1 - t0) * 1000.0)

        mean_ms = sum(timings) / len(timings)
        fps = 1000.0 / mean_ms
        act_mem_fp32_mb = (dummy_input.numel() + out.numel()) * 4 / (1024 * 1024)

        print(f"    Resolution {W}x{H}:")
        print(f"      Mean Latency:    {mean_ms:.2f} ms")
        print(f"      Estimated FPS:   {fps:.1f} FPS (Inference Only, excludes pre/post)")
        print(f"      I/O Tensor RAM:  {act_mem_fp32_mb:.2f} MB")

    print("=" * 65)

if __name__ == "__main__":
    profile_model()
