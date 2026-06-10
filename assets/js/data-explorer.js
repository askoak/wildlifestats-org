/* WildlifeStats /data/ explorer.
   Loads the synthetic admissions cube once, filters it in memory, and renders
   an aggregate summary, a state choropleth, and a k-suppressed CSV download.
   No backend, no CDN. topojson-client is loaded from a committed vendor file. */

(function () {
  'use strict';

  var CUBE_URL = '/data/cube/admissions-cube.json';
  var TOPO_URL = '/assets/maps/us-states.topojson';

  // 2-digit state FIPS -> USPS abbreviation (matches the cube's state dimension).
  var FIPS_USPS = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
    "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
    "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
    "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY"
  };

  var REASON_LABELS = {
    vehicle_strike: "Vehicle strike", window_strike: "Window strike",
    predation: "Predation", entanglement: "Entanglement",
    orphan_displacement: "Orphan / displacement", habitat_disruption: "Habitat disruption",
    anthropogenic_poisoning: "Poisoning", infectious_disease: "Infectious disease",
    other_trauma: "Other trauma", unknown: "Unknown"
  };

  var cube = null, topo = null, stateFeatures = null;
  var sel = { years: new Set(), states: new Set(), classes: new Set(), reasons: new Set() };
  // Column indices in each compact cell.
  var Y = 0, M = 1, ST = 2, CL = 4, RS = 6, N = 9;

  function el(id) { return document.getElementById(id); }
  function titleCase(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

  function ringPath(ring) {
    var d = "M";
    for (var i = 0; i < ring.length; i++) {
      d += (i ? "L" : "") + ring[i][0].toFixed(1) + "," + ring[i][1].toFixed(1);
    }
    return d + "Z";
  }
  function geomPath(geom) {
    if (!geom) return "";
    if (geom.type === "Polygon") return geom.coordinates.map(ringPath).join("");
    if (geom.type === "MultiPolygon") {
      return geom.coordinates.map(function (p) { return p.map(ringPath).join(""); }).join("");
    }
    return "";
  }

  // ---- filter UI ----
  function buildCheckboxGroup(hostId, items, labelFn, set, scroll) {
    var host = el(hostId);
    host.innerHTML = "";
    host.className = "filter-options" + (scroll ? " filter-options--scroll" : "");
    items.forEach(function (val) {
      var id = hostId + "-" + val;
      var wrap = document.createElement("label");
      wrap.className = "filter-opt";
      var cb = document.createElement("input");
      cb.type = "checkbox"; cb.value = String(val); cb.id = id;
      cb.addEventListener("change", function () {
        if (cb.checked) set.add(String(val)); else set.delete(String(val));
        render();
      });
      var span = document.createElement("span");
      span.textContent = labelFn(val);
      wrap.appendChild(cb); wrap.appendChild(span);
      host.appendChild(wrap);
    });
  }

  function clearAll() {
    sel.years.clear(); sel.states.clear(); sel.classes.clear(); sel.reasons.clear();
    document.querySelectorAll(".filter-options input[type=checkbox]").forEach(function (cb) {
      cb.checked = false;
    });
    render();
  }

  // ---- filtering + aggregation ----
  function matches(cell) {
    if (sel.years.size && !sel.years.has(String(cube.dimensions.years[cell[Y]]))) return false;
    if (sel.states.size && !sel.states.has(cube.dimensions.states[cell[ST]])) return false;
    if (sel.classes.size && !sel.classes.has(cube.dimensions.classes[cell[CL]])) return false;
    if (sel.reasons.size && !sel.reasons.has(cube.dimensions.reasons[cell[RS]])) return false;
    return true;
  }

  function aggregate() {
    var total = 0;
    var byYear = {}, byState = {};
    var cells = cube.cells;
    for (var i = 0; i < cells.length; i++) {
      var c = cells[i];
      if (!matches(c)) continue;
      var n = c[N];
      total += n;
      var yr = cube.dimensions.years[c[Y]];
      byYear[yr] = (byYear[yr] || 0) + n;
      var stt = cube.dimensions.states[c[ST]];
      byState[stt] = (byState[stt] || 0) + n;
    }
    return { total: total, byYear: byYear, byState: byState };
  }

  // ---- rendering ----
  function render() {
    if (!cube) return;
    var agg = aggregate();

    el("result-total").textContent = agg.total.toLocaleString() + " records";

    // by-year table
    var yrs = cube.dimensions.years;
    var yhtml = "<table class='agg-table'><thead><tr><th>Year</th><th>Records</th></tr></thead><tbody>";
    yrs.forEach(function (y) {
      yhtml += "<tr><td>" + y + "</td><td>" + (agg.byYear[y] || 0).toLocaleString() + "</td></tr>";
    });
    yhtml += "</tbody></table>";
    el("agg-year").innerHTML = yhtml;

    // top states table
    var states = Object.keys(agg.byState).sort(function (a, b) { return agg.byState[b] - agg.byState[a]; });
    var top = states.slice(0, 10);
    var shtml = "<table class='agg-table'><thead><tr><th>State</th><th>Records</th></tr></thead><tbody>";
    top.forEach(function (s) {
      shtml += "<tr><td>" + s + "</td><td>" + agg.byState[s].toLocaleString() + "</td></tr>";
    });
    shtml += "</tbody></table>";
    el("agg-state").innerHTML = shtml;

    renderMap(agg.byState);
  }

  function colorFor(v, max) {
    if (!v) return "#EFEADA";
    var t = Math.sqrt(v / max); // sqrt for perceptual spread
    // interpolate paper -> slate
    var c0 = [214, 224, 210], c1 = [42, 63, 82];
    var r = Math.round(c0[0] + (c1[0] - c0[0]) * t);
    var g = Math.round(c0[1] + (c1[1] - c0[1]) * t);
    var b = Math.round(c0[2] + (c1[2] - c0[2]) * t);
    return "rgb(" + r + "," + g + "," + b + ")";
  }

  function renderMap(byState) {
    if (!stateFeatures) return;
    var max = 0;
    Object.keys(byState).forEach(function (s) { if (byState[s] > max) max = byState[s]; });
    max = max || 1;
    var svg = el("us-map");
    var paths = "";
    stateFeatures.forEach(function (f) {
      var usps = FIPS_USPS[f.id];
      if (!usps) return;
      var v = byState[usps] || 0;
      paths += "<path d='" + geomPath(f.geometry) + "' fill='" + colorFor(v, max) +
        "' stroke='#FAF6EC' stroke-width='0.7'><title>" + usps + ": " +
        v.toLocaleString() + "</title></path>";
    });
    svg.innerHTML = paths;
  }

  // ---- CSV with k-suppression (spec §10) ----
  function downloadCsv() {
    var grain = {}; // key year|month|state|class|reason -> n
    var cells = cube.cells;
    for (var i = 0; i < cells.length; i++) {
      var c = cells[i];
      if (!matches(c)) continue;
      var key = cube.dimensions.years[c[Y]] + "|" + c[M] + "|" + cube.dimensions.states[c[ST]] +
        "|" + cube.dimensions.classes[c[CL]] + "|" + cube.dimensions.reasons[c[RS]];
      grain[key] = (grain[key] || 0) + c[N];
    }
    var rows = [["year", "month", "state", "class", "reason", "n"]];
    var suppressed = 0;
    Object.keys(grain).sort().forEach(function (k) {
      var n = grain[k];
      if (n < 10) { suppressed += n; return; }
      rows.push(k.split("|").concat([n]));
    });
    if (suppressed > 0) {
      rows.push(["Suppressed (n<10)", "", "", "", "", suppressed]);
    }
    var csv = rows.map(function (r) {
      return r.map(function (v) { return '"' + String(v).replace(/"/g, '""') + '"'; }).join(",");
    }).join("\n");
    var blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = "wildlifestats-filtered.csv";
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // ---- init ----
  function init() {
    var statusEl = el("explorer-status");
    Promise.all([
      fetch(CUBE_URL).then(function (r) { return r.json(); }),
      fetch(TOPO_URL).then(function (r) { return r.json(); })
    ]).then(function (res) {
      cube = res[0]; topo = res[1];
      stateFeatures = topojson.feature(topo, topo.objects.states).features;

      buildCheckboxGroup("filter-year", cube.dimensions.years, function (y) { return String(y); }, sel.years, false);
      buildCheckboxGroup("filter-class", cube.dimensions.classes, titleCase, sel.classes, false);
      buildCheckboxGroup("filter-reason", cube.dimensions.reasons, function (r) { return REASON_LABELS[r] || r; }, sel.reasons, false);
      buildCheckboxGroup("filter-state", cube.dimensions.states, function (s) { return s; }, sel.states, true);

      el("btn-clear").addEventListener("click", clearAll);
      el("btn-csv").addEventListener("click", downloadCsv);

      if (statusEl) statusEl.style.display = "none";
      el("explorer-body").hidden = false;
      render();
    }).catch(function () {
      if (statusEl) statusEl.textContent = "The dataset could not be loaded. Please try again later.";
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
