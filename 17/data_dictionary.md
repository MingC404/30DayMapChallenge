# 灯光数据字典

对应 `light_inventory.csv`；UTF-8 BOM、标准 CSV 引号，JSON 列可能包含逗号。空字符串表示没有取得可用值，**不是 0、恒明或无扇区的证明**。坐标为 WGS84，经度在前、纬度在后；时间字段以 UTC 保存。统计与范围见 `data_feasibility.md`。

## 灯光属性的含义

| 属性 | 含义与限制 |
|---|---|
| Fl | 闪光；每周期的发光时间少于黑暗时间。单独 Fl 不能给出单次闪光秒数。 |
| Fl(3) 6s | 每 6 秒重复三闪组；不能推出三闪各持续多久、组内间隔多长。 |
| Fl(2+1) | 复合组闪；保留组内结构，不能只写成“3 闪”。 |
| Oc | 明长暗短的遮断光。周期不等于熄灭时长。 |
| Iso | 等明暗；有明确周期 T 时，可依定义设亮 T/2、暗 T/2。该推导须与原始 SIGSEQ 分列。 |
| Q / VQ / UQ | 快闪 / 甚快闪 / 超快闪。类型不直接决定某个对象的准确周期；以对象的 SIGPER/SIGSEQ 为依据。 |
| F | 恒明；没有周期不属于缺失闪光周期。不是旋转光束。 |
| Mo(A) | Morse 字母 A 组；字母不是普通闪光次数。仍需要 SIGPER/SIGSEQ 才能确定实际秒数。 |
| STROBE | 频闪描述；不能据此给定周期、灯色或脉冲宽度。 |
| W / R / G / Y / Bu / OR | 白 / 红 / 绿 / 黄 / 蓝 / 橙。与浮标本体的红绿外观分开。 |
| LIGHT_CHAR | USCG 组合文本，可能同时含灯质、分组、灯色、周期。完整原文优先保存。 |
| LIGHT_NOM_RANGE | USCG 标称射程；与单位字段一起读。不是实际可见覆盖面。 |
| LIGHT_FOCAL_PLANE | 灯焦点高程；不是灯塔结构高度，也不是观察者眼高。 |
| REMARK | 可能含角度扇区、导标可见宽度、雾号、passing light、运行条件；不可混淆声音和光。 |
| COLOR / DAYMARK_COLOR | USCG 航标本体或日标颜色，不能拿来补灯光颜色。 |
| SIGPER | NOAA 信号完整重复周期，单位秒；不是单闪持续时间。 |
| SIGGRP | NOAA 分组字符串，`(1)` 表示单组单闪编码，`(2+1)` 保留复合结构，`(A)` 为 Morse 字母。恒明无组码正常。 |
| SIGSEQ | NOAA 明暗序列，未加括号的时长为亮，加括号的时长为暗，`+` 连接。例如 `00.3+(02.2)` 为亮 0.3 秒、暗 2.2 秒。不是从 Fl 文本猜测。 |
| COLOUR | NOAA S-57 灯色列表；本次用到代码 1=白、3=红、4=绿、6=黄；保留原代码。 |
| LITCHR | NOAA S-57 灯质枚举；匹配使用 1=F、2=Fl、3=LFl、4=Q、5=VQ、6=UQ、7=Iso、8=Oc、12=Mo。未识别的枚举不自行翻译。 |
| SECTR1 / SECTR2 | 真北参考的扇区起止方位，度。跨北扇区可能 start > end；不是错误，也不是零宽度。遵守从海上看灯的方位约定，未来绘图须核对向外画射线时的方向转换，不能直接将角度当投射方向。 |
| ORIENT | 方向信息，度；本次匹配值全空。空 ORIENT 不抹去 SECTR1/2 已知的方向边界。 |
| VALNMR | NOAA 标称射程（海里），可以因同址不同颜色或 passing light 而不同，不能简单取最大值当真实覆盖。 |
| HEIGHT | NOAA 灯高；需结合垂直基准，不与 USCG STRUCTURE_HEIGHT 自动互换。 |
| CATLIT / EXCLIT / LITVIS / STATUS | 灯光类别、光的显著性、可见性、状态等 S-57 枚举。保留原值；不在缺少解释时转成“正常运行”布尔量。 |
| SORDAT / SORIND | 要素来源日期 / 来源标识。SORDAT 可以很旧；它不是 ENC 最新更新日期。 |
| DSID_EDTN / UPDN / UADT / ISDT | 原始 ENC 的 edition、update number、update application date、issue date；用于判断本轮读入了哪个版本。 |
| LNAM | ENC 要素长名称/标识，用于跨比例尺去重；不是 USCG LLNR。多个颜色扇区可各有 LNAM。 |

SIGSEQ 的括号解释见 [IHO S-65 Annex C, §29.25](https://iho.int/uploads/user/pubs/standards/s-65/S-65%20Annex%20C_Ed%201.0.0_FINAL.pdf)。USCG 灯质、射程、备注与日标定义见 [Light List Preface](https://navcen.uscg.gov/sites/default/files/pdf/msi/Light_List_Preface.pdf)。不得为缺少扇区属性的灯补写 0–360°；参见 [IHO ENC Encoding Bulletins](https://docs.iho.int/mtg_docs/enc/enc_prod/S-57EncodingBulletins.htm)。

## 清单列

| CSV 列 | 解释 |
|---|---|
| llnr | USCG LIGHT_LIST_NUMBER，十进制登记号；消除浮点尾差，最多保留 4 位小数。不是浮标表面编号。 |
| llen_uid / aid_uid / lsys_uid | 原始登记条目、设施、灯系统标识。统计单位为 llen_uid，保留其他标识便于审计。 |
| name | 原始官方名称，通常包含航道及航标编号。 |
| longitude / latitude | 原始 GeoJSON 点坐标，经度 / 纬度（度）。输出多位小数不代表厘米级准确。 |
| waterway | USCG HWATERWAY_NAME；范围筛选依据。 |
| type | lighthouse / lighted_beacon / lighted_buoy / other_light。分类优先级见报告。 |
| classification_evidence | DESCRIPTION_TYPE、AID_SUBTYPE、STRUCTURE_TYPE，按 `|` 分隔。 |
| confirmed_light | 本轮跨源确认属于灯光登记对象；不表示正在运行。37032 由 LB 分类、名称与唯一近邻 ENC 补证。 |
| confirmation_source | 上述确认依据；绝大多数是 USCG LIGHT_CHAR。 |
| uscg_has_characteristic | USCG 原始 LIGHT_CHAR 是否非空。 |
| light_characteristic_raw | 完整 USCG LIGHT_CHAR；37032 留空，不把 NOAA 文本冒充 USCG 原文。 |
| characteristic_type | 直接从 USCG 原文读出的 F、Fl、Iso、Q 等；STROBE 的枚举列留空，原文仍在。 |
| uscg_colors / light_colors / color_source | USCG 主灯色 / 主灯色经 ENC 补缺的结果 / 依据。扇区其他颜色另见 sector_enc_json。 |
| uscg_period_s / period_s / period_source | USCG 明示周期 / 经 ENC 补缺的周期 / 依据。F 的周期空值正常。 |
| flash_group / flash_group_source | 显式分组或 NOAA SIGGRP 补充；不抹去 Morse 字母或复合组结构。 |
| exact_sequence_raw | 通过校验的原始 NOAA SIGSEQ；Iso 推导不会写入此列。 |
| exact_sequence_json | 该原始序列的 `state=on/off, seconds` 数组。 |
| exact_sequence_source | 对应 `cell:LNAM`，分号分隔；原始证据可追溯。 |
| sector_status | explicit_absolute_angles=有明确数值边界；relative_width_only=仅相对导标线宽度；range_line_only=仅知导标线；not_documented=无可用扇区资料。 |
| sector_uscg_text | 与扇区/导标方向相关的原始 REMARK；可能同时包含雾号文字，不能全按灯光解析。 |
| sector_enc_json | 每个明确扇区的 cell、lnam、colour、start、end。未取得扇区为 `[]`。 |
| orient_enc_values | 匹配 ENC 的 ORIENT 非空值列表，本次均为空。 |
| nominal_range_nm / nominal_range_unit | 保留 USCG 主灯标称射程和单位；本次非空值单位为 NAUT MI。NOAA 组件值在 enc_matches_json。 |
| focal_height / focal_height_unit | USCG 灯焦点高度与原始单位，通常 FT。 |
| enc_match_status | position_and_characteristic_agree / position_only_uscg_characteristic_missing / ambiguous / no_candidate_within_25m / attribute_conflict。不是官方跨源身份保证。 |
| enc_matches_json | 可接受的匹配及距离、LNAM、cell、光学字段、要素来源日期/状态。保留多个扇区与组件。 |
| nearby_enc_ids | 25 米内所有候选，含未接受者。便于人工检查同址灯及冲突。 |
| reliable_period_animation | 有可验证单灯明暗时序：原始 SIGSEQ，或明确周期的 Iso 定义；不含恒明灯，不代表实时运行或同步相位已知。 |
| animation_timing_basis | explicit ENC SIGSEQ / Iso definition / fixed light / insufficient。 |
| animation_note | 可复现范围与相位限制说明。 |
| steady_light | 原文是否为 F 恒明灯。 |
| operation_condition | docking only / seasonal or ice-dependent / no extra condition recorded; live status unverified。是筛选提示，不是实时状态。 |
| audit_notes | 匹配歧义、主灯缺失、附属 passing light、雾号及运行条件的审计提示。 |
| remarks | USCG 原始备注；37032 的跨源说明明确标注，原始空备注仍可在 GeoJSON 找到。 |
| structure_description | 原始 STRUCTURE_REMARK，含外观/结构描述。 |
| season_from / season_to | 原始季节性边界，可能只填一端。不能把空值理解为全年运行。 |
| inactive | USCG 原始 INACTIVE 标记；本次全为字符串 0。 |
| uscg_source_file | 对应 District 01 分片文件名。 |
| uscg_modified_utc | 由 MODIFIED_DATE 毫秒时间戳转换的 UTC 时间；不是抓取时间。 |

## 缺失值与动画规则

1. `exact_sequence_raw` 非空才计入“有原始精确亮灭序列”；Iso 数学定义可另计动画可行性。
2. 只有正 SIGPER、可解析序列、时段合计匹配周期且无同址身份歧义，才接受 ENC 时序。没有原始序列时不推导 Fl 的脉冲宽度。
3. F 恒明的“无周期”是属性不适用。Q 只有灯质代码、无对象级时序时仍不足以指定准确秒数。
4. 同一条目的主灯、备用灯、passing light、不同色扇区可能有不同属性。CSV 主字段不意味着所有组件都相同。
5. 所有灯的相对起始相位未知；可制作公布节奏示意，无法复原历史某秒的港口全景。
6. 标称射程、实际可见范围、艺术光晕是三个概念。光晕没有物理单位，不能替代前两者。

所有原始 USCG 字段名逐文件列于 `raw/uscg_schema_audit.json`；所有原始 NOAA 属性保留于 `raw/enc_current_lights.json`。未列入精简 CSV 的字段没有从快照中删除。
