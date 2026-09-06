"""
Tier 3: Automation Tooling E2E Tests
Validates scripts/fill_placeholders.py and scripts/validate_isms.py CLI behavior,
flags, dry-run safety, and framework coverage reporting.
"""

import hashlib
import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

def get_python_executable() -> str:
    """Finds the python executable in environment, local venv, or sys.executable."""
    if "PYTHON_BIN" in os.environ and Path(os.environ["PYTHON_BIN"]).exists():
        return os.environ["PYTHON_BIN"]
    local_venv = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    if local_venv.exists():
        return str(local_venv)
    return sys.executable


class TestTier3Automation(unittest.TestCase):
    """Tier 3: Automation script invocation, dry-run safety, and compliance verification."""

    def setUp(self):
        self.python_bin = get_python_executable()
        self.fill_script = REPO_ROOT / "scripts" / "fill_placeholders.py"
        self.val_script = REPO_ROOT / "scripts" / "validate_isms.py"

    def test_fill_placeholders_help(self):
        """Verifies scripts/fill_placeholders.py --help succeeds with code 0."""
        self.assertTrue(self.fill_script.exists(), "scripts/fill_placeholders.py not found")
        cmd = [self.python_bin, str(self.fill_script), "--help"]
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
            f"fill_placeholders.py --help failed: {result.stderr}",
        )
        self.assertIn("usage", result.stdout.lower())

    def test_fill_placeholders_dry_run_execution(self):
        """Verifies fill_placeholders.py --dry-run operates safely without mutating files."""
        self.assertTrue(self.fill_script.exists(), "scripts/fill_placeholders.py not found")

        # Snapshot mkdocs.yml and docs/index.md content hashes before dry-run
        files_to_watch = [REPO_ROOT / "mkdocs.yml", REPO_ROOT / "docs" / "index.md"]
        hashes_before = {}
        for f in files_to_watch:
            if f.exists():
                hashes_before[f] = hashlib.sha256(f.read_bytes()).hexdigest()

        cmd = [
            self.python_bin,
            str(self.fill_script),
            "--dry-run",
            "--company-name",
            "Acme Cybersecurity Corp",
            "--ciso-name",
            "Jane Doe",
            "--author-name",
            "Security Engineering Team",
            "--dpo-name",
            "Alex Rivera",
            "--insert-date",
            "2026-10-26",
            "--min-password-length",
            "14",
        ]

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
            f"fill_placeholders.py --dry-run failed with code {result.returncode}.\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}",
        )

        # Ensure no syntax/attribute bugs occurred
        self.assertNotIn("AttributeError", result.stderr)
        self.assertNotIn("ciso-name", result.stderr)
        self.assertNotIn("SyntaxError", result.stderr)

        # Verify that files were not modified on disk
        for f, h_before in hashes_before.items():
            if f.exists():
                h_after = hashlib.sha256(f.read_bytes()).hexdigest()
                self.assertEqual(
                    h_before,
                    h_after,
                    f"File {f} was modified during --dry-run execution!",
                )

    def test_fill_placeholders_list_remaining(self):
        """Verifies fill_placeholders.py --list-remaining executes with exit code 0 and discovers standardized placeholders."""
        self.assertTrue(self.fill_script.exists(), "scripts/fill_placeholders.py not found")
        cmd = [self.python_bin, str(self.fill_script), "--list-remaining"]
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
            f"fill_placeholders.py --list-remaining failed: {result.stderr}",
        )
        for expected_tag in (
            "[COMPANY_NAME]",
            "[CISO_NAME]",
            "[APPLICABLE_REGULATIONS]",
            "[INDUSTRY_SECTOR]",
            "[ORG_STRUCTURE]",
            "[ISMS_SCOPE]",
        ):
            self.assertIn(
                expected_tag,
                result.stdout,
                f"Expected placeholder {expected_tag} not found in --list-remaining output",
            )

    def test_fill_placeholders_context_flags_dry_run(self):
        """Verifies fill_placeholders.py supports context flags (--applicable-regulations, --industry-sector, --org-structure, --isms-scope)."""
        cmd = [
            self.python_bin,
            str(self.fill_script),
            "--dry-run",
            "--applicable-regulations", "GDPR, SOC 2, ISO 27001",
            "--industry-sector", "Cloud FinTech",
            "--org-structure", "Remote-first global engineering organization",
            "--isms-scope", "Core SaaS platform and cloud infrastructure",
        ]
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, f"Context flags dry-run failed: {result.stderr}")
        self.assertIn("[APPLICABLE_REGULATIONS]: 1", result.stdout)
        self.assertIn("[INDUSTRY_SECTOR]: 1", result.stdout)
        self.assertIn("[ORG_STRUCTURE]: 1", result.stdout)
        self.assertIn("[ISMS_SCOPE]: 1", result.stdout)

    def test_validate_isms_help(self):
        """Verifies scripts/validate_isms.py --help succeeds with code 0."""
        self.assertTrue(self.val_script.exists(), "scripts/validate_isms.py not found")
        cmd = [self.python_bin, str(self.val_script), "--help"]
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
            f"validate_isms.py --help failed: {result.stderr}",
        )
        self.assertIn("usage", result.stdout.lower())

    def test_validate_isms_strict_mode(self):
        """Verifies scripts/validate_isms.py --strict validates the repository cleanly."""
        self.assertTrue(self.val_script.exists(), "scripts/validate_isms.py not found")
        cmd = [self.python_bin, str(self.val_script), "--strict"]
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
            f"validate_isms.py --strict failed with code {result.returncode}.\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}",
        )

    def test_validate_isms_coverage_report(self):
        """Verifies validate_isms.py --coverage-report reports full framework metrics."""
        self.assertTrue(self.val_script.exists(), "scripts/validate_isms.py not found")
        cmd = [self.python_bin, str(self.val_script), "--coverage-report"]
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
            f"validate_isms.py --coverage-report failed with code {result.returncode}.\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}",
        )

        output = result.stdout
        # Assert coverage reporting includes the major compliance frameworks
        self.assertTrue(
            "ISO" in output or "27001" in output,
            "Coverage report missing ISO/IEC 27001 section",
        )
        self.assertTrue(
            "SOC 2" in output or "SOC2" in output or "TSC" in output,
            "Coverage report missing SOC 2 section",
        )
        self.assertTrue(
            "NIST" in output or "CSF" in output,
            "Coverage report missing NIST CSF section",
        )
        self.assertTrue(
            "GDPR" in output,
            "Coverage report missing GDPR section",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
