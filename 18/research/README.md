# Day 18 — Among the Ancient Trees：数据可行性调查

> 2026-11-20 复核入口：[data_feasibility.md](data_feasibility.md)、[tree_inventory.csv](tree_inventory.csv)、[trail_sources.md](trail_sources.md)、[cartographic_options.md](cartographic_options.md)。以下为 2026-11-19 原始研究记录；其中“没有 DEM 栅格”仅描述当时本研究目录及 MOI 取数状态。仓库另有后续取得的 Copernicus 30m DSM 小裁切，详见新报告；不能等同于成功取得 MOI 20m DTM。本轮没有制作图像。

研究日期：2026-11-19（America/New_York）。研究对象是拉拉山国家森林游乐区巨木群，不是北面的拉拉山山顶。仅进行资料调查和 GIS 数据核验，未制作地图、GIF 或 PNG。

**结论：真实地形适合做山水地图，但目前不能将 24 个巨木符号全部放到经过验证的精确位置，也不能把现有步道直接称作完整官方网络。建议以 A / Topographic Shanshui 为最终方向，先补齐坐标与 DEM 原始图幅，再进入制图。**

| 用户关心的问题 | 本次核查结果 |
|---|---|
| 24 棵巨木有多少可以可靠定位？ | 严格按“经过验证的树干坐标”计 **0/24**；OSM 有 **15/24 个编号各有一个无编号冲突的候选点**，可供概略参考，但不是验证精度后的可靠定位。另有 13 号双点冲突。官方有与 6 个编号相关的通讯标示点，不能计作 6 个树干测量点。 |
| 步道有完整几何吗？ | 已下载一条连续 GPX 和 OSM 步行线；GPX 接近全部 10 个官方参考点，具备重建基础。**全支线几何及准确连通性尚未验证**，不是已取得完整官方 GIS。 |
| DEM 能用吗？ | **20m 开放 DTM 在授权和技术上可用**；目录已获取，目标参考图幅已确定。TGOS 数据链接实测返回 403，**本地还没有成功取得 DEM 栅格，未运行地形派生验证**。 |
| 推荐哪种构图？ | **A. Topographic Shanshui**：保留真实平面位置和坡谷关系，以水墨晕渲及青绿等高线表达。B 可作后续艺术变体，需要额外清楚披露投影与夸张。 |
| 最大缺口？ | **完整、带测量语义和来源的 1–24 号树位表**。其次是原始 DTM 下载成功与支线网络核验；GPX 再利用授权也待确认。 |

详细证据见 [地形](terrain_feasibility.md)、[巨木](trees_feasibility.md)、[步道](trails_feasibility.md)、[构图判断](cartographic_feasibility.md)、[来源目录](sources.md)。逐树表见 [tree_inventory_1_24.csv](data/tree_inventory_1_24.csv)。

本目录的数据层全部保留来源角色：`official_communication_points.geojson` 是官方通讯标示点；`osm_tree_candidates.geojson` 是其他公开地理数据的树位候选；`public_track_20240802.geojson` 是游客实录轨迹。没有将它们合成为“精确树位”成品。C 类仅记录官方图中的相对位置，不输出估计经纬度；D 类的选定坐标为空。

复核可运行 `scripts/analyze_data.py`。它读取已保存的原始 OSM、GPX、官方 PDF 和图幅索引，输出 CSV、GeoJSON 与 `data/validation_summary.json`，不会绘图。依赖为 `pypdf==7.1.1`、`pyproj==3.8.0`、`pyshp==3.1.9`；本次用 `uv pip install --target 18/research/.deps ...` 安装在本目录的忽略文件夹中。`scripts/fetch_sources.py` 是有 12 MB 单文件上限的资料抓取脚本；失败记录应与 HTTP headers 一起检查，不应只凭目标文件存在就认定下载成功。

数值距离采用 TWD97 / TM2 121（EPSG:3826）投影后的平面距离，保留两位小数只为复算，不代表厘米精度。树位与步道均未进行现场验证。只修改 `18/research/`；没有 commit 或 push。
