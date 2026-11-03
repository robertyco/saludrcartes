/* ============================================================================
   saludrcartes — Sistema de iconos (SVG, sin dependencias)
   Trazo de 1.8 px, extremos redondeados, 24 × 24.
   ========================================================================== */

(function () {
  'use strict';

  var P = {
    'clipboard-pulse': '<path d="M9 4h6v3H9z"/><path d="M9 4H7a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2"/><path d="M7.5 14h2l1-2.5 2 5 1-2.5h3"/>',
    'pill': '<path d="M10.5 20.5a5 5 0 0 1-7-7l6-6a5 5 0 0 1 7 7z"/><path d="M8.5 8.5l7 7"/>',
    'flask': '<path d="M9 3h6"/><path d="M10 3v6L5.5 17a2 2 0 0 0 1.7 3h9.6a2 2 0 0 0 1.7-3L14 9V3"/><path d="M7.5 15h9"/>',
    'brain': '<path d="M9.5 4.5A3 3 0 0 0 7 7.5a3.2 3.2 0 0 0-1.5 5.8A3 3 0 0 0 8 18.5a3 3 0 0 0 4 1.5V4.5a3 3 0 0 0-2.5 0z"/><path d="M14.5 4.5A3 3 0 0 1 17 7.5a3.2 3.2 0 0 1 1.5 5.8 3 3 0 0 1-2.5 5.2 3 3 0 0 1-4 1.5V4.5a3 3 0 0 1 2.5 0z"/><path d="M12 8.5h2M10 12h2"/>',
    'heart-pulse': '<path d="M20.8 5.6a5.5 5.5 0 0 0-7.8 0L12 6.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 22l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/><path d="M3.5 12h4l1.5-3 3 6 2-4h6.5"/>',
    'heart': '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1.1L12 21l7.8-7.5 1-1.1a5.5 5.5 0 0 0 0-7.8z"/>',
    'activity': '<path d="M3 12h4l2.5-7 5 14L17 12h4"/>',
    'dumbbell': '<path d="M6.5 6.5v11M17.5 6.5v11"/><path d="M3.5 9v6M20.5 9v6"/><path d="M6.5 12h11"/>',
    'message-wave': '<path d="M21 11.5a8.5 8.5 0 0 1-12.3 7.6L3 21l1.9-5.7A8.5 8.5 0 1 1 21 11.5z"/><path d="M8 10.5v2M12 8.5v6M16 10.5v2"/>',
    'mind': '<path d="M12 21a9 9 0 1 0-9-9"/><path d="M12 16a4 4 0 1 0-4-4"/><path d="M12 12h.01"/><path d="M12 21v-5"/><path d="M12 3v3"/>',
    'hand': '<path d="M18 11V6a2 2 0 0 0-4 0v5"/><path d="M14 10V4a2 2 0 0 0-4 0v6"/><path d="M10 10V5a2 2 0 0 0-4 0v9"/><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2a8 8 0 0 1-8-8v-1a2 2 0 1 1 4 0"/>',
    'footprints': '<path d="M4 16v-2.4A3.6 3.6 0 0 1 7.6 10h.8A3.6 3.6 0 0 1 12 13.6V16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><path d="M4 16h8"/><path d="M14 8V5.4A3.4 3.4 0 0 1 17.4 2h.2A3.4 3.4 0 0 1 21 5.4V8a2 2 0 0 1-2 2h-3a2 2 0 0 1-2-2z"/><path d="M14 8h7"/>',
    'phone-call': '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7a2 2 0 0 1 1.7 2z"/><path d="M15 3a6 6 0 0 1 6 6M15 7a2 2 0 0 1 2 2"/>',
    'phone': '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7a2 2 0 0 1 1.7 2z"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    'shield': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    'shield-heart': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 15.5s-3.2-1.8-3.2-4a1.9 1.9 0 0 1 3.2-1.3 1.9 1.9 0 0 1 3.2 1.3c0 2.2-3.2 4-3.2 4z"/>',
    'shield-check': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m8.5 11.5 2.5 2.5 4.5-5"/>',
    'lock': '<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/><path d="M12 15v2"/>',
    'printer': '<path d="M6 9V3h12v6"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8" rx="1"/>',
    'share': '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 10.6 6.8-4.2M8.6 13.4l6.8 4.2"/>',
    'arrow-right': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'arrow-up-right': '<path d="M7 17 17 7M8 7h9v9"/>',
    'arrow-left': '<path d="M19 12H5M11 18l-6-6 6-6"/>',
    'chevron-down': '<path d="m6 9 6 6 6-6"/>',
    'chevron-right': '<path d="m9 18 6-6-6-6"/>',
    'close': '<path d="M18 6 6 18M6 6l12 12"/>',
    'menu': '<path d="M4 6h16M4 12h16M4 18h16"/>',
    'check': '<path d="m4 12 5 5L20 6"/>',
    'check-circle': '<circle cx="12" cy="12" r="9"/><path d="m8 12 2.5 2.5L16 9"/>',
    'alert-triangle': '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
    'alert-circle': '<circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16h.01"/>',
    'info': '<circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/>',
    'type': '<path d="M4 7V4h16v3M9 20h6M12 4v16"/>',
    'contrast': '<circle cx="12" cy="12" r="9"/><path d="M12 3v18A9 9 0 0 0 12 3z" fill="currentColor" stroke="none"/>',
    'motion': '<path d="M3 8h10a3 3 0 1 0-3-3M3 12h14a3 3 0 1 1-3 3M3 16h7a3 3 0 1 1-3 3"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    'users': '<circle cx="9" cy="8" r="4"/><path d="M2 21a7 7 0 0 1 14 0"/><path d="M17 4a4 4 0 0 1 0 8M22 21a7 7 0 0 0-4-6.3"/>',
    'logout': '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5M21 12H9"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    'calendar': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18"/>',
    'file-text': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h6"/>',
    'file-heart': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M12 17.5s-3-1.6-3-3.6a1.8 1.8 0 0 1 3-1.2 1.8 1.8 0 0 1 3 1.2c0 2-3 3.6-3 3.6z"/>',
    'download': '<path d="M12 3v12M7 10l5 5 5-5"/><path d="M4 19h16"/>',
    'eye': '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    'eye-off': '<path d="M3 3l18 18"/><path d="M10.6 5.1A10.5 10.5 0 0 1 12 5c6.5 0 10 7 10 7a17.8 17.8 0 0 1-3.2 4.1M6.6 6.6C3.6 8.5 2 12 2 12s3.5 7 10 7a10 10 0 0 0 4.4-1"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/>',
    'external-link': '<path d="M15 3h6v6M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    'copy': '<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
    'hospital': '<path d="M3 21h18M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16"/><path d="M9 7h6M12 4v6M9 13h6M9 17h6"/>',
    'ambulance': '<path d="M3 17V7a1 1 0 0 1 1-1h11v11"/><path d="M15 9h3.5L22 13v4h-7"/><circle cx="7" cy="18" r="2"/><circle cx="18" cy="18" r="2"/><path d="M7 10h4M9 8v4"/>',
    'flame': '<path d="M12 22c4 0 7-3 7-7 0-3-2-5-4-8-1 3-3 4-3 4s0-3-2-5c-1 2-5 5-5 9 0 4 3 7 7 7z"/><path d="M12 22c2 0 3.5-1.5 3.5-3.5 0-1.5-1-2.5-1.5-4-.8 1.5-2 2-2 2s0-1.5-1-2.5c-.5 1-2.5 2.5-2.5 4.5S10 22 12 22z"/>',
    'stethoscope': '<path d="M6 3v6a5 5 0 0 0 10 0V3"/><path d="M6 3H4M16 3h2"/><path d="M11 14v1a5 5 0 0 0 10 0v-2"/><circle cx="21" cy="11" r="2"/>',
    'compass': '<circle cx="12" cy="12" r="9"/><path d="m16 8-2.5 5.5L8 16l2.5-5.5z"/>',
    'link': '<path d="M10 13a5 5 0 0 0 7.5.5l2-2a5 5 0 0 0-7-7l-1.2 1.2"/><path d="M14 11a5 5 0 0 0-7.5-.5l-2 2a5 5 0 0 0 7 7l1.2-1.2"/>',
    'sparkle': '<path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="m19 16 .8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z"/>',
    'home': '<path d="m3 10 9-7 9 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    'book': '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    'list': '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    'filter': '<path d="M3 5h18l-7 8v6l-4 2v-8z"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    'droplet': '<path d="M12 2.7 6.5 8.2a7.5 7.5 0 1 0 11 0z"/>',
    'pulse': '<path d="M2 12h4l2.5-7 5 14L17 12h5"/>',
    'refresh': '<path d="M21 12a9 9 0 1 1-2.6-6.4"/><path d="M21 3v6h-6"/>',
    'folder': '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    'accessibility': '<circle cx="12" cy="4" r="2"/><path d="M4 8h16M12 8v6M12 14l-3 7M12 14l3 7"/>',
    'x-circle': '<circle cx="12" cy="12" r="9"/><path d="m9 9 6 6M15 9l-6 6"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'minus': '<path d="M5 12h14"/>',
    'arrow-down': '<path d="M12 5v14M6 13l6 6 6-6"/>',
    'quote': '<path d="M9 11H5a1 1 0 0 1-1-1V6a3 3 0 0 1 3-3M20 11h-4a1 1 0 0 1-1-1V6a3 3 0 0 1 3-3"/>',
    'clock-check': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/><path d="m16 3 2 2 3-3"/>'
  };

  function icon(name, className, size) {
    var inner = P[name] || P['info'];
    var cls = className ? ' class="' + className + '"' : '';
    var s = size || 24;
    return '<svg' + cls + ' width="' + s + '" height="' + s + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' + inner + '</svg>';
  }

  function brandMark(size, className) {
    var cls = className ? ' class="' + className + '"' : '';
    var s = size || 36;
    return '<svg' + cls + ' width="' + s + '" height="' + s + '" viewBox="0 0 48 48" fill="none" aria-hidden="true" focusable="false">'
      + '<rect x="2" y="2" width="44" height="44" rx="15" fill="#0B7A57"/>'
      + '<path d="M24 38s-11-6.4-11-14.2A6.6 6.6 0 0 1 24 19a6.6 6.6 0 0 1 11 4.8C35 31.6 24 38 24 38z" fill="#FFF8F0"/>'
      + '<path d="M15.5 26.5h5l1.8-3.6 3.4 7.2 1.8-3.6h5" stroke="#0E9F6E" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
      + '<circle cx="36.5" cy="11.5" r="4.5" fill="#FF6B6B"/>'
      + '</svg>';
  }

  function hydrate(root) {
    var scope = root || document;
    scope.querySelectorAll('[data-brand-mark]').forEach(function (el) {
      if (el.querySelector('svg')) return;
      var size = parseInt(el.getAttribute('data-brand-mark'), 10) || 36;
      el.innerHTML = brandMark(size);
    });
    scope.querySelectorAll('[data-icon]').forEach(function (el) {
      if (el.querySelector('svg')) return;
      var name = el.getAttribute('data-icon');
      var size = parseInt(el.getAttribute('data-icon-size'), 10) || 20;
      el.innerHTML = icon(name, null, size);
      el.classList.add('icon-ready');
    });
    return scope;
  }

  window.SaludIcons = { icon: icon, brandMark: brandMark, hydrate: hydrate, paths: P };
})();
