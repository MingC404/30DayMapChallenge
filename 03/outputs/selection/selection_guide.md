# Day 03 选点预览

先查看 [全市编号 PNG](jc_selection_preview.png)，再用下面编号选择 4–6 个场地。所有 50 条 OSM 记录保留；编号按本轮几何由北到南排列，不是评分。

全部 86 条官方公园记录只作背景：32 条 OSM 场地有空间相交证据，其中 1 条对应无名官方公园；18 条没有相交。完整覆盖、部分相交和点落入公园分别记录于 park_match_evidence.csv。公园名称是所在公园候选，未更改 OSM 场地名称或边界。

最近公园仅是定位参考，**不代表该场地属于该公园或社区**。未匹配的社区名称为 Not recorded。官方原名称 Newport Green? 的问号保留；01 与两条相邻公园记录相交，18 只有约 45% 位于 BOYD-McGUINESS PARK，不能把部分相交当作完整归属。

陆地背景为 [US Census 2024 Cartographic Boundary](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html)，1:500000 概化岸线，仅供全市定位；场地几何始终使用原 OSM。原始下载与哈希见 land_source.json。公园数据沿用前轮 2018 数据修改日期；设施数据沿用 2026-11-03 OSM 缓存，本轮不添加现场判断。

## 人工复核

复查了所有 OSM 两两几何关系：1 组点面相交、0 组面面相交。另保留 50 m 内近邻，合计 9 对，逐组放大查看形状、位置、原始 tags 和设施；这是桌面复核，未用现场或影像确认。

| 编号 | 复核结论 | 证据与限制 |
|---|---|---|
| 11 / 12 | 不同已绘制分区，功能未明确 | 两个不相交边界，形状与位置不同，间隔 3.14 m；均无设施/年龄标签，不能推定不同年龄组。 |
| 11 / 13 | 不同已绘制分区，功能未明确 | 不规则边界与多边形分别绘制，间隔 13.55 m；无相同几何，不按未命名或距离去重。 |
| 12 / 13 | 不同已绘制分区，功能未明确 | 圆形与多边形相邻但不相交，间隔 2.65 m；功能 Not recorded。 |
| 16 / 17 | 可能重复表达同一场地 | Hamilton Park 命名点位于 playground 面内；点只有名称与 leisure 标签，未见独立分区证据。保留两 ID，选点时视为同一候选组，尚未合并。 |
| 22 / 23 | 不同已绘制分区，功能未明确 | 两个相似弧形面分离 32.78 m；相似形状不构成重复证据，场地名称和年龄均 Not recorded。 |
| 30 / 31 | 同一公园内不同已绘制分区 | Arlington 两个面相距 10.81 m，不重叠；30 内记录 monkey_bars，31 设施 Not recorded；不据此断言两个年龄组。 |
| 33 / 34 | 不同功能分区证据明确 | Lafayette 的 33 内有两个 slide 对象，34 自身 playground=water_sprayer，边界相隔 11.44 m；保留干式游乐区与喷水区两个表达。 |
| 37 / 39 | 不同功能分区证据明确 | Berry Lane 的 37 含婴幼儿秋千、springy、stepping_stone；39 为 playground=splash_pad，边界相隔 16.99 m；不同功能，不作重复删除。 |
| 43 / 44 | 可能点位偏移或独立场地，无法判定 | Liberty State Park 命名点在面外 29.01 m，均 access=yes，缺乏设施或年龄证据；距离与公园名称不足以确定同一场地。保留并标待核实。 |

图证：[九组复核图](overlap_review_atlas.png)；完整记录：manual_overlap_review.csv。未按名称去重，未删除对象，未将面积或设施完整度用于评分。

## 编号清单

设施列包含自身 playground 标签和边界内独立设施对象（带 OSM ID）；点位不接收附近设施。surface、适用年龄、围栏、开放时间、access 等逐项证据见 selection_sites.csv。缺失为 **Not recorded**，不是没有。无归属对象仍见上轮 ../unassigned_facilities.csv，本轮不强行分配。

| 编号 | OSM 名称 | 所在公园候选 / 定位参考 | 几何 | 已记录设施 |
|---|---|---|---|
| 01 | Not recorded | TERRACE AVENUE /  EDWARD CRINCOLI; TERRANCE AVENUE PARK（部分相交） | Polygon | Not recorded |
| 02 | Not recorded | LEONARD GORDON PARK | Polygon | Not recorded |
| 03 | Not recorded | FISK PARK（部分相交） | Polygon | node/11836274078: playhouse |
| 04 | Not recorded | Near PERSHING FIELD (61 m; reference only) | Point | 场地标签 playground=structure |
| 05 | Pershing Field Playground | PERSHING FIELD | Polygon | Not recorded |
| 06 | Not recorded | Near PERSHING FIELD (195 m; reference only) | Polygon | way/1334919520: barrier=fence |
| 07 | Not recorded | Near PERSHING FIELD (290 m; reference only) | Polygon | way/1332532141: barrier=fence |
| 08 | Not recorded | Near CUENO PLACE PARK (17 m; reference only) | Polygon | Not recorded |
| 09 | Children's play area | PAVONIA/MARION PLAYGROUND POOL | Polygon | Not recorded |
| 10 | Not recorded | Newport Green? | Polygon | Not recorded |
| 11 | Not recorded | Near SGT. ANTHONY PARK (234 m; reference only) | Polygon | Not recorded |
| 12 | Not recorded | Near SGT. ANTHONY PARK (236 m; reference only) | Polygon | Not recorded |
| 13 | Not recorded | Near SGT. ANTHONY PARK (231 m; reference only) | Polygon | Not recorded |
| 14 | Not recorded | LINCOLN PARK | Polygon | Not recorded |
| 15 | Not recorded | ENOS JONES PARK / ROBERTO CLEMENTE | Polygon | Not recorded |
| 16 | Hamilton Park Playground | HAMILTON PARK | Point | Not recorded |
| 17 | Not recorded | HAMILTON PARK（部分相交） | Polygon | Not recorded |
| 18 | Not recorded | BOYD-McGUINESS PARK（部分相交） | Polygon | Not recorded |
| 19 | Villa Borinquen playground | Near ROBERTO CLEMENTE LL (113 m; reference only) | Polygon | Not recorded |
| 20 | Not recorded | LINCOLN PARK | Polygon | way/413233046: swing |
| 21 | Not recorded | Near Unnamed official park (176 m; reference only) | Polygon | Not recorded |
| 22 | Not recorded | Near GATEWAY PARK COMPLEX (97 m; reference only) | Polygon | Not recorded |
| 23 | Not recorded | Near GATEWAY PARK COMPLEX (61 m; reference only) | Polygon | Not recorded |
| 24 | Not recorded | Near FITZGERALD-HOLOTA PARK (225 m; reference only) | Polygon | Not recorded |
| 25 | Not recorded | VAN VORST PARK | Polygon | Not recorded |
| 26 | Not recorded | EXCHANGE PLACE（部分相交） | Polygon | Not recorded |
| 27 | Not recorded | Near Unnamed official park (53 m; reference only) | Polygon | Not recorded |
| 28 | Not recorded | Near PAULUS HOOK PARK (21 m; reference only) | Polygon | Not recorded |
| 29 | Not recorded | Near Unnamed official park (169 m; reference only) | Polygon | Not recorded |
| 30 | Not recorded | ARLINGTON PARK | Polygon | node/11878484562: monkey_bars |
| 31 | Not recorded | ARLINGTON PARK | Polygon | Not recorded |
| 32 | Not recorded | LAFAYETTE PARK | Polygon | way/1279587374: swing; baby=yes |
| 33 | Not recorded | LAFAYETTE PARK | Polygon | node/11878484512: slide; node/11878484513: slide |
| 34 | Not recorded | LAFAYETTE PARK | Polygon | 场地标签 playground=water_sprayer |
| 35 | Not recorded | DR. LENA EDWARDS PARK（部分相交） | Polygon | Not recorded |
| 36 | Not recorded | Unnamed official park (name Not recorded) | Polygon | Not recorded |
| 37 | Not recorded | Berry Lane | Polygon | node/11878484454: stepping_stone; node/11878484465: springy; way/1279587372: swing; baby=yes; way/1279587373: swing; baby=yes |
| 38 | Not recorded | Near METRO FIELD (937 m; reference only) | Polygon | Not recorded |
| 39 | spray park | Berry Lane | Polygon | 场地标签 playground=splash_pad |
| 40 | Not recorded | Near LIBERTY STATE PARK (54 m; reference only) | Point | Not recorded |
| 41 | Wildlife Challenge | LIBERTY STATE PARK | Polygon | Not recorded |
| 42 | Not recorded | AUDUBON PARK | Polygon | Not recorded |
| 43 | Liberty State Park Playground | LIBERTY STATE PARK | Point | Not recorded |
| 44 | Not recorded | LIBERTY STATE PARK | Polygon | Not recorded |
| 45 | Not recorded | Near THOMAS McGOVERN PARK (843 m; reference only) | Polygon | Not recorded |
| 46 | Not recorded | LIBERTY STATE PARK | Polygon | Not recorded |
| 47 | Not recorded | BAYSIDE PARK | Polygon | Not recorded |
| 48 | Not recorded | THOMAS McGOVERN PARK | Polygon | Not recorded |
| 49 | Not recorded | COLUMBIA PARK GREENVILLE MEMORIAL | Polygon | Not recorded |
| 50 | Not recorded | LIBERTY STATE PARK | Polygon | Not recorded |

选点提示：16/17 是一组可能重复表达；43/44 尚不能判断，不宜直接当作两个独立场地。30/31、33/34、37/39 可按同一公园下的分区讨论，保留各自 ID。以上只帮助界定选择范围，不代表推荐排名。

复现：`python3.14 03/scripts/selection_preview.py`；缓存齐全可离线运行。输出在 03/outputs/selection/，未改动 Day01/02，未 commit/push。
