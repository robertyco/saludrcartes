# Contenido del sitio

## Rutas (hash routing)

- `#/` — Inicio: 12 tarjetas agrupadas en 3 bloques (Registro clínico, Especialidades médicas y Emergencia) + CTA fijo de emergencia coral.
- `#/categoria/:slug` — página de una categoría: diagnósticos, medicamentos, laboratorio, las 8 especialidades y contactos de emergencia.
- `#/documentos` — biblioteca de documentos con filtros por categoría.
- `#/acerca` — Acerca, privacidad y paleta.

## Datos

- `assets/js/data/clinica.js` — dataset completo de ejemplo (`meta.demo = true`).
- `assets/js/data/emergencia.js` — datos críticos mínimos para la ficha pública (`meta.demo = true`).
- `assets/docs/` — 19 PDF de ejemplo marcados como “DOCUMENTO DE EJEMPLO — SIN VALOR CLÍNICO”.

Al reemplazar los datos:

1. Edita el perfil, las categorías, las afecciones, los medicamentos, las alergias, los contactos y los documentos.
2. Actualiza las rutas de los PDF en `documentos`.
3. Cambia `meta.demo` a `false` en ambos archivos.
4. Verifica que la ficha de emergencia no incluya datos que no quieras exponer.

## Plantillas compartidas

Cada página de categoría comparte:

- Encabezado con estado, fecha y profesional tratante.
- Resumen.
- Línea de evolución ordenada por fecha.
- Documentos descargables con acento dorado.
- Notas actuales y tratamiento.

## Paleta

- Verde `#0E9F6E`, turquesa `#38BDF8`, coral `#FF6B6B`, amarillo `#FFC94A`, violeta `#8B5CF6`.
- Crema `#FFF8F0`, tinta `#1F2937`, blanco `#FFFFFF`.
- Oro `#D4AF37` para documentos y respaldos.
- Plata `#C0C7CE` para archivos y metadatos.

## Accesibilidad

- Navegación por teclado, foco visible (outline de 3 px) y salto al contenido.
- Control de tamaño de texto (md / lg / xl).
- Modo de alto contraste.
- Preferencia de movimiento reducido.
- Objetivos táctiles de 44 × 44 px.
- WCAG 2.1 AA: contraste, estructura semántica y estados que no dependen solo del color.
