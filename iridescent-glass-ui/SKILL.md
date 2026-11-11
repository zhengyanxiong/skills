---
name: iridescent-glass-ui
description: >
  幻彩琉璃 (Iridescent Glass) 全场景 UI 设计系统 — 高透光毛玻璃、流体圆角、渐变金属包边、
  环境光晕与流光交互，内置 6 套东方主题色板（雾青/孔雀蓝/琥珀金/胭脂红/葡萄紫/月白灰）
  与明暗双模式，所有文字/背景组合已通过 WCAG AA 实测。
  Use this skill whenever the user asks for: 琉璃风、幻彩、玻璃拟态、glassmorphism、
  glass UI、毛玻璃界面、晶莹 / 通透 / 空灵 / 仙气 / 高级感的设计、东方美学 UI、
  水晶质感、渐变金属边、光晕背景、国风仪表盘、高端 landing page、
  or wants to restyle an existing page into a translucent frosted-glass look with
  serif display type and gold accents. Also use when picking theme palettes or
  checking contrast/fallback behaviour for glass surfaces — even if the user never
  says "琉璃" or "glassmorphism" out loud.
license: MIT
compatibility: >
  纯 CSS，无构建步骤、无 JS 依赖。需要支持 backdrop-filter 的现代浏览器；
  不支持时自动降级为近不透明表面（见 references/accessibility.md 的降级矩阵）。
metadata:
  author: 熊仔
  version: "1.0"
  category: frontend-design
  tags: [ui, design-system, glassmorphism, css, theming, accessibility, wcag, dark-mode, east-asian-aesthetics]
---

# 幻彩琉璃 · Iridescent Glass

## 这套风格的可辨识特征

三个特征同时出现，才叫琉璃；缺一个就退化成普通的圆角卡片：

1. **透光** — 半透明表面 + 背景模糊，能看见后面的光斑在动
2. **包边** — 1.5px 金属渐变描边，像水晶切面镶了金
3. **光斑** — 页面底层有大面积模糊色晕，不是纯色背景

再加一条排版骨架：**衬线体承情绪，无衬线体承信息**。大标题和大数字用宋体，正文和控件用黑体。

## 何时不要用

这套风格成本不低（模糊层、字体、对比度预算），以下场景换别的：

| 场景 | 原因 |
|---|---|
| 密集数据表、后台管理系统 | 玻璃表面对齐和扫读都差，用素色表格 |
| 长时间阅读的正文页 | 背景光晕干扰视线，用纯色阅读版式 |
| 低端设备为主的场景 | 模糊层是 GPU 开销大头 |
| 需要在照片/视频上叠加内容 | 改用 `.glass-solid`，或干脆不用玻璃 |

## 工作流

### 1. 定主题，不要现场调色

六套主题已实测过对比度。先问用户要哪个色系，没有偏好就用 `mist`（雾青）。换主题只切 `data-theme`，不要改 CSS。

需要新色系时，按 `references/palettes.md` 的四步派生，并**必须**跑校验脚本 —— 手工挑的颜色几乎不可能刚好过 AA。

### 2. 搭骨架

```html
<html lang="zh-CN" data-theme="mist">
  <body>
    <div class="ambient" aria-hidden="true"></div>
    <header class="glass-nav">…</header>
    <main class="page stack">…</main>
  </body>
</html>
```

引入两份 CSS，顺序不能反（第二份 `@import` 第一份）：

```html
<link rel="stylesheet" href="iridescent-glass.css" />
```

`.ambient` 是光斑容器，必须是空的独立节点且 `aria-hidden`。

### 3. 排内容：先定 60/30/10

| 比例 | 内容 |
|---|---|
| 60% | 底色、留白、非玻璃区块 |
| 30% | 主色：按钮、强调块、图表主序列、光晕 |
| 10% | 金砂：包边、1px 分割线、徽章、hover 流光 |

金色是**装饰预算**。一旦有文字压在金色上，就换成实测过的 `--theme-btn-to`。

### 4. 选组件

组件清单、HTML 片段、以及"什么场景不该用玻璃"的对照表在 `references/components.md`。

高频组合：`.glass` 卡片 + `.display-1` 标题 + `.btn` 主按钮 + `.glass-input` 表单 + `.card-grid` 栅格。

### 5. 交付前跑校验

```bash
python3 scripts/contrast_check.py assets/tokens.json
```

退出码 0 才算完成。改了任何颜色都要重跑 —— 肉眼判断玻璃上的文字对比度不可靠。

## 五条材质法则（附原因）

### 圆角：卡片 24–32px，按钮胶囊

直角会把"水流"打断。琉璃的形态语言是液体凝固的瞬间，转角处的曲率必须连续。大面积用 `--radius-card`（24px），大面板用 `--radius-card-lg`（32px），按钮用 `--radius-pill`（99px）。

同一个容器内的圆角要成倍数关系，24 / 12 / 99 —— 随机取值会让边缘互相打架。

### 玻璃：`backdrop-filter: blur(24px) saturate(180%)`

只写 `blur` 出来的玻璃是灰的，因为模糊会把色彩的饱和度一起抹平。`saturate(180%)` 把颜色找回来，这才是"水晶"而不是"磨砂塑料"。

模糊值不要超过 24px：40px 以上在中端安卓上单帧超 30ms。导航条可以降到 20px（面积小，视觉差异不明显）。

alpha 不要低于 0.30 —— 再低就无法给出稳定的文字对比度保证。

### 包边：1.5px 渐变 + mask 遮罩

包边不是 `border`，是**挖出来的一圈渐变**：元素自身填充渐变，用 `mask-composite` 只留下 `padding` 厚度的那一圈。这样拐角处的渐变是连续的，而不像 `border-image` 那样在圆角处断开。

渐变走向 `金 → 浅金 → 主色`，模拟水晶切面在不同角度折射不同色。中点用 `--theme-gold-light` 而不是纯白 —— 纯白会让包边看起来像描边失败。

`mask-composite` 不被支持时已经内建退回 `1px solid var(--theme-gold)`，所以不用自己写降级。

### 光晕：径向渐变，不要 blur

页面底层两枚色斑（右上一枚主题色、左下一枚金砂）。实现上是多段 `radial-gradient`，**不要加 `filter: blur()`**：

- 渐变本身已经是平滑衰减，blur 在视觉上几乎没有增益
- 而 blur 作用在 60vw 的 `fixed` 元素上，每次合成都处理一块巨大的离屏表面，滚动时开销很明显

光斑的不透明度 0.42 → 0.18 → 0.05 → 0，三段衰减比两段更接近真实的折射散焦。

### 动效：缓动函数模拟水，只动 transform

所有过渡用 `--ease-fluid`（`cubic-bezier(.175,.885,.32,1.275)`，带轻微回弹）或 `--ease-soft`。线性缓动是机械的，琉璃是柔的。

只对 `transform` 和 `opacity` 做动画。改 `left`/`width`/`top` 会触发 layout，流光动画会变成每帧重排。

`will-change` **不要常驻**：每个带 `will-change` 的元素都占一个合成层，20 张卡片就把移动端 GPU 内存吃满。用 `.is-live` 在动画期间临时加，结束移除。

**动效由交互触发，不按定时器循环。** 按钮绸光写成 `animation: btn-shine 4s infinite` 是错的——它每 4 秒抢一次注意力，而读者可能只想读按钮上的字。正确写法是绑到 `:hover` / `:focus-visible`，一次扫完就停：

```css
.btn:not(:disabled):hover::after,
.btn:not(:disabled):focus-visible::after {
  animation: btn-shine 0.75s var(--ease-soft) 1;
}
```

同样的原则适用于任何装饰动画：**动效应该是"响应"，不是"噪音"**。判断标准就一句——内容没变，它凭什么一直动？

## 排版

| 元素 | 字体 | 用途 |
|---|---|---|
| `.display-1` / `.display-2` | `--font-display`（宋体栈） | 大标题、大数字 |
| 正文、按钮、表单 | `--font-body`（黑体栈） | 所有信息载体 |

字体栈已内置系统回退（`Songti SC` / `SimSun` / `PingFang SC`），所以**不加载 webfont 也能看**。要正版思源宋体时注意体积：完整 CJK 衬线包接近 10MB，必须子集化，见 `references/accessibility.md` 第 5 节。

`.text-iridescent` 只用于 2–6 字的强调。整句渐变会让行末颜色变淡、对比度掉到不合格。

**但它不能用在数字上。** 指标、统计、价格这类要"一眼读清"的内容一律用实色 `--theme-text-main`。渐变是沿字符流动的，同一个数字的不同笔画亮度不同，读一个 `96` 要多花一瞬——这一瞬就是装饰挤占功能。第三方检测器（`impeccable detect`）会直接把渐变文字标成 AI 生成痕迹，标题和指标是两个重点扫描区。

## 硬约束（不可协商）

这几条是 WCAG 要求，不是审美偏好：

1. **正文和次要文字的对比度 ≥ 4.5:1**，按**复合后**的背景色算（玻璃卡片比页面底色更亮，所以对比度更低）
2. **包边、图标等非文本元素 ≥ 3:1**
3. **键盘焦点必须可见**：`:focus-visible` 有 2px `outline` + 3px offset，且不能只靠颜色变化
4. **错误状态不能只靠红色**传达，要有文字说明 + `aria-invalid`
5. **`prefers-reduced-motion` 下停止所有动效**，`prefers-contrast: more` 下玻璃退回不透明

细节、降级矩阵、浏览器坑都在 `references/accessibility.md`。

## 反模式

| 反模式 | 为什么错 | 正确做法 |
|---|---|---|
| 纯黑 `#000` 或纯白 `#FFF` 当文字色 | 与有色环境光冲突，看起来像贴上去的 | 用带环境色的 `--theme-text-main` / `--theme-text-sub` |
| 实色 `1px solid #ccc` 分割线 | 生硬直线破坏连续性，且灰色与主题色不搭 | `.gold-rule` 金砂渐隐线 |
| 大面积实心无透明度色块 | 丢掉"透光呼吸感"，风格塌成普通卡片 | 保留 alpha，或改用 `.glass` |
| 玻璃套玻璃（两层以上） | 模糊层叠，低端机掉到 20fps；视觉上层次糊成一片 | 外层改 `.section-quiet`（无表面，靠间距 + 发丝线分隔），内层保留唯一一层玻璃 |
| 指标数字用 `.text-iridescent` | 装饰挤占功能，读数变慢；检测器标记为 AI 痕迹 | 数字用实色 `--theme-text-main`，渐变留给标题里 1–2 个字的强调 |
| 常驻 `animation: … infinite` 的装饰动效 | 每几秒抢一次注意力，读者只想读字却一直在动 | 绑到 `:hover` / `:focus-visible`，`iteration-count: 1` |
| 玻璃上压长段落正文 | 背景光晕让视线不断被拉走 | 长文用纯色版式，玻璃只做容器 |
| 主按钮渐变里混入金色 | 白字在金色端对比度不够（`#C58A2A` 上白字仅 2.98:1） | 用实测过的 `btn_from → btn_to`，金色留给包边和流光 |
| 每个卡片都加 `will-change` | 合成层爆炸，GPU 内存耗尽 | 只在动画期间加 `.is-live` |
| 给玻璃元素加 `overflow: hidden` | Safari 会丢掉 `backdrop-filter`，玻璃变白板 | 让内容自己滚，或调整内边距 |
| `filter: blur()` 做光斑 | 巨大离屏表面，滚动时明显卡顿 | 多段 `radial-gradient` |

## 交付前自检

```
[ ] python3 scripts/contrast_check.py assets/tokens.json  → 0 failing
[ ] Tab 键走一遍，每个可交互元素都有可见焦点环
[ ] 系统开「减少动态效果」，流光与上浮停止
[ ] 缩到 320px 宽，胶囊按钮不换行溢出
[ ] 切暗色，卡片是烟水晶而不是发白的塑料
[ ] 打开 assets/demo.html，六个主题逐个切换无颜色断层
[ ] 一屏内玻璃元素不超过 12 个
[ ] 正文没有压在渐变金色上
[ ] 指标数字是实色，没有用 `.text-iridescent`
[ ] 没有常驻循环动画：`grep -n "infinite" assets/*.css` 只应剩光晕这类无位移的
[ ] （可选，装了 impeccable 才跑）`impeccable detect assets/demo.html` —— 剩余项每条都要能说出理由
```

## 文件与加载顺序

按需加载，不要一次性全读：

| 文件 | 什么时候读 |
|---|---|
| `assets/tokens.json` | 改色、加主题（唯一数据源） |
| `assets/iridescent-glass.css` | 拷贝组件样式、看降级实现 |
| `assets/demo.html` | 需要完整样张 / 视觉回归基线 |
| `references/palettes.md` | 选主题、派生新主题、看实测数值 |
| `references/components.md` | 写页面、判断某场景该不该用玻璃 |
| `references/accessibility.md` | 对比度算法、性能预算、浏览器坑、CJK 字体 |
| `scripts/contrast_check.py` | 校验色板；`--emit-css` 重新生成 token 的 CSS 变量 |

`assets/_tokens.generated.css` 是生成产物，**永远不要手改** —— 改 `tokens.json` 后重新生成：

```bash
python3 scripts/contrast_check.py assets/tokens.json --emit-css > assets/_tokens.generated.css
```
