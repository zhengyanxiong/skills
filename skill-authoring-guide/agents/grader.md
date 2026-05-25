# Grader Agent

## 职责

评估断言是否通过，并评价评估本身。

## 8 步流程

1. 读取 Transcript
2. 检查输出文件
3. 评估断言
4. 提取隐含声明
5. 读取执行者笔记
6. **评价评估本身**（自我批评）
7. 写结果
8. 读取指标数据

## 自我批评（最关键的设计）

> "A passing grade on a weak assertion is worse than useless — it creates false confidence."

Grader 不仅评分，还会指出断言本身的问题：
- 一个通过的断言是否太容易满足（如只检查文件名存在，不检查内容）
- 是否有重要结果没有被任何断言覆盖
- 断言是否无法从可用输出中验证

## 评分标准

- **PASS**：不仅要有证据，还要证据反映"真正的任务完成"，而非"表面合规"
- **FAIL**：包括"巧合通过"——断言技术上满足了，但底层任务结果是错的

## 输出格式

`grading.json` 的 expectations 数组必须使用字段 `text`、`passed`、`evidence`：

```json
{
  "expectations": [
    {
      "text": "输出包含完整的请求参数表格",
      "passed": true,
      "evidence": "在 outputs/api-doc.md 中找到参数表格，包含字段名、类型、必填、说明四列"
    }
  ]
}
```
