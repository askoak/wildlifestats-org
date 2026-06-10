/* Header behavior: mark the nav link for the current section.
   No framework, no dependencies. Pages work fully without JS;
   this only adds the current-section highlight. */

(function () {
  'use strict';

  var path = window.location.pathname;
  var links = document.querySelectorAll('.site-nav a');

  links.forEach(function (link) {
    var href = link.getAttribute('href');
    if (!href) return;

    var isCurrent =
      href === path ||
      (href !== '/' && path.indexOf(href) === 0);

    if (isCurrent) {
      link.setAttribute('aria-current', 'true');
    }
  });
})();
