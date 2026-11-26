/* Lab 01 · KV 缓存计算器 */
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var L = $("kvL"), H = $("kvH"), S = $("kvS"), B = $("kvB"), model = $("kvModel");
  if (!L || !model) return;

  var CONFIG = { "8": [32, 8, 128], "13": [40, 40, 128], "70": [80, 8, 128], "405": [126, 8, 128] };
  var CAPS = [24, 40, 80, 192];

  function dtype() {
    var r = document.querySelector("input[name=kvdtype]:checked");
    return r ? parseFloat(r.value) : 2;
  }

  function paramsB() { return model.value.split(",")[0]; }

  function read() {
    return {
      params: parseFloat(paramsB()),
      L: +L.value,
      H: +H.value,
      S: +S.value * 1000,
      B: +B.value,
      bpt: dtype()
    };
  }

  function fmtGB(x) {
    return x >= 100 ? Math.round(x) + " GB" : x.toFixed(1) + " GB";
  }

  function barRow(cap, parts, scale) {
    var total = parts.weights + parts.kv + parts.other;
    var fit = total <= cap;
    var w = function (v) { return Math.max(0, Math.min(100, (v / scale) * 100)); };
    var capLeft = (cap / scale) * 100;
    return '<div class="lab-bar-row"><span>' + cap + ' GB</span>' +
      '<div class="lab-bar"><i class="seg-a" style="width:' + w(parts.weights) + '%"></i>' +
      '<i class="seg-b" style="width:' + w(parts.kv) + '%;left:' + w(parts.weights) + '%"></i>' +
      '<i class="seg-d" style="width:' + w(parts.other) + '%;left:' + w(parts.weights + parts.kv) + '%"></i>' +
      '<span class="lab-cap" style="left:' + capLeft + '%"></span></div>' +
      '<span><span class="lab-badge ' + (fit ? "ok" : "no") + '">' + (fit ? "放得下" : "超出") + '</span> ' +
      fmtGB(total) + '</span></div>';
  }

  function render() {
    var d = read();
    var perToken = 2 * d.L * d.H * 128 * d.bpt;
    var kvGB = (perToken * d.S * d.B) / 1e9;
    var weightsGB = d.params * d.bpt;
    var otherGB = 1 + (weightsGB + kvGB) * 0.08; // 固定开销 + 8%
    var total = weightsGB + kvGB + otherGB;
    var scale = Math.max(Math.max.apply(null, CAPS), total * 1.12);

    $("kvLOut").textContent = d.L;
    $("kvHOut").textContent = d.H;
    $("kvSOut").textContent = (d.S / 1000) + "k";
    $("kvBOut").textContent = d.B;
    $("kvPerToken").textContent = Math.round(perToken / 1024) + " KiB";
    $("kvTotal").textContent = fmtGB(kvGB);
    $("kvWeights").textContent = fmtGB(weightsGB);
    $("kvAll").textContent = fmtGB(total);

    $("kvChart").innerHTML = CAPS.map(function (cap) {
      return barRow(cap, { weights: weightsGB, kv: kvGB, other: otherGB }, scale);
    }).join("");
  }

  function syncModel() {
    var cfg = CONFIG[paramsB()];
    if (!cfg) return;
    L.value = cfg[0]; H.value = cfg[1];
  }
  model.addEventListener("change", function () { syncModel(); render(); });

  [L, H, S, B].forEach(function (el) { el.addEventListener("input", render); });
  document.querySelectorAll("input[name=kvdtype]").forEach(function (r) {
    r.addEventListener("change", render);
  });
  syncModel();
  render();
})();
