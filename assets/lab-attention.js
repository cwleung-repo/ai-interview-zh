/* Lab 05 · 注意力热力图 */
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var D = $("atD"), T = $("atT"), scale = $("atScale"), causal = $("atCausal");
  var grid = $("atGrid"), bars = $("atRowBars"), sel = $("atRowSel");
  if (!D || !grid) return;

  var TOK = ["猫", "坐", "在", "垫子", "上", "因为", "它", "很", "累"];
  var DMAX = 128;
  var selected = 4;

  function rng(seed) {
    var s = seed >>> 0;
    return function () {
      s = (s * 1664525 + 1013904223) >>> 0;
      return (s / 4294967296) * 2 - 1;
    };
  }

  var Q = TOK.map(function (_, i) { var r = rng(i * 131 + 7); return Array.from({ length: DMAX }, r); });
  var K = TOK.map(function (_, j) { var r = rng(j * 197 + 11); return Array.from({ length: DMAX }, r); });

  function rgbOf(varName, fallback) {
    var v = getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
    if (!v) return fallback;
    if (v[0] === "#") {
      var n = parseInt(v.slice(1), 16);
      return [ (n >> 16) & 255, (n >> 8) & 255, n & 255 ];
    }
    var m = v.match(/\d+/g);
    return m ? [+m[0], +m[1], +m[2]] : fallback;
  }

  function compute() {
    var d = +D.value, t = +T.value, useScale = scale.checked, useCausal = causal.checked;
    var f = useScale ? Math.sqrt(d) : 1;
    var rows = [];
    for (var i = 0; i < TOK.length; i++) {
      var logits = [], masked = [];
      for (var j = 0; j < TOK.length; j++) {
        if (useCausal && j > i) { logits.push(null); masked.push(true); continue; }
        var s = 0;
        for (var k = 0; k < d; k++) s += Q[i][k] * K[j][k];
        logits.push(s / f / t);
        masked.push(false);
      }
      var max = -Infinity;
      logits.forEach(function (v) { if (v !== null && v > max) max = v; });
      var sum = 0, ex = [];
      logits.forEach(function (v) { if (v === null) { ex.push(0); return; } var e = Math.exp(v - max); ex.push(e); sum += e; });
      rows.push({ p: ex.map(function (e) { return sum ? e / sum : 0; }), masked: masked, logits: logits });
    }
    return rows;
  }

  function render() {
    var rows = compute();
    var blue = rgbOf("--lab-blue", [53, 83, 255]);
    var html = '<div class="att-row"><div class="att-rowlabel" style="visibility:hidden">·</div>';
    TOK.forEach(function (t) { html += '<div class="att-head">' + t + "</div>"; });
    html += "</div>";

    rows.forEach(function (r, i) {
      html += '<div class="att-row' + (i === selected ? " sel-row" : "") + '"><div class="att-rowlabel">' + TOK[i] + "</div>";
      r.p.forEach(function (p, j) {
        if (r.masked[j]) {
          html += '<div class="att-cell masked' + (i === selected ? " sel-row" : "") + '" data-row="' + i + '" title="被掩码"></div>';
          return;
        }
        var a = 0.08 + p * 0.92;
        html += '<div class="att-cell on' + (i === selected ? " sel-row" : "") + '" style="background:rgba(' +
          blue.join(",") + "," + a.toFixed(3) + ')" title="' + TOK[i] + " → " + TOK[j] + ": " +
          (p * 100).toFixed(1) + '%" data-row="' + i + '"></div>';
      });
      html += "</div>";
    });
    grid.innerHTML = html;

    var selRow = rows[selected];
    var ps = selRow.p.filter(function (p, j) { return !selRow.masked[j]; });
    var maxP = Math.max.apply(null, ps);
    var ent = -ps.reduce(function (a, p) { return a + (p > 0 ? p * Math.log(p) : 0); }, 0);
    var eff = Math.exp(ent);
    $("atRowLabel").textContent = TOK[selected] + "（第 " + (selected + 1) + " 行）";
    $("atMax").textContent = (maxP * 100).toFixed(1) + "%";
    $("atEnt").textContent = ent.toFixed(2) + " nats";
    $("atN").textContent = eff.toFixed(1);
    var lv = selRow.logits.filter(function (v) { return v !== null; });
    var mean = lv.reduce(function (a, v) { return a + v; }, 0) / lv.length;
    var sig = Math.sqrt(lv.reduce(function (a, v) { return a + (v - mean) * (v - mean); }, 0) / lv.length);
    $("atSig").textContent = (isFinite(sig) ? sig.toFixed(2) : "0.00");
    $("atDOut").textContent = +D.value;
    $("atTOut").textContent = (+T.value).toFixed(2);

    var maxForBar = Math.max.apply(null, ps);
    bars.innerHTML = TOK.map(function (name, j) {
      var p = selRow.p[j], isMask = selRow.masked[j];
      var w = isMask ? 0 : (p / maxForBar) * 100;
      return '<div class="lab-bar-row"><span>' + name + '</span>' +
        '<div class="lab-bar thin"><i class="' + (isMask ? "seg-c" : "seg-a") + '" style="width:' + w + '%;' +
        (isMask ? "opacity:.18;" : "") + '"></i></div>' +
        '<span>' + (isMask ? "掩码" : (p * 100).toFixed(1) + "%") + "</span></div>";
    }).join("");

    $("atRowSel").value = String(selected);
    grid.onclick = function (e) {
      var cell = e.target.closest ? e.target.closest(".att-cell") : null;
      if (!cell) return;
      var row = +cell.getAttribute("data-row");
      if (!isNaN(row)) { selected = row; render(); }
    };
  }

  if (sel) sel.addEventListener("change", function () { selected = +sel.value; render(); });
  [D, T].forEach(function (el) { el.addEventListener("input", render); });
  [scale, causal].forEach(function (el) { el.addEventListener("change", render); });
  window.addEventListener("themechange", render);
  render();
})();
