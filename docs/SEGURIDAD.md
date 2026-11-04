# Seguridad

## Modelo actual: acceso libre

El SDD define el ingreso **sin usuario y clave** (sección 4). Por eso el sitio abre directamente el registro y no muestra credenciales de demostración.

Eso significa que cualquier persona con la URL puede leer el contenido publicado. Las protecciones actuales son de exposición, no de autenticación:

- `noindex`, `nofollow`, `noarchive` y `nosnippet` en las páginas.
- `robots.txt` con `Disallow: /`.
- `_headers` con CSP, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` y HSTS.
- La ficha de emergencia (`emergencia.html`) carga solo `data/emergencia.js`; nunca importa `clinica.js`.
- Los documentos viven en `assets/docs/` y son estáticos.

**Importante:** un archivo JavaScript estático se puede descargar aunque exista una pantalla de login. Si el registro contiene datos clínicos reales y quieres restringir su lectura, no basta con ocultar la interfaz: hay que mover los datos a un backend con permisos.

## Antes de publicar datos reales

1. Reemplaza los datos de ejemplo y los PDF.
2. Cambia `meta.demo` a `false` en `clinica.js` y `emergencia.js`.
3. Revisa la normativa aplicable, el consentimiento del titular y el riesgo de exponer información de salud en un sitio público.
4. Si decides mantener el acceso libre, asume que la URL es el único control de acceso. No la publiques en buscadores, redes ni listados.
5. Si decides protegerlo, activa el modo privado descrito abajo.

## Modo privado opcional

- `assets/js/config.js`: `auth.mode = 'supabase'`.
- Supabase Auth con correo y clave.
- RLS en todas las tablas clínicas (`auth.uid() = owner_id`).
- Bucket `documentos-clinicos` privado y URLs firmadas de corta duración mediante `netlify/functions/signed-url.js`.
- La `anonKey` es pública por diseño. **Nunca** pongas la `service_role` en el frontend ni en el repositorio.
- Variables de entorno de Netlify: `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY` solo para la función.

## Cabeceras y caché

- `_headers` permite `script-src 'self' https://cdn.jsdelivr.net` para que el modo privado pueda cargar Supabase bajo demanda.
- `connect-src` incluye `https://*.supabase.co` y `wss://*.supabase.co`.
- `index.html`, `emergencia.html`, `assets/js/data/*` y `assets/docs/*` usan `no-store`.
- Las fuentes e imágenes públicas tienen caché larga.

## Rutas

- `index.html` — registro completo.
- `emergencia.html` — ficha mínima, sin historial.
- `netlify.toml` — redirección `/emergencia` → `/emergencia.html`.
