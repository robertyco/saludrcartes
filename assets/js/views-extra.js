/* ============================================================================
   saludrcartes — Biblioteca de documentos y página “Acerca de”
   ========================================================================== */

(function () {
  'use strict';

  const App = window.SaludApp;
  if (!App) return;

  const U = App.util;
  const CONFIG = window.SALUD_CONFIG;

  /* --------------------------- Documentos --------------------------------- */
  function renderDocumentos(route) {
    const docs = App.index.docs;
    const withDocs = App.index.categorias.filter((cat) => (App.index.docsByCat[cat.id] || []).length);
    const requested = route && route.query ? route.query.get('cat') : '';
    const initial = withDocs.some((cat) => cat.slug === requested) ? requested : 'all';
    const latest = docs[0] ? docs[0].fecha : '';

    const chips = ['<button class="filter-chip" type="button" data-doc-filter="all" aria-pressed="' + (initial === 'all' ? 'true' : 'false') + '">Todos · ' + docs.length + '</button>']
      .concat(withDocs.map((cat) => {
        const count = (App.index.docsByCat[cat.id] || []).length;
        return '<button class="filter-chip" type="button" data-doc-filter="' + U.attr(cat.slug) + '" aria-pressed="' + (initial === cat.slug ? 'true' : 'false') + '">' + U.esc(cat.nombre) + ' · ' + count + '</button>';
      })).join('');

    const html = App.simpleHero({
      title: 'Biblioteca de documentos',
      lead: 'Informes, recetas, imágenes y exámenes en un solo lugar. Cada archivo conserva su fecha, su contexto clínico y una vista previa antes de descargarlo.',
      icon: 'folder',
      accent: 'turquesa',
      chips: [
        App.chip(docs.length + ' documentos', 'turquesa', 'folder'),
        App.chip('PDF descargable', 'neutral', 'download'),
        App.chip('Última carga ' + U.formatDate(latest, 'medium'), 'neutral', 'calendar')
      ],
      aside: '<span class="label">Archivo personal</span>' +
        '<strong class="value value--big">' + docs.length + ' documentos</strong>' +
        '<hr class="divider">' +
        '<span class="label">Categorías con archivos</span><span class="value">' + withDocs.length + ' de ' + App.index.categorias.length + '</span>' +
        '<a href="#/categoria/diagnosticos">Volver a diagnósticos</a>'
    }) +
    '<section class="section section--tight">' +
      '<div class="container">' +
        '<div class="library-toolbar">' +
          '<div class="search-field">' + U.icon('search', 19) +
            '<label class="sr-only" for="library-search">Buscar documentos</label>' +
            '<input class="input" id="library-search" type="search" placeholder="Buscar por nombre, fecha o especialidad…" autocomplete="off">' +
          '</div>' +
          '<div class="filter-group" role="group" aria-label="Filtrar documentos">' + chips + '</div>' +
          '<span class="library-count" id="library-count">' + docs.length + ' de ' + docs.length + ' documentos</span>' +
        '</div>' +
        '<div class="library-grid" id="library-grid">' +
          docs.map((doc) => App.docCard(doc, { showCategory: true })).join('') +
        '</div>' +
        '<div class="empty-state" id="library-empty" hidden>' + U.icon('search', 30) + '<h3>Sin documentos para este filtro</h3><p>Prueba con otra palabra o vuelve a “Todos”.</p></div>' +
        '<div class="callout callout--amarillo" style="margin-top:1rem">' + U.icon('info', 20) +
          '<div><strong>Documentos de ejemplo.</strong> Los PDF incluidos están marcados como demostración y no tienen valor clínico. Reemplázalos por tus informes reales y considera almacenarlos de forma privada en Supabase Storage.</div>' +
        '</div>' +
      '</div>' +
    '</section>';

    function mount(root) {
      const search = root.querySelector('#library-search');
      const countEl = root.querySelector('#library-count');
      const empty = root.querySelector('#library-empty');
      const cards = Array.from(root.querySelectorAll('[data-doc-card]'));
      const filterChips = Array.from(root.querySelectorAll('[data-doc-filter]'));
      let filter = initial;

      function apply() {
        const query = U.strip(search ? search.value : '').trim();
        let visible = 0;
        cards.forEach((card) => {
          const cat = card.getAttribute('data-cat') || '';
          const text = card.getAttribute('data-search') || '';
          const show = (filter === 'all' || cat === filter) && (!query || text.indexOf(query) !== -1);
          card.hidden = !show;
          if (show) visible += 1;
        });
        if (countEl) countEl.textContent = visible + ' de ' + cards.length + ' documentos';
        if (empty) empty.hidden = visible !== 0;
      }

      filterChips.forEach((chip) => {
        chip.addEventListener('click', function () {
          filter = chip.getAttribute('data-doc-filter');
          filterChips.forEach((item) => item.setAttribute('aria-pressed', item === chip ? 'true' : 'false'));
          apply();
          if (window.history.replaceState) {
            window.history.replaceState(null, '', filter === 'all' ? '#/documentos' : '#/documentos?cat=' + filter);
          }
        });
      });
      if (search) search.addEventListener('input', apply);
      apply();
    }

    return { html, mount };
  }

  /* ------------------------------- Acerca --------------------------------- */
  function renderAcerca() {
    const data = App.data;
    const demo = data.meta.demo || CONFIG.demo;

    const html = App.simpleHero({
      title: 'Acerca y privacidad',
      lead: 'saludrcartes es un registro clínico personal: una forma más clara de guardar diagnósticos, tratamiento, exámenes y documentos, con una ficha de emergencia separada y sin exponer el historial completo.',
      icon: 'shield-heart',
      accent: 'violeta',
      chips: [
        App.chip('Versión ' + CONFIG.version, 'neutral', 'sparkle'),
        App.chip('Accesible AA', 'verde', 'accessibility'),
        App.chip(demo ? 'Modo demostración' : 'Datos personales', demo ? 'amarillo' : 'verde', demo ? 'info' : 'shield-check')
      ],
      aside: '<span class="label">Titular</span>' +
        '<strong class="value value--big">' + U.esc(data.perfil.nombre) + '</strong>' +
        '<hr class="divider">' +
        '<span class="label">Última actualización</span><span class="value">' + U.esc(U.formatDate(data.meta.actualizado)) + '</span>' +
        '<a href="#/documentos">Ver documentos</a>'
    }) +
    '<section class="section section--tight">' +
      '<div class="container">' +
        '<div class="about-grid">' +
          '<article class="about-card">' +
            '<span class="about-icon">' + U.icon('compass', 22) + '</span>' +
            '<h3>Qué es este sitio</h3>' +
            '<p>Un registro personal que ordena la información clínica en tres capas: lo esencial, las especialidades y la emergencia. La idea es que cualquier lectura —tuya, de tu familia o de un profesional— encuentre rápido lo que necesita.</p>' +
            '<ul class="about-list">' +
              '<li>' + U.icon('check', 15) + ' 12 secciones clínicas agrupadas en 3 categorías.</li>' +
              '<li>' + U.icon('check', 15) + ' Línea de evolución, documentos y notas por especialidad.</li>' +
              '<li>' + U.icon('check', 15) + ' Ficha de emergencia independiente e imprimible.</li>' +
            '</ul>' +
          '</article>' +

          '<article class="about-card about-card--green">' +
            '<span class="about-icon">' + U.icon('lock', 22) + '</span>' +
            '<h3>Privacidad por diseño</h3>' +
            '<p>El historial completo no está pensado para publicarse. La versión de producción debe protegerlo con autenticación real, reglas por fila y almacenamiento privado.</p>' +
            '<ul class="about-list">' +
              '<li>' + U.icon('check', 15) + ' Sin indexación: <code>robots.txt</code> y <code>noindex</code>.</li>' +
              '<li>' + U.icon('check', 15) + ' Ficha pública con datos mínimos, separada del historial.</li>' +
              '<li>' + U.icon('check', 15) + ' Sesión local en la demo; Supabase Auth + RLS en producción.</li>' +
              '<li>' + U.icon('check', 15) + ' URLs firmadas y bucket privado para documentos.</li>' +
            '</ul>' +
          '</article>' +

          '<article class="about-card">' +
            '<span class="about-icon">' + U.icon('accessibility', 22) + '</span>' +
            '<h3>Accesibilidad</h3>' +
            '<p>El sitio sigue criterios WCAG 2.1 AA en lo posible: navegación por teclado, foco visible, contraste, texto ampliable y objetivos táctiles de al menos 44 × 44 px.</p>' +
            '<ul class="about-list">' +
              '<li>' + U.icon('check', 15) + ' Preferencias de lectura persistentes en el dispositivo.</li>' +
              '<li>' + U.icon('check', 15) + ' Alto contraste y reducción de movimiento.</li>' +
              '<li>' + U.icon('check', 15) + ' Estructura semántica, saltar al contenido y textos alternativos.</li>' +
            '</ul>' +
          '</article>' +

          '<article class="about-card">' +
            '<span class="about-icon">' + U.icon('link', 22) + '</span>' +
            '<h3>Cómo está construido</h3>' +
            '<p>Una base liviana, sin dependencias de terceros ni rastreo. Los datos clínicos viven separados de la interfaz para poder migrarlos a Supabase sin rehacer las páginas.</p>' +
            '<div class="chip-row" style="margin-top:.8rem">' +
              App.chip('HTML5', 'neutral', 'file-text') +
              App.chip('CSS', 'turquesa', 'sparkle') +
              App.chip('JavaScript', 'amarillo', 'activity') +
              App.chip('Netlify', 'verde', 'compass') +
              App.chip('Supabase', 'violeta', 'shield-check') +
            '</div>' +
            '<ul class="about-list">' +
              '<li>' + U.icon('check', 15) + ' Fuentes Quicksand e Inter autoalojadas.</li>' +
              '<li>' + U.icon('check', 15) + ' Iconos SVG propios, sin librerías externas.</li>' +
              '<li>' + U.icon('check', 15) + ' Funciones serverless preparadas para URLs firmadas.</li>' +
            '</ul>' +
          '</article>' +
        '</div>' +

        '<div class="about-grid" style="margin-top:1rem">' +
          '<article class="about-card">' +
            '<span class="about-icon">' + U.icon('info', 22) + '</span>' +
            '<h3>Contenido de demostración</h3>' +
            '<p>Todo el contenido clínico de esta copia es ficticio y está marcado como ejemplo. Sirve para revisar el diseño, la navegación y los estados de cada página antes de cargar información real.</p>' +
            (demo ? '<div class="callout callout--amarillo" style="margin-top:.8rem">' + U.icon('alert-triangle', 20) +
              '<div><strong>Credenciales de la demo:</strong> <code>roberto@saludrcartes.cl</code> · <code>saludrcartes</code><br>No uses este acceso para datos personales.</div></div>' : '') +
            '<ul class="about-list">' +
              '<li>' + U.icon('check', 15) + ' Reemplaza <code>assets/js/data/clinica.js</code> por tus datos.</li>' +
              '<li>' + U.icon('check', 15) + ' Genera tus PDF y actualiza las rutas en <code>documentos</code>.</li>' +
              '<li>' + U.icon('check', 15) + ' Cambia <code>meta.demo</code> a <code>false</code> y desactiva <code>CONFIG.demo</code>.</li>' +
            '</ul>' +
          '</article>' +

          '<article class="about-card">' +
            '<span class="about-icon">' + U.icon('phone-call', 22) + '</span>' +
            '<h3>Emergencia separada</h3>' +
            '<p>La ficha pública vive en <code>emergencia.html</code> y carga un archivo de datos mínimo. No incluye diagnósticos, documentos ni el historial completo: solo grupo sanguíneo, alergias, condiciones, medicamentos esenciales y contactos.</p>' +
            '<ul class="about-list">' +
              '<li>' + U.icon('check', 15) + ' Se puede imprimir y llevar en la billetera.</li>' +
              '<li>' + U.icon('check', 15) + ' Los teléfonos usan enlaces <code>tel:</code>.</li>' +
              '<li>' + U.icon('check', 15) + ' No requiere iniciar sesión, por diseño.</li>' +
            '</ul>' +
            '<a class="btn btn--secondary btn--sm" style="margin-top:.8rem" href="' + U.attr(CONFIG.rutas.emergenciaPublica) + '" target="_blank" rel="noopener">' + U.icon('external-link', 16) + ' Abrir ficha pública</a>' +
          '</article>' +
        '</div>' +

        '<article class="about-card" style="margin-top:1rem">' +
          '<span class="about-icon">' + U.icon('shield-check', 22) + '</span>' +
          '<h3>Antes de publicar con datos reales</h3>' +
          '<div class="about-list" style="margin-top:.6rem">' +
            '<li>' + U.icon('check', 15) + ' Conectar Supabase Auth y activar RLS en todas las tablas clínicas.</li>' +
            '<li>' + U.icon('check', 15) + ' Mover los PDF a un bucket privado y servirlos con URLs firmadas de corta duración.</li>' +
            '<li>' + U.icon('check', 15) + ' Revisar <code>_headers</code>, CSP y las variables de entorno de Netlify.</li>' +
            '<li>' + U.icon('check', 15) + ' Probar la ficha de emergencia impresa y los enlaces <code>tel:</code> en un teléfono real.</li>' +
            '<li>' + U.icon('check', 15) + ' Confirmar que <code>robots.txt</code> y <code>noindex</code> sigan activos.</li>' +
          '</div>' +
          '<div class="callout callout--coral" style="margin-top:.9rem">' + U.icon('alert-triangle', 20) +
            '<div><strong>Importante:</strong> un sitio estático con datos reales en el JavaScript no es privado, aunque tenga una pantalla de login. La protección real requiere que los datos vivan en un backend con permisos.</div>' +
          '</div>' +
        '</article>' +
      '</div>' +
    '</section>';

    return { html };
  }

  App.registerView('documentos', renderDocumentos);
  App.registerView('acerca', renderAcerca);
})();
