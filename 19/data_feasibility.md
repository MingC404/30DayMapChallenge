# Day 19 — The Invisible Streets：数据可行性

> 历史记录：本文对应 Williamsburg 阶段。当前 SoHo 原型的数据与选址见 [soho_research.md](soho_research.md)；以下原调查内容保留。

调查日期：2026-11-18。投诉统一采用 **2025-01-01 ≤ created_date < 2026-01-01** 的完整日历年；OSM、建筑和道路为本次访问时的现状快照。两者不能解释为同期实测。本轮未制作地图。

## 结论与证据等级

可支持“潜在香气来源 + 历史气味投诉 + 卫生线索”的交互叙事，**不能支持实测气味浓度地图**。

|层级|本次取得的数据|允许的表述|
|---|---|---|
|实际气味测量／现场嗅觉观测|未取得|不能声称传感器、嗅闻调查或浓度实测|
|明确提及气味的投诉|311 Sewer Odor、餐馆 Odor/Fumes、Food Establishment Odor 等|有人在某时某地报告过气味／油烟；不保证现场调查确认|
|卫生或行为记录|垃圾堆积、垃圾未清理、公共便溺|与气味可能有关的线索，不能直接改名为臭味或尿味|
|潜在香气来源|OSM cafe、bakery、restaurant、fast_food、coffee、florist|可能产生咖啡、烘焙、食物、花香；不证明正在营业或气味逸出|

香／臭的感受也不固定：同类餐饮活动可以同时是潜在食物香气来源和气味投诉对象。

## 1. NYC 311 Service Requests

来源：[2020 to Present / erm2-nwe9](https://data.cityofnewyork.us/d/erm2-nwe9)，[字段元数据](https://data.cityofnewyork.us/api/views/erm2-nwe9.json)，[官方数据调整说明](https://www.nyc.gov/opendata/news/all-news/311-Service-Requests-Updates)。2020 以前历史数据已另列，不能继续把这个接口称为 2010 至今完整库。

已实际请求 API，不仅根据说明页判断。可用字段：`unique_key`、`created_date`、`closed_date`、`agency`、`complaint_type`、`descriptor`、`descriptor_2`、`location_type`、`address_type`、`latitude`、`longitude`、`location`、州平面坐标、街名、地址、`status`、`resolution_description` 等。元数据存于 `research/schema_erm2-nwe9.json`。

`descriptor` / `descriptor_2` 是分类描述，`resolution_description` 是处理说明；**没有可供本次读取的原始投诉自由文本**。不能从这些字段补写“某人闻到了腐烂垃圾”等具体叙述。

### 已在实际样本中确认的类别

下表为四个最终五街块区域的合计；各区边界与分项见 `site_selection.md`。同一服务请求只计一次，不同请求即使坐标相同仍保留，并另报独立坐标数。

|分类／描述|记录数|使用限制|
|---|---:|---|
|Sewer → Sewer Odor (SA2)|1|明确污水／下水道气味投诉；不能当排水口精确位置|
|Air Quality → Air: Odor/Fumes, Restaurant (AD2)|11|餐馆气味／油烟，不能细分烹饪品种|
|Air Quality → Air: Odor/Fumes, Vehicle Idling (AD3)|7|怠速废气／气味投诉|
|Food Establishment → Odor|2|食物经营场所的气味投诉|
|Mobile Food Vendor → Smoke/Odor|3|烟／气味合并分类，不能保证仅为嗅觉投诉|
|Hazardous Materials → Chemical Odor (HD1)|2|化学气味投诉，不能推断具体物质|
|Indoor Air Quality → Sewage Odor|1|室内污水气味，不作为室外扩散源|
|Indoor Air Quality → Chemical Vapors/Gases/Odors|5|室内合并类别，不作为室外扩散源|
|垃圾／卫生代理，严格筛选后|152|垃圾存在或管理问题，不证明气味|
|Urinating in Public → N/A|1|公共便溺行为，不证明尿味|

最终合计 **185 条相关记录**，其中 **26 条室外／经营场所气味或油烟相关投诉**、6 条室内相关投诉、152 条垃圾卫生线索、1 条公共便溺记录。并无实测浓度。

### 尿味核查

精确条件 `complaint_type = 'Urinating in Public'` 的全市 2025 年聚合返回 **1,419 条**，`descriptor = 'N/A'`，其中 **1,405 条有纬经度**（14 条缺坐标；聚合结果在查询记录中）。分类聚合原始响应存于 `research/urination_citywide_2025.json`。

[官方 Public Urination or Defecation 页面](https://portal.311.nyc.gov/article/?kanumber=KA-01958)明确描述举报人的公共便溺行为。**本次未确认独立且可用的“尿味投诉”分类**；四个最终区域及五个初筛样本中，也未得到可直接识别为尿味的描述。不能据此断言整个历史数据库从无尿味相关记录，但不能在作品中把 `Urinating in Public` 改成 `Urine odor observed`。

`URIN` 子串会误匹配 `MANUFACTURING` 和 `Urinal`，前者是制造业噪音，后者可能只是节水／器具问题，均剔除。普通 Sewer、catch basin 堵塞、漏水也不自动计入污水气味；饮用水 Taste/Odor、车内出租车卫生投诉不参与街道空气传播。

### 精度、遗漏与抽样

先按五个约 0.13–0.15 km² 的 bbox 请求小样本，共返回 608 条宽口径记录；所有请求上限 5,000，最大实际返回 251，未触及分页上限。再按精确五街块边界筛选。宽口径中包含误匹配和非气味卫生类别，**608 不是气味投诉数**。历史筛选结果的 `evidence_group` 保存在各候选 `*_selected_311.json`；本轮清理后不再保留旧过程脚本和宽窗口重复副本，保留范围见 `research/README.md`。

空间查询先要求纬经度落入 bbox，因此本地样本天然不含缺坐标投诉，无法据此计算各街区全体投诉的坐标完整率。坐标多为地址地理编码点，数字小数位数不代表厘米级精度；地址点、楼体中心、路口与真实感知位置可能相差数十米。足以探索街块分布，**不足以定位某个门口、排风口、垃圾袋或井盖**。同一地址重复投诉、居民举报倾向、机构处理流程都会影响数量；结案也不等于确认或消除气味。

## 2. OpenStreetMap POI

优先尝试 Overpass，主／备用接口连接失败或超时；最终成功通过 [OSM API 0.6 小 bbox 接口](https://wiki.openstreetmap.org/wiki/API_v0.6)读取五个局部范围。不是下载纽约全量。正式产品应使用预处理静态样本，不能让用户每次移动鼠标都请求公共 API。

提取标签：`amenity=cafe|restaurant|fast_food|food_court`，`shop=bakery|coffee|florist`。保留 OSM `type/id`、标签、名称（如有）和坐标。node 用原坐标；way 用边界框中心并标为 `way_bbox_center`，不是入口。命中多个标签时优先 bakery / coffee / florist，避免同一对象跨类重复；同名且距离小于 30 m 的对象标记复核，不擅自合并连锁门店。五个初筛样本没有命中相关 POI relation，最终四个区域没有同名近距重复标记，但仍不能保证商铺实体绝对无重复或遗漏。

最终四区合计 **130 个 OSM 对象**：餐馆 67、咖啡馆 25、快餐 29、面包店 8、花店 1；独立 `shop=coffee` 和 food_court 在最终范围中均为 0。不是经核实的营业商户名册。未命名 POI 保留，但不编造店名；咖啡馆不一定现场烘豆，面包店不一定现场烘焙，花店不一定向街道释放明显花香。

OSM 是当前编辑快照，无法证明某店在 2025 年投诉发生时已经存在。推荐区的 24 个对象为 4 cafe、2 bakery、13 restaurant、5 fast_food，花店为 0；若选此区域，本轮证据不支持单独花香图层。

许可：[OpenStreetMap copyright / ODbL](https://www.openstreetmap.org/copyright)。后续展示应署名 `© OpenStreetMap contributors` 并提供许可链接；再发布提取／派生数据库须按 ODbL 处理。本轮把 OSM 和 NYC 原始来源分开保存。

## 3. NYC Building Footprints

采用当前 polygon 数据集 [BUILDING / 5zhs-2jue](https://data.cityofnewyork.us/d/5zhs-2jue)，[官方几何元数据](https://github.com/CityOfNewYork/nyc-geo-metadata/blob/main/Metadata/Metadata_BuildingFootprints.md)。未采用 `BUILDING_P` 或地图视图中的点图层代替轮廓。

实查字段：`the_geom`（MultiPolygon）、`bin`、`doitt_id`、`objectid`、`base_bbl`、`mappluto_bbl`、`geom_source`、`height_roof`、`ground_elevation`、`construction_year`、`last_edited_date`、`shape_area`、`shape_length` 等。SODA GeoJSON 坐标为经纬度；网格计算必须转为米制坐标，不能把经纬度直接当米。当前分析使用局部等距近似，后续实现宜统一用本地投影／EPSG:2263 并正确换算英尺。

五个小 bbox 共取得 1,770 个轮廓对象；最终四区相交轮廓分别为 150、123、147、118，合计 538。保留 bbox 外延出的完整几何有助于边缘遮挡；覆盖率按统计边界裁切后、轮廓合并面积计算，不能把对象数当建筑栋数。

可用作平面障碍。不能辨认所有围墙、脚手架、围栏、树篱、雨棚、穿楼通道或巷道通行权；楼间空地也未必公众可达。二层连廊和高架结构不能一律作为地面封堵。高度可作视觉辅助，本轮不依据高度推导风场。

## 4. NYC Street Centerline

来源：[CSCL / inkn-q76z](https://data.cityofnewyork.us/d/inkn-q76z)。实查为 `the_geom`（MultiLineString）、`physicalid`、`full_street_name`、`street_name`、`streetwidth`、`rw_type`、`segment_type`、`trafdir`、`nonped`、地址范围、`from_level_code` / `to_level_code` 等。五个 bbox 共 230 个 segment；四个最终范围相交 segment 分别为 29、29、43、32。

CSCL 是 road-bed representation，分隔车道等会形成多个段，不能把每条线围成的面直接当完整城市 block。最终街块边界用 OSM 街道网络识别，CSCL 用于交叉核对街名、转角和街道结构。路宽字段存在也不能代替 sidewalk/open-space 面；本轮没有验证其完整性与单位，因此不将其直接用于精确路缘或通行空间重建。

## 5. NYC 数据使用与保存范围

NYC 三项数据按 [NYC Open Data Technical Standards / Public Policies](https://cityofnewyork.github.io/opendatatsm/publicpolicies.html)及 NYC.gov 条款使用；不擅自标为 CC0。公开可访问不代表市府担保完整性、精度或适用性。后续作品应注明机构、数据集、投诉时间窗、获取日期、裁切和艺术化处理。

`research/` 保留历史选定区域的必要来源点、元数据、统计与边界，以及当前 SoHo 的复现输入；边界是调查数据，不是旧版地图输出。保留请求 ID 以便核查，不保存举报人信息或推测身份。清理后复现说明和接口失败记录见 `research/README.md`。
