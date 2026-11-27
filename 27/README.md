# Day 27 / New Tool — Among the Giants

当前交付：[合成 PNG](outputs/among_the_giants.png) · [分层 PSD](outputs/among_the_giants_layers.psd) · [同画布透明 PNG 图层包](outputs/photoshop_layers.zip)。1800×2520 竖幅，署名 Ming Cao。只作本地预览，未更新 gallery、commit 或 push。

## Photoshop 微调

直接打开 `outputs/among_the_giants_layers.psd`。21 个独立图层包括天空、山体、参考步道、候选点、入口标记、每株主树/每组林丛、标题、图例、注释和署名。五个古画拼贴各一层，可单独移动、缩放或调整不透明度。

同时提供 `outputs/photoshop_layers/` 和 ZIP 备份。所有 PNG 均为 **1800×2520、同原点 (0,0)、8-bit RGBA**；不要逐层裁边、自动对齐或缩放。文件编号为从下到上：00 天空，20 署名；Photoshop 图层面板顺序相反。可在 Photoshop 的 File > Scripts > Browse 中运行解压目录内的 `load_png_layers.jsx`，按正确顺序建立图层堆栈。

PSD 里的文字是独立像素层，以保持与预览精确一致。若要改字，在 Photoshop 运行 `outputs/make_text_editable.jsx`：它打开 PSD，隐藏原像素文字，创建真正可编辑的文字层。检查字体度量后另存；该可选脚本未在 Photoshop 应用内实测。字号、英文文案、Georgia / Segoe UI、颜色、基线与对齐方式同时保存在 `editable_text.json`。原 PSD 不会被脚本自动覆盖。

`outputs/psd_validation.json` 记录核验：重新打开 PSD 后，各层可见像素、alpha、名称、尺寸与原点均与 PNG 一致；从 PSD 逐层重建与交付 PNG **逐像素相同**。PSD 自带兼容预览有最多 1/255 的合成舍入差异，不是位置偏移。没有声称已在 Photoshop 应用内打开测试。

## 构图、地形与光照

按用户选择改为竖幅。保持 **315° 方位 / 42° 俯角**，横向世界视野从 900 m 拉远 5% 至 **945 m**；竖向视野为 1323 m，parallel scale 661.5。增加的画幅高度用于同时保留原山顶轮廓和入口，而不是进一步拉近。相机焦点沿画面右向仍偏移 28.42 m、上向改为 225 m。参数在 `camera_portrait.json`，此前恢复机位仍保存在 `camera_restored.json`。

D18 为只读输入：

- `../18/oblique/scene_mesh_epsg3826.npz`：原 1804 个顶点、3440 个面片，以及 `track_segments_xyz`、`track_segment_part`、`tree_xyz`、`tree_numbers`。
- `../18/oblique/composition_dem_30m.tif` 与 `composition_dem_source.json`：D18 已有的 5.4×6.0 km、200×180 像元扩展真实 DSM。没有联网重取地形。
- `../18/oblique/camera_c.json`：原世界目标 `[294300,2733845,1707.492919921875]`。
- `../18/research/data/official_communication_points.geojson`：游客中心通讯标示点，第275行。Entrance / Visitor center 指游客中心一侧接近入口，不等于售票口实测坐标。

地形仍是 **Copernicus GLO-30 DSM，名义 30 m**，含林冠；EPSG:3826 / EGM2008。仅在内存中向西、北方向追加扩展 DSM 中的真实前景网格，保留原远景轮廓。原顶点和原面片数组保留为扩展网格的前段，重叠高程逐点一致，差值 0。未简化、平滑或捏造原几何；面片绕序仅在 VTK 渲染副本中反转以使用正确正面光照。所有三维图层统一减去原目标并施加 1.2×垂直夸张。没有地形遮罩、羽化、模糊、留白带或填造白角；**底边及两个底角的真实地形 alpha 覆盖率为 100%**。上方露出的天空由真实渲染轮廓决定。

先渲染两版 600×840 低分辨率光照，并检查加入相同路线和树木后的对照，见 [A/B 对比](review/lighting_comparison.png)。选 **A**：环境光 0.77、漫反射 0.25、侧光 `(-1700,300,1600)`、specular 0；浅灰绿、低反差，沟谷比上一版明亮，原坡面法线仍能表达山脊与坡向。B 版沟谷反差更强，未采用。只用标准差0.45的微弱颗粒作视觉表现，不增加地形信息。

## 步道、候选点与分层遮挡

步道沿既有赋高线段绘制，不重排、不平滑、不补连接、不吸附树位，保留原部分及每条边的端点顺序。显示上移1 m，暖赭色线宽5.5 px是显示宽度，不表示实际路宽。候选点仍为15处，半径统一2.5 m，显示上移2 m；13号冲突及缺失编号不补造。

`scene_layers.py` 使用共同相机和地形深度分别输出步道、候选点与入口的透明图层。地形在图层提取通道中仍写深度，但不写可见颜色；低于地面40 m的测试球可见像素为0，确认图层没有把埋在山后的对象透视显示。输出采用直通 alpha，并处理 VTK 抗锯齿边缘的预乘颜色。

主树参照 **候选1** 的投影落脚，脚部作 `(28,-8)` px 的艺术微调；新增曲树参照候选16附近，疏树组参照候选5附近。候选坐标只定位巨木活动范围，不把拼贴画形、树高或物种解释为这些候选树的实测属性。具体投影、树脚、偏移、透明度和图层位置在 `outputs/photoshop_layers/layer_manifest.json` 及 `render_report.json`。候选源XYZ未改动；拼贴树是二维艺术图层，不声称与地形存在三维遮挡关系。

## 实际古画局部与图档授权

核对日期：2026-11-27。均为实际古画扫描局部，沿轮廓与墨色密度生成透明蒙版，去掉绢地、统一绿黑墨色；不生成或重绘仿古树，不用矩形框或引线。图上标注 “Tree collage from classical ink paintings”。

| 画作、作者与馆藏 | 实际文件与使用条款 | 本版使用的局部 |
|---|---|---|
| 郭熙《树色平远图》 / Old Trees, Level Distance，约1080年，The Metropolitan Museum of Art，1981.276；Gift of John M. Crawford Jr., in honor of Douglas Dillon, 1981 | [馆藏页](https://www.metmuseum.org/art/collection/search/39668)，Public Domain；[实际 DP167812_CRD.jpg](https://images.metmuseum.org/CRDImages/as/original/DP167812_CRD.jpg)，3508×1872；[Met Open Access 政策](https://www.metmuseum.org/policies/image-resources) 对此类图档采用 **CC0**，可复制、改作及商业/非商业再利用。官方 API 元数据 `isPublicDomain=true`，下载URL相符。 | 保留近景曲干主树；新增画心右侧偏斜曲树，以及亭阁左侧的疏树组。三处各自一层，姿态与浓淡不同。 |
| 马远《高士观瀑图》 / Scholar viewing a waterfall，13世纪早期，The Metropolitan Museum of Art，1973.120.9；Ex coll.: C. C. Wang Family, Gift of The Dillon Fund, 1973 | [馆藏页](https://www.metmuseum.org/art/collection/search/40086)，Public Domain；[实际 DP154090.jpg](https://images.metmuseum.org/CRDImages/as/original/DP154090.jpg)，3407×3000；同样适用 Met **CC0**。官方 API 元数据 `isPublicDomain=true`。 | 新增原画左侧斜出的松干与针叶局部，置于左侧前景边缘。原画该树本就出画，保留其入画姿态，不补画截断部分。 |
| 董源《潇湘图》 / Xiao and Xiang Rivers，五代，故宫博物院（北京），新00147099 | [馆藏核对](https://www.dpm.org.cn/collection/paint/234585.html)；实际采用 [Commons 文件页](https://commons.wikimedia.org/wiki/File:Xiao_and_Xiang_rivers.jpg) 对应的 [8475×3000 JPG](https://upload.wikimedia.org/wikipedia/commons/b/b3/Xiao_and_Xiang_rivers.jpg)，2019-08-20 Eugene a 上传的高分辨率版本。该文件标记 **Public Domain Mark / PD-old-100-expired**；不是页面文本的 CC BY-SA，也不声称故宫另行授予了图档改作许可。 | 保留原画左侧近岸林丛局部，缩小、淡化后置于右侧远坡。 |

`assets/sources/` 保存实际下载源图、Met API JSON、Commons 文件说明页、source_manifest.json 与授权核对记录。准确裁切坐标、轮廓多边形、增益、透明度及 SHA-256 在 `assets/cutouts/extraction.json`。`prepare_collage.py` 可重新生成五个独立去背局部；每株/每组另存为一张与成图同原点的整画布图层，方便 Photoshop 调整。

## 运行与核验

Windows PowerShell，仓库根目录：

```powershell
uv --cache-dir 27/.uv-cache venv 27/.venv --python 3.14
uv --cache-dir 27/.uv-cache pip install --python 27/.venv/Scripts/python.exe -r 27/requirements.txt
& 27/.venv/Scripts/python.exe -B 27/prepare_collage.py
& 27/.venv/Scripts/python.exe -B 27/render.py
```

`render.py` 调用 `build_layers.py`，依次输出光照试样、透明图层、合成预览、分层PSD、验证和ZIP。`scene_layers.py` 负责三维几何及深度通道；`export_psd.py` 负责8-bit PSD及回读验证。字体读取 `C:/Windows/Fonts/`。依赖版本固定在 requirements.txt，包含 rasterio 和 psd-tools。未修改 D18；运行前后直接输入 SHA-256 相同。

已打开1800×2520原图与390×546缩略图：山顶完整、底角无网格白边；淡墨坡谷可读，主树曲干与新增松枝可辨，主要步道可从入口顺线阅读。两版带拼贴的低分辨率光照也已对照。细小来源注释需读原尺寸。未把 Photoshop 应用内验证或原生文字层支持说成已完成；PSD层数据和合成对齐已实际回读核验。

## 地理数据授权限制

沿用 [D18 NOTICE](../18/NOTICE.md)、[sources](../18/research/sources.md) 与 [Copernicus 许可证](../18/terrain/sources/License-COPDEM-30.pdf)。完整地形署名：

produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.

The organisations in charge of the Copernicus programme by law or by delegation do not incur any liability for any use of the Copernicus WorldDEM-30.

候选点 © OpenStreetMap contributors，ODbL 1.0；原ID和证据保留于D18，位置未经现场验证。游客中心是官方通讯标示点，并非实测入口。

Reference GPS track 来自 Taiwan Outdoors 链接的2024-08-02游客GPX，非权威完整步道网。第三方再发布许可未确认；本地PNG、PSD及含轨迹的图层仍仅作用户指定的讨论预览。公开再利用前须确认相关条款。古画图档的开放状态不改变GPX授权限制。
