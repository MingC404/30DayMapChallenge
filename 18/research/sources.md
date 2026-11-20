# 来源、访问状态与再利用说明

访问日期均为 2026-11-19。本地原始资料位于 `sources/`；`source_manifest.json` 记录保留文件的字节数与 SHA-256。文件保存表示研究取证，不表示该网站所有插图或游客轨迹均已获得最终地图的再利用许可。

| ID | 来源与直接链接 | 保存的证据 | 结果 / 权利 |
|---|---|---|---|
| T1 | [MOI 2026 DTM 数据集](https://data.gov.tw/dataset/178729) | `dtm_2026_catalog.csv` | 免费，政府资料开放授权条款第1版。CSV 仅为目录。网页下载项误标 DSM，须以实际文件复核。 |
| T2 | [CSV 原始资源](https://opdadm.moi.gov.tw/api/v1/no-auth/resource/api/dataset/B6219841-E247-4743-958D-77FB61067092/resource/D788C60B-33CB-4A84-A438-EC6E8B7060F1/download) | 同上，已下载 | 目录包含桃园、新北等分幅包与全国包；未获取全国包。 |
| T3 | [桃园县市分幅 ZIP](https://www.tgos.tw/MDE/VirtualDir_TC/Product/6c64edb5-09e8-4d5a-8a15-ea5a77440d48/%E5%88%86%E5%B9%85_%E6%A1%83%E5%9C%92%E5%B8%8220MDEM%282026%29.zip) | `taoyuan_range_retry.headers`、`taoyuan_range_retry.bin` | 尾部 Range 请求 403；bin 为 HTTP 错误正文，**无高程值**。 |
| T4 | [分幅头文件 schema ZIP](https://www.tgos.tw/MDE/VirtualDir_TC/Product/342505d1-81bc-490a-8e10-9f7e1ec0ed98/schema_hdr.zip) | `schema_hdr_http403.html` 与原 headers | 403，未取得格式定义；特意不保留成 `.zip` 以防误认有效包。 |
| T5 | [DTM 加值平台](https://dtm.moi.gov.tw/) / [Swagger JSON](https://dtm-openapi.colife.org.tw/swagger/v1/swagger.json) | `dtm_openapi.json` | 20m 开放；1m 管制。API 路径含 api_key。未调用任何影像生成接口。 |
| T6 | [官方供图平台 FAQ](https://applydtm.moi.gov.tw/FAQ.php) | `dtm_faq.html` | 说明高精度资料受管制及身份/项目申请，不等于公开开放数据。 |
| T7 | [官方 5000 参考索引 121 分带](https://data.gov.tw/dataset/115926) / [直接 SHP ZIP](https://opdadm.moi.gov.tw/api/v1/no-auth/resource/api/dataset/0265D8AF-27A9-42B7-B302-4B5962DCC4FF/resource/85F8C9C7-12BC-4A44-948E-BD4BDBE75918/download) | `nlsc_5k_index.zip`，314437 bytes；内含 SHP/SHX/DBF/PRJ/CPG | 政府资料开放授权条款第1版；提取 017/018 参考框。不是 2026 DTM 有效像元索引。 |
| T8 | [ODC 10m 产品页](https://twodc.colife.org.tw/products/dem_10m_taiwan) | `odc_10m.html` | 页面 footprint 不覆盖拉拉山；排除。没有下载 10m DEM。 |
| T9 | [moidemd 维护者说明](https://github.com/outdoorsafetylab/moidemd) / [取数源码](https://github.com/outdoorsafetylab/moidemd/blob/master/scripts/fetch-dem.py) | `moidemd_readme.md`、`moidemd_fetch_reference.py` | 原始数据格式、TGOS 地理限制的外部直接测试证据；未运行其全国数据下载程序。引用的代码 BSD-3-Clause，不把代码许可证误写成地形数据许可证。 |
| F1 | [官方拉拉山园区页](https://recreation.forest.gov.tw/Forest/RA?typ=0&typ_id=0200005) | `official_park.html` | 编号、游程、图件链接。园区统一 POI 经纬度不能当逐树坐标。 |
| F2 | [2026-04 单张导览图](https://recreation.forest.gov.tw/Files/Forest/RA/DM/0200005/%E6%8B%89%E6%8B%89%E5%B1%B1%E8%B7%AF%E7%B7%9A%E5%9C%B0%E5%9C%96B4_20260331%20.jpg) | `official_224.jpg` | 原始官方参考 JPG，未改作或生成地图。示意地理，非量测底图。 |
| F3 | [2026-04 折页正面](https://recreation.forest.gov.tw/Files/Forest/RA/DM/0200005/%E6%8B%89%E6%8B%89%E5%B1%B1%E6%91%BA%E9%A0%81%E6%8E%92%E7%89%88_%E5%AE%8C%E7%A8%BF_%E6%9E%97%E6%A5%AD%E4%BF%9D%E8%82%B2%E7%BD%B2_11504_1.jpg) / [背面](https://recreation.forest.gov.tw/Files/Forest/RA/DM/0200005/%E6%8B%89%E6%8B%89%E5%B1%B1%E6%91%BA%E9%A0%81%E6%8E%92%E7%89%88_%E5%AE%8C%E7%A8%BF_%E6%9E%97%E6%A5%AD%E4%BF%9D%E8%82%B2%E7%BD%B2_11504_2.jpg) | `official_225.jpg`、`official_226.jpg` | 树种、倒木标记和游程。未核验图像作者/委托创作的独立授权；后续宜重新设计自己的符号而非复制官方插画。 |
| F4 | [树龄鉴定官方公告 2023-04-12](https://recreation.forest.gov.tw/News/News?id=20230412001) | `official_age_20230412.html` | 2022 调查的部分新属性，作为表内数值来源。 |
| F5 | [官方通讯点表，11502](https://www.forest.gov.tw/UserFiles/001/Images/web/communication_11502.pdf) | PDF、提取 TXT，表第6页275–284行 | 官方公开坐标；对象是通讯标示牌，非树干测量成果。公开内容使用仍需依网站开放宣告核对，不能把 DTM 许可自动套用。 |
| F6 | [官方历史研究报告 2008](https://www.forest.gov.tw/file/18599) | 仅链接；不保留整份约17MB报告 | 历史树龄、胸围等线索；不用于填补最新调查字段。 |
| G1 | [OSM 查询框 API](https://api.openstreetmap.org/api/0.6/map?bbox=121.430,24.706,121.445,24.715) / [版权与许可](https://www.openstreetmap.org/copyright) | `osm_api_bbox.osm` 及响应头 | © OpenStreetMap contributors，ODbL 1.0。树位、路径均保留 OSM id 和源标签。衍生数据库/地图须依实际用途遵守署名及适用条款。 |
| G2 | [Taiwan Outdoors 文章](https://taiwanoutdoors.com/hiking/lalashan-national-forest/) / [其链接的 GPX](https://drive.google.com/file/d/1bVygQYIaeDWBmjvAJsWfG5LvUPoaCP1A/view) | `taiwanoutdoors.html`、`public_gpx_download_response`（实际为有效 GPX XML） | 下载无需登录，1491点，2024-08-02实录。不是官方资料；再利用许可未确认。 |
| G3 | [健行笔记另一条巨木步道记录](https://hiking.biji.co/index.php?act=gpx_detail&id=1146679&q=trail) | 仅链接 | 备选线索；未作为实测比较数据。 |

下载过程中的 Overpass 主站返回 406、备站超时，随后改用 OSM 官方小范围 `/api/0.6/map` 成功获取。失败正文已移到 `osm_overpass_error.html`，没有作为 JSON 解析。官方网站部分 TLS 证书被 Python 3.14 的严格链校验拒绝，改用 Windows `curl.exe` 成功取资料；没有关闭证书验证。对 TGOS 的 403 原样记录，没有伪装成下载成功。

其余搜索曾发现全球 30m 模型、地形图衍生产品及民间完整旧树龄表，没有把它们当作更精细开放 DTM 或最新官方树位。未使用 Google Maps 商业地图坐标批量推断树位，未进行示意图地理配准或坐标补造。
