# Despliegue

## Netlify

- El sitio publica la raíz del repositorio (`.`) con `netlify.toml`.
- Las funciones viven en `netlify/functions` y usan `node_bundler = "esbuild"`.
- URL del sitio: <https://saludrcartes.netlify.app/>.
- Redirección corta: `/emergencia` → `/emergencia.html`.

Desde una terminal vinculada al sitio correcto:

```bash
netlify deploy --prod
```

También puedes publicar desde el panel de Netlify conectando el repositorio de GitHub. Si el CLI no encuentra el sitio, verifica `netlify status` y `netlify link` antes de desplegar.

## Cabeceras

`_headers` define:

- CSP con `script-src 'self' https://cdn.jsdelivr.net` (Supabase se carga solo en modo privado).
- `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` y HSTS.
- `noindex` para las páginas principales.
- `no-store` para HTML, datos clínicos y documentos.
- Caché larga para fuentes e imágenes.

## Verificación después del despliegue

1. Abre `https://saludrcartes.netlify.app/` y confirma que entra directo al registro, sin login.
2. Recorre Inicio, una especialidad, la biblioteca de documentos y Acerca.
3. Abre `https://saludrcartes.netlify.app/emergencia.html`.
4. Comprueba que la ficha de emergencia muestra el aviso de ejemplo mientras `meta.demo` sea `true`.
5. Prueba la impresión y la descarga del PDF.
6. Revisa la consola del navegador: no debe haber errores de carga.
7. Verifica que `assets/js/data/clinica.js` no contenga datos reales hasta que decidas publicarlos.

## Antes de datos reales

- Reemplaza datos y PDF.
- Ajusta `meta.demo` a `false`.
- Decide entre acceso libre y modo privado con Supabase Auth + RLS.
- Revisa `docs/SEGURIDAD.md`.
