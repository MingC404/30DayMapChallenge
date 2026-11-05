# Day05 — Seeing New York from the Water

本轮保留已认可的白底、蓝灰建筑、深蓝地标、水面和右下角定位图，只调整距离着色及几何遮挡，并加入同航线第 2 号观察点对照。画布均为 **2600 × 1500**，署名 Ming Cao。

## 输出与版本

| 版本 | PNG | 可编辑矢量 |
| --- | --- | --- |
| 已认可版，第 3 号位置 | [保存的原稿](outputs/approved/seeing_new_york_waterfront.png) | [SVG](outputs/approved/seeing_new_york_waterfront.svg) |
| 第 3 号位置，微调版 | [PNG](outputs/seeing_new_york_lookout_03_refined.png) | [SVG](outputs/seeing_new_york_lookout_03_refined.svg) |
| 第 2 号位置，对照版 | [PNG](outputs/seeing_new_york_lookout_02_refined.png) | [SVG](outputs/seeing_new_york_lookout_02_refined.svg) |

原 `outputs/seeing_new_york_waterfront.png/.svg` 保持不变；`approved/` 另存其逐字节相同的快照、原 README 和渲染参数，原脚本快照在 `scripts/build_waterfront_approved.py`。所有新稿另命名，便于比较。

## 两个视点的变化

第 2 号位置位于航程较早处，与第 3 号位置直线相距 **332.82 米**，沿线间距约 332.72 米。两图均独立从相同的局部建筑数据重新计算，没有平移成图。

| 地标 | 第 3 号方位角 | 第 2 号方位角 | 当前简化模型中的变化 |
| --- | ---: | ---: | --- |
| 70 Pine Street | 288.758806° | 306.463612° | 向右、距离更近；第 2 号视点被近处体块完全遮住，不强行露出或标注 |
| One World Trade Center | 307.434696° | 317.701883° | 向右；第 2 号视点主要露出尖塔和少量顶部 |
| Woolworth Building | 317.205958° | 331.811958° | 向右越出 330° 窗口，不为保留它扩大视场或移动建筑 |

第 3 号微调版也不再完整显示地标塔身：近处建筑遮挡三个地标的大部分下部。这些是**当前简化几何的渲染结果**，不是实际可见性调查结论。第 2 号近处楼体在相同角度比例下更高、更宽，部分超出景观区域上沿；不为比较而缩小建筑或改动投影。

## 距离与遮挡修正

旧稿的问题已确认：先绘全部背景，再将三个地标置于其上，仅让部分低层覆盖地标底部；地标另有最小显示宽度。新稿撤销这些规则。

- **按距离着色**：以建筑几何中心至当前观察点的实际测地距离连续插值，400–2600 米对应从 `#ADC9D8` 到 `#DFE8ED`，超出两端保持端点色；近处略深、远处略淡。两个视点使用相同函数，没有随机分色。地标仍为海军蓝。
- **同一实体模型**：普通建筑按真实 footprint 和屋顶高度构成拉伸体；地标在其原 footprint 内作简化退台、收分和尖顶。退缩比例不大于 1，不设置像素最小宽度、不移动建筑、不增加窗户。地标中心使用原坐标，背景和地标均转到同一 UTM 度量空间。
- **同一深度规则**：每条像素视线计算穿入三维实体的最近距离，决定最终表面归属；不按“地标优先”绘制，也不只按整栋中心距离排序。不同退台层、背景和地标共享一个深度缓冲。
- **标签**：引线终点选取该建筑实际未被遮住的投影像素，非固定中心空点；全遮挡的地标不标注。标签不移动建筑；引线相交断言通过，没有增加其他建筑名称。
- **可编辑 SVG**：从同一深度结果的可见区域合并为原生矢量路径，按建筑分组，不嵌入位图。可见边界离散精度为 1 像素；字体为 Georgia / Arial。

两个视点共用 **275°–330°** 方位窗口、横向 44.363636 像素/度、纵向 30 像素/度、模型眼高 6 米、视平线 y=1000、相同天空/水面区域及定位图尺寸。岸线仍由当前视点射线与官方陆地首次相交后投影；小地图同步更新观察点与观看扇区。

使用同一批 2,323 个局部建筑要素，第 3 号窗口进入 886 个有效体块，第 2 号窗口进入 444 个。与旧稿的计数差异来自按 footprint 与窗口相交筛选，并撤销 350 米近距排除，而非新增数据。普通建筑仍只有单一 roof height；退台、冠部、模型水位、眼高均有简化，不能据此声称精确或已实证的视线可见性。

## 重建与核验

```powershell
python3.14.exe 05/scripts/build_waterfront_comparison.py --verify-depth
```

两图均重建；`--verify-depth` 将建筑遍历顺序反转后再次计算，断言最终逐像素建筑归属完全一致，排除依赖绘制顺序或地标覆盖优先级。报告保存于 `data/lookout_03_render.json`、`data/lookout_02_render.json`，含方位、距离、投影参数、遮挡后的模型像素计数及标签锚点。像素比例仅是模型内部统计，不是现实可见比例。

已核验：两图参数一致、地标测地方位、最小显示宽度规则已撤销、标签引线不交叉、SVG 无嵌入位图、PNG 尺寸、认可版快照哈希。只读取 Day01–04 的现有依赖和陆地数据，未修改它们，未制作 GIF、commit 或 push。

依赖 Pillow、NumPy、Shapely、pyproj；复用只读 `02/.deps` 和 Windows 字体。生成图像不联网。本轮没有补充建筑数据。

## 数据与参考

- **局部建筑**：[NYC OTI / NYC Open Data BUILDING](https://data.cityofnewyork.us/City-Government/BUILDING/5zhs-2jue)，[官方字段说明](https://github.com/CityOfNewYork/nyc-geo-metadata/blob/main/Metadata/Metadata_BuildingFootprints.md)。经度 -74.024 至 -73.996、纬度 40.700 至 40.722；HEIGHT_ROOF 为英尺，换算为米。`data/lower_manhattan_buildings.geojson`、`data/building_sources.json` 保留原缓存、查询 URL、时间及 SHA-256。原获取时间为 2026-11-04 美东时间 / 2026-11-05 UTC。
- **陆地**：[NYC DCP Borough Boundaries，26b](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne)，复用项目 15 米简化版，2026-11-02 获取。
- **航线**：[NYC Ferry Developer Tools](https://www.ferry.nyc/developer-tools/)，本地 GTFS 版本 20261103。ER / shape 9 前四个顶点为 Wall St/Pier 11 → DUMBO 约 1.04 公里运营路线段，非实测船迹；原航线和三个观察点保留于 `data/view_context.geojson`。
- **地标坐标**：[1 WTC / Q11245](https://www.wikidata.org/wiki/Q11245)、[70 Pine / Q262041](https://www.wikidata.org/wiki/Q262041)、[Woolworth / Q217652](https://www.wikidata.org/wiki/Q217652)，保留原始实体 JSON；Wikidata 结构化数据为 CC0。
- **顶部特征参考**：[Skyscraper Museum — 1 WTC](https://www.skyscraper.org/supertall/building/one-world-trade-center/)、[NYC LPC — 70 Pine](https://s-media.nyc.gov/agencies/lpc/lp/2441.pdf)、[Skyscraper Museum — Woolworth](https://old.skyscraper.org/EXHIBITIONS/TEN_TOPS/woolworth.php)。保持简化识别特征，不模拟细部实景。
