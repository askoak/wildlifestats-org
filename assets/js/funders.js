(function () {
  'use strict';

  var root = document.querySelector('[data-funders-root]');
  if (!root) return;

  var search = root.querySelector('[data-filter="search"]');
  var type = root.querySelector('[data-filter="type"]');
  var focus = root.querySelector('[data-filter="focus"]');
  var reset = root.querySelector('[data-filter="reset"]');
  var cards = Array.prototype.slice.call(root.querySelectorAll('.source-card'));
  var visibleCount = root.querySelector('[data-visible-count]');
  var emptyState = root.querySelector('[data-empty-state]');

  function matchesToken(card, attributeName, value) {
    if (value === 'all') return true;
    var raw = card.getAttribute(attributeName) || '';
    if (!raw) return false;
    return raw.split('|').indexOf(value) >= 0;
  }

  function applyFilters() {
    var q = (search && search.value || '').toLowerCase().trim();
    var typeValue = type ? type.value : 'all';
    var focusValue = focus ? focus.value : 'all';
    var shown = 0;

    cards.forEach(function (card) {
      var text = card.textContent.toLowerCase();
      var isMatch =
        (q === '' || text.indexOf(q) >= 0) &&
        matchesToken(card, 'data-type', typeValue) &&
        matchesToken(card, 'data-focus', focusValue);

      card.hidden = !isMatch;
      if (isMatch) shown += 1;
    });

    if (visibleCount) {
      visibleCount.textContent = 'Showing ' + shown + ' of ' + cards.length + ' funders';
    }

    if (emptyState) {
      emptyState.classList.toggle('is-visible', shown === 0);
    }
  }

  function resetFilters() {
    if (search) search.value = '';
    if (type) type.value = 'all';
    if (focus) focus.value = 'all';
    applyFilters();
  }

  [search, type, focus].forEach(function (field) {
    if (!field) return;
    field.addEventListener('input', applyFilters);
    field.addEventListener('change', applyFilters);
  });

  if (reset) {
    reset.addEventListener('click', resetFilters);
  }

  applyFilters();
})();
