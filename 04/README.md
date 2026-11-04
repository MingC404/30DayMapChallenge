# Day 04 — Clusters of Play

Jersey City + Hoboken；署名 Ming Cao。当前仅输出两张深色光效评审 PNG，**视觉确认后再生成 GIF**。

- [单群组放大效果](outputs/01_single_group_detail.png)：Hamilton Park（P14），1 个 playground、4 个关联 daycare、4 条邻近连线。视野内其他 daycare 保持暗灰色，仅代表尚未在这一示范中点亮。
- [全市结束帧](outputs/02_citywide_final.png)：全部 62 个 playground、114 个青色匹配 daycare、92 个紫色未匹配 daycare、259 条邻近连线。
- [两图对照](outputs/dark_design_preview.png)；[整体预览](outputs/00_overall_preview.png)与全市结束帧一致。

正式 PNG 均为 2400 × 2000。全市图保留上一版整体预览的范围和真实坐标；放大图是单独的光效评审视图，不改变数据坐标。后续 GIF 使用固定全市范围，放大图不意味着动画必须缩放或移动点位。

## 视觉规则

深蓝灰陆地、更深水面；街道、公园和地名降低亮度，水岸保持可辨识。Playground 是半径 9.5 px 的暖金色核心，daycare 是半径 4.5 px 的统一小圆点。青色 daycare 有明亮核心和小光晕，紫色未匹配点保留较弱光效。未点亮的 daycare 为暗灰色。

金色光源附近的光晕集中在核心附近。完整 400 m 圆形范围仅用极淡透明光区表达，范围光的峰值 alpha 为 3/255，在半径边缘渐变至零；核心光晕也截断在 400 m 内。单群组评审额外显示非常淡的 400 m 圆线，便于核对尺度。不会用明亮大圆遮住底图。

Playground 到其 400 m 内 daycare 绘制细直线，颜色从暖金向青色过渡；线表示直线邻近，**不是路线**。所有 259 条关系均保留。共享 daycare 按唯一 ID 绘制一次，不随相邻 playground 数量重复绘制。光晕合成取每个像素的最大 alpha，不累加重叠光效，避免密集区域过曝。

全市结束帧保留全部金色中心、青色 daycare 和连线，然后加入紫色未匹配 daycare。结束帧图例没有 “awaiting reveal”。右侧只保留当前阶段、两项数量和图例；方法说明在本文件中。

## 未来 GIF 顺序（尚未生成）

1. 所有 daycare 暗灰色显示，先示范 Hamilton Park 一个群组。
2. Playground 核心亮起 → 光区向外展开，最多到 400 m → 连线从核心向 daycare 生长 → 关联 daycare 逐个亮起。
3. 第一组完整显示并短暂停留后，其余 playground 每批约 8 个加入，每个均遵循上述内部顺序。
4. 已亮中心、daycare 和连线持续保留；共享 daycare 不闪回、不重复绘制或叠加亮度。
5. 全部 playground 加入后，按全量数据判定的未匹配 daycare 再以紫色亮起，结尾停留约 3 秒。

阶段及批次计划保存在 `outputs/validation.json`。单群组图中的其他暗灰 daycare 不属于“最终未匹配”类别；最终分类从不依赖示范子集或动画点亮顺序。

## 分析规则与复用数据

本轮**不改变点位、筛选、地点整理和 400 m 计算**。以 playground 为中心，在 **EPSG:32618 / WGS84 UTM 18N（米）**中计算其与 daycare 代表点的直线距离，阈值 ≤400 m。渲染前将全部缓存关系与原坐标下的全量点对重新核对，完全一致。

全部 62 个 playground 参与最终分类，53 个有 daycare 在范围内，9 个没有。共有 **259 条多对多关联**，**114 个匹配 daycare**、**92 个未匹配 daycare**；68 个 daycare 与多个 playground 关联。最终每个紫色 daycare 到全部 playground 的最小距离都大于 400 m。紫色只表示“400 米内没有已收录的 playground”，不表示服务不足或现实中没有游乐设施。

- `outputs/playground_places.geojson`、`playground_crosswalk.csv`：复用的 62 个 playground 地点及来源整理证据。
- `outputs/playground_groups.csv`：每个 playground 的关联 daycare。
- `outputs/daycare_proximity.csv`：全部 daycare 的年龄、匹配状态、最近距离和关联地点 ID。
- `outputs/proximity_links.csv`：全部 259 条邻近关系，以 playground ID 为首。
- `outputs/validation.json`：范围、数量、当前图像参数和未来动画阶段。

### Daycare 来源

复用 `04/data/childcare_official_filtered.geojson`，来自 NJDCF Office of Licensing 持证名录，经 [NJDEP Child Care Centers GIS 服务](https://mapsdep.nj.gov/arcgis/rest/services/Features/Structures/MapServer/4)发布；[官方元数据与定位方法](https://njdep.maps.arcgis.com/sharing/rest/content/items/0bc9fe070d4c49e1a6555c3fdea15b8a/info/metadata/metadata.xml?format=default&output=html)。源记录日期为 2026-10-06，获取日期为 2026-11-03。已有坐标原位使用，可能存在地址匹配误差；本轮无下载、无新增地址定位、无逐家调查。

原始 Hudson County 407 条，两市名称和市界筛选均为 216 条。排除 10 条仅服务 6–13 岁的机构后，保留 **206 条：JC 160，Hoboken 46**。134 条年龄下限为 0 岁、72 条为 2½ 岁，均覆盖学前阶段；年龄未知时保留标记，本批未知 0 条。许可年龄不保证当前各年龄均有班级或名额。筛选见 `official_center_review.csv`。

当前官方底表替换旧 OSM 托育底表。旧 OSM 宽查询有 183 条含学校对象；标签/名称检查后、市界前有 19 个托育候选，市界内 15 个，11 个有 playground 关联，旧图隐藏了 4 个未匹配点。旧图空白不能解释为没有机构。官方内部按规范化名称、地址、城市检查重复，本批无重复键；OSM 名称地址对照见 `osm_official_crosswalk.csv`。缺地址、同址异名或同名多分店不凭距离合并，也不据此推断机构已关闭。

### Playground 与底图来源

只读复用 Day03 的 82 条 OSM playground 点面记录，之前已整理为 62 个地点，本轮不重新合并。历史规则：重叠点面合并；同一已绘制公园内间隙 ≤65 m 的相邻分区通过连通关系归为一处；另按 Day03 复核合并 `way/469610934`、`way/469610947`、`way/469610935` 三个紧邻分区。不把大型公园远处分区一概合并，不逐件计数设备。代表点优先使用被面覆盖的原始点，否则使用最大原始面的内部代表点，不取多个分区的平均坐标。

底图复用 `04/data/background.json`，来源 [OpenStreetMap contributors](https://www.openstreetmap.org/copyright)。NJ 水岸复用 [US Census 2024 1:500000 cartographic boundary](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html)，存在概化；纽约侧复用 [NYC DCP Borough Boundaries 26b](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne)。背景不替代真实地点坐标。OSM playground 覆盖不完整，光效不代表通达性、实际使用、合作关系或服务质量。

## 复现

项目根目录离线运行：

```powershell
python3.14 04/scripts/night_light.py
```

需要重新准备关系表时运行 `prepare_proximity.py`（沿用此前的相同 400 m 计算）。`prepare_official.py`、`prepare_playgrounds.py` 与 `acquire_official.py` 保留作来源准备，命中缓存无需重新下载。依赖 Pillow、Shapely、pyproj，本机只读复用 `02/.deps`。

旧浅色关键帧及旧制图脚本已替换，来源数据和关系表保持不变。未修改 Day01–03，未 commit/push，未生成 GIF。
