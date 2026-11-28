---
name: coding-standards
description: >
  编码规范总入口。声明「格式由 formatter 自动处理」，列出各语言的工具选型与语义要点，
  按语言路由到 references/ 或 alibaba-java-coding-guidelines。写 Java/Python/TypeScript/
  Vue/React 代码、或要求遵守编码规范时加载。
---

# 编码规范总入口

## 核心原则：格式与语义分离（最重要）

- **格式**（缩进、换行、引号、分号、空行）由 formatter 自动处理，你**不需要在生成时关心**。
- **语义**（命名、类型、错误处理、边界、结构）是你要遵守的，见各语言规范。

## 各语言工具选型

| 语言 | Formatter（格式，自动） | Linter（语义，会拦你） | 成文规范 |
|------|------------------------|----------------------|----------|
| Python | Ruff format | Ruff（E/F/UP/B/SIM/I） | PEP 8 + Google Python Style |
| TypeScript/React | Biome | Biome recommended preset | Google TS Style Guide |
| Vue | Prettier | ESLint + eslint-plugin-vue | Vue 官方风格指南 |
| Java | prettier-plugin-java | Checkstyle | 阿里手册黄山版（见下方路由） |

## 语言路由

生成代码前，按语言读对应规范：

- TypeScript / React → `references/typescript.md`
- Python → `references/python.md`
- Vue → `references/vue.md`
- Java → 加载 `alibaba-java-coding-guidelines` skill（327 条规约，强制/推荐/参考三档）

规则冲突时，语言规范优先。
