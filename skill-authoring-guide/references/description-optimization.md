# Description 优化指南

## 为什么重要

Description 是主要触发机制，决定 Claude 是否调用 Skill。Claude 有 undertrigger 倾向——即使 Skill 有用也可能不触发。

## 优化步骤

### 步骤 1：生成触发评估查询

创建 20 个评估查询——混合 should-trigger 和 should-not-trigger：

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

**查询要求**：
- 真实、具体、有细节（文件路径、列名、公司名、URL）
- 包含大小写混合、缩写、错别字、 casual speech
- 不同长度，聚焦边缘案例而非清晰案例

**should-trigger（8-10）**：
- 不同措辞的相同意图（正式/ casual）
- 未明确命名 Skill 但明显需要
- 不常见用例
- 与竞争 Skill 对比但应获胜

**should-not-trigger（8-10）**：
- Near-misses：共享关键词但不同需求
- 相邻领域
- 模糊措辞
- 触及 Skill 能力但其他工具更合适

**差的查询**：`"Format this data"`、`"Extract text from PDF"` —— 太抽象
**好的查询**：`"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"` —— 具体、有细节、 casual

### 步骤 2：用户评审

使用 HTML 模板展示评估集，用户可编辑查询、切换 should-trigger、添加/删除条目。

### 步骤 3：运行优化循环

```bash
python -m scripts.run_loop   --eval-set <path>   --skill-path <path>   --model <model-id>   --max-iterations 5   --verbose
```

**自动处理**：
- 60% train / 40% test 分割
- 每次查询运行 3 次获取可靠触发率
- Claude 基于失败案例提出改进
- 在 train 和 test 上重新评估新 description
- 最多 5 次迭代
- 返回 JSON 含 `best_description`（按 test score 选择，避免过拟合）

### 触发机制理解

Claude 只在需要时才咨询 Skill——简单的一步查询（如"read this PDF"）即使 description 完美匹配也可能不触发，因为 Claude 可直接用基础工具处理。

**评估查询应足够实质**，让 Claude 确实能从咨询 Skill 中受益。
