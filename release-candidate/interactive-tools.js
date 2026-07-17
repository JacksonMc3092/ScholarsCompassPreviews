/* Scholar's Compass chapter-specific interactive tools. */
(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }
  function qs(sel, root) { return (root || document).querySelector(sel); }
  function qsa(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function currentFile() {
    var f = (window.location.pathname || '').split('/').pop();
    return (f && f.trim()) ? f : 'index.html';
  }
  function storageGet(key, fallback) {
    try {
      var raw = localStorage.getItem(key);
      return raw === null ? fallback : JSON.parse(raw);
    } catch (err) { return fallback; }
  }
  function storageSet(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); return true; }
    catch (err) { return false; }
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

  if (typeof window.toggleAnnotation !== 'function') {
    window.toggleAnnotation = function (item) {
      if (!item) return;
      var pressed = item.getAttribute('aria-pressed') === 'true' || item.classList.contains('active');
      item.setAttribute('aria-pressed', pressed ? 'false' : 'true');
      item.classList.toggle('active', !pressed);
    };
  }

  function drawClusterConnections() {
    var container = qs('#clusterDiagram');
    if (!container) return;
    qsa('.cluster-connection', container).forEach(function (line) { line.remove(); });
    var center = qs('.cluster-center', container);
    if (!center) return;
    var cLeft = center.offsetLeft + center.offsetWidth / 2;
    var cTop = center.offsetTop + center.offsetHeight / 2;
    qsa('.cluster-node:not(.cluster-center)', container).forEach(function (node) {
      var nLeft = node.offsetLeft + node.offsetWidth / 2;
      var nTop = node.offsetTop + node.offsetHeight / 2;
      var dx = nLeft - cLeft;
      var dy = nTop - cTop;
      var line = document.createElement('div');
      line.className = 'cluster-connection';
      line.style.left = cLeft + 'px';
      line.style.top = cTop + 'px';
      line.style.width = Math.sqrt(dx * dx + dy * dy) + 'px';
      line.style.transform = 'rotate(' + Math.atan2(dy, dx) + 'rad)';
      container.insertBefore(line, container.firstChild);
    });
  }

  function makeClusterNodeDraggable(node) {
    if (!node || node.getAttribute('data-drag-ready') === 'true') return;
    node.setAttribute('data-drag-ready', 'true');
    var dragging = false;
    var startX = 0;
    var startY = 0;
    var startLeft = 0;
    var startTop = 0;

    node.addEventListener('pointerdown', function (event) {
      if (event.target && String(event.target.tagName).toLowerCase() === 'input') return;
      dragging = true;
      startX = event.clientX;
      startY = event.clientY;
      startLeft = node.offsetLeft;
      startTop = node.offsetTop;
      try { node.setPointerCapture(event.pointerId); } catch (err) {}
    });
    node.addEventListener('pointermove', function (event) {
      if (!dragging) return;
      var container = node.parentElement;
      var maxLeft = Math.max(0, container.clientWidth - node.offsetWidth);
      var maxTop = Math.max(0, container.clientHeight - node.offsetHeight);
      node.style.left = Math.min(maxLeft, Math.max(0, startLeft + event.clientX - startX)) + 'px';
      node.style.top = Math.min(maxTop, Math.max(0, startTop + event.clientY - startY)) + 'px';
      drawClusterConnections();
    });
    node.addEventListener('pointerup', function (event) {
      dragging = false;
      try { node.releasePointerCapture(event.pointerId); } catch (err) {}
    });
    node.addEventListener('dblclick', function () { window.editNode(node); });
  }

  function createClusterNode(text, left, top, isCenter) {
    var container = qs('#clusterDiagram');
    if (!container) return null;
    var node = document.createElement('div');
    node.className = 'cluster-node' + (isCenter ? ' cluster-center' : '');
    node.style.left = left + 'px';
    node.style.top = top + 'px';
    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'editable-node';
    input.value = text || (isCenter ? 'Main Topic' : 'New Idea');
    input.addEventListener('blur', function () { window.updateNodeText(input); });
    input.addEventListener('keypress', function (event) { window.handleKeyPress(event, input); });
    node.appendChild(input);
    container.appendChild(node);
    makeClusterNodeDraggable(node);
    return node;
  }

  window.addClusterNode = function () {
    var container = qs('#clusterDiagram');
    if (!container) return;
    var count = qsa('.cluster-node:not(.cluster-center)', container).length;
    var width = Math.max(320, container.clientWidth || 600);
    var height = Math.max(300, container.clientHeight || 400);
    var left = 20 + ((count * 113) % Math.max(120, width - 150));
    var top = 25 + ((count * 79) % Math.max(120, height - 90));
    var node = createClusterNode('New Idea', left, top, false);
    drawClusterConnections();
    if (node) window.editNode(node);
  };

  window.clearCluster = function () {
    var container = qs('#clusterDiagram');
    if (!container) return;
    qsa('.cluster-node:not(.cluster-center)', container).forEach(function (node) { node.remove(); });
    var centerInput = qs('.cluster-center .editable-node', container);
    if (centerInput) centerInput.value = 'Main Topic';
    drawClusterConnections();
    storageRemove('scholarsCompass:chapter-3:cluster');
    setToolStatus(container, 'Cluster cleared.', 'success');
  };

  window.saveCluster = function () {
    var container = qs('#clusterDiagram');
    if (!container) return;
    var data = qsa('.cluster-node', container).map(function (node) {
      var input = qs('.editable-node', node);
      return {
        text: input ? input.value.trim() : node.textContent.trim(),
        left: node.offsetLeft,
        top: node.offsetTop,
        center: node.classList.contains('cluster-center')
      };
    });
    storageSet('scholarsCompass:chapter-3:cluster', data);
    setToolStatus(container, 'Cluster saved in this browser.', 'success');
  };

  window.loadCluster = function () {
    var container = qs('#clusterDiagram');
    if (!container) return;
    var data = storageGet('scholarsCompass:chapter-3:cluster', null);
    if (!data || !data.length) {
      setToolStatus(container, 'No saved cluster was found in this browser.', 'error');
      return;
    }
    qsa('.cluster-node', container).forEach(function (node) { node.remove(); });
    data.forEach(function (item) {
      createClusterNode(item.text, Number(item.left) || 0, Number(item.top) || 0, !!item.center);
    });
    if (!qs('.cluster-center', container)) createClusterNode('Main Topic', 190, 180, true);
    drawClusterConnections();
    setToolStatus(container, 'Saved cluster loaded.', 'success');
  };

  window.editNode = function (node) {
    var input = node ? qs('.editable-node', node) : null;
    if (!input) return;
    input.focus();
    input.select();
  };

  window.updateNodeText = function (input) {
    if (!input) return;
    if (!input.value.trim()) input.value = 'Idea';
    drawClusterConnections();
  };

  window.handleKeyPress = function (event, input) {
    if (event && event.key === 'Enter') {
      event.preventDefault();
      if (input && input.blur) input.blur();
    }
  };

  var draggedListItem = null;
  function prepareListItem(item) {
    if (!item || item.getAttribute('data-list-ready') === 'true') return;
    item.setAttribute('data-list-ready', 'true');
    item.setAttribute('draggable', 'true');
    item.setAttribute('tabindex', '0');
    item.setAttribute('role', 'button');
    item.setAttribute('aria-label', 'Move idea between columns. Press Delete to remove.');
    item.addEventListener('dragstart', function () {
      draggedListItem = item;
      item.classList.add('dragging');
    });
    item.addEventListener('dragend', function () {
      item.classList.remove('dragging');
      draggedListItem = null;
    });
    item.addEventListener('keydown', function (event) {
      if (event.key === 'Delete' || event.key === 'Backspace') {
        event.preventDefault();
        item.remove();
      } else if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        var target = item.parentElement && item.parentElement.id === 'ideaList' ? qs('#groupedIdeas') : qs('#ideaList');
        if (target) target.appendChild(item);
      }
    });
  }

  function createListItem(text, target) {
    var item = document.createElement('div');
    item.className = 'list-item';
    item.textContent = text;
    prepareListItem(item);
    (target || qs('#ideaList')).appendChild(item);
    return item;
  }

  window.addListItem = function () {
    var input = qs('#listItemInput');
    var target = qs('#ideaList');
    if (!input || !target) return;
    var text = input.value.trim();
    if (!text) {
      setToolStatus(input, 'Type an idea before adding it.', 'error');
      input.focus();
      return;
    }
    createListItem(text, target);
    input.value = '';
    input.focus();
  };

  window.handleListKeyPress = function (event) {
    if (event && event.key === 'Enter') {
      event.preventDefault();
      window.addListItem();
    }
  };

  window.saveList = function () {
    var data = {
      ideas: qsa('#ideaList .list-item').map(function (item) { return item.textContent.trim(); }),
      grouped: qsa('#groupedIdeas .list-item').map(function (item) { return item.textContent.trim(); })
    };
    storageSet('scholarsCompass:chapter-3:list', data);
    setToolStatus(qs('#ideaList'), 'List saved in this browser.', 'success');
  };

  window.clearList = function () {
    qsa('#ideaList .list-item, #groupedIdeas .list-item').forEach(function (item) { item.remove(); });
    storageRemove('scholarsCompass:chapter-3:list');
    setToolStatus(qs('#ideaList'), 'List cleared.', 'success');
  };

  function roman(num) {
    var map = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'];
    return map[num - 1] || String(num);
  }

  function prepareOutlineItem(item) {
    if (!item || item.getAttribute('data-outline-ready') === 'true') return;
    item.setAttribute('data-outline-ready', 'true');
    item.setAttribute('contenteditable', 'true');
    item.setAttribute('role', 'textbox');
    item.setAttribute('aria-label', 'Editable outline item');
  }

  window.addOutlineItem = function (level) {
    var container = qs('#outlineContainer');
    if (!container) return;
    level = Math.max(1, Math.min(3, Number(level) || 1));
    var count = qsa('.outline-level-' + level, container).length + 1;
    var prefixes = level === 1 ? roman(count) + '. ' : (level === 2 ? String.fromCharCode(64 + Math.min(26, count)) + '. ' : count + '. ');
    var labels = { 1: 'Main Point', 2: 'Supporting Point', 3: 'Detail' };
    var item = document.createElement('div');
    item.className = 'outline-item outline-level-' + level;
    item.textContent = prefixes + labels[level];
    prepareOutlineItem(item);
    container.appendChild(item);
    item.focus();
    try {
      var range = document.createRange();
      range.selectNodeContents(item);
      var selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
    } catch (err) {}
  };

  window.saveOutline = function () {
    var container = qs('#outlineContainer');
    if (!container) return;
    var data = qsa('.outline-item', container).map(function (item) {
      var level = item.classList.contains('outline-level-3') ? 3 : (item.classList.contains('outline-level-2') ? 2 : 1);
      return { level: level, text: item.textContent.trim() };
    });
    storageSet('scholarsCompass:chapter-3:outline', data);
    setToolStatus(container, 'Outline saved in this browser.', 'success');
  };

  var timerInterval = null;
  var timerInitial = 300;
  var timerRemaining = 300;

  function updateTimerDisplay() {
    var display = qs('#freewriteTimer');
    if (!display) return;
    var minutes = Math.floor(Math.max(0, timerRemaining) / 60);
    var seconds = Math.max(0, timerRemaining) % 60;
    display.textContent = String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
  }

  window.startTimer = function (seconds) {
    if (!qs('#freewriteTimer')) return;
    if (typeof seconds === 'number' && isFinite(seconds) && seconds > 0) {
      timerInitial = Math.floor(seconds);
      timerRemaining = timerInitial;
    } else if (timerRemaining <= 0) {
      timerRemaining = timerInitial;
    }
    if (timerInterval) clearInterval(timerInterval);
    updateTimerDisplay();
    timerInterval = window.setInterval(function () {
      timerRemaining -= 1;
      updateTimerDisplay();
      if (timerRemaining <= 0) {
        clearInterval(timerInterval);
        timerInterval = null;
        setToolStatus(qs('#freewriteTimer'), 'Time is up. Save what you wrote before moving on.', 'success');
      }
    }, 1000);
  };

  window.pauseTimer = function () {
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = null;
    setToolStatus(qs('#freewriteTimer'), 'Timer paused.', 'info');
  };

  window.resetTimer = function () {
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = null;
    timerRemaining = timerInitial;
    updateTimerDisplay();
    setToolStatus(qs('#freewriteTimer'), 'Timer reset.', 'info');
  };

  window.saveFreewrite = function () {
    var field = qs('#freewriteText');
    if (!field) return;
    storageSet('scholarsCompass:chapter-3:freewrite', field.value);
    setToolStatus(field, 'Freewrite saved in this browser.', 'success');
  };

  var QUESTION_PROMPTS = [
    'What is the most important problem connected to this topic?',
    'Who is most affected by this topic, and how?',
    'What do people commonly assume about this topic?',
    'What has changed about this topic over time?',
    'What evidence would help you answer your biggest question?',
    'Where do experts or stakeholders disagree?',
    'What specific example could make this topic concrete?',
    'Why does this topic matter now?',
    'What causes this issue, and what effects follow?',
    'What would a skeptical reader want you to explain?'
  ];
  var questionIndex = -1;

  window.generateQuestion = function () {
    var display = qs('#questionDisplay');
    if (!display) return;
    questionIndex = (questionIndex + 1) % QUESTION_PROMPTS.length;
    display.textContent = QUESTION_PROMPTS[questionIndex];
    display.setAttribute('aria-live', 'polite');
  };

  function renderSavedQuestions() {
    var list = qs('#savedQuestions');
    if (!list) return;
    list.innerHTML = '';
    storageGet('scholarsCompass:chapter-3:questions', []).forEach(function (text) {
      var li = document.createElement('li');
      li.textContent = text;
      list.appendChild(li);
    });
  }

  window.saveQuestion = function () {
    var display = qs('#questionDisplay');
    if (!display) return;
    var text = display.textContent.trim();
    if (!text || text.indexOf('Generate Question') !== -1) {
      setToolStatus(display, 'Generate a question before saving it.', 'error');
      return;
    }
    var questions = storageGet('scholarsCompass:chapter-3:questions', []);
    if (questions.indexOf(text) === -1) questions.push(text);
    storageSet('scholarsCompass:chapter-3:questions', questions);
    renderSavedQuestions();
    setToolStatus(display, 'Question saved.', 'success');
  };

  window.startChallenge = function () {
    var topic = qs('#challengeTopic');
    var results = qs('#challengeResults');
    if (!topic || !results) return;
    var selected = qsa('input[name="technique"]:checked').map(function (box) { return box.value; });
    if (!topic.value.trim()) {
      setToolStatus(topic, 'Enter a specific writing topic first.', 'error');
      topic.focus();
      return;
    }
    if (selected.length < 2) {
      setToolStatus(topic, 'Choose at least two pre-writing techniques to compare.', 'error');
      return;
    }
    results.style.display = 'block';
    var heading = qs('h4', results);
    if (heading) heading.textContent = 'Challenge: ' + topic.value.trim();
    var p = qs('p', results);
    if (p) p.textContent = 'Try ' + selected.join(' and ') + '. Then use the box below to compare which method generated more useful ideas and why.';
    var field = qs('textarea', results);
    if (field) field.focus();
    setToolStatus(topic, 'Challenge started. Compare the two methods after you try them.', 'success');
  };

  function initChapter3Tools() {
    var cluster = qs('#clusterDiagram');
    if (cluster) {
      qsa('.cluster-node', cluster).forEach(makeClusterNodeDraggable);
      drawClusterConnections();
      window.addEventListener('resize', drawClusterConnections);
    }

    qsa('.drop-zone').forEach(function (zone) {
      zone.addEventListener('dragover', function (event) {
        event.preventDefault();
        zone.classList.add('drag-over');
      });
      zone.addEventListener('dragleave', function () { zone.classList.remove('drag-over'); });
      zone.addEventListener('drop', function (event) {
        event.preventDefault();
        zone.classList.remove('drag-over');
        if (draggedListItem) zone.appendChild(draggedListItem);
      });
    });
    qsa('.list-item').forEach(prepareListItem);
    var savedList = storageGet('scholarsCompass:chapter-3:list', null);
    if (savedList && !qsa('#ideaList .list-item, #groupedIdeas .list-item').length) {
      (savedList.ideas || []).forEach(function (text) { createListItem(text, qs('#ideaList')); });
      (savedList.grouped || []).forEach(function (text) { createListItem(text, qs('#groupedIdeas')); });
    }

    var outline = qs('#outlineContainer');
    if (outline) {
      var savedOutline = storageGet('scholarsCompass:chapter-3:outline', null);
      if (savedOutline && savedOutline.length) {
        outline.innerHTML = '';
        savedOutline.forEach(function (item) {
          var div = document.createElement('div');
          div.className = 'outline-item outline-level-' + item.level;
          div.textContent = item.text;
          outline.appendChild(div);
        });
      }
      qsa('.outline-item', outline).forEach(prepareOutlineItem);
    }

    var freewrite = qs('#freewriteText');
    if (freewrite) {
      var saved = storageGet('scholarsCompass:chapter-3:freewrite', '');
      if (saved && !freewrite.value) freewrite.value = saved;
      updateTimerDisplay();
    }
    renderSavedQuestions();
  }

  var CONVERSATIONS = [
    [
      ['Original Claim', 'Social media has primarily negative effects on mental health.'],
      ['Response', 'While there are risks, social media also provides valuable support communities.'],
      ['Counterargument', 'Those benefits may not outweigh documented harms to adolescent development.']
    ],
    [
      ['Original Claim', 'College courses should eliminate traditional exams.'],
      ['Response', 'Projects may demonstrate applied learning more effectively than timed tests.'],
      ['Counterargument', 'Some exams still measure foundational knowledge efficiently and consistently.']
    ],
    [
      ['Original Claim', 'Remote work improves employee productivity.'],
      ['Response', 'Flexible schedules can reduce commuting stress and increase focused work time.'],
      ['Counterargument', 'Collaboration and mentoring may become harder when teams rarely share a physical space.']
    ]
  ];
  var conversationIndex = 0;

  window.changeConversation = function () {
    var viz = qs('#conversationViz');
    if (!viz) return;
    conversationIndex = (conversationIndex + 1) % CONVERSATIONS.length;
    var bubbles = qsa('.conversation-bubble', viz);
    CONVERSATIONS[conversationIndex].forEach(function (entry, index) {
      if (!bubbles[index]) return;
      bubbles[index].innerHTML = '';
      var strong = document.createElement('strong');
      strong.textContent = entry[0] + ': ';
      bubbles[index].appendChild(strong);
      bubbles[index].appendChild(document.createTextNode('“' + entry[1] + '”'));
    });
  };

  var POSITION_EXPLANATIONS = {
    agree: ['Agree', 'Build on an existing claim by adding evidence, a new example, or a perspective the original writer did not fully develop.'],
    disagree: ['Disagree', 'Challenge the claim with counterevidence, a different interpretation, or a problem in the writer’s reasoning.'],
    complicate: ['Complicate', 'Acknowledge what the claim gets right while showing that the issue changes across contexts, groups, or conditions.']
  };

  window.selectPosition = function (type) {
    var info = POSITION_EXPLANATIONS[type];
    var explanation = qs('#positionExplanation');
    if (!info || !explanation) return;
    qsa('.position-option').forEach(function (option) {
      var selected = option.classList.contains('position-' + type);
      option.classList.toggle('selected', selected);
      option.setAttribute('aria-pressed', selected ? 'true' : 'false');
    });
    explanation.innerHTML = '';
    var h = document.createElement('h4');
    h.textContent = info[0];
    var p = document.createElement('p');
    p.textContent = info[1];
    explanation.appendChild(h);
    explanation.appendChild(p);
  };

  function positionTextarea() {
    var button = qs('button[onclick="savePosition()"]');
    var tool = button ? closestTool(button) : null;
    return tool ? qs('textarea', tool) : null;
  }

  window.savePosition = function () {
    var field = positionTextarea();
    if (!field || !field.value.trim()) {
      setToolStatus(field || qs('#positionExplanation'), 'Write a position before saving it.', 'error');
      return;
    }
    storageSet('scholarsCompass:chapter-5:position', field.value);
    setToolStatus(field, 'Position saved in this browser.', 'success');
  };

  window.clearPosition = function () {
    var field = positionTextarea();
    if (!field) return;
    field.value = '';
    storageRemove('scholarsCompass:chapter-5:position');
    setToolStatus(field, 'Position cleared.', 'success');
    field.focus();
  };

  window.generateCounterargument = function () {
    var claim = qs('#mainClaim');
    var counter = qs('#counterargument');
    var responseType = qs('#responseType');
    var response = qs('#response');
    var output = qs('#argumentOutput');
    if (!claim || !counter || !responseType || !response || !output) return;
    if (!claim.value.trim() || !counter.value.trim() || !responseType.value || !response.value.trim()) {
      setToolStatus(output, 'Complete the claim, counterargument, response strategy, and response fields.', 'error');
      return;
    }
    var labels = {
      acknowledge: 'Acknowledging the concern',
      refute: 'Refuting with stronger evidence',
      redefine: 'Refining the terms or scope',
      concede: 'Conceding part of the point'
    };
    output.textContent = 'Counterargument: ' + counter.value.trim() + ' ' + labels[responseType.value] + ', the response is: ' + response.value.trim() + ' This response supports the main claim: ' + claim.value.trim();
    setToolStatus(output, 'Response generated. Revise the wording so it matches your own voice.', 'success');
  };

  function initChapter5Tools() {
    qsa('.position-option').forEach(function (option) {
      option.setAttribute('role', 'button');
      option.setAttribute('tabindex', '0');
      option.setAttribute('aria-pressed', 'false');
      option.addEventListener('keydown', function (event) {
        if (event.key !== 'Enter' && event.key !== ' ') return;
        event.preventDefault();
        if (option.classList.contains('position-agree')) window.selectPosition('agree');
        else if (option.classList.contains('position-disagree')) window.selectPosition('disagree');
        else window.selectPosition('complicate');
      });
    });
    var field = positionTextarea();
    var saved = storageGet('scholarsCompass:chapter-5:position', '');
    if (field && saved && !field.value) field.value = saved;
  }

  window.checkAnswer = function (button, result) {
    if (!button) return;
    var tool = closestTool(button);
    qsa('button[onclick*="checkAnswer"]', tool || document).forEach(function (candidate) {
      candidate.setAttribute('aria-pressed', candidate === button ? 'true' : 'false');
      candidate.style.boxShadow = '';
    });
    button.style.boxShadow = result === 'correct' ? '0 0 0 3px #28a745' : '0 0 0 3px #ffc107';
    setToolStatus(button,
      result === 'correct'
        ? 'Correct. Quote when the source’s exact wording adds meaning, authority, or language you plan to analyze.'
        : 'Try again. Time pressure or difficulty rephrasing is not a good reason to quote.',
      result === 'correct' ? 'success' : 'error');
  };

  window.checkParaphrase = function () {
    var input = qs('#paraphraseInput');
    var feedback = qs('#paraphraseFeedback');
    var text = qs('#feedbackText');
    if (!input || !feedback || !text) return;
    var value = input.value.trim();
    feedback.style.display = 'block';
    feedback.classList.remove('good', 'improve');
    if (!value) {
      feedback.classList.add('improve');
      text.textContent = 'Write a paraphrase first. Aim to restate the complete idea in a new sentence structure.';
      return;
    }
    var original = 'The proliferation of digital technology has fundamentally altered how young people form and maintain interpersonal relationships.';
    var normalize = function (s) {
      return s.toLowerCase().replace(/[^a-z0-9\s]/g, '').split(/\s+/).filter(function (word) { return word.length > 3; });
    };
    var originalWords = normalize(original);
    var draftWords = normalize(value);
    var overlap = draftWords.filter(function (word) { return originalWords.indexOf(word) !== -1; }).length;
    var ratio = draftWords.length ? overlap / draftWords.length : 1;
    if (draftWords.length < 7) {
      feedback.classList.add('improve');
      text.textContent = 'This is probably too brief to preserve the original idea. Include both the change caused by digital technology and its effect on young people’s relationships.';
    } else if (ratio > 0.65 || value.toLowerCase() === original.toLowerCase()) {
      feedback.classList.add('improve');
      text.textContent = 'This still follows too much of the original wording. Change the sentence structure, not just a few words, and remember to cite the source.';
    } else {
      feedback.classList.add('good');
      text.textContent = 'Your wording appears substantially different. Now compare it with the original to confirm that the meaning is accurate, then add the appropriate citation.';
    }
  };

  window.updateProgress = function () {
    var boxes = qsa('input[onchange*="updateProgress"]');
    var indicator = qs('#progressIndicator');
    var percentText = qs('#progressPercent');
    if (!boxes.length || !indicator || !percentText) return;
    var completed = [];
    boxes.forEach(function (box, index) { if (box.checked) completed.push(index); });
    var percent = Math.round((completed.length / boxes.length) * 100);
    indicator.style.width = percent + '%';
    indicator.setAttribute('role', 'progressbar');
    indicator.setAttribute('aria-valuemin', '0');
    indicator.setAttribute('aria-valuemax', '100');
    indicator.setAttribute('aria-valuenow', String(percent));
    percentText.textContent = percent + '%';
    storageSet('scholarsCompass:' + currentFile() + ':progress', completed);
  };

  function initChapter7Tools() {
    var boxes = qsa('input[onchange*="updateProgress"]');
    if (boxes.length) {
      var saved = storageGet('scholarsCompass:' + currentFile() + ':progress', []);
      boxes.forEach(function (box, index) { box.checked = saved.indexOf(index) !== -1; });
      window.updateProgress();
    }
  }

  window.generateSandwich = function () {
    var top = qs('#topBun');
    var meat = qs('#meat');
    var bottom = qs('#bottomBun');
    var output = qs('#sandwichOutput');
    var result = qs('#sandwichResult');
    if (!top || !meat || !bottom || !output || !result) return;
    if (!top.value.trim() || !meat.value.trim() || !bottom.value.trim()) {
      setToolStatus(output, 'Complete all three parts of the quote sandwich.', 'error');
      return;
    }
    result.textContent = top.value.trim() + ' ' + meat.value.trim() + ' ' + bottom.value.trim();
    output.style.display = 'block';
    storageSet('scholarsCompass:chapter-8:sandwich', result.textContent);
    setToolStatus(output, 'Sandwich built. Read it aloud and revise the transitions as needed.', 'success');
  };

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
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
      } catch (err) {
        area.remove();
        reject(err);
      }
    });
  }

  window.copySandwich = function () {
    var result = qs('#sandwichResult');
    if (!result || !result.textContent.trim()) return;
    copyText(result.textContent.trim()).then(function () {
      setToolStatus(result, 'Copied to the clipboard.', 'success');
    }).catch(function () {
      setToolStatus(result, 'The browser blocked copying. Select the text and copy it manually.', 'error');
    });
  };

  window.analyzeThesis = function () {
    var input = qs('#templatePractice');
    if (!input) return;
    var value = input.value.trim();
    if (!value) {
      setToolStatus(input, 'Write a working thesis before analyzing it.', 'error');
      return;
    }
    var words = value.split(/\s+/).length;
    var lower = value.toLowerCase();
    var claimSignal = /(argue|should|because|although|while|by examining|reveals|demonstrates|suggests)/.test(lower);
    var feedback = [];
    feedback.push(words < 8 ? 'The thesis may be too brief to establish a clear claim.' : (words > 55 ? 'The thesis may be doing too much in one sentence.' : 'The length is workable.'));
    feedback.push(claimSignal ? 'It includes language that signals an arguable relationship or claim.' : 'Strengthen the arguable claim by showing what you believe the evidence demonstrates.');
    feedback.push('Check that it names a specific subject, makes a debatable claim, and gives the reader a reason the claim matters.');
    setToolStatus(input, feedback.join(' '), claimSignal && words >= 8 && words <= 55 ? 'success' : 'info');
  };

  window.generateThesis = function () {
    var topic = qs('#topic');
    var problem = qs('#problem');
    var questions = qs('#questions');
    var research = qs('#research');
    var thesis = qs('#thesis');
    var output = qs('#thesisOutput');
    if (!topic || !problem || !questions || !research || !thesis || !output) return;
    if (!topic.value.trim() || !problem.value.trim()) {
      setToolStatus(output, 'Enter both a topic and a specific problem or observation.', 'error');
      return;
    }
    var result;
    if (thesis.value.trim()) {
      result = thesis.value.trim();
    } else {
      result = 'Working thesis scaffold: Although ' + problem.value.trim() + ', this paper argues that [state your specific, debatable claim about ' + topic.value.trim() + ']' + (research.value.trim() ? ', because ' + research.value.trim() : '') + '.';
    }
    output.textContent = result;
    setToolStatus(output, 'This is a working thesis. Revise the bracketed language into your own evidence-based claim.', thesis.value.trim() ? 'success' : 'info');
  };

  var BLOOM_DETAILS = {
    remember: ['Remember', 'Recall facts, terms, or basic concepts.', 'Useful verbs: identify, define, list, recognize.'],
    understand: ['Understand', 'Explain ideas or concepts in your own words.', 'Useful verbs: summarize, describe, interpret, compare.'],
    apply: ['Apply', 'Use knowledge in a new but related situation.', 'Useful verbs: demonstrate, use, solve, implement.'],
    analyze: ['Analyze', 'Break material into parts and explain relationships or patterns.', 'Useful verbs: examine, distinguish, connect, infer.'],
    evaluate: ['Evaluate', 'Make a judgment using clear criteria and evidence.', 'Useful verbs: assess, justify, critique, defend.'],
    create: ['Create', 'Combine ideas into a new argument, design, or interpretation.', 'Useful verbs: develop, compose, formulate, produce.']
  };

  window.showBloomDetails = function (level) {
    var details = BLOOM_DETAILS[level];
    var box = qs('#bloomsDetails');
    if (!details || !box) return;
    qsa('.blooms-level').forEach(function (item) {
      var selected = item.textContent.trim().toLowerCase() === level;
      item.setAttribute('aria-pressed', selected ? 'true' : 'false');
      item.style.outline = selected ? '3px solid var(--secondary)' : '';
      item.style.outlineOffset = selected ? '3px' : '';
    });
    box.innerHTML = '';
    var h = document.createElement('h4');
    h.textContent = details[0];
    var p1 = document.createElement('p');
    p1.textContent = details[1];
    var p2 = document.createElement('p');
    p2.textContent = details[2];
    box.appendChild(h);
    box.appendChild(p1);
    box.appendChild(p2);
    box.setAttribute('aria-live', 'polite');
  };

  window.generateQuoteSandwich = function () {
    var front = qs('#frontLoad');
    var quote = qs('#quoteText');
    var analysis = qs('#quoteAnalysis');
    var output = qs('#quoteOutput');
    if (!front || !quote || !analysis || !output) return;
    if (!front.value.trim() || !quote.value.trim() || !analysis.value.trim()) {
      setToolStatus(output, 'Complete the introduction, evidence, and analysis fields.', 'error');
      return;
    }
    output.textContent = front.value.trim() + ' ' + quote.value.trim() + ' ' + analysis.value.trim();
    setToolStatus(output, 'Paragraph generated. Check the citation and make sure the analysis explains why the evidence matters.', 'success');
  };

  function initChapter10Tools() {
    qsa('.blooms-level').forEach(function (item) {
      item.setAttribute('role', 'button');
      item.setAttribute('tabindex', '0');
      item.setAttribute('aria-pressed', 'false');
      item.addEventListener('keydown', function (event) {
        if (event.key !== 'Enter' && event.key !== ' ') return;
        event.preventDefault();
        window.showBloomDetails(item.textContent.trim().toLowerCase());
      });
    });
  }

  window.generatePIEParagraph = function () {
    var point = qs('#point');
    var illustration = qs('#illustration');
    var explanation = qs('#explanation');
    var output = qs('#pieOutput');
    if (!point || !illustration || !explanation || !output) return;
    if (!point.value.trim() || !illustration.value.trim() || !explanation.value.trim()) {
      setToolStatus(output, 'Complete the Point, Illustration, and Explanation fields.', 'error');
      return;
    }
    output.textContent = point.value.trim() + ' ' + illustration.value.trim() + ' ' + explanation.value.trim();
    setToolStatus(output, 'PIE paragraph generated. Add transitions and revise the explanation so the connection is unmistakable.', 'success');
  };

  function initChapterSpecificTools() {
    initChapter3Tools();
    initChapter5Tools();
    initChapter7Tools();
    initChapter10Tools();
  }

  ready(function () {
    initChapterSpecificTools();
  });

})();
