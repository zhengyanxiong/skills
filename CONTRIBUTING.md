# Contributing to Skills Repository

🎉 感谢你考虑为本项目做贡献！每一个 PR、Issue、Discussion 都是宝贵的。

## 📋 目录

- [行为准则](#行为准则)
- [我能贡献什么？](#我能贡献什么)
- [提 Issue](#提-issue)
- [提 Pull Request](#提-pull-request)
- [开发流程](#开发流程)
- [测试要求](#测试要求)
- [Commit 规范](#commit-规范)
- [Style Guide](#style-guide)
- [社区](#社区)

## 行为准则

本项目采用 [Contributor Covenant v2.1](CODE_OF_CONDUCT.md)。参与即代表你同意遵守该准则。请将不可接受的行为报告给项目维护者。

## 我能贡献什么？

我们欢迎以下形式的贡献：

### 1. 添加新 Skill

最常见的贡献类型：

- 你写了一个新 skill → 提交为本仓库的 local skill
- 上游仓库有新的好 skill → 通过 `./skills add owner/repo` 添加

### 2. 改进现有 Skill

- 修正 SKILL.md 中的事实错误、错别字
- 补充 frontmatter 字段（author、version、tags）
- 改进 Skill 描述（description 是触发匹配的关键）
- 拆分巨型 Skill 到 references/

### 3. 改进 CLI 工具 (`skills.py`)

- Bug 修复
- 新功能（如 `--update` 子命令、JSON 输出格式）
- 性能优化
- 错误信息更友好
- 增加测试覆盖率

### 4. 文档 & 教程

- 改进 README
- 添加 example/ 目录（使用案例）
- 翻译（English / 其他语言）

## 提 Issue

提 Issue 前请先：

1. **搜索现有 Issue**：避免重复
2. **使用 Issue 模板**：选最匹配的（bug / feature / question）
3. **提供复现信息**：
   - 操作系统 + Python 版本 (`python3 --version`)
   - 完整错误堆栈
   - 你执行过的命令
   - 期望结果 vs 实际结果

## 提 Pull Request

### 工作流程

```bash
# 1. Fork 仓库（在 GitHub UI 点击 Fork）

# 2. 克隆你的 fork
git clone https://github.com/YOUR_USERNAME/skills.git
cd skills

# 3. 创建 feature 分支
git checkout -b feat/your-feature-name

# 4. 做出修改（保持原子性）

# 5. 跑本地测试
./skills doctor
python3 -m unittest discover -s tests -v

# 6. 提交（遵循 commit 规范）
git add .
git commit -m "feat: add new skill XYZ"

# 7. 推到你的 fork
git push origin feat/your-feature-name

# 8. 在 GitHub 开 PR（使用 PR 模板）
```

### PR 要求

- ✅ 通过所有测试（doctor + unittest）
- ✅ 单个 PR 只解决一个 issue
- ✅ commit message 遵循 [Conventional Commits](https://www.conventionalcommits.org/)
- ✅ PR 描述中链接相关 Issue（`Closes #123`）
- ✅ 与现有代码风格一致

## 开发流程

### 添加新 Skill（最常见场景）

```bash
# Step 1: 创建目录
mkdir -p my-new-skill

# Step 2: 写 SKILL.md（参考 skill-authoring-guide）
$EDITOR my-new-skill/SKILL.md

# Step 3: 验证
./skills doctor
# 应该看到 [ok] my-new-skill has SKILL.md
# 应该看到 [ok] my-new-skill frontmatter name matches

# Step 4: 添加到 manifest
# 如果是 third-party 来源：
./skills add owner/repo/path/to/skill --agent codex --agent hermes

# 如果是 local skill：手动编辑 skills.manifest.json
```

### 修改 CLI (`skills.py`)

```bash
# Step 1: 激活 venv（如果有）
# 本项目使用 stdlib only，无需 venv

# Step 2: 跑现有测试
python3 -m unittest discover -s tests -v

# Step 3: 编辑 skills.py
$EDITOR skills.py

# Step 4: 添加新测试（tests/test_your_feature.py）
$EDITOR tests/test_your_feature.py

# Step 5: 完整测试套件
python3 -m unittest discover -s tests -v

# Step 6: 跑 doctor 防止破坏 manifest
./skills doctor
```

## 测试要求

所有 PR 必须通过 CI。CI 包含：

| 检查 | 命令 | 期望结果 |
|---|---|---|
| Skills 完整性 | `./skills doctor` | 所有 check 全 `[ok]` |
| 单元测试 | `python3 -m unittest discover -s tests -v` | 所有 test pass |
| Manifest 一致性 | `./skills status` | 所有 tracked skills 都已 installed |

如果你修改了 `skills.py`，**必须**为新功能添加单元测试，**必须**确保现有测试 pass。

## Commit 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>(<scope>): <description>

<body>

<footer>
```

**type**：
- `feat` — 新功能（新 skill、新 CLI 命令）
- `fix` — Bug 修复
- `docs` — 仅文档变更
- `refactor` — 代码重构（无功能变化）
- `test` — 添加/调整测试
- `chore` — 杂项（CI、构建等）

**scope**（可选）：
- `skills` — 涉及 skill 内容
- `cli` — 涉及 skills.py 工具

**示例**：

```
feat(skills): add brand-guidelines from anthropics/skills

Sources: anthropics/skills @ 9d2f1ae

Trigger: 2026-07-03 github-trending-skills cron digest.

---

fix(cli): preserve cache when source_path is "."

When source_path is set to ".", cache key computation was incorrect,
causing cache invalidation and re-fetch on every sync.
```

## Style Guide

### Skills (SKILL.md)

- 目录名：小写字母、数字、连字符（与 `name` frontmatter 一致）
- `SKILL.md` ≤ 500 行，长内容移到 `references/`
- YAML frontmatter 必须有 `name` 和 `description`
- `description` 字段是触发匹配的关键，**必须**清晰描述使用场景

### Python (`skills.py`)

- 类型注解（PEP 484）
- 仅使用 stdlib（无外部依赖）
- 函数 ≤ 50 行
- 模块 docstring + 复杂函数 docstring

### Shell Scripts

```bash
set -euo pipefail
```

### Markdown

- 标题层级：H1 只用 1 次（在 README/顶部）
- 列表用 `-` 而非 `*`
- 代码块标记语言：` ```bash `, ` ```python ` 等

## 社区

- 💬 [GitHub Discussions](../../discussions) — 问答、想法、Show & Tell
- 🐛 [GitHub Issues](../../issues) — Bug 报告、功能请求
- 🔒 [Security Advisories](SECURITY.md) — 安全漏洞（私密）

## 许可

通过贡献，你同意你的贡献按 [MIT 许可证](LICENSE) 发布。

---

再次感谢你的贡献！🙌
