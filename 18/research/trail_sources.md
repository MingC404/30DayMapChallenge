# 巨木群步道来源与可行性

复核日期：2026-11-20。完整的来源比较、节点距离及局部拓扑统计见 [trails_feasibility.md](trails_feasibility.md)；此处为本轮研究入口。GIS 沿用 2026-11-19 原始快照，未补画线。

| 来源 | 已取得几何 | 适用性与限制 |
|---|---|---|
| [林业保育署园区页](https://recreation.forest.gov.tw/Forest/RA?typ=0&typ_id=0200005)的2026-04导览图 | JPG示意图，无已验证的官方全网络矢量下载 | 可核对24个编号、分支和游程；不能当作测量路线直接描摹定位。官网称完整游程约4km。 |
| [OSM 局部地图 API](https://api.openstreetmap.org/api/0.6/map?bbox=121.430,24.706,121.445,24.715) | `data/osm_pedestrian_ways.geojson`，14条步行way；原XML在sources | 开放再利用的主几何候选，© OpenStreetMap contributors / ODbL。未知测量精度，需核对支线及现况。 |
| [Taiwan Outdoors](https://taiwanoutdoors.com/hiking/lalashan-national-forest/)链接的[公开GPX](https://drive.google.com/file/d/1bVygQYIaeDWBmjvAJsWfG5LvUPoaCP1A/view) | `data/public_track_20240802.gpx/.geojson`，1491点，单段 | 2024-08-02游客轨迹；约5852.50m含往返及漂移，不等于净路网长度；再发布许可尚未确认。 |
| [健行笔记列表](https://hiking.biji.co/index.php?act=gpx_list&keyword=%E6%8B%89%E6%8B%89%E5%B1%B1&q=trail) | 线索，未作为第二条下载实录 | 不能将列表存在视为已获取或可再利用的独立验证。 |

局部框 `[121.432,24.708,121.4435,24.713]` 的 OSM 网络有205节点、206唯一边、2个连通分量、3个独立环，约3336.74m。原始way引用节点完整，但不代表全部官方支线完整；分析边界也会影响分量。不能自动吸附或连接几何交叉来消除断点。

官方通讯点包括游客中心、1号、休憩区、5号观景台、岔路、达观亭、15号旁路牌、19号、21号、24号支线。GPX到这10个点的距离均约9m以内；OSM在游客中心及24号支线较弱，分别约48.20m及25.56m。它们说明接近程度，不能当作中心线误差。详细数据见 `data/trail_control_point_distances.csv`。

必须区分售票管理站、游客中心步道入口、桥、休憩平台和福巴越岭管制口。尚需逐段核对游客中心接近段、24号终端、13号附近分岔，以及9–11、17–18、22–23等所有分支，建立“官方拓扑边—GIS线段”对应表。4km游程、3.3km步道全程及GPX累计里程的口径不同，不能为匹配数字而缩放路线。

**结论：已取得可用线几何，能够作为连贯路网的研究基础；尚未验证完整、可信且可公开再利用的全支线网络。** 以OSM为主、官方图检查拓扑、GPX寻找疑似漏段；保持来源分层，不凭示意图补造精确路径。静态几何不证明开放通行，当前福巴越岭停开公告也不能用来删除真实地理线段。
