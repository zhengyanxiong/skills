# Vue 规范

## 工具（格式与语义分离）

- **Formatter：Prettier** —— 自动处理 `.vue` 三段（template/script/style）的缩进/换行/引号，**你不需要关心格式**。
- **Linter：ESLint + eslint-plugin-vue** —— 语义检查，三档规则（见下）。

## 语义要点（少量，真正要记住的）

- **组件命名多词**（`vue/multi-word-component-names`）：`UserCard` 不是 `Card`，避免与 HTML 元素冲突。
- **props 定义完整**（`vue/require-default-prop`）：类型 + 默认值（或 required）。
- **`v-for` 配 `key`**（`vue/require-v-for-key`）：列表渲染必须有唯一 key。
- **`v-if` 与 `v-for` 不同元素**：不要在同一元素上同时用，用 `<template>` 包一层。
- **`v-bind` 顺序、属性顺序**：按官方风格指南的推荐顺序组织。

## 规则集映射

eslint-plugin-vue 三档，对应 Vue 官方风格指南的优先级：

- `essential`（Priority C）：基础正确性，必须遵守（error）
- `strongly-recommended`（Priority B）：强烈推荐，提高可读性（error/warning）
- `recommended`（Priority A）：推荐，风格统一（warning）

落地时建议启用 `plugin:vue/vue3-recommended`（含 A/B/C 三档）。

格式由 Prettier 自动处理，你不用管。真正的规则以 `eslint.config.js` 配置为准。
