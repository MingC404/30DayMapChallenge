# Day 19 — SoHo 选址与数据更新

调查日期：2026-11-18。当前原型已从 Williamsburg 改为 SoHo；[原数据调查](data_feasibility.md)、[原选址](site_selection.md)和 [传播方法](propagation_methods.md)保留为历史记录。没有保存第二套旧版 HTML／地图输出。

## 调查口径

初筛窗口为 south 40.7195、west −74.0040、north 40.7260、east −73.9955，覆盖 Prince、Spring、Broome 和 Broadway、Greene、Mercer 周边，并包括相邻道路以便比较。它只是 API 取样窗口，不是正式研究区。

实际调用四类来源：

|来源|局部获取结果|保留内容与限制|
|---|---:|---|
|[NYC 311 / erm2-nwe9](https://data.cityofnewyork.us/d/erm2-nwe9)|61 条宽口径记录|2025 完整日历年，分类／描述提及 Odor 或 Fumes；不是 61 条室外气味投诉|
|[OpenStreetMap API](https://wiki.openstreetmap.org/wiki/API_v0.6)|150 个命中 POI 对象|amenity=cafe/restaurant/fast_food/food_court，shop=bakery/coffee/florist；不是营业商户普查|
|[NYC OTI BUILDING / 5zhs-2jue](https://data.cityofnewyork.us/d/5zhs-2jue)|933 个轮廓对象|真实 MultiPolygon，不用建筑质心代替遮挡|
|[NYC CSCL / inkn-q76z](https://data.cityofnewyork.us/d/inkn-q76z)|138 条 segment|真实道路中心线；不推断精确路缘或人行道宽度|

311 使用 `2025-01-01 ≤ created_date < 2026-01-01`。61 条中严格保留可用于室外／经营场所示意的 49 条，另有 11 条室内相关、1 条饮用水 Taste/Odor 排除。不存在原始投诉自由文本，只有类型、两级描述和机构处理说明。数据字段、完整查询及获取时间见 `research/soho/query.json`。

空间查询天然排除了缺纬经度的投诉，不能用样本声称该街区坐标完整率 100%。坐标通常是地址地理编码或 POI 代表点，数字小数位不意味着门口／井盖精度。不同 unique_key 即使同坐标仍保留，独立坐标数单独统计。

OSM node 保留原坐标，way 使用包络中心并披露方法。相关 relation 数为 0；候选区同名且相距小于 30 m 的 POI 重复复核标记为 0，不能保证无漏标或异名重复。当前 POI 快照不证明商户在 2025 年已经存在、现场烘焙或正在释放气味。

## 四个相邻 4–6 街块候选

从真实 OSM 街道线构面，排除小于 1,900 m² 的碎面；每个组合验证了街块共享边界超过 2 m、整体连通。统计范围为街块合并面外扩 12 m，以涵盖道路地址点；这只是计数边界，不是气味 buffer。候选重叠，不能把各行数量相加。候选精确范围可由 `block-faces.geojson` 和 `candidate-comparison.json` 的 face_ids 重建；不再保存四套可推导的候选 GeoJSON 副本。

|候选|街块数|范围|面积 km²|潜在来源|气味／油烟投诉|独立投诉坐标|室内排除|建筑覆盖率|
|---|---:|---|---:|---:|---:|---:|---:|---:|
|A|4|Greene–Broadway，Prince–Broome|0.0628|3|14|12|3|56.3%|
|B|6|Wooster–Broadway，Prince–Broome|0.0893|3|17|14|3|57.9%|
|C|6|Greene–Crosby，Prince–Broome|0.0910|6|16|14|7|58.9%|
|**D（采用）**|**6**|**Mercer–Lafayette，Prince–Broome**|**0.0886**|**18**|**12**|**10**|**7**|**54.9%**|

A、B 在中心街道有多个投诉坐标，但 POI 只有 2 restaurant + 1 shop=coffee，没有 cafe 或 bakery 代理。C 虽增加餐饮点，仍没有 cafe／bakery。D 向东覆盖 Broadway、Crosby 至 Lafayette，在六个街块内同时有咖啡、烘焙、餐饮和多个独立投诉位置，因而更适合两类证据的交互比较。不是因为预设 SoHo 更臭或更香。

## 最终范围与数量

最终为 Prince–Spring 与 Spring–Broome 两排，Mercer–Broadway、Broadway–Crosby、Crosby–Lafayette 三列，共 **6 个相邻街块**。街块 core 包络为 west −74.0006646、south 40.7210819、east −73.9964625、north 40.7246320；包络不是精确统计边界，以 `research/soho/selected-extent.geojson` 的 `counting_extent` 为准。12 m 街缘可能包括对侧地址点，标记按原始坐标绘制。

|证据|实际数量|页面表达|
|---|---:|---|
|OSM cafe|4|暖色 Potential Aromas：Coffee|
|OSM shop=coffee|1|与 cafe 合并为 Coffee 筛选，仍是 POI 代理|
|OSM bakery|1|暖色 Potential Aromas：Baking|
|OSM restaurant|10|暖色 Potential Aromas：Food|
|OSM fast_food|2|暖色 Potential Aromas：Food|
|311 Restaurant Odor/Fumes (AD2)|4|紫色 Reported Odors|
|311 Vehicle Idling Odor/Fumes (AD3)|6|紫色 Reported Odors|
|311 Food Establishment / Odor|1|紫色 Reported Odors|
|311 Mobile Food Vendor / Smoke/Odor|1|紫色 Reported Odors；不能分离烟与气味|
|室内相关投诉，排除|7|不出现在室外来源图层，不生成传播|

最终为 **18 个 POI + 12 条历史投诉 = 30 条可查看记录**；投诉坐标为 **10 个**，并不等于 12 个独立排放源。地图对完全同坐标的记录加数量提示，具体日期可从列表选择。没有 Sewer Odor、Chemical Odor 或 florist 命中最终范围，不补造。卫生／公共便溺不是本轮的查询目标，未纳入当前图层，**不能把未查询解释为街区没有垃圾或便溺事件**，也不声称有尿味实测。

最终范围有 141 个相交建筑轮廓对象、34 个相交 CSCL 段；建筑覆盖率 54.9%（合并几何并按统计范围裁切后计算），对象数不是建筑栋数。投诉到范围内最近 POI 代表点的直线距离中位数约 51.7 m，仅支持“空间相邻且未完全重合”，不支持归因，也不代表精度误差已被消除。

## 相对 Williamsburg 的取舍

原 Williamsburg 五街块为 24 个 POI、5 条气味投诉／5 个坐标，建筑覆盖率 34.6%；本次 SoHo 六街块为 18 个 POI、12 条投诉／10 个坐标，建筑覆盖率 54.9%。SoHo 的 POI 更少、街块更多、建筑更密，不能说整体数据全面优于前者。其优势是历史投诉的空间位置更丰富，仍保留三类潜在香气代理，适合当前“来源对比”的设计；劣势是没有原区那条明确 Sewer Odor。本轮改版并不比较街区卫生或风险。

## 传播与交互语义

默认 Explore Smells，展示全部真实标记，不自动生成鼠标 buffer。暖色圆点是 OSM **潜在香气来源**，紫色菱形是 **311 历史气味／油烟投诉**。颜色表达来源和证据类别，不表达客观愉悦度、浓度或健康风险。

Explore Smells 仍悬停预览、点击固定，最多两个真实记录。固定 ① 实线、② 虚线；第三个不会自动替换已有来源，筛选也不会隐藏固定记录。该模式的重叠是独立图层叠加，不是新气味类别。

Explore Space 已改为 **One Fluid, Multiple Smells**：只有一个鼠标几何中心、一片连通液体和一个等值轮廓，不再有子模式或参考源。几何形状是假设性的，颜色则由本节真实来源决定。同坐标投诉先去重，18 个 OSM 位置与 10 个投诉坐标按来源类别各自计算 `max_i K(D_i)`，单位峰值归一化，不相加原始次数。两类各做一次多源 Dijkstra 后缓存，与鼠标几何场分开；无邻近证据处保持低饱和中性。颜色混合和核参数详见 [README.md](README.md) 的 Smell Evidence Field 归一化说明，不代表浓度或实时气味。

形状含义为 **Illustrative spatial reach under a building-constrained propagation model.** 所有来源初始 Spread 为 55，共用一个无单位的艺术预算；滑块不是经验证的气味传播米数。真实地图的 50 m 比例尺只解释地理空间。轮廓从各自计算起点逐渐生长，不平移已经完成的区域冒充传播。没有真实排放量、浓度、风场、物理流体守恒或当前闻到气味的保证。

沿用 2 m 保守障碍网格、加权 Dijkstra 和 Marching Squares；颜色填充、线性插值、平滑及渐显最终全部裁切到建筑 mask 和精确统计边界。计算外延为 110 m，只新增几何上下文，当前共 647 个轮廓对象、102 条道路段，不增加来源点或研究街块。未采用城市全量原始数据。

来源在楼体内时，仅为算法寻找 20 m 内开放网格点；原始标记不移动，偏移可在来源卡片展开查看，不称为入口／排风口／井盖。当前 30 个来源均可计算，最大偏移约 8.9 m。模型未知围墙、关闭通道和通行权，2 m 保守网格也可能封闭真实窄缝。

## 文件、许可与复现

- `research/soho/`：原始窗口输入、街块面、比较表、最终来源与边界、室内排除记录、查询参数。清理后不保留 classified、inventory、空 relation 文件及候选面副本。
- `node 19/scripts/rebuild.mjs` 离线重现既定 D 范围。`--refresh` 才执行小范围抓取、内存 XML 构面、既定候选统计和计算几何更新；Python 不再通过工作目录里的临时 XML 接收数据。
- Python 使用 Shapely；依赖位置沿用历史调查的临时环境。重跑 API 可能因动态数据修订而得到不同结果，当前页面以保存的样本为准。
- [OSM ODbL](https://www.openstreetmap.org/copyright)：页面署名并链接许可，OSM 与 NYC 来源分开保存；再发布派生数据库需遵守 ODbL。NYC 适用 [Open Data 使用条款](https://cityofnewyork.github.io/opendatatsm/publicpolicies.html)，不自行标为 CC0。

本轮仅更新 HTML 原型、代码和局部样本；历史 Williamsburg 研究文件保留，旧版运行几何已替换。无最终图像或动画导出。
