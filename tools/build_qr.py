"""Genera el código QR de acceso a saludrcartes.

Salidas:
  assets/img/qr/saludrcartes-qr.png   (1600 x 1600, con sello central)
  assets/img/qr/saludrcartes-qr.svg   (vectorial, para impresión)

Uso:
  python tools/build_qr.py
"""

from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont
from qrcode.constants import ERROR_CORRECT_H

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "img" / "qr"

URL = "https://saludrcartes.netlify.app/"

CREAM = "#FFF8F0"
PAPER = "#FFFCF7"
FOREST = "#0B2A21"
GOLD = "#D4AF37"
GOLD_DEEP = "#9A7420"

CANVAS = 1600
MODULE_PX = 28
BORDER_MODULES = 4
SEAL_RADIUS = 196  # en píxeles del PNG final


def build_matrix():
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=1,
        border=BORDER_MODULES,
    )
    qr.add_data(URL)
    qr.make(fit=True)
    return qr.get_matrix()


def load_font(size, italic=True):
    candidates = [
        "georgiai.ttf",
        "Georgia Italic.ttf",
        "timesi.ttf",
        "Times New Roman Italic.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_png(matrix):
    modules = len(matrix)
    qr_size = modules * MODULE_PX
    offset = (CANVAS - qr_size) // 2

    img = Image.new("RGB", (CANVAS, CANVAS), CREAM)
    draw = ImageDraw.Draw(img)

    # Panel blanco: además de estética, garantiza la zona de silencio.
    panel = 40
    draw.rounded_rectangle(
        (offset - panel, offset - panel, offset + qr_size + panel, offset + qr_size + panel),
        radius=44,
        fill=PAPER,
        outline="#E6D3A0",
        width=3,
    )

    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            if value:
                x0 = offset + x * MODULE_PX
                y0 = offset + y * MODULE_PX
                draw.rectangle(
                    (x0, y0, x0 + MODULE_PX - 1, y0 + MODULE_PX - 1),
                    fill=FOREST,
                )

    # Sello central (monograma rc) sobre disco crema.
    cx = cy = CANVAS // 2
    draw.ellipse(
        (cx - SEAL_RADIUS - 14, cy - SEAL_RADIUS - 14, cx + SEAL_RADIUS + 14, cy + SEAL_RADIUS + 14),
        fill=PAPER,
    )
    draw.ellipse(
        (cx - SEAL_RADIUS, cy - SEAL_RADIUS, cx + SEAL_RADIUS, cy + SEAL_RADIUS),
        fill=FOREST,
        outline=GOLD,
        width=6,
    )
    inner = SEAL_RADIUS - 34
    draw.ellipse(
        (cx - inner, cy - inner, cx + inner, cy + inner),
        outline=GOLD_DEEP,
        width=2,
    )

    font = load_font(150)
    text = "rc"
    box = draw.textbbox((0, 0), text, font=font)
    tw, th = box[2] - box[0], box[3] - box[1]
    draw.text(
        (cx - tw / 2 - box[0], cy - th / 2 - box[1]),
        text,
        fill=CREAM,
        font=font,
    )

    draw.ellipse((cx - 232, cy - 232, cx - 218, cy - 218), fill=GOLD)
    draw.ellipse((cx + 218, cy - 232, cx + 232, cy - 218), fill=GOLD)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUT_DIR / "saludrcartes-qr.png"
    img.save(target, "PNG", optimize=True)
    return target


def render_svg(matrix):
    modules = len(matrix)
    scale = 10
    size = modules * scale
    cx = cy = size / 2
    seal_r = (SEAL_RADIUS / MODULE_PX) * scale

    cells = []
    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            if value:
                cells.append(f"M{x * scale} {y * scale}h{scale}v{scale}h-{scale}z")

    path = " ".join(cells)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}" role="img" aria-label="Código QR de acceso a saludrcartes">
  <title>saludrcartes · {URL}</title>
  <rect width="{size}" height="{size}" fill="{PAPER}"/>
  <path d="{path}" fill="{FOREST}" shape-rendering="crispEdges"/>
  <g>
    <circle cx="{cx}" cy="{cy}" r="{seal_r + 3}" fill="{PAPER}"/>
    <circle cx="{cx}" cy="{cy}" r="{seal_r}" fill="{FOREST}" stroke="{GOLD}" stroke-width="1.4"/>
    <circle cx="{cx}" cy="{cy}" r="{seal_r - 7}" fill="none" stroke="{GOLD_DEEP}" stroke-width="0.5"/>
    <text x="{cx}" y="{cy + 12}" text-anchor="middle" fill="{CREAM}" font-family="Georgia, 'Times New Roman', serif" font-style="italic" font-size="31">rc</text>
    <circle cx="{cx - seal_r - 6}" cy="{cy - seal_r + 1}" r="1.8" fill="{GOLD}"/>
    <circle cx="{cx + seal_r + 6}" cy="{cy - seal_r + 1}" r="1.8" fill="{GOLD}"/>
  </g>
</svg>
"""
    target = OUT_DIR / "saludrcartes-qr.svg"
    target.write_text(svg, encoding="utf-8")
    return target


def main():
    matrix = build_matrix()
    png = render_png(matrix)
    svg = render_svg(matrix)
    print(f"URL: {URL}")
    print(f"PNG: {png.relative_to(ROOT)}")
    print(f"SVG: {svg.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
