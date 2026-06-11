#!/usr/bin/env python3
"""
Capability Evolver — 通用确定性日志分析引擎
分析运行时日志，检测错误模式、回归、低效，计算健康评分，生成改进建议。
支持 Docker、本地文件、标准输入三种日志源。
"""
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime

# ─── 常量 ───────────────────────────────────────────────────
VALID_ACTIONS = ["analyze", "evolve", "status"]
VALID_STRATEGIES = ["auto", "balanced", "innovate", "harden", "repair-only"]
VALID_SOURCES = ["auto", "docker", "file", "stdin"]
VERSION = "2.2.0"

LogEntry = dict
PatternEntry = dict


# ─── 日志获取 ───────────────────────────────────────────────

def fetch_logs(source: str = "auto", container: str = None,
               file_path: str = None, lines: int = 500,
               since: str = None) -> list[LogEntry]:
    """从指定来源获取日志并解析为结构化条目"""
    if source == "stdin" or (source == "auto" and not sys.stdin.isatty()):
        return parse_log_lines(sys.stdin.read())

    if source == "docker" or (source == "auto" and container):
        return fetch_docker_logs(container=container, lines=lines, since=since)

    if source == "file" or (source == "auto" and file_path):
        return fetch_file_logs(path=file_path, lines=lines)

    # auto 模式：尝试 docker → 常见日志路径
    logs = fetch_docker_logs(container=container or "_", lines=lines, since=since, silent=True)
    if logs:
        return logs
    common_paths = [
        "/var/log/app.log", "/var/log/application.log",
        "/var/log/backend.log", "/var/log/server.log",
        "/home/ubuntu/workspace/*/logs/app.log",
        "/home/ubuntu/workspace/*/backend/logs/app.log",
    ]
    if file_path:
        common_paths.insert(0, file_path)
    for pattern in common_paths:
        import glob
        matches = glob.glob(pattern)
        if matches:
            logs = fetch_file_logs(path=matches[0], lines=lines)
            if logs:
                return logs
    return []


def fetch_docker_logs(container: str, lines: int = 500,
                      since: str = None, silent: bool = False) -> list[LogEntry]:
    """从 Docker 容器拉取日志"""
    container = container or os.environ.get("CAPABILITY_EVOLVER_CONTAINER", "")
    if not container:
        return []
    cmd = ["docker", "logs", container, "--tail", str(lines), "--timestamps"]
    if since:
        cmd.extend(["--since", since])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            if not silent:
                print(f"⚠️  docker logs 失败: {result.stderr.strip()}", file=sys.stderr)
            return []
        return parse_log_lines(result.stdout)
    except FileNotFoundError:
        if not silent:
            print("⚠️  docker 命令未找到", file=sys.stderr)
        return []
    except subprocess.TimeoutExpired:
        if not silent:
            print("⚠️  docker logs 超时", file=sys.stderr)
        return []


def fetch_file_logs(path: str, lines: int = 500) -> list[LogEntry]:
    """从本地文件读取日志"""
    try:
        with open(path) as f:
            content = "".join(f.readlines()[-lines:])
            if content.strip():
                return parse_log_lines(content)
    except (FileNotFoundError, PermissionError, IsADirectoryError):
        pass
    return []


def parse_log_lines(raw: str) -> list[LogEntry]:
    """解析日志行为结构化条目 —— 支持常见日志格式"""
    entries = []
    # ISO 时间戳通用匹配
    iso_ts = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?00)?)')
    # 标准日志格式: [时间] [LEVEL] logger - message
    standard = re.compile(
        r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?00)?)'
        r'\s+(?:\[[^\]]*\]\s+)?(ERROR|WARN|INFO|DEBUG|TRACE|FATAL)\s+'
        r'([\w.]+)\s*[-:]\s*(.*)', re.IGNORECASE)
    # syslog 格式
    syslog = re.compile(
        r'^(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+\S+\s+'
        r'(\w+)(?:\[(\d+)\])?:\s*(.*)')

    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue

        # 标准日志格式
        m = standard.match(line)
        if m:
            entries.append({
                "timestamp": m.group(1),
                "level": m.group(2).lower(),
                "message": m.group(4).strip(),
                "context": m.group(3),
            })
            continue

        # syslog 格式
        m = syslog.match(line)
        if m:
            entries.append({
                "timestamp": m.group(1),
                "level": "error" if "ERROR" in m.group(4).upper() or "FATAL" in m.group(4).upper()
                            else "warn" if "WARN" in m.group(4).upper() else "info",
                "message": m.group(4).strip()[:200],
                "context": m.group(2),
            })
            continue

        # 无结构行 —— 自动检测级别
        dm = iso_ts.match(line)
        ts = dm.group(1) if dm else datetime.now().isoformat()
        message = line[dm.end():].strip() if dm else line[:200]
        upper = message.upper() if message else ""
        level = "error" if re.search(r'\b(ERROR|FATAL|CRITICAL|EXCEPTION|TRACE\(.*\))\b', upper) else \
                "warn" if re.search(r'\b(WARN|WARNING)\b', upper) else "info"

        # 尝试提取包名/模块名
        ctx = ""
        cls = re.search(r'(?:com|org|net|io|cn)\.[\w.]+', line)
        if cls:
            ctx = cls.group().split(".")[-1]
        else:
            mod = re.search(r'\[(\w+)\]', line)
            if mod:
                ctx = mod.group(1)

        entries.append({
            "timestamp": ts,
            "level": level,
            "message": message[:200],
            "context": ctx,
        })

    return entries


# ─── JVM/GC 诊断 ────────────────────────────────────────────

# JVM 问题类型及对应 regex
JVM_PATTERNS = {
    "oom-heap": {
        "label": "堆内存溢出 (OOM)",
        "severity": "critical",
        "regex": r'java\.lang\.OutOfMemoryError\s*:\s*Java heap space',
        "desc": "堆内存溢出 — 对象无法分配，可能导致应用崩溃",
    },
    "oom-gc-overhead": {
        "label": "GC 开销超限 (OOM)",
        "severity": "critical",
        "regex": r'GC overhead limit exceeded|java\.lang\.OutOfMemoryError.*GC overhead',
        "desc": "JVM 把 98%+ 时间花在 GC 上但回收不到 2% 堆",
    },
    "oom-metaspace": {
        "label": "元空间溢出 (OOM)",
        "severity": "critical",
        "regex": r'java\.lang\.OutOfMemoryError.*Metaspace|java\.lang\.OutOfMemoryError.*PermGen',
        "desc": "元空间/永久代溢出 — 类加载过多或内存泄漏",
    },
    "oom-native-thread": {
        "label": "无法创建原生线程 (OOM)",
        "severity": "critical",
        "regex": r'Unable to create new native thread|java\.lang\.OutOfMemoryError.*unable to create',
        "desc": "操作系统线程数达到上限 — 线程泄漏或线程池过大",
    },
    "oom-direct-memory": {
        "label": "直接内存溢出 (OOM)",
        "severity": "critical",
        "regex": r'Direct buffer memory|java\.lang\.OutOfMemoryError.*direct buffer',
        "desc": "直接内存 (DirectByteBuffer) 溢出 — NIO 操作未释放或配置过小",
    },
    "oom-swap": {
        "label": "Swap 空间溢出 (OOM)", "severity": "critical",
        "regex": r'Out of swap space|java\.lang\.OutOfMemoryError.*swap',
        "desc": "操作系统 Swap 空间耗尽 — 物理内存不足",
    },
    "oom-requested-array": {
        "label": "请求数组大小超限 (OOM)",
        "severity": "high",
        "regex": r'Requested array size exceeds VM limit',
        "desc": "试图创建超过 JVM 允许的最大数组",
    },
    "oom-other": {
        "label": "其他 OOM 异常",
        "severity": "critical",
        "regex": r'(?<!\.)OutOfMemoryError(?!.*?Java heap space|.*?Metaspace|.*?PermGen|.*?unable to create|.*?Direct buffer|.*?GC overhead|.*?swap|.*?array size)',
        "desc": "未分类的 OutOfMemoryError — 需进一步分析堆转储",
    },
    "stackoverflow": {
        "label": "栈溢出 (StackOverflow)",
        "severity": "high",
        "regex": r'StackOverflowError|java\.lang\.StackOverflowError',
        "desc": "调用栈过深 — 无限递归或递归层数过大",
    },
    "full-gc": {
        "label": "Full GC 频繁触发",
        "severity": "high",
        "regex": r'Full GC|FullGC',
        "desc": "Full GC 频繁触发意味着老年代空间紧张 — 典型的性能瓶颈信号",
    },
    "gc-pause-long": {
        "label": "GC 暂停时间过长",
        "severity": "high",
        "regex": r'GC pause.*(?:real|user|sys)=\s*[1-9]\.\d+ secs|gc.*\d+\.\d+s.*Full',
        "desc": "GC 暂停超过 1 秒 — 影响响应延迟和吞吐量",
    },
    "gc-frequent": {
        "label": "GC 过于频繁",
        "severity": "medium",
        "regex": r'Allocation Failure|allocation failure|GC.*young.*\d+K->',
        "desc": "频繁的年轻代 GC — 对象分配率过高或新生代太小",
    },
    "gc-promotion-failed": {
        "label": "GC 提升失败",
        "severity": "high",
        "regex": r'promotion failed|Promotion Failed|to-space overflow',
        "desc": "对象无法从年轻代提升到老年代 — 老年代空间不足",
    },
    "gc-concurrent-mode": {
        "label": "CMS 并发模式失败",
        "severity": "high",
        "regex": r'concurrent mode failure|Concurrent Mode Failure',
        "desc": "CMS 在并发收集完成前老年代就被填满 — 退化为 Serial Old GC",
    },
    "metaspace-growth": {
        "label": "Metaspace 持续增长",
        "severity": "medium",
        "regex": r'Metaspace.*(?:full|grow|up|class|load)',
        "desc": "元空间持续增长 — 类加载器泄漏或动态类生成过多",
    },
    "thread-deadlock": {
        "label": "线程死锁",
        "severity": "critical",
        "regex": r'deadlock|Found\s+\d+\s+Java-level\s+deadlock',
        "desc": "Java 级别线程死锁 — 线程互相等待锁释放",
    },
    "thread-pool-exhausted": {
        "label": "线程池耗尽",
        "severity": "high",
        "regex": r'RejectedExecutionException|Thread pool exhausted|rejected.*task|queue is full|线程池已满',
        "desc": "线程池任务队列满，新任务被拒绝 — 并发压力过大或线程泄漏",
    },
    "codecache-full": {
        "label": "CodeCache 已满",
        "severity": "medium",
        "regex": r'CodeCache is full|code cache|CodeCache.*full',
        "desc": "JIT 编译缓存满 — 编译器暂停，热点方法性能下降",
    },
    "compressed-oops": {
        "label": "压缩指针被禁用",
        "severity": "low",
        "regex": r'UseCompressedOops.*false|CompressedClassSpaceSize.*reserved',
        "desc": "堆 > 32GB 时压缩指针自动关闭 — 对象引用占用增大",
    },
}


# ─── GC 日志解析 ────────────────────────────────────────────

GCEvent = dict

def parse_mem_size(s: str) -> int:
    """解析内存大小字符串 ('512M', '2G', '1.5G', '1024K') 为字节数"""
    s = s.strip().upper()
    try:
        if s.endswith('G'):
            return int(float(s[:-1]) * 1024 * 1024 * 1024)
        elif s.endswith('M'):
            return int(float(s[:-1]) * 1024 * 1024)
        elif s.endswith('K'):
            return int(float(s[:-1]) * 1024)
        else:
            return int(s)
    except (ValueError, TypeError):
        return 0


def parse_gc_events(logs: list[LogEntry]) -> list[GCEvent]:
    """从日志中解析结构化的 GC 事件，支持现代 [gc] 标签格式和传统 Parallel GC 格式"""
    events: list[GCEvent] = []
    gc_id_counter = [0]

    # 现代 G1/ZGC 格式: [gc] GC(N) Pause Type ... before->after(max) pausems
    modern_gc = re.compile(
        r'GC\((\d+)\)\s+(Pause\s+(?:Young|Full|Mixed))\s+.*?'
        r'(\d+(?:\.\d+)?[KMG])\s*->\s*(\d+(?:\.\d+)?[KMG])\s*\((\d+(?:\.\d+)?[KMG])\)\s+([\d.]+)ms'
    )
    # 现代 [gc,heap] 格式: 提取各代信息
    modern_eden = re.compile(r'\[gc,heap\] GC\(\d+\) Eden regions:\s*(\d+)\s*->\s*(\d+)\s*\((\d+)\)')
    modern_surv = re.compile(r'\[gc,heap\] GC\(\d+\) Survivor regions:\s*(\d+)\s*->\s*(\d+)\s*\((\d+)\)')
    modern_old = re.compile(r'\[gc,heap\] GC\(\d+\) Old regions:\s*(\d+)\s*->\s*(\d+)')
    modern_hum = re.compile(r'\[gc,heap\] GC\(\d+\) Humongous regions:\s*(\d+)\s*->\s*(\d+)')
    modern_meta = re.compile(
        r'\[gc,metaspace\] GC\(\d+\) Metaspace:\s*([\d.]+[KMG])\(([\d.]+[KMG])\)\s*->\s*([\d.]+[KMG])\(([\d.]+[KMG])\)'
    )
    modern_cpu = re.compile(r'\[gc,cpu\] GC\(\d+\) User=([\d.]+)s Sys=([\d.]+)s Real=([\d.]+)s')

    # 传统 Parallel GC 格式
    legacy_young = re.compile(
        r'\[GC\s+\(([^)]+)\)\s*\[(?:PSYoungGen|DefNew|ParNew|Eden):\s*(\d+(?:\.\d+)?[KMG])->(\d+(?:\.\d+)?[KMG])\((\d+(?:\.\d+)?[KMG])\)\]\s*'
        r'(\d+(?:\.\d+)?[KMG])->(\d+(?:\.\d+)?[KMG])\((\d+(?:\.\d+)?[KMG])\),\s*([\d.]+)\s*ms\]'
    )
    legacy_full = re.compile(
        r'\[Full\s+GC\s+\(([^)]+)\)\s*'
        r'(?:\[[^\]]*\]\s+)*(\d+(?:\.\d+)?[KMG])->(\d+(?:\.\d+)?[KMG])\((\d+(?:\.\d+)?[KMG])\),\s*'
        r'(?:\[[^\]]*\]\s*,?\s*)*([\d.]+)\s*secs'
    )
    legacy_meta = re.compile(
        r'\[Metaspace:\s*(\d+(?:\.\d+)?[KMG])->(\d+(?:\.\d+)?[KMG])\((\d+(?:\.\d+)?[KMG])\)\]'
    )
    legacy_pause = re.compile(r'(?:real|Real)=\s*([\d.]+)\s*secs')

    # 先扫描所有日志，收集 heap 信息和 CPU 时间留给对应的 GC 事件
    heap_info_by_gc = {}
    cpu_info_by_gc = {}

    for log in logs:
        msg = log["message"]

        m = modern_eden.search(msg)
        if m:
            gid = int(re.search(r'GC\((\d+)\)', msg).group(1)) if re.search(r'GC\((\d+)\)', msg) else 0
            heap_info_by_gc.setdefault(gid, {})["eden"] = {
                "before": int(m.group(1)), "after": int(m.group(2)), "capacity": int(m.group(3))
            }
            continue

        m = modern_surv.search(msg)
        if m:
            gid = int(re.search(r'GC\((\d+)\)', msg).group(1)) if re.search(r'GC\((\d+)\)', msg) else 0
            heap_info_by_gc.setdefault(gid, {})["survivor"] = {
                "before": int(m.group(1)), "after": int(m.group(2)), "capacity": int(m.group(3))
            }
            continue

        m = modern_old.search(msg)
        if m:
            gid = int(re.search(r'GC\((\d+)\)', msg).group(1)) if re.search(r'GC\((\d+)\)', msg) else 0
            heap_info_by_gc.setdefault(gid, {})["old"] = {
                "before": int(m.group(1)), "after": int(m.group(2))
            }
            continue

        m = modern_hum.search(msg)
        if m:
            gid = int(re.search(r'GC\((\d+)\)', msg).group(1)) if re.search(r'GC\((\d+)\)', msg) else 0
            heap_info_by_gc.setdefault(gid, {})["humongous"] = {
                "before": int(m.group(1)), "after": int(m.group(2))
            }
            continue

        m = modern_meta.search(msg)
        if m:
            gid = int(re.search(r'GC\((\d+)\)', msg).group(1)) if re.search(r'GC\((\d+)\)', msg) else 0
            heap_info_by_gc.setdefault(gid, {})["metaspace"] = {
                "used_before": parse_mem_size(m.group(1)),
                "committed": parse_mem_size(m.group(2)),
                "used_after": parse_mem_size(m.group(3)),
                "max": parse_mem_size(m.group(4)),
            }
            continue

        m = modern_cpu.search(msg)
        if m:
            gid = int(re.search(r'GC\((\d+)\)', msg).group(1)) if re.search(r'GC\((\d+)\)', msg) else 0
            cpu_info_by_gc[gid] = {
                "user_s": float(m.group(1)), "sys_s": float(m.group(2)), "real_s": float(m.group(3))
            }
            continue

        # 现代 GC 主行
        m = modern_gc.search(msg)
        if m:
            gc_id = int(m.group(1))
            pause_type = m.group(2)
            gc_type = "full" if "Full" in pause_type else "mixed" if "Mixed" in pause_type else "young"
            gc_name = "G1" if "G1" in msg else "ZGC" if "ZGC" in msg else \
                      "Shenandoah" if "Shenandoah" in msg else "Unknown"

            event = {
                "timestamp": log["timestamp"],
                "gc_id": gc_id,
                "gc_type": gc_type,
                "gc_name": gc_name,
                "pause_time_ms": float(m.group(6)),
                "heap_before": parse_mem_size(m.group(3)),
                "heap_after": parse_mem_size(m.group(4)),
                "heap_max": parse_mem_size(m.group(5)),
                "recovery_mb": (parse_mem_size(m.group(3)) - parse_mem_size(m.group(4))) / 1024 / 1024,
                "heap_info": heap_info_by_gc.get(gc_id, {}),
                "cpu": cpu_info_by_gc.get(gc_id, {"user_s": 0, "sys_s": 0, "real_s": 0}),
            }
            events.append(event)
            continue

        # 传统 Full GC 格式
        m = legacy_full.search(msg)
        if m:
            reason = m.group(1)
            heap_before = parse_mem_size(m.group(2))
            heap_after = parse_mem_size(m.group(3))
            heap_max = parse_mem_size(m.group(4))
            pause_s = float(m.group(5))

            # 尝试提取 metaspace
            meta = legacy_meta.search(msg)
            meta_info = {
                "used": parse_mem_size(meta.group(1)) if meta else 0,
                "capacity": parse_mem_size(meta.group(3)) if meta else 0,
            }

            gc_id_counter[0] += 1
            events.append({
                "timestamp": log["timestamp"], "gc_id": gc_id_counter[0],
                "gc_type": "full", "gc_name": "Parallel",
                "pause_time_ms": pause_s * 1000,
                "heap_before": heap_before, "heap_after": heap_after,
                "heap_max": heap_max,
                "recovery_mb": (heap_before - heap_after) / 1024 / 1024,
                "heap_info": {"metaspace": meta_info} if meta else {},
                "cpu": {"user_s": 0, "sys_s": 0, "real_s": pause_s},
            })
            continue

        # 传统 Young GC 格式
        m = legacy_young.search(msg)
        if m:
            heap_before = parse_mem_size(m.group(5))
            heap_after = parse_mem_size(m.group(6))
            heap_max = parse_mem_size(m.group(7))
            pause_ms = float(m.group(8))

            gc_id_counter[0] += 1
            events.append({
                "timestamp": log["timestamp"], "gc_id": gc_id_counter[0],
                "gc_type": "young", "gc_name": "Parallel",
                "pause_time_ms": pause_ms,
                "heap_before": heap_before, "heap_after": heap_after,
                "heap_max": heap_max,
                "recovery_mb": (heap_before - heap_after) / 1024 / 1024,
                "heap_info": {},
                "cpu": {"user_s": 0, "sys_s": 0, "real_s": pause_ms / 1000},
            })
            continue

    return events


def analyze_gc_events(events: list[GCEvent], total_logs: int) -> list[PatternEntry]:
    """对结构化的 GC 事件做定量分析，检测性能瓶颈和恶化趋势"""
    patterns: list[PatternEntry] = []
    if not events:
        return patterns

    total = len(events)
    full_gc = [e for e in events if e["gc_type"] == "full"]
    young_gc = [e for e in events if e["gc_type"] == "young"]
    pauses = [e["pause_time_ms"] for e in events if e.get("pause_time_ms") is not None]

    # ── 1. GC 频率 ──
    gc_ratio = total / max(total_logs, 1)
    if gc_ratio > 0.3:
        patterns.append({
            "type": "jvm", "subtype": "gc-high-frequency", "severity": "high",
            "description": f"GC 日志占比 {gc_ratio:.0%} — GC 开销过高，严重影响应用性能",
            "occurrences": total, "first_seen": events[0]["timestamp"],
            "last_seen": events[-1]["timestamp"],
            "affected_contexts": [], "level": "error", "jvm_category": "gc",
        })

    # ── 2. Full GC 分析 ──
    if full_gc:
        total_full = len(full_gc)
        full_pauses = [e["pause_time_ms"] for e in full_gc if e.get("pause_time_ms")]
        avg_full_pause = sum(full_pauses) / len(full_pauses) if full_pauses else 0
        max_full_pause = max(full_pauses) if full_pauses else 0
        patterns.append({
            "type": "jvm", "subtype": "full-gc", "severity": "high",
            "description": f"Full GC 触发 {total_full} 次 (平均暂停 {avg_full_pause:.0f}ms, 最长 {max_full_pause:.0f}ms) — 老年代空间严重不足",
            "occurrences": total_full, "first_seen": full_gc[0]["timestamp"],
            "last_seen": full_gc[-1]["timestamp"],
            "affected_contexts": [], "level": "error", "jvm_category": "gc",
        })

    # ── 3. 暂停时间分析 ──
    if pauses:
        max_pause = max(pauses)
        avg_pause = sum(pauses) / len(pauses)
        total_stw_ms = sum(pauses)
        # 暂停 > 1s
        long_pauses = [p for p in pauses if p > 1000]
        if long_pauses:
            patterns.append({
                "type": "jvm", "subtype": "gc-pause-high",
                "severity": "critical" if max_pause > 5000 else "high",
                "description": f"GC 暂停时间过长 (最长 {max_pause:.0f}ms, 平均 {avg_pause:.0f}ms, "
                              f"累计 STW {total_stw_ms / 1000:.1f}s) — 建议调优 GC 参数或增大堆内存",
                "occurrences": len(long_pauses),
                "first_seen": events[0]["timestamp"],
                "last_seen": events[-1]["timestamp"],
                "affected_contexts": [], "level": "error", "jvm_category": "gc",
            })

        if avg_pause > 100:
            patterns.append({
                "type": "jvm", "subtype": "gc-pause-long",
                "severity": "high" if avg_pause > 500 else "medium",
                "description": f"GC 平均暂停 {avg_pause:.0f}ms — 偏高，关注对响应延迟的影响",
                "occurrences": len(pauses),
                "first_seen": events[0]["timestamp"],
                "last_seen": events[-1]["timestamp"],
                "affected_contexts": [], "level": "warn", "jvm_category": "gc",
            })

    # ── 4. 堆占用分析 ──
    if events:
        last = events[-1]
        heap_max = last["heap_max"]
        if heap_max > 0:
            last_occ = last["heap_after"] / heap_max
            if last_occ > 0.9:
                patterns.append({
                    "type": "jvm", "subtype": "heap-pressure",
                    "severity": "critical" if last_occ > 0.95 else "high",
                    "description": f"堆占用率 {last_occ:.0%} ({last['heap_after']/1024/1024:.0f}M/{heap_max/1024/1024:.0f}M) "
                                  f"— 堆内存即将耗尽，可能触发 OOM",
                    "occurrences": 1, "first_seen": last["timestamp"],
                    "last_seen": last["timestamp"],
                    "affected_contexts": [], "level": "error", "jvm_category": "gc",
                })
            elif last_occ > 0.7:
                patterns.append({
                    "type": "jvm", "subtype": "heap-pressure",
                    "severity": "medium",
                    "description": f"堆占用率 {last_occ:.0%} ({last['heap_after']/1024/1024:.0f}M/{heap_max/1024/1024:.0f}M) "
                                  f"— 偏高，建议监控趋势",
                    "occurrences": 1, "first_seen": last["timestamp"],
                    "last_seen": last["timestamp"],
                    "affected_contexts": [], "level": "warn", "jvm_category": "gc",
                })

    # ── 5. 回收效率趋势 ──
    if len(events) >= 3:
        efficiencies = []
        for e in events:
            if e["heap_before"] > 0:
                recovered = e["heap_before"] - e["heap_after"]
                eff = recovered / max(e["heap_before"], 1)
                efficiencies.append((e["gc_id"], eff))

        if len(efficiencies) >= 3:
            first_avg = sum(e for _, e in efficiencies[:len(efficiencies)//2]) / (len(efficiencies)//2)
            last_avg = sum(e for _, e in efficiencies[len(efficiencies)//2:]) / (len(efficiencies) - len(efficiencies)//2)
            if last_avg < first_avg * 0.5 and last_avg < 0.1:
                patterns.append({
                    "type": "jvm", "subtype": "gc-efficiency-decline",
                    "severity": "critical",
                    "description": f"GC 回收效率持续下降 (从 {first_avg:.0%} 降至 {last_avg:.0%}) — 堆碎片化或内存泄漏前兆",
                    "occurrences": len(efficiencies),
                    "first_seen": events[0]["timestamp"],
                    "last_seen": events[-1]["timestamp"],
                    "affected_contexts": [], "level": "error", "jvm_category": "gc",
                })
            elif last_avg < first_avg * 0.5:
                patterns.append({
                    "type": "jvm", "subtype": "gc-efficiency-decline",
                    "severity": "high",
                    "description": f"GC 回收效率下降 (从 {first_avg:.0%} 降至 {last_avg:.0%}) — 需关注",
                    "occurrences": len(efficiencies),
                    "first_seen": events[0]["timestamp"],
                    "last_seen": events[-1]["timestamp"],
                    "affected_contexts": [], "level": "warn", "jvm_category": "gc",
                })

    # ── 6. 元空间压力 ──
    meta_usages = []
    for e in events:
        hi = e.get("heap_info", {})
        meta = hi.get("metaspace", {})
        if meta.get("max") and meta.get("used_before"):
            ratio = meta["used_before"] / meta["max"]
            meta_usages.append((e["timestamp"], ratio))
    if meta_usages:
        last_meta_ratio = meta_usages[-1][1]
        if last_meta_ratio > 0.9:
            patterns.append({
                "type": "jvm", "subtype": "metaspace-pressure",
                "severity": "high",
                "description": f"Metaspace 占用率 {last_meta_ratio:.0%} — 接近上限，检查类加载器泄漏",
                "occurrences": len(meta_usages),
                "first_seen": meta_usages[0][0],
                "last_seen": meta_usages[-1][0],
                "affected_contexts": [], "level": "error", "jvm_category": "gc",
            })

    # ── 7. OOM 前兆预警: 连续 Full GC + 回收量越来越小 ──
    if len(full_gc) >= 2:
        last_two = full_gc[-2:]
        r1 = (last_two[0]["heap_before"] - last_two[0]["heap_after"]) / max(last_two[0]["heap_before"], 1)
        r2 = (last_two[1]["heap_before"] - last_two[1]["heap_after"]) / max(last_two[1]["heap_before"], 1)
        if r2 < r1 and r2 < 0.1:
            patterns.append({
                "type": "jvm", "subtype": "oom-impending",
                "severity": "critical",
                "description": f"连续 Full GC 且回收量持续减少 (从 {r1:.0%} 降至 {r2:.0%}) — OOM 即将发生！",
                "occurrences": 2,
                "first_seen": last_two[0]["timestamp"],
                "last_seen": last_two[1]["timestamp"],
                "affected_contexts": [], "level": "error", "jvm_category": "oom",
            })

    return patterns


def detect_jvm_issues(logs: list[LogEntry]) -> list[PatternEntry]:
    """从日志中检测 JVM/GC 相关问题模式"""
    patterns: list[PatternEntry] = []
    hits: dict[str, list[LogEntry]] = {k: [] for k in JVM_PATTERNS}

    for log in logs:
        msg = log["message"]
        msg_lower = msg.lower()

        # 依次匹配每个 JVM 模式
        for pid, spec in JVM_PATTERNS.items():
            if re.search(spec["regex"], msg, re.IGNORECASE):
                hits[pid].append(log)

    for pid, matched in hits.items():
        if not matched:
            continue
        spec = JVM_PATTERNS[pid]
        cnt = len(matched)
        first_ts = matched[0]["timestamp"]
        last_ts = matched[-1]["timestamp"]
        contexts = list({log.get("context", "") for log in matched if log.get("context")})

        # 动态严重度：次数越多越严重
        severity = spec["severity"]
        if severity == "medium" and cnt >= 5:
            severity = "high"
        elif severity == "high" and cnt >= 5:
            severity = "critical"

        patterns.append({
            "type": "jvm",
            "subtype": pid,
            "severity": severity,
            "description": spec["desc"],
            "occurrences": cnt,
            "first_seen": first_ts,
            "last_seen": last_ts,
            "affected_contexts": contexts,
            "level": "error" if severity in ("critical", "high") else "warn",
            "jvm_category": "gc" if pid.startswith("gc") or pid.startswith("full") else
                           "oom" if pid.startswith("oom") else
                           "thread" if pid.startswith("thread") else "other",
        })

    # GC 事件解析 + 定量分析（替换旧的文本匹配，文本 GC 模式不再需要）
    gc_events = parse_gc_events(logs)
    gc_patterns = analyze_gc_events(gc_events, len(logs))

    # 去重: GC 解析器的结果更精确，覆盖同 subtype 的文本匹配结果
    gc_subtypes = {p["subtype"] for p in gc_patterns}
    patterns = [p for p in patterns if p["subtype"] not in gc_subtypes]
    patterns.extend(gc_patterns)

    return patterns


def build_jvm_recommendations(jvm_patterns: list[PatternEntry]) -> list[str]:
    """根据 JVM pattern 生成结构化优化建议"""
    recs = []

    # 按 jvm_category 分组
    oom_patterns = [p for p in jvm_patterns if p.get("jvm_category") == "oom"]
    gc_patterns = [p for p in jvm_patterns if p.get("jvm_category") == "gc"]
    thread_patterns = [p for p in jvm_patterns if p.get("jvm_category") == "thread"]

    has_critical = any(p["severity"] == "critical" for p in jvm_patterns)
    has_high = any(p["severity"] in ("high", "critical") for p in jvm_patterns)

    if not jvm_patterns:
        return recs

    # OOM 优化建议
    oom_types = {p["subtype"] for p in oom_patterns}
    if "oom-heap" in oom_types:
        recs.append("🔴 JVM 堆溢出 — 增大 -Xmx 或使用 jmap dump 分析堆转储定位泄漏")
    if "oom-gc-overhead" in oom_types:
        recs.append("🔴 GC 开销超限 — 增大堆内存 (-Xmx) 或调优 GC 策略 (G1GC/ZGC)")
    if "oom-metaspace" in oom_types:
        recs.append("🔴 元空间溢出 — 增大 -XX:MaxMetaspaceSize，检查类加载器泄漏")
    if "oom-native-thread" in oom_types:
        recs.append("🔴 线程数超限 — 检查线程泄漏，增大 ulimit -u，或减小线程池大小")
    if "oom-direct-memory" in oom_types:
        recs.append("🔴 直接内存溢出 — 增大 -XX:MaxDirectMemorySize，检查 NIO buffer 释放")
    if "stackoverflow" in {p["subtype"] for p in jvm_patterns}:
        recs.append("🟠 栈溢出 — 增大 -Xss 或检查递归调用是否无限循环")
    if "oom-other" in oom_types:
        recs.append("🔴 未分类 OOM — 立即启用 -XX:+HeapDumpOnOutOfMemoryError 获取堆转储")

    # GC 优化建议
    gc_subtypes = {p["subtype"] for p in gc_patterns}
    if "full-gc" in gc_subtypes:
        total_full_gc = sum(p["occurrences"] for p in gc_patterns if p["subtype"] == "full-gc")
        recs.append(f"🟠 Full GC 触发 {total_full_gc} 次 — 老年代空间不足，增大 -Xmx 或调整 -XX:NewRatio")
    if "gc-pause-high" in gc_subtypes or "gc-pause-long" in gc_subtypes:
        recs.append("🟠 GC 暂停过长 — 考虑 G1GC: -XX:+UseG1GC -XX:MaxGCPauseMillis=200，或迁移 ZGC")
    if "gc-high-frequency" in gc_subtypes:
        recs.append("🟠 GC 频率过高 — 增大新生代 (-Xmn) 或调整 -XX:SurvivorRatio")
    if "gc-promotion-failed" in gc_subtypes:
        recs.append("🟠 GC 提升失败 — 增大老年代空间或调整 -XX:TenuringThreshold")
    if "gc-concurrent-mode" in gc_subtypes:
        recs.append("🟠 CMS 并发模式失败 — 增大老年代空间或切换 G1GC/ZGC")
    if "gc-frequent" in gc_subtypes:
        recs.append("🟡 年轻代 GC 频繁 — 分析对象分配率，增大新生代 (-Xmn)")

    # 线程优化建议
    if "thread-deadlock" in thread_patterns:
        recs.append("🔴 线程死锁 — 用 jstack 获取线程转储，分析锁顺序并修复")
    if "thread-pool-exhausted" in thread_patterns:
        recs.append("🟠 线程池耗尽 — 增大线程池 maxPoolSize 或减小任务处理时间")

    # 其他
    if "codecache-full" in {p["subtype"] for p in jvm_patterns}:
        recs.append("🟡 CodeCache 满 — 增大 -XX:ReservedCodeCacheSize (默认 240M)")
    if "metaspace-growth" in {p["subtype"] for p in jvm_patterns}:
        recs.append("🟡 Metaspace 持续增长 — 检查动态类加载，添加 -XX:MaxMetaspaceSize 限制")

    # 兜底诊断建议
    if has_critical and not any(r.startswith("🔴") for r in recs):
        recs.append("🔴 发现严重 JVM 模式 — 建议启用 JVM 诊断参数: -XX:+PrintGCDetails -XX:+HeapDumpOnOutOfMemoryError")
    if has_high and gc_patterns and not any("G1GC" in r or "ZGC" in r for r in recs):
        recs.append("💡 GC 调优一般原则: -Xmx 设为堆峰值 1.5-2x，监控 GC 日志，逐步调优")

    return recs


# ─── 分析引擎 ───────────────────────────────────────────────

def handle_analyze(logs: list[LogEntry]) -> dict:
    """分析日志：检测 pattern、计算健康分、生成建议"""
    patterns: list[PatternEntry] = []
    error_map: dict[str, dict] = {}

    # 1. 错误聚合 — 相同消息累计
    for log in logs:
        if log["level"] not in ("error", "warn", "fatal", "critical"):
            continue
        key = log["message"][:100]
        if key in error_map:
            error_map[key]["count"] += 1
            error_map[key]["last"] = log["timestamp"]
            if log.get("context"):
                error_map[key]["files"].add(log["context"])
        else:
            error_map[key] = {
                "count": 1, "first": log["timestamp"], "last": log["timestamp"],
                "files": {log["context"]} if log.get("context") else set(),
                "message": log["message"],
            }

    # 2. 转换为 pattern
    for data in error_map.values():
        cnt = data["count"]
        severity = "critical" if cnt >= 10 else ("high" if cnt >= 5 else ("medium" if cnt >= 2 else "low"))
        patterns.append({
            "type": "regression" if cnt >= 3 else "error",
            "severity": severity,
            "description": data["message"][:200],
            "occurrences": cnt,
            "first_seen": data["first"],
            "last_seen": data["last"],
            "affected_contexts": sorted(data["files"]),
            "level": "error" if severity != "low" else "warn",
        })

    # 3. 慢操作检测
    slow_ops = [l for l in logs if l["level"] in ("error", "warn", "info")
                and re.search(r'(\d{4,})ms|slow|timeout|耗时|latency|too long|exceeded',
                              l["message"], re.IGNORECASE)]
    if len(slow_ops) >= 2:
        patterns.append({
            "type": "inefficiency",
            "severity": "high" if len(slow_ops) >= 5 else "medium",
            "description": f"检测到 {len(slow_ops)} 个慢操作/超时",
            "occurrences": len(slow_ops),
            "first_seen": slow_ops[0]["timestamp"],
            "last_seen": slow_ops[-1]["timestamp"],
            "affected_contexts": list({l.get("context", "") for l in slow_ops if l.get("context")}),
            "level": "warn",
        })

    # 4. 级联错误检测 — 不同 context 短时间内集中报错
    if len(logs) >= 20:
        err_by_time = [(l["timestamp"], l.get("context", ""))
                       for l in logs if l["level"] == "error"]
        # 按时间窗口分组 (30 秒内)
        cascade_groups = []
        current_group = []
        for ts_raw, ctx in err_by_time:
            if not current_group:
                current_group.append((ts_raw, ctx))
                continue
            try:
                t_curr = parse_timestamp(ts_raw)
                t_prev = parse_timestamp(current_group[-1][0])
                if t_curr and t_prev and (t_curr - t_prev).total_seconds() < 30:
                    current_group.append((ts_raw, ctx))
                else:
                    if len(current_group) >= 3 and len(set(c for _, c in current_group if c)) >= 2:
                        cascade_groups.append(current_group)
                    current_group = [(ts_raw, ctx)]
            except Exception:
                current_group.append((ts_raw, ctx))
        if len(current_group) >= 3 and len(set(c for _, c in current_group if c)) >= 2:
            cascade_groups.append(current_group)

        for cg in cascade_groups[:3]:
            contexts = list(set(c for _, c in cg if c))
            patterns.append({
                "type": "error",
                "severity": "high" if len(cg) >= 5 else "medium",
                "description": f"级联错误: {len(cg)} 个错误在短时间内出现，涉及 {len(contexts)} 个模块",
                "occurrences": len(cg),
                "first_seen": cg[0][0],
                "last_seen": cg[-1][0],
                "affected_contexts": contexts,
                "level": "error",
            })

    # 5. 连接/网络错误检测 (通用)
    conn_errors = [p for p in patterns if p.get("level") == "error" and
                   re.search(r'connection|refused|timeout|reset|closed|unreachable',
                             p["description"], re.IGNORECASE)]
    if conn_errors:
        total_conn = sum(p["occurrences"] for p in conn_errors)
        patterns.append({
            "type": "error",
            "severity": "high" if total_conn >= 3 else "medium",
            "description": f"网络/连接相关错误 {total_conn} 次",
            "occurrences": total_conn,
            "first_seen": conn_errors[0]["first_seen"],
            "last_seen": conn_errors[-1]["last_seen"],
            "affected_contexts": list(set(c for p in conn_errors for c in p.get("affected_contexts", []))),
            "level": "error",
        })

    # 6. JVM/GC 诊断分析
    jvm_patterns = detect_jvm_issues(logs)
    patterns.extend(jvm_patterns)

    # 7. 健康分计算
    total = len(logs)
    err_cnt = sum(1 for l in logs if l["level"] in ("error", "fatal", "critical"))
    warn_cnt = sum(1 for l in logs if l["level"] == "warn")
    err_weight = err_cnt / max(total, 1) * 100
    warn_weight = warn_cnt / max(total, 1) * 30
    health = max(0, min(100, round(100 - err_weight - warn_weight)))

    # 8. 建议生成
    recs = []
    if sum(1 for p in patterns if p["severity"] == "critical") > 0:
        recs.append("发现严重模式 — 立即修复后再开发新功能")
    if sum(1 for p in patterns if p["type"] == "regression") >= 2:
        recs.append("发现多个回归 — 建议添加回归测试并使用 harden 策略")
    if health < 50:
        recs.append("健康分过低 — 建议先稳定再添加功能")
    if any(p["type"] == "inefficiency" for p in patterns):
        recs.append("检测到性能瓶颈 — 分析慢操作路径，添加缓存或优化")
    if conn_errors:
        recs.append("网络连接异常 — 检查服务状态和网络配置")

    # JVM 相关建议
    jvm_recs = build_jvm_recommendations(jvm_patterns)
    recs.extend(jvm_recs)

    # 热点模块
    hot: dict[str, int] = defaultdict(int)
    for p in patterns:
        for ctx in p.get("affected_contexts", []):
            hot[ctx] += p["occurrences"]
    top = sorted(hot.items(), key=lambda x: -x[1])[:3]
    if top:
        recs.append(f"热点模块: {', '.join(f'{c}({n})' for c, n in top)}")

    # 去重
    seen = set()
    unique_recs = [r for r in recs if not (r in seen or seen.add(r))]

    patterns.sort(key=lambda p: (-p["occurrences"], p["severity"]))
    return {
        "patterns": patterns[:50],
        "health_score": health,
        "recommendations": unique_recs,
        "summary": {
            "total_logs": total,
            "error_count": err_cnt,
            "warn_count": warn_cnt,
            "unique_patterns": len(patterns),
            "critical_count": sum(1 for p in patterns if p["severity"] == "critical"),
        },
    }


def parse_timestamp(ts_str: str) -> datetime | None:
    """尝试解析各种时间戳格式"""
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S,%f",
        "%Y-%m-%d %H:%M:%S",
        "%b %d %H:%M:%S",
    ]
    # 去掉时区后缀 (Z, +08:00 等)
    clean = re.sub(r'[Z+\-].*$', '', ts_str).strip()
    for fmt in formats:
        try:
            return datetime.strptime(clean[:len(fmt.replace("%f", "000000").replace("%S", "00"))], fmt)
        except ValueError:
            continue
    return None


def handle_evolve(logs: list[LogEntry], strategy: str = "auto",
                  target_file: str = None) -> dict:
    analysis = handle_analyze(logs)
    effective = strategy
    if strategy == "auto":
        h = analysis["health_score"]
        effective = "repair-only" if h < 40 else ("harden" if h < 70 else "balanced")
    evo_id = f"evo_{int(time.time()*1000):x}_{os.urandom(3).hex()}"
    recs = []
    for p in analysis["patterns"]:
        if target_file and p.get("affected_contexts") and target_file not in p["affected_contexts"]:
            continue
        if p["severity"] == "critical" or effective == "repair-only":
            recs.append({
                "priority": "immediate", "category": "error-handling",
                "description": f"修复: {p['description']}",
                "affected_contexts": p.get("affected_contexts", []),
                "suggested_approach": "添加回归测试后修复根因" if p["type"] == "regression" else "添加错误处理或输入验证",
            })
        if p["type"] == "inefficiency" and effective != "repair-only":
            recs.append({
                "priority": "medium", "category": "performance",
                "description": f"优化: {p['description']}",
                "affected_contexts": p.get("affected_contexts", []),
                "suggested_approach": "分析慢路径，添加缓存或批量操作",
            })
    if effective == "innovate" and analysis["health_score"] > 70:
        recs.append({
            "priority": "low", "category": "architecture",
            "description": "系统稳定 — 考虑添加新能力",
            "affected_contexts": [],
            "suggested_approach": "识别最常调用的代码路径并优化或扩展",
        })
    if effective == "harden":
        hot = list(set(c for p in analysis["patterns"] for c in p.get("affected_contexts", [])))[:5]
        recs.append({
            "priority": "high", "category": "monitoring",
            "description": "添加结构化日志和健康检查",
            "affected_contexts": hot,
            "suggested_approach": "添加错误率指标、延迟追踪和自动告警阈值",
        })
    crit = [p for p in analysis["patterns"] if p["severity"] == "critical"]
    cs = analysis["health_score"]
    return {
        "evolution_id": evo_id,
        "strategy": effective,
        "recommendations": recs[:20],
        "risk_assessment": {
            "level": "high" if len(crit) >= 3 else ("medium" if crit else "low"),
            "factors": [p["description"][:100] for p in crit][:5],
        },
        "estimated_improvement": f"Health score: {cs} → ~{min(100, cs + len(recs)*5)} (应用所有建议后)",
        "current_health": cs,
    }


def handle_status() -> dict:
    return {
        "skill": "capability-evolver",
        "version": VERSION,
        "engine": "deterministic-pattern-analysis",
        "supported_actions": VALID_ACTIONS,
        "supported_strategies": VALID_STRATEGIES,
        "supported_sources": VALID_SOURCES,
        "capabilities": [
            "重复错误检测 — 同一错误多次出现自动聚合",
            "回归信号检测 — 高频错误标记为回归",
            "慢操作检测 — 超时/延迟操作识别",
            "级联错误分析 — 短时窗口内跨模块错误链",
            "网络连接异常检测 — 连接/超时/重置错误聚合",
            "JVM 诊断 — OOM/GC/线程死锁/栈溢出等 20+ 种问题识别",
            "GC 耗时分析 — 提取暂停时间，量化 GC 对性能的影响",
            "GC 频率分析 — 识别 GC 开销过高导致的性能瓶颈",
            "热点模块定位 — 按错误频率排序问题模块",
            "系统健康评分 — 0-100 量化健康状态",
            "演化策略 — 按健康分自动推荐改进方案",
            "JVM 优化建议 — 结构化参数调优建议 (-Xmx, G1GC, ZGC...)"
        ],
        "limits": {
            "max_logs_per_request": 10000,
            "max_patterns_returned": 50,
            "max_recommendations": 20,
        },
    }


# ─── CLI ────────────────────────────────────────────────────

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action not in VALID_ACTIONS:
        print(f"❌ 无效 action: {action}. 可选: {', '.join(VALID_ACTIONS)}")
        sys.exit(1)

    # 默认值
    lines, strategy, target_file, since = 500, "auto", None, None
    source = "auto"
    container = None
    file_path = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--lines" and i + 1 < len(args):
            lines = int(args[i + 1]); i += 2
        elif args[i] == "--strategy" and i + 1 < len(args):
            strategy = args[i + 1]; i += 2
        elif args[i] == "--target" and i + 1 < len(args):
            target_file = args[i + 1]; i += 2
        elif args[i] == "--since" and i + 1 < len(args):
            since = args[i + 1]; i += 2
        elif args[i] == "--source" and i + 1 < len(args):
            source = args[i + 1]; i += 2
        elif args[i] == "--container" and i + 1 < len(args):
            container = args[i + 1]; i += 2
        elif args[i] == "--path" and i + 1 < len(args):
            file_path = args[i + 1]; i += 2
        else:
            i += 1

    if action == "status":
        result = handle_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 获取日志
    logs = fetch_logs(source=source, container=container,
                      file_path=file_path, lines=lines, since=since)
    if not logs:
        print("⚠️  未获取到日志。可尝试指定日志来源:", file=sys.stderr)
        print("   --source docker --container <容器名>", file=sys.stderr)
        print("   --source file --path /var/log/app.log", file=sys.stderr)
        print("   --source stdin (管道输入)", file=sys.stderr)
        print("   export CAPABILITY_EVOLVER_CONTAINER=myapp (默认 Docker 容器)", file=sys.stderr)
        sys.exit(1)

    if action == "analyze":
        result = handle_analyze(logs)
    elif action == "evolve":
        result = handle_evolve(logs, strategy=strategy, target_file=target_file)

    result["_meta"] = {
        "action": action,
        "strategy": strategy,
        "source": source,
        "container": container,
        "file_path": file_path,
        "logs_analyzed": len(logs),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
