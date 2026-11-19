# Day 19 清理审计

范围仅为 `19/`。先完成新版浏览器验证，再检查 HTML／ES module／Worker 数据依赖与研究脚本输入，最后按显式文件清单逐个删除；未使用跨目录或递归删除。

## 最终媒体导出清理

**本轮开始 56 个文件，最终保留 63 个文件**。新增七项均为必要交付：`day19_loop.gif`、`day19.png`、共享构图模块 `artwork.mjs`、`scripts/render_frames.cjs`、`scripts/export_media.py`、`requirements-export.txt` 和 `data/media_manifest.json`。没有旧正式媒体需要另行删除。

210 张 PNG 帧、调色板、暂存 GIF／PNG 和渲染报告均位于系统临时目录，由 Python TemporaryDirectory 在导出校验后自动删除；周期预演不落盘。Node 在 finally 中关闭浏览器和临时 HTTP server。当前 `19/` 无帧目录、截图、palette、缓存、旧版 HTML 或未使用的导出版本目录，最终只保留一份 GIF 和一份对应 PNG。

GIF 为 14 秒、15 fps、1600×1200、210 帧；PNG 从最终 GIF 的第 32 帧（2.13 s）解码提取并逐像素核对。全部帧的标题／图例／来源像素静止，首尾 RGB 一致；原数据、core、Worker 未变。交互 HTML 继续通过 Explore Smells / Explore Space 浏览器检查。详情见 `data/media_manifest.json` 和 README。

## 前期目录清理记录

**本轮单液体改版：清理前 56 个文件，清理后 56 个文件。** 旧子模式、固定参考点、双实验云的代码／样式／说明／测试已在原文件内删除或替换；复用现有 core、Worker 和测试文件，没有新增证据缓存文件或冗余版本。临时改写脚本执行后自行删除。

此前的目录清理记录：92 个文件减至 56 个，删除 39 个文件、共 3,243,470 字节，新增本审计、局部 `.gitignore` 和 `scripts/rebuild.mjs` 三个必要文件。总目录由约 4.69 MB 减至约 1.5 MB。下表为此前已完成的文件删除，保留其审计依据。

## 删除内容与依据

|内容|数量|删除依据|
|---|---:|---|
|四个历史候选的宽窗口 311、分类副本、建筑、道路、宽窗口 POI、过程街块面|24|当前地图不引用；历史选定来源、精确边界、统计和查询来源仍保留|
|旧 `analyze.py`、`blocks.py`、`boundary_names.py`、`collect.mjs`、`osm_fallback.mjs`、`select_sites.py`|6|属于已结束的纽约初筛流程，依赖已撤下的历史宽窗口或原 XML，不是当前 SoHo 构建入口|
|East Village 初筛街块面|1|该候选未采用；淘汰原因与统计在历史文档／summary 中保留|
|SoHo `311-classified.json`、`block-inventory.json`|2|可从保留原始记录和 block-faces 元数据推导；选择脚本已改为在内存中分类|
|SoHo `candidate-A/B/C/D-extent.geojson`|4|可从 block-faces 与 comparison 的 face_ids 精确重建；D 与 selected-extent 原本完全重复|
|SoHo `poi-relations.json` 空数组|1|零未处理 relation 的结果移入来源 query 元数据，无需独立空文件|
|根目录 `.gitkeep`|1|目录已包含正式文件，无需占位|

24 个历史过程文件为 `research/{chinatown,les,west_village,williamsburg}` 加以下六种后缀：`_311.json`、`_311_classified.json`、`_block_faces.geojson`、`_buildings.json`、`_osm_pois.json`、`_streets.json`。

没有发现需要删除的旧 HTML、动画帧、图像、备份／版本目录；本轮也没有生成这些输出。没有通过 `.gitignore` 隐藏必要来源数据。

## 保留内容

- 正式 `index.html`、`style.css`、`app.mjs`、`core.mjs`、`worker.mjs`、`server.mjs`。
- `data/` 三个当前运行几何／来源元数据文件。
- 三份指定研究文档、当前 `soho_research.md`、README 和研究目录说明。
- SoHo 12 份必要研究输入／选定数据／比较与排除记录，足以离线复现当前六街块。
- 历史四个候选的 12 份选定投诉、POI、边界；历史统计、原取样 bbox、三个 schema 和查询／尿味核查记录。可核查 185 条相关请求及 130 个 POI，不保留不再使用的旧几何大副本。
- `scripts/` 五个有效构建／获取／分析脚本，以及 `tests/` 两个可运行检查。

## 构建不会再制造过程副本

`node 19/scripts/rebuild.mjs` 默认为离线复现既定 D 区域，只覆盖选定文件和比较表，不增长文件数量。`--refresh` 才更新小窗口公开数据；OSM XML 从内存经 stdin 交给 Python，不落盘。分类与候选边界在内存中计算，只有实际选定边界被写入。Python 使用 `-B` 禁止缓存；`.gitignore` 只防止临时 XML、pyc、partial、日志进入版本管理。

## 验收

- 真实 18 个 POI／12 条投诉、10 个投诉坐标和 7 条室内排除记录保持一致；来源数据和运行几何有 SHA-256 前后核对。core 本轮新增多源路径搜索、证据归一化和单根连通筛选，仍使用同一建筑障碍 Dijkstra 与 Marching Squares。
- 离线构建在清理后连续运行，未重新生成已删除的 classified／inventory／候选面／XML 或缓存；文件数量稳定。
- 浏览器重新加载全部资源成功；Explore Space 只有一个几何场和一个轮廓，模型网格及实际渲染均检测为一个连通区域。同一片液体自然包含橙色、紫色及中性部分，证据缓存只构建一次；无紫色证据的网格没有被强行染紫。
- 连续鼠标输入不清空云层，Worker 只追踪最新位置，连通筛选避免插值产生第二个残留区域。鼠标停下、离开地图或进入建筑时保留有效状态。真实记录和单液体渲染分别检查未出现楼内漏色，Explore Smells 的原有交互保持正常。
- 前期交互迭代不保留媒体或临时截图；本轮新增的正式 GIF／PNG 如上节记录。没有更改其他 Day／Gallery，没有 commit 或 push。
# Final audit: November 18, 2026

This final review began with 63 files (4,666,558 bytes). No old GIF/PNG/HTML variants, frame sequences, screenshots, temporary downloads, caches or obsolete version directories remained. No source or research files were deleted to reduce the count. The earlier cleanup history below records previous prototype work.

The formal GIF and PNG, map geometry, selected records and propagation code are unchanged. The README is now a concise English overview; detailed single-fluid geometry, evidence normalization and export behavior are retained in `propagation_methods.md` and the media manifest. Historical Williamsburg samples and current SoHo selection inputs remain available for audit and offline rebuilding.

Local Pages staging copies one GIF and one formal PNG per day, Day 17's self-contained HTML, and only the twelve files required for Day 19's interactive runtime. The two research-document links in the staged HTML point to their canonical repository paths. Other Gallery rows, images and CSS are unchanged, and Day 18 had no existing Gallery row to alter. New scripts under `scripts/` provide a scoped idempotent update and a project-prefix preview server with ES-module MIME support. `tests/gallery.cjs` checks desktop/mobile sizing, actual painted GIF playback, byte-identical deployed media, links and both interactive pages without retaining images.

Final tests passed: both infinite-loop GIFs decode; Day 17's formal MP4 decodes; Day 19's PNG exactly matches decoded GIF frame 32 at 2.13 s; both HTMLs work; Day 19 retains one connected field with zero building-mask leaks and unchanged 18/12 records. READMEs' local links resolve. Temporary browser inspection JPEGs are removed after review. No frames or alternative outputs were generated in either day folder.

See [data/final_audit.json](data/final_audit.json) for final before/after counts, file types and directory sizes. Added audit, preview and Gallery-maintenance code explains the small increase in file count. No commit, push or deployment was performed.

