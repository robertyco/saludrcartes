# Supabase (modo privado opcional)

El sitio funciona sin Supabase en modo público. Esta guía es para cuando quieras exigir inicio de sesión y proteger los datos.

## 1. Configuración

Edita `assets/js/config.js`:

```js
auth: {
  mode: 'supabase'
},
supabase: {
  url: 'https://TU-PROYECTO.supabase.co',
  anonKey: 'TU_ANON_KEY',
  bucket: 'documentos-clinicos'
}
```

La `anonKey` puede estar en el frontend; la seguridad real depende de RLS. No publiques la `service_role`.

## 2. Esquema mínimo

Tablas sugeridas, alineadas al SDD:

- `categoria` — secciones clínicas y especialidades.
- `afeccion` — diagnósticos, evolución y notas.
- `documento` — metadatos y `url_storage`; nunca el archivo dentro de la tabla.
- `medicamento` — tratamiento activo.
- `alergia` — sustancia, severidad y reacción.
- `contacto_emergencia` — contactos y visibilidad pública.

Agrega `owner_id uuid` y políticas RLS del tipo:

```sql
create policy "leer propias filas"
on public.afeccion for select
using (auth.uid() = owner_id);
```

Repite el patrón para lectura y escritura en cada tabla clínica.

## 3. Usuario

1. Crea el usuario en Supabase Auth.
2. Desactiva el registro público si el sitio es de una sola persona.
3. Prueba inicio de sesión, recuperación de clave y cierre de sesión.

## 4. Documentos

1. Crea el bucket `documentos-clinicos` con acceso privado.
2. Sube un objeto por documento.
3. Guarda solo la ruta en `documento.url_storage`.
4. La función `netlify/functions/signed-url.js` genera URLs temporales.

Variables de entorno en Netlify:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY` (solo función; nunca en el navegador)

## 5. Verificación

- Sin sesión, el registro no debe renderizar datos.
- Con sesión, solo deben aparecer las filas del titular.
- Los enlaces de documentos deben caducar.
- El modo público debe seguir funcionando si vuelves a `auth.mode = 'public'`.
