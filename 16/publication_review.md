# Day 16 — Publication Review

**Why Are the Trains Late?**<br>
*An Atlas of NJ Transit Disruptions*<br>
Question by Chiun Heng Chou · Mapping by Ming Cao

审查日期：2026-11-16。预期目的地：个人 GitHub Pages 与 30DayMapChallenge 学院仓库。

**审查后的所有者发布决定：** 在已告知 OSM 替换未完成、两个成品仍使用 NJT GIS 且许可问题未明确后，用户明确要求“仍然发布”。本次按该最新指示，仅将现有版本发布到个人 `MingC404/30DayMapChallenge` 合集；不操作学院仓库。此决定覆盖此前暂缓发布的工作流程，但不改变下文的事实与许可评估，也不表示第三方已经授权。成品保持原校验值，来源继续准确标为 NJ TRANSIT GIS Department，未伪称 OSM。

**后续来源替换状态：** 已完成一轮本地 OSM 几何覆盖比较，但因 NJCL／RVL 服务范围差异未解决，按用户停止条件未切换成品。当前 PNG/GIF 和本报告所列校验值不变；不能将旧成品标为 OpenStreetMap 来源。下述 HOLD 是当时的审查建议；个人发布的最新工作流程决定见上一段。

**发布建议：HOLD，当前不建议直接发布这两个成品。** 绘制方式、聚合口径、空间措辞和文件技术检查通过；README 与本地数据隔离已补齐。但铁路／枢纽 GIS 的公开衍生地图使用权仍未明确，而且已找到 NJ Transit 通用材料条款中的网络转载和修改限制。NJ Transhit 的具体适用条款同样 Unknown。原创排版、聚合统计、非商业或教育目的，不自动解决这些不同来源的权利问题。

这是一份有证据范围的发布准备审查，**没有判定该作品必然侵权，也没有把“找不到开放许可证”等同于“任何统计都必须先获得许可”**。建议暂停的具体原因，是当前来源条款不足以确认拟议的两种公开发布场景可获授权，而不是单纯因为用了公开数据。

## 一、审查范围与证据

审查对象：

- `outputs/day16_njt_disruptions.gif`：291,022 bytes，1440×1440，9 帧，17.5 秒。
- `outputs/day16_njt_disruptions.png`：203,055 bytes，与 Opening Overview 构图一致。
- 生成脚本、动画 manifest、清理表、更新组清单、GIS 来源元数据、README。
- 本地 `docs/`、`scripts/gallery_entries.json`、Git 索引及 Day 16 忽略规则。
- 本轮重新读取的 NJT 官方版权条款、开发者条款和线路／站点 ArcGIS item 元数据；Census 对应产品的联邦目录许可记录。

GIF SHA256：`9eb94e1b05288c054f3e7eb3f8fec126ca541bd1182f2c487fd5ab32adbccde5`。<br>
PNG SHA256：`faa80ab82fb9c6e375d222ef3556d2d4ae1ab3bfc881cbf46690165c7dd40222`。

技术复核由 `scripts/audit_publication.py` 执行；本地明细在 `outputs/publication_audit/audit_results.json`。该目录包含第三方条款 HTML，因此已加入 Git 忽略，**不是公开发布目录**。审查没有重新抓取通知、清理数据或重绘成品，两个成品的校验值与之前一致。

**范围边界：** 仓库保留的配置与 gallery 文档指向 `main / docs`，但没有通过 GitHub 管理接口核验当前线上 Pages 设置、部署记录或远端完整历史。学院仓库 URL、既有内容与提交政策未提供，属于 **Unknown**。本报告能确认本地待发布树和索引的情况，不能保证此前任何线上位置都从未有过文件副本。

## 二、已通过的检查

| 检查 | 结果与依据 | 限定 |
|---|---|---|
| 原创绘制，无网站图表复制 | **通过。** Matplotlib 从几何和聚合量生成线条、文字与图例；调色板由自有渲染帧生成，没有读取 NJ Transhit 图表截图 | “原创绘制”不等于铁路几何本身由作者原创 |
| 无完整通知正文出现在成品中 | **通过。** 九帧与封面只呈现类别、数量和短说明；没有逐条通知、列车通告列表或原始 ID 列表 | 部分类别用语来自报告原因，属于必要的简短识别 |
| 无 NJ Transit 官方标志 | **通过。** 视觉检查九帧及绘图资源路径，未发现官方 chevron、标识、线路 logo 或网页 UI 截图 | 文本中的 NJ Transit 用于说明研究对象和来源，不表示官方背书 |
| 本地公开目录隔离 | **通过（本地 Day 16 范围）。** 检查 `docs/` 的 41 个文件，没有 Day 16 目录／素材；未发现 Day 16 数据文件的同 SHA256 副本，也没有 269 条完整通知的匹配正文 | 其他日期已有合法来源的 GIS 文件不属于本轮清理对象，未修改 |
| Gallery 不会自动复制 Day 16 | **通过。** 当前注册表没有 Day 16；builder 按明示文件复制，不递归复制整个日目录 | 将来新增 entry 或改变部署目录后须重检；本轮未运行 builder |
| Git 中未跟踪敏感 Day 16 数据 | **通过。** `git ls-files -- 16/data 16/outputs/publication_audit` 为空；修订后的忽略规则覆盖完整目录 | `.gitignore` 不能阻止强制添加、手工 ZIP、其他仓库的复制或已存在远端历史 |
| 同源统计与更新去重 | **通过既定计量规则。** 图面总数与类别数直接来自同一代表表，234 个本地通知 ID 与更新组 ID 均唯一 | 不能据此声称已识别全部真实事件关系 |
| 空间含义 | **通过。** 图面明确是 affected rail services，并排除事故地点和延误概率解释 | 全服务组几何仍不能证明具体支线／轨道段受影响 |
| GIF／PNG／README 一致 | **通过。** November 9–15, 2026；234 代表记录；七类 232 + Other / Unknown 2；PNG 为 GIF Opening Overview 的同源渲染 | PNG 真彩、GIF 量化，不要求两种编码逐像素相等 |
| 动画完整性 | **通过。** 9 帧、17,500 ms、无限循环、首尾解码像素一致；此前验证的地图变换与固定区像素检查通过 | 这些是技术结论，不是发布许可 |
| README 指定署名 | **通过，已补齐。** 见下文 | README 保留 HOLD，不伪称获得许可 |

### 统计复核

```text
269 原始通知 − 11 条排除 = 258 条合格通知
258 − 24 条已确认连续更新的额外计量 = 234 条代表记录
```

20 个多记录更新组已逐组复查：同一日、同一服务组、同一主列车；有合格异常通知的每组只保留一个代表。恢复记录不当作新的异常。取消后恢复的班次仍保留历史已报告异常，故不是“最终实际取消班次数”。

| 直接原因 | 成品与 README 数量 |
|---|---:|
| Mechanical & Equipment | 67 |
| Congestion | 41 |
| Signal & Switch | 11 |
| Slippery Rails & Weather | 24 |
| Track & Infrastructure | 29 |
| Staffing & Operations | 38 |
| External Incidents | 22 |
| Other / Unknown | 2 |
| **合计** | **234** |

每个代表只有一个用于动画的直接原因大类；上游原因不再加入第二个类别，因此不存在把多标签总数错误相加。七个原因帧合计 232，另 2 条仅在两个 Overview 总数和说明中出现。

**去重结论的边界：** 已核对组没有重复累计；不同列车、跨日相同正文，以及原因变化但关系不明的记录并没有被强行认定为同一事件。例如 11-12 #3153 的两种原因仍分别保留。234 只能叫“更新调整后的代表通知记录”，不可改写为“234 起独立事故”。本次审查没有为了获得整齐总数而改动分组。

### 图面与 README 的表达

GIF 和 PNG 保留：

> Linked updates counted once. Highlighted lines indicate affected services, not incident locations or delay probabilities.

原因帧固定 0–20 线宽计数尺度，共享轨道显示较大的服务组计数而不相加；Overview 线路统一线宽，只表示服务范围。点符号是参考枢纽，不是事件点。没有核密度、随机事件点、概率或实际损失分钟的图例。

新建的 [README.md](README.md) 包含用户指定的全部文字：

- `Question by Chiun Heng Chou`
- `Mapping by Ming Cao`
- `Service notice statistics derived from NJ Transhit`
- `Rail geometry` 与 `State boundaries` 的具体来源、维护者、链接与许可状态
- `Independent educational visualization; not affiliated with NJ Transit`

还说明历史窗口、完整计量链、未知原因的处理、组合服务组、非实时性及 provisional 分类。根目录 README 暂未添加 Day 16 发布入口，避免许可尚未确认时造成已发布印象。

## 三、数据来源与尚未确认的许可问题

### 1. NJ Transhit 通知与统计：Unknown，不等于自动禁止事实统计

来源：[NJ Transhit](https://njtranshit.com/)，既有七天公开日期页面。此前检查主页、导航、sitemap 与脚本未找到明确数据再利用许可；本轮公开检索也未确认其许可证或适用于衍生统计的服务条款。**站点自有条款、数据库权利安排、上游通知再利用授权与适用合同关系仍 Unknown。** robots 允许访问、无需登录、可以分享网页，都不是对批量数据或衍生作品的开放许可。

但不能反过来断言所有日期、事实或自行计算的数量都受到源站版权控制。[U.S. Copyright Office 的说明](https://www.copyright.gov/help/faq/faq-protect.html)区分事实与其表达；[数据库说明](https://www.copyright.gov/register/tx-databases.html)还区分底层事实与有原创性的选择、编排。作品没有复制源站图表、原版编排或完整通知，是本项目有利的区别。具体合同、数据库与上游材料问题不能仅凭这一区别全部排除，也不能自动用“教育用途”替代判断。

**尚需确认：** 如果以无须额外许可的原创事实汇总为依据发布，应形成针对本项目具体内容和访问方式的依据记录；或者取得源站对该非商业聚合可视化的适用授权。没有需要公开原始 HTML 或全文 CSV 的理由。本轮未联系任何维护者，也不将“未回复”当作同意。

### 2. 铁路与参考枢纽 GIS：公开可查，公开衍生图授权未清楚

直接来源：

- [Rail Lines of NJ Transit · item e6701817be974795aecc7f7a8cc42f79](https://www.arcgis.com/home/item.html?id=e6701817be974795aecc7f7a8cc42f79)，[实际使用的 Feature Layer](https://services6.arcgis.com/M0t0HPE53pFK525U/arcgis/rest/services/NJTRANSIT_RAIL_LINES_1/FeatureServer/0)。
- [Rail Stations of NJ Transit · item 4809dada94c542e0beff00600ee930f6](https://www.arcgis.com/home/item.html?id=4809dada94c542e0beff00600ee930f6)，用于必要枢纽坐标。

本轮重新读取两个 item，owner 均为 `NJT_GIS`，来源署名为 **NJ TRANSIT GIS Department.** 线路 `licenseInfo` 仅有 “Not for design purposes. Not survey grade data.”；站点为同类精度／用途声明。它们没有明确列出 CC BY、CC0、开放数据许可证或允许公开改绘的授予语句。**该声明不是“禁止所有制图”，但也不是对所有衍生发布方式的授权。** 原始调查／影像来源的权利链并未因此确认。

成品与 README 已保留该 GIS 部门来源，但精确规定的版权标记、许可通知和公开衍生使用条件仍 **Unknown**，不能把现有署名视为已满足所有尚不明确的要求。

#### NJ Transit 通用材料条款：存在明确限制，不能忽略

[Copyright & Disclaimer Statement](https://www.njtransit.com/copyright)将其服务中的材料纳入版权／许可规定；一般要求事先书面许可，并有附条件的内部、信息性、非商业、未经修改使用例外。其中写有 **“solely for internal and informational use”**，并限制在联网计算机张贴。另有非商业下载且不得实质修改的表述。**“非商业”单独并不足以证明面向公众的网站／学院仓库转载和改绘已获准。**

这是已发现的官方条款事实；但 ArcGIS 图层托管于其他域名，本轮没有找到能明确决定“该通用网页条款是否及如何覆盖这两个具体 GIS item、是否有更专门许可优先”的说明。因此不直接判定本作品必然违反该条款，也不能无视它授予发布许可。需要 NJT GIS 的适用许可说明／书面确认，或针对现有规则的具体权利判断。

[Developer Terms](https://developer.njtransit.com/terms/)针对 Data Feeds，允许在符合条件的情况下托管，同时限制误导、官方背书、数据改动及直接从 NJT 服务器向用户供数。本项目没有使用需 token 的 GTFS/API 注册授权。其文字范围较广，但**对当前 ArcGIS item 的适用性和改绘／投影／概化后 PNG/GIF 的许可边界仍 Unknown**，不能把另一条款简单当作默认开放授权。

**真正阻止本次“发布已获清楚授权”结论的主要来源问题，是铁路／枢纽 GIS，而不只是 NJ Transhit 没有一个 License 页面。** 不建议用“州公共机构的数据必然公有领域”替代确认；Census 的联邦数据许可也不能转授 NJT 材料。

### 3. 州界：许可来源已明确，本项通过

来源：**U.S. Census Bureau，2025 Cartographic Boundary Files，States，1:500,000**。[官方产品页](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.2025.html)、[实际 ZIP](https://www2.census.gov/geo/tiger/GENZ2025/shp/cb_2025_us_state_500k.zip)、[对应 Data.gov 联邦目录记录](https://catalog.data.gov/dataset/2025-cartographic-boundary-file-shp-state-and-equivalent-entities-for-united-states-1-5000)。该**同年份、同尺度、同格式**目录将许可标为 [CC0](https://creativecommons.org/publicdomain/zero/1.0/)，不是借用其他州界版本的许可。

图面与 README 已署名 U.S. Census Bureau, 2025；目录的 CC0 不是强制署名型许可证，但保留来源有助于学术可追溯。`provenance.json` 保留产品、ZIP 校验值、投影和裁剪方法。州际共同边界不含 NJ 海岸线冒充的州界，没有状态填色；没有发现本项目用途所需的额外许可缺口。边界仍是概化制图数据，不作法律界址担保。

### 4. 两类发布目标均需单独控制文件范围

公开 GitHub 源仓库与 GitHub Pages 是两个暴露面：即使 Pages 只部署 `docs/`，被提交的 `16/data/` 仍可能从 GitHub 仓库直接下载。学院仓库的附件、ZIP、工作流 artifacts 或其他发布分支也不受本地 Pages 目录约束。

本轮仅核验本地配置与索引；**当前线上 Pages 部署设置／远端历史、学院仓库具体政策：Unknown**。本地忽略规则减少误提交风险，但不证明任何远端已被审计或清除。

## 四、必须修改的内容与本轮已完成的修复

### 本轮已完成，未改变图像和统计

1. **补建 `16/README.md`。** 已加入指定作者、数据源、非隶属声明、窗口、类别数、更新计数规则和 HOLD 状态。
2. **补齐 `16/.gitignore` 的隔离。** 原先只忽略依赖和字体缓存，`git add 16/` 可能误加数据。现新增 `/data/` 和 `/outputs/publication_audit/`，检查确认原始 HTML、两份含全文的清理表、GIS 下载和本轮条款 HTML 均被忽略，且未被跟踪。
3. **增加只读发布审计脚本。** 不清理数据、不重绘、不 stage／commit／push；输出保留本地。

特别注意：`analysis_representatives.csv` 虽只有 234 条代表记录，仍包含 `original_text` 和 `sample_csv_text`，**不是可直接公开的纯聚合表**。`notices_reviewed.csv` 同样含全文。不能因为文件名叫 cleaned / analysis 就把它们列入发布包。

### 公开发布前仍必须完成

1. **解决实际 GIS item 的发布使用依据。** 确认当前两层的公开衍生地图条件与官方材料条款适用范围，并记录所需版权／许可通知。若无法确认，只能在用户决定后换用有明确适用许可的铁路／枢纽来源并重绘重审；本轮没有自动替换数据。
2. **记录 NJ Transhit 聚合发布的依据。** 区分无须复制表达的原创事实汇总与站点可能适用的合同／数据库／上游材料问题；不以“网站公开”或“教育用途”作为唯一依据。
3. **按最终目标做明确白名单包。** 权利问题解决后，最小候选是 `README.md`、本审查说明及两个成品。不得直接上传整个 `16/`、`outputs/`、ZIP 或包含原始输入的源代码复现包。其他脚本／聚合文件如需公开，另列具体文件逐个复核。
4. **在实际发布环境复核。** 检查 Pages source、待提交 diff、远端历史与学院仓库内容／政策，确认无敏感副本。`.gitignore` 不作为 ZIP 或外部上传的过滤工具。
5. **只有条件真正满足后才更新发布状态。** 将 README 的 HOLD、manifest 的 LOCAL ONLY 及图面 LOCAL REVIEW 标记调整为准确状态；保留 provisional 分类与空间含义说明。当前不提前删除这些标记、不添加 gallery entry 或公开链接。

## 五、是否建议发布

| 方面 | 结论 |
|---|---|
| 原创布局／绘制，没有网站图表／正文／官方 logo | 通过，但承认 GIS 输入来自第三方 |
| 数据口径／更新计量／空间措辞／README | 通过，保留不确定性 |
| 本地 `docs/` 与 Git 索引隔离 | 通过；本轮已补齐忽略保护 |
| Census 州界来源与许可 | 通过，匹配产品目录为 CC0 |
| NJT 铁路／枢纽 GIS 公开改绘授权 | **未确认，主要发布阻碍** |
| NJ Transhit 的适用数据使用条款／聚合发布依据 | **未确认，需记录具体依据** |
| 线上 Pages／学院仓库实际 payload 与历史 | **未核验** |
| **综合建议** | **暂不发布个人 Pages 或学院仓库；保留本地成品，先解决上述事项** |

本轮仅修改 Day 16 的 README、忽略规则、审计脚本与审查报告；没有修改 Day 01–15、原始通知、分析结果或成品。没有联系第三方、上传数据、生成公开部署、commit 或 push。
