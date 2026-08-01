# Skills Repository

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License: MIT"></a>
  <a href="https://github.com/zhengyanxiong/skills/stargazers"><img src="https://img.shields.io/github/stars/zhengyanxiong/skills" alt="GitHub Stars"></a>
  <a href="https://github.com/zhengyanxiong/skills/commits/main"><img src="https://img.shields.io/github/last-commit/zhengyanxiong/skills" alt="Last Commit"></a>
  <img src="https://img.shields.io/badge/skills-113-blue" alt="113 Skills">
</p>

**Agent Skills 中央仓库 + 跨 Agent CLI**

一个命令，统一管理 [Claude Code](#known-agent-directories)、[Codex](#known-agent-directories)、[Hermes](#known-agent-directories)、[Kimi](#known-agent-directories)、[OpenCode](#known-agent-directories)、[Minimax](#known-agent-directories) 等多个 AI Agent 工具的 Skills。通过 symlink 实现单源真相：**一处改动，6 个 Agent 同步生效**。

> 🈶 **English version**: This README is in Chinese (中文). The CLI commands and structure are designed for a global audience — code samples use English. A future English translation of this README is on the roadmap.

---

## ✨ Why this repo?

AI Agent 工具爆发后（Claude Code、Codex、Hermes、Kimi、OpenCode、Minimax…），每个工具都有各自的 `SKILL.md` 格式和 skills 目录。这带来**三个问题**：

1. **重复维护** — 同一个 skill 要在 N 个 Agent 目录复制 N 份
2. **版本碎片化** — 每个 Agent 看到的 skill 版本彼此不一致
3. **更新繁琐** — 本地改一个 skill，要在 N 个目录手工同步

**这个仓库的解法**：

- ✅ **单源真相（Source of Truth）** — 仓库即中央存储
- ✅ **CLI 工具 (`skills.py`)** — 自动 symlink 到所有 Agent
- ✅ **Source manifest** — 每个 skill 跟踪 upstream + commit hash，可追溯
- ✅ **跨 6+ Agent** — Codex / Claude Code / Hermes / Kimi / OpenCode / Minimax
- ✅ **Upstream 感知** — 检测上游更新并支持 sync
- ✅ **零依赖** — 仅 Python stdlib，跨平台（Linux/macOS/WSL）

## 🚀 Quick Start

### 1. 克隆仓库

```bash
git clone https://github.com/zhengyanxiong/skills.git ~/skills
cd ~/skills
```

### 2. 安装（创建 symlink 到你的 Agent）

```bash
# 指定 Agent 安装（推荐）
./skills install --agent codex --agent hermes

# 或全部安装（缺失目录自动跳过）
./skills install
```

### 3. 验证

```bash
./skills status
# 输出应显示 113 个 skills 都已 linked
```

### 4. 添加新 Skill

```bash
# 从 GitHub 整仓库添加
./skills add owner/repo --agent codex --agent hermes

# 仓库内特定路径
./skills add anthropics/skills/brand-guidelines --agent codex
```

### 5. 维护

```bash
./skills doctor    # 验证所有 SKILL.md + frontmatter
./skills outdated  # 查看哪些 skills 有可用更新
./skills sync      # 拉取 upstream 变更
```

---

## 📚 文档导航

- [✨ Why this repo?](#-why-this-repo) — 我们解决的问题
- [🚀 Quick Start](#-quick-start) — 5 分钟上手
- [🗂 Skills 一览](#skills-一览) — 113 个 skill 详情
- [⚙️ Commands](#commands) — 全部 CLI 命令
- [🤝 贡献指南](#贡献指南) — 如何添加新 skill
- [🔒 Security](SECURITY.md) — 漏洞报告
- [📄 License](LICENSE) — MIT

---

## Skills 一览

共 113 个 skills（精选 50 个核心技能展示在下表，完整列表见 `skills.py list`）。来源及简要描述如下：

| Skill | 来源 | 描述 |
|-------|------|------|
| agent-reach | [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | 跨平台互联网内容路由器，支持 13 个平台（X/Twitter、B站、Reddit、V2EX、小红书、LinkedIn、YouTube、GitHub、RSS、雪球等）。路由至 OpenCLI / 各平台 CLI / API 后端。 |
| algorithmic-art | [anthropics/skills](https://github.com/anthropics/skills) | 使用 p5.js 创建算法艺术，支持种子随机性和交互式参数探索。 |
| api-and-interface-design | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 指导稳定的 API 与接口设计。适用于设计 API、模块边界或任何公共接口。 |
| audit-context-building | [trailofbits/skills](https://github.com/trailofbits/skills) | 超细粒度逐行代码分析，构建深层架构上下文。审计前阶段，使用第一性原理、5 Whys、5 Hows。 |
| autoresearch | [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | 端到端自主 AI 研究项目编排，双循环架构：内循环快速实验迭代，外循环综合结果并调整方向。 |
| brainstorming | [obra/superpowers](https://github.com/obra/superpowers) | 将创意或产品想法塑造成可落地的设计方案，包括需求、权衡和审批关卡。 |
| brandkit | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | 品牌套件生成器（taste-skill 套件之一），输出颜色/字体/资产规范。 |
| browser-testing-with-devtools | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 通过 Chrome DevTools MCP 在真实浏览器中测试。 |
| brutalist-skill | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | 工业粗野主义 UI 风格（taste-skill 套件），避免居中+阴影+卡片模板化。 |
| canvas-design | [anthropics/skills](https://github.com/anthropics/skills) | 使用设计理念在 .png 和 .pdf 中创建精美的视觉艺术作品。 |
| capability-evolver | local（本仓库） | 分析运行时日志，检测错误模式、JVM/GC 问题、性能瓶颈和健康评分。 |
| ci-cd-and-automation | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 自动化 CI/CD 流水线设置。 |
| code-review-and-quality | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 多维度代码审查。在合并任何变更前使用。 |
| code-simplification | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 简化代码以提高清晰度，不改变行为。 |
| context-engineering | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 优化 Agent 上下文设置，提高输出质量。 |
| coross-platform-vim-nvim-deploy | local（本仓库） | 在 macOS、Linux、Windows 和 WSL 间部署和同步跨平台 Vim/Neovim 开发环境。 |
| council | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 召集四方议会（Skeptic/Pragmatist/Critic/in-context）处理模糊决策与权衡取舍。 |
| debugging-and-error-recovery | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 系统性根因调试指南。 |
| deep-research | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 多源深度研究 + 综合。补充 `autoresearch`。 |
| deprecation-and-migration | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 管理废弃和迁移流程。 |
| dispatching-parallel-agents | [obra/superpowers](https://github.com/obra/superpowers) | 通过将任务委派给隔离的并行 Agent 来协调多个独立的调查或实现任务。 |
| documentation-and-adrs | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 记录架构决策和文档（ADR）。 |
| doubt-driven-development | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 在每次非平凡决策前进行对抗性审查。 |
| drawio-skill | local（本仓库） | 创建和导出 draw.io 图表（架构图、流程图、ERD、UML、网络图等）。 |
| ecc-harness | local（本仓库） | ECC 集成 Hub：解释已安装的 31 个精选 ECC 子技能、选择逻辑、如何按需取用。 |
| entry-point-analyzer | [trailofbits/skills](https://github.com/trailofbits/skills) | 识别和分析代码库中的入口点（外部函数、端点、处理器）以进行攻击面映射。 |
| executing-plans | [obra/superpowers](https://github.com/obra/superpowers) | 按任务执行已编写的实现计划，附带验证检查点和完成处理。 |
| finishing-a-development-branch | [obra/superpowers](https://github.com/obra/superpowers) | 完成开发分支：验证测试、选择合并/PR/保留/丢弃策略，安全清理 worktree。 |
| frontend-design | [anthropics/skills](https://github.com/anthropics/skills) | 指导 Agent 构建美观、生产级的前端界面。 |
| frontend-ui-engineering | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 构建生产级 UI。 |
| git-workflow-and-versioning | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 规范 Git 工作流实践。 |
| idea-refine | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 通过结构化发散-收敛思维将原始想法打磨为可执行概念。 |
| incremental-implementation | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 增量交付变更。 |
| interview-me | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 通过一问一答的面试方式提取用户真实需求（而非用户认为他们想要的东西）。 |
| market-research | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 面向决策的市场研究、竞争分析、投资者尽调和行业情报，附带来源归因。 |
| mcp-builder | [anthropics/skills](https://github.com/anthropics/skills) | 创建高质量 MCP Server 的指南（支持 FastMCP Python 和 MCP SDK Node/TypeScript）。 |
| observability-and-instrumentation | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 为代码添加可观测性，使生产行为可见且可诊断。 |
| performance-optimization | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 优化应用性能。 |
| planning-and-task-breakdown | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 将工作分解为有序任务。 |
| receiving-code-review | [obra/superpowers](https://github.com/obra/superpowers) | 以技术严谨性评估和实现代码审查反馈。 |
| redesign-skill | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | 现有项目重设计（taste-skill 套件之一）。 |
| requesting-code-review | [obra/superpowers](https://github.com/obra/superpowers) | 在合并前或重大实现后向独立的审查 Agent 请求集中式代码审查。 |
| security-and-hardening | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 强化代码安全性。 |
| security-review | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 通用安全审查工作流（框架无关），结构化输出。补充 `security-and-hardening`。 |
| semgrep-rule-creator | [trailofbits/skills](https://github.com/trailofbits/skills) | 创建和优化 Semgrep 规则，用于静态分析和安全扫描。 |
| sharp-edges | [trailofbits/skills](https://github.com/trailofbits/skills) | 识别代码中的危险边界情况、安全反模式和特定语言"锋利边缘"。 |
| shipping-and-launch | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 准备生产发布。 |
| skill-authoring-guide | local（本仓库） | 教授如何编写高质量、可复用的 Agent Skill（SKILL.md），含评估工程体系（A/B 测试、量化断言、聚合基准、方差分析）和 Description 优化。 |
| skill-creator | [anthropics/skills](https://github.com/anthropics/skills) | 使用评估框架和基准测试创建、测试和迭代改进 Agent Skills。 |
| skill-first-workflow | local（本仓库） | 强制 Skill First 规范：每次操作前扫描可用技能，加载任何相关度 ≥ 1% 的技能并按流程执行。 |
| source-driven-development | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 将每个实现决策建立在官方文档之上。 |
| spec-driven-development | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 编码前创建 Spec。 |
| static-analysis | local（本仓库） | 静态分析工具包，集成 CodeQL、Semgrep 和 SARIF 解析。包含三个子技能：codeql、semgrep、sarif-parsing。 |
| subagent-driven-development | [obra/superpowers](https://github.com/obra/superpowers) | 通过为每个任务分配全新的子 Agent 来实施计划，并逐任务审查规范合规性和代码质量。 |
| systematic-debugging | [obra/superpowers](https://github.com/obra/superpowers) | 在修复之前通过查找根因来调查 Bug、测试失败和意外行为。 |
| taste-skill | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | 反 AI Slop 前端审美框架（V2 默认）：VARIANCE/MOTION/DENSITY 三旋钮，硬禁 em-dash。 |
| test-driven-development | [obra/superpowers](https://github.com/obra/superpowers) | 通过红-绿-重构循环指导功能和 Bug 修复实现。 |
| theme-factory | [anthropics/skills](https://github.com/anthropics/skills) | 为制品提供主题样式工具包，内置 10 套预设主题。 |
| ua-understand | [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) | 把代码库转成可交互知识图谱（Tree-sitter + LLM 混合管线）。`ua-*` 前缀避免命名冲突。 |
| ui-ux-pro-max | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 提供可搜索的 UI/UX 设计智能库。 |
| using-agent-skills | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 发现和调用 Agent Skills 的元技能。 |
| market-research | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 面向决策的市场研究、竞争分析、投资者尽调和行业情报，附带来源归因。 |
| using-git-worktrees | [obra/superpowers](https://github.com/obra/superpowers) | 在功能开发前设置或检测隔离的 Git Worktree。 |
| using-superpowers | [obra/superpowers](https://github.com/obra/superpowers) | 在对话启动时引导技能使用，强制在响应前选择相关技能。 |
| verification-before-completion | [obra/superpowers](https://github.com/obra/superpowers) | 声称工作完成前要求新鲜的验证证据。 |
| web-artifacts-builder | [anthropics/skills](https://github.com/anthropics/skills) | 使用 React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui 构建复杂多组件 HTML 制品。 |
| writing-plans | [obra/superpowers](https://github.com/obra/superpowers) | 将已批准的 Spec 或需求转化为详细、可测试的实现计划。 |
| writing-skills | [obra/superpowers](https://github.com/obra/superpowers) | 使用测试驱动技能设计和部署检查来创建、编辑和验证可复用的 Agent Skills。 |

## CLI Quick Start

列出本地 skills：

```bash
./skills list
```

Windows PowerShell：

```powershell
.\skills.ps1 list
```

检查 skills 是否已链接到 Agent 全局目录：

```bash
./skills status
./skills status --agent codex
```

安装所有 skills 到所有已知 Agent：

```bash
./skills install --agent all
```

安装单个 skill 到单个 Agent：

```bash
./skills install --agent codex --skill using-superpowers
```

移除管理的 symlink：

```bash
./skills uninstall --agent codex --skill using-superpowers
```

## Source Tracking

每个 skill 在 `skills.manifest.json` 中有元数据：

```json
{
  "description": "What this skill is for.",
  "source": {
    "type": "git",
    "repo": "https://github.com/obra/superpowers.git",
    "ref": "main",
    "path": "skills/using-superpowers",
    "last_commit": "..."
  }
}
```

`type: local` 表示当前仓库是 source of truth。

管理 source 条目：

```bash
./skills sources list
./skills sources add frontend-design --repo https://github.com/anthropics/skills.git --path skills/frontend-design --ref main
./skills sources remove frontend-design
```

## Update Checks And Sync

检查上游状态：

```bash
./skills outdated
./skills outdated using-superpowers
```

对于 Git 源的 skills，更新检测是路径感知的——CLI 检查配置的 `source.path` 的最新 commit，而非仓库 HEAD。

从上游同步单个 skill：

```bash
./skills sync using-superpowers
```

同步所有 tracked skills：

```bash
./skills sync --all
```

`sync` 拒绝覆盖脏的本地 skill 目录。请先 commit 或 stash 本地修改。

## Health Checks

运行结构验证：

```bash
./skills doctor
```

检查项：每个 skill 是否有 `SKILL.md`、frontmatter `name` 是否匹配目录名、manifest 条目是否指向本地 skill。

运行测试：

```bash
python3 -m unittest discover -s tests -v
```

## Known Agent Directories

CLI 当前支持以下全局 skill 位置：

- Codex: `~/.codex/skills`
- Claude Code: `~/.claude/skills`
- OpenCode: `~/.config/opencode/skills`
- Kimi: `~/.kimi/skills`
- Hermes: `~/.hermes/skills`
- Minimax: `~/.minimax/skills`

如果目标路径已包含真实目录或指向其他位置的 symlink，install 会报告 `conflict` 并保持原样。

## 最近更新

```
1982829 chore(skills): refresh last_checked_at after final sync
75d2c30 fix(skills): preserve cache when source_path is "."
400aa19 fix(skills): atomic replace in copy_source_path
d6a92c9 fix(skills): skip type=local skills in sync --all
ef3be16 fix(skills): add source entry for canvas-design
9b73418 fix(skills): add source entry for algorithmic-art
8f2e5e2 feat: collect theme-factory from anthropics/skills
74450e9 feat: collect 2 skills from 2026-06-23 trending digest
953c518 feat: add web-artifacts-builder, skill-creator and addyosmani/agent-skills
da4a94e feat: add algorithmic-art and canvas-design skills from anthropics/skills
6ae2c2e perf: skills.py 添加 fetch 缓存，同仓库 5 分钟内不重复 fetch
```

## 已知 Bug 修复记录

### `fix(skills): skip type=local skills in sync --all`（d6a92c9）

`sync --all` 会遍历 manifest 中所有条目进行同步。此前未过滤 `type=local` 的技能，导致 sync 对本仓库自有的技能（如 skill-first-workflow、drawio-skill 等）执行不必要的上游检查。修复后跳过 local 类型的技能。

### `fix(skills): atomic replace in copy_source_path`（400aa19）

`copy_source_path` 使用非原子方式复制文件到目标目录，中断后可能留下不完整文件。改为写入临时文件后重命名（rename），确保替换要么完全成功要么不做任何更改。

### `fix(skills): preserve cache when source_path is "."`（75d2c30）

当 source_path 设置为 `"."` 时，缓存 key 计算错误导致缓存失效，每次 sync 都会重新 fetch 远程仓库。修复后正确处理根路径缓存。

## 贡献指南

添加新 skill 的标准流程：

```bash
# 1. 创建 skill 目录和 SKILL.md
mkdir -p my-new-skill
# 在 my-new-skill/SKILL.md 中编写 frontmatter + 内容

# 2. 添加到 manifest
./skills add https://github.com/owner/repo.git

# 3. 安装验证
./skills install --dry-run

# 4. 运行健康检查
./skills doctor

# 5. 运行完整测试
python3 -m unittest discover -s tests -v

# 6. 提交
git add my-new-skill/
git commit -m "feat: add my-new-skill — 简短描述"
```

### 规范要求

- Skill 目录名使用小写字母、数字和连字符，与 `SKILL.md` 中 `name` frontmatter 值完全一致。
- `SKILL.md` 控制在 500 行以内，长内容移到 `references/` 子目录。
- Shell 脚本使用 `set -euo pipefail`。
- Python 脚本添加类型注解，只使用 stdlib（无外部依赖）。
- 提交信息使用 Conventional Commits 格式：`feat:`、`fix:`、`docs:`、`refactor:`、`test:`。
- 每次提交只涉及单个 skill 或工具变更。

## Development Notes

Before committing CLI changes, run:

```bash
python3 -m unittest discover -s tests -v
./skills doctor
```
