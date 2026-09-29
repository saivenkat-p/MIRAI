# MIRAI — Bill of Materials (BOM) — Prototype v1 (POC)

| Category | Component / Model | Interface | Power Requirement | Mounting Requirement | Purpose | Est. Cost (USD) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Glass** | Dielectric 70/30 Beam Splitter Glass (43" 6mm tempered) | Optical surface | Passive | Custom aluminum extrusion frame rebate | Provides mirror reflection while passing through display light | $180.00 | Specified |
| **Display** | 43" 4K Commercial IPS Display (700+ nits) | HDMI 2.0 / DP | 100-240V AC (~85W) | VESA 200x200 portrait mount inside rear enclosure | Visual feedback for AR try-on and mirror UI | $350.00 | Specified |
| **Camera** | 1080p 60fps Wide-Angle UVC USB Camera (90°–100° FOV, low distortion) | USB 2.0 / 3.0 Type-A | 5V DC via USB (<500mA) | Top bezel center cutout with 6°–8° downward tilt | Ingests customer video feed for AI pose tracking | $65.00 | Sourced |
| **Touch** | 43" Infrared (IR) 10-Point Multi-touch Frame | USB 2.0 (HID standard) | 5V DC via USB (<300mA) | Flush mounted on outer edge of two-way mirror glass | Enables customer touch interaction directly on mirror surface | $110.00 | Specified |
| **Compute** | Mini PC / Laptop (Intel Core i5/i7 or AMD Ryzen 7, 16GB RAM, RTX 3050 or Iris Xe) | HDMI out, USB 3.0 in, AC in | 19V DC / 65W–120W adapter | Internal shelf / VESA mount behind display | Local real-time pose estimation and rendering compute | $600.00 | Testing |
| **Microphone** | Dual-channel USB Omnidirectional Mic Array (with DSP noise suppression) | USB 2.0 | 5V DC via USB (<100mA) | Top bezel hidden perforations | Prepares hardware for Phase 4 voice interaction | $35.00 | Sourced |
| **Audio** | Integrated 2x 10W Stereo Speakers | 3.5mm AUX / USB | 12V DC / 1.5A | Bottom enclosure grille vents | Audio cues, welcome greeting, feedback tones | $25.00 | Specified |
| **Power** | 4-Outlet Surge Protector Strip & IEC AC Inlets | AC Mains | 110V–240V AC 50/60Hz, 10A max | Bottom rear cabinet cavity | Single main AC cord power input for entire mirror | $20.00 | Acquired |
| **Cooling** | Dual 120mm Silent 12V DC Blower / Exhaust Fans | 12V DC (via DC jack) | 12V DC / 0.3A each | Top and bottom ventilation plenum | Maintains enclosure temperature <40°C during continuous operation | $25.00 | Specified |
| **Cabling** | High-speed HDMI 2.0 (1.5m), Right-angle USB 3.0 cables, Cable zip channels | Digital / Power | Passive | Internal routing channels | Clean, snag-free internal cable management | $25.00 | Acquired |
| **Frame** | Anodized Black Aluminum Extrusion Housing + VESA Bracket | Structural | N/A | Floor stand / Wall anchor mount | Rigid structural housing holding glass, display, and components | $220.00 | In Design |

**Total Estimated Prototype Hardware Cost**: ~$1,655.00
