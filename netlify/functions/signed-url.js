/* ==========================================================================
   netlify/functions/signed-url.js
   --------------------------------------------------------------------------
   Endpoint Netlify para crear URLs firmadas de Supabase Storage.
   Recibe POST { "file": "ruta/al/archivo.pdf" } y devuelve URL temporal.
   ------------------------------------------------------ */
exports.handler = async (event) => {
  // Permitir tanto Netlify Functions v2 como v1
  if (event.httpMethod && event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    const { createClient } = require('@supabase/supabase-js');
    const supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    const body = event.body ? JSON.parse(event.body) : {};
    const { file } = body; // ej: "documentos-clinicos/foo.pdf"

    if (!file) {
      return {
        statusCode: 400,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: 'Parámetro "file" requerido' })
      };
    }

    const { data, error } = await supabase.storage
      .from('documentos-clinicos')
      .createSignedUrl(file, 300); // 300 segundos = 5 min

    if (error) {
      return {
        statusCode: 400,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: error.message })
      };
    }

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: data?.signedUrl, expiresIn: 300 })
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message })
    };
  }
};