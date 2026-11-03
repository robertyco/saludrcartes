# Contenido del sitio

## Estructura de rutas (hash routing)

- `#/` — Inicio: 12 tarjetas agrupadas en 3 bloques (Registro clínico, Especialidades médicas, Emergencia) + CTA fijo de emergencia coral.
- `#/categoria/:slug` — Página de una categoría (diagnósticos, medicamentos, laboratorio, 8 especialidades, emergencia).
- `#/documentos` — Biblioteca de documentos con filtros por categoría.
- `#/acerca` — Acerca y privacidad.

## Datos

- `assets/js/data/clinica.js` — dataset completo de ejemplo (`meta.demo = true`).
- `assets/js/data/emergencia.js` — datos críticos mínimos para la ficha pública.
- `assets/docs/` — 19 PDFs de ejemplo (marcados “DOCUMENTO DE EJEMPLO — SIN VALOR CLÍNICO”).

## Plantillas compartidas

Cada página de categoría comparte:
- Encabezado con estado, fecha y médico tratante.
- Resumen.
- Línea de tiempo de evolución (ordenada por fecha).
- Documentos descargables.
- Notas actuales / tratamiento.

## Accesibilidad

- Navegación por teclado, foco visible (outline 3px), saltos al contenido principal.
- Control de tamaño de texto (md / lg / xl).
- Modo alto contraste.
- Preferencia de movimiento reducido.
- Objetivos táctiles ≥ 44×44 px.
- WCAG 2.1 AA (axe-core verificado en escritorio, tableta y móvil).