"""
Tier 3: Automation Tooling E2E Tests
Validates scripts/fill_placeholders.py, scripts/validate_isms.py, scripts/export_oscal.py,
scripts/check_adoption.py, and scripts/generate_docs.py CLI behavior, flags, dry-run safety,
and 6-framework coverage reporting.
"""

import hashlib
import json
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
        self.oscal_script = REPO_ROOT / "scripts" / "export_oscal.py"
        self.adopt_script = REPO_ROOT / "scripts" / "check_adoption.py"
        self.gendoc_script = REPO_ROOT / "scripts" / "generate_docs.py"

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

        self.assertNotIn("AttributeError", result.stderr)
        self.assertNotIn("ciso-name", result.stderr)
        self.assertNotIn("SyntaxError", result.stderr)

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
        """Verifies scripts/validate_isms.py --strict --check-drift validates the repository cleanly."""
        self.assertTrue(self.val_script.exists(), "scripts/validate_isms.py not found")
        cmd = [self.python_bin, str(self.val_script), "--strict", "--check-drift"]
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
            f"validate_isms.py --strict --check-drift failed with code {result.returncode}.\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}",
        )

    def test_validate_isms_coverage_report_and_formats(self):
        """Verifies validate_isms.py --coverage-report reports all 6 frameworks and supports json/sarif/markdown."""
        self.assertTrue(self.val_script.exists(), "scripts/validate_isms.py not found")
        cmd = [self.python_bin, str(self.val_script), "--coverage-report"]
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, f"validate_isms.py --coverage-report failed:\n{result.stderr}")

        output = result.stdout
        for fw in ("ISO/IEC 27001:2022", "SOC 2", "NIST Cybersecurity Framework 2.0", "GDPR", "NIST SP 800-53", "ASD Essential Eight"):
            self.assertIn(fw, output, f"Coverage report missing framework: {fw}")

        # Verify JSON and SARIF formats
        for fmt in ("json", "sarif"):
            res_fmt = subprocess.run(
                [self.python_bin, str(self.val_script), "--format", fmt],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res_fmt.returncode, 0)
            parsed = json.loads(res_fmt.stdout)
            self.assertIsInstance(parsed, dict)

    def test_export_oscal_cli_validate_and_check(self):
        """Verifies scripts/export_oscal.py --validate --check succeeds with exit code 0."""
        self.assertTrue(self.oscal_script.exists(), "scripts/export_oscal.py not found")
        res = subprocess.run(
            [self.python_bin, str(self.oscal_script), "--validate", "--check"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            res.returncode,
            0,
            f"export_oscal.py --validate --check failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}",
        )
        self.assertIn("[PASS]", res.stdout)

    def test_check_adoption_cli_strict(self):
        """Verifies scripts/check_adoption.py --manifest mappings/compliance_manifest.yaml --strict succeeds."""
        self.assertTrue(self.adopt_script.exists(), "scripts/check_adoption.py not found")
        res = subprocess.run(
            [
                self.python_bin,
                str(self.adopt_script),
                "--manifest",
                "mappings/compliance_manifest.yaml",
                "--strict",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            res.returncode,
            0,
            f"check_adoption.py --strict failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}",
        )
        self.assertIn("[PASS]", res.stdout)

    def test_generate_docs_cli_check(self):
        """Verifies scripts/generate_docs.py --check succeeds with exit code 0."""
        self.assertTrue(self.gendoc_script.exists(), "scripts/generate_docs.py not found")
        res = subprocess.run(
            [self.python_bin, str(self.gendoc_script), "--check"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            res.returncode,
            0,
            f"generate_docs.py --check failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}",
        )
        self.assertIn("[PASS]", res.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
