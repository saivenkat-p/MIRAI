/**
 * MIRAI — Garment SVG Asset Generator
 *
 * Generates color-parameterized SVG garment assets for live AR rendering.
 * Each SVG is designed with specific shoulder anchor coordinates so the
 * GarmentRenderer2D can align it precisely to MediaPipe pose landmarks.
 *
 * SVG coordinate spec (all assets share the same anchor system):
 *   viewBox  : "0 0 1000 1200"
 *   Left shoulder  : x=175, y=250   (landmark id 11)
 *   Right shoulder : x=825, y=250   (landmark id 12)
 *   Shoulder span  : 650 px  ← renderer uses this to compute scale
 *   Shoulder mid   : x=500, y=250   ← renderer places this at landmark midpoint
 *
 * Lower body uses a different anchor:
 *   Left hip  : x=200, y=60
 *   Right hip : x=800, y=60
 *   Hip span  : 600 px
 */

// ── Color utilities ──────────────────────────────────────────────────────────

function clamp(v: number): number { return Math.min(255, Math.max(0, v)); }

/**
 * Shift a hex color by `amount` (positive = lighter, negative = darker).
 */
function shade(hex: string, amount: number): string {
  const h = hex.replace('#', '');
  const num = parseInt(h.length === 3
    ? h.split('').map(c => c + c).join('')
    : h, 16);
  const r = clamp((num >> 16) + amount);
  const g = clamp(((num >> 8) & 0xff) + amount);
  const b = clamp((num & 0xff) + amount);
  return `#${[r, g, b].map(v => v.toString(16).padStart(2, '0')).join('')}`;
}

// ── SVG generators ───────────────────────────────────────────────────────────

/**
 * Camp-collar shirt SVG (for category: shirts)
 * Real shirt silhouette: camp collar, long sleeves, button placket.
 */
function shirtSVG(color: string): string {
  const dark  = shade(color, -35);
  const mid   = shade(color, -18);
  const light = shade(color, 20);

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1200" overflow="visible">
  <defs>
    <filter id="sf" x="-10%" y="-5%" width="120%" height="115%">
      <feDropShadow dx="0" dy="6" stdDeviation="12" flood-color="#000" flood-opacity="0.18"/>
    </filter>
    <linearGradient id="bodyGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="${shade(color,-8)}"/>
      <stop offset="50%"  stop-color="${light}"/>
      <stop offset="100%" stop-color="${shade(color,-8)}"/>
    </linearGradient>
    <linearGradient id="slvL" x1="1" y1="0" x2="0" y2="0">
      <stop offset="0%"  stop-color="${color}"/>
      <stop offset="100%" stop-color="${shade(color,-22)}"/>
    </linearGradient>
    <linearGradient id="slvR" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"  stop-color="${color}"/>
      <stop offset="100%" stop-color="${shade(color,-22)}"/>
    </linearGradient>
  </defs>

  <!-- Left sleeve -->
  <path d="M 175,250 L 0,600 L 75,680 L 270,440 Z"
        fill="url(#slvL)" filter="url(#sf)"/>
  <!-- Right sleeve -->
  <path d="M 825,250 L 1000,600 L 925,680 L 730,440 Z"
        fill="url(#slvR)" filter="url(#sf)"/>

  <!-- Main body -->
  <path d="M 175,250
           C 280,215 400,140 490,105
           L 510,105
           C 600,140 720,215 825,250
           L 795,440 L 740,440
           L 780,1150 L 220,1150
           L 260,440 L 205,440
           Z"
        fill="url(#bodyGrad)" filter="url(#sf)"/>

  <!-- Left collar flap -->
  <path d="M 490,105 L 195,265 L 245,400 L 495,370 Z"
        fill="${mid}" opacity="0.9"/>
  <!-- Right collar flap -->
  <path d="M 510,105 L 805,265 L 755,400 L 505,370 Z"
        fill="${mid}" opacity="0.9"/>

  <!-- Collar edge lines -->
  <path d="M 490,105 L 195,265 L 245,400"
        fill="none" stroke="${dark}" stroke-width="5" stroke-linecap="round" opacity="0.7"/>
  <path d="M 510,105 L 805,265 L 755,400"
        fill="none" stroke="${dark}" stroke-width="5" stroke-linecap="round" opacity="0.7"/>

  <!-- Centre placket -->
  <rect x="491" y="365" width="18" height="790" fill="${mid}" opacity="0.8"/>

  <!-- Buttons -->
  ${[455,555,655,755,855,955].map(y =>
    `<circle cx="500" cy="${y}" r="14" fill="${dark}" opacity="0.75"/>
     <circle cx="500" cy="${y}" r="9"  fill="${shade(dark,18)}" opacity="0.6"/>`
  ).join('\n  ')}

  <!-- Side seams -->
  <path d="M 205,440 Q 200,795 220,1150"
        fill="none" stroke="${mid}" stroke-width="3" opacity="0.5"/>
  <path d="M 795,440 Q 800,795 780,1150"
        fill="none" stroke="${mid}" stroke-width="3" opacity="0.5"/>

  <!-- Sleeve under-seam -->
  <path d="M 270,440 L 75,680"
        fill="none" stroke="${shade(color,-28)}" stroke-width="3" opacity="0.4"/>
  <path d="M 730,440 L 925,680"
        fill="none" stroke="${shade(color,-28)}" stroke-width="3" opacity="0.4"/>
</svg>`;
}

/**
 * Bomber/moto jacket SVG (for category: jackets)
 * Wider lapels, zip placket, shorter body.
 */
function jacketSVG(color: string): string {
  const dark  = shade(color, -45);
  const mid   = shade(color, -22);
  const light = shade(color, 15);

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1200" overflow="visible">
  <defs>
    <filter id="jf" x="-10%" y="-5%" width="120%" height="115%">
      <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#000" flood-opacity="0.22"/>
    </filter>
    <linearGradient id="jbody" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="${shade(color,-12)}"/>
      <stop offset="45%"  stop-color="${light}"/>
      <stop offset="100%" stop-color="${shade(color,-12)}"/>
    </linearGradient>
  </defs>

  <!-- Left sleeve (slightly puffier) -->
  <path d="M 175,250 L -20,590 L 70,680 L 265,440 Z"
        fill="${shade(color,-15)}" filter="url(#jf)"/>
  <path d="M 265,440 L 70,680" fill="none" stroke="${dark}" stroke-width="4" opacity="0.4"/>

  <!-- Right sleeve -->
  <path d="M 825,250 L 1020,590 L 930,680 L 735,440 Z"
        fill="${shade(color,-15)}" filter="url(#jf)"/>
  <path d="M 735,440 L 930,680" fill="none" stroke="${dark}" stroke-width="4" opacity="0.4"/>

  <!-- Body -->
  <path d="M 175,250
           C 290,205 410,145 480,108
           L 520,108
           C 590,145 710,205 825,250
           L 800,440 L 745,440
           L 760,1080 L 240,1080
           L 255,440 L 200,440
           Z"
        fill="url(#jbody)" filter="url(#jf)"/>

  <!-- Left lapel (wide jacket lapel) -->
  <path d="M 480,108 L 155,280 L 200,440 L 490,340 Z"
        fill="${mid}" opacity="0.92"/>
  <!-- Right lapel -->
  <path d="M 520,108 L 845,280 L 800,440 L 510,340 Z"
        fill="${mid}" opacity="0.92"/>

  <!-- Lapel notch lines -->
  <path d="M 480,108 L 155,280 L 200,440"
        fill="none" stroke="${dark}" stroke-width="5" stroke-linecap="round"/>
  <path d="M 520,108 L 845,280 L 800,440"
        fill="none" stroke="${dark}" stroke-width="5" stroke-linecap="round"/>

  <!-- Zip track -->
  <rect x="493" y="335" width="14" height="750" fill="${dark}" opacity="0.7" rx="4"/>
  <!-- Zip teeth marks -->
  ${Array.from({length: 12}, (_, i) => {
    const y = 360 + i * 60;
    return `<rect x="486" y="${y}" width="28" height="4" fill="${shade(dark,25)}" opacity="0.6" rx="2"/>`;
  }).join('\n  ')}

  <!-- Collar band -->
  <path d="M 350,195 Q 500,150 650,195"
        fill="none" stroke="${dark}" stroke-width="18" stroke-linecap="round" opacity="0.55"/>

  <!-- Bottom hem ribbing lines -->
  ${[1060,1075,1090].map(y =>
    `<path d="M 240,${y} L 760,${y}" fill="none" stroke="${mid}" stroke-width="3" opacity="0.5"/>`
  ).join('\n  ')}

  <!-- Side seams -->
  <path d="M 200,440 Q 205,760 240,1080"
        fill="none" stroke="${mid}" stroke-width="3" opacity="0.45"/>
  <path d="M 800,440 Q 795,760 760,1080"
        fill="none" stroke="${mid}" stroke-width="3" opacity="0.45"/>
</svg>`;
}

/**
 * Hoodie/sweatshirt SVG (for category: hoodies)
 * Hood visible at top, kangaroo pocket, drawstrings.
 */
function hoodieSVG(color: string): string {
  const dark  = shade(color, -38);
  const mid   = shade(color, -18);
  const light = shade(color, 22);

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1200" overflow="visible">
  <defs>
    <filter id="hf" x="-10%" y="-5%" width="120%" height="115%">
      <feDropShadow dx="0" dy="6" stdDeviation="12" flood-color="#000" flood-opacity="0.20"/>
    </filter>
    <linearGradient id="hbody" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="${shade(color,-10)}"/>
      <stop offset="50%"  stop-color="${light}"/>
      <stop offset="100%" stop-color="${shade(color,-10)}"/>
    </linearGradient>
  </defs>

  <!-- Left sleeve -->
  <path d="M 175,250 L 5,610 L 85,690 L 268,445 Z"
        fill="${shade(color,-12)}" filter="url(#hf)"/>
  <!-- Right sleeve -->
  <path d="M 825,250 L 995,610 L 915,690 L 732,445 Z"
        fill="${shade(color,-12)}" filter="url(#hf)"/>

  <!-- Body -->
  <path d="M 175,250
           C 285,210 395,148 472,112
           C 485,105 515,105 528,112
           C 605,148 715,210 825,250
           L 798,445 L 740,445
           L 758,1140 L 242,1140
           L 260,445 L 202,445
           Z"
        fill="url(#hbody)" filter="url(#hf)"/>

  <!-- Hood (folded, visible at back of neckline) -->
  <path d="M 330,185 Q 500,80 670,185 L 630,265 Q 500,195 370,265 Z"
        fill="${mid}" opacity="0.85" filter="url(#hf)"/>
  <path d="M 330,185 Q 500,80 670,185"
        fill="none" stroke="${dark}" stroke-width="6" opacity="0.6"/>

  <!-- Kangaroo pocket -->
  <rect x="340" y="780" width="320" height="180" rx="16"
        fill="${mid}" opacity="0.55"/>
  <path d="M 500,780 L 500,960"
        fill="none" stroke="${shade(mid,-15)}" stroke-width="3" opacity="0.6"/>

  <!-- Drawstrings -->
  <line x1="430" y1="270" x2="418" y2="380" stroke="${dark}" stroke-width="5"
        stroke-linecap="round" opacity="0.5"/>
  <line x1="570" y1="270" x2="582" y2="380" stroke="${dark}" stroke-width="5"
        stroke-linecap="round" opacity="0.5"/>
  <!-- Drawstring tips -->
  <circle cx="418" cy="385" r="8" fill="${dark}" opacity="0.6"/>
  <circle cx="582" cy="385" r="8" fill="${dark}" opacity="0.6"/>

  <!-- Ribbed hem -->
  ${[1120,1133,1146].map(y =>
    `<path d="M 242,${y} L 758,${y}" fill="none" stroke="${mid}" stroke-width="3" opacity="0.45"/>`
  ).join('\n  ')}

  <!-- Side seams -->
  <path d="M 202,445 Q 208,792 242,1140"
        fill="none" stroke="${mid}" stroke-width="3" opacity="0.4"/>
  <path d="M 798,445 Q 792,792 758,1140"
        fill="none" stroke="${mid}" stroke-width="3" opacity="0.4"/>
</svg>`;
}

/**
 * Trousers/pants SVG (for category: trousers).
 *
 * Lower-body anchor spec:
 *   viewBox: "0 0 800 1100"
 *   Left hip : x=80,  y=60
 *   Right hip: x=720, y=60
 *   Hip span : 640 px
 */
function trousersSVG(color: string): string {
  const dark = shade(color, -35);
  const mid  = shade(color, -15);

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1100" overflow="visible">
  <defs>
    <filter id="tf">
      <feDropShadow dx="0" dy="5" stdDeviation="10" flood-color="#000" flood-opacity="0.15"/>
    </filter>
  </defs>

  <!-- Left leg -->
  <path d="M 80,60 L 70,580 L 0,1090 L 240,1090 L 320,590 L 400,590
           L 400,60 Z"
        fill="${color}" filter="url(#tf)"/>

  <!-- Right leg -->
  <path d="M 720,60 L 730,580 L 800,1090 L 560,1090 L 480,590 L 400,590
           L 400,60 Z"
        fill="${color}" filter="url(#tf)"/>

  <!-- Waistband -->
  <rect x="70" y="45" width="660" height="60" rx="10"
        fill="${mid}" opacity="0.9"/>

  <!-- Belt loops -->
  ${[120,230,380,420,570,680].map(x =>
    `<rect x="${x}" y="42" width="22" height="70" rx="5" fill="${dark}" opacity="0.45"/>`
  ).join('\n  ')}

  <!-- Centre seam -->
  <line x1="400" y1="60" x2="400" y2="590"
        stroke="${dark}" stroke-width="4" opacity="0.4"/>

  <!-- Left side seam -->
  <path d="M 80,60 Q 75,570 0,1090"
        fill="none" stroke="${mid}" stroke-width="3" opacity="0.4"/>
  <!-- Right side seam -->
  <path d="M 720,60 Q 725,570 800,1090"
        fill="none" stroke="${mid}" stroke-width="3" opacity="0.4"/>

  <!-- Pocket lines (left) -->
  <path d="M 150,90 Q 100,180 90,270"
        fill="none" stroke="${dark}" stroke-width="3" opacity="0.35"/>
  <!-- Pocket lines (right) -->
  <path d="M 650,90 Q 700,180 710,270"
        fill="none" stroke="${dark}" stroke-width="3" opacity="0.35"/>
</svg>`;
}

/**
 * Dress SVG (for category: dresses)
 * Fitted at torso, flared skirt.
 */
function dressSVG(color: string): string {
  const dark  = shade(color, -35);
  const mid   = shade(color, -15);
  const light = shade(color, 25);

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1400" overflow="visible">
  <defs>
    <filter id="df">
      <feDropShadow dx="0" dy="6" stdDeviation="12" flood-color="#000" flood-opacity="0.16"/>
    </filter>
    <linearGradient id="dbody" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="${shade(color,-5)}"/>
      <stop offset="40%"  stop-color="${light}"/>
      <stop offset="100%" stop-color="${shade(color,-10)}"/>
    </linearGradient>
  </defs>

  <!-- Thin straps -->
  <rect x="360" y="80" width="40" height="185" rx="12" fill="${mid}" filter="url(#df)"/>
  <rect x="600" y="80" width="40" height="185" rx="12" fill="${mid}" filter="url(#df)"/>

  <!-- Fitted bodice -->
  <path d="M 280,260 L 720,260 L 760,680 L 240,680 Z"
        fill="url(#dbody)" filter="url(#df)"/>

  <!-- Flared skirt -->
  <path d="M 240,680 L 760,680 L 900,1370 L 100,1370 Z"
        fill="url(#dbody)" filter="url(#df)"/>

  <!-- Neckline -->
  <path d="M 280,260 Q 500,215 720,260"
        fill="none" stroke="${mid}" stroke-width="6" opacity="0.6"/>

  <!-- Waist seam -->
  <line x1="240" y1="680" x2="760" y2="680"
        stroke="${dark}" stroke-width="5" opacity="0.5"/>

  <!-- Skirt seam lines (fold detail) -->
  <path d="M 500,680 L 500,1370" fill="none" stroke="${mid}" stroke-width="2" opacity="0.3"/>
  <path d="M 350,680 L 250,1370" fill="none" stroke="${mid}" stroke-width="2" opacity="0.3"/>
  <path d="M 650,680 L 750,1370" fill="none" stroke="${mid}" stroke-width="2" opacity="0.3"/>

  <!-- Side seams -->
  <path d="M 280,260 L 240,680 L 100,1370"
        fill="none" stroke="${mid}" stroke-width="3" opacity="0.4"/>
  <path d="M 720,260 L 760,680 L 900,1370"
        fill="none" stroke="${mid}" stroke-width="3" opacity="0.4"/>
</svg>`;
}

// ── Public API ───────────────────────────────────────────────────────────────

export interface GarmentAsset {
  svgString: string;
  /** Width of the SVG viewBox */
  svgW: number;
  /** Height of the SVG viewBox */
  svgH: number;
  /**
   * X position of the LEFT anchor landmark in SVG coordinates.
   * Upper body → left shoulder (landmark 11).
   * Lower body → left hip (landmark 23).
   */
  anchorLeftX: number;
  anchorLeftY: number;
  /**
   * X position of the RIGHT anchor landmark in SVG coordinates.
   * Upper body → right shoulder (landmark 12).
   * Lower body → right hip (landmark 24).
   */
  anchorRightX: number;
  anchorRightY: number;
  /** Distance between anchor points in SVG units (used to compute scale). */
  anchorSpan: number;
  /** Which MediaPipe landmark IDs are the primary anchors. */
  anchorLandmarkIds: [number, number]; // [left, right]
}

/**
 * Generate a garment asset for the given category and hex color.
 * Returns an `GarmentAsset` with the SVG string and anchor metadata
 * needed by GarmentRenderer2D.
 */
export function getGarmentAsset(categoryId: string, colorHex: string): GarmentAsset {
  const c = colorHex.startsWith('#') ? colorHex : `#${colorHex}`;

  switch (categoryId) {
    case 'jackets':
      return {
        svgString: jacketSVG(c),
        svgW: 1000, svgH: 1200,
        anchorLeftX: 175, anchorLeftY: 250,
        anchorRightX: 825, anchorRightY: 250,
        anchorSpan: 650,
        anchorLandmarkIds: [11, 12],
      };
    case 'hoodies':
      return {
        svgString: hoodieSVG(c),
        svgW: 1000, svgH: 1200,
        anchorLeftX: 175, anchorLeftY: 250,
        anchorRightX: 825, anchorRightY: 250,
        anchorSpan: 650,
        anchorLandmarkIds: [11, 12],
      };
    case 'trousers':
      return {
        svgString: trousersSVG(c),
        svgW: 800, svgH: 1100,
        anchorLeftX: 80, anchorLeftY: 60,
        anchorRightX: 720, anchorRightY: 60,
        anchorSpan: 640,
        anchorLandmarkIds: [23, 24],
      };
    case 'dresses':
      return {
        svgString: dressSVG(c),
        svgW: 1000, svgH: 1400,
        anchorLeftX: 280, anchorLeftY: 260,
        anchorRightX: 720, anchorRightY: 260,
        anchorSpan: 440,
        anchorLandmarkIds: [11, 12],
      };
    default: // shirts, and anything else → shirt shape
      return {
        svgString: shirtSVG(c),
        svgW: 1000, svgH: 1200,
        anchorLeftX: 175, anchorLeftY: 250,
        anchorRightX: 825, anchorRightY: 250,
        anchorSpan: 650,
        anchorLandmarkIds: [11, 12],
      };
  }
}

/** Convert an SVG string to a data URL. */
export function svgToDataUrl(svg: string): string {
  const encoded = btoa(unescape(encodeURIComponent(svg)));
  return `data:image/svg+xml;base64,${encoded}`;
}

/** Load an SVG data URL as an HTMLImageElement (resolves when loaded). */
export function loadGarmentImage(asset: GarmentAsset): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = svgToDataUrl(asset.svgString);
  });
}
