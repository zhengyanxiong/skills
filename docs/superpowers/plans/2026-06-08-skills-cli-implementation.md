# Skills CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build a Python CLI that installs repository skills into agent global directories via symlinks and tracks/syncs GitHub subdirectory sources.

**Architecture:** Add a focused `skills.py` entrypoint backed by pure-Python helper functions for skill discovery, manifest handling, agent link state, source cache management, and command rendering. Tests use `unittest` with temporary directories and temporary Git repositories so real agent config directories are not touched.

**Tech Stack:** Python 3.12 standard library, `argparse`, `json`, `pathlib`, `subprocess`, `unittest`.

---

### Task 1: Local Skill Discovery and Link Status

**Files:**
- Create: `skills.py`
- Create: `tests/test_skills_cli.py`

- [x] **Step 1: Write failing tests for skill discovery and link status**

Create tests that build temporary skill directories, symlinks, conflicts, and broken links. Assert discovery ignores non-skill directories and link status returns `linked`, `missing`, `conflict`, and `broken`.

- [x] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests.test_skills_cli -v`
Expected: FAIL because `skills.py` does not exist.

- [x] **Step 3: Implement discovery and link status**

Add `discover_skills`, `link_status`, agent registry helpers, and basic command scaffolding.

- [x] **Step 4: Run tests and verify pass**

Run: `python3 -m unittest tests.test_skills_cli -v`
Expected: PASS for discovery and link status tests.

### Task 2: Install, Uninstall, and Status Commands

**Files:**
- Modify: `skills.py`
- Modify: `tests/test_skills_cli.py`

- [x] **Step 1: Write failing CLI tests**

Add tests for `install`, `uninstall`, and `status` using a temporary agent registry override. Verify install creates symlinks, refuses conflicts, uninstall removes expected links only, and status prints useful state.

- [x] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests.test_skills_cli -v`
Expected: FAIL because commands are not implemented.

- [x] **Step 3: Implement commands**

Add argparse subcommands for `list`, `status`, `install`, and `uninstall`.

- [x] **Step 4: Run tests and verify pass**

Run: `python3 -m unittest tests.test_skills_cli -v`
Expected: PASS.

### Task 3: Manifest and Source Commands

**Files:**
- Modify: `skills.py`
- Modify: `tests/test_skills_cli.py`

- [x] **Step 1: Write failing manifest tests**

Add tests for empty manifest loading, source add/remove/list, and JSON persistence under `skills.manifest.json`.

- [x] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests.test_skills_cli -v`
Expected: FAIL because manifest commands are not implemented.

- [x] **Step 3: Implement manifest functions and `sources` subcommands**

Add load/save helpers and `sources list/add/remove`.

- [x] **Step 4: Run tests and verify pass**

Run: `python3 -m unittest tests.test_skills_cli -v`
Expected: PASS.

### Task 4: Outdated and Sync with Git Subdirectory Sources

**Files:**
- Modify: `skills.py`
- Modify: `tests/test_skills_cli.py`

- [x] **Step 1: Write failing Git integration tests**

Create temporary upstream Git repos containing skills in subdirectories. Verify `latest_path_commit` tracks only commits touching the configured path, `outdated` reports `current` and `update-available`, and `sync` copies the source path into the local skill directory.

- [x] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests.test_skills_cli -v`
Expected: FAIL because source cache, outdated, and sync behavior are not implemented.

- [x] **Step 3: Implement Git source handling**

Add source cache clone/fetch, path commit detection, dirty local checks, `outdated`, and `sync`.

- [x] **Step 4: Run tests and verify pass**

Run: `python3 -m unittest tests.test_skills_cli -v`
Expected: PASS.

### Task 5: Doctor and Final Verification

**Files:**
- Modify: `skills.py`
- Modify: `tests/test_skills_cli.py`

- [x] **Step 1: Write failing doctor tests**

Add tests for missing `SKILL.md`, frontmatter name mismatch, manifest pointing to missing local skill, and valid local skill.

- [x] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests.test_skills_cli -v`
Expected: FAIL because `doctor` is not implemented.

- [x] **Step 3: Implement doctor checks**

Add local structural checks and manifest consistency checks.

- [x] **Step 4: Run full verification**

Run: `python3 -m unittest discover -s tests -v`
Expected: all tests PASS.

- [x] **Step 5: Smoke test CLI help**

Run: `python3 skills.py --help`
Expected: command exits 0 and lists subcommands.
