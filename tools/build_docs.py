#!/usr/bin/env python3
"""Split the personal archive into documents and build data/expediente.json.

Usage:
    python -X utf8 tools/build_docs.py

The source PDF is not stored in the repository. Point SALUD_PDF at it if the
default path does not exist. OCR text for scanned pages lives in
data/ocr_pages.jsonl (one JSON object per page: {"page": n, "lines": [...]}).
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Iterable

import fitz

ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(
    os.environ.get(
        "SALUD_PDF",
        r"C:\Users\rober\Downloads\archivos saludrcartes 01.pdf",
    )
)
OCR_PATH = ROOT / "data" / "ocr_pages.jsonl"
DOCS_DIR = ROOT / "assets" / "docs"
OUT_PATH = ROOT / "data" / "expediente.json"


# ---------------------------------------------------------------------------
# Document inventory
# ---------------------------------------------------------------------------
# pages are 1-based page numbers in the source archive.
DOC_SPECS: list[dict] = [
    # --- Denuncias ---------------------------------------------------------
    {
        "slug": "cgr-272122-2026",
        "id": "doc-cgr-272122",
        "cat": "denuncias",
        "nombre": "Denuncia CGR N° 272122/2026 — paralización del sumario 2478",
        "fecha": "2026-04-17",
        "descripcion": "Presentación ante la Contraloría General por la paralización del sumario administrativo Res. Ex. N° 2478 y la falta de respuesta del Hospital El Carmen.",
        "descripcion_larga": (
            "Escrito ingresado a la Contraloría General de la República el 17 de abril de 2026. "
            "Denuncia la paralización por más de 19 meses del sumario instruido mediante Resolución Exenta N° 2478, "
            "la falta de conclusividad del procedimiento y la demora en resolver el recurso de reposición presentado el 9 de marzo de 2026. "
            "Solicita fiscalización, entrega íntegra del expediente y determinación de responsabilidades administrativas."
        ),
        "pages": [12, 13, 14, 15, 16],
        "formato": "prosa",
        "fuente": "Contraloría General de la República — denuncia ciudadana",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "cgr-270649-2026",
        "id": "doc-cgr-270649",
        "cat": "denuncias",
        "nombre": "Denuncia CGR N° 270649/2026 — falta a la probidad y abandono de deberes",
        "fecha": "2026-04-16",
        "descripcion": "Denuncia por falta grave a la probidad administrativa, obstrucción del procedimiento y abandono de deberes en el Hospital El Carmen.",
        "descripcion_larga": (
            "Presentación ingresada a la Contraloría General el 16 de abril de 2026. "
            "Relata la retención de respuestas del Hospital El Carmen, la falta de notificación del reclamo 3180597 y la invención de requisitos "
            "para postergar prestaciones. Adjunta antecedentes del sumario 2478, de la solicitud de acceso a la información AO111T0001708 "
            "y de la tramitación ante la Superintendencia de Salud."
        ),
        "pages": [17, 18, 19, 20, 21],
        "formato": "prosa",
        "fuente": "Contraloría General de la República — denuncia ciudadana",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "cgr-denuncias-abril-2026",
        "id": "doc-cgr-serie-abril",
        "cat": "denuncias",
        "nombre": "Denuncias CGR — serie de escritos de abril de 2026",
        "fecha": "2026-04-17",
        "descripcion": "Compilación de escritos de denuncia por falta a la probidad, obstrucción administrativa y dilación injustificada.",
        "descripcion_larga": (
            "Serie de presentaciones preparadas para la Contraloría General durante abril de 2026. "
            "Cada escrito desarrolla un eje distinto: la paralización del sumario 2478, la retención de respuestas, "
            "la obstrucción del reclamo 3180597, la falta de notificación y la demora en la tramitación del recurso de reposición. "
            "Se conservan juntos porque forman una misma línea de reclamación administrativa."
        ),
        "pages": [46, 47, 48, 49, 50, 51, 52, 53],
        "formato": "prosa",
        "fuente": "Contraloría General de la República — serie de denuncias",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "cgr-oficio-123850-2026",
        "id": "doc-cgr-oficio",
        "cat": "denuncias",
        "nombre": "Oficio CGR OF123850/2026 y respuesta del HEC",
        "fecha": "2026-06-26",
        "descripcion": "La Contraloría remite las denuncias al Hospital El Carmen y el director responde que el sumario 2478 sigue en etapa indagatoria.",
        "descripcion_larga": (
            "Oficio de la Contraloría General que remite las presentaciones 270649/2026 y 272122/2026 al Hospital El Carmen para respuesta directa. "
            "La respuesta del director, firmada el 4 de septiembre de 2026, informa que la investigación sumaria instruida por Resolución Exenta N° 2478 "
            "permanece en etapa indagatoria según el certificado interno N° 1692."
        ),
        "pages": [215, 227],
        "formato": "prosa",
        "fuente": "Contraloría General de la República / Hospital El Carmen",
        "afeccion": "afeccion-discapacidad",
    },
    # --- Transparencia -----------------------------------------------------
    {
        "slug": "sai-ao111t0001708",
        "id": "doc-sai-ao111",
        "cat": "transparencia",
        "nombre": "Solicitud de acceso a la información AO111T0001708",
        "fecha": "2026-03-05",
        "descripcion": "Solicitud de acceso a la información sobre el sumario 2478, la solicitud de fuerza pública y el protocolo de clave verde.",
        "descripcion_larga": (
            "Solicitud ingresada al Portal de Transparencia del Estado el 5 de marzo de 2026. "
            "Pide el resultado del procedimiento disciplinario Res. Ex. N° 2478, la identificación del funcionario que solicitó la intervención de Carabineros "
            "y el sustento normativo del protocolo de clave verde. Incluye el comprobante de ingreso y los datos de tramitación."
        ),
        "pages": [32, 33, 34, 35, 36],
        "formato": "lineas",
        "fuente": "Portal de Transparencia del Estado — Hospital El Carmen",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "sai-prorroga-carta-708",
        "id": "doc-sai-prorroga",
        "cat": "transparencia",
        "nombre": "Prórroga y respuesta a la SAI AO111T0001708 (Carta N° 708)",
        "fecha": "2026-04-02",
        "descripcion": "Prórroga de 10 días hábiles, Carta N° 708 y correo de respuesta del Hospital El Carmen a la solicitud de transparencia.",
        "descripcion_larga": (
            "El Hospital El Carmen comunicó una prórroga de diez días hábiles mediante Carta N° 708, fechada el 2 de abril de 2026, "
            "y respondió por correo el 15 de abril. El expediente reúne la prórroga, la carta firmada por la encargada de transparencia "
            "y el correo de notificación con los antecedentes adjuntos."
        ),
        "pages": [62, 63, 64, 30, 31],
        "formato": "prosa",
        "fuente": "Hospital El Carmen — Unidad de Transparencia",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "oirs-3129968",
        "id": "doc-oirs-3129968",
        "cat": "transparencia",
        "nombre": "Respuesta OIRS 3129968 — informe de salud mental",
        "fecha": "2026-02-10",
        "descripcion": "Respuesta del Hospital El Carmen a la solicitud OIRS 3129968, con entrega del informe psiquiátrico y correo de notificación.",
        "descripcion_larga": (
            "Comprobante y respuesta a la solicitud ciudadana ingresada el 28 de enero de 2026. "
            "El hospital informa que entregó presencialmente el informe del psiquiatra del Centro de Salud Mental Ambulatorio. "
            "Se incluye el correo del sistema OIRS que notifica la respuesta el 6 de marzo de 2026."
        ),
        "pages": [80, 81, 82],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — OIRS / Ministerio de Salud",
        "afeccion": "afeccion-tept",
    },
    {
        "slug": "listas-espera-hec",
        "id": "doc-listas-espera",
        "cat": "transparencia",
        "nombre": "Listas de espera y orientación del Hospital El Carmen",
        "fecha": None,
        "descripcion": "Instructivo de orientación sobre listas de espera quirúrgica, interconsultas y derivaciones del Hospital El Carmen.",
        "descripcion_larga": (
            "Documento informativo entregado por el Hospital El Carmen. Explica las ventanillas de atención, "
            "el flujo de derivación a listas de espera quirúrgica y las especialidades disponibles. "
            "Se conserva como respaldo del recorrido administrativo del paciente."
        ),
        "pages": [92, 93],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — orientación al usuario",
        "afeccion": None,
    },
    # --- Superintendencia --------------------------------------------------
    {
        "slug": "reclamo-5007075-2026",
        "id": "doc-reclamo-5007075",
        "cat": "superintendencia",
        "nombre": "Reclamo Superintendencia N° 5007075/2026 — obstrucción y falta de notificación",
        "fecha": "2026-03-28",
        "descripcion": "Reclamo contra el Hospital El Carmen por obstrucción al derecho de reclamo y falta de notificación de respuestas.",
        "descripcion_larga": (
            "Formulario y relato del reclamo ingresado el 28 de marzo de 2026. "
            "Denuncia que el Hospital El Carmen habría redactado la respuesta al folio 3180597 sin notificarla, "
            "con el efecto de impedir el acceso a la Superintendencia. Solicita fiscalización de oficio y un sumario administrativo."
        ),
        "pages": [112, 113, 114],
        "formato": "lineas",
        "fuente": "Superintendencia de Salud — Intendencia de Prestadores",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "denuncia-obstruccion-3180597",
        "id": "doc-obstruccion-3180597",
        "cat": "superintendencia",
        "nombre": "Denuncia por obstrucción y respuesta del HEC (folio 3180597)",
        "fecha": "2026-03-28",
        "descripcion": "Denuncia ante la Superintendencia por bloqueo de la tutela administrativa y respuesta del Hospital El Carmen al folio 3180597.",
        "descripcion_larga": (
            "Escrito que denuncia el ocultamiento de la notificación del folio 3180597 y la respuesta posterior del Hospital El Carmen. "
            "La institución sostiene que el personal actuó dentro de sus funciones y que la solicitud se encontraba dentro de plazo. "
            "El documento conserva ambas versiones para contraste."
        ),
        "pages": [117, 118, 119],
        "formato": "prosa",
        "fuente": "Superintendencia de Salud / Hospital El Carmen",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "ord-ip-10369-2026",
        "id": "doc-ord-10369",
        "cat": "superintendencia",
        "nombre": "ORD. IP/N° 10369 — derivación del reclamo 5007075",
        "fecha": "2026-04-13",
        "descripcion": "Oficio de la Intendencia de Prestadores que deriva el reclamo 5007075 al Hospital El Carmen para respuesta directa.",
        "descripcion_larga": (
            "Oficio firmado por el Intendente de Prestadores de Salud el 13 de abril de 2026. "
            "Deriva el reclamo 5007075 al Hospital El Carmen para que responda directamente al reclamante dentro de quince días hábiles "
            "y adopte las medidas que correspondan conforme a la Ley N° 20.584."
        ),
        "pages": [141, 142],
        "formato": "prosa",
        "fuente": "Superintendencia de Salud — Intendencia de Prestadores",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "reclamo-5008126-2026",
        "id": "doc-reclamo-5008126",
        "cat": "superintendencia",
        "nombre": "Reclamo Superintendencia N° 5008126/2026 — falta de servicio grave",
        "fecha": "2026-04-09",
        "descripcion": "Reclamo por falta de servicio grave, vulneración de la seguridad del paciente y abandono técnico.",
        "descripcion_larga": (
            "Formulario y relato del reclamo ingresado el 9 de abril de 2026. "
            "Invoca la resolución de la Corte de Apelaciones Rol 10275-2026, el incumplimiento del compromiso Folio 29052025-01 "
            "y la activación arbitraria de la clave verde. Pide fiscalización, reparación integral y un gestor de caso."
        ),
        "pages": [144, 145],
        "formato": "lineas",
        "fuente": "Superintendencia de Salud — Intendencia de Prestadores",
        "afeccion": "afeccion-tept",
    },
    {
        "slug": "ord-ip-13532-2026",
        "id": "doc-ord-13532",
        "cat": "superintendencia",
        "nombre": "ORD. IP/N° 13532 — inadmisibilidad del reclamo 5008126",
        "fecha": "2026-05-27",
        "descripcion": "Oficio que declara inadmisible el reclamo 5008126 por no observar vulneraciones a la Ley N° 20.584.",
        "descripcion_larga": (
            "Respuesta de la Intendencia de Prestadores de Salud fechada el 27 de mayo de 2026. "
            "Sostiene que los hechos descritos no comprenden transgresiones a los derechos expresamente consagrados en la Ley N° 20.584 "
            "y cierra la tramitación del reclamo en esa sede."
        ),
        "pages": [199],
        "formato": "prosa",
        "fuente": "Superintendencia de Salud — Intendencia de Prestadores",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "reclamo-5005142-2026",
        "id": "doc-reclamo-5005142",
        "cat": "superintendencia",
        "nombre": "Reclamo 5005142/2026 y ORD. IP/N° 9265 — solicitud de expediente",
        "fecha": "2026-03-26",
        "descripcion": "Oficio de la Superintendencia que formaliza el reclamo 5005142 y solicita al HEC el expediente clínico y administrativo.",
        "descripcion_larga": (
            "Oficio ORD. IP/N° 9265, del 26 de marzo de 2026. "
            "Informa al Hospital El Carmen del inicio del reclamo 5005142, le pide pronunciarse dentro de veinte días hábiles "
            "y remitir la ficha clínica ambulatoria y hospitalaria del período reclamado."
        ),
        "pages": [231, 232],
        "formato": "prosa",
        "fuente": "Superintendencia de Salud — Intendencia de Prestadores",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "denuncia-falta-servicio-2026",
        "id": "doc-denuncia-falta-servicio",
        "cat": "superintendencia",
        "nombre": "Denuncia por falta de servicio grave y abandono técnico",
        "fecha": "2026-04-09",
        "descripcion": "Escrito presentado a la Intendencia de Prestadores por la falta de reparación y el abandono del paciente.",
        "descripcion_larga": (
            "Denuncia fechada el 9 de abril de 2026. Relata la agresión del 13 de agosto de 2024, "
            "el incumplimiento del compromiso de reparación dental y psiquiátrica y la activación de la clave verde el 2 de abril de 2026. "
            "Solicita reparación integral, gestor de caso y fiscalización del Hospital El Carmen."
        ),
        "pages": [179],
        "formato": "prosa",
        "fuente": "Superintendencia de Salud — Intendencia de Prestadores",
        "afeccion": "afeccion-tept",
    },
    {
        "slug": "reclamo-5011276-2025",
        "id": "doc-reclamo-5011276",
        "cat": "superintendencia",
        "nombre": "Reclamo 5011276/2025 — compromisos de atención y respuesta del HEC",
        "fecha": "2025-05-31",
        "descripcion": "Reclamo por incumplimiento de los compromisos de la reunión del 20 de mayo de 2025 y respuesta del Hospital El Carmen.",
        "descripcion_larga": (
            "Expediente del reclamo 5011276, ingresado el 31 de mayo de 2025. "
            "Incluye el oficio de derivación de la Superintendencia, el formulario, la petición concreta de horas de psiquiatría y fisiatría, "
            "y la respuesta del director del Hospital El Carmen del 1 de diciembre de 2025."
        ),
        "pages": [217, 218, 219, 220, 216],
        "formato": "lineas",
        "fuente": "Superintendencia de Salud / Hospital El Carmen",
        "afeccion": "afeccion-tept",
    },
    # --- Tribunales --------------------------------------------------------
    {
        "slug": "caj-metro-presentacion",
        "id": "doc-caj-presentacion",
        "cat": "tribunales",
        "nombre": "Presentación a la CAJ Metro — patrocinio causa RUC 2400965059-4",
        "fecha": "2026-03-05",
        "descripcion": "Solicitud de patrocinio y representación judicial a la Corporación de Asistencia Judicial Metropolitana.",
        "descripcion_larga": (
            "Carta de instrucción al abogado patrocinante de la CAJ Metro, con el detalle de la causa penal RUC 2400965059-4. "
            "Incluye el comprobante de ingreso OIRS, el cargo de recepción y los antecedentes de la causa. "
            "Es la puerta de entrada de la representación jurídica en el caso."
        ),
        "pages": [1, 2, 3, 4],
        "formato": "prosa",
        "fuente": "Corporación de Asistencia Judicial — CAJ Metro",
        "afeccion": "afeccion-tept",
    },
    {
        "slug": "caj-metro-nuevos-hechos",
        "id": "doc-caj-nuevos-hechos",
        "cat": "tribunales",
        "nombre": "Carta a la CAJ Metro — nuevos hechos de violencia institucional",
        "fecha": "2026-04-06",
        "descripcion": "Ampliación de la denuncia penal con los hechos del 2 de abril de 2026 y solicitud de diligencias urgentes.",
        "descripcion_larga": (
            "Escrito dirigido a la abogada patrocinante de la CAJ Metro el 6 de abril de 2026. "
            "Denuncia la activación arbitraria de la clave verde, la intervención de guardias y Carabineros, "
            "y pide diligencias urgentes, resguardo de pruebas y coordinación con la Fiscalía."
        ),
        "pages": [5, 6, 7, 8, 9],
        "formato": "prosa",
        "fuente": "Corporación de Asistencia Judicial — CAJ Metro",
        "afeccion": "afeccion-tept",
    },
    {
        "slug": "certificados-medicos-2021",
        "id": "doc-certificados-2021",
        "cat": "neurologia",
        "nombre": "Certificados médicos — secuelas de ACV y limitación motora",
        "fecha": "2021-04-12",
        "descripcion": "Dos certificados del neurólogo que acreditan las secuelas del ACV y la limitación para trámites presenciales.",
        "descripcion_larga": (
            "Certificados emitidos el 12 de abril de 2021 por el Dr. Ignacio Gutiérrez Corvalán. "
            "Consignan hipertensión arterial, cardiopatía hipertensiva, ACV isquémico cerebeloso izquierdo, síndrome atáxico, "
            "parálisis pseudobulbar y trastorno de la marcha. El segundo certificado agrega insuficiencia cardíaca congestiva "
            "y limita la realización de trámites presenciales."
        ),
        "pages": [10, 11],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — Neurología",
        "afeccion": "afeccion-acv",
    },
    {
        "slug": "relato-primera-visita-hec",
        "id": "doc-relato-hec",
        "cat": "tribunales",
        "nombre": "Relato de la primera visita al HEC — 13 de agosto de 2024",
        "fecha": "2024-08-13",
        "descripcion": "Relato personal de la consulta traumatológica y de la agresión ocurrida en el Hospital El Carmen.",
        "descripcion_larga": (
            "Testimonio escrito de los hechos del martes 13 de agosto de 2024. "
            "Describe la consulta con el traumatólogo, el recorrido por farmacia y laboratorio, la espera por la cirugía de hombro "
            "y el altercado en el área administrativa que derivó en la intervención de Carabineros. "
            "Es la base narrativa de la causa penal y de las denuncias administrativas."
        ),
        "pages": [56, 57],
        "formato": "prosa",
        "fuente": "Relato del titular",
        "afeccion": "afeccion-tept",
    },
    {
        "slug": "recurso-proteccion-10275-2026",
        "id": "doc-recurso-proteccion",
        "cat": "tribunales",
        "nombre": "Recurso de protección Rol 10275-2026",
        "fecha": "2026-04-06",
        "descripcion": "Recurso de protección por vulneración del derecho a la vida, integridad física y salud, con solicitud de orden de no innovar.",
        "descripcion_larga": (
            "Recurso presentado ante la Corte de Apelaciones de Santiago contra el Hospital El Carmen. "
            "Relata el patrón de hostigamiento, la interrupción de tratamientos y el riesgo vital derivado de la insuficiencia cardíaca, "
            "la diabetes mal controlada y el trastorno de estrés postraumático. Solicita orden de no innovar y medidas de resguardo."
        ),
        "pages": [192, 193, 194],
        "formato": "prosa",
        "fuente": "Corte de Apelaciones de Santiago",
        "afeccion": "afeccion-insuficiencia-cardiaca",
    },
    {
        "slug": "resolucion-inadmisible-10275-2026",
        "id": "doc-resolucion-10275",
        "cat": "tribunales",
        "nombre": "Resolución de inadmisibilidad — Protección 10275-2026",
        "fecha": "2026-04-08",
        "descripcion": "La Corte de Apelaciones declara inadmisible el recurso y remite la materia a la Superintendencia de Salud.",
        "descripcion_larga": (
            "Resolución de la Primera Sala de la Corte de Apelaciones de Santiago, del 8 de abril de 2026. "
            "Declara inadmisible el recurso por no ser la vía idónea y señala que los hechos deben reclamarse ante la Superintendencia de Salud. "
            "La resolución se conserva con la firma electrónica y el código de validación."
        ),
        "pages": [190, 191],
        "formato": "prosa",
        "fuente": "Corte de Apelaciones de Santiago",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "parte-carabineros-7265",
        "id": "doc-parte-7265",
        "cat": "tribunales",
        "nombre": "Parte de Carabineros N° 7265 — denuncia de los hechos",
        "fecha": "2024-08-13",
        "descripcion": "Copia del parte policial por los hechos ocurridos al interior del Hospital El Carmen el 13 de agosto de 2024.",
        "descripcion_larga": (
            "Parte de Carabineros elaborado por el Sargento 1° Sergio Cortés Rodríguez. "
            "Contiene la identificación del denunciante, el relato de los hechos, la individualización del funcionario involucrado "
            "y la relación de lesiones. La copia fue obtenida desde el sistema de atención de usuarios el 9 de febrero de 2026."
        ),
        "pages": [159, 160, 161, 162, 163, 164],
        "formato": "lineas",
        "fuente": "Carabineros de Chile — 25° Comisaría de Maipú",
        "afeccion": "afeccion-tept",
    },
    {
        "slug": "orientacion-juridica-caj",
        "id": "doc-orientacion-caj",
        "cat": "tribunales",
        "nombre": "Orientación jurídica y orden de atención CAJ",
        "fecha": None,
        "descripcion": "Listado de clínicas jurídicas y orden de atención de la Corporación de Asistencia Judicial.",
        "descripcion_larga": (
            "Documento de orientación entregado por la CAJ. Incluye el listado de clínicas jurídicas universitarias "
            "y la orden de atención N° 431270. Se conserva como respaldo del primer contacto con la corporación."
        ),
        "pages": [22, 23],
        "formato": "lineas",
        "fuente": "Corporación de Asistencia Judicial",
        "afeccion": None,
    },
    {
        "slug": "modelo-recurso-proteccion",
        "id": "doc-modelo-recurso",
        "cat": "tribunales",
        "nombre": "Modelo de recurso de protección — documento de apoyo",
        "fecha": None,
        "descripcion": "Formulario modelo para preparar un recurso de protección ante la Corte de Apelaciones.",
        "descripcion_larga": (
            "Modelo de escrito con instrucciones para completar un recurso de protección. "
            "No es un documento del caso, sino material de apoyo que quedó incorporado al expediente. "
            "Se conserva para reconstruir el proceso de preparación del recurso."
        ),
        "pages": [95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105],
        "formato": "prosa",
        "fuente": "Documento de apoyo — Poder Judicial",
        "afeccion": None,
    },
    # --- Cartas ------------------------------------------------------------
    {
        "slug": "interpelacion-hec-2026-04-15",
        "id": "doc-interpelacion",
        "cat": "cartas",
        "nombre": "Interpelación formal y apercibimiento legal al HEC",
        "fecha": "2026-04-15",
        "descripcion": "Correo y cartas de interpelación por la respuesta dilatoria a la SAI AO111T0001708 y la activación de la clave verde.",
        "descripcion_larga": (
            "Correo enviado el 15 de abril de 2026 a la Dirección, Asesoría Jurídica y Transparencia del Hospital El Carmen. "
            "Rechaza la respuesta dilatoria, notifica el estado de rebeldía administrativa y adjunta el recurso de reposición "
            "y el último apercibimiento legal. Fija un plazo de 24 horas para entregar el sumario 2478."
        ),
        "pages": [37, 38, 39, 40],
        "formato": "prosa",
        "fuente": "Correspondencia del titular",
        "afeccion": "afeccion-tept",
    },
    {
        "slug": "carta-director-2026-03-05",
        "id": "doc-carta-director",
        "cat": "cartas",
        "nombre": "Carta al Director del HEC — incumplimiento de plazo OIRS",
        "fecha": "2026-03-05",
        "descripcion": "Denuncia formal por el vencimiento del plazo del folio OIRS 3146846 y por la conducta de funcionarias de atención al usuario.",
        "descripcion_larga": (
            "Carta dirigida al director del Hospital El Carmen el 5 de marzo de 2026. "
            "Sostiene que la solicitud ingresada el 9 de febrero venció el 2 de marzo y que las funcionarias Fernanda Aguayo y Romina Peña "
            "habrían entregado información falsa sobre el plazo. Pide investigación sumaria y anotación de demérito."
        ),
        "pages": [115],
        "formato": "prosa",
        "fuente": "Correspondencia del titular",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "notificacion-responsabilidad-2026-04",
        "id": "doc-notificacion-responsabilidad",
        "cat": "cartas",
        "nombre": "Notificación de responsabilidad penal y civil al HEC",
        "fecha": "2026-04-08",
        "descripcion": "Carta que notifica responsabilidad personal por la vejación injusta y la activación de la clave verde.",
        "descripcion_larga": (
            "Escrito dirigido al director del Hospital El Carmen con copia al Consejo de Defensa del Estado, Contraloría e INDH. "
            "Califica los hechos del 2 de abril como vejación injusta y tortura institucional, "
            "anuncia acciones penales y civiles y exige la entrega inmediata del sumario 2478."
        ),
        "pages": [148, 149],
        "formato": "prosa",
        "fuente": "Correspondencia del titular",
        "afeccion": "afeccion-tept",
    },
    {
        "slug": "carta-hec-2025-05-29",
        "id": "doc-carta-hec-2905",
        "cat": "cartas",
        "nombre": "Carta a la Dirección del HEC — incumplimiento de compromisos (folio 29052025-01)",
        "fecha": "2025-05-29",
        "descripcion": "Carta por el incumplimiento sistemático de los compromisos de la reunión del 20 de mayo de 2025.",
        "descripcion_larga": (
            "Carta fechada el 29 de mayo de 2025 y dirigida a la directora subrogante y al abogado jefe del Hospital El Carmen. "
            "Relata la falta de contacto, la demora en la hora de psiquiatría y la postergación de la evaluación fisíatrica. "
            "Incluye un anexo con el detalle de los compromisos y las cartas anteriores."
        ),
        "pages": [196, 197, 198],
        "formato": "prosa",
        "fuente": "Correspondencia del titular",
        "afeccion": "afeccion-tept",
    },
    {
        "slug": "carta-hec-2025-05-30",
        "id": "doc-carta-hec-3005",
        "cat": "cartas",
        "nombre": "Carta de reiteración a la Dirección del HEC (folio 30052025-01)",
        "fecha": "2025-05-30",
        "descripcion": "Reiteración de la carta del 29 de mayo, con la exigencia de respuestas concretas antes del 3 de junio de 2025.",
        "descripcion_larga": (
            "Segunda carta consecutiva, fechada el 30 de mayo de 2025. "
            "Exige la entrega de fechas, horas y profesionales para la atención psiquiátrica y fisíatrica, "
            "y advierte que si el hospital no cumple asumirá el costo del plazo. Forma parte del mismo intercambio que la carta anterior."
        ),
        "pages": [221, 222],
        "formato": "prosa",
        "fuente": "Correspondencia del titular",
        "afeccion": "afeccion-tept",
    },
    {
        "slug": "correo-indh-2024-08-29",
        "id": "doc-correo-indh",
        "cat": "cartas",
        "nombre": "Correo al INDH — estado emocional y síntomas postraumáticos",
        "fecha": "2024-08-29",
        "descripcion": "Correo enviado al INDH dos semanas después de la agresión, con la descripción de los síntomas y el miedo persistente.",
        "descripcion_larga": (
            "Mensaje enviado el 29 de agosto de 2024 a la encargada del INDH. "
            "Describe ansiedad extrema, percepción constante de peligro, miedo a salir, llanto inconsolable, pensamientos intrusivos "
            "y temor a regresar al Hospital El Carmen. Es uno de los primeros registros del impacto psíquico de los hechos."
        ),
        "pages": [94],
        "formato": "prosa",
        "fuente": "Correspondencia del titular — INDH",
        "afeccion": "afeccion-tept",
    },
    # --- Discapacidad ------------------------------------------------------
    {
        "slug": "senadis-oficio-hec-2024",
        "id": "doc-senadis-hec",
        "cat": "discapacidad",
        "nombre": "Oficio SENADIS al HEC — denuncia por apremios",
        "fecha": "2024-08-21",
        "descripcion": "Oficio del Servicio Nacional de la Discapacidad que informa al Hospital El Carmen la denuncia por apremios ilegítimos.",
        "descripcion_larga": (
            "Oficio R4-2024, firmado por el director nacional de SENADIS el 21 de agosto de 2024. "
            "Informa al Hospital El Carmen la denuncia presentada por Roberto Cartes y solicita antecedentes sobre el actuar de guardias y funcionarios. "
            "Incluye el relato de la entrevista presencial del 19 de agosto de 2024."
        ),
        "pages": [203, 204, 205, 206, 207],
        "formato": "prosa",
        "fuente": "Servicio Nacional de la Discapacidad — SENADIS",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "senadis-oficio-carabineros-2024",
        "id": "doc-senadis-carabineros",
        "cat": "discapacidad",
        "nombre": "Oficio SENADIS a Carabineros — denuncia por apremios",
        "fecha": "2024-08-21",
        "descripcion": "Oficio que pide a Carabineros investigar la actuación policial denunciada al interior del hospital.",
        "descripcion_larga": (
            "Oficio 803-2024, del 21 de agosto de 2024, dirigido a la Dirección de Derechos Humanos y Protección de la Familia de Carabineros. "
            "Solicita informar si los hechos eran conocidos, las medidas adoptadas y las acciones para evitar que se repitan. "
            "Adjunta el relato detallado de la detención y los golpes."
        ),
        "pages": [208, 209, 210, 211, 212],
        "formato": "prosa",
        "fuente": "Servicio Nacional de la Discapacidad — SENADIS",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "carabineros-respuesta-senadis-2024",
        "id": "doc-carabineros-respuesta",
        "cat": "discapacidad",
        "nombre": "Respuesta de Carabineros a SENADIS",
        "fecha": "2024-09-23",
        "descripcion": "Carabineros informa que el parte N° 7265 fue enviado a la Fiscalía y que se instruyó una investigación administrativa.",
        "descripcion_larga": (
            "Oficio N° 34, del 23 de septiembre de 2024, de la Dirección de Derechos Humanos y Protección de la Familia de Carabineros. "
            "Confirma que el Sargento 1° Sergio Cortés Rodríguez denunció los hechos a la Fiscalía Local de Maipú mediante el parte N° 7265 "
            "y que se dispuso una investigación administrativa."
        ),
        "pages": [213, 214],
        "formato": "prosa",
        "fuente": "Carabineros de Chile — Dirección de DD.HH.",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "senadis-respuesta-2026",
        "id": "doc-senadis-respuesta",
        "cat": "discapacidad",
        "nombre": "Respuesta de SENADIS — gestión del caso y derivación a la CAJ",
        "fecha": None,
        "descripcion": "SENADIS detalla las gestiones realizadas, la derivación a la CAJ y los límites de su competencia.",
        "descripcion_larga": (
            "Respuesta del director nacional de SENADIS a la solicitud ciudadana de 2026. "
            "Reconstruye las gestiones desde 2024, la derivación al Programa de Acceso a la Justicia, la entrevista con la CAJ "
            "y la elaboración del escrito judicial. Aclara que no puede financiar implantes dentales ni otorgar prestaciones de salud."
        ),
        "pages": [228, 229, 230],
        "formato": "prosa",
        "fuente": "Servicio Nacional de la Discapacidad — SENADIS",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "certificado-discapacidad-2024",
        "id": "doc-certificado-discapacidad",
        "cat": "discapacidad",
        "nombre": "Certificado de discapacidad — 13,40% leve, movilidad reducida",
        "fecha": "2024-05-06",
        "descripcion": "Certificado del Registro Civil que acredita discapacidad global leve de 13,40%, causa física y movilidad reducida.",
        "descripcion_larga": (
            "Certificado emitido el 6 de mayo de 2024. "
            "Consigna el dictamen de COMPIN Poniente del 21 de enero de 2022, el grado global de discapacidad de 13,40% "
            "y la causa principal física con movilidad reducida. El folio 500566593358 permite verificar el documento."
        ),
        "pages": [54],
        "formato": "lineas",
        "fuente": "Servicio de Registro Civil e Identificación",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "credencial-discapacidad-2024",
        "id": "doc-credencial-discapacidad",
        "cat": "discapacidad",
        "nombre": "Credencial de discapacidad — Registro Nacional",
        "fecha": "2024-05-06",
        "descripcion": "Credencial del Registro Nacional de la Discapacidad con el grado global y la causa principal.",
        "descripcion_larga": (
            "Credencial emitida el 6 de mayo de 2024 por el Servicio de Registro Civil. "
            "Individualiza a Roberto Carlos Cartes Jiménez, su domicilio en Maipú, el grado global de discapacidad leve de 13,40% "
            "y la causa física con movilidad reducida. Folio 500566593350."
        ),
        "pages": [131],
        "formato": "lineas",
        "fuente": "Servicio de Registro Civil e Identificación",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "pension-invalidez-2026-01",
        "id": "doc-pension-invalidez",
        "cat": "discapacidad",
        "nombre": "Liquidación de pensión de invalidez — enero 2026",
        "fecha": "2026-01-19",
        "descripcion": "Comprobante de pago de la pensión de invalidez, con haberes, descuentos y monto líquido.",
        "descripcion_larga": (
            "Liquidación de pago de la pensión de invalidez correspondiente a enero de 2026. "
            "Detalla el aporte previsional solidario, la bonificación fiscal de salud, los descuentos de caja de compensación y salud, "
            "y un pago neto de $236.608. Se conserva como respaldo del ingreso del hogar."
        ),
        "pages": [70],
        "formato": "lineas",
        "fuente": "Instituto de Previsión Social / administradora de pensiones",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "cartola-rsh-2026-02",
        "id": "doc-cartola-rsh",
        "cat": "discapacidad",
        "nombre": "Cartola del Registro Social de Hogares — Tramo 40",
        "fecha": "2026-02-09",
        "descripcion": "Cartola del RSH que ubica al hogar en el tramo 40% y resume integrantes, dependencia e ingresos.",
        "descripcion_larga": (
            "Cartola descargada el 9 de febrero de 2026. "
            "El hogar de tres personas se ubica en el tramo 40% de vulnerabilidad socioeconómica. "
            "Registra una persona con dependencia, los rangos de ingreso del trabajo y de pensión, y los integrantes del hogar. "
            "Se incluye como antecedente de apoyo social."
        ),
        "pages": [178],
        "formato": "lineas",
        "fuente": "Registro Social de Hogares — Chile Atiende",
        "afeccion": "afeccion-discapacidad",
    },
    {
        "slug": "certificado-antecedentes-2026",
        "id": "doc-certificado-antecedentes",
        "cat": "discapacidad",
        "nombre": "Certificado de antecedentes para fines particulares",
        "fecha": "2026-02-09",
        "descripcion": "Certificado del Registro Civil que acredita ausencia de anotaciones en los registros de condenas.",
        "descripcion_larga": (
            "Certificado emitido el 9 de febrero de 2026. "
            "Acredita que Roberto Carlos Cartes Jiménez no registra anotaciones en el Registro General de Condenas "
            "ni en el Registro Especial de Condenas por Actos de Violencia Intrafamiliar. Folio 500678620867."
        ),
        "pages": [158],
        "formato": "lineas",
        "fuente": "Servicio de Registro Civil e Identificación",
        "afeccion": None,
    },
    # --- Médicos -----------------------------------------------------------
    {
        "slug": "laboratorio-2026-03-25",
        "id": "doc-laboratorio-2026-03",
        "cat": "laboratorio",
        "nombre": "Laboratorio — hemograma, bioquímica y coagulación (25-03-2026)",
        "fecha": "2026-03-25",
        "descripcion": "Resultados de laboratorio con glicemia 160 mg/dL, HbA1c 8,5%, creatinina 1,09 y VHS 43.",
        "descripcion_larga": (
            "Informe del laboratorio del Hospital El Carmen, muestra del 25 de marzo de 2026. "
            "Destacan glicemia de 160 mg/dL, hemoglobina glicosilada de 8,5%, creatinina de 1,09 mg/dL, "
            "filtración glomerular de 75,2 mL/min, ácido úrico de 6,2 mg/dL, eosinófilos de 8,4%, VHS de 43 mm/h y plaquetas de 152.000. "
            "La coagulación se encuentra dentro de rango."
        ),
        "pages": [58, 59, 60, 61],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — Laboratorio clínico",
        "afeccion": "afeccion-diabetes",
    },
    {
        "slug": "cardiologia-control-2026-04-02",
        "id": "doc-cardiologia-control",
        "cat": "cardiologia",
        "nombre": "Control de cardiología — insuficiencia cardíaca y DM2 (02-04-2026)",
        "fecha": "2026-04-02",
        "descripcion": "Informe ambulatorio con el ajuste de tratamiento cardíaco y el resumen metabólico de marzo.",
        "descripcion_larga": (
            "Informe de atención ambulatoria del 2 de abril de 2026, firmado por el Dr. Rami Souki Chmeit. "
            "Concluye insuficiencia cardíaca con FEVI levemente reducida, miocardiopatía secundaria a disincronía y diabetes tipo 2 mal controlada. "
            "Ajusta empagliflozina a 25 mg, bisoprolol a 5 mg y agrega furosemida 20 mg; insiste en suspender carvedilol."
        ),
        "pages": [65, 66],
        "formato": "prosa",
        "fuente": "Hospital El Carmen — Cardiología",
        "afeccion": "afeccion-insuficiencia-cardiaca",
    },
    {
        "slug": "kinesiologia-evaluacion-marcha",
        "id": "doc-kinesiologia",
        "cat": "rehabilitacion",
        "nombre": "Evaluación de kinesiología — equilibrio y marcha",
        "fecha": None,
        "descripcion": "Evaluación funcional con Mini Best Test 14/28, Up and Go de 20 segundos y velocidad de marcha de 0,87 m/s.",
        "descripcion_larga": (
            "Informe de kinesiología del Hospital El Carmen, firmado por el Klgo. Daniel Bustos. "
            "Documenta la rehabilitación de 2022, la marcha extradomiciliaria independiente y el aumento de la inestabilidad. "
            "El Mini Best Test marca 14/28, el Up and Go 20 segundos y la velocidad de marcha 0,87 m/s, con riesgo elevado de caída."
        ),
        "pages": [67, 68, 69],
        "formato": "prosa",
        "fuente": "Hospital El Carmen — Kinesiología",
        "afeccion": "afeccion-marcha",
    },
    {
        "slug": "psiquiatria-informe-2026-02-04",
        "id": "doc-psiquiatria-informe",
        "cat": "psiquiatria",
        "nombre": "Informe de psiquiatría — TEPT y psicosis lúcida (04-02-2026)",
        "fecha": "2026-02-04",
        "descripcion": "Informe del psiquiatra tratante que confirma trastorno de estrés postraumático y psicosis lúcida de origen orgánico.",
        "descripcion_larga": (
            "Informe médico de respuesta a solicitud ciudadana, folio 3129968, del 4 de febrero de 2026. "
            "El Dr. Lucas Domínguez Hernández confirma controles periódicos desde abril de 2025, "
            "diagnostica trastorno de estrés postraumático y psicosis lúcida de origen orgánico, y consigna un GAF de 41-50%."
        ),
        "pages": [71],
        "formato": "prosa",
        "fuente": "Hospital El Carmen — Centro de Salud Mental Ambulatorio",
        "afeccion": "afeccion-tept",
    },
    {
        "slug": "ecocardiograma-2026-03-18",
        "id": "doc-ecocardiograma",
        "cat": "cardiologia",
        "nombre": "Ecocardiograma transtorácico — FEVI 47% (18-03-2026)",
        "fecha": "2026-03-18",
        "descripcion": "Ecocardiograma con FEVI biplano de 47%, ventrículo izquierdo hipertrófico leve y disfunción diastólica grado I.",
        "descripcion_larga": (
            "Estudio realizado el 18 de marzo de 2026 en el Hospital El Carmen. "
            "Informa FEVI biplano de 47%, hipocinesia difusa y movimiento septal disincrónico por bloqueo de rama izquierda, "
            "ventrículo izquierdo hipertrófico leve, aurícula izquierda levemente dilatada, PSAP de 26 mmHg y presión de llenado normal. "
            "Sugiere complementar con resonancia cardíaca con gadolinio."
        ),
        "pages": [122, 123, 124, 125, 126],
        "formato": "prosa",
        "fuente": "Hospital El Carmen — Ecocardiografía",
        "afeccion": "afeccion-insuficiencia-cardiaca",
    },
    {
        "slug": "ecg-2026-03-12",
        "id": "doc-ecg",
        "cat": "cardiologia",
        "nombre": "Electrocardiograma — BCRI y PR prolongado (12-03-2026)",
        "fecha": "2026-03-12",
        "descripcion": "ECG con frecuencia de 78 lpm, PR de 214 ms, QRS de 150 ms y QTc de 442 ms; informe no confirmado.",
        "descripcion_larga": (
            "Trazado electrocardiográfico del 12 de marzo de 2026. "
            "Registra frecuencia cardíaca de 78 lpm, PR de 214 ms, QRS de 150 ms y QT/QTc de 388/442 ms. "
            "El informe está marcado como no confirmado y será validado por el cardiólogo tratante."
        ),
        "pages": [120, 121],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — Electrocardiografía",
        "afeccion": "afeccion-insuficiencia-cardiaca",
    },
    {
        "slug": "analisis-marcha-2025-11-03",
        "id": "doc-analisis-marcha",
        "cat": "rehabilitacion",
        "nombre": "Análisis computarizado de marcha — zebris (03-11-2025)",
        "fecha": "2025-11-03",
        "descripcion": "Informe de marcha con cadencia de 91 pasos/min, velocidad de 1,2 km/h y asimetría de apoyo.",
        "descripcion_larga": (
            "Estudio de marcha realizado el 3 de noviembre de 2025 con plataforma zebris FDM-T. "
            "Registra cadencia de 91 ± 8 pasos/min, velocidad de 1,2 ± 0,3 km/h, longitud de paso asimétrica y mayor tiempo de apoyo en el lado derecho. "
            "El informe incluye mapas de presión, análisis del centro de presión y curvas de fuerza."
        ),
        "pages": [132, 133, 134, 135, 136],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — Análisis de marcha",
        "afeccion": "afeccion-marcha",
    },
    {
        "slug": "receta-cardiologia-2026-04-02",
        "id": "doc-med-receta",
        "cat": "medicamentos",
        "nombre": "Receta crónica de cardiología — 02-04-2026",
        "fecha": "2026-04-02",
        "descripcion": "Receta de bisoprolol 5 mg y empagliflozina 25 mg, con vigencia de 180 días.",
        "descripcion_larga": (
            "Receta crónica emitida el 2 de abril de 2026 por el Dr. Rami Souki Chmeit. "
            "Prescribe bisoprolol 5 mg cada 24 horas y empagliflozina 25 mg cada 24 horas por 180 días. "
            "Incluye una segunda impresión con el mismo contenido y las anotaciones de entrega de farmacia."
        ),
        "pages": [106, 107],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — Cardiología",
        "afeccion": "afeccion-insuficiencia-cardiaca",
    },
    {
        "slug": "receta-cardiologia-2026-02-09",
        "id": "doc-receta-cardio-febrero",
        "cat": "medicamentos",
        "nombre": "Recetas crónicas de cardiología — 09-02-2026",
        "fecha": "2026-02-09",
        "descripcion": "Recetas de empagliflozina, aspirina y bisoprolol emitidas por cardiología.",
        "descripcion_larga": (
            "Tres recetas crónicas del 9 de febrero de 2026, firmadas por el Dr. Santiago Márquez Herrero. "
            "Prescriben empagliflozina 25 mg, ácido acetilsalicílico 100 mg y bisoprolol 5 mg. "
            "Se conservan juntas porque corresponden a la misma atención y al mismo ajuste de tratamiento."
        ),
        "pages": [108, 109, 110],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — Cardiología",
        "afeccion": "afeccion-insuficiencia-cardiaca",
    },
    {
        "slug": "receta-tamsulosina-2025-12-18",
        "id": "doc-receta-tamsulosina",
        "cat": "medicamentos",
        "nombre": "Receta de tamsulosina — 18-12-2025",
        "fecha": "2025-12-18",
        "descripcion": "Receta crónica de tamsulosina 0,4 mg para el adenoma benigno de próstata.",
        "descripcion_larga": (
            "Receta crónica emitida el 18 de diciembre de 2025 por la Dra. María Ebensperger Carrasco. "
            "Prescribe tamsulosina 0,4 mg en cápsula de liberación prolongada, una vez al día por 365 días. "
            "El diagnóstico registrado es adenoma benigno de próstata."
        ),
        "pages": [111],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — Anestesiología",
        "afeccion": "afeccion-prostata",
    },
    {
        "slug": "epicrisis-tunel-carpiano-2025-11",
        "id": "doc-epicrisis-tunel",
        "cat": "traumatologia-superior",
        "nombre": "Epicrisis — cirugía de túnel carpiano izquierdo (noviembre 2025)",
        "fecha": "2025-11-07",
        "descripcion": "Epicrisis de la liberación quirúrgica del túnel carpiano izquierdo, sin incidentes y con evolución favorable.",
        "descripcion_larga": (
            "Epicrisis de cirugía mayor ambulatoria del Hospital El Carmen. "
            "Ingreso el 6 de noviembre de 2025 y alta el 7 de noviembre. "
            "El procedimiento de liberación del túnel carpiano izquierdo fue sin incidentes; se indican reposo relativo, mano en alto, "
            "control de equipo de mano en 10 a 14 días y analgesia con celecoxib, paracetamol y tramadol condicionado."
        ),
        "pages": [74],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — Cirugía Mayor Ambulatoria",
        "afeccion": "afeccion-tunel-carpiano",
    },
    {
        "slug": "derivacion-cirugia-cardiovascular-2024-10",
        "id": "doc-derivacion-vascular",
        "cat": "cardiologia",
        "nombre": "Derivación a cirugía cardiovascular — insuficiencia venosa",
        "fecha": "2024-10-10",
        "descripcion": "Interconsulta por insuficiencia venosa profunda bilateral de las extremidades inferiores.",
        "descripcion_larga": (
            "Solicitud de interconsulta del 10 de octubre de 2024. "
            "Deriva a cirugía cardiovascular por insuficiencia venosa profunda bilateral de extremidades inferiores, "
            "con fundamento en el eco-Doppler venoso. El documento incluye los datos de admisión y el profesional solicitante."
        ),
        "pages": [84],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — Cirugía Cardiovascular",
        "afeccion": "afeccion-insuficiencia-venosa",
    },
    {
        "slug": "pase-operatorio-colecistectomia-2026-04",
        "id": "doc-pase-operatorio",
        "cat": "diagnosticos",
        "nombre": "Pase operatorio — colecistectomía laparoscópica",
        "fecha": "2026-04-16",
        "descripcion": "Evaluación preoperatoria de medicina interna para colecistectomía laparoscópica por colelitiasis.",
        "descripcion_larga": (
            "Solicitud de interconsulta y evaluación preoperatoria del 16 de abril de 2026. "
            "Resume los antecedentes de hipertensión, diabetes tipo 2, ACV cerebeloso secuelado, insuficiencia cardíaca, "
            "estrés postraumático y psicosis lúcida. Concluye que el paciente se encuentra en condiciones para el pase operatorio "
            "de colecistectomía laparoscópica."
        ),
        "pages": [89, 88, 86],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — Medicina Interna",
        "afeccion": "afeccion-colelitiasis",
    },
    {
        "slug": "derivacion-kinesiologia-2025-12",
        "id": "doc-derivacion-kine",
        "cat": "rehabilitacion",
        "nombre": "Derivación a kinesiología — postoperatorio túnel carpiano",
        "fecha": "2025-12-02",
        "descripcion": "Interconsulta a kinesiología para rehabilitación motora después de la cirugía de túnel carpiano izquierdo.",
        "descripcion_larga": (
            "Solicitud de interconsulta del 2 de diciembre de 2025. "
            "Deriva a kinesiología para sesiones de motricidad después de la liberación del túnel carpiano izquierdo. "
            "El diagnóstico registrado es síndrome del túnel carpiano y el fundamento es el postoperatorio."
        ),
        "pages": [87],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — Traumatología y Ortopedia",
        "afeccion": "afeccion-tunel-carpiano",
    },
    {
        "slug": "derivacion-columna-lumbar-2026-04",
        "id": "doc-derivacion-columna",
        "cat": "traumatologia-inferior",
        "nombre": "Derivaciones de columna lumbar — hernia del núcleo pulposo",
        "fecha": "2026-04-09",
        "descripcion": "Interconsultas a traumatología y neurología por dolor lumbar crónico y hernia del núcleo pulposo L5-S1.",
        "descripcion_larga": (
            "Dos solicitudes de interconsulta por columna lumbar. "
            "La primera, del 9 de abril de 2026, deriva al equipo de columna por dolor lumbar de un año de evolución, "
            "discopatía degenerativa y estenosis foraminal L5-S1 con aparente conflicto de la raíz L5 derecha. "
            "La segunda, del 16 de abril de 2025, solicita tratamiento quirúrgico de hernia del núcleo pulposo lumbar."
        ),
        "pages": [90, 91],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — Traumatología y Neurología",
        "afeccion": "afeccion-lumbar",
    },
    {
        "slug": "solicitudes-laboratorio-2025-2026",
        "id": "doc-solicitudes-laboratorio",
        "cat": "laboratorio",
        "nombre": "Solicitudes de laboratorio (2025–2026)",
        "fecha": "2026-11-12",
        "descripcion": "Órdenes de laboratorio de diabetología, medicina interna y neurología, con los exámenes solicitados.",
        "descripcion_larga": (
            "Compilación de órdenes de laboratorio emitidas entre diciembre de 2025 y noviembre de 2026. "
            "Incluye controles de diabetes, hemograma, VHS, perfil lipídico, función renal, electrolitos, PSA, NT-proBNP, "
            "vitaminas B12 y D, y pruebas hepáticas. Cada página conserva la fecha, el diagnóstico y el profesional solicitante."
        ),
        "pages": [241, 239, 78, 76, 77, 75],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — Laboratorio clínico",
        "afeccion": "afeccion-diabetes",
    },
    {
        "slug": "solicitudes-imagenes-2026",
        "id": "doc-solicitudes-imagenes",
        "cat": "diagnosticos",
        "nombre": "Solicitudes de imágenes y procedimientos (2026)",
        "fecha": "2026-07-27",
        "descripcion": "Órdenes de ecografía, tomografía de cerebro, uroflujometría y eco de estrés.",
        "descripcion_larga": (
            "Compilación de solicitudes de diagnóstico por imagen y procedimientos. "
            "Incluye ecografía de pelvis masculina por adenoma prostático, tomografía de cerebro sin contraste por control de ACV y cefalea recurrente, "
            "uroflujometría y eco de estrés cardíaco. Cada orden registra el profesional solicitante y el diagnóstico asociado."
        ),
        "pages": [79, 236, 237, 242],
        "formato": "lineas",
        "fuente": "Hospital El Carmen — Imagenología y procedimientos",
        "afeccion": "afeccion-acv",
    },
]


# ---------------------------------------------------------------------------
# Text extraction and cleaning
# ---------------------------------------------------------------------------
def load_ocr() -> dict[int, str]:
    result: dict[int, str] = {}
    if not OCR_PATH.exists():
        print(f"  warning: no OCR cache at {OCR_PATH}")
        return result
    for line in OCR_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        result[int(item["page"])] = "\n".join(item.get("lines", []))
    return result


def clean_common(text: str) -> str:
    text = text.replace("\ufeff", "").replace("\u00ad", "")
    text = text.replace("\uf0b7", "•").replace("\uf0a7", "•")
    text = text.replace("\u00a0", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_lines(text: str) -> str:
    """Preserve lines, removing only obvious page furniture."""
    text = clean_common(text)
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if lines and lines[-1] != "":
                lines.append("")
            continue
        if re.fullmatch(r"\d{1,2}\s*/\s*\d{1,2}", line):
            continue
        if re.fullmatch(r"Página \d+ de \d+", line, re.I):
            continue
        if re.fullmatch(r"Fojas \d+", line, re.I):
            continue
        if re.fullmatch(r"\d{7}-\d{4}\.pdf", line, re.I):
            continue
        lines.append(line)
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def paragraphize(text: str, max_len: int = 850) -> str:
    """Turn a page of justified PDF text into readable paragraphs."""
    text = clean_common(text)
    text = re.sub(r"\s*\n\s*", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡«\"(])", text)
    paragraphs: list[str] = []
    current = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if current and len(current) + len(sentence) + 1 > max_len:
            paragraphs.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        paragraphs.append(current.strip())
    return "\n\n".join(paragraphs)


def page_text(page_no: int, source: fitz.Document, ocr: dict[int, str]) -> tuple[str, str]:
    if page_no in ocr and ocr[page_no].strip():
        return ocr[page_no], "ocr"
    return source[page_no - 1].get_text("text"), "texto"


def build_transcription(spec: dict, source: fitz.Document, ocr: dict[int, str]) -> tuple[str, str, list[str]]:
    blocks: list[str] = []
    kinds: list[str] = []
    for page_no in spec["pages"]:
        raw, kind = page_text(page_no, source, ocr)
        kinds.append(kind)
        blocks.append(raw)
    if spec["formato"] == "prosa":
        chunks = [paragraphize(block) for block in blocks]
        transcription = "\n\n".join(chunk for chunk in chunks if chunk)
    else:
        chunks = [clean_lines(block) for block in blocks]
        transcription = "\n\n".join(chunk for chunk in chunks if chunk)
    if all(kind == "ocr" for kind in kinds):
        nota = "Transcripción asistida por OCR. Puede contener errores de lectura; el PDF original es la fuente definitiva."
    elif any(kind == "ocr" for kind in kinds):
        nota = "Transcripción mixta: texto digital y OCR. Puede contener errores de lectura; el PDF original es la fuente definitiva."
    else:
        nota = "Transcripción extraída del texto digital del PDF original."
    return transcription, nota, kinds


# ---------------------------------------------------------------------------
# PDF output
# ---------------------------------------------------------------------------
def split_pdfs(source: fitz.Document, specs: Iterable[dict]) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        target = DOCS_DIR / f"{spec['slug']}.pdf"
        out = fitz.open()
        for page_no in spec["pages"]:
            out.insert_pdf(source, from_page=page_no - 1, to_page=page_no - 1)
        out.set_metadata({
            "title": spec["nombre"],
            "author": "Roberto Carlos Cartes Jiménez",
            "subject": spec["descripcion"],
            "creator": "saludrcartes · tools/build_docs.py",
            "producer": "PyMuPDF",
        })
        out.save(target, garbage=3, deflate=True)
        out.close()
        print(f"  split {target.relative_to(ROOT)} ({len(spec['pages'])} pág.)")


def format_pages(pages: list[int]) -> str:
    if not pages:
        return "Sin páginas"
    ranges: list[str] = []
    start = prev = pages[0]
    for page in pages[1:]:
        if page == prev + 1:
            prev = page
            continue
        ranges.append(f"{start}–{prev}" if start != prev else str(start))
        start = prev = page
    ranges.append(f"{start}–{prev}" if start != prev else str(start))
    return ", ".join(ranges)


def build_emergency_pdf() -> None:
    """Create a one-page emergency sheet with the real critical data."""
    from reportlab.lib.pagesizes import A4  # type: ignore
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore
    from reportlab.lib.units import mm  # type: ignore
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle  # type: ignore
    from reportlab.lib import colors  # type: ignore

    target = DOCS_DIR / "emergencia-ficha-resumen.pdf"
    doc = SimpleDocTemplate(str(target), pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm, topMargin=14 * mm, bottomMargin=14 * mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=colors.HexColor("#123F32"), spaceAfter=2)
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=12, textColor=colors.HexColor("#5B6B63"), spaceAfter=10)
    head = ParagraphStyle("head", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=colors.HexColor("#123F32"), spaceBefore=8, spaceAfter=3)
    body = ParagraphStyle("body", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=12, textColor=colors.HexColor("#1E2A24"))
    small = ParagraphStyle("small", parent=body, fontSize=8, leading=10, textColor=colors.HexColor("#5B6B63"))

    story = [
        Paragraph("Ficha de emergencia", title),
        Paragraph("Roberto Carlos Cartes Jiménez · RUT 12.466.937-5 · Nacido el 05-03-1973 · FONASA B", sub),
        Paragraph("Diagnósticos", head),
        Paragraph("ACV isquémico cerebeloso izquierdo secuelado (2019), con hemiparesia braquiocrural izquierda, ataxia y trastorno de la marcha. Insuficiencia cardíaca con FEVI 40–45%, miocardiopatía secundaria a disincronía y BCRI. Diabetes mellitus tipo 2 mal controlada (HbA1c 8,5%). Trastorno de estrés postraumático y psicosis lúcida de origen orgánico. Discapacidad física leve 13,40% con movilidad reducida. Hernia del núcleo pulposo lumbar L5-S1. Túnel carpiano izquierdo operado.", body),
        Paragraph("Alergias", head),
        Paragraph("Sin alergias medicamentosas conocidas.", body),
        Paragraph("Medicamentos actuales", head),
        Paragraph("Bisoprolol 5 mg/día · Empagliflozina 25 mg/día · Furosemida 20 mg/día · Aspirina 100 mg/día · Atorvastatina 20 mg/día · Metformina 850 mg cada 12 h · Semaglutida 0,5 mg/semana · Losartán 25 mg/día · Ácido valproico 250 mg/día · Quetiapina 12,5 mg/día · Pregabalina 75 mg cada 12 h · Tamsulosina 0,4 mg/día.", body),
        Paragraph("Notas para la atención", head),
        Paragraph("Portar el PDF del expediente en cada control. No suspender la medicación cardíaca ni psiquiátrica sin indicación. Confirmar los teléfonos antes de una urgencia. Ante riesgo vital, llamar al SAMU 131.", body),
        Spacer(1, 6),
        Paragraph("Contactos", head),
    ]
    data = [
        ["Contacto", "Relación", "Teléfono"],
        ["Allan", "Hijo", "+56 9 7188 8887"],
        ["Nicholas", "Hijo", "+56 9 7850 2717"],
        ["Luis", "Cuñado", "+56 9 9827 1956"],
        ["SAMU", "Emergencia", "131"],
        ["Carabineros", "Emergencia", "133"],
        ["Bomberos", "Emergencia", "132"],
    ]
    table = Table(data, colWidths=[45 * mm, 45 * mm, 55 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#123F32")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D8D2C4")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFF8F0"), colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 8))
    story.append(Paragraph("Documento generado desde saludrcartes. No reemplaza la evaluación médica. Actualizado 19-11-2026.", small))
    doc.build(story)
    print(f"  wrote {target.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(
            f"No se encontró el PDF de origen: {SOURCE}\n"
            "Defina la variable SALUD_PDF con la ruta del archivo."
        )
    print(f"Opening {SOURCE}")
    source = fitz.open(SOURCE)
    ocr = load_ocr()
    print(f"  {source.page_count} pages · {len(ocr)} OCR pages")

    split_pdfs(source, DOC_SPECS)

    documents = []
    for spec in DOC_SPECS:
        transcription, nota, kinds = build_transcription(spec, source, ocr)
        target = DOCS_DIR / f"{spec['slug']}.pdf"
        doc = {
            "id": spec["id"],
            "slug": spec["slug"],
            "categoria_id": spec["cat"],
            "afeccion_id": spec.get("afeccion"),
            "nombre": spec["nombre"],
            "archivo": f"assets/docs/{spec['slug']}.pdf",
            "tipo_archivo": "PDF",
            "fecha": spec["fecha"],
            "tamano": f"{len(spec['pages'])} pág{'s' if len(spec['pages']) != 1 else ''}.",
            "descripcion": spec["descripcion"],
            "descripcion_larga": spec["descripcion_larga"],
            "transcripcion": transcription,
            "nota_transcripcion": nota,
            "formato": "prosa" if spec["formato"] == "prosa" else "lineas",
            "folios": f"Páginas {format_pages(spec['pages'])} del archivo original",
            "fuente": spec["fuente"],
            "paginas_originales": spec["pages"],
            "sheet_url": f"doc-{spec['slug']}.html",
            "bytes": target.stat().st_size,
            "origen_transcripcion": "ocr" if all(k == "ocr" for k in kinds) else ("mixto" if any(k == "ocr" for k in kinds) else "texto"),
        }
        documents.append(doc)

    documents.sort(key=lambda item: item["nombre"].lower())
    payload = {
        "meta": {
            "fuente": "Archivo personal «archivos saludrcartes 01.pdf»",
            "total_paginas": source.page_count,
            "total_documentos": len(documents),
            "generado": "2026-11-19",
            "nota": (
                "Se excluyeron la página 55 (cédula de identidad) y las páginas 72–73 "
                "(publicación del Diario Oficial sobre un tercero), por tratarse de datos de identificación "
                "y de un documento ajeno al expediente. El resto del archivo se conserva en PDF."
            ),
            "nota_ocr": (
                "Los documentos escaneados se transcribieron con OCR. La transcripción es una ayuda de lectura; "
                "el PDF original es la fuente definitiva."
            ),
        },
        "documentos": documents,
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  wrote {OUT_PATH.relative_to(ROOT)} ({len(documents)} documents)")

    build_emergency_pdf()
    source.close()


if __name__ == "__main__":
    main()
