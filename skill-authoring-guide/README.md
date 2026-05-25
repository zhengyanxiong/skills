# Skill 编写规范指南 v2.0

基于 Anthropic Agent Skill 开放标准的 Skill 编写教学工具。

## 目录结构

```
skill-authoring-guide/
├── SKILL.md                              # 核心指令（L2 层，407行）
├── evals.json                            # 测试用例
├── assertions.json                       # 量化断言
├── README.md                             # 本文件
├── agents/
│   ├── grader.md                         # 评分者 Agent 定义
│   ├── comparator.md                     # 盲比较者 Agent 定义
│   └── analyzer.md                       # 分析者 Agent 定义
└── references/
    ├── skill-format-spec.md              # 格式规范详解（L3）
    ├── design-patterns.md                # 5 种设计模式（L3）
    ├── evaluation-guide.md               # 评估与迭代指南（L3）
    ├── platform-adaptation.md            # 多平台适配（L3）
    └── description-optimization.md       # Description 优化（L3）
```

## 使用方式

### 1. 触发条件

当用户输入涉及以下场景时自动激活：
- "怎么写 Skill"
- "把这段 Prompt 做成 Skill"
- "Skill 设计模式"
- "评估 Skill 质量"
- "优化 Skill 触发"
- "Prompt 工程化"
- "Agent 能力包"

### 2. 核心能力

1. **格式规范**：YAML frontmatter、目录结构、命名规则
2. **设计模式**：工具封装器、生成器、审查器、交互式、流水线
3. **评估体系**：A/B 测试、量化断言、Grader/Comparator/Analyzer
4. **Description 优化**：20 个查询、train/test 分割、自动迭代
5. **多平台适配**：Claude Code / Claude.ai / Cowork / OpenClaw / Kimi
6. **常见错误诊断**：触发失败、上下文溢出、边界处理差等

### 3. 学习路径

**新手**：从"最小形态 SKILL.md"开始 → 学习 description 设计 → 掌握三层加载
**进阶**：学习 5 种设计模式 → 掌握评估体系 → 实践迭代优化
**专家**：设计复杂 Pipeline → 建立团队 Skill 规范 → 优化 description 触发率

## v2.0 改进（对比 v1.0）

| 改进项 | v1.0 | v2.0 |
|--------|------|------|
| 用户沟通策略 | 无 | 新增：根据用户技术水平调整术语 |
| Capture Intent | 部分覆盖 | 完整 4 个问题清单 |
| Interview & Research | 无 | 新增：主动询问边界情况 |
| 渐进披露细节 | 粗略 | 精确：>300行 reference 需目录 |
| Domain Organization | 无 | 新增：多域支持按变体组织 |
| Writing Patterns | 无 | 新增：命令式语气、输出格式模板、示例格式 |
| 测试执行细节 | 简单 | 完整：同 turn 启动、timing 捕获、workspace 结构 |
| 子 Agent 体系 | 概念描述 | 完整定义：grader/comparator/analyzer |
| Eval Viewer | 无 | 新增：generate_review.py 使用方式 |
| Description 优化 | 无 | 完整：20 查询、train/test、run_loop.py |
| 多平台适配 | 无 | 完整：Claude Code/Claude.ai/Cowork/OpenClaw/Kimi |
| 安全原则 | 无 | 新增：Principle of Lack of Surprise |
| 打包发布 | 无 | 新增：present_files 工具、.skill 文件 |

## 设计要点

1. **三层渐进加载**：L1 仅加载 name+description，L2 激活时加载 SKILL.md body（407行），L3 按需加载 references/
2. **模型驱动触发**：description 覆盖多种用户表述，适当"强势"对抗 undertrigger
3. **解释优于命令**：解释"为什么"比堆砌"必须"更能获得稳定输出
4. **量化评估**：10 条断言覆盖结构、正确性、完整性、一致性、格式五个维度
5. **迭代闭环**：需求捕获 → 编写 → 测试 → 评估 → 改进 → 优化，完整 6 步

## 迭代记录

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-05-13 | 初始版本，基于 Anthropic 开放标准 |
| 2.0 | 2026-05-25 | 对照官方 skill-creator 完整重构，新增评估工程体系、Description 优化、多平台适配、子 Agent 定义 |
