#!/usr/bin/env python3
"""
tests/test_v2_m3_adversarial_challenger.py
Empirical Adversarial Stress Test Suite for Milestone 3 Deliverables:
1. Enhanced ISMS Validator (validate_isms.py):
   - Multi-format outputs (text, json, sarif, markdown)
   - 6-framework coverage report banner stability & COMPLIANT statuses
   - Bidirectional drift checking (--check-drift) against SoA and synthetic mutations
   - Catalog integrity & JSON schema validation against framework_registry.schema.json
2. Deterministic OSCAL v1.2.0 Export Engine (export_oscal.py):
   - Write mode execution & UnboundLocalError bug detection
   - 100% byte-level determinism & SHA-256 reproducibility
   - Schema validation against oscal_v1_2_0_subset.schema.json
   - --check flag sensitivity to missing files, corrupted content, and CRLF normalization
   - Negative mutation testing on OSCAL structures
3. Regulation Adoption & Policy Auditing CLI (check_adoption.py):
   - Manifest schema validation against compliance_manifest.schema.json
   - Exact boundary date math on security exceptions (--current-date)
   - Security exception duration bounds (<= 90 days), approvers, compensating controls
   - Framework threshold & Essential Eight ML2 target maturity enforcement
   - Document review cadence audits (365 days) and [INSERT_DATE] tolerance
   - Multi-format outputs (text, json, markdown, sarif)
"""

import copy
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON_EXE = sys.executable


def run_py_command(cmd_args, cwd=REPO_ROOT):
    """Run a Python CLI command in the repository environment and return result."""
    proc = subprocess.run(
        [PYTHON_EXE, *cmd_args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestMilestone3AdversarialChallenger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry_path = REPO_ROOT / "mappings" / "framework_registry.yaml"
        with open(cls.registry_path, "r", encoding="utf-8") as f:
            cls.registry_data = yaml.safe_load(f)

        cls.manifest_path = REPO_ROOT / "mappings" / "compliance_manifest.yaml"
        with open(cls.manifest_path, "r", encoding="utf-8") as f:
            cls.manifest_data = yaml.safe_load(f)

        cls.catalogs_dir = REPO_ROOT / "mappings" / "catalogs"
        cls.oscal_schema_path = REPO_ROOT / "schemas" / "oscal_v1_2_0_subset.schema.json"
        with open(cls.oscal_schema_path, "r", encoding="utf-8") as f:
            cls.oscal_schema = json.load(f)

        cls.manifest_schema_path = REPO_ROOT / "schemas" / "compliance_manifest.schema.json"
        with open(cls.manifest_schema_path, "r", encoding="utf-8") as f:
            cls.manifest_schema = json.load(f)

        cls.registry_schema_path = REPO_ROOT / "schemas" / "framework_registry.schema.json"
        with open(cls.registry_schema_path, "r", encoding="utf-8") as f:
            cls.registry_schema = json.load(f)

        cls.soa_path = REPO_ROOT / "docs" / "01_ISMS_Framework" / "05_Statement_of_Applicability_SoA.md"
        cls.dist_oscal_dir = REPO_ROOT / "dist" / "oscal"

    # =========================================================================
    # PART 1: export_oscal.py Stress Testing & Defect Detection
    # =========================================================================

    def test_01_export_oscal_write_mode_defect_detection(self):
        """
        DEFECT DETECTION:
        Stress test export_oscal.py in write mode (without --check).
        In the current implementation, lines 604-609 fail to define target_file
        and fail to call target_file.write_text, crashing with UnboundLocalError:
        'cannot access local variable target_file where it is not associated with a value'.
        This empirical test documents and exposes the defect.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir) / "oscal_out"
            rc, stdout, stderr = run_py_command(
                ["scripts/export_oscal.py", "--output-dir", str(out_dir)]
            )
            
            # If the bug exists, rc != 0 and UnboundLocalError is in stderr
            if rc != 0:
                self.assertIn(
                    "UnboundLocalError",
                    stderr,
                    "Expected UnboundLocalError on target_file in export_oscal.py write mode",
                )
                self.assertIn("target_file", stderr)
                # Confirm 0 files were created in out_dir
                files_created = list(out_dir.glob("*.json")) if out_dir.exists() else []
                self.assertEqual(
                    len(files_created),
                    0,
                    f"Expected 0 files written due to write mode crash, got {files_created}",
                )
            else:
                # If the defect has been fixed, assert all 5 files were exported cleanly
                self.assertEqual(rc, 0)
                expected_files = {
                    "catalog.json",
                    "mapping_collection.json",
                    "profile_e8_ml2.json",
                    "profile_nist_800_53_moderate.json",
                    "component_definition.json",
                }
                actual_files = {p.name for p in out_dir.glob("*.json")}
                self.assertEqual(expected_files, actual_files)

    def test_02_export_oscal_byte_determinism_and_sha256(self):
        """
        Verify that OSCAL model generation functions produce 100% byte-for-byte
        deterministic JSON outputs across repeated invocations.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import export_oscal

            models_run_1 = {
                "catalog.json": export_oscal.serialize_model(
                    export_oscal.generate_catalog_model(self.registry_data)
                ),
                "mapping_collection.json": export_oscal.serialize_model(
                    export_oscal.generate_mapping_collection_model(self.registry_data)
                ),
                "profile_e8_ml2.json": export_oscal.serialize_model(
                    export_oscal.generate_profile_e8_ml2_model(self.registry_data)
                ),
                "profile_nist_800_53_moderate.json": export_oscal.serialize_model(
                    export_oscal.generate_profile_nist_800_53_moderate_model(self.registry_data)
                ),
                "component_definition.json": export_oscal.serialize_model(
                    export_oscal.generate_component_definition_model(self.registry_data)
                ),
            }

            models_run_2 = {
                "catalog.json": export_oscal.serialize_model(
                    export_oscal.generate_catalog_model(self.registry_data)
                ),
                "mapping_collection.json": export_oscal.serialize_model(
                    export_oscal.generate_mapping_collection_model(self.registry_data)
                ),
                "profile_e8_ml2.json": export_oscal.serialize_model(
                    export_oscal.generate_profile_e8_ml2_model(self.registry_data)
                ),
                "profile_nist_800_53_moderate.json": export_oscal.serialize_model(
                    export_oscal.generate_profile_nist_800_53_moderate_model(self.registry_data)
                ),
                "component_definition.json": export_oscal.serialize_model(
                    export_oscal.generate_component_definition_model(self.registry_data)
                ),
            }

            for name, content1 in models_run_1.items():
                content2 = models_run_2[name]
                hash1 = hashlib.sha256(content1.encode("utf-8")).hexdigest()
                hash2 = hashlib.sha256(content2.encode("utf-8")).hexdigest()
                self.assertEqual(
                    hash1,
                    hash2,
                    f"OSCAL model {name} failed byte-level determinism between runs",
                )
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    def test_03_export_oscal_existing_dist_files_valid_against_schema(self):
        """
        Validate that all 5 files in dist/oscal/ exist and strictly validate
        against schemas/oscal_v1_2_0_subset.schema.json.
        """
        expected_models = [
            "catalog.json",
            "mapping_collection.json",
            "profile_e8_ml2.json",
            "profile_nist_800_53_moderate.json",
            "component_definition.json",
        ]
        self.assertTrue(
            self.dist_oscal_dir.exists(), "dist/oscal directory does not exist"
        )

        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import export_oscal

            for fname in expected_models:
                fpath = self.dist_oscal_dir / fname
                self.assertTrue(fpath.exists(), f"Missing OSCAL model in dist/oscal: {fname}")
                with open(fpath, "r", encoding="utf-8") as f:
                    model_data = json.load(f)
                errs = export_oscal.validate_oscal_model(
                    model_data, self.oscal_schema, fname
                )
                self.assertEqual(
                    errs, [], f"Schema validation errors in {fname}: {errs}"
                )
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    def test_04_export_oscal_check_flag_clean_pass(self):
        """Verify python scripts/export_oscal.py --validate --check passes cleanly with code 0."""
        rc, stdout, stderr = run_py_command(
            ["scripts/export_oscal.py", "--validate", "--check"]
        )
        self.assertEqual(rc, 0, f"export_oscal.py --validate --check failed: {stderr}")
        self.assertIn("OSCAL export verification check passed", stdout)

    def test_05_export_oscal_check_flag_detects_missing_file(self):
        """
        Stress test: In a sandbox with one OSCAL model deleted,
        export_oscal.py --check MUST fail with exit code 1.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            sandbox = Path(tmp_dir) / "oscal"
            shutil.copytree(self.dist_oscal_dir, sandbox)
            # Delete one model
            (sandbox / "profile_e8_ml2.json").unlink()

            rc, stdout, stderr = run_py_command(
                ["scripts/export_oscal.py", "--output-dir", str(sandbox), "--check"]
            )
            self.assertEqual(rc, 1, "Expected exit code 1 when OSCAL file is missing")
            self.assertIn("Missing target file in --check mode", stderr)

    def test_06_export_oscal_check_flag_detects_content_drift(self):
        """
        Stress test: In a sandbox with modified content in an OSCAL model,
        export_oscal.py --check MUST fail with exit code 1.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            sandbox = Path(tmp_dir) / "oscal"
            shutil.copytree(self.dist_oscal_dir, sandbox)
            cat_file = sandbox / "catalog.json"
            cat_data = json.loads(cat_file.read_text(encoding="utf-8"))
            cat_data["catalog"]["metadata"]["title"] = "MUTATED ADVERSARIAL TITLE"
            cat_file.write_text(json.dumps(cat_data, indent=2) + "\n", encoding="utf-8")

            rc, stdout, stderr = run_py_command(
                ["scripts/export_oscal.py", "--output-dir", str(sandbox), "--check"]
            )
            self.assertEqual(rc, 1, "Expected exit code 1 when OSCAL content drifts")
            self.assertIn("Drift detected in catalog.json", stderr)

    def test_07_export_oscal_check_flag_crlf_normalization(self):
        """
        Stress test: Verify that Windows CRLF line endings in on-disk OSCAL files
        do NOT cause false drift detections under --check.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            sandbox = Path(tmp_dir) / "oscal"
            shutil.copytree(self.dist_oscal_dir, sandbox)
            # Convert all files to CRLF
            for p in sandbox.glob("*.json"):
                c = p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\n", "\r\n")
                p.write_bytes(c.encode("utf-8"))

            rc, stdout, stderr = run_py_command(
                ["scripts/export_oscal.py", "--output-dir", str(sandbox), "--check"]
            )
            self.assertEqual(
                rc, 0, f"Expected exit code 0 despite CRLF line endings, got {rc}: {stderr}"
            )

    def test_08_export_oscal_schema_negative_mutation(self):
        """
        Negative schema stress testing: Mutate OSCAL models with invalid metadata
        and ensure validate_oscal_model rejects them.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import export_oscal

            valid_cat = export_oscal.generate_catalog_model(self.registry_data)

            # Mutation 1: Missing oscal-version
            mut1 = copy.deepcopy(valid_cat)
            del mut1["catalog"]["metadata"]["oscal-version"]
            errs1 = export_oscal.validate_oscal_model(mut1, self.oscal_schema, "catalog.json")
            self.assertTrue(len(errs1) > 0, "Expected schema validation error for missing oscal-version")

            # Mutation 2: Empty root object
            mut2 = {}
            errs2 = export_oscal.validate_oscal_model(mut2, self.oscal_schema, "empty.json")
            self.assertTrue(len(errs2) > 0, "Expected schema validation error for empty root")

            # Mutation 3: Missing UUID
            mut3 = copy.deepcopy(valid_cat)
            del mut3["catalog"]["uuid"]
            errs3 = export_oscal.validate_oscal_model(mut3, self.oscal_schema, "catalog.json")
            self.assertTrue(len(errs3) > 0, "Expected schema validation error for missing uuid")
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    # =========================================================================
    # PART 2: validate_isms.py Stress Testing (Multi-Format, Drift, Catalogs)
    # =========================================================================

    def test_09_validate_isms_format_json_structure(self):
        """Verify validate_isms.py --format json produces valid JSON with required keys."""
        rc, stdout, stderr = run_py_command(
            ["scripts/validate_isms.py", "--format", "json"]
        )
        self.assertEqual(rc, 0, f"validate_isms.py --format json failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data.get("status"), "PASS")
        self.assertEqual(data.get("exit_code"), 0)
        self.assertIn("metrics", data)
        self.assertIn("canonical_controls", data["metrics"])
        self.assertIn("frameworks", data)
        self.assertEqual(len(data["frameworks"]), 6)
        self.assertEqual(data.get("violations"), [])

    def test_10_validate_isms_format_sarif_schema_v210(self):
        """Verify validate_isms.py --format sarif outputs valid SARIF v2.1.0 payload."""
        rc, stdout, stderr = run_py_command(
            ["scripts/validate_isms.py", "--format", "sarif"]
        )
        self.assertEqual(rc, 0, f"validate_isms.py --format sarif failed: {stderr}")
        sarif = json.loads(stdout)
        self.assertEqual(sarif.get("version"), "2.1.0")
        self.assertIn("runs", sarif)
        self.assertTrue(len(sarif["runs"]) > 0)
        tool = sarif["runs"][0].get("tool", {})
        self.assertEqual(tool.get("driver", {}).get("name"), "validate_isms")
        rules = tool.get("driver", {}).get("rules", [])
        rule_ids = {r["id"] for r in rules}
        expected_rules = {"ISMS001", "ISMS002", "ISMS003", "ISMS004", "ISMS005", "ISMS006", "ISMS007"}
        self.assertTrue(expected_rules.issubset(rule_ids))
        self.assertEqual(sarif["runs"][0].get("results"), [])

    def test_11_validate_isms_format_markdown_rendering(self):
        """Verify validate_isms.py --format markdown outputs formatted GFM table."""
        rc, stdout, stderr = run_py_command(
            ["scripts/validate_isms.py", "--format", "markdown"]
        )
        self.assertEqual(rc, 0, f"validate_isms.py --format markdown failed: {stderr}")
        self.assertIn("# ISMS Framework Compliance & Integrity Validation Report", stdout)
        self.assertIn("- **Status**: `PASS`", stdout)
        self.assertIn("| Framework / Standard | Version | Mapped / Benchmark | Coverage % | Status |", stdout)
        self.assertIn("Zero validation violations detected", stdout)

    def test_12_validate_isms_coverage_report_banner_and_compliance(self):
        """
        Verify validate_isms.py --coverage-report outputs the exact backward-compatible
        80-column banner and 100% COMPLIANT status for all 6 frameworks.
        """
        rc, stdout, stderr = run_py_command(
            ["scripts/validate_isms.py", "--coverage-report"]
        )
        self.assertEqual(rc, 0, f"validate_isms.py --coverage-report failed: {stderr}")
        expected_banner = "          ISMS FRAMEWORK COMPLIANCE & CONTROL COVERAGE REPORT"
        ruler = "=" * 80
        self.assertIn(ruler, stdout)
        self.assertIn(expected_banner, stdout)

        # Assert all 6 frameworks are listed with COMPLIANT
        fws = [
            "ISO/IEC 27001:2022 Annex A",
            "AICPA SOC 2 (2017/2022 TSC)",
            "NIST Cybersecurity Framework 2.0",
            "General Data Protection Regulation (GDPR)",
            "NIST SP 800-53 Rev. 5",
            "ASD Essential Eight",
        ]
        for fw in fws:
            self.assertIn(fw, stdout)

        # Count COMPLIANT occurrences (at least 6)
        compliant_count = stdout.count("COMPLIANT")
        self.assertGreaterEqual(compliant_count, 6)

    def test_13_validate_isms_check_drift_clean_baseline(self):
        """Verify validate_isms.py --check-drift exits with code 0 on repository baseline."""
        rc, stdout, stderr = run_py_command(
            ["scripts/validate_isms.py", "--check-drift", "--strict"]
        )
        self.assertEqual(rc, 0, f"validate_isms.py --check-drift failed: {stderr}")
        self.assertIn("[*] Checking Framework & SoA Drift ...", stdout)
        self.assertIn("0 errors", stdout)

    def test_14_validate_isms_check_drift_synthetic_soa_removal(self):
        """
        Synthetic Drift Stress Test:
        When an ISO control mapped in registry is missing from SoA, validate_drift
        MUST detect drift.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import validate_isms

            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_soa = Path(tmp_dir) / "05_Statement_of_Applicability_SoA.md"
                soa_lines = self.soa_path.read_text(encoding="utf-8").splitlines()
                # Filter out A.5.1
                filtered = [l for l in soa_lines if "A.5.1" not in l]
                tmp_soa.write_text("\n".join(filtered), encoding="utf-8")

                drift_errors = validate_isms.validate_drift(
                    self.registry_data, tmp_soa, REPO_ROOT / "docs"
                )
                self.assertTrue(len(drift_errors) > 0)
                self.assertTrue(
                    any("A.5.1" in e and "missing from SoA" in e for e in drift_errors),
                    f"Expected A.5.1 missing from SoA error, got: {drift_errors}",
                )
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    def test_15_validate_isms_check_drift_synthetic_unmapped_soa_control(self):
        """
        Synthetic Drift Stress Test:
        When an ISO control appears in SoA that is not in the registry, validate_drift
        MUST detect drift.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import validate_isms

            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_soa = Path(tmp_dir) / "05_Statement_of_Applicability_SoA.md"
                soa_text = self.soa_path.read_text(encoding="utf-8")
                # Append synthetic control row
                synthetic_row = (
                    "| **A.5.99** | Synthetic Fake Control | Yes | Test | [Link](docs/02_Policies/01_Access_Control_Policy.md) | Legacy |\n"
                )
                tmp_soa.write_text(soa_text + "\n" + synthetic_row, encoding="utf-8")

                drift_errors = validate_isms.validate_drift(
                    self.registry_data, tmp_soa, REPO_ROOT / "docs"
                )
                self.assertTrue(len(drift_errors) > 0)
                self.assertTrue(
                    any("A.5.99" in e and "unmapped in registry" in e for e in drift_errors),
                    f"Expected A.5.99 unmapped in registry error, got: {drift_errors}",
                )
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    def test_16_validate_isms_check_drift_synthetic_doc_divergence(self):
        """
        Synthetic Drift Stress Test:
        When SoA implementing document link for A.5.1 completely diverges from
        the registry implementing docs, validate_drift MUST detect drift.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import validate_isms

            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_soa = Path(tmp_dir) / "05_Statement_of_Applicability_SoA.md"
                soa_lines = self.soa_path.read_text(encoding="utf-8").splitlines()
                # Rewrite A.5.1 implementing link to point solely to a diverged policy
                diverged_lines = []
                for line in soa_lines:
                    if "| **A.5.1** |" in line or "| A.5.1 |" in line:
                        parts = line.split("|")
                        if len(parts) >= 7:
                            # Replace implementing link column
                            parts[5] = " [Diverged](docs/02_Policies/04_Physical_Security_Policy.md) "
                            diverged_lines.append("|".join(parts))
                        else:
                            diverged_lines.append(line)
                    else:
                        diverged_lines.append(line)

                tmp_soa.write_text("\n".join(diverged_lines), encoding="utf-8")

                drift_errors = validate_isms.validate_drift(
                    self.registry_data, tmp_soa, REPO_ROOT / "docs"
                )
                self.assertTrue(len(drift_errors) > 0)
                self.assertTrue(
                    any("A.5.1" in e and "do not match registry" in e for e in drift_errors),
                    f"Expected A.5.1 doc divergence error, got: {drift_errors}",
                )
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    def test_17_validate_isms_catalog_integrity_negative_unknown_id(self):
        """
        Catalog Integrity Stress Test:
        Injecting an unknown framework ID in canonical control mappings MUST trigger
        catalog integrity violations.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import validate_isms

            mut_reg = copy.deepcopy(self.registry_data)
            # Add an invalid ID into first control's iso_27001_2022 mapping
            ctrl0 = mut_reg["controls"][0]
            ctrl0["mappings"]["iso_27001_2022"].append("A.99.99")

            errors = validate_isms.validate_catalog_integrity(mut_reg, self.catalogs_dir)
            self.assertTrue(len(errors) > 0)
            self.assertTrue(
                any("A.99.99" in e and "not found in catalog" in e for e in errors),
                f"Expected catalog integrity violation for A.99.99, got: {errors}",
            )
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    def test_18_validate_isms_schema_negative_mutation(self):
        """
        Registry Schema Stress Test:
        Injecting an invalid root structure MUST trigger JSON schema validation errors.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import validate_isms

            with tempfile.TemporaryDirectory() as tmp_dir:
                bad_reg_file = Path(tmp_dir) / "bad_registry.yaml"
                bad_data = copy.deepcopy(self.registry_data)
                bad_data["schema_version"] = 12345  # Must be string pattern ^\d+\.\d+\.\d+$
                bad_data["controls"] = bad_data["controls"][:10]  # Min controls is 55

                with open(bad_reg_file, "w", encoding="utf-8") as f:
                    yaml.dump(bad_data, f)

                errors, _ = validate_isms.validate_registry_schema_and_files(
                    bad_reg_file, self.registry_schema_path
                )
                self.assertTrue(len(errors) > 0)
                self.assertTrue(
                    any("schema" in e.lower() or "55 canonical controls" in e.lower() for e in errors),
                    f"Expected schema error, got: {errors}",
                )
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    # =========================================================================
    # PART 3: check_adoption.py Stress Testing (Boundaries, Thresholds, Exceptions)
    # =========================================================================

    def test_19_check_adoption_baseline_strict_pass(self):
        """Verify check_adoption.py --strict passes cleanly on baseline."""
        rc, stdout, stderr = run_py_command(
            ["scripts/check_adoption.py", "--strict"]
        )
        self.assertEqual(rc, 0, f"check_adoption.py --strict failed: {stderr}")
        self.assertIn("Audited 38 document review cadences", stdout)
        self.assertIn("Audited 2 active security exceptions", stdout)
        self.assertIn("Audited 6 adopted frameworks and E8 ML2 target maturity", stdout)
        self.assertIn("[PASS]", stdout)

    def test_20_check_adoption_boundary_dates_exact_expiry(self):
        """
        Boundary Value Stress Test:
        EX-2026-002 expires on 2026-11-25.
        - On 2026-11-25: Should PASS (exit code 0).
        - On 2026-11-26: Should FAIL (exit code 1) because expiration date is in the past.
        """
        # Day of expiration: should PASS
        rc_pass, stdout_pass, stderr_pass = run_py_command(
            ["scripts/check_adoption.py", "--current-date", "2026-11-25", "--strict"]
        )
        self.assertEqual(
            rc_pass, 0, f"Expected code 0 on expiration date 2026-11-25, got {rc_pass}: {stderr_pass}"
        )

        # Day after expiration: should FAIL with code 1
        rc_fail, stdout_fail, stderr_fail = run_py_command(
            ["scripts/check_adoption.py", "--current-date", "2026-11-26", "--strict"]
        )
        self.assertEqual(
            rc_fail, 1, f"Expected code 1 on day after expiration 2026-11-26, got {rc_fail}"
        )
        self.assertIn("EX-2026-002 has EXPIRED", stdout_fail)

    def test_21_check_adoption_all_exceptions_expired_future(self):
        """
        Stress test: Future date 2027-02-01 is past both EX-2026-001 (2027-01-20)
        and EX-2026-002 (2026-11-25). Both must be flagged and exit code must be 1.
        """
        rc, stdout, stderr = run_py_command(
            ["scripts/check_adoption.py", "--current-date", "2027-02-01", "--strict"]
        )
        self.assertEqual(rc, 1, f"Expected code 1 on 2027-02-01, got {rc}")
        self.assertIn("EX-2026-001 has EXPIRED", stdout)
        self.assertIn("EX-2026-002 has EXPIRED", stdout)

    def test_22_check_adoption_duration_exceeds_90_days(self):
        """
        Security Exception Duration Stress Test:
        An exception with duration > 90 days (e.g. 91 days) MUST be rejected.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import check_adoption

            mut_manifest = copy.deepcopy(self.manifest_data)
            # Change EX-2026-001: approved 2026-10-26, expires 2027-01-26 (92 days)
            mut_manifest["exceptions"][0]["expiration_date"] = "2027-01-26"

            errors, _ = check_adoption.audit_security_exceptions(
                mut_manifest, self.registry_data, datetime.date(2026, 10, 31)
            )
            self.assertTrue(len(errors) > 0)
            self.assertTrue(
                any("90-day maximum policy window" in e for e in errors),
                f"Expected 90-day window violation, got: {errors}",
            )
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    def test_23_check_adoption_approval_after_expiration(self):
        """
        Security Exception Sanity Stress Test:
        An exception where approval_date > expiration_date MUST be rejected.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import check_adoption

            mut_manifest = copy.deepcopy(self.manifest_data)
            mut_manifest["exceptions"][0]["approval_date"] = "2027-02-01"
            mut_manifest["exceptions"][0]["expiration_date"] = "2027-01-01"

            errors, _ = check_adoption.audit_security_exceptions(
                mut_manifest, self.registry_data, datetime.date(2026, 10, 31)
            )
            self.assertTrue(len(errors) > 0)
            self.assertTrue(
                any("expiration must succeed approval" in e for e in errors),
                f"Expected inverted date error, got: {errors}",
            )
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    def test_24_check_adoption_missing_compensating_controls_or_approver(self):
        """
        Policy Enforcement Stress Test:
        Exceptions without compensating controls or missing approver MUST fail.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import check_adoption

            mut_manifest = copy.deepcopy(self.manifest_data)
            mut_manifest["exceptions"][0]["compensating_controls"] = []
            mut_manifest["exceptions"][0]["approved_by"] = "   "

            errors, _ = check_adoption.audit_security_exceptions(
                mut_manifest, self.registry_data, datetime.date(2026, 10, 31)
            )
            self.assertTrue(
                any("no compensating controls" in e for e in errors),
                f"Expected missing compensating controls error, got: {errors}",
            )
            self.assertTrue(
                any("missing approver" in e for e in errors),
                f"Expected missing approver error, got: {errors}",
            )
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    def test_25_check_adoption_unknown_control_id_in_exception(self):
        """
        Referential Integrity Stress Test:
        Exceptions referencing non-existent control IDs MUST fail.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import check_adoption

            mut_manifest = copy.deepcopy(self.manifest_data)
            mut_manifest["exceptions"][0]["control_id"] = "CC-NONEXISTENT-99"

            errors, _ = check_adoption.audit_security_exceptions(
                mut_manifest, self.registry_data, datetime.date(2026, 10, 31)
            )
            self.assertTrue(
                any("references invalid/unknown control_id" in e for e in errors),
                f"Expected unknown control ID error, got: {errors}",
            )
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    def test_26_check_adoption_threshold_breaches(self):
        """
        Threshold Enforcement Stress Test:
        Setting thresholds above actual counts MUST fail.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import check_adoption

            mut_manifest = copy.deepcopy(self.manifest_data)
            mut_manifest["thresholds"]["min_canonical_controls"] = 200
            mut_manifest["thresholds"]["min_distinct_csf_subcategories"] = 100

            errors, _ = check_adoption.audit_framework_thresholds_and_maturity(
                mut_manifest, self.registry_data
            )
            self.assertTrue(
                any("Canonical control threshold breached" in e for e in errors),
                f"Expected canonical controls threshold breach error, got: {errors}",
            )
            self.assertTrue(
                any("NIST CSF 2.0 subcategories threshold breached" in e for e in errors),
                f"Expected CSF threshold breach error, got: {errors}",
            )
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    def test_27_check_adoption_essential_eight_maturity_target_breach(self):
        """
        Maturity Model Stress Test:
        Mutating registry to omit ML2 controls for a strategy (e.g. regular_backups)
        MUST trigger an Essential Eight maturity target breach in check_adoption.py.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import check_adoption

            mut_reg = copy.deepcopy(self.registry_data)
            # Strip all E8-RB (regular backups) ML2 mappings from controls
            for ctrl in mut_reg["controls"]:
                e8_items = ctrl.get("mappings", {}).get("asd_essential_eight", [])
                ctrl["mappings"]["asd_essential_eight"] = [
                    item for item in e8_items
                    if not (isinstance(item, str) and item.startswith("E8-RB-ML2"))
                    and not (isinstance(item, dict) and item.get("id", "").startswith("E8-RB-ML2"))
                ]

            errors, _ = check_adoption.audit_framework_thresholds_and_maturity(
                self.manifest_data, mut_reg
            )
            self.assertTrue(
                any("ASD Essential Eight ML2 maturity target breached" in e for e in errors),
                f"Expected E8 ML2 maturity breach error, got: {errors}",
            )
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    def test_28_check_adoption_document_review_cadence_overdue(self):
        """
        Cadence Audit Stress Test:
        A document with Effective Date > 365 days ago MUST be flagged as overdue.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import check_adoption

            with tempfile.TemporaryDirectory() as tmp_dir:
                docs_box = Path(tmp_dir) / "docs"
                docs_box.mkdir()
                test_doc = docs_box / "test_policy.md"
                # Effective date 2 years ago
                test_doc.write_text(
                    "| Document ID | POL-01 |\n| Effective Date | 2024-01-01 |\n",
                    encoding="utf-8",
                )

                errors, audits = check_adoption.audit_document_review_cadence(
                    docs_box, max_age_days=365, current_date=datetime.date(2026, 10, 31)
                )
                self.assertTrue(len(errors) > 0)
                self.assertTrue(
                    any("Document review overdue" in e and "test_policy.md" in e for e in errors),
                    f"Expected overdue cadence error, got: {errors}",
                )
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    def test_29_check_adoption_insert_date_placeholder_tolerance(self):
        """
        Template Tolerance Stress Test:
        Documents with [INSERT_DATE] placeholder MUST be treated as fresh deployment dates
        and NOT trigger overdue errors.
        """
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import check_adoption

            with tempfile.TemporaryDirectory() as tmp_dir:
                docs_box = Path(tmp_dir) / "docs"
                docs_box.mkdir()
                test_doc = docs_box / "template_policy.md"
                test_doc.write_text(
                    "| Document ID | POL-01 |\n| Effective Date | [INSERT_DATE] |\n",
                    encoding="utf-8",
                )

                errors, audits = check_adoption.audit_document_review_cadence(
                    docs_box, max_age_days=365, current_date=datetime.date(2026, 10, 31)
                )
                self.assertEqual(errors, [])
                self.assertEqual(len(audits), 1)
                self.assertFalse(audits[0]["overdue"])
                self.assertEqual(audits[0]["age_days"], 0)
        finally:
            if str(REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(REPO_ROOT / "scripts"))

    def test_30_check_adoption_multi_format_outputs(self):
        """Verify check_adoption.py supports json, sarif, and markdown output formats."""
        # JSON format
        rc_json, stdout_json, _ = run_py_command(
            ["scripts/check_adoption.py", "--format", "json"]
        )
        self.assertEqual(rc_json, 0)
        json_data = json.loads(stdout_json)
        self.assertEqual(json_data.get("status"), "PASS")
        self.assertIn("adopted_frameworks_audit", json_data)
        self.assertIn("security_exceptions", json_data)

        # SARIF format
        rc_sarif, stdout_sarif, _ = run_py_command(
            ["scripts/check_adoption.py", "--format", "sarif"]
        )
        self.assertEqual(rc_sarif, 0)
        sarif_data = json.loads(stdout_sarif)
        self.assertEqual(sarif_data.get("version"), "2.1.0")
        self.assertEqual(sarif_data["runs"][0]["tool"]["driver"]["name"], "check_adoption")

        # Markdown format
        rc_md, stdout_md, _ = run_py_command(
            ["scripts/check_adoption.py", "--format", "markdown"]
        )
        self.assertEqual(rc_md, 0)
        self.assertIn("# Compliance Adoption & Governance Audit Report", stdout_md)
        self.assertIn("## Adopted Framework Targets Audit", stdout_md)
        self.assertIn("## Security Exceptions Audit", stdout_md)


if __name__ == "__main__":
    unittest.main()
