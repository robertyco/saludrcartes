/* ============================================================================
   saludrcartes — Configuración del sitio
   ----------------------------------------------------------------------------
   Este archivo es el único que necesitas tocar para cambiar el modo de
   autenticación o conectar Supabase en una fase posterior.
   ========================================================================== */

window.SALUD_CONFIG = {
  sitio: 'saludrcartes',
  lema: 'Tu historia clínica, con calidez y a mano.',
  version: '1.0.0',
  anio: 2026,

  /* Modo demostración: muestra un aviso visible y credenciales de prueba.
     Cámbialo a false cuando uses datos reales y autenticación real. */
  demo: false,

  auth: {
    mode: 'supabase', // 'demo' | 'supabase'
    sessionKey: 'saludrcartes.sesion',
    sessionHours: 12,
    rememberDays: 30
  },

  /* Fase 2: completa estos valores y cambia auth.mode a 'supabase'.
     La guía está en docs/SEGURIDAD.md y docs/SUPABASE.md. */
  supabase: {
    url: 'https://hwgmclnoabyjckpehuvc.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh3Z21jbG5vYWJ5amNrcGVodXZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM2NDY4NDcsImV4cCI6MjEwOTIyMjg0N30.CjYf9NcgP-bchKxmz2VxuD1bnffyBRLZf6Ru5kNBKJk',
    bucket: 'documentos-clinicos'
  },

  rutas: {
    emergenciaPublica: 'emergencia.html',
    inicio: 'index.html'
  },

  formatos: {
    locale: 'es-CL',
    moneda: 'CLP'
  }
};
