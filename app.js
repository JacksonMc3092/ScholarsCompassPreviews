/* Scholar's Compass — global behavior (GitHub Pages static site)
   Phase A stabilization:
   - Theme toggle (persistent)
   - Back-to-top
   - Sidebar / hamburger
   - Scroll progress (top bars)
   - Chapters list (single array)
   - Quick-nav active highlight
   - Chapter section expand/collapse (toggleSection)
*/

(function () {
  'use strict';

    var CHAPTERS_1010 = [
    { href: 'chapter-1.html', icon: 'fas fa-highlighter', title: '1. Annotating: Reading Like a Writer', readingTime: '12 min' },
    { href: 'chapter-2.html', icon: 'fas fa-book-reader', title: '2. Active Reading: Reading With a Purpose', readingTime: '12 min' },
    { href: 'chapter-3.html', icon: 'fas fa-bullhorn', title: '3. Understanding Rhetoric: The Art of Persuasion', readingTime: '18 min' },
    { href: 'chapter-4.html', icon: 'fas fa-layer-group', title: '4. Values, Assumptions, and Ideology', readingTime: '14 min' },
    { href: 'chapter-5.html', icon: 'fas fa-pen-fancy', title: '5. Strategies for Getting Started', readingTime: '10 min' },
    { href: 'chapter-6.html', icon: 'fas fa-bullseye', title: '6. Crafting Powerful Thesis Statements', readingTime: '12 min' },
    { href: 'chapter-7.html', icon: 'fas fa-align-left', title: '7. Designing Effective Paragraphs', readingTime: '13 min' },
    { href: 'chapter-8.html', icon: 'fas fa-clipboard-list', title: '8. Summarizing Your Way to Synthesis', readingTime: '10 min' },
    { href: 'chapter-9.html', icon: 'fas fa-project-diagram', title: '9. Analysis and Synthesis', readingTime: '16 min' },
    { href: 'chapter-10.html', icon: 'fas fa-comments', title: '10. Argumentation: Joining the Academic Conversation', readingTime: '18 min' },
    { href: 'chapter-11.html', icon: 'fas fa-images', title: '11. Reading Visual and Digital Texts', readingTime: '12 min' },
    { href: 'chapter-12.html', icon: 'fas fa-clipboard-check', title: '12. Observation and Evidence Logs', readingTime: '12 min' },
    { href: 'chapter-13.html', icon: 'fas fa-search', title: '13. Finding and Evaluating Sources', readingTime: '14 min' },
    { href: 'chapter-14.html', icon: 'fas fa-quote-left', title: '14. Quoting, Paraphrasing, and Signal Phrases', readingTime: '12 min' },
    { href: 'chapter-15.html', icon: 'fas fa-link', title: '15. Using Sources in Your Argument', readingTime: '14 min' },
    { href: 'chapter-16.html', icon: 'fas fa-file-lines', title: '16. MLA and Formatting Survival Guide', readingTime: '14 min' },
    { href: 'chapter-17.html', icon: 'fas fa-people-arrows', title: '17. Peer Review and Giving Useful Feedback', readingTime: '12 min' },
    { href: 'chapter-18.html', icon: 'fas fa-route', title: '18. From Feedback to Revision Plan', readingTime: '10 min' },
    { href: 'chapter-19.html', icon: 'fas fa-pen-to-square', title: '19. Revision: From Draft to Final', readingTime: '12 min' }
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
    // fallback to body attribute if present
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

  function qs(sel) { return document.querySelector(sel); }
  function qsa(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }

  // ---- Chapter section expand/collapse
  // Many chapter pages use inline onclick="toggleSection(this)".
  // Provide a stable global implementation.
  window.toggleSection = function (headerEl) {
    if (!headerEl) return;
    var section = headerEl.closest ? headerEl.closest('.section') : null;
    if (!section) {
      var p = headerEl.parentElement;
      while (p && !(p.classList && p.classList.contains('section'))) p = p.parentElement;
      section = p;
    }
    if (!section) return;
    section.classList.toggle('active');
  };

  // ---- Theme
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
    if (isDark) document.body.classList.add('dark-mode');
    else document.body.classList.remove('dark-mode');

    localStorage.setItem('darkMode', isDark ? 'true' : 'false');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');

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

  // ---- Back-to-top
  function initBackToTop() {
    var btn = qs('#backToTop');
    if (!btn) return;
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ---- Sidebar
  function initSidebar() {
    var hamburger = qs('#hamburgerMenu');
    var sidebar = qs('#sidebar');
    var overlay = qs('#sidebarOverlay');
    var closeBtn = qs('#sidebarClose');

    if (!hamburger || !sidebar || !overlay) return;

    function openSidebar() {
      sidebar.classList.add('active');
      overlay.classList.add('active');
      hamburger.classList.add('active');
      document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
      sidebar.classList.remove('active');
      overlay.classList.remove('active');
      hamburger.classList.remove('active');
      document.body.style.overflow = '';
    }

    hamburger.addEventListener('click', openSidebar);
    if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
    overlay.addEventListener('click', closeSidebar);

    // Auto-close on mobile when selecting a chapter
    qsa('.sidebar-link[href*="chapter"]').forEach(function (a) {
      a.addEventListener('click', function () {
        if (window.innerWidth <= 768) closeSidebar();
      });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && sidebar.classList.contains('active')) closeSidebar();
    });

    // Touch swipe
    var touchStartX = 0;
    var touchEndX = 0;

    document.addEventListener('touchstart', function (e) {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    document.addEventListener('touchend', function (e) {
      touchEndX = e.changedTouches[0].screenX;
      var swipeThreshold = 100;
      var swipeDistance = touchEndX - touchStartX;
      if (Math.abs(swipeDistance) <= swipeThreshold) return;

      if (swipeDistance > 0 && touchStartX < 50) openSidebar();
      else if (swipeDistance < 0 && sidebar.classList.contains('active')) closeSidebar();
    }, { passive: true });
  }

  // ---- Chapters nav (single source of truth)
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

  // ---- Scroll progress + quick nav
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
      if (a.getAttribute('data-section') === activeId) a.classList.add('active');
      else a.classList.remove('active');
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
    if (back) {
      if (winScroll > 300) back.classList.add('visible');
      else back.classList.remove('visible');
    }

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

  // ---- Smooth anchors (quick-nav, in-page links)
  function initSmoothAnchors() {
    qsa('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var href = a.getAttribute('href');
        if (!href || href.length < 2) return;
        var target = qs(href);
        if (!target) return;

        e.preventDefault();
        var yOffset = -80;
        var y = target.getBoundingClientRect().top + window.pageYOffset + yOffset;
        window.scrollTo({ top: y, behavior: 'smooth' });
      });
    });
  }



  // ---- Lightweight helpers for chapter activities
  function setText(id, value) {
    var el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  window.toggleAnnotation = function (el) {
    if (el && el.classList) el.classList.toggle('active');
  };

  function checkedCount(selector) {
    return qsa(selector).filter(function (x) { return x.checked; }).length;
  }

  function initProgressCheckboxes() {
    qsa('.progress-checkbox, .skill-checkbox, .argument-checkbox, .sq3r-checkbox').forEach(function (box) {
      box.addEventListener('change', function () {
        window.updateProgress();
      });
    });
  }

  window.updateProgress = function () {
    var selector = '.progress-checkbox, .skill-checkbox, .argument-checkbox, .sq3r-checkbox, input[onchange*="updateProgress"]';
    var boxes = qsa(selector);
    if (!boxes.length) return;
    var pct = Math.round((checkedCount(selector) / boxes.length) * 100);
    var bar = qs('#progressIndicator');
    var label = qs('#progressPercent');
    if (bar) bar.style.width = pct + '%';
    if (label) label.textContent = pct + '%';
  };

  window.generateSandwich = function () {
    var top = (qs('#topBun') || {}).value || '';
    var meat = (qs('#meat') || {}).value || '';
    var bottom = (qs('#bottomBun') || {}).value || '';
    var out = qs('#sandwichOutput');
    if (out) out.textContent = [top, meat, bottom].filter(Boolean).join('\n\n');
  };

  window.copySandwich = function () {
    var out = qs('#sandwichOutput');
    if (!out) return;
    navigator.clipboard && navigator.clipboard.writeText ? navigator.clipboard.writeText(out.textContent) : null;
  };

  window.generateQuoteSandwich = function () {
    var a = (qs('#frontLoad') || {}).value || '';
    var b = (qs('#quoteText') || {}).value || '';
    var c = (qs('#quoteAnalysis') || {}).value || '';
    var out = qs('#quoteOutput') || qs('#generatedParagraph');
    if (out) out.textContent = [a, b, c].filter(Boolean).join('\n\n');
  };

  window.generatePIEParagraph = function () {
    var point = (qs('#point') || qs('#mainPoint') || {}).value || '';
    var info = (qs('#information') || qs('#evidence') || {}).value || '';
    var expl = (qs('#explanation') || qs('#analysis') || {}).value || '';
    var out = qs('#pieOutput') || qs('#paragraphOutput');
    if (out) out.textContent = [point, info, expl].filter(Boolean).join('\n\n');
  };

  window.analyzeThesis = function () {
    var t = ((qs('#templatePractice') || {}).value || '').trim();
    var out = qs('#thesisAnalysis') || qs('#analysisResult');
    if (out) out.textContent = t.length < 20 ? 'This thesis may need more specificity and an arguable claim.' : 'Now check: is it specific, arguable, evidence-based, and appropriate for the assignment length?';
  };

  window.generateThesis = function () {
    var topic = ((qs('#topic') || {}).value || '').trim();
    var problem = ((qs('#problem') || {}).value || '').trim();
    var thesis = qs('#thesis');
    if (thesis && !thesis.value) thesis.value = topic && problem ? 'Because ' + problem + ', ' + topic + ' matters because...' : 'Although..., I argue that... because...';
  };

  window.checkAnswer = function () { setText('answerFeedback', 'Check whether your answer explains why the choice matters, not just what the source says.'); };
  window.checkParaphrase = function () { setText('paraphraseFeedback', 'A strong paraphrase changes sentence structure and wording while preserving the original meaning and citing the source.'); };
  window.showBloomDetails = function (level) { setText('bloomDetails', 'Focus on the level you selected: ' + level + '. In essays, move beyond remembering toward analyzing, evaluating, and creating a claim.'); };
  window.changeConversation = function () { setText('conversationText', 'Example: Some readers argue X. Others complicate that view by pointing to Y. Your task is to enter that conversation with a focused claim.'); };
  window.selectPosition = function (pos) { setText('positionFeedback', 'Selected position: ' + pos + '. Now explain why your position is more specific than simple agreement or disagreement.'); };
  window.savePosition = function () { setText('positionStatus', 'Position saved for this page session.'); };
  window.clearPosition = function () { qsa('textarea').forEach(function (t) { if (!t.classList.contains('freewriting-textarea')) t.value = ''; }); setText('positionStatus', 'Cleared.'); };
  window.generateCounterargument = function () {
    var claim = ((qs('#mainClaim') || {}).value || '').trim();
    var counter = ((qs('#counterargument') || {}).value || '').trim();
    var response = qs('#response');
    if (response && !response.value) response.value = 'While ' + (counter || 'some readers may disagree') + ', ' + (claim || 'my claim') + ' still matters because...';
  };

  var timerId = null, timerRemaining = 300;
  window.startTimer = function (seconds) {
    if (seconds) timerRemaining = seconds;
    clearInterval(timerId);
    timerId = setInterval(function () {
      timerRemaining -= 1;
      var display = qs('#timerDisplay');
      if (display) {
        var m = Math.floor(timerRemaining / 60), s = timerRemaining % 60;
        display.textContent = m + ':' + String(s).padStart(2, '0');
      }
      if (timerRemaining <= 0) clearInterval(timerId);
    }, 1000);
  };
  window.pauseTimer = function () { clearInterval(timerId); };
  window.resetTimer = function () { clearInterval(timerId); timerRemaining = 300; var d = qs('#timerDisplay'); if (d) d.textContent = '5:00'; };
  window.saveFreewrite = function () { setText('freewriteStatus', 'Freewrite saved for this page session.'); };
  window.generateQuestion = function () {
    var qsList = ['What pattern do I notice?', 'Why does this matter?', 'Who benefits from this?', 'What assumption is being made?', 'What evidence would prove this?'];
    setText('currentQuestion', qsList[Math.floor(Math.random() * qsList.length)]);
  };
  window.saveQuestion = function () {
    var q = (qs('#currentQuestion') || {}).textContent || '';
    var list = qs('#savedQuestions');
    if (list && q) { var li = document.createElement('li'); li.textContent = q; list.appendChild(li); }
  };
  window.addClusterNode = window.clearCluster = window.saveCluster = window.loadCluster = window.addListItem = window.saveList = window.clearList = window.addOutlineItem = window.saveOutline = window.startChallenge = function () {};

  function initQuickDraftTools() {
    qsa('.copy-draft-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var wrap = btn.closest('.writer-tool') || document;
        var draft = wrap.querySelector('.quick-draft');
        if (draft && navigator.clipboard) navigator.clipboard.writeText(draft.value || '');
      });
    });
    qsa('.clear-draft-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var wrap = btn.closest('.writer-tool') || document;
        var draft = wrap.querySelector('.quick-draft');
        if (draft) draft.value = '';
      });
    });
  }

  ready(function () {
    buildChaptersNav();
    initSidebar();
    initThemeToggle();
    initBackToTop();
    initScrollHandlers();
    initSmoothAnchors();
    initProgressCheckboxes();
    initQuickDraftTools();
  });

})();
