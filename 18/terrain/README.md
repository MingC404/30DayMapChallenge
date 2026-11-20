# 真实地形获取与首版分析

日期：2026-11-19。原有 `18/research/` 未改写，本轮文件单独保存于 `18/terrain/` 与 `18/preview/`。

## 20m DTM 获取排查

本次实际请求的状态保存在 `sources/*.headers`、`moi_probe_log.json` 中：

| 检查 | 结果 | 可支持的判断 |
|---|---|---|
| 2026 桃园 DTM ZIP 的尾部 Range | 403，134-byte HTML 正文 | 没有获得 ZIP 字节；不是有效高程数据。 |
| 2025 官方目录中的桃园 ZIP | 403 | 改用旧版县市包仍未解决。 |
| 官方 `schema_hdr.zip` | 403 | 路径不含汉字，错误并非只由中文编码造成。 |
| `https://www.tgos.tw/` 主页 | 同样 403 | 拒绝至少不限于某个 ZIP 或 Range 请求；不能将其简单解释成文件不存在。 |
| 政府开放资料平台另一 DTM 目录 | 200，有效 CSV | 官方目录仍可获取，链接仍进入 TGOS。 |
| 官方 opdadm 小型 SHP 资源对照 | 200，有效文件 | 非本环境所有台湾政府下载均受阻。对照请求 Range 未生效，取得314437-byte索引，无全国地形大包。 |
| 旧官方 `tgos.nat.gov.tw` 主机 | curl 6，DNS 失败 | 不能作为可用备用入口。 |

另外查看了[内政部 DTM 平台](https://dtm.moi.gov.tw/)：20m 开放与分析服务登录/API key 是不同问题，不能把 API 分析图像当成原始高程。未注册账号、申请受管制高精度资料、绕过登录、使用地区代理或执行未经授权的下载。

**403 的直接原因仍然只可确认到“请求在 TGOS 分发入口被拒绝”。** HTTP 正文及 `via: 1.1 google` 没有提供细分原因；该头也不足以证明哪一层执行了地理过滤。[moidemd 维护者的台湾/日本/美国区域对照](https://github.com/outdoorsafetylab/moidemd#建置環境)支持地域过滤解释，但本次只有一个出口，没有服务器日志或第二地域的独立测试，不能把推断写成已证实事实。

通过[官方其他 DTM 数据集入口](https://data.gov.tw/dataset/175239)成功取得 `moi_alternate_catalog.csv`，实际为 2025 目录。其县市包仍指向同一 TGOS 主机，实测未解决。没有继续下载全国大包。由于已有合法且足够本轮构图使用的替代源，转而取得 GLO-30。

## 实际使用的数据

- 产品：**Copernicus DEM GLO-30 Public，AWS 公共 COG 分发，registry 标注 2021 release**。不是最新 CDSE 版本的保证。
- [数据分发说明](https://registry.opendata.aws/copernicus-dem/)；[原始 COG 说明](https://copernicus-dem-30m.s3.amazonaws.com/readme.html)。页面副本已存于 `sources/`。
- 实际文件：`Copernicus_DSM_COG_10_N24_00_E121_00_DEM/Copernicus_DSM_COG_10_N24_00_E121_00_DEM.tif`。
- [直接源 URL](https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/Copernicus_DSM_COG_10_N24_00_E121_00_DEM/Copernicus_DSM_COG_10_N24_00_E121_00_DEM.tif)。源对象全长 36,927,113 bytes；文件头小请求返回 **206 Partial Content**。后续使用 GDAL `/vsicurl` 读取研究窗口所需 COG 块，**未下载整幅源文件**。块大小意味着网络传输量会大于最终小裁片；没有将裁片字节数冒称为实际网络流量。
- 原始 CRS：**EPSG:4326**，1/3600°×1/3600° 网格。纬向约31m、此纬度经向约28m，产品标称30m；不是20m。
- 垂直基准：**EGM2008（米，正高）**，依据[产品官方规格](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM)。未转换为 TWVD2001；不能与台湾 DTM 高程做未经基准处理的精确差值。
- 数据语义：**DSM**，包括树冠及其他地物表面。林区的局部高程、山脊和小谷可能有植被影响，不能解释成裸地微地形。
- 格式：Float32 GeoTIFF。原始研究窗口裁片 `copernicus_glo30_native_aoi.tif` 保留本次源网格的真实采样值；`dem_acquisition.json` 保存请求地址、窗口、源分辨率、裁剪参数和 SHA-256。
- 授权：COP-DEM-GLO-30-F / Free & Open，可复制、组合、改作与传播，须保留指定署名、责任说明等要求。已保存许可证原文，并在 PNG 与 [NOTICE.md](../NOTICE.md) 中提供对应说明。无须 AWS 账户。

## 范围与分析参数

预览矩形 EPSG:3826：**E293250–295050，N2732900–2735300**，即1.8×2.4km，覆盖巨木群、游客中心侧与周围山体。这是研究视窗，不是官方游乐区界，也不声称覆盖拉拉山山顶。

计算矩形：**E292950–295350，N2732600–2735600**，即2.4×3km、7.2km²。视窗每边多300m，避免梯度和邻域计算在显示边界截断。源窗口再多取数个像元，随后以 bilinear 重投影到 **EPSG:3826、30m**，100×80个像元。没有上采样成20m，没有填补 NoData；本研究框重投影后无缺值。

| 产物 | 参数与含义 |
|---|---|
| `dem_glo30_tm2_30m.tif` | 米制分析表面；数据来源仍是GLO-30 DSM。 |
| `hillshade_nw.tif` | 315°方位、38°太阳高度，计算前Gaussian σ0.65像元抑制单格噪声。 |
| `hillshade_multidirectional.tif` | 315°权重0.5，270°与45°各0.25，同为38°太阳高度；没有垂直夸张。 |
| `contours_20m.geojson` | 在未平滑的30m投影DSM上 marching squares，**20m是等高距，不是空间分辨率**；100m主曲线。WGS84输出，每条记录EGM2008基准。 |
| `tpi_150m.tif` | 轻微平滑后的DSM减去Gaussian σ150m邻域均值；正值为局部相对高处，负值为局部相对低处。 |
| `ridge_candidate_mask.tif` / `valley_candidate_mask.tif` | TPI阈值±12m、坡度>4°后骨架化；去除小于5格的连通斑块。 |
| `ridge_valley_candidates.geojson` | 骨架链候选线，不是实测山脊，不是水文河网，也不表示常年有水。必须结合地形与其他资料人工解释。 |
| `elevation_distribution.csv` | 计算框30m格点，50m高程分箱、面积和百分比；不是树高分布或官方园区面积统计。 |
| `terrain_diagnostics.pdf` | 四幅分析图：DSM、multi-hillshade、TPI及候选结构、高程直方图。 |

模型结果表明视窗中有明显坡谷与相邻山体结构，可支持真实俯视青绿山水表达。山脊/谷地解释采用相对高度的候选结构，未画出未经证实的河流。不能据这些结果推断小尺度树根、栈道坡折或精确排水线。

计算框表面高程约 **1287.9–2127.5m**，均值1717.9m，中位数1719.0m；5–95百分位1435.1–2014.2m。显示窗约 **1345.3–2077.4m**。高值属于附近山体和地物表面，不以视窗最大值重新定义“拉拉山峰高”。具体浮点统计以 `analysis_summary.json` 为准。

## 预览绘制与位置限制

PNG来自米制DSM、高程设色与multi-hillshade，纸纹仅为图面材质，不进入地形分析。显示分辨率的放大只为绘图，不能带来更精细的地形信息。地形没有旋转、透视变换或垂直夸张；北向及比例尺有效于同一平面投影。

等高线显示采用40m辅线并叠加100m主线；分析文件保留完整20m等高距。已减少复杂数字标签，保留概略高程提示。谷地留白和淡墨是视觉处理，不是 NoData 或新增虚构山形。

GPX直接读取已有研究的 `public_track_20240802.geojson`，不补线、不移动、不平滑改线。原始驻留漂移在图中仍可见。OSM只使用 `tree_inventory_1_24.csv` 中候选数为1的15行：1、2、3、4、5、6、7、8、12、14、15、16、19、20、21。13号冲突点排除，其他编号不补齐。小圆圈锚点不移动，15号短斜线表示倒木。游客中心侧的文字仅描述接近段；没有将官方通讯标示点充当树干。

## 复算

`scripts/acquire_dem.py`：网络读取小范围COG并保存源裁片。`scripts/analyze_terrain.py`：保留科学分析与诊断PDF，不再制作废弃二维PNG。正式三维艺术入口为`../oblique/render_art.py`。原`validation.json`、`provenance_manifest.json`与研究哈希基线是当次获取/分析的历史证据，其中废弃图面脚本已按清理计划移除，不应将历史manifest当作当前文件列表。

依赖隔离在 `.deps/`（已忽略），使用Python 3.14.2。主要版本为 rasterio1.5.2、numpy2.5.5、scipy1.18.1、scikit-image0.26.0、matplotlib3.11.2、Pillow13.0.0。中文字体为Windows本地 `kaiu.ttf`，英文字体Georgia。复算用解释器：`E:/MUSA/650 deep learning with python/vision-EO/.venv/Scripts/python.exe`。

运行获取脚本需要网络；分析和验证仅使用本地文件。复算无需重新运行旧研究脚本，也不会改写旧研究结果。
