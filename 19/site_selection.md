# Day 19 — The Invisible Streets：候选区域与选址

> 历史记录：本文保留 Williamsburg 阶段的候选与结论。当前采用的 SoHo 六街块范围见 [soho_research.md](soho_research.md)。

调查日期：2026-11-18。**推荐 Williamsburg 的 Bedford Avenue–Grand Street–Metropolitan Avenue 周边五街块**；若必须保留公共便溺行为线索，改选 LES 的 Allen–Orchard–Ludlow 一带。推荐依据是本次实际记录和几何条件，不是对街区卫生状况的评价。

## 方法与边界

先以五个紧凑 bbox 探测 Chinatown、LES、East Village、West Village、Williamsburg，每个约 0.13–0.15 km²；这些是取样窗口，不当作最终范围。候选不是全纽约穷举排名。

从局部 OSM 街道线构面：使用 primary、secondary、tertiary、residential、unclassified、living_street、pedestrian，排除 service 小路和非街道步道，剔除小于约 1,900 m² 的碎面。每个最终候选固定取 **5 个共享边界超过 2 m 的相邻面**，在所有符合条件的组合中选择质心距离初筛窗口中心之和最小者。这个几何规则不使用投诉数量挑选街块。

以五面合并边界外扩 **12 m**、并裁回原 bbox 的范围计数，以涵盖街道地址点；这 12 m 是统计边界处理，不是气味传播 buffer。精确边界在 `research/*_selected_extent.geojson`，其中 `five_blocks` 是街块核心，`counting_extent` 是统计范围。所有 POI、投诉和建筑覆盖率均按后者重新计算，不能引用大 bbox 总数替代最终数量。外扩带可能纳入对侧街缘，作品须据精确坐标呈现。

East Village 初筛有 119 个 POI、13 条室外／经营场所气味或油烟投诉，但原窗口仅包含一个完整封闭街块；它切断了长街块。为避免把半个街块凑成五个，本轮不列入最终四候选，也没有为它扩大下载。

## 四个最终候选的实际数量

投诉均为 2025 全年；OSM 为获取时现状。这里“气味投诉”包括明确 Odor/Fumes、Smoke/Odor 类，并不保证市府核实或确在室外释放。室内投诉单列。

|候选（均 5 街块）|统计面积 km²|气味／油烟投诉|独立气味坐标|室内气味类|垃圾卫生线索|公共便溺行为|POI|
|---|---:|---:|---:|---:|---:|---:|---:|
|Chinatown，Grand–Broome 周边|0.0638|2|1|3|44|0|43|
|LES，Allen–Orchard–Ludlow|0.0456|14|5|0|18|1|37|
|West Village，Bleecker–Grove–Christopher|0.0536|5|3|3|70|0|26|
|Williamsburg，Bedford–Grand–Metropolitan|0.0494|5|5|0|20|0|24|

同一坐标可能对应多条独立请求；“独立坐标”只是减少重复地点膨胀的指标，并不证明是独立气味源。上述四类投诉列互斥，总相关请求分别是 49、33、78、25。

|候选|Cafe|Bakery|Restaurant|Fast food|Florist|轮廓对象数|建筑覆盖率|CSCL 相交段|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|Chinatown|13|2|16|11|1|150|47.9%|29|
|LES|6|3|18|10|0|123|39.4%|29|
|West Village|2|1|20|3|0|147|38.9%|43|
|Williamsburg|4|2|13|5|0|118|34.6%|32|

轮廓数不是建筑栋数。覆盖率为范围内 footprint 合并面积／统计范围面积，支持“有足够建筑障碍，同时保留开放空间”的判断；没有证明剩余空间全部是公共可走空间。

## 空间相邻而非重叠

按局部米制近似，计算每条气味投诉到**同一统计范围内**最近 POI 代表点的直线距离（非沿街距离）。跨边界商铺不参与，不能称为全局最近店。

|候选|最近距离 min / median / max，m|距离 20–100 m 的请求数|距离 ≤5 m 的请求数|
|---|---|---:|---:|
|Chinatown|11.1 / 11.1 / 11.1|0 / 2|0|
|LES|8.6 / 32.3 / 32.4|13 / 14|0|
|West Village|8.9 / 25.2 / 25.2|3 / 5|0|
|Williamsburg|9.5 / 12.7 / 38.2|2 / 5|0|

这仅证明当前代表点并非完全重合，且存在邻近关系；311 地址点和 OSM 中心点误差可达类似距离，**不能把 10 m 差异解释为可靠的不同排放点**，也不能据距离认定某家店造成某条投诉。LES 的 13 条相邻记录受到重复地址影响，不能等同 13 个独立空间关系。

## 候选判断

### A. Chinatown：香气 POI 丰富，独立室外投诉不足

核心边界包络：west −73.9971031，south 40.7172902，east −73.9933726，north 40.7201804；精确范围不是该矩形。位于 Grand、Broome、Hester、Mott、Bowery、Chrystie 周边的五块相邻街块。

13 家 cafe、2 家 bakery 和 1 个 florist 使潜在香气种类最完整。但最终范围只有 2 条怠速 Odor/Fumes，且位于同一坐标；初筛大 bbox 的一条 Sewer Odor 和三条公共便溺均不在最终范围内，不能借用。其 44 条垃圾卫生线索仍不能弥补明确气味投诉不足。不作为首选。

### B. LES：投诉数量最多，保留了公共便溺线索

核心包络：west −73.9904681，south 40.7188741，east −73.9877644，north 40.7216145。包括 Allen、Orchard、Ludlow 一带，在 Delancey–Rivington–Stanton 周边形成五块相邻街块；精确外边界为不规则形。

14 条气味相关请求：9 条 Restaurant AD2、3 条 Vehicle Idling AD3、1 条 Food Establishment Odor、1 条 Chemical Odor HD1；另有 18 条垃圾卫生线索、1 条公共便溺。37 个 POI 含 6 cafe、3 bakery。香气与投诉组合较强，街道转角和 Allen 周边道路结构可形成分支流动。

限制是 14 条请求仅 5 个独立坐标，餐馆类重复集中，数量优势不等于持续污染或更臭；没有 Sewer Odor，没有花店代理。如果叙事必须出现“公共便溺记录（非尿味实测）”，这是最合适的备选。

### C. West Village：街道几何最丰富，卫生线索多于气味证据

核心包络：west −74.0035825，south 40.7317060，east −74.0000660，north 40.7338470。Bleecker、Grove、Christopher、Barrow、Waverly、7th Avenue South 周边。

不规则交汇最适合测试绕角轮廓，覆盖率 38.9%。5 条气味相关请求中 3 条为流动餐车 Smoke/Odor，其余为 Restaurant AD2、Chemical Odor 各 1 条；有 70 条垃圾卫生线索和 26 个 POI。投诉点不一定是餐车长期位置；最终范围也没有公共便溺记录，不能引用大 bbox 的 7 条。作为几何效果实验备选，数据叙事弱于 Williamsburg／LES。

### D. Williamsburg：推荐

核心包络：west −73.9622890，south 40.7133450，east −73.9588018，north 40.7159300。涉及 Berry、Bedford、Driggs、Grand、Metropolitan、North 1st、North 3rd、South 1st；实际范围以 GeoJSON 为准，不是这些道路的整个街区。

5 条明确类别分别为 **Sewer Odor 1、Food Establishment Odor 1、Restaurant AD2 1、Vehicle Idling AD3 2**，分布在 5 个独立坐标。20 条垃圾卫生线索另列；24 个 POI 含 4 cafe、2 bakery、13 restaurant、5 fast_food。建筑覆盖率 34.6%，118 个相交轮廓对象，街道方向变化与交汇足够支持绕建筑、转角和细长分支的视觉试验；不需要先假设这里有臭味。

可核查例子：

|311 unique_key|日期|原始类别|街名|解释|
|---|---|---|---|---|
|64971320|2025-05-16|Sewer / Sewer Odor (SA2)|Bedford Avenue|处理说明为检查并清理 catch basin／inlet；不提供实测气味值|
|63683214|2025-01-08|Food Establishment / Odor|Grand Street|经营场所气味投诉，结案不等于确认排放|
|66313832|2025-09-29|Air Quality / Restaurant AD2|Bedford Avenue|处理说明称检查时未观察到违规，须保留这个区别|
|63805540、66589069|2025-01-18、2025-10-23|Air Quality / Vehicle Idling AD3|Metropolitan Avenue|历史废气／气味投诉，并非实时源|

POI 例子包括 OSM 中的 Black Brick Coffee、Martha’s Country Bakery、La Bicyclette Bakery；仅作潜在来源举例，不将任何投诉归因到这些店。

取舍：推荐范围**没有公共便溺记录和花店 POI**。不能为了画出尿味或花香而补点。作品可聚焦咖啡／烘焙／食物潜在来源、历史污水／餐饮／废气投诉、垃圾卫生线索三类证据。若必须在同一范围展示尿味，“尿味”需另有明确观测，当前两个推荐选项都不能直接满足。

## 下一阶段边界条件

数据足以支持五街块的探索性示意，不足以支持门口级精确源定位。下一阶段只需在选定范围外增加约 100–150 m 的建筑计算边缘，避免屏幕边界截断绕行路径；不必下载全纽约。源点落在楼体里时应显示原始位置，并仅为算法生成可追溯的外墙／街缘投影点，不伪装成入口或排风口。楼间缝隙是否真可通行、是否有墙或围栏仍需单独核验；本轮不通过猜测制造巷道。

原始 API 数据集链接、字段及许可见 [data_feasibility.md](data_feasibility.md)；历史精确计数见 `research/selected_summary.json`，选择规则已在本文“方法与边界”记录。失效旧脚本与宽窗口过程数据已清理，选定来源记录和边界仍保留，详见 `research/README.md`。
