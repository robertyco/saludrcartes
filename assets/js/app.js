/* ============================================================================
   saludrcartes — Núcleo de la aplicación
   ----------------------------------------------------------------------------
   Utilidades compartidas, índices de datos, “chrome” del sitio, rutas y portada.
   Las vistas clínicas viven en views-*.js y la interacción en ui.js.
   ========================================================================== */

(function () {
  'use strict';

  const CONFIG = window.SALUD_CONFIG;
  const Icons = window.SaludIcons;
  const appRoot = document.getElementById('app-root');
  const main = document.getElementById('contenido');
  const views = {};

  let D = null;
  let idx = null;

  const TONE_MAP = { ambar: 'amarillo', amarillo: 'amarillo', verde: 'verde', coral: 'coral', turquesa: 'turquesa', violeta: 'violeta', neutral: 'neutral' };
  const ICON_ALIAS = { arm: 'hand', leg: 'footprints' };
  const dateCache = new Map();

  /* ------------------------------ Utilidades ------------------------------ */
  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function attr(value) { return esc(value); }

  function strip(value) {
    return String(value == null ? '' : value)
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase();
  }

  function icon(name, size, cls) { return Icons.icon(name, cls, size || 20); }

  function catIcon(cat) {
    const name = cat && cat.icono ? cat.icono : 'info';
    return ICON_ALIAS[name] || name;
  }

  function toneOf(tone) { return TONE_MAP[tone] || 'neutral'; }

  function formatDate(iso, style) {
    if (!iso) return 'Sin fecha';
    const key = iso + '|' + (style || 'long');
    if (dateCache.has(key)) return dateCache.get(key);
    const date = new Date(iso + 'T12:00:00');
    if (isNaN(date.getTime())) return iso;
    const options = style === 'medium'
      ? { day: '2-digit', month: 'short', year: 'numeric' }
      : style === 'short'
        ? { day: 'numeric', month: 'short' }
        : style === 'month'
          ? { month: 'long', year: 'numeric' }
          : { day: 'numeric', month: 'long', year: 'numeric' };
    const text = new Intl.DateTimeFormat(CONFIG.formatos.locale, options).format(date).replace(/\./g, '');
    dateCache.set(key, text);
    return text;
  }

  function yearOf(iso) {
    if (!iso) return '';
    const date = new Date(iso + 'T12:00:00');
    return isNaN(date.getTime()) ? '' : String(date.getFullYear());
  }

  function telHref(phone) {
    return 'tel:' + String(phone || '').replace(/[^\d+]/g, '');
  }

  function countLabel(n, one, many) { return n === 1 ? one : many; }

  function statusBadge(text, tone, iconName) {
    const t = TONE_MAP[tone] === 'amarillo' && tone === 'ambar' ? 'ambar' : (TONE_MAP[tone] || 'neutral');
    return '<span class="status status--' + t + '">' +
      (iconName ? icon(iconName, 14) : '<span class="dot"></span>') +
      esc(text) + '</span>';
  }

  function chip(text, tone, iconName) {
    return '<span class="chip chip--' + (tone || 'neutral') + '">' +
      (iconName ? icon(iconName, 14) : '') + esc(text) + '</span>';
  }

  function byDateDesc(a, b) { return String(b.fecha || b.fecha_diagnostico || '').localeCompare(String(a.fecha || a.fecha_diagnostico || '')); }

  function unique(list) { return Array.from(new Set(list)); }

  /* ------------------------------- Índices -------------------------------- */
  function buildIndex(data) {
    const categorias = data.categorias.slice().sort((a, b) => a.orden - b.orden);
    const catBySlug = {};
    const catById = {};
    const afecciones = {};
    const afeccionesByCat = {};
    const docsByCat = {};
    const docsByAfeccion = {};

    categorias.forEach((cat) => { catBySlug[cat.slug] = cat; catById[cat.id] = cat; });

    data.afecciones.forEach((a) => {
      afecciones[a.id] = a;
      (afeccionesByCat[a.categoria_id] = afeccionesByCat[a.categoria_id] || []).push(a);
    });

    const docs = data.documentos.slice().sort(byDateDesc);
    docs.forEach((doc) => {
      (docsByCat[doc.categoria_id] = docsByCat[doc.categoria_id] || []).push(doc);
      (docsByAfeccion[doc.afeccion_id] = docsByAfeccion[doc.afeccion_id] || []).push(doc);
    });

    const diagnosticos = data.afecciones
      .filter((a) => a.categoria_id !== 'medicamentos' && a.categoria_id !== 'laboratorio')
      .sort((a, b) => (a.tipo === b.tipo ? byDateDesc(a, b) : a.tipo === 'activa' ? -1 : 1));

    const meds = data.medicamentos.slice().sort((a, b) => {
      if (a.activo !== b.activo) return a.activo ? -1 : 1;
      return String(b.inicio).localeCompare(String(a.inicio));
    });

    const panels = unique(data.laboratorio.map((row) => row.panel));
    const latestLab = data.laboratorio.reduce((max, row) => (row.fecha > max ? row.fecha : max), '');

    idx = {
      categorias,
      grupos: data.grupos,
      catBySlug,
      catById,
      afecciones,
      afeccionesByCat,
      docs,
      docsByCat,
      docsByAfeccion,
      diagnosticos,
      meds,
      medsActive: meds.filter((m) => m.activo),
      labs: data.laboratorio,
      labsAbnormal: data.laboratorio.filter((row) => row.estado !== 'normal'),
      latestLab,
      panels,
      alergias: data.alergias,
      contactos: data.contactos.slice().sort((a, b) => a.orden - b.orden),
      principios: data.principios
    };
  }

  function docsForCat(cat) {
    if (!cat) return [];
    return idx.docsByCat[cat.id] || [];
  }

  function docsForAfeccion(id) { return idx.docsByAfeccion[id] || []; }

  function docsForDiagnoses() {
    const ids = new Set(idx.diagnosticos.map((a) => a.id));
    return idx.docs.filter((doc) => ids.has(doc.afeccion_id));
  }

  function catName(id) { return idx.catById[id] ? idx.catById[id].nombre : 'Registro clínico'; }

  function catMeta(cat) {
    if (!cat) return '';
    if (cat.tipo === 'diagnosticos') return idx.diagnosticos.length + ' condiciones';
    if (cat.tipo === 'medicamentos') return idx.medsActive.length + ' activos';
    if (cat.tipo === 'laboratorio') return idx.labs.length + ' resultados';
    if (cat.tipo === 'emergencia') return idx.contactos.length + ' contactos';
    return cat.estado || 'En seguimiento';
  }

  function homeMeta(cat) {
    const pieces = [catMeta(cat)];
    if (cat.tipo !== 'emergencia') pieces.push(formatDate(cat.actualizado, 'medium'));
    else pieces.push('Siempre disponible');
    return pieces.join(' · ');
  }

  function activeDiagnoses() { return idx.diagnosticos.filter((a) => a.tipo === 'activa'); }

  /* -------------------------------- Chrome -------------------------------- */
  function setText(selector, text) {
    document.querySelectorAll(selector).forEach((el) => { el.textContent = text; });
  }

  function navItem(cat) {
    return '<a class="nav-panel__link" href="#/categoria/' + attr(cat.slug) + '">' +
      '<span class="nav-panel__icon">' + icon(catIcon(cat), 18) + '</span>' +
      '<span><span class="nav-panel__title">' + esc(cat.nombre) + '</span>' +
      '<span class="nav-panel__desc">' + esc(catMeta(cat)) + '</span></span></a>';
  }

  function drawerItem(cat) {
    return '<a class="drawer__link" href="#/categoria/' + attr(cat.slug) + '">' +
      '<span class="drawer__link-icon">' + icon(catIcon(cat), 18) + '</span>' +
      esc(cat.nombre) + icon('chevron-right', 16) + '</a>';
  }

  function populateChrome() {
    document.querySelectorAll('[data-nav-group]').forEach((wrap) => {
      const group = wrap.getAttribute('data-nav-group');
      wrap.innerHTML = idx.categorias.filter((cat) => cat.grupo === group).map(navItem).join('');
    });

    document.querySelectorAll('[data-drawer-group]').forEach((wrap) => {
      const group = wrap.getAttribute('data-drawer-group');
      wrap.innerHTML = idx.categorias.filter((cat) => cat.grupo === group).map(drawerItem).join('');
    });

    document.querySelectorAll('[data-footer-group]').forEach((wrap) => {
      const group = wrap.getAttribute('data-footer-group');
      wrap.innerHTML = idx.categorias
        .filter((cat) => cat.grupo === group)
        .map((cat) => '<li><a href="#/categoria/' + attr(cat.slug) + '">' + esc(cat.nombre) + '</a></li>')
        .join('');
    });

    const diagFoot = document.querySelector('.nav-panel__foot a[href="#/categoria/diagnosticos"]');
    if (diagFoot) diagFoot.innerHTML = 'Ver las ' + idx.diagnosticos.length + ' condiciones ' + icon('arrow-right', 14);
    const espFoot = document.querySelector('.nav-panel__foot a[href="#/categoria/neurologia"]');
    if (espFoot) espFoot.innerHTML = 'Explorar las ' + idx.categorias.filter((c) => c.tipo === 'especialidad').length + ' especialidades ' + icon('arrow-right', 14);

    const profile = D.perfil;
    const privateMode = CONFIG.auth && CONFIG.auth.mode === 'supabase';
    setText('#user-name', profile.nombre);
    setText('#user-email', privateMode ? (profile.correo || 'Sesión iniciada') : 'Acceso libre · sin clave');
    setText('#drawer-user-name', profile.nombre);
    document.querySelectorAll('.avatar').forEach((el) => { el.textContent = profile.iniciales || 'RC'; });

    document.querySelectorAll('#footer-year').forEach((el) => { el.textContent = String(new Date().getFullYear()); });
    document.querySelectorAll('#footer-version').forEach((el) => { el.textContent = CONFIG.version; });

    // Hidrata los iconos estáticos del encabezado, cajón y pie.
    Icons.hydrate(document);

    const printDate = document.getElementById('print-date');
    if (printDate) {
      printDate.textContent = new Intl.DateTimeFormat(CONFIG.formatos.locale, {
        day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
      }).format(new Date());
    }
  }

  /* ---------------------------- Componentes ------------------------------- */
  function pageHero(cat, options) {
    const opts = options || {};
    const accent = cat.acento || 'verde';
    const group = idx.grupos.find((g) => g.id === cat.grupo);
    const chips = (opts.chips || []).join('');
    return '<section class="page-hero accent-' + attr(accent) + '">' +
      '<span class="page-hero__watermark" aria-hidden="true">' + icon(catIcon(cat), 76) + '</span>' +
      '<div class="container">' +
        '<nav class="breadcrumb" aria-label="Ruta de navegación">' +
          '<a href="#/">Inicio</a>' + icon('chevron-right', 14) +
          '<span>' + esc(group ? group.nombre : 'Registro clínico') + '</span>' + icon('chevron-right', 14) +
          '<span aria-current="page">' + esc(cat.nombre) + '</span>' +
        '</nav>' +
        '<div class="page-hero__grid">' +
          '<div>' +
            '<div class="page-hero__icon">' + icon(catIcon(cat), 32) + '</div>' +
            '<h1>' + esc(opts.title || cat.nombre) + '</h1>' +
            '<p class="page-hero__lead">' + esc(opts.lead || cat.resumen) + '</p>' +
            (chips ? '<div class="page-hero__chips">' + chips + '</div>' : '') +
          '</div>' +
          '<div class="page-hero__aside">' + (opts.aside || defaultAside(cat)) + '</div>' +
        '</div>' +
      '</div>' +
    '</section>';
  }

  function simpleHero(options) {
    const opts = options || {};
    const accent = opts.accent || 'verde';
    return '<section class="page-hero accent-' + attr(accent) + '">' +
      '<span class="page-hero__watermark" aria-hidden="true">' + icon(opts.icon || 'folder', 76) + '</span>' +
      '<div class="container">' +
        '<nav class="breadcrumb" aria-label="Ruta de navegación">' +
          '<a href="#/">Inicio</a>' + icon('chevron-right', 14) +
          '<span aria-current="page">' + esc(opts.title) + '</span>' +
        '</nav>' +
        '<div class="page-hero__grid">' +
          '<div>' +
            '<div class="page-hero__icon">' + icon(opts.icon || 'folder', 32) + '</div>' +
            '<h1>' + esc(opts.title) + '</h1>' +
            '<p class="page-hero__lead">' + esc(opts.lead) + '</p>' +
            (opts.chips && opts.chips.length ? '<div class="page-hero__chips">' + opts.chips.join('') + '</div>' : '') +
          '</div>' +
          (opts.aside ? '<div class="page-hero__aside">' + opts.aside + '</div>' : '') +
        '</div>' +
      '</div>' +
    '</section>';
  }

  function defaultAside(cat) {
    if (cat.tipo === 'diagnosticos') {
      return '<span class="label">Tu panorama</span>' +
        '<strong class="value value--big">' + idx.diagnosticos.length + ' condiciones</strong>' +
        '<hr class="divider">' +
        '<span class="label">Actualizado</span><span class="value">' + formatDate(cat.actualizado) + '</span>' +
        '<a href="#/categoria/medicamentos">Revisar tratamiento</a>';
    }
    if (cat.tipo === 'medicamentos') {
      return '<span class="label">Tratamiento vigente</span>' +
        '<strong class="value value--big">' + idx.medsActive.length + ' activos</strong>' +
        '<hr class="divider">' +
        '<span class="label">Alergias registradas</span><span class="value">' + idx.alergias.length + ' · ' + esc(idx.alergias[0] ? idx.alergias[0].sustancia : 'Sin datos') + '</span>' +
        '<a href="#/categoria/laboratorio">Ver examen de control</a>';
    }
    if (cat.tipo === 'laboratorio') {
      return '<span class="label">Último panel</span>' +
        '<strong class="value value--big">' + esc(formatDate(idx.latestLab, 'medium')) + '</strong>' +
        '<hr class="divider">' +
        '<span class="label">Fuera de rango</span><span class="value">' + idx.labsAbnormal.length + ' de ' + idx.labs.length + ' resultados</span>' +
        '<a href="#/categoria/cardiologia">Revisar control cardiovascular</a>';
    }
    if (cat.tipo === 'emergencia') {
      return '<span class="label">Grupo sanguíneo</span>' +
        '<strong class="value value--big">' + esc(D.critico.grupoSanguineo) + '</strong>' +
        '<hr class="divider">' +
        '<span class="label">Contactos</span><span class="value">' + idx.contactos.length + ' teléfonos directos</span>' +
        '<a href="' + attr(CONFIG.rutas.emergenciaPublica) + '">Abrir ficha pública</a>';
    }
    const mainAfeccion = idx.afecciones[cat.afeccion_id];
    return '<span class="label">Estado actual</span>' +
      '<strong class="value value--big">' + esc(mainAfeccion ? mainAfeccion.estado : (cat.estado || 'En seguimiento')) + '</strong>' +
      '<hr class="divider">' +
      '<span class="label">Profesional</span><span class="value">' + esc(mainAfeccion ? mainAfeccion.medico : 'Por confirmar') + '</span>' +
      '<a href="#/documentos?cat=' + attr(cat.slug) + '">Ver documentos</a>';
  }

  function sectionNav(items) {
    return '<nav class="section-nav" aria-label="Secciones de esta página">' +
      '<div class="container section-nav__inner">' +
        items.map((item) => '<a href="#/categoria/actual" data-scroll="' + attr(item.id) + '">' +
          (item.icon ? icon(item.icon, 15) : '') + esc(item.label) + '</a>').join('') +
      '</div>' +
    '</nav>';
  }

  function docCard(doc, options) {
    const opts = options || {};
    const cat = idx.catById[doc.categoria_id];
    const meta = [opts.showCategory && cat ? cat.nombre : null, formatDate(doc.fecha, 'medium'), doc.tipo_archivo || 'PDF', doc.tamano].filter(Boolean).join(' · ');
    const search = strip([doc.nombre, doc.descripcion, cat ? cat.nombre : '', doc.fecha].join(' '));
    return '<article class="doc-card" data-doc-card data-cat="' + attr(doc.categoria_id) + '" data-search="' + attr(search) + '">' +
      '<span class="doc-card__icon">' + icon('file-text', 22) + '</span>' +
      '<div><span class="doc-card__name">' + esc(doc.nombre) + '</span>' +
      '<span class="doc-card__meta">' + esc(meta) + (doc.descripcion ? ' · ' + esc(doc.descripcion) : '') + '</span></div>' +
      '<div class="doc-card__actions">' +
        '<button class="icon-btn" type="button" data-doc="' + attr(doc.id) + '" aria-label="Vista previa de ' + attr(doc.nombre) + '">' + icon('eye', 18) + '</button>' +
        '<a class="icon-btn" href="' + attr(doc.archivo) + '" download aria-label="' + attr('Descargar ' + doc.nombre + ', ' + (doc.tipo_archivo || 'PDF') + ', ' + (doc.tamano || 'documento')) + '">' + icon('download', 18) + '</a>' +
      '</div>' +
    '</article>';
  }

  function docStack(docs, emptyText) {
    if (!docs.length) {
      return '<div class="doc-empty">' + icon('info', 20) + '<span>' + esc(emptyText || 'No hay documentos asociados a esta sección.') + '</span></div>';
    }
    return '<div class="doc-stack">' + docs.map((doc) => docCard(doc)).join('') + '</div>';
  }

  function noteList(notes, label) {
    if (!notes || !notes.length) return '';
    return '<div class="note-list">' + notes.map((note) => '<div class="note">' +
      '<span class="note__check">' + icon('check', 14) + '</span>' +
      '<span>' + (label ? '<strong>' + esc(label) + '</strong> ' : '') + esc(note) + '</span>' +
    '</div>').join('') + '</div>';
  }

  function conditionCard(a, options) {
    const opts = options || {};
    const accent = toneOf(a.tono);
    const docs = docsForAfeccion(a.id);
    return '<article class="condition-card accent-' + attr(accent) + '" data-condition-card data-status="' + attr(a.tipo) + '" data-estado="' + attr(strip(a.estado)) + '" data-search="' + attr(strip([a.titulo, a.descripcion, a.medico, a.especialidad, a.cie10, a.estado].join(' '))) + '">' +
      '<div class="condition-card__top">' +
        '<h3 class="condition-card__title">' + esc(a.titulo) + '</h3>' +
        statusBadge(a.estado, a.tono === 'ambar' ? 'ambar' : a.tono, a.tipo === 'activa' ? 'activity' : 'check-circle') +
      '</div>' +
      '<p class="condition-card__desc">' + esc(a.descripcion) + '</p>' +
      '<div class="condition-card__meta">' +
        '<span>' + icon('calendar', 14) + '<strong>' + esc(formatDate(a.fecha_diagnostico, 'medium')) + '</strong></span>' +
        '<span>' + icon('stethoscope', 14) + '<strong>' + esc(a.medico) + '</strong></span>' +
        '<span>' + icon('activity', 14) + '<strong>' + esc(a.especialidad) + '</strong></span>' +
        '<span>' + icon('folder', 14) + '<strong>' + docs.length + ' ' + countLabel(docs.length, 'documento', 'documentos') + '</strong></span>' +
      '</div>' +
      '<div class="condition-card__foot">' +
        '<span class="condition-card__cie">' + (a.cie10 ? 'CIE-10 ' + esc(a.cie10) : 'Sin código CIE-10') + '</span>' +
        (opts.hideButton ? '' : '<button class="btn btn--ghost btn--sm" type="button" data-condition="' + attr(a.id) + '">Ver detalle ' + icon('arrow-right', 15) + '</button>') +
      '</div>' +
    '</article>';
  }

  function timeline(entries) {
    if (!entries.length) {
      return '<div class="empty-state">' + icon('clock', 28) + '<h3>Sin evoluciones registradas</h3><p>Aún no hay controles en esta sección.</p></div>';
    }
    return '<div class="timeline">' + entries.map((entry) => '<div class="timeline__item">' +
      '<span class="timeline__date">' + esc(formatDate(entry.fecha, 'short')) + '<small>' + esc(yearOf(entry.fecha)) + '</small></span>' +
      '<div class="timeline__body">' +
        '<h3 class="timeline__title">' + esc(entry.titulo) +
          (entry.badge ? '<span class="chip chip--neutral">' + esc(entry.badge) + '</span>' : '') +
        '</h3>' +
        '<p class="timeline__text">' + esc(entry.hallazgo) + '</p>' +
        '<div class="timeline__action">' + icon('arrow-right', 14) + '<span><strong>Plan:</strong> ' + esc(entry.accion) + '</span></div>' +
      '</div>' +
    '</div>').join('') + '</div>';
  }

  function asideKey(rows) {
    return '<dl class="kv">' + rows.map((row) => '<div class="kv__row"><dt>' + esc(row[0]) + '</dt><dd>' + esc(row[1]) + '</dd></div>').join('') + '</dl>';
  }

  function asideDocs(docs, limit, href) {
    if (!docs.length) return '<p class="tiny soft">Sin documentos asociados.</p>';
    const shown = docs.slice(0, limit || 3);
    return '<div class="aside-docs">' + shown.map((doc) => '<button class="aside-doc" type="button" data-doc="' + attr(doc.id) + '" aria-label="' + attr('Vista previa de ' + doc.nombre) + '">' +
      icon('file-text', 16) + '<span>' + esc(doc.nombre) + '</span></button>').join('') + '</div>' +
      '<a class="aside-link" href="' + attr(href || '#/documentos') + '">Ver todos los documentos ' + icon('arrow-right', 15) + '</a>';
  }

  /* -------------------------------- Portada ------------------------------- */
  function healthCard(cat) {
    const accent = cat.acento || 'verde';
    const emergency = cat.id === 'emergencia';
    return '<a class="health-card accent-' + attr(accent) + (emergency ? ' health-card--emergency' : '') + '" href="#/categoria/' + attr(cat.slug) + '">' +
      '<div class="health-card__top">' +
        '<span class="health-card__icon">' + icon(catIcon(cat), 25) + '</span>' +
        (emergency ? '<span class="health-card__flag">' + icon('alert-triangle', 12) + ' Prioritario</span>' : '<span class="chip chip--' + (accent === 'amarillo' ? 'amarillo' : accent) + '">' + esc(catMeta(cat)) + '</span>') +
      '</div>' +
      '<h3 class="health-card__title">' + esc(cat.nombre) + '</h3>' +
      '<p class="health-card__desc">' + esc(cat.descripcion) + '</p>' +
      '<div class="health-card__foot">' +
        '<span class="health-card__meta">' + icon(emergency ? 'phone-call' : 'refresh', 14) + esc(homeMeta(cat)) + '</span>' +
        '<span class="health-card__arrow">' + icon('arrow-right', 17) + '</span>' +
      '</div>' +
    '</a>';
  }

  function groupSection(group, number) {
    const cats = idx.categorias.filter((cat) => cat.grupo === group.id);
    const gridClass = group.id === 'emergencia' ? 'cards-grid cards-grid--emergencia' : group.id === 'especialidades' ? 'cards-grid cards-grid--especialidades' : 'cards-grid';
    const count = group.id === 'emergencia'
      ? idx.contactos.length + ' contactos directos'
      : group.id === 'especialidades'
        ? cats.length + ' especialidades'
        : cats.length + ' secciones';
    return '<div class="group-section" id="grupo-' + attr(group.id) + '">' +
      '<div class="group-head">' +
        '<span class="group-num" aria-hidden="true">' + String(number).padStart(2, '0') + '</span>' +
        '<div><h2 class="group-title">' + esc(group.nombre) + '</h2><p class="group-desc">' + esc(group.descripcion) + '</p></div>' +
        '<span class="group-count">' + icon(group.id === 'emergencia' ? 'phone-call' : 'list', 14) + esc(count) + '</span>' +
      '</div>' +
      '<div class="' + gridClass + '">' + cats.map(healthCard).join('') + '</div>' +
    '</div>';
  }

  function renderHome() {
    const p = D.perfil;
    const c = D.critico;
    const active = activeDiagnoses().length;
    const recent = idx.docs.slice(0, 4);
    const samu = idx.contactos.find((x) => x.nombre === 'SAMU') || { telefono: '131' };
    const allergy = c.alergias[0];
    const specialties = idx.categorias.filter((x) => x.tipo === 'especialidad').length;

    return '<section class="hero">' +
      '<div class="container hero__grid">' +
        '<div class="hero__copy">' +
          '<span class="hero__eyebrow"><span class="dot"></span> Actualizado el ' + esc(formatDate(D.meta.actualizado)) + (D.meta.demo ? ' · Modo demostración' : '') + '</span>' +
          '<h1>Hola, ' + esc(p.preferido || p.nombre.split(' ')[0]) + '.<br>Tu salud, <span class="highlight">clara</span><br>y <span class="highlight-coral">a mano</span>.</h1>' +
          '<p class="hero__lead">Diagnósticos, tratamiento, exámenes y documentos en una sola historia. Clara para ti, útil para tu familia y lista para cualquier profesional que la necesite.</p>' +
          '<div class="hero__actions">' +
            '<a class="btn btn--primary btn--lg" href="#/categoria/diagnosticos">' + icon('clipboard-pulse', 19) + ' Ver mi registro clínico</a>' +
            '<a class="btn btn--secondary btn--lg" href="#/categoria/emergencia">' + icon('phone-call', 19) + ' Ficha de emergencia</a>' +
          '</div>' +
          '<p class="hero__meta">' +
            '<span>' + icon('eye', 14) + ' Acceso libre sin clave</span>' +
            '<span>' + icon('shield-check', 14) + ' Sin buscadores ni terceros</span>' +
            '<span>' + icon('folder', 14) + ' ' + idx.docs.length + ' documentos disponibles</span>' +
          '</p>' +
        '</div>' +
        '<div class="hero-art" aria-hidden="true">' +
          '<div class="hero-art__blob"></div><div class="hero-art__ring"></div><div class="hero-art__dot"></div>' +
          '<div class="hero-card">' +
            '<div class="hero-card__head">' +
              '<div class="hero-card__title">' + icon('shield-heart', 22) + '<span>Ficha esencial<small>Resumen de emergencia</small></span></div>' +
              '<span class="hero-card__pulse">' + icon('heart-pulse', 20) + '</span>' +
            '</div>' +
            '<div class="hero-card__ecg">' +
              '<svg viewBox="0 0 300 34" role="presentation" focusable="false"><path d="M0 20h45l8-13 10 25 12-30 14 30 10-17 8 5h48l9-11 9 21 12-28 13 28 9-16 7 6h46" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>' +
            '</div>' +
            '<div class="hero-card__rows">' +
              '<div class="hero-card__row"><span>' + icon('droplet', 15) + ' Grupo sanguíneo</span><strong>' + esc(c.grupoSanguineo) + '</strong></div>' +
              '<div class="hero-card__row"><span>' + icon('alert-triangle', 15) + ' Alergia principal</span><strong>' + esc(allergy ? allergy.sustancia : 'Sin registrar') + '</strong></div>' +
              '<div class="hero-card__row"><span>' + icon('pill', 15) + ' Tratamiento</span><strong>' + idx.medsActive.length + ' activos</strong></div>' +
              '<div class="hero-card__row"><span>' + icon('clipboard-pulse', 15) + ' Condiciones</span><strong>' + active + ' en seguimiento</strong></div>' +
            '</div>' +
            '<div class="hero-card__foot"><span>Actualizado ' + esc(formatDate(D.meta.actualizado, 'medium')) + '</span><span>Datos de ejemplo</span></div>' +
          '</div>' +
          '<span class="hero-float hero-float--1"><span class="hero-float__icon">' + icon('book', 15) + '</span><span>' + idx.docs.length + ' documentos<small>Informes y recetas</small></span></span>' +
          '<span class="hero-float hero-float--2"><span class="hero-float__icon">' + icon('heart-pulse', 15) + '</span><span>' + specialties + ' especialidades<small>Una sola historia</small></span></span>' +
          '<span class="hero-float hero-float--3"><span class="hero-float__icon">' + icon('users', 15) + '</span><span>' + idx.contactos.length + ' contactos<small>Llamada directa</small></span></span>' +
          '<span class="hero-float hero-float--4"><span class="hero-float__icon">' + icon('shield-check', 15) + '</span><span>Sin indexar<small>Fuera de buscadores</small></span></span>' +
        '</div>' +
      '</div>' +

      '<div class="container">' +
        '<div class="snapshot">' +
          '<div class="snapshot__head">' +
            '<span class="snapshot__title">' + icon('shield-heart', 19) + ' Lo esencial, en 20 segundos</span>' +
            '<a class="text-link" href="' + attr(CONFIG.rutas.emergenciaPublica) + '" target="_blank" rel="noopener">Abrir ficha pública ' + icon('external-link', 14) + '</a>' +
          '</div>' +
          '<div class="snapshot__grid">' +
            '<a class="snapshot__item" href="#/categoria/emergencia"><span class="snapshot__icon">' + icon('droplet', 19) + '</span><span><span class="snapshot__label">Grupo sanguíneo</span><span class="snapshot__value">' + esc(c.grupoSanguineo) + '</span><span class="snapshot__note">Dato crítico</span></span></a>' +
            '<a class="snapshot__item" href="#/categoria/medicamentos"><span class="snapshot__icon">' + icon('alert-triangle', 19) + '</span><span><span class="snapshot__label">Alergia medicamentosa</span><span class="snapshot__value">' + esc(allergy ? allergy.sustancia + ' · ' + allergy.severidad : 'Sin registrar') + '</span><span class="snapshot__note">Informar en cada atención</span></span></a>' +
            '<a class="snapshot__item" href="#/categoria/diagnosticos"><span class="snapshot__icon">' + icon('clipboard-pulse', 19) + '</span><span><span class="snapshot__label">Condiciones activas</span><span class="snapshot__value">' + active + ' en seguimiento</span><span class="snapshot__note">Con plan y evolución</span></span></a>' +
            '<a class="snapshot__item" href="#/documentos"><span class="snapshot__icon">' + icon('folder', 19) + '</span><span><span class="snapshot__label">Documentos</span><span class="snapshot__value">' + idx.docs.length + ' archivos</span><span class="snapshot__note">Último: ' + esc(formatDate(idx.docs[0] ? idx.docs[0].fecha : null, 'medium')) + '</span></span></a>' +
          '</div>' +
        '</div>' +
      '</div>' +
    '</section>' +

    '<div class="container">' +
      D.grupos.map((group, i) => groupSection(group, i + 1)).join('') +
    '</div>' +

    '<section class="section">' +
      '<div class="container recent-grid">' +
        '<div class="recent-copy">' +
          '<p class="eyebrow">Documentos recientes</p>' +
          '<h2>Todo respaldado, todo descargable.</h2>' +
          '<p>Informes, recetas y exámenes con fecha y contexto. Puedes revisarlos aquí o descargarlos para llevarlos a una consulta.</p>' +
          '<a class="btn btn--secondary" href="#/documentos">' + icon('folder', 18) + ' Abrir biblioteca completa</a>' +
        '</div>' +
        '<div class="doc-list">' +
          recent.map((doc) => '<button class="doc-list__item" type="button" data-doc="' + attr(doc.id) + '">' +
            '<span class="doc-list__icon">' + icon('file-text', 20) + '</span>' +
            '<span><span class="doc-list__name">' + esc(doc.nombre) + '</span><span class="doc-list__meta">' + esc(catName(doc.categoria_id)) + ' · ' + esc(formatDate(doc.fecha, 'medium')) + '</span></span>' +
            '<span class="doc-list__arrow">' + icon('arrow-right', 17) + '</span>' +
          '</button>').join('') +
        '</div>' +
      '</div>' +
    '</section>' +

    '<section class="section section--tight">' +
      '<div class="container">' +
        '<div class="principles-band">' +
          '<div class="principles-band__head">' +
            '<div><p class="eyebrow eyebrow--cream">Cómo está pensado</p><h2>Un registro que se entiende.</h2></div>' +
            '<p>La información clínica sirve cuando es clara, está ordenada y aparece en el momento correcto.</p>' +
          '</div>' +
          '<div class="principles-grid">' +
            idx.principios.map((principle, i) => '<article class="principle"><span class="principle__num">' + String(i + 1).padStart(2, '0') + '</span>' +
              '<span class="principle__icon">' + icon(principle.icono, 20) + '</span>' +
              '<h3>' + esc(principle.titulo) + '</h3><p>' + esc(principle.texto) + '</p></article>').join('') +
          '</div>' +
        '</div>' +
      '</div>' +
    '</section>' +

    '<section class="section section--tight">' +
      '<div class="container">' +
        '<div class="emergency-band">' +
          '<div class="emergency-band__copy">' +
            '<p class="eyebrow eyebrow--coral">Cuando no hay tiempo</p>' +
            '<h2>La información crítica, sin laberintos.</h2>' +
            '<p>Grupo sanguíneo, alergias, condiciones y teléfonos directos en una sola pantalla. También puedes imprimir una ficha para llevar contigo.</p>' +
            '<div class="emergency-band__actions">' +
              '<a class="btn btn--dark" href="#/categoria/emergencia">' + icon('phone-call', 18) + ' Ver contactos de emergencia</a>' +
              '<a class="btn btn--ghost" href="' + attr(CONFIG.rutas.emergenciaPublica) + '" target="_blank" rel="noopener">' + icon('printer', 18) + ' Ficha imprimible</a>' +
            '</div>' +
          '</div>' +
          '<div class="emergency-band__card">' +
            '<span class="icon">' + icon('phone-call', 24) + '</span>' +
            '<span class="emergency-band__number">' + esc(samu.telefono) + '</span>' +
            '<span class="emergency-band__label">SAMU · Chile</span>' +
            '<a class="btn btn--primary btn--sm" href="' + attr(telHref(samu.telefono)) + '">Llamar ahora</a>' +
          '</div>' +
        '</div>' +
      '</div>' +
    '</section>';
  }

  function render404() {
    return '<section class="section">' +
      '<div class="container">' +
        '<div class="empty-state">' +
          icon('compass', 34) +
          '<h1>No encontramos esta página</h1>' +
          '<p>El enlace puede estar incompleto o la sección cambió de nombre.</p>' +
          '<div class="hero__actions" style="justify-content:center">' +
            '<a class="btn btn--primary" href="#/">Volver al inicio</a>' +
            '<a class="btn btn--secondary" href="#/documentos">Ir a documentos</a>' +
          '</div>' +
        '</div>' +
      '</div>' +
    '</section>';
  }

  /* -------------------------------- Rutas --------------------------------- */
  function parseRoute() {
    const raw = window.location.hash.replace(/^#/, '');
    if (!raw || raw === '/' || raw === '') return { name: 'home' };
    const pieces = raw.split('?');
    const segments = pieces[0].replace(/^\/+/, '').replace(/\/+$/, '').split('/');
    const query = new URLSearchParams(pieces[1] || '');
    if (segments[0] === 'categoria') return { name: 'categoria', slug: decodeURIComponent(segments[1] || ''), query };
    if (segments[0] === 'documentos') return { name: 'documentos', query };
    if (segments[0] === 'acerca') return { name: 'acerca' };
    if (segments[0] === 'afeccion') return { name: 'afeccion', id: decodeURIComponent(segments[1] || '') };
    return { name: '404' };
  }

  function renderCategory(cat) {
    const view = views[cat.tipo] || views.especialidad;
    if (!view) return render404();
    const result = view(cat);
    return typeof result === 'string' ? { html: result } : result;
  }

  function updateActiveNav(cat) {
    const home = !cat;
    document.querySelectorAll('[data-nav-home]').forEach((el) => {
      el.classList.toggle('is-active', home);
      if (home) el.setAttribute('aria-current', 'page'); else el.removeAttribute('aria-current');
    });
    document.querySelectorAll('[data-nav-docs]').forEach((el) => {
      const current = parseRoute().name === 'documentos';
      el.classList.toggle('is-active', current);
      if (current) el.setAttribute('aria-current', 'page'); else el.removeAttribute('aria-current');
    });
    document.querySelectorAll('.drawer__link[href]').forEach((el) => {
      const current = !!cat && el.getAttribute('href') === '#/categoria/' + cat.slug;
      el.classList.toggle('is-active', current);
      if (current) el.setAttribute('aria-current', 'page'); else el.removeAttribute('aria-current');
    });
  }

  function route() {
    if (!D) return;
    const r = parseRoute();
    let result = null;
    let cat = null;
    let after = null;

    if (r.name === 'home') {
      result = { html: renderHome() };
    } else if (r.name === 'categoria') {
      cat = idx.catBySlug[r.slug];
      if (!cat) result = { html: render404() };
      else result = renderCategory(cat);
    } else if (r.name === 'documentos') {
      result = views.documentos ? views.documentos(r) : { html: render404() };
    } else if (r.name === 'acerca') {
      result = views.acerca ? views.acerca(r) : { html: render404() };
    } else if (r.name === 'afeccion') {
      const afeccion = idx.afecciones[r.id];
      if (!afeccion) {
        result = { html: render404() };
      } else {
        cat = idx.catById[afeccion.categoria_id];
        result = renderCategory(cat);
        after = function () {
          if (window.history.replaceState) window.history.replaceState(null, '', '#/categoria/' + cat.slug);
          window.setTimeout(function () {
            if (window.SaludUI) window.SaludUI.openCondition(afeccion.id);
          }, 50);
        };
      }
    } else {
      result = { html: render404() };
    }

    appRoot.innerHTML = result.html;
    Icons.hydrate(appRoot);
    if (typeof result.mount === 'function') {
      try { result.mount(appRoot); } catch (error) { console.error('[saludrcartes] Error al montar la vista', error); }
    }

    updateActiveNav(cat);

    const titles = {
      home: 'Inicio',
      documentos: 'Biblioteca de documentos',
      acerca: 'Acerca y privacidad',
      404: 'Página no encontrada'
    };
    const title = cat ? cat.nombre : (titles[r.name] || 'Registro clínico');
    document.title = title + ' · saludrcartes';

    if (window.SaludUI) {
      try { window.SaludUI.onRoute(); } catch (error) { console.error('[saludrcartes] Error en la interfaz', error); }
    }

    window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
    if (main) main.focus({ preventScroll: true });
    if (after) after();
    if (r.query && r.query.get('sec')) {
      const target = document.getElementById(r.query.get('sec'));
      if (target) window.setTimeout(function () { target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 120);
    }
  }

  function registerView(name, fn) { views[name] = fn; }

  function init(data) {
    if (!data || !Array.isArray(data.categorias)) {
      throw new Error('Los datos clínicos no tienen el formato esperado.');
    }
    D = data;
    buildIndex(data);
    populateChrome();

    if (window.SaludUI && typeof window.SaludUI.init === 'function') {
      window.SaludUI.init();
    }

    window.addEventListener('hashchange', route);
    if (!window.location.hash) {
      if (window.history.replaceState) window.history.replaceState(null, '', '#/');
    }
    route();
  }

  /* ------------------------------- Exports -------------------------------- */
  window.SaludApp = {
    init,
    route,
    registerView,
    get data() { return D; },
    get index() { return idx; },
    get views() { return views; },
    pageHero,
    simpleHero,
    sectionNav,
    docCard,
    docStack,
    noteList,
    conditionCard,
    timeline,
    asideKey,
    asideDocs,
    statusBadge,
    chip,
    telemetry: null,
    util: {
      esc,
      attr,
      strip,
      icon,
      catIcon,
      toneOf,
      formatDate,
      yearOf,
      telHref,
      countLabel,
      docsForCat,
      docsForAfeccion,
      docsForDiagnoses,
      catName,
      catMeta,
      homeMeta,
      activeDiagnoses
    }
  };
})();
