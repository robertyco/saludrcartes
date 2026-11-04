# saludrcartes

Registro clínico personal de **Roberto Carlos Cartes Jiménez**.

- **Acceso:** libre, sin usuario ni clave, según la sección 4 del SDD.
- **Estado:** 13 páginas (Inicio + 12 páginas clínicas), 19 PDF de ejemplo y ficha pública de emergencia.
- **Diseño:** paleta del SDD con **oro #D4AF37** y **plata #C0C7CE** incorporados; Quicksand + Inter; WCAG 2.1 AA.
- **Pila:** HTML/CSS/JS estático, Netlify Functions y Supabase opcional para el modo privado.
- **Contenido:** los datos clínicos actuales son de ejemplo. Reemplaza `assets/js/data/clinica.js`, `assets/js/data/emergencia.js` y los PDF antes de usar el sitio con información real.

## Estructura rápida

- `index.html` — shell del registro, navegación por hash y páginas clínicas.
- `emergencia.html` — ficha pública mínima; solo carga `data/emergencia.js`.
- `assets/js/app.js` + `views-*.js` — aplicación y plantillas compartidas.
- `assets/js/data/clinica.js` — dataset clínico de ejemplo (`meta.demo: true`).
- `assets/js/data/emergencia.js` — datos críticos mínimos de la ficha pública.
- `assets/docs/` — 19 PDF de ejemplo marcados como documentos sin valor clínico.
- `assets/css/` — base, páginas, overlays, responsive, impresión y emergencia.
- `netlify.toml`, `_headers`, `manifest.webmanifest` — despliegue, seguridad y PWA.

## Acceso público y modo privado

El valor por defecto es `auth.mode = 'public'` en `assets/js/config.js`:

- El sitio abre directamente el registro, sin pantalla de login.
- No se cargan credenciales de demostración.
- Supabase no se descarga en modo público: no hay peticiones a terceros.

Si más adelante quieres proteger el historial:

1. Cambia `auth.mode` a `'supabase'`.
2. Configura Supabase Auth, las tablas y las políticas RLS.
3. Revisa `docs/SUPABASE.md` y `docs/SEGURIDAD.md`.

La pantalla de login sigue disponible para ese modo, pero permanece oculta mientras el acceso sea libre.

## Paleta

| Color | Hex |
| --- | --- |
| Verde | `#0E9F6E` |
| Turquesa | `#38BDF8` |
| Coral | `#FF6B6B` |
| Amarillo | `#FFC94A` |
| Violeta | `#8B5CF6` |
| Crema | `#FFF8F0` |
| Tinta | `#1F2937` |
| Blanco | `#FFFFFF` |
| **Oro** | `#D4AF37` |
| **Plata** | `#C0C7CE` |

El oro destaca documentos y respaldos clínicos; la plata identifica archivos y metadatos. Ambos se combinan con texto oscuro para conservar el contraste AA.

## Accesibilidad

- Navegación por teclado y foco visible.
- Enlace para saltar al contenido.
- Tamaño de texto ajustable y modo de alto contraste.
- Preferencia de movimiento reducido.
- Objetivos táctiles de al menos 44 × 44 px.
- Estados con icono y texto, no solo color.

## Documentación

- `docs/CONTENIDO.md` — rutas, datos y plantillas.
- `docs/SEGURIDAD.md` — modelo de acceso y recomendaciones.
- `docs/SUPABASE.md` — pasos para el modo privado.
- `docs/DESPLIEGUE.md` — Netlify, cabeceras y verificación.

## Documentos de ejemplo

Todos los PDF de `assets/docs/` son ficticios. El generador está en `tools/generate-demo-pdfs.py` (PyMuPDF + fuentes locales). Reemplázalos por tus informes reales y actualiza las rutas en `clinica.js`.
