/* Lab 04 · 吞吐 roofline */
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var N = $("rfN"), BW = $("rfBW"), BATCH = $("rfB"), CTX = $("rfS"), svg = $("rfSvg");
  if (!N || !svg) return;

  var CFG = { "7": [32, 8], "70": [80, 8], "405": [126, 8] };
  var PEAK = { "2": 990, "1": 1979, "0.5": 990 }; // TFLOPS（INT4 权重仍以 bf16 计算）
  var BATCHES = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512];

  function prec() {
    var r = document.querySelector("input[name=rfPrec]:checked");
    return r ? parseFloat(r.value) : 2;
  }

  function model() {
    var n = parseFloat(N.value) * 1e9;
    var cfg = CFG[N.value];
    return { n: n, L: cfg[0], H: cfg[1] };
  }

  function tokensPerSec(m, bpt, bw, batch, seq) {
    var weightBytes = m.n * bpt;
    var kvPerToken = 2 * m.L * m.H * 128 * bpt;
    var bytes = weightBytes + kvPerToken * seq * batch;
    var flops = 2 * m.n * batch;
    var tMem = bytes / (bw * 1e12);
    var tComp = flops / (PEAK[String(bpt)] * 1e12);
    return { tok: batch / Math.max(tMem, tComp), mem: tMem, comp: tComp, bytes: bytes };
  }

  function fmtNum(x) {
    if (x >= 1e6) return (x / 1e6).toFixed(1) + "M";
    if (x >= 1e3) return (x / 1e3).toFixed(1) + "k";
    return Math.round(x);
  }

  function render() {
    var m = model();
    var bpt = prec();
    var bw = parseFloat(BW.value);
    var batch = parseInt(BATCH.value, 10);
    var seq = parseInt(CTX.value, 10) * 1000;

    $("rfBWOut").textContent = bw.toFixed(2) + " TB/s";
    $("rfBOut").textContent = batch;
    $("rfSOut").textContent = (seq / 1000) + "k";

    var cur = tokensPerSec(m, bpt, bw, batch, seq);
    var bound = cur.mem > cur.comp ? "带宽受限" : "算力受限";
    $("rfTok").textContent = fmtNum(cur.tok) + " tok/s";
    $("rfBytes").textContent = (cur.bytes / batch / 1e9).toFixed(2) + " GB";
    $("rfAI").textContent = (2 * m.n / (cur.bytes / batch)).toFixed(1) + " FLOP/B";
    $("rfBound").textContent = bound;

    var ys = BATCHES.map(function (b) { return tokensPerSec(m, bpt, bw, b, seq).tok; });
    var maxY = Math.max.apply(null, ys) * 1.08;
    var W = 640, H = 260, ml = 52, mr = 16, mt = 18, mb = 34;
    var x = function (i) { return ml + (i / (BATCHES.length - 1)) * (W - ml - mr); };
    var y = function (v) { return H - mb - (v / maxY) * (H - mt - mb); };

    var grid = "";
    for (var g = 0; g <= 4; g++) {
      var gv = (maxY / 4) * g, gy = y(gv);
      grid += '<line class="grid" x1="' + ml + '" y1="' + gy + '" x2="' + (W - mr) + '" y2="' + gy + '"/>' +
        '<text class="tick" x="' + (ml - 8) + '" y="' + (gy + 3) + '" text-anchor="end">' + fmtNum(gv) + '</text>';
    }
    var pts = ys.map(function (v, i) { return x(i) + "," + y(v); }).join(" ");
    var area = x(0) + "," + y(0) + " " + pts + " " + x(BATCHES.length - 1) + "," + y(0);
    var idx = BATCHES.indexOf(batch);
    var cx = x(idx), cy = y(ys[idx]);

    var ticks = "";
    [0, 3, 6, 8, 9].forEach(function (i) {
      ticks += '<text class="tick" x="' + x(i) + '" y="' + (H - 10) + '" text-anchor="middle">' + BATCHES[i] + '</text>';
    });

    svg.innerHTML = grid +
      '<polygon class="area" points="' + area + '"/>' +
      '<polyline class="line" points="' + pts + '"/>' +
      '<line class="axis" x1="' + ml + '" y1="' + (H - mb) + '" x2="' + (W - mr) + '" y2="' + (H - mb) + '"/>' +
      '<line class="axis" x1="' + ml + '" y1="' + mt + '" x2="' + ml + '" y2="' + (H - mb) + '"/>' +
      '<circle class="point" cx="' + cx + '" cy="' + cy + '" r="5"/>' +
      '<text class="lbl" x="' + (W - mr) + '" y="' + (mt + 10) + '" text-anchor="end">' + bound + '</text>' +
      ticks +
      '<text class="tick" x="' + (ml - 8) + '" y="' + (H - 10) + '" text-anchor="end">batch</text>';
  }

  [BW, BATCH, CTX, N].forEach(function (el) { el.addEventListener("input", render); el.addEventListener("change", render); });
  document.querySelectorAll("input[name=rfPrec]").forEach(function (r) { r.addEventListener("change", render); });
  render();
})();
