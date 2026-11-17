# Day 16 — OSM geometry replacement review

**结果：按用户第 7 条停止，未执行正式几何替换，未重新导出 PNG 或 GIF。** 当前证据不能同时满足“只用可确认的 OSM 几何”与“保留旧图全部服务范围”。未画猜测接线、未从旧 NJT 线形描摹／吸附，也未仅修改署名冒充 OSM。

现有 `outputs/day16_njt_disruptions.gif` 与 `.png` **仍是旧 NJT GIS 几何版本**，不是 OSM 替换成功的新版本，原来的发布 HOLD 不变。

## 1. 固定内容与实际变更

未访问或重新抓取 NJ Transhit；未运行 `clean_notices.py`，未重算、清理或分类 234 条代表通知；未运行绘图脚本。`data/processed/` 的全部 8 个文件、两个绘图脚本、原 PNG/GIF 与 animation manifest，共 13 个冻结文件，SHA256 均与本轮开始前一致。

因此原因统计、配色、布局、字体、地图范围、UTM 18N 投影、州界、9 帧与 17.5 秒动画参数均未改变。

本轮新增：

- `data/gis/osm/relations/*.osm`：15 份通过 relation ID 核验的 OSM API 完整关系响应，含成员 ways/nodes；未成为正式渲染输入。
- `data/gis/osm/parents_*.osm`、`route_parents.osm`：服务主关系及成员归属证据。
- `data/gis/osm/nec_old_history.osm`：核查旧 NEC 索引已删除，避免使用过期关系。
- `data/gis/osm/initial_geometry_comparison.json`：单个 relation 的标签、版本、覆盖距离与具名停靠节点候选。
- `data/gis/osm/group_geometry_comparison.json`：按已有服务组组合后与旧 GIS 的量化比较。
- `data/gis/osm/frozen_baseline.json`、`replacement_status.json`：冻结校验与停止状态、来源 URL、版本、保存时间和 SHA256。
- `scripts/review_osm_sources.py`：受限范围的公开关系发现查询；本机 Overpass 请求未能完成，不能将失败响应解释为“没有数据”。
- `scripts/compare_osm_geometry.py`：仅作 GIS 覆盖比较，**不读取代表通知作重新分析，不导出供正式图使用的混合几何**。

原 `rail_lines.geojson`、`rail_stations.geojson`、两个绘图脚本和正式图面均未被替换或重写。旧 NJT 几何只在本地比较脚本中读取，不用来补充 OSM 成员、改造轨道走向或生成所谓 OSM 版。

## 2. OSM 发现与验证方式

最初参考 [OSM New Jersey Mass Transit Relations 索引](https://wiki.openstreetmap.org/wiki/New_Jersey/Mass_Transit_Relations)，但逐个读取当前公开 API 的实际成员，而不把索引里的旧状态当作事实。完整关系访问形式：

```text
https://api.openstreetmap.org/api/0.6/relation/RELATION_ID/full
```

旧索引的 NEC relation `1380577` 返回 HTTP 410；其公开历史确认 version 90 在 2019-12-19 已删除。之后通过当前 NEC route master `9795466` 找到方向关系 `9795464` 与 `9795465`，已经解决这一旧索引问题。**NEC 不是因为过期 ID 而被判定不存在。**

组合服务关系依据当前 OSM 的明示成员：

- [Main & Bergen County route master 2641820](https://www.openstreetmap.org/relation/2641820) 包含 Main `1377995`、Bergen County `1377997`、Port Jervis `1190915`。
- [Morris & Essex route master 10441055](https://www.openstreetmap.org/relation/10441055) 包含 Morristown `1377998` 与 Gladstone `1377996`。
- [NEC route master 9795466](https://www.openstreetmap.org/relation/9795466) 包含 New York→Trenton `9795464`、Trenton→New York `9795465`。
- [NJCL route master 10441056](https://www.openstreetmap.org/relation/10441056) 本次响应仅列出 `207401`。
- [RVL route master 10441058](https://www.openstreetmap.org/relation/10441058) 本次响应仅列出 `1122386`。

关系标签与实际几何不能混同：Bergen/Main 的 `to=Port Jervis` 不代表单个 relation 的 way 成员就完整延伸至 Port Jervis；加入 master 明示的 Port Jervis relation 后才补齐。相反，Meadowlands 的起点标签虽写 Secaucus，实际 way 成员包含 Hoboken。该项起初被误列为疑点，**成员检查后已排除**，不作为停止理由。

本机无法连接 Overpass 主端点，另两个公共镜像超时。因此当前发现并不是完整、穷尽的 OSM 服务关系检索。可以确认下表中的关系及其成员，但不能把未找到的服务变体写成“OSM 中绝不存在”。没有绕过访问限制或使用登录资源。

## 3. 覆盖与匹配结果

比较方法：将两个来源各自投影到原图 EPSG:32618。OSM 仅读取明确关系的 `railway=rail` 成员，不把站台、废弃线等自动当作运营铁路；按既有服务组组合。以旧线形长度中落在 OSM 几何 100 m／250 m 范围内的比例作为**单向空间覆盖诊断**。

该比例不是数据正确率，不表示端点、拓扑与服务语义已全部通过；旧 GIS 本身也可能有站外延伸或历史服务范围。OSM 可能包含多股平行轨道，线路总长度不能与旧简化中心线直接相等。没有利用这些缓冲区去吸附、描摹或补画 OSM 轨道。

| 既有服务组／背景 | 核查的 OSM relation | 100 m 覆盖 | 250 m 覆盖 | 结论 |
|---|---|---:|---:|---|
| ACRL | [206515](https://www.openstreetmap.org/relation/206515) | 100.00% | 100.00% | Philadelphia—Atlantic City 主体吻合 |
| MBPJ | [1377995](https://www.openstreetmap.org/relation/1377995)、[1377997](https://www.openstreetmap.org/relation/1377997)、[1190915](https://www.openstreetmap.org/relation/1190915) | 100.00% | 100.00% | 组合后 Main／Bergen／Port Jervis 范围吻合；不能只用单个关系 |
| MNE | [1377998](https://www.openstreetmap.org/relation/1377998)、[1377996](https://www.openstreetmap.org/relation/1377996) | 100.00% | 100.00% | Morristown／Gladstone 组合吻合 |
| MOBO | [1377999](https://www.openstreetmap.org/relation/1377999) | 100.00% | 100.00% | 主体及 New York／Hoboken 连接覆盖 |
| NEC | [9795464](https://www.openstreetmap.org/relation/9795464)、[9795465](https://www.openstreetmap.org/relation/9795465) | 97.34% | 97.59% | New York／Trenton 有明确服务关系；旧几何约 2.315 km 位于 250 m 范围外，仍需逐段解释，不能直接补线 |
| **NJCL** | [207401](https://www.openstreetmap.org/relation/207401) | **93.05%** | **93.43%** | **Hoboken 接入差异未解决** |
| PVL | [2641819](https://www.openstreetmap.org/relation/2641819) | 100.00% | 100.00% | Hoboken—Spring Valley 主体吻合 |
| **RVL** | [1122386](https://www.openstreetmap.org/relation/1122386) | **82.11%** | **82.28%** | **Newark—New York Penn 延伸差异未解决** |
| 背景 Princeton | [196612](https://www.openstreetmap.org/relation/196612) | 99.68% | 100.00% | 小尺度端点差异，未自动保留旧端点 |
| 背景 Meadowlands | [2641818](https://www.openstreetmap.org/relation/2641818) | 100.00% | 100.00% | 实际成员覆盖旧 Hoboken 接入，非阻碍 |

### 两个不能靠猜测解决的服务范围问题

**NJCL：** relation 的明示服务为 New York Penn—Bay Head；实际几何可覆盖 Newark Penn、New York Penn 与 Bay Head，但距旧 Hoboken 枢纽约 **2.945 km**。旧 NJCL 约 **7.598 km** 的几何落在该关系 250 m 范围外，涉及旧图中对 Hoboken 接入的表达。本次 master 未提供另一条明确的 Hoboken 变体关系。其他线路在相邻轨道上存在，并不足以把它们的路径自动归入 NJCL。

**RVL：** relation 标签明示 Newark Penn—High Bridge，实际也覆盖这两个端点，距旧 New York Penn 约 **14.399 km**。旧 RVL 约 **15.830 km** 的几何位于 250 m 范围外。不能为了保持旧图效果，将 NEC 或其他服务的 Penn 接入段直接复制到 RVL；那会新增未经核验的服务归属。

这些不证明旧 GIS 或 OSM 谁“必然错误”，而是当前 service group 定义与来源覆盖并不一致。将它们强行做成旧图同样高亮范围，已经超出“只换来源、不要猜测”的授权。

## 4. 枢纽候选与未完成事项

实际关系成员已找到一些可追溯的 OSM 对象：

| 旧标注语义 | OSM 候选 | 当前核验程度 |
|---|---|---|
| New York Penn Station | node `895371274` | 明示 railway=station / public_transport=station |
| Newark Penn Station | node `2051677435` | 明示 station |
| Hoboken Terminal | node `7024801771` | 明示 station |
| Secaucus Junction | 多个 stop_position 成员，例如 `6615178658` | 需进一步确定单一站点／站组参考对象，未随意取平均或套用旧坐标 |
| Trenton | stop_position `299183385`、`1401177251` | 已发现停靠对象，尚未最终选定站级参考点 |
| Philadelphia 30th Street | stop_position `3426249723` | 明示停靠位置，不自动等同原站级中心 |
| Atlantic City | stop_position `762246639` | 候选未切换到成品 |

轨道服务范围已未通过替换门槛，因此本轮没有继续把不完整的站点候选拼成正式站点文件。没有把 stop_position、station 与 stop_area 当作同一几何语义，也没有在新 OSM 站点文件中偷偷保留旧 NJT 坐标。

## 5. 视觉一致性与输出状态

**不能声称 OSM 版最终 GIF 与旧版基本一致，因为没有生成 OSM 版。** 地理覆盖诊断显示，多数服务组有很好的空间对应，但 NJCL、RVL 直接切换后会改变受影响服务高亮范围；NEC 尚有局部剩余差异。保留旧段、随机补线或仅改署名都不可接受。

两个现有成品校验值未变：

- GIF：`9eb94e1b05288c054f3e7eb3f8fec126ca541bd1182f2c487fd5ab32adbccde5`
- PNG：`faa80ab82fb9c6e375d222ef3556d2d4ae1ab3bfc881cbf46690165c7dd40222`

这只表示旧文件被完整保留，**不是 OSM 替换完成的证明**。旧图仍须按 NJT GIS 来源和旧的许可 HOLD 对待。

## 6. 如果后续通过映射门槛，OSM 的署名与数据义务

OSM 的许可是明确的：[OpenStreetMap copyright](https://www.openstreetmap.org/copyright)、[ODbL 1.0 正文](https://opendatacommons.org/licenses/odbl/1-0/)、[OSMF Attribution Guidelines](https://osmfoundation.org/wiki/Licence/Attribution_Guidelines)。但“许可明确”不能替代对线路归属的核验。

真正替换完成后，图面应明确写 **Rail & hubs: © OpenStreetMap contributors**，提供可读的 `openstreetmap.org/copyright` 地址；README 同时链接 ODbL。PNG/GIF 无法自行提供普通可点击超链接，不能只把全部许可信息藏在一个可能不随图转发的文档里。现有图没有切换来源，故本轮**没有将图面 NJT 署名改成 OSM**。

ODbL 区分数据库与制成的图片：公开 Produced Work 需要来源／许可告知；若它来自公开使用的 Derivative Database，则该衍生数据库涉及同许可与可获取义务。按 §4.4、§4.6，应提供适用的机器可读衍生数据库，或完整改动／生成方法，并保留通知，在线提供不得收费。投影、筛选、组合后的 OSM-only 轨道与站点数据，不能仅以“只发布 PNG”规避这项检查。

落实时应把 **OSM 几何数据**与 **NJ Transhit 通知统计**分开记录、分开打包：OSM-only 导出及其生成方法按适用 ODbL 条款提供，通知全文和旧 NJT 几何不混入其中。不能把 ODbL 简化为“所有原创画面和独立统计都必须改成 ODbL”，也不能把通知数字错误署名为 OSM。

以上是后续实现要求，本轮未公开发布候选数据库或成品，也没有形成“已满足全部 ODbL 发布义务”的结论。

## 7. 仍未解决的发布问题与下一步条件

1. **几何映射未完成。** 需要可验证的 OSM NJCL Hoboken 服务变体与 RVL Penn 接入依据，并解释 NEC 的局部范围差异；之后才能在不改统计和设计的前提下替换。
2. **枢纽对象尚未全部选定。** 尤其需区分 Secaucus 等站组、站点与停靠节点的角色。
3. **旧 NJT GIS 许可问题尚未被消除。** 当前成品仍使用旧几何，所以不能因本轮下载了 OSM 就撤销该项 HOLD。
4. **NJ Transhit 依然是通知统计来源。** 其适用数据使用条款／聚合发布依据问题不因地图底图更换而自动消失；没有重新抓取或上传正文。
5. **ODbL 发布义务未进入执行阶段。** 只有几何通过、真正生成 OSM 成品之后，才可核查图面署名、许可链接与 OSM-only 衍生数据提供方式。

本轮依照用户明确的停止条件结束。未改 Day 01–15，未 commit、push 或发布；未请求或代发第三方消息。继续工作所需的是补齐上述映射证据，而不是允许猜线或将旧几何改名。
