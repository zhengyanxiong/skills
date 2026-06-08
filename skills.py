#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AGENTS = {
    "codex": "~/.codex/skills",
    "claude-code": "~/.claude/skills",
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
    if not link_path.exists() and not link_path.is_symlink():
        return LinkStatus("missing")
    if link_path.is_symlink():
        raw_target = Path(os.readlink(link_path))
        target = raw_target if raw_target.is_absolute() else (link_path.parent / raw_target)
        if not target.exists():
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


def ensure_source_repo(root: Path, source: dict[str, Any]) -> Path:
    repo = source["repo"]
    cache = source_cache_dir(root, repo)
    if cache.exists():
        run_git(cache, "fetch", "--all", "--prune")
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


def source_status(root: Path, skill_name: str) -> dict[str, str]:
    manifest = load_manifest(root)
    source = source_entry(manifest, skill_name)
    if not source:
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
    print("Skill\tRepo\tRef\tPath\tLast Commit")
    for name in sorted(manifest["skills"]):
        source = manifest["skills"][name].get("source", {})
        print(
            f"{name}\t{source.get('repo', '-')}\t{source.get('ref', '-')}"
            f"\t{source.get('path', '-')}\t{source.get('last_commit', '-')}"
        )
    return 0


def sources_add(root: Path, skill_name: str, repo: str, source_path: str, ref: str) -> int:
    select_skills(skill_name, root)
    manifest = load_manifest(root)
    manifest["skills"][skill_name] = {
        "source": {
            "type": "git",
            "repo": repo,
            "ref": ref,
            "path": source_path,
            "last_commit": "",
            "last_checked_at": "",
        }
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

    sub.add_parser("list", help="List local skills")
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
        for skill in discover_skills(root):
            print(skill.name)
        return 0
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
