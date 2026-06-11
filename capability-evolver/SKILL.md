---
name: capability-evolver
description: >
  Use this skill when asked to analyze runtime logs, diagnose system errors, check service health, identify performance bottlenecks, or generate improvement plans. Works with Docker containers, log files, or piped stdin. Detects error patterns, OOM/GC issues (JVM), network failures, slow operations, cascading failures, and regression signals. Computes a health score (0-100) and produces structured recommendations. 中文触发: 分析日志、检查服务健康、诊断错误、性能分析、OOM、GC 暂停、Full GC、堆溢出、瓶颈定位。Make sure to use this skill whenever the user mentions log analysis, error diagnosis, health checks, OOM, GC pauses, performance bottlenecks, or system diagnostics — even if they don't explicitly ask for 'capability-evolver.'
version: 2.2.0
license: MIT-0
metadata:
  author: zhengyanxiong
  category: devops
  tags: [logs, diagnostics, jvm, gc, monitoring, performance]
compatibility: Python 3.10+ with Docker CLI (optional, for --source docker)
---
# Capability Evolver — 通用日志分析引擎

> 确定性日志分析引擎：分析运行时日志 → 检测错误模式、OOM/GC 瓶颈、回归、低效 → 计算健康评分 → 生成改进建议。
> 原版: [kennyzir/capability-evolver](https://github.com/kennyzir/capability-evolver)

## 1. 何时使用

当用户需要以下任何一项时触发：

- **分析应用日志** — 查看运行中的错误、警告、异常
- **诊断服务健康** — 检查服务是否稳定，有没有隐藏问题
- **定位性能瓶颈** — 慢操作、GC 暂停、超时
- **JVM/GC 问题排查** — OOM、Full GC 频繁、堆压力、元空间泄漏
- **生成改进方案** — 基于日志分析输出结构化优化建议
- **回归检测** — 判断最近变更是否引入了新错误

> Agent 会自动检测日志来源（Docker 容器 → 本地文件 → stdin），无需手动指定。

### 何时不使用

- 需要实时监控面板（用 Prometheus/Grafana）
- 需要深度堆转储分析（用 Eclipse MAT）
- 日志文件超过 100MB（建议先截取最近 500~2000 行）

## 2. 核心设计原则

### 为什么用这个引擎，而不是直接 grep

| 问题 | grep | capability-evolver |
|------|------|-------------------|
| 重复错误 | 手动 count | 自动聚合 + 动态严重度 |
| 回归信号 | 看不出 | 高频错误自动标记 |
| 慢操作 | 需自写 regex | 内置 timeout/ms/latency 检测 |
| 级联错误 | 需跨行分析 | 30s 窗口自动关联 |
| GC/堆分析 | 看不懂 GC 日志 | 结构化解析 + 趋势分析 |
| 健康评分 | ❌ | 0-100 量化指标 |
| 改进方案 | ❌ | 按策略生成结构化建议 |

### 三层检测策略

1. **文本模式匹配** — OOM 异常、StackOverflow、线程池拒绝等 20+ 种 JVM 模式
2. **结构化 GC 解析** — 解析 `-Xlog:gc*` 格式的暂停时间、堆占用、回收效率
3. **定量趋势分析** — 比较前后半段回收效率、连续 Full GC 回收量变化，预判 OOM

## 3. 使用方式

### 命令行

```bash
# 1) 分析 Docker 容器日志（推荐）
python3 ~/.hermes/skills/capability-evolver/scripts/analyze_logs.py analyze --source docker --container my-app --lines 500

# 2) 分析本地文件
python3 ~/.hermes/skills/capability-evolver/scripts/analyze_logs.py analyze --source file --path /var/log/app.log --lines 500

# 3) 管道输入
cat app.log | python3 ~/.hermes/skills/capability-evolver/scripts/analyze_logs.py analyze --source stdin

# 4) 生成改进方案
python3 ~/.hermes/skills/capability-evolver/scripts/analyze_logs.py evolve --source docker --container my-app --strategy harden

# 5) 查看能力信息
python3 ~/.hermes/skills/capability-evolver/scripts/analyze_logs.py status
```

### Agent 自动模式

在对话中说 **"分析一下日志"**、**"检查后端健康"**、**"看看有没有 OOM"**、**"诊断错误"** 即可自动触发。Agent 会自动判断日志来源。

## 4. 日志来源

| 来源 | 参数 | 说明 |
|------|------|------|
| `auto` | (默认) | 自动检测：先试 Docker，再搜常见路径 |
| `docker` | `--container <容器名>` | 从 Docker 容器拉取，也支持环境变量 `CAPABILITY_EVOLVER_CONTAINER` |
| `file` | `--path <文件路径>` | 读取本地日志文件 |
| `stdin` | 管道输入 | `cat /var/log/syslog \| python3 analyze_logs.py analyze --source stdin` |

## 5. 分析能力

| 能力 | 说明 |
|------|------|
| 🔁 **重复错误检测** | 同一错误消息多次出现 → 自动聚合标记 |
| 📈 **回归信号检测** | 高频重复错误（≥3 次）→ 标记为回归 |
| 🐢 **慢操作检测** | 匹配 `timeout` / `ms` 耗时 / `latency` 等关键词 |
| 🔗 **级联错误分析** | 30 秒窗口内跨模块错误链检测 |
| 🌐 **网络异常检测** | `connection` / `refused` / `timeout` / `reset` 等通用连接错误 |
| ☕ **JVM 诊断 (20+ 种模式)** | OOM 分类、GC 暂停/频率分析、线程死锁、栈溢出、元空间泄漏… |
| ⏱ **GC 耗时分析** | 自动提取 GC 暂停时间，量化 STW（Stop-The-World）影响 |
| 📊 **堆占用分析** | 实时堆占用率监控，预警 OOM 风险 |
| 📉 **回收效率趋势** | 跟踪 GC 回收率变化，识别内存泄漏前兆 |
| 🔥 **热点模块定位** | 按错误频率排序问题模块 |
| 💚 **健康评分** | 0-100 量化健康状态，含错误/警告权重 |

## 6. JVM 诊断能力

### 检测模式清单

| 类别 | 模式 | 严重度 | 说明 |
|------|------|--------|------|
| 🚨 OOM | `oom-heap` | 🔴 critical | Java heap space — 堆内存溢出 |
| 🚨 OOM | `oom-gc-overhead` | 🔴 critical | GC 开销超限 (98%+ 时间 GC) |
| 🚨 OOM | `oom-metaspace` | 🔴 critical | 元空间/永久代溢出 |
| 🚨 OOM | `oom-native-thread` | 🔴 critical | 无法创建原生线程 |
| 🚨 OOM | `oom-direct-memory` | 🔴 critical | Direct buffer memory |
| 🚨 OOM | `oom-swap` | 🔴 critical | Swap 空间溢出 |
| 🚨 OOM | `oom-requested-array` | 🟠 high | 数组大小超 JVM 限制 |
| 🚨 栈 | `stackoverflow` | 🟠 high | StackOverflowError |
| ⏱ GC | `full-gc` | 🟠 high | Full GC (含定量暂停分析: 次数/平均/最长) |
| ⏱ GC | `gc-pause-long` | 🟠 high | 平均暂停 >100ms |
| ⏱ GC | `gc-pause-high` | 🟠~🔴 | 超过 1s 的暂停 (最长/平均/累计 STW) |
| ⏱ GC | `gc-high-frequency` | 🟠 high | GC 事件占比 > 30% |
| ⏱ GC | `heap-pressure` | 🟡~🔴 | 堆占用率 > 70%/90%/95% |
| ⏱ GC | `gc-efficiency-decline` | 🟠~🔴 | 回收效率持续下降，内存泄漏前兆 |
| ⏱ GC | `oom-impending` | 🔴 critical | 连续 Full GC + 回收量递减 → OOM 即将发生 |
| ⏱ GC | `metaspace-pressure` | 🟠 high | 元空间占用率 > 90% |
| ⏱ GC | `gc-promotion-failed` | 🟠 high | 提升失败 |
| ⏱ GC | `gc-concurrent-mode` | 🟠 high | CMS 并发模式失败 |
| ⏱ GC | `gc-frequent` | 🟡 medium | 年轻代 GC 过于频繁 |
| ⏱ GC | `metaspace-growth` | 🟡 medium | 元空间持续增长 |
| 🧵 线程 | `thread-deadlock` | 🔴 critical | Java 级别线程死锁 |
| 🧵 线程 | `thread-pool-exhausted` | 🟠 high | 线程池任务被拒绝 |
| 🛠 其他 | `codecache-full` | 🟡 medium | JIT 编译缓存满 |
| 🛠 其他 | `compressed-oops` | 🟢 low | 压缩指针禁用 (>32GB 堆) |

### 优化建议示例

检测到 JVM 问题后自动生成结构化调优建议：

```
🔴 JVM 堆溢出 — 增大 -Xmx 或使用 jmap dump 分析堆转储定位泄漏
🔴 线程数超限 — 检查线程泄漏，增大 ulimit -u，或减小线程池大小
🟠 Full GC 触发 5 次 — 老年代空间不足，增大 -Xmx 或调整 -XX:NewRatio
🟠 GC 暂停过长 — 考虑 G1GC: -XX:+UseG1GC -XX:MaxGCPauseMillis=200
🟡 年轻代 GC 频繁 — 分析对象分配率，增大新生代 (-Xmn)
🔴 线程死锁 — 用 jstack 获取线程转储，分析锁顺序并修复
💡 GC 调优一般原则: -Xmx 设为堆峰值 1.5-2x，监控 GC 日志逐步调优
```

## 7. Evolution 策略

| 策略 | 倾向 | 适用场景 |
|------|------|----------|
| `auto` | 根据健康分自动选 | 默认 |
| `balanced` | 可靠性和功能均衡 | 中等健康 |
| `innovate` | 优先新能力 | 健康系统 (健康分 > 70) |
| `harden` | 优先可靠性 | 频繁故障 |
| `repair-only` | 只修关键问题 | 崩溃中系统 (健康分 < 40) |

## 8. 输出格式

```json
{
  "patterns": [
    {
      "type": "error|regression|inefficiency|jvm",
      "severity": "low|medium|high|critical",
      "description": "...",
      "occurrences": 5,
      "affected_contexts": ["ServiceA", "ServiceB"]
    }
  ],
  "health_score": 72,
  "recommendations": ["..."],
  "summary": {
    "total_logs": 500,
    "error_count": 3,
    "warn_count": 12,
    "unique_patterns": 2,
    "critical_count": 0
  }
}
```

## 9. 边界情况处理

| 场景 | 处理方式 |
|------|----------|
| Docker 容器不存在 | 询问引导用户输入容器名称 |
| 没有日志 | 提示检查容器名或文件路径，列出运行中的容器 |
| JDK 8 旧格式 GC 日志 | 自动识别 Parallel GC `[Full GC ...]` 格式 |
| JRE 无 jcmd | 只分析 stdout 日志，不尝试 docker exec |
| 日志含 ANSI 颜色码 | 解析器自动处理（不退化为乱码） |
| 超大日志文件 (>10MB) | 只取最后 N 行，建议显式指定 --lines |
| 非 Java 应用日志 | 仍可使用重复错误、慢操作、级联、健康分能力 |
| 空日志或无 ERROR/WARN | 健康分 = 100，返回无 pattern 的空结果 |

## 10. 文件引用规范

以下 L3 资源按需加载，不占用当前上下文：

- `scripts/analyze_logs.py` — 日志分析引擎主脚本。当需要直接运行分析或修改分析逻辑时加载。
- `references/gc-log-format-reference.md` — GC 日志格式详解、正则陷阱和验证方法。在扩展 GC 解析或调试匹配失败时必读。
