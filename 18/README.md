# Day 18 — Among the Ancient Trees

[当前艺术化PNG：C / Monumental Mountain](oblique/shanshui_C_art.png)（1800×2025）。固定采用真实三维地形的C视角，不再发展二维俯视方向。

相机：**315°方位、18°俯角、1.20×垂直夸张，正交高度1808.836708m（约1809m）**。目标点和矩阵直接读取 [camera_c.json](oblique/camera_c.json)，没有重新选择相机。画布是原C预览统一放大1.125倍，投影视口比例与位置对应原C；图面不显示技术相机参数。

## 山体与古树

山体仍是既有Copernicus GLO-30 **DSM、名义30m** 三角网，工作坐标EPSG:3826，Z为EGM2008。未修改DEM、网格顶点、山脊、谷地或遮挡几何，也没有将二维hillshade扭曲成斜视地形。

原面片色差通过面积加权顶点法线及逐片元法线插值弱化，仅改变光照，不增加地形分辨率。背光陡坡的墨色由真实法线、坡度和光源控制；使用灰青、淡石绿和墨绿，远处适度减淡。干笔纹理是**世界坐标中的沿坡曲线**，每点在原网格表面重新赋高，并通过同一相机与深度测试。谷地轻雾由局部相对地势控制，不增加遮盖全图的雾层。面片已不再形成明显的彩色三角拼贴，但30m网格的局部外轮廓折线仍存在，不能宣称高精度地形。

15个候选根部全部保持原世界XYZ，贴地残差0。树木改为真正的三维弯曲枝干、分枝、根须和叶簇，全部投影并进行遮挡测试，不是另放在屏幕上的二维贴图。1、5、12号作为艺术主树，其余更小更淡；尺寸**不编码实测树高或树龄**。15号为贴地倒木，不伪装成活立木。根部被山体挡住时仅可能露出上方枝叶，不强行显示根部。

本轮15个候选对象至少有部分枝叶/倒木可见，判定口径为最终仍有至少4个经过深度测试的可见像素。这不同于历史22m测试杆的14个部分可见、13个根部可见；不能用艺术夸张后的树形推断根部可见性或精确定位。13号冲突点和缺失编号仍不补造。

参考GPX在内存中按原部分及顶点顺序进行轻微Gaussian平滑，单点水平位移限制4m，端点不动；随后重新在同一三角网赋高。此举仅减弱显示抖动，不改写源GPX、不拼接断点、不吸附树位、不重建权威步道。线条使用较细淡赭色，世界坐标线段逐采样进行深度测试，山体遮挡的部分隐藏。保留原始连接顺序不等于已纠正GPS自交或定位误差。

## 主要文件与复现

| 内容 | 位置 |
|---|---|
| 当前唯一保留的项目PNG预览 | [shanshui_C_art.png](oblique/shanshui_C_art.png) |
| 正式三维艺术渲染代码 | [render_art.py](oblique/render_art.py) |
| 固定C参数与相机研究 | [camera_c.json](oblique/camera_c.json)、[camera_study.md](oblique/camera_study.md) |
| 原始世界坐标场景 | [scene_mesh_epsg3826.npz](oblique/scene_mesh_epsg3826.npz)、[scene.json](oblique/scene.json) |
| 当前艺术渲染验证 | [art_validation.json](oblique/art_validation.json) |
| 资料可行性、逐树名录、OSM、GPX及证据 | [research/README.md](research/README.md)，研究内容原样保留 |
| 原始/投影DEM与科学派生结果 | [terrain/README.md](terrain/README.md)、[terrain_diagnostics.pdf](terrain/data/terrain_diagnostics.pdf) |
| 来源与授权 | [NOTICE.md](NOTICE.md)、[research/sources.md](research/sources.md) |
| 清理统计与删除依据 | [cleanup_report.md](cleanup_report.md)、[cleanup_plan.json](cleanup_plan.json) |

正式构建：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'E:\MUSA\650 deep learning with python\vision-EO\.venv\Scripts\python.exe' -B 18/oblique/render_art.py
```

必要依赖保留于`terrain/.deps/`，可再生成的字节码缓存已清理。`terrain/scripts/acquire_dem.py`可重新下载研究范围原始裁片；`terrain/scripts/analyze_terrain.py`保留原流水线的科学分析及诊断PDF，不再绘制旧二维PNG。`oblique/build_study.py`只供显式复现历史相机比较，正式构建不导入它，也不改写固定C文件。`research/scripts/`中的资料解析与核查代码保留。

## 清理与限制

已先将相机比较结论存入`camera_study.md`，再删除二维01/02A/02B/03与三张Camera Study的PNG、可再生成的旧深度缓冲，以及只服务于废弃二维图面的代码和核验输出。原始数据、研究成果、来源响应及许可证不删。比较JSON/CSV、旧研究记录和必要分析代码保留。清理统计包含git忽略的依赖与缓存，详见清理报告。

图面保留候选位置未经验证及树形不按比例的说明。DSM包含植被，不是20m裸地DTM；根部赋高不是实测树干基部。GPX再发布授权局限不变，见NOTICE。本轮只作本地艺术讨论预览，无GIF、Gallery更新、学院仓库修改、commit或push。
