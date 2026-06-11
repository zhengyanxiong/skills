# GC 日志格式参考

> 供 capability-evolver 维护者和扩展者参考。记录了 `parse_gc_events()` 支持的日志格式及解析陷阱。

## 一、支持的格式

### 1. 现代 G1/ZGC 格式 (JDK 11+ `-Xlog:gc*`)

```
[2026-06-11T10:00:00.224+0000][gc] GC(N) Pause Young (Normal) (G1 Evacuation Pause) 512M->384M(1024M) 101.2ms
[2026-06-11T10:01:02.300+0000][gc] GC(N) Pause Full (Allocation Failure) 2G->1G(2G) 2300.5ms
[2026-06-11T10:00:00.224+0000][gc,cpu] GC(N) User=0.45s Sys=0.08s Real=0.10s
[2026-06-11T10:00:00.224+0000][gc,heap] GC(N) Eden regions: 128->0 (48)
[2026-06-11T10:00:00.224+0000][gc,metaspace] GC(N) Metaspace: 48.5M(64.0M)->48.5M(64.0M)
```

解析正则 (modern_gc):
```
GC\((\d+)\)\s+(Pause\s+(?:Young|Full|Mixed))\s+.*?(\d+(?:\.\d+)?[KMG])\s*->\s*(\d+(?:\.\d+)?[KMG])\((\d+(?:\.\d+)?[KMG])\)\s+([\d.]+)ms
```

**注意** heap 大小可以含小数 (如 `1.5G`)，必须用 `\d+(?:\.\d+)?[KMG]` 而非 `\d+[KMG]`。

### 2. 传统 Parallel GC 格式 (JDK 8 常用)

**Young GC:**
```
2026-06-11T10:02:00.123+0800: 120.123: [GC (Allocation Failure) [PSYoungGen: 2048K->1024K(4096K)] 8192K->7168K(16384K), 0.015 ms] [Times: user=0.01 sys=0.01, real=0.02 secs]
```

**Full GC (含 Metaspace):**
```
2026-06-11T10:02:15.456+0800: 135.456: [Full GC (Ergonomics) [PSYoungGen: 4096K->0K(4096K)] [ParOldGen: 11264K->11264K(12288K)] 15360K->11264K(16384K), [Metaspace: 32768K->32768K(65536K)], 0.890 secs]
```

解析注意：
- Young GC 暂停单位是 **ms** (`0.015 ms`)
- Full GC 暂停单位是 **secs** (`0.890 secs`) — 捕获后 ×1000 转为 ms
- Metaspace 出现在 `[Metaspace: X->Y(Max)]` 方括号中，在 heap 之后、暂停时间之前。解析 Full GC 的末尾暂停时间时，需要用 `(?:\[[^\]]*\]\s*,?\s*)*` 跳过中间的可选方括号组

### 3. CMS 格式 (较少见)

```
2026-06-11T10:00:00.123+0800: [GC [ParNew: 2048K->256K(4096K)] 8192K->6412K(16384K), 0.023 secs]
2026-06-11T10:00:00.456+0800: [GC [CMS: 11264K->11264K(12288K), 0.567 secs] 17408K->11264K(16384K), [CMS Perm : 32768K->32768K(65536K)], 0.567 secs]
2026-06-11T10:00:05.789+0800: [Full GC [CMS: 12288K->12288K(12288K), 1.234 secs] 16384K->12288K(16384K), [CMS Perm : 65536K->65536K(65536K)], 1.234 secs]
```

CMS 格式比 Parallel 更复杂，暂未在 `legacy_full`/`legacy_young` 正则中完整覆盖。如果遇到 CMS 日志、解析失败，需要添加 `cms_young` 和 `cms_cms` 两条额外正则。

## 二、已知解析陷阱

### 陷阱 1: 小数 heap 大小

| 错误 | 正确 |
|------|------|
| `(\d+[KMG])` | `(\d+(?:\.\d+)?[KMG])` |

现代 G1 GC 日志可能输出 `1.5G`、`0.5M` 等小数。`\d+[KMG]` 只能匹配 `\d+` 部分（如 `1`），然后 `[KMG]` 尝试匹配 `.` 导致失败。

### 陷阱 2: 暂停时间单位不一致

| GC 类型 | 格式 | 单位 | 正则 |
|---------|------|------|------|
| 现代 GC 主行 | `101.2ms` | ms | `([\d.]+)ms` |
| 传统 Young GC | `0.015 ms` | ms | `([\d.]+)\s*ms\]` |
| 传统 Full GC | `0.890 secs` | seconds | `([\d.]+)\s*secs` → ×1000 |

### 陷阱 3: Legacy Full GC 的 Metaspace 干扰

传统 Full GC 格式中 heap 数据 `15360K->11264K(16384K)` 之后先出现 `[Metaspace: 32768K->32768K(65536K)]`，再出现 `0.890 secs`。

如果用 `,\s*([\d.]+)\s*secs` 直接匹配，会匹配 `, [Metaspace: ...]` 的第一个逗号而非末尾的逗号。

**修复**：用 `(?:\[[^\]]*\]\s*,?\s*)*` 跳过中间的所有方括号组。

### 陷阱 4: 多日志行关联

现代 G1 GC 格式中，同一 GC 事件的信息分散在多行：
- `[gc]` 主行 — GC 类型、heap 变化、暂停时间
- `[gc,heap]` — Eden/Survivor/Old 各代 region 数
- `[gc,metaspace]` — Metaspace 使用情况
- `[gc,cpu]` — CPU 时间

这些行通过 `GC(N)` 的编号关联。处理时先扫描所有行收集到 `heap_info_by_gc` / `cpu_info_by_gc` 字典，遇到 `[gc]` 主行时合并。

### 陷阱 5: 时间戳格式不一

| 来源 | 示例 |
|------|------|
| Docker 日志 | `2026-06-11T10:00:00.123456789Z` |
| GC 日志 | `[2026-06-11T10:00:00.224+0000]` |
| 传统 GC | `2026-06-11T10:02:00.123+0800: 120.123:` |

传统格式中 `: 120.123:` 是 JVM 启动后的秒数偏移，不影响解析但需要注意这不是时间戳的一部分。

## 三、GC 事件结构

```python
GCEvent = {
    "timestamp": str,           # 日志时间戳
    "gc_id": int,               # GC 事件编号
    "gc_type": str,             # "young" | "full" | "mixed"
    "gc_name": str,             # "G1" | "Parallel" | "ZGC" | "Shenandoah" | "Unknown"
    "pause_time_ms": float,     # 暂停毫秒数
    "heap_before": int,         # 堆 GC 前大小 (bytes)
    "heap_after": int,          # 堆 GC 后大小 (bytes)
    "heap_max": int,            # 堆最大容量 (bytes)
    "recovery_mb": float,       # 本次回收量 (MB)
    "heap_info": dict,          # 各代信息 (eden/survivor/old/humongous/metaspace)
    "cpu": dict,                # {"user_s": float, "sys_s": float, "real_s": float}
}
```

## 四、验证方法

解析正确性验证：

```bash
# 快速验证一条日志是否能被解析
python3 -c "
from analyze_logs import parse_gc_events, fetch_file_logs
logs = fetch_file_logs('test-gc.log', 500)
events = parse_gc_events(logs)
for e in events:
    print(f'GC#{e[\"gc_id\"]:>3} {e[\"gc_type\"]:>5} '
          f'{e[\"heap_before\"]/1024/1024:5.0f}M->{e[\"heap_after\"]/1024/1024:4.0f}M'
          f'({e[\"heap_max\"]/1024/1024:4.0f}M) {e[\"pause_time_ms\"]:8.1f}ms')
"
```

若发现未被解析的 GC 行，打印该行并用分段正则测试定位问题。
