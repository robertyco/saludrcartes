"""Normalise the clinical dataset and add editorial metadata for the new site."""
import json
from pathlib import Path

ROOT = Path(".")
SRC = ROOT / "registro.json"
DST = ROOT / "data" / "registro.json"
DST.parent.mkdir(parents=True, exist_ok=True)

data = json.loads(SRC.read_text(encoding="utf-8"))

PAGE_EXTRA = {
    "diagnosticos": {
        "numero": "01",
        "heroLine": "Lo que ya tiene nombre.",
        "caption": "Nombrar lo que pasa es el primer cuidado.",
        "keywords": "diagnóstico CIE-10 lumbalgia hombro túnel carpiano cefalea colesterol rinitis gastritis",
        "metaTitle": "Diagnósticos",
    },
    "medicamentos": {
        "numero": "02",
        "heroLine": "Qué tomas, cuándo y por qué.",
        "caption": "Cada dosis tiene un porqué.",
        "keywords": "medicamentos receta paracetamol ibuprofeno vitamina D omeprazol alergia penicilina polen",
        "metaTitle": "Medicamentos y alergias",
    },
    "laboratorio": {
        "numero": "03",
        "heroLine": "Los números detrás del cuidado.",
        "caption": "Pequeños datos, una lectura completa.",
        "keywords": "laboratorio hemograma perfil lipídico colesterol LDL HDL glicemia creatinina TSH vitamina D",
        "metaTitle": "Laboratorio",
    },
    "neurologia": {
        "numero": "04",
        "heroLine": "La red que ordena el día.",
        "caption": "La red que sostiene la calma.",
        "keywords": "neurología cefalea tensional EEG electroencefalograma",
        "metaTitle": "Neurología",
    },
    "cardiologia": {
        "numero": "05",
        "heroLine": "El pulso de tu historia.",
        "caption": "Un ritmo que acompaña todo.",
        "keywords": "cardiología corazón ECG electrocardiograma ecocardiograma presión arterial",
        "metaTitle": "Cardiología",
    },
    "fisiatria": {
        "numero": "06",
        "heroLine": "Moverse sin miedo.",
        "caption": "El cuerpo aprendiendo a moverse de nuevo.",
        "keywords": "fisiatría evaluación funcional rehabilitación fuerza movilidad dolor lumbar hombro",
        "metaTitle": "Fisiatría",
    },
    "rehabilitacion": {
        "numero": "07",
        "heroLine": "Volver a tu cuerpo, paso a paso.",
        "caption": "Volver, paso a paso.",
        "keywords": "rehabilitación kinesiología sesiones progreso objetivos terapia",
        "metaTitle": "Rehabilitación",
    },
    "fonoaudiologia": {
        "numero": "08",
        "heroLine": "La voz que te representa.",
        "caption": "La voz también se cuida.",
        "keywords": "fonoaudiología habla voz deglución fatiga vocal",
        "metaTitle": "Fonoaudiología",
    },
    "psiquiatria": {
        "numero": "09",
        "heroLine": "Un espacio para estar bien.",
        "caption": "Un lugar seguro para la mente.",
        "keywords": "psiquiatría salud mental ansiedad sueño terapia confidencial",
        "metaTitle": "Psiquiatría",
    },
    "traumatologia-superior": {
        "numero": "10",
        "heroLine": "Hombro, mano y fuerza.",
        "caption": "Fuerza que se reconstruye.",
        "keywords": "traumatología superior hombro supraespinosa túnel carpiano mano ecografía",
        "metaTitle": "Traumatología superior",
    },
    "traumatologia-inferior": {
        "numero": "11",
        "heroLine": "La base de cada paso.",
        "caption": "La columna que nos sostiene.",
        "keywords": "traumatología inferior columna lumbar lumbalgia resonancia espalda",
        "metaTitle": "Traumatología inferior",
    },
    "emergencia": {
        "numero": "12",
        "heroLine": "Todo lo crítico, al instante.",
        "caption": "Cuando cada segundo cuenta.",
        "keywords": "emergencia urgencia contactos grupo sanguíneo alergias SAMU 131",
        "metaTitle": "Contactos de emergencia",
    },
}

for cat in data["categorias"]:
    extra = PAGE_EXTRA[cat["slug"]]
    cat.update(extra)
    cat["arte"] = f"assets/img/art/{cat['slug']}.svg"
    cat["url"] = "emergencia.html" if cat["slug"] == "emergencia" else f"{cat['slug']}.html"
    cat["navLabel"] = {
        "medicamentos": "Medicamentos y alergias",
        "traumatologia-superior": "Traumatología superior",
        "traumatologia-inferior": "Traumatología inferior",
    }.get(cat["slug"], cat["nombre"])

# The emergency page is the public ficha: keep its contact set aligned with the
# critical data and the public profile.
data["sitio"] = {
    "nombre": "saludrcartes",
    "titular": data["meta"]["titular"],
    "preferido": data["perfil"]["preferido"],
    "lema": "Tu historia clínica, con calidez y a mano.",
    "descripcion": "Registro clínico personal de Roberto Carlos Cartes Jiménez. Diagnósticos, tratamiento, especialidades y documentos en un solo lugar.",
    "version": "2.0.0",
    "anio": 2026,
    "actualizado": "2026-10-28",
}

# Derived labels and counts used by the templates.
data["resumen_sitio"] = {
    "paginas": 13,
    "capitulos": 12,
    "especialidades": 8,
    "documentos": len(data["documentos"]),
    "diagnosticos": len([a for a in data["afecciones"] if a.get("cie10")]),
    "medicamentos_activos": len([m for m in data["medicamentos"] if m.get("activo")]),
}

data["grupos"][0]["color"] = "verde"
data["grupos"][1]["color"] = "violeta"
data["grupos"][2]["color"] = "coral"

DST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote {DST} ({DST.stat().st_size/1024:.1f} KB)")
