# Role 4: Hardware / Embedded Engineering

**Domain Ownership**: `/hardware/**`  
**Engineer**: Founding Hardware / Embedded Intern  
**Advisors**: Chandu & Sai  

---

## Scope & Responsibilities
- Physical MIRAI smart mirror prototype design & assembly.
- Semi-transparent two-way mirror glass selection (transmission/reflectance ratios).
- High-brightness commercial display integration (portrait orientation, 9:16).
- USB camera positioning, lens FOV selection, and downward tilt angle optimization for full-body tracking at 1.5m–2.5m distance.
- IR Multi-touch frame calibration and USB HID controller integration.
- Power distribution (AC mains), cable management, and thermal dissipation/ventilation.

> **Ownership Boundary**: Hardware owns the physical apparatus, cabling, glass, mounts, and hardware validation checklists. Hardware does **not** edit `/ai/**`, `/frontend/**`, or `/backend/**`.

---

## Directory Structure
- `bom/`: [BOM.md](bom/BOM.md) with components, suppliers, interfaces, power specs, and estimated costs.
- `diagrams/`: [wiring_and_connections.md](diagrams/wiring_and_connections.md) electrical, signal, and USB topology schematics.
- `mechanical/`:
  - [enclosure_specs.md](mechanical/enclosure_specs.md): Physical dimensions, frame mounting, and airflow cooling layout.
  - [camera_geometry_and_fov.md](mechanical/camera_geometry_and_fov.md): 7° downward tilt calculation and 1.8m standing FOV envelope.
- `tests/`:
  - [hardware_checklist.md](tests/hardware_checklist.md): Physical trial-room readiness checklist.
  - [camera_display_verification_procedure.md](tests/camera_display_verification_procedure.md): Physical calibration and simulation verification protocols.
