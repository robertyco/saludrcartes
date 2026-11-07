# saludrcartes

Registro clínico personal de **Roberto Carlos Cartes Jiménez**, construido como sitio estático de 13 páginas. El objetivo es que cualquier persona —Roberto, su familia o un equipo de salud— encuentre en segundos lo que necesita, incluso en una urgencia.

> Los teléfonos de contacto fueron entregados por el titular. El centro asistencial aún no está confirmado y debe verificarse antes de una urgencia.

## Páginas

| Archivo | Capítulo | Grupo |
|---|---|---|
| `index.html` | Inicio | Portada |
| `diagnosticos.html` | Diagnósticos | Registro clínico |
| `medicamentos.html` | Medicamentos y alergias | Registro clínico |
| `laboratorio.html` | Laboratorio | Registro clínico |
| `neurologia.html` | Neurología | Especialidades médicas |
| `cardiologia.html` | Cardiología | Especialidades médicas |
| `fisiatria.html` | Fisiatría | Especialidades médicas |
| `rehabilitacion.html` | Rehabilitación | Especialidades médicas |
| `fonoaudiologia.html` | Fonoaudiología | Especialidades médicas |
| `psiquiatria.html` | Psiquiatría | Especialidades médicas |
| `traumatologia-superior.html` | Traumatología superior | Especialidades médicas |
| `traumatologia-inferior.html` | Traumatología inferior | Especialidades médicas |
| `emergencia.html` | Contactos de emergencia | Emergencia |

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
