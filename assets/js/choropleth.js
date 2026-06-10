/* Shared US-states choropleth helper for WildlifeStats.
   Renders a state-shaded map into an <svg viewBox="0 0 975 610"> from a
   { USPS -> count } map, using a committed albers-projected TopoJSON and the
   vendored topojson-client (global `topojson`). No projection library needed —
   the TopoJSON is pre-projected to 975x610. */

window.WSChoropleth = (function () {
  'use strict';

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

  function colorFor(v, max) {
    if (!v) return "#EFEADA";
    var t = Math.sqrt(v / max);
    var c0 = [214, 224, 210], c1 = [42, 63, 82];
    return "rgb(" +
      Math.round(c0[0] + (c1[0] - c0[0]) * t) + "," +
      Math.round(c0[1] + (c1[1] - c0[1]) * t) + "," +
      Math.round(c0[2] + (c1[2] - c0[2]) * t) + ")";
  }

  function render(svgEl, byState, topo) {
    var features = topojson.feature(topo, topo.objects.states).features;
    var max = 0;
    Object.keys(byState).forEach(function (s) { if (byState[s] > max) max = byState[s]; });
    max = max || 1;
    var paths = "";
    features.forEach(function (f) {
      var usps = FIPS_USPS[f.id];
      if (!usps) return;
      var v = byState[usps] || 0;
      paths += "<path d='" + geomPath(f.geometry) + "' fill='" + colorFor(v, max) +
        "' stroke='#FAF6EC' stroke-width='0.7'><title>" + usps + ": " +
        v.toLocaleString() + "</title></path>";
    });
    svgEl.innerHTML = paths;
  }

  return { render: render, FIPS_USPS: FIPS_USPS, colorFor: colorFor };
})();
