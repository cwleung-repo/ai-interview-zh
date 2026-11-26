/* Lab 02 · 微调显存预算 */
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var params = $("ftParams"), R = $("ftR"), S = $("ftS"), B = $("ftB"), ckpt = $("ftCkpt"), master = $("ftMaster");
  if (!params) return;

  var CFG = { "7": { L: 32, d: 4096 }, "13": { L: 40, d: 5120 }, "70": { L: 80, d: 8192 } };
  var CAPS = [24, 40, 80];

  function method() {
    var r = document.querySelector("input[name=ftMethod]:checked");
    return r ? r.value : "lora";
  }
  function stateBytes() {
    var r = document.querySelector("input[name=ftState]:checked");
    return r ? parseFloat(r.value) : 2;
  }
  function fmt(x) { return x >= 100 ? Math.round(x) + " GB" : x.toFixed(1) + " GB"; }

  function compute() {
    var N = parseFloat(params.value) * 1e9;
    var cfg = CFG[params.value];
    var m = method();
    var sb = stateBytes();
    var r = +R.value, s = +S.value, b = +B.value;

    var weights, grad, opt, adapter = 0;
    if (m === "full") {
      weights = 2 * N; grad = 2 * N; opt = 2 * N * sb;
      if (master && master.checked) weights += 4 * N; // fp32 主权重
    } else {
      weights = (m === "qlora" ? 0.53 : 2) * N;
      adapter = 8 * cfg.d * r * cfg.L * 2; // q/k/v/o 四个矩阵，各 A+B，bf16
      grad = adapter; opt = adapter * sb;
    }
    var act = b * s * cfg.d * cfg.L * 2 * 8;
    if (ckpt && ckpt.checked) act = act / 3;

    var W = weights / 1e9, G = grad / 1e9, O = opt / 1e9, A = act / 1e9;
    return { W: W, G: G, O: O, A: A, total: W + G + O + A, m: m };
  }

  function row(cap, d) {
    var total = d.total;
    var scale = Math.max(80, total * 1.12);
    var fit = total <= cap;
    var w = function (v) { return Math.max(0, Math.min(100, (v / scale) * 100)); };
    var left1 = w(d.W), left2 = left1 + w(d.G), left3 = left2 + w(d.O);
    return '<div class="lab-bar-row"><span>' + cap + ' GB</span>' +
      '<div class="lab-bar"><i class="seg-a" style="width:' + left1 + '%"></i>' +
      '<i class="seg-b" style="width:' + w(d.G) + '%;left:' + left1 + '%"></i>' +
      '<i class="seg-c" style="width:' + w(d.O) + '%;left:' + left2 + '%"></i>' +
      '<i class="seg-d" style="width:' + w(d.A) + '%;left:' + left3 + '%"></i>' +
      '<span class="lab-cap" style="left:' + Math.min(100, (cap / scale) * 100) + '%"></span></div>' +
      '<span><span class="lab-badge ' + (fit ? "ok" : "no") + '">' + (fit ? "放得下" : "超出") + '</span> ' +
      fmt(total) + '</span></div>';
  }

  function render() {
    var d = compute();
    $("ftROut").textContent = R.value;
    $("ftSOut").textContent = S.value;
    $("ftBOut").textContent = B.value;
    $("ftTotal").textContent = fmt(d.total);
    $("ftW").textContent = fmt(d.W);
    $("ftO").textContent = fmt(d.G + d.O);
    $("ftA").textContent = fmt(d.A);
    var fit = CAPS.filter(function (c) { return d.total <= c; })[0];
    $("ftFit").textContent = fit ? "1×" + fit + " GB" : "单卡装不下";
    $("ftChart").innerHTML = CAPS.map(function (cap) { return row(cap, d); }).join("");
  }

  document.querySelectorAll("input[name=ftMethod]").forEach(function (r) { r.addEventListener("change", render); });
  document.querySelectorAll("input[name=ftState]").forEach(function (r) { r.addEventListener("change", render); });
  [params, R, S, B, ckpt, master].forEach(function (el) { el.addEventListener("input", render); el.addEventListener("change", render); });
  render();
})();
