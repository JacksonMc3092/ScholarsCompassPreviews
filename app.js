/* Scholar's Compass — global behavior (GitHub Pages static site)
   Shared shell stabilization and approved ENG 1010 display order.
*/

(function () {
  'use strict';

  document.documentElement.classList.add('js');

  // Load the reversible shared correction layer from the same folder as app.js.
  (function loadStabilizationStyles() {
    if (document.querySelector('link[data-sc-stabilization="0.5"]')) return;
    var current = document