# MIRAI — Team Roles & Ownership Matrix

---

## 1. Engineering Team Structure

The MIRAI engineering team consists of four primary roles operating under a strict domain-ownership model:

- **Lead / Product / Architecture**: Sai
- **Hardware Advisor**: Chandu
- **Role 1**: Founding AI / Computer Vision Intern
- **Role 2**: Founding Frontend / AR Intern
- **Role 3**: Founding Backend Intern
- **Role 4**: Founding Hardware / Embedded Intern

---

## 2. Absolute Ownership Matrix

| Role | Authorized Write Area | Primary Responsibilities | Forbidden Write Areas |
| :--- | :--- | :--- | :--- |
| **Role 1: AI / Computer Vision** | `/ai/**` | Camera frame ingestion, pose estimation, landmark detection, coordinate normalization, tracking confidence, jitter smoothing | `/frontend/**`<br>`/backend/**`<br>`/hardware/**` |
| **Role 2: Frontend / AR** | `/frontend/**` | Smart mirror UI (1080x1920 portrait), WebGL/Canvas garment overlay, touch controls, lookbook, tracking visualizer | `/ai/**`<br>`/backend/**`<br>`/hardware/**` |
| **Role 3: Backend** | `/backend/**` | Product catalog, inventory, store data, session management, saved looks, analytics API, FastAPI/database | `/ai/**`<br>`/frontend/**`<br>`/hardware/**` |
| **Role 4: Hardware / Embedded** | `/hardware/**` | Mirror glass selection (semi-transparent), display integration, camera FOV & positioning, IR touch frame, BOM, thermal management | `/ai/**`<br>`/frontend/**`<br>`/backend/**` |

---

## 3. Strict Rules of Engagement

1. **Read Access ≠ Write Access**: Any engineer can read another domain's code to understand interfaces, but must **never** modify, refactor, or delete files outside their authorized directory.
2. **No Duplicate Implementations**:
   - Frontend must never implement its own pose detection.
   - Backend must never process camera frames or render graphics.
   - AI must never build a UI or database.
   - Hardware drivers are encapsulated; software interfaces with standard OS USB/video devices.
3. **Cross-Team Protocol**:
   - If a change is needed across boundaries:
     1. Stop immediately.
     2. Report: `OWNERSHIP BOUNDARY REACHED`.
     3. Document the required interface change in `/docs/INTEGRATION_CONTRACTS.md`.
     4. Notify the owning role.
     5. The owning role updates its implementation.
     6. Requesting role adapts its consumer code.

---

## 4. Branch Ownership Conventions

- `main`: Protected production branch (requires Lead review).
- `develop`: Integration branch.
- `role/ai`: Exclusively for Role 1.
- `role/frontend`: Exclusively for Role 2.
- `role/backend`: Exclusively for Role 3.
- `role/hardware`: Exclusively for Role 4.
