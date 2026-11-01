"""Build the vector Open Source Community logo.

Hybrid approach:
- Geometry (circle, stripes, underline, strikethrough): rebuilt from measurements.
- Blue mark: traced from the average of two aligned raster references.
- Lettering: real fonts converted to outline paths, fitted to measured boxes.
"""
import sys, numpy as np, potrace
from PIL import Image
from scipy import ndimage as nd
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

SRC, REF2, FONTDIR, OUT = sys.argv[1:5]

# ---------- 1. blue mark: average two references ----------
def rgb(path, size=None):
    im = Image.open(path).convert('RGB')
    if size: im = im.resize(size, Image.LANCZOS)
    return np.asarray(im).astype(float)
A = rgb(SRC)
B = rgb(REF2, (1080, round(356 * 3)))
blueness = lambda a: (255 - a[..., 0]) * np.clip((a[..., 2] - a[..., 0] - 8) / 20, 0, 1)  # ink strength, blue-tinted only (excludes black text)
ra = blueness(A)
rb_small = blueness(B)
rb = np.full_like(ra, np.nan)
dx, dy = -2, 5                      # measured registration offset (corr 0.95)
h, w = rb_small.shape
ys, xs = slice(max(0, dy), min(1080, h + dy)), slice(max(0, dx), min(1080, w + dx))
rb[ys, xs] = rb_small[ys.start - dy:ys.stop - dy, xs.start - dx:xs.stop - dx]
avg = np.where(np.isnan(rb), ra, (ra + rb) / 2)

S = 3                                # trace at 3x for smoother curves
big = np.asarray(Image.fromarray(avg.astype(np.float32), mode='F').resize((1080 * S,) * 2, Image.BICUBIC))
big = nd.gaussian_filter(big, (4.5 * S / 2, 1.6 * S / 2))   # extra vertical blur kills stripe scallops
H = big.shape[0]
yy, xx = np.mgrid[0:H, 0:H]
mask = (big > 85) & (np.hypot(xx - 543 * S, yy - 547 * S) < 495 * S)
mask &= ~((yy >= 681 * S) & (xx >= 346 * S))  # "Open" letters handled by font
mask &= ~(yy >= 812 * S)                      # underline handled geometrically
lab, n = nd.label(mask)
sizes = nd.sum(mask, lab, range(1, n + 1))
mask = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 2000 * S])   # drop specks
holes, nh = nd.label(~mask)
hs = nd.sum(~mask, holes, range(1, nh + 1))
mask |= np.isin(holes, [i + 1 for i, s in enumerate(hs) if s < 400 * S])     # fill pinholes
mask = nd.binary_opening(nd.binary_closing(mask, iterations=2), iterations=2)

def trace(m, scale):
    paths = potrace.Bitmap(~m).trace(turdsize=60, alphamax=1.15, opticurve=True, opttolerance=0.5)
    f = lambda p: f"{p.x/scale:.1f},{p.y/scale:.1f}"
    out = []
    for c in paths:
        d = [f"M{f(c.start_point)}"]
        for sg in c.segments:
            d.append(f"L{f(sg.c)}L{f(sg.end_point)}" if sg.is_corner
                     else f"C{f(sg.c1)} {f(sg.c2)} {f(sg.end_point)}")
        out.append("".join(d) + "Z")
    return " ".join(out)
mark_d = trace(mask, S)

# ---------- 2. lettering from fonts ----------
def text_path(font_file, text, x0, x1, top, baseline, ref_char, clip_bottom=None, letter_spacing=0):
    """Fit `text` so ref_char spans top..baseline and the run spans x0..x1."""
    f = TTFont(font_file); gs = f.getGlyphSet(); cmap = f.getBestCmap()
    hmtx = f['hmtx']
    bp = BoundsPen(gs); gs[cmap[ord(ref_char)]].draw(bp)
    ref_h = bp.bounds[3]                       # height above baseline (font units)
    sy = (baseline - top) / ref_h
    # natural advance layout
    pen_x, items = 0, []
    for ch in text:
        g = cmap[ord(ch)]
        items.append((g, pen_x)); pen_x += hmtx[g][0] + letter_spacing
    # ink bounds of the whole run
    xmin, xmax = 1e9, -1e9
    for g, ox in items:
        b2 = BoundsPen(gs); gs[g].draw(b2)
        if b2.bounds: xmin = min(xmin, ox + b2.bounds[0]); xmax = max(xmax, ox + b2.bounds[2])
    sx = (x1 - x0) / (xmax - xmin)
    sp = SVGPathPen(gs)
    for g, ox in items:
        tp = TransformPen(sp, (sx, 0, 0, -sy, x0 + (ox - xmin) * sx, baseline))
        gs[g].draw(tp)
    return sp.getCommands(), sx / sy

fd = FONTDIR
open_d, r1 = text_path(f"{fd}/oswald-latin-700-normal.ttf", "Open", 350, 606, 682, 806, "O", letter_spacing=0)
source_d, r2 = text_path(f"{fd}/cinzel-latin-600-normal.ttf", "Source", 546, 903, 599, 678, "S", letter_spacing=-45)
tag_d, r3 = text_path(f"{fd}/open-sans-latin-600-italic.ttf", "The Open Source Community", 182, 785, 846, 875, "T", letter_spacing=35)
print(f"horizontal/vertical scale ratios: Open {r1:.2f}, Source {r2:.2f}, tagline {r3:.2f}", file=sys.stderr)

# ---------- 3. geometry ----------
CX, CY, R = 543, 547, 514          # solved from three measured chords
per, phase = 20.85, 1.25
stripes = "".join(f'<rect x="{CX-R}" y="{phase+k*per-4:.2f}" width="{2*R}" height="8"/>'
                  for k in range(int((CY - R - phase) // per), int((CY + R) // per) + 2))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{CX-R-8} {CY-R-8} {2*R+16} {2*R+16}" width="1024" height="1024">
  <title>The Open Source Community</title>
  <defs>
    <clipPath id="disc"><circle cx="{CX}" cy="{CY}" r="{R}"/></clipPath>
    <radialGradient id="mark" gradientUnits="userSpaceOnUse" cx="330" cy="390" r="520">
      <stop offset="0" stop-color="#2b3ef2"/>
      <stop offset="0.4" stop-color="#1621bd"/>
      <stop offset="1" stop-color="#0a0d7c"/>
    </radialGradient>
    <clipPath id="above-line"><rect x="0" y="0" width="1100" height="821"/></clipPath>
  </defs>
  <circle cx="{CX}" cy="{CY}" r="{R}" fill="#ffffff"/>
  <g clip-path="url(#disc)" fill="#e3e6eb">{stripes}</g>
  <circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="#1d2fc8" stroke-width="6"/>
  <path id="symbol" fill="url(#mark)" d="{mark_d}"/>
  <path id="open" fill="#0f168f" clip-path="url(#above-line)" d="{open_d}"/>
  <rect id="underline" x="183" y="821" width="722" height="6" fill="#0f168f"/>
  <path id="source" fill="#111111" d="{source_d}"/>
  <rect id="strike" x="546" y="648" width="357" height="3" fill="#111111"/>
  <path id="tagline" fill="#1a1a1a" d="{tag_d}"/>
</svg>
'''
open(OUT, 'w').write(svg)
print(f"wrote {OUT} ({len(svg)} bytes)", file=sys.stderr)
