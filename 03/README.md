# Day 03 — Inside the Park

当前版本：[三座 JC 公园横排 PNG](outputs/inside_the_park_jc.png)，3600 × 2380 像素。

1. Hamilton Park
2. Lafayette Park
3. Berry Lane Park

三张主图分别放大至适合阅读内部空间的尺度，保留最初横排版的 1100 × 1280 像素绘图区；不压缩主图来容纳定位图。各图北向上、不拉伸几何，各自有按米计算的准确比例尺。它们不用于直接比较公园的真实面积大小。底部 JC 定位图使用灰白陆地、水域和淡灰街道，根据公园边界质心的真实坐标落点，灰色圆形编号通过引线避让，与标题 1–3 对应。街道复用已有 OSM 缓存。

## 数据与表示

本轮全部复用缓存，没有新增下载或数据审计。公园边界和内部 OSM 数据来自：

- `data_raw/day03_playgrounds/three_panel_background_osm.json`：三座公园边界。
- `data_raw/family/jersey_city_osm_map_4_1.xml`：Hamilton Park 原始 OSM map 缓存，只读使用。
- `data_raw/day03_playgrounds/activity_spaces/lafayette_map.osm`、`berry_lane_map.osm`：公园及紧邻范围的原始 OSM map 缓存。
- 定位图陆地：已有 US Census 2024 Cartographic Boundary 1:500000 派生缓存 `outputs/selection/jc_land_background.geojson`，仅作概化背景，不能用于精确岸线判读。

延续此前分类色：playground、sports、water play、grass、dog area；步道以线表示。球场类型依据 OSM sport 标签。游泳池与戏水区不是同一类型。只有记录了实际几何和相关标签的对象才被绘制；不依据肉眼或名称补造用途分区，普通草地不被推断为儿童训练场。

未着分类色的公园区域保持未分类，不代表没有活动或设施。缺失标签不代表设施不存在。Hamilton Park 边界内未找到明确草地面；Lafayette Park 邻近的泳池、球场在本次公园边界之外，未作为园内分区绘制。内部步道仅在公园范围内强调，外围道路作淡背景；原始缓存未被裁切或改写。

Rittenhouse Square 与 Clark Park 暂不出现在当前图中，已下载的原始数据继续保留。旧五公园、早期全市 playground、三片区试排的结果及专用绘图过程已清理；共享原始数据和后续版本依赖的数据处理脚本保留。

## 复现

从项目根目录运行：

```powershell
python3.14 03/scripts/inside_the_park_jc.py
```

依赖 Pillow、Shapely、pyproj；本机只读复用 `02/.deps`，脚本可离线运行。主图和定位图采用以 Jersey City 为中心的 WGS84 局部等距投影，单位为米；主图 x/y 使用相同缩放。

署名 Ming Cao；来源 OpenStreetMap contributors、US Census（定位图）。本轮不做交互、评分、额外审计；不修改 Day01/02，不 commit/push。
