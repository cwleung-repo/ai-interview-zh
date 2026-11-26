/* Lab 03 · 采样实验室 */
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var T = $("smT"), K = $("smK"), P = $("smP"), chart = $("smChart"), samples = $("smSamples");
  if (!T || !chart) return;

  var TOKENS = ["巴黎", "伦敦", "罗马", "柏林", "马德里", "维也纳", "布拉格", "里斯本", "雅典", "华沙", "布达佩斯", "其他"];
  var LOGITS = [4.2, 3.7, 3.1, 2.6, 2.1, 1.5, 1.0, 0.5, 0.1, -0.4, -0.9, -1.6];
  var current = [];

  function softmax(z, t) {
    var max = Math.max.apply(null, z);
    var ex = z.map(function (v) { return Math.exp((v - max) / t); });
    var sum = ex.reduce(function (a, b) { return a + b; }, 0);
    return ex.map(function (v) { return v / sum; });
  }

  function compute() {
    var t = parseFloat(T.value);
    var k = parseInt(K.value, 10);
    var p = parseFloat(P.value);

    var base = softmax(LOGITS, t);
    var order = base.map(function (v, i) { return { i: i, p: v }; })
      .sort(function (a, b) { return b.p - a.p; });

    var kept = order.slice(0, k);
    var keptSum = kept.reduce(function (a, b) { return a + b.p; }, 0);
    // top-p: 按累积概率保留，至少保留 1 个
    var cum = 0, cut = [];
    var finalists = [];
    kept.forEach(function (o) {
      var np = o.p / keptSum;
      // 前缀式 nucleus：一直保留到累积概率 >= p（保留跨过 p 的那个 token）
      if (p >= 1 || cum < p || finalists.length === 0) {
        finalists.push({ i: o.i, p: np });
        cum += np;
      } else {
        cut.push(o.i);
      }
    });
    // 最后一并重归一化
    var fsum = finalists.reduce(function (a, b) { return a + b.p; }, 0);
    finalists.forEach(function (f) { f.p = f.p / fsum; });

    var byIndex = {};
    finalists.forEach(function (f) { byIndex[f.i] = f.p; });
    return { finalists: finalists, cut: cut, byIndex: byIndex };
  }

  function render() {
    var r = compute();
    var max = Math.max.apply(null, r.finalists.map(function (f) { return f.p; }));
    var ent = -r.finalists.reduce(function (a, f) { return a + f.p * Math.log(f.p); }, 0);
    if (Math.abs(ent) < 1e-9) ent = 0;

    $("smTOut").textContent = parseFloat(T.value).toFixed(2);
    $("smKOut").textContent = K.value;
    $("smPOut").textContent = parseFloat(P.value).toFixed(2);
    $("smN").textContent = r.finalists.length + " / 12";
    $("smMax").textContent = (max * 100).toFixed(1) + "%";
    $("smEnt").textContent = ent.toFixed(2) + " nats";

    chart.innerHTML = TOKENS.map(function (name, i) {
      var p = r.byIndex[i];
      var kept = p !== undefined;
      var width = kept ? (p / max) * 100 : 100;
      var style = kept ? "" : "opacity:.18;";
      return '<div class="lab-bar-row"><span>' + name + '</span>' +
        '<div class="lab-bar thin"><i class="' + (kept ? "seg-a" : "seg-c") + '" style="width:' +
        width + '%;' + style + '"></i></div>' +
        '<span>' + (kept ? (p * 100).toFixed(1) + "%" : "截断") + '</span></div>';
    }).join("");

    current = r.finalists;
  }

  function draw() {
    if (!current.length) return;
    var cum = [], acc = 0;
    current.forEach(function (f) { acc += f.p; cum.push(acc); });
    var out = [];
    var counts = {};
    for (var n = 0; n < 30; n++) {
      var u = Math.random(), pick = current[current.length - 1];
      for (var i = 0; i < cum.length; i++) { if (u <= cum[i]) { pick = current[i]; break; } }
      out.push(pick.i);
      counts[pick.i] = (counts[pick.i] || 0) + 1;
    }
    samples.innerHTML = out.map(function (i) {
      var top = counts[i] >= 5 ? " class=\"hit\"" : "";
      return "<span" + top + ">" + TOKENS[i] + "</span>";
    }).join("");
  }

  [T, K, P].forEach(function (el) { el.addEventListener("input", function () { render(); }); });
  $("smDraw").addEventListener("click", draw);
  render();
})();
