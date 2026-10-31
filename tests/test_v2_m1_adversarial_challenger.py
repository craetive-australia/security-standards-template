#!/usr/bin/env python3
"""
tests/test_v2_m1_adversarial_challenger.py
Adversarial Stress Test Suite for Milestone 1 Deliverables:
- JSON Schemas (Draft 2020-12) validation and negative mutation attacks
- Authoritative reference catalogs (ID uniqueness, exact counts, category/family distributions)
- Compliance manifest bounds and exception window logic (<= 90 days, non-negative, non-expired)
- Workspace hygiene (zero serve_*.txt, gitignore coverage, LICENSE, ADR placement)
"""

import copy
import glob
import json
import re
import unittest
from datetime import datetime
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

# Optional official jsonschema import
try:
    import jsonschema
    from jsonschema.validators import Draft202012Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def resolve_schema_ref(root_schema: dict, ref: str) -> dict:
    """Resolve local JSON Pointer like '#/$defs/catalogEntry'."""
    if not ref.startswith("#/"):
        raise ValueError(f"Only local refs supported: {ref}")
    parts = ref.lstrip("#/").split("/")
    curr = root_schema
    for p in parts:
        curr = curr[p]
    return curr


def naive_validate(root_schema: dict, schema: dict, data, path: str = "root"):
    """
    Fallback structural validator when jsonschema is not installed in the local environment.
    Checks types, required fields, enum constraints, patterns, min/max bounds, refs, and additionalProperties.
    """
    if "$ref" in schema:
        resolved = resolve_schema_ref(root_schema, schema["$ref"])
        naive_validate(root_schema, resolved, data, path)
        return

    if "oneOf" in schema:
        passed = 0
        for branch in schema["oneOf"]:
            try:
                naive_validate(root_schema, branch, data, path)
                passed += 1
            except AssertionError:
                pass
        if passed != 1:
            raise AssertionError(f"[{path}] Expected exactly 1 oneOf match, got {passed}")
        return

    schema_type = schema.get("type")
    if schema_type == "object":
        if not isinstance(data, dict):
            raise AssertionError(f"[{path}] Expected object, got {type(data).__name__}")
        required = schema.get("required", [])
        for req in required:
            if req not in data:
                raise AssertionError(f"[{path}] Missing required property: {req}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            allowed = set(properties.keys())
            extra = set(data.keys()) - allowed
            if extra:
                raise AssertionError(f"[{path}] Forbidden additional properties: {extra}")
        for k, v in data.items():
            if k in properties:
                sub_schema = properties[k]
                naive_validate(root_schema, sub_schema, v, f"{path}.{k}")
    elif schema_type == "array":
        if not isinstance(data, list):
            raise AssertionError(f"[{path}] Expected array, got {type(data).__name__}")
        min_items = schema.get("minItems")
        if min_items is not None and len(data) < min_items:
            raise AssertionError(f"[{path}] Array has {len(data)} items, minimum is {min_items}")
        items_schema = schema.get("items")
        if items_schema:
            for i, item in enumerate(data):
                naive_validate(root_schema, items_schema, item, f"{path}[{i}]")
    elif schema_type == "string":
        if not isinstance(data, str):
            raise AssertionError(f"[{path}] Expected string, got {type(data).__name__}")
        if "pattern" in schema and not re.search(schema["pattern"], data):
            raise AssertionError(f"[{path}] String '{data}' does not match pattern {schema['pattern']}")
        if "enum" in schema and data not in schema["enum"]:
            raise AssertionError(f"[{path}] Value '{data}' not in enum {schema['enum']}")
        if "const" in schema and data != schema["const"]:
            raise AssertionError(f"[{path}] Value '{data}' != const '{schema['const']}'")
    elif schema_type == "integer":
        if not isinstance(data, int) or isinstance(data, bool):
            raise AssertionError(f"[{path}] Expected integer, got {type(data).__name__}")
        if "minimum" in schema and data < schema["minimum"]:
            raise AssertionError(f"[{path}] Integer {data} < minimum {schema['minimum']}")
        if "maximum" in schema and data > schema["maximum"]:
            raise AssertionError(f"[{path}] Integer {data} > maximum {schema['maximum']}")
    elif schema_type == "number":
        if not (isinstance(data, (int, float)) and not isinstance(data, bool)):
            raise AssertionError(f"[{path}] Expected number, got {type(data).__name__}")
        if "minimum" in schema and data < schema["minimum"]:
            raise AssertionError(f"[{path}] Number {data} < minimum {schema['minimum']}")
        if "maximum" in schema and data > schema["maximum"]:
            raise AssertionError(f"[{path}] Number {data} > maximum {schema['maximum']}")
    elif schema_type == "boolean":
        if not isinstance(data, bool):
            raise AssertionError(f"[{path}] Expected boolean, got {type(data).__name__}")


def validate_against_schema(schema: dict, data: dict):
    """Validates data against schema using jsonschema if available, else naive_validate."""
    if HAS_JSONSCHEMA:
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(data))
        if errors:
            raise AssertionError(f"JSONSchema validation failed: {[e.message for e in errors]}")
    else:
        naive_validate(schema, schema, data)


class TestDraft202012SchemasAdversarial(unittest.TestCase):
    """Adversarial stress-testing of all JSON Schemas in schemas/."""

    @classmethod
    def setUpClass(cls):
        cls.schema_paths = {
            "catalog": REPO_ROOT / "schemas" / "catalog.schema.json",
            "compliance_manifest": REPO_ROOT / "schemas" / "compliance_manifest.schema.json",
            "framework_registry": REPO_ROOT / "schemas" / "framework_registry.schema.json",
            "oscal_subset": REPO_ROOT / "schemas" / "oscal_v1_2_0_subset.schema.json",
        }
        cls.schemas = {}
        for name, path in cls.schema_paths.items():
            with open(path, "r", encoding="utf-8") as f:
                cls.schemas[name] = json.load(f)

    def test_01_all_schemas_exist_and_conform_to_draft_2020_12(self):
        """Verify all 4 schemas declare Draft 2020-12, have $id and title, and are meta-schema valid."""
        for name, schema in self.schemas.items():
            self.assertEqual(
                schema.get("$schema"),
                "https://json-schema.org/draft/2020-12/schema",
                f"Schema {name} does not target Draft 2020-12",
            )
            self.assertIn("$id", schema, f"Schema {name} missing $id")
            self.assertIn("title", schema, f"Schema {name} missing title")
            self.assertEqual(schema.get("type"), "object", f"Schema {name} root type should be object")

            if HAS_JSONSCHEMA:
                Draft202012Validator.check_schema(schema)

    def test_02_catalog_schema_negative_mutations(self):
        """Adversarially inject invalid inputs into catalog schema to verify strict rejection."""
        schema = self.schemas["catalog"]

        valid_sample = {
            "id": "iso_27001_2022",
            "name": "ISO/IEC 27001:2022",
            "version": "2022",
            "authority": "ISO/IEC",
            "total_controls": 1,
            "controls": [{"id": "A.5.1", "title": "Policies for information security"}],
        }
        validate_against_schema(schema, valid_sample)

        # Attack 1: Invalid framework ID not in enum
        bad_id = copy.deepcopy(valid_sample)
        bad_id["id"] = "invalid_framework_xyz"
        with self.assertRaises(AssertionError, msg="Failed to reject invalid catalog framework ID"):
            validate_against_schema(schema, bad_id)

        # Attack 2: total_controls < 1
        bad_count = copy.deepcopy(valid_sample)
        bad_count["total_controls"] = 0
        with self.assertRaises(AssertionError, msg="Failed to reject total_controls = 0"):
            validate_against_schema(schema, bad_count)

        # Attack 3: Empty controls array
        empty_controls = copy.deepcopy(valid_sample)
        empty_controls["controls"] = []
        with self.assertRaises(AssertionError, msg="Failed to reject empty controls array"):
            validate_against_schema(schema, empty_controls)

        # Attack 4: Missing required title in control entry
        missing_title = copy.deepcopy(valid_sample)
        del missing_title["controls"][0]["title"]
        with self.assertRaises(AssertionError, msg="Failed to reject missing control title"):
            validate_against_schema(schema, missing_title)

        # Attack 5: Invalid maturity_level enum
        bad_ml = copy.deepcopy(valid_sample)
        bad_ml["controls"][0]["maturity_level"] = "ML4"
        with self.assertRaises(AssertionError, msg="Failed to reject invalid maturity_level ML4"):
            validate_against_schema(schema, bad_ml)

        # Attack 6: Additional property injected at root
        extra_prop = copy.deepcopy(valid_sample)
        extra_prop["unauthorized_field"] = "hacked"
        with self.assertRaises(AssertionError, msg="Failed to reject root additional property"):
            validate_against_schema(schema, extra_prop)

    def test_03_compliance_manifest_schema_negative_mutations(self):
        """Adversarially inject invalid configurations into compliance manifest schema."""
        schema = self.schemas["compliance_manifest"]

        with open(REPO_ROOT / "mappings" / "compliance_manifest.yaml", "r", encoding="utf-8") as f:
            valid_sample = yaml.safe_load(f)

        validate_against_schema(schema, valid_sample)

        # Attack 1: review_policy.max_age_days > 365
        bad_age = copy.deepcopy(valid_sample)
        bad_age["review_policy"]["max_age_days"] = 366
        with self.assertRaises(AssertionError, msg="Failed to reject max_age_days = 366"):
            validate_against_schema(schema, bad_age)

        # Attack 2: review_policy.max_age_days < 1
        bad_age_zero = copy.deepcopy(valid_sample)
        bad_age_zero["review_policy"]["max_age_days"] = 0
        with self.assertRaises(AssertionError, msg="Failed to reject max_age_days = 0"):
            validate_against_schema(schema, bad_age_zero)

        # Attack 3: Invalid review_policy cadence
        bad_cadence = copy.deepcopy(valid_sample)
        bad_cadence["review_policy"]["cadence"] = "weekly"
        with self.assertRaises(AssertionError, msg="Failed to reject cadence 'weekly'"):
            validate_against_schema(schema, bad_cadence)

        # Attack 4: Adopted frameworks fewer than 4
        few_fw = copy.deepcopy(valid_sample)
        few_fw["adopted_frameworks"] = few_fw["adopted_frameworks"][:3]
        with self.assertRaises(AssertionError, msg="Failed to reject adopted_frameworks < 4"):
            validate_against_schema(schema, few_fw)

        # Attack 5: Target coverage percentage > 100
        bad_cov = copy.deepcopy(valid_sample)
        bad_cov["adopted_frameworks"][0]["target_coverage_pct"] = 105.0
        with self.assertRaises(AssertionError, msg="Failed to reject target_coverage_pct > 100"):
            validate_against_schema(schema, bad_cov)

        # Attack 6: Invalid exception ID pattern
        bad_ex_id = copy.deepcopy(valid_sample)
        bad_ex_id["exceptions"][0]["id"] = "EX-26-1"
        with self.assertRaises(AssertionError, msg="Failed to reject malformed exception ID 'EX-26-1'"):
            validate_against_schema(schema, bad_ex_id)

        # Attack 7: Invalid exception status
        bad_status = copy.deepcopy(valid_sample)
        bad_status["exceptions"][0]["status"] = "pending"
        with self.assertRaises(AssertionError, msg="Failed to reject invalid status 'pending'"):
            validate_against_schema(schema, bad_status)

        # Attack 8: Empty compensating controls
        no_comp = copy.deepcopy(valid_sample)
        no_comp["exceptions"][0]["compensating_controls"] = []
        with self.assertRaises(AssertionError, msg="Failed to reject empty compensating_controls"):
            validate_against_schema(schema, no_comp)

        # Attack 9: Additional properties at root
        extra_root = copy.deepcopy(valid_sample)
        extra_root["bogus"] = True
        with self.assertRaises(AssertionError, msg="Failed to reject additional properties at manifest root"):
            validate_against_schema(schema, extra_root)

    def test_04_framework_registry_schema_negative_mutations(self):
        """Adversarially inject invalid entries into framework registry schema."""
        schema = self.schemas["framework_registry"]

        valid_sample = {
            "schema_version": "2.0.0",
            "version": "2.0.0",
            "metadata": {
                "repository": "security-standards-template",
                "title": "Test Registry",
                "last_updated": "2026-10-31",
                "author": "SecOps",
                "description": "Test registry description",
            },
            "frameworks": {
                "iso_27001_2022": {"name": "ISO 27001"},
                "soc2_tsc_2017": {"name": "SOC 2"},
                "nist_csf_2_0": {"name": "CSF 2.0"},
                "gdpr": {"name": "GDPR"},
                "nist_sp_800_53_rev5": {"name": "800-53"},
                "asd_essential_eight": {"name": "E8"},
            },
            "domains": [{"id": f"D{i}", "name": f"Domain {i}"} for i in range(14)],
            "controls": [
                {
                    "id": f"CC-GV-{i:02d}",
                    "name": f"Control {i}",
                    "domain": "governance",
                    "description": "Desc",
                    "implementing_docs": ["docs/01.md"],
                    "mappings": {
                        "iso_27001_2022": ["A.5.1"],
                        "iso_27001_2013_legacy": ["A.5.1.1"],
                        "soc2_tsc_2017": ["CC1.1"],
                        "nist_csf_2_0": ["GV.OC-01"],
                        "gdpr_articles": ["Art. 5"],
                        "nist_sp_800_53_rev5": ["AC-1"],
                        "asd_essential_eight": ["E8-AC-ML1"],
                    },
                }
                for i in range(1, 56)
            ],
        }

        validate_against_schema(schema, valid_sample)

        # Attack 1: schema_version not matching ^2\.\d+\.\d+$
        bad_ver = copy.deepcopy(valid_sample)
        bad_ver["schema_version"] = "1.0.0"
        with self.assertRaises(AssertionError, msg="Failed to reject schema_version 1.0.0"):
            validate_against_schema(schema, bad_ver)

        # Attack 2: Control ID pattern violation (e.g. CC-GV-1 instead of CC-GV-01)
        bad_ctrl_id = copy.deepcopy(valid_sample)
        bad_ctrl_id["controls"][0]["id"] = "CC-GV-1"
        with self.assertRaises(AssertionError, msg="Failed to reject malformed control ID CC-GV-1"):
            validate_against_schema(schema, bad_ctrl_id)

    def test_05_oscal_subset_schema_root_validation_defect_audit(self):
        """
        AUDIT / CHALLENGE DEFECT DETECTION:
        Demonstrate that oscal_v1_2_0_subset.schema.json has a root additionalProperties bug
        that rejects valid OSCAL documents because properties are declared inside oneOf
        while additionalProperties: false is placed at the root level without top-level properties.
        """
        schema = self.schemas["oscal_subset"]

        valid_catalog = {
            "catalog": {
                "uuid": "6ba7b810-9dad-51d1-80b4-00c04fd430c8",  # RFC 4122 UUIDv5
                "metadata": {
                    "title": "ISMS Canonical Catalog",
                    "last-modified": "2026-10-31T00:00:00Z",
                    "version": "2.0.0",
                    "oscal-version": "1.2.0",
                },
                "groups": [],
            }
        }

        # If jsonschema is available, demonstrate the exact failure mode
        if HAS_JSONSCHEMA:
            v = Draft202012Validator(schema)
            errors = list(v.iter_errors(valid_catalog))
            # EMPIRICAL OBSERVATION: Root additionalProperties: false causes 'catalog' to be unexpected
            # We record this defect:
            if errors:
                err_messages = [e.message for e in errors]
                self.assertIn(
                    "Additional properties are not allowed ('catalog' was unexpected)",
                    err_messages,
                    "Schema should exhibit the reported additionalProperties bug",
                )


class TestAuthoritativeCatalogsIntegrity(unittest.TestCase):
    """Stress-test and audit all 6 authoritative reference catalogs in mappings/catalogs/."""

    @classmethod
    def setUpClass(cls):
        cls.catalogs_dir = REPO_ROOT / "mappings" / "catalogs"
        cls.catalog_files = sorted(list(cls.catalogs_dir.glob("*.yaml")))
        cls.catalogs = {}
        for cp in cls.catalog_files:
            with open(cp, "r", encoding="utf-8") as f:
                cls.catalogs[cp.stem] = yaml.safe_load(f)

    def test_01_all_six_catalogs_exist_and_match_declared_enum(self):
        """Verify all 6 catalogs exist and match expected framework IDs."""
        expected_frameworks = {
            "iso_27001_2022",
            "soc2_tsc_2017",
            "nist_csf_2_0",
            "gdpr",
            "nist_sp_800_53_rev5",
            "asd_essential_eight",
        }
        self.assertEqual(set(self.catalogs.keys()), expected_frameworks)

    def test_02_catalogs_control_id_uniqueness_and_counts(self):
        """Empirically verify ZERO duplicate control IDs and strict count matching."""
        expected_counts = {
            "iso_27001_2022": 93,
            "soc2_tsc_2017": 61,
            "nist_csf_2_0": 106,
            "gdpr": 26,
            "nist_sp_800_53_rev5": 177,
            "asd_essential_eight": 24,
        }

        for fw_id, cat in self.catalogs.items():
            declared_total = cat.get("total_controls")
            controls = cat.get("controls", [])
            actual_len = len(controls)

            self.assertEqual(
                declared_total,
                actual_len,
                f"Catalog {fw_id} declared total {declared_total} != len(controls) {actual_len}",
            )

            self.assertEqual(
                actual_len,
                expected_counts[fw_id],
                f"Catalog {fw_id} count {actual_len} != expected count {expected_counts[fw_id]}",
            )

            # Check for duplicate IDs
            ids = [c["id"] for c in controls]
            seen = set()
            duplicates = []
            for cid in ids:
                if cid in seen:
                    duplicates.append(cid)
                seen.add(cid)

            self.assertEqual(
                len(duplicates),
                0,
                f"Catalog {fw_id} contains duplicate control IDs: {duplicates}",
            )
            self.assertEqual(
                len(seen),
                actual_len,
                f"Catalog {fw_id} unique IDs {len(seen)} != total controls {actual_len}",
            )

    def test_03_iso_27001_2022_annex_a_coverage(self):
        """Verify ISO 27001:2022 contains all 93 official controls across all 4 themes."""
        cat = self.catalogs["iso_27001_2022"]
        ids = set(c["id"] for c in cat["controls"])

        expected_ids = (
            [f"A.5.{i}" for i in range(1, 38)]
            + [f"A.6.{i}" for i in range(1, 9)]
            + [f"A.7.{i}" for i in range(1, 15)]
            + [f"A.8.{i}" for i in range(1, 35)]
        )
        self.assertEqual(len(expected_ids), 93)
        missing = set(expected_ids) - ids
        self.assertEqual(len(missing), 0, f"ISO 27001:2022 missing Annex A controls: {missing}")

    def test_04_soc2_tsc_2017_criteria_coverage(self):
        """Verify SOC 2 catalog covers Common Criteria (33), Availability (3), Confidentiality (2), PI (5), Privacy (18)."""
        cat = self.catalogs["soc2_tsc_2017"]
        controls = cat["controls"]

        cc_controls = [c for c in controls if c["id"].startswith("CC")]
        a_controls = [c for c in controls if c["id"].startswith("A1.")]
        c_controls = [c for c in controls if c["id"].startswith("C1.")]
        pi_controls = [c for c in controls if c["id"].startswith("PI1.")]
        p_controls = [c for c in controls if c["id"].startswith("P") and not c["id"].startswith("PI")]

        self.assertEqual(len(cc_controls), 33, f"Expected 33 CC controls, got {len(cc_controls)}")
        self.assertEqual(len(a_controls), 3, f"Expected 3 Availability controls, got {len(a_controls)}")
        self.assertEqual(len(c_controls), 2, f"Expected 2 Confidentiality controls, got {len(c_controls)}")
        self.assertEqual(len(pi_controls), 5, f"Expected 5 PI controls, got {len(pi_controls)}")
        self.assertEqual(len(p_controls), 18, f"Expected 18 Privacy controls, got {len(p_controls)}")
        self.assertEqual(len(controls), 61)

    def test_05_nist_csf_2_0_functions_and_subcategories(self):
        """Verify NIST CSF 2.0 covers all 6 functions (GV:31, ID:20, PR:22, DE:11, RS:13, RC:9)."""
        cat = self.catalogs["nist_csf_2_0"]
        controls = cat["controls"]

        function_counts = {}
        for c in controls:
            fn = c["function"]
            function_counts[fn] = function_counts.get(fn, 0) + 1

        self.assertEqual(function_counts.get("GV"), 31, "GV subcategory count != 31")
        self.assertEqual(function_counts.get("ID"), 20, "ID subcategory count != 20")
        self.assertEqual(function_counts.get("PR"), 22, "PR subcategory count != 22")
        self.assertEqual(function_counts.get("DE"), 11, "DE subcategory count != 11")
        self.assertEqual(function_counts.get("RS"), 13, "RS subcategory count != 13")
        self.assertEqual(function_counts.get("RC"), 9, "RC subcategory count != 9")
        self.assertEqual(len(controls), 106)

    def test_06_nist_sp_800_53_rev5_all_20_families_represented(self):
        """Verify NIST SP 800-53 Rev. 5 spans all 20 control families (AC-SR) and >= 85 controls."""
        cat = self.catalogs["nist_sp_800_53_rev5"]
        controls = cat["controls"]
        self.assertGreaterEqual(len(controls), 85, "NIST 800-53 controls < 85")
        self.assertEqual(len(controls), 177, "Expected exactly 177 Moderate baseline controls")

        families_found = set(c["family"] for c in controls)
        expected_20_families = {
            "AC", "AT", "AU", "CA", "CM", "CP", "IA", "IR", "MA", "MP",
            "PE", "PL", "PM", "PS", "PT", "RA", "SA", "SC", "SI", "SR"
        }
        missing_families = expected_20_families - families_found
        self.assertEqual(len(missing_families), 0, f"NIST 800-53 missing control families: {missing_families}")

    def test_07_asd_essential_eight_strategies_and_maturity_levels(self):
        """Verify Essential Eight covers all 8 strategies across ML1, ML2, ML3 with mapped ISM IDs."""
        cat = self.catalogs["asd_essential_eight"]
        controls = cat["controls"]
        self.assertEqual(len(controls), 24, "Expected exactly 24 E8 capability controls (8x3)")

        expected_strategies = {
            "application_control",
            "patch_applications",
            "configure_office_macros",
            "user_application_hardening",
            "restrict_admin_privileges",
            "patch_operating_systems",
            "multi_factor_authentication",
            "regular_backups",
        }
        found_strategies = set(c["strategy"] for c in controls)
        self.assertEqual(found_strategies, expected_strategies, "Missing E8 strategies")

        for strat in expected_strategies:
            strat_ctrls = [c for c in controls if c["strategy"] == strat]
            mls = sorted([c["maturity_level"] for c in strat_ctrls])
            self.assertEqual(mls, ["ML1", "ML2", "ML3"], f"Strategy {strat} missing required ML1-ML3 levels")

        for c in controls:
            self.assertIn("mapped_ism_ids", c, f"E8 control {c['id']} missing mapped_ism_ids")
            self.assertGreater(len(c["mapped_ism_ids"]), 0, f"E8 control {c['id']} has empty mapped_ism_ids")


class TestComplianceManifestBoundsAndExceptions(unittest.TestCase):
    """Stress-test compliance manifest review cadences and time-bound exception windows."""

    @classmethod
    def setUpClass(cls):
        cls.manifest_path = REPO_ROOT / "mappings" / "compliance_manifest.yaml"
        with open(cls.manifest_path, "r", encoding="utf-8") as f:
            cls.manifest = yaml.safe_load(f)

    def test_01_all_adopted_frameworks_configured(self):
        """Verify compliance manifest configures all 6 adopted frameworks with 100% target coverage."""
        frameworks = self.manifest["adopted_frameworks"]
        fw_ids = [fw["framework_id"] for fw in frameworks]
        self.assertEqual(len(fw_ids), 6)
        expected = {
            "iso_27001_2022",
            "soc2_tsc_2017",
            "nist_csf_2_0",
            "gdpr",
            "nist_sp_800_53_rev5",
            "asd_essential_eight",
        }
        self.assertEqual(set(fw_ids), expected)

        e8 = next(fw for fw in frameworks if fw["framework_id"] == "asd_essential_eight")
        self.assertEqual(e8.get("target_maturity_level"), "ML2")

        nist = next(fw for fw in frameworks if fw["framework_id"] == "nist_sp_800_53_rev5")
        self.assertEqual(nist.get("target_baseline"), "Moderate")

    def test_02_thresholds_meet_minimum_bounds(self):
        """Verify declared thresholds meet or exceed authoritative project minimums."""
        th = self.manifest["thresholds"]
        self.assertGreaterEqual(th["min_canonical_controls"], 55)
        self.assertGreaterEqual(th["min_distinct_csf_subcategories"], 45)
        self.assertGreaterEqual(th["min_distinct_nist_800_53_controls"], 85)
        self.assertEqual(th["min_essential_eight_strategies"], 8)

    def test_03_active_exceptions_window_strictly_within_90_days(self):
        """Verify every active exception is strictly time-bound: 0 < duration <= 90 days."""
        exceptions = self.manifest.get("exceptions", [])
        self.assertGreaterEqual(len(exceptions), 1, "Must contain at least 1 sample exception")

        for ex in exceptions:
            ex_id = ex["id"]
            app_date = datetime.strptime(str(ex["approval_date"]), "%Y-%m-%d")
            exp_date = datetime.strptime(str(ex["expiration_date"]), "%Y-%m-%d")

            duration = (exp_date - app_date).days

            self.assertGreater(
                duration,
                0,
                f"Exception {ex_id}: expiration date {ex['expiration_date']} is on or before approval date {ex['approval_date']}",
            )

            self.assertLessEqual(
                duration,
                90,
                f"Exception {ex_id}: window duration ({duration} days) exceeds strict 90-day limit",
            )

            compensating = ex.get("compensating_controls", [])
            self.assertGreaterEqual(
                len(compensating),
                1,
                f"Exception {ex_id} lacks mandatory compensating controls",
            )

    def test_04_negative_adversarial_exception_durations(self):
        """Adversarial oracle verifying that exception durations > 90 days or negative are detected."""
        def evaluate_exception(approval_str, expiration_str):
            app = datetime.strptime(approval_str, "%Y-%m-%d")
            exp = datetime.strptime(expiration_str, "%Y-%m-%d")
            delta = (exp - app).days
            if delta <= 0:
                return "NEGATIVE_OR_ZERO_WINDOW"
            if delta > 90:
                return "EXCEEDS_90_DAYS"
            return "VALID"

        self.assertEqual(evaluate_exception("2026-10-26", "2027-01-20"), "VALID")  # 86 days
        self.assertEqual(evaluate_exception("2026-10-28", "2026-11-25"), "VALID")  # 28 days
        self.assertEqual(evaluate_exception("2026-10-26", "2026-10-26"), "NEGATIVE_OR_ZERO_WINDOW")
        self.assertEqual(evaluate_exception("2026-10-26", "2026-10-20"), "NEGATIVE_OR_ZERO_WINDOW")
        self.assertEqual(evaluate_exception("2026-10-26", "2027-01-25"), "EXCEEDS_90_DAYS")  # 91 days
        self.assertEqual(evaluate_exception("2026-10-26", "2027-04-26"), "EXCEEDS_90_DAYS")  # 182 days


class TestWorkspaceHygieneAndADRs(unittest.TestCase):
    """Stress-test git hygiene, untracked dev logs, LICENSE, and ADR isolation."""

    def test_01_no_serve_logs_exist(self):
        """Verify zero serve_*.txt or zserve_*.txt exist anywhere in workspace."""
        matches = list(REPO_ROOT.glob("**/serve_*.txt")) + list(REPO_ROOT.glob("**/zserve_*.txt"))
        self.assertEqual(
            len(matches),
            0,
            f"Found untracked dev server log files: {matches}",
        )

    def test_02_gitignore_covers_build_and_dev_artifacts(self):
        """Verify .gitignore includes serve_*.txt, zserve_*.txt, *.sarif, dist/."""
        gitignore_path = REPO_ROOT / ".gitignore"
        self.assertTrue(gitignore_path.exists(), ".gitignore is missing")
        content = gitignore_path.read_text(encoding="utf-8")
        self.assertIn("serve_*.txt", content)
        self.assertIn("zserve_*.txt", content)
        self.assertIn("*.sarif", content)
        self.assertIn("dist/", content)

    def test_03_license_file_valid_apache2(self):
        """Verify LICENSE file exists at root, is Apache-2.0, and contains 2026 copyright notice."""
        license_path = REPO_ROOT / "LICENSE"
        self.assertTrue(license_path.exists(), "LICENSE file missing at root")
        text = license_path.read_text(encoding="utf-8")
        self.assertIn("Apache License", text)
        self.assertIn("Version 2.0", text)
        self.assertIn("Copyright 2026", text)

    def test_04_adrs_exist_and_isolated_from_docs(self):
        """Verify ADR-001, ADR-002, ADR-003 exist strictly under architecture/adr/ and not in docs/."""
        adr_dir = REPO_ROOT / "architecture" / "adr"
        self.assertTrue(adr_dir.exists(), "architecture/adr/ directory missing")

        adrs = sorted([f.name for f in adr_dir.glob("*.md")])
        expected_adrs = [
            "ADR-001-yaml-sot-and-oscal-export.md",
            "ADR-002-mkdocs-zensical-migration.md",
            "ADR-003-essential-eight-and-nist-800-53-mapping.md",
        ]
        self.assertEqual(adrs, expected_adrs)

        docs_adrs = list((REPO_ROOT / "docs").glob("**/ADR-*.md"))
        self.assertEqual(len(docs_adrs), 0, f"ADR files mistakenly placed in docs/: {docs_adrs}")

        mkdocs_path = REPO_ROOT / "mkdocs.yml"
        mkdocs_content = mkdocs_path.read_text(encoding="utf-8")
        self.assertNotIn("architecture/adr", mkdocs_content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
