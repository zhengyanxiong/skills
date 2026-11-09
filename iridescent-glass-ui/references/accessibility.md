# 可访问性与性能

## 1. 为什么毛玻璃是对比度的陷阱

玻璃卡片的真实背景色不是 `--theme-base`，而是 `base` 与半透明白按 alpha 复合后的颜色。浏览器算的是复合色，人眼看的也是复合色。

```
composited = overlay × alpha + backdrop × (1 − alpha)
```

`base = #F4F7F8`，白 alpha 0.30 →
`0.30×255 + 0.70×244 = 255×0.3 + 170.8 = 247.3`（R），G≈249，B≈250 → 实际是 `#F7F9FA`。

这个偏移很小，但方向固定：**玻璃卡片永远比页面底色更亮**，所以深色文字在卡片上对比度**更低**，而不是更高。放在彩色光斑上的那一侧还要再降。

`scripts/contrast_check.py` 就是按这个公式复合的，跟浏览器一致。手算过 `#6B777E` 在月白底上"看起来够深"，实测只有 4.27:1（在玻璃复合色上 4.37:1）—— 不合格。所以 `text_sub` 统一压到 6:1 以上留余量。

## 2. 三个必须守住的硬指标

| 指标 | 要求 | 为什么 |
|---|---|---|
| 正文/次要文字 vs 复合底色 | ≥ 4.5:1 | WCAG AA 1.4.3 |
| 装饰线、包边、图标 | ≥ 3:1 | WCAG AA 1.4.11（非文本对比） |
| 焦点指示 vs 相邻色 | ≥ 3:1 | WCAG 2.4.11，且必须**可见地改变** |

玻璃的 alpha 不建议低于 0.30：低于这个值，背景的任何变化都会穿透到文字上，无法给出稳定的对比度保证。

## 3. 降级矩阵

`backdrop-filter` 不是所有环境都有（旧 Firefox、部分安卓 WebView、被系统关掉硬件加速的浏览器）。降级靠 `@supports` 分层，而不是 JS 检测：

| 能力 | 支持时 | 不支持时 |
|---|---|---|
| `backdrop-filter` | `rgba(255,255,255,0.30)` + blur | `rgba(255,255,255,0.72)` 近不透明 |
| `mask-composite` | 1.5px 渐变金属包边 | 退回 `1px solid var(--theme-gold)` |
| `background-clip: text` | 渐变文字 | 退回实色 `--theme-primary-deep` |
| `overflow: clip` | 不创建滚动容器（sticky 可用） | 退回 `overflow-x: hidden` |
| `prefers-reduced-motion` | 完整动效 | 动效降到 0.001ms，流光隐藏 |

四个降级里最危险的是**渐变文字**：如果不加 `@supports` 保护，`color: transparent` 会照常生效，标题直接消失。这不是样式退化，是内容丢失。

## 4. 性能：三个真实开销点

**① 环境光斑不要 blur。**
`filter: blur(100px)` 作用在 `position: fixed` 的 60vw 元素上，会让浏览器每次合成都处理一块巨大的离屏表面。而 `radial-gradient` 本身就是平滑衰减的，blur 在视觉上几乎无收益。所以本样式表用多段 `radial-gradient` 近似衰减，不写 blur。

**② `will-change` 不是免费的。**
每个带 `will-change: transform, backdrop-filter` 的元素都会分配一个独立合成层。20 张卡片 = 20 个层，移动端 GPU 内存直接爆。所以它只挂在 `.is-live` 上，由 JS 在动画期间临时加、`animationend` 后移除：

```js
card.addEventListener("pointerenter", () => card.classList.add("is-live"));
card.addEventListener("animationend", () => card.classList.remove("is-live"));
card.addEventListener("pointerleave", () => card.classList.remove("is-live"));
```

**③ 只动 `transform` 和 `opacity`。**
流光按钮原本用 `left: -100% → 200%`，每帧触发 layout。改成 `translateX()` 后整段动画在合成器上跑完，布局零参与。

其他约束：

- 一屏内玻璃元素控制在 **12 个以内**（含卡片、导航、输入框）。
- 模糊半径 ≤ 24px。40px 以上的 `backdrop-filter` 在中端安卓上单帧超过 30ms。
- 不要给玻璃元素加 `overflow: hidden` —— 除了会丢 Safari 的 blur，还会强制创建裁剪上下文。

## 5. CJK 衬线字体的体积问题

`Noto Serif SC` 完整包 **接近 10MB**（简体常用字 8000+）。直接 `<link>` 会让首屏空窗几百毫秒，标题要么闪一下要么根本没字。

三种处理，按场景选：

| 场景 | 做法 |
|---|---|
| 只有标题用衬线 | 只加载标题需要的字符集（子集化），`font-display: swap` |
| 中文标题很长 | 用系统字体栈：`"Songti SC", "SimSun", Georgia, serif` |
| 快速原型 | 完全用系统栈，不加载 webfont |

本样式的字体栈已经内置系统回退，所以**不加载 webfont 也能看**，只是不够"宋"。子集化工具用 `fonttools pyftsubset`：

```bash
pyftsubset NotoSerifSC-Regular.otf \
  --text-file=headings.txt \
  --flavor=woff2 \
  --layout-features='*' \
  --output-file=NotoSerifSC-subset.woff2
```

## 6. 照片/视频背景

毛玻璃无法对任意背景保证对比度 —— 一张白墙和一张雪景会让同一个卡片变成两个颜色。照片上的面板加 `.glass-solid`：

```html
<div class="glass glass-solid">…</div>
```

`.glass-solid` 用不透明的 `--theme-base`，并用 `!important` 关掉 backdrop-filter，确保不被 `@supports` 块覆盖。

## 7. 用户偏好

| 偏好 | 响应 |
|---|---|
| `prefers-reduced-motion: reduce` | 动效时长归零、流光隐藏、hover 位移取消 |
| `prefers-contrast: more` | 玻璃退回不透明底色、包边不透明度拉满 |
| `forced-colors: active`（Windows 高对比） | 自定义阴影和渐变会被系统覆盖，确保不依赖它们传达信息 |
| 暗色 | `.dark` 类，映射见 `references/palettes.md` |

## 8. 浏览器坑

| 现象 | 原因 | 处理 |
|---|---|---|
| Safari 玻璃突然变白板 | 元素自身 `overflow: hidden` + 圆角 → blur 被丢弃 | 不要在玻璃元素上用 `overflow: hidden` |
| Firefox 包边渲染成整块 | 只写了 `-webkit-mask-composite` | 同时声明 `mask` 与 `mask-composite` |
| 渐变文字在 iOS 15 隐形 | `background-clip: text` 需要 `-webkit-text-fill-color` | 用 `@supports` 包裹 `transparent` |
| 页面横向出现滚动条 | 光斑超出视口 | `overflow-x: clip`，并把光斑放进 `.ambient` 裁剪容器 |
| sticky 导航失效 | 祖先有 `overflow-x: hidden` | 改 `clip` |

## 9. 提交前必须跑

```bash
python3 scripts/contrast_check.py assets/tokens.json     # 必须 0 failing
```

CI 里用 `--json` 判断退出码即可：

```yaml
- run: python3 scripts/contrast_check.py assets/tokens.json
```

退出码 0 = 全部达标，1 = 有组合低于要求，2 = 输入文件有问题。
