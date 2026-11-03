# Supabase (fase 2)

- Editar `assets/js/config.js`: `url`, `anonKey`, `bucket` y `auth.mode = 'supabase'`.
- Reemplazar `auth.js` por `@supabase/supabase-js` (`auth.signInWithPassword`, JWT).
- Esquema sugerido: `profiles` + `clinical_records` con `owner_id uuid` y RLS (`auth.uid() = owner_id`).
- Documentos privados: bucket `documentos-clinicos` (`public: false`) + `netlify/functions/signed-url.js`.
- PDFs actuales (`assets/docs/`) son estáticos y solo para la demo.
