#!/usr/bin/env python3
"""
Milestone 2 Independent Adversarial Challenger Test Suite
Agent: challenger_v2_m2_2 (Role: teamwork_preview_challenger)
Target: Milestone 2 Deliverables
  - Deep Structural Validation: mappings/framework_registry.yaml against Draft 2020-12 schemas/framework_registry.schema.json
  - Negative Mutation Stress Testing: Invalid control IDs, invalid schema_version, forbidden additional properties,
    invalid OSCAL relationships, missing required framework keys, invalid mappedItem variants, - None literals
  - Multi-Framework & Catalog Consistency: NIST CSF 2.0 remediation (zero retired IDs repo-wide, >= 45 subcategories),
    NIST SP 800-53 Rev. 5 (>= 85 controls across all 20 families), ASD Essential Eight (all 8 strategies across ML1-ML3)
  - Policy & Standard Harmonization: Explicit Essential Eight ML2/ML3 threshold requirements in 02/05, 02/13, 03/01, 03/04
  - Full Regression & MkDocs Strict Build Verification
"""

import copy
import glob
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest
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


class UniqueKeyLoader(yaml.SafeLoader):
    """YAML Loader that strictly forbids duplicate mapping keys at any depth."""
    pass


def _construct_mapping_unique(loader, node, deep=False):
    loader.flatten_mapping(node)
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"Duplicate YAML key encountered: '{key}'")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping_unique
)


def resolve_local_ref(ref: str, root_schema: dict) -> dict:
    """Resolve JSON pointer like '#/$defs/canonicalControl'."""
    if not ref.startswith("#/"):
        raise ValueError(f"Only local refs starting with '#/' supported: {ref}")
    parts = ref.lstrip("#/").split("/")
    cur = root_schema
    for p in parts:
        cur = cur[p]
    return cur


def validate_draft202012_schema(data, schema: dict, root_schema: dict, path: str = "root"):
    """
    Independent Draft 2020-12 schema validator.
    Evaluates:
      - $ref resolution
      - not constraints (e.g., {"const": "None"})
      - oneOf alternatives
      - object validation (type, required, properties, additionalProperties)
      - array validation (type, items, minItems)
      - string validation (pattern, enum, const)
      - integer/number/boolean types
    Raises AssertionError on validation violation.
    """
    if "$ref" in schema:
        target = resolve_local_ref(schema["$ref"], root_schema)
        validate_draft202012_schema(data, target, root_schema, path)
        return

    if "not" in schema:
        try:
            validate_draft202012_schema(data, schema["not"], root_schema, path)
            matched_not = True
        except (AssertionError, ValueError):
            matched_not = False
        if matched_not:
            raise AssertionError(f"[{path}] Data matches forbidden 'not' schema: {data}")

    if "oneOf" in schema:
        matches = 0
        match_errors = []
        for branch in schema["oneOf"]:
            try:
                validate_draft202012_schema(data, branch, root_schema, path)
                matches += 1
            except (AssertionError, ValueError) as err:
                match_errors.append(str(err))
        if matches != 1:
            raise AssertionError(f"[{path}] Expected exactly 1 oneOf match, got {matches}. Branch errors: {match_errors}")
        return

    if "const" in schema:
        if data != schema["const"]:
            raise AssertionError(f"[{path}] Value {data!r} does not match const {schema['const']!r}")

    if "enum" in schema:
        if data not in schema["enum"]:
            raise AssertionError(f"[{path}] Value {data!r} not in enum {schema['enum']}")

    stype = schema.get("type")
    if stype == "object":
        if not isinstance(data, dict):
            raise AssertionError(f"[{path}] Expected object, got {type(data).__name__}")
        for req in schema.get("required", []):
            if req not in data:
                raise AssertionError(f"[{path}] Missing required property: '{req}'")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            allowed = set(props.keys())
            extra = set(data.keys()) - allowed
            if extra:
                raise AssertionError(f"[{path}] Forbidden additional properties: {extra}")
        for k, v in data.items():
            if k in props:
                validate_draft202012_schema(v, props[k], root_schema, f"{path}.{k}")
    elif stype == "array":
        if not isinstance(data, list):
            raise AssertionError(f"[{path}] Expected array, got {type(data).__name__}")
        min_items = schema.get("minItems")
        if min_items is not None and len(data) < min_items:
            raise AssertionError(f"[{path}] Array has {len(data)} items, minimum required is {min_items}")
        items_schema = schema.get("items")
        if items_schema:
            for idx, item in enumerate(data):
                validate_draft202012_schema(item, items_schema, root_schema, f"{path}[{idx}]")
    elif stype == "string":
        if not isinstance(data, str):
            raise AssertionError(f"[{path}] Expected string, got {type(data).__name__}")
        if "pattern" in schema:
            if not re.search(schema["pattern"], data):
                raise AssertionError(f"[{path}] String '{data}' does not match pattern '{schema['pattern']}'")
    elif stype == "integer":
        if not isinstance(data, int) or isinstance(data, bool):
            raise AssertionError(f"[{path}] Expected integer, got {type(data).__name__}")
        if "minimum" in schema and data < schema["minimum"]:
            raise AssertionError(f"[{path}] Integer {data} < minimum {schema['minimum']}")
        if "maximum" in schema and data > schema["maximum"]:
            raise AssertionError(f"[{path}] Integer {data} > maximum {schema['maximum']}")
    elif stype == "number":
        if not (isinstance(data, (int, float)) and not isinstance(data, bool)):
            raise AssertionError(f"[{path}] Expected number, got {type(data).__name__}")
    elif stype == "boolean":
        if not isinstance(data, bool):
            raise AssertionError(f"[{path}] Expected boolean, got {type(data).__name__}")


class TestMilestone2AdversarialChallenger(unittest.TestCase):
    """Independent Challenger 2 test suite targeting Milestone 2 deliverables."""

    @classmethod
    def setUpClass(cls):
        cls.registry_path = REPO_ROOT / "mappings" / "framework_registry.yaml"
        cls.schema_path = REPO_ROOT / "schemas" / "framework_registry.schema.json"
        
        with open(cls.schema_path, "r", encoding="utf-8") as f:
            cls.schema = json.load(f)
            
        with open(cls.registry_path, "r", encoding="utf-8") as f:
            cls.raw_registry_text = f.read()
            
        cls.registry = yaml.load(cls.raw_registry_text, Loader=UniqueKeyLoader)

        with open(REPO_ROOT / "mappings" / "catalogs" / "nist_csf_2_0.yaml", "r", encoding="utf-8") as f:
            cls.cat_csf = yaml.safe_load(f)
        with open(REPO_ROOT / "mappings" / "catalogs" / "nist_sp_800_53_rev5.yaml", "r", encoding="utf-8") as f:
            cls.cat_53 = yaml.safe_load(f)
        with open(REPO_ROOT / "mappings" / "catalogs" / "asd_essential_eight.yaml", "r", encoding="utf-8") as f:
            cls.cat_e8 = yaml.safe_load(f)

    # =========================================================================
    # 1. Production Registry Deep Structural Validation
    # =========================================================================

    def test_01_registry_production_file_validity(self):
        """Verify production framework_registry.yaml conforms strictly to Draft 2020-12 schema and v2.0 rules."""
        # 1. Full schema validation
        validate_draft202012_schema(self.registry, self.schema, self.schema)

        # 2. Schema version and version
        self.assertEqual(self.registry.get("schema_version"), "2.0.0")
        self.assertEqual(self.registry.get("version"), "2.0.0")

        # 3. Exactly 98 canonical controls
        controls = self.registry.get("controls", [])
        self.assertEqual(len(controls), 98, f"Expected exactly 98 controls, found {len(controls)}")

        # 4. No YAML anchors/aliases or legacy keys in text
        self.assertNotIn("*id001", self.raw_registry_text)
        self.assertNotIn("&id001", self.raw_registry_text)
        self.assertNotIn("- None", self.raw_registry_text)
        self.assertNotIn("canonical_controls:", self.raw_registry_text)

        # 5. Zero duplicate keys or legacy field names inside controls
        for c in controls:
            cid = c["id"]
            self.assertNotIn("implementing_documents", c, f"Found legacy 'implementing_documents' in {cid}")
            m = c["mappings"]
            self.assertNotIn("soc2_tsc", m, f"Found legacy 'soc2_tsc' in {cid}")
            self.assertNotIn("gdpr", m, f"Found legacy 'gdpr' in {cid}")
            # Ensure iso_27001_2013_legacy does not contain "None"
            self.assertNotIn("None", m["iso_27001_2013_legacy"])

    # =========================================================================
    # 2. Negative Mutation Testing Against Framework Registry Schema
    # =========================================================================

    def test_02_mutation_invalid_control_id_patterns(self):
        """Adversarially inject invalid control IDs to verify regex pattern enforcement."""
        invalid_ids = [
            "CC-INVALID",
            "CC-gv-01",     # lowercase family
            "CC-GOV-01",    # 3-letter family
            "CC-G-01",      # 1-letter family
            "CC-GV-1",       # 1-digit number
            "CC-GV-001",     # 3-digit number
            "ISO-A5-01",     # wrong prefix
            "CC_GV_01",      # underscore separator
            "",              # empty string
        ]
        base = copy.deepcopy(self.registry)
        for bad_id in invalid_ids:
            base["controls"][0]["id"] = bad_id
            with self.assertRaises(AssertionError, msg=f"Should reject invalid control ID: {bad_id}"):
                validate_draft202012_schema(base, self.schema, self.schema)

    def test_03_mutation_invalid_schema_versions(self):
        """Adversarially inject invalid schema_version values."""
        invalid_versions = [
            "1.0.0",        # Major version 1
            "3.0.0",        # Major version 3
            "2.0",          # Missing patch
            "v2.0.0",       # Leading v
            "2.0.0-beta",   # Prerelease tag
        ]
        base = copy.deepcopy(self.registry)
        for bad_ver in invalid_versions:
            base["schema_version"] = bad_ver
            with self.assertRaises(AssertionError, msg=f"Should reject invalid schema_version: {bad_ver}"):
                validate_draft202012_schema(base, self.schema, self.schema)

    def test_04_mutation_forbidden_additional_properties(self):
        """Verify additionalProperties: false is enforced at root, metadata, control, and mapping levels."""
        # Root level
        base = copy.deepcopy(self.registry)
        base["unauthorized_root_field"] = "malicious"
        with self.assertRaises(AssertionError, msg="Root should reject additionalProperties"):
            validate_draft202012_schema(base, self.schema, self.schema)

        # Metadata level
        base = copy.deepcopy(self.registry)
        base["metadata"]["extra_meta"] = "malicious"
        with self.assertRaises(AssertionError, msg="Metadata should reject additionalProperties"):
            validate_draft202012_schema(base, self.schema, self.schema)

        # Control level
        base = copy.deepcopy(self.registry)
        base["controls"][0]["extra_control_field"] = "malicious"
        with self.assertRaises(AssertionError, msg="Control should reject additionalProperties"):
            validate_draft202012_schema(base, self.schema, self.schema)

        # Mappings level
        base = copy.deepcopy(self.registry)
        base["controls"][0]["mappings"]["pci_dss"] = []
        with self.assertRaises(AssertionError, msg="Mappings should reject additionalProperties"):
            validate_draft202012_schema(base, self.schema, self.schema)

        # Mapped item object level
        base = copy.deepcopy(self.registry)
        base["controls"][0]["mappings"]["nist_sp_800_53_rev5"][0]["extra_attr"] = "invalid"
        with self.assertRaises(AssertionError, msg="Mapped item should reject additionalProperties"):
            validate_draft202012_schema(base, self.schema, self.schema)

    def test_05_mutation_invalid_oscal_relationship_enums(self):
        """Adversarially inject invalid relationship enum strings into OSCAL mapped items."""
        invalid_relationships = [
            "mapped-to",
            "exact",
            "subsumes",
            "EQUIVALENT-TO",
            "subset_of",
            "",
            "related",
        ]
        base = copy.deepcopy(self.registry)
        for bad_rel in invalid_relationships:
            base["controls"][0]["mappings"]["nist_sp_800_53_rev5"][0]["relationship"] = bad_rel
            with self.assertRaises(AssertionError, msg=f"Should reject invalid relationship: {bad_rel}"):
                validate_draft202012_schema(base, self.schema, self.schema)

    def test_06_mutation_mapped_item_schema_variants(self):
        """Verify mappedItem oneOf correctly rejects malformed items."""
        base = copy.deepcopy(self.registry)
        
        # Missing id in object
        base["controls"][0]["mappings"]["nist_sp_800_53_rev5"][0] = {"relationship": "equivalent-to"}
        with self.assertRaises(AssertionError, msg="Should reject mapped item missing 'id'"):
            validate_draft202012_schema(base, self.schema, self.schema)

        # Missing relationship in object
        base = copy.deepcopy(self.registry)
        base["controls"][0]["mappings"]["nist_sp_800_53_rev5"][0] = {"id": "AC-1"}
        with self.assertRaises(AssertionError, msg="Should reject mapped item missing 'relationship'"):
            validate_draft202012_schema(base, self.schema, self.schema)

        # Invalid type (integer)
        base = copy.deepcopy(self.registry)
        base["controls"][0]["mappings"]["nist_sp_800_53_rev5"][0] = 12345
        with self.assertRaises(AssertionError, msg="Should reject integer mapped item"):
            validate_draft202012_schema(base, self.schema, self.schema)

        # Invalid type (array)
        base = copy.deepcopy(self.registry)
        base["controls"][0]["mappings"]["nist_sp_800_53_rev5"][0] = ["AC-1", "equivalent-to"]
        with self.assertRaises(AssertionError, msg="Should reject array mapped item"):
            validate_draft202012_schema(base, self.schema, self.schema)

    def test_07_mutation_iso_2013_legacy_rejects_none_literal(self):
        """Verify schema 'not: {const: None}' strictly rejects 'None' strings in legacy ISO mappings."""
        base = copy.deepcopy(self.registry)
        base["controls"][0]["mappings"]["iso_27001_2013_legacy"] = ["None"]
        with self.assertRaises(AssertionError, msg="Should reject literal 'None' in iso_27001_2013_legacy"):
            validate_draft202012_schema(base, self.schema, self.schema)

    def test_08_mutation_missing_required_framework_keys(self):
        """Verify that omitting any of the 7 required framework keys in mappings causes validation failure."""
        required_frameworks = [
            "iso_27001_2022",
            "iso_27001_2013_legacy",
            "soc2_tsc_2017",
            "nist_csf_2_0",
            "gdpr_articles",
            "nist_sp_800_53_rev5",
            "asd_essential_eight",
        ]
        for fkey in required_frameworks:
            base = copy.deepcopy(self.registry)
            del base["controls"][0]["mappings"][fkey]
            with self.assertRaises(AssertionError, msg=f"Should reject control mappings missing '{fkey}'"):
                validate_draft202012_schema(base, self.schema, self.schema)

    def test_09_mutation_empty_collections_min_items(self):
        """Verify minItems bounds on controls (>=55), domains (>=14), and implementing_docs (>=1)."""
        # implementing_docs minItems: 1
        base = copy.deepcopy(self.registry)
        base["controls"][0]["implementing_docs"] = []
        with self.assertRaises(AssertionError, msg="Should reject empty implementing_docs"):
            validate_draft202012_schema(base, self.schema, self.schema)

        # controls minItems: 55
        base = copy.deepcopy(self.registry)
        base["controls"] = base["controls"][:50]
        with self.assertRaises(AssertionError, msg="Should reject controls array with < 55 items"):
            validate_draft202012_schema(base, self.schema, self.schema)

        # domains minItems: 14
        base = copy.deepcopy(self.registry)
        base["domains"] = base["domains"][:10]
        with self.assertRaises(AssertionError, msg="Should reject domains array with < 14 items"):
            validate_draft202012_schema(base, self.schema, self.schema)

    # =========================================================================
    # 3. Repository-wide NIST CSF 2.0 Integrity & Catalog Verification
    # =========================================================================

    def test_10_zero_retired_csf_ids_repo_wide(self):
        """Verify exactly zero retired/invalid NIST CSF 2.0 IDs exist repository-wide."""
        pattern = re.compile(r"\b(GV\.CO-0[12]|PR\.DS-0[3579]|PR\.PS-0[789]|DE\.CM-04|RS\.AN-0[45]|RS\.RP-01)\b")
        offending_occurrences = []

        for p in REPO_ROOT.rglob("*"):
            if not p.is_file():
                continue
            if ".venv" in p.parts or ".git" in p.parts or "site" in p.parts or ".agents" in p.parts:
                continue
            if p.suffix in (".md", ".yaml", ".yml", ".json"):
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        for line_no, line in enumerate(f, 1):
                            match = pattern.search(line)
                            if match:
                                offending_occurrences.append((str(p.relative_to(REPO_ROOT)), line_no, match.group(0), line.strip()))
                except Exception as ex:
                    self.fail(f"Could not read {p}: {ex}")

        self.assertEqual(
            len(offending_occurrences), 0,
            f"Found {len(offending_occurrences)} retired CSF 2.0 IDs across repository:\n"
            + "\n".join(f"  {f}:{l} [{cid}] -> {text}" for f, l, cid, text in offending_occurrences)
        )

    def test_11_all_mapped_csf_ids_exist_in_catalog_and_coverage(self):
        """Verify 100% of mapped NIST CSF 2.0 IDs belong to the authoritative catalog with >= 45 distinct subcategories."""
        valid_csf_ids = {c["id"] for c in self.cat_csf["controls"]}
        mapped_csf_ids = set()

        for ctrl in self.registry["controls"]:
            cid = ctrl["id"]
            for csf_id in ctrl["mappings"]["nist_csf_2_0"]:
                self.assertIn(
                    csf_id, valid_csf_ids,
                    f"Control {cid} references invalid NIST CSF 2.0 ID '{csf_id}' not in catalog!"
                )
                mapped_csf_ids.add(csf_id)

        self.assertGreaterEqual(
            len(mapped_csf_ids), 45,
            f"Expected at least 45 distinct NIST CSF 2.0 subcategories, but found {len(mapped_csf_ids)}"
        )

        # Check representation across all 6 CSF functions (GV, ID, PR, DE, RS, RC)
        functions_present = {cid.split(".")[0] for cid in mapped_csf_ids}
        expected_functions = {"GV", "ID", "PR", "DE", "RS", "RC"}
        self.assertEqual(
            functions_present, expected_functions,
            f"Missing CSF functions in registry mapping: {expected_functions - functions_present}"
        )

    # =========================================================================
    # 4. NIST SP 800-53 Rev. 5 & ASD Essential Eight Catalog Integrity & Coverage
    # =========================================================================

    def test_12_nist_800_53_coverage_and_all_20_families(self):
        """Verify NIST SP 800-53 Rev. 5 mappings: >= 85 distinct controls, all 20 families, valid OSCAL semantics."""
        valid_53_ids = {c["id"] for c in self.cat_53["controls"]}
        allowed_rels = {"equivalent-to", "subset-of", "superset-of", "intersects-with"}
        
        mapped_53_ids = set()
        mapped_53_families = set()

        for ctrl in self.registry["controls"]:
            cid = ctrl["id"]
            for item in ctrl["mappings"]["nist_sp_800_53_rev5"]:
                self.assertIsInstance(item, dict, f"Control {cid} item must be object with id & relationship")
                fid = item.get("id")
                rel = item.get("relationship")
                self.assertIn(fid, valid_53_ids, f"Control {cid} references unknown NIST 800-53 ID '{fid}'")
                self.assertIn(rel, allowed_rels, f"Control {cid} has invalid relationship '{rel}'")
                mapped_53_ids.add(fid)
                mapped_53_families.add(fid.split("-")[0])

        self.assertGreaterEqual(
            len(mapped_53_ids), 85,
            f"Expected at least 85 distinct NIST 800-53 controls, but found {len(mapped_53_ids)}"
        )

        expected_20_families = {
            "AC", "AT", "AU", "CA", "CM", "CP", "IA", "IR", "MA", "MP",
            "PE", "PL", "PM", "PS", "PT", "RA", "SA", "SC", "SI", "SR"
        }
        self.assertEqual(
            mapped_53_families, expected_20_families,
            f"Missing 800-53 control families: {expected_20_families - mapped_53_families}"
        )

    def test_13_asd_essential_eight_coverage_and_all_8_strategies(self):
        """Verify ASD Essential Eight mappings: all 8 strategies, ML1-ML3 represented, valid OSCAL semantics."""
        valid_e8_ids = {c["id"] for c in self.cat_e8["controls"]}
        allowed_rels = {"equivalent-to", "subset-of", "superset-of", "intersects-with"}

        mapped_e8_ids = set()
        mapped_e8_strategies = set()
        mapped_e8_levels = set()

        for ctrl in self.registry["controls"]:
            cid = ctrl["id"]
            for item in ctrl["mappings"]["asd_essential_eight"]:
                self.assertIsInstance(item, dict, f"Control {cid} item must be object with id & relationship")
                eid = item.get("id")
                rel = item.get("relationship")
                self.assertIn(eid, valid_e8_ids, f"Control {cid} references unknown Essential Eight ID '{eid}'")
                self.assertIn(rel, allowed_rels, f"Control {cid} has invalid relationship '{rel}'")
                mapped_e8_ids.add(eid)
                # Format: E8-XX-MLY
                parts = eid.split("-")
                self.assertEqual(len(parts), 3, f"Unexpected E8 ID format: {eid}")
                mapped_e8_strategies.add(parts[1])
                mapped_e8_levels.add(parts[2])

        expected_8_strategies = {"AC", "AH", "AP", "MF", "OM", "PA", "PO", "RB"}
        self.assertEqual(
            mapped_e8_strategies, expected_8_strategies,
            f"Missing Essential Eight strategies: {expected_8_strategies - mapped_e8_strategies}"
        )

        expected_levels = {"ML1", "ML2", "ML3"}
        self.assertEqual(
            mapped_e8_levels, expected_levels,
            f"Missing Essential Eight maturity levels: {expected_levels - mapped_e8_levels}"
        )

    # =========================================================================
    # 5. Textual Verification of Essential Eight ML2/ML3 Threshold Policies
    # =========================================================================

    def test_14_policy_02_05_application_allowlisting_thresholds(self):
        """Verify docs/02_Policies/05_Operations_Security_Policy.md contains E8 application control thresholds."""
        policy_path = REPO_ROOT / "docs" / "02_Policies" / "05_Operations_Security_Policy.md"
        self.assertTrue(policy_path.exists(), f"Missing policy file: {policy_path}")
        text = policy_path.read_text(encoding="utf-8")

        # 1. Application allowlisting / control statement
        self.assertRegex(text, r"(?i)application control.*allowlisting", "Missing Application Control (Allowlisting)")

        # 2. Blocking unapproved binaries/scripts in user-writable paths
        self.assertIn("%APPDATA%", text, "Missing %APPDATA% blocking requirement")
        self.assertIn("%TEMP%", text, "Missing %TEMP% blocking requirement")
        self.assertRegex(text, r"(?i)user-writable directories", "Missing user-writable directories restriction")
        self.assertRegex(text, r"(?i)enforced in block mode", "Missing block mode enforcement requirement")

        # 3. Essential Eight mapping citation
        self.assertRegex(text, r"ASD Essential Eight.*E8-AC-ML2", "Missing ASD Essential Eight E8-AC-ML2 citation")

    def test_15_policy_02_13_macro_security_and_app_hardening(self):
        """Verify docs/02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md contains E8 macro & app hardening thresholds."""
        policy_path = REPO_ROOT / "docs" / "02_Policies" / "13_Acceptable_Use_and_AI_Security_Policy.md"
        self.assertTrue(policy_path.exists(), f"Missing policy file: {policy_path}")
        text = policy_path.read_text(encoding="utf-8")

        # 1. Internet macro blocking
        self.assertRegex(text, r"(?i)internet macro blocking", "Missing Internet Macro Blocking heading")
        self.assertRegex(text, r"(?i)originating from the internet.*strictly blocked", "Missing internet macro blocking mandate")
        self.assertRegex(text, r"(?i)disabled by default", "Missing disabled by default macro rule")
        self.assertRegex(text, r"(?i)digitally signed macros.*trusted publishers", "Missing digital signature requirement")
        self.assertRegex(text, r"(?i)strictly prohibited from bypassing macro security", "Missing user bypass prohibition")

        # 2. User application hardening
        self.assertRegex(text, r"(?i)user application hardening", "Missing User Application Hardening heading")
        self.assertRegex(text, r"(?i)block or disable web advertisements", "Missing web ad blocking")
        self.assertRegex(text, r"(?i)browser extension", "Missing browser extension control")
        self.assertRegex(text, r"(?i)child process", "Missing child process protection")
        self.assertIn("cmd.exe", text, "Missing cmd.exe child process block")
        self.assertIn("powershell.exe", text, "Missing powershell.exe child process block")

        # 3. Essential Eight citations
        self.assertIn("E8-OM-ML2", text)
        self.assertIn("E8-OM-ML3", text)
        self.assertIn("E8-AH-ML2", text)
        self.assertIn("E8-AH-ML3", text)

    def test_16_standard_03_01_phishing_resistant_mfa_and_paw_separation(self):
        """Verify docs/03_Standards_and_Procedures/01_Password_and_Authentication_Standard.md contains E8 MFA & PAW thresholds."""
        std_path = REPO_ROOT / "docs" / "03_Standards_and_Procedures" / "01_Password_and_Authentication_Standard.md"
        self.assertTrue(std_path.exists(), f"Missing standard file: {std_path}")
        text = std_path.read_text(encoding="utf-8")

        # 1. Phishing-resistant MFA
        self.assertRegex(text, r"(?i)phishing-resistant mfa", "Missing phishing-resistant MFA mandate")
        self.assertRegex(text, r"(?i)fido2|webauthn|yubikey", "Missing FIDO2/WebAuthn/YubiKey protocols")
        self.assertRegex(text, r"(?i)sms.*strictly prohibited", "Missing SMS prohibition")

        # 2. Privileged Account Separation
        self.assertRegex(text, r"(?i)privileged account separation", "Missing Privileged Account Separation heading")
        self.assertRegex(text, r"(?i)separated from standard.*accounts", "Missing account separation mandate")
        self.assertRegex(text, r"(?i)prohibited from reading corporate email.*browsing the open internet", "Missing email/internet barring")
        self.assertRegex(text, r"(?i)dedicated.*administrative workstations|privileged access workstations", "Missing PAW mandate")

        # 3. Essential Eight citations
        self.assertIn("E8-MF-ML2", text)
        self.assertIn("E8-MF-ML3", text)
        self.assertIn("E8-AP-ML2", text)
        self.assertIn("E8-AP-ML3", text)

    def test_17_standard_03_04_vulnerability_patch_sla_and_scanning_cadence(self):
        """Verify docs/03_Standards_and_Procedures/04_Vulnerability_and_Patch_Management_Standard.md contains 48h patch SLA."""
        std_path = REPO_ROOT / "docs" / "03_Standards_and_Procedures" / "04_Vulnerability_and_Patch_Management_Standard.md"
        self.assertTrue(std_path.exists(), f"Missing standard file: {std_path}")
        text = std_path.read_text(encoding="utf-8")

        # 1. Fortnightly / weekly scanning cadence
        self.assertRegex(text, r"(?i)fortnightly.*14 days", "Missing fortnightly scanning cadence for ML2")
        self.assertRegex(text, r"(?i)weekly.*ml3", "Missing weekly scanning cadence for ML3")

        # 2. 48-Hour Patch SLA
        self.assertRegex(text, r"(?i)48-hour threshold|48 hours", "Missing 48-hour patch SLA")
        self.assertRegex(text, r"(?i)cisa kev", "Missing CISA KEV prioritization")
        self.assertRegex(text, r"(?i)14 days", "Missing 14-day high SLA")

        # 3. EOL software decommissioning within 30 days
        self.assertRegex(text, r"(?i)end-of-life.*30 days|decommissioned.*30 days", "Missing 30-day EOL decommissioning rule")

        # 4. Essential Eight citations
        self.assertIn("E8-PA-ML2", text)
        self.assertIn("E8-PO-ML2", text)

    # =========================================================================
    # 6. Backward Compatibility & Regression Suite Health
    # =========================================================================

    def test_18_mkdocs_strict_build_unaffected(self):
        """Verify MkDocs strict build completes with code 0 and zero warnings."""
        env = os.environ.copy()
        env["NO_MKDOCS_2_WARNING"] = "1"
        res = subprocess.run(
            [get_mkdocs(), "build", "--strict"],
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True
        )
        self.assertEqual(
            res.returncode, 0,
            f"mkdocs build --strict failed with code {res.returncode}:\nStdout: {res.stdout}\nStderr: {res.stderr}"
        )

    def test_19_regression_suites_execution(self):
        """Verify all existing repository test suites pass with code 0."""
        suites = [
            "tests/e2e/run_all_tests.py",
            "tests/test_tier5_adversarial_challenger.py",
            "tests/test_m1_stress_challenger.py",
            "tests/test_v2_m1_adversarial_challenger.py",
            "tests/test_milestone1_adversarial_challenger2.py",
        ]
        for suite in suites:
            res = subprocess.run(
                [get_python(), str(REPO_ROOT / suite)],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True
            )
            self.assertEqual(
                res.returncode, 0,
                f"Suite {suite} failed with exit code {res.returncode}:\n{res.stdout}\n{res.stderr}"
            )


if __name__ == "__main__":
    unittest.main()
