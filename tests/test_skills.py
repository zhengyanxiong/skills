"""Tests for skills.py — path safety, parsing, and core logic.

Run with: python3 -m pytest tests/
"""

import os
import json
from pathlib import Path

# conftest.py adds repo root to sys.path
import skills


# ── Path safety tests ──────────────────────────────────────────────────


class TestSanitizeName:
    def test_keeps_safe_names(self):
        assert skills.sanitize_name("my-skill") == "my-skill"
        assert skills.sanitize_name("skill_42") == "skill_42"
        assert skills.sanitize_name("hello.world") == "hello.world"

    def test_replaces_unsafe_chars(self):
        assert skills.sanitize_name("../etc/passwd") == "..-etc-passwd"
        assert skills.sanitize_name("a b c") == "a-b-c"
        assert skills.sanitize_name("foo/bar") == "foo-bar"

    def test_empty_string(self):
        assert skills.sanitize_name("") == ""


class TestIsSafePath:
    def test_under_base(self):
        base = Path("/home/user/skills")
        assert skills.is_safe_path(base / "my-skill", base)
        assert skills.is_safe_path(base / "sub" / "nested", base)

    def test_escapes_base(self):
        base = Path("/home/user/skills")
        assert not skills.is_safe_path(Path("/etc/passwd"), base)
        assert not skills.is_safe_path(base / ".." / "secret", base)

    def test_same_as_base(self):
        base = Path("/home/user/skills")
        assert not skills.is_safe_path(base, base)


class TestIsSafeSkillDir:
    def test_valid_directory(self, tmp_path):
        d = _make_skill_dir(tmp_path, "safe-skill")
        assert skills.is_safe_skill_dir(d)

    def test_symlink_outside(self, tmp_path):
        outside = Path("/tmp")  # outside tmp_path
        link = tmp_path / "evil-link"
        link.symlink_to(outside)
        assert not skills.is_safe_skill_dir(link)


# ── GitHub shorthand parsing ────────────────────────────────────────────


class TestParseGitHubShorthand:
    def test_owner_repo(self):
        result = skills.parse_github_shorthand("owner/repo")
        assert result is not None
        assert result["repo"] == "https://github.com/owner/repo.git"
        assert result["path"] == "skills"

    def test_owner_repo_subpath(self):
        result = skills.parse_github_shorthand("owner/repo/path/to/skill")
        assert result is not None
        assert result["path"] == "skills/path/to/skill"

    def test_not_a_shorthand(self):
        assert skills.parse_github_shorthand("just-a-string") is None
        assert skills.parse_github_shorthand("https://example.com/repo.git") is None


# ── Skill discovery ─────────────────────────────────────────────────────


class TestDiscoverSkills:
    def test_finds_skills(self, tmp_path):
        _make_skill_dir(tmp_path, "alpha")
        _make_skill_dir(tmp_path, "beta")
        found = skills.discover_skills(tmp_path)
        assert {s.name for s in found} == {"alpha", "beta"}

    def test_skips_dirs_without_skill_md(self, tmp_path):
        _make_skill_dir(tmp_path, "valid")
        (tmp_path / "no-skill").mkdir()
        found = skills.discover_skills(tmp_path)
        assert len(found) == 1 and found[0].name == "valid"

    def test_empty_directory(self, tmp_path):
        assert skills.discover_skills(tmp_path) == []


# ── Link status ─────────────────────────────────────────────────────────


class TestLinkStatus:
    def test_missing(self, tmp_path):
        skill = _make_skill_dir(tmp_path, "test-skill")
        status = skills.link_status(skill, tmp_path / "agent" / "test-skill")
        assert status.state == "missing"

    def test_correct_symlink(self, tmp_path):
        skill = _make_skill_dir(tmp_path, "test-skill")
        link_dir = tmp_path / "agent"
        link_dir.mkdir()
        link = link_dir / "test-skill"
        os.symlink(skill, link)
        status = skills.link_status(skill, link)
        assert status.state == "linked"
        assert status.target == skill.resolve()

    def test_broken_symlink(self, tmp_path):
        skill = _make_skill_dir(tmp_path, "real-skill")
        link_dir = tmp_path / "agent"
        link_dir.mkdir()
        link = link_dir / "ghost"
        os.symlink(tmp_path / "nonexistent", link)
        status = skills.link_status(skill, link)
        assert status.state == "broken"


# ── Manifest operations ─────────────────────────────────────────────────


class TestManifest:
    def test_load_empty(self, tmp_path):
        m = skills.load_manifest(tmp_path)
        assert m == {"skills": {}}

    def test_save_and_load(self, tmp_path):
        skills.save_manifest(tmp_path, {"skills": {"test": {"desc": "foo"}}})
        m = skills.load_manifest(tmp_path)
        assert m["skills"]["test"]["desc"] == "foo"

    def test_invalid_manifest(self, tmp_path):
        p = skills.manifest_path(tmp_path)
        p.write_text('{"not_skills": {}}', encoding="utf-8")
        import pytest
        with pytest.raises(SystemExit):
            skills.load_manifest(tmp_path)


# ── Agent directory resolution ──────────────────────────────────────────


class TestAgentDirs:
    def test_contains_known_agents(self):
        dirs = skills.agent_dirs()
        for agent in ("codex", "claude-code", "hermes"):
            assert agent in dirs
            assert dirs[agent].is_absolute()

    def test_with_overrides(self):
        dirs = skills.agent_dirs({"custom-agent": "/tmp/custom"})
        assert str(dirs["custom-agent"]) == "/tmp/custom"

    def test_select(self):
        reg = {"a": Path("/p1"), "b": Path("/p2")}
        assert list(skills.select_agents("a", reg)) == ["a"]
        assert list(skills.select_agents("all", reg)) == ["a", "b"]


# ── Helpers ─────────────────────────────────────────────────────────────


def _make_skill_dir(root: Path, name: str) -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(
        f"---\nname: {name}\n---\n\n# {name}\n", encoding="utf-8"
    )
    return d
