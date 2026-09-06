"""
Tier 2: MkDocs Strict Build & Navigation Parity E2E Tests
Validates strict compilation, zero build warnings, bidirectional nav/file parity,
and Material theme configuration.
"""

import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

WORKTREE_VENV_MKDOCS = (
    Path(
        "C:/Users/andre/.gemini/antigravity/worktrees/security-standards-template/swift_axis_crosses_22h57/.venv/Scripts/mkdocs.exe"
    )
)


def get_mkdocs_executable() -> str:
    """Finds the mkdocs executable in environment, worktree venv, or local venv."""
    if "MKDOCS_BIN" in os.environ and Path(os.environ["MKDOCS_BIN"]).exists():
        return os.environ["MKDOCS_BIN"]
    if WORKTREE_VENV_MKDOCS.exists():
        return str(WORKTREE_VENV_MKDOCS)
    local_venv = REPO_ROOT / ".venv" / "Scripts" / "mkdocs.exe"
    if local_venv.exists():
        return str(local_venv)
    which_path = shutil.which("mkdocs")
    if which_path:
        return which_path
    return "mkdocs"


def extract_nav_targets(nav_item, collected: list):
    """Recursively extracts target markdown file paths from mkdocs nav structure."""
    if isinstance(nav_item, str):
        collected.append(nav_item.replace("\\", "/"))
    elif isinstance(nav_item, dict):
        for val in nav_item.values():
            extract_nav_targets(val, collected)
    elif isinstance(nav_item, list):
        for item in nav_item:
            extract_nav_targets(item, collected)


class TestTier2MkDocsBuild(unittest.TestCase):
    """Tier 2: MkDocs strict build execution and navigation consistency."""

    def test_mkdocs_configuration_exists(self):
        """Verifies mkdocs.yml exists in the repository root."""
        mkdocs_yml = REPO_ROOT / "mkdocs.yml"
        self.assertTrue(mkdocs_yml.exists(), "mkdocs.yml must exist at repository root")

    def test_material_theme_configuration(self):
        """Verifies that mkdocs.yml configures Material theme with required features."""
        mkdocs_yml = REPO_ROOT / "mkdocs.yml"
        self.assertTrue(mkdocs_yml.exists(), "mkdocs.yml not found")

        with open(mkdocs_yml, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # Theme validation
        theme = config.get("theme", {})
        if isinstance(theme, str):
            theme_name = theme
            theme_features = []
            theme_palette = None
        else:
            theme_name = theme.get("name", "")
            theme_features = theme.get("features", [])
            theme_palette = theme.get("palette", None)

        self.assertEqual(
            theme_name,
            "material",
            f"Expected theme name 'material', got '{theme_name}'",
        )

        expected_features = [
            "navigation.instant",
            "navigation.sections",
            "navigation.tabs",
            "navigation.top",
        ]
        for feature in expected_features:
            self.assertIn(
                feature,
                theme_features,
                f"Missing recommended Material navigation feature: {feature}",
            )

        self.assertIsNotNone(
            theme_palette,
            "Material theme palette should be configured for light/dark mode support",
        )

        # Plugins validation
        plugins = config.get("plugins", [])
        plugin_names = []
        for p in plugins:
            if isinstance(p, str):
                plugin_names.append(p)
            elif isinstance(p, dict):
                plugin_names.extend(p.keys())
        self.assertIn(
            "search",
            plugin_names,
            "Search plugin must be configured in mkdocs.yml",
        )

        # Markdown extensions validation
        exts = config.get("markdown_extensions", [])
        ext_names = []
        for e in exts:
            if isinstance(e, str):
                ext_names.append(e)
            elif isinstance(e, dict):
                ext_names.extend(e.keys())

        for required_ext in ["admonition", "tables"]:
            self.assertIn(
                required_ext,
                ext_names,
                f"Missing essential markdown extension: {required_ext}",
            )

    def test_bidirectional_nav_file_parity(self):
        """Verifies 100% bidirectional parity between mkdocs.yml nav and docs/ files."""
        mkdocs_yml = REPO_ROOT / "mkdocs.yml"
        self.assertTrue(mkdocs_yml.exists(), "mkdocs.yml not found")

        with open(mkdocs_yml, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        nav = config.get("nav", [])
        self.assertTrue(nav, "mkdocs.yml must define a 'nav' structure")

        nav_files = []
        extract_nav_targets(nav, nav_files)
        nav_set = {p.replace("\\", "/").lstrip("/") for p in nav_files}

        docs_dir = REPO_ROOT / "docs"
        self.assertTrue(docs_dir.exists(), "docs/ directory not found")

        disk_files = []
        for md_path in docs_dir.rglob("*.md"):
            rel_to_docs = md_path.relative_to(docs_dir).as_posix()
            disk_files.append(rel_to_docs)
        disk_set = set(disk_files)

        orphaned_files = disk_set - nav_set
        dead_nav_entries = nav_set - disk_set

        self.assertEqual(
            orphaned_files,
            set(),
            f"Files exist in docs/ but are missing from mkdocs.yml nav: {orphaned_files}",
        )
        self.assertEqual(
            dead_nav_entries,
            set(),
            f"Entries in mkdocs.yml nav do not exist in docs/: {dead_nav_entries}",
        )

    def test_mkdocs_strict_build(self):
        """Executes 'mkdocs build --strict' and verifies exit code 0 with zero warnings."""
        mkdocs_bin = get_mkdocs_executable()
        cmd = [mkdocs_bin, "build", "--strict"]

        site_dir = REPO_ROOT / "site"
        # Run build
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(
            result.returncode,
            0,
            f"'mkdocs build --strict' failed with exit code {result.returncode}.\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}",
        )

        # Verify HTML output
        index_html = site_dir / "index.html"
        self.assertTrue(
            index_html.exists(),
            f"Expected build artifact {index_html} to exist after build",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
