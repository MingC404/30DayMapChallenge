# Where the Darkness Ends
*Navigation Lights of New York Harbor — Day 17: Light & Dark*

调查日期：2026-11-17（America/New_York）。本轮仅下载、核查和整理数据，未制作最终地图或 GIF。

## 结论与统计

**可以制作有来源依据的单灯节奏动画，但不能据此复原纽约港某一时刻的整体灯光实况或真实可见范围。** NOAA 原始 ENC 的 LIGHTS 含有 USCG GeoJSON 缺少的 `SIGSEQ`，因此无需从 `Fl(3) 6s` 猜测单次闪光时长。

统计单位是一条 USCG Light List 灯光登记条目（`LLEN_UID`），不是每个灯泡、每段颜色扇区或每个 ENC 要素。清单 153 行、153 个独立 LLEN_UID。一个登记条目可能包含多灯或附属 passing light；本次不把附属灯、备用灯及颜色扇区重复计数。因此 153 是本调查口径的登记对象数，不能解释为港内所有物理发光器的精确总数。

| 核查项 | USCG 单独 | 合并核查后 / 153 |
|---|---:|---:|
| 有灯光的登记对象 | 152 有 LIGHT_CHAR；另 1 条 LB 缺灯质 | 153 |
| 经纬度、名称、编号 | 153 | 153（100%） |
| 明确灯光颜色 | 151 | 153（100%） |
| 明确周期（秒） | 114 | 144（94.1%） |
| 原始精确亮灭序列 | 0 | 141（92.2%） |
| 明确绝对扇区起止角 | 2（在 REMARK 中） | 5（3.3%） |
| 主灯标称射程 | 108 | USCG 108；ENC 各组件值保留在 JSON 列，不强行合并 |
| 闪光分组编码 | LIGHT_CHAR 的括号部分 | 144 有组码，包含单闪 (1) 和 Morse 字母组 |
| LIGHTS.ORIENT 非空 | 无独立字段 | 0 |
| 可可靠复现单灯周期及明暗节奏 | 单独不能普遍实现 | **142（92.8%）** |

142 = 141 个有通过校验的原始 SIGSEQ + 1 个 `Iso Y 6s`（依据 Iso 定义，明暗各 3 秒；这不是原始序列字段）。其中 2 个 Claremont 导标仅在船舶靠泊时点亮，11 个还有季节或冰况条件；129 个未记录这类额外条件。上述数量均表示**公布节奏可复现**，不保证当前正在点亮。8 个 F 恒明灯另作静态点，不计入周期动画数量。其余 3 个是 Romer Shoal、OPT research buoy 和 St. George strobe，缺少可验证的完整时序。

分类：灯塔 7、灯标 32、灯浮标 114、其他 0。`STRUCTURE_TYPE=LT HOUSE` 优先归灯塔（含灯塔结构上的导标）；`DESCRIPTION_TYPE=LB` 归灯浮标；其余 `AID_SUBTYPE=FX` 归固定灯标。保留原始分类证据，不能把 LTMA 一概翻译为灯塔。St. George strobe 为固定灯标中的特殊灯质。

## 范围与筛选

采用 WGS84 包围框 **西 -74.20、南 40.40、东 -73.85、北 40.72**，再按官方 `HWATERWAY_NAME` 白名单筛选，覆盖 Upper Bay、The Narrows、Lower Bay、Sandy Hook Bay 及相关航道，并保留为这些航道服务的岸上导标。

白名单见 [study_waterways.json](raw/study_waterways.json)：Ambrose Channel、Main Channel、Swash Channel、Sandy Hook Channel、Chapel Hill South/North Channel、Gravesend Bay、Coney Island Channel、Coney Island Creek Entrance、Bay Ridge Channel、Buttermilk Channel、Erie Basin、Claremont Terminal Channel、Port Jersey Channel、New Jersey Pierhead Channel、New Jersey Pierhead、Constable Hook Channel、National Dock Channel、Sandy Hook Bay、Terminal Channel、Old Orchard Shoal。

此操作范围刻意不延伸到 Newark Bay、Kill Van Kull 上游、Arthur Kill、Raritan Bay 西部、Jamaica Bay、Shrewsbury/Navesink Rivers 或 East River。包围框内的这些相邻水域不自动算入。它不是法定水域边界；日后更改范围必须重新统计。当前包围框共 460 条 USCG 候选，水道筛选后 243 条，其中排除 90 条无灯航标、纯 AIS/RACON 等条目，留下 153 条。所有纳入条目 `INACTIVE=0`，但不能据此确认实时无故障。

这是对官方登记数据的清单调查，不是对桥梁灯、城市照明、所有私人设施或 ENC 中每一个无名 LIGHTS 组件的实地普查。框内 Harbor ENC 共 289 个 LIGHTS/LNAM，其中 130 个距本清单所有对象超过 25 米，包含范围外相邻水域及未匹配要素；未强行并入主清单，也未声称它们都无关。其属性和最近登记对象保留在 [ENC 空间审计](raw/enc_harbor_spatial_audit.csv)。

## 官方来源与版本

### USCG MSI GeoJSON

入口：[Maritime Safety Information](https://navcen.uscg.gov/msi)。下载 District 01 的全部 10 个分片，合计 **9,227 条**，以避免误把 `_1` 当成完整东北区。实际纽约港灯光条目分布在 `_1`（61）、`_2`（42）、`_7`（2）、`_8`（19）、`_9`（28）、`_10`（1）。这类编号是分片，不是水域名称。

具体 URL：`https://navcen.uscg.gov/sites/default/files/msi/lightListD01_{1..10}.geojson`。原文件均保留于 `raw/`；文件哈希、下载时间、条数和完整字段列在 [source_manifest.json](source_manifest.json) 与 [uscg_schema_audit.json](raw/uscg_schema_audit.json)。数据没有单独的发布版号；逐条保留 `MODIFIED_DATE`，不可把下载日期或该字段当作全量数据截至日期。

**调查时 MSI 页面明确提示显示数据可能过时、不完整或不可用，且无恢复时间。** 本报告保留该限制，不能认定下载成功即表示没有遗漏。[页面快照](raw/msi.html)。

关键字段：geometry.coordinates、DECIMAL_LONGITUDE/LATITUDE、NAME、LIGHT_LIST_NUMBER、LLEN_UID、AID_UID、LSYS_UID、AID_TYPE/SUBTYPE、DESCRIPTION_TYPE、STRUCTURE_TYPE、LIGHT_CHAR、LIGHT_NOM_RANGE/UNIT、LIGHT_FOCAL_PLANE/UNIT、REMARK、SEASON_FROM/TO、INACTIVE、HWATERWAY_NAME。**COLOR 是航标外观颜色，不能直接当成灯光颜色**；灯色从 LIGHT_CHAR 读取。GeoJSON 没有独立 SIGSEQ、SIGPER、SECTR1/2、ORIENT 字段；扇区与附加灯常藏在 REMARK。

### USCG Volume I 与前言

用户指定的 [年度出版入口](https://www.navcen.uscg.gov/light-list-annual-publication) 本次直接访问返回 403，备用官方 CMS 页面也返回 403。因此不能确认该入口目前提供哪一年版，尤其不能声称拿到了 2026 年版。

找到并下载了官方 [Volume I 2025 PDF](https://navcen.uscg.gov/sites/default/files/pdf/lightLists/LightList_V1_2025.pdf)，作为历史出版物参考，不覆盖当前 MSI/ENC 的值，也不作为 2026 实况依据。另下载 [Light List Preface](https://navcen.uscg.gov/sites/default/files/pdf/msi/Light_List_Preface.pdf)，修订日期 2025-09-17，用于字段、灯质、扇区备注和射程定义。前言说明 Volume I 涵盖 Maine 至 Shrewsbury River, NJ；包括联邦与私人助航设施。年度入口的访问限制与已取得 PDF 的实际年份须分开记录。

### NOAA 原始 ENC

入口：[ENC 下载](https://charts.noaa.gov/ENCs/ENCs.shtml)。取得官方 `ENCProdCat_19115.xml`，目录时间戳 **2026-11-17T05:55:51Z**。从目录中按覆盖多边形包围框选择与调查框相交的 band 4/5/6 单元，实际取得 **32 个 band 4/5 单元 ZIP**。全部单元、目录 edition、日期、URL 见 manifest 和 `raw/enc_selected_catalog.json`。

使用本机 GDAL/OGR S-57 驱动读取 LIGHTS，默认应用随 ZIP 提供的更新文件。核对 DSID 的 EDTN/UPDN/UADT/ISDT，并保存 `raw/enc_current_versions.json`。例如 US5NYCDF 为目录版 16.5，包含 `.000` 与 `.001`–`.005`，目录 publication 为 2026-11-13；US5NYCBF 为 4.0、2026-11-10。**SORDAT 是单个要素来源日期，不是 ENC 单元发行日期；老 SORDAT 不足以证明当前单元过时。**

原始框内得到 530 条跨比例尺 LIGHTS；band 4/5 对同一助航灯重复描绘，不能相加计数。优先 band 5、没有符合条件的 band 5 才用 band 4，按 LNAM 去重。LIGHTS 的颜色扇区可以各占一个要素，也不能当作多座设施。

另试查官方 [ENC Direct to GIS](https://nauticalcharts.noaa.gov/learn/encdirect/)，保留 Harbor 服务下载样本（287 条）及服务响应。部分 schema、Approach、Berthing 请求返回服务错误；其数据仅用于比较入口与字段，最终补充统计来自**当前原始 ENC**，不依赖这些服务的可用性。

## 跨源核对及完整度限制

主清单使用 USCG 位置与身份。对每个对象查找 25 米内的 ENC LIGHTS，核对灯质类型、已知颜色、已知周期与显式分组；优先 Harbor band 5，再按 LNAM 去重。同一距离内存在另一条相同灯质的 USCG 登记时，标记 ambiguous，不自动移植时序。**这个匹配是有证据的空间关联，不是官方身份连接表。** 每个候选的距离、LNAM、单元、属性和来源日期均保留在 CSV JSON 列。

147 条位置和主灯质一致；2 条同址近邻歧义（34795、35035）；3 条 25 米内无候选（35192、35615、37209.1）；1 条是 USCG 灯质缺失的 37032。后者 `DESCRIPTION_TYPE=LB`，名称明确为 Lighted Buoy，距唯一 ENC 灯仅 0.23 米，ENC 给出 Fl R 4s、红灯与完整序列，作为补证纳入。St. George strobe 的 USCG 没有灯色，ENC 同位置给白色；它依然没有可用完整时序。缺失的字段不按邻近航标规则推定。

精确序列校验：只接受原始 SIGSEQ 可解析为亮/暗时段、各段之和与 SIGPER 相差不超过 0.02 秒，且匹配的组件无互相冲突的序列。无 SIGSEQ 的 `Fl (2)W 15s`（Romer Shoal）不会被人为补成两次等长闪光。其 REMARK 中的 `2s bl` 是**雾号**，不是灯光时长。

有 SIGSEQ 的例子：Ambrose Buoy 5 为 `00.3+(02.2)`、总周期 2.5 秒；Robbins Reef 为 `00.6+(05.4)`、总周期 6 秒。Q 也必须使用该对象实际 ENC 的 SIGPER/SIGSEQ，不能一律假设 60 次/分钟。

有绝对角度的 5 个登记对象：34790 West Bank Front、35135 Sandy Hook Channel Front、35140 Sandy Hook Channel Rear (East)、36975/36980 Buttermilk Front/Rear。保留各颜色组件全部角度；例如 Sandy Hook Front 红 63–73°、绿 300.5–315.5°，白色另分跨北与另一段。没有角度的其余对象标为 `not_documented`，不赋 0–360°，也不假造扇区。Staten Island Rear 的“仅在导标线上可见”没有数值宽度，不能画成精确扇区。Sandy Hook Rear 主段即使名称含 Range，也不自动赋予东段的扇区。

CSV 的 `light_colors` 是主灯质颜色；不同颜色的扇区完整颜色保存在 `sector_enc_json`，不可只按主灯质颜色绘制整个扇区系统。ORIENT 全为空不表示没有方向性；SECTR1/2 与 REMARK 已能说明部分方向信息。多灯附注如两个 Sandy Hook Rear 条目中的黄色 passing light 原文保留，未假装它们与主灯具有相同周期或射程。

## 可见范围与视觉表达

标称射程是标准气象能见度 10 海里下的光度距离指标，不是本地任意时刻都可见的圆形半径。实际可见性还取决于天气、灯高、观察者眼高、地球曲率、遮挡、灯的方向与运行状态。这里没有齐全的实时天气、观察者位置或遮挡模型，无法计算真实光照/可见覆盖。

扇区角度是真实公布的方向边界，但扇形外缘仍不能用标称射程冒充真实可见边界。艺术性光晕可用固定屏幕尺寸或视觉规则制作，必须明确标为示意，不以海里标尺暗示真实覆盖。不用陆地裁切光晕来声称已完成视域模拟。

## 再利用条件

NOAA [Coast Survey Data Licensing](https://nauticalcharts.noaa.gov/data/data-licensing.html) 将 OCS 获取的数据以 CC0-1.0 贡献给公共领域。ENC 还附带独立 [User Agreement](https://charts.noaa.gov/ENCs/ENC_Agreement.shtml)：允许下载、使用和再分发；再分发副本通常不算官方 ENC，不能冒充满足航海携图要求的认证产品；再次分发原 ENC 时应保留协议和官方来源，并注意衍生产品条款。商标和徽章不随数据许可转让。ZIP 内的 USERAGREEMENT.TXT 保留。本地分析快照没有发布到公共服务器。

USCG 本次 GeoJSON 没发现单独开放数据许可证，**不标 CC0 或 CC-BY**。[USCG 官方 FAQ](https://www.uscg.mil/Community/faq/) 允许复制、分发公共信息，同时对商业使用与暗示 USCG 背书有约束。[17 USC §105](https://uscode.house.gov/us/usc/t17/s105/) 对美国政府职务作品的版权原则不等于这个文件所有潜在第三方内容都自动取得全球开放许可。本次可据已查政策进行非商业研究并标注来源；后续若整体公开打包原始数据或商业化，仍需核实具体适用条款。结论是“有公开信息复用依据，但没有查到 GeoJSON 专属开放许可证”，不是“公开下载即无限制授权”。本轮没有进行对外再发布。

推荐署名：USCG NAVCEN, Light List District 01, downloaded 2026-11-17；NOAA Office of Coast Survey, NOAA Electronic Navigational Charts (ENC), accessed 2026-11-17, https://doi.org/10.25923/jyyk-j845。作品标注“非航海用途；根据公布特征制作的时序示意；灯间相位未知”。

## 推荐范围与动画形式

主图推荐完整保留上述调查框，以 Sandy Hook–Ambrose–The Narrows–Upper Bay 为阅读主轴；外围相邻水域适度留白，不把 Raritan/Newark/Jamaica 航道混入主题。这样同时有海上入口、密集灯浮标与 Upper Bay 的港口背景，题目更完整。可另用纯信息面板解释 5 个有资料的扇区，不需要将全港画成光束森林。

推荐未来使用**按真实秒数连续运行的交互动画或视频**：141 个对象照 SIGSEQ 明暗变化，Claremont Rear 的 Iso 依据定义，恒明灯保持亮；缺少时序的 3 个使用静态标记和灯质标签。靠泊灯、季节/冰况灯需明确条件；11 月默认不要把 7–10 月研究灯画成正在运行。灯间统一从零开始仅是展示相位，必须标明人为设定。用小光点和克制光晕呈现节奏，公布扇区作为辅助信息；不模拟扫海旋转光束。

不优先推荐短 GIF：已知周期包括 2.5、4、5、6、8、15 秒，其共同整周期为 120 秒，短 GIF 容易在接缝处破坏真实周期（应以 CSV 最终周期集合再次核验）。视频或交互动画更适合精确时序；若以后必须 GIF，采用选定对象的短周期子集并明确筛选标准。本轮未制作任何图像或动画。

## 复核入口

`scripts/data/download*.cjs` 保留下载逻辑；`scripts/data/select_enc.py` 选择目录单元；`scripts/data/extract_enc.py` 读取 S-57；`scripts/data/build_inventory.cjs` 生成清单和统计；`scripts/data/audit.cjs` 保存空间审计与字段审计。脚本从仓库根目录运行，Python 使用带 GDAL 的环境。所有处理仅写入 `17/`。`source_manifest.json` 记录输入哈希，可用本轮快照复算。
