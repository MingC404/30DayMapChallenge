# Where the Darkness Ends — Lighthouse Beam Research

调查日期：2026-11-17，America/New_York。研究对象来自现有 [light_inventory.csv](light_inventory.csv) 中 `type=lighthouse` 的 7 条记录。本轮只研究，未修改地图、153 条清单、光学属性或现有交互功能，未制作新动画或发布。

## 结论

**7 条登记对应 6 座独立灯塔塔体。当前资料不足以支持 3 座按真实旋转参数运行的灯塔光束动画；严格按现役机制和参数核验，本轮 A 类为 0 座。**

- **Romer Shoal 有明确的历史旋转装置证据**：2006 年 USCG 编写的国家史迹登记材料记载约 1997 年安装 VRB-25。但器材目录存在冲突，当前设备、现场转速、转向和面板配置未确认，不能把历史装置直接当作 2026 年现役配置。[USCG/NPS 原始材料，PDF 页 9–10](https://npgallery.nps.gov/NRHP/GetAsset/990d94d0-8683-4719-a533-d857cba14081)
- **Coney Island 有明确的旧透镜转速证据**：收藏机构介绍其旧透镜按 2 rpm 旋转，即每圈 30 秒；该透镜已在 1989 年被移出。这个数值不能用于今天的 `Fl R 5s`。[Custom House Maritime Museum，旧透镜藏品说明](https://customhousemaritimemuseum.org/u-s-coast-guard/)
- **Sandy Hook 和 Staten Island / Swash Rear 属于恒明灯或定向恒明导标**，不适合改画为旋转扫海光束。West Bank 的已知资料重点是固定方位的红白扇区、导标线和等明暗节奏，也不应替换为自由旋转光束。

建议采用“少数灯塔的不同光学性格”，而不是“多座灯塔一律旋转”。Romer 可作为继续核实旋转装置的首要对象，不能为达到 3–5 座而补造旋转机制。

## 1. 证据口径与 A / B / C

本报告区分四件事：**灯塔建筑仍存在、登记为现役助航灯、当前某时刻正在发光、现役光学装置的机械运动**。前两项的证据不能自动证明后两项。

分类针对拟表现的**当前灯塔版本**，不是它在历史上是否曾经转过：

| 类别 | 本报告采用的判断标准 |
|---|---|
| A | 有可适用于当前装置的直接旋转证据，且资料足以支持有依据的真实旋转动画。未确认的关键参数不能默认补齐。 |
| B | 有现役灯光登记，但当前旋转机制不明确、记录冲突或关键参数缺失；如使用光束运动，必须标为艺术示意，不能声称真实旋转复现。 |
| C | 公布的工作方式是恒明、定向导标或固定方向扇区等，不适合本项目绘制自由旋转光束。C 是表现方式判断，不等于证明装置内部任何部件都不运动。 |

**按独立塔体计：A=0、B=3、C=3。按 7 条登记计：A=0、B=3、C=4。** C 多出的一个条目是同塔的 Swash Channel Rear。Romer 的历史 VRB 及 Coney 的已移出透镜均有旋转证据，单独列为历史资料，不计作当前 A 类。

`Unknown` 表示本轮没有找到足够证据，不表示物理上一定不存在。F 恒明没有“闪光周期”；这里写“不适用”，不填 0 秒。

运行属性继续采用 2026-11-17 已审计 USCG / NOAA 快照，**不是重新观测的实时状态**。7 条均为 `INACTIVE=0`，都有灯质记录；本轮未发现足以据此宣布其退役的证据，但即时故障、检修、临时熄灭及备用灯启用状态均为 **Unknown**。原 MSI 关于数据可能过时或不完整的警告仍适用。

## 2. 七个登记对象核实表

坐标顺序为 **纬度、经度**，WGS84，展示至小数点后 5 位；原清单的更长浮点值未修改。射程仅填写清单中 `LIGHT_NOM_RANGE` 的海里值，空值不从旅游介绍补齐。

| LLNR / 建筑组 | 登记名称 | 纬度、经度 | 独立塔体判断 | 现役登记与运行条件 | 灯色、灯质、完整重复周期 | 标称射程 | 类别 |
|---|---|---|---|---|---|---|---|
| 34790 / T1 | West Bank Front Range Light | 40.53797, −74.04287 | 是；海上沉箱式塔，塔内兼生活空间 | 现役登记；注明 24 小时点亮；无季节边界 | 主字段 W；另有 R/W 方位扇区；`Iso W 6s`，6 秒 | **Unknown**：该字段为空 | C |
| 34795 / T2 | Staten Island Rear Range Light | 40.57609, −74.14125 | 是；独立八角砖塔，亦承载 35035 | 现役登记；仅导标线上可见；注明 24 小时点亮；无季节边界 | W；`F W`；恒明，周期不适用 | **Unknown**：该字段为空 | C |
| 34910 / T3 | Coney Island Light | 40.57661, −74.01176 | 是；独立骨架式塔，不是传统封闭砖石塔楼 | 现役登记；注明 24 小时点亮；无季节边界；2026 年 NYC LPC 文件也确认仍由 USCG 运行 | R；`Fl R 5s`；5 秒 | 16 NM | B |
| 34975 / T4 | Robbins Reef Light | 40.65737, −74.06536 | 是；海上沉箱式塔，住舱与塔一体 | 现役登记；无已录入季节边界；明确每日点亮时段 **Unknown** | G；`Fl G 6s`；6 秒 | 7 NM | B |
| 35035 / T2 | Swash Channel Range Rear Light | 40.57607, −74.14121 | **不是另一座塔**；原始结构备注明确与 Staten Island Light 同塔 | 现役登记；未另列季节边界；不能把另一条目的 24h 备注自动当作本灯独立运行记录 | W；`F W`；恒明，周期不适用 | **Unknown**：该字段为空 | C |
| 35040 / T5 | Sandy Hook Light | 40.46172, −74.00203 | 是；独立历史石塔 | 现役登记；注明 24 小时点亮；NPS 2026 年更新页面亦确认工作状态；无季节边界 | W；`F W`；恒明，周期不适用 | 19 NM | C |
| 35070 / T6 | Romer Shoal Light | 40.51302, −74.01352 | 是；海上沉箱式塔，塔内兼住舱 | 现役登记；无季节边界；主灯熄灭时有低强度应急灯，当前使用哪一套 **Unknown** | W；`Fl (2)W 15s`；15 秒 | 15 NM | B |

表内数据可回查：34790 / 34795 / 34910 / 34975 位于 [District 01 分片 2](raw/lightListD01_2.geojson)；35035 / 35040 / 35070 位于 [分片 1](raw/lightListD01_1.geojson)。全部 7 条的 `SEASON_FROM` / `SEASON_TO` 为空，含义是“未录入”，不是保证任何天气、任何日期都开灯。

**West Bank 的颜色不能只概括为白光。** `LIGHT_CHAR` 主字段是 W，但 REMARK 和 ENC 中同时有明确红白扇区。相反，不能把灯塔外墙颜色或浮标本体颜色当灯色。

### 建筑去重依据

1. 35035 的原始 `STRUCTURE_REMARK` 为 “On same structure as Staten Island Light.”，这是直接同塔证据。
2. 两条坐标相距约 **4.0 米**，可与同塔不同灯位或登记定位差异相容；不是仅靠距离阈值强行合并。
3. 两条拥有不同的登记、设施及灯系统标识，应继续保留在原始清单中。去重只用于“选几座塔做主角”，不删除条目、不平均坐标。
4. USCG 对 Staten Island 的建筑和原始二阶 range lens 有独立记录；National Lighthouse Museum 2021 年刊物又明确描述同塔的一道主导标光与第二道 Swash Channel 光。后者是双功能，不是双塔。[USCG，Staten Island Range Lighthouse](https://www.history.uscg.mil/Browse-by-Topic/Assets/Land/All/Article/1991117/staten-island-range-lighthouse/)、[National Lighthouse Museum，Spring 2021，PDF 页 8](https://lighthousemuseum.org/wp-content/uploads/2021/06/nlm_newsletter_spring2021.pdf)

这里的“独立灯塔建筑”指独立物理塔体，包含骨架塔与沉箱式塔，不等同于国家史迹登记中 building / structure 的法律分类，也不要求守塔人住宅与塔分离。

## 3. 各塔的光学机制、方向与历史

### T1. West Bank — 34790 — C

**当前可确认**：等明暗主灯，ENC 序列为亮 3 秒、暗 3 秒。原 REMARK 给白色 181°→004°、红色 004°→181°，并给出以 297° 导标线为轴、两侧各 4° 的高强度白光。原始 ENC 也分别记录 181°→4°、4°→181° 与 293°→301°。这些是颜色区间和导标方向，不是旋转起止角。

**当前光学设备**：管理网站检索资料称太阳能 300 mm 现代光学装置，历史四阶 Fresnel 于 1998 年移出；专家目录也记录该透镜的移出。但未取得最新现场设备单、具体灯器型号、电子闪光器或遮光器说明，故这些硬件细节及是否有内部运动均标 **Unknown**。不能仅凭“300 mm”就断言某款电子灯器已经安装。[管理机构历史页：仅检索正文可见，直接打开失败](https://romershoal.org/history/west-bank)、[Russ Rowlett，West Bank 条目](https://www.ibiblio.org/lighthouse/nydn.htm)

**旋转周期 / 顺逆时针**：均为 **Unknown**，6 秒只是等明暗周期。虽然不能证明内部所有部件静止，但现有数据支持的是固定方位扇区与导标功能，**不支持一条光束不断绕塔扫转**，故列 C。没有找到可另行绘制的数值遮光边界，不补造遮光楔形。

**照片、档案与限制**：专家目录链接了 2025 年塔体照片；NPS 有 NRIS 06001230 元数据，但其下载链接本次实际返回“尚未数字化”的占位 PDF，不能声称已读到完整提名材料。[NPS 元数据及下载入口](https://npgallery.nps.gov/AssetDetail/NRIS/06001230)

不要把旧网页中的 16 / 12 海里直接写回现有清单：本次 USCG 的对应射程字段为空；本轮保持 Unknown。标称射程也不是实际可见覆盖半径。

### T2. Staten Island / Swash Rear — 34795 + 35035 — C

**当前可确认**：同塔两项定向恒明白光功能。34795 与 West Bank 构成导标关系，USCG 备注仅允许确认“导标线上可见”；没有数值扇区宽度。35035 是 Swash Channel 的后导标，也没有独立数值扇区。不得将二者画成两个旋转灯塔，也不能给“仅线上可见”随意加几度宽度。

**光学机制证据**：USCG 历史说明列原始二阶 range lens；National Lighthouse Museum 的 Spring 2021 刊物描述 Fresnel 主光及另一道较小的 Swash 光，并有夜景照片。2019 年 USCG 维护人员陪同的现场报道明确将 Staten Island 主光描述为固定光，展示透镜和反射器。它是机构现场采访的辅助证据，不替代最新灯器维修记录。[USCG 条目](https://www.history.uscg.mil/Browse-by-Topic/Assets/Land/All/Article/1991117/staten-island-range-lighthouse/)、[博物馆刊物，页 8](https://lighthousemuseum.org/wp-content/uploads/2021/06/nlm_newsletter_spring2021.pdf)、[2019 年现场报道](https://statenislander.org/2019/10/25/century-old-staten-island-range-lighthouse-a-tour-with-the-u-s-coast-guard/)

**当前灯源型号 / 功率、是否改装 LED**：2026 年现场配置为 **Unknown**。公开旧记录中透镜仍在使用，不等于每次电灯更换都有资料。不要把“电灯光源升级”说成“透镜旋转”。

**旋转周期 / 顺逆时针**：对已公布的恒明定向表现不适用；未取得另一个旋转装置的证据。两个光轴可由导标关系研究，但不能由灯塔坐标推导真实束宽、遮挡或扫描运动。类别 C；适合固定导标轴线的解释，不适合旋转扫海。

**来源冲突提醒**：上述 2019 年报道还笼统把 West Bank 也说成不闪。它与现有 West Bank `Iso W 6s` 不一致，不能将该句套用到 West Bank；本报告以本地官方灯质数据为准。

### T3. Coney Island — 34910 — B；历史旋转资料价值高

**当前运行与设备**：NYC Landmarks Preservation Commission 的 2026-10-20 文件确认它仍由 USCG 拥有、运行且已自动化，并描述独立骨架塔及住宅，附 2025 年塔体照片。它没有给出当前旋转机构。[NYC LPC 文件](https://www.nyc.gov/assets/lpc/downloads/pdf/proposed_landmarks/Coney_Island_Lighthouse_Calendaring_20261020.pdf)

USCG 2019 年资料明确旧 Fresnel 在 1989 年自动化时移出；USLHS 档案与专家目录将后续光学装置写作 190 mm。但这不足以确认今天的具体型号、电子闪光模块、镜头是否转动或旋转速度。因此当前旋转机制、完整旋转周期、顺逆时针、束数、束宽均 **Unknown**；只能确认红色 `Fl R 5s`，现有 ENC 亮灭时序为亮 0.5 秒、暗 4.5 秒。[USCG 历史说明](https://www.history.uscg.mil/Browse-by-Topic/Assets/Land/Lighthouses-Light-Stations/Article/1912771/coney-island-lighthouse/)、[USLHS 档案](https://archives.uslhs.org/places/coney-island)

**直接历史机械证据**：Custom House Maritime Museum 的旧透镜 #BB-113 藏品介绍记载 1897 年制造、约 1898 年投入使用、设计转速 **2 rpm**，因此完整机械转一圈是 **30 秒**。这是从明确 rpm 换算，不是从“五秒一闪”推出来的。该透镜 1989 年移出，馆方说明其 2025 年获 USCG 长期借展并修复。[博物馆设备介绍及照片](https://customhousemaritimemuseum.org/u-s-coast-guard/)

**时间分层结论**：旧透镜可以成为有转速依据的历史说明案例；它不能证明当前仍以 2 rpm 运行。旧透镜旋转方向也 **Unknown**。没有当前 SECTR1/2 或数值遮光区，不能创作“真实方向扇区”。当前列 B；若用扫转光束必须标为艺术示意，或明确另做“1989 年以前旧装置”的历史叙事，不能混成年份不明的现役实况。

### T4. Robbins Reef — 34975 — B

**运行证据**：维护塔体的 Noble Maritime Collection 说明 USCG 维护太阳能灯，NOAA 维护气象设备。官方光学数据为绿灯每 6 秒重复，ENC 给亮 0.6 秒、暗 5.4 秒。[Noble Maritime Collection，管理机构 FAQ](https://noblemaritime.org/robbins-reef)

**最近可明确追溯的设备更换**：2006 年 NPS 提名档案写明四阶 Fresnel 于 1986-04-30 被移出，替换为 300 mm 光学装置。档案有灯室装置描述及历史、当时塔体照片，但未提供可用于当前旋转复现的 rpm、传动或转向证据。[NPS 原始提名材料，PDF 页 10、17、23](https://npgallery.nps.gov/GetAsset/fe9abab9-95b3-493d-9f2c-8c25dad4043d)

**当前旋转、电子闪光、灯源类型**：均 **Unknown**；300 mm 只是口径/装置描述，不能直接当作某具体型号。太阳能供电和“六秒一闪”都不证明镜头旋转。历史 Fresnel 是否转动、当时转速也 **Unknown**，不因它是 Fresnel 就填“旋转”。无已核验的数值方向扇区或遮光区。

类别 B。可保持有依据的绿色明暗节奏；如果强调光束，可用明确标为艺术效果的非扫描辉光，不应声称真实旋转。Noble 的展览及修复记录提供塔体、历史生活和照片线索，适合辨认塔形，不能用静态夜景照片推算转速。

### T5. Sandy Hook — 35040 — C

**当前机制证据最清楚之一**：NPS 页面更新于 2026-08-25，直接说明当前是自动化三阶 Fresnel、固定白光，由 USCG 维护并全天点亮；另一 NPS 页面于 2026-06-23 更新，说明 1857 年透镜仍电力点亮、作为工作灯塔使用。[NPS 灯塔介绍](https://www.nps.gov/gate/learn/historyculture/sandy-hook-lighthouse.htm)、[NPS Maritime Structures](https://www.nps.gov/gate/learn/historyculture/sandyhookmaritime.htm)

**光源 / 旋转**：电力点亮可确认；最新灯泡或 LED 型号 **Unknown**。公布的是固定光，不是等待转到观察者方向才出现的一束扫光。旋转周期对该工作方式不适用，没有支持额外旋转的证据。

**历史差异**：光源经历燃料灯到电灯的变化，1857 年三阶透镜的保留不能解释为机械扫描升级。无已核验数值 SECTR1/2、束宽或遮光边界，不把缺少扇区资料写成“已确认无遮挡的 360° 实测覆盖”。19 NM 继续仅解释为标称射程。

类别 C。适合安静的固定暖白光与灯塔建筑锚点；不适合为增强动态效果加上旋转。NPS 的塔体照片和灯塔介绍可作形态参考，不能由其中散射光的照片测出真实束长。

### T6. Romer Shoal — 35070 — B；旋转机制继续核查的首选

**历史 / 最近可直接确认的机械证据**：USCG 编写、日期为 2006-08-08 的 NRHP 材料，在 PDF 页 9 明确描述灯室内 VRB-25 marine rotating beacon，页 10 记其约 1997 年安装；同时记载 1898 年四阶 Fresnel、1966 年换为 190 mm 亚克力光学装置的演变。这里的“旋转”是设备文字证据，不是由两闪/15 秒猜出来的。[官方 NRHP PDF](https://npgallery.nps.gov/NRHP/GetAsset/990d94d0-8683-4719-a533-d857cba14081)

**当前资料冲突**：USLHS 的 Romer Shoal 条目仍列 Current Optic: 190 MM，条目输入日期为 2017-07-21；管理机构历史页的搜索可读正文则列 VRB-25。**2017 是目录录入日期，不是现场检查日期；搜索引擎刚抓取网页也不是刚更新过设备。** 不能据此宣布 VRB 被换回 190 mm，也不能凭管理页未注明时点的文字完全排除后续改装。[USLHS 档案](https://archives.uslhs.org/places/romer-shoal)、[管理机构历史页，直接打开未成功](https://romershoal.org/history/romer-shoal)

因此当前实际安装型号为 **Unknown（存在 VRB-25 的强历史证据）**。当前主灯/备用灯启用状态、转速、顺逆时针、启用透镜面板数、遮黑面板布局、束宽和遮光区均 **Unknown**。本轮没有取得足以解决冲突的 2026 年维护记录或带时间信息的设备照片。

**不能从 VRB 型号及灯质补参数**：USCG 2008 年 servicing guide 第 3-50 页说明 VRB-25 为可选转速的多面板旋转信标，部分面板可遮黑。设备族有可调速度，不意味着 Romer 使用出厂速度；六个安装位置不等于现场有六道有效光束，也不能从两闪/15 秒反算唯一转一圈时间。[USCG 设备手册，PDF 页 102](https://www.govinfo.gov/content/pkg/GOVPUB-HS7-PURL-LPS104000/pdf/GOVPUB-HS7-PURL-LPS104000.pdf)

**更早的旋转史**：US Lighthouse Society 的 Thomas Tag《Lens Rotation》记 Romer Shoal 的早期四阶滚珠轴承透镜每 20 秒一转。这是旧 Fresnel 时代的机械记录，不能与 1997 年 VRB 或今天的两闪/15 秒混用；旧装置旋转方向仍 **Unknown**。[USLHS，Lens Rotation](https://old-site.uslhs.org/lens-rotation)

**当前可用光学约束**：W、两闪一组、总周期 15 秒、标称 15 NM 可保留；原 ENC 的 SIGSEQ 仍为空，不知道两次闪光各持续多久。雾号的“2s bl”等是声音，不是光。没有明确数值扇区，不能为它画“已验证的扫描扇区”。

类别 B，并列为继续索取设备证据的第一优先级。若未来取得现役 VRB 确认、转速及面板配置，可重新评估 A；在此之前只能做明确标为示意的光束运动，或限定时代的历史机制说明。

## 4. 旋转参数与方向证据汇总

| 独立塔体 | 当前旋转机制证据 | 当前完整旋转周期 | 顺 / 逆时针 | 当前公开方向信息 | 历史参数是否可用 |
|---|---|---|---|---|---|
| West Bank | 具体调制装置 Unknown；已知固定方位扇区和导标功能 | Unknown；**不能写 6 秒/圈** | Unknown | 红 4°–181°；白 181°–4°；白色导标 293°–301° | 旧设备记录不能代替现役调制方式 |
| Staten Island / Swash Rear | 当前灯质是两项 F W 定向功能；公开记录描述固定透镜光路 | 固定导标光不适用 | 不适用；无另一旋转系统证据 | 34795 仅导标线上可见；35035 另一导标线；均缺数值宽度 | 透镜史能说明方向性，不能生成扫描 |
| Coney Island | 现役具体机构 Unknown；后续装置有 190 mm 记录 | Unknown；**不能写 5 秒/圈** | Unknown | 无已核验数值扇区/遮光区 | **旧透镜 2 rpm → 30 秒/圈**，只适用其历史时期 |
| Robbins Reef | 300 mm 后续装置有记录；旋转/电子闪光细节 Unknown | Unknown；**不能写 6 秒/圈** | Unknown | 无已核验数值扇区/遮光区 | 旧 Fresnel 传动/转速 Unknown |
| Sandy Hook | NPS 明确固定三阶 Fresnel 白光 | 固定光不适用 | 不适用 | 无已核验数值扇区/遮光区 | 电灯化不是旋转证据 |
| Romer Shoal | 2006 官方材料证明曾有 VRB-25；现役记录存在冲突 | Unknown；**不能写 15 秒/圈** | Unknown | 无已核验数值扇区/遮光区 | 早期 Fresnel **20 秒/圈**；不能用于当前 VRB |

扇区角度保留原始海上观察方位约定；若日后转换为从灯向外的射线，需要处理视向反转。扇区边界、机械转向和机械转速是不同概念。夜间照片或长曝光中的光带还受到摄影机曝光和空气散射影响，不能单独作为转速、束宽或真实覆盖距离的测量。

## 5. 来源质量、访问限制与照片使用

优先使用本地已审计的 USCG / NOAA 运行属性，再查政府设备/历史材料、管理机构及收藏机构说明；专家目录仅补线索。所有网络来源访问日期均为本报告日期；网页访问日期不代表资料截至日期。

| 来源 | 资料时点 | 本轮用途与限制 |
|---|---|---|
| [本地 source_manifest.json](source_manifest.json)、[USCG MSI](https://navcen.uscg.gov/msi)、[NOAA ENC](https://charts.noaa.gov/ENCs/ENCs.shtml) | 2026-11-17 下载快照 | 坐标、名称、灯质、周期、射程、备注、扇区；不是现场设备清单或实时状态 |
| [NPS Sandy Hook](https://www.nps.gov/gate/learn/historyculture/sandy-hook-lighthouse.htm) | 页面更新 2026-08-25 | 对当前固定三阶 Fresnel 的较新直接说明 |
| [NYC LPC Coney Island PDF](https://www.nyc.gov/assets/lpc/downloads/pdf/proposed_landmarks/Coney_Island_Lighthouse_Calendaring_20261020.pdf) | 2026-10-20；附 2025 照片 | 工作状态、独立塔体及结构；未给现役转动装置 |
| [Custom House Maritime Museum](https://customhousemaritimemuseum.org/u-s-coast-guard/) | 2025 借展/修复信息 | 被移出旧透镜的藏品、照片与明确设计 rpm；不是当前安装证明 |
| [USCG/NPS Romer Shoal NRHP PDF](https://npgallery.nps.gov/NRHP/GetAsset/990d94d0-8683-4719-a533-d857cba14081) | 2006-08-08；附 2004 照片目录 | 旋转机构的直接历史证据；不是 2026 检修记录 |
| [NPS Robbins Reef NRHP PDF](https://npgallery.nps.gov/GetAsset/fe9abab9-95b3-493d-9f2c-8c25dad4043d) | 2006-01-25；附 2003 及更早照片目录 | 透镜替换历史；没有当前 rpm |
| [National Lighthouse Museum，Spring 2021](https://lighthousemuseum.org/wp-content/uploads/2021/06/nlm_newsletter_spring2021.pdf) | 2021 | Staten Island 两道固定光及夜景照片；全文抓取遇到体积限制，相关页内容通过官方域名搜索索引核查，未把照片当运动测量 |
| [Noble Maritime Collection FAQ](https://noblemaritime.org/robbins-reef) | 页面未注明技术更新日期 | 管理与运行分工、太阳能信号；不能据此推断旋转 |
| [USCG servicing guide](https://www.govinfo.gov/content/pkg/GOVPUB-HS7-PURL-LPS104000/pdf/GOVPUB-HS7-PURL-LPS104000.pdf) | 2008-06-04，第 3-50 页 | 设备族结构及可配置性；不是某塔的设置记录 |
| [USLHS Romer Shoal](https://archives.uslhs.org/places/romer-shoal)、[Coney Island](https://archives.uslhs.org/places/coney-island) | 所示条目输入 2017-07-21 | 设备线索及图片目录；Romer 与 NRHP 存在冲突，未视为最新现场结论 |
| [USLHS，Thomas Tag: Lens Rotation](https://old-site.uslhs.org/lens-rotation) | 历史技术研究；页面未注明现场更新 | Romer 早期轴承透镜转速，不证明现役转速 |

访问限制：部分 USCG Historian 页直接请求 403，相关内容通过同一官方域名搜索索引读取；USLHS 页部分请求超时/429；Romer 管理站历史页只能取得搜索索引正文；West Bank 的 NPS PDF 为占位内容。几份 PDF 的截图接口也失败，本报告引用其文字和照片目录，不声称已通过照片判定现役装置。故 **Unknown 保留为 Unknown**，没有用普通搜索摘要或第三方复制页补成现场观测。

照片和设备图本轮只提供参考链接，没有下载后嵌入地图或重新发布；公开可浏览不等于可自由用于成图。以后如采用管理机构、博物馆、摄影者或档案中的图片，应逐件核对作者、年代、授权及署名。也不要把旅游/博物馆旧文中“仍使用原 Fresnel”的泛称覆盖 USCG 的拆除记录；Coney 的旧设备已移出是明确的时间分界。

## 6. 推荐重点对象与视觉建议

推荐 **4 座主角 + 1 座可选补充**，按建筑而不是登记数组织：

| 优先级 | 独立塔体 | 有依据的表现内容 | 不应声称 |
|---|---|---|---|
| 1 | Sandy Hook | 港口入口的恒明暖白锚点、清楚的历史塔形 | 真实旋转、19 NM 内全可见 |
| 2 | Romer Shoal | 作为继续调查旋转机构的主候选；现阶段只可明确标注艺术示意，或讲清时代的历史装置 | 当前实际旋转周期、方向、束宽及两次闪光时长 |
| 3 | West Bank | 红白固定方位、窄导标方向、6 秒等明暗，体现光的方向性 | 6 秒扫一圈、以标称距离铺满的光照覆盖 |
| 4 | Robbins Reef | Upper Bay 的绿色灯塔焦点，0.6 秒亮 / 5.4 秒暗，固定短光带也须标艺术效果 | 已证实旋转镜头或 6 秒转一圈 |
| 可选 5 | Coney Island | 红色灯塔焦点；若做设备历史，可另注明旧透镜 2 rpm / 30 秒一圈 | 把历史转速用作现役红灯速度 |

Staten Island / Swash Rear 可作为 West Bank 的固定导标对应端，以**一座塔、两项功能**辅助解释，不必再作为另一座“旋转主角”。

**简短视觉建议**：保留现有深海军蓝海面与暗海岸，153 条原登记点全部保留为克制背景；把注意力集中于上述少数灯塔的建筑与不同光学功能。固定白光、红白定向光和绿色节奏可以形成层次，无需每座都扫转。若最终选择艺术化运动，统一清楚标为“illustrative beams”，长度与宽度均为艺术参数；当前真实旋转仍不足 3 座，不能用不明参数凑数。本轮不实施这些调整，现有 153 点交互及其原始灯质数据完整保留。

### 若下一步要提升为真实旋转动画，仍缺什么

优先向 USCG Aids to Navigation 维护记录或实际光学维护机构核实 Romer；其次核实 Coney 与 Robbins。需要的是现役设备型号及安装/检修日期、旋转机构确认、现场 rpm 或一圈实测时间、从上方观察的旋转方向、有效面板/束的方位配置、遮黑/遮光信息，以及主灯与备用灯状态。**本轮没有发送邮件或联系机构。** 在获得这些证据前，不把 B 改为 A，不改写现有数据。


## Final implementation and timing

These final rendering notes supersede the preliminary visual recommendations above; source research remains unchanged.

## 两种时间模式

### Continuous data：准确航标时序的连续 HTML

HTML 默认模式。灯塔光束仍是艺术化 12 秒旋转，但航标的时钟持续运行，不在第 12 秒重置，也不施加接缝渐隐。

- 141 条按已核验原始 SIGSEQ 每段秒数运行。
- 1 条 `Iso Y 6s` 按等明暗定义运行，亮 3 秒 / 暗 3 秒；不冒充原始 SIGSEQ。
- 8 条恒明灯保持常亮。
- 3 条缺少完整可靠时序的登记点维持低亮静态，不猜测周期或脉冲时长。
- 13 条有季节、冰况或靠泊条件的记录默认维持低亮底点；主动开启 **Include conditional-operation scenario** 才播放其节奏，仍不表示当前正在运行。

支持 Play / Pause、Restart、0.5× / 1× / 2×、时间轴、153 条登记搜索与选择、点击航标查看名称、灯色、原始灯质、周期、亮灭序列、条件和来源。实际灯间相位未知；所有共同零相位仅是可视化设定。

### 12 s artistic loop：GIF / MP4 与 HTML 短循环模式

两座旋转光束统一每 12 秒一圈，起始角度不同。12 秒是传播用的艺术参数，**不是历史或现役转速**。

51 条有节奏记录的周期不能整除 12 秒，包括 2.5、5、8 秒等。这些对象的原始 SIGSEQ 和周期没有改写、拉伸或加速：仅在每轮最初 / 最后 **1.2 秒**将参与播放的光晕与亮点平滑衰减至微弱底点，遮掩第 12 秒处的人为显示相位重置。渐隐期间不再属于完整准确的灯光时间复现。条件未启用的对象一直低亮，不另外播放。

周期可整除 12 秒的灯光保留原始节奏；恒明灯与缺时序静态点不受接缝渐隐影响。熄灭时不移除位置底点。短循环与连续数据模式的差别明确显示在 HTML 信息面板中。

GIF 与 MP4 使用同一 30 fps 确定性画面序列；GIF 再按 20 fps 采样、固定 128 色调色板压缩，无整图接缝交叉淡化。MP4 使用 CRF 18 保留暗部层次。两个格式布局相同，只改变分辨率、帧率和编码。

## 灯塔光束：艺术层与数据层分开

| 对象 | 本版表现 | 证据与限制 |
|---|---|---|
| Romer Shoal | 白色光束顺时针 12 秒/圈，980 px 艺术长度 | 历史 20 秒/圈仅作为研究背景，本版不播放该历史转速；当前旋转机制未确认；原登记缺完整 SIGSEQ，登记点保持低亮静态 |
| Coney Island | 红色光束顺时针 12 秒/圈，840 px 艺术长度 | 旧透镜历史 30 秒/圈不再作为本版转速；真实登记点仍按 `Fl R 5s` 的核验序列播放，光束与该灯质是两层不同含义 |
| Sandy Hook | 稳定白光，不旋转 | 核验 F W；辉光尺寸是艺术参数 |
| West Bank | 固定红白方向光，显示长度 720 px | 原角度保留：红 4°–181°、白 181°–4°、白导标 293°–301°；沿用亮 3 秒 / 暗 3 秒，不旋转 |
| Robbins Reef | 绿色周期脉冲，不强制旋转 | 核验亮 0.6 秒 / 暗 5.4 秒；时间边界不人为延长 |

旋转光束相比上一阶段长度增加约 40%，角向高斯宽度也适度增加；继续使用半透明、连续羽化和径向衰减，不画硬三角形。West Bank 不扩大已知角度，只扩大艺术显示长度并保留区内羽化。航标光晕比灯塔光束弱。

灯塔真实位置不动；顺逆时针、初始方向、长度、宽度、亮度及光束形态均为艺术化重构，不是实测。光束长度不取自标称射程。陆海遮罩只调节画面层次，不模拟遮挡、视域、天气、眼高或真实可见范围。

## Methodology / Limitations

- **153**：USCG Light List 独立登记条目数，非物理灯具总数。一个条目可能包含多个灯、passing light、备用灯或颜色扇区，不重复累加。五个主角来自这 153 条，没有新增航标。
- **142**：141 个原始 SIGSEQ 加 1 个 Iso 定义可复现节奏的条目数，不是旋转光束数量。
- **5**：有明确方向扇区角度资料的登记条目数，不是扇区组件总数。
- 本地 CSV 中 7 条 lighthouse 登记实际对应 6 座塔体；共塔关系与现役/历史设备差异见 [灯塔光束研究](lighthouse_beam_research.md)。
- 灯色及有依据的闪烁节奏来自 USCG / NOAA，未拿浮标外观颜色替代灯色，未将所有 Q 灯统一为每分钟 60 闪。
- St. George Ferry Terminal Fog Light（34949）、Romer Shoal（35070）、OPT Lighted Research Test Buoy（35192）缺可靠完整时序，不能按原始数据准确复现闪光；不从 `Fl(2)` 猜测脉冲时长。
- 所有灯光同步展示仅为可视化，不表示港口某一真实时刻；`INACTIVE=0`、有设备或有登记不保证当前正常运行。原 MSI 数据可能过时/不完整的警告保留。
- 原静态图移出的说明在这里完整保留：

> Counts refer to registered entries, not individual fixtures.
>
> Published light characteristics; not a real-time display or navigational chart.
>
> Soft glows are artistic, not calculated light coverage.
>
> Fine directional ticks mark documented sector bearings only.

颜色含义仅是一般解释：Red — starboard-side lateral aids；Green — port-side lateral aids；White — other navigation functions；Yellow — special-purpose aids。没有仅凭灯色给单个对象推定助航功能。

**Not for navigation.**

