/* ============================================================================
   saludrcartes — Acceso y arranque
   ----------------------------------------------------------------------------
   MODO DEMOSTRACIÓN: valida credenciales locales y guarda una sesión en el
   navegador. NO es seguridad real: cualquier persona con acceso a los archivos
   puede leer el código. Para producción usa Supabase Auth + RLS.

   La interfaz está preparada para que la sustitución por Supabase sea acotada:
   solo hay que reemplazar startSession/readSession y la carga de datos.
   ========================================================================== */

(function () {
  'use strict';

  var CONFIG = window.SALUD_CONFIG;
  var ICONS = window.SaludIcons;
  var loginView = document.getElementById('vista-login');
  var appView = document.getElementById('vista-app');
  var form = document.getElementById('login-form');
  var emailInput = document.getElementById('login-email');
  var passwordInput = document.getElementById('login-password');
  var rememberInput = document.getElementById('login-remember');
  var errorBox = document.getElementById('login-error');
  var errorText = document.getElementById('login-error-text');
  var submitBtn = document.getElementById('login-submit');
  var submitLabel = document.getElementById('login-submit-label');
  var booted = false;
  var loadingPromise = null;

  /* ------------------------------ Toast --------------------------------- */
  function showToast(message, type, timeout) {
    var region = document.getElementById('toast-region');
    if (!region) return;
    var toast = document.createElement('div');
    toast.className = 'toast toast--' + (type || 'success');
    var iconName = type === 'error' ? 'alert-circle' : type === 'info' ? 'info' : 'check-circle';
    var iconWrap = document.createElement('span');
    iconWrap.innerHTML = ICONS.icon(iconName, null, 18);
    var text = document.createElement('span');
    text.textContent = message;
    toast.appendChild(iconWrap);
    toast.appendChild(text);
    region.appendChild(toast);
    window.setTimeout(function () {
      toast.classList.add('is-leaving');
      window.setTimeout(function () { toast.remove(); }, 220);
    }, timeout || 4200);
  }
  window.SaludToast = { show: showToast };

  /* ----------------------------- Sesión --------------------------------- */
  function safeGet(storage, key) {
    try { return storage.getItem(key); } catch (e) { return null; }
  }
  function safeSet(storage, key, value) {
    try { storage.setItem(key, value); } catch (e) { /* modo privado */ }
  }
  function safeRemove(storage, key) {
    try { storage.removeItem(key); } catch (e) { /* modo privado */ }
  }

  function readSession() {
    var key = CONFIG.auth.sessionKey;
    var raw = safeGet(window.sessionStorage, key) || safeGet(window.localStorage, key);
    if (!raw) return null;
    try {
      var session = JSON.parse(raw);
      if (!session || !session.expiresAt || session.expiresAt < Date.now()) {
        clearSession();
        return null;
      }
      return session;
    } catch (e) {
      clearSession();
      return null;
    }
  }

  function writeSession(remember) {
    var hours = CONFIG.auth.sessionHours || 12;
    var days = CONFIG.auth.rememberDays || 30;
    var session = {
      email: CONFIG.auth.demoUser.email,
      name: CONFIG.auth.demoUser.nombre,
      startedAt: Date.now(),
      expiresAt: Date.now() + (remember ? days : hours) * (remember ? 86400000 : 3600000)
    };
    var key = CONFIG.auth.sessionKey;
    if (remember) {
      safeSet(window.localStorage, key, JSON.stringify(session));
      safeRemove(window.sessionStorage, key);
    } else {
      safeSet(window.sessionStorage, key, JSON.stringify(session));
      safeRemove(window.localStorage, key);
    }
    return session;
  }

  function clearSession() {
    var key = CONFIG.auth.sessionKey;
    safeRemove(window.sessionStorage, key);
    safeRemove(window.localStorage, key);
  }

  /* ----------------------------- Interfaz -------------------------------- */
  function showLogin(message) {
    if (appView) appView.hidden = true;
    if (loginView) loginView.hidden = false;
    document.body.classList.remove('is-authed');
    if (message) showError(message); else hideError();
    if (emailInput) emailInput.focus({ preventScroll: true });
  }

  function showError(message) {
    if (!errorBox || !errorText) return;
    errorText.textContent = message;
    errorBox.hidden = false;
    document.getElementById('field-email').classList.add('field--error');
    document.getElementById('field-password').classList.add('field--error');
  }

  function hideError() {
    if (!errorBox) return;
    errorBox.hidden = true;
    var fieldEmail = document.getElementById('field-email');
    var fieldPassword = document.getElementById('field-password');
    if (fieldEmail) fieldEmail.classList.remove('field--error');
    if (fieldPassword) fieldPassword.classList.remove('field--error');
  }

  function setLoading(loading) {
    if (!submitBtn) return;
    submitBtn.disabled = loading;
    submitBtn.setAttribute('aria-busy', loading ? 'true' : 'false');
    if (submitLabel) submitLabel.textContent = loading ? 'Entrando…' : 'Entrar a mi registro';
  }

  function bootLoading() {
    var root = document.getElementById('app-root');
    if (!root) return;
    root.innerHTML =
      '<div class="boot-loading">' +
        '<div class="boot-loading__card">' +
          '<div class="spinner" aria-hidden="true"></div>' +
          '<h2>Preparando tu registro</h2>' +
          '<p>Verificando la sesión y cargando la información clínica.</p>' +
        '</div>' +
      '</div>';
  }

  function loadClinicalData() {
    if (window.SALUD_DATA) return Promise.resolve(window.SALUD_DATA);
    if (loadingPromise) return loadingPromise;
    loadingPromise = new Promise(function (resolve, reject) {
      var script = document.createElement('script');
      script.src = 'assets/js/data/clinica.js';
      script.async = true;
      script.onload = function () {
        if (window.SALUD_DATA) resolve(window.SALUD_DATA);
        else reject(new Error('El archivo de datos no definió SALUD_DATA.'));
      };
      script.onerror = function () {
        loadingPromise = null;
        reject(new Error('No se pudo cargar assets/js/data/clinica.js.'));
      };
      document.body.appendChild(script);
    });
    return loadingPromise;
  }

  function enterApp() {
    hideError();
    if (loginView) loginView.hidden = true;
    if (appView) appView.hidden = false;
    document.body.classList.add('is-authed');
    bootLoading();
    loadClinicalData().then(function (data) {
      if (!window.SaludApp || typeof window.SaludApp.init !== 'function') {
        throw new Error('La aplicación no está disponible.');
      }
      window.SaludApp.init(data);
      ICONS.hydrate(document);
      booted = true;
    }).catch(function (error) {
      console.error('[saludrcartes]', error);
      clearSession();
      loadingPromise = null;
      showLogin('No se pudo cargar el registro. Revisa la consola o vuelve a intentarlo.');
    });
  }

  /* --------------------------- Iniciar sesión ---------------------------- */
  function handleSubmit(event) {
    event.preventDefault();
    hideError();

    var email = (emailInput.value || '').trim().toLowerCase();
    var password = passwordInput.value || '';

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      showError('Escribe un correo válido para continuar.');
      emailInput.focus();
      return;
    }
    if (!password) {
      showError('Escribe tu clave para continuar.');
      passwordInput.focus();
      return;
    }

    if (CONFIG.auth.mode !== 'demo') {
      showError('El modo Supabase aún no está configurado en esta copia. Revisa docs/SUPABASE.md o vuelve al modo demostración.');
      return;
    }

    var expectedEmail = CONFIG.auth.demoUser.email.toLowerCase();
    var expectedPassword = CONFIG.auth.demoUser.password;

    if (email !== expectedEmail || password !== expectedPassword) {
      showError('El correo o la clave no coinciden. En esta demostración puedes usar el botón de credenciales de ejemplo.');
      passwordInput.select();
      return;
    }

    setLoading(true);
    writeSession(!!rememberInput.checked);
    window.setTimeout(function () {
      setLoading(false);
      enterApp();
    }, 260);
  }

  /* ---------------------------- Eventos login ---------------------------- */
  function bindLogin() {
    if (form) form.addEventListener('submit', handleSubmit);

    if (passwordInput) {
      passwordInput.addEventListener('input', hideError);
      passwordInput.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
          event.preventDefault();
          if (form) form.requestSubmit();
        }
      });
    }
    if (emailInput) emailInput.addEventListener('input', hideError);

    var toggle = document.getElementById('toggle-password');
    if (toggle && passwordInput) {
      toggle.addEventListener('click', function () {
        var visible = passwordInput.type === 'text';
        passwordInput.type = visible ? 'password' : 'text';
        toggle.setAttribute('aria-pressed', visible ? 'false' : 'true');
        toggle.setAttribute('aria-label', visible ? 'Mostrar clave' : 'Ocultar clave');
        toggle.innerHTML = ICONS.icon(visible ? 'eye' : 'eye-off', null, 20);
        passwordInput.focus();
      });
    }

    var demoFill = document.getElementById('demo-fill');
    if (demoFill) {
      demoFill.addEventListener('click', function () {
        emailInput.value = CONFIG.auth.demoUser.email;
        passwordInput.value = CONFIG.auth.demoUser.password;
        hideError();
        if (form) form.requestSubmit();
      });
    }

    var forgot = document.getElementById('forgot-link');
    if (forgot) {
      forgot.addEventListener('click', function (event) {
        event.preventDefault();
        showToast('En producción, usa la recuperación de clave de Supabase Auth. En la demostración, la clave es «saludrcartes».', 'info', 6500);
      });
    }
  }

  /* ------------------------------- Arranque ------------------------------ */
  function applyConfigVisibility() {
    var demoBox = document.getElementById('login-demo');
    if (demoBox) demoBox.hidden = !CONFIG.demo;
    var banner = document.getElementById('demo-banner');
    if (banner) banner.hidden = !CONFIG.demo;
    var chip = document.getElementById('demo-chip');
    if (chip) chip.hidden = !CONFIG.demo;
  }

  function boot() {
    ICONS.hydrate(document);
    applyConfigVisibility();
    bindLogin();

    var year = document.getElementById('footer-year');
    if (year) year.textContent = String(new Date().getFullYear());
    var version = document.getElementById('footer-version');
    if (version) version.textContent = CONFIG.version;
    var printDate = document.getElementById('print-date');
    if (printDate) {
      printDate.textContent = new Intl.DateTimeFormat(CONFIG.formatos.locale, {
        day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
      }).format(new Date());
    }

    var session = readSession();
    if (session) {
      enterApp();
    } else {
      showLogin();
    }

    if (window.location.hash === '#recuperar') {
      showToast('En producción, usa la recuperación de clave de Supabase Auth. En la demostración, la clave es «saludrcartes».', 'info', 6500);
    }

    window.addEventListener('storage', function (event) {
      if (event.key === CONFIG.auth.sessionKey && !event.newValue && booted) {
        window.location.reload();
      }
    });
  }

  window.SaludAuth = {
    logout: function () {
      clearSession();
      booted = false;
      var root = document.getElementById('app-root');
      if (root) root.innerHTML = '';
      if (history.replaceState) history.replaceState(null, '', window.location.pathname);
      window.location.reload();
    },
    getSession: readSession,
    clearSession: clearSession,
    showToast: showToast
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
