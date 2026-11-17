# Day 16 — Data feasibility investigation

**Why Are the Trains Late? — An Atlas of NJ Transit Disruptions**  
合作：Guoguo 提出 NJ Transit 延误原因及空间分布问题；Ming Cao 负责数据分析、制图与可视化。调查日期：2026-11-16（America/New_York）。本阶段未制作地图、GIF 或页面。

**结论：技术上 Conditional Go，直接公开发布暂 No-go。** NJ Transhit 有无需登录的逐条通知和日期查询，远超过 30 天；适合表达“按通知原因划分的受影响线路”，不足以直接制作精确事故地点图。网站自身的数据再利用许可、完整采集历史、原始官方接口及去重规则均为 **Unknown**。公开浏览和 robots 允许抓取不等于获得再发布许可。

## 1. Data source and provenance

- [NJ Transhit 首页](https://njtranshit.com/)是第三方透明度追踪网站；不是 NJ Transit 官方数据库。通知正文使用 NJT 运营通知语言，但抓取来源、采集周期、官方通知 ID 和原始发布时间与入库时间的关系 **Unknown**。
- [日期页面](https://njtranshit.com/graph/count/2026-11-15)提供完整通知正文；页面有日期选择表单，公开导航就是 `/graph/count/YYYY-MM-DD`，不是猜测的后台接口。
- [原因列表](https://njtranshit.com/excuses)、[原因详情示例](https://njtranshit.com/excuse/2/mechanical-problem)、[线路列表](https://njtranshit.com/routes)、[列车详情示例](https://njtranshit.com/train/0725)提供交叉查询。
- 检查直接返回的 HTML 与页面引用的 `script.min.js`：通知与 C3 图表数据由服务端嵌入 HTML；本站脚本只处理搜索、菜单和分享，未发现用于通知的 fetch/XHR 接口。没有运行真实浏览器 Network 面板，因此不能断言网站完全没有其他请求。
- [robots.txt](https://njtranshit.com/robots.txt)是 `User-agent: * / Disallow:` 空值，并链接 [sitemap.xml](https://njtranshit.com/sitemap.xml)。已检查 sitemap 和样本页面链接，未发现公开 JSON/CSV 下载、API 文档、条款或源码仓库链接。网页搜索 `njtranshit github/source/API/license` 未确认相关公开源码仓库；仓库是否存在 **Unknown**。未枚举后台路径或访问报错中泄露的内部资源。
- 本次仅低频 GET 公开页面，没有登录、绕过限制或大批量抓取。网络直连最初被本地沙箱阻止，获工具批准后取得 HTTP 200；这不是网站反爬拦截。

## 2. Temporal coverage

首页“Top Rail Delay Excuses / Top Inconvenienced Trains”标示最近 30 天，这是排行榜窗口，**不是历史保留期限**。机械问题详情显示首次记录 2014-02-12；[当天历史页](https://njtranshit.com/graph/count/2014-02-12)仍有正文，已保存。2026-11-16 首页有当天记录。因此已验证记录跨及 2014-02-12 与 2026-11-16；最早全站记录、期间连续性、缺失日、是否所有通知均入库为 **Unknown**，不能称作完整十二年数据。

为避免当天未结束与不同缓存时间混用，实际统计采用 **2026-11-09—2026-11-15 七个完整日历日**，逐日直接下载 HTML。显示时间无时区偏移，网站时区 **Unknown**，尚不能将这些显示时间当作已确认的纽约时区事件时间。

| 日期 | 解析通知数 |
|---|---:|
| 2026-11-09 | 51 |
| 2026-11-10 | 33 |
| 2026-11-11 | 42 |
| 2026-11-12 | 77 |
| 2026-11-13 | 46 |
| 2026-11-14 | 9 |
| 2026-11-15 | 11 |
| 合计 | **269** |

这是网页记录数，不是唯一事故数或全部晚点列车数。七天记录数与保存的首页逐日线路图表合计相符。搜索工具缓存有明显过时现象：11-12 页面摘要只有较早的部分通知，直接下载却有 77 条；机械原因详情缓存累计 29,311，直接页面为 29,575。统计以本地保存的直接响应为准，不能拼接不同时间的网页摘要。建议正式阶段若获许可，使用完整 30 天同一批次的日期页面；本次没有抓取整月。

## 3. Available fields

原始载体是 HTML，不是有文档的数据库 schema。CSV 中衍生字段均见 [解析脚本](data/sample/analyze.ps1)。

| 字段 | 是否可取得及示例 | 限制 |
|---|---|---|
| 通知显示时间 | `November 15th, 2026 at 6:47pm` | 无 offset；非已验证事故开始时间 |
| 受影响线路标签/代码/URL | Atlantic City Rail Line / ACRL / `/route/1/...` | 历史标签存在错误，需正文校验 |
| 通知全文 | 有，保存在 CSV `text` | 有些正文一次包含初始通知及 Update |
| 原因链接 ID、slug、原文片段 | `/excuse/2904/request-for-ems-assistance` | 可能多原因，也可能有明确原因却没有链接 |
| 列车号 | `#4682`；CSV 保留首个 `train #...` | 替代列车和上游列车也出现在正文；必须保留前导零 |
| 计划到发时间/站点 | `7:01 PM ... Philadelphia` | 计划目的地不是故障地点 |
| 事故/影响位置文字 | `in Hammonton`、`near Spring Lake` | 没有结构化坐标；城镇、站点、区间混合 |
| 延误分钟 | `up to 25 minutes late` | 是通知上限，不是实际到达延误；小时及区间表达需另解析 |
| 取消/恢复/加停/接驳 | `cancelled`、`WILL operate` 等 | 全程取消、途中取消、恢复不能只靠布尔值区分 |
| 官方事件 ID、坐标、事件起止时间 | **Unknown / 样本未提供** | 本地 page_ordinal 只是定位索引，不是事件 ID |
| 受影响列车总数 | **Unknown** | 不能把正文所有列车号都计作受影响列车 |

实际质量计数：269 条均有线路标签；22 条没有原因链接（不等于 22 条原因未知）；63 条含显式 Update 前缀；60 条提及 canceled/cancelled（含替代列车描述，不等于 60 次独立取消）；192 条匹配简单 `up to N min...` 表达。其余记录不能填为 0 分钟。小时表达示例 `up to 2 hour and 15 minutes` 会漏于这个简易字段，原文仍保留。

## 4. Spatial granularity

应为每条记录同时保存 `affected_route` 与独立的 `incident_location_text / role / precision / confidence`，不能以一个“地点”字段混淆它们。此次 CSV 只提取线路，**未声称已完成 269 条地点标注**；七天四档精度的最终数量 **Unknown**。

| 精度 | 实际证据与判断 | 可采用的表达 |
|---|---|---|
| Exact incident location | 269 条没有结构化坐标。正文可指名 Delair Bridge 等设施，需外部验证才能定位；本次没有验证到精确事故点 | 暂不绘精确事故点 |
| Station-level location | 11-09 NJCL #3228：医疗协助 `at Aberdeen-Matawan Station`；NEC #3848：警务 `at Newark Penn Station` | 人工核验后可作“通知提及的事件站点”，非全量热力图 |
| Affected rail line only | 大量机械/人员通知只给计划到发站；11-15 #0715 到 Gladstone 不代表故障在 Gladstone | 线路高亮，说明位置未详 |
| System-wide / unknown location | 历史页有全系统 cross-honoring 和线路标签缺失；影响范围可能多线路 | 单独计数，不能丢弃或强行落点 |

四档还需辅以“不确定地点文本”字段：`near Spring Lake`、`in Hammonton` 并不足以证明就在同名车站；`between Millington and Stirling` 是区间而非点。若不能验证地点，保留文字并以受影响线路级表达。取消站（例如 `cancelled at Millburn`）只说明取消发生范围，不自动证明湿滑原因发生在该站。

逐条人工阅读 11-15 的 11 条：0 条有精确坐标，0 条明确给出可确认的事故车站，4 条含大致事故地名（Spring Lake 2、Hammonton 2），另外 7 条没有事故地点；11 条均可做受影响线路表达。这个小样本不能外推全周比例。

## 5. Delay cause categories

网站有规范化原因实体：`mechanical issues` 链到 `mechanical-problem`；同一通知可以同时链接 `equipment-availability` 和 `mechanical-problem`。但词表保留 `Mechanial Problem`、`Rack Maintenance`、不同 drawbridge 拼写及超具体文字，说明它不是可以直接采用的稳定官方原因编码。**原因文字来自通知正文这一点可见；正文是否逐字来自官方、分类算法是否人工或规则、是否官方分类均 Unknown。** 应称“网站提取的通知原因”，不是“官方调查确认的事故成因”。

七天中原因链接的精确组合例：仅 mechanical-problem 37、仅 congestion 33、仅 slippery-rail-conditions 28、仅 track-maintenance 20、仅 equipment-availability 18、equipment-availability + mechanical-problem 11。它们不是独立事故数，也不是合并大类计数。

为了检验帧数量与空间差异，脚本对全文做了**临时、互斥、有优先级的关键词分类**，不是最终编码。优先级依次为机械/设备→信号/道岔→天气/树木/附着→轨道/设施→拥堵→人员/运营/接续→外部事件/协助→其他。它可能把“拥堵由信号导致”归到信号，把上游原因归到机械；正式阶段应分别标注直接原因、上游原因，人工审查后再决定多标签或主因。不可把此表宣称为已核验最终原因频数。

| 临时大类 | 通知数 | 空间差异例 | 成帧建议 |
|---|---:|---|---|
| Mechanical / equipment | 76 | MNE 18、NEC 18、MBPJ 16，8 个线路组都有 | 可单独成帧 |
| Congestion | 32 | ACRL 11、MNE 9，7 个线路组 | 可单独成帧 |
| Signal / switch | 17 | RVL 9，6 个线路组 | 可单独成帧；样本较小 |
| Weather / vegetation / adhesion | 30 | MNE 21、MBPJ 5、ACRL 3、RVL 1 | 本周主要为湿滑轨；不能统称恶劣天气 |
| Track / infrastructure | 38 | RVL 7、NEC 7、MNE 6、MOBO 6 等 | 桥梁开放与故障/维护应标子类 |
| Staffing / operations / connections | 40 | NJCL 16、MBPJ 6，7 个线路组 | 人员、接续、旅客加停可后续拆分 |
| External incidents / assistance | 31 | MNE 11、MBPJ 9 等 | 真实样本支持新增此类；车辆占轨、警务、医疗协助不应埋入 Unknown |
| Other / unknown | 5 | RVL 2、NEC 2、MBPJ 1 | 不必单帧，可用文字列示 |
| 合计 | **269** | 完整矩阵见 pilot_statistics.json | 所有帧必须同一窗口 |

Other / unknown 的 5 条是两条 speed restriction、一条全站加停信息及两条恢复运行信息；这再次说明关键词残余不等于真实未知原因，需人工重标。本表只证明存在可研究的线路差异，不能证明因果空间聚集或统计显著性。

## 6. Data quality and limitations

1. **更新不能累加为事故或分钟。** 11-15 ACRL #4682 在 18:25 为 20 分钟、18:47 为 25 分钟，是同一列车同日相同 EMS 原因的连续通知，不能相加为 45 分钟。11-11 #1357 有 7 条通知。全周有 21 个重复 train-day 组，但“日期+列车号”也不是可靠事故 ID。
2. **相同文字不一定重复事件。** 全周存在 3 组完全相同规范化正文，各 2 条；应再核查时间和日期，不能仅按文本跨日去重。历史 2014-02-12 同一时刻同一系统通知以不同线路标签多次出现，是跨线路复制的直接证据。
3. **历史线路标签错误。** 2014-02-12 正文 Pascack Valley 被标 Newark Light Rail；[列车 #1822](https://njtranshit.com/train/1822)正文 MBPJ 却标 HBLR；[列车 #0725](https://njtranshit.com/train/0725)有 MNE 正文标 ACRL。正式分析需保存网站标签、正文推断线路与冲突标志；不能盲信 route ID，尤其不能把这些错标当作轻轨延误。
4. **恢复与信息通知混入。** `will operate`、加停、cross-honoring、on or close to schedule 不是新延误事件；取消关键词可能来自替代列车背景。本次以 notice 为单位，正式样本应另做 status/type。
5. **没有分母。** 线路通告数受班次数、发通知习惯、多次更新影响，不能宣称为晚点概率、可靠性排名或旅客损失。没有已验证的实际到达延误、事故持续时长、旅客数或 train-minutes。
6. **抽取范围。** 七天 HTML 每个 `logs__item` 均计一行；未发现分页，本次逐日数量与首页图表匹配，但不保证官方通知覆盖完整。缺页不能直接填零；正式下载需记录状态、图表校验及缺失标志。
7. **临时脚本局限。** 正则针对当前静态 HTML；所有列车号先以字符串保存；没有通用 NLP 地点/因果抽取。分类、取消和分钟字段均是研究诊断字段。

## 7. Licensing and publication considerations

**NJ Transhit 的数据许可证、转载条款和明确衍生地图许可：Unknown。** 首页/原因/日期页面/脚本/sitemap 未发现相关说明；没有发现不等于不存在。robots 空 Disallow、公开 URL、分享按钮都不是开放许可证。现有样本是有限本地研究留档，未公开发布、未打包为公共数据产品；不应默认将原始 HTML/通知全文公开上传。

公开制图前应向网站维护者确认：是否允许非商业衍生统计 GIF、署名方式、历史批量访问节奏、是否允许保存或发布通知摘录。应保留 NJ Transit 原始通知与第三方抽取两级来源，避免暗示官方背书。**本次未代用户发送联系消息。**

[NJT Developer Terms](https://developer.njtransit.com/terms/)适用于官方 Data Feeds，不能自动视为对 NJ Transhit 的授权。其允许开发者按条件下载托管，同时有不得修改/删除原始数据、避免误导、非实时声明等要求；对衍生分类汇总的适用性需进一步确认。没有据此断言 GIS 或第三方数据具有同一许可。

## 8. Recommended mapping approach

推荐未来地图主题为 **“Where disruption notices affected service, by reported cause”**，图例明确“受影响线路，不代表故障位置”。先以所有帧一致的七天窗口做审核；如需扩大到 30 天，应所有原因一起扩大。固定投影、范围、线路宽度/颜色比例尺，每帧同时显示 N，避免各帧自动拉伸色阶造成误读。

主表达使用线路级颜色/高亮，必要时配原因×线路矩阵辅助核验。MBPJ 应对应 Main + Bergen + Port Jervis/Southern Tier 等已验证组合，MNE 对应 Morristown + Gladstone；不能把一个组合标签的所有通知重复计为每一支线独立事件。共享轨道、Penn Station 接近区和线路重叠须用偏移或示意网络处理。没有证据时不得把通知均匀撒点、按车站分摊或随机分配轨道段。

站点符号只适用于逐条人工核验的事件地点子集，并标明覆盖率和近似性，不应与线路级计数混成一套强度图。暂不以分钟加总作主指标；优先使用明确标注的通知数，或在完成状态解析与去重后使用“受影响 train-day 数”，并说明它仍非事故数。

### 铁路 GIS 可得性

- [新泽西州 GIS 数据目录](https://www.nj.gov/housingcouncil/resources/data-dictionaries.shtml)明确链接 [NJTRANSIT_RAIL_LINES_1 FeatureServer/0](https://services6.arcgis.com/M0t0HPE53pFK525U/arcgis/rest/services/NJTRANSIT_RAIL_LINES_1/FeatureServer/0)：Polyline、`LINE_NAME`、公开 Query，支持 JSON/GeoJSON/PBF，最大单次 2000 条。列名包括 Atlantic City、Main、Bergen、Morristown、Gladstone、Southern Tier 等，可构建线路底图。其空 Copyright Text 不等于开放许可；元数据及纽约/宾州端点覆盖需正式阶段核验。
- [New Jersey Railroad Network](https://services.arcgis.com/HggmsDF7UJsNN1FK/arcgis/rest/services/NJRailRoadNetworkOpenData/FeatureServer)也提供公开 GIS。已保存其 [ArcGIS item 元数据](https://www.arcgis.com/home/item.html?id=9b7498a04a6146ff859c07ac242ccbd1)：owner `NJDOTGIS`，署名 NJ Department of Transportation，licenseInfo 是准确性/法律文件免责说明。该数据混有轻轨、PATH、PATCO 等，需筛选；免责文字不应被改写成无限制开放授权。本次只查元数据，没有下载几何或切换数据源。
- 官方 [GTFS-RAIL 文档](https://developer.njtransit.com/registration/appdoc?app=GTFS-RAIL)提供铁路时刻表下载流程，当前文档要求账户 token。未来经正常注册可检查 stops/routes/trips/shapes 是否齐全；本次未注册、未调用受凭证保护接口，shapes 内容与完整性 **Unknown**。GIS 底图已存在公开服务，不必先依赖 GTFS。

### 替代数据源（仅提出，没有自动采用）

1. [NJT 官方开发者门户](https://developer.njtransit.com/)的 RailData / GTFS：来源链更清楚，需正常注册并审阅条款；历史通知归档、原因字段和事件级位置 **Unknown**。实时 GTFS 数据并不自动提供历史原因。
2. 请求 NJ Transhit 维护者提供带通知 ID、发布时间、线路和原因映射的许可导出：最贴近本项目，仍待明确许可与可得性。
3. 若官方/维护者不能提供历史导出，可在获准后前瞻采集官方通知，建立自己的固定窗口；这需要等待积累，不是现成历史数据替代。

## 9. Go / No-go recommendation

- **Go：** 数据探索与线路级“通知影响分布”的方法可行。七天 269 条覆盖 8 个铁路线路组，多个原因有不同空间构成，GIF 技术上成立。
- **Conditional Go：** 原因序列建议保留机械/设备、拥堵、信号/道岔、湿滑/天气相关、轨道/设施、人员/运营，并新增外部事件/协助；最终帧数须以人工原因审核和去重结果决定。不要沿用未核验的关键词分类当最终统计。
- **No-go（当前）：** 精确事故点/车站热力图、把所有目的地当事故站、实际损失分钟或唯一事故数、以及未经许可确认的公开发布。
- 下一阶段前置条件：确认数据衍生使用许可；人工核验统一窗口的线路与直接/上游原因；定义更新合并与恢复通知处理；完成 GIS 许可及线路组合映射核对。由 Ming 和 Guoguo 决定视觉设计后再执行，不在此调查中制作成品。

### 本地证据与复现

[样本目录](data/sample/)包含七天原始 HTML（`.txt`）、首页/原因页面/脚本/robots/sitemap、历史页、GIS item JSON；[CSV](data/sample/alerts_2026-11-09_2026-11-15.csv)有 269 行；[统计 JSON](data/sample/pilot_statistics.json)有逐日、逐线、原因与交叉统计。执行 `powershell -File 16/data/sample/analyze.ps1` 可离线重算；不会发起网络请求。HTML 保存的是服务器完整公开响应，版权/引用来源仍归各站；未经许可不建议公开分发这些原始样本。采集清单、UTC 留档时间与 SHA256 见 `data/sample/manifest.csv`。
