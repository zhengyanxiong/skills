---
name: skill-first-workflow
description: >
  Use this skill at the START of every task and before EVERY action step.
  Enforces "Skill First" discipline: scan available skills before acting,
  load any skill with even 1% relevance, and follow the loaded skill's process.
  Triggers on: any user request, any implementation task, any design work,
  any debugging, any code review, any planning — essentially always.
  Make sure to use this skill whenever you receive a new user message,
  start a new task, or are about to take any action — even if the task
  seems trivial or you feel confident you can handle it without skills.
license: MIT
compatibility: Hermes Agent, Claude Code, Codex CLI, any SKILL.md-compatible agent
metadata:
  author: bernie
  version: "1.0"
  category: workflow
  tags: [workflow, discipline, skills, process, superpowers]
---

# Skill First 工作流

## 1. 何时使用

**始终使用。** 每次收到用户消息、开始新任务、或即将执行任何操作之前，都必须执行此工作流。

这不是"建议"，是强制纪律。跳过此流程 = 无证上岗。

## 2. 核心原则：Skill First

**先找 Skill，再动手。** 哪怕只有 1% 的可能性某个 Skill 适用，都必须先加载查看。

为什么这条规则重要：
- 经验丰富反而容易跳过流程，"我觉得简单"是最危险的信号
- Skill 体系的价值在于强制流程纪律，而非知识补充
- 跳过 Skill 的决策本身就不该由自己做——让 Skill 内容决定是否适用

## 3. 执行流程

### 第一步：扫描（每条用户消息到达时）

收到用户消息后，**在做任何事之前**，扫描可用 Skills 列表：

```
1. 调用 skills_list() 获取当前可用 Skills
2. 对每个 Skill 的 description 做快速匹配：
   - 是否与当前任务直接相关？
   - 是否与当前任务的某个步骤相关？
   - 哪怕只有微弱关联，也标记为"待加载"
3. 所有标记的 Skill 都用 skill_view() 加载查看
4. 根据加载的内容决定是否遵循该 Skill 的流程
```

### 第二步：分类（根据任务性质匹配 Skill）

| 任务类型 | 必须触发的 Skill | 原因 |
|---------|-----------------|------|
| 创造性/设计/架构 | `brainstorming` | 先理解需求、提方案对比、获批准再动手 |
| 实现计划 | `writing-plans` → `executing-plans` | 先写计划再执行 |
| 编写/修改 Skill | `writing-skills` + `skill-authoring-guide` | TDD 流程写 Skill |
| 调试问题 | `systematic-debugging` | 先理解根因再修复 |
| 代码审查 | `requesting-code-review` / `receiving-code-review` | 按规范审查 |
| 多任务并行 | `dispatching-parallel-agents` | 协调并行 Agent |
| 完成任务前 | `verification-before-completion` | 必须有验证证据才能声称完成 |
| Git 操作 | `using-git-worktrees` | 隔离变更 |
| 任何任务 | `using-superpowers` | 顶层 Skill 使用规范 |

### 第三步：声明（加载 Skill 后告诉用户）

加载了哪个 Skill，用来做什么：

```
🐻 使用 [skill-name] 来 [目的]
```

这不仅是透明度，也让自己对流程负责。

### 第四步：执行（严格遵循 Skill 流程）

- Skill 有流程图的按流程图走
- Skill 有检查清单的逐项完成
- Skill 要求先问问题的，先问问题
- **不要"参考"Skill 然后按自己方式做**——要么严格遵循，要么明确说明为什么偏离

### 第五步：验证（完成任务前）

完成任何操作后，用 `verification-before-completion` 的思维：

- 我是否实际执行了验证？（不是"应该没问题"）
- 验证结果是什么？（不是"看起来正常"）
- 有没有遗留问题？

## 4. 红旗清单

以下想法出现时，**立即停下**，回到第一步扫描 Skills：

| 想法 | 现实 |
|------|------|
| "这太简单了不需要 Skill" | 简单任务恰恰是流程跳过的高发区 |
| "我凭经验就能搞定" | 经验丰富 ≠ 流程可省 |
| "先干了再说" | 先找 Skill 再干 |
| "这个 Skill 大材小用" | Skill 的价值在于纪律，不在知识 |
| "我记得这个 Skill" | Skill 会更新，每次都重新加载 |
| "来不及了先动手" | 跳过流程省的时间会在返工中加倍偿还 |
| "用户等着呢" | 走流程 30 秒，跳过流程返工 30 分钟 |

## 5. 常见错误与修正

| 错误 | 后果 | 修正 |
|------|------|------|
| 直接写代码没走 brainstorming | 设计不满足需求，返工 | 创造性任务先 brainstorming |
| 完成任务没验证 | 声称完成实际有问题 | 完成前必须跑验证 |
| 觉得 Skill 不适用跳过 | 漏掉关键流程步骤 | 1% 可能性就加载 |
| 加载了 Skill 但没严格遵循 | Skill 形同虚设 | 要么遵循要么说明原因 |
| 一次处理多步没逐步检查 Skill | 中间步骤遗漏 Skill | 每个关键步骤前都重新扫描 |

## 6. 产出物规范

按照此工作流执行时，在 python-tools 仓库新增脚本后，必须：
- 更新 `~/workspace/python-tools/MANIFEST.md` 清单
- 脚本归类到对应功能目录（db/encoding/conversion/file/network/text/media）

在 skills 仓库新增/修改 Skill 后，必须：
- 更新 `skills.manifest.json`（补充 description + source 信息）
- 通过 `skills.py install --agent hermes` 更新链接
- 验证 `skills status --agent hermes` 链接正常
- 提交并推送到 Git

**新增 Skill 前必须获得用户确认：**
- 发现值得沉淀为 Skill 的经验/流程时，先向用户推荐并说明理由
- 格式：推荐 Skill 名称 + 触发场景 + 为什么值得沉淀 + 预期收益
- 用户确认后才创建，不要自作主张

## 7. 与 using-superpowers 的关系

`using-superpowers` 是通用的"何时使用 Skill"指南，本 Skill 是对它的**执行强化版**：

- `using-superpowers`：如果 Skill 可能适用就必须用
- `skill-first-workflow`：具体怎么扫描、怎么匹配、怎么执行、怎么验证

两者同时生效，不冲突。
