# Day 19 研究数据与保留边界

当前地图仅使用 `soho/selected-extent.geojson`、`soho/selected-pois.json`、`soho/selected-311.json`，以及 `../data/` 的建筑／道路计算几何。当前区域、分类和证据说明未因文件清理改变。

## SoHo：完整的当前复现输入

- `311-window.json`：61 条原始宽口径请求，2025 全年；查询参数在 `query.json`。
- `pois-window.json`：150 个 OSM POI 对象及定位方式。
- `buildings-window.json`、`streets-window.json`：小范围原始几何，用于四候选统计与比较，不是全纽约下载。
- `block-faces.geojson`：真实街道构面，每个面内含街名及初筛元数据；不另存重复 inventory。
- `candidate-comparison.json`：四个候选的精确 face_ids 和数据数量；这些 ID 与 block-faces 可重建候选边界，不另存四套候选面。
- `selected-extent.geojson`、`selected-pois.json`、`selected-311.json`：当前六街块范围与 18 个 POI、12 条历史气味／油烟投诉。
- `selected-indoor-excluded.json`、`selected-summary.json`：7 条室内排除记录及最终统计。
- `query.json`：来源、时间窗、bbox、查询参数、提取检查说明。没有保存无关 OSM 编辑者信息。

分类直接在选择脚本内存中完成，不再依赖或生成 `311-classified.json`。未命中 POI relation 的事实记录在 query 元数据中，不单独保存空数组文件。

在仓库根目录运行 `node 19/scripts/rebuild.mjs`，从保存的输入离线复现 D 范围、比较表和选定数据，不联网、不生成候选副本。需要 Python + Shapely；支持 `DAY19_PYTHON` 指定解释器，脚本兼容已有 TEMP/day19_geo_deps 安装。

只有 `node 19/scripts/rebuild.mjs --refresh` 才更新公开数据：collect 抓取小窗口，OSM XML 从内存经 stdin 传给 analyze，随后 select 重现 D 范围，prepare 更新 110 m 计算外延。XML 不落盘，Python 用 -B 禁止缓存。普通预览只需 `node 19/server.mjs`。

动态 API 重抓可能改变数据数量；当前页面以保存的快照为准。完整选址、许可与局限见 [SoHo 研究](../soho_research.md)。

## 历史纽约候选：保留结论和证据，不保留旧地图过程副本

Chinatown、LES、West Village、Williamsburg 各保留三项：

- `*_selected_311.json`：有 unique_key、日期、分类、坐标及 evidence_group 的实际选定记录。
- `*_selected_pois.json`：实际选定 POI、OSM ID、标签与定位方法。
- `*_selected_extent.geojson`：原五相邻街块及其统计边界。

这 12 个文件支持复核历史表格中的 185 条相关请求、130 个 POI。`selected_summary.json` 与 `summary.json` 保存最终候选和初筛数量；`sites.json` 保存原取样 bbox；三个 `schema_*.json`、`query_log.json` 和 `urination_citywide_2025.json` 保存来源字段、失败／回退记录与尿味分类核查。

已删除历史宽窗口重复记录、原始建筑／道路几何、可推导的中间面和不再用于当前地图的旧脚本。历史建筑覆盖率等仍作为当时统计快照保留，不声称能仅靠剩余来源点重新测量旧几何；如需重做那一阶段，可按 sites bbox 和 query_log 的数据集接口重新获取。当前 SoHo 的几何复现输入仍完整。

历史选址规则与原结论见 [data_feasibility.md](../data_feasibility.md)、[site_selection.md](../site_selection.md)、[propagation_methods.md](../propagation_methods.md)。清理审计见 [cleanup_audit.md](../cleanup_audit.md)。

OSM 数据：© OpenStreetMap contributors / [ODbL](https://www.openstreetmap.org/copyright)。NYC 数据遵循 [NYC Open Data 使用条款](https://cityofnewyork.github.io/opendatatsm/publicpolicies.html)，来源分开保存。
