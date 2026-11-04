/* ============================================================================
   saludrcartes — Vistas del registro clínico
   Diagnósticos, medicamentos/alergias y laboratorio.
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

  function sidebarDocs(docs, cat) {
    return '<div class="aside-card">' +
      '<div class="aside-card__head">' + U.icon('folder', 18) + ' Documentos</div>' +
      App.asideDocs(docs, 3, '#/documentos?cat=' + cat.slug) +
    '</div>';
  }

  function emergencyAside() {
    return '<div class="aside-card aside-card--emergency">' +
      '<div class="aside-card__head">' + U.icon('phone-call', 18) + ' En una urgencia</div>' +
      '<p>La ficha de emergencia reúne solo lo crítico, con llamadas directas y una versión imprimible.</p>' +
      '<a class="btn btn--dark btn--sm" href="#/categoria/emergencia">Abrir emergencia</a>' +
    '</div>';
  }

  /* ----------------------------- Diagnósticos ----------------------------- */
  function renderDiagnosticos(cat) {
    const all = App.index.diagnosticos;
    const active = all.filter((a) => a.tipo === 'activa');
    const historical = all.filter((a) => a.tipo === 'historica');
    const inFollowUp = active.filter((a) => /seguimiento|tratamiento|evaluaci[oó]n|progreso/i.test(a.estado));
    const docs = U.docsForDiagnoses();
    const critical = App.data.critico;

    const html = App.pageHero(cat, {
      chips: [
        App.chip(all.length + ' condiciones', 'verde', 'clipboard-pulse'),
        App.chip(docs.length + ' documentos', 'oro', 'folder'),
        App.chip(active.length + ' activas', 'amarillo', 'activity'),
        App.chip('Actualizado ' + U.formatDate(cat.actualizado, 'medium'), 'neutral', 'refresh')
      ]
    }) +
    App.sectionNav([
      { id: 'resumen', label: 'Resumen', icon: 'compass' },
      { id: 'condiciones', label: 'Condiciones', icon: 'clipboard-pulse' },
      { id: 'documentos', label: 'Documentos', icon: 'folder' },
      { id: 'indicaciones', label: 'Indicaciones', icon: 'check-circle' }
    ]) +
    '<div class="container page-layout">' +
      '<div class="page-main">' +
        '<section class="content-section" id="resumen">' +
          '<div class="section-heading"><h2>' + U.icon('compass', 24) + ' Tu panorama clínico</h2><span class="section-heading__meta">Actualizado el ' + U.esc(U.formatDate(cat.actualizado)) + '</span></div>' +
          '<div class="stat-row">' +
            '<div class="stat-card"><span class="stat-card__num">' + all.length + '</span><span class="stat-card__label">condiciones registradas</span></div>' +
            '<div class="stat-card"><span class="stat-card__num">' + active.length + '</span><span class="stat-card__label">activas o en seguimiento</span></div>' +
            '<div class="stat-card"><span class="stat-card__num">' + historical.length + '</span><span class="stat-card__label">históricas y resueltas</span></div>' +
          '</div>' +
          '<div class="callout accent-verde">' +
            U.icon('info', 20) +
            '<div><strong>Una vista, todas las especialidades.</strong> Este listado reúne las condiciones de tu historia clínica, no solo las de una consulta. Cada ficha incluye fecha, código CIE-10, profesional y documentos de respaldo cuando existen.</div>' +
          '</div>' +
        '</section>' +

        '<section class="content-section" id="condiciones">' +
          '<div class="section-heading"><h2>' + U.icon('clipboard-pulse', 24) + ' Condiciones</h2><span class="section-heading__meta">' + inFollowUp.length + ' en seguimiento activo</span></div>' +
          '<div class="toolbar">' +
            '<div class="search-field">' + U.icon('search', 19) +
              '<label class="sr-only" for="condition-search">Buscar en los diagnósticos</label>' +
              '<input class="input" id="condition-search" type="search" placeholder="Buscar por condición, médico o especialidad…" autocomplete="off">' +
            '</div>' +
            '<div class="filter-group" role="group" aria-label="Filtrar diagnósticos">' +
              '<button class="filter-chip" type="button" data-filter="all" aria-pressed="true">Todas</button>' +
              '<button class="filter-chip" type="button" data-filter="activa" aria-pressed="false">Activas</button>' +
              '<button class="filter-chip" type="button" data-filter="seguimiento" aria-pressed="false">En seguimiento</button>' +
              '<button class="filter-chip" type="button" data-filter="historica" aria-pressed="false">Históricas</button>' +
            '</div>' +
          '</div>' +
          '<div class="condition-grid" id="condition-list">' + all.map((a) => App.conditionCard(a)).join('') + '</div>' +
          '<div class="empty-state" id="condition-empty" hidden>' + U.icon('search', 30) + '<h3>Sin resultados</h3><p>Prueba con otra palabra o cambia el filtro.</p></div>' +
        '</section>' +

        '<section class="content-section" id="documentos">' +
          '<div class="section-heading"><h2>' + U.icon('folder', 24) + ' Documentos de respaldo</h2><span class="section-heading__meta">' + docs.length + ' archivos vinculados</span></div>' +
          App.docStack(docs.slice(0, 6), 'Aún no hay documentos vinculados a los diagnósticos.') +
          (docs.length > 6 ? '<p class="tiny soft" style="margin-top:.7rem">Mostrando 6 de ' + docs.length + '. <a class="text-link" href="#/documentos">Ver la biblioteca completa</a>.</p>' : '') +
        '</section>' +

        '<section class="content-section" id="indicaciones">' +
          '<div class="section-heading"><h2>' + U.icon('check-circle', 24) + ' Para tener presente</h2></div>' +
          App.noteList([
            'Las condiciones históricas se mantienen visibles para dar contexto, aunque ya no requieran tratamiento activo.',
            'La alergia a penicilina debe declararse en cada atención, incluso en procedimientos menores.',
            'Lleva la ficha de emergencia impresa a controles y urgencias: resume lo crítico sin exponer todo el historial.'
          ]) +
          '<div class="callout callout--amarillo" style="margin-top:.8rem">' + U.icon('alert-triangle', 20) +
            '<div><strong>Contenido de demostración.</strong> Estos diagnósticos son ejemplos y no describen una situación clínica real. Reemplaza los datos antes de usar el sitio con información personal.</div>' +
          '</div>' +
        '</section>' +
      '</div>' +

      '<aside class="page-aside" aria-label="Información complementaria">' +
        '<div class="aside-card aside-card--key">' +
          '<div class="aside-card__head">' + U.icon('shield-heart', 18) + ' Datos clave</div>' +
          App.asideKey([
            ['Grupo sanguíneo', App.data.critico.grupoSanguineo],
            ['Alergia principal', critical.alergias[0] ? critical.alergias[0].sustancia : 'Sin registrar'],
            ['Condiciones activas', active.length + ' en seguimiento'],
            ['Última actualización', U.formatDate(cat.actualizado, 'medium')]
          ]) +
        '</div>' +
        sidebarDocs(docs, cat) +
        emergencyAside() +
        asideActions() +
        '<div class="aside-card">' +
          '<div class="aside-card__head">' + U.icon('link', 18) + ' Sigue revisando</div>' +
          '<div class="aside-links">' +
            '<a class="aside-link" href="#/categoria/medicamentos">Medicamentos y alergias ' + U.icon('chevron-right', 16) + '</a>' +
            '<a class="aside-link" href="#/categoria/laboratorio">Resultados de laboratorio ' + U.icon('chevron-right', 16) + '</a>' +
            '<a class="aside-link" href="#/categoria/cardiologia">Control cardiovascular ' + U.icon('chevron-right', 16) + '</a>' +
          '</div>' +
        '</div>' +
      '</aside>' +
    '</div>';

    function mount(root) {
      const search = root.querySelector('#condition-search');
      const chips = Array.from(root.querySelectorAll('[data-filter]'));
      const cards = Array.from(root.querySelectorAll('[data-condition-card]'));
      const empty = root.querySelector('#condition-empty');
      let filter = 'all';

      function apply() {
        const query = U.strip(search ? search.value : '').trim();
        let visible = 0;
        cards.forEach((card) => {
          const text = card.getAttribute('data-search') || '';
          const state = card.getAttribute('data-estado') || '';
          const status = card.getAttribute('data-status') || '';
          const statusMatch = filter === 'all'
            || (filter === 'activa' && status === 'activa')
            || (filter === 'historica' && status === 'historica')
            || (filter === 'seguimiento' && status === 'activa' && /seguimiento|tratamiento|evaluacion|progreso/.test(state));
          const show = (!query || text.indexOf(query) !== -1) && statusMatch;
          card.hidden = !show;
          if (show) visible += 1;
        });
        if (empty) empty.hidden = visible !== 0;
      }

      chips.forEach((chip) => {
        chip.addEventListener('click', function () {
          filter = chip.getAttribute('data-filter');
          chips.forEach((item) => item.setAttribute('aria-pressed', item === chip ? 'true' : 'false'));
          apply();
        });
      });
      if (search) search.addEventListener('input', apply);
      apply();
    }

    return { html, mount };
  }

  /* -------------------------- Medicamentos y alergias --------------------- */
  function renderMedicamentos(cat) {
    const data = App.data;
    const active = App.index.medsActive;
    const inactive = App.index.meds.filter((m) => !m.activo);
    const afeccion = App.index.afecciones[cat.afeccion_id];
    const docs = U.docsForCat(cat);
    const latest = active.reduce((max, m) => (m.inicio > max ? m.inicio : max), '');
    const primaryAllergy = App.index.alergias[0];

    function medCard(med) {
      return '<article class="med-card' + (med.activo ? '' : ' med-card--inactive') + '">' +
        '<div class="med-card__top">' +
          '<div class="med-card__identity"><span class="med-card__icon">' + U.icon('pill', 20) + '</span>' +
          '<div><h3>' + U.esc(med.nombre) + '</h3><span class="med-card__dose">' + U.esc(med.dosis) + ' · ' + U.esc(med.via) + '</span></div></div>' +
          App.statusBadge(med.activo ? 'Activo' : 'Suspendido', med.activo ? 'verde' : 'neutral', med.activo ? 'check-circle' : 'clock') +
        '</div>' +
        '<div class="med-card__rows">' +
          '<div class="med-card__row"><span>Frecuencia</span><strong>' + U.esc(med.frecuencia) + '</strong></div>' +
          '<div class="med-card__row"><span>Horario</span><strong>' + U.esc(med.horario) + '</strong></div>' +
          '<div class="med-card__row"><span>Indicación</span><strong>' + U.esc(med.indicacion) + '</strong></div>' +
          '<div class="med-card__row"><span>Límite</span><strong>' + U.esc(med.maximo) + '</strong></div>' +
          '<div class="med-card__row"><span>Desde</span><strong>' + U.esc(U.formatDate(med.inicio, 'medium')) + (med.fin ? ' · hasta ' + U.esc(U.formatDate(med.fin, 'medium')) : '') + '</strong></div>' +
        '</div>' +
        '<p class="med-card__note">' + U.esc(med.notas) + '</p>' +
      '</article>';
    }

    const html = App.pageHero(cat, {
      chips: [
        App.chip(active.length + ' medicamentos activos', 'coral', 'pill'),
        App.chip(App.index.alergias.length + ' alergias registradas', 'amarillo', 'alert-triangle'),
        App.chip('Revisado ' + U.formatDate(cat.actualizado, 'medium'), 'neutral', 'refresh')
      ]
    }) +
    App.sectionNav([
      { id: 'alergias', label: 'Alergias', icon: 'alert-triangle' },
      { id: 'medicamentos', label: 'Medicamentos', icon: 'pill' },
      { id: 'indicaciones', label: 'Indicaciones', icon: 'check-circle' },
      { id: 'documentos', label: 'Documentos', icon: 'folder' }
    ]) +
    '<div class="container page-layout">' +
      '<div class="page-main">' +
        '<section class="content-section" id="alergias">' +
          '<div class="section-heading"><h2>' + U.icon('alert-triangle', 24) + ' Alergias</h2><span class="section-heading__meta">Informar en cada atención</span></div>' +
          (primaryAllergy ? '<div class="alert-banner accent-coral">' +
            '<span class="alert-banner__icon">' + U.icon('alert-triangle', 22) + '</span>' +
            '<div><h3>Alergia a ' + U.esc(primaryAllergy.sustancia) + '</h3><p>' + U.esc(primaryAllergy.notas) + '</p></div>' +
            App.statusBadge(primaryAllergy.severidad, 'coral', 'alert-circle') +
          '</div>' : '') +
          '<div class="allergy-grid">' +
            App.index.alergias.map((allergy) => '<article class="allergy-card accent-' + U.toneOf(allergy.tono) + '">' +
              '<h3>' + U.esc(allergy.sustancia) + App.statusBadge(allergy.severidad, allergy.tono, 'alert-circle') + '</h3>' +
              '<p><strong>Reacción:</strong> ' + U.esc(allergy.reaccion) + '</p>' +
              '<small>Registrada el ' + U.esc(U.formatDate(allergy.fecha_registro)) + ' · ' + U.esc(allergy.notas) + '</small>' +
            '</article>').join('') +
          '</div>' +
        '</section>' +

        '<section class="content-section" id="medicamentos">' +
          '<div class="section-heading"><h2>' + U.icon('pill', 24) + ' Tratamiento vigente</h2><span class="section-heading__meta">' + active.length + ' activos · ' + inactive.length + ' suspendidos</span></div>' +
          '<div class="med-grid">' + active.map(medCard).join('') + '</div>' +
          (inactive.length ? '<h3 class="section-heading" style="margin-top:1.4rem"><span>' + U.icon('clock', 20) + ' Tratamientos anteriores</span></h3><div class="med-grid">' + inactive.map(medCard).join('') + '</div>' : '') +
        '</section>' +

        '<section class="content-section" id="indicaciones">' +
          '<div class="section-heading"><h2>' + U.icon('check-circle', 24) + ' Indicaciones de seguridad</h2></div>' +
          App.noteList(afeccion ? afeccion.notas : []) +
          '<div class="callout callout--turquesa" style="margin-top:.8rem">' + U.icon('info', 20) +
            '<div><strong>No suspendas un tratamiento por tu cuenta.</strong> Si aparece un efecto adverso, consulta con tu médico o llama al centro de salud antes de cambiar la dosis.</div>' +
          '</div>' +
        '</section>' +

        '<section class="content-section" id="documentos">' +
          '<div class="section-heading"><h2>' + U.icon('folder', 24) + ' Recetas y respaldos</h2><span class="section-heading__meta">' + docs.length + ' documentos</span></div>' +
          App.docStack(docs, 'No hay recetas descargables asociadas a este tratamiento.') +
        '</section>' +
      '</div>' +

      '<aside class="page-aside" aria-label="Información complementaria">' +
        '<div class="aside-card aside-card--key">' +
          '<div class="aside-card__head">' + U.icon('pill', 18) + ' Tratamiento</div>' +
          App.asideKey([
            ['Medicamentos activos', String(active.length)],
            ['Última revisión', U.formatDate(cat.actualizado, 'medium')],
            ['Alergia principal', primaryAllergy ? primaryAllergy.sustancia + ' · ' + primaryAllergy.severidad : 'Sin registrar'],
            ['Médica de cabecera', App.data.perfil.medicoCabecera]
          ]) +
        '</div>' +
        sidebarDocs(docs, cat) +
        emergencyAside() +
        asideActions() +
        '<div class="aside-card">' +
          '<div class="aside-card__head">' + U.icon('stethoscope', 18) + ' Contexto clínico</div>' +
          '<p class="tiny soft">' + U.esc(afeccion ? afeccion.resumen : '') + '</p>' +
          '<a class="aside-link" href="#/categoria/laboratorio">Ver laboratorio ' + U.icon('chevron-right', 16) + '</a>' +
        '</div>' +
      '</aside>' +
    '</div>';

    return { html };
  }

  /* ------------------------------- Laboratorio ---------------------------- */
  function renderLaboratorio(cat) {
    const data = App.data;
    const rows = App.index.labs;
    const abnormal = App.index.labsAbnormal;
    const normal = rows.length - abnormal.length;
    const docs = U.docsForCat(cat);
    const afeccion = App.index.afecciones[cat.afeccion_id];
    const latest = rows.reduce((max, row) => (row.fecha > max ? row.fecha : max), '');

    function labRow(row) {
      const tone = row.estado === 'normal' ? 'verde' : 'coral';
      const resultClass = row.estado === 'normal' ? '' : ' result--' + row.estado;
      const statusText = row.estado === 'normal' ? 'En rango' : row.estado === 'alto' ? 'Alto' : 'Bajo';
      return '<tr>' +
        '<td data-label="Examen">' + U.esc(row.examen) + '</td>' +
        '<td data-label="Resultado" class="result' + resultClass + '">' + U.esc(row.resultado) + ' <span class="tiny soft">' + U.esc(row.unidad) + '</span></td>' +
        '<td data-label="Referencia" class="ref">' + U.esc(row.referencia) + '</td>' +
        '<td data-label="Estado">' + App.statusBadge(statusText, tone, row.estado === 'normal' ? 'check-circle' : 'alert-circle') + '</td>' +
      '</tr>';
    }

    const html = App.pageHero(cat, {
      chips: [
        App.chip(rows.length + ' resultados', 'turquesa', 'flask'),
        App.chip(abnormal.length + ' fuera de rango', 'amarillo', 'alert-triangle'),
        App.chip(U.formatDate(latest, 'medium'), 'neutral', 'calendar')
      ],
      aside: '<span class="label">Último panel</span>' +
        '<strong class="value value--big">' + U.esc(U.formatDate(latest, 'medium')) + '</strong>' +
        '<hr class="divider">' +
        '<span class="label">Resultados</span><span class="value">' + normal + ' en rango · ' + abnormal.length + ' por revisar</span>' +
        '<a href="#/categoria/cardiologia">Revisar control cardiovascular</a>'
    }) +
    App.sectionNav([
      { id: 'resumen', label: 'Resumen', icon: 'compass' },
      { id: 'resultados', label: 'Resultados', icon: 'flask' },
      { id: 'documentos', label: 'Documentos', icon: 'folder' },
      { id: 'indicaciones', label: 'Indicaciones', icon: 'check-circle' }
    ]) +
    '<div class="container page-layout">' +
      '<div class="page-main">' +
        '<section class="content-section" id="resumen">' +
          '<div class="section-heading"><h2>' + U.icon('flask', 24) + ' Lectura rápida</h2><span class="section-heading__meta">Panel del ' + U.esc(U.formatDate(latest)) + '</span></div>' +
          '<div class="lab-summary">' +
            '<div class="stat-card"><span class="stat-card__num">' + rows.length + '</span><span class="stat-card__label">resultados revisados</span></div>' +
            '<div class="stat-card"><span class="stat-card__num">' + normal + '</span><span class="stat-card__label">dentro del rango</span></div>' +
            '<div class="stat-card"><span class="stat-card__num">' + abnormal.length + '</span><span class="stat-card__label">para conversar en control</span></div>' +
          '</div>' +
          '<div class="callout callout--turquesa">' + U.icon('info', 20) +
            '<div><strong>Un resultado no es un diagnóstico.</strong> Los valores se interpretan junto con tus síntomas, tu historia y controles previos. Los rangos pueden variar según el laboratorio.</div>' +
          '</div>' +
        '</section>' +

        '<section class="content-section" id="resultados">' +
          '<div class="section-heading"><h2>' + U.icon('flask', 24) + ' Resultados por panel</h2></div>' +
          App.index.panels.map((panel) => {
            const panelRows = rows.filter((row) => row.panel === panel);
            const panelAbnormal = panelRows.filter((row) => row.estado !== 'normal').length;
            return '<section class="lab-panel" aria-label="' + U.attr(panel) + '">' +
              '<div class="lab-panel__head"><h3>' + U.icon('droplet', 18) + U.esc(panel) + '</h3>' +
                (panelAbnormal ? App.statusBadge(panelAbnormal + ' por revisar', 'amarillo', 'alert-triangle') : App.statusBadge('Todo en rango', 'verde', 'check-circle')) +
              '</div>' +
              '<table class="lab-table">' +
                '<caption class="sr-only">Resultados de ' + U.esc(panel) + '</caption>' +
                '<thead><tr><th scope="col">Examen</th><th scope="col">Resultado</th><th scope="col">Referencia</th><th scope="col">Estado</th></tr></thead>' +
                '<tbody>' + panelRows.map(labRow).join('') + '</tbody>' +
              '</table>' +
            '</section>';
          }).join('') +
          '<p class="lab-note">' + U.icon('info', 15) + '<span>Los valores y rangos son de ejemplo. Reemplázalos por los informes reales antes de usar el sitio con datos personales.</span></p>' +
        '</section>' +

        '<section class="content-section" id="documentos">' +
          '<div class="section-heading"><h2>' + U.icon('folder', 24) + ' Informes de laboratorio</h2><span class="section-heading__meta">' + docs.length + ' archivos</span></div>' +
          App.docStack(docs, 'No hay informes descargables para este panel.') +
        '</section>' +

        '<section class="content-section" id="indicaciones">' +
          '<div class="section-heading"><h2>' + U.icon('check-circle', 24) + ' Qué hacer con estos resultados</h2></div>' +
          App.noteList(afeccion ? afeccion.notas : []) +
          '<div class="callout callout--amarillo" style="margin-top:.8rem">' + U.icon('calendar', 20) +
            '<div><strong>Próximo control sugerido:</strong> repetir el perfil lipídico y la vitamina D en seis meses, o antes si el médico lo indica.</div>' +
          '</div>' +
        '</section>' +
      '</div>' +

      '<aside class="page-aside" aria-label="Información complementaria">' +
        '<div class="aside-card aside-card--key">' +
          '<div class="aside-card__head">' + U.icon('flask', 18) + ' En números</div>' +
          App.asideKey([
            ['Resultados', String(rows.length)],
            ['En rango', String(normal)],
            ['Fuera de rango', String(abnormal.length)],
            ['LDL', '128 mg/dL · levemente alto'],
            ['Vitamina D', '24 ng/mL · baja']
          ]) +
        '</div>' +
        sidebarDocs(docs, cat) +
        '<div class="aside-card">' +
          '<div class="aside-card__head">' + U.icon('calendar', 18) + ' Preparar el control</div>' +
          '<div class="about-list" style="margin-top:0">' +
            '<li>' + U.icon('check', 15) + ' Llevar el informe completo, no solo la foto del resultado.</li>' +
            '<li>' + U.icon('check', 15) + ' Anotar medicamentos y suplementos que estés tomando.</li>' +
            '<li>' + U.icon('check', 15) + ' Preguntar qué valores cambian el plan y cada cuánto repetir.</li>' +
          '</div>' +
        '</div>' +
        emergencyAside() +
        asideActions() +
      '</aside>' +
    '</div>';

    return { html };
  }

  App.registerView('diagnosticos', renderDiagnosticos);
  App.registerView('medicamentos', renderMedicamentos);
  App.registerView('laboratorio', renderLaboratorio);
})();
