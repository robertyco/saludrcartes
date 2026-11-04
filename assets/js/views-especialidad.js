/* ============================================================================
   saludrcartes — Vistas de especialidades y emergencia interna
   ========================================================================== */

(function () {
  'use strict';

  const App = window.SaludApp;
  if (!App) return;

  const U = App.util;

  function asideActions() {
    return '<div class="aside-card">' +
      '<div class="aside-card__head">' + U.icon('compass', 18) + ' Acciones</div>' +
      '<div class="aside-links">' +
        '<button class="aside-link" type="button" data-action="print">Imprimir esta página ' + U.icon('printer', 16) + '</button>' +
        '<button class="aside-link" type="button" data-action="share">Compartir enlace ' + U.icon('share', 16) + '</button>' +
      '</div>' +
    '</div>';
  }

  /* ----------------------------- Especialidad ----------------------------- */
  function renderEspecialidad(cat) {
    const afecciones = App.index.afeccionesByCat[cat.id] || [];
    const main = afecciones.find((a) => a.id === cat.afeccion_id) || afecciones[0];
    const docs = U.docsForCat(cat);
    const multiple = afecciones.length > 1;

    const evolution = [];
    afecciones.forEach((a) => {
      (a.evolucion || []).forEach((entry) => {
        evolution.push(Object.assign({}, entry, { badge: multiple ? a.titulo : null }));
      });
    });
    evolution.sort((a, b) => String(b.fecha).localeCompare(String(a.fecha)));

    const notes = [];
    afecciones.forEach((a) => (a.notas || []).forEach((note) => { if (notes.indexOf(note) === -1) notes.push(note); }));

    const related = ((main && main.relacionados) || [])
      .map((slug) => App.index.catBySlug[slug])
      .filter((item) => item && item.id !== cat.id);

    const nav = [
      { id: 'resumen', label: 'Resumen', icon: 'compass' }
    ];
    if (multiple) nav.push({ id: 'condiciones', label: 'Condiciones', icon: 'clipboard-pulse' });
    nav.push({ id: 'evolucion', label: 'Evolución', icon: 'clock' });
    nav.push({ id: 'documentos', label: 'Documentos', icon: 'folder' });
    nav.push({ id: 'indicaciones', label: 'Indicaciones', icon: 'check-circle' });

    const html = App.pageHero(cat, {
      chips: [
        App.statusBadge(main ? main.estado : cat.estado, main ? main.tono : 'neutral', 'activity'),
        App.chip((main && main.cie10 ? 'CIE-10 ' + main.cie10 : 'Sin CIE-10'), 'neutral', 'file-text'),
        App.chip(docs.length + ' ' + U.countLabel(docs.length, 'documento', 'documentos'), 'oro', 'folder'),
        App.chip('Actualizado ' + U.formatDate(cat.actualizado, 'medium'), 'neutral', 'refresh')
      ]
    }) +
    App.sectionNav(nav) +
    '<div class="container page-layout">' +
      '<div class="page-main">' +
        '<section class="content-section" id="resumen">' +
          '<div class="section-heading"><h2>' + U.icon('compass', 24) + ' Resumen de la especialidad</h2><span class="section-heading__meta">' + (multiple ? multiple + ' condiciones vinculadas' : '1 condición principal') + '</span></div>' +
          '<div class="summary-grid">' +
            '<div class="info-tile accent-' + U.toneOf(main ? main.tono : 'neutral') + '">' +
              '<span class="info-tile__label">' + U.icon('activity', 14) + ' Estado</span>' +
              '<span class="info-tile__value">' + U.esc(main ? main.estado : cat.estado) + '</span>' +
              '<span class="info-tile__note">' + (main && main.tipo === 'historica' ? 'Condición histórica' : 'Seguimiento vigente') + '</span>' +
            '</div>' +
            '<div class="info-tile">' +
              '<span class="info-tile__label">' + U.icon('calendar', 14) + ' Fecha de diagnóstico</span>' +
              '<span class="info-tile__value">' + U.esc(U.formatDate(main ? main.fecha_diagnostico : cat.actualizado)) + '</span>' +
              '<span class="info-tile__note">' + U.esc(main ? main.especialidad : cat.nombre) + '</span>' +
            '</div>' +
            '<div class="info-tile">' +
              '<span class="info-tile__label">' + U.icon('stethoscope', 14) + ' Profesional tratante</span>' +
              '<span class="info-tile__value">' + U.esc(main ? main.medico : 'Por confirmar') + '</span>' +
              '<span class="info-tile__note">' + U.esc(main ? main.centro : 'Centro por confirmar') + '</span>' +
            '</div>' +
          '</div>' +
          '<div class="callout accent-' + U.toneOf(main ? main.tono : cat.acento) + '">' + U.icon('shield-heart', 20) +
            '<div><strong>Qué está pasando.</strong> ' + U.esc(main ? main.resumen : cat.resumen) + '</div>' +
          '</div>' +
        '</section>' +

        (multiple ? '<section class="content-section" id="condiciones">' +
          '<div class="section-heading"><h2>' + U.icon('clipboard-pulse', 24) + ' Condiciones en esta especialidad</h2><span class="section-heading__meta">' + afecciones.length + ' registros</span></div>' +
          '<div class="condition-grid">' + afecciones.map((a) => App.conditionCard(a)).join('') + '</div>' +
        '</section>' : '') +

        '<section class="content-section" id="evolucion">' +
          '<div class="section-heading"><h2>' + U.icon('clock', 24) + ' Línea de evolución</h2><span class="section-heading__meta">' + evolution.length + ' hitos clínicos</span></div>' +
          App.timeline(evolution) +
        '</section>' +

        '<section class="content-section" id="documentos">' +
          '<div class="section-heading"><h2>' + U.icon('folder', 24) + ' Documentos</h2><span class="section-heading__meta">' + docs.length + ' ' + U.countLabel(docs.length, 'archivo', 'archivos') + '</span></div>' +
          App.docStack(docs, 'Esta especialidad aún no tiene documentos descargables.') +
        '</section>' +

        '<section class="content-section" id="indicaciones">' +
          '<div class="section-heading"><h2>' + U.icon('check-circle', 24) + ' Indicaciones y cuidados</h2></div>' +
          App.noteList(notes, null) +
          '<div class="callout callout--amarillo" style="margin-top:.8rem">' + U.icon('alert-triangle', 20) +
            '<div><strong>Contenido de demostración.</strong> La evolución, los documentos y las indicaciones son ejemplos. No uses esta página para tomar decisiones clínicas reales.</div>' +
          '</div>' +
        '</section>' +
      '</div>' +

      '<aside class="page-aside" aria-label="Información complementaria">' +
        '<div class="aside-card aside-card--key">' +
          '<div class="aside-card__head">' + U.icon('stethoscope', 18) + ' Ficha clave</div>' +
          App.asideKey([
            ['Estado', main ? main.estado : cat.estado],
            ['CIE-10', main && main.cie10 ? main.cie10 : 'No registrado'],
            ['Profesional', main ? main.medico : 'Por confirmar'],
            ['Centro', main ? main.centro : 'Por confirmar'],
            ['Actualizado', U.formatDate(cat.actualizado, 'medium')]
          ]) +
        '</div>' +
        '<div class="aside-card">' +
          '<div class="aside-card__head">' + U.icon('folder', 18) + ' Documentos</div>' +
          App.asideDocs(docs, 3, '#/documentos?cat=' + cat.slug) +
        '</div>' +
        (related.length ? '<div class="aside-card">' +
          '<div class="aside-card__head">' + U.icon('link', 18) + ' Especialidades relacionadas</div>' +
          '<div class="aside-links">' + related.map((item) => '<a class="aside-link" href="#/categoria/' + U.attr(item.slug) + '">' + U.esc(item.nombre) + U.icon('chevron-right', 16) + '</a>').join('') + '</div>' +
        '</div>' : '') +
        '<div class="aside-card aside-card--emergency">' +
          '<div class="aside-card__head">' + U.icon('phone-call', 18) + ' En una urgencia</div>' +
          '<p>Si hay un riesgo vital, llama al 131 y entrega la ficha de emergencia. No esperes a revisar todo el historial.</p>' +
          '<a class="btn btn--dark btn--sm" href="#/categoria/emergencia">Abrir emergencia</a>' +
        '</div>' +
        asideActions() +
      '</aside>' +
    '</div>';

    return { html };
  }

  /* ------------------------------- Emergencia ----------------------------- */
  function contactIcon(contact) {
    const known = ['users', 'stethoscope', 'hospital', 'ambulance', 'shield', 'flame', 'phone', 'phone-call'];
    return known.indexOf(contact.icono) !== -1 ? contact.icono : 'phone-call';
  }

  function renderEmergencia(cat) {
    const data = App.data;
    const critical = data.critico;
    const contacts = App.index.contactos;
    const primary = contacts.find((c) => c.principal) || contacts[0];
    const samu = contacts.find((c) => c.nombre === 'SAMU') || contacts[0];

    const contactCards = contacts.map((contact) => '<article class="contact-card accent-verde' + (contact.principal ? ' contact-card--principal' : '') + '">' +
      '<div class="contact-card__top">' +
        '<span class="contact-card__icon">' + U.icon(contactIcon(contact), 21) + '</span>' +
        '<div><h3 class="contact-card__name">' + U.esc(contact.nombre) + '</h3><span class="contact-card__relation">' + U.esc(contact.relacion) + (contact.principal ? ' · Principal' : '') + '</span></div>' +
      '</div>' +
      '<a class="contact-card__phone" href="' + U.attr(U.telHref(contact.telefono)) + '">' + U.esc(contact.telefono) + '</a>' +
      '<p class="contact-card__note">' + U.esc(contact.nota) + '</p>' +
      '<a class="btn ' + (contact.principal ? 'btn--primary' : 'btn--secondary') + ' btn--sm" href="' + U.attr(U.telHref(contact.telefono)) + '">' + U.icon('phone-call', 16) + ' Llamar</a>' +
    '</article>').join('');

    const html = App.pageHero(cat, {
      chips: [
        App.chip('Grupo sanguíneo ' + critical.grupoSanguineo, 'coral', 'droplet'),
        App.chip(critical.alergias.length + ' alergias', 'amarillo', 'alert-triangle'),
        App.chip(App.index.contactos.length + ' contactos', 'verde', 'phone-call'),
        App.chip('Ficha pública disponible', 'neutral', 'external-link')
      ]
    }) +
    App.sectionNav([
      { id: 'critico', label: 'Información crítica', icon: 'alert-triangle' },
      { id: 'contactos', label: 'Contactos', icon: 'phone-call' },
      { id: 'como-actuar', label: 'Cómo actuar', icon: 'compass' }
    ]) +
    '<div class="container page-layout">' +
      '<div class="page-main">' +
        '<section class="content-section" id="critico">' +
          '<div class="section-heading"><h2>' + U.icon('alert-triangle', 24) + ' Información crítica</h2><span class="section-heading__meta">Actualizado el ' + U.esc(U.formatDate(critical.actualizado)) + '</span></div>' +
          '<div class="critical-panel">' +
            '<div class="critical-panel__blood"><span class="label">Grupo sanguíneo</span><span class="value">' + U.esc(critical.grupoSanguineo) + '</span><p>Confirma este dato en tu carné o examen antes de una transfusión.</p></div>' +
            '<div class="critical-block"><h3>' + U.icon('alert-triangle', 17) + ' Alergias</h3><ul>' +
              critical.alergias.map((a) => '<li>' + U.icon('alert-circle', 14) + '<span><strong>' + U.esc(a.sustancia) + '</strong> · ' + U.esc(a.severidad) + '<br>' + U.esc(a.reaccion) + '</span></li>').join('') +
            '</ul></div>' +
            '<div class="critical-block"><h3>' + U.icon('clipboard-pulse', 17) + ' Condiciones</h3><ul>' +
              critical.condiciones.map((c) => '<li>' + U.icon('activity', 14) + '<span>' + U.esc(c) + '</span></li>').join('') +
            '</ul></div>' +
            '<div class="critical-block"><h3>' + U.icon('pill', 17) + ' Medicamentos</h3><ul>' +
              critical.medicamentos.map((m) => '<li>' + U.icon('pill', 14) + '<span>' + U.esc(m) + '</span></li>').join('') +
            '</ul></div>' +
          '</div>' +
          '<div class="emergency-note">' + U.icon('info', 18) + '<div><strong>Si hay riesgo vital, llama primero.</strong> Comunica el grupo sanguíneo, la alergia a penicilina y los medicamentos activos al personal de salud. La ficha pública resume esta misma información.</div></div>' +
        '</section>' +

        '<section class="content-section" id="contactos">' +
          '<div class="section-heading"><h2>' + U.icon('phone-call', 24) + ' Contactos directos</h2><span class="section-heading__meta">Toca un número para llamar</span></div>' +
          '<div class="contacts-grid">' + contactCards + '</div>' +
        '</section>' +

        '<section class="content-section" id="como-actuar">' +
          '<div class="section-heading"><h2>' + U.icon('compass', 24) + ' Cómo actuar</h2></div>' +
          App.noteList(critical.notas) +
          '<div class="emergency-actions">' +
            '<a class="btn btn--primary" href="assets/docs/emergencia-ficha-resumen.pdf" download>' + U.icon('download', 18) + ' Descargar ficha PDF</a>' +
            '<button class="btn btn--secondary" type="button" data-action="print">' + U.icon('printer', 18) + ' Imprimir esta ficha</button>' +
            '<a class="btn btn--secondary" href="' + U.attr(window.SALUD_CONFIG.rutas.emergenciaPublica) + '" target="_blank" rel="noopener">' + U.icon('external-link', 18) + ' Ficha pública</a>' +
            '<button class="btn btn--secondary" type="button" data-action="share">' + U.icon('share', 18) + ' Compartir enlace</button>' +
          '</div>' +
          '<div class="callout callout--coral" style="margin-top:1rem">' + U.icon('shield-check', 20) +
            '<div><strong>Privacidad:</strong> la ficha pública no incluye diagnósticos, documentos ni el resto del historial. Solo muestra la información necesaria para una urgencia.</div>' +
          '</div>' +
        '</section>' +
      '</div>' +

      '<aside class="page-aside" aria-label="Información complementaria">' +
        '<div class="aside-card aside-card--emergency">' +
          '<div class="aside-card__head">' + U.icon('phone-call', 18) + ' Llamar ahora</div>' +
          '<p>Ambulancia y urgencias en Chile.</p>' +
          '<a class="contact-card__phone" href="' + U.attr(U.telHref(samu.telefono)) + '">' + U.esc(samu.telefono) + '</a>' +
          '<a class="btn btn--dark btn--sm" href="' + U.attr(U.telHref(samu.telefono)) + '">' + U.icon('phone-call', 16) + ' SAMU</a>' +
        '</div>' +
        '<div class="aside-card">' +
          '<div class="aside-card__head">' + U.icon('users', 18) + ' Contacto principal</div>' +
          '<p class="tiny soft">' + U.esc(primary.nombre) + ' · ' + U.esc(primary.relacion) + '</p>' +
          '<a class="contact-card__phone" href="' + U.attr(U.telHref(primary.telefono)) + '">' + U.esc(primary.telefono) + '</a>' +
          '<p class="tiny soft">' + U.esc(primary.nota) + '</p>' +
        '</div>' +
        '<div class="aside-card">' +
          '<div class="aside-card__head">' + U.icon('compass', 18) + ' Qué decir al llamar</div>' +
          '<div class="about-list" style="margin-top:0">' +
            '<li>' + U.icon('check', 15) + ' Nombre completo y edad.</li>' +
            '<li>' + U.icon('check', 15) + ' Qué pasó y desde cuándo.</li>' +
            '<li>' + U.icon('check', 15) + ' Alergia a penicilina y medicamentos activos.</li>' +
            '<li>' + U.icon('check', 15) + ' Dirección exacta y un teléfono de contacto.</li>' +
          '</div>' +
        '</div>' +
        '<div class="aside-card">' +
          '<div class="aside-card__head">' + U.icon('external-link', 18) + ' Ficha pública</div>' +
          '<p class="tiny soft">Una versión mínima, imprimible y sin el historial completo.</p>' +
          '<a class="btn btn--secondary btn--sm btn--block" href="' + U.attr(window.SALUD_CONFIG.rutas.emergenciaPublica) + '" target="_blank" rel="noopener">Abrir ficha</a>' +
        '</div>' +
        asideActions() +
      '</aside>' +
    '</div>';

    return { html };
  }

  App.registerView('especialidad', renderEspecialidad);
  App.registerView('emergencia', renderEmergencia);
})();
