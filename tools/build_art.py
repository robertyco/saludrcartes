"""Generate the bespoke editorial artwork for each page as layered SVG scenes."""
from pathlib import Path
from textwrap import dedent

OUT = Path("assets/img/art")
OUT.mkdir(parents=True, exist_ok=True)

CREAM = "#FFF8F0"
INK = "#15352A"
DEEP = "#064E3B"
GREEN = "#0E9F6E"
TURQ = "#38BDF8"
CORAL = "#FF6B6B"
YELLOW = "#FFC94A"
VIOLET = "#8B5CF6"
GOLD = "#D4AF37"
SILVER = "#C0C7CE"


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    ra, ga, ba = hex_rgb(a)
    rb, gb, bb = hex_rgb(b)
    return "#%02X%02X%02X" % (
        round(ra + (rb - ra) * t),
        round(ga + (gb - ga) * t),
        round(ba + (bb - ba) * t),
    )


def defs(accent, secondary, dark_bg=False):
    base = "#0B1F19" if dark_bg else CREAM
    return f"""
    <defs>
      <radialGradient id="bg" cx="58%" cy="42%" r="80%">
        <stop offset="0%" stop-color="{mix(accent, base, 0.82)}"/>
        <stop offset="48%" stop-color="{mix(secondary, base, 0.9)}"/>
        <stop offset="100%" stop-color="{base}"/>
      </radialGradient>
      <radialGradient id="aura" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="{accent}" stop-opacity="0.55"/>
        <stop offset="55%" stop-color="{accent}" stop-opacity="0.18"/>
        <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
      </radialGradient>
      <radialGradient id="aura2" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="{secondary}" stop-opacity="0.5"/>
        <stop offset="100%" stop-color="{secondary}" stop-opacity="0"/>
      </radialGradient>
      <linearGradient id="a" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="{mix(accent, '#FFFFFF', 0.15)}"/>
        <stop offset="52%" stop-color="{accent}"/>
        <stop offset="100%" stop-color="{mix(accent, INK, 0.28)}"/>
      </linearGradient>
      <linearGradient id="b" x1="1" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{mix(secondary, '#FFFFFF', 0.2)}"/>
        <stop offset="100%" stop-color="{mix(secondary, INK, 0.18)}"/>
      </linearGradient>
      <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#F8E9B0"/>
        <stop offset="38%" stop-color="{GOLD}"/>
        <stop offset="68%" stop-color="#B98B24"/>
        <stop offset="100%" stop-color="#F3DF9B"/>
      </linearGradient>
      <linearGradient id="silver" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#FFFFFF"/>
        <stop offset="42%" stop-color="{SILVER}"/>
        <stop offset="100%" stop-color="#7A8791"/>
      </linearGradient>
      <linearGradient id="glass" x1="0" y1="0" x2="0.7" y2="1">
        <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.72"/>
        <stop offset="55%" stop-color="{mix(accent, '#FFFFFF', 0.55)}" stop-opacity="0.34"/>
        <stop offset="100%" stop-color="{mix(accent, INK, 0.1)}" stop-opacity="0.16"/>
      </linearGradient>
      <linearGradient id="glass2" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.6"/>
        <stop offset="60%" stop-color="{mix(secondary, '#FFFFFF', 0.5)}" stop-opacity="0.24"/>
        <stop offset="100%" stop-color="{mix(secondary, INK, 0.15)}" stop-opacity="0.12"/>
      </linearGradient>
      <radialGradient id="orb" cx="35%" cy="30%" r="70%">
        <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.95"/>
        <stop offset="22%" stop-color="{mix(accent, '#FFFFFF', 0.55)}" stop-opacity="0.7"/>
        <stop offset="62%" stop-color="{accent}" stop-opacity="0.3"/>
        <stop offset="100%" stop-color="{mix(accent, INK, 0.2)}" stop-opacity="0.5"/>
      </radialGradient>
      <radialGradient id="sun" cx="42%" cy="38%" r="65%">
        <stop offset="0%" stop-color="#FFFDF0"/>
        <stop offset="38%" stop-color="{mix(YELLOW, '#FFFFFF', 0.35)}"/>
        <stop offset="75%" stop-color="{YELLOW}"/>
        <stop offset="100%" stop-color="{mix(YELLOW, CORAL, 0.3)}"/>
      </radialGradient>
      <filter id="blur60" x="-60%" y="-60%" width="220%" height="220%">
        <feGaussianBlur stdDeviation="60"/>
      </filter>
      <filter id="blur28" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="28"/>
      </filter>
      <filter id="blur10" x="-30%" y="-30%" width="160%" height="160%">
        <feGaussianBlur stdDeviation="10"/>
      </filter>
      <filter id="shadow" x="-40%" y="-40%" width="180%" height="190%">
        <feDropShadow dx="0" dy="26" stdDeviation="26" flood-color="{INK}" flood-opacity="0.16"/>
      </filter>
      <filter id="shadowSoft" x="-40%" y="-40%" width="180%" height="190%">
        <feDropShadow dx="0" dy="14" stdDeviation="14" flood-color="{INK}" flood-opacity="0.12"/>
      </filter>
      <filter id="grain">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" stitchTiles="stitch"/>
        <feColorMatrix type="saturate" values="0"/>
        <feComponentTransfer><feFuncA type="linear" slope="0.09"/></feComponentTransfer>
      </filter>
      <pattern id="dots" width="30" height="30" patternUnits="userSpaceOnUse">
        <circle cx="2" cy="2" r="1.25" fill="{INK}" opacity="0.14"/>
      </pattern>
      <pattern id="grid" width="80" height="80" patternUnits="userSpaceOnUse">
        <path d="M80 0H0V80" stroke="{INK}" stroke-opacity="0.06" stroke-width="1"/>
      </pattern>
    </defs>
    <rect width="1600" height="1100" fill="url(#bg)"/>
    <ellipse cx="1050" cy="500" rx="540" ry="470" fill="url(#aura)"/>
    <ellipse cx="380" cy="820" rx="420" ry="300" fill="url(#aura2)"/>
    """


def orb(cx, cy, r, opacity=0.7, stroke=None):
    stroke_attr = f' stroke="{stroke}" stroke-opacity="0.5" stroke-width="1.2"' if stroke else ""
    return f"""
    <g filter="url(#shadowSoft)">
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#orb)" opacity="{opacity}"{stroke_attr}/>
      <ellipse cx="{cx - r * 0.28}" cy="{cy - r * 0.36}" rx="{r * 0.3}" ry="{r * 0.16}" fill="#FFFFFF" opacity="0.65" transform="rotate(-28 {cx - r * 0.28} {cy - r * 0.36})"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="1"/>
    </g>"""


def spark(cx, cy, s, color=GOLD, opacity=0.85):
    return f"""<path d="M{cx} {cy - s} C{cx + s * 0.12} {cy - s * 0.25} {cx + s * 0.25} {cy - s * 0.12} {cx + s} {cy} C{cx + s * 0.25} {cy + s * 0.12} {cx + s * 0.12} {cy + s * 0.25} {cx} {cy + s} C{cx - s * 0.12} {cy + s * 0.25} {cx - s * 0.25} {cy + s * 0.12} {cx - s} {cy} C{cx - s * 0.25} {cy - s * 0.12} {cx - s * 0.12} {cy - s * 0.25} {cx} {cy - s} Z" fill="{color}" opacity="{opacity}"/>"""


def leaf(cx, cy, rot, scale, color, opacity=0.7):
    return f"""<g transform="translate({cx} {cy}) rotate({rot}) scale({scale})" opacity="{opacity}">
      <path d="M0 0C28 -66 112 -86 152 -22C108 40 48 46 0 0Z" fill="{color}"/>
      <path d="M7 -2C52 -18 100 -30 146 -20" fill="none" stroke="#FFFFFF" stroke-opacity="0.5" stroke-width="2"/>
      <path d="M44 -12C55 -34 69 -50 88 -60M70 -8C82 -24 96 -34 112 -38M36 -6C42 12 50 24 60 34" fill="none" stroke="{INK}" stroke-opacity="0.18" stroke-width="1.5"/>
    </g>"""


def sprig(cx, cy, rot, scale, color, opacity=0.65):
    return f"""<g transform="translate({cx} {cy}) rotate({rot}) scale({scale})" fill="none" stroke="{color}" stroke-opacity="{opacity}" stroke-width="2.2" stroke-linecap="round">
      <path d="M0 180C10 90 28 20 86 -50"/>
      <path d="M18 120C-10 102 -32 76 -38 44C-2 44 16 62 28 88" fill="{color}" fill-opacity="0.16" stroke="none"/>
      <path d="M32 72C62 58 86 32 96 0C58 2 36 26 28 52" fill="{color}" fill-opacity="0.18" stroke="none"/>
      <path d="M50 25C48 -8 58 -38 80 -64C92 -32 80 -2 62 20" fill="{color}" fill-opacity="0.2" stroke="none"/>
      <path d="M8 152C-22 144 -46 128 -60 104C-24 94 0 108 20 130" fill="{color}" fill-opacity="0.14" stroke="none"/>
    </g>"""


def capsule(cx, cy, length, width, rot, c1, c2):
    x = -length / 2
    return f"""<g transform="translate({cx} {cy}) rotate({rot})" filter="url(#shadow)">
      <rect x="{x}" y="{-width / 2}" width="{length}" height="{width}" rx="{width / 2}" fill="{c2}"/>
      <path d="M0 {-width / 2}H{x + width / 2}A{width / 2} {width / 2} 0 0 1 {x + width / 2} {width / 2}H0Z" fill="{c1}"/>
      <rect x="{x + 6}" y="{-width / 2 + 5}" width="{length - 12}" height="{width - 10}" rx="{width / 2 - 5}" fill="none" stroke="#FFFFFF" stroke-opacity="0.38" stroke-width="2"/>
      <ellipse cx="{x + width * 0.52}" cy="{-width * 0.16}" rx="{length * 0.2}" ry="{width * 0.13}" fill="#FFFFFF" opacity="0.42" transform="rotate(-8 {x + width * 0.52} {-width * 0.16})"/>
      <line x1="0" y1="{-width / 2 + 4}" x2="0" y2="{width / 2 - 4}" stroke="{INK}" stroke-opacity="0.12" stroke-width="2"/>
    </g>"""


def paper_card(cx, cy, w, h, rot, opacity=0.58, lines=4, accent=GREEN):
    line_el = "".join(
        f'<rect x="{-w/2 + 26}" y="{-h/2 + 54 + i*30}" width="{w * (0.72 if i % 3 else 0.46)}" height="5" rx="2.5" fill="{INK}" opacity="0.12"/>'
        for i in range(lines)
    )
    return f"""<g transform="translate({cx} {cy}) rotate({rot})" filter="url(#shadowSoft)">
      <rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="26" fill="#FFFFFF" opacity="{opacity}" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="1.4"/>
      <rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="26" fill="none" stroke="{accent}" stroke-opacity="0.2" stroke-width="1.4"/>
      <rect x="{-w/2 + 24}" y="{-h/2 + 22}" width="48" height="8" rx="4" fill="{accent}" opacity="0.36"/>
      {line_el}
      <circle cx="{w/2 - 34}" cy="{-h/2 + 30}" r="8" fill="none" stroke="{GOLD}" stroke-opacity="0.65" stroke-width="1.6"/>
    </g>"""


def constellation(points, color=GOLD, opacity=0.5):
    out = []
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        out.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-opacity="{opacity * 0.55}" stroke-width="1.1" stroke-dasharray="2 7"/>'
        )
    for x, y in points:
        out.append(f'<circle cx="{x}" cy="{y}" r="3.2" fill="{color}" opacity="{opacity}"/>')
        out.append(f'<circle cx="{x}" cy="{y}" r="9" fill="none" stroke="{color}" stroke-opacity="{opacity * 0.3}" stroke-width="0.9"/>')
    return "".join(out)


def wave_path(y, amplitude, length, color, opacity=0.28, width=2.2, phase=0):
    import math

    pts = []
    for x in range(0, length + 1, 16):
        yy = y + math.sin((x / length) * math.pi * 6 + phase) * amplitude
        pts.append(f"{x},{yy:.1f}")
    d = "M" + " L".join(pts)
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity="{opacity}" stroke-width="{width}" stroke-linecap="round"/>'


def shell(content, accent, secondary, dark_bg=False, extra_defs=""):
    return dedent(
        f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1100" fill="none" role="img">
        {defs(accent, secondary, dark_bg)}
        {extra_defs}
        {content}
        <rect width="1600" height="1100" filter="url(#grain)" opacity="0.5"/>
        </svg>"""
    )


# ---------------------------------------------------------------------------
# 01 · Inicio — a floating care landscape
# ---------------------------------------------------------------------------
def art_inicio():
    hills = f"""
    <path d="M-80 880C140 780 320 760 500 812C700 870 860 770 1060 760C1260 750 1440 830 1680 780V1120H-80Z" fill="{mix(GREEN, CREAM, 0.45)}" opacity="0.66"/>
    <path d="M-80 950C180 860 350 900 540 936C760 978 940 884 1160 896C1360 906 1500 960 1680 930V1120H-80Z" fill="{mix(GREEN, CREAM, 0.2)}" opacity="0.58"/>
    <path d="M-80 1018C180 960 400 1002 620 1018C860 1036 1080 976 1300 1004C1440 1022 1560 1042 1680 1030V1120H-80Z" fill="{DEEP}" opacity="0.18"/>
    """
    sun = f"""
    <g filter="url(#blur28)" opacity="0.7"><circle cx="1090" cy="430" r="265" fill="url(#sun)"/></g>
    <circle cx="1090" cy="430" r="205" fill="url(#sun)" opacity="0.92"/>
    <circle cx="1090" cy="430" r="205" fill="none" stroke="#FFFFFF" stroke-opacity="0.42" stroke-width="2"/>
    <ellipse cx="1090" cy="430" rx="300" ry="86" transform="rotate(-16 1090 430)" fill="none" stroke="url(#gold)" stroke-opacity="0.65" stroke-width="1.6"/>
    <ellipse cx="1090" cy="430" rx="340" ry="118" transform="rotate(12 1090 430)" fill="none" stroke="{TURQ}" stroke-opacity="0.3" stroke-width="1.2" stroke-dasharray="3 9"/>
    """
    portal = f"""
    <g filter="url(#shadow)" opacity="0.9">
      <path d="M720 850V660C720 520 830 430 950 430C1070 430 1180 520 1180 660V850Z" fill="url(#glass2)" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="2"/>
      <path d="M756 850V666C756 550 844 476 950 476C1056 476 1144 550 1144 666V850Z" fill="none" stroke="{GOLD}" stroke-opacity="0.45" stroke-width="1.4" stroke-dasharray="2 8"/>
    </g>
    """
    cards = paper_card(790, 700, 180, 220, -13, 0.5, 3, GREEN) + paper_card(1250, 640, 190, 240, 9, 0.5, 4, TURQ)
    cross = f"""
    <g transform="translate(1160 700) rotate(-8)" filter="url(#shadow)">
      <rect x="-58" y="-58" width="116" height="116" rx="30" fill="#FFFFFF" opacity="0.62" stroke="#FFFFFF" stroke-opacity="0.7"/>
      <rect x="-11" y="-34" width="22" height="68" rx="11" fill="url(#a)"/>
      <rect x="-34" y="-11" width="68" height="22" rx="11" fill="url(#a)"/>
    </g>
    """
    points = [(690, 245), (810, 190), (945, 215), (1060, 150), (1185, 205), (1305, 170), (1390, 255)]
    content = (
        hills
        + sun
        + portal
        + cards
        + cross
        + constellation(points, GOLD, 0.6)
        + orb(760, 330, 44, 0.55)
        + orb(1350, 520, 66, 0.5)
        + orb(620, 610, 28, 0.5)
        + leaf(1370, 760, -16, 1.1, GREEN, 0.55)
        + sprig(650, 760, -8, 1.15, GREEN, 0.55)
        + spark(1210, 300, 16)
        + spark(880, 180, 11)
        + spark(1460, 420, 10, TURQ, 0.7)
        + f'<rect x="530" y="120" width="630" height="800" fill="url(#dots)" opacity="0.5"/>'
    )
    return shell(content, GREEN, TURQ)


# ---------------------------------------------------------------------------
# 02 · Diagnósticos — the lens that makes sense of the story
# ---------------------------------------------------------------------------
def art_diagnosticos():
    body_line = f"""
    <g opacity="0.25" stroke="{DEEP}" stroke-width="2" fill="none" stroke-linecap="round">
      <path d="M620 190C650 150 700 130 740 150C780 170 790 230 760 270C735 304 690 310 655 285"/>
      <path d="M700 320C640 360 610 450 620 540C630 630 660 700 690 760"/>
      <path d="M700 320C760 355 785 430 778 520C770 620 735 700 700 760"/>
      <path d="M620 430C570 470 540 540 545 610M778 430C830 470 860 540 855 610"/>
    </g>
    """
    cards = (
        paper_card(980, 610, 380, 480, 7, 0.68, 7, GREEN)
        + paper_card(905, 560, 330, 430, -6, 0.48, 5, TURQ)
        + paper_card(1120, 540, 300, 390, 14, 0.35, 4, GOLD)
    )
    lens = f"""
    <g filter="url(#shadow)">
      <circle cx="1060" cy="470" r="210" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="3"/>
      <circle cx="1060" cy="470" r="210" fill="none" stroke="{GOLD}" stroke-opacity="0.55" stroke-width="2"/>
      <circle cx="1060" cy="470" r="174" fill="none" stroke="{GREEN}" stroke-opacity="0.28" stroke-width="1.2" stroke-dasharray="2 7"/>
      <path d="M936 372C972 326 1032 304 1092 314" fill="none" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="8" stroke-linecap="round"/>
      <path d="M1194 616L1310 742" stroke="url(#gold)" stroke-width="34" stroke-linecap="round"/>
      <path d="M1194 616L1310 742" stroke="#FFFFFF" stroke-opacity="0.3" stroke-width="8" stroke-linecap="round"/>
    </g>
    """
    content = (
        body_line
        + f'<rect x="760" y="180" width="620" height="720" fill="url(#grid)" opacity="0.7"/>'
        + cards
        + lens
        + constellation([(760, 200), (850, 250), (940, 220), (1030, 260), (1120, 210), (1230, 260), (1330, 220)], GOLD, 0.55)
        + orb(740, 520, 34, 0.55)
        + orb(1370, 690, 62, 0.5)
        + orb(840, 800, 24, 0.5)
        + leaf(1380, 300, 30, 0.9, GREEN, 0.42)
        + sprig(590, 780, 12, 1.0, TURQ, 0.45)
        + spark(1260, 340, 14)
        + spark(820, 300, 10, TURQ, 0.8)
        + paper_card(720, 870, 160, 190, -12, 0.3, 2, CORAL)
    )
    return shell(content, GREEN, TURQ)


# ---------------------------------------------------------------------------
# 03 · Medicamentos y alergias
# ---------------------------------------------------------------------------
def art_medicamentos():
    bottle = f"""
    <g transform="translate(840 600) rotate(-6)" filter="url(#shadow)">
      <rect x="-95" y="-120" width="190" height="300" rx="34" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="2"/>
      <rect x="-95" y="-120" width="190" height="300" rx="34" fill="{CORAL}" opacity="0.12"/>
      <rect x="-52" y="-168" width="104" height="52" rx="14" fill="url(#gold)"/>
      <rect x="-52" y="-168" width="104" height="52" rx="14" fill="none" stroke="#FFFFFF" stroke-opacity="0.35"/>
      <rect x="-68" y="36" width="136" height="100" rx="14" fill="#FFFFFF" opacity="0.5"/>
      <rect x="-42" y="62" width="84" height="7" rx="3.5" fill="{INK}" opacity="0.18"/>
      <rect x="-42" y="82" width="58" height="5" rx="2.5" fill="{INK}" opacity="0.12"/>
      <path d="M-73 -96C-58 -92 -44 -90 -30 -90" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="5" stroke-linecap="round"/>
    </g>
    """
    content = (
        bottle
        + capsule(1080, 420, 300, 118, -18, CORAL, mix(CREAM, CORAL, 0.12))
        + capsule(1180, 690, 260, 100, 16, GREEN, mix(CREAM, GREEN, 0.08))
        + capsule(880, 350, 210, 82, 28, YELLOW, mix(CREAM, YELLOW, 0.12))
        + f'<g opacity="0.8">{sprig(700, 610, -14, 1.3, GREEN, 0.55)}{sprig(1370, 700, 18, 1.1, GREEN, 0.4)}</g>'
        + orb(760, 350, 40, 0.6)
        + orb(1330, 330, 30, 0.55)
        + orb(980, 840, 54, 0.45)
        + constellation([(700, 230), (820, 190), (940, 240), (1080, 190), (1210, 250), (1340, 210)], GOLD, 0.5)
        + spark(1240, 470, 15)
        + spark(790, 470, 10, TURQ, 0.8)
        + spark(1430, 580, 12, CORAL, 0.7)
        + f'<rect x="620" y="190" width="760" height="700" fill="url(#dots)" opacity="0.45"/>'
    )
    return shell(content, CORAL, GREEN)


# ---------------------------------------------------------------------------
# 04 · Laboratorio
# ---------------------------------------------------------------------------
def art_laboratorio():
    def tube(x, y, rot, liquid, h=330, w=92):
        return f"""
        <g transform="translate({x} {y}) rotate({rot})" filter="url(#shadow)">
          <path d="M{-w/2} {-h/2}V{h/2 - w/2}A{w/2} {w/2} 0 0 0 {w/2} {h/2 - w/2}V{-h/2}" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.75" stroke-width="2"/>
          <path d="M{-w/2 + 5} {-h/2 + 165}V{h/2 - w/2 - 1}A{w/2 - 5} {w/2 - 5} 0 0 0 {w/2 - 5} {h/2 - w/2 - 1}V{-h/2 + 165}Z" fill="{liquid}" opacity="0.62"/>
          <ellipse cx="0" cy="{-h/2 + 165}" rx="{w/2 - 5}" ry="7" fill="#FFFFFF" opacity="0.35"/>
          <ellipse cx="0" cy="{-h/2}" rx="{w/2}" ry="10" fill="#FFFFFF" opacity="0.5"/>
          <path d="M{-w/2 + 12} {-h/2 + 30}V{h/2 - 40}" stroke="#FFFFFF" stroke-opacity="0.72" stroke-width="4" stroke-linecap="round"/>
          <g stroke="{INK}" stroke-opacity="0.18" stroke-width="1.4">
            <path d="M{w/2 - 18} {-30}H{w/2 - 4}M{w/2 - 18} {10}H{w/2 - 4}M{w/2 - 18} {50}H{w/2 - 4}"/>
          </g>
        </g>"""
    content = (
        f'<ellipse cx="1040" cy="800" rx="400" ry="80" fill="{DEEP}" opacity="0.1" filter="url(#blur28)"/>'
        + f'<g opacity="0.5">{wave_path(300, 52, 1600, TURQ, 0.42, 2.4)}{wave_path(350, 40, 1600, GREEN, 0.3, 1.6, 1.2)}{wave_path(410, 30, 1600, GOLD, 0.32, 1.4, 2.4)}</g>'
        + tube(900, 560, -10, TURQ) + tube(1040, 520, -2, GREEN, 370) + tube(1190, 570, 9, YELLOW, 320)
        + f'<g filter="url(#shadowSoft)"><ellipse cx="1310" cy="760" rx="170" ry="52" fill="url(#glass2)" stroke="#FFFFFF" stroke-opacity="0.7"/><ellipse cx="1310" cy="752" rx="126" ry="34" fill="none" stroke="{TURQ}" stroke-opacity="0.5" stroke-width="1.4"/></g>'
        + orb(800, 340, 46, 0.56)
        + orb(1270, 300, 28, 0.6)
        + orb(980, 250, 16, 0.6)
        + f'<path d="M960 320C970 300 990 300 1000 320C1000 342 980 354 980 354C980 354 960 342 960 320Z" fill="{TURQ}" opacity="0.55"/>'
        + f'<path d="M1140 760C1150 740 1170 740 1180 760C1180 782 1160 794 1160 794C1160 794 1140 782 1140 760Z" fill="{GREEN}" opacity="0.5"/>'
        + constellation([(760, 220), (860, 260), (980, 210), (1110, 260), (1230, 210), (1340, 260)], GOLD, 0.5)
        + spark(1320, 470, 15)
        + spark(840, 650, 10, GREEN, 0.8)
        + f'<rect x="650" y="200" width="760" height="660" fill="url(#dots)" opacity="0.45"/>'
    )
    return shell(content, TURQ, GREEN)


# ---------------------------------------------------------------------------
# 05 · Neurología
# ---------------------------------------------------------------------------
def art_neurologia():
    brain = f"""
    <g filter="url(#shadow)">
      <path d="M1010 264C940 236 866 264 850 330C788 344 760 412 800 456C762 506 798 578 858 586C874 646 948 676 1009 642V264Z" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.65" stroke-width="2.5"/>
      <path d="M1010 264C1080 236 1154 264 1170 330C1232 344 1260 412 1220 456C1258 506 1222 578 1162 586C1146 646 1072 676 1011 642V264Z" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.65" stroke-width="2.5"/>
      <path d="M1010 270V650" stroke="{VIOLET}" stroke-opacity="0.35" stroke-width="2" stroke-dasharray="3 8"/>
      <g fill="none" stroke="{VIOLET}" stroke-opacity="0.55" stroke-width="2" stroke-linecap="round">
        <path d="M1008 330C958 326 926 348 914 382C948 402 980 400 1008 386"/>
        <path d="M1008 420C948 410 902 434 888 474C926 500 972 496 1008 478"/>
        <path d="M1008 512C962 508 930 532 920 566C952 588 984 584 1008 570"/>
        <path d="M1012 356C1058 344 1094 364 1110 396C1078 420 1044 418 1012 406"/>
        <path d="M1012 450C1068 438 1112 462 1126 500C1090 526 1044 522 1012 504"/>
        <path d="M1012 548C1054 540 1086 562 1096 594C1064 616 1032 610 1012 596"/>
      </g>
    </g>
    """
    nodes = [(950, 348), (960, 470), (930, 560), (1060, 374), (1080, 480), (1050, 580), (910, 410), (1100, 430)]
    node_markup = "".join(
        f'<circle cx="{x}" cy="{y}" r="7" fill="{GOLD}" opacity="0.9"/><circle cx="{x}" cy="{y}" r="16" fill="none" stroke="{VIOLET}" stroke-opacity="0.4"/>'
        for x, y in nodes
    )
    net = "".join(
        f'<line x1="{nodes[i][0]}" y1="{nodes[i][1]}" x2="{nodes[i+1][0]}" y2="{nodes[i+1][1]}" stroke="{VIOLET}" stroke-opacity="0.25" stroke-width="1"/>'
        for i in range(0, len(nodes) - 1, 2)
    )
    content = (
        f'<ellipse cx="1050" cy="500" rx="480" ry="420" fill="url(#aura)" opacity="0.8"/>'
        + f'<g filter="url(#blur60)" opacity="0.5"><ellipse cx="820" cy="770" rx="300" ry="100" fill="{VIOLET}"/><ellipse cx="1280" cy="730" rx="260" ry="90" fill="{TURQ}"/></g>'
        + brain + net + node_markup
        + f'<ellipse cx="1040" cy="470" rx="340" ry="300" transform="rotate(-18 1040 470)" fill="none" stroke="{GOLD}" stroke-opacity="0.42" stroke-width="1.4"/>'
        + f'<ellipse cx="1040" cy="470" rx="400" ry="360" transform="rotate(14 1040 470)" fill="none" stroke="{TURQ}" stroke-opacity="0.24" stroke-width="1" stroke-dasharray="2 10"/>'
        + orb(760, 300, 34, 0.55) + orb(1350, 360, 50, 0.5) + orb(1370, 760, 30, 0.5)
        + constellation([(720, 220), (820, 270), (920, 220), (1020, 270), (1120, 220), (1230, 270), (1340, 220)], GOLD, 0.45)
        + spark(1260, 640, 16, VIOLET, 0.8) + spark(810, 600, 11, TURQ, 0.8)
        + sprig(600, 780, 8, 1.1, VIOLET, 0.35)
        + f'<rect x="660" y="210" width="760" height="650" fill="url(#dots)" opacity="0.4"/>'
    )
    return shell(content, VIOLET, TURQ)


# ---------------------------------------------------------------------------
# 06 · Cardiología
# ---------------------------------------------------------------------------
def art_cardiologia():
    heart = f"""
    <g filter="url(#shadow)">
      <path d="M1040 780C1010 742 850 616 850 470C850 370 930 314 1015 344C1026 348 1034 353 1040 358C1046 353 1054 348 1065 344C1150 314 1230 370 1230 470C1230 616 1070 742 1040 780Z" fill="url(#a)" opacity="0.82"/>
      <path d="M1040 780C1010 742 850 616 850 470C850 370 930 314 1015 344C1026 348 1034 353 1040 358C1046 353 1054 348 1065 344C1150 314 1230 370 1230 470C1230 616 1070 742 1040 780Z" fill="url(#glass)" opacity="0.55"/>
      <path d="M1040 780C1010 742 850 616 850 470C850 370 930 314 1015 344C1026 348 1034 353 1040 358C1046 353 1054 348 1065 344C1150 314 1230 370 1230 470C1230 616 1070 742 1040 780Z" fill="none" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="2.5"/>
      <path d="M930 400C900 430 888 470 892 512" fill="none" stroke="#FFFFFF" stroke-opacity="0.65" stroke-width="8" stroke-linecap="round"/>
      <path d="M1050 410C1080 470 1100 540 1082 610" fill="none" stroke="{CORAL}" stroke-opacity="0.4" stroke-width="3" stroke-linecap="round"/>
    </g>
    """
    ribbon = f"""
    <path d="M690 610C820 500 860 720 1010 650C1160 580 1160 350 1320 330C1410 318 1470 360 1490 410" fill="none" stroke="url(#gold)" stroke-opacity="0.75" stroke-width="7" stroke-linecap="round"/>
    <path d="M690 610C820 500 860 720 1010 650C1160 580 1160 350 1320 330C1410 318 1470 360 1490 410" fill="none" stroke="#FFFFFF" stroke-opacity="0.28" stroke-width="2" stroke-linecap="round"/>
    """
    ecg = f'<path d="M560 860H760L800 860L824 800L852 920L884 700L920 860H1080L1110 860L1134 820L1160 890L1186 820L1210 860H1430" fill="none" stroke="{GOLD}" stroke-opacity="0.72" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    petals = "".join(
        f'<path d="M{x} {y}C{x-30} {y-58} {x+42} {y-70} {x+20} {y}C{x+52} {y+18} {x+8} {y+48} {x} {y}Z" fill="{CORAL}" opacity="{opacity}" transform="rotate({rot} {x} {y})"/>'
        for x, y, rot, opacity in [(760, 420, 24, 0.4), (1320, 600, -30, 0.34), (1180, 300, 12, 0.3), (860, 780, 40, 0.28)]
    )
    content = (
        petals + ribbon + heart + ecg
        + f'<ellipse cx="1040" cy="500" rx="380" ry="330" transform="rotate(-22 1040 500)" fill="none" stroke="{GOLD}" stroke-opacity="0.35" stroke-width="1.3"/>'
        + orb(780, 330, 38, 0.55) + orb(1340, 450, 30, 0.55) + orb(900, 850, 46, 0.42)
        + constellation([(700, 222), (820, 260), (940, 210), (1060, 250), (1180, 205), (1300, 250)], CORAL, 0.4)
        + spark(1300, 330, 16, GOLD) + spark(760, 560, 10, CORAL, 0.7)
        + sprig(620, 790, 6, 1.1, CORAL, 0.3)
        + f'<rect x="630" y="210" width="790" height="680" fill="url(#dots)" opacity="0.4"/>'
    )
    return shell(content, CORAL, GOLD)


# ---------------------------------------------------------------------------
# 07 · Fisiatría
# ---------------------------------------------------------------------------
def art_fisiatria():
    body = f"""
    <g filter="url(#shadow)" stroke-linecap="round" stroke-linejoin="round" fill="none">
      <path d="M1010 300C1010 264 1040 244 1072 260C1104 276 1104 322 1072 336C1044 348 1012 334 1010 300Z" fill="url(#glass2)" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="3"/>
      <path d="M1040 350C1020 430 1008 500 1012 580C1018 650 1050 700 1080 770C1094 804 1090 846 1072 880" stroke="url(#a)" stroke-width="34" opacity="0.88"/>
      <path d="M1034 392C974 406 930 450 912 516" stroke="url(#a)" stroke-width="28" opacity="0.82"/>
      <path d="M1040 392C1104 398 1152 438 1180 500C1202 550 1200 600 1178 640" stroke="url(#b)" stroke-width="28" opacity="0.78"/>
      <path d="M1014 584C952 620 916 676 912 740C908 796 928 844 960 884" stroke="url(#b)" stroke-width="30" opacity="0.8"/>
      <path d="M1020 584C1072 626 1096 682 1088 748C1082 798 1062 836 1032 870" stroke="url(#a)" stroke-width="30" opacity="0.72"/>
    </g>
    """
    joints = "".join(
        f'<g>{orb(x, y, r, 0.62, GOLD)}</g>'
        for x, y, r in [(1040, 350, 22), (1034, 398, 18), (1012, 580, 24), (960, 884, 16), (1032, 870, 16)]
    )
    arcs = f"""
    <g fill="none" stroke-linecap="round">
      <path d="M740 860C770 610 930 390 1140 300" stroke="{GOLD}" stroke-opacity="0.38" stroke-width="1.4" stroke-dasharray="2 9"/>
      <path d="M820 900C820 650 940 450 1130 370" stroke="{TURQ}" stroke-opacity="0.38" stroke-width="1.2" stroke-dasharray="2 10"/>
      <path d="M1210 800C1260 640 1250 500 1180 380" stroke="{GREEN}" stroke-opacity="0.3" stroke-width="1.2" stroke-dasharray="2 10"/>
    </g>
    """
    content = (
        arcs + body + joints
        + f'<circle cx="1080" cy="560" r="300" fill="none" stroke="{GOLD}" stroke-opacity="0.28" stroke-width="1.3"/>'
        + f'<circle cx="1080" cy="560" r="360" fill="none" stroke="{TURQ}" stroke-opacity="0.2" stroke-width="1" stroke-dasharray="2 12"/>'
        + orb(760, 300, 38, 0.5) + orb(1350, 680, 52, 0.5) + orb(700, 690, 26, 0.5)
        + constellation([(700, 220), (820, 260), (940, 210), (1060, 250), (1180, 205), (1300, 250)], GOLD, 0.45)
        + spark(1240, 330, 15, TURQ, 0.8) + spark(850, 760, 11, GOLD, 0.8)
        + leaf(1380, 430, -24, 0.85, GREEN, 0.4)
        + f'<rect x="680" y="200" width="720" height="700" fill="url(#dots)" opacity="0.42"/>'
    )
    return shell(content, TURQ, GREEN)


# ---------------------------------------------------------------------------
# 08 · Rehabilitación
# ---------------------------------------------------------------------------
def art_rehabilitacion():
    steps = ""
    for i, (x, y, w, h) in enumerate([(760, 840, 190, 74), (860, 760, 200, 70), (970, 668, 210, 68), (1090, 560, 220, 66), (1210, 440, 230, 64)]):
        steps += f"""
        <g filter="url(#shadowSoft)">
          <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="url(#glass2)" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="2"/>
          <rect x="{x+8}" y="{y+8}" width="{w-16}" height="{h-16}" rx="{(h-16)/2}" fill="none" stroke="{GOLD}" stroke-opacity="0.28" stroke-width="1.2" stroke-dasharray="2 7"/>
          <circle cx="{x+w-26}" cy="{y+h/2}" r="7" fill="{GOLD}" opacity="0.8"/>
        </g>"""
    band = f"""
    <g filter="url(#shadow)">
      <ellipse cx="1060" cy="610" rx="290" ry="170" transform="rotate(-28 1060 610)" fill="none" stroke="url(#a)" stroke-width="28" opacity="0.34"/>
      <ellipse cx="1060" cy="610" rx="290" ry="170" transform="rotate(-28 1060 610)" fill="none" stroke="#FFFFFF" stroke-opacity="0.28" stroke-width="3"/>
    </g>"""
    plant = f"""
    <g transform="translate(1330 690) scale(1.1)" filter="url(#shadowSoft)">
      <path d="M0 120V-10" stroke="{GREEN}" stroke-width="4" stroke-linecap="round"/>
      <path d="M0 40C-42 38 -70 12 -76 -26C-34 -30 -4 -4 0 40Z" fill="{GREEN}" opacity="0.65"/>
      <path d="M0 10C36 8 64 -18 70 -54C32 -56 4 -30 0 10Z" fill="{mix(GREEN, '#FFFFFF', 0.15)}" opacity="0.75"/>
      <path d="M0 76C-38 74 -62 52 -68 20C-30 16 -4 40 0 76Z" fill="{TURQ}" opacity="0.5"/>
    </g>"""
    content = (
        steps + band + plant
        + f'<path d="M690 900C760 760 870 640 1030 560C1130 510 1230 500 1320 520" fill="none" stroke="{GOLD}" stroke-opacity="0.5" stroke-width="1.4" stroke-dasharray="2 9"/>'
        + f'<circle cx="1050" cy="580" r="380" fill="none" stroke="{GREEN}" stroke-opacity="0.22" stroke-width="1.2"/>'
        + orb(820, 320, 42, 0.55) + orb(1350, 320, 30, 0.55) + orb(730, 610, 22, 0.5)
        + constellation([(700, 230), (820, 270), (940, 220), (1060, 260), (1180, 215), (1300, 260)], GOLD, 0.45)
        + spark(1260, 300, 16) + spark(820, 470, 10, TURQ, 0.8)
        + leaf(620, 760, 14, 0.95, GREEN, 0.45)
        + f'<rect x="650" y="210" width="770" height="730" fill="url(#dots)" opacity="0.45"/>'
    )
    return shell(content, GREEN, GOLD)


# ---------------------------------------------------------------------------
# 09 · Fonoaudiología
# ---------------------------------------------------------------------------
def art_fonoaudiologia():
    waves = ""
    for i, r in enumerate([90, 160, 235, 315, 405, 500]):
        waves += f'<circle cx="930" cy="540" r="{r}" fill="none" stroke="{GOLD if i % 2 == 0 else TURQ}" stroke-opacity="{0.42 - i * 0.045}" stroke-width="{2.4 - i * 0.22}"/>'
    ear = f"""
    <g transform="translate(1080 520)" filter="url(#shadowSoft)">
      <path d="M100 -170C180 -110 190 10 130 80C92 124 44 138 10 116C-24 94 -22 56 4 46C30 36 48 56 40 82" fill="none" stroke="url(#a)" stroke-width="18" stroke-linecap="round"/>
      <path d="M62 -112C112 -70 118 20 74 66" fill="none" stroke="{GOLD}" stroke-opacity="0.62" stroke-width="2.4" stroke-linecap="round"/>
      <path d="M62 -112C112 -70 118 20 74 66" fill="none" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="1"/>
    </g>"""
    content = (
        waves + ear
        + f'<path d="M620 850C720 810 780 900 880 860C980 820 1030 900 1130 860C1230 820 1290 890 1390 850" fill="none" stroke="{GOLD}" stroke-opacity="0.4" stroke-width="2" stroke-linecap="round"/>'
        + orb(800, 320, 38, 0.55) + orb(1320, 330, 28, 0.55) + orb(1250, 800, 52, 0.45)
        + f'<circle cx="930" cy="540" r="30" fill="url(#sun)" opacity="0.8"/>'
        + constellation([(700, 230), (820, 270), (940, 220), (1060, 260), (1180, 215), (1300, 260)], GOLD, 0.5)
        + spark(1320, 500, 15, YELLOW, 0.9) + spark(760, 650, 11, TURQ, 0.8)
        + sprig(620, 790, 12, 1.0, TURQ, 0.4)
        + f'<rect x="650" y="200" width="760" height="720" fill="url(#dots)" opacity="0.45"/>'
    )
    return shell(content, YELLOW, TURQ)


# ---------------------------------------------------------------------------
# 10 · Psiquiatría
# ---------------------------------------------------------------------------
def art_psiquiatria():
    petals = ""
    import math

    for i in range(9):
        angle = i * 40
        petals += f'<path d="M1040 540C1040 400 1088 330 1152 310C1200 380 1180 480 1100 540Z" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.5" stroke-width="1.6" transform="rotate({angle} 1040 540)"/>'
        petals += f'<path d="M1040 540C1040 430 1074 370 1124 350" fill="none" stroke="{VIOLET}" stroke-opacity="0.28" stroke-width="1.2" transform="rotate({angle} 1040 540)"/>'
    bloom = f"""
    <g filter="url(#shadow)">
      {petals}
      <circle cx="1040" cy="540" r="90" fill="url(#sun)" opacity="0.9"/>
      <circle cx="1040" cy="540" r="90" fill="none" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="2"/>
      <circle cx="1040" cy="540" r="46" fill="{mix(VIOLET, '#FFFFFF', 0.45)}" opacity="0.55"/>
    </g>"""
    clouds = f"""
    <g filter="url(#blur28)" opacity="0.55">
      <ellipse cx="760" cy="810" rx="260" ry="74" fill="{mix(VIOLET, '#FFFFFF', 0.55)}"/>
      <ellipse cx="940" cy="850" rx="310" ry="86" fill="{mix(VIOLET, '#FFFFFF', 0.7)}"/>
      <ellipse cx="1240" cy="800" rx="270" ry="78" fill="{mix(TURQ, '#FFFFFF', 0.6)}"/>
    </g>"""
    content = (
        clouds + bloom
        + f'<circle cx="1040" cy="540" r="380" fill="none" stroke="{GOLD}" stroke-opacity="0.3" stroke-width="1.3"/>'
        + f'<circle cx="1040" cy="540" r="440" fill="none" stroke="{SILVER}" stroke-opacity="0.35" stroke-width="1" stroke-dasharray="2 12"/>'
        + orb(760, 300, 40, 0.55) + orb(1360, 360, 30, 0.55) + orb(700, 620, 22, 0.5)
        + constellation([(700, 230), (820, 270), (940, 220), (1060, 260), (1180, 215), (1300, 260)], SILVER, 0.55)
        + spark(1260, 420, 16, VIOLET, 0.8) + spark(820, 500, 11, GOLD, 0.8)
        + f'<path d="M620 730C720 700 780 760 880 730C980 700 1030 760 1130 730C1230 700 1290 750 1390 720" fill="none" stroke="{VIOLET}" stroke-opacity="0.25" stroke-width="1.6"/>'
        + f'<rect x="650" y="200" width="760" height="710" fill="url(#dots)" opacity="0.4"/>'
    )
    return shell(content, VIOLET, SILVER)


# ---------------------------------------------------------------------------
# 11 · Traumatología superior
# ---------------------------------------------------------------------------
def art_traumatologia_superior():
    bones = f"""
    <g filter="url(#shadow)">
      <path d="M1000 300C1038 296 1064 324 1060 362C1056 392 1038 408 1042 438L1068 642C1070 668 1052 688 1028 688C1004 688 988 670 990 646L1014 438C1014 410 994 392 992 362C990 326 964 304 1000 300Z" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="2.5"/>
      <path d="M1050 350C1060 360 1064 380 1060 396" fill="none" stroke="{CORAL}" stroke-opacity="0.35" stroke-width="2"/>
      <path d="M920 470C950 420 1010 400 1060 416C1110 432 1138 478 1132 530C1128 570 1102 602 1064 614" fill="url(#glass2)" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="2.5"/>
      <path d="M820 500C850 454 900 430 950 438C990 444 1016 470 1028 504" fill="none" stroke="url(#silver)" stroke-width="20" stroke-linecap="round"/>
      <path d="M820 500C850 454 900 430 950 438C990 444 1016 470 1028 504" fill="none" stroke="#FFFFFF" stroke-opacity="0.4" stroke-width="4" stroke-linecap="round"/>
      <circle cx="1030" cy="452" r="48" fill="url(#glass)" stroke="{GOLD}" stroke-opacity="0.5" stroke-width="2"/>
      <circle cx="1030" cy="452" r="20" fill="{CORAL}" opacity="0.4"/>
    </g>"""
    grid = f'<rect x="730" y="220" width="620" height="620" fill="url(#grid)" opacity="0.7"/>'
    content = (
        grid + bones
        + f'<circle cx="1040" cy="520" r="330" fill="none" stroke="{CORAL}" stroke-opacity="0.22" stroke-width="1.2" stroke-dasharray="3 10"/>'
        + orb(780, 300, 36, 0.5) + orb(1340, 650, 48, 0.5)
        + constellation([(700, 230), (820, 270), (940, 220), (1060, 260), (1180, 215), (1300, 260)], GOLD, 0.45)
        + spark(1280, 340, 15) + spark(820, 620, 10, CORAL, 0.75)
        + leaf(1370, 440, -26, 0.9, CORAL, 0.32)
        + f'<rect x="650" y="200" width="760" height="700" fill="url(#dots)" opacity="0.4"/>'
    )
    return shell(content, CORAL, SILVER)


# ---------------------------------------------------------------------------
# 12 · Traumatología inferior
# ---------------------------------------------------------------------------
def art_traumatologia_inferior():
    spine = ""
    coords = [(1050, 250), (1042, 330), (1030, 410), (1016, 490), (1000, 570), (986, 650), (978, 730)]
    for i, (x, y) in enumerate(coords):
        spine += f"""
        <g filter="url(#shadowSoft)">
          <rect x="{x-82}" y="{y-28}" width="164" height="56" rx="28" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.65" stroke-width="2"/>
          <rect x="{x-62}" y="{y-16}" width="124" height="32" rx="16" fill="none" stroke="{GOLD}" stroke-opacity="0.3" stroke-width="1" stroke-dasharray="2 6"/>
          <circle cx="{x}" cy="{y}" r="7" fill="url(#gold)" opacity="0.75"/>
        </g>"""
    pelvis = f"""
    <g opacity="0.72" filter="url(#shadowSoft)">
      <path d="M810 800C850 730 940 700 1020 728C1080 750 1100 810 1080 860C1060 910 1000 930 960 900C920 870 910 820 930 780" fill="none" stroke="url(#a)" stroke-width="26" stroke-linecap="round"/>
      <path d="M960 900C970 960 970 1010 950 1060" fill="none" stroke="url(#b)" stroke-width="26" stroke-linecap="round"/>
    </g>"""
    dunes = f"""
    <g opacity="0.5">
      <path d="M-80 930C160 850 380 900 600 940C840 984 1060 900 1280 920C1440 934 1580 980 1680 960V1120H-80Z" fill="{mix(YELLOW, CREAM, 0.5)}"/>
      <path d="M-80 1010C200 950 420 1000 640 1020C900 1044 1100 980 1320 1000C1460 1012 1580 1048 1680 1040V1120H-80Z" fill="{mix(GREEN, CREAM, 0.5)}" opacity="0.55"/>
    </g>"""
    content = (
        dunes + spine + pelvis
        + f'<path d="M740 300C780 500 790 700 760 900" fill="none" stroke="{YELLOW}" stroke-opacity="0.5" stroke-width="1.2" stroke-dasharray="2 9"/>'
        + f'<circle cx="1000" cy="500" r="360" fill="none" stroke="{YELLOW}" stroke-opacity="0.2" stroke-width="1.2"/>'
        + orb(770, 320, 38, 0.5) + orb(1340, 400, 52, 0.5) + orb(1360, 760, 24, 0.5)
        + constellation([(700, 230), (820, 270), (940, 220), (1060, 260), (1180, 215), (1300, 260)], GOLD, 0.45)
        + spark(1240, 580, 15) + spark(830, 760, 10, TURQ, 0.8)
        + sprig(620, 790, 10, 1.0, GREEN, 0.4)
        + f'<rect x="650" y="210" width="760" height="710" fill="url(#dots)" opacity="0.42"/>'
    )
    return shell(content, YELLOW, TURQ)


# ---------------------------------------------------------------------------
# 13 · Emergencia
# ---------------------------------------------------------------------------
def art_emergencia():
    beam = f"""
    <g filter="url(#blur60)" opacity="0.65">
      <path d="M1050 180L720 1100H1440Z" fill="{CORAL}"/>
    </g>
    <g filter="url(#blur28)" opacity="0.55">
      <path d="M1050 250L860 1100H1260Z" fill="{mix(CORAL, YELLOW, 0.4)}"/>
    </g>"""
    cross = f"""
    <g transform="translate(1050 470)" filter="url(#shadow)">
      <rect x="-96" y="-96" width="192" height="192" rx="54" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="2.5"/>
      <rect x="-20" y="-60" width="40" height="120" rx="20" fill="url(#a)"/>
      <rect x="-60" y="-20" width="120" height="40" rx="20" fill="url(#a)"/>
      <circle cx="-52" cy="-52" r="6" fill="{GOLD}"/>
    </g>"""
    phone = f"""
    <g transform="translate(790 760) rotate(-14)" filter="url(#shadow)">
      <path d="M-120 -60C-110 -100 -70 -108 -40 -82C-12 -58 -20 -26 -44 -10C-18 26 20 62 62 82C82 60 114 58 136 84C158 110 148 148 112 160C68 176 0 130 -62 68C-122 6 -158 -60 -148 -98C-144 -114 -132 -122 -120 -120Z" fill="url(#glass2)" stroke="#FFFFFF" stroke-opacity="0.65" stroke-width="2"/>
      <path d="M-106 -58C-96 -88 -68 -94 -46 -74" fill="none" stroke="#FFFFFF" stroke-opacity="0.5" stroke-width="5" stroke-linecap="round"/>
    </g>"""
    pulse = f'<path d="M520 860H760L790 860L812 810L838 920L866 730L900 860H1040L1068 860L1090 820L1114 900L1138 820L1162 860H1360" fill="none" stroke="{GOLD}" stroke-opacity="0.8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    content = (
        beam + cross + phone + pulse
        + f'<circle cx="1050" cy="470" r="300" fill="none" stroke="{CORAL}" stroke-opacity="0.3" stroke-width="1.4"/>'
        + f'<circle cx="1050" cy="470" r="370" fill="none" stroke="{GOLD}" stroke-opacity="0.3" stroke-width="1" stroke-dasharray="2 12"/>'
        + orb(700, 330, 46, 0.4) + orb(1330, 330, 30, 0.4) + orb(1280, 720, 22, 0.4)
        + constellation([(700, 230), (820, 270), (940, 220), (1060, 260), (1180, 215), (1300, 260)], GOLD, 0.45)
        + spark(1280, 600, 16, CORAL, 0.9) + spark(800, 470, 11, GOLD, 0.8)
        + f'<g filter="url(#blur60)" opacity="0.5"><ellipse cx="720" cy="940" rx="320" ry="90" fill="{CORAL}"/><ellipse cx="1300" cy="980" rx="300" ry="80" fill="{YELLOW}"/></g>'
            + f'<rect x="620" y="190" width="800" height="780" fill="url(#dots)" opacity="0.25"/>'
    )
    return shell(content, CORAL, GOLD, dark_bg=True)


ARTWORKS = {
    "inicio": art_inicio,
    "diagnosticos": art_diagnosticos,
    "medicamentos": art_medicamentos,
    "laboratorio": art_laboratorio,
    "neurologia": art_neurologia,
    "cardiologia": art_cardiologia,
    "fisiatria": art_fisiatria,
    "rehabilitacion": art_rehabilitacion,
    "fonoaudiologia": art_fonoaudiologia,
    "psiquiatria": art_psiquiatria,
    "traumatologia-superior": art_traumatologia_superior,
    "traumatologia-inferior": art_traumatologia_inferior,
    "emergencia": art_emergencia,
}

if __name__ == "__main__":
    for name, fn in ARTWORKS.items():
        path = OUT / f"{name}.svg"
        path.write_text(fn(), encoding="utf-8")
        print(f"{path}  {path.stat().st_size / 1024:.1f} KB")
