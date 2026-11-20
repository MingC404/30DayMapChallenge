"""Read-only source checks, plus cleanup statistics and report. Use Python -B."""
from pathlib import Path
import json,hashlib,sys,re
DAY=Path(__file__).resolve().parents[1]
plan=json.loads((DAY/'cleanup_plan.json').read_text(encoding='utf8'))
before=json.loads((DAY/'cleanup_before.json').read_text(encoding='utf-8-sig'))
for name,expected in plan['protected_source_hashes'].items():
    p=DAY/name
    assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==expected,name
assert all(not (DAY/f['path']).exists() for f in plan['delete_files'])
assert all(not (DAY/f['path']).exists() for f in plan['delete_cache_directories'])
pngs=[p for p in DAY.rglob('*.png') if '.deps' not in p.parts]
assert [p.relative_to(DAY).as_posix() for p in pngs]==['oblique/shanshui_C_art.png']
art=json.loads((DAY/'oblique/art_validation.json').read_text())
assert art['camera']['azimuth_deg']==315 and art['camera']['elevation_deg']==18
assert art['camera']['vertical_exaggeration']==1.2 and abs(art['camera']['orthographic_height_m']-1808.8367082405482)<1e-8
assert art['root_surface_residual_max_m']<1e-8
assert hashlib.sha256(pngs[0].read_bytes()).hexdigest()==art['output_sha256']
sys.path.insert(0,str(DAY/'terrain/.deps'))
from PIL import Image
im=Image.open(pngs[0]);assert im.size==(1800,2025);im.verify()
# Compile-only check proves the retained scientific pipeline remains syntactically valid,
# without rewriting any historical analysis products.
for p in [DAY/'oblique/render_art.py',DAY/'oblique/build_study.py',DAY/'terrain/scripts/analyze_terrain.py']:
    compile(p.read_text(encoding='utf8'),str(p),'exec')
report={'before':{'files':before['file_count'],'bytes':before['bytes']},'after':{},'protected_source_files_verified':len(plan['protected_source_hashes']),'retired_files_removed':len(plan['delete_files']),'cache_directories_removed':len(plan['delete_cache_directories']),'cache_files_removed':sum(c['files'] for c in plan['delete_cache_directories']),'project_png_outputs':1,'package_data_images_preserved':True,'camera_locked':True,'visible_tree_candidates':art['visible_tree_candidate_count'],'original_root_coordinates_unchanged':True}
def size():
    ps=[p for p in DAY.rglob('*') if p.is_file()];return {'files':len(ps),'bytes':sum(p.stat().st_size for p in ps)}
def markdown():
    b=report['before'];a=report['after']
    return f'''# Day18 cleanup report

统计范围为整个`18/`，包含git忽略的本地依赖和第三方包内资源；磁盘占用为逻辑文件字节数，不是文件系统簇占用。清理前为本轮工作开始时，清理后包含新增艺术预览、代码、相机文档和审计报告。

| 时点 | 文件数 | 字节 | MiB |
|---|---:|---:|---:|
| 清理前 | {b['files']:,} | {b['bytes']:,} | {b['bytes']/1048576:.2f} |
| 清理后 | {a['files']:,} | {a['bytes']:,} | {a['bytes']/1048576:.2f} |

净减少 {b['files']-a['files']:,} 个文件、{(b['bytes']-a['bytes'])/1048576:.2f} MiB。该净值同时计入本轮新增文件，不应等同于删除清单的字节总和。

删除了{len(plan['delete_files'])}个明确废弃的输出/脚本/零字节安装残留，以及{len(plan['delete_cache_directories'])}个Python字节码缓存目录（{sum(c['files'] for c in plan['delete_cache_directories'])}个缓存文件）。具体路径、大小、原因在[cleanup_plan.json](cleanup_plan.json)。

先将固定C参数、历史相机比较和结论保存到[oblique/camera_study.md](oblique/camera_study.md)，再移除三张Camera Study PNG及可再生成的深度缓冲。二维01、02A、02B、03旧PNG和仅服务废弃图面的脚本已移除；原流水线的科学分析部分另存为`terrain/scripts/analyze_terrain.py`。正式构建不导入被删除脚本。

对{len(plan['protected_source_hashes'])}个研究、GIS及来源证据文件逐一核验SHA-256，均未改变。原始DEM、投影DEM、OSM候选点、GPX、官方图件、许可证、下载失败证据、研究文档与科学派生结果均保留。已安装依赖仍供复现使用，未为减少文件数随意破坏第三方包；包内示例/工具图标不是旧项目预览，未删除。当前项目输出PNG仅[oblique/shanshui_C_art.png](oblique/shanshui_C_art.png)一张。

固定相机315°/18°/1.20×/1808.836708m核验通过，树根赋高残差0，艺术树形部分可见数量{art['visible_tree_candidate_count']}；不是实测树位精度或根部全部可见的声明。PNG可解码、保留脚本语法检查通过。原始研究结论未改变。

主要保留代码：`oblique/render_art.py`（正式构建）、`oblique/build_study.py`（历史相机复现）、`terrain/scripts/acquire_dem.py`、`terrain/scripts/analyze_terrain.py`和`research/scripts/`。`oblique/prepare_cleanup.py`、`finalize_docs.py`、`finish_audit.py`只记录本轮审计工作，不是日常艺术构建依赖。

没有生成GIF，没有更新Gallery、学院仓库，没有commit或push；工作范围仅Day18。
'''
# Include these output files themselves. Iterate until digit lengths and file totals stabilize.
(DAY/'cleanup_after.json').touch(exist_ok=True);(DAY/'cleanup_report.md').touch(exist_ok=True)
for _ in range(8):
    report['after']=size()
    (DAY/'cleanup_report.md').write_text(markdown(),encoding='utf8')
    (DAY/'cleanup_after.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    if size()==report['after']:break
assert size()==report['after']
print(json.dumps(report,ensure_ascii=False,indent=2))
