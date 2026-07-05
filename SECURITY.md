# Security Policy

## Supported Versions

The latest release of `skills` is actively supported with security updates.

| Version | Supported          |
|---------|--------------------|
| main    | ✅ Active          |
| < main  | ❌ No longer supported |

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, **do not open a public issue**.

Use one of the following channels instead:

### 1. GitHub Security Advisories (preferred)

Report privately via [GitHub Security Advisories](https://github.com/zhengyanxiong/skills/security/advisories/new).

**Why prefer this method**:
- Your report is kept private until a fix is released
- The maintainer is notified immediately
- Coordinated disclosure timeline can be tracked in-thread

### 2. What to Include

Please include as much of the following as possible:

- A clear description of the vulnerability
- Steps to reproduce (proof-of-concept snippet or commands)
- Affected versions / commits
- Potential impact (RCE / data leak / privilege escalation / etc.)
- Suggested mitigation, if any

### 3. Response Timeline

- **Acknowledgement**: Within 72 hours
- **Initial triage**: Within 7 days
- **Coordinated disclosure**: Fix released within 90 days (or sooner if critical)

## Scope

This repository contains:
- `skills.py` — CLI for managing AI Agent Skills (this is the surface area needing security review)
- 60+ `SKILL.md` files — documentation content, reviewed for accuracy and license compliance
- Upstream-tracked skills — these are sourced from public repositories via source manifest; vulnerabilities in third-party skills should be reported to their respective upstream maintainers

When in doubt, if your report is about an upstream-tracked skill, please report to the upstream project first and link us in the discussion.

## Out of Scope

- Issues with downstream Agent tools (Claude Code, Codex, Hermes, etc.) — report to those projects directly
- Skill content suggestions / correctness feedback — open a regular issue instead

Thank you for helping keep this project and its users safe.
