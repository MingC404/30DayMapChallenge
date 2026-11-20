# Day18 cleanup report

统计范围为整个`18/`，包含git忽略的本地依赖和第三方包内资源；磁盘占用为逻辑文件字节数，不是文件系统簇占用。清理前为本轮工作开始时，清理后包含新增艺术预览、代码、相机文档和审计报告。

| 时点 | 文件数 | 字节 | MiB |
|---|---:|---:|---:|
| 清理前 | 6,969 | 412,461,066 | 393.35 |
| 清理后 | 6,200 | 374,928,690 | 357.56 |

净减少 769 个文件、35.79 MiB。该净值同时计入本轮新增文件，不应等同于删除清单的字节总和。

删除了19个明确废弃的输出/脚本/零字节安装残留，以及98个Python字节码缓存目录（763个缓存文件）。具体路径、大小、原因在[cleanup_plan.json](cleanup_plan.json)。

先将固定C参数、历史相机比较和结论保存到[oblique/camera_study.md](oblique/camera_study.md)，再移除三张Camera Study PNG及可再生成的深度缓冲。二维01、02A、02B、03旧PNG和仅服务废弃图面的脚本已移除；原流水线的科学分析部分另存为`terrain/scripts/analyze_terrain.py`。正式构建不导入被删除脚本。

对96个研究、GIS及来源证据文件逐一核验SHA-256，均未改变。原始DEM、投影DEM、OSM候选点、GPX、官方图件、许可证、下载失败证据、研究文档与科学派生结果均保留。已安装依赖仍供复现使用，未为减少文件数随意破坏第三方包；包内示例/工具图标不是旧项目预览，未删除。当前项目输出PNG仅[oblique/shanshui_C_art.png](oblique/shanshui_C_art.png)一张。

固定相机315°/18°/1.20×/1808.836708m核验通过，树根赋高残差0，艺术树形部分可见数量15；不是实测树位精度或根部全部可见的声明。PNG可解码、保留脚本语法检查通过。原始研究结论未改变。

主要保留代码：`oblique/render_art.py`（正式构建）、`oblique/build_study.py`（历史相机复现）、`terrain/scripts/acquire_dem.py`、`terrain/scripts/analyze_terrain.py`和`research/scripts/`。`oblique/prepare_cleanup.py`、`finalize_docs.py`、`finish_audit.py`只记录本轮审计工作，不是日常艺术构建依赖。

没有生成GIF，没有更新Gallery、学院仓库，没有commit或push；工作范围仅Day18。
