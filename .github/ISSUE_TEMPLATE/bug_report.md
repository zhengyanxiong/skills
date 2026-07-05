---
name: Bug Report
about: Report something that doesn't work as expected
title: "[Bug]: "
labels: ["bug"]
assignees: []
---

## 🐛 Bug Description

A clear and concise description of what the bug is.

## 🔁 Steps to Reproduce

1. Command run / action taken
2. Expected behavior
3. Actual behavior

Example:
```bash
$ ./skills add owner/repo
[OK] Cloning https://...
[ERROR] Clone failed: ...
```

## 🖥️ Environment

- **OS**: (e.g., Ubuntu 22.04, macOS 14.4, Windows 11 + WSL2)
- **Python version**: `python3 --version` (output: _______)
- **CLI version**: `./skills --version` (if available)
- **Skills count**: `./skills list | wc -l` (output: _______)

## 📋 Expected Behavior

What you expected to happen.

## 📷 Actual Output

Full error output, traceback, or screenshot. Use code blocks:

```
[paste error here]
```

## 📎 Additional Context

- Have you tried reinstalling?
- Does the issue reproduce on a fresh checkout?
- Any related PRs or issues?

## ✅ Checklist

- [ ] I have searched existing issues to avoid duplicates
- [ ] I have run `./skills doctor` (and the output, if relevant, is below)
- [ ] I am using the latest `main` branch
