"""Make an explicit, bounded cleanup plan; actual removals use native PowerShell.
Keep all research/source/GIS data. Save C camera conclusions before removing PNGs.
"""
from pathlib import Path
import json,hashlib
DAY=Path(__file__).resolve().parents[1];R=DAY/'oblique'
old=(R/'README.md').read_text(encoding='utf8')
prefix='# Camera study — archived comparison and adopted C camera\n\n用户正式选择 **C / Monumental Mountain**：315°方位、18°俯角、1.20×垂直夸张，正交高度1808.836708m（约1809m）。最终艺术构建只读取 `camera_c.json`，不再运行方位筛选或切换相机。\n\n下列比较结论、相机矩阵和可见性统计保留；三个阶段PNG及可再生成的深度缓冲已列入清理。历史测试的22m竖杆与本轮艺术化古树高度不同，不能混用可见数量。\n\n'
old=old.replace('# Oblique Shanshui — camera and terrain study','## 历史技术研究')
for name,title in [('A_gentle_oblique','A / Gentle Oblique'),('B_landscape_depth','B / Landscape Depth'),('C_monumental_mountain','C / Monumental Mountain')]:old=old.replace(f'[{title}]({name}.png)',title+'（阶段PNG已清理）')
old=old.replace('**建议下一轮以 B 为起点。**','**历史测试曾建议 B；现以用户正式选择的 C 为准。**')
old=old.replace('`*_depth.npz`：三张图的地形相机深度缓冲，空白为负无穷；供后续遮挡核查。','`*_depth.npz`：历史可再生成深度缓冲，已清理；显式运行历史测试脚本可重新生成。')
(R/'camera_study.md').write_text(prefix+old,encoding='utf8')
# Preserve the analytical part of the old pipeline, drop its retired image rendering.
src=DAY/'terrain/scripts/build_preview.py'
code=src.read_text(encoding='utf8').split('# Cartographic preview,')[0]
code=code.replace('D=R/\'data\';P=R.parent/\'preview\';P.mkdir(exist_ok=True)',"D=R/'data'")
code=code.replace('Real DSM analysis + cartographic styling; never generate terrain or tree coordinates.','Real DSM analysis only. Historical 2-D preview rendering has been retired.')
(DAY/'terrain/scripts/analyze_terrain.py').write_text(code,encoding='utf8')
retired=[
'preview/day18_shanshui_composition_01.png','preview/day18_shanshui_composition_02A.png','preview/day18_shanshui_composition_02B.png','preview/day18_shanshui_composition_03.png',
'preview/composition_02_validation.json','preview/composition_03_validation.json',
'oblique/A_gentle_oblique.png','oblique/B_landscape_depth.png','oblique/C_monumental_mountain.png',
'oblique/A_gentle_oblique_depth.npz','oblique/B_landscape_depth_depth.npz','oblique/C_monumental_mountain_depth.npz',
'terrain/scripts/build_preview.py','terrain/scripts/refine_preview.py','terrain/scripts/paint_shanshui.py','terrain/scripts/validate_outputs.py',
'terrain/.deps/scipy-1.18.1-cp314-cp314-win_amd64.whl','terrain/.deps/.lock','research/.deps/.lock']
files=[]
for name in retired:
    p=(DAY/name).resolve();assert p.is_relative_to(DAY.resolve())
    if p.is_file():files.append({'path':name,'bytes':p.stat().st_size,'reason':'retired image pipeline/output or zero-byte installer residue'})
caches=[]
for p in DAY.rglob('__pycache__'):
    if p.is_dir():
        pp=p.resolve();assert pp.is_relative_to(DAY.resolve())
        fs=[q for q in p.rglob('*') if q.is_file()]
        caches.append({'path':p.relative_to(DAY).as_posix(),'files':len(fs),'bytes':sum(q.stat().st_size for q in fs),'reason':'regenerable Python bytecode cache'})
baseline={}
for folder in ['research','terrain/data','terrain/sources']:
    for p in (DAY/folder).rglob('*'):
        if not p.is_file() or '.deps' in p.parts or '__pycache__' in p.parts:continue
        baseline[p.relative_to(DAY).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
plan={'root':str(DAY.resolve()),'camera_conclusions_saved':'oblique/camera_study.md','fixed_camera':'oblique/camera_c.json','delete_files':files,'delete_cache_directories':caches,'protected_source_hashes':baseline,'preserve_dependency_installations':True}
(DAY/'cleanup_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
# Compact the full pre-audit inventory to its summary, avoiding retaining 1MB of cache names.
before=json.loads((DAY/'cleanup_before.json').read_text(encoding='utf-8-sig'));before.pop('files',None)
(DAY/'cleanup_before.json').write_text(json.dumps(before,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'explicit_retired_files':len(files),'cache_directories':len(caches),'cache_files':sum(c['files'] for c in caches),'planned_removed_bytes':sum(f['bytes'] for f in files)+sum(c['bytes'] for c in caches),'protected_source_records':len(baseline)},indent=2))
