/* ============================================================================
   saludrcartes — Ficha pública de emergencia
   ----------------------------------------------------------------------------
   Esta página carga SOLO assets/js/data/emergencia.js. No importa el historial
   completo, no usa autenticación y está pensada para abrirse rápido.
   ========================================================================== */

(function () {
  'use strict';

  const CONFIG = window.SALUD_CONFIG;
  const ICONS = window.SaludIcons;
  const DATA = window.EMERGENCIA_DATA;
  const root = document.getElementById('ep-root');
  const mobileBar = document.getElementById('ep-mobile-bar');
  const demoBar = document.getElementById('ep-demo');

  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function icon(name, size) { return ICONS.icon(name, null, size || 18); }

  function telHref(phone) { return 'tel:' + String(phone || '').replace(/[^\d+]/g, ''); }

  function formatDate(iso) {
    if (!iso) return '';
    const date = new Date(iso + 'T12:00:00');
    if (isNaN(date.getTime())) return iso;
    return new Intl.DateTimeFormat(CONFIG.formatos.locale, { day: 'numeric', month: 'long', year: 'numeric' }).format(date);
  }

  function toast(message) {
    if (window.SaludToast) {
      window.SaludToast.show(message, 'success');
      return;
    }
    const region = document.getElementById('toast-region');
    if (!region) return;
    const item = document.createElement('div');
    item.className = 'toast toast--success';
    item.textContent = message;
    region.appendChild(item);
    window.setTimeout(function () { item.remove(); }, 3600);
  }

  function sharePage() {
    const payload = {
      title: 'Ficha de emergencia · saludrcartes',
      text: 'Información crítica de emergencia de ' + DATA.perfil.nombre,
      url: window.location.href
    };
    if (navigator.share) {
      navigator.share(payload).catch(function (error) {
        if (!error || error.name !== 'AbortError') copyLink(payload.url);
      });
      return;
    }
    copyLink(payload.url);
  }

  function copyLink(url) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(url).then(function () {
        toast('Enlace de la ficha copiado.');
      }).catch(function () { toast('No se pudo copiar el enlace.'); });
      return;
    }
    const area = document.createElement('textarea');
    area.value = url;
    area.setAttribute('readonly', '');
    area.className = 'sr-only';
    document.body.appendChild(area);
    area.select();
    try {
      document.execCommand('copy');
      toast('Enlace de la ficha copiado.');
    } catch (error) {
      toast('No se pudo copiar el enlace.');
    }
    document.body.removeChild(area);
  }

  function contactRow(contact) {
    return '<div class="ep-contact' + (contact.principal ? ' ep-contact--principal' : '') + '">' +
      '<span class="ep-contact__icon">' + icon(contact.principal ? 'users' : (contact.publico ? 'ambulance' : 'phone-call'), 20) + '</span>' +
      '<div><span class="ep-contact__name">' + esc(contact.nombre) + '</span>' +
      '<span class="ep-contact__relation">' + esc(contact.relacion) + (contact.principal ? ' · Llamar primero' : '') + '</span></div>' +
      '<div class="ep-contact__actions">' +
        '<a class="ep-contact__phone" href="' + esc(telHref(contact.telefono)) + '">' + esc(contact.telefono) + '</a>' +
        '<a class="btn btn--secondary btn--sm" href="' + esc(telHref(contact.telefono)) + '" aria-label="' + esc('Llamar a ' + contact.nombre) + '">' + icon('phone-call', 16) + ' Llamar</a>' +
      '</div>' +
    '</div>';
  }

  function render() {
    if (!DATA || !DATA.perfil) {
      root.innerHTML = '<div class="empty-state">' + icon('alert-triangle', 32) +
        '<h1>No se pudo cargar la ficha</h1><p>Revisa que <code>assets/js/data/emergencia.js</code> exista y esté bien formado.</p></div>';
      return;
    }

    const perfil = DATA.perfil;
    const critical = DATA.critico;
    const contacts = DATA.contactos || [];
    const primary = contacts.find(function (contact) { return contact.principal; }) || contacts[0];
    const samu = contacts.find(function (contact) { return contact.nombre === 'SAMU'; }) || { telefono: '131' };
    const demo = DATA.meta && DATA.meta.demo;

    document.title = 'Ficha de emergencia · ' + perfil.nombre;

    if (demoBar) demoBar.hidden = !demo;
    const updated = document.getElementById('ep-updated');
    if (updated && DATA.meta) updated.textContent = 'Actualizada el ' + formatDate(DATA.meta.actualizado);

    const allergies = critical.alergias.map(function (allergy) {
      return '<li>' + icon('alert-circle', 14) + '<span><strong>' + esc(allergy.sustancia) + '</strong> · ' + esc(allergy.severidad) + '<br>' + esc(allergy.reaccion) + '</span></li>';
    }).join('');

    const conditions = critical.condiciones.map(function (condition) {
      return '<li>' + icon('activity', 14) + '<span>' + esc(condition) + '</span></li>';
    }).join('');

    const meds = critical.medicamentos.map(function (med) {
      return '<li>' + icon('pill', 14) + '<span>' + esc(med) + '</span></li>';
    }).join('');

    root.innerHTML =
      '<div class="ep-intro">' +
        '<div>' +
          '<p class="ep-eyebrow">' + icon('heart-pulse', 16) + ' Ficha pública de emergencia</p>' +
          '<h1>Datos críticos de ' + esc(perfil.preferido || perfil.nombre) + '</h1>' +
          '<p>Muestra esta ficha al personal de salud. Contiene solo la información necesaria para actuar rápido; no incluye el historial completo.</p>' +
        '</div>' +
        '<span class="ep-badge">' + icon('shield-check', 15) + ' Información mínima y privada</span>' +
      '</div>' +

      '<div class="ep-print-only ep-print-warning">' + (demo ? 'DOCUMENTO DE EJEMPLO — SIN VALOR CLÍNICO' : 'Ficha de emergencia · ' + esc(perfil.nombre)) + '</div>' +

      '<section class="ep-critical" aria-label="Información crítica">' +
        '<div class="ep-blood"><span class="label">Grupo sanguíneo</span><strong>' + esc(perfil.grupoSanguineo) + '</strong><small>Confirmar con carné o examen antes de una transfusión.</small></div>' +
        '<div class="ep-critical__block"><h2>' + icon('alert-triangle', 17) + ' Alergias</h2><ul>' + (allergies || '<li>' + icon('check', 14) + '<span>Sin alergias registradas.</span></li>') + '</ul></div>' +
        '<div class="ep-critical__block"><h2>' + icon('clipboard-pulse', 17) + ' Condiciones</h2><ul>' + conditions + '</ul></div>' +
        '<div class="ep-critical__block"><h2>' + icon('pill', 17) + ' Medicamentos</h2><ul>' + meds + '</ul></div>' +
      '</section>' +

      '<div class="ep-columns">' +
        '<section class="ep-card" aria-labelledby="ep-contacts-title">' +
          '<h2 id="ep-contacts-title">' + icon('phone-call', 20) + ' Contactos directos</h2>' +
          '<div class="ep-contact-list">' + contacts.map(contactRow).join('') + '</div>' +
          '<p class="ep-footer">' + esc(perfil.nombre) + ' · Ficha actualizada el ' + esc(formatDate(DATA.meta.actualizado)) + '. ' +
            'Si esta ficha está desactualizada, prevalece siempre la indicación del personal de salud.</p>' +
        '</section>' +

        '<aside class="ep-side" aria-label="Recomendaciones">' +
          '<div class="ep-call">' +
            '<h2>¿Es una urgencia?</h2>' +
            '<p>Ambulancia y urgencias con riesgo vital en Chile.</p>' +
            '<a class="ep-call__phone" href="' + esc(telHref(samu.telefono)) + '">' + esc(samu.telefono) + '</a>' +
            '<a class="btn btn--primary" href="' + esc(telHref(samu.telefono)) + '">' + icon('phone-call', 18) + ' Llamar al SAMU</a>' +
          '</div>' +
          '<div class="ep-note">' +
            '<strong>Qué decir al llamar</strong>' +
            '<ul>' +
              '<li>' + icon('check', 14) + '<span>Nombre completo y edad.</span></li>' +
              '<li>' + icon('check', 14) + '<span>Qué pasó y desde cuándo.</span></li>' +
              '<li>' + icon('check', 14) + '<span>Alergia a penicilina y medicamentos activos.</span></li>' +
              '<li>' + icon('check', 14) + '<span>Dirección exacta y teléfono de contacto.</span></li>' +
            '</ul>' +
          '</div>' +
          '<div class="ep-note">' +
            '<strong>Privacidad</strong>' +
            '<p style="margin:.35rem 0 0">Esta ficha no muestra diagnósticos, documentos ni el resto del historial. Compártela solo con quien necesite actuar en una urgencia.</p>' +
          '</div>' +
        '</aside>' +
      '</div>' +

      '<div class="ep-actions">' +
        '<a class="btn btn--primary" href="assets/docs/emergencia-ficha-resumen.pdf" download="' + esc('emergencia-ficha-resumen.pdf') + '">' + icon('download', 18) + ' Descargar ficha PDF</a>' +
        '<button class="btn btn--secondary" type="button" id="ep-print-2">' + icon('printer', 18) + ' Imprimir esta ficha</button>' +
        '<button class="btn btn--secondary" type="button" id="ep-share">' + icon('share', 18) + ' Compartir enlace</button>' +
        '<a class="btn btn--ghost" href="index.html">' + icon('lock', 17) + ' Ir al registro privado</a>' +
      '</div>' +

      '<p class="ep-footer">' + icon('info', 13) + ' saludrcartes · Registro clínico personal. ' +
        (demo ? 'Contenido de demostración sin valor clínico. ' : '') +
        'En caso de emergencia, llama al 131.</p>';

    if (mobileBar && primary) {
      mobileBar.innerHTML =
        '<div class="ep-mobile-bar">' +
          '<a class="btn btn--primary" href="' + esc(telHref(samu.telefono)) + '">' + icon('ambulance', 17) + ' SAMU ' + esc(samu.telefono) + '</a>' +
          '<a class="btn btn--secondary" href="' + esc(telHref(primary.telefono)) + '">' + icon('phone-call', 17) + ' Contacto</a>' +
        '</div>';
    }

    const print = document.getElementById('ep-print');
    if (print) print.addEventListener('click', function () { window.print(); });
    const print2 = document.getElementById('ep-print-2');
    if (print2) print2.addEventListener('click', function () { window.print(); });
    const share = document.getElementById('ep-share');
    if (share) share.addEventListener('click', sharePage);

    ICONS.hydrate(document);
  }

  function boot() {
    ICONS.hydrate(document);
    render();
    const year = document.getElementById('footer-year');
    if (year) year.textContent = String(new Date().getFullYear());
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
