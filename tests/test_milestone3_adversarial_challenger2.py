#!/usr/bin/env python3
"""
Milestone 3 Independent Adversarial Challenger Test Suite
Agent: challenger_v2_m3_2 (Role: teamwork_preview_challenger)
Target: Milestone 3 Deliverables
  1. Deep OSCAL Schema Mutation Stress Testing:
     - All 5 generated OSCAL v1.2.0 models (catalog, mapping_collection, profile_e8_ml2,
       profile_nist_800_53_moderate, component_definition) validated against schemas/oscal_v1_2_0_subset.schema.json.
     - Adversarial mutations: root UUIDv5 corruption, metadata omission, invalid oscal-version,
       missing required groups/imports/components/mappings, empty arrays violating minItems: 1,
       illegal relationship semantics, forbidden additionalProperties, and oneOf violations.
     - CLI corruption detection via export_oscal.py --check.
  2. Reference Catalog Integrity & Mutation Stress Testing:
     - Missing reference catalog files (iso_27001_2022, asd_essential_eight, nist_sp_800_53_rev5, etc.).
     - Unmapped/invalid control IDs injected into registry (A.5.999, E8-XX-ML9, ZZ-99, CC9.99, XX.YY-99, Article 999).
     - Deletion of an actively mapped control from authoritative catalog.
     - Corrupted catalog YAML syntax handling.
  3. SARIF v2.1.0 Schema Conformance:
     - Structural and schema validation against OASIS SARIF v2.1.0 JSON Schema.
     - Conformance under both clean baseline runs and simulated violation runs for both
       validate_isms.py --format sarif and check_adoption.py --format sarif.
     - Complete rule descriptor integrity (ISMS001-ISMS007 and ADOPT001-ADOPT007).
  4. Markdown Table Structure and Syntax:
     - GitHub-Flavored Markdown (GFM) table syntax, column count alignment, delimiter syntax,
       and status reporting under clean and violation modes for both CLIs.
"""

import copy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional
import unittest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def get_python() -> str:
    local_venv = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    if local_venv.exists():
        return str(local_venv)
    return sys.executable


class TestOscalDeepSchemaMutation(unittest.TestCase):
    """Deep schema mutation testing against generated OSCAL JSON models."""

    @classmethod
    def setUpClass(cls):
        cls.schema_path = REPO_ROOT / "schemas" / "oscal_v1_2_0_subset.schema.json"
        assert cls.schema_path.exists(), f"Missing OSCAL schema: {cls.schema_path}"
        with open(cls.schema_path, "r", encoding="utf-8") as f:
            cls.oscal_schema = json.load(f)

        import jsonschema

        # Prepare Draft 2020-12 schema with root properties hoisted from oneOf branches
        schema_copy = copy.deepcopy(cls.oscal_schema)
        if "properties" not in schema_copy and "oneOf" in schema_copy:
            root_props = {}
            for branch in schema_copy["oneOf"]:
                root_props.update(branch.get("properties", {}))
            schema_copy["properties"] = root_props

        cls.validator_cls = jsonschema.validators.validator_for(schema_copy)
        cls.validator_cls.check_schema(schema_copy)
        cls.validator = cls.validator_cls(schema_copy)

        cls.oscal_dir = REPO_ROOT / "dist" / "oscal"
        cls.expected_models = [
            "catalog.json",
            "mapping_collection.json",
            "profile_e8_ml2.json",
            "profile_nist_800_53_moderate.json",
            "component_definition.json",
        ]

    def test_baseline_oscal_models_valid(self):
        """All 5 generated OSCAL models in dist/oscal must pass strict schema validation."""
        self.assertTrue(self.oscal_dir.exists(), f"OSCAL directory missing: {self.oscal_dir}")
        for filename in self.expected_models:
            model_file = self.oscal_dir / filename
            self.assertTrue(model_file.exists(), f"OSCAL model missing: {filename}")
            with open(model_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            errors = list(self.validator.iter_errors(data))
            self.assertEqual(len(errors), 0, f"{filename} schema errors: {[e.message for e in errors]}")

    def test_oscal_metadata_mutations(self):
        """Metadata mutations (missing required keys, invalid oscal-version) must fail validation."""
        cat_file = self.oscal_dir / "catalog.json"
        with open(cat_file, "r", encoding="utf-8") as f:
            base_data = json.load(f)

        # 1. Missing title in metadata
        mutated = copy.deepcopy(base_data)
        del mutated["catalog"]["metadata"]["title"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Removing metadata.title must fail validation")

        # 2. Missing last-modified in metadata
        mutated = copy.deepcopy(base_data)
        del mutated["catalog"]["metadata"]["last-modified"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Removing metadata.last-modified must fail validation")

        # 3. Invalid oscal-version (must be const '1.2.0')
        mutated = copy.deepcopy(base_data)
        mutated["catalog"]["metadata"]["oscal-version"] = "1.0.0"
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Mutating oscal-version to 1.0.0 must fail validation")

        mutated["catalog"]["metadata"]["oscal-version"] = "2.0.0"
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Mutating oscal-version to 2.0.0 must fail validation")

    def test_oscal_catalog_deep_mutations(self):
        """Catalog model mutations (corrupted UUIDv5, missing groups, extra properties) must fail."""
        cat_file = self.oscal_dir / "catalog.json"
        with open(cat_file, "r", encoding="utf-8") as f:
            base_data = json.load(f)

        # 1. Missing root uuid
        mutated = copy.deepcopy(base_data)
        del mutated["catalog"]["uuid"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Removing catalog.uuid must fail validation")

        # 2. Corrupted UUID format (not RFC 4122 UUIDv5)
        mutated = copy.deepcopy(base_data)
        mutated["catalog"]["uuid"] = "not-a-valid-uuid-format"
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Non-UUID string must fail validation")

        # UUID with wrong version (version 4 instead of 5: e.g. -4xxx-)
        mutated = copy.deepcopy(base_data)
        valid_uuid = mutated["catalog"]["uuid"]
        v4_uuid = valid_uuid[:14] + "4" + valid_uuid[15:]
        mutated["catalog"]["uuid"] = v4_uuid
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "UUIDv4 must fail UUIDv5-specific schema pattern")

        # 3. Missing groups
        mutated = copy.deepcopy(base_data)
        del mutated["catalog"]["groups"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Removing catalog.groups must fail validation")

        # 4. Group missing required 'controls'
        mutated = copy.deepcopy(base_data)
        del mutated["catalog"]["groups"][0]["controls"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Removing group.controls must fail validation")

        # 5. Group control missing required 'id'
        mutated = copy.deepcopy(base_data)
        del mutated["catalog"]["groups"][0]["controls"][0]["id"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Removing control.id must fail validation")

        # 6. Forbidden additionalProperties on catalog root
        mutated = copy.deepcopy(base_data)
        mutated["catalog"]["forbidden_extra_property"] = "hostile_injection"
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Catalog additionalProperties must fail validation")

    def test_oscal_profile_deep_mutations(self):
        """Profile mutations (empty imports, missing href, oneOf violation) must fail."""
        prof_file = self.oscal_dir / "profile_e8_ml2.json"
        with open(prof_file, "r", encoding="utf-8") as f:
            base_data = json.load(f)

        # 1. Missing imports
        mutated = copy.deepcopy(base_data)
        del mutated["profile"]["imports"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Removing profile.imports must fail validation")

        # 2. Empty imports array (minItems: 1)
        mutated = copy.deepcopy(base_data)
        mutated["profile"]["imports"] = []
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Empty profile.imports must fail minItems: 1")

        # 3. Import item missing href
        mutated = copy.deepcopy(base_data)
        del mutated["profile"]["imports"][0]["href"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Import item missing href must fail validation")

        # 4. Multi-root oneOf violation (combining catalog and profile)
        mutated = copy.deepcopy(base_data)
        mutated["catalog"] = {"uuid": mutated["profile"]["uuid"], "metadata": mutated["profile"]["metadata"], "groups": []}
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Combining catalog and profile must violate oneOf")

    def test_oscal_component_definition_deep_mutations(self):
        """Component definition mutations (empty components, missing fields) must fail."""
        comp_file = self.oscal_dir / "component_definition.json"
        with open(comp_file, "r", encoding="utf-8") as f:
            base_data = json.load(f)

        # 1. Missing components
        mutated = copy.deepcopy(base_data)
        del mutated["component-definition"]["components"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Removing components must fail validation")

        # 2. Empty components array (minItems: 1)
        mutated = copy.deepcopy(base_data)
        mutated["component-definition"]["components"] = []
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Empty components array must fail minItems: 1")

        # 3. Component missing description
        mutated = copy.deepcopy(base_data)
        del mutated["component-definition"]["components"][0]["description"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Component missing description must fail validation")

        # 4. Component missing type
        mutated = copy.deepcopy(base_data)
        del mutated["component-definition"]["components"][0]["type"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Component missing type must fail validation")

    def test_oscal_mapping_collection_deep_mutations(self):
        """Mapping collection mutations (missing fields, corrupted types) must fail."""
        map_file = self.oscal_dir / "mapping_collection.json"
        with open(map_file, "r", encoding="utf-8") as f:
            base_data = json.load(f)

        # 1. Missing mappings root key
        mutated = copy.deepcopy(base_data)
        del mutated["mapping-collection"]["mappings"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Removing mappings must fail validation")

        # 2. Mapping item missing target_control_id
        mutated = copy.deepcopy(base_data)
        del mutated["mapping-collection"]["mappings"][0]["target_control_id"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Missing target_control_id must fail validation")

        # 3. Mapping item missing source_control_id
        mutated = copy.deepcopy(base_data)
        del mutated["mapping-collection"]["mappings"][0]["source_control_id"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Missing source_control_id must fail validation")

        # 4. Mapping item missing target_framework
        mutated = copy.deepcopy(base_data)
        del mutated["mapping-collection"]["mappings"][0]["target_framework"]
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Missing target_framework must fail validation")

        # 5. Relationship corrupted to non-string type
        mutated = copy.deepcopy(base_data)
        mutated["mapping-collection"]["mappings"][0]["relationship"] = 12345
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Integer relationship must fail string type validation")

        # 6. Additional forbidden property on mapping-collection root
        mutated = copy.deepcopy(base_data)
        mutated["mapping-collection"]["forbidden_prop"] = True
        errors = list(self.validator.iter_errors(mutated))
        self.assertGreater(len(errors), 0, "Forbidden additionalProperties must fail")

    def test_export_oscal_check_cli_drift_detection(self):
        """export_oscal.py --check must catch single-byte drift and missing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            # Copy baseline oscal models to tmpdir
            for f in self.expected_models:
                shutil.copy2(self.oscal_dir / f, tmp_path / f)

            # 1. Baseline check should pass
            cmd_base = [get_python(), "scripts/export_oscal.py", "--output-dir", str(tmp_path), "--check"]
            p_base = subprocess.run(cmd_base, cwd=REPO_ROOT, capture_output=True, text=True)
            self.assertEqual(p_base.returncode, 0, f"Baseline check failed: {p_base.stdout}\n{p_base.stderr}")

            # 2. Mutate a single byte in catalog.json
            cat_copy = tmp_path / "catalog.json"
            with open(cat_copy, "r+", encoding="utf-8") as f:
                content = f.read()
                mutated_content = content.replace("Canonical", "Mutated-Canonical", 1)
                f.seek(0)
                f.write(mutated_content)
                f.truncate()

            p_drift = subprocess.run(cmd_base, cwd=REPO_ROOT, capture_output=True, text=True)
            self.assertNotEqual(p_drift.returncode, 0, "Mutated catalog.json must trigger non-zero exit in --check")
            self.assertIn("differs", p_drift.stdout + p_drift.stderr)

            # 3. Delete a model file
            prof_copy = tmp_path / "profile_e8_ml2.json"
            prof_copy.unlink()
            p_missing = subprocess.run(cmd_base, cwd=REPO_ROOT, capture_output=True, text=True)
            self.assertNotEqual(p_missing.returncode, 0, "Missing profile file must trigger non-zero exit in --check")


class TestCatalogIntegrityAndDriftMutations(unittest.TestCase):
    """Adversarial mutation testing on reference catalogs and catalog verification logic."""

    @classmethod
    def setUpClass(cls):
        cls.catalogs_dir = REPO_ROOT / "mappings" / "catalogs"
        cls.registry_path = REPO_ROOT / "mappings" / "framework_registry.yaml"
        assert cls.catalogs_dir.exists(), f"Catalogs dir missing: {cls.catalogs_dir}"
        assert cls.registry_path.exists(), f"Registry path missing: {cls.registry_path}"

    def test_missing_individual_catalogs_rejected(self):
        """validate_isms.py must exit with non-zero code if any reference catalog is missing."""
        catalogs = [
            "iso_27001_2022.yaml",
            "soc2_tsc_2017.yaml",
            "nist_csf_2_0.yaml",
            "gdpr.yaml",
            "nist_sp_800_53_rev5.yaml",
            "asd_essential_eight.yaml",
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_cat_dir = Path(tmpdir)
            # Copy all catalogs
            for c in catalogs:
                shutil.copy2(self.catalogs_dir / c, tmp_cat_dir / c)

            # Test removing each catalog individually
            for target_cat in ["iso_27001_2022.yaml", "asd_essential_eight.yaml", "nist_sp_800_53_rev5.yaml"]:
                target_file = tmp_cat_dir / target_cat
                target_file.unlink()

                cmd = [
                    get_python(),
                    "scripts/validate_isms.py",
                    "--catalogs-dir",
                    str(tmp_cat_dir),
                    "--format",
                    "text",
                ]
                proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
                self.assertNotEqual(
                    proc.returncode,
                    0,
                    f"validate_isms.py must fail when catalog {target_cat} is missing",
                )
                output = proc.stdout + proc.stderr
                self.assertTrue(
                    "Catalog file missing" in output or "maps unknown" in output,
                    f"Expected missing catalog or unknown ID message, got: {output}",
                )

                # Restore for next test iteration
                shutil.copy2(self.catalogs_dir / target_cat, target_file)

    def test_catalog_invalid_control_ids_in_registry(self):
        """validate_isms.py must exit with code 1 when registry contains fictitious control IDs."""
        with open(self.registry_path, "r", encoding="utf-8") as f:
            registry_data = yaml.safe_load(f)

        test_cases = [
            ("iso_27001_2022", "A.5.999", "iso_27001_2022.yaml"),
            ("asd_essential_eight", "E8-XX-ML9", "asd_essential_eight.yaml"),
            ("nist_sp_800_53_rev5", "ZZ-99", "nist_sp_800_53_rev5.yaml"),
            ("soc2_tsc_2017", "CC9.99", "soc2_tsc_2017.yaml"),
            ("nist_csf_2_0", "XX.YY-99", "nist_csf_2_0.yaml"),
            ("gdpr_articles", "Article 999", "gdpr.yaml"),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_reg_path = Path(tmpdir) / "framework_registry.yaml"

            for reg_key, fake_id, cat_name in test_cases:
                mutated = copy.deepcopy(registry_data)
                ctrls = mutated.get("controls") or mutated.get("canonical_controls", [])
                self.assertGreater(len(ctrls), 0)

                # Inject fake control into first canonical control's mappings
                mappings = ctrls[0].setdefault("mappings", {})
                current = mappings.get(reg_key, [])
                if isinstance(current, list):
                    mappings[reg_key] = current + [fake_id]
                else:
                    mappings[reg_key] = [fake_id]

                with open(tmp_reg_path, "w", encoding="utf-8") as f:
                    yaml.dump(mutated, f)

                cmd = [
                    get_python(),
                    "scripts/validate_isms.py",
                    "--registry",
                    str(tmp_reg_path),
                    "--format",
                    "text",
                ]
                proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
                self.assertNotEqual(
                    proc.returncode,
                    0,
                    f"validate_isms.py must fail when fake ID {fake_id} is mapped for {reg_key}",
                )
                output = proc.stdout + proc.stderr
                self.assertIn(
                    fake_id,
                    output,
                    f"Error output must mention the invalid control ID '{fake_id}'",
                )

    def test_catalog_removed_active_control(self):
        """Removing an actively mapped control from a catalog must trigger validation failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_cat_dir = Path(tmpdir)
            for c in self.catalogs_dir.glob("*.yaml"):
                shutil.copy2(c, tmp_cat_dir / c.name)

            # Mutate iso_27001_2022.yaml to remove A.5.1
            iso_cat_file = tmp_cat_dir / "iso_27001_2022.yaml"
            with open(iso_cat_file, "r", encoding="utf-8") as f:
                cat_data = yaml.safe_load(f)

            cat_data["controls"] = [c for c in cat_data["controls"] if c["id"] != "A.5.1"]
            with open(iso_cat_file, "w", encoding="utf-8") as f:
                yaml.dump(cat_data, f)

            cmd = [
                get_python(),
                "scripts/validate_isms.py",
                "--catalogs-dir",
                str(tmp_cat_dir),
                "--format",
                "text",
            ]
            proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0, "Removing mapped control A.5.1 from catalog must fail validation")
            output = proc.stdout + proc.stderr
            self.assertIn("A.5.1", output)

    def test_corrupted_catalog_file_syntax(self):
        """Corrupted YAML syntax in any catalog file must cause validation failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_cat_dir = Path(tmpdir)
            for c in self.catalogs_dir.glob("*.yaml"):
                shutil.copy2(c, tmp_cat_dir / c.name)

            # Write broken YAML syntax
            bad_cat = tmp_cat_dir / "gdpr.yaml"
            with open(bad_cat, "w", encoding="utf-8") as f:
                f.write("controls:\n  - id: Article 5\n    title: [broken unclosed array\n")

            cmd = [
                get_python(),
                "scripts/validate_isms.py",
                "--catalogs-dir",
                str(tmp_cat_dir),
                "--format",
                "text",
            ]
            proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0, "Corrupted catalog syntax must trigger failure")


class TestSarifSchemaConformance(unittest.TestCase):
    """Validation of SARIF v2.1.0 output against the OASIS SARIF v2.1.0 specification."""

    @classmethod
    def setUpClass(cls):
        cls.sarif_schema_path = REPO_ROOT / "tests" / "fixtures" / "sarif-schema-2.1.0.json"
        assert cls.sarif_schema_path.exists(), f"SARIF schema missing: {cls.sarif_schema_path}"
        with open(cls.sarif_schema_path, "r", encoding="utf-8") as f:
            cls.sarif_schema = json.load(f)

        import jsonschema
        cls.validator = jsonschema.Draft4Validator(cls.sarif_schema)

    def _assert_valid_sarif(self, payload: Dict[str, Any], expected_tool_name: str, expected_rule_prefix: str):
        """Assert strict schema validity and structural compliance of a SARIF payload."""
        errors = list(self.validator.iter_errors(payload))
        self.assertEqual(len(errors), 0, f"SARIF schema validation errors: {[e.message for e in errors]}")

        # Strict SARIF v2.1.0 invariant checks
        self.assertEqual(payload.get("version"), "2.1.0")
        self.assertIn("sarif-schema-2.1.0.json", payload.get("$schema", ""))
        self.assertIn("runs", payload)
        self.assertGreater(len(payload["runs"]), 0)

        run = payload["runs"][0]
        self.assertIn("tool", run)
        driver = run["tool"]["driver"]
        self.assertEqual(driver.get("name"), expected_tool_name)
        self.assertEqual(driver.get("version"), "2.0.0")

        rules = driver.get("rules", [])
        self.assertGreater(len(rules), 0)
        rule_ids = set()
        for r in rules:
            self.assertTrue(r["id"].startswith(expected_rule_prefix))
            self.assertIn("name", r)
            self.assertIn("text", r.get("shortDescription", {}))
            rule_ids.add(r["id"])

        results = run.get("results", [])
        for res in results:
            self.assertIn("ruleId", res)
            self.assertIn(res["ruleId"], rule_ids, f"Result ruleId '{res['ruleId']}' must be declared in driver.rules")
            self.assertEqual(res.get("level"), "error")
            self.assertIn("text", res.get("message", {}))
            locations = res.get("locations", [])
            self.assertGreater(len(locations), 0)
            phys = locations[0]["physicalLocation"]
            self.assertTrue(phys["artifactLocation"]["uri"])
            self.assertGreaterEqual(phys["region"]["startLine"], 1)

    def test_validate_isms_sarif_clean_and_schema_valid(self):
        """validate_isms.py --format sarif on clean repo must pass SARIF v2.1.0 validation."""
        cmd = [get_python(), "scripts/validate_isms.py", "--format", "sarif"]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)

        payload = json.loads(proc.stdout)
        self._assert_valid_sarif(payload, expected_tool_name="validate_isms", expected_rule_prefix="ISMS")
        self.assertEqual(len(payload["runs"][0]["results"]), 0)

    def test_validate_isms_sarif_with_violations_schema_valid(self):
        """validate_isms.py --format sarif with injected violations must produce valid SARIF."""
        cmd = [get_python(), "scripts/validate_isms.py", "--config", "nonexistent_config.yml", "--format", "sarif"]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)

        payload = json.loads(proc.stdout)
        self._assert_valid_sarif(payload, expected_tool_name="validate_isms", expected_rule_prefix="ISMS")
        results = payload["runs"][0]["results"]
        self.assertGreater(len(results), 0)
        self.assertTrue(any(r["ruleId"].startswith("ISMS") for r in results))

    def test_check_adoption_sarif_clean_and_schema_valid(self):
        """check_adoption.py --format sarif on clean repo must pass SARIF v2.1.0 validation."""
        cmd = [get_python(), "scripts/check_adoption.py", "--manifest", "mappings/compliance_manifest.yaml", "--format", "sarif"]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)

        payload = json.loads(proc.stdout)
        self._assert_valid_sarif(payload, expected_tool_name="check_adoption", expected_rule_prefix="ADOPT")
        self.assertEqual(len(payload["runs"][0]["results"]), 0)

    def test_check_adoption_sarif_with_expired_exception_schema_valid(self):
        """check_adoption.py --format sarif with simulated future date must output valid SARIF results."""
        cmd = [
            get_python(),
            "scripts/check_adoption.py",
            "--manifest",
            "mappings/compliance_manifest.yaml",
            "--current-date",
            "2027-02-01",
            "--format",
            "sarif",
        ]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)

        payload = json.loads(proc.stdout)
        self._assert_valid_sarif(payload, expected_tool_name="check_adoption", expected_rule_prefix="ADOPT")
        results = payload["runs"][0]["results"]
        self.assertGreater(len(results), 0)
        self.assertTrue(any(r["ruleId"] == "ADOPT005" for r in results), "Must flag ADOPT005 for expired exception")


class TestMarkdownReportStructureAndSyntax(unittest.TestCase):
    """Validation of Markdown report structure, GFM table formatting, and syntax."""

    def _parse_and_validate_gfm_tables(self, md_text: str) -> List[Dict[str, Any]]:
        """Extract and validate all GFM tables in markdown content."""
        lines = md_text.splitlines()
        tables = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Check for table header candidate
            if line.startswith("|") and line.endswith("|") and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # Check delimiter row
                if next_line.startswith("|") and next_line.endswith("|") and re.match(r"^\|(\s*:?-+:?\s*\|)+$", next_line):
                    header_cells = [c.strip() for c in line.split("|")[1:-1]]
                    delim_cells = [c.strip() for c in next_line.split("|")[1:-1]]
                    col_count = len(header_cells)
                    self.assertEqual(len(delim_cells), col_count, f"Delimiter column count mismatch at line {i+2}")

                    rows = []
                    row_idx = i + 2
                    while row_idx < len(lines) and lines[row_idx].strip().startswith("|") and lines[row_idx].strip().endswith("|"):
                        data_line = lines[row_idx].strip()
                        data_cells = [c.strip() for c in data_line.split("|")[1:-1]]
                        self.assertEqual(
                            len(data_cells),
                            col_count,
                            f"Table row at line {row_idx+1} has {len(data_cells)} columns, expected {col_count}",
                        )
                        rows.append(data_cells)
                        row_idx += 1

                    tables.append({
                        "header": header_cells,
                        "columns": col_count,
                        "rows": rows,
                    })
                    i = row_idx
                    continue
            i += 1
        return tables

    def test_validate_isms_markdown_clean_structure(self):
        """validate_isms.py --format markdown on clean repo must generate valid GFM report."""
        cmd = [get_python(), "scripts/validate_isms.py", "--format", "markdown"]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)

        md = proc.stdout
        self.assertTrue(md.startswith("# ISMS Framework Compliance & Integrity Validation Report"))
        self.assertIn("- **Status**: `PASS`", md)
        self.assertIn("- **Total Canonical Controls**: 98", md)
        self.assertIn("- **Total Violations**: 0", md)
        self.assertIn("[PASS] Zero validation violations detected", md)

        tables = self._parse_and_validate_gfm_tables(md)
        self.assertEqual(len(tables), 1, "Expected exactly 1 coverage table in validate_isms markdown")
        cov_table = tables[0]
        self.assertEqual(cov_table["header"], ["Framework / Standard", "Version", "Mapped / Benchmark", "Coverage %", "Status"])
        self.assertEqual(len(cov_table["rows"]), 6, "Must contain all 6 frameworks in coverage table")
        for row in cov_table["rows"]:
            self.assertEqual(row[4], "COMPLIANT", f"Framework {row[0]} not marked COMPLIANT")

    def test_validate_isms_markdown_violations_structure(self):
        """validate_isms.py --format markdown with violations must format violations section cleanly."""
        cmd = [get_python(), "scripts/validate_isms.py", "--config", "nonexistent.yml", "--format", "markdown"]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)

        md = proc.stdout
        self.assertIn("- **Status**: `FAIL`", md)
        self.assertIn("## Violations Detected", md)
        self.assertIn("- [FAIL]", md)

    def test_check_adoption_markdown_clean_structure(self):
        """check_adoption.py --format markdown on clean repo must generate 2 valid GFM tables."""
        cmd = [
            get_python(),
            "scripts/check_adoption.py",
            "--manifest",
            "mappings/compliance_manifest.yaml",
            "--format",
            "markdown",
        ]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)

        md = proc.stdout
        self.assertTrue(md.startswith("# Compliance Adoption & Governance Audit Report"))
        self.assertIn("- **Audit Status**: `PASS`", md)
        self.assertIn("- **Total Violations**: 0", md)
        self.assertIn("[PASS] All adoption policies, review cadences, and time-bound exceptions are fully compliant.", md)

        tables = self._parse_and_validate_gfm_tables(md)
        self.assertEqual(len(tables), 2, "Expected exactly 2 tables in check_adoption markdown")

        # Table 1: Adopted Frameworks Audit
        t1 = tables[0]
        self.assertEqual(t1["header"], ["Framework ID", "Target Metric", "Achieved / Target", "Status"])
        self.assertEqual(len(t1["rows"]), 6)
        for r in t1["rows"]:
            self.assertEqual(r[3], "COMPLIANT")

        # Table 2: Security Exceptions Audit
        t2 = tables[1]
        self.assertEqual(t2["header"], ["Exception ID", "Control ID", "Approval Date", "Expiry Date", "Duration", "Days Left", "Status"])
        self.assertEqual(len(t2["rows"]), 2)
        for r in t2["rows"]:
            self.assertEqual(r[6], "ACTIVE")

    def test_check_adoption_markdown_violations_structure(self):
        """check_adoption.py --format markdown with expired exceptions must show EXPIRED status."""
        cmd = [
            get_python(),
            "scripts/check_adoption.py",
            "--manifest",
            "mappings/compliance_manifest.yaml",
            "--current-date",
            "2027-02-01",
            "--format",
            "markdown",
        ]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)

        md = proc.stdout
        self.assertIn("- **Audit Status**: `FAIL`", md)
        self.assertIn("## Violations Detected", md)
        self.assertIn("- [FAIL]", md)
        self.assertIn("EXPIRED", md)

        tables = self._parse_and_validate_gfm_tables(md)
        self.assertEqual(len(tables), 2)
        ex_table = tables[1]
        for r in ex_table["rows"]:
            self.assertEqual(r[6], "EXPIRED", "All exceptions should be marked EXPIRED on 2027-02-01")


if __name__ == "__main__":
    unittest.main()
