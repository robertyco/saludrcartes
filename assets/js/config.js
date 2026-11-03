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
  demo: true,

  auth: {
    mode: 'demo', // 'demo' | 'supabase'
    demoUser: {
      email: 'roberto@saludrcartes.cl',
      password: 'saludrcartes',
      nombre: 'Roberto'
    },
    sessionKey: 'saludrcartes.sesion',
    sessionHours: 12,
    rememberDays: 30
  },

  /* Fase 2: completa estos valores y cambia auth.mode a 'supabase'.
     La guía está en docs/SEGURIDAD.md y docs/SUPABASE.md. */
  supabase: {
    url: '',
    anonKey: '',
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
