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
- `bom/`: Bill of Materials with components, suppliers, interfaces, power specs, and estimated costs.
- `diagrams/`: Electrical, signal, and USB topology schematics.
- `mechanical/`: Physical dimensions, frame mounting, bezel cutouts, and airflow cooling layout.
- `tests/`: Physical hardware verification checklists.
