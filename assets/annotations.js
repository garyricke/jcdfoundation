/* ==========================================================================
   JCD Foundation — highlight & comment layer
   --------------------------------------------------------------------------
   Reusable, dependency-free annotation engine for internal review pages.

   Usage (after the DOM is ready):
       JCDAnnotations.init({ page: 'status', backend: 'local' });

   - page    : unique slug stored with every annotation (e.g. 'status').
   - backend : 'local'  -> stores in this browser only (works with no setup).
               'api'    -> talks to /.netlify/functions/comments (Supabase).
   - root    : optional CSS selector to constrain commentable text
               (defaults to <body>; nav / footer / UI are always excluded).

   Anchoring is by text-quote (quote + surrounding context), so highlights
   survive reloads and minor edits. If a quote is later edited away, its
   thread becomes "orphaned" and is listed in the panel instead of vanishing.
   ========================================================================== */
(function () {
  'use strict';

  var CTX_LEN = 40;                 // chars of prefix/suffix context to store
  var EXCLUDE = '#nav, footer, script, style, noscript, .jcd-ann-ui';

  var page, rootEl, store, author;
  var state = [];                   // [{ id, quote, prefix, suffix, start_offset, author, comments:[], _placed }]
  var els = {};
  var pending = null;               // { range, info } captured at selection time
  var current = null;               // annotation open in the popover
  var mode = 'new';                 // 'new' | 'existing'

  /* ---------------------------------------------------------------- utils */
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
  function fmtTime(ts) {
    try { return new Date(ts).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }); }
    catch (e) { return ''; }
  }
  function isExcluded(node) {
    var el = node && node.nodeType === 3 ? node.parentNode : node;
    return !!(el && el.closest && el.closest(EXCLUDE));
  }

  /* --------------------------------------------------- text-quote anchoring */
  // Build an immutable string of the page's commentable text + a map back to
  // the live text nodes, so global character offsets resolve to DOM ranges.
  function buildMap() {
    var map = [], idx = 0, parts = [];
    var walker = document.createTreeWalker(rootEl, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (!n.nodeValue || !n.nodeValue.length) return NodeFilter.FILTER_REJECT;
        if (isExcluded(n)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var n;
    while ((n = walker.nextNode())) {
      var len = n.nodeValue.length;
      map.push({ node: n, start: idx, end: idx + len });
      parts.push(n.nodeValue);
      idx += len;
    }
    return { map: map, text: parts.join('') };
  }

  function globalOffset(map, node, offset) {
    for (var i = 0; i < map.length; i++) if (map[i].node === node) return map[i].start + offset;
    return null;
  }

  // Capture anchor data for a fresh selection range.
  function capture(range) {
    var m = buildMap();
    var quote = range.toString();
    if (!quote) return null;
    var s = globalOffset(m.map, range.startContainer, range.startOffset);
    if (s == null) s = m.text.indexOf(quote);     // fallback for element boundaries
    if (s < 0) s = 0;
    var e = s + quote.length;
    return {
      quote: quote,
      prefix: m.text.slice(Math.max(0, s - CTX_LEN), s),
      suffix: m.text.slice(e, e + CTX_LEN),
      start_offset: s
    };
  }

  // Find the best [start,end] for a stored annotation in the current text.
  function locate(text, ann) {
    var q = ann.quote;
    if (!q) return null;
    var occ = [], from = 0, i;
    while ((i = text.indexOf(q, from)) !== -1) { occ.push(i); from = i + 1; }
    if (!occ.length) return null;
    var best = occ[0], bestScore = -Infinity;
    for (var k = 0; k < occ.length; k++) {
      var pos = occ[k], score = 0;
      if (ann.prefix) {
        var pre = text.slice(Math.max(0, pos - ann.prefix.length), pos);
        if (pre === ann.prefix) score += 3; else if (pre.slice(-6) === ann.prefix.slice(-6)) score += 1;
      }
      if (ann.suffix) {
        var suf = text.slice(pos + q.length, pos + q.length + ann.suffix.length);
        if (suf === ann.suffix) score += 3; else if (suf.slice(0, 6) === ann.suffix.slice(0, 6)) score += 1;
      }
      if (typeof ann.start_offset === 'number') score -= Math.abs(pos - ann.start_offset) / 100000;
      if (score > bestScore) { bestScore = score; best = pos; }
    }
    return [best, best + q.length];
  }

  // Wrap the live DOM range [s,e] (global offsets) in <mark> pieces.
  function wrap(s, e, ann) {
    var m = buildMap(), pieces = [];
    for (var i = 0; i < m.map.length; i++) {
      var seg = m.map[i];
      if (seg.end <= s || seg.start >= e) continue;
      var ls = Math.max(s, seg.start) - seg.start;
      var le = Math.min(e, seg.end) - seg.start;
      if (le > ls) pieces.push({ node: seg.node, ls: ls, le: le });
    }
    var marks = [];
    pieces.forEach(function (p) {
      var r = document.createRange();
      try {
        r.setStart(p.node, p.ls); r.setEnd(p.node, p.le);
        var mk = document.createElement('mark');
        mk.className = 'jcd-hl'; mk.dataset.ann = ann.id;
        r.surroundContents(mk);
        marks.push(mk);
      } catch (err) { /* skip un-wrappable piece */ }
    });
    if (marks.length) {
      var flag = document.createElement('button');
      flag.type = 'button'; flag.className = 'jcd-flag jcd-ann-ui'; flag.dataset.ann = ann.id;
      flag.textContent = (ann.comments ? ann.comments.length : 1);
      marks[marks.length - 1].after(flag);
      ann._marks = marks; ann._flag = flag;
    }
    return marks.length > 0;
  }

  function placeOne(ann) {
    var m = buildMap();
    var range = locate(m.text, ann);
    ann._placed = range ? wrap(range[0], range[1], ann) : false;
  }
  function placeAll() { state.forEach(placeOne); }

  function updateFlag(ann) {
    if (ann._flag) ann._flag.textContent = ann.comments.length;
  }

  /* ------------------------------------------------------------------- UI */
  function buildUI() {
    var add = el('button', 'jcd-add jcd-ann-ui', 'Comment'); add.type = 'button'; add.hidden = true;
    var ctx = el('div', 'jcd-ctx jcd-ann-ui'); ctx.hidden = true;
    ctx.innerHTML = '<button type="button">💬 Comment</button>';

    var pop = el('div', 'jcd-pop jcd-ann-ui'); pop.hidden = true;
    pop.innerHTML =
      '<div class="jcd-pop-head"><span class="jcd-pop-title">Comments</span><button type="button" class="jcd-pop-x" aria-label="Close">&times;</button></div>' +
      '<div class="jcd-pop-quote"></div>' +
      '<div class="jcd-pop-list"></div>' +
      '<form class="jcd-pop-form">' +
        '<input class="jcd-name" type="text" placeholder="Your name" autocomplete="name" />' +
        '<textarea class="jcd-body" placeholder="Add a comment…"></textarea>' +
        '<div class="jcd-asline"></div>' +
        '<div class="jcd-pop-actions"><button type="button" class="jcd-cancel">Cancel</button><button type="submit" class="jcd-post">Post</button></div>' +
      '</form>';

    var toggle = el('button', 'jcd-toggle jcd-ann-ui'); toggle.type = 'button';
    toggle.innerHTML = '<span class="jcd-dot">💬</span> Comments <span class="jcd-count">0</span>';
    var panel = el('aside', 'jcd-panel jcd-ann-ui'); panel.hidden = true;
    panel.innerHTML = '<div class="jcd-panel-head">All comments on this page</div><div class="jcd-panel-body"></div>';

    [add, ctx, pop, toggle, panel].forEach(function (n) { document.body.appendChild(n); });

    els = {
      add: add, ctx: ctx, pop: pop, toggle: toggle, panel: panel,
      title: pop.querySelector('.jcd-pop-title'),
      quote: pop.querySelector('.jcd-pop-quote'),
      list: pop.querySelector('.jcd-pop-list'),
      form: pop.querySelector('.jcd-pop-form'),
      name: pop.querySelector('.jcd-name'),
      body: pop.querySelector('.jcd-body'),
      asline: pop.querySelector('.jcd-asline'),
      count: toggle.querySelector('.jcd-count'),
      panelBody: panel.querySelector('.jcd-panel-body')
    };

    add.addEventListener('click', function (e) { e.stopPropagation(); openComposer(); });
    ctx.querySelector('button').addEventListener('click', function (e) { e.stopPropagation(); hideCtx(); openComposer(); });
    pop.querySelector('.jcd-pop-x').addEventListener('click', closePop);
    pop.querySelector('.jcd-cancel').addEventListener('click', closePop);
    els.form.addEventListener('submit', onSubmit);
    toggle.addEventListener('click', function (e) { e.stopPropagation(); panel.hidden ? openPanel() : (panel.hidden = true); });
  }
  function el(tag, cls, text) {
    var n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n;
  }

  /* --------------------------------------------------------- selection flow */
  function validSelection() {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) return null;
    if (!sel.toString().trim()) return null;
    var r = sel.getRangeAt(0);
    if (!rootEl.contains(r.commonAncestorContainer)) return null;
    if (isExcluded(r.startContainer) || isExcluded(r.endContainer)) return null;
    return r;
  }
  function showAddNear(rect) {
    els.add.style.top = (rect.top + window.scrollY - 42) + 'px';
    els.add.style.left = (rect.left + window.scrollX + rect.width / 2) + 'px';
    els.add.hidden = false;
  }
  function hideAdd() { els.add.hidden = true; }
  function hideCtx() { els.ctx.hidden = true; }

  function maybeShowAdd() {
    var r = validSelection();
    if (!r) { hideAdd(); return; }
    pending = { range: r.cloneRange(), info: null };
    showAddNear(r.getBoundingClientRect());
  }

  /* -------------------------------------------------------------- composer */
  function openComposer() {
    var r = pending && pending.range;
    if (!r) return;
    pending.info = capture(r);
    if (!pending.info) return;
    hideAdd();
    mode = 'new'; current = null;
    els.title.textContent = 'New comment';
    els.quote.textContent = pending.info.quote;
    els.list.innerHTML = '';
    els.body.value = '';
    syncNameField();
    positionPop(r.getBoundingClientRect());
    els.pop.hidden = false;
    els.body.focus();
  }

  function openThread(ann, anchorEl) {
    mode = 'existing'; current = ann;
    els.title.textContent = 'Comments';
    els.quote.textContent = ann.quote;
    renderThread(ann);
    els.body.value = '';
    syncNameField();
    var rect;
    if (anchorEl && anchorEl.getBoundingClientRect) rect = anchorEl.getBoundingClientRect();
    else if (ann._marks && ann._marks[0]) rect = ann._marks[0].getBoundingClientRect();
    else rect = { top: window.innerHeight / 2 - 100, left: window.innerWidth / 2, width: 0 };
    positionPop(rect);
    els.pop.hidden = false;
    if (ann._marks) ann._marks.forEach(function (m) { m.classList.add('jcd-active'); });
    els.body.focus();
  }

  function renderThread(ann) {
    var html = '';
    (ann.comments || []).forEach(function (c) {
      html += '<div class="jcd-c"><div class="jcd-c-meta"><span class="jcd-c-author">' +
        esc(c.author || 'Anonymous') + '</span><span class="jcd-c-time">' + esc(fmtTime(c.created_at)) +
        '</span></div><div class="jcd-c-body">' + esc(c.body) + '</div></div>';
    });
    els.list.innerHTML = html;
    els.list.scrollTop = els.list.scrollHeight;
  }

  function syncNameField() {
    if (author) {
      els.name.hidden = true;
      els.asline.innerHTML = 'Commenting as <strong>' + esc(author) + '</strong> · <button type="button">change</button>';
      els.asline.querySelector('button').onclick = function () {
        author = ''; els.name.value = ''; els.name.hidden = false; els.asline.innerHTML = ''; els.name.focus();
      };
    } else {
      els.name.hidden = false;
      els.asline.innerHTML = '';
    }
  }

  function positionPop(rect) {
    els.pop.hidden = false; // measure
    var w = els.pop.offsetWidth, h = els.pop.offsetHeight;
    var top = rect.top + window.scrollY + (rect.height || 0) + 8;
    var left = rect.left + window.scrollX + (rect.width || 0) / 2 - w / 2;
    var maxLeft = window.scrollX + document.documentElement.clientWidth - w - 12;
    left = Math.max(window.scrollX + 12, Math.min(left, maxLeft));
    if (rect.top + (rect.height || 0) + h + 16 > window.innerHeight && rect.top - h - 8 > 0) {
      top = rect.top + window.scrollY - h - 8; // flip above
    }
    els.pop.style.top = top + 'px';
    els.pop.style.left = left + 'px';
  }

  function closePop() {
    els.pop.hidden = true;
    if (current && current._marks) current._marks.forEach(function (m) { m.classList.remove('jcd-active'); });
    current = null;
  }

  function onSubmit(e) {
    e.preventDefault();
    var body = els.body.value.trim();
    if (!body) { els.body.focus(); return; }
    var name = author || els.name.value.trim();
    if (!name) { els.name.hidden = false; els.name.focus(); return; }
    if (!author) { author = name; try { localStorage.setItem('jcd_ann_author', author); } catch (x) {} }

    els.form.querySelector('.jcd-post').disabled = true;

    if (mode === 'new') {
      var ann = {
        page: page, quote: pending.info.quote, prefix: pending.info.prefix,
        suffix: pending.info.suffix, start_offset: pending.info.start_offset,
        color: 'gold', author: name
      };
      store.createAnnotation(ann).then(function (saved) {
        saved.comments = saved.comments || [];
        return store.addComment(saved.id, { author: name, body: body }).then(function (c) {
          saved.comments.push(c);
          state.push(saved);
          placeOne(saved);
          updateCount();
          openThread(saved);
        });
      }).catch(reportErr).then(reEnable);
    } else {
      store.addComment(current.id, { author: name, body: body }).then(function (c) {
        current.comments = current.comments || [];
        current.comments.push(c);
        els.body.value = '';
        renderThread(current);
        updateFlag(current);
        syncNameField();
      }).catch(reportErr).then(reEnable);
    }
  }
  function reEnable() { els.form.querySelector('.jcd-post').disabled = false; }
  function reportErr(err) { console.error('[jcd-annotations]', err); alert('Could not save the comment. Please try again.'); }

  /* ------------------------------------------------------------------ panel */
  function openPanel() {
    var html = '';
    if (!state.length) {
      html = '<div class="jcd-panel-empty">No comments yet. Select any text on the page to leave one.</div>';
    } else {
      state.slice().reverse().forEach(function (ann) {
        var n = ann.comments ? ann.comments.length : 0;
        var orphan = ann._placed ? '' : ' · <span class="jcd-item-orphan">text changed</span>';
        html += '<button type="button" class="jcd-item" data-ann="' + esc(ann.id) + '">' +
          '<div class="jcd-item-quote">“' + esc(ann.quote) + '”</div>' +
          '<div class="jcd-item-meta"><span>' + n + ' comment' + (n === 1 ? '' : 's') + '</span>' +
          '<span>' + esc((ann.comments && ann.comments[0] && ann.comments[0].author) || '') + '</span>' + orphan +
          '</div></button>';
      });
    }
    els.panelBody.innerHTML = html;
    els.panel.hidden = false;
  }

  function openById(id, anchorEl) {
    var ann = find(id);
    if (ann) openThread(ann, anchorEl);
  }
  function find(id) { for (var i = 0; i < state.length; i++) if (String(state[i].id) === String(id)) return state[i]; return null; }

  function updateCount() { els.count.textContent = state.length; }

  /* --------------------------------------------------------------- storage */
  function makeStore(backend) {
    if (backend === 'api') {
      var EP = '/.netlify/functions/comments';
      var post = function (b) {
        return fetch(EP, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(b) })
          .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); });
      };
      return {
        list: function () {
          return fetch(EP + '?page=' + encodeURIComponent(page))
            .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
            .then(function (d) { return d.annotations || []; });
        },
        createAnnotation: function (a) { return post({ type: 'annotation', annotation: a }).then(function (d) { return d.annotation; }); },
        addComment: function (id, c) { return post({ type: 'comment', annotation_id: id, comment: c }).then(function (d) { return d.comment; }); }
      };
    }
    // localStorage backend
    var KEY = 'jcd_ann_' + page;
    var read = function () { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } };
    var save = function (a) { try { localStorage.setItem(KEY, JSON.stringify(a)); } catch (e) {} };
    return {
      list: function () { return Promise.resolve(read()); },
      createAnnotation: function (a) {
        a.id = uuid(); a.created_at = new Date().toISOString(); a.comments = [];
        var all = read(); all.push(a); save(all); return Promise.resolve(a);
      },
      addComment: function (id, c) {
        c.id = uuid(); c.created_at = new Date().toISOString();
        var all = read(), x = null;
        for (var i = 0; i < all.length; i++) if (all[i].id === id) x = all[i];
        if (x) { x.comments = x.comments || []; x.comments.push(c); save(all); }
        return Promise.resolve(c);
      }
    };
  }

  /* ------------------------------------------------------------------ wire */
  function bindGlobal() {
    document.addEventListener('mouseup', function (e) {
      if (e.target.closest && e.target.closest('.jcd-ann-ui')) return;
      setTimeout(maybeShowAdd, 0);
    });
    document.addEventListener('mousedown', function (e) {
      if (e.target.closest && e.target.closest('.jcd-ann-ui')) return;
      hideAdd(); hideCtx();
    });
    document.addEventListener('contextmenu', function (e) {
      if (e.target.closest && e.target.closest('.jcd-ann-ui')) return;
      var r = validSelection();
      if (!r) return;                       // no selection → keep native menu
      e.preventDefault();
      pending = { range: r.cloneRange(), info: null };
      els.ctx.style.top = (e.pageY) + 'px';
      els.ctx.style.left = (e.pageX) + 'px';
      els.ctx.hidden = false;
    });
    document.addEventListener('click', function (e) {
      var hit = e.target.closest && e.target.closest('.jcd-hl, .jcd-flag');
      if (hit) { e.preventDefault(); openById(hit.dataset.ann, hit); return; }
      var item = e.target.closest && e.target.closest('.jcd-item');
      if (item) {
        var ann = find(item.dataset.ann);
        els.panel.hidden = true;
        if (ann && ann._marks && ann._marks[0]) ann._marks[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
        if (ann) openThread(ann);
        return;
      }
      if (!e.target.closest('.jcd-ann-ui')) { els.ctx.hidden = true; }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { closePop(); hideAdd(); hideCtx(); els.panel.hidden = true; }
    });
  }

  /* ------------------------------------------------------------------ init */
  function init(opts) {
    opts = opts || {};
    page = opts.page || (location.pathname.split('/').pop() || 'index').replace(/\.html?$/, '');
    rootEl = (opts.root && document.querySelector(opts.root)) || document.body;
    try { author = localStorage.getItem('jcd_ann_author') || ''; } catch (e) { author = ''; }
    store = makeStore(opts.backend === 'api' ? 'api' : 'local');

    buildUI();
    bindGlobal();

    store.list().then(function (rows) {
      state = (rows || []).map(function (a) { a.comments = a.comments || []; return a; });
      placeAll();
      updateCount();
    }).catch(function (err) {
      console.error('[jcd-annotations] load failed', err);
      updateCount();
    });
  }

  window.JCDAnnotations = { init: init };
})();
