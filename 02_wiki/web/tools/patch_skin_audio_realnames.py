# -*- coding: utf-8 -*-
"""board.html：皮肤音效区补「真名（内部名）」展示。"""
from __future__ import annotations

import pathlib

P = pathlib.Path("E:/la拆包项目/02_wiki/web/board.html")
OLD_START = "function renderSkinAudio(it){"
OLD_END = "  return `<details class=\"audio\"><summary>皮肤音效 ${n} 条</summary>${groups}`+\n    `<div class=\"audio-note\">音频由客户端音频库静态提取；含义为人工听辨标注，仅供试听参考。</div></details>`;\n}"

NEW = r'''function renderSfxRealNames(it){
  const names=Array.isArray(it.sfx_real_names)?it.sfx_real_names:[];
  const state=it.sfx_audio_state||"";
  if(!names.length)return "";
  const rows=names.map(n=>`<li class="audio-row" title="${esc(n)}"><code class="sfx-real">${esc(n)}</code></li>`).join("");
  return `<div class="audio-group">音效真名（内部名）${names.length} 条${state?" · "+esc(state):""}</div>`+
    `<ul class="audio-list">${rows}</ul>`;
}
function renderSkinAudio(it){
  const names=(Array.isArray(it.sfx_real_names)?it.sfx_real_names:[]);
  const bank=(window.WEAPON_SKIN_AUDIO_ATTACHMENTS||{}).skins||{};
  const rec=bank[String(it.skin_id??it.id??"")];
  const hasFiles=rec&&Array.isArray(rec.groups)&&rec.groups.length;
  if(!hasFiles&&!names.length)return "";
  let n=0;
  const groups=hasFiles?rec.groups.map(g=>{
    const items=g.items||[];n+=items.length;
    const rows=items.map(x=>{
      const pend=x.pending?'<i class="pres-mark">待确认</i>':"";
      const stem=String(x.file||"").replace(/\.wav$/i,"");
      const src="assets/audio/weapon_skin/"+(g.dir||rec.dir)+"/"+x.file;
      return `<li class="audio-row" title="${esc(x.file)}"><span class="audio-label">${esc(x.label||"音效")}</span>`+
        `<code class="sfx-real">${esc(stem)}</code>${pend}<audio controls preload="metadata" src="${esc(src)}"></audio></li>`;
    }).join("");
    return (g.label?`<div class="audio-group">${esc(g.label)}</div>`:"")+`<ul class="audio-list">${rows}</ul>`;
  }).join(""):"";
  const head=hasFiles?`皮肤音效 ${n} 条`:"皮肤音效";
  return `<details class="audio"><summary>${head}${names.length?" · 真名 "+names.length+" 条":""}</summary>`+
    renderSfxRealNames(it)+groups+
    `<div class="audio-note">真名取自带内联键值对的音效查询表，内部名原样保留；音频为客户端音频库静态提取，含义为人工听辨标注，仅供试听参考。</div></details>`;
}'''


def main() -> int:
    s = P.read_text(encoding="utf-8")
    i = s.find(OLD_START)
    j = s.find(OLD_END, i)
    if i < 0 or j < 0:
        raise SystemExit("锚点未命中 i=%d j=%d" % (i, j))
    j += len(OLD_END)
    out = s[:i] + NEW + s[j:]
    if "renderSfxRealNames" not in out:
        raise SystemExit("写出失败")
    P.write_text(out, encoding="utf-8")
    print("renderSkinAudio 已替换，新增 renderSfxRealNames")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
