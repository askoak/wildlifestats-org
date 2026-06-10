/* /parks/ — National Parks lens. Loads the parks overlay, offers a searchable
   list of NPS units, and renders a per-park synthetic profile (top classes,
   dominant reasons, monthly seasonal bars). All synthetic; caveat shown on
   every profile. */

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

  var parks = [];

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function barChart(monthly) {
    var max = Math.max.apply(null, monthly) || 1;
    var w = 320, h = 120, pad = 18, bw = (w - pad * 2) / 12;
    var bars = "";
    for (var i = 0; i < 12; i++) {
      var bh = (monthly[i] / max) * (h - pad * 2);
      var x = pad + i * bw;
      var y = h - pad - bh;
      bars += "<rect x='" + (x + 1).toFixed(1) + "' y='" + y.toFixed(1) +
        "' width='" + (bw - 2).toFixed(1) + "' height='" + bh.toFixed(1) +
        "' fill='#2A3F52'><title>" + MONTHS[i] + ": " + monthly[i] + "</title></rect>";
      bars += "<text x='" + (x + bw / 2).toFixed(1) + "' y='" + (h - 5) +
        "' text-anchor='middle' font-size='8' fill='#6B6B65'>" + MONTHS[i][0] + "</text>";
    }
    return "<svg viewBox='0 0 " + w + " " + h + "' role='img' aria-label='Monthly admissions' class='spark'>" + bars + "</svg>";
  }

  function renderProfile(p) {
    var host = document.getElementById("park-profile");
    var caveat = "<p class='park-caveat'>These profiles use synthetic data plausibly shaped by regional species composition. They are not measured against any specific park's actual wildlife activity, and they are not a substitute for NPS interpretive resources or wildlife management reports.</p>";

    if (!p.n_counties || !p.total) {
      host.innerHTML = "<h2>" + esc(p.name) + " National Park</h2>" + caveat +
        "<p>No counties fall within 50 miles of this unit's centroid in the current snapshot, so no synthetic profile is available.</p>";
      host.hidden = false;
      return;
    }

    var classes = p.classes.map(function (c) {
      return "<li><span>" + (CLASS_LABELS[c["class"]] || c["class"]) + "</span><span>" +
        c.n.toLocaleString() + "</span></li>";
    }).join("");
    var reasons = p.reasons.map(function (r) {
      return "<li><span>" + (REASON_LABELS[r.reason] || r.reason) + "</span><span>" +
        r.n.toLocaleString() + "</span></li>";
    }).join("");

    host.innerHTML =
      "<h2>" + esc(p.name) + " National Park</h2>" +
      "<p class='park-meta'>" + esc(p.state) + " · " + p.n_counties +
      " counties within 50 mi · " + p.total.toLocaleString() + " synthetic admissions</p>" +
      caveat +
      "<div class='park-cols'>" +
        "<div><h3>Top species classes</h3><ul class='kv-list'>" + classes + "</ul></div>" +
        "<div><h3>Dominant admission reasons</h3><ul class='kv-list'>" + reasons + "</ul></div>" +
      "</div>" +
      "<h3>Seasonal pattern</h3>" + barChart(p.monthly);
    host.hidden = false;
    host.scrollIntoView({ block: "nearest" });
  }

  function renderList(filter) {
    var ul = document.getElementById("park-list");
    var f = (filter || "").toLowerCase();
    var items = parks.filter(function (p) {
      return !f || p.name.toLowerCase().indexOf(f) >= 0 || p.state.toLowerCase() === f;
    });
    ul.innerHTML = items.map(function (p) {
      return "<li><button type='button' class='park-link' data-name='" + esc(p.name) + "'>" +
        esc(p.name) + " <span class='park-state'>" + esc(p.state) + "</span></button></li>";
    }).join("");
    ul.querySelectorAll(".park-link").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var p = parks.find(function (x) { return x.name === btn.getAttribute("data-name"); });
        if (p) renderProfile(p);
      });
    });
  }

  function init() {
    var status = document.getElementById("park-status");
    fetch("/data/cube/parks-overlay.json").then(function (r) { return r.json(); })
      .then(function (d) {
        parks = d.parks.slice().sort(function (a, b) { return a.name.localeCompare(b.name); });
        if (status) status.hidden = true;
        document.getElementById("park-browser").hidden = false;
        renderList("");
        var search = document.getElementById("park-search");
        search.addEventListener("input", function () { renderList(search.value); });
      }).catch(function () {
        if (status) status.textContent = "The parks dataset could not be loaded.";
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else { init(); }
})();
