/* /one-health/ — renders the "zoonotic risk by region" choropleth from the
   cube, filtered to reason = infectious_disease. Static (no filters). */

(function () {
  'use strict';
  var CL = 4, ST = 2, RS = 6, N = 9; // cube cell column indices

  function init() {
    var svg = document.getElementById("zoonotic-map");
    var status = document.getElementById("zoonotic-status");
    if (!svg) return;
    Promise.all([
      fetch("/data/cube/admissions-cube.json").then(function (r) { return r.json(); }),
      fetch("/assets/maps/us-states.topojson").then(function (r) { return r.json(); })
    ]).then(function (res) {
      var cube = res[0], topo = res[1];
      var infIdx = cube.dimensions.reasons.indexOf("infectious_disease");
      var byState = {};
      var total = 0;
      cube.cells.forEach(function (c) {
        if (c[RS] !== infIdx) return;
        var s = cube.dimensions.states[c[ST]];
        byState[s] = (byState[s] || 0) + c[N];
        total += c[N];
      });
      WSChoropleth.render(svg, byState, topo);
      if (status) {
        status.textContent = total.toLocaleString() +
          " synthetic infectious-disease admissions across all states, 2017–2025.";
      }
    }).catch(function () {
      if (status) status.textContent = "The regional map could not be loaded.";
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else { init(); }
})();
