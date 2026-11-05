# Day05 — Seeing New York from the Water

当前版本：**下曼哈顿水岸横向局部**，2600 × 1500，署名 Ming Cao。纯白背景、深海蓝地标、浅蓝灰城市体块与海蓝水面。

- [PNG 预览](outputs/seeing_new_york_waterfront.png)
- [可编辑 SVG](outputs/seeing_new_york_waterfront.svg)：原生矢量，无嵌入位图；地标、城市体块、近岸建筑、水面、标签、小地图分别分组。Georgia / Arial 文字可编辑，替换字体后需检查文字宽度。
- [绘图脚本](scripts/build_waterfront.py)

## 当前视段与方法

复用原第 3 号观察点 **-73.997881669, 40.703903390**，距 Wall St/Pier 11 选段起点约 832 米。它是航线上的示意位置，不是实测拍摄点。观看窗口收拢为 **275°–330°**，朝向下曼哈顿。Brooklyn Bridge 在约 33.75°，留作后续片段。

| 地标 | 真方位角 | 官方建筑 DOITT_ID | 屋顶高度，米 |
| --- | ---: | --- | ---: |
| 70 Pine Street | 288.758806° | 671705 | 249.26 |
| One World Trade Center | 307.434696° | 1114961 | 429.27 |
| Woolworth Building | 317.205958° | 401853 | 237.74 |

横向统一使用 `x = 80 + (方位角 - 275) / 55 × 2440`；地标锚点未移动，顺序未调整。

仅获取下曼哈顿局部建筑框：经度 -74.024 至 -73.996、纬度 40.700 至 40.722，共 **2,323 个要素**。按视角、距离、要素类型与有效高度筛选，使用 **881 栋真实建筑**；4 个建筑要素因高度缺失或非正被排除。没有随机补楼，也没有进行全市审计。

背景由真实轮廓按单一屋顶高度拉伸，再根据各顶点的方位角、距离与高程投影，按距离由远至近绘制。近岸低层叠加到地标底部，形成沿岸前景。屋顶字段不包含实际退台或精细屋面，因此背景为**数据驱动的简化体块，并非准确天际线**。三个地标沿用可靠参考中的识别特征，减少窗户与立面线，并强调显露；绘制顺序不等于精确遮挡结果。

纵向按相对视线的仰角计算，固定 30 像素/度；横向约 44.36 像素/度，即纵向统一压缩约 0.676 倍，以适应横幅。假设模型眼高 **6 米**，不是实测船舶参数。1 WTC 的识别尖顶参考约 541.3 米总高，70 Pine 参考约 290.2 米总高，Woolworth 冠部作少量图形概括；这些细部不等同于屋顶字段测量结果。

岸线按同一观察点和窗口的射线，与官方 NYC 陆地轮廓首次相交后投影到视平面，交点距离约 **284–468 米**；没有贴入俯视岸线。岸边窄色带是简化表达，水位以模型零面近似，不模拟潮汐、码头或精确岸壁高度。前景水面只加少量波纹。定位图放在右下角，标出航线、观察点和当前观看扇区。

图内说明集中为一行：**Local footprints + roof heights · Simplified landmark crowns · Not a surveyed skyline or visibility model.**

## 数据与参考

- **建筑**：[NYC OTI / NYC Open Data BUILDING](https://data.cityofnewyork.us/City-Government/BUILDING/5zhs-2jue)。[官方字段说明](https://github.com/CityOfNewYork/nyc-geo-metadata/blob/main/Metadata/Metadata_BuildingFootprints.md)：HEIGHT_ROOF 为地面以上屋顶高度，单位英尺，脚本换算为米。局部缓存为 `data/lower_manhattan_buildings.geojson`，查询 URL、时间及 SHA-256 见 `data/building_sources.json`，字段说明另有缓存。获取时间为 **2026-11-04 美东时间 / 2026-11-05 UTC**；不是实地确认日期。
- **陆地**：[NYC DCP Borough Boundaries，26b](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne)，复用 `data_raw/boundaries/nyc_boroughs_simplified.geojson`，2026-11-02 获取，15 米简化。
- **航线**：[NYC Ferry Developer Tools](https://www.ferry.nyc/developer-tools/) 的 [官方 GTFS](https://nycferry.connexionz.net/rtt/public/resource/gtfs.zip)，本地包 `data/nycferry_gtfs.zip`，版本 20261103。ER / shape 9 前四个顶点形成约 1.04 公里 Wall St/Pier 11 → DUMBO 选段；运营方路线几何不是某次实测船迹。
- **坐标**：[1 WTC / Q11245](https://www.wikidata.org/wiki/Q11245)、[70 Pine / Q262041](https://www.wikidata.org/wiki/Q262041)、[Woolworth / Q217652](https://www.wikidata.org/wiki/Q217652)，原始实体 JSON 留在 `data/`。Wikidata 结构化数据为 CC0。
- **造型**：[The Skyscraper Museum — 1 WTC](https://www.skyscraper.org/supertall/building/one-world-trade-center/)；[NYC LPC — 70 Pine，LP-2441](https://s-media.nyc.gov/agencies/lpc/lp/2441.pdf)；[The Skyscraper Museum — Woolworth](https://old.skyscraper.org/EXHIBITIONS/TEN_TOPS/woolworth.php)。采用原创简化识别轮廓，没有生成或嵌入照片。

## 重建与整理

```powershell
python3.14.exe 05/scripts/build_waterfront.py
```

依赖 Pillow、Shapely、pyproj，复用现有只读 `02/.deps` 和 Windows 字体。输入已缓存，重建不联网。仅刷新建筑数据时运行 `05/scripts/acquire_waterfront.py`，需要联网，并更新局部数据和来源清单。

`data/view_context.geojson` 保存原航线、三个观察点、四个地标坐标和来源，供后续延展。`data/render_manifest.json` 保存筛选计数、投影参数、建筑匹配与地标锚点。

清理了被替代的两张 PNG、一份旧 SVG、旧方位 CSV、旧锚点 JSON、两个旧绘图脚本、字段试探样本、未用的桥梁原始实体 JSON 和占位文件。原 `outputs/sight_geometry.geojson` 移至 `data/view_context.geojson`。**outputs/ 只保留当前 PNG 和 SVG**；保留重建与来源核验所需的数据和脚本。

已重建并目视检查 PNG；核验 SVG XML、矢量分组、地标方位、建筑匹配及输入数据哈希。未制作 GIF，未修改 Day01–04，未 commit / push。
