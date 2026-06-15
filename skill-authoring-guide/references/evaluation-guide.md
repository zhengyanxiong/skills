# Skill 评估指南

## 评估体系：A/B 测试 + 量化断言

### 六阶段闭环流程

```
需求捕获 → 编写 Skill → 测试执行 → 评估评审 → 迭代改进 → 优化发布
```

### 测试设计原则

1. 设计 **2-3 个测试用例**，覆盖典型场景和边界场景
2. **并行运行** `with_skill` 和 `without_skill` 两组 Agent（A/B 测试）
3. 用 **量化断言** 而非主观判断

### 测试用例格式（evals.json）

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

### 断言设计示例（assertions.json）

```json
{
  "skill_name": "api-doc-generator",
  "assertions": [
    {
      "id": "A1",
      "description": "输出包含完整的请求参数表格（字段名、类型、必填、说明）",
      "type": "structure",
      "weight": 1.0
    },
    {
      "id": "A2",
      "description": "输出包含响应体结构说明",
      "type": "completeness",
      "weight": 1.0
    },
    {
      "id": "A3",
      "description": "如果输入包含实体类，必须生成对应的 DTO/VO 类定义",
      "type": "correctness",
      "weight": 1.0
    }
  ]
}
```

### 评分断言格式（grading.json）

每次 eval 运行后，Grader Agent 按此格式输出：

```json
{
  "eval_id": 1,
  "eval_name": "api-doc-generation",
  "prompt": "The user's task prompt",
  "assertions": [
    {
      "id": "A1",
      "text": "输出包含完整的请求参数表格",
      "passed": true,
      "evidence": "Output contains a table with columns: 字段名, 类型, 必填, 说明, covering all 8 parameters"
    }
  ]
}
```

### 工作区目录结构

```
{skill-name}-workspace/
  iteration-1/
    eval-0/
      with_skill/outputs/
      without_skill/outputs/
      timing.json          # token 和耗时数据
      eval_metadata.json   # 断言定义
      grading.json         # 评分结果
    eval-1/
      ...
    benchmark.json         # 聚合基准数据
    benchmark.md           # 可读基准报告
```

### 时序数据捕获（timing.json）

子 Agent 完成时自动保存：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

## 三个专业化评估 Agent

| Agent | 职责 | 核心设计 |
|-------|------|----------|
| **Grader** | 评估断言是否通过 | 自我批评：指出薄弱断言和遗漏覆盖 |
| **Comparator** | 盲比较 A/B 输出 | 双盲实验，去偏见化 |
| **Analyzer** | 分析 WHY 赢家赢了 | 方差分析、非判别性断言检测、改进建议 |

### Grader Agent 要点

- 每个 assertion 必须有 `passed` + `evidence`
- **PASS**：不仅要有证据，还要证据反映"真正的任务完成"，而非"表面合规"
- **FAIL**：包括"巧合通过"——断言技术上满足了，但底层任务结果是错的
- 自我批评：完成后指出哪些断言太弱、哪些场景没覆盖

### Analyzer Agent 方差分析

Analyzer 做三件事：

1. **非判别性断言检测**：如果 with_skill 和 without_skill 都通过的断言，说明该断言无法区分 Skill 价值 → 降权或重写
2. **高方差检测**：同一 eval 多次运行结果不一致 → 说明指令不够确定性，需要加固
3. **时间/Token 权衡**：with_skill 耗时/耗 token 更多时，评估增量价值是否值得成本

## 聚合基准（Benchmark）

### 运行聚合

```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

生成 `benchmark.json` 和 `benchmark.md`，包含：

| 指标 | 含义 |
|------|------|
| pass_rate | 断言通过率 |
| mean_tokens ± stddev | 平均 token 消耗及标准差 |
| mean_duration ± stddev | 平均耗时及标准差 |
| delta_vs_baseline | 相对 baseline 的变化 |

### 可视化 Viewer

```bash
python <skill-path>/eval-viewer/generate_review.py \
  <workspace>/iteration-N \
  --skill-name "my-skill" \
  --benchmark <workspace>/iteration-N/benchmark.json
```

生成浏览器可查看的评估报告。迭代对比时加 `--previous-workspace` 参数。

## 评分标准

- **PASS**：不仅要有证据，还要证据反映"真正的任务完成"，而非"表面合规"
- **FAIL**：包括"巧合通过"——断言技术上满足了，但底层任务结果是错的

## 迭代原则

1. **泛化而非过拟合**：遇到顽固问题，换个隐喻或推荐不同工作模式
2. **提取重复模式**：如果所有测试用例中 Agent 都独立写了类似的辅助脚本，应该放到 `scripts/` 目录
3. **避免虚假信心**：一个通过的断言如果太容易满足，其危害比毫无用处还要糟糕
4. **读 transcript**：不只看最终输出，阅读完整 transcript 理解 Agent 的推理过程
5. **对照前次迭代**：使用 `--previous-workspace` 对比改进效果
