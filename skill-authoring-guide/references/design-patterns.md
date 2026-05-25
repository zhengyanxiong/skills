# Skill 设计模式详解

## 模式 1：工具封装器（Tool Wrapper）

**核心思想**：SKILL.md 使用 `load_skill_resource` 从 `references/` 加载规范文件，Agent 应用这些规则后瞬间成为领域专家。

**适用场景**：
- FastAPI 路由规范和响应模型规范
- Terraform 资源命名和模块模式
- PostgreSQL 查询优化最佳实践
- 内部 API 设计指南

**文件结构**：
```
api-expert/
├── SKILL.md              # 触发关键词 + 加载指令（无脚本，无模板）
└── references/
    └── conventions.md    # 规范、规则、最佳实践
```

**SKILL.md 示例**：
```markdown
---
name: fastapi-expert
description: FastAPI development best practices. Use when building, reviewing, or debugging FastAPI applications.
---

# FastAPI Expert Mode

## 激活规则
加载参考文档：`references/conventions.md`
确保所有生成的 FastAPI 代码遵循该文档中的规范。

## 审查代码时
1. 加载 conventions 参考文档
2. 逐条检查用户代码
3. 对每个违规项，引用具体规则并建议修复

## 编写代码时
1. 加载 conventions 参考文档
2. 严格遵循每一条规范
3. 为所有函数签名添加类型注解
```

## 模式 2：生成器（Generator）

**核心思想**：从结构化输入生成标准化输出。

**适用场景**：
- 接口文档生成
- 代码模板生成
- 配置文件生成
- 报表生成

**关键设计**：
1. 提供输入格式规范（用户应该如何提供信息）
2. 提供输出模板（减少模型"猜测"）
3. 包含边界处理（缺字段、缺类型等）

**示例**：API 文档生成 Skill

## 模式 3：审查器（Reviewer）

**核心思想**：按清单评分代码质量。

**适用场景**：
- 代码审查
- 安全审计
- 性能评估
- 规范合规检查

**关键设计**：
1. 定义明确的评分维度（正确性、完整性、一致性、安全性）
2. 区分严重级别（Critical / Warning / Suggestion）
3. 提供修复示例，而非仅指出问题

**示例**：Code Review Skill

## 模式 4：交互式（Inversion）

**核心思想**：Agent 先访谈用户，再执行任务。

**适用场景**：
- 需求不明确
- 需要收集多维度信息
- 复杂配置任务

**关键设计**：
1. 定义必须收集的信息清单
2. 每个问题解释为什么需要这个信息
3. 提供默认值和选项，减少用户输入成本

**示例**：项目初始化 Skill（先问技术栈、再生成配置）

## 模式 5：流水线（Pipeline）

**核心思想**：强制执行严格的多步骤工作流。

**适用场景**：
- 关务系统页面开发（7步流程）
- CI/CD 流程
- 数据迁移流程
- 标准化发布流程

**关键设计**：
1. 每步有明确的输入、输出、校验点
2. 前一步未完成不得进入下一步
3. 提供检查清单（Checklist）确保不遗漏

**示例**：越南关务页面开发 Skill
