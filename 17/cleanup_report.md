# Day 17 directory cleanup

## Final audit: November 18, 2026

The final review found 397 files (113,471,550 bytes) before edits. No obsolete media, frame sequences, screenshots, logs or unused version folders remained. The only GIF, MP4 and root poster are the formal outputs. The other PNGs are renderer textures; the other HTML files are the source template and saved official source pages, not competing map versions.

All 336 files in `raw/` are retained: official source snapshots, ENC archives and extracted exchange files, updates, catalog, user agreements and research audits. Repeated agreement text belongs to distinct official exchange packages; ZIP and extracted files serve provenance and the existing GDAL pipeline. Empty API responses also document unsuccessful source queries. These are not disposable caches.

The README is now an English overview. Unique rendering/timing details were moved into `lighthouse_beam_research.md`. The final GIF, PNG, MP4, HTML, inventory, geometry and artwork were not changed. Existing HTML and media checks passed, including all 153 entries, offline interaction, mobile layout, infinite GIF metadata and full MP4 decode.

The exporter already uses `TemporaryDirectory` for 360 frames and the palette, including automatic cleanup on failure. The frame helper now rejects any destination outside an export-owned `day17-render-*` directory under the OS temporary root. A rejection check confirms that it cannot write a frame sequence into `17/`. The new local ignore rules cover bytecode and accidental temporary artifacts.

Final counts, file types and subdirectory totals for both days are recorded in [the shared final audit](../19/data/final_audit.json). No research or original-source files were removed. No new media export was necessary. Local Gallery staging is reproducible with `python -B 19/scripts/update_gallery.py`; it does not publish.

清理范围仅为 `17/`，未改动其他 Day、Gallery 或共享仓库文件。未 commit / push。

## 保留

- 正式作品：`day17.png`、`day17_loop.gif`、`day17_loop.mp4`、`day17.html`。
- 当前源代码：`src/` 与 `scripts/`，以及依赖清单 `requirements.txt`、`package.json`。HTML 离线自包含；源代码中的图层和纹理用于可复现构建。
- 数据：完整 `raw/`、`light_inventory.csv`、`source_manifest.json`，以及 `data/` 内正式海岸线、版式参照、验证报告与导出参数。没有删除原始 ENC、官方 GeoJSON 或来源证据。
- 文档：README、数据可行性调查、数据字典与 `lighthouse_beam_research.md`。
- 数据处理流程迁入 `scripts/data/`，保留下载、解析、清单与来源整理代码；删除根目录的重复副本。

## 删除

共清理 38 个明确路径（目录包括其内容），逐项记录见 [data/cleanup_manifest.json](data/cleanup_manifest.json)。

- 被新版替代的 `where_the_darkness_ends.html`、`where_the_darkness_ends_beams.html`；原交互探索功能合并入正式 HTML。
- 旧 `interactive/`、`lighthouse_beams/`、`outputs/`，其中包括旧地图、旧动画资源、检查截图、接触表和中间导出。
- 旧设计渲染器、旧交互和光束构建器、旧版检查脚本、一次性迁移脚本及已被 README 替代的设计说明。
- `.render-tools/` 临时依赖目录、Python 字节码缓存和无用途占位文件。

先检查当前构建引用，再删除；保留源码不再依赖上述路径。渲染帧和编码调色板由系统临时目录承载，导出结束自动清除。

## 清理前归档

旧版在删除前已完整归档并检查关键条目，归档在最终作品目录之外：

`C:\Users\Yiming\AppData\Local\Temp\Day17-preserved-20261117-234620.zip`

归档 447 个条目，26,059,890 字节。此系统临时目录归档只用于本次清理前恢复，不是永久备份，也不是任何最终构建依赖。

## 清理后验证

完整重建命令：`python -B 17/scripts/build.py`（仓库根目录）。构建生成同一地图构图的 PNG、独立 HTML、12 秒 GIF 和 MP4，并自动执行源数据哈希、153 个点位和灯色、逐段时序、交互、离线打开、循环像素和媒体完整解码检查。

结果记录在 `data/validation.json`、`data/media_validation.json` 与 `data/media_manifest.json`。最终目录不需要旧版文件即可重新生成；原始数据处理脚本也已保留。
