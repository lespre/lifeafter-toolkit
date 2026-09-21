# -*- coding: utf-8 -*-
"""snap_shader_db.py — 抓取游戏 shader_compile.db 快照 (供"跑游戏→打开展示位"实验)
用法: python snap_shader_db.py [tag]
  将 E:\\mrzh\\Documents\\db\\shader_compile.db* 复制到工作区, 文件名带时间戳与 tag, 并打印各文件大小与记录数。
"""
import os, shutil, sqlite3, sys, time
SRC = r'E:\mrzh\Documents\db'
DST = r'E:\la拆包项目\03拆包产物\render_1003_010\_game_shader_db'
def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else 'snap'
    os.makedirs(DST, exist_ok=True)
    ts = time.strftime('%Y%m%d_%H%M%S')
    for f in ('shader_compile.db', 'shader_compile.db-wal', 'shader_compile.db-shm'):
        sp = os.path.join(SRC, f)
        if os.path.exists(sp):
            dp = os.path.join(DST, '%s_%s_%s' % (f, tag, ts))
            try:
                shutil.copy2(sp, dp)
                print('copied %s -> %s (%.2f MB)' % (f, os.path.basename(dp), os.path.getsize(dp) / 1e6))
            except Exception as e:
                print('copy fail', f, e)
        else:
            print('absent:', f)
    # 读取记录数 (对副本)
    dbp = os.path.join(DST, 'shader_compile.db_%s_%s' % (tag, ts))
    if os.path.exists(dbp):
        try:
            con = sqlite3.connect(dbp)
            rows = con.execute('SELECT COUNT(*) FROM shader_compile_records').fetchone()[0]
            print('records:', rows)
            if rows:
                for r in con.execute('SELECT effect_filename, hash_code, tag, timestamp FROM shader_compile_records LIMIT 50'):
                    print('   ', r)
            con.close()
        except Exception as e:
            print('sqlite read fail:', e)
if __name__ == '__main__':
    main()
