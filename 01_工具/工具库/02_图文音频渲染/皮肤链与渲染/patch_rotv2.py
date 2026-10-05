"""按引擎机制重写旋转（✓ 学自 WeaponSkinPreview）：
   · 拖拽 = 跟随手指（on_touch_began ✓）
   · 松手 = 惯性续转（rotate_speed_x × rotate_time ✓ 带衰减）
   · 参数可在面板上调（速度/时长 ✓）
   · 默认不自动转（引擎只在拖拽时转 ✓）
"""
from pathlib import Path

HTML = Path(r'E:\la拆包项目\04_站点\web\skin_preview_v2.html')
t = HTML.read_text('utf-8')
BAK = HTML.with_suffix('.html.bak_before_rotv2')
if not BAK.is_file():
    BAK.write_text(t, encoding='utf-8')
    print('  ✓ 备份 .bak_before_rotv2')

# 面板：加"转速/惯性"控制
OLD_UI = """  <div class="row">
    <button id="bReset">官方默认</button>"""
NEW_UI = """  <div class="row"><span>转速</span><input id="rsp" type="range" min="0" max="3" step="0.05" value="1"><i class="val" id="vsp">1.0</i></div>
  <div class="row"><span>惯性</span><input id="rtm" type="range" min="0" max="2200" step="50" value="900"><i class="val" id="vtm">900</i></div>
  <div class="row">
    <button id="bReset">官方默认</button>"""
if OLD_UI in t:
    t = t.replace(OLD_UI, NEW_UI, 1)
    print('  ✓ ① 面板加"转速/惯性"')

# 旋转逻辑：换成引擎机制（拖拽 + 惯性）
OLD = """// 画布拖拽 = 旋转武器（左键 ✓）；滚轮 = 缩放（相机 ✓）
let _drag = false, _px = 0, _py = 0;
canvas.addEventListener('mousedown', (e) => { if (e.button === 0) { _drag = true; _px = e.clientX; _py = e.clientY; } });
window.addEventListener('mouseup', () => { _drag = false; });
window.addEventListener('mousemove', (e) => {
  if (!_drag || !WEAPON) return;
  const dx = e.clientX - _px, dy = e.clientY - _py; _px = e.clientX; _py = e.clientY;
  RY.value = ((parseFloat(RY.value) + dx * 0.5 + 540) % 360) - 180;
  RX.value = Math.max(-180, Math.min(180, parseFloat(RX.value) + dy * 0.5));
  applyRot();
});"""
NEW = """/* ★ 旋转 = 引擎机制（学自 WeaponSkinPreview ✓）：
     拖拽跟随 → 松手惯性续转（rotate_speed_x × rotate_time ✓ 指数衰减） */
const RSP = document.getElementById('rsp'), RTM = document.getElementById('rtm');
const VSP = document.getElementById('vsp'), VTM = document.getElementById('vtm');
RSP.addEventListener('input', () => { VSP.textContent = parseFloat(RSP.value).toFixed(1); });
RTM.addEventListener('input', () => { VTM.textContent = RTM.value; });

let _drag = false, _px = 0, _py = 0;
let _vx = 0, _vy = 0;            // 角速度（度/帧）
let _lastMoveT = 0, _lastDx = 0, _lastDy = 0;

canvas.addEventListener('mousedown', (e) => {
  if (e.button !== 0) return;
  _drag = true; _px = e.clientX; _py = e.clientY;
  _vx = _vy = 0;                 // ★ 按下即停惯性（引擎同 ✓）
  _lastMoveT = performance.now(); _lastDx = _lastDy = 0;
});
window.addEventListener('mouseup', () => { _drag = false; });
window.addEventListener('mousemove', (e) => {
  if (!_drag || !WEAPON) return;
  const sp = parseFloat(RSP.value) || 1;
  const dx = e.clientX - _px, dy = e.clientY - _py;
  _px = e.clientX; _py = e.clientY;
  RY.value = ((parseFloat(RY.value) + dx * 0.5 * sp + 540) % 360) - 180;
  RX.value = Math.max(-180, Math.min(180, parseFloat(RX.value) + dy * 0.5 * sp));
  applyRot();
  // 记录末速度（用于松手惯性 ✓）
  const now = performance.now();
  const dt = Math.max(1, now - _lastMoveT);
  _vx = (_vx * 0.6) + ((dx * 0.5 * sp) / dt * 16) * 0.4;
  _vy = (_vy * 0.6) + ((dy * 0.5 * sp) / dt * 16) * 0.4;
  _lastMoveT = now;
});
// 惯性衰减循环（rotate_time 决定衰减时长 ✓）
(function spinLoop() {
  requestAnimationFrame(spinLoop);
  if (!WEAPON || _drag) return;
  const life = parseFloat(RTM.value) || 900;     // rotate_time
  const k = Math.exp(-16.7 / Math.max(60, life));  // 每秒衰减到 ~0
  if (Math.abs(_vx) < 0.01 && Math.abs(_vy) < 0.01) { _vx = _vy = 0; return; }
  RY.value = ((parseFloat(RY.value) + _vx + 540) % 360) - 180;
  RX.value = Math.max(-180, Math.min(180, parseFloat(RX.value) + _vy));
  applyRot();
  _vx *= k; _vy *= k;
})();"""
if OLD in t:
    t = t.replace(OLD, NEW, 1)
    print('  ✓ ② 旋转改为引擎机制（拖拽 + 惯性 ✓）')
else:
    print('  ⚠ ② 锚点没匹配')

HTML.write_text(t, encoding='utf-8')
print('  写回 ✓ %d B' % len(t.encode('utf-8')))
