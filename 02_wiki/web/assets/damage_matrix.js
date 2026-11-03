/* （六）伤害计算四板块 · 矩阵表视图（B 方案，攻击力/加成附折线图）2026-11-04 */
(function () {
  var bid = (function () { try { return new URLSearchParams(location.search).get('b') || ''; } catch (e) { return ''; } })();
  var CFG = {
    damage_attack: { chart: 'attack' },
    damage_bonus: { chart: 'bonus' },
    damage_defense: {}
  };
  if (!CFG[bid]) return;

  // 2026-11-04 用户反馈「色调不对」：这套表格/图原来是浅色硬编码（#fff 底 + 深蓝字），
  // 在深色站点里是块白板。改成全部走主题变量，跟随站点明暗。
  var CSS = ''
    + '.dm-wrap{margin:14px 0 8px}'
    + '.dm-note{font-size:12px;color:var(--muted-foreground,#8a94a6);margin:8px 0 16px}'
    + '.dm-tab{width:100%;border-collapse:collapse;font-size:13px;background:var(--card,#141a24);color:var(--foreground,#e7eaf4)}'
    + '.dm-tab th,.dm-tab td{border:1px solid var(--border,#2a3444);padding:7px 9px;vertical-align:middle}'
    + '.dm-tab thead th{background:rgba(255,255,255,.06);font-size:12.5px;color:var(--foreground,#e7eaf4);font-weight:600;text-align:left}'
    + '.dm-tab td.num{text-align:center;font-variant-numeric:tabular-nums;font-size:13.5px}'
    + '.dm-tab .win{color:#4ade80;font-weight:600}'
    + '.dm-tab .tight{color:#fb923c;font-weight:600}'
    + '.dm-tab .none{color:var(--muted-foreground,#8a94a6)}'
    + '.dm-tab tr:hover td{background:rgba(255,255,255,.035)}'
    + '.dm-lg{font-size:11.5px;color:var(--muted-foreground,#8a94a6);margin-top:8px}'
    + '.dm-chart{background:var(--card,#141a24);border:1px solid var(--border,#2a3444);border-radius:10px;padding:10px 12px 6px;margin:18px 0 6px}'
    + '.dm-chart h4{margin:2px 0 4px;font-size:13.5px;color:var(--foreground,#e7eaf4)}'
    + '.dm-chart .sub{font-size:11.5px;color:var(--muted-foreground,#8a94a6);margin-bottom:4px}'
    + '.dm-chart svg text{fill:var(--muted-foreground,#8a94a6)}'
    + '.dm-chart svg .dm-title{fill:var(--foreground,#e7eaf4);font-weight:600}'
    + '.dm-chart svg line{stroke:var(--border,#2a3444)}'
    + '.dm-legend{display:flex;gap:16px;font-size:11.5px;color:var(--muted-foreground,#8a94a6);margin:2px 0 6px;flex-wrap:wrap}'
    + '.dm-legend i{display:inline-block;width:16px;height:2px;margin-right:5px;vertical-align:middle}'
    + '.dm-sec{font-size:13px;color:var(--muted-foreground,#8a94a6);margin:20px 0 6px;font-weight:600}';

  var ATTACK = {
    head: ['场景', '经典断点', '简单断点', '月卡', 'x=50 经典 / 简单 / 月卡', 'x=100 经典 / 简单 / 月卡'],
    rows: [
      ['远星城 23', '30/50/70/100', '30/50/70/100', '无行（不压缩）', ['44', '44', 'win:50'], ['63', '63', 'win:100']],
      ['远星城 448', 'tight:20/25/30', '无行（不压缩）', '无行（不压缩）', ['21', '50', '50'], ['tight:20.8', 'win:100', 'win:100']],
      ['远星城 698', '30/40/60', '35/60/80', '无行（不压缩）', ['37', '44', '50'], ['38.4', 'win:52.2', '100']],
      ['夏尔镇 6 / 799 / 19 / 20', '30/50/70/100', '50/60/70/100', '无行（不压缩）', ['44', 'win:50', '50'], ['63', 'win:71', '100']],
      ['夏尔镇 304 / 305', '30/50/70/100', '30/50/70/100', '无行（不压缩）', ['44', '44', '50'], ['63', '63', '100']]
    ],
    legend: '月卡在以上场景均无专属行 → 回退全局 hurt_params_data（该表无 source_hurt 列）→ 攻击力不做折线压缩，数值即原值。'
  };

  var BONUS = {
    head: ['场景', '服型', '+20%', '+40%', '+60%', '+80%', '净 0.6（加成对减免）'],
    rows: [
      ['远星城 23', '经典服', '1.20', '1.34', '1.42', '1.47', 'tight:0.75'],
      ['', '简单生存服', '1.10', '1.20', '1.30', '1.40', '0.80'],
      ['', '月卡服', '1.20', '1.40', '1.60', '1.80', '0.60'],
      ['远星城 448', '经典服', '1.02', '1.04', '1.05', '1.05', '1.00'],
      ['', '简单生存服', '1.20', '1.40', '1.60', '1.80', '0.60'],
      ['', '月卡服', '1.20', '1.40', '1.60', '1.80', '0.60'],
      ['远星城 698', '经典服', '1.14', '1.24', '1.27', '1.27', '0.80'],
      ['', '简单生存服', '1.10', '1.20', '1.30', '1.40', '0.80'],
      ['', '月卡服', '1.20', '1.40', '1.60', '1.80', '0.60'],
      ['夏尔镇 6 / 799 / 19 / 20', '经典服', '1.20', '1.34', '1.42', '1.47', '0.80'],
      ['', '简单生存服', '1.10', '1.20', '1.30', '1.40', '0.80'],
      ['', '月卡服', '1.20', '1.40', '1.60', '1.80', '0.60'],
      ['夏尔镇 304 / 305', '经典服', '1.20', '1.40', '1.60', '1.60', '0.60'],
      ['', '简单生存服', '1.10', '1.20', '1.30', '1.40', '0.60'],
      ['', '月卡服', '1.20', '1.40', '1.60', '1.80', '0.60']
    ],
    legend: 'rate ≤ 1 时负数不过曲线，只受窗口下限：夏尔镇两服下限 0.80（304/305 为 0.60），月卡回退全局后为 0.50。'
  };

  var DEFENSE = {
    head: ['曲线', '经典服', '简单生存服', '月卡服', '是否分服'],
    rows: [
      ['b_class', '0/0.8 · 0.8/1.0 · 1.0+', '同左', '同左', 'win:一致'],
      ['c_class', '0/1.0 · 1.0/1.2 · 1.2+', '同左', '同左', 'win:一致'],
      ['HP 百分比上限', '同函数', '同左', '同左', 'win:一致']
    ],
    legend: '守方侧不产生跨服差异；差异只可能来自玩家身上的增伤/减伤桶。注意：加成环节里的「守方减免」是 player_hurt_reduction_rate，与这里的「目标减伤桶」不是同一个量。'
  };

  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function cellText(v) {
    var m = /^(win|tight|none):(.+)$/.exec(String(v));
    if (m) return '<span class="' + m[1] + '">' + esc(m[2]) + '</span>';
    return esc(v);
  }
  function renderTable(d) {
    var h = '<div class="dm-wrap"><table class="dm-tab"><thead><tr>';
    d.head.forEach(function (x) { h += '<th>' + esc(x) + '</th>'; });
    h += '</tr></thead><tbody>';
    d.rows.forEach(function (r, ri) {
      h += '<tr>';
      var span = 1;
      if (r[0]) { while (d.rows[ri + span] && !d.rows[ri + span][0]) span += 1; }
      r.forEach(function (c, i) {
        if (i === 0 && !c) return;
        var rs = (i === 0 && span > 1) ? ' rowspan="' + span + '"' : '';
        if (Array.isArray(c)) {
          h += '<td class="num"' + rs + '>' + c.map(cellText).join(' / ') + '</td>';
        } else if (i === 0) {
          h += '<td' + rs + '>' + cellText(c) + '</td>';
        } else {
          h += '<td class="num">' + cellText(c) + '</td>';
        }
      });
      h += '</tr>';
    });
    h += '</tbody></table><div class="dm-lg">' + esc(d.legend) + '</div></div>';
    return h;
  }

  function svg(title, sub, series, xdom, ydom, xlabel, ylabel, note) {
    var W = 900, H = 360, L = 64, R = 18, T = 42, Bc = 54;
    var pw = W - L - R, ph = H - T - Bc;
    function sx(x) { return L + (x - xdom[0]) / (xdom[1] - xdom[0]) * pw; }
    function sy(y) { return T + ph - (y - ydom[0]) / (ydom[1] - ydom[0]) * ph; }
    var p = ['<svg viewBox="0 0 ' + W + ' ' + H + '" style="width:100%;height:auto">'];
    var i, j;
    for (i = 0; i <= 5; i++) {
      var xv = xdom[0] + (xdom[1] - xdom[0]) * i / 5;
      p.push('<line x1="' + sx(xv).toFixed(1) + '" y1="' + T + '" x2="' + sx(xv).toFixed(1) + '" y2="' + (T + ph) + '" stroke="#eef2f8"/>');
      p.push('<text x="' + sx(xv).toFixed(1) + '" y="' + (T + ph + 16) + '" font-size="11" text-anchor="middle">' + (Math.round(xv * 100) / 100) + '</text>');
    }
    for (j = 0; j <= 4; j++) {
      var yv = ydom[0] + (ydom[1] - ydom[0]) * j / 4;
      p.push('<line x1="' + L + '" y1="' + sy(yv).toFixed(1) + '" x2="' + (L + pw) + '" y2="' + sy(yv).toFixed(1) + '" stroke="#eef2f8"/>');
      p.push('<text x="' + (L - 8) + '" y="' + (sy(yv) + 4).toFixed(1) + '" font-size="11" text-anchor="end">' + (Math.round(yv * 100) / 100) + '</text>');
    }
    p.push('<line x1="' + L + '" y1="' + (T + ph) + '" x2="' + (L + pw) + '" y2="' + (T + ph) + '"/>');
    p.push('<line x1="' + L + '" y1="' + T + '" x2="' + L + '" y2="' + (T + ph) + '"/>');
    p.push('<text x="' + (L + pw / 2) + '" y="' + (H - 8) + '" font-size="12" text-anchor="middle">' + esc(xlabel) + '</text>');
    p.push('<text x="16" y="' + (T + ph / 2) + '" font-size="12" text-anchor="middle" transform="rotate(-90 16 ' + (T + ph / 2) + ')">' + esc(ylabel) + '</text>');
    series.forEach(function (s) {
      var pts = [];
      s.segs.forEach(function (g) {
        var a = g[0], b = g[1] == null ? xdom[1] : g[1], k = g[2], o = g[3];
        var lo = Math.max(a, xdom[0]), hi = Math.min(b, xdom[1]);
        if (hi < lo) return;
        pts.push([lo, k * lo + o]);
        pts.push([hi, k * hi + o]);
      });
      var d = pts.map(function (q) {
        var y = Math.max(ydom[0], Math.min(ydom[1], q[1]));
        return sx(q[0]).toFixed(1) + ',' + sy(y).toFixed(1);
      }).join(' ');
      p.push('<polyline points="' + d + '" fill="none" stroke="' + s.color + '" stroke-width="2"' + (s.dash ? ' stroke-dasharray="5 4"' : '') + '/>');
    });
    p.push('<text x="' + L + '" y="20" font-size="13" class="dm-title">' + esc(title) + '</text>');
    if (sub) p.push('<text x="' + L + '" y="34" font-size="11">' + esc(sub) + '</text>');
    p.push('</svg>');
    var lg = '<div class="dm-legend">' + series.map(function (s) {
      return '<span><i style="background:' + s.color + '"></i>' + esc(s.name) + '</span>';
    }).join('') + '</div>';
    return '<div class="dm-chart">' + lg + p.join('') + (note ? '<div class="dm-lg">' + esc(note) + '</div>' : '') + '</div>';
  }

  function attackChart() {
    return svg('夏尔镇 6 · 攻击力压缩（横轴=input，纵轴=压缩后攻击力）',
      '经典 30 起压，简单 50 起压；月卡无分段列，沿 y = x',
      [
        { name: '经典服', color: '#5b9df9', segs: [[0, 30, 1, 0], [30, 50, 0.7, 9], [50, 70, 0.5, 19], [70, 100, 0.3, 33], [100, null, 0.1, 53]] },
        { name: '简单生存服', color: '#fb923c', segs: [[0, 50, 1, 0], [50, 60, 0.7, 15], [60, 70, 0.5, 27], [70, 100, 0.3, 41], [100, null, 0.1, 61]] },
        { name: '月卡服（不压缩）', color: '#4ade80', segs: [[0, null, 1, 0]], dash: true }
      ], [0, 120], [0, 120], '输入攻击力', '压缩后攻击力',
      '同输入 x=50 → 44 / 50 / 50；x=100 → 63 / 71 / 100。');
  }

  function bonusChart() {
    return svg('夏尔镇 6 · 加成映射（横轴=原始 rate，纵轴=生效 rate）',
      'rate ≤ 1 段三服都沿 y = x（负数不过曲线）',
      [
        { name: 'y = x（不压缩）', color: '#6b7280', segs: [[0.6, 2.2, 1, 0]], dash: true },
        { name: '月卡（全局默认）', color: '#4ade80', segs: [[1, 2, 1, 0], [2, 2.2, 0.3, 1.4], [2.2, 2.5, 0.2, 1.62], [2.5, null, 0.1, 1.97]], dash: true },
        { name: '简单生存 p2p', color: '#fb923c', segs: [[1, 2.1, 0.5, 0.5], [2.1, null, 0.1, 1.34]] },
        { name: '经典服 p2p', color: '#5b9df9', segs: [[1, 1.2, 1, 0], [1.2, 1.4, 0.7, 0.36], [1.4, 1.6, 0.4, 0.78], [1.6, 2, 0.25, 1.02], [2, null, 0.1, 1.32]] }
      ], [0.6, 2.2], [0.6, 2.2], '原始 rate（加成 − 减免）', '生效 rate',
      '原始 1.6：经典 1.42 / 简单 1.30 / 月卡 1.60；净 0.8 时三服都是 0.80。');
  }

  function build() {
    var grid = document.getElementById('grid');
    if (!grid) return;
    var host = document.getElementById('dmHost');
    if (!host) {
      host = document.createElement('div');
      host.id = 'dmHost';
      grid.parentNode.insertBefore(host, grid);
    }
    var h = '';
    if (bid === 'damage_attack') h = renderTable(ATTACK) + attackChart();
    else if (bid === 'damage_bonus') h = renderTable(BONUS) + bonusChart();
    else h = renderTable(DEFENSE);
    host.innerHTML = h;
    grid.style.display = 'none';
    var cnt = document.getElementById('count'); if (cnt) cnt.style.display = 'none';
  }

  var st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
  document.addEventListener('DOMContentLoaded', function () { setTimeout(build, 60); });
  setTimeout(build, 400);
})();
