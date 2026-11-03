/* ============================================================================
   auth.js — Autenticación Supabase (Fase 2)
   ----------------------------------------------------------------------------
   Usa @supabase/supabase-js desde CDN. No requiere build step.
   ---------------------------------------- */
window.AUTH_SUPA = {
  // Inicializa el cliente una sola vez
  init() {
    if (window.sbInited) return;
    window.sbInited = true;
    this.client = supabase.createClient(
      SALUD_CONFIG.supabase.url,
      SALUD_CONFIG.supabase.anonKey
    );
  },
  // Login con credenciales reales
  async login(email, password) {
    this.init();
    const { error, data } = await this.client.auth.signInWithPassword({ email, password });
    if (error) throw error;
    // Guarda sesión en sessionStorage (sobrevive recarga)
    sessionStorage.setItem('supabase_session', JSON.stringify(data.session));
    return data;
  },
  // Ver usuario actual
  async getUser() {
    this.init();
    const { data } = await this.client.auth.getUser();
    return data.user;
  },
  // Cerrar sesión
  async logout() {
    this.init();
    await this.client.auth.signOut();
    sessionStorage.removeItem('supabase_session');
  }
};