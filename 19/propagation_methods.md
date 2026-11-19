# Day 19 — The Invisible Streets：建筑约束传播方法

> 历史方法调查。当前原型继续使用推荐算法，但区域与交互已改为 SoHo 双来源比较；实现和验证见 [README.md](README.md)。

建议采用 **建筑障碍网格 + 开放空间加权最短路径距离场 + Marching Squares**。它能在浏览器中形成绕建筑、沿街道转角延伸的有机轮廓；鼠标和源点选择可驱动轮廓变化。这里是空间约束的艺术化传播示意，**不是 CFD、气象预测、实测浓度或真实扩散距离**。本轮只有方法调查，没有实现正式地图或性能实测。

## 三种方法比较

|方法|轮廓与互动|数据需求|计算量与性能预期|主要局限|
|---|---|---|---|---|
|A. 开放网格上的加权 Dijkstra 距离场|阈值边界沿可达路径绕角；源点切换、半径和方向偏好可交互|建筑 mask、源点、米制网格；街道作低成本偏好，可选开放空间到障碍的距离场|二叉堆约 O(N log N)，每个源／成本设置更新时重算；静态场可缓存，轮廓约 O(KN)|是可达距离，不是流体；单纯阈值易显均匀，需要克制的艺术调制|
|B. 带障碍的简化扩散／衰减 PDE|逐步渗透与淡出更像液体；鼠标可扰动注入或方向|同上，加时间步、扩散系数、衰减、边界条件；风向若没有观测只能称艺术参数|每步 O(N)，每秒多步；小网格 CPU Worker 可尝试，较大网格考虑 WebGL ping-pong|参数无实测标定；扩散受 CFL 稳定条件约束，易跨墙泄漏或出现数值伪影|
|C. 开放空间导航网格／街道图上的最短路径，再生成可变宽廊道|沿中心线形成分叉、拐角和带状形；选择源点响应快|建筑差集、可通行空间／navmesh，或 CSCL 图；需几何清理和路口连接|路径搜索依图规模约 O(E log V)，图通常远小于像元网格；廊道并集和裁切可能较贵|仅中心线会忽略广场与楼间缝；铺成管道感强，路宽及巷道通行数据不足|

本阶段优先 A：最容易保证“不穿建筑”，同时支持连续不规则边界。B 是后续强化动态质感的方案；C 可用于低性能设备的降级模式。Marching Squares 只是从标量场提取边界，**自身不实现遮挡**。

## 推荐方案 A：实施设计

### 1. 建立空间与障碍

将选定五街块及约 100–150 m 计算边缘转成米制坐标。建筑 footprint 合并并检查有效性，栅格化为不可通行 mask；保留洞，但不默认建筑内 courtyard 与街道连通。初版网格取 **2 m**；对关键狭缝局部检查 1 m，移动端可降到 3 m。窄于网格的通道可能丢失，不能用视觉噪声人为打穿。

楼体是已知障碍；非建筑区域只可称“模型开放空间”。私有院落、围墙和关闭通道没有数据时不应画成已确认的公共路线。若后续补入围墙或构筑物，需保留来源；高架、连廊和架空结构按地面通行语义处理，不能简单填满地面。

为防栅格漏角，走斜向边时要求对应两个正交邻格都开放；更严格可检查整条边是否与建筑相交。障碍边缘可做半格保守膨胀，但须核查是否误封真实窄缝。建筑 mask 与障碍距离场只需在范围或分辨率变化时重算。

### 2. 处理源点不确定性

311 地址点或 OSM way 中心可能落在楼体内部。原始点永久保留；只为计算向附近可达街缘生成投影点，并记录偏移距离和方式。建议超过 20 m 的移动标记人工复核，无法可靠投影的源不参与传播。不能把投影点称为店门、排气口或井盖，也不能直接穿过建筑连接源点。

潜在香气 POI 和历史投诉分别形成可选择图层；垃圾、公共便溺保持“代理线索”标签。室内投诉默认不生成室外场。同地址多次请求可用于显示历史频次，但不能据频次赋予真实排放强度。

### 3. 计算开放空间成本与路径距离

对开放像元建立 8 邻接图，建筑像元不加入图。对边 i→j 定义：

`w(i,j) = 边长 × 开放空间成本 × 可选方向偏好`

所有成本为正。街道附近可设成本 1，其他模型开放空间设 1.3–2；这些是视觉参数。开放空间到建筑的距离场可用来调整窄缝／宽阔区域的相对阻力，但不能把它当作真实风速。不要用“到源的欧氏距离”代替路径距离，否则会穿墙。

用 Dijkstra 从源计算 `D(x)`，封闭且不可达区域保持无穷大。示意强度可取 `I(x) = A × exp(-D(x)/L)`；A、L 都是艺术参数，没有浓度单位。多源可以取 max 以保留源的归属；若采用 sum，需明确是视觉叠加。初版同时激活 1–3 个源，避免每个 POI 都算独立场。

### 4. 有机边界与平滑

对 I 场设置 3–5 个阈值，由 [d3-contour](https://github.com/d3/d3-contour) 的 Marching Squares 提取多层轮廓。低幅连续噪声可调制强度或局部成本，增加不规则性；不能改变障碍连通性。轮廓的圆滑／模糊必须最后再与开放 mask 相交；否则曲线平滑或跨楼 blur 会重新穿墙。不要直接对源画圆形 buffer，也不要使用只能沿视线遮挡的 viewshed。

最稳妥的平滑是对标量场做障碍感知的邻域平滑，再提取等值线。若保留柔光，柔光同样受 mask 裁切。由一个场插值到另一个场时保持建筑像元为 0，不对相隔的多边形顶点直接 morph，避免跨楼跳变。

### 5. 鼠标与源点选择

选择已有 POI／投诉：优先加载缓存场，约 200–350 ms 交叉淡入。鼠标在开放空间移动：可将其作为明确标注的“探索扰动点”，影响方向偏好、扩散阈值或视觉注入；不能把鼠标点显示成新增公开记录。

轻量方案是鼠标只改变已缓存场的阈值／展示层次，轮廓变化不必重新搜索。若鼠标改变传播源或成本，则在 Worker 以 10–15 Hz 节流计算，并丢弃过期任务；鼠标在建筑上时吸附到可达开放像元或不更新。渲染与强度过渡由 requestAnimationFrame 驱动，不能每一帧对所有源全量 Dijkstra。

## 性能预算与验证要求

推荐区约 0.049 km²；加计算边缘后，按约 600 × 600 m 的包络估算，2 m 网格约 **90,000 像元**，1 m 约 360,000。每个 Float32 场约 0.36 MB / 1.44 MB；6 个场约 2.16 MB / 8.64 MB，另加 mask、堆、邻接和轮廓内存。应按隐式网格访问邻居，不为每个像元创建 JS 对象。

2 m 网格、1–3 个活动源、静态 mask 与缓存距离场在现代浏览器中具有实现可行性；**尚未实测，不能承诺 60 fps 或每次更新小于某固定毫秒**。建议验收目标：主线程绘制帧预算约 16.7 ms；Worker 单次重算争取 100 ms 内，超出则降分辨率或采用缓存场。移动端须独立测量。Worker 可避免搜索阻塞 UI，参考 [MDN Web Workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers)。

若升级 B，显式四邻域纯扩散满足 `D × dt / h² ≤ 1/4` 的稳定性要求；加入平流后还要满足相应 CFL 条件。建筑两侧使用零通量／断邻接，不把楼体值置零后仍允许跨楼双线性采样。GPU 采样也必须检查障碍。视觉上的快速流动可用纹理／透明度动画实现，无需伪造现实物理时间。

下一阶段只需做针对性验证：L 形街道是否真正绕角、封闭院落是否保持不可达、斜角相邻建筑是否漏流、源点在楼内时投影是否可追溯、边界外是否可合理绕行、轮廓平滑后是否侵入建筑，以及快速鼠标移动是否出现过期结果覆盖。当前没有正式地图，以上是实现验收条件。

## 解释边界

该方法把二维开放空间视为艺术化传播介质。没有真实排放量、实时经营状态、风场、湍流、温度、湿度、化学反应、三维建筑通风或人体感知阈值。它适合表达“街道空间可能如何组织看不见的流动”，不能据此判断某店污染邻居、某街块现在有臭味、某条投诉仍持续，或用动画幅度比较健康风险。

## Final implementation: one fluid, separate evidence

The sections above record the original feasibility recommendation. The final SoHo implementation uses one cursor-driven geometry field and a separately cached evidence field. Explore Smells retains its actual-record previews and up to two pinned records; Explore Space has no warm/violet submodes or fixed reference source.

The metric grid is 2 m, with every building-intersecting cell blocked. Eight-neighbor weighted Dijkstra allows a diagonal step only when both orthogonal neighbors are open. A 110 m geometry-only context margin permits paths beyond the visible study boundary. Source coordinates remain unchanged on the map; computational starts may snap to open space within 20 m, with the offset disclosed. All 30 current records qualify (maximum offset about 8.9 m).

The Worker caches 12 roots and the main thread retains up to 18 results. Cursor requests are limited to one in flight and approximately one every 40 ms; only the latest desired position is retained. New distances transition over approximately 120 ms. A four-neighbor root-connected support filter removes detached remnants, then Marching Squares traces the single outer boundary. Contour updates are throttled to approximately 32 ms in Explore Space and 65 ms for actual-record previews. Spread transitions over approximately 320 ms. Geometry, interpolation, fills and outlines remain clipped to the building mask and study boundary; no cross-wall blur is applied. Moving into a building or leaving the map preserves the last valid position.

### Evidence normalization

Evidence origins are deduplicated within each class at projected coordinates rounded to 0.01 m: 18 OSM origins and 10 distinct report coordinates from 12 complaints. Neither record frequency nor raw counts are added. For each class independently:

`W(x) = max_i K(D_i(x)) = K(min_i D_i(x))`

`K(d) = exp(-d/58) * (1 - (d/150)^2)^2` for `d < 150`; otherwise zero.

Two multi-source Dijkstra searches therefore suffice at initialization. Each class has unit peak. These artistic weighted-path budgets are not validated odor travel distances or comparable physical measurements. Duplicate reports at one coordinate do not strengthen its color.

Hue mixes amber RGB (233,168,79) and violet (121,81,178) by `V/(A+V)`. Confidence is `max(A,V)`: values at or below 0.12 remain neutral RGB (182,181,175); saturation rises smoothly between 0.12 and 0.6. Evidence colors are cached independently of the cursor and Spread. No purple is fabricated where report evidence is zero. The single geometry field controls opacity and support, rather than overlaying two independently generated clouds.

Building highlights sample evidence on adjacent open cells within 4.5 m of footprint edges, only where the fluid is present. This is cartographic emphasis, not propagation into buildings. The conservative grid may close narrow gaps; model-open space is not necessarily publicly accessible. There is no physical conservation law, wind, emissions or three-dimensional transport model.

### Reproduction and verification

`node 19/scripts/rebuild.mjs` uses retained local inputs; `--refresh` intentionally updates the small study snapshot. The collector pipes temporary OSM XML in memory and overwrites selected outputs. Export uses `scripts/export_media.py` and the same app renderer through `index.html?art=1`; `artwork.mjs` contains composition and street-route sampling, not a duplicate propagation algorithm. A complete unwritten pre-roll precedes capture; temporary frames and palettes are automatically removed on success or failure. The final manifest records the 210-frame route, shared-source hashes, stationary annotations, zero blocked support and exact PNG/GIF frame identity.

Run `node 19/tests/core.test.mjs`, then `node 19/tests/browser.cjs` with the local server running. Browser checks cover real-record interactions, source growth, evidence deduplication, connected rendered support, neutral areas, no mask leaks, rapid cursor movement, held positions, reset and mobile overflow. Tests save no screenshots or animation frames.
