# MIRAI — Hardware Wiring & Electrical Connections

## 1. Electrical & Signal Topology

```
                      [ 110V - 240V AC Mains Inlet ]
                                    │
                                    ▼
                     [ 4-Outlet Surge Protector ]
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
[ 19V / 90W DC Adapter ]  [ 12V / 3A DC Adapter ]  [ Display Power Cable ]
           │                        │                        │
           ▼                        │                        ▼
     [ Mini PC / Compute ]          │               [ 43" 4K Display ]
      ├── USB Port 1 ───────────────┼────────────────► IR Touch Frame (5V)
      ├── USB Port 2 ───────────────┼────────────────► UVC Wide-Angle Camera (5V)
      ├── USB Port 3 ───────────────┼────────────────► USB Mic Array (5V)
      ├── HDMI 2.0 Out ─────────────┼────────────────► Display HDMI In
      └── AUX Audio Out ────────────┼────────────────► Stereo Amp / Speakers
                                    ▼
                       [ Dual 120mm Cooling Fans ]
```

---

## 2. Key Connection Protocols

### 2.1 Camera Connection
- Direct USB 3.0 Type-A port connection on the motherboard (avoid passive unpowered hubs to eliminate frame dropping and bus latency).
- Cable length: ≤ 1.5m shielded cable with ferrite choke.

### 2.2 Touch Frame Connection
- USB 2.0 Type-A connection. Operates as standard plug-and-play USB HID compliant multi-touch digitizer.
- No third-party drivers required; compatible with standard Linux/Windows HID drivers.

### 2.3 Display Output
- Dedicated HDMI 2.0 output configured in OS display settings for portrait orientation:
  - Width: 1080 px
  - Height: 1920 px
  - Refresh Rate: 60 Hz
  - Color Range: Full RGB (0–255)

---

## 3. Power Distribution Rules
- Single master AC rocker switch on the bottom outer cabinet for emergency cut-off.
- No batteries in POC prototype v1; powered strictly from grounded AC mains.
- Grounding lug securely bonded to the aluminum mirror frame to prevent static buildup on the two-way glass.
