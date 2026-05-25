# SKILL.md 格式规范详解

## 最小形态

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

## YAML Frontmatter 完整字段

| 字段 | 必填 | 说明 | 约束 |
|------|------|------|------|
| `name` | 是 | Skill 唯一标识 | 1-64字符，小写+数字+连字符，与目录名一致 |
| `description` | 是 | 功能描述和触发场景 | 1-1024字符，不能为空，包含触发关键词 |
| `license` | 否 | 许可证信息 | 许可证名称或指向许可证文件的引用 |
| `compatibility` | 否 | 环境兼容性要求 | 最多500字符 |
| `metadata` | 否 | 自定义扩展元数据 | 键值对映射 |

## name 命名规则

- 必须为 1-64 个字符
- 只能包含 `a-z`、`0-9`、`-`
- 不能以 `-` 开头或结尾
- 不得包含连续连字符 `--`
- 必须与父目录名称匹配

**合法示例**：
```
name: pdf-processing
name: data-analysis
name: code-review
```

**非法示例**：
```
name: PDF-Processing    # 不允许大写字母
name: -pdf               # 不能以连字符开头
name: pdf--processing    # 不允许连续连字符
```

## description 写法建议

**好的示例**：
```yaml
description: >
  Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs.
  Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

**差的示例**：
```yaml
description: Helps with PDFs.
```

## Markdown 正文内容

元数据之后的 Markdown 正文部分就是 Skill 的核心指令。对正文格式没有硬性限制，只要能帮助 AI 有效执行任务即可。

**建议包含**：
- 分步骤的操作说明
- 输入输出示例
- 常见边界情况处理

**建议正文控制在 500 行以内**。如果内容较多，把详细参考资料拆分到单独的文件中。

## 文件引用规范

在 SKILL.md 中引用其他文件时，使用相对于 Skill 根目录的路径：

- 引用参考文档：`references/REFERENCE.md`
- 引用脚本：`scripts/extract.py`

建议文件引用保持在一层深度，避免深层嵌套的引用链。

## 可选目录结构

### scripts/ 目录

存放 AI 可以运行的可执行代码。脚本应该是自包含的或明确说明依赖关系，包含有用的错误提示信息，并能妥善处理边界情况。

常见支持的语言：Python、Bash、JavaScript。

### references/ 目录

存放 AI 在需要时可以读取的补充文档，例如：
- `REFERENCE.md` — 详细技术参考
- `FORMS.md` — 表单模板或结构化数据格式
- 特定领域的文档（如 `finance.md`、`legal.md`）

**建议每个参考文件保持聚焦**，因为 AI 是按需加载这些文件的，文件越小，消耗的上下文越少。

**大型参考文件（>300 行）应包含目录**（Table of Contents）。

### assets/ 目录

存放静态资源文件，包括：
- 模板文件（文档模板、配置模板）
- 图片（示意图、示例图）
- 数据文件（查找表、Schema 定义）
