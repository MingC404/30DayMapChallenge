# Day05 — Seeing New York from the Water

当前版本为**三层纸景式视差动画**。视觉基础是原认可稿 `seeing_new_york_waterfront.png/.svg`，未使用 `lookout_02_refined` 或 `lookout_03_refined` 的画面。保留纯白背景、海洋配色、舒展水面、简洁地标名称和角落定位图，署名 Ming Cao。

## 输出

- **[短 GIF](outputs/seeing_new_york_paper_parallax.gif)**：1560 × 900，144 帧，9.6 秒，约 3.5 MB。
- **[静态合成预览](outputs/paper_parallax_preview.png)**：2600 × 1500，为完整平移的起始状态。

| 独立透明图层 | PNG | 可编辑 SVG | 速度比 | 完整平移量 |
| --- | --- | --- | ---: | ---: |
| 后层：浅蓝灰远景 | [PNG](outputs/paper_parallax_back.png) | [SVG](outputs/paper_parallax_back.svg) | 0.3 | 向左 108 px |
| 中层：深海蓝地标与连接体块 | [PNG](outputs/paper_parallax_middle.png) | [SVG](outputs/paper_parallax_middle.svg) | 0.6 | 向左 216 px |
| 前层：中浅蓝沿岸低层 | [PNG](outputs/paper_parallax_front.png) | [SVG](outputs/paper_parallax_front.svg) | 1.0 | 向左 360 px |

图层 PNG 均为 **3400 × 1500 RGBA**；SVG 使用 `viewBox="-400 0 3400 1500"`。左右各准备 400 px 画外余量；PNG 中原画布 x=0 对应 x=400。三层不含固定标题、水面或小地图。中层包含地标名称及引线，二者与建筑一起移动。SVG 是原生路径及可编辑文字，没有嵌入位图。

## 纸景构成与运动

从原认可稿提取 70 Pine Street、One World Trade Center、Woolworth Building 的轮廓、尖顶和标签；去掉立面细线与折面颜色，形成三个单次出现的深海蓝识别剪影。每个地标仅出现一次，没有镜像或复制填补边缘。

城市背景与画外延伸复用已缓存的下曼哈顿建筑几何及高度，在固定参考视点下投影一次。扩展取样范围，用原局部数据补足画外上下文；未下载新数据。艺术分层使用约 1097 个背景体块、15 个分散选择的低层连接体块、120 个近岸低层，合并并简化为连续纸层。底部补齐为同一层的连续纸面，顶部轮廓仍取自这些建筑，未随机生成高楼。

前层最高处控制在画布 y=875 以下，三个地标顶部均在它之上；前层可遮住塔身下部，不会在平移过程中长期遮住顶部。层间叠放是艺术构图，不是逐像素真实空间深度；与上一轮几何遮挡图的目的不同。

时间安排：**8 秒单次匀速向左平移 + 0.8 秒建筑层淡出 + 0.8 秒复位后淡入**。三个位移轨迹为同一线性进度乘以各自幅度，速度比例严格为 0.3 / 0.6 / 1.0，不往返倒放。淡出到完全透明时复位；水面、水平线、标题、来源、署名和定位图均不参与淡出或平移。

定位图保留原认可稿的参考位置、航线和方向扇区，标注 **REFERENCE LOOKOUT 03**；船点固定，不暗示真实航行。地标起始位置继承原稿，其动画位移不再代表随航线变化的真实方位、距离或可见性。

图内注明：**“An interpretive skyline · Three-layer parallax, not a simulated voyage.”**

## 重建与核验

```powershell
python3.14.exe 05/scripts/build_paper_parallax.py
```

依赖 Pillow、NumPy、Shapely、pyproj，以及 Windows Arial / Georgia 字体；复用现有只读 `02/.deps`。脚本只使用缓存数据与认可稿，无需联网，不会重写认可稿。参数、输入哈希、图层尺寸与时间信息见 `data/paper_parallax_manifest.json`。

已检查起始、中间和末尾画面；验证整段平移的画外支撑连续、三层 PNG 带透明通道、SVG 无嵌入位图、地标没有重复。解码 GIF 核验 144 帧共 9600 毫秒，所有帧的标题、水面、小地图和来源区域保持不变；循环末帧与首帧一致，纯白背景有独立调色板色值。

此前的认可版及双视点试验保留供比较，本轮不覆盖。上一轮方法记录另存于 `outputs/approved/README_comparison.md`。不改 Day01–04，不 commit / push。

## 来源

- 建筑轮廓、高度：[NYC OTI / NYC Open Data BUILDING](https://data.cityofnewyork.us/City-Government/BUILDING/5zhs-2jue)，局部缓存 `data/lower_manhattan_buildings.geojson`；查询、时间和哈希见 `data/building_sources.json`。
- 陆地：[NYC DCP Borough Boundaries，26b](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne)，复用项目简化轮廓。
- 参考航线：[NYC Ferry Developer Tools](https://www.ferry.nyc/developer-tools/)，已有官方 GTFS 与 `data/view_context.geojson`；路线在本动画中不驱动相机或船点。
- 地标坐标：Wikidata [Q11245](https://www.wikidata.org/wiki/Q11245)、[Q262041](https://www.wikidata.org/wiki/Q262041)、[Q217652](https://www.wikidata.org/wiki/Q217652)。
- 原稿识别造型参考：[Skyscraper Museum — 1 WTC](https://www.skyscraper.org/supertall/building/one-world-trade-center/)、[NYC LPC — 70 Pine](https://s-media.nyc.gov/agencies/lpc/lp/2441.pdf)、[Skyscraper Museum — Woolworth](https://old.skyscraper.org/EXHIBITIONS/TEN_TOPS/woolworth.php)。本轮直接复用并概括原稿，不生成或嵌入照片。
