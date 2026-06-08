import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import skills


class SkillsCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def make_skill(self, name, body=None):
        skill_dir = self.root / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        text = body or f"---\nname: {name}\ndescription: test skill\n---\n# {name}\n"
        (skill_dir / "SKILL.md").write_text(text, encoding="utf-8")
        return skill_dir

    def git(self, cwd, *args):
        return subprocess.run(["git", *args], cwd=cwd, check=True, text=True, capture_output=True)

    def init_git_repo(self, path):
        path.mkdir(parents=True, exist_ok=True)
        self.git(path, "init")
        self.git(path, "config", "user.email", "test@example.com")
        self.git(path, "config", "user.name", "Test User")

    def test_discovers_only_top_level_skill_directories(self):
        self.make_skill("frontend-design")
        self.make_skill("skill-authoring-guide")
        (self.root / "docs").mkdir()
        nested = self.root / "nested" / "inner"
        nested.mkdir(parents=True)
        (nested / "SKILL.md").write_text("---\nname: inner\n---\n", encoding="utf-8")

        discovered = skills.discover_skills(self.root)

        self.assertEqual(["frontend-design", "skill-authoring-guide"], [s.name for s in discovered])

    def test_link_status_identifies_linked_missing_conflict_and_broken(self):
        local = self.make_skill("frontend-design")
        agent_dir = self.root / "agent" / "skills"
        agent_dir.mkdir(parents=True)

        self.assertEqual("missing", skills.link_status(local, agent_dir / "frontend-design").state)

        os.symlink(local, agent_dir / "frontend-design")
        linked = skills.link_status(local, agent_dir / "frontend-design")
        self.assertEqual("linked", linked.state)
        self.assertEqual(local.resolve(), linked.target)

        conflict_local = self.make_skill("ui-ux-pro-max")
        conflict_path = agent_dir / "ui-ux-pro-max"
        conflict_path.mkdir()
        self.assertEqual("conflict", skills.link_status(conflict_local, conflict_path).state)

        broken_local = self.make_skill("broken-skill")
        broken_path = agent_dir / "broken-skill"
        missing_target = self.root / "missing-target"
        os.symlink(missing_target, broken_path)
        self.assertEqual("broken", skills.link_status(broken_local, broken_path).state)

    def test_install_status_and_uninstall_use_symlinks(self):
        self.make_skill("frontend-design")
        agent_dir = self.root / "codex-skills"

        out = io.StringIO()
        with redirect_stdout(out):
            rc = skills.main([
                "--root",
                str(self.root),
                "--agent-dir",
                f"codex={agent_dir}",
                "install",
                "--agent",
                "codex",
                "--skill",
                "frontend-design",
            ])

        self.assertEqual(0, rc)
        link = agent_dir / "frontend-design"
        self.assertTrue(link.is_symlink())
        self.assertEqual((self.root / "frontend-design").resolve(), link.resolve())

        out = io.StringIO()
        with redirect_stdout(out):
            rc = skills.main([
                "--root",
                str(self.root),
                "--agent-dir",
                f"codex={agent_dir}",
                "status",
                "--agent",
                "codex",
            ])

        self.assertEqual(0, rc)
        self.assertIn("frontend-design", out.getvalue())
        self.assertIn("linked", out.getvalue())

        out = io.StringIO()
        with redirect_stdout(out):
            rc = skills.main([
                "--root",
                str(self.root),
                "--agent-dir",
                f"codex={agent_dir}",
                "uninstall",
                "--agent",
                "codex",
                "--skill",
                "frontend-design",
            ])

        self.assertEqual(0, rc)
        self.assertFalse(link.exists())
        self.assertFalse(link.is_symlink())

    def test_install_refuses_conflicting_real_directory(self):
        self.make_skill("frontend-design")
        agent_dir = self.root / "codex-skills"
        (agent_dir / "frontend-design").mkdir(parents=True)

        out = io.StringIO()
        with redirect_stdout(out):
            rc = skills.main([
                "--root",
                str(self.root),
                "--agent-dir",
                f"codex={agent_dir}",
                "install",
                "--agent",
                "codex",
                "--skill",
                "frontend-design",
            ])

        self.assertEqual(1, rc)
        self.assertFalse((agent_dir / "frontend-design").is_symlink())

    def test_sources_add_list_and_remove_persist_manifest(self):
        self.make_skill("frontend-design")

        out = io.StringIO()
        with redirect_stdout(out):
            rc = skills.main([
                "--root",
                str(self.root),
                "sources",
                "add",
                "frontend-design",
                "--repo",
                "https://github.com/example/agent-skills.git",
                "--path",
                "skills/frontend-design",
                "--ref",
                "main",
            ])

        self.assertEqual(0, rc)
        manifest = json.loads((self.root / "skills.manifest.json").read_text(encoding="utf-8"))
        source = manifest["skills"]["frontend-design"]["source"]
        self.assertEqual("git", source["type"])
        self.assertEqual("https://github.com/example/agent-skills.git", source["repo"])
        self.assertEqual("skills/frontend-design", source["path"])
        self.assertEqual("main", source["ref"])

        out = io.StringIO()
        with redirect_stdout(out):
            rc = skills.main(["--root", str(self.root), "sources", "list"])

        self.assertEqual(0, rc)
        self.assertIn("frontend-design", out.getvalue())
        self.assertIn("skills/frontend-design", out.getvalue())

        out = io.StringIO()
        with redirect_stdout(out):
            rc = skills.main(["--root", str(self.root), "sources", "remove", "frontend-design"])

        self.assertEqual(0, rc)
        manifest = json.loads((self.root / "skills.manifest.json").read_text(encoding="utf-8"))
        self.assertNotIn("frontend-design", manifest["skills"])

    def test_load_manifest_returns_empty_structure_when_missing(self):
        self.assertEqual({"skills": {}}, skills.load_manifest(self.root))

    def test_latest_path_commit_tracks_only_source_subdirectory(self):
        upstream = self.root / "upstream"
        self.init_git_repo(upstream)
        source_dir = upstream / "skills" / "frontend-design"
        source_dir.mkdir(parents=True)
        (source_dir / "SKILL.md").write_text(
            "---\nname: frontend-design\ndescription: test\n---\n# v1\n",
            encoding="utf-8",
        )
        self.git(upstream, "add", ".")
        self.git(upstream, "commit", "-m", "add frontend skill")
        path_commit = self.git(upstream, "rev-parse", "HEAD").stdout.strip()

        (upstream / "README.md").write_text("repo docs\n", encoding="utf-8")
        self.git(upstream, "add", ".")
        self.git(upstream, "commit", "-m", "update repo docs")

        latest = skills.latest_path_commit(upstream, "HEAD", "skills/frontend-design")

        self.assertEqual(path_commit, latest)

    def test_outdated_reports_update_available_for_changed_source_path(self):
        local = self.make_skill("frontend-design")
        upstream = self.root / "upstream"
        self.init_git_repo(upstream)
        source_dir = upstream / "skills" / "frontend-design"
        source_dir.mkdir(parents=True)
        (source_dir / "SKILL.md").write_text(
            "---\nname: frontend-design\ndescription: test\n---\n# v1\n",
            encoding="utf-8",
        )
        self.git(upstream, "add", ".")
        self.git(upstream, "commit", "-m", "add frontend skill")
        first_commit = self.git(upstream, "rev-parse", "HEAD").stdout.strip()
        (source_dir / "README.md").write_text("new docs\n", encoding="utf-8")
        self.git(upstream, "add", ".")
        self.git(upstream, "commit", "-m", "update frontend skill")

        skills.save_manifest(self.root, {
            "skills": {
                "frontend-design": {
                    "source": {
                        "type": "git",
                        "repo": str(upstream),
                        "ref": "HEAD",
                        "path": "skills/frontend-design",
                        "last_commit": first_commit,
                        "last_checked_at": "",
                    }
                }
            }
        })

        status = skills.source_status(self.root, local.name)

        self.assertEqual("update-available", status["status"])

    def test_sync_copies_source_subdirectory_and_updates_manifest(self):
        self.make_skill("frontend-design")
        upstream = self.root / "upstream"
        self.init_git_repo(upstream)
        source_dir = upstream / "packages" / "frontend-design"
        source_dir.mkdir(parents=True)
        (source_dir / "SKILL.md").write_text(
            "---\nname: frontend-design\ndescription: synced\n---\n# Synced\n",
            encoding="utf-8",
        )
        (source_dir / "README.md").write_text("from upstream\n", encoding="utf-8")
        self.git(upstream, "add", ".")
        self.git(upstream, "commit", "-m", "add source skill")
        latest = self.git(upstream, "rev-parse", "HEAD").stdout.strip()
        skills.save_manifest(self.root, {
            "skills": {
                "frontend-design": {
                    "source": {
                        "type": "git",
                        "repo": str(upstream),
                        "ref": "HEAD",
                        "path": "packages/frontend-design",
                        "last_commit": "",
                        "last_checked_at": "",
                    }
                }
            }
        })

        out = io.StringIO()
        with redirect_stdout(out):
            rc = skills.main(["--root", str(self.root), "sync", "frontend-design"])

        self.assertEqual(0, rc)
        self.assertEqual("from upstream\n", (self.root / "frontend-design" / "README.md").read_text(encoding="utf-8"))
        manifest = skills.load_manifest(self.root)
        self.assertEqual(latest, manifest["skills"]["frontend-design"]["source"]["last_commit"])

    def test_doctor_reports_valid_skill_and_manifest_problem(self):
        self.make_skill("frontend-design")
        skills.save_manifest(self.root, {
            "skills": {
                "missing-skill": {
                    "source": {
                        "type": "git",
                        "repo": "https://github.com/example/repo.git",
                        "ref": "main",
                        "path": "skills/missing-skill",
                        "last_commit": "",
                        "last_checked_at": "",
                    }
                }
            }
        })

        out = io.StringIO()
        with redirect_stdout(out):
            rc = skills.main(["--root", str(self.root), "doctor"])

        self.assertEqual(1, rc)
        text = out.getvalue()
        self.assertIn("[ok] frontend-design has SKILL.md", text)
        self.assertIn("[error] manifest references missing local skill: missing-skill", text)

    def test_doctor_reports_frontmatter_name_mismatch(self):
        self.make_skill("frontend-design", "---\nname: wrong-name\ndescription: test\n---\n# Skill\n")

        out = io.StringIO()
        with redirect_stdout(out):
            rc = skills.main(["--root", str(self.root), "doctor"])

        self.assertEqual(1, rc)
        self.assertIn("[error] frontend-design frontmatter name is wrong-name", out.getvalue())


if __name__ == "__main__":
    unittest.main()
