/* Демо-оверлей: курсор, субтитры и главы.
 *
 * Инжектится в каждую страницу через page.addInitScript(). Экспортирует в
 * window два объекта:
 *   - window.__demoOverlay: { showChapter, showSubtitle, hideSubtitle, attentionRing }
 *   - window.__demoCursor:  { moveTo, pressAt, ensureMounted, show, hide }
 *
 * Координаты — viewport, в пикселях.
 */

(function () {
  if (window.__demoInstalled) return;
  window.__demoInstalled = true;

  const SVG_CURSOR =
    "<svg viewBox='0 0 32 32' xmlns='http://www.w3.org/2000/svg'>" +
    "<path d='M5 3 L5 26 L12 19 L15.5 28 L20 26 L16.5 17 L25 17 Z' " +
    "fill='#111827' stroke='#f8fafc' stroke-width='1.5' stroke-linejoin='round'/>" +
    "</svg>";

  // addInitScript может сработать ДО появления <body>. Подождём DOMContentLoaded.
  function onReady(fn) {
    if (document.body) return fn();
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      // Если уже loaded но body нет — поллим 5 раз по 10мс.
      let tries = 0;
      const t = setInterval(() => {
        if (document.body) {
          clearInterval(t);
          fn();
        } else if (++tries > 20) {
          clearInterval(t);
        }
      }, 10);
    }
  }

  function ensureEl(id, tag = "div") {
    if (!document.body) return null;
    let el = document.getElementById(id);
    if (!el) {
      el = document.createElement(tag);
      el.id = id;
      document.body.appendChild(el);
    }
    return el;
  }

  function mountCursor() {
    const el = ensureEl("__demo_cursor");
    if (!el) return null;
    if (!el.firstChild) el.innerHTML = SVG_CURSOR;
    return el;
  }

  // Очередь операций, которые дожидаются body.
  const pending = [];
  function enqueueOrRun(fn) {
    if (document.body) return fn();
    pending.push(fn);
  }
  onReady(() => {
    while (pending.length) {
      const fn = pending.shift();
      try { fn(); } catch (e) { console.error(e); }
    }
  });

  function wait(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  const state = {
    cursorX: 200,
    cursorY: 200,
    cursorMoving: false,
    subtitleEl: null,
    chapterEl: null,
    chapterTimer: null,
  };

  function placeCursor(x, y) {
    const el = mountCursor();
    state.cursorX = x;
    state.cursorY = y;
    el.style.transform = `translate(${x - 4}px, ${y - 4}px)`;
  }

  function show() {
    mountCursor().classList.add("__demo_visible");
  }

  function hide() {
    mountCursor().classList.remove("__demo_visible");
  }

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  async function moveTo(x, y, durMs) {
    const el = mountCursor();
    el.classList.add("__demo_visible");
    const fromX = state.cursorX;
    const fromY = state.cursorY;
    const dx = x - fromX;
    const dy = y - fromY;
    const dist = Math.hypot(dx, dy);
    if (dist < 2) {
      placeCursor(x, y);
      return;
    }
    if (!durMs) durMs = Math.max(280, Math.min(1100, dist / 1.6));
    const t0 = performance.now();
    return new Promise((resolve) => {
      function step(now) {
        const p = Math.min(1, (now - t0) / durMs);
        const e = easeOutCubic(p);
        const cx = fromX + dx * e;
        const cy = fromY + dy * e;
        placeCursor(cx, cy);
        if (p < 1) requestAnimationFrame(step);
        else resolve();
      }
      requestAnimationFrame(step);
    });
  }

  async function pressAt(x, y) {
    const el = mountCursor();
    el.classList.add("__demo_visible");
    placeCursor(x, y);
    // ripple
    const ripple = document.createElement("div");
    ripple.className = "__demo_ripple";
    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;
    document.body.appendChild(ripple);
    setTimeout(() => ripple.remove(), 500);
    // press feedback
    el.classList.add("__demo_pressed");
    el.style.transform = `translate(${x - 4}px, ${y - 4}px) scale(0.92)`;
    await wait(90);
    el.classList.remove("__demo_pressed");
    el.style.transform = `translate(${x - 4}px, ${y - 4}px)`;
  }

  function attentionRing(rect, durationMs = 550) {
    enqueueOrRun(() => {
      if (!document.body) return;
      const ring = document.createElement("div");
      ring.className = "__demo_ring";
      ring.style.left = `${rect.x - 6}px`;
      ring.style.top = `${rect.y - 6}px`;
      ring.style.width = `${rect.width + 12}px`;
      ring.style.height = `${rect.height + 12}px`;
      document.body.appendChild(ring);
      setTimeout(() => ring.remove(), durationMs);
    });
  }

  function showChapter(text, holdMs = 1500) {
    enqueueOrRun(() => {
      if (state.chapterTimer) {
        clearTimeout(state.chapterTimer);
        state.chapterTimer = null;
      }
      if (state.chapterEl) state.chapterEl.remove();
      const el = document.createElement("div");
      el.id = "__demo_chapter";
      el.textContent = text;
      document.body.appendChild(el);
      state.chapterEl = el;
      state.chapterTimer = setTimeout(() => {
        el.classList.add("__demo_leaving");
        setTimeout(() => {
          el.remove();
          if (state.chapterEl === el) state.chapterEl = null;
        }, 260);
      }, holdMs);
    });
  }

  function showSubtitle(text) {
    enqueueOrRun(() => {
      if (state.subtitleEl) {
        state.subtitleEl.remove();
        state.subtitleEl = null;
      }
      const el = document.createElement("div");
      el.id = "__demo_subtitle";
      el.setAttribute("aria-live", "polite");
      el.textContent = text;
      document.body.appendChild(el);
      state.subtitleEl = el;
    });
  }

  function hideSubtitle() {
    enqueueOrRun(() => {
      if (!state.subtitleEl) return;
      const el = state.subtitleEl;
      state.subtitleEl = null;
      el.classList.add("__demo_leaving");
      setTimeout(() => el.remove(), 220);
    });
  }

  window.__demoOverlay = {
    showChapter,
    showSubtitle,
    hideSubtitle,
    attentionRing,
  };
  window.__demoCursor = {
    moveTo,
    pressAt,
    placeCursor,
    show,
    hide,
    ensureMounted: mountCursor,
  };
})();
