/* ==========================================================================
   saludrcartes · interacciones
   ========================================================================== */
(function () {
  "use strict";

  var doc = document;
  var body = doc.body;
  var root = doc.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia("(pointer: fine)").matches;
  var lastFocus = null;
  var activeSheet = null;
  var docModal = null;
  var searchInput = null;
  var searchIndex = [];

  function $(selector, context) {
    return (context || doc).querySelector(selector);
  }
  function $$(selector, context) {
    return Array.prototype.slice.call((context || doc).querySelectorAll(selector));
  }
  function on(element, event, handler, options) {
    if (element) element.addEventListener(event, handler, options);
  }
  function storage(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      localStorage.setItem(key, value);
    } catch (error) {
      return null;
    }
    return value;
  }
  function normalize(value) {
    return (value || "")
      .toString()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  /* ---------- generic dialogs ------------------------------------------- */
  function focusable(container) {
    return $$(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), iframe, [tabindex]:not([tabindex="-1"])',
      container
    ).filter(function (element) {
      return element.offsetParent !== null || element === doc.activeElement;
    });
  }

  function trapFocus(event) {
    if (event.key !== "Tab") return;
    var container = docModal && docModal.classList.contains("is-open") ? docModal : activeSheet;
    if (!container) return;
    var items = focusable(container);
    if (!items.length) return;
    var first = items[0];
    var last = items[items.length - 1];
    if (event.shiftKey && doc.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && doc.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  function openSheet(name, focusSelector) {
    var sheet = $('[data-sheet="' + name + '"]');
    if (!sheet) return;
    if (activeSheet && activeSheet !== sheet) closeSheet(true);
    lastFocus = doc.activeElement;
    activeSheet = sheet;
    sheet.inert = false;
    sheet.classList.add("is-open");
    sheet.setAttribute("aria-hidden", "false");
    body.classList.add("is-locked");
    window.setTimeout(function () {
      var target = focusSelector ? $(focusSelector, sheet) : focusable(sheet)[0];
      if (target) target.focus({ preventScroll: true });
      else sheet.focus({ preventScroll: true });
    }, 80);
  }

  function closeSheet(skipFocus) {
    if (!activeSheet) return;
    var sheet = activeSheet;
    sheet.classList.remove("is-open");
    sheet.setAttribute("aria-hidden", "true");
    sheet.inert = true;
    activeSheet = null;
    if (!docModal || !docModal.classList.contains("is-open")) body.classList.remove("is-locked");
    if (!skipFocus && lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  }

  function openDocModal(button) {
    if (!docModal) return;
    var src = button.getAttribute("data-preview");
    var title = button.getAttribute("data-title") || "Documento clínico";
    var download = button.getAttribute("data-download") || src;
    var meta = button.getAttribute("data-meta") || "PDF";
    var frame = $(".doc-modal iframe", docModal);
    var heading = $(".doc-modal__title-text", docModal);
    var sub = $(".doc-modal__sub", docModal);
    var link = $(".doc-modal__download", docModal);
    heading.textContent = title;
    sub.textContent = meta;
    link.href = download;
    link.setAttribute("download", "");
    frame.src = src;
    lastFocus = button;
    docModal.classList.add("is-open");
    docModal.setAttribute("aria-hidden", "false");
    docModal.inert = false;
    body.classList.add("is-locked");
    window.setTimeout(function () {
      var close = $(".doc-modal__close", docModal);
      if (close) close.focus({ preventScroll: true });
    }, 60);
  }

  function closeDocModal() {
    if (!docModal || !docModal.classList.contains("is-open")) return;
    docModal.classList.remove("is-open");
    docModal.setAttribute("aria-hidden", "true");
    body.classList.remove("is-locked");
    var frame = $("iframe", docModal);
    window.setTimeout(function () {
      if (frame) frame.src = "about:blank";
      docModal.inert = true;
    }, 250);
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  }

  /* ---------- theme preferences ----------------------------------------- */
  function currentSize() {
    return root.getAttribute("data-size") || "md";
  }

  function syncPreferences() {
    var size = currentSize();
    $$("[data-text-size]").forEach(function (button) {
      button.setAttribute("aria-pressed", button.getAttribute("data-text-size") === size ? "true" : "false");
    });
    var contrast = root.getAttribute("data-contrast") === "high";
    $$("[data-toggle-contrast]").forEach(function (button) {
      button.setAttribute("aria-checked", contrast ? "true" : "false");
    });
    var motion = root.getAttribute("data-motion") === "reduce";
    $$("[data-toggle-motion]").forEach(function (button) {
      button.setAttribute("aria-checked", motion ? "true" : "false");
    });
  }

  function setTextSize(size) {
    if (size === "md") root.removeAttribute("data-size");
    else root.setAttribute("data-size", size);
    storage("src-text-size", size);
    syncPreferences();
  }

  function toggleContrast() {
    var next = root.getAttribute("data-contrast") === "high" ? "false" : "true";
    if (next === "true") root.setAttribute("data-contrast", "high");
    else root.removeAttribute("data-contrast");
    storage("src-contrast", next === "true" ? "high" : "normal");
    syncPreferences();
  }

  function toggleMotion() {
    var next = root.getAttribute("data-motion") === "reduce" ? "false" : "true";
    if (next === "true") root.setAttribute("data-motion", "reduce");
    else root.removeAttribute("data-motion");
    storage("src-motion", next === "true" ? "reduce" : "normal");
    syncPreferences();
  }

  /* ---------- search ----------------------------------------------------- */
  function renderSearch(query) {
    var results = $("[data-search-results]");
    if (!results) return;
    var term = normalize(query).trim();
    var matches = searchIndex.filter(function (item) {
      if (!term) return item.featured;
      var haystack = normalize([item.title, item.group, item.description, item.keywords].join(" "));
      return haystack.indexOf(term) !== -1;
    }).slice(0, 18);

    if (!matches.length) {
      results.innerHTML =
        '<p class="search-empty">No encontramos una página con “' +
        escapeHtml(query) +
        '”. Prueba con <strong>medicamentos</strong>, <strong>dolor</strong> o <strong>corazón</strong>.</p>';
      return;
    }

    results.innerHTML = matches
      .map(function (item) {
        return (
          '<a class="search-result" href="' +
          item.url +
          '">' +
          '<span class="search-result__num">' +
          (item.number || "·") +
          "</span>" +
          "<span>" +
          '<span class="search-result__title">' +
          escapeHtml(item.title) +
          "</span>" +
          '<span class="search-result__meta">' +
          escapeHtml(item.group) +
          " · " +
          escapeHtml(item.description) +
          "</span>" +
          "</span>" +
          '<svg class="icon" aria-hidden="true"><use href="#i-arrow-right"></use></svg>' +
          "</a>"
        );
      })
      .join("");
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function openSearch() {
    openSheet("search", "[data-search-input]");
    if (searchInput) {
      searchInput.value = "";
      renderSearch("");
    }
  }

  /* ---------- filter rows ------------------------------------------------ */
  function initFilters() {
    var buttons = $$("[data-filter]");
    var rows = $$("[data-states], [data-state]");
    if (!buttons.length || !rows.length) return;
    var counter = $("[data-filter-count]");
    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        var value = button.getAttribute("data-filter");
        buttons.forEach(function (other) {
          other.setAttribute("aria-pressed", other === button ? "true" : "false");
        });
        var visible = 0;
        rows.forEach(function (row) {
          var states = (row.getAttribute("data-states") || row.getAttribute("data-state") || "")
            .split(",")
            .map(function (state) { return state.trim(); })
            .filter(Boolean);
          var show = value === "all" || states.indexOf(value) !== -1;
          row.style.display = show ? "" : "none";
          if (show) visible += 1;
        });
        if (counter) counter.textContent = visible + (visible === 1 ? " registro" : " registros");
      });
    });
  }

  /* ---------- scroll spy ------------------------------------------------- */
  function initScrollSpy() {
    var links = $$("[data-spy]");
    if (!links.length) return;
    var sections = links
      .map(function (link) {
        var id = link.getAttribute("href");
        return id && id.charAt(0) === "#" ? $(id) : null;
      })
      .filter(Boolean);
    if (!sections.length) return;
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          links.forEach(function (link) {
            var active = link.getAttribute("href") === "#" + entry.target.id;
            link.classList.toggle("is-active", active);
            if (active) link.setAttribute("aria-current", "location");
            else link.removeAttribute("aria-current");
          });
        });
      },
      { rootMargin: "-15% 0px -65% 0px", threshold: 0 }
    );
    sections.forEach(function (section) {
      observer.observe(section);
    });
  }

  /* ---------- pointer & reveal ------------------------------------------ */
  function initPointer() {
    var art = $(".hero-art");
    if (!art || !finePointer || reduceMotion) return;
    var targetX = 0;
    var targetY = 0;
    var currentX = 0;
    var currentY = 0;
    var raf = null;

    function animate() {
      currentX += (targetX - currentX) * 0.08;
      currentY += (targetY - currentY) * 0.08;
      art.style.setProperty("--px", currentX.toFixed(2) + "px");
      art.style.setProperty("--py", currentY.toFixed(2) + "px");
      if (Math.abs(targetX - currentX) > 0.1 || Math.abs(targetY - currentY) > 0.1) {
        raf = requestAnimationFrame(animate);
      } else {
        raf = null;
      }
    }

    window.addEventListener(
      "pointermove",
      function (event) {
        var x = event.clientX / window.innerWidth - 0.5;
        var y = event.clientY / window.innerHeight - 0.5;
        targetX = x * 14;
        targetY = y * 10;
        if (!raf) raf = requestAnimationFrame(animate);
      },
      { passive: true }
    );
  }

  function initReveal() {
    var items = $$("[data-reveal]");
    if (!items.length) return;
    if (reduceMotion || root.getAttribute("data-motion") === "reduce") {
      items.forEach(function (item) {
        item.classList.add("is-visible");
      });
      return;
    }
    if (!("IntersectionObserver" in window)) {
      items.forEach(function (item) {
        item.classList.add("is-visible");
      });
      return;
    }
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: "0px 0px -6% 0px" }
    );
    items.forEach(function (item) {
      observer.observe(item);
    });
  }

  /* ---------- initialise ------------------------------------------------ */
  function init() {
    syncPreferences();
    initFilters();
    initScrollSpy();
    initPointer();
    initReveal();

    var header = $("[data-header]");
    function onScroll() {
      if (!header) return;
      header.classList.toggle("is-scrolled", window.scrollY > 24);
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    $$("[data-open-index]").forEach(function (button) {
      button.addEventListener("click", function () {
        openSheet("index");
      });
    });
    $$("[data-open-search]").forEach(function (button) {
      button.addEventListener("click", openSearch);
    });
    $$("[data-open-prefs]").forEach(function (button) {
      button.addEventListener("click", function () {
        openSheet("index");
        var sheet = $("[data-sheet='index']");
        var prefs = $(".prefs", sheet);
        if (prefs) {
          requestAnimationFrame(function () {
            prefs.scrollIntoView({ block: "end", behavior: "smooth" });
          });
        }
      });
    });
    $$("[data-close-sheet]").forEach(function (button) {
      button.addEventListener("click", function () {
        closeSheet();
      });
    });
    $$(".sheet").forEach(function (sheet) {
      sheet.inert = true;
      var backdrop = $(".sheet__backdrop", sheet);
      if (backdrop) backdrop.addEventListener("click", closeSheet);
    });

    $$("[data-toggle-contrast]").forEach(function (button) {
      button.addEventListener("click", toggleContrast);
    });
    $$("[data-toggle-motion]").forEach(function (button) {
      button.addEventListener("click", toggleMotion);
    });
    $$("[data-text-size]").forEach(function (button) {
      button.addEventListener("click", function () {
        setTextSize(button.getAttribute("data-text-size"));
      });
    });

    searchInput = $("[data-search-input]");
    searchIndex = Array.isArray(window.SALUD_BUSQUEDA) ? window.SALUD_BUSQUEDA : [];
    if (searchInput) {
      searchInput.addEventListener("input", function () {
        renderSearch(searchInput.value);
      });
      searchInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
          var first = $(".search-result", $("[data-search-results]"));
          if (first) {
            event.preventDefault();
            window.location.href = first.getAttribute("href");
          }
        }
      });
      renderSearch("");
    }

    $$("[data-preview]").forEach(function (button) {
      button.addEventListener("click", function () {
        openDocModal(button);
      });
    });
    docModal = $("[data-doc-modal]");
    if (docModal) {
      docModal.inert = true;
      docModal.setAttribute("aria-hidden", "true");
      $$("[data-close-doc]", docModal).forEach(function (button) {
        button.addEventListener("click", closeDocModal);
      });
      var backdrop = $(".doc-modal__backdrop", docModal);
      if (backdrop) backdrop.addEventListener("click", closeDocModal);
    }

    $$("[data-print]").forEach(function (button) {
      button.addEventListener("click", function () {
        window.print();
      });
    });

    var printDates = $$("[data-print-date]");
    if (printDates.length) {
      var stamped = new Intl.DateTimeFormat("es-CL", {
        dateStyle: "long",
        timeStyle: "short",
      }).format(new Date());
      printDates.forEach(function (element) {
        element.textContent = stamped;
      });
    }

    $$("[data-year]").forEach(function (element) {
      element.textContent = new Date().getFullYear();
    });

    doc.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        if (docModal && docModal.classList.contains("is-open")) {
          closeDocModal();
          return;
        }
        if (activeSheet) closeSheet();
      }
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        openSearch();
      }
      if (
        event.key === "/" &&
        !event.ctrlKey &&
        !event.metaKey &&
        !event.altKey &&
        doc.activeElement &&
        !/^(INPUT|TEXTAREA|SELECT)$/.test(doc.activeElement.tagName)
      ) {
        event.preventDefault();
        openSearch();
      }
      trapFocus(event);
    });

    doc.addEventListener("click", function (event) {
      if (!event.target.closest) return;
      var searchResult = event.target.closest(".search-result");
      var sheetLink = event.target.closest(".sheet a[href]");
      if (searchResult || sheetLink) closeSheet(true);
    });
  }

  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
