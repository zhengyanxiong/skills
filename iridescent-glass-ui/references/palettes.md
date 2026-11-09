# 主题色板与 Token 契约

## 为什么是这套 token，而不是「一个主色 + 一个金色」

朴素做法只有 `--primary` 和 `--gold` 两个颜色，于是按钮、边框、文字、光晕全用同一个值。结果是：
把 `#7FA7C7`（雾青）当按钮底色配白字，对比度只有 **2.54:1**，远低于 AA 要求的 4.5:1 —— 按钮在阳光下基本看不清。

所以这里把「同一个色相」拆成**承担不同职责的五个 token**：

| Token | 职责 | 对比度要求 |
|---|---|---|
| `primary` | 装饰、图标、强调底色（不承载小字） | 装饰 3:1 |
| `primary_deep` | 深端：标题、focus ring、需承字的实底 | 4.5:1 vs 正文 |
| `btn_from` / `btn_to` | 按钮渐变两端，**每一端都必须独立过 AA** | 4.5:1 vs `on_primary` |
| `base` | 60% 底色 | — |
| `text_main` / `text_sub` | 正文 / 次要文字 | 4.5:1 vs base 与玻璃复合色 |
| `gold` | 金砂装饰线（1px 分割线、包边） | 3:1 vs base |
| `gold_light` | 渐变中段、光晕（**永不承载文字**） | 不要求 |

`gold` 在浅色主题下比品牌金 `#C58A2A` 更深（雾青主题用 `#A8741F`），因为 `#C58A2A` 在月白底上只有 2.77:1，连装饰线的 3:1 都不到。

**10% 金砂点缀是装饰预算，不是文字预算。** 金色出现在包边、光晕、hover 流光里；一旦有文字压在金色上，就必须换成实测过的 `btn_to`。

## 内置六主题

| 主题 | `data-theme` | 主色 | 气质 |
|---|---|---|---|
| 雾青 | `mist`（默认） | `#7FA7C7` | 清透空灵 |
| 孔雀蓝 | `peacock` | `#0F7C90` | 沉静深邃 |
| 琥珀金 | `amber` | `#B67A1F` | 温暖琥珀 |
| 胭脂红 | `rouge` | `#A94A63` | 东方胭脂 |
| 葡萄紫 | `amethyst` | `#6F52C9` | 夜宴葡萄 |
| 月白灰 | `moon` | `#8E9EAC` | 素净月白 |

用法：`<html data-theme="peacock">`，暗色再加 `class="dark"` → `<html data-theme="peacock" class="dark">`。

## 实测对比度（`scripts/contrast_check.py` 输出）

浅色模式：

| 主题 | 正文/base | 次要/base | 白字/按钮终点 | 金线/base |
|---|---|---|---|---|
| mist | 11.64 | 6.41 | 4.58 | 3.76 |
| peacock | 12.37 | 6.15 | 4.88 | 4.09 |
| amber | 13.23 | 7.34 | 4.99 | 4.04 |
| rouge | 13.76 | 7.59 | 5.46 | 4.04 |
| amethyst | 13.67 | 7.34 | 5.64 | 4.37 |
| moon | 11.87 | 6.43 | 4.83 | 4.72 |

暗色模式（正文都在 15:1 以上，暗色下反而不紧张）：

| 主题 | 正文/base | 次要/base | 按钮墨字/终点 |
|---|---|---|---|
| mist | 15.70 | 9.04 | 9.50 |
| peacock | 15.13 | 8.91 | 7.13 |
| amber | 15.70 | 9.07 | 8.13 |
| rouge | 15.40 | 8.86 | 5.51 |
| amethyst | 15.54 | 8.94 | 6.36 |
| moon | 15.97 | 9.53 | 9.50 |

全表 96 对组合，0 失败。**改动任何颜色后必须重跑**：

```bash
python3 scripts/contrast_check.py assets/tokens.json
```

## 新增一个主题（四个步骤）

色板是数据，不是散落在 CSS 里的魔数。新增主题只改 `assets/tokens.json`：

1. **定主色**：选一个有明确色相的颜色，写进 `primary`。
2. **派生深端与按钮端点**：`primary_deep` 压暗约 30%，`btn_from`/`btn_to` 压到「白字能过 4.5:1」的区间。经验值：白字要过 4.5:1，背景的相对亮度必须 ≤ 0.183，大致是压到 `#4E7A9C` 这个深度。
3. **配 base 与文字**：`base` 取主色的极淡tint（明度 96–98），`text_main` 用带环境色的深灰（不要纯黑），`text_sub` 必须过 6:1 才有余量。
4. **跑校验并生成 CSS**：

```bash
python3 scripts/contrast_check.py assets/tokens.json            # 必须 0 failing
python3 scripts/contrast_check.py assets/tokens.json --emit-css > assets/_tokens.generated.css
```

暗色映射不是「把浅色反过来」，而是**独立判断**：

- `base` 用带主色色相的深蓝黑（`#0D1418` 这类），不要 `#000`。
- 暗色下 `primary` 要**提亮**（深色底上深色强调看不见），按钮文字改用**墨色** `on_primary`，因为浅色填充 + 白字的对比度在暗色下依然不够。
- `primary_deep` 在暗色下比 `primary` 略深一点点即可，它承担渐变深端。
- 玻璃填充在暗色下是 `rgba(255,255,255,0.10)` —— 暗色玻璃靠极低的白叠加上浮，不能靠透明度加深。

## 60 / 30 / 10 的落地

| 比例 | 落在哪 | 常见错误 |
|---|---|---|
| 60% `base` | 页面底色、大块留白、`.glass-solid` | 用主色的 20% tint 当底色 → 整页发闷 |
| 30% `primary` | 环境光晕、按钮、强调块、图表主序列 | 主色铺满整个 hero → 失去「透光呼吸感」 |
| 10% `gold` | 1.5px 包边、1px 分割线、hover 流光、徽章 | 金色做大面积填充 → 廉价，且对比度全线崩 |

比例不是审美偏好，是**可读性预算**：底色越花，压在玻璃上的文字越难救。

## 相关文件

- `assets/tokens.json` — 唯一数据源，所有颜色在这里改
- `assets/_tokens.generated.css` — 生成产物，勿手改
- `scripts/contrast_check.py` — 校验 + 生成，`--json` 出机读结果供 CI 用
- `references/accessibility.md` — 为什么这些数字是这样算的
