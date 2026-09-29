# MIRAI — Physical Hardware Validation Checklist

Use this checklist prior to mounting the prototype in a trial-room environment:

---

## 1. Electrical & Power Safety
- [ ] Ground continuity verified between aluminum outer housing and electrical earth (< 0.1 Ω).
- [ ] Surge protector circuit breaker tested.
- [ ] All 12V and 19V adapters securely anchored with strain relief brackets.
- [ ] Emergency power rocker switch easily accessible on outer frame.

---

## 2. Optical & Display Verification
- [ ] Display set to 1080x1920 @ 60Hz portrait mode.
- [ ] Brightness output through 70/30 mirror glass measures > 250 nits in 400 lux ambient lighting.
- [ ] Contrast test: deep black UI backgrounds blend seamlessly into the physical mirror surface.
- [ ] No visible moiré patterns or optical distortions from glass-to-display air gap.

---

## 3. Touch Frame Calibration
- [ ] IR touch overlay recognized as USB HID digitizer on host compute.
- [ ] 4-point corner touch calibration completed.
- [ ] Touch response latency verified < 15ms without phantom touches near edges.
- [ ] Multi-touch gesture test: single tap, drag, scroll.

---

## 4. Camera FOV & Body Tracking Readiness
- [ ] USB camera recognized at 1080p / 720p @ 30+ FPS.
- [ ] Subject standing at 1.8m distance has full body visible (head to feet) in portrait frame.
- [ ] Camera downward tilt angle (6°–8°) verified to eliminate perspective warping at shoulder level.
- [ ] Low-light test: image clear without excessive sensor noise under typical store lighting (300–500 lux).

---

## 5. Thermal & Acoustics
- [ ] Dual 120mm exhaust fans operating at < 28 dBA noise floor.
- [ ] System run continuously for 4 hours; internal enclosure temperature remains below 40°C.
