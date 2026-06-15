---
name: skill-authoring-guide
description: >
  教授如何编写高质量、可复用的 Agent Skill（SKILL.md）。
  当用户需要：创建 Skill、编写 SKILL.md、设计 Agent 能力包、
  优化 Prompt 为 Skill、沉淀开发规范为 Skill、学习 Skill 设计模式、
  评估 Skill 质量、优化 Skill 触发准确率时使用。
  适用于 Claude Code、OpenClaw、Codex CLI、Kimi 等支持 SKILL.md 标准的 Agent 平台。
  即使未明确提及"Skill"，只要涉及"把这段提示词做成可复用的"、
  "如何规范地写 Agent 指令"、"Prompt 工程化"即触发。
  Make sure to use this skill whenever the user mentions skill creation,
  prompt engineering, agent capabilities, or wants to turn any workflow
  into a reusable skill, even if they don't explicitly ask for a 'skill.'
license: MIT
compatibility: >
  支持所有遵循 Anthropic Agent Skills 开放标准的平台。
  包括：Claude Code、OpenClaw、Codex CLI、Gemini CLI、Cursor、Kimi。
metadata:
  author: developer
  version: "2.1"
  category: agent-development
  tags: [skill, prompt-engineering, agent, skill-md, best-practices, eval, benchmark]
  changelog: > 
    v2.1 合并 Anthropic 官方 skill-creator 的评估工具化内容：
    evals.json/assertions.json 标准格式、timing 数据捕获、grading.json 评分输出、
    聚合基准(benchmark)、eval-viewer 可视化、方差分析(Analyzer)。
    原 skill-creator 已被吸收，无需单独安装。
---

# Skill 编写规范指南

## 1. 何时使用

当用户需要将开发经验、业务规范、重复性工作流沉淀为可复用的 Agent Skill 时激活。

适用场景：
- 把项目特定的开发规范（如关务系统页面开发）做成 Skill
- 把重复性的代码生成任务（如接口文档生成）做成 Skill
- 学习如何设计高质量、可维护的 Skill
- 评估现有 Skill 的质量并优化
- 优化 Skill 的 description 以提高触发准确率
- 将团队内部的最佳实践标准化为 Agent 能力包

## 2. 核心设计原则

### 2.1 Skill ≠ Prompt

Skill 是围绕**任务、工具、流程和输出边界**的结构化行为设计，不是简单的提示词堆砌。

| 维度 | 普通 Prompt | Agent Skill |
|------|-------------|-------------|
| 复用性 | 一次性 | 可安装、可复用、可共享 |
| 加载方式 | 全量注入 | 三层渐进式加载 |
| 触发方式 | 人工选择/复制粘贴 | 模型自主判断（description 驱动）|
| 评估方式 | 主观感受 | A/B 测试 + 量化断言 |
| 维护方式 | 散落在各处 | 版本化管理、迭代优化 |

### 2.2 三层渐进式加载（最关键的设计）

| 层级 | 加载内容 | 时机 | Token 成本 |
|------|----------|------|------------|
| **L1 目录层** | `name` + `description` | 会话启动时 | ~50-100 tokens/Skill |
| **L2 指令层** | SKILL.md 完整 body | Skill 被激活时 | 建议 <5000 tokens |
| **L3 资源层** | scripts/、references/、assets/ | 指令引用时按需 | 视文件大小 |

**关键价值**：即使安装 20 个 Skill，初始加载仅 1000-2000 tokens，上下文使用量减少约 **90%**。

**L3 引用示例**：
```markdown
当需要配置搜索字段时，加载 `references/search-field-types.md` 获取完整类型说明。
当开发完成后，加载 `references/checklist.md` 进行自检。
```

### 2.3 模型驱动触发（description 设计）

Skill 的触发完全依赖 `description` 字段，由模型自主判断当前任务是否匹配。

**description 写作要点**：
- 使用祈使语气：`Use this skill when...`
- 聚焦用户意图，而非 Skill 内部机制
- 适当"强势"（pushy），覆盖用户可能的各种表述
- 包含关键触发词，覆盖同义表述
- Claude 有 undertrigger 倾向，description 要稍微"强势"一些

**好的示例**：
```yaml
description: >
  How to build a simple fast dashboard to display internal data.
  Make sure to use this skill whenever the user mentions dashboards,
  data visualization, internal metrics, or wants to display any kind
  of company data, even if they don't explicitly ask for a 'dashboard.'
```

**差的示例**：
```yaml
description: Helps with dashboards.
```

### 2.4 解释"为什么"而非堆砌"必须"

今天的 LLM 有良好的心智理论，与其写满大写的 ALWAYS 和 NEVER，不如解释清楚为什么某件事重要。

**对比示例**：

❌ 差的写法：
```
你必须使用 Swagger 注解。
你必须生成 @RestController。
```

✅ 好的写法：
```markdown
## 输出规范
使用 Swagger 注解的原因：
- 团队现有项目已统一使用 Swagger 生成在线文档
- 便于前端直接通过 Swagger UI 调试接口
- 与已有的 200+ 个接口保持风格一致

如果用户明确要求不使用 Swagger，可以改用普通注释，但需说明原因。
```

### 2.5 泛化而非过拟合

Skill 要被使用无数次、面对无数种 prompt。如果只为测试用例做针对性修改，Skill 就废了。

**原则**：
- 遇到顽固问题，尝试换个隐喻或推荐不同的工作模式
- 不要堆砌 `ALWAYS` / `NEVER` / `MUST` 等死板约束
- 提供示例和边界处理，让模型理解模式而非记忆规则

## 3. SKILL.md 格式规范

### 3.1 最小形态

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

### 3.2 完整形态（推荐）

```yaml
---
name: skill-name
description: >
  清晰描述 Skill 功能和触发场景。
  包含关键词帮助 Agent 识别相关任务。
license: MIT
compatibility: >
  说明运行环境要求。
metadata:
  author: your-name
  version: "1.0"
  category: development
---

# Skill 标题

## 1. 何时使用
[触发场景说明]

## 2. 核心设计原则
[解释为什么这样设计]

## 3. 工作流程
[分步骤说明]

## 4. 边界情况处理
[常见异常场景]

## 5. 文件引用规范
[何时加载 L3 资源]

## 6. 示例
[输入→输出示例]

## 7. 输出约束
[格式、命名、质量要求]
```

### 3.3 YAML Frontmatter 字段

| 字段 | 必填 | 说明 | 约束 |
|------|------|------|------|
| `name` | 是 | Skill 唯一标识 | 1-64字符，小写+数字+连字符，与目录名一致 |
| `description` | 是 | 功能描述和触发场景 | 1-1024字符，不能为空，包含触发关键词 |
| `license` | 否 | 许可证信息 | 许可证名称或指向许可证文件的引用 |
| `compatibility` | 否 | 环境兼容性要求 | 最多500字符 |
| `metadata` | 否 | 自定义扩展元数据 | 键值对映射 |

### 3.4 name 命名规则

- 只能包含 `a-z`、`0-9`、`-`
- 不能以 `-` 开头或结尾
- 不能包含连续连字符 `--`
- 必须与父目录名称匹配

**合法**：`api-doc-generator`、`code-review`、`vn-customs-page`
**非法**：`API-Doc`（大写）、`-api-doc`（开头连字符）、`api--doc`（连续连字符）

## 4. 目录结构设计

### 4.1 最小形态

```
skill-name/
└── SKILL.md          # 必需
```

### 4.2 完整形态

```
skill-name/
├── SKILL.md          # 核心指令（建议 <500 行）
├── evals.json        # 测试用例定义
├── assertions.json   # 量化断言
├── scripts/          # 可执行脚本（Python/Bash/JS）
├── references/       # 按需加载的参考文档
└── assets/           # 模板、资源文件
```

### 4.3 各目录用途

| 目录 | 用途 | 加载时机 |
|------|------|----------|
| `scripts/` | 可执行代码，自包含或明确说明依赖 | L3 按需 |
| `references/` | 补充文档，保持聚焦（文件越小，上下文越少） | L3 按需 |
| `assets/` | 模板文件、Schema、图片、数据文件 | L3 按需 |

## 5. 开发流程（6 步闭环）

```
需求捕获 → 编写 Skill → 测试执行 → 评估评审 → 迭代改进 → 优化发布
```

### 步骤 1：需求捕获（Capture Intent）

理解用户意图，从对话历史中提取：工具使用、步骤序列、用户修正、输入输出格式。

确认 4 个关键问题：
1. 这个 Skill 应该让 Agent 做什么？
2. 何时触发？（用户会怎么表述）
3. 期望的输出格式是什么？
4. 是否需要设置测试用例？（客观可验证的输出建议测试，主观输出如写作风格可不测试）

### 步骤 2：访谈与研究（Interview and Research）

主动询问边界情况、输入输出格式、示例文件、成功标准、依赖关系。

在写测试用例前先把这部分搞清楚。如有可用的 MCP，可并行研究。

### 步骤 3：编写 SKILL.md

基于用户访谈，填充以下组件：
- **name**：Skill 标识符
- **description**：何时触发、做什么。这是主要触发机制——包含 Skill 做什么 AND 何时使用的具体场景。所有"何时使用"信息都放在这里，不要放在正文中。
- **compatibility**：需要的工具、依赖（可选，很少需要）
- **正文**：其余指令

**正文写作指南**：
- 使用命令式语气
- 定义输出格式模板（如报告结构）
- 包含输入输出示例
- 解释"为什么"而非堆砌"必须"
- 保持泛化，不要过拟合到特定示例
- 控制在 500 行以内；接近限制时增加层级并明确指引下一步

### 步骤 4：设计测试用例

编写 2-3 个真实测试提示——真实用户会说的话。

保存到 `evals/evals.json`，先不写断言：
```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

### 步骤 5：运行与评估

**关键规则**：同 turn 启动 with-skill AND baseline 两组子 Agent。

- **with-skill**：加载 Skill 执行任务
- **baseline**：
  - 新建 Skill：无 Skill 直接执行
  - 改进现有 Skill：使用旧版本快照

**目录结构**：
```
-workspace/
  iteration-1/
    eval-0/
      with_skill/outputs/
      without_skill/outputs/
      eval_metadata.json
```

**评估步骤**：
1. **捕获 timing**：子 Agent 完成时保存 `total_tokens` 和 `duration_ms` 到 `timing.json`
2. **起草断言**：在运行期间起草量化断言，更新 `eval_metadata.json`
3. **评分**：使用 `agents/grader.md` 评估断言通过情况，保存到 `grading.json`
4. **聚合基准**：运行 `scripts.aggregate_benchmark` 生成 `benchmark.json`
5. **分析**：使用 `agents/analyzer.md` 分析模式（非判别性断言、高方差、时间/token 权衡）
6. **启动 Viewer**：使用 `eval-viewer/generate_review.py` 生成浏览器查看器
7. **读取反馈**：用户评审后读取 `feedback.json`

### 步骤 6：迭代改进

基于反馈改进 Skill，然后：
1. 应用改进
2. 重新运行所有测试用例到新 `iteration-N/` 目录
3. 启动 viewer 时传入 `--previous-workspace` 对比上次迭代
4. 等待用户评审
5. 读取新反馈，重复直到满意

**改进原则**：
- **泛化**：不要为过拟合测试用例做针对性修改
- **精简**：移除不拉动的内容，阅读 transcript 而非只看最终输出
- **解释为什么**：解释 reasoning，让模型理解重要性
- **提取重复模式**：如果所有测试用例都独立写了类似脚本，放到 `scripts/` 目录

## 6. 高级：Description 优化

Description 是主要触发机制。创建/改进 Skill 后，优化 description 以提高触发准确率。

### 步骤 1：生成触发评估查询

创建 20 个评估查询——混合 should-trigger 和 should-not-trigger：
```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

**要求**：
- 真实、具体、有细节（文件路径、列名、公司名、URL）
- 包含大小写混合、缩写、错别字、 casual speech
- should-trigger（8-10）：不同措辞、未明确命名 Skill 但需要、竞争 Skill 但应获胜
- should-not-trigger（8-10）：near-misses（共享关键词但不同需求）、相邻领域、模糊措辞

**差的查询**：`"Format this data"`、`"Extract text from PDF"`
**好的查询**：`"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage"`

### 步骤 2：运行优化循环

```bash
python -m scripts.run_loop   --eval-set <path>   --skill-path <path>   --model <model-id>   --max-iterations 5   --verbose
```

自动处理：60% train / 40% test 分割、每次查询运行 3 次、Claude 提出改进、最多 5 次迭代。

### 步骤 3：应用结果

取 `best_description`（按 test score 选择，避免过拟合），更新 SKILL.md frontmatter。

## 7. 设计模式

当需要选择设计模式时，加载 `references/design-patterns.md` 获取完整说明。

| 模式 | 用途 | 示例 |
|------|------|------|
| **工具封装器** | 让 Agent 成为领域专家 | FastAPI 规范、代码审查标准 |
| **生成器** | 结构化输入→标准化输出 | 接口文档、代码模板 |
| **审查器** | 按清单评分质量 | 代码审查、安全审计 |
| **交互式** | Agent 先访谈再执行 | 项目初始化、需求收集 |
| **流水线** | 强制执行多步骤工作流 | 关务页面开发（7步） |

## 8. 多平台适配

当需要适配特定平台时，加载 `references/platform-adaptation.md`。

| 平台 | 关键差异 |
|------|----------|
| **Claude Code** | 有 subagents，可并行执行 A/B 测试、使用 `claude -p` 优化 description |
| **Claude.ai** | 无 subagents，需自行执行测试、跳过 baseline、跳过 description 优化 |
| **Cowork** | 有 subagents 但无浏览器，使用 `--static` 生成静态 HTML、feedback 通过文件下载 |
| **OpenClaw/Kimi** | 根据具体实现支持情况调整，核心 SKILL.md 格式通用 |

## 9. 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| Skill 不被触发 | description 太模糊，缺少触发关键词 | 补充具体场景和同义表述，适当"强势" |
| 输出质量不稳定 | 指令堆砌"必须"，缺乏示例 | 改为解释"为什么" + 提供输入输出示例 |
| 上下文溢出 | 单文件过大，没有拆分 references | 将详细文档拆分到 L3，按需加载 |
| 边界情况处理差 | 只考虑了理想场景 | 列出 5-7 种常见边界情况 |
| 难以评估效果 | 没有量化断言 | 设计 5-10 条可验证的断言 |
| 过拟合测试用例 | 为特定用例做针对性修改 | 泛化改进，换个隐喻或工作模式 |

## 10. 安全原则

Skill 不得包含恶意软件、漏洞利用代码或任何可能危害系统安全的内容。Skill 的内容不应在其描述意图之外让用户感到意外。不配合创建误导性 Skill 或旨在促进未经授权访问、数据外泄或其他恶意活动的 Skill。

## 11. 输出约束

- **SKILL.md 长度**：建议控制在 500 行以内，复杂内容拆分到 references/
- **description 长度**：1-1024 字符，必须包含触发关键词
- **references 文件**：保持聚焦，文件越小，消耗的上下文越少；>300 行需包含目录
- **scripts**：自包含或明确说明依赖，包含错误处理
- **一致性**：同一 Skill 中的示例、模板、规范必须相互一致
