/* /wildlife/ — taxonomic browse of the synthetic dataset.
   Class -> species archetype. Each archetype: a range hint (states where its
   region archetype applies, shaded), top-3 synthetic admission reasons, a
   monthly seasonal chart, and generic find-one routing to AnimalHelpNow.
   The dataset's species granularity is archetype-level (see Methodology). */

(function () {
  'use strict';

  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  var CLASS_LABELS = { bird: "Birds", mammal: "Mammals", reptile: "Reptiles", amphibian: "Amphibians", marine: "Marine" };
  var REASON_LABELS = {
    vehicle_strike: "Vehicle strike", window_strike: "Window strike",
    predation: "Predation", entanglement: "Entanglement",
    orphan_displacement: "Orphan / displacement", habitat_disruption: "Habitat disruption",
    anthropogenic_poisoning: "Poisoning", infectious_disease: "Infectious disease",
    other_trauma: "Other trauma", unknown: "Unknown"
  };

  var cube, topo, archetypes, regionMap;
  var speciesClass = {};   // species -> class
  var classSpecies = {};   // class -> [species]
  var speciesRegions = {}; // species -> Set(region)
  var SP = 5, RS = 6, M = 1, ST = 2, N = 9;

  function prettySpecies(s) {
    return s.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }

  function barChart(monthly) {
    var max = Math.max.apply(null, monthly) || 1;
    var w = 320, h = 120, pad = 18, bw = (w - pad * 2) / 12, bars = "";
    for (var i = 0; i < 12; i++) {
      var bh = (monthly[i] / max) * (h - pad * 2);
      var x = pad + i * bw, y = h - pad - bh;
      bars += "<rect x='" + (x + 1).toFixed(1) + "' y='" + y.toFixed(1) + "' width='" +
        (bw - 2).toFixed(1) + "' height='" + bh.toFixed(1) + "' fill='#2A3F52'><title>" +
        MONTHS[i] + ": " + monthly[i] + "</title></rect>";
      bars += "<text x='" + (x + bw / 2).toFixed(1) + "' y='" + (h - 5) +
        "' text-anchor='middle' font-size='8' fill='#6B6B65'>" + MONTHS[i][0] + "</text>";
    }
    return "<svg viewBox='0 0 " + w + " " + h + "' role='img' aria-label='Monthly admissions' class='spark'>" + bars + "</svg>";
  }

  function speciesProfile(sp) {
    // aggregate cube for this species
    var spIdx = cube.dimensions.species.indexOf(sp);
    var reasons = {}, monthly = new Array(12).fill(0), total = 0;
    cube.cells.forEach(function (c) {
      if (c[SP] !== spIdx) return;
      var n = c[N];
      total += n;
      var rn = cube.dimensions.reasons[c[RS]];
      reasons[rn] = (reasons[rn] || 0) + n;
      monthly[c[M] - 1] += n;
    });
    var top3 = Object.keys(reasons).sort(function (a, b) { return reasons[b] - reasons[a]; }).slice(0, 3);

    // range: states in regions whose archetype includes this species
    var states = {};
    (speciesRegions[sp] ? Array.from(speciesRegions[sp]) : []).forEach(function (region) {
      Object.keys(regionMap).forEach(function (st) {
        if (regionMap[st].region === region) states[st] = 1;
      });
    });

    var host = document.getElementById("species-profile");
    var reasonHtml = top3.map(function (r) {
      return "<li><span>" + (REASON_LABELS[r] || r) + "</span><span>" +
        reasons[r].toLocaleString() + "</span></li>";
    }).join("");

    host.innerHTML =
      "<h2>" + prettySpecies(sp) + "</h2>" +
      "<p class='species-meta'>" + CLASS_LABELS[speciesClass[sp]] + " · " +
      total.toLocaleString() + " synthetic admissions · appears in " +
      Object.keys(states).length + " states</p>" +
      "<div class='species-cols'>" +
        "<div><h3>Range (modeled)</h3>" +
          "<figure class='map-figure'><svg id='species-map' viewBox='0 0 975 610' role='img' aria-label='States where this archetype is modeled' preserveAspectRatio='xMidYMid meet'></svg>" +
          "<figcaption>States whose regional archetype includes this species. Modeled coverage, not an observed range map.</figcaption></figure>" +
        "</div>" +
        "<div>" +
          "<h3>Top admission reasons</h3><ul class='kv-list'>" + reasonHtml + "</ul>" +
          "<h3>Seasonal pattern</h3>" + barChart(monthly) +
        "</div>" +
      "</div>" +
      "<div class='find-one'><h3>If you find one</h3>" +
      "<p>If you find this animal injured, orphaned, or in distress, contact a licensed wildlife professional through " +
      "<a href='https://ahnow.org' rel='noopener' target='_blank'>AnimalHelpNow</a>, the national directory of wildlife responders. " +
      "Do not attempt treatment yourself. This page offers no triage or handling advice.</p></div>";

    host.hidden = false;
    // shade the range map
    var byState = {};
    Object.keys(states).forEach(function (s) { byState[s] = 1; });
    WSChoropleth.render(document.getElementById("species-map"), byState, topo);
    host.scrollIntoView({ block: "nearest" });
  }

  function renderClass(cls) {
    var ul = document.getElementById("species-list");
    var list = (classSpecies[cls] || []).slice().sort();
    ul.innerHTML = list.map(function (sp) {
      return "<li><button type='button' class='species-link' data-sp='" + sp + "'>" +
        prettySpecies(sp) + "</button></li>";
    }).join("");
    ul.querySelectorAll(".species-link").forEach(function (b) {
      b.addEventListener("click", function () { speciesProfile(b.getAttribute("data-sp")); });
    });
    document.getElementById("species-profile").hidden = true;
    document.querySelectorAll(".class-tab").forEach(function (t) {
      t.setAttribute("aria-pressed", t.getAttribute("data-cls") === cls ? "true" : "false");
    });
  }

  function buildIndexes() {
    Object.keys(archetypes).forEach(function (region) {
      var spd = archetypes[region].species;
      Object.keys(spd).forEach(function (cls) {
        Object.keys(spd[cls]).forEach(function (sp) {
          speciesClass[sp] = cls;
          (classSpecies[cls] = classSpecies[cls] || []);
          if (classSpecies[cls].indexOf(sp) < 0) classSpecies[cls].push(sp);
          (speciesRegions[sp] = speciesRegions[sp] || new Set()).add(region);
        });
      });
    });
  }

  function init() {
    var status = document.getElementById("wildlife-status");
    Promise.all([
      fetch("/data/cube/admissions-cube.json").then(function (r) { return r.json(); }),
      fetch("/assets/maps/us-states.topojson").then(function (r) { return r.json(); }),
      fetch("/wildlifestats/_build/species-archetypes.json").then(function (r) { return r.json(); }),
      fetch("/wildlifestats/_build/state-region-map.json").then(function (r) { return r.json(); })
    ]).then(function (res) {
      cube = res[0]; topo = res[1]; archetypes = res[2].regions; regionMap = res[3].states;
      buildIndexes();
      var tabHost = document.getElementById("class-tabs");
      tabHost.innerHTML = ["bird", "mammal", "reptile", "amphibian", "marine"].map(function (cls) {
        return "<button type='button' class='class-tab' data-cls='" + cls +
          "' aria-pressed='false'>" + CLASS_LABELS[cls] + "</button>";
      }).join("");
      tabHost.querySelectorAll(".class-tab").forEach(function (t) {
        t.addEventListener("click", function () { renderClass(t.getAttribute("data-cls")); });
      });
      if (status) status.hidden = true;
      document.getElementById("wildlife-browser").hidden = false;
      renderClass("bird");
    }).catch(function () {
      if (status) status.textContent = "The wildlife dataset could not be loaded.";
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else { init(); }
})();
