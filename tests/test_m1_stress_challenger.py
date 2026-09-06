"""
Milestone 1 Adversarial Stress Test Suite
Author: challenger_m1_1 (Milestone 1 Challenger)
Target: scripts/fill_placeholders.py, mkdocs.yml, and MkDocs build strictness
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

def get_python() -> str:
    local_venv = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    if local_venv.exists():
        return str(local_venv)
    return sys.executable


def get_mkdocs() -> str:
    local_mkdocs = REPO_ROOT / ".venv" / "Scripts" / "mkdocs.exe"
    if local_mkdocs.exists():
        return str(local_mkdocs)
    which_path = shutil.which("mkdocs")
    if which_path:
        return which_path
    return "mkdocs"


class TestMilestone1AdversarialStress(unittest.TestCase):
    """Adversarial challenge test cases for Milestone 1."""

    def setUp(self):
        self.python_bin = get_python()
        self.mkdocs_bin = get_mkdocs()
        self.fill_script = REPO_ROOT / "scripts" / "fill_placeholders.py"
        self.mkdocs_yml = REPO_ROOT / "mkdocs.yml"

    def test_01_fill_placeholders_idempotency_and_hash_preservation(self):
        """Stress: Multiple --dry-run executions must preserve 100% file hashes and timestamps, and verify O'Connor single-quote parsing."""
        # Collect all markdown files and mkdocs.yml
        target_files = list((REPO_ROOT / "docs").rglob("*.md")) + [self.mkdocs_yml]
        self.assertGreater(len(target_files), 30)

        initial_hashes = {f: hashlib.sha256(f.read_bytes()).hexdigest() for f in target_files}
        initial_mtimes = {f: f.stat().st_mtime_ns for f in target_files}

        cmd = [
            self.python_bin,
            str(self.fill_script),
            "--dry-run",
            "--company-name", "O'Connor & Sons Security",
            "--ciso-name", "Jane Doe",
            "--author-name", "Security Engineering",
            "--dpo-name", "Alex Rivera",
            "--insert-date", "2026-10-26",
            "--min-password-length", "16",
        ]

        # Run 5 consecutive times
        for i in range(5):
            res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Run {i+1} failed: {res.stderr}")

            current_hashes = {f: hashlib.sha256(f.read_bytes()).hexdigest() for f in target_files}
            current_mtimes = {f: f.stat().st_mtime_ns for f in target_files}

            self.assertEqual(initial_hashes, current_hashes, f"File hashes mutated on dry-run {i+1}")
            self.assertEqual(initial_mtimes, current_mtimes, f"File timestamps mutated on dry-run {i+1}")

        # Verify O'Connor single-quote parsing in mkdocs.yml
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            tmp_mkdocs = tmp_path / "mkdocs.yml"
            tmp_docs = tmp_path / "docs"
            tmp_docs.mkdir()
            (tmp_docs / "index.md").write_text("# [COMPANY_NAME] Docs\n", encoding="utf-8")
            tmp_mkdocs.write_text(self.mkdocs_yml.read_text(encoding="utf-8"), encoding="utf-8")

            res_fill = subprocess.run(
                [self.python_bin, str(self.fill_script), "--docs-dir", str(tmp_docs), "--company-name", "O'Connor & Sons Security"],
                cwd=str(tmp_path),
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_fill.returncode, 0, f"Fill script failed: {res_fill.stderr}")
            parsed = yaml.safe_load(tmp_mkdocs.read_text(encoding="utf-8"))
            self.assertEqual(
                parsed["site_name"],
                "O'Connor & Sons Security Information Security Management System"
            )

    def test_02_fill_placeholders_empty_string_handling(self):
        """Edge Case: Passing empty string values (--company-name '') is silently dropped."""
        cmd = [
            self.python_bin,
            str(self.fill_script),
            "--dry-run",
            "--company-name", "",
        ]
        res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        # Empty string results in 'no placeholder arguments provided'
        self.assertEqual(res.returncode, 0)
        self.assertIn("No placeholder arguments provided", res.stdout)

        # Empty string alongside valid parameter
        cmd2 = [
            self.python_bin,
            str(self.fill_script),
            "--dry-run",
            "--company-name", "",
            "--ciso-name", "Jane Doe",
        ]
        res2 = subprocess.run(cmd2, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(res2.returncode, 0)
        # Demonstrates that [COMPANY_NAME] is silently ignored rather than replaced with empty string
        self.assertNotIn("[COMPANY_NAME]", res2.stdout)
        self.assertIn("[CISO_NAME]", res2.stdout)

    def test_03_fill_placeholders_inexistent_docs_dir(self):
        """Validation: Non-existent docs directory must abort with exit code 1 and error on stderr."""
        cmd = [
            self.python_bin,
            str(self.fill_script),
            "--dry-run",
            "--docs-dir", "non_existent_directory_xyz",
            "--company-name", "Acme Corp",
        ]
        res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn("does not exist", res.stderr)

        # Also verify file path passed to --docs-dir is rejected
        cmd_file = [
            self.python_bin,
            str(self.fill_script),
            "--dry-run",
            "--docs-dir", "mkdocs.yml",
            "--company-name", "Acme Corp",
        ]
        res_file = subprocess.run(cmd_file, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(res_file.returncode, 1)
        self.assertIn("does not exist", res_file.stderr)

    def test_04_fill_placeholders_min_password_length_custom(self):
        """Stress: Verify custom --min-password-length value and default propagation."""
        # 1. Custom value standalone
        cmd = [
            self.python_bin,
            str(self.fill_script),
            "--dry-run",
            "--min-password-length", "20",
        ]
        res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("[MIN_PASSWORD_LENGTH] => '20'", res.stdout)

        # 2. Invalid integer argument rejected by argparse
        cmd_invalid = [
            self.python_bin,
            str(self.fill_script),
            "--dry-run",
            "--min-password-length", "not_a_number",
        ]
        res_invalid = subprocess.run(cmd_invalid, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertNotEqual(res_invalid.returncode, 0)

    def test_05_special_characters_single_quote_yaml_hazard(self):
        """Verify company name with single quote safely populates mkdocs.yml and parses correctly."""
        sample_company = "O'Connor & Sons Security"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            tmp_mkdocs = tmp_path / "mkdocs.yml"
            tmp_docs = tmp_path / "docs"
            tmp_docs.mkdir()
            (tmp_docs / "index.md").write_text("# [COMPANY_NAME] Docs\n", encoding="utf-8")
            tmp_mkdocs.write_text(self.mkdocs_yml.read_text(encoding="utf-8"), encoding="utf-8")

            cmd = [
                self.python_bin,
                str(self.fill_script),
                "--docs-dir", str(tmp_docs),
                "--company-name", sample_company,
            ]
            res = subprocess.run(cmd, cwd=tmp_dir, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Script failed: {res.stderr}")

            parsed = yaml.safe_load(tmp_mkdocs.read_text(encoding="utf-8"))
            self.assertEqual(
                parsed["site_name"],
                "O'Connor & Sons Security Information Security Management System"
            )
            md_content = (tmp_docs / "index.md").read_text(encoding="utf-8")
            self.assertIn("# O'Connor & Sons Security Docs", md_content)

    def test_06_special_characters_unicode_console_crash(self):
        """Verify Unicode emojis do not crash script under cp1252 or legacy console."""
        cmd = [
            self.python_bin,
            str(self.fill_script),
            "--dry-run",
            "--company-name", "🛡️ CyberGuard",
        ]
        env = dict(os.environ)
        # Force cp1252 legacy encoding to simulate Windows default non-UTF-8 console
        env["PYTHONIOENCODING"] = "cp1252"
        res = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            env=env,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(res.returncode, 0, f"Script failed with stderr: {res.stderr}")
        self.assertNotIn("UnicodeEncodeError", res.stderr)
        self.assertIn("CyberGuard", res.stdout)
        self.assertIn("Files modified: 39 / 39", res.stdout)

    def test_07_mkdocs_strict_build_fails_on_missing_nav_file(self):
        """Stress: Verify mkdocs build --strict fails when a nav target file is missing."""
        orig_yml = self.mkdocs_yml.read_text(encoding="utf-8")
        corrupted_yml = orig_yml + "\n  - Broken Entry: 99_Missing/non_existent.md\n"
        try:
            self.mkdocs_yml.write_text(corrupted_yml, encoding="utf-8")
            res = subprocess.run(
                [self.mkdocs_bin, "build", "--strict"],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(res.returncode, 0, "mkdocs build --strict MUST fail on missing nav file")
            self.assertIn("Aborted with", res.stdout)
        finally:
            self.mkdocs_yml.write_text(orig_yml, encoding="utf-8")

    def test_08_mkdocs_strict_build_fails_on_broken_relative_link(self):
        """Stress: Verify mkdocs build --strict fails when an invalid relative link is introduced."""
        index_md = REPO_ROOT / "docs" / "index.md"
        orig_content = index_md.read_text(encoding="utf-8")
        corrupted_content = orig_content + "\n\n[Adversarial Link Test](non_existent_document.md)\n"
        try:
            index_md.write_text(corrupted_content, encoding="utf-8")
            res = subprocess.run(
                [self.mkdocs_bin, "build", "--strict"],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(res.returncode, 0, "mkdocs build --strict MUST fail on broken relative link")
            self.assertIn("Aborted with", res.stdout)
        finally:
            index_md.write_text(orig_content, encoding="utf-8")

    def test_09_mkdocs_search_index_and_theme_assets(self):
        """Stress: Verify search_index.json completeness and Material theme assets."""
        site_dir = REPO_ROOT / "site"
        # Run strict build to ensure fresh artifacts
        res = subprocess.run(
            [self.mkdocs_bin, "build", "--strict"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"mkdocs build failed: {res.stderr}")

        # Check search index
        search_idx = site_dir / "search" / "search_index.json"
        self.assertTrue(search_idx.exists(), "search_index.json missing")
        with open(search_idx, "r", encoding="utf-8") as f:
            data = json.load(f)
        docs = data.get("docs", [])
        self.assertGreater(len(docs), 200, "Search index should contain >200 indexed sections")

        # Check theme assets
        assets_dir = site_dir / "assets"
        self.assertTrue((assets_dir / "stylesheets").exists(), "stylesheets dir missing")
        self.assertTrue((assets_dir / "javascripts").exists(), "javascripts dir missing")
        self.assertGreater(len(list((assets_dir / "stylesheets").glob("*.css"))), 0)
        self.assertGreater(len(list((assets_dir / "javascripts").glob("*.js"))), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
