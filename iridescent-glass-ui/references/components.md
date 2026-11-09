# 组件用法

样式在 `assets/iridescent-glass.css`，这里只讲**怎么组合、什么时候用哪个**。所有类名都是可拷贝的真实代码。

## 页面骨架

```html
<html lang="zh-CN" data-theme="mist">
  <head>
    <link rel="stylesheet" href="iridescent-glass.css" />
  </head>
  <body>
    <div class="ambient" aria-hidden="true"></div>
    <header class="glass-nav">…</header>
    <main class="page stack">…</main>
  </body>
</html>
```

`.ambient` 是必须的空节点：两枚光斑挂在它的伪元素上。写在 `body::before` 也可以，但独立节点能让你在不同路由下单独控制光斑层（比如登录页关掉、仪表盘加强）。

`aria-hidden="true"` 不能省——光斑是纯装饰，读屏器不该读到它。

## 玻璃卡片

```html
<section class="glass" style="padding: var(--space-6)">…</section>
<article class="glass is-interactive" tabindex="0">…</article>
```

- `.glass` = 表面 + 包边 + 阴影。**不包含内边距**，由使用处给（`var(--space-5)` 或 `--space-6`）。
- `.is-interactive` 才会 hover 上浮。静态卡片加上去会让用户以为能点。
- 可点的卡片必须同时是 `<button>` 或带 `tabindex="0"`，否则键盘用户点不到。

**什么时候不要用玻璃**：

| 场景 | 不要用 | 改用 |
|---|---|---|
| 正文段落 > 3 行 | `.glass` 上压长文 | 普通底色 + 细金线分隔 |
| 背景是照片/视频 | `.glass` | `.glass-solid` |
| 表格数据 > 20 行 | 每行套玻璃 | 一个玻璃容器 + 内部普通行 |
| 嵌套两层以上 | 玻璃套玻璃 | 内层用 `rgba(255,255,255,.06)` 纯色块 |

玻璃套玻璃会让模糊层层叠加，低端机直接掉到 20fps。

## 按钮

```html
<button class="btn">主操作</button>
<button class="btn btn--ghost">次操作</button>
<button class="btn btn--sm">小号</button>
<button class="btn" disabled>已禁用</button>
```

- 主按钮用 `--theme-btn-from → --theme-btn-to` 渐变，**两端都实测过 AA**。想换色改 tokens，不要临时改 `background`。
- 一个视图里主按钮只放一个。琉璃风格的主按钮自带流光，多个会互相抢。
- `.btn::after` 的流光靠 `transform` 动画，不加 `will-change` 也流畅；不要给它再加 `filter`。
- 禁用态只降透明度不加描边——禁用按钮仍然要能被看见。

## 渐变标题

```html
<h1 class="display-1">光在<span class="text-iridescent">琉璃</span>里拐了个弯</h1>
```

只用于**短促的强调**（2–6 字）。整句用渐变会让行末颜色变淡、对比度掉到不合格。

`@supports` 降级已内置：不支持 `background-clip: text` 的浏览器会看到实色 `--theme-primary-deep`，而不是隐形文字。

## 金线分隔

```html
<hr class="gold-rule" />
```

从金砂渐隐到透明。**不要用 `1px solid #ccc`**——生硬直线会破坏「水流」的连续感，且灰色与主题色不搭。

## 输入框

```html
<label class="text-sub" for="email">邮箱</label>
<input class="glass-input" id="email" type="email" placeholder="you@example.com" />
```

- `placeholder` 的 `opacity: 1` 是必须的（Firefox 默认降到 0.54，对比度直接不合格）。
- 焦点环同时有 `border-color` + `box-shadow` 光环，两者都要保留：单靠颜色变化在灰度打印或色觉障碍下不可辨。
- 错误态不要只靠红色：

```html
<input class="glass-input" aria-invalid="true" aria-describedby="err-1" />
<p id="err-1" class="text-sub" role="alert">邮箱格式不正确</p>
```

## 徽章

```html
<span class="badge">进行中</span>
<span class="badge badge--gold">金砂</span>
```

胶囊形、13px、带主色 tint 底。适合状态标签，不要塞超过 6 个字的文案。

## 弹层

```html
<div class="scrim">
  <div class="glass modal" role="dialog" aria-modal="true" aria-labelledby="t1">
    <h2 class="display-2" id="t1">标题</h2>
    <p class="text-sub">正文…</p>
  </div>
</div>
```

`.modal` 刻意**没有** `overflow: hidden`：Safari 在自裁剪的圆角元素上会丢掉 `backdrop-filter`，弹窗会突然变成白板。需要滚动就让它自己滚（已设 `overflow: auto`）。

## 提示条

```html
<div class="glass toast" role="status">已保存</div>
```

`role="status"` 让读屏器朗读；不要用 `alert`，`toast` 不是紧急信息。

## 典型组合

**数据卡三连**

```html
<section class="card-grid">
  <article class="glass is-interactive" tabindex="0" style="padding: var(--space-5)">
    <p class="display-2 text-iridescent" style="margin:0">96</p>
    <p class="text-sub" style="margin:0; font-size:14px">通过 AA 的组合数</p>
  </article>
</section>
```

数字用衬线体 + 渐变，说明用无衬线 + 次要色。这是整套风格的排版骨架：**衬线承情绪，无衬线承信息**。

**带背景图的 hero**

照片挂在**父层**，面板放里面；面板用 `.glass-solid`（不透明）：

```html
<section class="hero hero--dim" style="background-image: url(hero.jpg)">
  <div class="page">
    <div class="glass glass-solid" style="padding: var(--space-6)">…</div>
  </div>
</section>
```

照片上永远用 `.glass-solid`，毛玻璃无法保证照片任意区域的对比度。

注意 `.glass-solid` 只设 `background-color` 且带 `!important`。**不要**把 `background-image` 写在同一元素上 —— `!important` 的 `background` 简写会连图片一起清掉，这是踩过的坑。

## 自检

改完组件在浏览器里确认：

1. `Tab` 走一遍，每个可交互元素都有可见焦点环
2. 系统开「减少动态效果」，流光和上浮停止
3. 缩到 320px 宽，胶囊按钮文字不换行溢出
4. 切暗色，卡片不是发白的塑料感（应该是烟水晶）
5. 打开 `assets/demo.html`，六个主题逐个切换看有没有颜色断层
