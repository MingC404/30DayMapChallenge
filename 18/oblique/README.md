# Adopted C camera — Oblique Shanshui

2026-11-20 构图修订：查看 [新版 PNG](shanshui_C_composition.png) 与 [构图说明](composition_revision.md)。运行 `render_art.py --composition` 使用独立相机配置及扩展真实 DSM；默认运行仍复现旧版。旧预览与冻结 C 参数保留。

正式参数固定于[camera_c.json](camera_c.json)，只沿用C。查看[当前艺术预览](shanshui_C_art.png)与[制作说明](../README.md)。

完整相机比较、矩阵定义和历史可见性统计保存在[camera_study.md](camera_study.md)。阶段PNG与可再生成的深度缓冲已清理，`camera_comparison.json/.csv`、网格、输入哈希与研究代码保留。

正式入口为`render_art.py`；只读取冻结C参数及既有世界坐标场景，输出一张PNG及`art_validation.json`。`build_study.py`仅供显式复现历史比较，不是正式构建依赖。`prepare_cleanup.py`、`finalize_docs.py`是本轮审计记录工具，不是日常构建步骤。
