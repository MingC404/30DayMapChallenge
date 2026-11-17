# 30DayMapChallenge 2026 — Typography Consistency Pass

本轮为**本地审查与规范提案**，不是系列最终文件的批量修改。审查对象是作品内部的文字，不包括合集网页左侧标题。未覆盖任何 Day 目录中的成图、脚本或网页；未 commit / push。

## 审查范围与读数规则

以 `scripts/gallery_entries.json` 指向的当前最终文件为准，检查关联 PNG、GIF、SVG、HTML/CSS 和生成脚本。Day 01–16 中找到 **15 个已完成日期**：Day 07 只有 `.gitkeep`，不补画、不添加标题。Day 12 有两组季节作品，分别纳入文件清单。Day 13 的本地作品纳入内部审查，仍不公开。

- [原作 contact sheet](contact_sheet_current.png)：各图按原始宽高比适配相同缩略框，不模拟网页里个别日期的 70% / 75% 缩放。
- [文件清单](asset_inventory.json)：最终文件尺寸、GIF 帧数、时长、循环设置和 SHA-256。
- [脚本证据](source_evidence.json)、[SVG 标题记录](title_records.json)：字体、坐标、字号的原始证据。
- 坐标为脚本坐标，除明确标为 figure / axes 的项目外，从左上角计量。SVG 的 y 通常为基线；Pillow 的 y 是绘制锚点，不能直接当作字形顶部。
- 字号为字体 em 尺寸，不是实际字形高度。Pillow / SVG / CSS 使用 px 或逻辑单位；Matplotlib 使用 pt，换算为输出像素时乘 `dpi / 72`。
- 不把导出 PNG、逻辑 SVG、网页 GIF 的不同分辨率误认为不同字号设计。尺寸均直接读取现存文件。除明确设置外，字距为默认 0，字重为 400；Pillow 单行文字没有 CSS 行高。

## Typography audit：原始设置与建议

下表 D / T / S 分别为 Day/Theme、Main title、Subtitle。无对应元素时明确标为“无”，不从网页注册表补入。地理说明、来源及图例不是自动新增的副标题。

| Day | 当前最终输出尺寸，px | 原始 D / T / S：字体、字号、字重 | 原始位置与间距 | 建议与特殊处理 |
|---|---|---|---|---|
| 01 | PNG、GIF 1200×900 | D 无；T Georgia 32/400，字距 −0.8px；S 系统 sans（本机 Segoe UI）14/400 | HTML header 左上 `(34,23)`，高 112；T 下 margin 7；S 紧随。HTML 小屏 T=26 | Georgia 保留；参考 1200 宽 T≈34、S≈14。只改 h1 与 header 的副标题，不动 sidebar h2、计数、地图相机；不新增 D |
| 02 | PNG 2120×1500；GIF 1200×900 | D 在说明行内：Arial 12/400（export）；T：HTML Arial `clamp(20px,1.8vw,30px)` /500，导出 Arial 64/800，字距 −2px、行高 .88；S Arial 11（HTML）/12（export） | 左侧地图内，left 2.4%、top 1.4%，另有后续断点覆盖；HTML 两行 `Waterfront / Walks`，导出两行 `Enjoy the / Waterfront`；S margin-top 7 /12 | **保留两个版本各自现有文字**。窄地图标题槽不能套整个画布宽度；按实际左侧地图面板宽度、约 32–36px 的两行 T 试排，保持控件、图例不动。属于受限布局例外，待批量阶段做专门浏览器碰撞检查 |
| 03 | PNG 3600×2380；GIF 1200×793 | D 无；T Arial 82/400（轻背景描边 2px）；S 无。右上 `JERSEY CITY / ACTIVITY SPACES` 为区域说明，Arial 34 | T `(65,32)`；右上说明 `(3535,77)`、右对齐；面板标题 y=153 | T 改 Georgia 101/400（2.8%W），保持锚点、描边与面板位置；不新增 D/S。已制作预览 |
| 04 | PNG 2400×2000；GIF 1440×1200 | D Arial Bold 24/700；T Arial Bold 58/700；S Arial 26/400 | D `(70,40)`；T `(65,91)`；S `(70,171)`；地图 y=240；T 是完整的 `Clusters of Play — Jersey City & Hoboken` | D Segoe UI Semibold 26；T Georgia 67；S Segoe UI 29。完整文字保留，仍单行。参考 tracking .08em 的提案另列，预览暂用字体默认字距。已制作预览 |
| 05 | GIF 1560×1130；另有 5839×1500 scroll JPG、分层 SVG | D sans；T Georgia Regular；S Arial Regular。保留静态头部；相关 still 脚本为 23/78/25 的逻辑字号 | 固定头部左上，动画仅读取 `05/assets/fixed_canvas.png`；still 版本 x≈80，D 基线65、T基线155、S基线210 | 保留 Georgia；**GIF 固定标题层的原始字号/字重生成设置 Unknown**（现存脚本读取已烘焙 PNG；不能把 scroll still 设置当作最终 GIF 的精确读数）。后续从保留头部重建专用文字层，不能用整幅 scroll JPG 替换 GIF 构图；不动地标标签字体 |
| 06 | PNG 4620×3030；GIF 1200×787 | D Arial Bold 34/700；T Georgia 108/400；S Arial 39/400 | 左上 D `(115,85)`、T `(107,153)`、S `(115,300)`；背景是历史扫描图，不是平色纸张 | 复用 Georgia；T 建议≈129px、D≈51px、S≈55px，在现有左上文字区内复核。**历史底图原生标签完全排除**；不能用涂抹历史纹理的方式换字，应回到生成脚本 |
| 07 | 无 | 无最终作品、无可核验标题设置 | 仅 `.gitkeep` | N/A；不补内容 |
| 08 | PNG 5700×4380；GIF 1200×922；SVG viewBox 1900×1460 | D Arial Bold 24/700；T Arial Bold 51/700；S Arial 22/400，均为逻辑尺寸（PNG ×3） | D `(100,30)`；T `(98,77)`；S `(101,150)`；右上作者独立 | 逻辑 T≈53 Georgia、D≈21 Segoe UI Semibold、S≈23 Segoe UI；保留插画文字、路名、作者与全部构图 |
| 09 | PNG 4200×4500；GIF 1200×1286；SVG viewBox 2100×2250 | D Arial 19/400；T Arial 53/400；S Arial 21/400。地图姓氏另用 **Noto Serif TC /650，52.8–129.6**（逻辑单位） | D `(55,50.5)`、T `(55,115.5)`、S `(57,161)`，SVG 基线；作者 `(1930,198)` | **保留姓氏字形、字号和位置：它们编码数据。** 建议本轮保留整组原有标题；若以后调整，仅英文标题作为独立可选方案，不能连带统一地图字形或表格 |
| 10 | PNG 4800×3600；GIF 1200×900；交互 SVG 使用逻辑 2400×1800 | D Arial Bold 19/700；T Georgia 83/400；S Arial 29/400（PNG ×2） | D `(65,45)`；T `(62,85)`；S `(66,192)`；右上另有统计，不能并入标题 | 标题已是 Georgia，建议只改 D/S 字体；T **保留83逻辑单位**作为较大 editorial 例外，避免为数值统一而削弱现有层级。交互标题在生成的 SVG 固定 artwork 中，不能只改外层 body CSS |
| 11 | PNG 2600×1910；GIF 1200×882；SVG 同逻辑画布 | D 无独立标题标签（页脚有 Day 11）；T Noto Sans SC 48/400；S Noto Sans SC 25/400；IPA 另用 Arial | T `(65,30)`、S `(65,96)`，SVG `text-before-edge`；来源及作者在底部 | T Georgia≈73；S Segoe UI≈31，`水` 保留 Noto Sans SC fallback。现有 T/S 间距不足以直接放大，后续只在原头部区内调标题行距并做字形碰撞检查，不能移动波形/地图；不新增 D |
| 12 | PNG 两张均3840×3520；GIF 两条均1056×968 | D Arial Bold 34/700；T Georgia132/400；独立 S 无，地理上下文 Arial28；上方 series 标签 Arial30 | 左上 x=100，series y=70、T y=148、D y=340、地区 y=410；署名 Georgia42 | Georgia 保留；建议保留较大132作为暗色风场特例，只统一 D 字体与 tracking。**不要把月份、地区、图例标题误当作新副标题**；January / September 同步，保持全部时长与风场不变 |
| 13 | 本地PNG 1800×1450；另有交互HTML | 静态 D Arial19/400、字距2；T Georgia76/400 两行、基线差90；地理/时间说明 Arial18；HTML h1 Georgia48/400、行高1.1、字距−1.3（大屏53、小屏39） | 静态 x70，T基线181/271，D `(75,331)`；HTML masthead `(30,26)`，响应式覆盖；作者独立 | **保留两行大字号的编辑式标题**，不强制降到2.8%W。D 可统一 Segoe UI Semibold，HTML只改标题选择器；静态与交互是不同构图。仍为本地内部评审，不公开 |
| 14 | GIF 720×655 | D Matplotlib 默认 DejaVu Sans 8.5pt/400；T Georgia24pt/400；S DejaVu Sans10.5pt/400，100dpi | figure T `(.045,.93)`、S `(.045,.885)`、D `(.045,.84)`；T≈33.3px，即4.63%W | **保留大 Georgia 主标题与标题在 D 上方的顺序**。只考虑 D/S 换为系列 sans；不能将其缩成普通2.8%W或移动地图。即便只换字，也须保持相机动画和所有帧时长 |
| 15 | PNG 2880×2115；逻辑画布3200×2350，90dpi导出 | D DejaVu Serif12pt/400；T DejaVu Serif37pt/400；S DejaVu Serif13pt/400，全大写；导出约15/46.25/16.25px | 地图坐标 y 向上：D `(95,2278)`、T `(95,2218)`、S `(98,2172)`；左上方志式小标题组 | **完整保留方志题签**，含 DejaVu Serif、大写、紧凑字号与细线；它属于图像叙事，而不是常规 editorial 标题。不可替换为网页注册表中的长标题 |
| 16 | PNG、GIF1440×1440 | D Consolas10pt/400（16.67px）；T Georgia23pt/400（38.33px）两行、行距1.12；S Georgia12pt/400（20px）两行 | D figure `(.05,.965)`；T axes `(.015,.84)` top；S axes `(.015,.745)` top；120dpi；作者、日期独立 | T Georgia24.192pt≈40.32px；D Segoe UI Semibold9.504pt≈15.84px；S Segoe UI10.368pt≈17.28px。保持地图内锚点、换行与统计字号。已制作预览；几何仍为已授权的 NJT 版本，不改数据来源 |

## Credits / Sources 审查（不统一）

| Day | 当前署名与来源文字的排印特征 | 处理 |
|---|---|---|
| 01 | 页脚系统 sans 10px；地图 attribution 9px；带可点击来源链接 | 原样保留 |
| 02 | `.map-credit` Arial10px，移动端8px；靠底部右对齐 | 原样保留，不能因标题放大遮住 |
| 03 | 底部 Arial32px，x65 / y2310 | 原样保留 |
| 04 | Ming Cao Arial Bold32px；来源23px，y1880 /1920 | 原样保留 |
| 05 | 固定页脚；相关 still 作者 Georgia29、来源Arial20；固定 GIF 源像素不能据此宣称精确字号一致 | 原样保留；烘焙层原始设置标为 Unknown |
| 06 | 来源 Arial35px；作者 Georgia55px | 原样保留；不改历史扫描文字 |
| 07 | N/A | 无操作 |
| 08 | 右上作者 Arial Bold28逻辑单位；底部来源18 | 原样保留 |
| 09 | 作者 Arial22逻辑单位；统计表、来源、姓氏数据字形独立 | 原样保留 |
| 10 | 作者 Georgia38逻辑单位；来源Arial18/17 | 原样保留 |
| 11 | 来源、署名 Noto Sans SC；署名记录为19px；IPA样例Arial | 原样保留；避免 CJK / IPA 丢字 |
| 12 | 作者 Georgia42px；日期数据上下文Arial28px | 原样保留 |
| 13 | 静态作者Georgia27px、来源Arial16/14px；交互byline sans12px | 原样保留；许可状态不变 |
| 14 | 作者默认sans8.5pt；来源6.4pt，100dpi | 原样保留 |
| 15 | 小号DejaVu Serif来源7pt；方志页脚与地图一体 | 原样保留 |
| 16 | 作者 Segoe UI11pt；来源9.3pt；日期Consolas10pt | 原样保留；不把 NJT 几何改署名为 OSM |

## 建议的统一字体规范

这是一个**带明确例外的标题系统**，不是强制把所有标题摆到同一位置。

以最终作品自身的有效画布宽度 `W` 为基准，而非文件 DPI 元数据，也不根据当前网页 70% 显示比例反向放大字体。

| Token | 字体 | 字重 | 基准字号 | 字距 | 行高 |
|---|---|---:|---:|---:|---:|
| Day / Theme | Segoe UI Semibold | 600 | `0.011 × W` | `+0.08em` | 1.25 |
| Main title | Georgia Regular | 400 | `0.028 × W` | 0 | 1.08–1.12 |
| Subtitle | Segoe UI Regular | 400 | `0.012 × W` | 0 | 1.30 |

主标题是 D 的约2.55倍，S 的约2.33倍。参考：1200宽作品为 T33.6 / D13.2 / S14.4px；1440宽为 T40.32 / D15.84 / S17.28px；2400宽为 T67.2 / D26.4 / S28.8px。SVG先按viewBox换算；Matplotlib先转换成输出像素，再除 `dpi /72` 求pt。

- D 与 T 相邻时，目标字形可见边缘间距约 `0.45T`；T 与 S 间距约 `0.25–0.35T`。先满足不遮挡、不移动地图，再决定是否需要调整现有标题槽内部的基线。Day 16 的 D 在画面顶端、T 在地图内，**不把二者强行拉到一起**。
- 文本超长先在现有标题槽里换行，行高1.1；不能随意缩小或删字。若换行会挤入地图主体，则该日保留既有字号并登记例外，不扩大标题区或推动地图。
- Day 02 使用左侧面板宽度作为受限标题槽参考；Day 10、12、13、14 保留已有较大 Georgia 尺度；Day 09、15 保留特殊设计。统一字体与层级，比机械追求同一个字号百分比重要。
- 不新增缺少的 D/S，不更改标题大小写或文字。Day 04 的 D 实际写的是 `CLUSTERS OF PLAY`，不是注册表的 `MY DATA`；本轮不纠正文案。Day 15 的成图实际是 `PHILADELPHIA / A GAZETTEER OF PLACES`，同样保留。
- CJK 副标题使用已存在的 Noto Sans SC fallback，例如 Day 11 的“水”；IPA、地图字形、表格数字、图例、注释、作者、来源全部不套主标题 token。
- Georgia / Segoe UI 是现有机器上的字体。审查包不复制或分发字体文件；跨平台渲染需核验实际 fallback 和字形宽度，不能只凭 CSS 声明认定输出一致。

## 三张 Before / After

- [Day 03 对比](previews/day03_before_after.png)：浅色多面板。仅将已有主标题改为 Georgia101；缺少的 D/S 不添加。
- [Day 04 对比](previews/day04_before_after.png)：深色统计地图。主标题由 Arial Bold58 改 Georgia67，D/S 改系列 sans；统计数字、灯光、连线、图例和来源不动。
- [Day 16 对比](previews/day16_before_after.png)：地图内两行标题。保留位置和文字，仅轻微调整主标题比例，并把副标题改为 sans，使其与主标题的区分更清楚；234 与其他统计完全不动。

**预览细节：**三张是静态排印样张，不是更新后的正式 GIF。D 的 `+0.08em` 是待确认的 tracking 规范，当前样张为默认字距，以便先审定字体和层级；不能把样张称为全部 token 均已落地。现有手工空格全部保留。三张预览也保留现有基线锚点，间距比例是下一阶段在标题槽内复核的目标，不宣称已对所有日期重排。

[预览脚本](scripts/render_previews.py) 从原生成脚本制作内存变体，[字体修改 diff](scripts/proposed_title_changes.diff) 记录对应改动。Day 03/04 的本地 GIS 渲染依赖会造成少量非文字抗锯齿差异，因此预览只把重新生成的**标题区**合成回原批准图，标题区外逐像素保持原样；Day 16 直接重绘后也通过非标题区域逐像素检查。最终批量修改时必须先解决重绘差异，或沿用这一受限文字层合成方式，不能把地图差异当作字体修改一并覆盖。

[preview_checks.json](preview_checks.json) 记录了三张的变化边界；三张的**非标题区域像素变化均为0**。没有重编码或缩短任何原GIF；没有修改交互事件、数据加载和网页布局。

## 批量阶段前的确认点

1. 是否接受 Georgia / Segoe UI 的主标题、D与S搭配，以及2.8% /1.1% /1.2%的基础比例。
2. 是否接受 Day 09、15 保留原设计，Day 02 受限面板与 Day 10/12/13/14 大字号构图保留例外。
3. Day 02 的 HTML / 导出标题不同、Day 05 的固定标题层缺少精确生成设置：本轮不擅自改字，也不宣称这些问题已解决。
4. 确认后才修改各日正式脚本、重生成必要帧、比较逐帧标题位置及原时长/循环、更新公开副本。当前只在 `typography_review/` 写入审查包。


## ???????

Day 02/10 ???GIF? `scripts/capture_collection.cjs` ????HTML?????? `scripts/animate_collection.py` ???????PNG??????Day 03/06/08/09 ???GIF??? `scripts/animate_collection.py` ? `scripts/collection_layers.py`????????????PNG???GIF????Day 05??????????Day 11???scene??????????????GIF???????loop?????asset_inventory.json?
