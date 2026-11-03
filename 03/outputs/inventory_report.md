# Day 03 — Jersey City playgrounds 数据盘点

本轮为数据盘点与简单全市 PNG；署名 Ming Cao。没有合并来源计数、补造边界或综合评分。

官方 8 条 polygon；OSM 50 条 leisure=playground（46 polygon、4 point）。另保留 25 个设施/属性对象，其中 16 个带 playground 标签，其余为与场地相交的独立围栏。几何有效性检查无错误。

## 来源、字段与日期

官方来源：[Jersey City Parks](https://data.jerseycitynj.gov/explore/dataset/jersey-city-parks-map/)；下载完整 86 条 GeoJSON，再精确筛选 park 名称含 PLAYGROUND 的 8 条。这个筛选不是官方的全市游乐场分类清单。字段：geo_point_2d、park、govt、area、acre、x、4；几何另存于 geometry。area/acre 原值保留，未假定未说明的单位；x、4 含义未说明。无设施字段、逐场地调查日期或原生唯一 ID，导出也无 feature ID，故用内容 SHA256 的前 16 位生成可追溯 ID。
官方元数据 modified=2018-12-11T23:34:57+00:00；data_processed=2018-12-12T14:39:55+00:00；metadata_processed=2026-06-17T13:01:55.771751+00:00。这些不是现场核验日期。下载为 2026-11-03（UTC 文件时间见 provenance.json）。
OSM 市界为 relation/170953（admin_level=8）；按与市界相交选取，原几何不裁切。全市查询覆盖市界 bbox；时间和请求保存在原始 metadata，逐对象 timestamp/version 在输出中。先复用 Day02 缓存，再补全市数据；相同 type/ID 用本轮响应，最终无只来自旧缓存的对象。OSM tags、唯一 type/ID、来源完整保留。
独立设施查询包括 playground、playground:*、leisure=spray_park；另下载 barrier=fence，保留与任何选中场地相交的围栏。未标注为 playground 相关、也不在此查询范围的喷泉等不能据此推断为喷水游乐区。

## 官方 8 条与 OSM 对照

空间重叠视为匹配候选；50 米内仅列候选，不据此赋予名称或合并。polygon 与 point 始终分开；OSM 同源重叠也可能是不同年龄分区或不同对象表达，需要人工复核。

| 图号 | 官方名称 | govt | OSM 对照 |
|---|---|---|---|
| 1 | CLAREMONT AVENUE PLAYGROUND | PRIVATE | source-only in this extraction: Not recorded |
| 2 | PAVONIA/MARION PLAYGROUND POOL | CITY | spatial counterpart: way/798501324 |
| 3 | FIRST STREET PLAYGROUND | CITY | source-only in this extraction: Not recorded |
| 4 | PAT DeANGELO PLAYGROUND | PRIVATE | source-only in this extraction: Not recorded |
| 5 | SIXTEENTH STREET PLAYGROUND | CITY | source-only in this extraction: Not recorded |
| 6 | EGE AVENUE PLAYGROUND | PRIVATE | source-only in this extraction: Not recorded |
| 7 | WAYNE STREET PLAYGROUND | CITY | source-only in this extraction: Not recorded |
| 8 | PAVONIA/MARION PLAYGROUND POOL | CITY | source-only in this extraction: Not recorded |

官方来源独有记录 7 条；OSM 来源独有记录 49 条。完整逐行清单见 source_only_sites.csv，交叉匹配与同源重复候选见 comparison.csv。

PAVONIA/MARION PLAYGROUND POOL 两条同名官方记录边界不相同；保留两个 ID，不能按名称去重。其中一条与 OSM Children’s play area 空间重叠。Hamilton Park 的 OSM 点/面重叠也是重复候选，暂不去重。

## 设施与属性覆盖

以下分母为各来源的场地记录，表示场地自身标签或完全包含的独立对象中有相关记录，不是拥有设施的比例。显式 no 也属于有记录；原值始终显示。缺失统一为 **Not recorded**，不表示没有。

| 属性 | 官方有记录 / 8 | OSM 有记录 / 50 |
|---|---|---|
| swings | 0 | 3 |
| baby_swings | 0 | 2 |
| slides | 0 | 1 |
| climbing | 0 | 1 |
| spray | 0 | 2 |
| surface | 0 | 2 |
| age | 0 | 0 |
| fence | 0 | 4 |
| opening_hours | 0 | 0 |
| access | 0 | 11 |

婴幼儿秋千同时检查 playground=baby_swing 等以及 playground=swing + baby=yes/no；structure 不直接推断为攀爬设施。喷水检查 splash_pad / water_play / water_sprayer / spray_park 等。年龄检查 min_age/max_age/age/age_group；围栏检查场地 barrier/fenced 和独立 fence 几何。
独立对象归属：{'unassigned; no containing site boundary': 13, 'contained in site geometry': 12}。归属只按完整几何被场地 polygon covers 判断；点位场地不生成假边界。跨出边界、仅相交或没有场地边界的对象不强行归属，见 unassigned_facilities.csv；同一对象可对应不同来源的边界，不能将多次引用相加作为设施数。
未归属清单中包含 baby=yes/no 秋千、普通秋千、structure、map 和围栏；这些不计入任何场地的覆盖率。围栏相交也不证明场地完全封闭。

## 交付与复现

- sites.csv：58 条来源分开的场地记录、原始 tags、geometry_type、来源和匹配状态。
- playgrounds_sources.geojson：场地及设施原几何、来源 ID、tags；jc_city_boundary.geojson 单独保留市界。
- facilities.csv / unassigned_facilities.csv：独立对象及归属证据。
- comparison.csv / source_only_sites.csv / attribute_coverage.csv：逐条对照与逐场地十类属性证据。
- summary.json / provenance.json：数量、几何检查、原始文件哈希及日期。

复现：`python3.14 03/scripts/acquire.py`（已有缓存即跳过）；`python3.14 03/scripts/inventory.py`（离线）。运行依赖 Shapely、Pillow；本机只读复用 02/.deps。OSM API fallback 脚本为 Overpass 不可用时备用；本次 POST 成功，先前预取的少量 XML 未参与最终结果。

限制：OSM 完整查询不等于现实设施完整；官方数据较旧且口径不同。地图仅帮助下一轮选择范围，未做交互或正式排版。Day01/02 未修改；未 commit/push。
