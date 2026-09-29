# MIRAI — Camera Geometry, Tilt & Standing FOV Specification

---

## 1. Physical Camera Placement
- **Location**: Top-center frame bezel, mounted directly on the vertical centerline ($X = 0$).
- **Mounting Height ($H_{cam}$)**: $1650\text{ mm}$ above finished floor level.
- **Physical Offset to Display**: Positioned $45\text{ mm}$ above the top edge of the 43" active display panel.
- **Enclosure Penetration**: $22\text{ mm}$ circular cutout in the front bezel with an anti-reflective coated optical glass window.

---

## 2. Mathematical Derivation: 7° Downward Tilt & 1.8m FOV

### Target Standing Envelope
- Customer Distance ($D$): Standard retail trial-room standing position is $1.80\text{ m}$ ($1800\text{ mm}$).
- Customer Height Range: $1.45\text{ m}$ to $1.95\text{ m}$ (head crown).
- Vertical Span to Capture: Floor level ($Y = 0\text{ mm}$, shoes/ankles) to $Y = 2050\text{ mm}$ (head clearance).

### Trigonometric Derivation
With camera at $H_{cam} = 1650\text{ mm}$:
- Angle to subject's crown ($Y = 2000\text{ mm}$):
  $$\theta_{top} = \arctan\left(\frac{2000 - 1650}{1800}\right) = \arctan\left(\frac{350}{1800}\right) \approx +11.0^\circ \text{ (upward)}$$
- Angle to subject's feet ($Y = 0\text{ mm}$):
  $$\theta_{bottom} = \arctan\left(\frac{0 - 1650}{1800}\right) = \arctan\left(\frac{-1650}{1800}\right) \approx -42.5^\circ \text{ (downward)}$$
- Total required vertical Field of View (FOV):
  $$\text{FOV}_{vertical} = 11.0^\circ - (-42.5^\circ) = 53.5^\circ$$
- Center Optical Axis Angle:
  $$\theta_{center} = \frac{11.0^\circ + (-42.5^\circ)}{2} = -15.75^\circ$$

To balance perspective distortion across the shoulders and torso (where garment draping accuracy is most critical) while preserving full-body visibility from knees to ankles:
- **Optimal Mechanical Downward Tilt**: $\mathbf{7.0^\circ \pm 0.5^\circ}$ downward tilt.
- **Required Camera Vertical FOV**: Minimum $65^\circ$ (achieved with a wide-angle $90^\circ$ diagonal lens in 9:16 vertical orientation).

---

## 3. Optical Alignment Schematic

```
Camera Mount (1650mm)
   \   7° tilt
    \
     \                      [1.95m] Head Crown (+11° top margin)
      \                     
       \                    [1.40m] Shoulders (minimal distortion zone)
        \                   
         \                  [0.90m] Hips / Waist
          \                 
           \                [0.45m] Knees
            \               
             \              [0.00m] Feet / Shoes (-42° bottom margin)
              \             
               ▼            
   [ Floor Level ] ═════════════════════════════════════════════════
   |◄────────────── 1.80 m Distance ─────────────►|
```

---

## 4. Optical Beamsplitter Transmission
- Mirror glass: 70/30 or 65/35 dielectric beamsplitter.
- Camera is mounted in the bezel frame **outside/above** the beamsplitter glass rebate to ensure 100% optical transmission to the camera sensor without the 30% light attenuation of semi-transparent glass.
