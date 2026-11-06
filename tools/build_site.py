#!/usr/bin/env python3
"""Build the static saludrcartes site.

Usage:
    python tools/build_site.py

Reads `data/registro.json`, writes the 13 HTML pages plus the search index,
manifest and deployment helper files. No third-party dependencies.
"""
from __future__ import annotations

import html
import json
import re
import shutil
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "registro.json"
DATA = json.loads(DATA_PATH.read_text(encoding="utf-8"))

SITE = DATA["sitio"]
PERFIL = DATA["perfil"]
CRITICO = DATA["critico"]
GRUPOS = {group["id"]: group for group in DATA["grupos"]}
CATEGORIAS = {cat["id"]: cat for cat in DATA["categorias"]}
CATEGORIAS_ORDER = sorted(DATA["categorias"], key=lambda item: item["orden"])
AFECCIONES = DATA["afecciones"]
DOCS = DATA["documentos"]
MEDICAMENTOS = DATA["medicamentos"]
ALERGIAS = DATA["alergias"]
CONTACTOS = sorted(DATA["contactos"], key=lambda item: item["orden"])
LABORATORIO = DATA["laboratorio"]
PRINCIPIOS = DATA["principios"]
RESUMEN = DATA["resumen_sitio"]

MONTHS = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]
MONTHS_SHORT = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sept", "oct", "nov", "dic"]

EMERGENCY_DOC = {
    "id": "doc-emergencia-ficha",
    "afeccion_id": "afeccion-emergencia",
    "categoria_id": "emergencia",
    "nombre": "Ficha de emergencia — resumen clínico",
    "archivo": "assets/docs/emergencia-ficha-resumen.pdf",
    "tipo_archivo": "PDF",
    "fecha": CRITICO["actualizado"],
    "tamano": "1 pág.",
    "descripcion": "Diagnósticos, alergias, medicamentos y contactos en una hoja imprimible.",
}
DOCS_ALL = DOCS + [EMERGENCY_DOC]
DOCS_BY_CAT: dict[str, list[dict]] = {}
for _doc in DOCS_ALL:
    DOCS_BY_CAT.setdefault(_doc["categoria_id"], []).append(_doc)

AFECCIONES_BY_CAT: dict[str, list[dict]] = {}
for _afeccion in AFECCIONES:
    AFECCIONES_BY_CAT.setdefault(_afeccion["categoria_id"], []).append(_afeccion)

PRIMARY_CONTACT = next((contact for contact in CONTACTOS if contact.get("principal")), CONTACTOS[0])
PUBLIC_CONTACTS = [contact for contact in CONTACTOS if contact["tipo_contacto"] == "Emergencia pública"]
PRIVATE_CONTACTS = [contact for contact in CONTACTOS if contact["tipo_contacto"] != "Emergencia pública"]


# ---------------------------------------------------------------------------
# Icon sprite
# ---------------------------------------------------------------------------
ICONS = {
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "arrow-right": '<path d="M4 12h15"/><path d="m13 6 6 6-6 6"/>',
    "arrow-left": '<path d="M20 12H5"/><path d="m11 18-6-6 6-6"/>',
    "arrow-up-right": '<path d="M7 17 17 7"/><path d="M8 7h9v9"/>',
    "arrow-down": '<path d="M12 4v15"/><path d="m6 13 6 6 6-6"/>',
    "chevron-right": '<path d="m9 5 7 7-7 7"/>',
    "chevron-left": '<path d="m15 5-7 7 7 7"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "home": '<path d="M3 10.5 12 3l9 7.5V20a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/><path d="M9 22v-9h6v9"/>',
    "clipboard-pulse": '<rect x="5" y="4" width="14" height="18" rx="2"/><path d="M9 4V3.5A1.5 1.5 0 0 1 10.5 2h3A1.5 1.5 0 0 1 15 3.5V4"/><path d="M8 11h2.2l1.2-2 2 4 1.2-2H17"/>',
    "pill": '<path d="M10.5 20.5 3.5 13.5a5 5 0 0 1 7-7l7 7a5 5 0 0 1-7 7Z"/><path d="m8.5 8.5 7 7"/>',
    "flask": '<path d="M9 3h6"/><path d="M10 3v6L4.8 18.6A2 2 0 0 0 6.6 22h10.8a2 2 0 0 0 1.8-3.4L14 9V3"/><path d="M8 15h8"/>',
    "brain": '<path d="M9.5 3A2.5 2.5 0 0 0 7 5.5v.2A3.2 3.2 0 0 0 5 11a3.2 3.2 0 0 0 1.2 4.8A3.2 3.2 0 0 0 9 21a3 3 0 0 0 4-2.8V5.5A2.5 2.5 0 0 0 9.5 3Z"/><path d="M14.5 3A2.5 2.5 0 0 1 17 5.5v.2a3.2 3.2 0 0 1 2 5.3 3.2 3.2 0 0 1-1.2 4.8A3.2 3.2 0 0 1 15 21a3 3 0 0 1-4-2.8"/><path d="M9 8.5h1.5M13.5 9H15M9 14h1.5M13.5 14H15"/>',
    "heart-pulse": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1.1L12 21.3l7.8-7.8 1.1-1.1a5.5 5.5 0 0 0 0-7.8Z"/><path d="M4.2 12h3.4l1.5-3.2 2.5 5.8 1.5-2.6h3.4"/>',
    "activity": '<path d="M3 12h4l3-9 4 18 3-9h4"/>',
    "dumbbell": '<path d="M6 5v14M18 5v14M3 8v8M21 8v8M6 12h12"/>',
    "message-wave": '<path d="M21 11.5a8.4 8.4 0 0 1-8.5 8.5 8.5 8.5 0 0 1-3.8-.9L3 21l1.6-4.3A8.5 8.5 0 1 1 21 11.5Z"/><path d="M8 10h.5M11.8 10h.5M15.6 10h.5" stroke-width="2.2"/>',
    "mind": '<path d="M14.5 21v-3.5H17a2 2 0 0 0 2-2v-1.8A7.5 7.5 0 1 0 5.2 10a5 5 0 0 0 1.6 10h1.7v1"/><path d="M9 8h.5M12.5 8h.5M9 12h.5M12.5 12h.5"/>',
    "arm": '<path d="M5 4h3.5L10 9l7-2 3.5 1-1 4-5 1.5-1 7.5h-3l-1-6.5L5 12V4Z"/><path d="M8.5 4v5"/>',
    "leg": '<path d="M8 3h5l1 8 4.5 7-3 3-5-7-3 4-3-2 3.5-6L8 3Z"/><path d="M10 3v6"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/>',
    "phone-call": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/><path d="M14 2a8 8 0 0 1 8 8M14.5 6a4 4 0 0 1 3.5 3.5"/>',
    "users": '<circle cx="9" cy="7" r="3"/><path d="M3 21v-2a5 5 0 0 1 5-5h2a5 5 0 0 1 5 5v2"/><circle cx="17.5" cy="8" r="2.5"/><path d="M17.5 14a4.5 4.5 0 0 1 4.5 4.5V20"/>',
    "stethoscope": '<path d="M5 3v6a4 4 0 0 0 8 0V3"/><path d="M5 3H3M13 3h2"/><path d="M9 13v2a5 5 0 0 0 10 0v-1"/><circle cx="19" cy="10" r="2"/>',
    "hospital": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 21v-6h6v6M12 7v6M9 10h6"/>',
    "ambulance": '<path d="M2 17V7h11v10"/><path d="M13 10h4l3 3.2V17h-7"/><circle cx="6" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M4 17h0M10 17h5"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/>',
    "shield-heart": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="M12 16s-3-1.7-3-4a2 2 0 0 1 3-1.7A2 2 0 0 1 15 12c0 2.3-3 4-3 4Z"/>',
    "flame": '<path d="M12 22c4 0 7-3 7-7 0-4-3-6-4-10-1 3-3 4-3 7-1-1-2-2-2-4-2 2-5 4-5 8 0 4 3 6 7 6Z"/>',
    "folder": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/>',
    "file-text": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
    "download": '<path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
    "print": '<path d="M6 9V3h12v6"/><rect x="6" y="14" width="12" height="7"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
    "alert-triangle": '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>',
    "alert-circle": '<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21v-1a7 7 0 0 1 7-7h2a7 7 0 0 1 7 7v1"/>',
    "building": '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01"/>',
    "droplet": '<path d="M12 2.7 5.6 9.1a9 9 0 1 0 12.8 0Z"/>',
    "sparkles": '<path d="m12 3 1.8 4.2L18 9l-4.2 1.8L12 15l-1.8-4.2L6 9l4.2-1.8Z"/><path d="m19 15 .9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9Z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 4 13c0-6 7-9 16-9 0 9-3 16-9 16Z"/><path d="M4 21c4-8 8-11 12-13"/>',
    "book-open": '<path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2Z"/><path d="M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7Z"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    "sliders": '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3"/><path d="M1 14h6M9 8h6M17 16h6"/>',
    "contrast": '<circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 0 18Z" fill="currentColor" stroke="none"/>',
    "type": '<path d="M4 7V4h16v3M12 4v16M8 20h8"/>',
    "wind": '<path d="M3 8h11a3 3 0 1 0-3-3"/><path d="M3 12h15a3 3 0 1 1-3 3"/><path d="M3 16h7"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "lock": '<rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="m16 8-2.3 5.7L8 16l2.3-5.7L16 8Z"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1.1L12 21.3l7.8-7.8 1.1-1.1a5.5 5.5 0 0 0 0-7.8Z"/>',
    "quote": '<path d="M10 11H6a3 3 0 0 1 3-3V5a6 6 0 0 0-6 6v6h7Z"/><path d="M21 11h-4a3 3 0 0 1 3-3V5a6 6 0 0 0-6 6v6h7Z"/>',
}


def icon(name: str, cls: str = "") -> str:
    """Return an inline <svg> that references the sprite."""
    classes = ("icon " + cls).strip()
    return (
        f'<svg class="{classes}" aria-hidden="true" focusable="false">'
        f'<use href="#i-{name}"></use></svg>'
    )


def icon_sprite() -> str:
    symbols = "".join(
        f'<symbol id="i-{name}" viewBox="0 0 24 24">{body}</symbol>'
        for name, body in ICONS.items()
    )
    return (
        '<svg class="icon-sprite" aria-hidden="true" focusable="false" '
        'xmlns="http://www.w3.org/2000/svg">' + symbols + "</svg>"
    )


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def esc(value) -> str:
    return html.escape(str(value), quote=True)


def human_date(iso: str | None, style: str = "short") -> str:
    if not iso:
        return "Sin fecha"
    try:
        year, month, day = (int(part) for part in iso.split("-")[:3])
    except (ValueError, AttributeError):
        return esc(iso)
    month_name = MONTHS[month - 1] if style == "long" else MONTHS_SHORT[month - 1]
    if style == "long":
        return f"{day} de {month_name} de {year}"
    return f"{day} {month_name} {year}"


def time_tag(iso: str | None, style: str = "short") -> str:
    label = human_date(iso, style)
    if not iso:
        return esc(label)
    return f'<time datetime="{esc(iso)}">{esc(label)}</time>'


def fecha_short(iso: str | None) -> str:
    return human_date(iso, "short")


def fecha_long(iso: str | None) -> str:
    return human_date(iso, "long")


def tel_href(phone: str) -> str:
    clean = re.sub(r"[^\d+]", "", phone or "")
    return "tel:" + clean


def status_tone(estado: str) -> str:
    value = (estado or "").lower()
    if "seguimiento" in value:
        return "status--seguimiento"
    if "tratamiento" in value:
        return "status--tratamiento"
    if "resuelta" in value:
        return "status--resuelta"
    if "evaluación" in value or "evaluacion" in value or "preventivo" in value:
        return "status--evaluacion"
    if "progreso" in value:
        return "status--progreso"
    if "vigente" in value:
        return "status--vigente"
    return "status--estable"


def status_badge(estado: str, extra: str = "") -> str:
    return (
        f'<span class="status {status_tone(estado)} {extra}">'
        '<span class="status__dot" aria-hidden="true"></span>'
        f"{esc(estado)}</span>"
    )


def group_of(cat: dict) -> dict:
    return GRUPOS[cat["grupo"]]


def nav_label(cat: dict) -> str:
    return cat.get("navLabel") or cat["nombre"]


def cat_url(cat: dict) -> str:
    return cat["url"]


def related_categories(ids: list[str]) -> list[dict]:
    return [CATEGORIAS[item] for item in ids if item in CATEGORIAS]


def docs_for(cat_id: str) -> list[dict]:
    return DOCS_BY_CAT.get(cat_id, [])


def conditions_for(cat_id: str) -> list[dict]:
    return AFECCIONES_BY_CAT.get(cat_id, [])


def unique(values) -> list[str]:
    result = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def total_documents() -> int:
    return len(DOCS_ALL)


# ---------------------------------------------------------------------------
# Document cards
# ---------------------------------------------------------------------------
def document_card(doc: dict, show_category: bool = False) -> str:
    cat = CATEGORIAS.get(doc["categoria_id"])
    meta = [fecha_short(doc["fecha"]), doc["tamano"]]
    if show_category and cat:
        meta.insert(0, cat["navLabel"])
    meta_text = " · ".join(esc(part) for part in meta)
    doc_meta = f'PDF · {fecha_short(doc["fecha"])} · {doc["tamano"]}'
    return f"""
    <article class="doc-card">
      <div class="doc-card__icon" aria-hidden="true">PDF</div>
      <div>
        <p class="doc-card__meta">{meta_text}</p>
        <h3 class="doc-card__title">{esc(doc["nombre"])}</h3>
        <p class="doc-card__desc">{esc(doc["descripcion"])}</p>
      </div>
      <div class="doc-card__actions">
        <button type="button" class="btn btn--small btn--ghost"
          data-preview="{esc(doc["archivo"])}"
          data-title="{esc(doc["nombre"])}"
          data-download="{esc(doc["archivo"])}"
          data-meta="{esc(doc_meta)}"
          aria-label="Vista previa de {esc(doc["nombre"])}">
          {icon("eye")} Vista previa
        </button>
        <a class="btn btn--small btn--ghost" href="{esc(doc["archivo"])}"
          download="{esc(Path(doc["archivo"]).name)}"
          aria-label="Descargar {esc(doc["nombre"])}, PDF, {esc(doc["tamano"])}">
          {icon("download")} Descargar
        </a>
      </div>
    </article>"""


def document_table(docs: list[dict], title: str, description: str = "") -> str:
    rows = []
    for doc in docs:
        cat = CATEGORIAS.get(doc["categoria_id"])
        rows.append(
            "<tr>"
            f'<td data-label="Documento"><span class="cell-title">{esc(doc["nombre"])}</span>'
            f'<span class="cell-muted">{esc(doc["descripcion"])}</span></td>'
            f'<td data-label="Fecha" class="cell-mono">{time_tag(doc["fecha"])}</td>'
            f'<td data-label="Categoría">{esc(cat["navLabel"] if cat else "Emergencia")}</td>'
            f'<td data-label="Acciones"><a class="cell-link" href="{esc(doc["archivo"])}" download>Descargar PDF</a></td>'
            "</tr>"
        )
    return f"""
    <div class="table-card">
      <div class="table-card__head">
        <div><h3>{esc(title)}</h3>{f'<p>{esc(description)}</p>' if description else ''}</div>
      </div>
      <div class="table-scroll">
        <table class="data-table">
          <thead><tr><th>Documento</th><th>Fecha</th><th>Categoría</th><th>Acciones</th></tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </div>
    </div>"""


# ---------------------------------------------------------------------------
# Common chrome
# ---------------------------------------------------------------------------
def masthead(current: str, emergency: bool = False) -> str:
    home_href = "" if current == "inicio" else "index.html"
    registro_href = "#registro" if current == "inicio" else "index.html#registro"
    especialidades_href = "#especialidades" if current == "inicio" else "index.html#especialidades"
    if emergency:
        call = f'<a class="sos" href="{tel_href(PRIMARY_CONTACT["telefono"])}"><span class="sos__dot" aria-hidden="true"></span><span class="sos__full">Llamar ahora</span><span class="sos__short">Llamar</span></a>'
    else:
        call = (
            '<a class="sos" href="emergencia.html" aria-label="Abrir la ficha de emergencia">'
            '<span class="sos__dot" aria-hidden="true"></span>'
            '<span class="sos__full">Emergencia</span><span class="sos__short">SOS</span>'
            f"{icon('phone-call')}</a>"
        )
    return f"""
  <header class="masthead" data-header>
    <div class="shell masthead__inner">
      <a class="brand" href="{home_href or 'index.html'}" aria-label="saludrcartes, ir al inicio">
        <span class="brand__mark" aria-hidden="true">rc</span>
        <span><span class="brand__word">salud<span>rcartes</span></span><span class="brand__tag">Registro clínico personal</span></span>
      </a>
      <nav class="primary-nav" aria-label="Navegación principal">
        <a href="{home_href or 'index.html'}"{' aria-current="page"' if current == 'inicio' else ''}>Inicio</a>
        <a href="{registro_href}">Registro clínico</a>
        <a href="{especialidades_href}">Especialidades</a>
      </nav>
      <div class="masthead__actions">
        <button type="button" class="search-trigger" data-open-search aria-label="Buscar en el registro">
          {icon("search")}<span class="search-label">Buscar</span><span class="kbd" aria-hidden="true">/</span>
        </button>
        <button type="button" class="icon-btn index-toggle" data-open-index aria-label="Abrir el índice de capítulos">
          {icon("list")}
        </button>
        <button type="button" class="icon-btn menu-toggle" data-open-index aria-label="Abrir el índice de capítulos">
          {icon("menu")}
        </button>
        <button type="button" class="icon-btn" data-open-prefs aria-label="Preferencias de lectura">
          {icon("sliders")}
        </button>
        {call}
      </div>
    </div>
  </header>"""


def sheet_index() -> str:
    links_registro = "".join(index_link(cat) for cat in CATEGORIAS_ORDER if cat["grupo"] == "registro")
    links_especialidades = "".join(index_link(cat) for cat in CATEGORIAS_ORDER if cat["grupo"] == "especialidades")
    links_emergencia = "".join(index_link(cat) for cat in CATEGORIAS_ORDER if cat["grupo"] == "emergencia")
    return f"""
  <section class="sheet" data-sheet="index" aria-hidden="true" aria-labelledby="index-title" inert>
    <button type="button" class="sheet__backdrop" data-close-sheet tabindex="-1" aria-label="Cerrar el índice"></button>
    <div class="sheet__panel" role="dialog" aria-modal="true" aria-labelledby="index-title">
      <div class="sheet__head">
        <span class="sheet__title" id="index-title">{icon("book-open")} Índice de la historia</span>
        <button type="button" class="icon-btn" data-close-sheet aria-label="Cerrar el índice">{icon("close")}</button>
      </div>
      <div class="index-grid">
        <aside class="index-aside">
          <div>
            <img class="index-aside__seal" src="assets/img/ui/sello.svg" alt="" width="200" height="200">
            <h2>Doce capítulos,<br><em>una vida.</em></h2>
            <p>Recorre el registro completo o salta directo a lo que necesitas. La ficha de emergencia está siempre a un toque.</p>
            <a class="index-aside__sos" href="emergencia.html">{icon("phone-call")} Abrir ficha de emergencia</a>
          </div>
          <a class="link-arrow" href="index.html">{icon("home")} Volver al inicio</a>
        </aside>
        <div class="index-main">
          <div class="index-group">
            <p class="index-group__title">Registro clínico</p>
            {links_registro}
          </div>
          <div class="index-group">
            <p class="index-group__title">Especialidades médicas</p>
            {links_especialidades}
          </div>
          <div class="index-group">
            <p class="index-group__title">Emergencia</p>
            {links_emergencia}
          </div>
          {preferences_panel()}
        </div>
      </div>
    </div>
  </section>"""


def index_link(cat: dict) -> str:
    return f"""
    <a class="index-link" href="{esc(cat['url'])}">
      <span class="index-link__num">{esc(cat['numero'])}</span>
      <span><span class="index-link__title">{esc(cat['nombre'])}</span><span class="index-link__desc">{esc(cat['descripcion'])}</span></span>
      {icon("arrow-right")}
    </a>"""


def preferences_panel() -> str:
    return f"""
    <div class="prefs">
      <p class="prefs__title">{icon("sliders")} Preferencias de lectura</p>
      <div class="prefs__row">
        <span class="prefs__label">Tamaño del texto<span class="prefs__hint">Ajusta sin romper el diseño</span></span>
        <div class="seg" role="group" aria-label="Tamaño del texto">
          <button type="button" data-text-size="md" aria-pressed="true">A</button>
          <button type="button" data-text-size="lg" aria-pressed="false">A+</button>
          <button type="button" data-text-size="xl" aria-pressed="false">A++</button>
        </div>
      </div>
      <div class="prefs__row">
        <span class="prefs__label">Alto contraste<span class="prefs__hint">Bordes y texto reforzados</span></span>
        <button type="button" class="switch" data-toggle-contrast role="switch" aria-checked="false" aria-label="Activar alto contraste"></button>
      </div>
      <div class="prefs__row">
        <span class="prefs__label">Reducir movimiento<span class="prefs__hint">Detiene animaciones decorativas</span></span>
        <button type="button" class="switch" data-toggle-motion role="switch" aria-checked="false" aria-label="Reducir movimiento"></button>
      </div>
      <p class="sheet-note">Atajos: <span class="kbd">Ctrl</span> + <span class="kbd">K</span> para buscar · <span class="kbd">Esc</span> para cerrar. Las preferencias se guardan en este dispositivo.</p>
    </div>"""


def sheet_search() -> str:
    return f"""
  <section class="sheet" data-sheet="search" aria-hidden="true" aria-labelledby="search-title" inert>
    <button type="button" class="sheet__backdrop" data-close-sheet tabindex="-1" aria-label="Cerrar la búsqueda"></button>
    <div class="sheet__panel search-panel" role="dialog" aria-modal="true" aria-labelledby="search-title">
      <div class="sheet__head search-head">
        <span class="sheet__title" id="search-title">{icon("search")} Buscar en la historia</span>
        <button type="button" class="icon-btn" data-close-sheet aria-label="Cerrar la búsqueda">{icon("close")}</button>
      </div>
      <label class="search-box">
        <span class="sr-only">Buscar un diagnóstico, medicamento, especialidad o documento</span>
        {icon("search")}
        <input type="search" data-search-input placeholder="Diagnóstico, medicamento, especialidad…" autocomplete="off" spellcheck="false">
      </label>
      <div class="search-hint">
        <span>{len(CATEGORIAS)} páginas · {total_documents()} documentos · {len(AFECCIONES)} diagnósticos</span>
        <span><span class="kbd">Esc</span> para cerrar</span>
      </div>
      <div class="search-results" data-search-results role="list" aria-live="polite"></div>
    </div>
  </section>"""


def doc_modal() -> str:
    return f"""
  <div class="doc-modal" data-doc-modal aria-hidden="true" inert>
    <button type="button" class="doc-modal__backdrop" data-close-doc tabindex="-1" aria-label="Cerrar la vista previa"></button>
    <div class="doc-modal__panel" role="dialog" aria-modal="true" aria-labelledby="doc-modal-title">
      <div class="doc-modal__head">
        <p class="doc-modal__title" id="doc-modal-title">
          <span class="doc-modal__title-text">Documento clínico</span>
          <span class="doc-modal__sub">PDF</span>
        </p>
        <div class="doc-modal__actions">
          <a class="btn btn--small btn--ghost doc-modal__download" href="#" download>{icon("download")} Descargar</a>
          <button type="button" class="icon-btn" data-close-doc aria-label="Cerrar la vista previa">{icon("close")}</button>
        </div>
      </div>
      <iframe title="Vista previa del documento clínico" src="about:blank" loading="lazy"></iframe>
    </div>
  </div>"""


def site_footer() -> str:
    registro_links = "".join(
        f'<a href="{esc(cat["url"])}">{icon("arrow-right")} {esc(cat["navLabel"])}</a>'
        for cat in CATEGORIAS_ORDER if cat["grupo"] == "registro"
    )
    emergency_link = f'<a href="emergencia.html">{icon("phone-call")} Emergencia</a>'
    specialty_links = "".join(
        f'<a href="{esc(cat["url"])}">{icon("arrow-right")} {esc(cat["navLabel"])}</a>'
        for cat in CATEGORIAS_ORDER if cat["grupo"] == "especialidades"
    )
    return f"""
  <footer class="site-footer">
    <div class="shell">
      <div class="footer__top">
        <div class="footer__brand">
          <a class="brand" href="index.html" aria-label="saludrcartes, ir al inicio">
            <span class="brand__mark" aria-hidden="true">rc</span>
            <span><span class="brand__word">salud<span>rcartes</span></span><span class="brand__tag">Registro clínico personal</span></span>
          </a>
          <p class="footer__tagline">{esc(SITE["lema"])} Un archivo personal, claro y confidencial, para consultar solo o acompañado.</p>
          <div class="footer__badges">
            <span class="footer__badge">{icon("lock")} Sin indexación</span>
            <span class="footer__badge">{icon("check-circle")} WCAG 2.1 AA</span>
            <span class="footer__badge">{icon("file-text")} {total_documents()} PDF</span>
          </div>
        </div>
        <div>
          <p class="footer__title">Registro clínico</p>
          <div class="footer__links">
            {registro_links}
            {emergency_link}
          </div>
        </div>
        <div>
          <p class="footer__title">Especialidades</p>
          <div class="footer__links">{specialty_links}</div>
        </div>
        <div class="footer__note">
          <p><strong>En una urgencia, no busques.</strong> La ficha pública reúne grupo sanguíneo, alergias, condiciones, medicamentos y teléfonos con llamada directa.</p>
          <a class="link-arrow" href="emergencia.html">{icon("phone-call")} Abrir ficha de emergencia</a>
        </div>
      </div>
      <div class="footer__bottom">
        <p>© <span data-year>{SITE["anio"]}</span> {esc(SITE["titular"])} · Sitio personal, sin cookies de terceros.</p>
        <div class="footer__bottom-links">
          <a href="index.html">Inicio</a>
          <a href="index.html#registro">Registro clínico</a>
          <a href="emergencia.html">Emergencia</a>
          <button type="button" class="footer__plain" data-open-search>Buscar</button>
          <button type="button" class="footer__plain" data-open-index>Índice</button>
          <button type="button" class="footer__plain" data-print>Imprimir</button>
        </div>
        <span class="footer__version">v{SITE["version"]} · Actualizado {fecha_short(SITE["actualizado"])}</span>
      </div>
    </div>
  </footer>"""


def emergency_footer() -> str:
    return f"""
  <footer class="ep-footer">
    <div class="shell ep-footer__inner">
      <p>© <span data-year>{SITE["anio"]}</span> saludrcartes · Ficha pública de emergencia · v{SITE["version"]}</p>
      <div class="ep-footer__links">
        <a href="index.html">Inicio</a>
        <a href="index.html#registro">Registro clínico</a>
        <a href="index.html#especialidades">Especialidades</a>
        <button type="button" class="footer__plain" data-print>Imprimir ficha</button>
      </div>
    </div>
  </footer>"""


def overlays() -> str:
    return f"""
  <div class="toast-region" aria-live="polite" aria-atomic="true"></div>
  {sheet_index()}
  {sheet_search()}
  {doc_modal()}"""


# ---------------------------------------------------------------------------
# Page head / shell
# ---------------------------------------------------------------------------
def page_head(
    *,
    slug: str,
    title: str,
    description: str,
    accent: str,
    art: str,
    extra_css: tuple[str, ...] = (),
    emergency: bool = False,
) -> str:
    theme = "#081b15" if emergency else "#fff8f0"
    page_classes = [f"accent-{accent}", f"page--{slug}"]
    if slug == "inicio":
        page_classes.append("page--home")
    if emergency:
        page_classes.append("theme-emergency")
    css_files = ["assets/css/fonts.css", "assets/css/base.css", "assets/css/accents.css", "assets/css/home.css"]
    css_files.extend(extra_css)
    css_files.append("assets/css/responsive.css")
    css_tags = "\n  ".join(f'<link rel="stylesheet" href="{href}">' for href in css_files)
    return f"""<!doctype html>
<html lang="es-CL" class="no-js">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="noindex, nofollow, noarchive, nosnippet">
  <meta name="theme-color" content="{theme}">
  <meta name="color-scheme" content="{'dark' if emergency else 'light'}">
  <link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
  <link rel="manifest" href="manifest.webmanifest">
  <script src="assets/js/theme-boot.js"></script>
  {css_tags}
  <noscript><style>[data-reveal]{{opacity:1!important;transform:none!important}}</style></noscript>
</head>
<body class="{' '.join(page_classes)}" style="--ambient-art:url('{art}')">
<a class="skip-link" href="#contenido">Saltar al contenido</a>
{icon_sprite()}
<div class="ambient" aria-hidden="true">
  <div class="ambient__art"></div>
  <div class="ambient__veil"></div>
  <div class="ambient__orb ambient__orb--a"></div>
  <div class="ambient__orb ambient__orb--b"></div>
  <div class="ambient__grain"></div>
</div>"""


def render_page(
    *,
    slug: str,
    title: str,
    description: str,
    accent: str,
    art: str,
    main_html: str,
    extra_css: tuple[str, ...] = (),
    emergency: bool = False,
    footer_html: str | None = None,
    print_title: str = "",
) -> str:
    footer = footer_html if footer_html is not None else site_footer()
    print_header = f"""
    <div class="print-header">
      <strong>saludrcartes</strong> · Registro clínico personal<br>
      {esc(print_title or title)} · {esc(PERFIL['nombre'])} · Impreso: <span data-print-date></span>
    </div>"""
    print_footer = """
    <div class="print-footer">
      Documento generado desde saludrcartes. Los datos de contacto son de ejemplo y deben confirmarse antes de una urgencia.
    </div>"""
    return (
        page_head(
            slug=slug,
            title=title,
            description=description,
            accent=accent,
            art=art,
            extra_css=extra_css,
            emergency=emergency,
        )
        + "\n"
        + masthead(slug, emergency=emergency)
        + f'\n<main id="contenido">{print_header}{main_html}{print_footer}</main>'
        + "\n"
        + footer
        + overlays()
        + '\n<script src="assets/js/search-index.js"></script>\n<script src="assets/js/site.js"></script>\n</body>\n</html>\n'
    )


# ---------------------------------------------------------------------------
# Art frame
# ---------------------------------------------------------------------------
def art_frame(art: str, alt: str, caption: str, chips: str = "") -> str:
    return f"""
      <div class="hero-art" data-reveal>
        <div class="hero-art__glow" aria-hidden="true"></div>
        <div class="art-float">
          <div class="art-backplate" aria-hidden="true"></div>
          <figure class="art-frame">
            <img src="{esc(art)}" alt="{esc(alt)}" width="1600" height="1100">
            <figcaption class="art-frame__caption">{esc(caption)}</figcaption>
          </figure>
        </div>
        {chips}
        <img class="seal" src="assets/img/ui/sello.svg" alt="" width="200" height="200" aria-hidden="true">
      </div>"""


def chip(icon_name: str, label: str, value: str, position: str) -> str:
    return f"""
        <div class="float-chip float-chip--{position}">
          <span class="float-chip__icon">{icon(icon_name)}</span>
          <span><span class="float-chip__label">{esc(label)}</span><strong>{esc(value)}</strong></span>
        </div>"""


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------
def portal_card(cat: dict) -> str:
    return f"""
    <a class="portal-card accent-{cat['acento']}" href="{esc(cat['url'])}" data-reveal>
      <img class="portal-card__media" src="{esc(cat['arte'])}" alt="Ilustración de {esc(cat['nombre'])}" loading="lazy" width="1600" height="1100">
      <span class="portal-card__top">
        <span class="portal-card__num" aria-hidden="true">{esc(cat['numero'])}</span>
        <span class="portal-card__arrow" aria-hidden="true">{icon("arrow-up-right")}</span>
      </span>
      <span class="portal-card__body">
        <span class="portal-card__kicker">{esc(group_of(cat)['nombre'])}</span>
        <span class="portal-card__title">{esc(cat['nombre'])}</span>
        <span class="portal-card__desc">{esc(cat['descripcion'])}</span>
        <span class="portal-card__foot">
          <span>{status_badge(cat['estado'])}</span>
          <span class="portal-card__cta">Abrir {icon("arrow-right")}</span>
        </span>
      </span>
    </a>"""


def chapter_card(cat: dict, delay: int = 0) -> str:
    return f"""
    <a class="chapter-card accent-{cat['acento']}" href="{esc(cat['url'])}" data-reveal style="--d:{delay}ms">
      <span class="chapter-card__media">
        <img src="{esc(cat['arte'])}" alt="Ilustración de {esc(cat['nombre'])}" loading="lazy" width="1600" height="1100">
        <span class="chapter-card__num" aria-hidden="true">{esc(cat['numero'])}</span>
      </span>
      <span class="chapter-card__body">
        <span class="chapter-card__title">{esc(cat['navLabel'])}</span>
        <span class="chapter-card__desc">{esc(cat['descripcion'])}</span>
        <span class="chapter-card__foot">
          <span>{esc(cat['estado'])}</span>
          <span class="chapter-card__arrow" aria-hidden="true">{icon("arrow-up-right")}</span>
        </span>
      </span>
    </a>"""


def section_head(eyebrow: str, number: str, title: str, lead: str) -> str:
    return f"""
      <div class="section__head" data-reveal>
        <p class="section__eyebrow"><span class="section__num">{esc(number)}</span>{esc(eyebrow)}</p>
        <h2 class="section__title">{title}</h2>
        <p class="section__lead">{lead}</p>
      </div>"""


def home_page() -> str:
    registro = [cat for cat in CATEGORIAS_ORDER if cat["grupo"] == "registro"]
    especialidades = [cat for cat in CATEGORIAS_ORDER if cat["grupo"] == "especialidades"]
    emergency_cat = next(cat for cat in CATEGORIAS_ORDER if cat["grupo"] == "emergencia")
    recent_docs = sorted(DOCS, key=lambda doc: doc["fecha"], reverse=True)[:4]
    marquee_items = [
        "Diagnósticos", "Medicamentos", "Laboratorio", "Neurología", "Cardiología",
        "Fisiatría", "Rehabilitación", "Fonoaudiología", "Psiquiatría",
        "Traumatología superior", "Traumatología inferior", "Emergencia",
    ]
    marquee = "".join(f'<span class="marquee__item">{esc(item)}</span>' for item in marquee_items)
    principles = "".join(
        f"""
        <div class="principle" data-reveal>
          <span class="principle__num">0{index}</span>
          <span class="principle__icon">{icon(item['icono'])}</span>
          <h3>{esc(item['titulo'])}</h3>
          <p>{esc(item['texto'])}</p>
        </div>"""
        for index, item in enumerate(PRINCIPIOS, 1)
    )
    art = "assets/img/art/inicio.svg"
    main = f"""
  <header class="hero hero--home">
    <div class="shell hero__grid">
      <div class="hero__copy" data-reveal>
        <p class="eyebrow">Registro clínico personal <span class="eyebrow__badge">{icon("lock")} v{SITE["version"]} · 2026</span></p>
        <h1 class="display">
          <span class="line">Mi salud,</span>
          <span class="line"><em>en una sola</em></span>
          <span class="line">historia<span class="accent-dot">.</span></span>
        </h1>
        <p class="lead">Soy <strong>{esc(PERFIL['preferido'])}</strong>. Aquí vive mi registro clínico completo: diagnósticos, tratamiento, especialidades y documentos. Ordenado para mí, mi familia y cualquier profesional que lo necesite en segundos.</p>
        <div class="hero__actions">
          <a class="btn btn--primary" href="#registro">Explorar el registro {icon("arrow-down")}</a>
          <button type="button" class="btn btn--ghost" data-open-search>{icon("search")} Buscar en la historia</button>
        </div>
        <div class="hero__facts" aria-label="Resumen del registro">
          <div class="fact"><span class="fact__value">13</span><span class="fact__label">páginas</span></div>
          <div class="fact"><span class="fact__value">8</span><span class="fact__label">especialidades</span></div>
          <div class="fact"><span class="fact__value">{total_documents()}</span><span class="fact__label">documentos PDF</span></div>
          <div class="fact"><span class="fact__value">{len(AFECCIONES)}</span><span class="fact__label">diagnósticos</span></div>
        </div>
        <div class="hero__trust">
          <span>{icon("lock")} Acceso directo, sin cuentas</span>
          <span>{icon("shield")} Sin indexación</span>
          <span>{icon("check-circle")} WCAG 2.1 AA</span>
        </div>
        <span class="scroll-cue"><span class="scroll-cue__line" aria-hidden="true"></span> Sigue leyendo</span>
      </div>
      {art_frame(
        art,
        "Ilustración cálida de un amanecer, hojas y una ficha clínica",
        "Registro personal · 2026",
        chip("droplet", "Grupo sanguíneo", PERFIL["grupoSanguineo"], "tl")
        + chip("alert-triangle", "Alergia registrada", ALERGIAS[0]["sustancia"], "br"),
      )}
    </div>
  </header>

  <div class="marquee" aria-hidden="true">
    <div class="marquee__track">
      <div class="marquee__group">{marquee}</div>
      <div class="marquee__group">{marquee}</div>
    </div>
  </div>

  <section class="section" id="registro">
    <div class="shell">
      {section_head("Registro clínico", "01", 'Lo esencial,<br><em>sin vueltas.</em>', "Tres puertas de entrada al núcleo del registro: qué condiciones están en juego, qué estás tomando y qué dicen los exámenes.")}
      <div class="portal-grid">
        {''.join(portal_card(cat) for cat in registro)}
      </div>
      <div class="section__foot">
        <button type="button" class="link-arrow" data-open-index>Abrir el índice completo {icon("arrow-right")}</button>
      </div>
    </div>
  </section>

  <section class="section section--tint" id="especialidades">
    <div class="shell">
      {section_head("Especialidades médicas", "02", 'Ocho miradas,<br><em>una historia.</em>', "Cada especialidad tiene su capítulo, su evolución y sus documentos. Todo conectado, sin perder el hilo de lo que importa.")}
      <div class="chapters-grid">
        {''.join(chapter_card(cat, index * 45) for index, cat in enumerate(especialidades))}
      </div>
    </div>
  </section>

  <section class="section" id="emergencia">
    <div class="shell">
      <div class="emergency-banner" data-reveal>
        <img class="emergency-banner__art" src="assets/img/art/emergencia.svg" alt="" loading="lazy" width="1600" height="1100">
        <div>
          <p class="eyebrow">03 · Cuando importa</p>
          <h2 class="emergency-banner__title">Cuando cada segundo <em>cuenta.</em></h2>
          <p>Grupo sanguíneo, alergias, condiciones y contactos con llamada directa en una sola ficha. Sin menús, sin login, sin vueltas.</p>
          <div class="emergency-banner__chips">
            <span>{icon("droplet")} {esc(PERFIL['grupoSanguineo'])}</span>
            <span>{icon("alert-triangle")} Alergia a {esc(ALERGIAS[0]['sustancia'])}</span>
            <span>{icon("phone")} SAMU 131</span>
          </div>
          <div class="emergency-banner__actions">
            <a class="btn btn--coral" href="emergencia.html">{icon("phone-call")} Abrir ficha de emergencia</a>
            <a class="btn btn--ghost" href="{tel_href(PRIMARY_CONTACT['telefono'])}">{icon("phone")} Llamar al contacto principal</a>
          </div>
        </div>
        <div class="sos-medallion" aria-hidden="true">
          <div class="sos-medallion__text">
            <strong>131</strong>
            <span>SAMU · Chile</span>
            <small>Riesgo vital</small>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section section--panel" id="documentos">
    <div class="shell">
      {section_head("Archivo clínico", "04", 'Papeles que<br><em>acompañan.</em>', "Informes, recetas y exámenes descargables. Cada documento se puede leer antes de bajar y queda enlazado a su capítulo.")}
      <div class="doc-grid">
        {''.join(document_card(doc, show_category=True) for doc in recent_docs)}
      </div>
      <div class="section__foot">
        <button type="button" class="link-arrow" data-open-index>Ver todos los capítulos y documentos {icon("arrow-right")}</button>
      </div>
    </div>
  </section>

  <section class="section" id="principios">
    <div class="shell">
      {section_head("Cómo está pensado", "05", 'Cuidado en los<br><em>detalles.</em>', "Un registro personal debe ser legible, privado y útil incluso cuando quien lo abre no es su dueño. Estas son las reglas de la casa.")}
      <div class="principles">{principles}</div>
    </div>
  </section>

  <section class="section">
    <div class="shell">
      <div class="closing" data-reveal>
        <img class="closing__seal" src="assets/img/ui/sello.svg" alt="" width="200" height="200" aria-hidden="true">
        <h2>Una historia clínica<br><em>que se puede leer.</em></h2>
        <p>Si eres Roberto, encuentra lo que buscas. Si eres su familia o su equipo de salud, gracias por mirar con cuidado. Si es una urgencia, empieza por la ficha de emergencia.</p>
        <div class="closing__actions">
          <a class="btn btn--primary" href="emergencia.html">{icon("phone-call")} Ficha de emergencia</a>
          <button type="button" class="btn btn--ghost" data-open-index>{icon("book-open")} Ver todos los capítulos</button>
        </div>
        <p class="closing__meta">Actualizado {fecha_long(SITE['actualizado'])} · 13 páginas · {total_documents()} PDF descargables</p>
      </div>
    </div>
  </section>"""
    return render_page(
        slug="inicio",
        title=f"saludrcartes · Registro clínico personal de {PERFIL['nombre']}",
        description=SITE["descripcion"],
        accent="verde",
        art=art,
        main_html=main,
        print_title="Inicio",
    )


# ---------------------------------------------------------------------------
# Detail components
# ---------------------------------------------------------------------------
def breadcrumb(cat: dict) -> str:
    group = group_of(cat)
    anchor = "registro" if cat["grupo"] == "registro" else "especialidades"
    return f"""
        <nav class="breadcrumb" aria-label="Camino de navegación">
          <a href="index.html">{icon("home")} Inicio</a>
          <span class="breadcrumb__sep" aria-hidden="true">/</span>
          <a href="index.html#{anchor}">{esc(group['nombre'])}</a>
          <span class="breadcrumb__sep" aria-hidden="true">/</span>
          <span aria-current="page">{esc(cat['navLabel'])}</span>
        </nav>"""


def summary_chips(cat: dict, conditions: list[dict], docs: list[dict]) -> str:
    chips = [status_badge(cat["estado"])]
    if len(conditions) == 1 and conditions[0].get("cie10"):
        chips.append(f'<span class="status">CIE-10 {esc(conditions[0]["cie10"])}</span>')
    chips.append(f'<span class="status">{len(conditions)} condición{"es" if len(conditions) != 1 else ""}</span>')
    chips.append(f'<span class="status">{len(docs)} documento{"s" if len(docs) != 1 else ""}</span>')
    return "".join(chips)


def fact_item(label: str, value: str) -> str:
    return f'<div class="fact-item"><span class="fact-item__label">{esc(label)}</span><span class="fact-item__value">{value}</span></div>'


def summary_section(
    *,
    cat: dict,
    quote: str,
    facts: list[tuple[str, str]],
    conditions: list[dict],
    docs: list[dict],
    updated: str,
) -> str:
    return f"""
      <section class="content-section" id="resumen">
        <p class="section-label">Resumen</p>
        <div class="content-section__head">
          <div><h2>La historia <em>en breve.</em></h2></div>
          <span class="content-section__count">{icon("clock")} Actualizado {time_tag(updated)}</span>
        </div>
        <div class="summary-card">
          <p class="summary-card__quote">«{esc(quote)}»</p>
          <div class="summary-card__foot">{summary_chips(cat, conditions, docs)}</div>
        </div>
        <div class="fact-grid">{''.join(fact_item(label, value) for label, value in facts)}</div>
      </section>"""


def timeline(events: list[dict], label: str) -> str:
    if not events:
        return ""
    items = []
    for event in reversed(events):
        items.append(f"""
          <li class="timeline__item">
            <time class="timeline__date" datetime="{esc(event['fecha'])}">{fecha_short(event['fecha'])}<span>{event['fecha'][:4]}</span></time>
            <span class="timeline__dot" aria-hidden="true"></span>
            <div class="timeline__card">
              <h4 class="timeline__title">{esc(event['titulo'])}</h4>
              <p class="timeline__finding">{esc(event['hallazgo'])}</p>
              <p class="timeline__action"><strong>Acción</strong> {esc(event['accion'])}</p>
            </div>
          </li>""")
    return f'<ol class="timeline" aria-label="{esc(label)}">{"".join(items)}</ol>'


def condition_block(afeccion: dict, show_timeline: bool = True) -> str:
    meta = []
    if afeccion.get("cie10"):
        meta.append(f'<span>{icon("clipboard-pulse")} CIE-10 {esc(afeccion["cie10"])}</span>')
    meta.append(f'<span>{icon("calendar")} Desde {time_tag(afeccion["fecha_diagnostico"])}</span>')
    if afeccion.get("medico"):
        meta.append(f'<span>{icon("user")} {esc(afeccion["medico"])}</span>')
    if afeccion.get("centro"):
        meta.append(f'<span>{icon("building")} {esc(afeccion["centro"])}</span>')
    return f"""
        <article class="condition-block" id="{esc(afeccion['id'])}">
          <div class="condition-head">
            <div>
              <h3>{esc(afeccion['titulo'])}</h3>
              <p class="condition-summary">{esc(afeccion['resumen'] or afeccion['descripcion'])}</p>
            </div>
            {status_badge(afeccion['estado'])}
          </div>
          <div class="condition-meta">{''.join(meta)}</div>
          {timeline(afeccion['evolucion'], 'Evolución de ' + afeccion['titulo']) if show_timeline else ''}
        </article>"""


def notes_section(notes: list[str], updated: str, source: str = "") -> str:
    items = "".join(
        f'<li><span class="icon-wrap" aria-hidden="true">{icon("check")}</span><span>{esc(note)}</span></li>'
        for note in notes
    )
    source_text = source or "Registro personal"
    return f"""
      <section class="content-section" id="notas">
        <p class="section-label">Notas y cuidados</p>
        <div class="notes-card">
          <h2 class="notes-card__title">{icon("heart")} Para llevar</h2>
          <ul class="notes-list">{items}</ul>
          <p class="notes-card__foot">Última revisión: {time_tag(updated)} · {esc(source_text)}. Ante una duda, consulta con tu equipo de salud.</p>
        </div>
      </section>"""


def documents_section(docs: list[dict], title: str = "Documentos que respaldan esta historia") -> str:
    if not docs:
        return f"""
      <section class="content-section" id="documentos">
        <p class="section-label">Documentos</p>
        <div class="content-section__head">
          <div><h2>El respaldo, <em>a mano.</em></h2></div>
          <span class="content-section__count">{icon("file-text")} 0 documentos</span>
        </div>
        <p>Los documentos de esta categoría se encuentran en los capítulos de cada especialidad. Usa el índice para llegar a ellos.</p>
      </section>"""
    return f"""
      <section class="content-section" id="documentos">
        <p class="section-label">Documentos</p>
        <div class="content-section__head">
          <div><h2>{title.split(',')[0]}, <em>{title.split(',')[1].strip() if ',' in title else 'a mano.'}</em></h2></div>
          <span class="content-section__count">{icon("folder")} {len(docs)} archivo{'s' if len(docs) != 1 else ''}</span>
        </div>
        <div class="doc-grid">{''.join(document_card(doc) for doc in docs)}</div>
        <p class="editorial-note">{icon("info")} <span><strong>Antes de descargar:</strong> los documentos son informes de ejemplo. Se abren en una vista previa y conservan su nombre original para que puedas identificarlos fuera del sitio.</span></p>
      </section>"""


def related_section(ids: list[str]) -> str:
    cats = related_categories(ids)
    if not cats:
        return ""
    cards = "".join(
        f"""
        <a class="related-card accent-{cat['acento']}" href="{esc(cat['url'])}">
          <span class="related-card__media"><img src="{esc(cat['arte'])}" alt="" loading="lazy" width="1600" height="1100"></span>
          <span class="related-card__body">
            <span class="related-card__kicker">{esc(group_of(cat)['nombre'])}</span>
            <h3>{esc(cat['navLabel'])}</h3>
            <span class="related-card__cta">Ver capítulo {icon("arrow-up-right")}</span>
          </span>
        </a>"""
        for cat in cats[:3]
    )
    return f"""
      <section class="content-section" id="relacionado">
        <p class="section-label">Sigue el hilo</p>
        <div class="content-section__head">
          <div><h2>También se <em>conecta.</em></h2></div>
        </div>
        <div class="related-grid">{cards}</div>
      </section>"""


def chapter_nav(cat: dict) -> str:
    order = [{"url": "index.html", "navLabel": "Inicio", "nombre": "Inicio", "numero": "00"}] + CATEGORIAS_ORDER
    index = next((i for i, item in enumerate(order) if item.get("url") == cat["url"]), None)
    if index is None:
        return ""
    previous = order[index - 1] if index > 0 else None
    following = order[index + 1] if index + 1 < len(order) else None
    parts = []
    if previous:
        parts.append(
            f'<a class="chapter-nav__link" href="{esc(previous["url"])}">'
            f'<span class="chapter-nav__icon">{icon("arrow-left")}</span>'
            f'<span class="chapter-nav__text"><small>Anterior</small><strong>{esc(previous["navLabel"])}</strong></span></a>'
        )
    if following:
        parts.append(
            f'<a class="chapter-nav__link chapter-nav__link--next" href="{esc(following["url"])}">'
            f'<span class="chapter-nav__text"><small>Siguiente</small><strong>{esc(following["navLabel"])}</strong></span>'
            f'<span class="chapter-nav__icon">{icon("arrow-right")}</span></a>'
        )
    if not parts:
        return ""
    return f'<nav class="chapter-nav" aria-label="Capítulos anterior y siguiente">{"".join(parts)}</nav>'


def rail_sos() -> str:
    return f"""
        <div class="rail__sos">
          <span class="rail__sos-icon">{icon("phone-call")}</span>
          <h2>¿Es una urgencia?</h2>
          <p>La ficha de emergencia reúne lo crítico y los teléfonos directos.</p>
          <a href="emergencia.html">{icon("arrow-up-right")} Abrir ficha</a>
        </div>"""


def rail(links: list[tuple[str, str]]) -> str:
    nav = "".join(
        f'<a class="rail__link{" is-active" if index == 0 else ""}" href="#{esc(target)}" data-spy>{icon("chevron-right")}{esc(label)}</a>'
        for index, (target, label) in enumerate(links)
    )
    return f"""
      <aside class="rail" aria-label="En esta página">
        <div>
          <p class="rail__label">En esta página</p>
          <nav class="rail__nav">{nav}</nav>
        </div>
        {rail_sos()}
      </aside>"""


def detail_hero(cat: dict, conditions: list[dict], docs: list[dict]) -> str:
    docs_count = len(docs)
    conditions_count = len(conditions)
    return f"""
  <header class="page-hero">
    <div class="shell page-hero__grid">
      <div class="page-hero__copy" data-reveal>
        {breadcrumb(cat)}
        <p class="eyebrow">{esc(group_of(cat)['nombre'])} <span class="eyebrow__badge">{esc(cat['numero'])} · {esc(cat['estado'])}</span></p>
        <h1>{esc(cat['nombre'])}<span class="accent-dot">.</span></h1>
        <p class="hero-line">{esc(cat['heroLine'])}</p>
        <p class="lead">{esc(cat['resumen'])}</p>
        <div class="page-hero__actions">
          <button type="button" class="btn btn--primary" data-print>{icon("print")} Imprimir esta página</button>
          <a class="btn btn--ghost" href="#documentos">{icon("file-text")} Ver documentos</a>
        </div>
        <div class="hero-facts" aria-label="Datos de la página">
          <div class="fact"><span class="fact__value">{conditions_count}</span><span class="fact__label">condición{'es' if conditions_count != 1 else ''}</span></div>
          <div class="fact"><span class="fact__value">{docs_count}</span><span class="fact__label">documento{'s' if docs_count != 1 else ''}</span></div>
          <div class="fact"><span class="fact__value">{fecha_short(cat['actualizado'])}</span><span class="fact__label">actualización</span></div>
        </div>
      </div>
      {art_frame(cat['arte'], f"Ilustración de {cat['nombre']}", cat['caption'])}
    </div>
  </header>"""


# ---------------------------------------------------------------------------
# Page builders
# ---------------------------------------------------------------------------
def build_diagnosticos() -> str:
    cat = CATEGORIAS["diagnosticos"]
    cats_conditions = conditions_for("diagnosticos")
    all_docs = sorted(DOCS, key=lambda doc: doc["fecha"], reverse=True)
    featured_docs = all_docs[:6]
    active = [item for item in AFECCIONES if item["tipo"] == "activa"]
    historical = [item for item in AFECCIONES if item["tipo"] == "historica"]
    follow = [item for item in AFECCIONES if "seguimiento" in item["estado"].lower() or "tratamiento" in item["estado"].lower()]
    rows = []
    for item in sorted(AFECCIONES, key=lambda value: (value["tipo"] != "activa", value["fecha_diagnostico"]), reverse=False):
        item_cat = CATEGORIAS[item["categoria_id"]]
        states = [item["tipo"]]
        if "seguimiento" in item["estado"].lower():
            states.append("seguimiento")
        if "tratamiento" in item["estado"].lower():
            states.append("tratamiento")
        if item["tipo"] == "historica":
            states.append("resuelta")
        rows.append(f"""
          <tr data-states="{','.join(states)}">
            <td data-label="Condición">
              <span class="cell-title">{esc(item['titulo'])}</span>
              <span class="cell-muted">{esc(item['descripcion'])}</span>
            </td>
            <td data-label="CIE-10" class="cell-mono">{esc(item.get('cie10') or '—')}</td>
            <td data-label="Estado">{status_badge(item['estado'])}</td>
            <td data-label="Desde" class="cell-mono">{time_tag(item['fecha_diagnostico'])}</td>
            <td data-label="Profesional">{esc(item['medico'])}<br><a class="cell-link" href="{esc(item_cat['url'])}">{esc(item_cat['navLabel'])}</a></td>
          </tr>""")
    fact_items = [
        ("Condiciones registradas", f"{len(AFECCIONES)}"),
        ("Activas", f"{len(active)}"),
        ("En seguimiento o tratamiento", f"{len(follow)}"),
        ("Históricas / resueltas", f"{len(historical)}"),
        ("Documentos clínicos", f"{len(all_docs)}"),
        ("Última actualización", time_tag(cat["actualizado"])),
    ]
    conditions_html = "".join(condition_block(item) for item in cats_conditions)
    notes = unique(
        [note for item in cats_conditions for note in item["notas"]]
        + CRITICO["notas"]
    )
    main = f"""
  {detail_hero(cat, AFECCIONES, all_docs)}
  <div class="shell detail">
    {rail([("resumen", "Resumen"), ("condiciones", "Todas las condiciones"), ("seguimiento", "Seguimiento"), ("documentos", "Documentos"), ("notas", "Notas"), ("relacionado", "Relacionado")])}
    <div class="detail-content">
      {summary_section(cat=cat, quote=cat["resumen"], facts=fact_items, conditions=AFECCIONES, docs=all_docs, updated=cat["actualizado"])}

      <section class="content-section" id="condiciones">
        <p class="section-label">Mapa clínico</p>
        <div class="content-section__head">
          <div><h2>Todas las <em>condiciones.</em></h2><p>Activas e históricas, con su código CIE-10 y el profesional que las respalda.</p></div>
          <span class="content-section__count" data-filter-count>{len(AFECCIONES)} registros</span>
        </div>
        <div class="filter-bar" role="group" aria-label="Filtrar diagnósticos">
          <button type="button" class="filter-btn" data-filter="all" aria-pressed="true">Todas · {len(AFECCIONES)}</button>
          <button type="button" class="filter-btn" data-filter="activa" aria-pressed="false">Activas · {len(active)}</button>
          <button type="button" class="filter-btn" data-filter="seguimiento" aria-pressed="false">En seguimiento · {len(follow)}</button>
          <button type="button" class="filter-btn" data-filter="historica" aria-pressed="false">Históricas · {len(historical)}</button>
        </div>
        <div class="table-card">
          <div class="table-scroll">
            <table class="data-table">
              <thead><tr><th>Condición</th><th>CIE-10</th><th>Estado</th><th>Desde</th><th>Profesional</th></tr></thead>
              <tbody>{''.join(rows)}</tbody>
            </table>
          </div>
          <div class="table-card__foot">Los filtros se aplican sin recargar la página. Cada condición enlaza al capítulo donde vive su evolución completa.</div>
        </div>
        <div class="editorial-note">{icon("info")} <span><strong>Lectura rápida:</strong> “Activa” significa que sigue en control; “histórica” que ya está resuelta. El estado clínico se muestra siempre con texto, no solo con color.</span></div>
      </section>

      <section class="content-section" id="seguimiento">
        <p class="section-label">Seguimiento</p>
        <div class="content-section__head">
          <div><h2>Las que siguen <em>en el mapa.</em></h2></div>
          <span class="content-section__count">{icon("activity")} {len(cats_conditions)} fichas</span>
        </div>
        {conditions_html}
      </section>

      {documents_section(featured_docs, "Documentos clave, a mano")}
      {notes_section(notes, cat['actualizado'], 'Diagnósticos y notas generales')}
      {related_section(["cardiologia", "laboratorio", "medicamentos"])}
      {chapter_nav(cat)}
    </div>
  </div>"""
    return render_page(
        slug=cat["slug"],
        title=f"{cat['metaTitle']} · saludrcartes",
        description=f"Diagnósticos de {PERFIL['nombre']} con código CIE-10, estado, médico tratante, evolución y documentos descargables.",
        accent=cat["acento"],
        art=cat["arte"],
        main_html=main,
        extra_css=("assets/css/detail.css",),
        print_title=cat["navLabel"],
    )


def build_medicamentos() -> str:
    cat = CATEGORIAS["medicamentos"]
    condition = conditions_for("medicamentos")[0]
    docs = docs_for("medicamentos")
    active_meds = [med for med in MEDICAMENTOS if med["activo"]]
    inactive_meds = [med for med in MEDICAMENTOS if not med["activo"]]
    active_cards = "".join(medication_card(med) for med in active_meds)
    inactive_cards = "".join(medication_card(med) for med in inactive_meds)
    allergy_cards = "".join(allergy_card(allergy) for allergy in ALERGIAS)
    primary_allergy = ALERGIAS[0]
    fact_items = [
        ("Medicamentos activos", f"{len(active_meds)}"),
        ("Alergias registradas", f"{len(ALERGIAS)}"),
        ("Receta vigente", time_tag("2026-10-20")),
        ("Profesional", esc(condition["medico"])),
        ("Centro", esc(condition["centro"])),
        ("Actualizado", time_tag(cat["actualizado"])),
    ]
    med_timeline = timeline(condition["evolucion"], "Historial del tratamiento")
    main = f"""
  {detail_hero(cat, [condition], docs)}
  <div class="shell detail">
    {rail([("resumen", "Resumen"), ("alergias", "Alergias"), ("medicamentos", "Medicamentos"), ("documentos", "Documentos"), ("notas", "Notas"), ("relacionado", "Relacionado")])}
    <div class="detail-content">
      {summary_section(cat=cat, quote=cat["resumen"], facts=fact_items, conditions=[condition], docs=docs, updated=cat["actualizado"])}

      <section class="content-section" id="alergias">
        <p class="section-label">Seguridad primero</p>
        <div class="content-section__head">
          <div><h2>Alergias <em>registradas.</em></h2><p>Información que debe decirse en voz alta antes de cualquier receta.</p></div>
          <span class="content-section__count">{icon("alert-triangle")} {len(ALERGIAS)} alertas</span>
        </div>
        <div class="allergy-alert">
          <span class="allergy-alert__icon">{icon("alert-triangle")}</span>
          <div>
            <h3>{esc(primary_allergy['sustancia'])} · {esc(primary_allergy['severidad'])}</h3>
            <p>{esc(primary_allergy['notas'])} Reacción registrada: {esc(primary_allergy['reaccion'])}.</p>
          </div>
        </div>
        <div class="allergy-grid">{allergy_cards}</div>
      </section>

      <section class="content-section" id="medicamentos">
        <p class="section-label">Tratamiento</p>
        <div class="content-section__head">
          <div><h2>Lo que está <em>activo.</em></h2><p>Dosis, frecuencia, vía y precauciones. No suspender sin indicación profesional.</p></div>
          <span class="content-section__count">{icon("pill")} {len(active_meds)} activos</span>
        </div>
        <div class="med-grid">{active_cards}</div>
        {f'<h3 class="subsection-title">Histórico</h3><div class="med-grid">{inactive_cards}</div>' if inactive_cards else ''}
        <h3 class="subsection-title">Historial del tratamiento</h3>
        {med_timeline}
      </section>

      {documents_section(docs, "La receta, a mano")}
      {notes_section(unique(condition['notas'] + CRITICO['notas']), cat['actualizado'], 'Tratamiento y alergias')}
      {related_section(condition['relacionados'])}
      {chapter_nav(cat)}
    </div>
  </div>"""
    return render_page(
        slug=cat["slug"],
        title=f"{cat['metaTitle']} · saludrcartes",
        description=f"Medicamentos activos, dosis, horarios, alergias y receta descargable de {PERFIL['nombre']}.",
        accent=cat["acento"],
        art=cat["arte"],
        main_html=main,
        extra_css=("assets/css/detail.css",),
        print_title=cat["navLabel"],
    )


def medication_card(med: dict) -> str:
    active = med["activo"]
    note = med.get("notas") or ""
    return f"""
      <article class="med-card{' med-card--off' if not active else ''}">
        <div class="med-card__top">
          <span class="med-card__icon">{icon("pill")}</span>
          <span class="med-card__status"><span class="status__dot" aria-hidden="true"></span>{'Activo' if active else 'Suspendido'}</span>
        </div>
        <h3>{esc(med['nombre'])}</h3>
        <p class="med-card__dose">{esc(med['dosis'])} · {esc(med['via'])}</p>
        <dl class="med-card__list">
          <div><dt>Frecuencia</dt><dd>{esc(med['frecuencia'])}</dd></div>
          <div><dt>Horario</dt><dd>{esc(med['horario'])}</dd></div>
          <div><dt>Indicación</dt><dd>{esc(med['indicacion'])}</dd></div>
          <div><dt>Máximo</dt><dd>{esc(med['maximo'])}</dd></div>
          <div><dt>Desde</dt><dd>{time_tag(med['inicio'])}</dd></div>
          {f'<div><dt>Hasta</dt><dd>{time_tag(med["fin"])}</dd></div>' if med.get("fin") else ''}
        </dl>
        {f'<p class="med-card__note">{esc(note)}</p>' if note else ''}
      </article>"""


def allergy_card(allergy: dict) -> str:
    severity_class = "severity--moderada" if "moderada" in allergy["severidad"].lower() else "severity--leve"
    return f"""
      <article class="allergy-card">
        <div class="allergy-card__top">
          <h3>{esc(allergy['sustancia'])}</h3>
          <span class="severity {severity_class}">{icon("alert-circle")} {esc(allergy['severidad'])}</span>
        </div>
        <p><strong>Reacción:</strong> {esc(allergy['reaccion'])}</p>
        <small>{esc(allergy['notas'])} · Registrada el {fecha_short(allergy['fecha_registro'])}</small>
      </article>"""


def build_laboratorio() -> str:
    cat = CATEGORIAS["laboratorio"]
    condition = conditions_for("laboratorio")[0]
    docs = docs_for("laboratorio")
    out_of_range = [row for row in LABORATORIO if row["estado"] != "normal"]
    panels: OrderedDict[str, list[dict]] = OrderedDict()
    for row in LABORATORIO:
        panels.setdefault(row["panel"], []).append(row)
    panel_html = "".join(lab_panel(name, rows) for name, rows in panels.items())
    out_list = ", ".join(f"{row['examen']} {row['resultado']} {row['unidad']}" for row in out_of_range)
    fact_items = [
        ("Resultados", f"{len(LABORATORIO)}"),
        ("Fuera de rango", f"{len(out_of_range)}"),
        ("Muestra", time_tag("2026-01-15")),
        ("Paneles", f"{len(panels)}"),
        ("Profesional", esc(condition["medico"])),
        ("Actualizado", time_tag(cat["actualizado"])),
    ]
    main = f"""
  {detail_hero(cat, [condition], docs)}
  <div class="shell detail">
    {rail([("resumen", "Resumen"), ("resultados", "Resultados"), ("evolucion", "Evolución"), ("documentos", "Documentos"), ("notas", "Notas"), ("relacionado", "Relacionado")])}
    <div class="detail-content">
      {summary_section(cat=cat, quote=cat["resumen"], facts=fact_items, conditions=[condition], docs=docs, updated=cat["actualizado"])}

      <section class="content-section" id="resultados">
        <p class="section-label">Resultados</p>
        <div class="content-section__head">
          <div><h2>Los números, <em>en contexto.</em></h2><p>Una lectura por panel, con rango de referencia y estado visible.</p></div>
          <span class="content-section__count">{icon("flask")} {len(LABORATORIO)} exámenes</span>
        </div>
        <div class="lab-callout">
          <span class="lab-callout__icon">{icon("alert-triangle")}</span>
          <div>
            <h3>{len(out_of_range)} resultados fuera de rango</h3>
            <p>{esc(out_list)}. Ninguno es una urgencia por sí solo: se interpretan con el informe completo y el control médico.</p>
          </div>
        </div>
        {panel_html}
        <p class="editorial-note">{icon("info")} <span><strong>Cómo leer:</strong> “Alto” y “bajo” se refieren al rango de referencia del laboratorio, no a un diagnóstico. La decisión clínica siempre es del profesional tratante.</span></p>
      </section>

      <section class="content-section" id="evolucion">
        <p class="section-label">Evolución</p>
        <div class="content-section__head">
          <div><h2>El control, <em>en el tiempo.</em></h2></div>
          <span class="content-section__count">{icon("activity")} {len(condition['evolucion'])} hitos</span>
        </div>
        {timeline(condition['evolucion'], 'Evolución del control de laboratorio')}
      </section>

      {documents_section(docs, "Los informes, completos")}
      {notes_section(condition['notas'], cat['actualizado'], 'Lectura de laboratorio')}
      {related_section(condition['relacionados'])}
      {chapter_nav(cat)}
    </div>
  </div>"""
    return render_page(
        slug=cat["slug"],
        title=f"{cat['metaTitle']} · saludrcartes",
        description=f"Resultados de laboratorio de {PERFIL['nombre']} con fecha, rango de referencia, lectura rápida y documentos descargables.",
        accent=cat["acento"],
        art=cat["arte"],
        main_html=main,
        extra_css=("assets/css/detail.css",),
        print_title=cat["navLabel"],
    )


def lab_panel(name: str, rows: list[dict]) -> str:
    body = []
    for row in rows:
        state = row["estado"]
        state_label = {"normal": "En rango", "alto": "Alto", "bajo": "Bajo"}.get(state, state.title())
        state_class = {"normal": "result-status--normal", "alto": "result-status--alto", "bajo": "result-status--bajo"}.get(state, "result-status--normal")
        flag_class = {"alto": "result-flag--alto", "bajo": "result-flag--bajo"}.get(state, "")
        body.append(f"""
          <tr>
            <td data-label="Examen"><span class="cell-title">{esc(row['examen'])}</span></td>
            <td data-label="Resultado"><span class="cell-mono result-flag {flag_class}">{esc(row['resultado'])}</span> <span class="cell-muted">{esc(row['unidad'])}</span></td>
            <td data-label="Referencia" class="cell-mono">{esc(row['referencia'])}</td>
            <td data-label="Estado"><span class="result-status {state_class}">{icon("check-circle" if state == 'normal' else "alert-circle")} {esc(state_label)}</span></td>
          </tr>""")
    return f"""
        <div class="lab-panel table-card">
          <div class="table-card__head"><div><h3>{esc(name)}</h3><p>Muestra del {fecha_short('2026-01-15')}</p></div></div>
          <div class="table-scroll">
            <table class="data-table">
              <thead><tr><th>Examen</th><th>Resultado</th><th>Referencia</th><th>Estado</th></tr></thead>
              <tbody>{''.join(body)}</tbody>
            </table>
          </div>
        </div>"""


def build_especialidad(cat: dict) -> str:
    conditions = conditions_for(cat["id"])
    docs = docs_for(cat["id"])
    doctors = unique(item["medico"] for item in conditions)
    centers = unique(item["centro"] for item in conditions)
    codes = unique(item.get("cie10") for item in conditions if item.get("cie10"))
    earliest = min((item["fecha_diagnostico"] for item in conditions), default=cat["actualizado"])
    latest = max((item["actualizado"] for item in conditions), default=cat["actualizado"])
    fact_items = [
        ("Estado actual", status_badge(cat["estado"])),
        ("Condiciones", f"{len(conditions)}"),
        ("Desde", time_tag(earliest)),
        ("Última actualización", time_tag(latest)),
        ("Profesional", "<br>".join(esc(name) for name in doctors)),
        ("Centro", "<br>".join(esc(name) for name in centers)),
        ("CIE-10", ", ".join(esc(code) for code in codes) or "—"),
        ("Documentos", f"{len(docs)}"),
    ]
    conditions_html = "".join(condition_block(item) for item in conditions)
    notes = unique(note for item in conditions for note in item["notas"])
    related = unique(item for condition in conditions for item in condition["relacionados"])
    related = [item for item in related if item != cat["id"]][:3]
    main = f"""
  {detail_hero(cat, conditions, docs)}
  <div class="shell detail">
    {rail([("resumen", "Resumen"), ("condiciones", "Condiciones"), ("documentos", "Documentos"), ("notas", "Notas"), ("relacionado", "Relacionado")])}
    <div class="detail-content">
      {summary_section(cat=cat, quote=cat["resumen"], facts=fact_items, conditions=conditions, docs=docs, updated=latest)}

      <section class="content-section" id="condiciones">
        <p class="section-label">Clínica</p>
        <div class="content-section__head">
          <div><h2>Qué estamos <em>tratando.</em></h2><p>La evolución se lee de lo más reciente a lo más antiguo.</p></div>
          <span class="content-section__count">{icon("activity")} {len(conditions)} ficha{'s' if len(conditions) != 1 else ''}</span>
        </div>
        {conditions_html}
      </section>

      {documents_section(docs, "El respaldo, a mano")}
      {notes_section(notes, latest, cat["navLabel"])}
      {related_section(related)}
      {chapter_nav(cat)}
    </div>
  </div>"""
    return render_page(
        slug=cat["slug"],
        title=f"{cat['metaTitle']} · saludrcartes",
        description=f"{cat['descripcion']} Registro clínico de {PERFIL['nombre']} con evolución, notas y documentos descargables.",
        accent=cat["acento"],
        art=cat["arte"],
        main_html=main,
        extra_css=("assets/css/detail.css",),
        print_title=cat["navLabel"],
    )


# ---------------------------------------------------------------------------
# Emergency
# ---------------------------------------------------------------------------
def emergency_page() -> str:
    cat = CATEGORIAS["emergencia"]
    call = tel_href(PRIMARY_CONTACT["telefono"])
    private_cards = "".join(contact_card(contact) for contact in PRIVATE_CONTACTS)
    public_cards = "".join(
        f'<a class="public-number" href="{tel_href(contact["telefono"])}"><span>{esc(contact["nombre"])}<br>{esc(contact["nota"])}</span><strong>{esc(contact["telefono"])}</strong></a>'
        for contact in PUBLIC_CONTACTS
    )
    meds_list = "".join(f'<li>{icon("pill")}<span>{esc(med)}</span></li>' for med in CRITICO["medicamentos"])
    notes_list = "".join(f'<li>{icon("check")}<span>{esc(note)}</span></li>' for note in CRITICO["notas"])
    conditions_list = "".join(f'<li>{icon("heart-pulse")} {esc(item)}</li>' for item in CRITICO["condiciones"])
    allergy_items = "".join(
        f'<li>{icon("alert-triangle")} {esc(item["sustancia"])} · {esc(item["severidad"])}: {esc(item["reaccion"])}</li>'
        for item in CRITICO["alergias"]
    )
    crit_meds = "".join(f'<li>{icon("pill")} {esc(med)}</li>' for med in CRITICO["medicamentos"])
    main = f"""
  <section class="ep-hero">
    <div class="shell">
      <div class="ep-alert">
        <span>{icon("lock")} Ficha pública de emergencia</span>
        <span>{icon("check-circle")} No requiere inicio de sesión</span>
      </div>
      <div class="ep-hero__grid">
        <div data-reveal>
          <p class="eyebrow">Emergencia · capítulo 12</p>
          <h1>Todo lo crítico,<br><em>al instante.</em></h1>
          <p class="lead">Grupo sanguíneo, alergias, condiciones, medicamentos y contactos en una sola pantalla. Pensada para leer sin lentes, llamar con un toque y compartir con personal de salud.</p>
          <div class="ep-actions">
            <a class="btn btn--coral" href="{call}">{icon("phone-call")} Llamar al contacto principal</a>
            <a class="btn btn--gold" href="{esc(EMERGENCY_DOC['archivo'])}" download>{icon("download")} Descargar ficha PDF</a>
            <button type="button" class="btn btn--ghost" data-print>{icon("print")} Imprimir</button>
          </div>
          <p class="ep-note">{icon("info")} Ante riesgo vital, llama primero al <strong>131</strong>. Esta ficha no reemplaza la evaluación médica.</p>
        </div>
        <div class="critical-panel" data-reveal>
          <div class="critical-panel__head">
            <span>{icon("alert-triangle")} Información crítica</span>
            <small>Actualizada {fecha_short(CRITICO['actualizado'])}</small>
          </div>
          <div class="critical-panel__blood">
            <strong>{esc(PERFIL['grupoSanguineo'])}</strong>
            <span>Grupo<br>sanguíneo</span>
          </div>
          <div class="critical-block">
            <h2>{icon("alert-circle")} Alergias</h2>
            <ul>{allergy_items}</ul>
          </div>
          <div class="critical-block">
            <h2>{icon("heart-pulse")} Condiciones</h2>
            <ul>{conditions_list}</ul>
          </div>
          <div class="critical-block">
            <h2>{icon("pill")} Medicamentos</h2>
            <ul>{crit_meds}</ul>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="ep-section" id="contactos">
    <div class="shell">
      <div class="ep-section__head" data-reveal>
        <div>
          <p class="eyebrow">Contactos</p>
          <h2 class="ep-title">Una llamada, <em>sin buscar.</em></h2>
        </div>
        <p>Primero el círculo cercano y el equipo tratante. A la derecha, los números públicos de emergencia en Chile.</p>
      </div>
      <div class="contact-grid">
        <div class="contact-list">{private_cards}</div>
        <div class="ep-public">
          <h3>{icon("phone")} Números públicos</h3>
          <p>Emergencias en Chile · llamada directa</p>
          <div class="public-grid">{public_cards}</div>
        </div>
      </div>
    </div>
  </section>

  <section class="ep-section" id="indicaciones">
    <div class="shell">
      <div class="ep-section__head" data-reveal>
        <div>
          <p class="eyebrow">Indicaciones</p>
          <h2 class="ep-title">Lo que hay que <em>saber.</em></h2>
        </div>
        <p>Medicamentos vigentes y notas para quien acompañe la atención.</p>
      </div>
      <div class="ep-info-grid">
        <div class="ep-panel" data-reveal>
          <h3 class="ep-panel__title">{icon("pill")} Medicamentos actuales</h3>
          <ul>{meds_list}</ul>
          <p class="ep-panel__note">Dosis registradas en el capítulo de medicamentos. Confirmar con la receta vigente.</p>
        </div>
        <div class="ep-panel" data-reveal>
          <h3 class="ep-panel__title">{icon("heart")} Notas para la atención</h3>
          <ul>{notes_list}</ul>
          <p class="ep-panel__note">Datos de contacto de ejemplo: reemplazar por teléfonos reales antes de usar esta ficha.</p>
        </div>
      </div>
      <div class="ep-panel" style="margin-top:.9rem" data-reveal>
        <h3 class="ep-panel__title">{icon("file-text")} Ficha de emergencia imprimible</h3>
        <p style="margin-top:.45rem;color:rgba(255,248,240,.62);font-size:.84rem">Una hoja con diagnósticos, alergias, medicamentos y contactos. Descárgala o imprímela para llevar en la billetera o el teléfono.</p>
        <div class="ep-ficha-actions">
          <a class="btn btn--gold" href="{esc(EMERGENCY_DOC['archivo'])}" download>{icon("download")} Descargar PDF</a>
          <button type="button" class="btn btn--ghost" data-print>{icon("print")} Imprimir ficha</button>
          <a class="btn btn--ghost" href="medicamentos.html">{icon("pill")} Ver medicamentos</a>
        </div>
      </div>
    </div>
  </section>

  <div class="ep-sticky" aria-label="Acciones rápidas de emergencia">
    <a class="btn btn--coral" href="{call}">{icon("phone-call")} Llamar</a>
    <a class="btn btn--gold" href="{esc(EMERGENCY_DOC['archivo'])}" download>{icon("download")} Ficha</a>
  </div>"""
    return render_page(
        slug=cat["slug"],
        title=f"Emergencia · {PERFIL['nombre']} · saludrcartes",
        description=f"Ficha pública de emergencia de {PERFIL['nombre']}: grupo sanguíneo, alergias, condiciones, medicamentos y contactos con llamada directa.",
        accent="coral",
        art=cat["arte"],
        main_html=main,
        extra_css=("assets/css/emergency.css",),
        emergency=True,
        footer_html=emergency_footer(),
        print_title="Ficha de emergencia",
    )


def contact_card(contact: dict) -> str:
    primary = " contact-card--primary" if contact.get("principal") else ""
    icon_name = contact.get("icono") or "phone"
    return f"""
        <article class="contact-card{primary}">
          <span class="contact-card__icon">{icon(icon_name)}</span>
          <div class="contact-card__body">
            <span class="contact-card__relation">{esc(contact['relacion'])}</span>
            <h3>{esc(contact['nombre'])}</h3>
            <span class="contact-card__phone">{esc(contact['telefono'])}</span>
            <span class="contact-card__nota">{esc(contact['nota'])}</span>
          </div>
          <a class="contact-card__call" href="{tel_href(contact['telefono'])}">{icon("phone")} Llamar</a>
        </article>"""


# ---------------------------------------------------------------------------
# 404
# ---------------------------------------------------------------------------
def not_found_page() -> str:
    cat = CATEGORIAS["diagnosticos"]
    main = f"""
  <section class="hero" style="min-height:70vh;display:flex;align-items:center">
    <div class="shell hero__grid">
      <div class="hero__copy" data-reveal>
        <p class="eyebrow">Error 404 <span class="eyebrow__badge">Fuera del índice</span></p>
        <h1 class="display"><span class="line">Esta página</span><span class="line"><em>no está</em></span><span class="line">en la historia<span class="accent-dot">.</span></span></h1>
        <p class="lead">Puede que el enlace haya cambiado o que el capítulo todavía no exista. Vuelve al inicio o abre el índice completo.</p>
        <div class="hero__actions">
          <a class="btn btn--primary" href="index.html">{icon("home")} Volver al inicio</a>
          <button type="button" class="btn btn--ghost" data-open-index>{icon("book-open")} Abrir el índice</button>
        </div>
      </div>
      {art_frame(cat['arte'], 'Ilustración de una ficha clínica', 'Página no encontrada')}
    </div>
  </section>"""
    return render_page(
        slug="404",
        title="Página no encontrada · saludrcartes",
        description="La página solicitada no existe en el registro clínico.",
        accent="verde",
        art="assets/img/art/inicio.svg",
        main_html=main,
        print_title="Página no encontrada",
    )


# ---------------------------------------------------------------------------
# Generated assets
# ---------------------------------------------------------------------------
def build_search_index() -> str:
    items = []
    items.append({
        "title": "Inicio",
        "group": "Portada",
        "description": "La historia clínica completa, con acceso a los doce capítulos.",
        "keywords": "inicio portada saludrcartes roberto registro clinico",
        "url": "index.html",
        "number": "00",
        "featured": True,
    })
    for cat in CATEGORIAS_ORDER:
        items.append({
            "title": cat["navLabel"],
            "group": group_of(cat)["nombre"],
            "description": cat["descripcion"],
            "keywords": cat["keywords"],
            "url": cat["url"],
            "number": cat["numero"],
            "featured": cat["orden"] <= 6,
        })
    for condition in AFECCIONES:
        cat = CATEGORIAS[condition["categoria_id"]]
        category_has_condition_anchor = cat["grupo"] in ("registro", "especialidades") and cat["id"] not in ("medicamentos", "laboratorio")
        items.append({
            "title": condition["titulo"],
            "group": f"Diagnóstico · CIE-10 {condition.get('cie10') or 's/c'}",
            "description": f"{condition['estado']} · {condition['especialidad']} · {condition['medico']}",
            "keywords": f"{condition['descripcion']} {condition['especialidad']} {condition['medico']}",
            "url": f"{cat['url']}#{condition['id']}" if category_has_condition_anchor else cat["url"],
            "number": condition.get("cie10") or cat["numero"],
            "featured": False,
        })
    for doc in DOCS_ALL:
        cat = CATEGORIAS.get(doc["categoria_id"])
        items.append({
            "title": doc["nombre"],
            "group": f"Documento PDF · {fecha_short(doc['fecha'])}",
            "description": doc["descripcion"],
            "keywords": f"{doc['nombre']} {doc['descripcion']} {cat['navLabel'] if cat else 'emergencia'} pdf documento",
            "url": doc["archivo"],
            "number": "PDF",
            "featured": False,
        })
    payload = json.dumps(items, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return "/* Generado por tools/build_site.py — no editar a mano. */\nwindow.SALUD_BUSQUEDA = " + payload + ";\n"


def build_manifest() -> str:
    data = {
        "name": "saludrcartes · Registro clínico personal",
        "short_name": "saludrcartes",
        "description": (
            "Registro clínico personal de Roberto Carlos Cartes Jiménez, "
            "con ficha pública de emergencia."
        ),
        "lang": "es-CL",
        "dir": "ltr",
        "start_url": "./index.html",
        "scope": "./",
        "display": "standalone",
        "orientation": "portrait-primary",
        "background_color": "#FFF8F0",
        "theme_color": "#FFF8F0",
        "categories": ["health", "medical", "productivity"],
        "icons": [
            {"src": "assets/img/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "assets/img/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "assets/img/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "shortcuts": [
            {
                "name": "Ficha de emergencia",
                "short_name": "Emergencia",
                "description": "Abrir la ficha pública con información crítica y contactos directos.",
                "url": "./emergencia.html",
                "icons": [
                    {"src": "assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"}
                ],
            }
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def build_headers() -> str:
    return """/*
  Content-Security-Policy: default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'self'; form-action 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; frame-src 'self'; connect-src 'self'; upgrade-insecure-requests
  X-Frame-Options: SAMEORIGIN
  X-Content-Type-Options: nosniff
  Referrer-Policy: no-referrer
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()
  Cross-Origin-Opener-Policy: same-origin
  Cross-Origin-Resource-Policy: same-origin
  Strict-Transport-Security: max-age=31536000; includeSubDomains

/*.html
  Cache-Control: no-store, max-age=0
  X-Robots-Tag: noindex, nofollow, noarchive, nosnippet

/assets/js/*.js
  Cache-Control: public, max-age=3600

/assets/css/*.css
  Cache-Control: public, max-age=3600

/assets/docs/*
  Cache-Control: no-store, max-age=0
  Content-Disposition: inline

/assets/fonts/*
  Cache-Control: public, max-age=31536000, immutable

/assets/img/*
  Cache-Control: public, max-age=604800
"""


def build_netlify() -> str:
    return """[build]
  publish = "."

# URL corta para compartir la ficha pública de emergencia.
[[redirects]]
  from = "/emergencia"
  to = "/emergencia.html"
  status = 200
"""


def build_robots() -> str:
    return """# saludrcartes — registro clínico personal
# Ninguna ruta debe indexarse. La ficha de emergencia tampoco.
User-agent: *
Disallow: /

# Sin sitemap público.
"""


def build_readme() -> str:
    pages = "\n".join(
        f"| `{cat['url']}` | {cat['navLabel']} | {group_of(cat)['nombre']} |"
        for cat in CATEGORIAS_ORDER
    )
    return f"""# saludrcartes

Registro clínico personal de **{PERFIL['nombre']}**, construido como sitio estático de 13 páginas. El objetivo es que cualquier persona —Roberto, su familia o un equipo de salud— encuentre en segundos lo que necesita, incluso en una urgencia.

> Los datos de contacto y el centro asistencial son de ejemplo. Reemplázalos por información real antes de usar la ficha de emergencia.

## Páginas

| Archivo | Capítulo | Grupo |
|---|---|---|
| `index.html` | Inicio | Portada |
{pages}

Además: `emergencia.html` (ficha pública, sin login) y `404.html`.

## Cómo verlo en local

No requiere dependencias externas:

```powershell
python -m http.server 8080
```

Abre `http://localhost:8080/`.

## Cómo reconstruirlo

Los datos viven en `data/registro.json` y el sitio se genera con Python estándar:

```powershell
python tools/prepare_data.py   # normaliza la fuente clínica
python tools/build_art.py      # regenera las 13 ilustraciones SVG
python tools/build_site.py     # genera HTML, búsqueda, manifest y configuración
```

`tools/build_site.py` escribe las 13 páginas, `assets/js/search-index.js`, `manifest.webmanifest`, `_headers`, `netlify.toml`, `robots.txt` y `404.html`.

## Diseño

- Estética editorial cálida: crema, verde bosque, detalles en oro y plata.
- Tipografías locales: Quicksand (display), Inter (texto) y Fraunces (editorial).
- Ilustración SVG original para cada página en `assets/img/art/`.
- Fondo ambiental con arte propia, parallax suave, revelados y marcos arqueados.
- Componentes: índice lateral, búsqueda global (`Ctrl+K` o `/`), visor de PDF, ajustes de lectura y ficha de emergencia sticky.

## Accesibilidad

- HTML semántico, enlace para saltar al contenido y foco visible.
- Contraste WCAG 2.1 AA; los estados siempre llevan texto además de color.
- Objetivos táctiles de 44×44 px.
- Preferencias de tamaño de texto, alto contraste y reducción de movimiento.
- Navegación por teclado y cierre con `Esc`.
- Estilos de impresión para la ficha de emergencia y las páginas clínicas.

## Privacidad y despliegue

- `noindex, nofollow` en todas las páginas y `robots.txt` con `Disallow: /`.
- Sin cookies de terceros, sin analítica y sin llamadas a servicios externos.
- Los PDF viven en `assets/docs/` y se sirven desde el mismo origen.
- Configuración lista para Netlify: `netlify.toml`, `_headers`, `manifest.webmanifest` y `404.html`.
- El sitio es público (sin login) por decisión de producto; la ficha de emergencia funciona de forma independiente.

## Estructura

```text
assets/
  css/         sistema de diseño, temas por página y responsive
  docs/        PDF clínicos preservados + ficha de emergencia
  fonts/       fuentes locales
  img/art/     ilustraciones SVG por página
  img/ui/      sello y favicon
  js/          theme-boot.js, site.js y search-index.js
data/          registro clínico normalizado
tools/         generadores de datos, arte y sitio
```

## Nota clínica

Este sitio organiza información personal; no reemplaza una consulta médica. Ante una urgencia con riesgo vital, llama al **131** (SAMU) o acude al servicio de urgencia más cercano.
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def write(path: str | Path, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
    print(f"  wrote {target.relative_to(ROOT)}")


def main() -> None:
    print("Building saludrcartes…")
    write("index.html", home_page())
    write("diagnosticos.html", build_diagnosticos())
    write("medicamentos.html", build_medicamentos())
    write("laboratorio.html", build_laboratorio())
    for cat in CATEGORIAS_ORDER:
        if cat["grupo"] == "especialidades":
            write(cat["url"], build_especialidad(cat))
    write("emergencia.html", emergency_page())
    write("404.html", not_found_page())
    write("assets/js/search-index.js", build_search_index())
    write("manifest.webmanifest", build_manifest())
    write("_headers", build_headers())
    write("netlify.toml", build_netlify())
    write("robots.txt", build_robots())
    write("README.md", build_readme())
    print(f"Done: 13 pages, {total_documents()} documents indexed.")


if __name__ == "__main__":
    main()
