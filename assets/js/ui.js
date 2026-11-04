/* ============================================================================
   saludrcartes — Interfaz e interacciones
   Navegación, búsqueda, modales, visor de documentos, accesibilidad y avisos.
   ========================================================================== */

(function () {
  'use strict';

  const App = window.SaludApp;
  if (!App) return;

  const U = App.util;
  const CONFIG = window.SALUD_CONFIG;
  const PREFS_KEY = 'saludrcartes.preferencias';

  let booted = false;
  let searchEl = null;
  let searchInput = null;
  let searchResults = null;
  let currentResults = [];
  let activeResult = -1;
  let searchOrigin = null;
  let currentModal = null;
  let modalOrigin = null;
  let sectionObserver = null;
  let drawerOrigin = null;
  let prefs = { text: 'md', contrast: false, motion: false };

  const drawer = document.getElementById('drawer');
  const drawerOverlay = document.getElementById('drawer-overlay');
  const menuToggle = document.getElementById('menu-toggle');
  const userPopover = document.getElementById('user-popover');
  const userTrigger = document.getElementById('user-trigger');
  const a11yPanel = document.getElementById('a11y-panel');
  const a11yTrigger = document.getElementById('a11y-trigger');
  const searchTrigger = document.getElementById('search-trigger');

  /* ------------------------------- Avisos --------------------------------- */
  function toast(message, type, timeout) {
    if (window.SaludToast) window.SaludToast.show(message, type, timeout);
  }

  /* --------------------------- Bloqueo de scroll -------------------------- */
  function syncScrollLock() {
    const open = (searchEl && searchEl.classList.contains('is-open')) ||
      !!document.querySelector('.modal-overlay.is-open') ||
      (drawer && drawer.classList.contains('is-open'));
    document.body.classList.toggle('no-scroll', !!open);
  }

  /* ------------------------------ Drawer ---------------------------------- */
  function openDrawer() {
    if (!drawer || !drawerOverlay) return;
    drawerOrigin = document.activeElement;
    drawer.classList.add('is-open');
    drawerOverlay.classList.add('is-open');
    drawer.setAttribute('aria-hidden', 'false');
    drawerOverlay.setAttribute('aria-hidden', 'false');
    if (menuToggle) menuToggle.setAttribute('aria-expanded', 'true');
    syncScrollLock();
    const close = document.getElementById('drawer-close');
    if (close) window.setTimeout(function () { close.focus(); }, 60);
  }

  function closeDrawer(restore) {
    if (!drawer || !drawerOverlay) return;
    drawer.classList.remove('is-open');
    drawerOverlay.classList.remove('is-open');
    drawer.setAttribute('aria-hidden', 'true');
    drawerOverlay.setAttribute('aria-hidden', 'true');
    if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
    syncScrollLock();
    if (restore !== false && drawerOrigin && drawerOrigin.isConnected) {
      try { drawerOrigin.focus({ preventScroll: true }); } catch (error) { /* sin foco */ }
    }
  }

  /* --------------------------- Menús y popovers --------------------------- */
  function closeDropdowns(except) {
    document.querySelectorAll('.nav-item.is-open').forEach((item) => {
      if (item === except) return;
      item.classList.remove('is-open');
      const trigger = item.querySelector('.nav-trigger');
      if (trigger) trigger.setAttribute('aria-expanded', 'false');
    });
  }

  function closeUserMenu() {
    if (!userPopover || !userTrigger) return;
    userPopover.classList.remove('is-open');
    userTrigger.setAttribute('aria-expanded', 'false');
  }

  function closeA11y(restore) {
    if (!a11yPanel || !a11yTrigger) return;
    const wasOpen = a11yPanel.classList.contains('is-open');
    a11yPanel.classList.remove('is-open');
    a11yTrigger.setAttribute('aria-expanded', 'false');
    if (wasOpen && restore && a11yTrigger.isConnected) a11yTrigger.focus({ preventScroll: true });
  }

  function closeTransient() {
    closeDropdowns();
    closeUserMenu();
    closeA11y(false);
    closeDrawer(false);
  }

  function bindMenus() {
    document.querySelectorAll('.nav-item[data-dropdown]').forEach((item) => {
      const trigger = item.querySelector('.nav-trigger');
      if (!trigger) return;
      trigger.addEventListener('click', function (event) {
        event.stopPropagation();
        const willOpen = !item.classList.contains('is-open');
        closeDropdowns(item);
        closeUserMenu();
        closeA11y(false);
        item.classList.toggle('is-open', willOpen);
        trigger.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
      });
      item.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
          item.classList.remove('is-open');
          trigger.setAttribute('aria-expanded', 'false');
          trigger.focus();
        }
      });
    });

    if (userTrigger && userPopover) {
      userTrigger.addEventListener('click', function (event) {
        event.stopPropagation();
        const willOpen = !userPopover.classList.contains('is-open');
        closeDropdowns();
        closeA11y(false);
        userPopover.classList.toggle('is-open', willOpen);
        userTrigger.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
        if (willOpen) {
          const first = userPopover.querySelector('button, a');
          if (first) window.setTimeout(function () { first.focus({ preventScroll: true }); }, 30);
        }
      });
    }

    if (menuToggle) menuToggle.addEventListener('click', openDrawer);
    const drawerClose = document.getElementById('drawer-close');
    if (drawerClose) drawerClose.addEventListener('click', function () { closeDrawer(true); });
    if (drawerOverlay) drawerOverlay.addEventListener('click', function () { closeDrawer(true); });

    if (drawer) {
      drawer.addEventListener('keydown', function (event) {
        if (event.key === 'Tab') trapFocus(event, drawer);
      });
    }

    if (a11yTrigger && a11yPanel) {
      a11yTrigger.addEventListener('click', function (event) {
        event.stopPropagation();
        const willOpen = !a11yPanel.classList.contains('is-open');
        closeDropdowns();
        closeUserMenu();
        if (searchEl) closeSearch(false);
        a11yPanel.classList.toggle('is-open', willOpen);
        a11yTrigger.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
        if (willOpen) {
          const first = a11yPanel.querySelector('button');
          if (first) window.setTimeout(function () { first.focus({ preventScroll: true }); }, 30);
        }
      });
    }

    document.addEventListener('click', function (event) {
      if (!event.target.closest('.nav-item[data-dropdown]')) closeDropdowns();
      if (userPopover && !event.target.closest('#user-menu')) closeUserMenu();
      if (a11yPanel && !event.target.closest('#a11y-panel') && !event.target.closest('#a11y-trigger')) closeA11y(false);
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 1100) closeDrawer(false);
    });

    if (drawer) {
      drawer.addEventListener('click', function (event) {
        if (event.target.closest('a[href]')) window.setTimeout(function () { closeDrawer(false); }, 20);
      });
    }
  }

  /* --------------------------- Preferencias ------------------------------- */
  function readPrefs() {
    let saved = null;
    try { saved = JSON.parse(window.localStorage.getItem(PREFS_KEY) || 'null'); } catch (error) { saved = null; }
    const osReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    prefs = Object.assign({ text: 'md', contrast: false, motion: !!osReduced }, saved || {});
    if (['md', 'lg', 'xl'].indexOf(prefs.text) === -1) prefs.text = 'md';
    prefs.contrast = !!prefs.contrast;
    prefs.motion = !!prefs.motion;
  }

  function savePrefs() {
    try { window.localStorage.setItem(PREFS_KEY, JSON.stringify(prefs)); } catch (error) { /* modo privado */ }
  }

  function applyPrefs() {
    const root = document.documentElement;
    if (prefs.text === 'md') root.removeAttribute('data-text');
    else root.setAttribute('data-text', prefs.text);
    if (prefs.contrast) root.setAttribute('data-contrast', 'high');
    else root.removeAttribute('data-contrast');
    if (prefs.motion) root.setAttribute('data-motion', 'reduced');
    else root.removeAttribute('data-motion');

    document.querySelectorAll('[data-text-size]').forEach((button) => {
      button.setAttribute('aria-pressed', button.getAttribute('data-text-size') === prefs.text ? 'true' : 'false');
    });
    document.querySelectorAll('[data-toggle="contrast"]').forEach((button) => {
      button.setAttribute('aria-checked', prefs.contrast ? 'true' : 'false');
    });
    document.querySelectorAll('[data-toggle="motion"]').forEach((button) => {
      button.setAttribute('aria-checked', prefs.motion ? 'true' : 'false');
    });
  }

  function setPrefs(patch) {
    prefs = Object.assign({}, prefs, patch);
    applyPrefs();
    savePrefs();
  }

  function resetPrefs() {
    prefs = { text: 'md', contrast: false, motion: false };
    applyPrefs();
    savePrefs();
    toast('Preferencias restablecidas.', 'success');
  }

  function bindPrefs() {
    document.querySelectorAll('[data-text-size]').forEach((button) => {
      button.addEventListener('click', function () {
        setPrefs({ text: button.getAttribute('data-text-size') || 'md' });
      });
    });
    document.querySelectorAll('[data-toggle]').forEach((button) => {
      button.addEventListener('click', function () {
        const key = button.getAttribute('data-toggle');
        if (key === 'contrast') setPrefs({ contrast: !prefs.contrast });
        if (key === 'motion') setPrefs({ motion: !prefs.motion });
      });
    });
    readPrefs();
    applyPrefs();
  }

  /* ------------------------------- Foco ----------------------------------- */
  function trapFocus(event, container) {
    if (event.key !== 'Tab') return;
    const focusables = Array.from(container.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), iframe, [tabindex]:not([tabindex="-1"])'
    )).filter((el) => el.offsetWidth > 0 || el.offsetHeight > 0 || el.getClientRects().length);
    if (!focusables.length) { event.preventDefault(); return; }
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    if (event.shiftKey && (document.activeElement === first || !container.contains(document.activeElement))) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && (document.activeElement === last || !container.contains(document.activeElement))) {
      event.preventDefault();
      first.focus();
    }
  }

  /* ------------------------------- Modales -------------------------------- */
  function closeModal(immediate) {
    const root = document.getElementById('modal-root');
    if (!root) return;
    const overlay = root.querySelector('.modal-overlay');
    if (!overlay) return;
    overlay.classList.remove('is-open');
    const origin = modalOrigin;
    currentModal = null;
    modalOrigin = null;
    const remove = function () {
      if (root.contains(overlay)) root.removeChild(overlay);
      syncScrollLock();
    };
    if (immediate) remove();
    else window.setTimeout(remove, 190);
    if (origin && origin.isConnected) {
      try { origin.focus({ preventScroll: true }); } catch (error) { /* sin foco */ }
    }
  }

  function openModal(options) {
    const opts = options || {};
    const root = document.getElementById('modal-root');
    if (!root) return;
    if (searchEl && searchEl.classList.contains('is-open')) closeSearch(false);
    if (root.querySelector('.modal-overlay')) closeModal(true);
    closeTransient();

    modalOrigin = document.activeElement;
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML =
      '<div class="modal' + (opts.size === 'sm' ? ' modal--sm' : '') + '" role="dialog" aria-modal="true" aria-labelledby="modal-title">' +
        '<div class="modal__head">' +
          '<h2 class="modal__title" id="modal-title">' + U.esc(opts.title || 'Detalle') +
            (opts.subtitle ? '<small>' + U.esc(opts.subtitle) + '</small>' : '') +
          '</h2>' +
          '<button class="icon-btn" type="button" data-close-modal aria-label="Cerrar ventana">' + U.icon('close', 21) + '</button>' +
        '</div>' +
        '<div class="modal__body' + (opts.flush ? ' modal__body--flush' : '') + '">' + opts.body + '</div>' +
        (opts.foot ? '<div class="modal__foot">' + opts.foot + '</div>' : '') +
      '</div>';
    root.appendChild(overlay);
    currentModal = overlay;
    syncScrollLock();
    window.requestAnimationFrame(function () { overlay.classList.add('is-open'); });

    overlay.addEventListener('click', function (event) {
      if (event.target === overlay) closeModal();
    });
    overlay.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        event.preventDefault();
        closeModal();
      } else if (event.key === 'Tab') {
        trapFocus(event, overlay);
      }
    });

    const closeButton = overlay.querySelector('[data-close-modal]');
    window.setTimeout(function () {
      if (closeButton) closeButton.focus({ preventScroll: true });
      if (typeof opts.onOpen === 'function') opts.onOpen(overlay);
    }, 40);
  }

  function openDoc(id) {
    const doc = App.index.docs.find((item) => item.id === id);
    if (!doc) return;
    const cat = App.index.catById[doc.categoria_id];
    const meta = [cat ? cat.nombre : '', U.formatDate(doc.fecha, 'medium'), doc.tipo_archivo || 'PDF', doc.tamano].filter(Boolean).join(' · ');
    const body = '<iframe class="doc-preview" src="' + U.attr(doc.archivo) + '#view=FitH" title="' + U.attr('Vista previa de ' + doc.nombre) + '" loading="lazy"></iframe>' +
      '<div class="doc-preview-note">' + U.icon('info', 15) +
        '<span>Si el visor no carga en tu navegador, descarga el archivo o ábrelo en una pestaña nueva. ' +
        '<a class="text-link" href="' + U.attr(doc.archivo) + '" target="_blank" rel="noopener">Abrir el PDF</a>.</span>' +
      '</div>';
    const foot = '<span class="tiny soft">' + U.esc(meta) + '</span>' +
      '<div class="modal__foot-actions">' +
        '<button class="btn btn--ghost btn--sm" type="button" data-close-modal>Cerrar</button>' +
        '<a class="btn btn--primary btn--sm" href="' + U.attr(doc.archivo) + '" download>' + U.icon('download', 16) + ' Descargar</a>' +
      '</div>';
    openModal({ title: doc.nombre, subtitle: meta, body, foot, flush: true });
  }

  function openCondition(id) {
    const a = App.index.afecciones[id];
    if (!a) return;
    const cat = App.index.catById[a.categoria_id];
    const docs = U.docsForAfeccion(a.id);
    const cells = [
      ['CIE-10', a.cie10 || 'No registrado'],
      ['Especialidad', a.especialidad],
      ['Profesional', a.medico],
      ['Fecha', U.formatDate(a.fecha_diagnostico)],
      ['Centro', a.centro],
      ['Estado', a.estado]
    ];

    const body = '<div class="condition-detail">' +
      '<div class="condition-detail__top">' +
        '<span class="condition-detail__icon">' + U.icon(U.catIcon(cat), 26) + '</span>' +
        '<div><h2>' + U.esc(a.titulo) + '</h2><div class="chip-row">' +
          App.statusBadge(a.estado, a.tono, 'activity') +
          App.chip(cat ? cat.nombre : a.especialidad, 'neutral', 'stethoscope') +
        '</div></div>' +
      '</div>' +
      '<p class="muted">' + U.esc(a.descripcion) + '</p>' +
      '<div class="condition-detail__grid">' +
        cells.map((cell) => '<div class="condition-detail__cell"><span>' + U.esc(cell[0]) + '</span><strong>' + U.esc(cell[1]) + '</strong></div>').join('') +
      '</div>' +
      '<div class="modal-section"><h3>' + U.icon('compass', 18) + ' Resumen clínico</h3><p class="muted">' + U.esc(a.resumen) + '</p></div>' +
      '<div class="modal-section"><h3>' + U.icon('check-circle', 18) + ' Indicaciones</h3>' +
        '<ul class="condition-detail__notes">' + (a.notas || []).map((note) => '<li>' + U.icon('check', 14) + '<span>' + U.esc(note) + '</span></li>').join('') + '</ul>' +
      '</div>' +
      '<div class="modal-section"><h3>' + U.icon('folder', 18) + ' Documentos</h3>' +
        (docs.length
          ? '<div class="modal-doc-list">' + docs.map((doc) => '<button class="modal-doc" type="button" data-doc="' + U.attr(doc.id) + '">' +
              U.icon('file-text', 17) + '<span>' + U.esc(doc.nombre) + '</span><small>' + U.esc(U.formatDate(doc.fecha, 'medium')) + '</small></button>').join('') + '</div>'
          : '<div class="doc-empty">' + U.icon('info', 18) + '<span>No hay documentos asociados a esta condición.</span></div>') +
      '</div>' +
    '</div>';

    const foot = '<span class="tiny soft">Actualizado el ' + U.esc(U.formatDate(a.actualizado, 'medium')) + '</span>' +
      '<div class="modal__foot-actions">' +
        '<button class="btn btn--ghost btn--sm" type="button" data-close-modal>Cerrar</button>' +
        (cat ? '<a class="btn btn--primary btn--sm" href="#/categoria/' + U.attr(cat.slug) + '" data-close-modal>Abrir página completa ' + U.icon('arrow-right', 16) + '</a>' : '') +
      '</div>';

    openModal({
      title: 'Detalle del diagnóstico',
      subtitle: a.estado + ' · ' + a.especialidad,
      body,
      foot
    });
  }

  /* ------------------------------- Búsqueda ------------------------------- */
  let searchIndex = [];
  let quickLinks = [];

  function buildSearchIndex() {
    const items = [];
    App.index.categorias.forEach((cat) => {
      items.push({
        type: cat.tipo === 'especialidad' ? 'Especialidad' : 'Sección',
        title: cat.nombre,
        meta: U.catMeta(cat) + ' · ' + cat.estado,
        icon: U.catIcon(cat),
        href: '#/categoria/' + cat.slug,
        haystack: U.strip([cat.nombre, cat.descripcion, cat.resumen, cat.estado].join(' '))
      });
    });
    items.push({
      type: 'Página',
      title: 'Biblioteca de documentos',
      meta: App.index.docs.length + ' archivos descargables',
      icon: 'folder',
      href: '#/documentos',
      haystack: U.strip('biblioteca documentos archivos pdf informes recetas examenes')
    });
    items.push({
      type: 'Página',
      title: 'Acerca y privacidad',
      meta: 'Cómo está hecho, accesibilidad y seguridad',
      icon: 'shield-heart',
      href: '#/acerca',
      haystack: U.strip('acerca privacidad seguridad accesibilidad supabase como funciona')
    });

    App.index.diagnosticos.forEach((a) => {
      items.push({
        type: 'Diagnóstico',
        title: a.titulo,
        meta: a.especialidad + ' · ' + a.estado + (a.cie10 ? ' · CIE-10 ' + a.cie10 : ''),
        icon: 'clipboard-pulse',
        openCondition: a.id,
        haystack: U.strip([a.titulo, a.descripcion, a.resumen, a.medico, a.especialidad, a.cie10, a.estado].join(' '))
      });
    });

    App.index.docs.forEach((doc) => {
      const cat = App.index.catById[doc.categoria_id];
      items.push({
        type: 'Documento',
        title: doc.nombre,
        meta: (cat ? cat.nombre + ' · ' : '') + U.formatDate(doc.fecha, 'medium') + ' · ' + (doc.tipo_archivo || 'PDF'),
        icon: 'file-text',
        openDoc: doc.id,
        haystack: U.strip([doc.nombre, doc.descripcion, cat ? cat.nombre : '', doc.fecha].join(' '))
      });
    });

    App.index.meds.forEach((med) => {
      items.push({
        type: 'Medicamento',
        title: med.nombre + ' · ' + med.dosis,
        meta: med.frecuencia + ' · ' + (med.activo ? 'Activo' : 'Suspendido'),
        icon: 'pill',
        href: '#/categoria/medicamentos',
        haystack: U.strip([med.nombre, med.dosis, med.frecuencia, med.indicacion, med.notas].join(' '))
      });
    });

    App.index.labs.forEach((row) => {
      items.push({
        type: 'Laboratorio',
        title: row.examen + ': ' + row.resultado + ' ' + row.unidad,
        meta: row.panel + ' · ' + row.estado + ' · ' + U.formatDate(row.fecha, 'medium'),
        icon: 'flask',
        href: '#/categoria/laboratorio',
        haystack: U.strip([row.panel, row.examen, row.resultado, row.referencia, row.estado].join(' '))
      });
    });

    App.index.contactos.forEach((contact) => {
      items.push({
        type: 'Contacto',
        title: contact.nombre,
        meta: contact.relacion + ' · ' + contact.telefono,
        icon: 'phone-call',
        href: '#/categoria/emergencia',
        haystack: U.strip([contact.nombre, contact.relacion, contact.telefono, contact.nota].join(' '))
      });
    });

    App.index.alergias.forEach((allergy) => {
      items.push({
        type: 'Alergia',
        title: allergy.sustancia,
        meta: allergy.severidad + ' · ' + allergy.reaccion,
        icon: 'alert-triangle',
        href: '#/categoria/medicamentos',
        haystack: U.strip([allergy.sustancia, allergy.severidad, allergy.reaccion, allergy.notas].join(' '))
      });
    });

    searchIndex = items;

    quickLinks = [
      { type: 'Acceso rápido', title: 'Inicio', meta: 'Resumen general y accesos', icon: 'home', href: '#/' },
      { type: 'Acceso rápido', title: 'Diagnósticos', meta: App.index.diagnosticos.length + ' condiciones', icon: 'clipboard-pulse', href: '#/categoria/diagnosticos' },
      { type: 'Acceso rápido', title: 'Medicamentos y alergias', meta: App.index.medsActive.length + ' activos', icon: 'pill', href: '#/categoria/medicamentos' },
      { type: 'Acceso rápido', title: 'Laboratorio', meta: App.index.labs.length + ' resultados', icon: 'flask', href: '#/categoria/laboratorio' },
      { type: 'Acceso rápido', title: 'Documentos', meta: App.index.docs.length + ' archivos', icon: 'folder', href: '#/documentos' },
      { type: 'Acceso rápido', title: 'Emergencia', meta: 'Contactos y datos críticos', icon: 'phone-call', href: '#/categoria/emergencia' }
    ];
  }

  function buildSearchOverlay() {
    searchEl = document.createElement('div');
    searchEl.className = 'search-overlay';
    searchEl.innerHTML =
      '<div class="search-dialog" role="dialog" aria-modal="true" aria-labelledby="search-title">' +
        '<div class="search-dialog__head">' +
          '<span class="search-dialog__icon">' + U.icon('search', 21) + '</span>' +
          '<h2 class="sr-only" id="search-title">Buscar en el registro clínico</h2>' +
          '<input class="search-dialog__input" id="search-input" type="search" placeholder="Busca un diagnóstico, medicamento, documento o contacto…" autocomplete="off" spellcheck="false" aria-controls="search-results">' +
          '<button class="icon-btn search-dialog__close" type="button" data-action="close-search" aria-label="Cerrar búsqueda">' + U.icon('close', 21) + '</button>' +
        '</div>' +
        '<div class="search-results" id="search-results" role="listbox" aria-label="Resultados de búsqueda"></div>' +
        '<div class="search-dialog__foot">' +
          '<div class="search-hints">' +
            '<span><kbd class="kbd">↑</kbd><kbd class="kbd">↓</kbd> navegar</span>' +
            '<span><kbd class="kbd">Enter</kbd> abrir</span>' +
            '<span><kbd class="kbd">Esc</kbd> cerrar</span>' +
          '</div>' +
          '<span>Contenido de demostración</span>' +
        '</div>' +
      '</div>';
    document.body.appendChild(searchEl);
    searchInput = searchEl.querySelector('#search-input');
    searchResults = searchEl.querySelector('#search-results');

    searchEl.addEventListener('click', function (event) {
      if (event.target === searchEl) closeSearch(true);
    });
    searchEl.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        event.preventDefault();
        closeSearch(true);
      } else if (event.key === 'Tab') {
        trapFocus(event, searchEl);
      }
    });
    searchInput.addEventListener('input', function () { renderSearch(searchInput.value); });
    searchInput.addEventListener('keydown', handleSearchKeys);
    searchResults.addEventListener('click', function (event) {
      const button = event.target.closest('[data-result]');
      if (button) runResult(parseInt(button.getAttribute('data-result'), 10));
    });
  }

  function highlightEscape(value) { return U.esc(value); }

  function renderSearch(query) {
    if (!searchResults) return;
    const q = U.strip(query).trim();
    currentResults = q
      ? searchIndex.filter((item) => item.haystack.indexOf(q) !== -1).slice(0, 30)
      : quickLinks.slice();
    activeResult = -1;
    searchInput.removeAttribute('aria-activedescendant');

    if (!currentResults.length) {
      searchResults.innerHTML = '<div class="search-empty">' + U.icon('search', 30) +
        '<h3>No encontramos coincidencias</h3><p>Prueba con el nombre de una especialidad, un medicamento, una fecha o una palabra clave.</p></div>';
      return;
    }

    const groups = {};
    currentResults.forEach((item, index) => {
      if (!groups[item.type]) groups[item.type] = [];
      groups[item.type].push({ item, index });
    });

    searchResults.innerHTML = Object.keys(groups).map((type) =>
      '<div class="search-group"><div class="search-group__label">' + U.esc(type) + '</div>' +
        groups[type].map((entry) => '<button class="search-result" type="button" role="option" id="search-result-' + entry.index + '" data-result="' + entry.index + '" aria-selected="false">' +
          '<span class="search-result__icon">' + U.icon(entry.item.icon, 18) + '</span>' +
          '<span><span class="search-result__title">' + highlightEscape(entry.item.title) + '</span>' +
          '<span class="search-result__meta">' + highlightEscape(entry.item.meta) + '</span></span>' +
          '<span class="search-result__type">' + U.esc(entry.item.type) + '</span>' +
        '</button>').join('') +
      '</div>'
    ).join('');
    searchResults.scrollTop = 0;
  }

  function setActiveResult(index) {
    if (!searchResults) return;
    const buttons = Array.from(searchResults.querySelectorAll('[data-result]'));
    buttons.forEach((button) => {
      const isActive = parseInt(button.getAttribute('data-result'), 10) === index;
      button.classList.toggle('is-active', isActive);
      button.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });
    activeResult = index;
    const active = searchResults.querySelector('[data-result="' + index + '"]');
    if (active) {
      searchInput.setAttribute('aria-activedescendant', 'search-result-' + index);
      active.scrollIntoView({ block: 'nearest' });
    }
  }

  function handleSearchKeys(event) {
    if (!currentResults.length) return;
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      if (event.key === 'ArrowDown') setActiveResult((activeResult + 1) % currentResults.length);
      else setActiveResult(activeResult <= 0 ? currentResults.length - 1 : activeResult - 1);
    } else if (event.key === 'Enter') {
      event.preventDefault();
      runResult(activeResult >= 0 ? activeResult : 0);
    }
  }

  function runResult(index) {
    const item = currentResults[index];
    if (!item) return;
    closeSearch(false);
    if (item.openCondition) {
      openCondition(item.openCondition);
      return;
    }
    if (item.openDoc) {
      openDoc(item.openDoc);
      return;
    }
    if (item.href) {
      window.location.hash = item.href;
    }
  }

  function openSearch() {
    if (!searchEl) buildSearchOverlay();
    closeTransient();
    if (document.querySelector('.modal-overlay.is-open')) closeModal(true);
    searchOrigin = document.activeElement;
    searchEl.classList.add('is-open');
    syncScrollLock();
    searchInput.value = '';
    renderSearch('');
    window.setTimeout(function () { searchInput.focus({ preventScroll: true }); }, 40);
  }

  function closeSearch(restore) {
    if (!searchEl) return;
    searchEl.classList.remove('is-open');
    syncScrollLock();
    if (restore && searchOrigin && searchOrigin.isConnected) {
      try { searchOrigin.focus({ preventScroll: true }); } catch (error) { /* sin foco */ }
    }
  }

  /* ---------------------------- Secciones / spy --------------------------- */
  function initScrollSpy() {
    if (sectionObserver) { sectionObserver.disconnect(); sectionObserver = null; }
    const links = Array.from(document.querySelectorAll('.section-nav [data-scroll]'));
    if (!links.length) return;
    const sections = links.map((link) => document.getElementById(link.getAttribute('data-scroll'))).filter(Boolean);
    if (!sections.length) return;

    const setActive = function (id) {
      links.forEach((link) => link.classList.toggle('is-active', link.getAttribute('data-scroll') === id));
    };
    setActive(sections[0].id);

    if (!('IntersectionObserver' in window)) return;
    sectionObserver = new IntersectionObserver(function (entries) {
      const visible = entries.filter((entry) => entry.isIntersecting);
      if (visible.length) {
        visible.sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        setActive(visible[0].target.id);
      }
    }, { rootMargin: '-25% 0px -60% 0px', threshold: 0 });
    sections.forEach((section) => sectionObserver.observe(section));
  }

  function scrollToSection(id) {
    const target = document.getElementById(id);
    if (!target) return;
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    document.querySelectorAll('.section-nav [data-scroll]').forEach((link) => {
      link.classList.toggle('is-active', link.getAttribute('data-scroll') === id);
    });
  }

  /* --------------------------- Acciones globales -------------------------- */
  function printPage() {
    closeSearch(false);
    closeModal(true);
    closeTransient();
    window.setTimeout(function () { window.print(); }, 80);
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      const area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', '');
      area.className = 'sr-only';
      document.body.appendChild(area);
      area.select();
      try {
        const ok = document.execCommand('copy');
        document.body.removeChild(area);
        if (ok) resolve(); else reject(new Error('No se pudo copiar'));
      } catch (error) {
        document.body.removeChild(area);
        reject(error);
      }
    });
  }

  function sharePage() {
    const payload = {
      title: document.title,
      text: 'Registro clínico personal · saludrcartes',
      url: window.location.href
    };
    if (navigator.share) {
      navigator.share(payload).catch(function (error) {
        if (error && error.name === 'AbortError') return;
        copyText(payload.url).then(function () {
          toast('Enlace copiado al portapapeles.', 'success');
        }).catch(function () {
          toast('No se pudo compartir el enlace en este navegador.', 'error');
        });
      });
      return;
    }
    copyText(payload.url).then(function () {
      toast('Enlace copiado al portapapeles.', 'success');
    }).catch(function () {
      toast('No se pudo copiar el enlace. Puedes copiarlo desde la barra de direcciones.', 'error');
    });
  }

  function handleAction(action, element) {
    switch (action) {
      case 'logout':
        if (window.SaludAuth && window.SaludAuth.logout) window.SaludAuth.logout();
        break;
      case 'a11y':
        closeDropdowns();
        closeUserMenu();
        closeDrawer(false);
        if (a11yPanel && a11yTrigger) {
          a11yPanel.classList.add('is-open');
          a11yTrigger.setAttribute('aria-expanded', 'true');
          const first = a11yPanel.querySelector('button');
          if (first) window.setTimeout(function () { first.focus({ preventScroll: true }); }, 40);
        }
        break;
      case 'a11y-reset':
        resetPrefs();
        break;
      case 'print':
        printPage();
        break;
      case 'share':
        sharePage();
        break;
      case 'to-top':
        window.scrollTo({ top: 0, behavior: 'smooth' });
        break;
      case 'search':
        openSearch();
        break;
      case 'close-search':
        closeSearch(true);
        break;
      case 'close-modal':
        closeModal();
        break;
      case 'close-demo':
        if (demoBanner) demoBanner.hidden = true;
        try { window.sessionStorage.setItem(BANNER_KEY, '1'); } catch (error) { /* modo privado */ }
        break;
      default:
        break;
    }
  }

  function bindGlobalActions() {
    document.addEventListener('click', function (event) {
      const closeModalEl = event.target.closest('[data-close-modal]');
      if (closeModalEl) {
        closeModal();
        if (closeModalEl.tagName !== 'A') event.preventDefault();
        if (closeModalEl.tagName === 'A') return;
        return;
      }

      const actionEl = event.target.closest('[data-action]');
      if (actionEl) {
        if (actionEl.tagName === 'A' && actionEl.getAttribute('href') === '#') event.preventDefault();
        handleAction(actionEl.getAttribute('data-action'), actionEl);
        if (actionEl.closest('#user-popover')) closeUserMenu();
        return;
      }

      const docEl = event.target.closest('[data-doc]');
      if (docEl) {
        event.preventDefault();
        openDoc(docEl.getAttribute('data-doc'));
        return;
      }

      const conditionEl = event.target.closest('[data-condition]');
      if (conditionEl) {
        event.preventDefault();
        openCondition(conditionEl.getAttribute('data-condition'));
        return;
      }

      const scrollEl = event.target.closest('[data-scroll]');
      if (scrollEl) {
        event.preventDefault();
        scrollToSection(scrollEl.getAttribute('data-scroll'));
      }
    });

    if (searchTrigger) {
      searchTrigger.addEventListener('click', function (event) {
        event.preventDefault();
        openSearch();
      });
    }

    const demoClose = document.getElementById('demo-banner-close');
    if (demoClose) {
      demoClose.addEventListener('click', function () {
        if (demoBanner) demoBanner.hidden = true;
        try { window.sessionStorage.setItem(BANNER_KEY, '1'); } catch (error) { /* modo privado */ }
      });
    }

    document.addEventListener('keydown', function (event) {
      const target = event.target;
      const typing = target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT' || target.isContentEditable);
      if ((event.ctrlKey || event.metaKey) && String(event.key).toLowerCase() === 'k') {
        event.preventDefault();
        if (searchEl && searchEl.classList.contains('is-open')) closeSearch(true);
        else openSearch();
        return;
      }
      if (event.key === '/' && !typing && !event.ctrlKey && !event.metaKey && !event.altKey) {
        event.preventDefault();
        openSearch();
        return;
      }
      if (event.key === 'Escape') {
        if (document.querySelector('.modal-overlay.is-open')) return;
        if (searchEl && searchEl.classList.contains('is-open')) return;
        if (drawer && drawer.classList.contains('is-open')) { closeDrawer(true); return; }
        if (userPopover && userPopover.classList.contains('is-open')) { closeUserMenu(); if (userTrigger) userTrigger.focus(); return; }
        if (a11yPanel && a11yPanel.classList.contains('is-open')) { closeA11y(true); return; }
        closeDropdowns();
      }
    });
  }

  /* -------------------------------- Init ---------------------------------- */
  function onRoute() {
    closeTransient();
    if (searchEl && searchEl.classList.contains('is-open')) closeSearch(false);
    initScrollSpy();
  }

  function init() {
    if (booted) return;
    booted = true;
    buildSearchIndex();
    buildSearchOverlay();
    bindMenus();
    bindPrefs();
    bindGlobalActions();
    try {
      if (window.sessionStorage.getItem(BANNER_KEY) === '1' && demoBanner) demoBanner.hidden = true;
    } catch (error) { /* modo privado */ }

    const globalDemo = document.getElementById('demo-banner');
    if (globalDemo && !CONFIG.demo) globalDemo.hidden = true;
  }

  window.SaludUI = {
    init,
    onRoute,
    openSearch,
    closeSearch,
    openDoc,
    openCondition,
    openModal,
    closeModal,
    closeTransient,
    printPage,
    sharePage,
    toast
  };
})();
