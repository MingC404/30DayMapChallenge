# Atlas of Impossible Places

2026 30DayMapChallenge · Day 14 / Borgesian Map  
**Current direction: Illustrated Architectural Montage.**  
**Real places. Impossible connections.**

当前仅完成三个横向 Composition Studies，等待选择。没有正式地图、完整排版、GIF、交互页面或合集网站更新。三张 PNG 是构图草图，不是正式输出；均无标题、图例和署名。

| 方案 | 草图 | 空间骨架 |
| --- | --- | --- |
| A — River as the Spine | [查看预览](work/composition_studies/option_a_river_spine.png) | 河道与两岸连续展开 |
| B — Street as the Spine | [查看预览](work/composition_studies/option_b_street_spine.png) | 行人视点、林荫道、转弯与桥下支巷 |
| C — Layered Urban Montage | [查看预览](work/composition_studies/option_c_layered_montage.png) | 广州前景、砖仓库与河岸中景、城墙山体远景 |

**推荐 C 深化**：屋顶、庭院、步道和桥梁形成多条探索路径，建筑遮挡将四城交织进同一空间。下一轮应先修正桥塔主次和桥梁落地关系，增强 Philadelphia 的具体识别度。选择前不进入正式绘制。

详细评估见 [COMPOSITION_STUDIES.md](COMPOSITION_STUDIES.md)，真实性与流程见 [METHODS.md](METHODS.md)，参考资料见 [references/SOURCES.md](references/SOURCES.md)。完整生成提示词保存在 [config/illustrated_montage_prompts.json](config/illustrated_montage_prompts.json)。

## 文件组织

```text
14/
  README.md
  COMPOSITION_STUDIES.md
  METHODS.md
  config/illustrated_montage_prompts.json
  references/SOURCES.md
  metadata/illustrated_montage_manifest.json
  work/composition_studies/       本轮三张构图预览
  work/study_*.png                旧版 OSM 平面拼接实验，不是本轮方案
  work/stage_a_candidates.png     旧版 OSM 数据检查
  data/, scripts/, requirements.txt 旧版平面研究的数据与 Python 工具
```

本轮替代了先前 figure-ground 方向；旧研究原样保留以便追溯，但其中的 A/B/C 与本轮的 A/B/C 含义不同。只比较 `work/composition_studies/` 下的三张新预览。未建立正式 output/outputs 目录。

## 当前工具与复现边界

- 已验证 Python 3.14 和本地 Pillow、Matplotlib、Shapely、PyProj 可用；可用于尺寸、文件校验、后续线稿与透视辅助。
- 本轮插画使用内置 `image_gen`，不是几何方块自动拼装，不需要外部 API key。
- 三图均为文字约束生成，网页参考用于研究和提示词约束，未把参考照片作为图像输入。没有逐栋测绘、照片投影或保证尺寸准确。
- 提示词可复用；生成结果不保证逐像素复现。原始生成图已复制到本目录，没有二次缩放或画面编辑。
- 浏览研究日期：2026-11-13（America/New_York）。图像不是现实存在的城市或真实相邻关系。
