# -*- coding: utf-8 -*-
"""
Generador de documentos clínicos de DEMOSTRACIÓN para saludrcartes.

Todos los PDF resultantes llevan marca de agua y la leyenda
"DOCUMENTO DE EJEMPLO — SIN VALOR CLÍNICO". No contienen datos reales.

Uso:
    python tools/generate-demo-pdfs.py

Requiere PyMuPDF (pip install pymupdf).
"""

from __future__ import annotations

import math
import os
import random
from datetime import datetime
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "docs"
OUT.mkdir(parents=True, exist_ok=True)

FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_ITAL = r"C:\Windows\Fonts\segoeuii.ttf"

W, H = 595, 842
ML, MR = 48, 547
CONTENT_W = MR - ML
FOOT_Y = 790

# Paleta del sitio
INK = "#22312B"
MUTED = "#5D6C64"
GREEN = "#1D6B50"
GREEN_DARK = "#14503B"
CORAL = "#B84337"
CORAL_DARK = "#963127"
CREAM = "#FFF8F0"
CREAM_DARK = "#F8EFE3"
LINE = "#E5DBCE"
TURQ = "#247C79"
AMBER = "#8A5D10"
VIOLET = "#5E4A9E"
WHITE = "#FFFFFF"
RED_SOFT = "#FBE9E5"
GREEN_SOFT = "#E8F1EC"
AMBER_SOFT = "#FBF1DC"
VIOLET_SOFT = "#EEEAF7"
TURQ_SOFT = "#E6F2F1"

FONTS = {
    "sg": FONT_REG,
    "sgb": FONT_BOLD,
    "sgi": FONT_ITAL,
}
MEASURE = {k: fitz.Font(fontfile=v) for k, v in FONTS.items()}

DOCUMENTS = []


def rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))


def font_for(name: str) -> str:
    return name if name in FONTS else "sg"


def text_width(text: str, size: float, font: str = "sg") -> float:
    return MEASURE[font].text_length(text, fontsize=size)


def wrap(text: str, size: float, max_width: float, font: str = "sg") -> list[str]:
    words = text.split()
    lines, current = [], ""
    for word in words:
        probe = (current + " " + word).strip()
        if text_width(probe, size, font) <= max_width or not current:
            current = probe
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fmt_date(iso: str) -> str:
    try:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%d-%m-%Y")
    except ValueError:
        return iso


def register(page: fitz.Page) -> None:
    page.insert_font(fontname="sg", fontfile=FONT_REG)
    page.insert_font(fontname="sgb", fontfile=FONT_BOLD)
    page.insert_font(fontname="sgi", fontfile=FONT_ITAL)


def draw_header(page: fitz.Page, title: str, meta: dict, continuation: bool = False) -> None:
    # Barra superior cálida
    page.draw_rect(fitz.Rect(0, 0, W, 8), color=None, fill=rgb(GREEN))

    # Marca
    cx, cy, r = 58, 44, 13
    page.draw_circle((cx, cy), r, color=None, fill=rgb(GREEN))
    page.draw_rect(fitz.Rect(cx - 1.7, cy - 7, cx + 1.7, cy + 7), color=None, fill=rgb(CREAM))
    page.draw_rect(fitz.Rect(cx - 7, cy - 1.7, cx + 7, cy + 1.7), color=None, fill=rgb(CREAM))

    page.insert_text((79, 40), "saludrcartes", fontsize=15, fontname="sgb", color=rgb(GREEN_DARK))
    page.insert_text((79.5, 52), "REGISTRO CLÍNICO PERSONAL", fontsize=6.6, fontname="sgb", color=rgb(MUTED))

    # Etiqueta de ejemplo
    label = "FICHA DE EJEMPLO"
    lw = text_width(label, 6.8, "sgb") + 16
    page.draw_rect(fitz.Rect(MR - lw, 31, MR, 45), color=None, fill=rgb(RED_SOFT), radius=0.18)
    page.insert_text((MR - lw + 8, 40.4), label, fontsize=6.8, fontname="sgb", color=rgb(CORAL_DARK))

    # Línea y datos del documento
    page.draw_line((ML, 66), (MR, 66), color=rgb(LINE), width=0.7)
    doc_id = meta.get("doc_id", "DEMO")
    page.insert_text((ML, 78), title if not continuation else title + " · continuación", fontsize=7.6, fontname="sgb", color=rgb(MUTED))
    id_text = doc_id
    page.insert_text((MR - text_width(id_text, 7.2), 78), id_text, fontsize=7.2, fontname="sg", color=rgb(MUTED))

    # Franja del paciente
    strip = fitz.Rect(ML, 88, MR, 124)
    page.draw_rect(strip, color=None, fill=rgb(CREAM), radius=0.10)
    page.draw_rect(fitz.Rect(ML, 88, ML + 3, 124), color=None, fill=rgb(CORAL))
    page.insert_text((ML + 13, 102), "PACIENTE", fontsize=6.4, fontname="sgb", color=rgb(MUTED))
    page.insert_text((ML + 13, 115), meta.get("patient", "Roberto Carlos Cartes Jiménez"), fontsize=10, fontname="sgb", color=rgb(INK))
    right = f"Grupo sanguíneo {meta.get('blood', 'O+')}  ·  Ficha {doc_id}"
    page.insert_text((MR - text_width(right, 7.6) - 12, 114), right, fontsize=7.6, fontname="sg", color=rgb(MUTED))
    page.insert_text((MR - text_width("Datos de demostración", 6.8) - 12, 101), "Datos de demostración", fontsize=6.8, fontname="sgb", color=rgb(CORAL))


def draw_footer(page: fitz.Page, number: int) -> None:
    page.draw_line((ML, 770), (MR, 770), color=rgb(LINE), width=0.6)
    page.insert_text((ML, 782), "saludrcartes · Documento de demostración", fontsize=7.2, fontname="sg", color=rgb(MUTED))
    page.insert_text((ML, 793), "No usar para decisiones clínicas. Reemplazar por el documento original.", fontsize=6.6, fontname="sgi", color=rgb(MUTED))
    p = f"Página {number}"
    page.insert_text((MR - text_width(p, 7.2), 782), p, fontsize=7.2, fontname="sg", color=rgb(MUTED))
    sin = "SIN VALOR CLÍNICO"
    page.insert_text((MR - text_width(sin, 6.6, "sgb"), 793), sin, fontsize=6.6, fontname="sgb", color=rgb(CORAL))


def draw_watermark(page: fitz.Page) -> None:
    """Marca de agua diagonal sutil, dibujada DEBAJO del contenido."""
    font = fitz.Font(fontfile=FONT_BOLD)
    matrix = fitz.Matrix(1, 1).prerotate(30)
    for text, pos, pivot, size in (
        ("DOCUMENTO DE EJEMPLO", (26, 395), (220, 410), 18),
        ("SIN VALOR CLÍNICO", (235, 690), (330, 700), 18),
    ):
        writer = fitz.TextWriter(page.rect)
        writer.append(pos, text, font=font, fontsize=size)
        writer.write_text(page, color=rgb("#F3DDD6"), opacity=0.65, morph=(fitz.Point(*pivot), matrix))


class Doc:
    def __init__(self, filename: str, title: str, meta: dict, toc_title: str | None = None):
        self.filename = filename
        self.title = title
        self.meta = meta
        self.toc_title = toc_title or title
        self.doc = fitz.open()
        self.doc.set_metadata(
            {
                "title": title,
                "author": "saludrcartes — demostración",
                "subject": "Documento clínico de ejemplo. Sin valor clínico.",
                "keywords": "saludrcartes, demostración, sin valor clínico, " + meta.get("doc_id", ""),
                "creator": "saludrcartes demo generator",
                "producer": "PyMuPDF",
            }
        )
        self.page = self._new_page(continuation=False)
        self.y = 146

    def _new_page(self, continuation: bool) -> fitz.Page:
        page = self.doc.new_page(width=W, height=H)
        register(page)
        draw_watermark(page)
        draw_header(page, self.title, self.meta, continuation)
        return page

    def ensure(self, height: float) -> None:
        if self.y + height > 760:
            self.page = self._new_page(continuation=True)
            self.y = 146

    def page_break(self) -> None:
        self.page = self._new_page(continuation=True)
        self.y = 146

    def ruled_notes(self, lines: int = 6) -> None:
        self.ensure(lines * 20 + 8)
        for _ in range(lines):
            self.page.draw_line((ML, self.y + 13), (MR, self.y + 13), color=rgb(LINE), width=0.55)
            self.y += 20
        self.y += 4

    def eyebrow(self, text: str, color: str = CORAL) -> None:
        self.ensure(16)
        self.page.insert_text((ML, self.y), text.upper(), fontsize=7, fontname="sgb", color=rgb(color))
        self.y += 13

    def heading(self, text: str, color: str = GREEN_DARK) -> None:
        self.ensure(34)
        self.page.draw_rect(fitz.Rect(ML, self.y - 9, ML + 3, self.y + 5), color=None, fill=rgb(color))
        self.page.insert_text((ML + 11, self.y), text, fontsize=11.8, fontname="sgb", color=rgb(color))
        self.page.draw_line((ML, self.y + 7), (MR, self.y + 7), color=rgb(LINE), width=0.6)
        self.y += 20

    def paragraph(self, text: str, size: float = 9.5, color: str = INK, gap: float = 5, italic: bool = False) -> None:
        font = "sgi" if italic else "sg"
        lines = wrap(text, size, CONTENT_W, font)
        lh = size * 1.34
        height = len(lines) * lh + gap
        self.ensure(height)
        for line in lines:
            self.page.insert_text((ML, self.y), line, fontsize=size, fontname=font, color=rgb(color))
            self.y += lh
        self.y += gap

    def small(self, text: str, color: str = MUTED, gap: float = 5, size: float = 7.8) -> None:
        lines = wrap(text, size, CONTENT_W, "sg")
        self.ensure(len(lines) * size * 1.35 + gap)
        for line in lines:
            self.page.insert_text((ML, self.y), line, fontsize=size, fontname="sg", color=rgb(color))
            self.y += size * 1.35
        self.y += gap

    def kv(self, items: list[tuple[str, str]], columns: int = 2) -> None:
        rows = math.ceil(len(items) / columns)
        self.ensure(rows * 18 + 6)
        col_w = CONTENT_W / columns
        for i, (key, value) in enumerate(items):
            row, col = divmod(i, columns)
            x = ML + col * col_w
            y = self.y + row * 18
            self.page.insert_text((x, y), key.upper(), fontsize=6.4, fontname="sgb", color=rgb(MUTED))
            self.page.insert_text((x + 92, y), value, fontsize=8.6, fontname="sg", color=rgb(INK))
        self.y += rows * 18 + 4

    def bullets(self, items: list[str], color: str = GREEN, gap: float = 3.2) -> None:
        for item in items:
            lines = wrap(item, 9.1, CONTENT_W - 16, "sg")
            height = len(lines) * 12.2 + gap
            self.ensure(height)
            self.page.draw_circle((ML + 3, self.y - 3), 1.8, color=None, fill=rgb(color))
            for line in lines:
                self.page.insert_text((ML + 13, self.y), line, fontsize=9.1, fontname="sg", color=rgb(INK))
                self.y += 12.2
            self.y += gap

    def note(self, title: str, text: str, tone: str = "green") -> None:
        palettes = {
            "green": (GREEN_SOFT, GREEN_DARK, GREEN),
            "coral": (RED_SOFT, CORAL_DARK, CORAL),
            "amber": (AMBER_SOFT, AMBER, "#B07C1A"),
            "violet": (VIOLET_SOFT, VIOLET, VIOLET),
            "turq": (TURQ_SOFT, TURQ, TURQ),
        }
        bg, fg, bar = palettes.get(tone, palettes["green"])
        lines = wrap(text, 8.8, CONTENT_W - 28, "sg")
        height = 24 + len(lines) * 12.2
        self.ensure(height + 8)
        box = fitz.Rect(ML, self.y - 10, MR, self.y - 10 + height)
        self.page.draw_rect(box, color=None, fill=rgb(bg), radius=0.12)
        self.page.draw_rect(fitz.Rect(box.x0, box.y0, box.x0 + 3, box.y1), color=None, fill=rgb(bar))
        self.page.insert_text((ML + 13, self.y + 3), title, fontsize=8.2, fontname="sgb", color=rgb(fg))
        yy = self.y + 17
        for line in lines:
            self.page.insert_text((ML + 13, yy), line, fontsize=8.8, fontname="sg", color=rgb(INK))
            yy += 12.2
        self.y = box.y1 + 12

    def table(self, headers: list[str], rows: list[list[str]], widths: list[float], align: list[str] | None = None, size: float = 8.3) -> None:
        align = align or ["left"] * len(headers)
        total = sum(widths)
        widths = [w / total * CONTENT_W for w in widths]
        header_h = 22
        row_h = 19
        self.ensure(header_h + len(rows) * row_h + 6)
        # Encabezado
        x = ML
        self.page.draw_rect(fitz.Rect(ML, self.y - 11, MR, self.y - 11 + header_h), color=None, fill=rgb(GREEN_DARK), radius=0.18)
        for i, head in enumerate(headers):
            if align[i] == "right":
                tx = x + widths[i] - 12 - text_width(head, size - 0.4, "sgb")
            elif align[i] == "center":
                tx = x + (widths[i] - text_width(head, size - 0.4, "sgb")) / 2
            else:
                tx = x + 6
            self.page.insert_text((tx, self.y + 3), head.upper(), fontsize=size - 0.4, fontname="sgb", color=rgb(WHITE))
            x += widths[i]
        self.y += header_h + 2
        for r, row in enumerate(rows):
            h = row_h
            self.ensure(h + 2)
            if r % 2 == 1:
                self.page.draw_rect(fitz.Rect(ML, self.y - 12, MR, self.y - 12 + h), color=None, fill=rgb(CREAM))
            x = ML
            for i, cell in enumerate(row):
                if align[i] == "right":
                    tx = x + widths[i] - 6 - text_width(cell, size, "sg")
                elif align[i] == "center":
                    tx = x + (widths[i] - text_width(cell, size, "sg")) / 2
                else:
                    tx = x + 6
                self.page.insert_text((tx, self.y + 2), cell, fontsize=size, fontname="sg", color=rgb(INK))
                x += widths[i]
            self.y += h
            self.page.draw_line((ML, self.y - 10), (MR, self.y - 10), color=rgb(LINE), width=0.4)
        self.y += 7

    def checklist(self, items: list[str], columns: int = 2) -> None:
        rows = math.ceil(len(items) / columns)
        self.ensure(rows * 20 + 8)
        col_w = CONTENT_W / columns
        for i, item in enumerate(items):
            row, col = divmod(i, columns)
            x = ML + col * col_w
            y = self.y + row * 20
            self.page.draw_rect(fitz.Rect(x, y - 8.5, x + 9, y + 0.5), color=rgb(GREEN), fill=None, width=0.8)
            self.page.insert_text((x + 16, y), item, fontsize=8.6, fontname="sg", color=rgb(INK))
        self.y += rows * 20 + 4

    def signature(self, name: str, role: str, extra: str = "Documento de ejemplo") -> None:
        self.ensure(64)
        self.y += 4
        self.page.draw_line((ML, self.y + 20), (ML + 210, self.y + 20), color=rgb(MUTED), width=0.7)
        self.page.insert_text((ML, self.y + 33), name, fontsize=9.2, fontname="sgb", color=rgb(INK))
        self.page.insert_text((ML, self.y + 44), role, fontsize=7.8, fontname="sg", color=rgb(MUTED))
        self.page.insert_text((ML, self.y + 54), extra, fontsize=6.8, fontname="sgi", color=rgb(MUTED))
        self.y += 60

    def finish(self) -> None:
        total = len(self.doc)
        for i, page in enumerate(self.doc):
            draw_footer(page, i + 1)
        self.doc.set_toc([[1, self.toc_title, 1]])
        try:
            self.doc.subset_fonts()
        except Exception:
            pass
        path = OUT / self.filename
        self.doc.save(str(path), garbage=4, deflate=True)
        self.doc.close()
        size_kb = path.stat().st_size / 1024
        DOCUMENTS.append((path.name, size_kb))


def base_meta(doc_id: str, date: str, professional: str, center: str) -> dict:
    return {
        "doc_id": doc_id,
        "patient": "Roberto Carlos Cartes Jiménez",
        "blood": "O+",
        "date": date,
        "professional": professional,
        "center": center,
    }


def title_block(doc: Doc, kind: str, title: str, subtitle: str, meta: dict, tone: str = CORAL) -> None:
    doc.eyebrow(kind, tone)
    doc.page.insert_text((ML, doc.y + 11), title, fontsize=20, fontname="sgb", color=rgb(GREEN_DARK))
    doc.y += 28
    for line in wrap(subtitle, 9.7, CONTENT_W, "sg"):
        doc.page.insert_text((ML, doc.y), line, fontsize=9.7, fontname="sg", color=rgb(MUTED))
        doc.y += 13
    doc.y += 6
    meta_line = f"Fecha: {fmt_date(meta['date'])}   ·   {meta['professional']}   ·   {meta['center']}"
    doc.small(meta_line, color=GREEN_DARK, size=8.2, gap=7)


def build_report(spec: dict) -> None:
    meta = base_meta(spec["doc_id"], spec["date"], spec["professional"], spec["center"])
    doc = Doc(spec["filename"], spec["doc_title"], meta, spec["title"])
    title_block(doc, spec.get("kind", "Informe clínico"), spec["title"], spec["subtitle"], meta, spec.get("accent", CORAL))

    if spec.get("reason"):
        doc.heading("Motivo de consulta")
        doc.paragraph(spec["reason"])

    if spec.get("background"):
        doc.heading("Antecedentes relevantes")
        doc.bullets(spec["background"], color=spec.get("accent", GREEN))

    if spec.get("findings"):
        doc.heading("Hallazgos")
        doc.bullets(spec["findings"], color=spec.get("accent", GREEN))

    if spec.get("diagnosis"):
        doc.heading("Diagnóstico e impresión clínica")
        doc.note("Diagnóstico de ejemplo", spec["diagnosis"], spec.get("tone", "green"))
        if spec.get("cie10"):
            doc.kv([("Código CIE-10", spec["cie10"]), ("Especialidad", spec.get("specialty", "Medicina general"))])

    if spec.get("plan"):
        doc.heading("Plan y recomendaciones")
        doc.bullets(spec["plan"], color=GREEN)

    if spec.get("alerts"):
        doc.note("Signos de alarma", spec["alerts"], "coral")

    doc.signature(spec["professional"], spec.get("role", "Profesional tratante"))
    doc.finish()


def build_lab(spec: dict) -> None:
    meta = base_meta(spec["doc_id"], spec["date"], spec["professional"], spec["center"])
    doc = Doc(spec["filename"], spec["doc_title"], meta, spec["title"])
    title_block(doc, "Laboratorio clínico", spec["title"], spec["subtitle"], meta, TURQ)
    doc.heading("Resultados")
    doc.table(spec["headers"], spec["rows"], spec["widths"], spec.get("align"), size=8.1)
    doc.heading("Lectura clínica")
    doc.bullets(spec["reading"], color=TURQ)
    doc.note("Importante", "Un resultado aislado no define un diagnóstico. Interpretar junto con la historia clínica y repetir según indicación médica.", "turq")
    doc.signature(spec["professional"], spec.get("role", "Médico solicitante"))
    doc.finish()


def build_imaging(spec: dict) -> None:
    meta = base_meta(spec["doc_id"], spec["date"], spec["professional"], spec["center"])
    doc = Doc(spec["filename"], spec["doc_title"], meta, spec["title"])
    title_block(doc, spec.get("kind", "Informe de imagen"), spec["title"], spec["subtitle"], meta, CORAL)
    doc.heading("Estudio realizado")
    doc.kv(spec["study"], columns=2)
    doc.heading("Hallazgos")
    doc.bullets(spec["findings"], color=CORAL)
    doc.heading("Impresión diagnóstica")
    doc.note("Conclusión del estudio", spec["impression"], "coral")
    if spec.get("plan"):
        doc.heading("Recomendaciones")
        doc.bullets(spec["plan"], color=GREEN)
    doc.signature(spec["professional"], spec.get("role", "Médico radiólogo"), "Informe de demostración")
    doc.finish()


def build_plan(spec: dict) -> None:
    meta = base_meta(spec["doc_id"], spec["date"], spec["professional"], spec["center"])
    doc = Doc(spec["filename"], spec["doc_title"], meta, spec["title"])
    title_block(doc, "Plan de tratamiento", spec["title"], spec["subtitle"], meta, GREEN)
    doc.heading("Objetivos")
    doc.bullets(spec["objectives"], color=GREEN)
    if spec.get("table"):
        doc.heading(spec["table_title"])
        doc.table(spec["table"]["headers"], spec["table"]["rows"], spec["table"]["widths"], spec["table"].get("align"), size=8.2)
    doc.heading("Indicaciones")
    doc.bullets(spec["indications"], color=TURQ)
    if spec.get("progress"):
        doc.heading("Criterios de progresión")
        doc.paragraph(spec["progress"])
    doc.note("Precaución", spec["precaution"], "amber")
    doc.signature(spec["professional"], spec.get("role", "Kinesiólogo/a tratante"))
    doc.finish()


def draw_ecg(doc: Doc) -> None:
    doc.heading("Trazado electrocardiográfico")
    doc.ensure(190)
    x0, y0, w, h = ML, doc.y, CONTENT_W, 150
    rect = fitz.Rect(x0, y0, x0 + w, y0 + h)
    doc.page.draw_rect(rect, color=rgb(LINE), fill=rgb("#FFFCF8"), width=0.7, radius=0.18)
    # Cuadrícula
    for gx in range(int(x0), int(x0 + w), 8):
        major = ((gx - x0) // 8) % 5 == 0
        doc.page.draw_line((gx, y0), (gx, y0 + h), color=rgb("#F4DDD7" if major else "#FAEBE7"), width=0.45 if major else 0.25)
    for gy in range(int(y0), int(y0 + h), 8):
        major = ((gy - y0) // 8) % 5 == 0
        doc.page.draw_line((x0, gy), (x0 + w, gy), color=rgb("#F4DDD7" if major else "#FAEBE7"), width=0.45 if major else 0.25)
    # Calibración
    base = y0 + h * 0.62
    doc.page.draw_polyline(
        [(x0 + 10, base), (x0 + 10, base - 30), (x0 + 18, base - 30), (x0 + 18, base), (x0 + 26, base)],
        color=rgb(CORAL),
        width=1,
    )
    # Latido sintético PQRST
    beat = [
        (0, 0), (4, 0), (7, -1), (9, -3), (11, -5), (13, -3), (15, 0), (17, 0),
        (19, 1), (20, 4), (21, 0), (22, -2), (23, -26), (24, -34), (25, -26), (26, -2),
        (27, 4), (29, 1), (31, 0), (35, 0), (37, -2), (39, -6), (41, -10), (43, -8),
        (45, -3), (47, 0), (52, 0),
    ]
    start = x0 + 35
    points = []
    x = start
    while x < x0 + w - 10:
        for dx, dy in beat:
            if x + dx < x0 + w - 8:
                points.append((x + dx, base + dy))
        x += 54
    doc.page.draw_polyline(points, color=rgb(CORAL_DARK), width=1.15)
    doc.page.insert_text((x0 + 12, y0 + 16), "II · 25 mm/s · 10 mm/mV", fontsize=7.3, fontname="sgb", color=rgb(MUTED))
    doc.y = y0 + h + 14


def draw_eeg(doc: Doc) -> None:
    doc.heading("Trazado electroencefalográfico")
    doc.ensure(230)
    x0, y0, w, h = ML, doc.y, CONTENT_W, 200
    doc.page.draw_rect(fitz.Rect(x0, y0, x0 + w, y0 + h), color=rgb(LINE), fill=rgb("#FCFDFC"), width=0.7, radius=0.18)
    labels = ["Fp1-F3", "F3-C3", "C3-P3", "P3-O1", "Fp2-F4", "F4-C4", "C4-P4", "P4-O2"]
    rng = random.Random(20250402)
    row_h = (h - 18) / len(labels)
    for i, label in enumerate(labels):
        baseline = y0 + 16 + i * row_h + row_h / 2
        doc.page.insert_text((x0 + 8, baseline + 3), label, fontsize=6.2, fontname="sgb", color=rgb(MUTED))
        pts = []
        amp = 5.5 if i < 4 else 5.0
        freq = 9.6 if i % 2 == 0 else 10.4
        phase = i * 0.7
        for step in range(0, int(w - 56), 2):
            xx = x0 + 48 + step
            yy = baseline + amp * math.sin((step / 12.5) * freq * 0.55 + phase) + rng.uniform(-0.8, 0.8)
            pts.append((xx, yy))
        doc.page.draw_polyline(pts, color=rgb("#3D6B62" if i < 4 else "#5D6B64"), width=0.55)
        doc.page.draw_line((x0 + 48, baseline + row_h / 2 - 1), (x0 + w - 8, baseline + row_h / 2 - 1), color=rgb("#EDF2EF"), width=0.3)
    doc.page.insert_text((x0 + 12, y0 + 10), "Montaje bipolar · 30 mm/s · filtro 70 Hz", fontsize=7, fontname="sgb", color=rgb(MUTED))
    doc.y = y0 + h + 14


def build_ecg_report() -> None:
    meta = base_meta("DEMO-CARD-2025-0122-ECG", "2025-01-22", "Dra. Valentina Rojas", "Hospital de Referencia (ejemplo)")
    doc = Doc("cardiologia-2025-01-22-ecg.pdf", "Electrocardiograma de reposo", meta, "Electrocardiograma — enero 2025")
    title_block(doc, "Cardiología · estudio", "Electrocardiograma de reposo", "Registro de 12 derivaciones realizado en control cardiovascular preventivo.", meta, CORAL)
    doc.heading("Datos del estudio")
    doc.kv([
        ("Fecha", fmt_date("2025-01-22")),
        ("Frecuencia", "68 lpm"),
        ("Ritmo", "Sinusal"),
        ("Eje", "Normal"),
        ("PR", "160 ms"),
        ("QRS", "92 ms"),
        ("QTc", "410 ms"),
        ("Conclusión", "Sin alteraciones agudas"),
    ], columns=2)
    draw_ecg(doc)
    doc.heading("Interpretación")
    doc.bullets([
        "Ritmo sinusal regular, frecuencia de 68 latidos por minuto.",
        "Intervalos PR, QRS y QTc dentro de rangos normales.",
        "Sin elevación o depresión significativa del segmento ST.",
        "Sin ondas Q patológicas ni alteraciones de la repolarización.",
    ], color=CORAL)
    doc.note("Impresión", "Electrocardiograma normal. Sin signos de isquemia aguda ni arritmia. Se recomienda control clínico habitual y perfil lipídico.", "green")
    doc.signature("Dra. Valentina Rojas", "Cardiología · documento de ejemplo")
    doc.finish()


def build_eeg_report() -> None:
    meta = base_meta("DEMO-NEURO-2025-0402-EEG", "2025-04-02", "Dr. Ignacio Pérez", "Hospital de Referencia (ejemplo)")
    doc = Doc("neurologia-2025-04-02-eeg.pdf", "Electroencefalograma", meta, "Electroencefalograma — abril 2025")
    title_block(doc, "Neurología · estudio", "Electroencefalograma", "Registro en vigilia con maniobras de activación, solicitado por cefalea tensional.", meta, VIOLET)
    doc.heading("Datos del estudio")
    doc.kv([
        ("Fecha", fmt_date("2025-04-02")),
        ("Duración", "20 minutos"),
        ("Estado", "Vigilia"),
        ("Activación", "Hiperventilación y fotoestimulación"),
        ("Técnica", "Montaje bipolar"),
        ("Tolerancia", "Buena"),
    ], columns=2)
    draw_eeg(doc)
    doc.heading("Hallazgos")
    doc.bullets([
        "Actividad de fondo alfa de 9-10 Hz, simétrica y reactiva.",
        "Sin actividad epileptiforme focal ni generalizada.",
        "Hiperventilación y fotoestimulación sin cambios significativos.",
        "Sin asimetrías ni enlentecimiento focal.",
    ], color=VIOLET)
    doc.note("Impresión", "Electroencefalograma normal en vigilia. Sin hallazgos epileptiformes. Correlacionar con clínica; no requiere tratamiento anticomicial por este estudio.", "green")
    doc.signature("Dr. Ignacio Pérez", "Neurología · documento de ejemplo")
    doc.finish()


def build_prescription() -> None:
    meta = base_meta("DEMO-RX-2026-1020-01", "2026-10-20", "Dra. Valentina Rojas", "Hospital de Referencia (ejemplo)")
    doc = Doc("medicamentos-2026-10-20-receta-vigente.pdf", "Receta médica vigente", meta, "Receta vigente — octubre 2026")
    title_block(doc, "Medicina general · receta", "Receta médica vigente", "Tratamiento ambulatorio actual. Revisión de indicaciones y dosis máximas.", meta, GREEN)
    doc.heading("Medicamentos indicados")
    doc.table(
        ["Medicamento", "Dosis", "Frecuencia", "Duración"],
        [
            ["Paracetamol", "500 mg", "Cada 8 h si hay dolor", "Según necesidad"],
            ["Ibuprofeno", "400 mg", "Cada 8 h con alimentos", "Máx. 3 días seguidos"],
            ["Vitamina D", "1000 UI", "Una vez al día", "Continuar"],
        ],
        [2.4, 1.1, 2.4, 2.0],
        size=8.2,
    )
    doc.heading("Indicaciones")
    doc.bullets([
        "Paracetamol: máximo 3 g al día. No combinar con otros productos que lo contengan.",
        "Ibuprofeno: tomar con alimentos; evitar si hay dolor gástrico o sangrado.",
        "Vitamina D: con el desayuno; reevaluar niveles en el próximo control de laboratorio.",
        "Mantener los medicamentos fuera del alcance de niños y revisar vencimientos.",
    ])
    doc.note("Alergia registrada", "Penicilina: urticaria y picazón. Moderada. Informar antes de cualquier antibiótico. Evitar penicilina y derivados.", "coral")
    doc.note("Tratamiento de ejemplo", "Esta receta no reemplaza una receta válida. Fue generada para demostrar el formato del sitio y no debe presentarse en una farmacia.", "amber")
    doc.signature("Dra. Valentina Rojas", "Medicina general · documento de ejemplo")
    doc.finish()


def build_emergency_summary() -> None:
    meta = base_meta("DEMO-EMERG-2026-1028", "2026-10-28", "Dra. Valentina Rojas", "Hospital de Referencia (ejemplo)")
    doc = Doc("emergencia-ficha-resumen.pdf", "Ficha de emergencia", meta, "Ficha de emergencia — resumen")
    title_block(doc, "Resumen para urgencias", "Ficha de emergencia", "Información crítica para entregar al personal de salud. Mantener junto a la identificación.", meta, CORAL)

    doc.heading("Identificación")
    doc.kv([
        ("Nombre", "Roberto Carlos Cartes Jiménez"),
        ("Grupo sanguíneo", "O+"),
        ("Alergia principal", "Penicilina (moderada)"),
        ("Médica de cabecera", "Dra. Valentina Rojas"),
    ], columns=2)

    doc.heading("Alergias")
    doc.table(
        ["Sustancia", "Severidad", "Reacción"],
        [["Penicilina", "Moderada", "Urticaria y picazón"], ["Polen", "Leve", "Rinorrea y estornudos"]],
        [2.2, 1.2, 3.4],
        size=8.2,
    )

    doc.heading("Condiciones que deben conocerse")
    doc.bullets([
        "Lumbalgia mecánica en seguimiento, sin compromiso radicular.",
        "Síndrome de túnel carpiano derecho, manejo conservador.",
        "Dolor de hombro derecho por tendinopatía del supraespinosa.",
        "Hipercolesterolemia leve y vitamina D baja en control.",
    ], color=CORAL)

    doc.heading("Medicamentos habituales")
    doc.bullets([
        "Paracetamol 500 mg, según necesidad (máximo 3 g al día).",
        "Ibuprofeno 400 mg, según necesidad, con alimentos.",
        "Vitamina D 1000 UI, una vez al día.",
    ], color=GREEN)

    doc.heading("Contactos")
    doc.table(
        ["Contacto", "Relación", "Teléfono"],
        [
            ["Contacto familiar principal", "Familiar directo", "+56 9 0000 0001"],
            ["Dra. Valentina Rojas", "Médica de cabecera", "+56 9 0000 0002"],
            ["Hospital de Referencia (ejemplo)", "Centro asistencial", "+56 2 0000 0000"],
            ["SAMU", "Ambulancia", "131"],
            ["Carabineros", "Emergencias", "133"],
            ["Bomberos", "Incendios y rescate", "132"],
        ],
        [2.6, 1.8, 2.0],
        ["left", "left", "right"],
        size=8.2,
    )

    # Segunda página: instrucciones, notas y espacio para observaciones.
    doc.page_break()
    doc.note("En una emergencia real", "Llama al 131 (SAMU) si hay riesgo vital. Esta ficha es un documento de demostración y no reemplaza la evaluación de un profesional.", "coral")

    doc.heading("Cómo usar esta ficha")
    doc.bullets([
        "Muestra esta ficha al ingresar a urgencias o al llamar al SAMU.",
        "Confirma nombre, grupo sanguíneo y alergias con la persona o su acompañante.",
        "No administres medicamentos sin indicación del equipo tratante.",
        "Actualiza los contactos y el tratamiento cuando cambien.",
    ], color=CORAL)

    doc.heading("Notas para el equipo de salud")
    doc.bullets([
        "Confirmar identidad y alergias antes de administrar medicamentos.",
        "No se registran alergias graves conocidas; la alergia a penicilina es moderada.",
        "Portar la ficha impresa en cada control y actualizarla si cambia el tratamiento.",
    ], color=TURQ)

    doc.heading("Observaciones")
    doc.small("Espacio para notas del equipo tratante.", color=MUTED, size=7.6, gap=4)
    doc.ruled_notes(6)

    doc.heading("Verificación rápida")
    doc.checklist([
        "Identidad confirmada",
        "Alergias verificadas",
        "Contacto familiar avisado",
        "Ficha actualizada",
    ])

    doc.note("Documento de ejemplo", "Todos los datos de esta ficha son ficticios y tienen fines de diseño. No usar para decisiones clínicas.", "amber")
    doc.signature("Dra. Valentina Rojas", "Responsable de la información de ejemplo")
    doc.finish()


def main() -> None:
    # 1. Informes y estudios
    build_report({
        "filename": "traumatologia-inferior-2024-08-14-informe-medico.pdf",
        "doc_id": "DEMO-TI-2024-0814-01",
        "doc_title": "Informe médico inicial — dolor lumbar",
        "title": "Dolor lumbar mecánico",
        "subtitle": "Evaluación inicial, diagnóstico y plan de manejo conservador.",
        "date": "2024-08-14",
        "professional": "Dr. Andrés Molina",
        "center": "Hospital de Referencia (ejemplo)",
        "specialty": "Traumatología",
        "kind": "Informe médico",
        "tone": "amber",
        "accent": AMBER,
        "reason": "Dolor lumbar bajo de tres semanas de evolución, intermitente, relacionado con cargas prolongadas y sedestación. Sin dolor irradiado a la pierna ni pérdida de fuerza.",
        "background": [
            "Sin cirugías previas de columna. Sin traumatismo reciente.",
            "Sin fiebre, pérdida de peso ni síntomas sistémicos.",
            "Actividad física irregular en los últimos meses.",
        ],
        "findings": [
            "Dolor a la palpación de musculatura paravertebral lumbar baja, sin contractura intensa.",
            "Movilidad lumbar: flexión 60°, extensión 20°, inclinaciones simétricas.",
            "Fuerza 5/5 en ambos miembros inferiores; reflejos rotulianos y aquíleos conservados.",
            "Lasègue negativo bilateral. Sensibilidad conservada. Sin signos de alarma.",
        ],
        "diagnosis": "Lumbalgia mecánica sin signos de compromiso radicular. Cuadro de origen postural, sin evidencia clínica de hernia aguda ni infección.",
        "cie10": "M54.5",
        "plan": [
            "Kinesiología: educación, movilidad y fortalecimiento progresivo.",
            "Paracetamol 500 mg cada 8 horas si hay dolor; máximo 3 g al día.",
            "Ibuprofeno 400 mg cada 8 horas con alimentos, solo si el dolor lo requiere.",
            "Evitar reposo prolongado; caminar y mantener actividad tolerada.",
            "Control en 4 semanas o antes si aparece dolor irradiado o déficit de fuerza.",
        ],
        "alerts": "Consultar de inmediato si aparece pérdida de fuerza, anestesia en silla de montar, alteración para orinar o defecar, fiebre o dolor nocturno progresivo.",
        "role": "Traumatología · documento de ejemplo",
    })

    build_report({
        "filename": "traumatologia-inferior-2024-08-14-informe-lumbar.pdf",
        "doc_id": "DEMO-TI-2024-0814-02",
        "doc_title": "Informe traumatológico — columna lumbar",
        "title": "Evaluación traumatológica lumbar",
        "subtitle": "Examen físico dirigido y plan conservador inicial.",
        "date": "2024-08-14",
        "professional": "Dr. Andrés Molina",
        "center": "Hospital de Referencia (ejemplo)",
        "specialty": "Traumatología",
        "kind": "Informe traumatológico",
        "tone": "green",
        "accent": GREEN,
        "reason": "Evaluación por dolor lumbar bajo de características mecánicas, sin irradiación distal.",
        "findings": [
            "Inspección: alineación conservada, sin deformidad evidente.",
            "Palpación: dolor selectivo en región lumbar baja, sin masas ni puntos de fractura.",
            "Rangos: flexión 60°, extensión 20°, rotaciones simétricas y algo limitadas.",
            "Pruebas radiculares: Lasègue y Bragard negativos; fuerza y sensibilidad conservadas.",
            "Marcha normal, sin claudicación.",
        ],
        "diagnosis": "Lumbalgia mecánica. Sin criterios clínicos de derivación urgente. Se indica manejo conservador y control evolutivo.",
        "cie10": "M54.5",
        "plan": [
            "Analgesia condicionada y educación sobre el dolor lumbar.",
            "Derivación a kinesiología para programa de ejercicio progresivo.",
            "Radiografía lumbar solo si persiste o aparecen signos de alarma.",
            "Control en 4 semanas; reevaluar necesidad de imagen.",
        ],
        "alerts": "Déficit neurológico progresivo, retención urinaria, fiebre, traumatismo de alta energía o dolor que no cede en reposo.",
        "role": "Traumatología · documento de ejemplo",
    })

    build_report({
        "filename": "traumatologia-superior-2025-05-06-informe-carpiano.pdf",
        "doc_id": "DEMO-TS-2025-0506-01",
        "doc_title": "Informe de evaluación — túnel carpiano",
        "title": "Síndrome de túnel carpiano derecho",
        "subtitle": "Evaluación clínica inicial y plan de manejo conservador.",
        "date": "2025-05-06",
        "professional": "Dra. Camila Fuentes",
        "center": "Hospital de Referencia (ejemplo)",
        "specialty": "Traumatología",
        "kind": "Informe médico",
        "tone": "coral",
        "accent": CORAL,
        "reason": "Parestesias nocturnas en pulgar, índice y dedo medio de la mano derecha, de aproximadamente tres meses de evolución. Se exacerban con el uso prolongado del computador.",
        "background": [
            "Sin traumatismo previo de muñeca ni cirugía de mano.",
            "Sin diabetes ni enfermedades inflamatorias conocidas.",
            "Trabajo con uso intensivo de teclado y mouse.",
        ],
        "findings": [
            "Tinel positivo en el túnel carpiano derecho; Phalen positivo a los 45 segundos.",
            "Sensibilidad conservada en territorio del mediano; sin atrofia de la eminencia tenar.",
            "Fuerza de pinza y prensión conservadas y simétricas.",
            "Movilidad de muñeca completa; sin signos de tenosinovitis aguda.",
        ],
        "diagnosis": "Síndrome de túnel carpiano derecho leve a moderado, de probable origen por sobrecarga. Sin déficit motor ni atrofia.",
        "cie10": "G56.0",
        "plan": [
            "Órtesis nocturna en muñeca derecha por 6 semanas.",
            "Pausas activas de 2 minutos cada 45 minutos frente al computador.",
            "Estudio de conducción nerviosa para confirmar severidad.",
            "Ibuprofeno 400 mg con alimentos solo si hay dolor inflamatorio.",
            "Control en 6 semanas con resultado del estudio.",
        ],
        "alerts": "Pérdida de fuerza en pinza, atrofia de la base del pulgar, dolor persistente en reposo o empeoramiento progresivo de los síntomas.",
        "role": "Traumatología · documento de ejemplo",
    })

    build_report({
        "filename": "neurologia-2025-03-11-informe-neurologico.pdf",
        "doc_id": "DEMO-NEURO-2025-0311-01",
        "doc_title": "Informe neurológico — marzo 2025",
        "title": "Cefalea tensional episódica",
        "subtitle": "Evaluación clínica inicial y plan de seguimiento.",
        "date": "2025-03-11",
        "professional": "Dr. Ignacio Pérez",
        "center": "Hospital de Referencia (ejemplo)",
        "specialty": "Neurología",
        "kind": "Informe neurológico",
        "tone": "violet",
        "accent": VIOLET,
        "reason": "Cefalea episódica de seis meses de evolución, holocraneana, opresiva, de intensidad leve a moderada, sin náuseas ni fotofobia marcada. Relacionada con semanas de mayor carga laboral.",
        "background": [
            "Sin migraña previa diagnosticada ni antecedentes familiares de epilepsia.",
            "Sueño irregular en períodos de mayor demanda.",
            "Sin uso excesivo de analgésicos.",
        ],
        "findings": [
            "Examen neurológico completo normal: pares craneales, fuerza, sensibilidad y reflejos.",
            "Sin rigidez de nuca ni signos meníngeos.",
            "Fondo de ojo sin edema papilar.",
            "Escala de impacto de cefalea leve; sin criterios de cefalea secundaria.",
        ],
        "diagnosis": "Cefalea tensional episódica, sin signos de alarma. Se solicita electroencefalograma para completar estudio y se refuerzan medidas de sueño e higiene.",
        "cie10": "G44.2",
        "plan": [
            "Pauta de sueño regular de 7 a 8 horas e hidratación adecuada.",
            "Pausas activas y ejercicios de cuello durante la jornada.",
            "Ejercicio aeróbico regular; evitar ayunos prolongados.",
            "Electroencefalograma y control en 6 semanas.",
            "Analgésicos solo de forma ocasional; evitar uso frecuente.",
        ],
        "alerts": "Cefalea súbita de máxima intensidad, fiebre con rigidez de nuca, déficit neurológico focal, alteración de conciencia o cefalea que despierta por la noche.",
        "role": "Neurología · documento de ejemplo",
    })

    build_report({
        "filename": "psiquiatria-2025-02-18-informe-seguimiento.pdf",
        "doc_id": "DEMO-PSIQ-2025-0218-01",
        "doc_title": "Informe de seguimiento — salud mental",
        "title": "Seguimiento de salud mental",
        "subtitle": "Evaluación inicial, confidencial, con foco en sueño y ansiedad.",
        "date": "2025-02-18",
        "professional": "Dra. Paula Contreras",
        "center": "Centro de Salud Mental (ejemplo)",
        "specialty": "Psiquiatría",
        "kind": "Informe confidencial",
        "tone": "violet",
        "accent": VIOLET,
        "reason": "Consulta por ansiedad leve intermitente y dificultad para conciliar el sueño en períodos de mayor exigencia. Sin crisis de angustia ni ideación de daño.",
        "background": [
            "Sin hospitalizaciones psiquiátricas previas.",
            "Sin tratamiento psicofarmacológico actual.",
            "Buena red de apoyo familiar y adherencia a controles.",
        ],
        "findings": [
            "Ánimo eutímico; ansiedad leve con preocupación anticipatoria.",
            "Sueño de latencia prolongada, sin despertares frecuentes.",
            "Sin ideación suicida ni síntomas psicóticos.",
            "Funcionalidad laboral y social conservada.",
        ],
        "diagnosis": "Trastorno de ansiedad no especificado, de intensidad leve, con impacto en el sueño. Sin criterios de gravedad ni necesidad de psicofármacos al momento.",
        "cie10": "F41.9",
        "plan": [
            "Psicoeducación e higiene del sueño.",
            "Terapia psicológica con enfoque en manejo de ansiedad.",
            "Actividad física regular y reducción de cafeína por la tarde.",
            "Control cada 3 meses; consulta antes si aparece descompensación.",
            "Derivación a urgencias si hay ideación de daño o crisis intensa.",
        ],
        "alerts": "Ideación suicida, crisis de angustia incapacitante, insomnio severo persistente o consumo de sustancias. Acudir a urgencias si hay riesgo para sí mismo o terceros.",
        "role": "Psiquiatría · documento confidencial de ejemplo",
    })

    build_report({
        "filename": "fonoaudiologia-2025-09-04-evaluacion-habla.pdf",
        "doc_id": "DEMO-FONO-2025-0904-01",
        "doc_title": "Evaluación de habla, voz y deglución",
        "title": "Evaluación fonoaudiológica",
        "subtitle": "Habla, voz y deglución en contexto de fatiga vocal.",
        "date": "2025-09-04",
        "professional": "Flga. Constanza Vidal",
        "center": "Centro de Especialidades (ejemplo)",
        "specialty": "Fonoaudiología",
        "kind": "Informe fonoaudiológico",
        "tone": "turq",
        "accent": TURQ,
        "reason": "Evaluación solicitada por fatiga vocal en días de mayor uso de la voz. Sin ronquera persistente ni dificultad para tragar.",
        "findings": [
            "Habla inteligible, fluida y bien articulada; sin omisiones ni distorsiones significativas.",
            "Voz con timbre adecuado; sin disfonía persistente al momento de la evaluación.",
            "Deglución segura con líquidos y sólidos; sin signos de aspiración.",
            "Fatiga vocal leve posterior a 20 minutos de conversación continua.",
        ],
        "diagnosis": "Sin hallazgos de riesgo en habla ni deglución. Fatiga vocal leve, probablemente asociada a demanda laboral y hábitos de uso de la voz.",
        "cie10": "R49.9",
        "plan": [
            "Hidratación frecuente durante el día; evitar carraspeo fuerte.",
            "Pausas vocales de 10 minutos por cada hora de conversación intensa.",
            "Técnica de proyección diafragmática y calentamiento vocal breve.",
            "Control en 3 meses o antes si aparece ronquera persistente.",
        ],
        "alerts": "Ronquera por más de tres semanas, pérdida de voz, dolor al tragar, ahogo con alimentos o cambios persistentes en la deglución.",
        "role": "Fonoaudiología · documento de ejemplo",
    })

    # 2. Imágenes
    build_imaging({
        "filename": "traumatologia-superior-2024-11-19-eco-hombro.pdf",
        "doc_id": "DEMO-TS-2024-1119-ECO",
        "doc_title": "Ecografía de hombro derecho",
        "title": "Ecografía musculoesquelética de hombro derecho",
        "subtitle": "Estudio dirigido a dolor lateral del hombro.",
        "date": "2024-11-19",
        "professional": "Dra. Camila Fuentes",
        "center": "Centro de Imágenes (ejemplo)",
        "kind": "Informe de imagen",
        "tone": "coral",
        "study": [
            ("Estudio", "Ecografía de partes blandas"),
            ("Región", "Hombro derecho"),
            ("Equipo", "Transductor lineal 12 MHz"),
            ("Técnica", "Planos longitudinal y transversal"),
        ],
        "findings": [
            "Tendón supraespinosa: engrosamiento leve difuso, con cambios de ecogenicidad. No se observa ruptura transfixiante.",
            "Tendones infraespinosa y subescapular: sin alteraciones significativas.",
            "Tendón de la porción larga del bíceps: normal, sin líquido en la vaina.",
            "Bursa subacromial-subdeltoidea: sin derrame significativo.",
            "Articulación acromioclavicular: sin hipertrofia ni osteofitos relevantes.",
        ],
        "impression": "Tendinopatía leve del supraespinosa derecho, sin ruptura ni calcificación. Hallazgos compatibles con sobrecarga.",
        "plan": [
            "Manejo conservador con kinesiología y control de carga.",
            "Analgesia condicionada; evitar dormir sobre el hombro derecho por períodos largos.",
            "Control clínico en 8 semanas; repetir imagen solo si hay empeoramiento.",
        ],
        "role": "Imagenología · documento de ejemplo",
    })

    build_imaging({
        "filename": "traumatologia-inferior-2025-08-21-resonancia-lumbar.pdf",
        "doc_id": "DEMO-TI-2025-0821-RM",
        "doc_title": "Resonancia magnética lumbar",
        "title": "Resonancia magnética de columna lumbar",
        "subtitle": "Estudio sin contraste por lumbalgia persistente.",
        "date": "2025-08-21",
        "professional": "Dr. Andrés Molina",
        "center": "Centro de Imágenes (ejemplo)",
        "kind": "Informe de imagen",
        "tone": "amber",
        "study": [
            ("Estudio", "RM de columna lumbar"),
            ("Contraste", "Sin contraste"),
            ("Secuencias", "T1, T2 y STIR"),
            ("Indicación", "Lumbalgia persistente"),
        ],
        "findings": [
            "Alineación lumbar conservada; sin listesis significativa.",
            "Discos L1-L2 a L3-L4 con altura y señal conservadas.",
            "L4-L5: protrusión discal leve difusa, sin estenosis de canal ni compromiso foraminal.",
            "L5-S1: cambios degenerativos leves, sin hernia ni compresión radicular.",
            "Cono medular y raíces de la cola de caballo sin alteraciones.",
            "Musculatura paravertebral sin signos de denervación aguda.",
        ],
        "impression": "Cambios degenerativos leves L4-L5 y L5-S1, sin compromiso radicular ni estenosis significativa. No explica déficit neurológico.",
        "plan": [
            "Manejo conservador con ejercicio progresivo y educación.",
            "Correlacionar con examen físico; no se requiere cirugía por este estudio.",
            "Control clínico anual o antes si aparecen signos de alarma.",
        ],
        "role": "Imagenología · documento de ejemplo",
    })

    build_imaging({
        "filename": "cardiologia-2025-03-05-ecocardiograma.pdf",
        "doc_id": "DEMO-CARD-2025-0305-ECO",
        "doc_title": "Ecocardiograma transtorácico",
        "title": "Ecocardiograma transtorácico",
        "subtitle": "Evaluación de estructura y función cardíaca en control preventivo.",
        "date": "2025-03-05",
        "professional": "Dra. Valentina Rojas",
        "center": "Centro de Imágenes (ejemplo)",
        "kind": "Informe de imagen",
        "tone": "green",
        "study": [
            ("Estudio", "Ecocardiograma transtorácico"),
            ("Modalidad", "Bidimensional y Doppler"),
            ("Indicación", "Control cardiovascular preventivo"),
            ("Tolerancia", "Buena"),
        ],
        "findings": [
            "Ventrículo izquierdo de tamaño normal, con fracción de eyección estimada en 60 %.",
            "Motilidad parietal conservada, sin alteraciones segmentarias.",
            "Aurículas y ventrículo derecho de dimensiones normales.",
            "Válvulas mitral, aórtica, tricúspide y pulmonar sin estenosis ni insuficiencia significativa.",
            "Sin derrame pericárdico ni trombos intracavitarios.",
            "Vena cava inferior de calibre y colapsabilidad normales.",
        ],
        "impression": "Ecocardiograma transtorácico normal. Función sistólica conservada y sin valvulopatías significativas.",
        "plan": [
            "Control clínico anual y refuerzo de hábitos cardiovasculares.",
            "Repetir estudio si aparece un cambio clínico o un nuevo soplo.",
        ],
        "role": "Cardiología · documento de ejemplo",
    })

    # 3. Laboratorio
    build_lab({
        "filename": "laboratorio-2026-01-15-perfil-lipidico.pdf",
        "doc_id": "DEMO-LAB-2026-0115-LIP",
        "doc_title": "Perfil lipídico — enero 2026",
        "title": "Perfil lipídico",
        "subtitle": "Muestra de sangre en ayunas para evaluación cardiovascular preventiva.",
        "date": "2026-01-15",
        "professional": "Dra. Valentina Rojas",
        "center": "Laboratorio Clínico (ejemplo)",
        "headers": ["Examen", "Resultado", "Unidad", "Referencia", "Estado"],
        "rows": [
            ["Colesterol total", "205", "mg/dL", "< 200", "Alto"],
            ["LDL colesterol", "128", "mg/dL", "< 100", "Alto"],
            ["HDL colesterol", "52", "mg/dL", "> 40", "Normal"],
            ["Triglicéridos", "145", "mg/dL", "< 150", "Normal"],
            ["Colesterol no HDL", "153", "mg/dL", "< 130", "Alto"],
        ],
        "widths": [2.0, 1.1, 0.9, 1.2, 1.1],
        "align": ["left", "right", "left", "left", "center"],
        "reading": [
            "LDL y colesterol total levemente elevados, en un contexto de riesgo cardiovascular bajo.",
            "HDL y triglicéridos dentro de rangos de referencia.",
            "No requiere tratamiento farmacológico de inicio; se prioriza alimentación y actividad física.",
            "Repetir perfil lipídico en seis meses o según control médico.",
        ],
        "role": "Medicina general · documento de ejemplo",
    })

    build_lab({
        "filename": "laboratorio-2026-01-15-hemograma.pdf",
        "doc_id": "DEMO-LAB-2026-0115-HEM",
        "doc_title": "Hemograma completo — enero 2026",
        "title": "Hemograma completo",
        "subtitle": "Serie roja, serie blanca y plaquetas.",
        "date": "2026-01-15",
        "professional": "Dra. Valentina Rojas",
        "center": "Laboratorio Clínico (ejemplo)",
        "headers": ["Examen", "Resultado", "Unidad", "Referencia"],
        "rows": [
            ["Hemoglobina", "14,2", "g/dL", "13,0 – 17,0"],
            ["Hematocrito", "42,1", "%", "40,0 – 50,0"],
            ["Leucocitos", "6,8", "x10³/µL", "4,0 – 11,0"],
            ["Neutrófilos", "56", "%", "40 – 70"],
            ["Linfocitos", "34", "%", "20 – 45"],
            ["Plaquetas", "245", "x10³/µL", "150 – 400"],
            ["VCM", "90", "fL", "80 – 100"],
            ["HCM", "30", "pg", "27 – 33"],
        ],
        "widths": [2.0, 1.1, 1.1, 1.7],
        "align": ["left", "right", "left", "left"],
        "reading": [
            "Hemograma dentro de rangos de referencia.",
            "Sin anemia, leucocitosis ni trombocitopenia.",
            "No se observan hallazgos que sugieran infección aguda o alteración hematológica.",
        ],
        "role": "Medicina general · documento de ejemplo",
    })

    # 4. Planes
    build_plan({
        "filename": "fisiatria-2025-06-02-evaluacion-funcional.pdf",
        "doc_id": "DEMO-FIS-2025-0602-01",
        "doc_title": "Evaluación funcional — junio 2025",
        "title": "Evaluación funcional musculoesquelética",
        "subtitle": "Dolor lumbar y hombro derecho: capacidad funcional y objetivos.",
        "date": "2025-06-02",
        "professional": "Dr. Sebastián Herrera",
        "center": "Centro de Rehabilitación (ejemplo)",
        "objectives": [
            "Medir el impacto funcional del dolor lumbar y del hombro derecho.",
            "Identificar déficits de fuerza y movilidad que limiten la actividad.",
            "Definir objetivos medibles para un programa de ejercicio progresivo.",
        ],
        "table_title": "Resultados de la evaluación",
        "table": {
            "headers": ["Dominio", "Hallazgo", "Objetivo"],
            "rows": [
                ["Fuerza hombro derecho", "Rotación externa 4+/5", "Simetría 5/5 en 12 semanas"],
                ["Movilidad lumbar", "Flexión 60°, extensión 20°", "Mejorar control y tolerancia"],
                ["Dolor lumbar", "4/10 con carga", "≤ 2/10 en actividad diaria"],
                ["Dolor hombro", "3/10 en reposo", "Sin dolor en reposo"],
                ["Funcionalidad", "Buena capacidad global", "Mantener independencia"],
            ],
            "widths": [1.7, 2.1, 2.4],
        },
        "indications": [
            "Programa de ejercicio progresivo 3 veces por semana, con calentamiento de 5 minutos.",
            "Fortalecimiento del manguito rotador y control lumbar.",
            "Educación en higiene postural y manejo de carga.",
            "Registrar dolor antes y después de cada sesión.",
        ],
        "progress": "Progresar la carga cuando el dolor posterior a la sesión sea menor o igual a 3/10 y ceda en 24 horas. Si el dolor supera 5/10 o dura más de 24 horas, reducir volumen y consultar.",
        "precaution": "Suspender el ejercicio y consultar si aparece dolor irradiado, pérdida de fuerza, fiebre o dolor que no cede con el reposo.",
        "role": "Fisiatría · documento de ejemplo",
    })

    build_plan({
        "filename": "fisiatria-2025-06-02-plan-rehabilitacion.pdf",
        "doc_id": "DEMO-FIS-2025-0602-02",
        "doc_title": "Plan de rehabilitación física",
        "title": "Plan de rehabilitación física",
        "subtitle": "Programa progresivo para dolor lumbar y hombro derecho.",
        "date": "2025-06-02",
        "professional": "Dr. Sebastián Herrera",
        "center": "Centro de Rehabilitación (ejemplo)",
        "objectives": [
            "Recuperar fuerza y control motor del hombro derecho.",
            "Mejorar la tolerancia lumbar a la carga y al movimiento.",
            "Entregar herramientas para mantener la actividad física sin recaídas.",
        ],
        "table_title": "Estructura del programa",
        "table": {
            "headers": ["Fase", "Semanas", "Contenido", "Frecuencia"],
            "rows": [
                ["1. Movilidad", "1 – 2", "Movilidad suave y activación", "3 veces/semana"],
                ["2. Fuerza", "3 – 6", "Fortalecimiento progresivo", "3 veces/semana"],
                ["3. Integración", "7 – 10", "Carga funcional y gesto", "3 veces/semana"],
                ["4. Mantención", "11 – 12", "Rutina autónoma", "2 – 3 veces/semana"],
            ],
            "widths": [1.4, 0.9, 2.3, 1.5],
        },
        "indications": [
            "Calentar 5 minutos con movilidad y caminata suave.",
            "Trabajar en rangos cómodos; evitar dolor agudo durante el ejercicio.",
            "Progresar una variable por vez: carga, repeticiones o rango.",
            "Registrar dolor y adherencia en la bitácora semanal.",
        ],
        "progress": "La progresión se ajusta según dolor y función. Si el dolor post-sesión es ≤ 3/10 y cede en 24 horas, se puede aumentar la carga en la siguiente semana.",
        "precaution": "No entrenar con dolor agudo, fiebre o síntomas neurológicos nuevos. Consultar antes de retomar cargas altas.",
        "role": "Fisiatría · documento de ejemplo",
    })

    build_plan({
        "filename": "rehabilitacion-2025-07-10-plan-terapeutico.pdf",
        "doc_id": "DEMO-REHAB-2025-0710-01",
        "doc_title": "Plan terapéutico — 12 sesiones",
        "title": "Plan terapéutico de rehabilitación",
        "subtitle": "Doce sesiones con objetivos de fuerza, movilidad y retorno progresivo.",
        "date": "2025-07-10",
        "professional": "Klga. Fernanda Soto",
        "center": "Centro de Rehabilitación (ejemplo)",
        "objectives": [
            "Disminuir el dolor lumbar y del hombro durante la actividad cotidiana.",
            "Mejorar fuerza de rotación externa y control lumbopélvico.",
            "Lograr adherencia a una rutina de mantención autónoma.",
        ],
        "table_title": "Cronograma de sesiones",
        "table": {
            "headers": ["Sesión", "Foco", "Contenido principal"],
            "rows": [
                ["1 – 2", "Evaluación y educación", "Movilidad, respiración y línea base"],
                ["3 – 5", "Activación", "Control motor y fuerza básica"],
                ["6 – 8", "Progresión", "Carga gradual y gesto funcional"],
                ["9 – 11", "Integración", "Circuito y tareas de la vida diaria"],
                ["12", "Cierre", "Rutina de mantención y autocontrol"],
            ],
            "widths": [1.0, 1.8, 3.4],
        },
        "indications": [
            "Asistir 3 veces por semana; avisar si no se puede completar la sesión.",
            "Usar ropa cómoda y calzado deportivo.",
            "Hidratarse y evitar entrenar en ayunas.",
            "Comunicar dolor, mareo o cualquier síntoma nuevo durante la sesión.",
        ],
        "progress": "Se reevalúa fuerza y dolor en las sesiones 6 y 12. El alta se considera cuando los objetivos funcionales se cumplen y la persona puede mantener la rutina sin supervisión.",
        "precaution": "Este plan es de ejemplo y no reemplaza la evaluación presencial. Suspender si aparece dolor torácico, disnea o déficit neurológico.",
        "role": "Kinesiología · documento de ejemplo",
    })

    build_plan({
        "filename": "rehabilitacion-2025-09-30-informe-evolucion.pdf",
        "doc_id": "DEMO-REHAB-2025-0930-02",
        "doc_title": "Informe de evolución — septiembre 2025",
        "title": "Informe de evolución del programa",
        "subtitle": "Adherencia, progreso y ajustes al plan de rehabilitación.",
        "date": "2025-09-30",
        "professional": "Klga. Fernanda Soto",
        "center": "Centro de Rehabilitación (ejemplo)",
        "objectives": [
            "Documentar el progreso funcional al completar 10 de 12 sesiones.",
            "Revisar adherencia y tolerancia al ejercicio.",
            "Definir el plan de mantención y los criterios de alta.",
        ],
        "table_title": "Indicadores de progreso",
        "table": {
            "headers": ["Indicador", "Inicio", "Actual", "Interpretación"],
            "rows": [
                ["Dolor lumbar", "4/10", "2/10", "Mejoría"],
                ["Dolor hombro", "3/10", "1/10", "Mejoría"],
                ["Rotación externa", "4+/5", "5/5", "Objetivo logrado"],
                ["Adherencia", "—", "83 %", "Buena"],
                ["Sesiones completadas", "0", "10 de 12", "En curso"],
            ],
            "widths": [1.7, 1.0, 1.2, 1.7],
        },
        "indications": [
            "Continuar con las dos sesiones restantes y transición a mantención.",
            "Rutina domiciliaria 3 veces por semana, con progresión gradual.",
            "Mantener pausas activas y higiene postural en el trabajo.",
            "Control de cierre en 4 semanas.",
        ],
        "progress": "El dolor y la fuerza mejoraron de forma consistente. La adherencia del 83 % se considera buena; el foco pasa a sostener la rutina y prevenir recaídas.",
        "precaution": "Reevaluar si el dolor vuelve a 5/10, limita actividades diarias o aparece déficit neurológico nuevo.",
        "role": "Kinesiología · documento de ejemplo",
    })

    # 5. Estudios con trazado
    build_ecg_report()
    build_eeg_report()
    build_prescription()
    build_emergency_summary()

    print(f"Generados {len(DOCUMENTS)} PDF en {OUT}\n")
    for name, kb in sorted(DOCUMENTS):
        print(f"  {name:66s} {kb:6.1f} KB")


if __name__ == "__main__":
    main()


