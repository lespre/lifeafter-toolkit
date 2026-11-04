// 3D 渲染研究 · 图表配置（ECharts）
(function () {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  var axisCommon = {
    axisLine: { lineStyle: { color: rule } },
    axisTick: { show: false },
    axisLabel: { color: muted, fontSize: 11 },
    splitLine: { lineStyle: { color: rule, type: 'dashed' } }
  };

  // --- 图 1 · 武器 KTX 内部格式 ---
  var ktx = echarts.init(document.getElementById('chart-ktx'), null, { renderer: 'svg' });
  ktx.setOption({
    animation: false,
    color: [accent, accent2, muted],
    tooltip: { trigger: 'item', appendToBody: true, valueFormatter: function (v) { return v + ' 张'; } },
    title: {
      text: '4,617 张',
      left: 'center',
      top: '38%',
      textAlign: 'center',
      textStyle: { color: ink, fontSize: 18, fontWeight: 700 }
    },
    legend: { bottom: 0, itemWidth: 10, itemHeight: 10, textStyle: { color: muted, fontSize: 11 } },
    series: [{
      type: 'pie',
      radius: ['42%', '66%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      label: { show: true, color: ink, fontSize: 11, formatter: '{d}%' },
      data: [
        { name: '0x9274 · ETC2 RGB8', value: 2364 },
        { name: '0x9278 · ETC2 RGBA8 EAC', value: 1391 },
        { name: '0x9272 · RG11 EAC（法线）', value: 862 }
      ]
    }]
  });
  window.addEventListener('resize', function () { ktx.resize(); });

  // --- 图 2 · 武器贴图尺寸 ---
  var size = echarts.init(document.getElementById('chart-size'), null, { renderer: 'svg' });
  var sizeData = [
    { name: '512²', value: 1669 },
    { name: '256²', value: 1201 },
    { name: '128²', value: 740 },
    { name: '64²', value: 593 },
    { name: '1024²', value: 62 }
  ];
  size.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true, axisPointer: { type: 'shadow' } },
    grid: { left: 58, right: 26, top: 18, bottom: 26 },
    xAxis: Object.assign({}, axisCommon, { type: 'value', axisLabel: { color: muted, fontSize: 11 } }),
    yAxis: Object.assign({}, axisCommon, { type: 'category', data: sizeData.map(function (d) { return d.name; }), splitLine: { show: false } }),
    series: [{
      type: 'bar',
      data: sizeData.map(function (d) { return d.value; }),
      barWidth: '55%',
      itemStyle: { color: accent, borderRadius: [0, 3, 3, 0] },
      label: { show: true, position: 'right', color: muted, fontSize: 10 }
    }]
  });
  window.addEventListener('resize', function () { size.resize(); });

  // --- 图 3 · 时装 GLB 体积 ---
  var glb = echarts.init(document.getElementById('chart-glb'), null, { renderer: 'svg' });
  var glbData = [
    { name: '3715_f（2025 合体）', value: 29.66 },
    { name: '3640_m（2025 合体）', value: 9.03 },
    { name: '3223_f（2021 分件）', value: 2.76 },
    { name: '3245_f（2021 分件）', value: 2.64 },
    { name: '3301_f（2021 整套）', value: 1.23 }
  ];
  glb.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true, axisPointer: { type: 'shadow' }, valueFormatter: function (v) { return v + ' MB'; } },
    grid: { left: 168, right: 46, top: 16, bottom: 26 },
    xAxis: Object.assign({}, axisCommon, { type: 'value', axisLabel: { color: muted, fontSize: 11, formatter: '{value} MB' } }),
    yAxis: Object.assign({}, axisCommon, { type: 'category', data: glbData.map(function (d) { return d.name; }), splitLine: { show: false }, axisLabel: { color: ink, fontSize: 11 } }),
    series: [{
      type: 'bar',
      data: glbData.map(function (d) { return d.value; }),
      barWidth: '52%',
      itemStyle: { color: accent2, borderRadius: [0, 3, 3, 0] },
      label: { show: true, position: 'right', color: muted, fontSize: 10, formatter: '{c} MB' }
    }]
  });
  window.addEventListener('resize', function () { glb.resize(); });

  // --- 图 4 · 着色器族 ---
  var shader = echarts.init(document.getElementById('chart-shader'), null, { renderer: 'svg' });
  var shaderData = [
    { name: 'pbr_weapon', value: 1562 },
    { name: 'pbr_default', value: 264 },
    { name: 'pbr_crystal', value: 40 },
    { name: 'pbr_transparent', value: 34 }
  ];
  shader.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true, axisPointer: { type: 'shadow' } },
    grid: { left: 118, right: 58, top: 16, bottom: 26 },
    xAxis: Object.assign({}, axisCommon, { type: 'value' }),
    yAxis: Object.assign({}, axisCommon, { type: 'category', data: shaderData.map(function (d) { return d.name; }), splitLine: { show: false }, axisLabel: { color: ink, fontSize: 11 } }),
    series: [{
      type: 'bar',
      data: shaderData.map(function (d) { return d.value; }),
      barWidth: '52%',
      itemStyle: { color: accent, borderRadius: [0, 3, 3, 0] },
      label: { show: true, position: 'right', color: muted, fontSize: 10 }
    }]
  });
  window.addEventListener('resize', function () { shader.resize(); });

  // --- 图 5 · IBL cube 声明频次 ---
  var cube = echarts.init(document.getElementById('chart-cube'), null, { renderer: 'svg' });
  var cubeData = [
    { name: 'car_studio01', value: 14 },
    { name: 'qiangpi', value: 10 },
    { name: 'glazed_patio', value: 7 },
    { name: 'glazed_patio2', value: 3 },
    { name: 'industrial_pipe', value: 2 },
    { name: 'over_the_clouds', value: 2 },
    { name: 'fashion_qiangpi', value: 1 }
  ];
  cube.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true, axisPointer: { type: 'shadow' } },
    grid: { left: 118, right: 40, top: 16, bottom: 26 },
    xAxis: Object.assign({}, axisCommon, { type: 'value', minInterval: 1 }),
    yAxis: Object.assign({}, axisCommon, { type: 'category', data: cubeData.map(function (d) { return d.name; }), splitLine: { show: false }, axisLabel: { color: ink, fontSize: 11 } }),
    series: [{
      type: 'bar',
      data: cubeData.map(function (d) { return d.value; }),
      barWidth: '52%',
      itemStyle: { color: accent2, borderRadius: [0, 3, 3, 0] },
      label: { show: true, position: 'right', color: muted, fontSize: 10 }
    }]
  });
  window.addEventListener('resize', function () { cube.resize(); });
})();
