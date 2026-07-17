/* Scholar's Compass — global behavior (GitHub Pages static site)
   Shared shell stabilization, approved ENG 1010 display order,
   and chapter-specific interactive tools.
*/

(function () {
  'use strict';

  document.documentElement.classList.add('js');

  // Load the reversible shared correction layer from the same folder as app.js.
  (function loadStabilizationStyles() {
    if (document.querySelector('link[data-sc-stabilization="0.7"]')) return;
    var current = document.currentScript;
    var href;
    try {
      href = current && current.src
        ? new URL('stabilization-0.2.css?v=7', current.src).href
        : ((window.location.pathname.indexOf('/1010/') !== -1 || window.location.pathname.indexOf('/1020/') !== -1)
          ? '../stabilization-0.2.css?v=7'
          : 'stabilization-0.2.css?v=7');
    } catch (err) {
      href = '../stabilization-0.2.css?v=7';
    }
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = href;
    link.setAttribute('data-sc-stabilization', '0.6');
    document.head.appendChild(link);
  })();

  // Approved ENG 1010 final deployment sequence and filenames.
  var CHAPTERS_1010 = [
    { href: 'chapter-1.html', icon: 'fas fa-highlighter', title: '1. Annotating Your Way to Greatness', readingTime: '15 min' },
    { href: 'chapter-2.html', icon: 'fas fa-book-reader', title: '2. Active Reading Strategies', readingTime: '12 min' },
    { href: 'chapter-3.html', icon: 'fas fa-clipboard-list', title: '3. Summarizing Your Way to Synthesis', readingTime: '10 min' },
    { href: 'chapter-4.html', icon: 'fas fa-quote-left', title: '4. Quoting, Paraphrasing, and Signal Phrases', readingTime: '12 min' },
    { href: 'chapter-5.html', icon: 'fas fa-bullhorn', title: '5. Understanding Rhetoric: The Art of Persuasion', readingTime: '18 min' },
    { href: 'chapter-6.html', icon: 'fas fa-layer-group', title: '6. Values, Assumptions, and Ideology', readingTime: '14 min' },
    { href: 'chapter-7.html', icon: 'fas fa-pen-fancy', title: '7. Strategies for Getting Started', readingTime: '9 min' },
    { href: 'chapter-8.html', icon: 'fas fa-bullseye', title: '8. Crafting Powerful Thesis Statements', readingTime: '11 min' },
    { href: 'chapter-9.html', icon: 'fas fa-align-left', title: '9. Designing Effective Paragraphs', readingTime: '13 min' },
    { href: 'chapter-10.html', icon: 'fas fa-project-diagram', title: '10. Analysis and Synthesis', readingTime: '16 min' },
    { href: 'chapter-11.html', icon: 'fas fa-comments', title: '11. Argumentation: Joining the Academic Conversation', readingTime: '18 min' },
    { href: 'chapter-12.html', icon: 'fas fa-search', title: '12. Finding and Evaluating Sources', readingTime: '12 min' },
    { href: 'chapter-13.html', icon: 'fas fa-link', title: '13. Using Sources in Your Argument', readingTime: '14 min' },
    { href: 'chapter-14.html', icon: 'fas fa-pen-to-square', title: '14. Revision: From Draft to Final', readingTime: '12 min' }
  ];

  var CHAPTERS_1020 = [
    { href: 'chapter-1.html', icon: 'fas fa-book-open', title: '1. Active Reading for Literature', readingTime: '10–15 min' },
    { href: 'chapter-2.html', icon: 'fas fa-highlighter', title: '2. Annotation for Close Reading', readingTime: '10–15 min' },
    { href: 'chapter-3.html', icon: 'fas fa-pen-fancy', title: '3. Getting Started: Prewriting for Literary Analysis', readingTime: '10–15 min' },
    { href: 'chapter-4.html', icon: 'fas fa-magnifying-glass', title: '4. Close Reading: From Passage to Claim', readingTime: '10–15 min' },
    { href: 'chapter-5.html', icon: 'fas fa-feather-pointed', title: '5. Fiction Toolkit: Narrative Craft + Character', readingTime: '10–15 min' },
    { href: 'chapter-6.html', icon: 'fas fa-music', title: '6. Poetry Toolkit: Reading What’s on the Line', readingTime: '10–15 min' },
    { href: 'chapter-7.html', icon: 'fas fa-masks-theater', title: '7. Drama Toolkit: Scenes, Staging, and Subtext', readingTime: '10–15 min' },
    { href: 'chapter-8.html', icon: 'fas fa-comments', title: '8. Argumentation in Literary Studies', readingTime: '10–15 min' },
    { href: 'chapter-9.html', icon: 'fas fa-search', title: '9. Finding and Evaluating Secondary Sources', readingTime: '10–15 min' },
    { href: 'chapter-10.html', icon: 'fas fa-glasses', title: '10. Working with Literary Criticism: Lens, Not Crutch', readingTime: '10–15 min' },
    { href: 'chapter-11.html', icon: 'fas fa-quote-left', title: '11. Quoting, Paraphrasing, and Signal Phrases', readingTime: '10–15 min' },
    { href: 'chapter-12.html', icon: 'fas fa-link', title: '12. Using Sources in Your Argument', readingTime: '10–15 min' },
    { href: 'chapter-13.html', icon: 'fas fa-bullseye', title: '13. Crafting Powerful Thesis Statements', readingTime: '10–15 min' },
    { href: 'chapter-14.html', icon: 'fas fa-align-left', title: '14. Designing Effective Literary Analysis Paragraphs', readingTime: '10–15 min' },
    { href: 'chapter-15.html', icon: 'fas fa-pen-to-square', title: '15. Revision: From Draft to Final', readingTime: '10–15 min' }
  ];

  function getCourse() {
    var p = (window.location.pathname || '').toLowerCase();
    if (p.indexOf('/1020/') !== -1) return '1020';
    if (p.indexOf('/1010/') !== -1) return '1010';
    var b = document.body;
    if (b && b.getAttribute) {
      var c = b.getAttribute('data-course');
      if (c) return String(c);
    }
    return '1010';
  }

  function getChapters() {
    return getCourse() === '1020' ? CHAPTERS_1020 : CHAPTERS_1010;
  }

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  function currentFile() {
    var f = (window.location.pathname || '').split('/').pop();
    return (f && f.trim()) ? f : 'index.html';
  }

  function qs(sel, root) { return (root || document).querySelector(sel); }
  function qsa(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function storageGet(key, fallback) {
    try {
      var raw = localStorage.getItem(key);
      return raw === null ? fallback : JSON.parse(raw);
    } catch (err) {
      return fallback;
    }
  }

  function storageSet(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (err) {
      return false;
    }
  }

  function storageRemove(key) {
    try { localStorage.removeItem(key); } catch (err) {}
  }

  function closestTool(element) {
    if (!element || !element.closest) return null;
    return element.closest('.interactive-element, .thesis-builder, .paragraph-builder, .quote-builder, .counterargument-builder, .freewriting-container, .question-prompter, .sandwich-builder');
  }

  function setToolStatus(element, message, tone) {
    var container = closestTool(element) || (element && element.parentElement) || document.body;
    var status = qs('.sc-tool-status', container);
    if (!status) {
      status = document.createElement('p');
      status.className = 'sc-tool-status';
      status.setAttribute('role', 'status');
      status.setAttribute('aria-live', 'polite');
      status.style.marginTop = '0.85rem';
      status.style.padding = '0.75rem 0.9rem';
      status.style.borderRadius = '0.35rem';
      status.style.fontWeight = '600';
      container.appendChild(status);
    }
    status.textContent = message;
    status.style.background = tone === 'error' ? '#fff3cd' : (tone === 'success' ? '#d4edda' : '#e9ecef');
    status.style.color = tone === 'error' ? '#664d03' : (tone === 'success' ? '#0f5132' : '#222');
    status.style.borderLeft = '4px solid ' + (tone === 'error' ? '#ffc107' : (tone === 'success' ? '#28a745' : '#6c757d'));
    return status;
  }

  function setElementText(id, text) {
    var el = qs('#' + id);
    if (el) el.textContent = text;
    return el;
  }

  window.toggleSection = function (headerEl) {
    if (!headerEl) return;
    var section = headerEl.closest ? headerEl.closest('.section') : null;
    if (!section) return;
    var willOpen = !section.classList.contains('active');
    section.classList.toggle('active', willOpen);
    headerEl.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
  };

  window.toggleAnnotation = function (item) {
    if (!item) return;
    var pressed = item.getAttribute('aria-pressed') === 'true' || item.classList.contains('active');
    item.setAttribute('aria-pressed', pressed ? 'false' : 'true');
    item.classList.toggle('active', !pressed);
  };

  function initPageLandmarks() {
    var main = qs('main') || qs('.container');
    if (!main) return;
    if (!main.id) main.id = 'main-content';
    if (String(main.tagName).toLowerCase() !== 'main') main.setAttribute('role', 'main');
    if (!main.hasAttribute('tabindex')) main.setAttribute('tabindex', '-1');

    var skip = qs('.skip-link');
    if (!skip) {
      skip = document.createElement('a');
      skip.className = 'skip-link';
      skip.textContent = 'Skip to main content';
    }
    skip.setAttribute('href', '#' + main.id);
    if (document.body.firstChild !== skip) document.body.insertBefore(skip, document.body.firstChild);

    skip.addEventListener('click', function (event) {
      event.preventDefault();
      try { main.focus({ preventScroll: true }); }
      catch (err) { main.focus(); }
      main.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  function isDarkPreferred() {
    var v = localStorage.getItem('darkMode');
    if (v === 'true') return true;
    if (v === 'false') return false;
    var theme = localStorage.getItem('theme');
    if (theme === 'dark') return true;
    if (theme === 'light') return false;
    return false;
  }

  function setTheme(isDark) {
    document.body.classList.toggle('dark-mode', isDark);
    try {
      localStorage.setItem('darkMode', isDark ? 'true' : 'false');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
    } catch (err) {}
    var toggle = qs('#darkModeToggle');
    if (toggle) {
      var icon = toggle.querySelector('i');
      if (icon) icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
      toggle.setAttribute('aria-pressed', isDark ? 'true' : 'false');
    }
  }

  function initThemeToggle() {
    setTheme(isDarkPreferred());
    var toggle = qs('#darkModeToggle');
    if (!toggle) return;
    toggle.addEventListener('click', function () {
      setTheme(!document.body.classList.contains('dark-mode'));
    });
  }

  function initBackToTop() {
    var btn = qs('#backToTop');
    if (!btn) return;
    btn.addEventListener('click', function (event) {
      event.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  function initSidebar() {
    var hamburger = qs('#hamburgerMenu');
    var sidebar = qs('#sidebar');
    var overlay = qs('#sidebarOverlay');
    var closeBtn = qs('#sidebarClose');
    if (!hamburger || !sidebar || !overlay) return;

    var previousFocus = null;
    function setSidebarState(isOpen) {
      sidebar.classList.toggle('active', isOpen);
      overlay.classList.toggle('active', isOpen);
      hamburger.classList.toggle('active', isOpen);
      hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      sidebar.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
      document.body.style.overflow = isOpen ? 'hidden' : '';
    }
    function openSidebar() {
      previousFocus = document.activeElement;
      setSidebarState(true);
      (closeBtn || sidebar).focus();
    }
    function closeSidebar() {
      setSidebarState(false);
      if (previousFocus && previousFocus.focus) previousFocus.focus();
      else hamburger.focus();
    }

    hamburger.addEventListener('click', openSidebar);
    if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
    overlay.addEventListener('click', closeSidebar);
    qsa('.sidebar-link[href*="chapter"]').forEach(function (a) {
      a.addEventListener('click', function () {
        if (window.innerWidth <= 768) closeSidebar();
      });
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && sidebar.classList.contains('active')) closeSidebar();
    });

    var touchStartX = 0;
    document.addEventListener('touchstart', function (event) {
      touchStartX = event.changedTouches[0].screenX;
    }, { passive: true });
    document.addEventListener('touchend', function (event) {
      var touchEndX = event.changedTouches[0].screenX;
      var swipeDistance = touchEndX - touchStartX;
      if (Math.abs(swipeDistance) <= 100) return;
      if (swipeDistance > 0 && touchStartX < 50) openSidebar();
      else if (swipeDistance < 0 && sidebar.classList.contains('active')) closeSidebar();
    }, { passive: true });
  }

  function buildChaptersNav() {
    var container = qs('#chaptersList');
    if (!container) return;
    container.innerHTML = '';
    var here = currentFile().toLowerCase();

    getChapters().forEach(function (ch) {
      var a = document.createElement('a');
      a.href = ch.href;
      a.className = 'sidebar-link';
      if (here === String(ch.href).toLowerCase()) {
        a.className += ' current';
        a.setAttribute('aria-current', 'page');
      }
      var icon = document.createElement('i');
      icon.className = ch.icon || 'fas fa-book';
      a.appendChild(icon);
      a.appendChild(document.createTextNode(ch.title));
      if (ch.readingTime) {
        var rt = document.createElement('span');
        rt.className = 'reading-time';
        rt.textContent = ch.readingTime;
        a.appendChild(rt);
      }
      container.appendChild(a);
    });
  }

  function apply1010IndexOrder() {
    if (getCourse() !== '1010' || currentFile().toLowerCase() !== 'index.html') return;
    var links = qsa('.chapter-link[href]');
    if (!links.length) return;
    var byHref = {};
    links.forEach(function (link) {
      var href = String(link.getAttribute('href') || '').split('/').pop().toLowerCase();
      byHref[href] = link;
    });
    var row = links[0].closest('.row');
    if (!row) return;
    CHAPTERS_1010.forEach(function (chapter, index) {
      var link = byHref[String(chapter.href).toLowerCase()];
      if (!link) return;
      link.setAttribute('data-chapter', String(index + 1));
      var number = link.querySelector('.card-number');
      if (number) number.textContent = String(index + 1);
      var column = link.closest('.col');
      if (column) row.appendChild(column);
    });
  }

  function normalize1010ChapterLinkLabels() {
    if (getCourse() !== '1010') return;
    var displayNumbers = {};
    CHAPTERS_1010.forEach(function (chapter, index) {
      displayNumbers[String(chapter.href).toLowerCase()] = index + 1;
    });
    qsa('a[href*="chapter-"]').forEach(function (anchor) {
      var file = String(anchor.getAttribute('href') || '').split('/').pop().toLowerCase();
      var displayNumber = displayNumbers[file];
      if (!displayNumber) return;
      Array.prototype.slice.call(anchor.childNodes).forEach(function (child) {
        if (child.nodeType !== 3) return;
        child.nodeValue = child.nodeValue.replace(/Chapter\s+\d+/g, 'Chapter ' + displayNumber);
      });
    });
  }

  function updateQuickNav() {
    var links = qsa('.quick-nav a[data-section]');
    if (!links.length) return;
    var markerY = 120;
    var activeId = null;
    qsa('.section[id]').forEach(function (sec) {
      var r = sec.getBoundingClientRect();
      if (r.top <= markerY && r.bottom >= markerY) activeId = sec.id;
    });
    if (!activeId) return;
    links.forEach(function (a) {
      a.classList.toggle('active', a.getAttribute('data-section') === activeId);
    });
  }

  function updateScrollUI() {
    var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    var scrolled = height > 0 ? (winScroll / height) * 100 : 0;
    var bar1 = qs('#progressBar');
    if (bar1) bar1.style.width = scrolled + '%';
    var bar2 = qs('#scrollProgress');
    if (bar2) bar2.style.width = scrolled + '%';
    var back = qs('#backToTop');
    if (back) back.classList.toggle('visible', winScroll > 300);
    updateQuickNav();
  }

  function initScrollHandlers() {
    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        updateScrollUI();
        ticking = false;
      });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    updateScrollUI();
  }

  function initSmoothAnchors() {
    qsa('a[href^="#"]').forEach(function (a) {
      if (a.classList.contains('skip-link')) return;
      a.addEventListener('click', function (event) {
        var href = a.getAttribute('href');
        if (!href || href.length < 2) return;
        var target = qs(href);
        if (!target) return;
        event.preventDefault();
        var y = target.getBoundingClientRect().top + window.pageYOffset - 80;
        window.scrollTo({ top: y, behavior: 'smooth' });
      });
    });
  }

  function initSectionDisclosures() {
    qsa('.section').forEach(function (section, index) {
      var header = section.querySelector('.section-header');
      var content = section.querySelector('.section-content');
      if (!header || !content || header.getAttribute('data-disclosure-ready') === 'true') return;
      var sectionId = section.id || ('section-' + (index + 1));
      var headerId = header.id || (sectionId + '-toggle');
      var contentId = content.id || (sectionId + '-content');
      section.id = sectionId;
      header.id = headerId;
      content.id = contentId;
      header.removeAttribute('onclick');
      header.setAttribute('aria-controls', contentId);
      header.setAttribute('aria-expanded', section.classList.contains('active') ? 'true' : 'false');
      header.setAttribute('data-disclosure-ready', 'true');
      content.setAttribute('role', 'region');
      content.setAttribute('aria-labelledby', headerId);
      var isNativeButton = String(header.tagName).toLowerCase() === 'button';
      if (!isNativeButton) {
        header.setAttribute('role', 'button');
        header.setAttribute('tabindex', '0');
        header.addEventListener('keydown', function (event) {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            window.toggleSection(header);
          }
        });
      } else if (!header.getAttribute('type')) {
        header.setAttribute('type', 'button');
      }
      header.addEventListener('click', function () { window.toggleSection(header); });
    });
  }

  function normalizeSharedCallouts() {
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var nodes = [];
    var node;
    while ((node = walker.nextNode())) nodes.push(node);
    nodes.forEach(function (textNode) {
      if (!/Research Insights?/.test(textNode.nodeValue)) return;
      textNode.nodeValue = textNode.nodeValue.replace(/Research Insights?/g, 'Key Insight');
    });

    qsa([
      '.highlight-box p:first-child > strong:first-child',
      '.tools-note p:first-child > strong:first-child',
      '.example-box > strong:first-child',
      '.example-box p:first-child > strong:first-child',
      '.key-takeaway p:first-child > strong:first-child',
      '.social-exercise > h4:first-child'
    ].join(',')).forEach(function (label) {
      label.classList.add('sc-callout-label');
      var box = label.closest('.highlight-box, .tools-note, .example-box, .key-takeaway, .social-exercise');
      if (box) box.classList.add('sc-callout-has-label');
    });

    qsa('.annotation-item').forEach(function (item) {
      if (item.querySelector('.sc-annotation-text')) return;
      var marker = item.querySelector('.annotation-color');
      var textWrap = document.createElement('span');
      textWrap.className = 'sc-annotation-text';
      Array.prototype.slice.call(item.childNodes).forEach(function (child) {
        if (child !== marker) textWrap.appendChild(child);
      });
      item.appendChild(textWrap);
    });
  }

  function initAnnotationExamples() {
    qsa('.annotation-item[aria-pressed]').forEach(function (item) {
      if (item.getAttribute('data-annotation-ready') === 'true') return;
      item.setAttribute('data-annotation-ready', 'true');
      item.addEventListener('click', function () { window.toggleAnnotation(item); });
    });
  }

  function initPracticeProgress() {
    qsa('[data-progress-tracker]').forEach(function (tracker) {
      var key = 'scholarsCompass:' + tracker.getAttribute('data-progress-tracker') + ':practice';
      var boxes = qsa('.progress-checkbox', tracker);
      var indicator = tracker.querySelector('#progressIndicator');
      var percentText = tracker.querySelector('#progressPercent');
      if (!boxes.length || !indicator || !percentText) return;
      var stored = storageGet(key, []);
      boxes.forEach(function (box, index) { box.checked = stored.indexOf(index) !== -1; });
      function update() {
        var completed = [];
        boxes.forEach(function (box, index) { if (box.checked) completed.push(index); });
        var percent = Math.round((completed.length / boxes.length) * 100);
        indicator.style.width = percent + '%';
        indicator.setAttribute('aria-valuemin', '0');
        indicator.setAttribute('aria-valuemax', '100');
        indicator.setAttribute('aria-valuenow', String(percent));
        indicator.setAttribute('role', 'progressbar');
        percentText.textContent = percent + '%';
        storageSet(key, completed);
      }
      boxes.forEach(function (box) { box.addEventListener('change', update); });
      update();
    });
  }

  function loadInteractiveTools() {
    if (document.querySelector('script[data-sc-interactive="1"]')) return;
    var scripts = qsa('script[src*="app.js"]');
    var appScript = scripts.length ? scripts[scripts.length - 1] : null;
    var src;
    try {
      src = appScript && appScript.src
        ? new URL('interactive-tools.js?v=2', appScript.src).href
        : ((window.location.pathname.indexOf('/1010/') !== -1 || window.location.pathname.indexOf('/1020/') !== -1)
          ? '../interactive-tools.js?v=2'
          : 'interactive-tools.js?v=2');
    } catch (err) {
      src = '../interactive-tools.js?v=2';
    }
    var script = document.createElement('script');
    script.src = src;
    script.async = false;
    script.setAttribute('data-sc-interactive', '1');
    document.head.appendChild(script);
  }

  ready(function () {
    initPageLandmarks();
    normalizeSharedCallouts();
    apply1010IndexOrder();
    normalize1010ChapterLinkLabels();
    buildChaptersNav();
    initSidebar();
    initThemeToggle();
    initBackToTop();
    initScrollHandlers();
    initSmoothAnchors();
    initSectionDisclosures();
    initAnnotationExamples();
    initPracticeProgress();
    loadInteractiveTools();
  });

})();
