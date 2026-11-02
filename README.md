# NYC Changing Station Explorer

静态地图：`outputs/nyc_changing_station_explorer.html`。使用 Go Live 或本地 HTTP 服务打开。

## 生成与查看

Python 3.9+，仅标准库；无需 pip 安装或后端。在项目根目录运行：

```powershell
python scripts/build_changing_station_explorer.py
python -m http.server 8000 --bind 127.0.0.1
```

访问 <http://127.0.0.1:8000/outputs/nyc_changing_station_explorer.html>。也可用 VS Code Go Live，不使用直接打开本地 HTML 的方式。

本机可将 `python` 替换为 `& C:\Users\Yiming\.conda\envs\geospatial\python.exe`。脚本按项目根目录定位文件，使用 `scripts/explorer_template.html` 生成页面。

生成 HTML 时会同步 `docs/nyc-changing-stations/index.html` 及所需本地署名资源。修改数据或视觉后，再运行下述 GIF 导出命令，自动同步新的 PNG/GIF 预览。

## 固定底图与初始筛选

固定使用 **Light streets＋无填色五区 outline**：单色 OpenFreeMap 浅灰街道、少量城市标签，并叠加本地五区细边界（`fill: false`、`fillOpacity: 0`），不覆盖道路。已移除 Compare basemaps 控件与切换逻辑。需要网络和 WebGL，[官方服务无需 key](https://openfreemap.org/)；署名保留，加载失败提示错误，不自动更换底图。

网页首次打开时四类均不勾选、没有 POI 点，**0 matching records**。勾选后按原 OR 逻辑显示；Select all 显示 795 条，Clear 恢复 0 条。生成数据中的 `initialSelectedKeys` 明确为空数组。此默认值仅影响交互网页；GIF 导出脚本独立设置每个状态，PNG/preview.png 仍显式显示全部 795 条。

默认地图几何来自 **NYC Department of City Planning (DCP)** 的 [NYC Open Data Borough Boundaries](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne)，官方元数据标为 **26b**，排除水域。保留原始 GeoJSON、官方元数据、15m 简化后的本地几何和来源说明，详见 [`data_raw/boundaries/README.md`](data_raw/boundaries/README.md)。没有用点数据推测陆地。

页面加载 Leaflet 1.9.4、MapLibre GL JS 5.6.2、MapLibre GL Leaflet 0.1.3，以及在线矢量瓦片、字体与图标。所有 JS/CSS CDN 版本固定。没有离线瓦片下载或批量预取。

Light streets 样式基于保留的 `data_raw/basemap/openfreemap_positron.json` 快照，由生成脚本改为单色，并隐藏多余图层。原始样式与上游许可文件保留，参见同目录说明。不使用 CARTO。

初始缩放比上版再提高 0.5 级（原五区 fitBounds 的缩放 +1.0），中心为 40.735, -73.96；Reset view 恢复该视野。View all locations 完整覆盖所有 795 条有效换尿布台记录，不改变筛选，也不删除外围记录。区名锚点来自边界几何的内部点，放大后部分区名可能在视窗外。

## Tooltip 和点击详情

Tooltip 按以下顺序，逐记录省略缺失项：

1. 名称（加粗）
2. Location type · Operator
3. Hours
4. Accessibility
5. Changing table
6. Restroom
7. Status

卡片约 280px，白底、自动换行、边缘防溢出。长时段原文最多显示三行，Click for details 可读取完整内容；没有改写时间、季节或限制含义，也不计算 Open now。Original changing-table label 仅在点击详情中展示。

Popup 保留完整 Hours、原始 changing-table 标签、Location 备注、Access / entry、Accessibility、Restroom、Status、额外备注、合法网站链接，以及有独立信息的 Opening pattern。若 Opening pattern 已原文包含于 Hours，则省略重复行。Accessibility 和 Access / entry 分别展示，不混用含义。设施可用性提示统一位于侧栏，不在每张卡中重复。

空字符串、纯空白、N/A、NA、null、None、NaN、Not reported、Not available、Not applicable、Unknown、`-`、`--` 均按缺失处理，不区分大小写。Python 处理时也剥除包裹的双引号后检查占位值。地址没有独立字段，Address 行整体移除；其他字段即使别的记录有值，当前记录缺失也不显示。Access / entry 有真实备注，因此仅在有值的记录详情中保留。

HTML 数据值继续转义，JSON 转义 `<`、`>`、`&`；网站只接受 http/https。普通 Yes 仍仅表示换尿布台存在、放置类型未注明，不从其他字段推断。

## 字段完整性

以下数量已排除占位值，完整结果在 `outputs/nyc_changing_station_audit_v4.json`。Address、Location 和 Access / entry 的统计范围说明见表中说明。

| 字段 | 全部 1,066 条 | 展示 795 条 |
|---|---:|---:|
| 名称 | 1066 | 795 |
| Location type | 1066 | 795 |
| Operator | 1066 | 795 |
| Hours | 973 | 752 |
| Accessibility | 891 | 687 |
| Restroom type | 922 | 737 |
| Status | 1066 | 795 |
| 原始 Changing Stations 有效文本 | 979 | 795 |
| Changing table 放置类型（明确肯定记录） | 795 | 795 |
| Single-stall（明确标签支持） | 26 | 26 |
| Opening pattern | 993 | 758 |
| Address（无独立字段） | 0 | 0 |
| Location（明确位置备注） | 15 | 5 |
| Access / entry（明确进入条件备注） | 60 | 43 |
| Additional Notes | 71 | 49 |
| Website | 228 | 178 |

源 CSV 的 `Location` 实际为坐标 WKT，不作地址或文字位置使用。表中 Location 和 Access / entry 来自审阅过的 Additional Notes 原文，不根据名称、机构类型或周边地图生成事实。Accessibility 来自独立原字段。没有独立室内外字段，也不从 single-stall 推断 accessible 或 family restroom。

## 数据口径与保留文件

公共厕所输入为 `data_raw/family/Public_Restrooms_20261024.csv`。项目没有确证的数据更新日期或上游发布链接，2026-10-24 仅是文件名日期；边界下载日期与版本不代表厕所数据更新日期。

四类记录仍为 women **83**、men **27**、all-gender **26**、unspecified **659**，共 **795**。原始标签中 only 完整保留在 popup。匹配标记可重叠，多选为 OR，同一 CSV 记录只绘制一次、计数一次，不是地点去重；本批实际重叠数为 0。没有根据设施名称或其他字段中的 men/women 推断位置。single-stall 仅在明确标签支持时额外展示。

筛选列表第一项显示 **Restroom with changing table**，次要说明 **Restroom type not specified.**。其内部 key 仍为 `unspecified`，只对应原始 `Yes`，不自动匹配其他厕所类型。仅改显示名称和排序；tooltip 仍明确说明类型未注明。

沿用原版排除：No 174 条、空白 86 条、N/A, restrooms closed 8 条、N/A 1 条、N/A - closed for capital 2 条。全部运营状态纳入，不表示当前开放或可用。四条 No 与备注提及 Changing Table 的冲突继续列入审计而不改分类。

全部 1,066 条坐标检查均有效；缺失/非数值、全球越界、疑似颠倒、NYC 宽松矩形外均为 0。范围检查不是行政边界检查。点坐标未扰动、未聚类，颜色和 OR 筛选保持；同坐标仍可能互相遮挡。

旧审计 v1/v2/v3、本地历史输出备份和原散点图均保留。`scripts/plot_changing_stations.py` 的既有工作区改动未修改，不在本次提交清单中。

## 验证与截图

```powershell
python scripts/check_placement.py
node scripts/check_explorer.cjs
```

可选浏览器检查需要 Playwright：`node scripts/check_explorer.cjs --browser`。脚本创建仅本机可访问的临时 HTTP 服务，启动 Edge，结束后关闭浏览器和服务。可用 `PLAYWRIGHT_PATH` 指定外部模块、`BROWSER_PATH` 指定浏览器。Playwright 不是页面依赖。

已通过 HTTP 检查固定 Light streets + 无填色 outline、控件移除、首次空选与 0 点/0 条、16 种筛选组合的复选框/marker ID/总数、Select all/Clear、OR 去重、鼠标 hover/click、视野按钮与移动端布局。Light streets 检查真实加载和截图，不将占位瓦片视为成功。

最终学院提交 PNG：`outputs/nyc_changing_station_explorer.png`，全部 795 条类别显示。GIF：`outputs/nyc_changing_station_explorer.gif`。其他信息卡/底图 QA 截图仅供本地检查，不列入本次提交清单。

## 导出 GIF 与 PNG

依赖：Python + Pillow（`requirements-export.txt`）、Node.js、Playwright、浏览器。本次实测 Pillow 12.1.1、Playwright 1.64.1、Windows Edge。依赖仅用于导出，线上页面不运行 Python 或 Node。

```powershell
python -m pip install -r requirements-export.txt
npm install --prefix .export-tools playwright@1.64.1
$env:PLAYWRIGHT_PATH="$PWD\.export-tools\node_modules\playwright"
python scripts/build_changing_station_explorer.py
python scripts/export_changing_station_explorer.py
```

默认使用本机 Windows Edge。若使用其他浏览器，以 `BROWSER_PATH` 指定可执行文件。非 Windows 环境未指定路径时使用 Playwright Chromium，需要先运行 `.export-tools/node_modules/.bin/playwright install chromium`。也可通过 `PLAYWRIGHT_PATH` 指向已有 Playwright。`.export-tools/` 已忽略，不提交依赖或缓存。

Python 导出脚本调用 `scripts/capture_explorer.cjs`，先确认网页初始空选，再独立显式设置各帧类别，通过临时 HTTP 服务实际渲染网页；固定 **1200×900** 视窗、中心和缩放，仅切换筛选。顺序：全部 → 未注明类型 → women’s → men’s → all-gender → 全部。首尾各 3 秒，其余各 2 秒，6 帧合计 **14 秒**，无限循环；首帧保存为全部类别 PNG，不受网页默认空选影响。

每帧右上角有明确类别文字和记录数。鼠标移出地图，关闭 tooltip/popup；等待字体、瓦片和点绘制完成后截图。检查实际渲染的矢量几何、加载错误、固定视野、marker 数量及统计；底图缺失或 blocked 时导出失败，不覆盖最终 PNG/GIF。Pillow 使用共享 256 色调色板压缩，并解码全部 GIF 帧验证时长、色彩和差分帧。临时 PNG 在系统临时目录中处理，完成后自动清理。

`outputs/nyc_changing_station_export.json` 记录 GIF 文件大小、状态、数量、时长、视野、尺寸与底图验证信息。导出成功后自动更新 Pages 的 `preview.png` 和 `preview.gif`。

## 仓库核实与 GitHub Pages 文件

检查结果：`origin = https://github.com/MingC404/30DayMapChallenge.git`，分支 `main`，无 upstream。GitHub 公共 API 返回 404，不能据此判定 fork 或私有状态；用户已明确确认这是个人作品仓库并授权准备 `docs/`，记录于 `pages_config.json`。没有把它假设为学院 fork，也没有写入学院提交目录。

发布结构：

```text
docs/
  .nojekyll
  index.html
  nyc-changing-stations/
    index.html
    preview.png
    preview.gif
    credits/
      README.md
      boroughs.geojson
      LICENSE-openfreemap.md
      LICENSE-positron.md
```

地图 HTML 内嵌 CSS、应用 JavaScript、POI 数据、几何和样式，不依赖 docs 之外的本地文件；外部库、瓦片等使用 HTTPS。地图合集入口本次新建；后续已有 `docs/index.html` 会保留内容，只在缺少入口时添加链接。所有本地链接相对路径，兼容仓库子路径。署名和许可文件保留。

手动重新同步：`python scripts/prepare_pages.py`。生成地图和导出媒体也会自动同步。Pages HTTP 验证：

```powershell
node scripts/check_pages.cjs
```

该检查仅服务 docs，挂载到 `/30DayMapChallenge/`，核对发布 HTML/PNG/GIF 与 outputs 的 SHA-256 一致、链接未逃出 docs、本地资源及地图筛选均正常。日常预览也可运行 `python -m http.server 8000 --directory docs --bind 127.0.0.1`，访问 <http://127.0.0.1:8000/nyc-changing-stations/>。

用户检查并另行决定提交/推送后，按 [GitHub 官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)，进入仓库 **Settings → Pages → Deploy from a branch → main → /docs → Save**。若仓库为私有，Pages 支持取决于账户方案；当前未核实可见性或修改任何设置。配置和发布完成后的预期路径为 `https://mingc404.github.io/30DayMapChallenge/nyc-changing-stations/`，目前未发布，不能当作已上线地址。

## 提交准备

精确提交白名单见 [`COMMIT_FILES.txt`](COMMIT_FILES.txt)，未运行任何 git add、commit、push 或 PR 操作。旧版备份、旧审计、其他 QA 截图仅保留本地，不在本次清单中；已有 CSV 已追踪且未修改。也不包含 `scripts/plot_changing_stations.py` 的既有无关改动、`.vscode`、临时目录、依赖、缓存或凭据。

建议 commit message：`Add NYC changing station explorer with GIF export and Pages assets`。

检查清单后若以后决定暂存，可在 PowerShell 使用文件白名单，而非 `git add .`：

```powershell
$commitFiles = Get-Content COMMIT_FILES.txt
git add -- $commitFiles
git diff --cached --stat
```

此处仅提供后续命令，本轮没有执行。
