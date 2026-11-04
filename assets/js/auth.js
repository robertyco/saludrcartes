/* ============================================================================
   saludrcartes — Acceso y arranque
   ----------------------------------------------------------------------------
   Modo 'public'  : acceso libre, sin usuario ni clave (SDD, sección 4).
   Modo 'supabase': login con Supabase Auth antes de cargar el registro
                    (SDD, sección 9). La clave anónima es pública por diseño;
                    la protección real vive en RLS y en el backend.

   Supabase se carga bajo demanda: en modo público el sitio no hace ninguna
   petición a terceros.
   ========================================================================== */

(function () {
  'use strict';

  const CONFIG = window.SALUD_CONFIG;
  const loginView = document.getElementById('vista-login');
  const appView = document.getElementById('vista-app');
  const form = document.getElementById('login-form');
  const emailInput = document.getElementById('login-email');
  const passwordInput = document.getElementById('login-password');
  const errorBox = document.getElementById('login-error');
  const errorText = document.getElementById('login-error-text');
  const submitButton = document.getElementById('login-submit');
  const submitLabel = document.getElementById('login-submit-label');

  let client = null;
  let booted = false;
  let supabaseLoader = null;

  function loadSupabase() {
    if (window.supabase && window.supabase.createClient) return Promise.resolve();
    if (supabaseLoader) return supabaseLoader;

    supabaseLoader = new Promise(function (resolve, reject) {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js';
      script.async = true;
      script.crossOrigin = 'anonymous';
      script.onload = function () {
        if (window.supabase && window.supabase.createClient) resolve();
        else reject(new Error('Supabase se cargó, pero no está disponible.'));
      };
      script.onerror = function () {
        supabaseLoader = null;
        reject(new Error('No se pudo cargar Supabase. Revisa la conexión e inténtalo de nuevo.'));
      };
      document.head.appendChild(script);
    });

    return supabaseLoader;
  }

  async function createClient() {
    if (client) return client;
    if (!CONFIG.supabase || !CONFIG.supabase.url || !CONFIG.supabase.anonKey) {
      throw new Error('Falta configurar la URL y la clave anónima de Supabase.');
    }
    await loadSupabase();
    client = window.supabase.createClient(CONFIG.supabase.url, CONFIG.supabase.anonKey);
    return client;
  }

  function showError(message) {
    if (!errorBox || !errorText) return;
    errorText.textContent = message;
    errorBox.hidden = false;
  }

  function clearError() {
    if (errorBox) errorBox.hidden = true;
  }

  function setBusy(busy) {
    if (!submitButton) return;
    submitButton.disabled = busy;
    if (submitLabel) submitLabel.textContent = busy ? 'Entrando…' : 'Entrar a mi registro';
  }

  function applyModeChrome(mode) {
    const isPublic = mode !== 'supabase';
    const logoutButton = document.getElementById('drawer-logout');
    const modeLabel = document.getElementById('drawer-user-mode');
    if (logoutButton) logoutButton.hidden = isPublic;
    if (modeLabel) modeLabel.textContent = isPublic ? 'Acceso libre' : 'Sesión privada';
    document.documentElement.setAttribute('data-auth', isPublic ? 'public' : 'private');
  }

  function showLogin() {
    if (appView) appView.hidden = true;
    if (loginView) loginView.hidden = false;
    const target = emailInput || passwordInput;
    if (target) window.setTimeout(function () { target.focus(); }, 60);
  }

  function bootApp() {
    if (booted) return;
    if (!window.SaludApp || typeof window.SaludApp.init !== 'function') {
      console.error('[saludrcartes] No se encontró el núcleo de la aplicación.');
      return;
    }
    if (!window.SALUD_DATA) {
      console.error('[saludrcartes] No se encontraron los datos clínicos.');
      return;
    }
    booted = true;
    if (loginView) loginView.hidden = true;
    if (appView) appView.hidden = false;
    window.SaludApp.init(window.SALUD_DATA);
  }

  async function login(event) {
    event.preventDefault();
    clearError();
    const email = (emailInput && emailInput.value || '').trim();
    const password = passwordInput ? passwordInput.value : '';

    if (!email || !password) {
      showError('Escribe tu correo y tu clave.');
      return;
    }

    setBusy(true);
    try {
      const sb = await createClient();
      const { error } = await sb.auth.signInWithPassword({ email: email, password: password });
      if (error) {
        showError(error.message === 'Invalid login credentials'
          ? 'El correo o la clave no son correctos.'
          : error.message);
        return;
      }
      bootApp();
    } catch (error) {
      showError(error && error.message ? error.message : 'No se pudo iniciar sesión.');
    } finally {
      setBusy(false);
    }
  }

  async function logout() {
    try {
      if (client) await client.auth.signOut();
    } catch (error) {
      /* La sesión local se limpia igualmente. */
    }
    booted = false;
    window.location.hash = '#/';
    showLogin();
  }

  function bindLogin() {
    if (!form || form.dataset.bound === 'true') return;
    form.dataset.bound = 'true';
    form.addEventListener('submit', login);

    const toggle = document.getElementById('toggle-password');
    if (toggle && passwordInput) {
      toggle.addEventListener('click', function () {
        const show = passwordInput.type === 'password';
        passwordInput.type = show ? 'text' : 'password';
        toggle.setAttribute('aria-pressed', show ? 'true' : 'false');
        toggle.setAttribute('aria-label', show ? 'Ocultar clave' : 'Mostrar clave');
        passwordInput.focus();
      });
    }

    const forgot = document.getElementById('forgot-link');
    if (forgot) {
      forgot.addEventListener('click', async function (event) {
        event.preventDefault();
        const email = (emailInput && emailInput.value || '').trim();
        if (!email) {
          showError('Escribe tu correo para enviarte el enlace de recuperación.');
          return;
        }
        try {
          const sb = await createClient();
          const { error } = await sb.auth.resetPasswordForEmail(email, {
            redirectTo: window.location.origin + window.location.pathname
          });
          if (error) showError(error.message);
          else if (window.SaludToast) window.SaludToast.show('Te enviamos un enlace de recuperación.', 'success');
        } catch (error) {
          showError(error && error.message ? error.message : 'No se pudo enviar el enlace.');
        }
      });
    }
  }

  async function start() {
    const mode = CONFIG.auth && CONFIG.auth.mode;
    applyModeChrome(mode);

    if (mode !== 'supabase') {
      bootApp();
      return;
    }

    bindLogin();
    try {
      const sb = await createClient();
      const { data } = await sb.auth.getSession();
      if (data && data.session) bootApp();
      else showLogin();
    } catch (error) {
      showError(error && error.message ? error.message : 'No se pudo comprobar la sesión.');
      showLogin();
    }
  }

  window.SaludAuth = {
    start,
    login,
    logout,
    showLogin,
    boot: bootApp,
    get client() { return client; }
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
