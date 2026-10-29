# -*- coding: utf-8 -*-
r"""修正 wiki 渲染：每个大类一个瓦片网格（原来每个叶子节点各一格，导致一列一个）。"""
from __future__ import annotations
import sys

import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

P = pathlib.Path(WEB / "wiki.html")

NEW = r'''  function collect(node, path, out){
    var p2 = path ? (path + ' · ' + node.name) : node.name;
    var i;
    for(i=0;i<(node.boards||[]).length;i++){
      var nm = node.boards[i];
      if(byId[nm]) out.push([nm, byId[nm], false, p2]);
      else if(showArchived && pol[nm]) out.push([nm, {name:nm}, true, p2]);
    }
    for(i=0;i<(node.children||[]).length;i++) collect(node.children[i], p2, out);
  }

  function render(){
    host.innerHTML = '';
    navSide.innerHTML = '';
    navTop.innerHTML = '';
    allTiles.length = 0;

    var tops = T['树'] || [];
    tops.forEach(function(top, i){
      var sec = document.createElement('section');
      sec.className = 'wp-cat';
      sec.id = 'cat-' + (i + 1);

      var num = top.name.match(/^([零一二三四五六七八九十]+)、/);
      var h2 = document.createElement('h2');
      var no = document.createElement('span'); no.className = 'no';
      no.textContent = num ? num[1] : String(i + 1);
      var ti = document.createElement('span');
      ti.textContent = top.name.replace(/^[零一二三四五六七八九十]+、/, '');
      var cn = document.createElement('span'); cn.className = 'cnt'; cn.textContent = badge(top);
      h2.appendChild(no); h2.appendChild(ti); h2.appendChild(cn);
      sec.appendChild(h2);

      var list = [];
      for(var bi=0; bi<(top.boards||[]).length; bi++){
        var nm0 = top.boards[bi];
        if(byId[nm0]) list.push([nm0, byId[nm0], false, '']);
        else if(showArchived && pol[nm0]) list.push([nm0, {name:nm0}, true, '']);
      }
      for(var ci=0; ci<(top.children||[]).length; ci++){
        collect(top.children[ci], '', list);
      }
      if(!list.length && top.placeholder){
        list.push([null, null, false, '']);
      }

      var g = document.createElement('div');
      g.className = 'tiles';
      for(var li=0; li<list.length; li++){
        var e = list[li];
        if(e[0]) g.appendChild(tile(e[0], e[1], e[2], e[3]));
        else g.appendChild(phTile(top.note));
      }
      sec.appendChild(g);
      host.appendChild(sec);

      var label = top.name.replace(/^[零一二三四五六七八九十]+、/, '');
      var a1 = document.createElement('a');
      a1.href = '#cat-' + (i + 1);
      var b1 = document.createElement('b'); b1.textContent = num ? num[1] : String(i + 1);
      var i1 = document.createElement('i'); i1.textContent = tally(top).boards;
      a1.appendChild(b1); a1.appendChild(document.createTextNode(' ' + label)); a1.appendChild(i1);
      navSide.appendChild(a1);

      var a2 = document.createElement('a');
      a2.href = '#cat-' + (i + 1);
      a2.textContent = label;
      navTop.appendChild(a2);
    });

    var boards = Object.keys(byId).length;
    var items = 0;
    for(var x=0;x<M.boards.length;x++) items += (M.boards[x].items || 0);
    document.getElementById('statBoards').textContent = boards;
    document.getElementById('statItems').textContent = items.toLocaleString('en-US');
    document.getElementById('statCats').textContent = tops.length;

    var pc = {};
    Object.keys(pol).forEach(function(k){
      var st = pol[k].publication_status;
      pc[st] = (pc[st] || 0) + 1;
    });
    document.getElementById('gen').textContent =
      '公开 ' + boards + ' · 隔离 ' + (pc.quarantined || 0) + ' · 退休 ' + (pc.retired || 0) +
      ' · 未发布 ' + (pc.unpublished || 0);

    filterHome();
  }

  document.getElementById('homeSearch').addEventListener('input', filterHome);
  document.getElementById('clearSearch').addEventListener('click', function(){
    document.getElementById('homeSearch').value = '';
    filterHome();
  });
  document.getElementById('showArchived').addEventListener('change', function(e){
    showArchived = e.target.checked;
    render();
  });

  render();
})();
'''


def main() -> int:
    h = P.read_text(encoding="utf-8")
    i = h.find("  function nodeBlock(node, depth){")
    if i < 0:
        print("找不到 nodeBlock")
        return 1
    j = h.rfind("})();")
    h = h[:i] + NEW + h[j + len("})();"):]
    # tile() 增加 path 参数
    h = h.replace("function tile(nm, b, arch){", "function tile(nm, b, arch, path){")
    h = h.replace("a.setAttribute('data-search', (cleanTitle(b, nm) + ' ' + nm + ' ' + ((b && b.category) || '')).toLowerCase());",
                  "a.setAttribute('data-search', (cleanTitle(b, nm) + ' ' + nm + ' ' + (path || '') + ' ' + ((b && b.category) || '')).toLowerCase());")
    h = h.replace("s.textContent = (b.items != null ? b.items + ' 条' : '') + (arch ? ' · 已归档' : '');",
                  "s.textContent = (b.items != null ? b.items + ' 条' : '') + (path ? ' · ' + path.split(' · ').pop() : '') + (arch ? ' · 已归档' : '');")
    P.write_text(h, encoding="utf-8")
    print("渲染已改为按大类平铺")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
