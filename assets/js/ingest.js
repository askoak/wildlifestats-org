/* /ingest/ — methodology demo. Fetches the committed sample CSVs, normalizes
   each into the canonical WildlifeStats schema in the browser, and shows the
   before (raw) / after (normalized JSON) for each. This is a demonstration of
   the conceptual pipeline, NOT a live ingestion service — there is no upload. */

(function () {
  'use strict';

  var SAMPLES = [
    { file: "center-a.csv", label: "Center A — comma-delimited" },
    { file: "center-b.csv", label: "Center B — semicolon-delimited" },
    { file: "center-c.csv", label: "Center C — tab-delimited" },
    { file: "center-d.csv", label: "Center D — county FIPS keyed" }
  ];

  // canonical column -> list of candidate source header names (lowercased)
  var FIELD_MAP = {
    source_id: ["patient id", "case_no", "id", "record"],
    species_raw: ["animal", "species", "commonname", "critter"],
    date_raw: ["found date", "intake", "datereceived", "admitted_on"],
    place_raw: ["city", "county", "location", "fips"],
    state_raw: ["state", "st"],
    reason_raw: ["reason", "presenting_complaint", "problem", "cause"],
    outcome_raw: ["outcome", "disposition", "result", "final"]
  };

  function normSpecies(s) {
    s = s.toLowerCase();
    if (/sea turtle/.test(s)) return ["sea_turtle", "marine"];
    if (/turtle|terrapin/.test(s)) return ["turtle_aquatic", "reptile"];
    if (/hawk|owl|eagle|falcon|kestrel|osprey|raptor/.test(s)) return ["raptor", "bird"];
    if (/robin|songbird|passerine|sparrow|finch|warbler|wren/.test(s)) return ["passerine_songbird", "bird"];
    if (/mallard|duck|goose|waterfowl/.test(s)) return ["waterfowl", "bird"];
    if (/cottontail|rabbit/.test(s)) return ["cottontail", "mammal"];
    if (/opossum/.test(s)) return ["opossum", "mammal"];
    if (/raccoon/.test(s)) return ["raccoon", "mammal"];
    if (/deer/.test(s)) return ["white_tailed_deer", "mammal"];
    if (/bat/.test(s)) return ["bat", "mammal"];
    return ["unknown_archetype", "unknown"];
  }

  function normReason(s) {
    s = s.toLowerCase();
    if (/car|vehicle|hit by/.test(s)) return "vehicle_strike";
    if (/window/.test(s)) return "window_strike";
    if (/orphan|nest|displac/.test(s)) return "orphan_displacement";
    if (/cat|predat|attack/.test(s)) return "predation";
    if (/entangl|line|net/.test(s)) return "entanglement";
    if (/oil|lead|tox|poison/.test(s)) return "anthropogenic_poisoning";
    if (/disease|infect/.test(s)) return "infectious_disease";
    if (/mower|injury|grounded|trauma/.test(s)) return "other_trauma";
    return "unknown";
  }

  function normOutcome(s) {
    s = s.toLowerCase();
    if (/euthan/.test(s)) return "euthanized";
    if (/died|death|dead/.test(s)) return "deceased";
    if (/transfer/.test(s)) return "transferred";
    if (/in care/.test(s)) return "in_care";
    if (/releas|rehab/.test(s)) return "released";
    return "unknown";
  }

  var MONTHS = { jan: "01", feb: "02", mar: "03", apr: "04", may: "05", jun: "06",
    jul: "07", aug: "08", sep: "09", oct: "10", nov: "11", dec: "12" };

  function normDate(s) {
    s = s.trim();
    var m;
    if ((m = s.match(/^(\d{4})-(\d{2})-\d{2}$/))) return m[1] + "-" + m[2];          // 2024-05-03
    if ((m = s.match(/^(\d{2})\/(\d{2})\/(\d{4})$/))) return m[3] + "-" + m[1];       // 05/14/2024
    if ((m = s.match(/^\d{1,2}-([A-Za-z]{3})-(\d{4})$/))) return m[2] + "-" + (MONTHS[m[1].toLowerCase()] || "??"); // 14-Apr-2024
    return s;
  }

  function detectDelim(text) {
    var first = text.split(/\r?\n/)[0];
    if (first.indexOf("\t") >= 0) return "\t";
    if (first.indexOf(";") >= 0) return ";";
    return ",";
  }

  function parse(text) {
    var delim = detectDelim(text);
    var lines = text.replace(/\s+$/, "").split(/\r?\n/);
    var headers = lines[0].split(delim).map(function (h) { return h.trim(); });
    var rows = lines.slice(1).map(function (ln) {
      var cells = ln.split(delim);
      var obj = {};
      headers.forEach(function (h, i) { obj[h] = (cells[i] || "").trim(); });
      return obj;
    });
    return { headers: headers, rows: rows };
  }

  function pick(row, headers, candidates) {
    for (var i = 0; i < headers.length; i++) {
      if (candidates.indexOf(headers[i].toLowerCase()) >= 0) return row[headers[i]];
    }
    return "";
  }

  function normalizeRows(parsed) {
    return parsed.rows.map(function (row) {
      var sp = normSpecies(pick(row, parsed.headers, FIELD_MAP.species_raw));
      return {
        source_id: pick(row, parsed.headers, FIELD_MAP.source_id),
        species_archetype: sp[0],
        class: sp[1],
        admitted: normDate(pick(row, parsed.headers, FIELD_MAP.date_raw)),
        admission_reason: normReason(pick(row, parsed.headers, FIELD_MAP.reason_raw)),
        outcome: normOutcome(pick(row, parsed.headers, FIELD_MAP.outcome_raw)),
        location: pick(row, parsed.headers, FIELD_MAP.place_raw),
        state: pick(row, parsed.headers, FIELD_MAP.state_raw)
      };
    });
  }

  function esc(s) { return String(s).replace(/[&<>]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }); }

  function renderSample(host, sample, raw) {
    var parsed = parse(raw);
    var normalized = normalizeRows(parsed);
    var block = document.createElement("div");
    block.className = "ingest-sample";
    block.innerHTML =
      "<h3>" + esc(sample.label) + "</h3>" +
      "<div class='ingest-cols'>" +
        "<div><p class='ingest-side'>Raw file</p><pre class='ingest-pre'>" + esc(raw.trim()) + "</pre></div>" +
        "<div><p class='ingest-side'>Normalized</p><pre class='ingest-pre'>" +
          esc(JSON.stringify(normalized, null, 2)) + "</pre></div>" +
      "</div>";
    host.appendChild(block);
  }

  function init() {
    var host = document.getElementById("ingest-samples");
    var status = document.getElementById("ingest-status");
    if (!host) return;
    Promise.all(SAMPLES.map(function (s) {
      return fetch("/samples/ingest/" + s.file).then(function (r) { return r.text(); })
        .then(function (t) { return { s: s, t: t }; });
    })).then(function (results) {
      if (status) status.hidden = true;
      results.forEach(function (r) { renderSample(host, r.s, r.t); });
    }).catch(function () {
      if (status) status.textContent = "The sample files could not be loaded.";
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else { init(); }
})();
