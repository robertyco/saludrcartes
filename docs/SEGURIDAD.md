# Seguridad

- **No usar datos reales** hasta conectar Supabase Auth + RLS.
- El archivo `clinica.js` contiene solo datos de ejemplo y está marcado `demo: true`.
- La ficha pública (`emergencia.html`) carga **solo** `emergencia.js` y nunca importa `clinica.js`; no expone historial.
- `_headers` establece CSP (`script-src 'self'`, `frame-src 'self'`, `connect-src 'self' https://*.supabase.co`), `noindex/nofollow` y caché controlado.
- `robots.txt`: `Disallow: /`.
- `netlify.toml`: redirección `/emergencia` → `emergencia.html`; funciones en `netlify/functions`.
- El flujo de login es demo (`localStorage`/`sessionStorage`). En producción reemplazar por Supabase Auth y usar `signed-url.js` para documentos privados.
