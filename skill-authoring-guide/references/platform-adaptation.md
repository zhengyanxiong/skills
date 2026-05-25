# 多平台适配指南

## Claude Code

**特点**：有 subagents，可并行执行 A/B 测试

**完整工作流**：
1. 同 turn 启动 with-skill + baseline 子 Agent
2. 使用 `eval-viewer/generate_review.py` 生成浏览器查看器
3. 使用 `claude -p` 运行 description 优化循环
4. 使用 `scripts.package_skill` 打包 `.skill` 文件

## Claude.ai

**特点**：无 subagents，无法并行执行

**适配方案**：
1. **运行测试**：自行执行测试用例（无并行），一次一个
2. **跳过 baseline**：只测试 with-skill 版本
3. **评审结果**：直接在对话中展示结果，询问用户反馈
4. **跳过 description 优化**：`claude -p` 不可用
5. **跳过盲比较**：需要 subagents
6. **打包**：`package_skill.py` 可在任何有 Python 和文件系统的环境运行

**更新现有 Skill**：
- 保留原始 name 和目录名
- 复制到可写位置（如 `/tmp/skill-name/`）再编辑
- 从副本打包

## Cowork

**特点**：有 subagents 但无浏览器/显示器

**适配方案**：
1. **测试执行**：subagents 可用，可并行。但如遇超时，可串行执行
2. **Eval Viewer**：使用 `--static` 参数生成静态 HTML 文件：
   ```bash
   python eval-viewer/generate_review.py /iteration-N --static /output.html
   ```
   然后提供链接让用户在浏览器中打开
3. **Feedback**："Submit All Reviews" 按钮会下载 `feedback.json` 文件，从下载文件夹读取
4. **Description 优化**：`run_loop.py` / `run_eval.py` 可用（通过 subprocess 调用 `claude -p`）
5. **更新现有 Skill**：遵循 Claude.ai 的更新指导

## OpenClaw / Kimi / 其他平台

**通用原则**：
- SKILL.md 格式（YAML frontmatter + Markdown body）是开放标准，通用
- subagents 支持情况决定是否能执行 A/B 测试
- 无 subagents 时，采用 Claude.ai 的适配方案
- description 优化需要平台支持自动触发测试
