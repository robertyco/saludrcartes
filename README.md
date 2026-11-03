# saludrcartes

Registro clínico personal de **Roberto Carlos Cartes Jiménez**.

- **Modo actual:** demostración (datos de ejemplo, autenticación local)
- **Estado:** 13 páginas completas (Inicio + 12 contenido), 19 PDFs de ejemplo, accesibilidad verificada (keyboard, focus, alta contraste, tamaño de texto, 44×44 px)
- **Pila:** HTML/CSS/JS estático, Netlify Functions (firmado), Supabase (fase 2), PWA (manifest + service worker básico)
- **No se publica con datos reales** hasta conectar Supabase Auth + RLS y reemplazar `clinica.js`

## Estructura rápida

- `index.html` — login + app shell (hash routing)
- `emergencia.html` — ficha pública mínima (solo `emergencia.js` + `data/emergencia.js`)
- `assets/js/app.js` + `views-*.js` — aplicación
- `assets/js/data/clinica.js` — datos de ejemplo (marcados `demo: true`)
- `assets/js/data/emergencia.js` — datos críticos mínimos (no expone historial)
- `assets/docs/` — 19 PDFs de ejemplo (todos marcados “DOCUMENTO DE EJEMPLO — SIN VALOR CLÍNICO”)
- `assets/css/` — base, páginas, overlays, responsive, impresión, emergencia
- `netlify.toml` + `_headers` + `manifest.webmanifest`

## Credenciales demo

- Correo: `roberto@saludrcartes.cl`
- Clave: `saludrcartes`

## Documentos generados

Todos los PDFs en `assets/docs/` son de ejemplo; los nombres coinciden con `clinica.js`. Generador: `tools/generate-demo-pdfs.py` (PyMuPDF + fuentes locales).
