#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import re
import sys

# ── Path safety ────────────────────────────────────────────────────
# Guard against path traversal and invalid skill names.

# Characters disallowed in skill names (will be replaced with '-')
_SANITIZE_RE = re.compile(r'[^a-zA-Z0-9_.-]')


def sanitize_name(name: str) -> str:
    """Replace unsafe characters in a skill/agent name with '-'.

    Prevents path traversal via ``../``, control characters, and
    other special chars that could escape the intended directory.
    """
    return _SANITIZE_RE.sub('-', name)


def is_safe_path(target: Path, base: Path) -> bool:
    """Return True if *target* resolves to a path under *base*.

    This prevents symlink/copy operations from escaping the intended
    parent directory via ``../`` or absolute-path trickery.
    """
    try:
        resolved = target.resolve()
        base_resolved = base.resolve()
        return str(resolved).startswith(str(base_resolved) + "/")
    except (OSError, ValueError):
        return False


def is_safe_skill_dir(candidate: Path) -> bool:
    """Return True if *candidate* is a safe name under the repo root.

    Also verifies the candidate is a directory (not a symlink to
    somewhere outside the repo).
    """
    if not candidate.is_dir():
        return False
    if candidate.is_symlink():
        target = candidate.resolve()
        if not str(target).startswith(str(candidate.parent.resolve()) + "/"):
            return False
    return True


# ── Terminal colors (no-op on Windows) ────────────────────────────
try:
    _IS_TTY = sys.stderr.isatty()
except (OSError, AttributeError):
    _IS_TTY = False

if _IS_TTY:
    DIM = '\x1b[2m'
    BOLD = '\x1b[1m'
    RESET = '\x1b[0m'
    OK = '\x1b[1;32m'    # bold green
    WARN = '\x1b[1;33m'  # bold yellow
    ERR = '\x1b[1;31m'   # bold red
    INFO = '\x1b[1;36m'  # bold cyan
else:
    DIM = BOLD = RESET = OK = WARN = ERR = INFO = ''


AGENTS = {
    "codex": "~/.codex/skills",
    "claude-code": "~/.claude/skills",
    "opencode": "~/.config/opencode/skills",
    "kimi": "~/.kimi/skills",
    "hermes": "~/.hermes/skills",
    "minimax": "~/.minimax/skills",
}

MANIFEST = "skills.manifest.json"


@dataclass(frozen=True)
class Skill:
    name: str
    path: Path


@dataclass(frozen=True)
class LinkStatus:
    state: str
    target: Path | None = None
    message: str = ""


def repo_root(start: Path | None = None) -> Path:
    return (start or Path.cwd()).resolve()


def discover_skills(root: Path) -> list[Skill]:
    result: list[Skill] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if (child / "SKILL.md").is_file():
            result.append(Skill(child.name, child.resolve()))
    return result


def link_status(local_skill: Path, link_path: Path) -> LinkStatus:
    local_skill = local_skill.resolve()
    try:
        path_exists = link_path.exists()
    except PermissionError:
        path_exists = False
    try:
        is_link = link_path.is_symlink()
    except PermissionError:
        is_link = False
    if not path_exists and not is_link:
        return LinkStatus("missing")
    if is_link:
        try:
            raw_target = Path(os.readlink(link_path))
        except OSError:
            return LinkStatus("broken", link_path)
        target = raw_target if raw_target.is_absolute() else (link_path.parent / raw_target)
        try:
            target_exists = target.exists()
        except PermissionError:
            target_exists = False
        if not target_exists:
            return LinkStatus("broken", target)
        resolved = target.resolve()
        if resolved == local_skill:
            return LinkStatus("linked", resolved)
        return LinkStatus("conflict", resolved, "symlink points elsewhere")
    return LinkStatus("conflict", link_path.resolve(), "target is not a symlink")


def agent_dirs(overrides: dict[str, str] | None = None) -> dict[str, Path]:
    values = dict(AGENTS)
    if overrides:
        values.update(overrides)
    return {name: Path(os.path.expanduser(path)).resolve() for name, path in values.items()}


def parse_agent_overrides(values: list[str] | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values or []:
        if "=" not in value:
            raise SystemExit(f"error: invalid --agent-dir value {value!r}; expected name=path")
        name, path = value.split("=", 1)
        if not name or not path:
            raise SystemExit(f"error: invalid --agent-dir value {value!r}; expected name=path")
        result[name] = path
    return result


def select_agents(name: str | None, registry: dict[str, Path]) -> dict[str, Path]:
    if name in (None, "all"):
        return registry
    if name not in registry:
        raise SystemExit(f"error: unknown agent {name}")
    return {name: registry[name]}


def select_skills(name: str | None, root: Path) -> list[Skill]:
    skills = discover_skills(root)
    if name is None:
        return skills
    selected = [skill for skill in skills if skill.name == name]
    if not selected:
        raise SystemExit(f"error: unknown skill {name}")
    return selected


def print_status(root: Path, registry: dict[str, Path], agent: str | None, skill_name: str | None) -> int:
    selected_agents = select_agents(agent, registry)
    selected_skills = select_skills(skill_name, root)
    print("Skill\tAgent\tState\tTarget")
    for skill in selected_skills:
        for agent_name, agent_dir in selected_agents.items():
            path = agent_dir / skill.name
            status = link_status(skill.path, path)
            target = str(status.target) if status.target else "-"
            print(f"{skill.name}\t{agent_name}\t{status.state}\t{target}")
    return 0


def install(root: Path, registry: dict[str, Path], agent: str | None, skill_name: str | None) -> int:
    selected_agents = select_agents(agent, registry)
    selected_skills = select_skills(skill_name, root)
    failed = False
    for skill in selected_skills:
        for agent_name, agent_dir in selected_agents.items():
            agent_dir.mkdir(parents=True, exist_ok=True)
            link_path = agent_dir / skill.name
            status = link_status(skill.path, link_path)
            if status.state == "linked":
                print(f"{skill.name}\t{agent_name}\tlinked")
                continue
            if status.state != "missing":
                failed = True
                print(f"error: {agent_name}/{skill.name} is {status.state}; expected missing or linked")
                continue
            os.symlink(skill.path, link_path)
            print(f"{skill.name}\t{agent_name}\tinstalled")
    return 1 if failed else 0


def uninstall(root: Path, registry: dict[str, Path], agent: str | None, skill_name: str | None) -> int:
    selected_agents = select_agents(agent, registry)
    selected_skills = select_skills(skill_name, root)
    failed = False
    for skill in selected_skills:
        for agent_name, agent_dir in selected_agents.items():
            link_path = agent_dir / skill.name
            status = link_status(skill.path, link_path)
            if status.state == "missing":
                print(f"{skill.name}\t{agent_name}\tmissing")
                continue
            if status.state != "linked":
                failed = True
                print(f"error: {agent_name}/{skill.name} is {status.state}; refusing to remove")
                continue
            link_path.unlink()
            print(f"{skill.name}\t{agent_name}\tuninstalled")
    return 1 if failed else 0


def _grouped_install_report(
    title: str, subtitle: str, rows: list[tuple[str, str, LinkStatus]]
) -> None:
    """Print a human-readable installed / not-installed / problematic report.

    *rows* is a list of ``(item_name, location, LinkStatus)`` tuples —
    *item_name* is the skill name (agent view) or agent name (skill view),
    and *location* is the agent dir or skill path shown as a subtitle.
    """
    installed = [(n, loc, s) for n, loc, s in rows if s.state == "linked"]
    missing = [(n, loc, s) for n, loc, s in rows if s.state == "missing"]
    other = [(n, loc, s) for n, loc, s in rows if s.state not in ("linked", "missing")]

    print(f"{BOLD}{title}{RESET}  {DIM}{subtitle}{RESET}")
    print()

    print(f"{BOLD}Installed ({len(installed)}):{RESET}")
    if installed:
        for name, _loc, _s in sorted(installed):
            print(f"  {OK}✓{RESET} {name}")
    else:
        print(f"  {DIM}(none){RESET}")
    print()

    print(f"{BOLD}Not installed ({len(missing)}):{RESET}")
    if missing:
        for name, _loc, _s in sorted(missing):
            print(f"  {ERR}✗{RESET} {name}")
    else:
        print(f"  {DIM}(none){RESET}")

    if other:
        print()
        print(f"{BOLD}Problematic ({len(other)}):{RESET}")
        for name, _loc, s in sorted(other):
            detail = s.message or s.state
            print(f"  {WARN}!{RESET} {name}  {DIM}({s.state}: {detail}){RESET}")


def list_for_agent(root: Path, registry: dict[str, Path], agent: str) -> int:
    """Show which local skills are installed (or not) for a specific agent."""
    if agent not in registry:
        raise SystemExit(f"error: unknown agent {agent!r}; known: {', '.join(sorted(registry))}")
    agent_dir = registry[agent]
    rows: list[tuple[str, str, LinkStatus]] = []
    for skill in discover_skills(root):
        rows.append((skill.name, str(agent_dir), link_status(skill.path, agent_dir / skill.name)))
    _grouped_install_report(f"Agent: {agent}", str(agent_dir), rows)
    return 0


def list_for_skill(root: Path, registry: dict[str, Path], skill_name: str) -> int:
    """Show which agents have a specific skill installed (or not)."""
    skills = [s for s in discover_skills(root) if s.name == skill_name]
    if not skills:
        raise SystemExit(f"error: unknown skill {skill_name!r}")
    skill = skills[0]
    rows: list[tuple[str, str, LinkStatus]] = []
    for agent_name, agent_dir in registry.items():
        rows.append((agent_name, str(agent_dir), link_status(skill.path, agent_dir / skill.name)))
    _grouped_install_report(f"Skill: {skill_name}", str(skill.path), rows)
    return 0


def cmd_list(
    root: Path, registry: dict[str, Path], agent: str | None, skill_name: str | None
) -> int:
    """List local skills, or query install status by agent / by skill.

    - No flags: print local skill names (one per line).
    - ``--agent NAME``: show which skills are installed vs. not for that agent.
    - ``--skill NAME``: show which agents have that skill installed vs. not.
    """
    if agent is None and skill_name is None:
        for skill in discover_skills(root):
            print(skill.name)
        return 0
    if agent is not None:
        return list_for_agent(root, registry, agent)
    return list_for_skill(root, registry, skill_name)


def manifest_path(root: Path) -> Path:
    return root / MANIFEST


def load_manifest(root: Path) -> dict[str, Any]:
    path = manifest_path(root)
    if not path.exists():
        return {"skills": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if "skills" not in data or not isinstance(data["skills"], dict):
        raise SystemExit(f"error: invalid manifest {path}: missing object field 'skills'")
    return data


def save_manifest(root: Path, manifest: dict[str, Any]) -> None:
    path = manifest_path(root)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, check=True, text=True, capture_output=True)


def source_cache_dir(root: Path, repo: str) -> Path:
    digest = hashlib.sha1(repo.encode("utf-8")).hexdigest()[:16]
    return root / ".cache" / "sources" / digest


# Track last fetch time per cache dir to avoid redundant fetches
_fetch_timestamps: dict[str, float] = {}
_FETCH_INTERVAL = 300  # seconds (5 min)


def ensure_source_repo(root: Path, source: dict[str, Any]) -> Path:
    repo = source["repo"]
    cache = source_cache_dir(root, repo)
    if cache.exists():
        # Skip fetch if recently done
        cache_key = str(cache)
        now = time.time()
        if cache_key not in _fetch_timestamps or (now - _fetch_timestamps[cache_key]) > _FETCH_INTERVAL:
            run_git(cache, "fetch", "--all", "--prune")
            _fetch_timestamps[cache_key] = now
        return cache
    cache.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--filter=blob:none", "--no-checkout", repo, str(cache)],
        check=True,
        text=True,
        capture_output=True,
    )
    return cache


def latest_path_commit(repo_dir: Path, ref: str, source_path: str) -> str:
    result = run_git(repo_dir, "log", "-1", "--format=%H", ref, "--", source_path)
    commit = result.stdout.strip()
    if not commit:
        raise FileNotFoundError(source_path)
    return commit


def source_entry(manifest: dict[str, Any], skill_name: str) -> dict[str, Any] | None:
    entry = manifest.get("skills", {}).get(skill_name)
    if not entry:
        return None
    return entry.get("source")



def parse_github_shorthand(ref: str) -> dict[str, str] | None:
    """Parse ``owner/repo`` or ``owner/repo/path/to/skill`` into source config.

    Returns ``None`` if the string isn't a GitHub shorthand.
    """
    m = re.match(r'^([\w.-]+)/([\w.-]+)(/.*)?$', ref)
    if not m:
        return None
    owner, repo, subpath = m.group(1), m.group(2), (m.group(3) or '').strip('/')
    return {
        'type': 'git',
        'repo': f'https://github.com/{owner}/{repo}.git',
        'path': f'skills/{subpath}' if subpath else 'skills',
        'ref': 'main',
        'last_commit': '',
        'last_checked_at': '',
    }


def cmd_add(root: Path, source_ref: str, agents: list[str] | None) -> int:
    """Clone a remote skills source and install all matching skills.

    *source_ref* can be a GitHub shorthand (``owner/repo``,
    ``owner/repo/path``) or a full git URL.
    """
    # Parse the source reference
    source = parse_github_shorthand(source_ref)
    if source is None:
        # Treat as full git URL — assume skills are at root
        source = {
            'type': 'git',
            'repo': source_ref,
            'path': '.',
            'ref': 'main',
            'last_commit': '',
            'last_checked_at': '',
        }

    # Resolve root for this source
    add_root = root / '.cache' / 'staging'
    add_root.mkdir(parents=True, exist_ok=True)

    print(f'  {OK} Cloning {source["repo"]} ...', flush=True)
    try:
        repo_dir = ensure_source_repo(root, source)
        # Checkout the relevant path
        checkout_path = repo_dir / source['path']
        if not checkout_path.exists():
            run_git(repo_dir, 'checkout', source['ref'], '--', source['path'])
        if not checkout_path.exists():
            print(f'  {ERR} Path "{source["path"]}" not found in {source["repo"]}')
            return 1
    except subprocess.CalledProcessError as e:
        print(f'  {ERR} Clone failed: {e.stderr.strip()}')
        return 1

    # Discover skills in the checked-out path
    discovered = discover_skills(checkout_path)
    if not discovered:
        print(f'  {WARN} No skills (SKILL.md) found in {source["repo"]}/{source["path"]}')
        return 0

    # Load manifest for tracking
    manifest = load_manifest(root)

    # Install each skill: copy to repo root + symlink to agents
    installed = []
    registry = agent_dirs()
    # Filter agents if specified
    selected_registry: dict[str, Path] = {}
    for name, path in registry.items():
        if agents is None or name in agents:
            selected_registry[name] = path

    for skill in discovered:
        safe_name = sanitize_name(skill.name)
        dest = root / safe_name

        # Copy skill to local repo root (idempotent — skip if already exists with same content)
        if not dest.exists() or (dest / 'SKILL.md').stat().st_mtime < (skill.path / 'SKILL.md').stat().st_mtime:
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(skill.path, dest, symlinks=True)
            print(f'  {OK} Copied skill "{safe_name}"', flush=True)
        else:
            print(f'  {DIM}Skill "{safe_name}" already exists, skipping copy{RESET}')

        # Add/update manifest entry
        skill_entry = manifest['skills'].setdefault(safe_name, {})
        if 'description' not in skill_entry:
            skill_entry['description'] = ''
        skill_entry['source'] = source.copy()
        commit = 'unknown'
        try:
            commit = run_git(repo_dir, 'log', '-1', '--format=%H', '--', source['path']).stdout.strip()
        except subprocess.CalledProcessError:
            pass
        skill_entry['source']['last_commit'] = commit
        skill_entry['source']['last_checked_at'] = (
            datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
        )

        # Symlink to agents
        for agent_name, agent_dir in selected_registry.items():
            safe_agent_name = sanitize_name(agent_name)
            agent_dir.mkdir(parents=True, exist_ok=True)
            link_target = agent_dir / safe_name
            try:
                link_exists = link_target.exists()
            except PermissionError:
                link_exists = False
            try:
                is_link = link_target.is_symlink()
            except PermissionError:
                is_link = False
            if link_exists or is_link:
                try:
                    if is_link and link_target.resolve() == dest.resolve():
                        continue  # already points here
                except PermissionError:
                    pass
                link_target.unlink()
            try:
                os.symlink(dest, link_target)
                installed.append(f'{safe_name} → {safe_agent_name}')
            except OSError as e:
                print(f'  {ERR} Symlink failed: {e}')

    save_manifest(root, manifest)
    print('')
    if installed:
        print(f'  {OK} Installed {len(installed)} skill(s)')
        for item in installed:
            print(f'      {DIM}{item}{RESET}')
    else:
        print(f'  {INFO} Nothing new to install')
    return 0


def source_status(root: Path, skill_name: str) -> dict[str, str]:
    manifest = load_manifest(root)
    source = source_entry(manifest, skill_name)
    if not source or source.get("type") == "local":
        return {"skill": skill_name, "status": "local-only", "local": "", "upstream": ""}
    try:
        repo_dir = ensure_source_repo(root, source)
        upstream = latest_path_commit(repo_dir, source.get("ref", "main"), source["path"])
    except FileNotFoundError:
        return {"skill": skill_name, "status": "source-missing", "local": source.get("last_commit", ""), "upstream": ""}
    except (subprocess.CalledProcessError, OSError):
        return {"skill": skill_name, "status": "source-invalid", "local": source.get("last_commit", ""), "upstream": ""}
    local = source.get("last_commit", "")
    status = "current" if local == upstream else "update-available"
    return {"skill": skill_name, "status": status, "local": local, "upstream": upstream}


def outdated(root: Path, skill_name: str | None) -> int:
    manifest = load_manifest(root)
    names = [skill_name] if skill_name else sorted({skill.name for skill in discover_skills(root)} | set(manifest["skills"]))
    print("Skill\tLocal Commit\tUpstream Commit\tStatus")
    failed = False
    for name in names:
        status = source_status(root, name)
        if status["status"] in {"source-missing", "source-invalid"}:
            failed = True
        print(f"{name}\t{status['local'] or '-'}\t{status['upstream'] or '-'}\t{status['status']}")
    return 1 if failed else 0


def is_dirty_path(root: Path, path: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", str(path.relative_to(root))],
            cwd=root,
            check=True,
            text=True,
            capture_output=True,
        )
    except (ValueError, subprocess.CalledProcessError):
        return False
    return bool(result.stdout.strip())


def copy_source_path(repo_dir: Path, ref: str, source_path: str, destination: Path) -> None:
    source_dir = repo_dir / source_path
    if source_dir.exists():
        shutil.rmtree(source_dir)
    run_git(repo_dir, "checkout", ref, "--", source_path)
    if not (source_dir / "SKILL.md").is_file():
        raise FileNotFoundError(f"{source_path}/SKILL.md")
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source_dir, destination)


def sync_skill(root: Path, skill_name: str) -> int:
    manifest = load_manifest(root)
    source = source_entry(manifest, skill_name)
    if not source:
        print(f"error: {skill_name} has no source entry")
        return 1
    destination = root / skill_name
    if is_dirty_path(root, destination):
        print(f"error: {skill_name} is dirty-local; commit or stash changes before sync")
        return 1
    try:
        repo_dir = ensure_source_repo(root, source)
        upstream = latest_path_commit(repo_dir, source.get("ref", "main"), source["path"])
        copy_source_path(repo_dir, source.get("ref", "main"), source["path"], destination)
    except FileNotFoundError as exc:
        print(f"error: source-missing: {exc}")
        return 1
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"error: source-invalid: {exc}")
        return 1
    source["last_commit"] = upstream
    source["last_checked_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    save_manifest(root, manifest)
    print(f"{skill_name}\tsynced\t{upstream}")
    return 0


def read_frontmatter_name(skill_md: Path) -> str | None:
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            return None
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def doctor(root: Path) -> int:
    failed = False
    local_names = {skill.name for skill in discover_skills(root)}
    for skill in discover_skills(root):
        skill_md = skill.path / "SKILL.md"
        if skill_md.is_file():
            print(f"[ok] {skill.name} has SKILL.md")
        else:
            failed = True
            print(f"[error] {skill.name} missing SKILL.md")
            continue
        frontmatter_name = read_frontmatter_name(skill_md)
        if frontmatter_name == skill.name:
            print(f"[ok] {skill.name} frontmatter name matches")
        else:
            failed = True
            print(f"[error] {skill.name} frontmatter name is {frontmatter_name or '-'}")

    manifest = load_manifest(root)
    for name in sorted(manifest["skills"]):
        if name not in local_names:
            failed = True
            print(f"[error] manifest references missing local skill: {name}")
        else:
            print(f"[ok] manifest references local skill: {name}")
    return 1 if failed else 0


def sources_list(root: Path) -> int:
    manifest = load_manifest(root)
    print("Skill\tType\tRepo\tRef\tPath\tLast Commit\tDescription")
    for name in sorted(manifest["skills"]):
        entry = manifest["skills"][name]
        source = entry.get("source", {})
        print(
            f"{name}\t{source.get('type', '-')}\t{source.get('repo', '-')}\t{source.get('ref', '-')}"
            f"\t{source.get('path', '-')}\t{source.get('last_commit', '-')}\t{entry.get('description', '-')}"
        )
    return 0


def sources_add(root: Path, skill_name: str, repo: str, source_path: str, ref: str) -> int:
    select_skills(skill_name, root)
    manifest = load_manifest(root)
    entry = manifest["skills"].setdefault(skill_name, {})
    entry["source"] = {
        "type": "git",
        "repo": repo,
        "ref": ref,
        "path": source_path,
        "last_commit": "",
        "last_checked_at": "",
    }
    save_manifest(root, manifest)
    print(f"{skill_name}\tsource-added")
    return 0


def sources_remove(root: Path, skill_name: str) -> int:
    manifest = load_manifest(root)
    manifest["skills"].pop(skill_name, None)
    save_manifest(root, manifest)
    print(f"{skill_name}\tsource-removed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skills", description="Manage repository agent skills")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help=argparse.SUPPRESS)
    parser.add_argument("--agent-dir", action="append", default=[], help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list", help="List local skills and agent install status")
    list_group = list_parser.add_mutually_exclusive_group()
    list_group.add_argument(
        "--agent",
        default=None,
        help="Show which skills are installed vs. not for a specific agent",
    )
    list_group.add_argument(
        "--skill",
        default=None,
        help="Show which agents have a specific skill installed vs. not",
    )
    add_parser = sub.add_parser("add", help="Install skills from a remote source")
    add_parser.add_argument("source", help="GitHub shorthand (owner/repo[/path]) or git URL")
    add_parser.add_argument("--agent", action="append", default=[], help="Only install for specific agent(s)")
    status_parser = sub.add_parser("status", help="Show local install status")
    status_parser.add_argument("--agent", default=None)
    status_parser.add_argument("--skill", default=None)
    install_parser = sub.add_parser("install", help="Install skills as symlinks")
    install_parser.add_argument("--agent", default="all")
    install_parser.add_argument("--skill", default=None)
    uninstall_parser = sub.add_parser("uninstall", help="Remove skill symlinks")
    uninstall_parser.add_argument("--agent", default="all")
    uninstall_parser.add_argument("--skill", default=None)
    sub.add_parser("doctor", help="Validate local skills and manifest")
    outdated_parser = sub.add_parser("outdated", help="Check upstream source updates")
    outdated_parser.add_argument("skill", nargs="?")
    sync_parser = sub.add_parser("sync", help="Sync upstream source updates")
    sync_parser.add_argument("skill", nargs="?")
    sync_parser.add_argument("--all", action="store_true")
    sources = sub.add_parser("sources", help="Manage source manifest")
    sources_sub = sources.add_subparsers(dest="sources_command", required=True)
    sources_sub.add_parser("list", help="List source entries")
    sources_add_parser = sources_sub.add_parser("add", help="Add or update source entry")
    sources_add_parser.add_argument("skill")
    sources_add_parser.add_argument("--repo", required=True)
    sources_add_parser.add_argument("--path", required=True)
    sources_add_parser.add_argument("--ref", default="main")
    sources_remove_parser = sources_sub.add_parser("remove", help="Remove source entry")
    sources_remove_parser.add_argument("skill")

    args = parser.parse_args(argv)
    root = repo_root(args.root)
    registry = agent_dirs(parse_agent_overrides(args.agent_dir))
    if args.command == "list":
        return cmd_list(root, registry, args.agent, args.skill)
    if args.command == "add":
        return cmd_add(root, args.source, args.agent or None)
    if args.command == "status":
        return print_status(root, registry, args.agent, args.skill)
    if args.command == "install":
        return install(root, registry, args.agent, args.skill)
    if args.command == "uninstall":
        return uninstall(root, registry, args.agent, args.skill)
    if args.command == "sources":
        if args.sources_command == "list":
            return sources_list(root)
        if args.sources_command == "add":
            return sources_add(root, args.skill, args.repo, args.path, args.ref)
        if args.sources_command == "remove":
            return sources_remove(root, args.skill)
    if args.command == "outdated":
        return outdated(root, args.skill)
    if args.command == "sync":
        if args.all:
            manifest = load_manifest(root)
            failed = False
            for name in sorted(manifest["skills"]):
                failed = sync_skill(root, name) != 0 or failed
            return 1 if failed else 0
        if not args.skill:
            parser.error("sync requires a skill or --all")
        return sync_skill(root, args.skill)
    if args.command == "doctor":
        return doctor(root)
    parser.error(f"command not implemented yet: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
