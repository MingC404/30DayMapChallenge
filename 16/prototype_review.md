# Day 16 — Collaborative Map · Prototype Review

**Why Are the Trains Late?**  
*An Atlas of NJ Transit Disruptions*  
Question by Chiun Heng Chou · Mapping by Ming Cao

**最新状态：已完成带州界的本地最终 GIF 与 Overview 封面，见第 10 节。** 动画 9 帧、17.5 秒、1440×1440，使用既有 234 条更新调整后的代表记录。没有发布、commit 或 push；原因分类仍是本轮审查口径，不将图像定稿解释为官方确认分类。

原型阶段范围：仅使用已保存的 **2026-11-09—2026-11-15、269 条通知**，新增本地数据审计、公开 GIS 下载及三张静态 PNG；当时未制作 GIF。本报告前九节保留原型阶段的方法与版本记录，第 10 节记录当前正式本地导出。本报告取代旧脚本的临时分类供评审使用，**不是最终分类或已由用户人工签核的结果**。

## 1. 数据清理与数量

269 条全部保存在 [notices_reviewed.csv](data/processed/notices_reviewed.csv)，附原始全文、原始线路标签、来源 URL、页内序号、分类依据、排除原因、更新组和置信度。原始 `data/sample/` 未改动。新标识如 `NJTLOCAL-2026-11-12-011` 是“本地日期 + 保存页面序号”，**不是 NJT 官方通知 ID**。

| 处理阶段 | 条数 | 含义 |
|---|---:|---|
| 已保存原始通知 | 269 | 逐条与原始 HTML 对照 |
| 暂不进入延误／取消分析 | 11 | 保留审计记录，未删除 |
| 合格通知 | 258 | 205 条延误、52 条主列车取消、1 条明确延后发车 |
| 已核对的更新序列 | 20 组 | 依据同车同日、计划班次、原因与连续文本，不跨车合并 |
| 更新组内额外通知 | 24 | 从地图计量中合并，仍可回溯 |
| 原型使用的代表记录 | **234** | 185 条延误、49 条取消；不是唯一事故数或所有延误列车数 |

图中 **retained notices** 指“258 条合格通知中，已确认连续更新每组计一次”的 234 条代表记录。既保留原始通知频率，也提供更新调整后的敏感性版本。地图使用后一版本；它仍然受漏报、通知习惯和未能合并的记录影响，不能称为去重后的唯一事件数。

| 不入图原因 | 条数 | 例子 |
|---|---:|---|
| 登乘／无障碍提示，没有主列车延误或取消 | 3 | 11-09 #5200、#3800、#7880 的 track-level boarding |
| 纯停站模式提示，没有明确主列车延误或取消 | 4 | 11-10 #6620 加停；11-11 #1171 加停；11-13 #3289、#3893 加停 |
| 恢复运行／接近正常 | 3 | 11-10 #3704；11-11 #3818；11-13 #1173 |
| 主列车状态不明确，待人工确认 | 1 | 11-12 #1651 原文缺少取消或延误谓语，虽写工程师不可用仍不推断取消 |

### 原因统计

“原始重标”列是对全部 269 条应用本轮原因规则后的分类，不是上一版脚本的关键词结果。原始纯信息记录仍可有原因；例如三条登乘提示写明 track maintenance，分类保留但不入图。

| 原因类别 | 原始重标 | 合格通知 | 更新调整后／原型 |
|---|---:|---:|---:|
| Mechanical & Equipment | 74 | 73 | **67** |
| Congestion | 41 | 41 | **41** |
| Signal & Switch | 14 | 14 | **11** |
| Slippery Rails & Weather | 28 | 28 | **24** |
| Track & Infrastructure | 33 | 30 | **29** |
| Staffing & Operations | 41 | 39 | **38** |
| External Incidents | 31 | 31 | **22** |
| Other / Unknown | 7 | 2 | **2** |
| 合计 | **269** | **258** | **234** |

两个 Other / Unknown 均明确报告 `speed restriction near Bound Brook`，但未说明限速的根本原因；没有强行归为轨道故障或天气。湿滑／天气类在本窗口全部是 slippery rail conditions，图中注明这一点，不能把它们全部解释成风暴或倒树。

### 线路数量与修正

| 服务组 | 原网站标签数（全部通知） | 修正线路并排除后 | 更新调整后 |
|---|---:|---:|---:|
| ACRL | 34 | 24 | 23 |
| MBPJ | 41 | 39 | 31 |
| MNE | 72 | 71 | 63 |
| MOBO | 14 | 14 | 12 |
| NEC | 41 | 40 | 37 |
| NJCL | 35 | 38 | 38 |
| PVL | 5 | 4 | 4 |
| RVL | 27 | 28 | 26 |
| 合计 | 269 | 258 | 234 |

确认 **10 条线路标签与主通知正文冲突**，全部在 11-12：页内 011、012、013、028、029、031、034、036、037、044 原标签都是 ACRL。按正文分别修正为 NJCL 5、NEC 4、RVL 1。审计表同时保留 `raw_route`、`body_route`、`affected_route` 与 `route_conflict`，不覆盖原标签。没有仅凭列车号推断线路。

## 2. 原因分类与更新处理

### 原因规则

先截取主列车通知，分离 `Please take…`、替代列车、接驳与附带说明，再从 `due to…` / `following…` 等因果语句读取原因。**按因果语句中的顺序区分直接原因和上游原因，不用全文关键词优先级。**

- `congestion resulting from switch issues` → 直接 Congestion；上游 Signal & Switch。
- `equipment availability resulting from mechanical issues` → 直接设备可用性；上游机械问题；两者都在 Mechanical & Equipment 大类，但原文层次分开保存。
- `equipment availability resulting from switch issues` → 直接 Mechanical & Equipment；上游 Signal & Switch。
- `accommodating customers from cancelled train #0808` → 直接 Staffing & Operations；上游记录为另一班取消列车。**不把另一通知中的机械原因自动传播过来。**
- `overheard wire issues near Newark Broad Street` → 中等置信度解释为 overhead wire，保留拼写和依据。旧脚本将 `Street` 的字串 `tree` 匹配为天气；本轮用词边界、原因语句修正。
- `mechanial issues` → 中等置信度按明确拼写变体读取，不改写原文。
- 旧脚本的 canceled 布尔值会命中“被取消的上游列车”。本轮主列车状态独立解析，因此不会把实际晚点、但搭载取消列车乘客的班次计成取消。

全体 269 条中，**41 条含多个可识别原因短语，52 条存在明示上游关系或上游列车背景**。这些不是 41 或 52 起多原因事故。`reported_cause`、`direct_cause`、`cause_category`、`upstream_cause`、`upstream_category`、`causal_relation` 和 `classification_basis` 分开保存。主图每条代表记录只进入一个直接原因类别；未来可另做上游原因版本，不能两套计数混用。

合格通知的原因置信度：High 253、Medium 3、Low 2。High 只表示原文原因短语清楚，**不表示官方证实其因果真实性、完成独立人工复核或分类最终有效**。所有记录的 `classification_status` 都是 provisional agent review。中等置信度包括拼写解释和 #1006 发车时间调整；Low 是两条未说明根因的限速。

### 连续更新与歧义

更新组见 [update_groups.csv](data/processed/update_groups.csv)。20 组由本轮逐条阅读核对，并以显式组清单固化在 [clean_notices.py](scripts/clean_notices.py)，可逐组复审，不使用自动 train-day 聚合覆盖不确定性。

- 11-11 #1357 同一计划到达、同一 Broadway 占轨车辆，7 条增长的延误估计归一组。
- 11-15 #4682 同一计划到达、同一 Hammonton EMS 协助，20→25 分钟归一组；不累加为 45 分钟。
- 11-11 #6209 明示 Correction，只修正计划到达时间；归同组并保留修正前正文。
- 11-12 `#432` / `#0432` 和 `#853` / `#0853` 只在列车号字符串中补零，结合相同计划时间、原因核对归组。
- **没有合并** 11-12 #3153 的轨道／电线问题通知与“为取消班次加停”的运营通知：同车同日但原因变化，无法确认是不是一个事件，保留两条代表记录。
- **没有跨列车合并** Broadway、Millburn 或 Millington—Stirling 的相似地点通知；这些可能是同一外部事件影响多列车，也可能有更多关系，缺少官方事件 ID。
- **没有跨日按相同文字去重**。旧报告找到的三组相同正文来自不同日期，不能据此删除。
- #3818、#1173 有取消后恢复。恢复通知单独排除，但先前已经发出的取消通知保留一次：指标是“这周报告过的服务异常”，不是最后一条状态或最终实际取消数。
- #0808 的一条正文附带 #1006 调整信息；本轮只计主列车 #0808，附带文本原样保留并标记。#1006 已有独立通知，不再从复合正文拆出第二条，避免双计。

组内选择最近一条**合格异常通知**作为代表，按同日页面倒序的最小序号定位；恢复通知不取代已经发出的异常通知。所有组内原记录仍在完整审计表。

## 3. 空间精度

| 本轮保守标注，全部 269 条 | 条数 |
|---|---:|
| Exact incident location | 0 |
| Station-level location | 2 |
| Affected rail line only | 267 |
| System-wide / unknown location | 0 |

仅两条在原因语句中明确写 `at … Station`：11-09 #3848 的 Newark Penn Station 警务，以及 #3228 的 Aberdeen-Matawan Station 医疗协助。没有为通知生成任何事件坐标。

另有 11 条 `at Ho-Ho-Kus`、`at Netherwood`、`at Otisville` 等站名候选，但同名城镇、上游列车或旅客转乘过程可能混淆，**仍保留在线路级精度**，详见 `station_name_candidate` 与 `location_role`。`near Spring Lake`、`near Long Branch Station` 也不等于在该站。区间、近似地名保存在 `incident_location_text`；取消地点另存 `cancellation_location`，目的地和计划到发站不能替代原因位置。

这些精度数量是“本轮保守可使用的表达精度”，不是对所有通知潜在空间信息的最终判定。地图上的点全部是 GIS 参考枢纽，不是事件点。

## 4. GIS 来源、线路对应与共享轨道

按用户指定服务下载：[Rail Lines of NJ Transit · FeatureServer/0](https://services6.arcgis.com/M0t0HPE53pFK525U/arcgis/rest/services/NJTRANSIT_RAIL_LINES_1/FeatureServer/0)。公开 `query` 使用 `where=1=1`、`outFields=OBJECTID,LINE_CODE,LINE_NAME`、`outSR=4326`、`f=geojson`，取得 **13 个线路要素**；没有使用登录、受保护端点或其他通知数据源。原始响应见 [rail_lines.geojson](data/gis/rail_lines.geojson)。

枢纽位置来自同一 GIS 部门维护的 [Rail Stations of NJ Transit](https://services6.arcgis.com/M0t0HPE53pFK525U/arcgis/rest/services/NJTransit_Rail_Stations/FeatureServer/0)。其站名、`RAIL_SERVICE`、`RAIL_SERVICE_NAME` 协助核验服务关系。

| 通知代码 | GIS 线路名称／代码 | 映射规则 |
|---|---|---|
| ACRL | Atlantic City Line / AC | 单一服务组 |
| MBPJ | Main Line / ML + Bergen County Line / BC + Southern Tier / ST | 一个组合服务组；GIS Port Jervis 站的 RAIL_SERVICE_NAME 明写 Port Jervis Line、LINE_CODE=ST；Suffern 站为 ML,BC |
| MNE | Morristown Line / ME + Gladstone Branch / GL | 一个 Morris & Essex 组合服务组；不推断具体支线 |
| MOBO | Montclair-Boonton Line / MC | 单一服务组 |
| NEC | Northeast Corridor / NE | 单一服务组；不自动把 Princeton Dinky 计入 NEC 通知 |
| NJCL | North Jersey Coast Line / NC | 单一服务组 |
| PVL | Pascack Valley Line / PV | 单一服务组 |
| RVL | Raritan Valley Line / RV | 单一服务组 |

Princeton Dinky / PRIN 与 Meadowlands / SL 只作为低对比网络背景，本样本没有归入它们的合格通知。零通知不表示服务从未异常。所有 8 个通知服务组均找到 GIS 对应；**具体班次的支线归属与真实受影响区间仍 Unknown**，没有为了填满地图强行分支。

MBPJ、MNE 的组件先作服务组几何合并，再关联一个组级计数。高亮整个组合范围只表示通知归属该服务组，**不代表组内每条支线发生同样数量的事故**；标题、脚注和图例要同时阅读。

### 重叠检查与绘制规则

使用 UTM 18N（EPSG:32618），在 5 m 几何简化后检测距离 ≤15 m、连续长度 ≥300 m 的共线候选，排除单纯交叉点，发现 **17 对服务组存在共线区段**。例如 NEC—NJCL 约 34.6 km，MNE—MOBO 约 64.4 km。后者包括铁路服务在西部与东部共享的几何，而不只是 Penn 接近区。它们是绘图近似检查，**不是官方轨道所有权或可求和的运营里程**；完整数值在 [gis_validation.json](data/gis/gis_validation.json)。

原型按该原因的服务组计数从小到大绘制，较大计数的线条覆盖较小计数；线条明度预先混合背景后以不透明笔画绘制，避免叠加透明度制造额外强度。**共享几何显示占主导的最大服务组计数，不将不同服务组的数值相加**。同一服务组分支内部也不累加。接近但不完全重合的线条仍可能出现边缘差异，因此精确数值以侧栏和分析表为准。未来可对共享区段设计并列服务带，现阶段不把图面颜色解释成轨道段的事故频率。

### 跨州与端点验证

以官方站点到原始铁路几何的最短距离核查：

| 站点 | 距网络最近位置 |
|---|---:|
| New York Penn Station | 5.4 m |
| Newark Penn Station | 2.0 m |
| Secaucus Junction | 11.2 m |
| Hoboken Terminal | 0.7 m |
| Trenton | 1.3 m |
| Philadelphia 30th Street | 65.0 m |
| Port Jervis | 35.8 m |

GIS 包含纽约 Penn、纽约州 Port Jervis 和宾州 Philadelphia 30th Street，未在 NJ 州界裁切；Atlantic City 线路确实过河进入 Philadelphia。几何有些端点在站外：NEC 向 Trenton 站南侧延伸约 2.6 km，不能机械地把 LineString 端点当站点。Main/Bergen 的 Suffern 北侧端点与 Southern Tier 相接，Port Jervis 并非截断于州界。**这只验证上述服务终点的覆盖，不保证每一股道、每一班次路径及 2026 年所有运营变化都完整。**

## 5. 视觉与符号

三图均为真实 GIS 地理形状，投影 EPSG:32618，渲染几何简化容差 25 m；保留原始坐标下载，不更改原始数据。不是示意线路图、核密度或随机事件坐标。主图范围固定，纽约／新泽西／宾州保持地理关系，北向与公里比例尺用于 A、C。都市放大图是独立局部比例，不能用主图比例尺测量。

- 背景恢复暖米色纸张 `#F3EDE1`，正文 `#383832`，辅助文字 `#77766E`。底网使用清晰但克制的暖灰 `#B7B4AA`、0.75 pt；分隔线 `#DCD5C8`、网格线 `#E6DFD3`，避免与强调线路竞争。标题 Georgia，数字／索引 Consolas，正文 Segoe UI。
- 每个原因使用独立的低饱和复古色相；计数线宽保持 `0.65 + 4.1 × n/20 pt`，所有图统一 0–20 数值上限。最大实际服务组值为 18，未截断。为保证少量通知的彩线在米色底上仍可辨认，强调色与背景的混合权重改为 `0.8 + 0.2 × n/20`；只是视觉对比调整，不改变数值、组别或统计尺度。背景线表示网络／该类未报告，不表示可靠性为零。
- 颜色只编码原因，线宽主要编码组级通知量。不同色相的亮度不能代替数值比较，尤其应结合 Small Multiples 数字。
- 每条记录只计入一个服务组和一个直接原因。线路分母、全部列车运行次数、实际晚点分钟均没有纳入，因此没有概率、可靠性排名或乘客损失推断。
- 仅标注重要参考枢纽与少量终点，A、C 用都市放大图分开 New York Penn、Newark Penn、Secaucus、Hoboken，避免全站名遮挡。点符号只作地理参照。
- 所有原型左上角统一为 `DAY 16 / COLLABORATIVE MAP`，移除年度挑战长标题。统一署名为 `Question by Chiun Heng Chou · Mapping by Ming Cao`，绘图脚本以一个共享常量提供署名，后续 GIF 沿用。
- C 的左侧地图画布高度由 0.58 增至 0.64，网络等比例放大约 **10.3%**，上下留白减少。地理范围、投影、坐标和 `aspect='equal'` 保持不变，没有单独拉伸横轴或纵轴；比例尺随地图一起更新。`C_MAP_RECT` 与 `C_LEGEND_POSITION` 是固定布局常量，所有后续原因帧复用相同地图范围、线路位置、枢纽位置和 0–20 图例尺度。

| 原因 | 强调色 |
|---|---|
| Mechanical & Equipment | `#C58B52` 赭金 |
| Congestion | `#B86D7C` 暗玫瑰 |
| Signal & Switch | `#9582AC` 灰紫 |
| Slippery Rails & Weather | `#5E9E98` 灰青绿 |
| Track & Infrastructure | `#85985D` 橄榄绿 |
| Staffing & Operations | `#6D87B3` 灰蓝 |
| External Incidents | `#A17B58` 棕赭 |
| Other / Unknown | `#99968D` 暖灰 |

## 6. 三张原型与推荐

### A. Geographic Network

[day16_geographic_network.png](outputs/prototypes/day16_geographic_network.png) · 1760 × 1920

机械／设备示例：**67 条代表记录，来自 73 条合格通知**。完整地理网络配服务组计数侧栏、统一图例、枢纽放大图。优点是精确数字可核对，作为静态海报内容完整；缺点是版式较高、信息量大，缩成手机 GIF 后部分侧栏字会偏小，组合服务范围仍需脚注。

### B. Small Multiples

[day16_small_multiples.png](outputs/prototypes/day16_small_multiples.png) · 2720 × 1600

展示更新调整后前四大直接原因：机械设备 **67**、拥堵 **41**、人员运营 **38**、轨道设施 **29**。四图使用相同地理范围、投影、线宽数值标尺和参考点。优点是无需记忆上一帧，空间差异最容易横向比较；缺点是横幅缩小后铁路分支较细，单张图未展示全部原因，不能作为完整原因总表。适合作为 GIF 的静态对照图或最后一帧。

### C. Animated GIF Frame Concept（静态 PNG）

[day16_gif_frame_concept.png](outputs/prototypes/day16_gif_frame_concept.png) · 1920 × 1920

湿滑轨示例：**24 条代表记录，来自 28 条合格通知**，MNE 服务组 16。固定主标题、原因标题、总数、日期、图例、数据来源、空间含义脚注和原因序列条；本轮左侧网络等比例放大约 10.3%，保持完整南北端点、枢纽标注和比例尺；没有实际播放或生成 GIF。优点是适合固定画布逐原因切换，重点明确；缺点是不能同步比较所有原因，而且小字脚注在社交媒体缩图时仍需简化。顶部 `04 OF 08` 仅是八类别方案的版式示例，未决定最终必须八帧。

**推荐以 C 为未来 GIF 主版式，吸收 A 的精确服务组侧栏，B 保留作静态对照。** 当前只提交静态原型供 Ming Cao／Chiun Heng Chou 选择。若选 C，建议锁定地图、图例、标题和枢纽位置，仅切换原因、色相、计数和一条事实说明；淡入淡出不改变数据窗口。初步可保留七个有量级的大类，Other / Unknown 的 2 条可在结尾说明或单独短帧，待用户决定。不得用“事件发生位置”措辞，也不应把极少数通知的类别渲染成统计显著热点。

## 7. 数据来源、署名与许可状态

1. 通知：[NJ Transhit 日期页面示例](https://njtranshit.com/graph/count/2026-11-15)，本轮全部来自既有七天快照；未联网重新获取通知、未扩展至 30 天。网站提取分类和官方原文链仍没有最终证明。**衍生统计／再发布许可 Unknown**，本次不公开完整通知、HTML、审计 CSV 或地图。
2. 线路：[ArcGIS item e6701817be974795aecc7f7a8cc42f79](https://www.arcgis.com/home/item.html?id=e6701817be974795aecc7f7a8cc42f79)，owner `NJT_GIS`，署名 **NJ TRANSIT GIS Department.** 元数据说明由 GIS 部门维护，基于 2019 TRO-7、2012 PTC imagery、2017–2019 NAIK survey 与 2007 LiDAR。说明来源不等于 2026 年所有线路变化已反映。
3. 站点：[ArcGIS item 4809dada94c542e0beff00600ee930f6](https://www.arcgis.com/home/item.html?id=4809dada94c542e0beff00600ee930f6)，同为 `NJT_GIS` 与相同署名。
4. 线路 `licenseInfo` 为 “Not for design purposes. Not survey grade data.”；站点类似，强调不用于设计、非测量级。**这是用途／精度声明，不是清晰的开放数据再分发许可证；公开衍生 PNG/GIF 的完整授权仍待确认。** 本轮局限于用户授权的本地内部评审，不据此声称已获公开发布许可。
5. 服务／item 元数据原文和公开请求清单保存到 `data/gis/` 与其 `manifest.csv`。没有使用底图瓦片、第三方地图截图或 AI 生成的地理线形。

## 8. 仍需人工确认

- 逐条抽查或签核本轮原因、10 条线路修正与 20 组更新关系；`High` 仍非最终批准。
- #1651 是否应计取消；#3153 的两种原因是否为同一序列；11-12 缺主列车号的 NJCL 通知是否能与其他记录对应。当前都未强行补全或合并。
- 是否接受“报告过的异常”保留已恢复班次的历史取消通知；若要研究最终真实取消，现有快照不足以保证正确状态。
- 是否采用代表通知数作为 GIF 主指标，或保留原始合格通知数作为通知频率分析；两种频数均已输出。
- MBPJ、MNE 采用组合服务范围是否满足叙事；若需要具体支线，应先补充有依据的班次路径对应，再改变图面。
- 共享轨道采用最大组值覆盖能否被受众理解；最终版可以考虑并列服务带或用侧栏明确各线路差异。
- 取得 NJ Transhit 与 GIS 衍生发布许可，确认署名与样本发布边界。没有向任何维护者自动发送消息。
- 在目标显示尺寸检查标题、枢纽标签和脚注。三张原型已经本地打开检查，避免放大图遮住南部网络；尚未进行最终 GIF 的压缩／动效测试。

## 9. 文件与复现

| 文件 | 用途 |
|---|---|
| `data/processed/notices_reviewed.csv` | 269 条完整审计，保留原文与原标签 |
| `data/processed/analysis_representatives.csv` | 原型使用的 234 条代表记录，含本地追溯 ID |
| `data/processed/update_groups.csv` | 20 组明示合并清单与依据 |
| `data/processed/category_counts.csv` | 三种口径的原因统计 |
| `data/processed/cause_route_counts.csv` | 原因 × 服务组，两种入选口径 |
| `data/processed/route_gis_crosswalk.csv` | GIS 线路组合对应 |
| `data/processed/cleaning_summary.json` | 清理数量、排除原因、空间精度等汇总 |
| `data/gis/gis_validation.json` | 几何清单、端点、重叠诊断和枢纽距离 |
| `scripts/clean_notices.py` | 离线重建清理表，不调用网站 |
| `scripts/inspect_gis.py` | 离线 GIS 核验 |
| `scripts/render_prototypes.py` | 只渲染三张 PNG，不生成 GIF 或网站 |

主要审计字段包括 notice identifier、date、affected route、reported/direct/upstream cause、category、notification type、duplicate/update group、location precision、classification confidence、classification basis、status 与 exclusion。时间沿用网站显示值，未臆造时区。用 HTML 对照 CSV 时发现一条末尾 NBSP 空白差异，保存两个版本并标记；其余 ASCII 正文逐字一致，未改变原文件。

依赖见 [requirements.txt](requirements.txt)。在本机可运行：

```powershell
& C:\ProgramData\anaconda3\python.exe 16/scripts/clean_notices.py
& C:\ProgramData\anaconda3\python.exe 16/scripts/inspect_gis.py
& C:\ProgramData\anaconda3\python.exe 16/scripts/render_prototypes.py
& C:\ProgramData\anaconda3\python.exe 16/scripts/validate_outputs.py
```

Shapely/PyProj 安装在 `16/.deps/`，脚本会优先读取；无需修改其他日期环境。依赖与字体缓存已在 Day 16 局部忽略，不属于待提交数据。所有原始记录及新表均保持本地，未接入 GitHub Pages 或 gallery 构建脚本。检查结果见 `data/processed/validation_results.json`：数量守恒、ID 唯一性、未强行合并的歧义记录、分组／矩阵一致性、GIS 映射、PNG 尺寸与完整性均通过；原清单中的 **18 个样本文件 SHA256 全部未变**。

### 暖米色视觉修订核查

本轮仅修改绘图样式、署名、C 版等比例尺寸与本报告，未运行数据清理或 GIS 重建脚本。对 `16/data/` 全部文件作修订前后 SHA256 对照，确认数据、分类与统计文件字节未变。三张 PNG 重新打开核查署名、纸张色、底网可见度、标签位置和地图完整性；尺寸维持 1760×1920、2720×1600、1920×1920。最新图片校验值记录在 `outputs/prototypes/visual_revision_checks.json`；`data/processed/validation_results.json` 保留上一阶段记录，其中 PNG 校验值属于此前深色版。未生成 GIF，未修改 Day 01–15，未 commit 或 push。

## 10. 最终本地 GIF 与州界

### 导出文件

| 文件 | 尺寸／参数 | 大小 |
|---|---|---:|
| [day16_njt_disruptions.gif](outputs/day16_njt_disruptions.gif) | 1440×1440，9 帧，17.5 秒，无限循环 | **291,022 bytes（284.2 KiB）** |
| [day16_njt_disruptions.png](outputs/day16_njt_disruptions.png) | 1440×1440，Opening Overview 完整构图 | **203,055 bytes（198.3 KiB）** |
| [animation_manifest.json](outputs/animation_manifest.json) | 帧次序、时长、统计、样式、数据校验值、坐标变换矩阵 | 本地复现记录 |
| [final_validation.json](outputs/final_validation.json) | 编码后 GIF 验证结果 | PASS |
| [animation_contact_sheet.png](outputs/animation_contact_sheet.png) | 九帧并列检查图 | 仅诊断 |
| [web_readability_preview_960.png](outputs/web_readability_preview_960.png) | 960px 宽的正常网页尺寸检查 | 仅诊断 |

使用用户本轮明确要求的“左地图、右原因／数字／说明”布局，沿用浅米色 C 的固定左右画布，而不是 B 的四图并列版。主标题、副标题和署名均固定为已确认版本。保留米色 `#F3EDE1`、七种复古强调色、重要参考枢纽与 25 km 主图比例尺。

### 州界数据源与裁剪

采用 **U.S. Census Bureau · 2025 Cartographic Boundary Files · States · 1:500,000**，从 [Census 官方下载页](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.2025.html)链接的 [州界 Shapefile ZIP](https://www2.census.gov/geo/tiger/GENZ2025/shp/cb_2025_us_state_500k.zip)取得。此产品由 MAF/TIGER 几何概化，适合小比例尺专题地图；这里不把它当测量级或法律界址。

本地来源及衍生文件位于 `data/gis/census_states/`：

- `cb_2025_us_state_500k.zip`：原始公开下载，不改写源几何。
- `state_borders_clipped_utm.geojson`：仅州际共同边界，EPSG:32618，严格裁剪到地图图框。
- `provenance.json`：源 URL、源 ZIP SHA256、保存 UTC、源 CRS、固定范围、边界对与处理方法。

源 CRS 为 NAD83 / EPSG:4269，重投影为既有 UTM 18N / EPSG:32618。没有改变铁路投影、位置、地理比例或图框。固定范围（单位 m）仍为：

```text
x: 472075.0882343396 — 600988.547794272
y: 4346213.670485008 — 4609134.765382982
```

检查全部州要素与该图框相交的结果是 **New Jersey、New York、Pennsylvania**；其他州没有进入当前图框，因而没有为了显示其他州或 NJ 全貌而扩图。

**州界不等于海岸线。** 本次不是描整个州 polygon 的外轮廓，而是先取两州原始 polygon 边界的共同部分，再投影并与固定图框求交。这样只画 NJ–NY、NJ–PA、NY–PA 的真实州际边界，不把 NJ 大西洋岸线误标成州界。也没有对“已裁剪 polygon”再取 boundary，避免把矩形图框边缘错误生成州界。

三段州际边界在框内的概化几何长度分别约为 NJ–NY 111.644 km、NJ–PA 270.967 km、NY–PA 63.783 km，只是来源与裁剪诊断，不用于铁路统计。小比例尺数据不代表完整的海上法定管辖边界。

绘图使用 **`#D8D1C5`、0.55 pt、无填充**；州界 z-order 0.5，铁路底网 z-order 1，强调服务线路更高。几何预先裁剪，主图和都市放大图还分别使用各自 axes patch 做像素裁剪。网格、州界、枢纽和位置在所有帧中不动。

### 统计与计数规则

正式 GIF 的分类总数、服务组计数和 Overview 全部直接读取同一个文件：`data/processed/analysis_representatives.csv`，没有重新分类或重新处理原始通知。数据表仍为 **269 原始通知 → 排除 11 → 258 合格通知 → 合并已确认更新中的额外 24 条 → 234 条代表记录**。

每条代表记录只有一个用于动画的**直接原因大类**，明示上游原因仍只留在审计字段，不作为第二次计数。因此七个原因可以相加，但须加上 Overview 中的两条 Other / Unknown 才等于总数：

| 动画帧 | 显示数量 | 停留时间 |
|---|---:|---:|
| Opening Overview | **234**（含 Other / Unknown 2） | 2.0 s |
| Mechanical & Equipment | **67** | 2.0 s |
| Congestion | **41** | 2.0 s |
| Signal & Switch | **11** | 2.0 s |
| Slippery Rails & Weather | **24** | 2.0 s |
| Track & Infrastructure | **29** | 2.0 s |
| Staffing & Operations | **38** | 2.0 s |
| External Incidents | **22** | 2.0 s |
| Closing Overview | **234** | 1.5 s |

**67 + 41 + 11 + 24 + 29 + 38 + 22 = 232；232 + 2 = 234。** Other / Unknown 没有单独成帧，但 Overview 明写 `232 across seven causes + 2 Other / Unknown`。这些是更新调整后的通知记录，仍不是独立事故数，也不是最终真实取消班次数。

**原因帧**继续采用相同 `0.65 + 4.1 × n/20 pt` 线宽公式、0–20 标尺与固定地图，不逐帧自动拉伸。最大服务组类别值为 18，没有截断。组合线路与共享轨道仍按前述规则绘制，不拆分为多个事件，不在共享段相加。

**Overview** 的所有服务线路采用一致灰色与 1.6 pt 线宽，只作全网服务范围概览，**不把服务组总数 63 等强行塞入原因帧的 0–20 标尺**。旁边明确写 `Overview lines are unweighted service extents`；底部说明 0–20 计数比例尺适用于原因帧。总数 234 是侧栏统计，不是轨道段强度。

所有帧底部保留以下完整说明（版面分两行）：

> Linked updates counted once. Highlighted lines indicate affected services, not incident locations or delay probabilities.

同时保留 `LOCAL REVIEW · CLASSIFICATIONS PROVISIONAL`。视觉成品完成，不等于原因分类获得官方认可或数据再利用许可已明确。

### 动画、编码与加载

- 9 帧直接切换，不加入移动、旋转、缩放或额外淡入帧；总时长严格为 **17,500 ms**，`loop=0` 无限循环。
- 帧画布、主图矩形、地理 extent、投影、都市放大图、枢纽、日期、标题和署名完全固定；只改变当前原因内容、数字、说明、强调色与线路高亮。
- 首尾 Overview 逐像素相同，闭环无位置跳变。连续循环时，Closing 1.5 秒与下一轮 Opening 2 秒自然形成 3.5 秒稳定概览。
- 所有帧共用一个 256 色调色板，并预留米色背景、文字／底网和七种强调色的精确 RGB 值。禁用抖动，使用 GIF 差分帧压缩。七种原因的数字强调色在编码后的 GIF 中均匹配原配色，RGB 最近误差为 0。
- GIF 仅约 **284 KiB**，封面约 **198 KiB**，不依赖外部瓦片或运行时资源；对将来的静态网站加载体积较轻。未部署公网，因此没有虚构 GitHub Pages 网络延迟或真实加载测速结果。
- 支持文字不小于 9 pt；在 960px 宽的网页显示尺寸下约为 10px，主标题、原因与总数更大。已检查该尺寸预览与全部九帧检查图。手机极窄屏等比缩图仍会使辅助标注变小，不能声称所有屏宽同样可读；原始 PNG/GIF 保持 1440px 可放大查看。

### 检查结果

[final_validation.json](outputs/final_validation.json) 为本轮最新检查记录，旧原型检查中“没有 GIF”仅代表当时阶段，不适用于本轮输出。

1. 三段州界几何全部位于原图框内；没有人工矩形边界线；绘制裁剪开启，且在铁路下方。
2. 9 帧主图及 inset 的实际坐标变换矩阵、bounds 和位置完全相同。
3. 解码并合成 GIF 后，标题、署名、日期、说明等固定区域在所有帧的**差异像素均为 0**；无抖动或调色板导致的文字闪烁。
4. 首尾解码像素完全一致；实际 GIF 帧数、每帧时长和循环标志均符合要求。
5. 数量与类别从同一代表表校验；每条更新组唯一；七类 232 加未知 2 等于 234。
6. PNG 封面与 Opening Overview 的原始渲染逐像素一致；GIF 为同一渲染的量化版本，平均 RGB 通道误差约 1.364/255，主色精确保留。
7. 所有文本都在画布内；已检查主图完整性、必要枢纽、比例尺、州界低对比与 960px 网页预览。
8. 既有 `16/data/` 文件（新增 `census_states/` 除外）与本轮开始前 SHA256 全部相同。未修改分类表、原始通知或旧统计。

### 复现

新增脚本：

```powershell
# 使用保存的 Census ZIP 离线派生州界；不重新抓取通知。
& C:\ProgramData\anaconda3\python.exe 16/scripts/prepare_state_boundaries.py
& C:\ProgramData\anaconda3\python.exe 16/scripts/render_final.py
& C:\ProgramData\anaconda3\python.exe 16/scripts/verify_final.py
```

`render_prototypes.py` 已加入 main guard，作为复用的样式／几何模块被导入时不会覆盖三个旧原型。`render_final.py` 和 `verify_final.py` 不进行网络访问、不运行清理脚本，输出单帧 PNG 留在 `outputs/frames/` 方便复核。依赖中新增 `pyshp==3.1.9`，仍安装在 Day 16 的 `.deps/`，没有修改其他日期环境。

**发布状态：本地最终成品，未公开发布。** NJ Transhit 再利用许可仍 Unknown，Census 州界来源不会消除通知或铁路 GIS 的许可问题。本轮没有上传原始 HTML、通知全文、GIF 或 PNG，没有加入 GitHub Pages／学院仓库，没有修改 Day 01–15，没有 commit 或 push。等待用户确认成品。
