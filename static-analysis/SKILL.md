---
name: static-analysis
description: Static analysis toolkit with CodeQL, Semgrep, and SARIF parsing for security vulnerability detection. Use when running or configuring static analysis tools, writing CodeQL queries, creating Semgrep rules, or parsing SARIF output files.
version: 1.2.2
author: Axel Mierczuk & Paweł Płatek
license: MIT
tags: [security, static-analysis, codeql, semgrep, sarif, vulnerability-detection]
---

# Static Analysis Toolkit

Three specialized sub-skills for static analysis and security vulnerability detection.

## Sub-Skills

| Sub-Skill | Description | When to Use |
|-----------|-------------|-------------|
| **codeql** | CodeQL query writing and database analysis | Writing CodeQL queries, analyzing CodeQL databases, configuring CodeQL scans |
| **semgrep** | Semgrep rule creation and scanning | Writing Semgrep rules, running Semgrep scans, configuring Semgrep |
| **sarif-parsing** | SARIF output parsing and analysis | Processing SARIF files from any static analysis tool, filtering results, generating reports |

## Quick Selection Guide

```
Need to find vulnerabilities in code?
  ├─ Using CodeQL? → Load codeql sub-skill
  ├─ Using Semgrep? → Load semgrep sub-skill
  └─ Have SARIF output? → Load sarif-parsing sub-skill
```

## Usage

Load the relevant sub-skill directory when working on a specific tool:

- For CodeQL work: `static-analysis/codeql/`
- For Semgrep work: `static-analysis/semgrep/`
- For SARIF parsing: `static-analysis/sarif-parsing/`

Each sub-skill has its own SKILL.md with detailed instructions, references, and workflows.
