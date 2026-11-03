# Despliegue

- Netlify: publica `.` con `netlify.toml`; funciones en `netlify/functions` (`node_bundler = esbuild`).
- CSP: `script-src 'self'`, `style-src 'self' 'unsafe-inline'`, `connect-src 'self' https://*.supabase.co`.
- `robots.txt`: `Disallow: /`; `noindex/nofollow` en meta + `_headers`.
- Demo: no publicar con datos reales hasta Supabase + RLS.
