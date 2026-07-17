/* Chapter 12 interactive tools: Finding and Evaluating Sources */
(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  function qs(selector, root) {
    return (root || document).querySelector(selector);
  }

  function qsa(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function setStatus(element, message) {
    if (!element) return;
    element.textContent = message;
    element.setAttribute('role', 'status');
    element.setAttribute('aria-live', 'polite');
  }

  function safeGet(key, fallback) {
    try {
      var raw = localStorage.getItem(key);
      return raw === null ? fallback : JSON.parse(raw);
    } catch (error) {
      return fallback;
    }
  }

  function safeSet(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      return false;
    }
  }

  function safeRemove(key) {
    try { localStorage.removeItem(key); } catch (error) {}
  }

  function quoteTerm(term) {
    var trimmed = String(term || '').trim();
    if (!trimmed) return '';
    return /\s/.test(trimmed) ? '"' + trimmed.replace(/"/g, '') + '"' : trimmed;
  }

  function alternatives(value) {
    return String(value || '')
      .split(',')
      .map(function (item) { return item.trim(); })
      .filter(Boolean);
  }

  function initKeywordBuilder() {
    var button = qs('#buildKeywords');
    var output = qs('#keywordOutput');
    if (!button || !output) return;

    button.addEventListener('click', function () {
      var concepts = qsa('.ch12-concept-row').map(function (row) {
        var main = qs('.ch12-main-concept', row);
        var related = qs('.ch12-related-terms', row);
        return {
          main: main ? main.value.trim() : '',
          related: related ? alternatives(related.value) : []
        };
      }).filter(function (item) { return item.main; });

      output.innerHTML = '';
      if (concepts.length < 2) {
        setStatus(output, 'Enter at least two main concepts before building search strings.');
        return;
      }

      var queries = [];
      queries.push(concepts.map(function (item) { return quoteTerm(item.main); }).join(' AND '));

      var alternateQuery = concepts.map(function (item, index) {
        var choice = item.related[index % Math.max(1, item.related.length)];
        return quoteTerm(choice || item.main);
      }).join(' AND ');
      if (alternateQuery !== queries[0]) queries.push(alternateQuery);

      if (concepts[0].related.length || concepts[1].related.length) {
        var firstGroup = [concepts[0].main].concat(concepts[0].related).slice(0, 4).map(quoteTerm).join(' OR ');
        var secondGroup = [concepts[1].main].concat(concepts[1].related).slice(0, 4).map(quoteTerm).join(' OR ');
        var grouped = '(' + firstGroup + ') AND (' + secondGroup + ')';
        if (concepts[2]) grouped += ' AND ' + quoteTerm(concepts[2].main);
        queries.push(grouped);
      }

      var heading = document.createElement('strong');
      heading.textContent = 'Search strings to try:';
      output.appendChild(heading);

      queries.forEach(function (query) {
        var line = document.createElement('div');
        line.className = 'ch12-search-string';
        var code = document.createElement('code');
        code.textContent = query;
        line.appendChild(code);
        output.appendChild(line);
      });

      var note = document.createElement('p');
      note.textContent = 'Use these as starting points. Scan the results for better vocabulary, then revise the search.';
      output.appendChild(note);
      output.setAttribute('role', 'status');
      output.setAttribute('aria-live', 'polite');
    });
  }

  var ROUTES = {
    scholarship: {
      title: 'Begin with a library database or Google Scholar.',
      detail: 'Use subject terms, abstracts, date filters, references, Cited by, and Related articles to enter the scholarly conversation.'
    },
    current: {
      title: 'Begin with credible journalism or a newspaper database.',
      detail: 'For a developing event, compare several reports and trace statistics, documents, and quoted claims toward their original sources.'
    },
    official: {
      title: 'Begin with the responsible government or institutional source.',
      detail: 'Use the original law, policy, dataset, court record, agency report, or official statement, then add independent analysis when your claim requires evaluation.'
    },
    primary: {
      title: 'Begin with the original primary source.',
      detail: 'Locate the speech, advertisement, social post, video, policy, interview, artifact, or dataset you plan to analyze.'
    },
    professional: {
      title: 'Begin with a trade or professional publication.',
      detail: 'Look for current practices, regulations, case studies, workplace perspectives, and field-specific vocabulary. Investigate sponsorship and evidence.'
    },
    background: {
      title: 'Begin with a strong reference source or research guide.',
      detail: 'Use the overview to learn vocabulary, names, dates, and major debates, then follow its references into more specialized sources.'
    }
  };

  function initRouteChooser() {
    var select = qs('#routeNeed');
    var button = qs('#chooseRoute');
    var output = qs('#routeOutput');
    if (!select || !button || !output) return;

    button.addEventListener('click', function () {
      var route = ROUTES[select.value];
      output.innerHTML = '';
      if (!route) {
        setStatus(output, 'Choose a research need first.');
        return;
      }
      var strong = document.createElement('strong');
      strong.textContent = route.title;
      var paragraph = document.createElement('p');
      paragraph.textContent = route.detail;
      output.appendChild(strong);
      output.appendChild(paragraph);
      output.setAttribute('role', 'status');
      output.setAttribute('aria-live', 'polite');
    });
  }

  function initTriage() {
    var button = qs('#checkTriage');
    var summary = qs('#triageSummary');
    if (!button || !summary) return;

    button.addEventListener('click', function () {
      var cards = qsa('.ch12-source-card[data-recommended]');
      var answered = 0;
      var aligned = 0;

      cards.forEach(function (card) {
        var selected = qs('input[type="radio"]:checked', card);
        var feedback = qs('.ch12-decision-feedback', card);
        if (!selected) {
          if (feedback) feedback.textContent = 'Choose a decision, then compare your reasoning with the guidance.';
          return;
        }

        answered += 1;
        var recommended = card.getAttribute('data-recommended');
        var reasoning = card.getAttribute('data-reasoning') || '';
        var matches = selected.value === recommended;
        if (matches) aligned += 1;
        if (feedback) {
          feedback.textContent = (matches ? 'A strong decision. ' : 'A defensible answer may differ, but consider this guidance: ') + reasoning;
          feedback.setAttribute('role', 'status');
        }
      });

      if (!answered) {
        setStatus(summary, 'Choose a decision for at least one source card.');
        return;
      }

      setStatus(summary, 'You completed ' + answered + ' source decision' + (answered === 1 ? '' : 's') + '. ' + aligned + ' matched the suggested category. Your explanation matters more than chasing a perfect score.');
    });
  }

  var LOG_KEY = 'scholarsCompass:chapter-12:source-log';
  var LOG_FIELDS = [
    'author', 'title', 'container', 'date', 'locator', 'type', 'lane',
    'terms', 'summary', 'evidence', 'location', 'credibility', 'use',
    'limits', 'mla'
  ];

  function collectLog() {
    var data = {};
    LOG_FIELDS.forEach(function (name) {
      var field = qs('[data-source-log="' + name + '"]');
      data[name] = field ? field.value.trim() : '';
    });
    return data;
  }

  function fillLog(data) {
    LOG_FIELDS.forEach(function (name) {
      var field = qs('[data-source-log="' + name + '"]');
      if (field) field.value = data && data[name] ? data[name] : '';
    });
  }

  function logAsText(data) {
    var labels = {
      author: 'Author or organization',
      title: 'Title',
      container: 'Publication or container',
      date: 'Date',
      locator: 'Stable URL, DOI, or permalink',
      type: 'Source type',
      lane: 'Search lane',
      terms: 'Search terms',
      summary: 'Summary',
      evidence: 'Important evidence or passage',
      location: 'Page, paragraph, section, or timestamp',
      credibility: 'Credibility notes',
      use: 'How I will use this source',
      limits: 'Questions, limits, or claims to check',
      mla: 'Draft MLA Works Cited entry'
    };
    return LOG_FIELDS.map(function (name) {
      return labels[name] + ': ' + (data[name] || '');
    }).join('\n\n');
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var area = document.createElement('textarea');
      area.value = text;
      area.style.position = 'fixed';
      area.style.opacity = '0';
      document.body.appendChild(area);
      area.select();
      try {
        document.execCommand('copy');
        area.remove();
        resolve();
      } catch (error) {
        area.remove();
        reject(error);
      }
    });
  }

  function initSourceLog() {
    var save = qs('#saveSourceLog');
    var load = qs('#loadSourceLog');
    var clear = qs('#clearSourceLog');
    var copy = qs('#copySourceLog');
    var status = qs('#sourceLogStatus');
    if (!save || !load || !clear || !copy || !status) return;

    save.addEventListener('click', function () {
      var data = collectLog();
      var usefulFields = data.title || data.author || data.summary || data.use;
      if (!usefulFields) {
        setStatus(status, 'Add at least a title, author, summary, or planned use before saving.');
        return;
      }
      var saved = safeSet(LOG_KEY, data);
      setStatus(status, saved ? 'Source-log entry saved in this browser.' : 'The browser blocked local saving. Use Copy Entry to preserve your work.');
    });

    load.addEventListener('click', function () {
      var data = safeGet(LOG_KEY, null);
      if (!data) {
        setStatus(status, 'No saved Chapter 12 source-log entry was found in this browser.');
        return;
      }
      fillLog(data);
      setStatus(status, 'Saved source-log entry loaded.');
    });

    clear.addEventListener('click', function () {
      fillLog({});
      safeRemove(LOG_KEY);
      setStatus(status, 'Source-log entry cleared from the page and this browser.');
      var first = qs('[data-source-log="author"]');
      if (first) first.focus();
    });

    copy.addEventListener('click', function () {
      var text = logAsText(collectLog());
      copyText(text).then(function () {
        setStatus(status, 'Source-log entry copied to the clipboard.');
      }).catch(function () {
        setStatus(status, 'The browser blocked copying. Select the fields and copy them manually.');
      });
    });
  }

  ready(function () {
    initKeywordBuilder();
    initRouteChooser();
    initTriage();
    initSourceLog();
  });
})();
