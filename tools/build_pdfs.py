"""Genera la receta vigente y la ficha de emergencia en PDF con Chrome headless.

Uso:
    python tools/build_pdfs.py
"""
from __future__ import annotations

import html
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "registro.json").read_text(encoding="utf-8"))
DOCS = ROOT / "assets" / "docs"
DOCS.mkdir(parents=True, exist_ok=True)

MONTHS = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

CHROME_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def fecha_larga(iso: str | None) -> str:
    if not iso:
        return "Sin fecha"
    year, month, day = (int(part) for part in iso.split("-")[:3])
    return f"{day} de {MONTHS[month - 1]} de {year}"


def find_browser() -> Path:
    for candidate in CHROME_CANDIDATES:
        if candidate.exists():
            return candidate
    found = shutil.which("chrome") or shutil.which("msedge")
    if found:
        return Path(found)
    raise SystemExit("No se encontró Chrome ni Edge para generar los PDFs.")


BASE_CSS = """
  @page { size: A4; margin: 13mm 13mm 14mm; }
  * { box-sizing: border-box; }
  html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  body {
    margin: 0;
    font-family: "Segoe UI", Arial, Helvetica, sans-serif;
    font-size: 10.2pt;
    line-height: 1.45;
    color: #23201c;
  }
  h1, h2, h3, p { margin: 0; }
  .brandbar {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
    padding-bottom: 7px;
    border-bottom: 2px solid #23201c;
  }
  .brandbar strong { font-size: 15pt; letter-spacing: -0.02em; }
  .brandbar span { font-size: 8pt; letter-spacing: 0.14em; text-transform: uppercase; color: #7a6f5f; }
  .meta { display: flex; justify-content: space-between; gap: 1rem; margin: 10px 0 14px; font-size: 8.6pt; color: #5c5448; }
  .meta strong { color: #23201c; }
  h1 { font-size: 22pt; letter-spacing: -0.03em; margin: 6px 0 2px; }
  .subtitle { font-size: 9.5pt; color: #6b6152; margin-bottom: 14px; }
  .callout {
    margin: 12px 0;
    padding: 9px 12px;
    border: 1px solid #b9dfcd;
    border-left: 4px solid #0e9f6e;
    border-radius: 0 8px 8px 0;
    background: #f1fbf6;
    font-size: 9.4pt;
  }
  .callout strong { color: #064e3b; }
  table { width: 100%; border-collapse: collapse; margin-top: 8px; }
  th {
    padding: 7px 8px;
    border-bottom: 1.5px solid #23201c;
    text-align: left;
    font-size: 7.4pt;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6b6152;
  }
  td { padding: 7px 8px; border-bottom: 1px solid #e3ddd2; vertical-align: top; }
  tr:nth-child(even) td { background: #faf7f1; }
  td.num { width: 22px; color: #9a8f7d; font-variant-numeric: tabular-nums; }
  td.med { font-weight: 600; }
  td.dose { white-space: nowrap; }
  .footer {
    margin-top: 18px;
    padding-top: 8px;
    border-top: 1px solid #d8d0c3;
    font-size: 7.8pt;
    color: #7a6f5f;
  }
  .page-break { break-before: page; }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .block { break-inside: avoid; margin-bottom: 12px; }
  .block h2 {
    font-size: 8pt;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #8a4b12;
    margin-bottom: 4px;
  }
  .block ul { margin: 0; padding-left: 16px; }
  .block li { margin: 2px 0; font-size: 9.4pt; }
  .emergency-head {
    padding: 12px 14px;
    border-radius: 10px;
    background: #26201b;
    color: #fff8f0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 14px;
  }
  .emergency-head h1 { font-size: 18pt; margin: 0; color: #fff8f0; }
  .emergency-head p { font-size: 8.4pt; letter-spacing: 0.12em; text-transform: uppercase; color: #f3b7a4; }
  .blood { text-align: center; }
  .blood strong { display: block; font-size: 26pt; line-height: 1; color: #ffc94a; }
  .blood span { font-size: 7pt; letter-spacing: 0.1em; text-transform: uppercase; color: #d9cbbb; }
  .contact-table td { padding: 5px 8px; }
  .priority { width: 18px; color: #9a8f7d; }
  .phone { white-space: nowrap; font-weight: 600; }
  .muted { color: #7a6f5f; }
"""


def render_html(body: str, title: str) -> str:
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<style>{BASE_CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


def receta_html() -> str:
    perfil = DATA["perfil"]
    meds = [med for med in DATA["medicamentos"] if med.get("activo")]
    receta = next(doc for doc in DATA["documentos"] if doc["id"] == "doc-med-receta")
    rows = "\n".join(
        f"""<tr>
          <td class="num">{index}</td>
          <td class="med">{esc(med['nombre'])}</td>
          <td class="dose">{esc(med['dosis'])}</td>
          <td>{esc(med['frecuencia'])}</td>
          <td>{esc(med.get('via') or 'Oral')}</td>
        </tr>"""
        for index, med in enumerate(meds, 1)
    )
    body = f"""
    <div class="brandbar">
      <strong>saludrcartes</strong>
      <span>Registro clínico personal</span>
    </div>
    <div class="meta">
      <span><strong>Titular:</strong> {esc(perfil['nombre'])}</span>
      <span><strong>Documento:</strong> Receta vigente</span>
      <span><strong>Fecha:</strong> {esc(fecha_larga(receta['fecha']))}</span>
    </div>

    <h1>Receta vigente</h1>
    <p class="subtitle">Tratamiento actual · {len(meds)} medicamentos activos</p>

    <div class="callout"><strong>Alergias:</strong> sin alergias a medicamentos conocidas.</div>

    <table>
      <thead>
        <tr><th>#</th><th>Medicamento</th><th>Dosis</th><th>Frecuencia</th><th>Vía</th></tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>

    <div class="footer">
      Documento generado desde saludrcartes el {esc(fecha_larga(receta['fecha']))}. No reemplaza la receta oficial del profesional tratante.
      No suspender ni ajustar dosis sin indicación médica.
    </div>
    """
    return render_html(body, "Receta vigente · saludrcartes")


def emergencia_html() -> str:
    perfil = DATA["perfil"]
    critico = DATA["critico"]
    operaciones = DATA.get("operaciones", [])
    contactos = sorted(DATA["contactos"], key=lambda item: item["orden"])
    familia = [c for c in contactos if c["tipo_contacto"] != "Emergencia pública"]
    publicos = [c for c in contactos if c["tipo_contacto"] == "Emergencia pública"]
    meds = [med for med in DATA["medicamentos"] if med.get("activo")]

    condiciones = "".join(f"<li>{esc(item)}</li>" for item in critico["condiciones"])
    operaciones_html = "".join(f"<li>{esc(op['nombre'])}</li>" for op in operaciones) or "<li>Sin operaciones registradas.</li>"
    alergias = "".join(
        f"<li>{esc(item['sustancia'])} · {esc(item['severidad'])}: {esc(item['reaccion'])}</li>"
        for item in critico["alergias"]
    ) or "<li>Sin alergias a medicamentos conocidas.</li>"
    meds_html = "".join(
        f"<li><strong>{esc(med['nombre'])}</strong> · {esc(med['dosis'])} · {esc(med['frecuencia'])}</li>"
        for med in meds
    )
    family_rows = "".join(
        f"""<tr>
          <td class="priority">{index}</td>
          <td><strong>{esc(c['nombre'])}</strong> <span class="muted">· {esc(c['relacion'])}</span></td>
          <td class="phone">{esc(c['telefono'])}</td>
        </tr>"""
        for index, c in enumerate(familia, 1)
    )
    public_rows = "".join(
        f"""<tr>
          <td><strong>{esc(c['nombre'])}</strong> <span class="muted">· {esc(c['nota'])}</span></td>
          <td class="phone">{esc(c['telefono'])}</td>
        </tr>"""
        for c in publicos
    )

    body = f"""
    <div class="emergency-head">
      <div>
        <p>Ficha pública de emergencia</p>
        <h1>{esc(perfil['nombre'])}</h1>
      </div>
      <div class="blood">
        <strong>{esc(perfil['grupoSanguineo'])}</strong>
        <span>Grupo sanguíneo</span>
      </div>
    </div>

    <div class="meta">
      <span><strong>Actualizada:</strong> {esc(fecha_larga(critico['actualizado']))}</span>
      <span><strong>Ante riesgo vital:</strong> llamar al 131 (SAMU)</span>
    </div>

    <div class="callout"><strong>Alergias:</strong> sin alergias a medicamentos conocidas.</div>

    <div class="two-col">
      <div class="block">
        <h2>Condiciones</h2>
        <ul>{condiciones}</ul>
      </div>
      <div class="block">
        <h2>Operaciones</h2>
        <ul>{operaciones_html}</ul>
      </div>
    </div>

    <div class="block">
      <h2>Alergias registradas</h2>
      <ul>{alergias}</ul>
    </div>

    <div class="block">
      <h2>Medicamentos activos</h2>
      <ul>{meds_html}</ul>
    </div>

    <div class="page-break"></div>

    <div class="brandbar">
      <strong>Contactos</strong>
      <span>En orden de prioridad</span>
    </div>

    <div class="two-col" style="margin-top:12px">
      <div class="block">
        <h2>Círculo cercano</h2>
        <table class="contact-table">
          <tbody>{family_rows}</tbody>
        </table>
      </div>
      <div class="block">
        <h2>Números públicos · Chile</h2>
        <table class="contact-table">
          <tbody>{public_rows}</tbody>
        </table>
      </div>
    </div>

    <div class="footer">
      Documento generado desde saludrcartes el {esc(fecha_larga(critico['actualizado']))}. Esta ficha no reemplaza la evaluación médica.
      Confirmar la vigencia de los teléfonos periódicamente.
    </div>
    """
    return render_html(body, "Ficha de emergencia · saludrcartes")


def print_pdf(browser: Path, html_text: str, target: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="saludrcartes-pdf-") as tmp:
        source = Path(tmp) / "documento.html"
        source.write_text(html_text, encoding="utf-8")
        target.parent.mkdir(parents=True, exist_ok=True)
        command = [
            str(browser),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--virtual-time-budget=2500",
            f"--print-to-pdf={target}",
            source.as_uri(),
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        if result.returncode != 0 or not target.exists():
            raise SystemExit(
                "Chrome no pudo generar el PDF.\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )


def main() -> None:
    browser = find_browser()
    receta = next(doc for doc in DATA["documentos"] if doc["id"] == "doc-med-receta")
    receta_target = ROOT / receta["archivo"]
    emergency_target = DOCS / "emergencia-ficha-resumen.pdf"

    print_pdf(browser, receta_html(), receta_target)
    print(f"  wrote {receta_target.relative_to(ROOT)}")

    print_pdf(browser, emergencia_html(), emergency_target)
    print(f"  wrote {emergency_target.relative_to(ROOT)}")

    old_receta = DOCS / "medicamentos-2026-10-20-receta-vigente.pdf"
    if old_receta.exists():
        old_receta.unlink()
        print(f"  removed {old_receta.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
