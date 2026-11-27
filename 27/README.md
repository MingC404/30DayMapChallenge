# Day 27 / New Tool — Among the Giants

## 最终文件：以 Photoshop 手调 PSD 为准

- [最终 PNG](outputs/among_the_giants_final.png)：1800×2520，全尺寸RGB。
- [加浓并增加山顶雾带的 GIF](outputs/among_the_giants_summit_mist.gif)：900×1260，120个时间采样，每个120 ms，14.4秒，无限循环；三片雾均为最上层水平移动，边缘高度羽化。
- [保留的手调 PSD](outputs/among_the_giants_layers.psd)：Photoshop于2026-11-27 16:26保存的版本，保留原文件及全部图层可见性、顺序、蒙版、透明度和混合设置，本轮未写入PSD。
- [低清 GIF 预览](review/final_animation/mist_preview.gif)：360×504，与正式版使用相同参数。

静态图直接读取Photoshop保存的全尺寸合并RGB，未用旧PNG图层堆栈重建。最终PNG与该合成逐像素相同，差值为0。此PSD的额外全零通道不是合并图透明度；使用 `psd_tools.topil()` 读取RGB，避免普通RGBA解码后的全透明问题。未转换RGB通道值；PSD未嵌入ICC配置，PNG也未擅自添加或转换配置。当前树木、瀑布、山脊与留白均以这份手调PSD为准。

动画将三片雾统一叠在最终PNG最上方，固定各自高度，只从左向右水平移动，从画外进入并淡出。山顶雾带中心位于全尺寸画布y=560，另两片保持y=950和1830。本次只进一步放宽山顶雾的羽化：纵向尺度由180增至270，横纵羽化再乘1.18，并以柔和渐变避让标题；其他两片雾参数保持不变。雾在整张画布上直接计算多个高斯团块及其宽幅纵向羽化，使用自然衰减的长尾，不使用有限矩形贴图，也没有旋转、斜向漂移、地形遮挡或树木镂空蒙版。原山体、步道、树木、瀑布和文字的位置与几何保持固定。标题及底部署名通过雾的高度与衰减范围避让，像素核对差值为0。使用统一256色GIF调色板且不抖动；雾外像素保持一致。GIF的256色量化只用于GIF，PNG保留全RGB颜色。

山顶雾的颜色匹配原图天空纸色（RGB 240,240,232），避免在天空中出现额外白色轮廓；另外两片雾的颜色和其他参数保持不变。本次还修正了水平画布坐标与云团中心变量重名覆盖的问题；横向高斯形状现在使用独立的 `screen_x` 网格，并验证横向透明度确有空间变化，避免退化成全宽均匀条带。最终PNG和手调PSD均保持原哈希。

复现最终导出（只读PSD，不渲染三维场景）：

```powershell
& 27/.venv/Scripts/python.exe -B 27/export_saved_psd.py
& 27/.venv/Scripts/python.exe -B 27/animate_final_mist.py
# 检查低清预览后：
& 27/.venv/Scripts/python.exe -B 27/animate_final_mist.py --final
```

`animation/mist_parameters.json` 保存尺寸、帧数、水平速度、固定高度、随机种子、相位、颜色及浓淡。当前动画不再读取任何保护区或留白导向蒙版。动画帧仅在内存生成，不保留临时帧。PSD哈希、保存状态和静态逐像素核对见 `outputs/final_static_validation.json`；GIF尺寸、时长、循环、固定高度及文字区域检查见 `outputs/final_gif_validation.json`。

静态和动画验证后，仅按具体路径清理无读取依赖的旧检查图、未采用的低清原画下载、下载检查文件和过时PNG图层ZIP，共13个文件、6.43 MiB；完整路径及删除前哈希见 `review/final_cleanup_report.json`。保留全部脚本、所需输入、树木/瀑布/山脊素材、清晰地形原层和来源授权说明。仍被历史脚本或README引用的旧PNG图层堆栈及预览先保留；它们不再代表手调成品。

上一次动效重做清理30个文件、13.15 MiB，记录见 `review/mist_revision_cleanup.json`；其中记录的旧GIF后来又由当前最上层水平羽化版本替换。旧预览的Markdown链接已改为历史清理说明；原画、实际去背素材、相机配置、皴纹计划、必要静态合成蒙版和清晰地形原层仍保留。

本轮继续清理被替换的GIF、不再读取的动画保护/导向蒙版、PSD元数据副本和检查拼图，共6个文件、10.82 MiB；逐路径记录见 `review/horizontal_mist_cleanup.json`。当前动画只需最终PNG、手调PSD用于哈希核对，以及动画脚本和参数，不再额外保留云雾贴图或蒙版。

**以后请打开上方最终PNG、GIF和手调PSD。下文为手调前的制作历史，旧 `outputs/among_the_giants.png`、`layer_manifest.json` 和旧PSD重建脚本不能还原手调状态；请勿用旧重建脚本覆盖手调PSD。** Gallery已按用户要求加入本地预览；commit和push未执行，D18继续只读。

## Gallery description

I used PyVista to render the terrain of Lalashan, Taiwan, and traced the giant-tree trail across its slopes. Trees and waterfalls collaged from classical Chinese paintings bring the landscape into dialogue with the terrain model, while drifting mist reveals and conceals the ridges.

古画拼贴素材｜[《早春图》](https://digitalarchive.npm.gov.tw/opendata/Pub/Detail/47?dep=P&mode=full)、[《树色平远图》](https://www.metmuseum.org/art/collection/search/39668)、[《双松平远图》](https://www.metmuseum.org/art/collection/search/40508)、[《江渚风林图》](https://www.metmuseum.org/art/collection/search/41154)、[《素庵图》](https://www.metmuseum.org/art/collection/search/39550)、[《潇湘图》](https://www.dpm.org.cn/collection/paint/234585.html)、[《松阴飞瀑图》](https://www.metmuseum.org/art/collection/search/45778)  
Collaged in Photoshop.

By Ming Cao. 本地条目为 `docs/index.html#day-27`，位于D26与D28之间。公开资源仅为 `docs/assets/27/among_the_giants.png` 和 `among_the_giants.gif`，分别逐字节复制自手调PSD导出的最终PNG与最新云雾GIF；PSD和工作图层留在27目录。GIF为正常展示，PNG为减少动态效果和加载失败时的静态回退，也可单独下载。运行 `27/update_gallery.py` 更新此条目，运行 `node 27/check_gallery.cjs` 进行本地浏览器验证，不部署、不commit或push。

上述7幅作品已逐项对应到手调PSD中12个可见古画图层，核对画布内裁切、蒙版、透明度和上层遮挡后仍有可见贡献；发表版PNG与PSD保存合成一致，GIF仅叠加程序云雾。来源原图哈希、去背记录、图层名称与可见像素核对见 [collage_source_audit.json](review/collage_source_audit.json)。备用的马远《高士观瀑图》、仅检查过的唐寅画作及范宽等早期参考均未列入gallery补注。同一作品的复制、缩放或多个局部只记一次。

<a id="data-sources"></a>

## Gallery data sources

- Copernicus GLO-30 DSM，名义30 m，EPSG:3826、EGM2008高程。真实网格与参考资料沿用D18：[NOTICE及完整署名](../18/NOTICE.md)、[数据来源记录](../18/research/sources.md)、[Copernicus许可](../18/terrain/sources/License-COPDEM-30.pdf)。
- 参考GPS轨迹来自D18记录的Taiwan Outdoors链接GPX；候选树位沿用OpenStreetMap资料，© OpenStreetMap contributors，ODbL 1.0，位置未经现场验证。轨迹的第三方再发布许可仍未确认；此次按所有者要求准备本地gallery资源，不代表已取得额外授权。既有来源限制与完整署名继续适用。

<a id="painting-sources"></a>

## Gallery classical painting sources

- 郭熙《早春图》，国立故宫博物院，台北；实际2011×2876中阶图档为CC BY 4.0，三处岩石/树梢经裁切、去背、改色与旋转。署名：Early Spring, The National Palace Museum, Taipei, CC BY 4.0 @ www.npm.gov.tw。见下方《早春图》图档与取用表，以及 [馆方开放资料页](https://digitalarchive.npm.gov.tw/opendata/Pub/Detail/47?dep=P&mode=full)。
- 树木：郭熙《树色平远图》、赵孟頫《双松平远图》、倪瓒《江渚风林图》、王蒙《素庵图》，均使用The Metropolitan Museum of Art开放CC0图档；董源《潇湘图》使用Commons标记公有领域的图档，不冒称馆方CC0。
- 瀑布：文徵明《松阴飞瀑图》局部，The Metropolitan Museum of Art，CC0。完整馆藏链接、图档URL、署名、裁切坐标及SHA-256保留于下文和 [source_manifest.json](assets/sources/source_manifest.json)、[rights_verification.json](assets/sources/rights_verification.json)。所有树木、山脊与瀑布拼贴均作艺术表现，不作为实测地物。

## 手调前：沿山势留白与《早春图》山脊拼贴（历史记录）

[合成 PNG](outputs/among_the_giants.png) · [31 层 PSD](outputs/among_the_giants_layers.psd) · 唯一低清构图预览 (historical preview removed; source retained)。当前相机、步道比例以及原有树木和瀑布位置均锁定；从未淡出的清晰地形原层开始，保留上一版独立的淡墨色阶和两处近坡皴纹。未调用PyVista重新渲染地形颜色。

参照用户上传的红圈，左侧留白由画外谷口斜向近坡后方，右侧由步道上方凹处斜绕坡肩后散入天空。`terrain_composite_support.py` 只从已有D18 DSM和同一相机计算坐标、相对高程与深度支持，不改变地形颜色、网格或步道。红圈锚点在附近DEM凹处落点，沿途高程变化；蒙版依据前坡深度遮挡，并加入可调整的视线后移量，形成隐入坡后、从邻近凹处再现的留白。天空出口与雾的体量是艺术处理，不是实测云雾或物理模拟。不是按画面高度或固定等高线铺带，也未羽化整座山。

PSD中两处 `Valley reserve` 各有独立可编辑像素蒙版；三处 `Ridge collage` 各自为一个独立透明像素层。主脊岩石较完整，侧脊使用短岩线及树梢，远脊降低墨色；只在三处局部接合，不覆盖整条外缘。步道、候选点、原有树木/林丛、每处瀑布、标题及注释继续独立。图例与主要内容已作避让。

### 《早春图》实际取用图档与许可

- 作品：郭熙《早春图》（1072），国立故宫博物院，台北，文物编号故画000053N000000000。[馆方开放资料页与许可](https://digitalarchive.npm.gov.tw/opendata/Pub/Detail/47?dep=P&mode=full)。馆方中阶图像为 **CC BY 4.0**，允许修改和再利用，须署名；未将其称为CC0。
- 实际输入：[guo_xi_early_spring_6mp.jpg](assets/sources/guo_xi_early_spring_6mp.jpg)，2011×2876；[实际IIIF下载链接](https://iiifod.npm.gov.tw/iiif/2/K2A%2FK2A000053N000000000PAA/full/!2011,2876/0/default.jpg)。页面证据保留于 `assets/sources/npm_early_spring_terms.html`，下载URL、实际像素、SHA-256及许可记录于 [npm_early_spring_source.json](assets/sources/npm_early_spring_source.json)，并已登记在 `source_manifest.json` 和 `rights_verification.json`。
- 署名：**Early Spring, The National Palace Museum, Taipei, CC BY 4.0 @ www.npm.gov.tw**。本版已在图面来源行标出，并注明 adapted；原有其他古画的详细署名见下文。
- 修改：三处不同岩石/树梢局部裁切、自然轮廓选取、去除绢底、统一灰墨、调整透明度、缩放与旋转；岩脚逐渐接入现有坡面。保留墨线、皴笔与细树梢，不复制题字、印章或矩形绢底。未生成替代古画的笔触。

| 独立素材 | 取用局部 | 实际源像素裁切框 (left, top, right, bottom) |
|---|---|---|
| [early_spring_main_ridge.png](assets/cutouts/early_spring_main_ridge.png) | 上部中央主峰的岩头、皴笔与稀疏松梢 | (827, 112, 1385, 670) |
| [early_spring_side_ridge.png](assets/cutouts/early_spring_side_ridge.png) | 左上独立岩头与树梢，排除相邻岩块 | (268, 603, 793, 1006) |
| [early_spring_far_ridge.png](assets/cutouts/early_spring_far_ridge.png) | 上部右侧岩沿与细松梢，淡墨处理 | (1312, 302, 1653, 637) |

透明蒙版、自然轮廓坐标和改色参数见 [early_spring_ridge_materials.json](assets/cutouts/early_spring_ridge_materials.json)。三处素材并非把同一去背图重复摆放。

复现本版：

```powershell
& 27/.venv/Scripts/python.exe -B 27/prepare_early_spring_ridges.py
& 27/.venv/Scripts/python.exe -B 27/compose_ridge_valley.py
# 查看低清预览后，仅导出一次全尺寸合成与PSD：
& 27/.venv/Scripts/python.exe -B 27/compose_ridge_valley.py --export
```

`review/ridge_valley/composition_plan.json` 记录红圈参考锚点、实际DEM坐标和高程、云雾深度与三处山脊变换；`terrain_depth_support.npz` 为可重建坐标/深度缓存。`export_report.json` 记录原有图层哈希；PSD回读对齐检查见 `outputs/psd_validation.json`。当前仍以 PNG、PSD 和 `outputs/photoshop_layers/layer_manifest.json` 为准；旧ZIP不代表当前版本。清晰地形层 `01_terrain_pale_ink.png` 保留原样。D18只读，gallery、commit和push均未执行。

## 上一版：淡墨分层、短弧皴纹与两道雾带（历史记录）

[合成 PNG](outputs/among_the_giants.png) · [28 层 PSD](outputs/among_the_giants_layers.psd) · 本轮低分辨率预览 (historical preview removed; source retained)。先检查630×882预览中的近坡、雾口与远山层次，再导出一次1800×2520成图和PSD。没有重新渲染三维场景，也没有移动步道、树木、林丛、瀑布或文字。

清晰地形原层 [01_terrain_pale_ink.png](outputs/photoshop_layers/01_terrain_pale_ink.png) 完整保留；新增 `Terrain - ink depth grading` 叠加色阶，近坡灰墨、中段浅灰绿、远坡淡墨，迎光面接近纸色。不改变地形透明边界，不对整座山羽化。当前相机仍为 `camera_portrait.json`：方位315°、俯角42°、正交宽945 m、parallel scale 661.5。

两处 `Cloud-curl dry brush` 各自独立成层；沿用 D18 `oblique/render_art.py:117–131` 的固定随机种子与坡向积分，再将短弧落在现有DSM表面，按同一相机投影，并检查笔触的前后遮挡。只在步道背后的两处背光转折加疏密不同的笔触。皴纹仅为表现，不增加名义30 m DSM的地形信息。

两道 `Mist` 层独立，带可编辑像素蒙版，分别处理顶部折角与右侧长直边；横向留白之间保留清晰坡脊。全边界大面积雾已从当前堆栈撤下，旧文件保留作历史资料。步道、树木与瀑布附近有保护区。

风格参照：[郭熙《早春图》，国立故宫博物院](https://digitalarchive.npm.gov.tw/Collection/Detail/47?dep=P)；参照卷云皴的弧转和山腰留白，未复制或拼贴该画的图像像素。沿用的古画树木、瀑布素材及授权说明见下文。

复现本轮合成（不调用PyVista渲染）：

```powershell
& 27/.venv/Scripts/python.exe -B 27/compose_early_spring.py
# 检查唯一低分辨率预览后：
& 27/.venv/Scripts/python.exe -B 27/compose_early_spring.py --export
```

`review/early_spring/stroke_plan.json` 保存短弧路径，`export_report.json` 保存锁定图层的哈希；`outputs/psd_validation.json` 记录当时的PSD回读核对。文字当时为独立像素层。旧PNG图层ZIP已在最终清理中移除；当时的图层PNG与清单仍保留，不能代替手调PSD。

旧版清理记录和干笔试验预览继续保留；旧哈希对应清理当时的工作稿。D18继续只读，未更新gallery，未commit或push。

## 历史清理与制作记录（以下机位、层数和版本状态为此前记录）

当前成对的全尺寸工作稿为 [PNG](outputs/among_the_giants.png) 和 [26 层 PSD](outputs/among_the_giants_layers.psd)。已逐层核对，两者合成像素一致；PSD 全部是内嵌像素层，没有外链智能对象或外部素材依赖。此次只清理文件，没有重新渲染、改构图或导出新设计。

最新的干笔与三段雾带试验仅有 630×882 预览 (historical preview removed; source retained)，尚未确认、尚无对应的全尺寸 PSD；其独立预览图层及 `preview_drybrush_banks.py` 一并保留，不要将它与当前全尺寸 PSD 误认为同一版本。

加大面积雾之前的清晰地形仍为 [01_terrain_pale_ink.png](outputs/photoshop_layers/01_terrain_pale_ink.png)，透明通道完整，也内嵌于当前 PSD 的 `terrain_pale_ink` 层。隐藏 `Ridge Mist - Full Boundary` 及其余 mist 层即可查看未加雾地形。当前相机以 `camera_portrait.json` 为准：方位315°、俯角42°、正交宽945 m、parallel scale 661.5；下文较远机位的参数为历史记录。

此前逐路径删除21张无引用的旧诊断、比较及素材浏览图，约17 MiB；[清理记录](review/cleanup_report.json) 保存具体路径、大小和删除前哈希。保留全部脚本、相机快照、输入、树木/瀑布去背素材、素材蒙版、来源和授权说明。`.venv/`、`.uv-cache/`及旧裁切参考图暂留。旧PNG图层ZIP后来在本轮最终清理中移除，不代表手调PSD状态。

以下为之前的制作过程及来源说明；本轮不更新 gallery，不 commit、不 push，D18 继续只读。

此前交付：[手调前合成 PNG](outputs/among_the_giants.png)及透明PNG图层堆栈。1800×2520，署名 Ming Cao，当时为**有天空的远斜视、古画树木及瀑布、局部薄雾版**。其ZIP已清理；现有同名PSD已由用户手调，最终入口见顶部。未更新 gallery、commit 或 push。

## 先检查构图，再完整合成

采用 D18 C 视角作为较远机位参照：**315°方位 / 18°俯角**，原世界目标不变，画面右向偏移28.42 m、上向450 m，正交世界宽1800 m、高2520 m、parallel scale 1260。相比此前315°/42°近景版，这次明确改变俯角与视野，以读出山体体量和天空；不是强行把旧山体外边界做成山脊。当前参数在 `camera_portrait.json`，修改前参数留存于 `review/camera_before_sky_revision.json`。D18 的冻结相机没有修改。

先比较多个低分辨率机位，记录在 `review/sky_camera_study.png`。选定后先输出并检查：

- 无拼贴地形预览 (historical preview removed; source retained)：720×1008，原始渲染天空约占33.2%。前坡、侧坡、谷地及远山可辨。
- 无拼贴、带参考轨迹预览 (historical preview removed; source retained)：参考轨迹所有原顶点均在画幅内，没有删去路线。实际背坡遮挡仍由三维地形深度决定，不强行显示隐藏段。
- 同相机线框与边界 (historical preview removed; source retained)：细灰线为真实三角网，品红为网格外边界；低分辨率仅左上远端有45个边界像素，框约为 `(50,299)–(65,309)`。其余主要天空轮廓由真实地形遮挡决定，不是上轮的尖角裁切。
- 原始边界透明通道与参数在 `review/sky_boundary_isolated.png`、`sky_composition_report.json`。正式分辨率另输出 `review/sky_boundary_full_resolution_isolated.png`，原始边界计数见 `outputs/render_report.json`，**本版不冒称原始边界为0**。

薄雾只有两组独立透明图层：左上诊断露边的小段远端转折，以及主/远瀑谷口附近。用局部横向雾团形成由浓到淡的坡脚/谷口形态，不作整圈羽化、不改变山体alpha、不对地形PNG作模糊；真实主山脊保持清楚。左上薄雾属于艺术处理，并没有把有限DSM变成无限数据。山体仍用浅灰绿淡墨；在此前浅底上稍加强侧光，采用B光照：环境光0.67、漫反射0.34、specular 0、光源局部坐标 `(-1300,-900,1500)`。颗粒标准差0.45只作表现，不增加地形信息。

## 真实地形和路线

D18只读输入：

- `../18/oblique/scene_mesh_epsg3826.npz`：原1804顶点、3440面片，参考轨迹、分段ID、候选树位。
- `../18/oblique/composition_dem_30m.tif` 与 `composition_dem_source.json`：D18已有5.4×6.0 km、200×180的扩展真实DSM。
- `../18/oblique/camera_c.json`：原目标与C视角参照。
- `../18/research/data/official_communication_points.geojson`：游客中心通讯标示点，非实测售票口。

Copernicus GLO-30 **DSM，名义30 m，含林冠**；EPSG:3826 / EGM2008。完整扩展网格36000顶点、71242面片，原顶点和面片保留在数组前段，重叠高程逐值一致；没有平滑几何、捏造山脊或更改高程基准。统一1.2×垂直夸张只影响显示。底边与两个底角仍由真实前景覆盖。原网格范围、轨迹和候选点XYZ没有改写。

步道保留原有赋高线段、部分及端点顺序，不平滑、不补连、不吸附树位；显示上移1 m避免深度冲突，5.5 px线宽不是实际路宽。15个候选点低调显示，13号冲突和缺失编号不补造。步道、候选点及入口各自通过同一相机和地形深度导出；地下测试球可见像素为0。主树以候选1附近坡面为艺术落脚参照，赵孟頫单松以候选16附近为参照；树形、大小和物种不编码实际调查值。

此前露边修正的42°版诊断文件保留供追溯，但不能把旧版“0边界”结论套用到本轮18°相机。

## 瀑布位置核查：两处均为艺术示意

核查记录：[waterfall_location_check.json](research/waterfall_location_check.json)。[桃园官方旅游页面](https://travel.tycg.gov.tw/zh-cn/Travel/Attraction/63)的索引图注出现“拉拉山国家森林游乐区内小瀑布”；[林业保育署园区介绍](https://recreation.forest.gov.tw/Forest/RA?typ_id=0200005)可核对园区环境。官网页面依赖JavaScript，取得的HTML不足以定位瀑布。另目视检查D18保存的官方导览图 `official_224.jpg`，并搜索D18研究、OSM/GeoJSON记录，没有取得可以独立核实到当前图幅的瀑布坐标。园区统一POI或游客中心坐标不等于瀑布位置。

因此**没有把主瀑或远瀑标作真实拉拉山瀑布**，也没有冠以已知瀑布名称。两处均为古画艺术点景。它们放在可读为谷槽的空处，以同一DSM表面的下降方向调整水线；DSM高差仅判断图像中的落水方向，不是瀑布实测高度，不能据此推断当地存在瀑布。

`plan_waterfalls.py` 只为版面在原三角面上寻找下降趋势，避开参考轨迹至少65 px；投影、头/尾位置和艺术属性在 `assets/waterfall_placements.json`。`verified_real_location=false` 为两处明确字段。主瀑沿右侧坡面斜垂、远瀑位于较远侧坡，尺寸更小，alpha约为主瀑的63%。瀑布是二维拼贴层，不声称为三维水流模拟或实测水文。

## 实际瀑布抠图与授权

先检查马远《高士观瀑图》，再比较文徵明和唐寅的开放图档。实际抠出三个不带人物和大片山石的溪瀑局部，见 瀑布去背检查图 (historical preview removed; source retained)。采用其中两处；**下载整画或仅列出处不计为已用素材**。

| 去背文件 / 本版用途 | 原画、馆藏及实际图档 | 取用部位和处理 |
|---|---|---|
| [waterfall_wen_main.png](assets/cutouts/waterfall_wen_main.png)，主瀑，已放入成图 | 文徵明《松阴飞瀑图》，Met英文馆藏名 *Recluse playing the zither in a pine grove*，约1540年，1982.1.6；[馆藏页](https://www.metmuseum.org/art/collection/search/45778)；[实际 DP-24654-002_crd.jpg](https://images.metmuseum.org/CRDImages/as/original/DP-24654-002_crd.jpg)，1678×3687 | 原画上中部双股长垂瀑的下段，源裁切 `(552,1170)–(688,1565)`；紧沿水道与少量贴岩笔触，不带人物、整片山石或矩形绢底。 |
| [waterfall_wen_far.png](assets/cutouts/waterfall_wen_far.png)，远瀑，已放入成图 | 同一文徵明馆藏图档 | 源裁切 `(553,924)–(616,1184)`，上段较细的转折水道，单独去背、缩小、淡化，保留原曲流水线；不是把主瀑重复复制。 |
| [waterfall_ma_rapids.png](assets/cutouts/waterfall_ma_rapids.png)，备选，未放入成图 | 马远《高士观瀑图》 / *Scholar viewing a waterfall*，13世纪早期，1973.120.9；[馆藏页](https://www.metmuseum.org/art/collection/search/40086)；[实际 DP154090.jpg](https://images.metmuseum.org/CRDImages/as/original/DP154090.jpg)，3407×3000 | 原画右下贴岩的小溪瀑/急流局部，源裁切 `(2630,2220)–(3005,2520)`；已沿不规则水线去背，但绢纹较明显，且不是长垂瀑，所以不用于主/远瀑。 |

两件作品的馆藏页均标记Public Domain，官方API的 `isPublicDomain=true`，下载URL与API primaryImage一致；依 [Met图像政策](https://www.metmuseum.org/policies/image-resources)，这些开放图像为 **CC0**，可复制、改作及再利用。实际源文件、元数据、SHA-256、源轮廓和使用状态见 `assets/sources/` 与 `assets/cutouts/waterfall_materials.json`。完整署名分别为 Edward Elliott Family Collection, Purchase, The Dillon Fund Gift, 1982（文徵明）；Ex coll.: C. C. Wang Family, Gift of The Dillon Fund, 1973（马远）。

`prepare_waterfalls.py` 保留源扫描里的水道负形和墨线：水线中的浅色不能像普通绢底一样按亮度全部删除，因此使用紧贴原水道的手工透明轮廓，只统一色调。没有生成或重绘水线，没有残留矩形底。源图所含人物、题字、印章和大块山石均不在使用轮廓内。唐寅《观瀑图》（Met 45772，CC0）也已检查，但局部不适合本轮小尺寸拼贴，未算作已用素材。

图上图注严格为 **Tree and waterfall collage from classical ink paintings.**

## 继续使用的古画树木

五张现有去背素材均保留，按远斜视的尺度重新安放，各一独立图层：

- 郭熙《树色平远图》近景曲干主树：`guo_xi_main_tree.png`；[Met 39668](https://www.metmuseum.org/art/collection/search/39668)，DP167812_CRD.jpg，CC0，候选1附近。
- 赵孟頫《双松平远图》右手单松：`new_zhao_single_pine.png`；[Met 40508](https://www.metmuseum.org/art/collection/search/40508)，DP153682.jpg，CC0，候选16附近。
- 倪瓒《江渚风林图》近岸疏林：`new_ni_sparse_grove.png`；[Met 41154](https://www.metmuseum.org/art/collection/search/41154)，DT6291.jpg，CC0，前景左侧。
- 王蒙《素庵图》庭院上方及右侧松林冠：`new_wang_dense_grove.png`；[Met 39550](https://www.metmuseum.org/art/collection/search/39550)，DP274196.jpg，CC0，较远侧坡。
- 董源《潇湘图》左侧近岸林丛：`dong_yuan_grove.png`；故宫博物院（北京），[实际Commons文件](https://commons.wikimedia.org/wiki/File:Xiao_and_Xiang_rivers.jpg)，Public Domain Mark / PD-old-100-expired，不冒称另有馆方CC0授权。

所有源扫描仍在 `assets/sources/`，实际取用部位和轮廓在 `extraction.json`、`new_materials.json`。树形和大小均为艺术表现，不按候选点逐棵摆放，不与树种/树高对应；无矩形框、引线或图卡。

## 分层文件与 Photoshop

当前为 **25层 PSD**：天空、山体、两组局部薄雾、步道、候选点、入口标记、五个树木/林丛、两处瀑布、标题与各项图注/署名分别独立。所有图层为1800×2520、同原点(0,0)、Normal混合；艺术不透明度已在各自alpha中。可以在Photoshop单独移动、缩放或调浓淡。

备份PNG在 `outputs/photoshop_layers/` 和ZIP内，编号从下到上，00天空、24署名；Photoshop图层面板顺序相反。不要单独裁边或自动对齐。解压后可运行 `load_png_layers.jsx` 建立相同堆栈。

文字在PSD中为独立像素层以保持对齐。若要改字，可在Photoshop运行 `outputs/make_text_editable.jsx`，隐藏原像素文字并建立原生文字，检查字体度量后另存。Georgia与Segoe UI的文案、字号、基线、颜色见 `editable_text.json`。可选脚本未在Photoshop应用内实测，不能声称交付PSD已含原生文字对象。

`outputs/psd_validation.json`：重新打开PSD后每层名称、尺寸、原点、alpha及可见像素均核对；逐层重建与合成PNG逐像素一致。PSD内嵌兼容预览最多1/255舍入差异，不是对齐偏移。全尺寸与390×546缩略图均已打开检查：天空、主山脊、步道、主瀑和远瀑可同时辨认，细小来源需读原尺寸。

## 重跑

Windows PowerShell，仓库根目录：

```powershell
uv --cache-dir 27/.uv-cache pip install --python 27/.venv/Scripts/python.exe -r 27/requirements.txt
& 27/.venv/Scripts/python.exe -B 27/prepare_collage.py
& 27/.venv/Scripts/python.exe -B 27/prepare_new_collage.py
& 27/.venv/Scripts/python.exe -B 27/prepare_waterfalls.py
& 27/.venv/Scripts/python.exe -B 27/preview_sky.py
& 27/.venv/Scripts/python.exe -B 27/plan_waterfalls.py
& 27/.venv/Scripts/python.exe -B 27/render.py
```

`scene_layers.py` 负责真实几何和共用相机/深度；`atmosphere.py` 只创建局部雾和源图瀑布的透明图层；`build_layers.py` 从交付图层生成最终PNG；`export_psd.py` 写入并回读PSD。输入文件哈希在render_report.json，D18未改动。当前相机不同于上一版，旧 `boundary_diagnosis.json` 的0像素结论只作为历史记录，不适用于本轮。

## 数据与再发布限制

沿用 [D18 NOTICE](../18/NOTICE.md)、[sources](../18/research/sources.md) 和 [Copernicus许可证](../18/terrain/sources/License-COPDEM-30.pdf)。完整署名：

produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.

The organisations in charge of the Copernicus programme by law or by delegation do not incur any liability for any use of the Copernicus WorldDEM-30.

候选点 © OpenStreetMap contributors，ODbL 1.0；源ID与证据留在D18，未经现场验证。游客中心是官方通讯标示点，不是实测售票口。Reference GPS track来自Taiwan Outdoors链接的2024-08-02游客GPX，第三方再发布许可未确认。PNG、PSD和含该轨迹的分层文件均仅作本地讨论预览；公开使用前仍须确认相关条款。古画CC0不改变地理轨迹的权利限制。
