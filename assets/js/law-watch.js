(function () {
  'use strict';

  var root = document.querySelector('[data-law-watch-root]');
  if (!root) return;

  var search = root.querySelector('[data-filter="search"]');
  var stage = root.querySelector('[data-filter="stage"]');
  var source = root.querySelector('[data-filter="source"]');
  var topic = root.querySelector('[data-filter="topic"]');
  var agency = root.querySelector('[data-filter="agency"]');
  var timing = root.querySelector('[data-filter="timing"]');
  var reset = root.querySelector('[data-filter="reset"]');
  var cards = Array.prototype.slice.call(root.querySelectorAll('.source-card'));
  var visibleCount = root.querySelector('[data-visible-count]');
  var emptyState = root.querySelector('[data-empty-state]');

  function parseDate(raw) {
    if (!raw) return null;
    var date = new Date(raw + 'T00:00:00');
    if (Number.isNaN(date.getTime())) return null;
    return date;
  }

  function matchesTiming(card, value) {
    if (value === 'any') return true;

    var now = new Date();
    var published = parseDate(card.getAttribute('data-publication-date'));
    var deadline = parseDate(card.getAttribute('data-comment-deadline'));
    var commentOpen = card.getAttribute('data-comment-open') === 'true';

    if (value === 'comment_open') {
      return commentOpen;
    }

    if (value === 'last_30_days') {
      if (!published) return false;
      var thirtyDaysAgo = new Date(now);
      thirtyDaysAgo.setDate(now.getDate() - 30);
      return published >= thirtyDaysAgo;
    }

    if (value === 'deadline_this_week') {
      if (!deadline) return false;
      var end = new Date(now);
      end.setDate(now.getDate() + 7);
      return deadline >= now && deadline <= end;
    }

    return true;
  }

  function matchesToken(card, attributeName, value) {
    if (value === 'all') return true;
    var raw = card.getAttribute(attributeName) || '';
    if (!raw) return false;
    return raw.split('|').indexOf(value) >= 0;
  }

  function applyFilters() {
    var q = (search && search.value || '').toLowerCase().trim();
    var stageValue = stage ? stage.value : 'all';
    var sourceValue = source ? source.value : 'all';
    var topicValue = topic ? topic.value : 'all';
    var agencyValue = agency ? agency.value : 'all';
    var timingValue = timing ? timing.value : 'any';
    var shown = 0;

    cards.forEach(function (card) {
      var text = card.textContent.toLowerCase();
      var isMatch =
        (q === '' || text.indexOf(q) >= 0) &&
        matchesToken(card, 'data-stage', stageValue) &&
        matchesToken(card, 'data-source', sourceValue) &&
        matchesToken(card, 'data-topic', topicValue) &&
        matchesToken(card, 'data-agency', agencyValue) &&
        matchesTiming(card, timingValue);

      card.hidden = !isMatch;
      if (isMatch) shown += 1;
    });

    if (visibleCount) {
      visibleCount.textContent = 'Showing ' + shown + ' of ' + cards.length + ' items';
    }

    if (emptyState) {
      emptyState.classList.toggle('is-visible', shown === 0);
    }
  }

  function resetFilters() {
    if (search) search.value = '';
    if (stage) stage.value = 'all';
    if (source) source.value = 'all';
    if (topic) topic.value = 'all';
    if (agency) agency.value = 'all';
    if (timing) timing.value = 'any';
    applyFilters();
  }

  [search, stage, source, topic, agency, timing].forEach(function (field) {
    if (!field) return;
    field.addEventListener('input', applyFilters);
    field.addEventListener('change', applyFilters);
  });

  if (reset) {
    reset.addEventListener('click', resetFilters);
  }

  applyFilters();
})();
