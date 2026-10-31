"""
Milestone 1 Independent Adversarial Challenger Test Suite
Agent: challenger_v2_m1_2 (Role: teamwork_preview_challenger)
Target: Milestone 1 Deliverables
  - Boundary Value Analysis on mappings/compliance_manifest.yaml (exception date windows, review policies, thresholds)
  - Catalog-to-SoA and Registry Crosswalk Consistency (ISO 27001:2022, SOC 2 TSC, NIST CSF 2.0, GDPR, NIST 800-53, Essential Eight)
  - Architecture Decision Records Integrity (ADR-001, ADR-002, ADR-003) & MkDocs Build Impact
  - Schema Draft 2020-12 Rigor and Repository Hygiene
"""

import copy
from datetime import datetime
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


def validate_manifest_dict(data: dict) -> list[str]:
    """
    Lightweight recursive validator checking mappings/compliance_manifest.yaml
    against the constraints defined in schemas/compliance_manifest.schema.json.
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    # 1. Top-level required keys
    required_top = [
        "schema_version", "organization", "review_policy",
        "adopted_frameworks", "thresholds", "exceptions"
    ]
    for k in required_top:
        if k not in data:
            errors.append(f"Missing required top-level key: {k}")
            
    # additionalProperties: false check at top level
    allowed_top = set(required_top)
    for k in data:
        if k not in allowed_top:
            errors.append(f"Unexpected top-level property: {k}")

    # schema_version
    sv = str(data.get("schema_version", ""))
    if not re.match(r"^\d+\.\d+\.\d+$", sv):
        errors.append(f"Invalid schema_version pattern: {sv}")

    # organization
    org = data.get("organization", {})
    if not isinstance(org, dict):
        errors.append("organization must be an object")
    else:
        for req in ["name", "ciso"]:
            if req not in org or not org[req]:
                errors.append(f"organization missing required field: {req}")
        allowed_org = {"name", "ciso", "dpo", "author"}
        for k in org:
            if k not in allowed_org:
                errors.append(f"Unexpected organization property: {k}")

    # review_policy
    rp = data.get("review_policy", {})
    if not isinstance(rp, dict):
        errors.append("review_policy must be an object")
    else:
        for req in ["max_age_days", "cadence"]:
            if req not in rp:
                errors.append(f"review_policy missing required field: {req}")
        allowed_rp = {"max_age_days", "cadence", "enforce_approval"}
        for k in rp:
            if k not in allowed_rp:
                errors.append(f"Unexpected review_policy property: {k}")
        max_age = rp.get("max_age_days")
        if not isinstance(max_age, int) or max_age < 1 or max_age > 365:
            errors.append(f"review_policy.max_age_days must be integer between 1 and 365, got: {max_age}")
        cadence = rp.get("cadence")
        if cadence not in ["annual", "semi-annual", "quarterly"]:
            errors.append(f"review_policy.cadence invalid enum: {cadence}")

    # adopted_frameworks
    af = data.get("adopted_frameworks", [])
    if not isinstance(af, list) or len(af) < 4:
        errors.append("adopted_frameworks must be array with minItems: 4")
    else:
        valid_fw_ids = {
            "iso_27001_2022", "soc2_tsc_2017", "nist_csf_2_0",
            "gdpr", "nist_sp_800_53_rev5", "asd_essential_eight"
        }
        for idx, item in enumerate(af):
            if not isinstance(item, dict):
                errors.append(f"adopted_frameworks[{idx}] must be an object")
                continue
            for req in ["framework_id", "name", "target_coverage_pct", "enforcement"]:
                if req not in item:
                    errors.append(f"adopted_frameworks[{idx}] missing: {req}")
            fw_id = item.get("framework_id")
            if fw_id not in valid_fw_ids:
                errors.append(f"adopted_frameworks[{idx}].framework_id invalid: {fw_id}")
            cov = item.get("target_coverage_pct")
            if not isinstance(cov, (int, float)) or cov < 0 or cov > 100:
                errors.append(f"adopted_frameworks[{idx}].target_coverage_pct invalid: {cov}")
            enf = item.get("enforcement")
            if enf not in ["mandatory", "advisory", "planned"]:
                errors.append(f"adopted_frameworks[{idx}].enforcement invalid: {enf}")
            if "target_maturity_level" in item:
                if item["target_maturity_level"] not in ["ML1", "ML2", "ML3"]:
                    errors.append(f"Invalid target_maturity_level: {item['target_maturity_level']}")
            if "target_baseline" in item:
                if item["target_baseline"] not in ["Low", "Moderate", "High"]:
                    errors.append(f"Invalid target_baseline: {item['target_baseline']}")

    # thresholds
    th = data.get("thresholds", {})
    if not isinstance(th, dict):
        errors.append("thresholds must be an object")
    else:
        req_th = [
            "min_canonical_controls", "min_distinct_csf_subcategories",
            "min_distinct_nist_800_53_controls", "min_essential_eight_strategies"
        ]
        for r in req_th:
            if r not in th:
                errors.append(f"thresholds missing: {r}")
        if th.get("min_canonical_controls", 0) < 55:
            errors.append("min_canonical_controls must be >= 55")
        if th.get("min_distinct_csf_subcategories", 0) < 45:
            errors.append("min_distinct_csf_subcategories must be >= 45")
        if th.get("min_distinct_nist_800_53_controls", 0) < 85:
            errors.append("min_distinct_nist_800_53_controls must be >= 85")
        if th.get("min_essential_eight_strategies") != 8:
            errors.append("min_essential_eight_strategies must be exactly 8")

    # exceptions
    exs = data.get("exceptions", [])
    if not isinstance(exs, list):
        errors.append("exceptions must be an array")
    else:
        req_ex = [
            "id", "control_id", "title", "justification", "approved_by",
            "approval_date", "expiration_date", "risk_level", "status",
            "compensating_controls"
        ]
        allowed_ex = set(req_ex)
        for idx, ex in enumerate(exs):
            if not isinstance(ex, dict):
                errors.append(f"exceptions[{idx}] must be an object")
                continue
            for r in req_ex:
                if r not in ex:
                    errors.append(f"exceptions[{idx}] missing field: {r}")
            for k in ex:
                if k not in allowed_ex:
                    errors.append(f"Unexpected exceptions[{idx}] property: {k}")
            
            # regex for id
            ex_id = str(ex.get("id", ""))
            if not re.match(r"^EX-\d{4}-\d{3,}$", ex_id):
                errors.append(f"exceptions[{idx}].id pattern mismatch: {ex_id}")

            # date formats
            app_str = str(ex.get("approval_date", ""))
            exp_str = str(ex.get("expiration_date", ""))
            d_app = None
            d_exp = None
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", app_str):
                errors.append(f"exceptions[{idx}].approval_date bad format: {app_str}")
            else:
                try:
                    d_app = datetime.strptime(app_str, "%Y-%m-%d")
                except ValueError as ve:
                    errors.append(f"exceptions[{idx}].approval_date invalid calendar date: {ve}")

            if not re.match(r"^\d{4}-\d{2}-\d{2}$", exp_str):
                errors.append(f"exceptions[{idx}].expiration_date bad format: {exp_str}")
            else:
                try:
                    d_exp = datetime.strptime(exp_str, "%Y-%m-%d")
                except ValueError as ve:
                    errors.append(f"exceptions[{idx}].expiration_date invalid calendar date: {ve}")

            # Duration check (business logic / policy rule: 0 < duration <= 90 days)
            if d_app and d_exp:
                diff = (d_exp - d_app).days
                if diff <= 0:
                    errors.append(f"exceptions[{idx}] expiration must be strictly after approval (diff={diff} <= 0)")
                elif diff > 90:
                    errors.append(f"exceptions[{idx}] window {diff} days exceeds maximum allowable 90-day window")

            # risk_level enum
            rl = ex.get("risk_level")
            if rl not in ["Low", "Medium", "High", "Critical"]:
                errors.append(f"exceptions[{idx}].risk_level invalid enum: {rl}")

            # status enum
            st = ex.get("status")
            if st not in ["active", "expired", "remediated"]:
                errors.append(f"exceptions[{idx}].status invalid enum: {st}")

            # compensating_controls array
            cc = ex.get("compensating_controls", [])
            if not isinstance(cc, list) or len(cc) < 1:
                errors.append(f"exceptions[{idx}].compensating_controls must be array with minItems: 1")
            else:
                for cidx, c_item in enumerate(cc):
                    if not isinstance(c_item, str) or not c_item.strip():
                        errors.append(f"exceptions[{idx}].compensating_controls[{cidx}] must be non-empty string")

    return errors


class TestMilestone1AdversarialChallenger(unittest.TestCase):
    """
    Independent Adversarial Stress Suite verifying Milestone 1 deliverables.
    """

    @classmethod
    def setUpClass(cls):
        cls.python_bin = get_python()
        cls.mkdocs_bin = get_mkdocs()
        cls.manifest_path = REPO_ROOT / "mappings" / "compliance_manifest.yaml"
        cls.registry_path = REPO_ROOT / "mappings" / "framework_registry.yaml"
        cls.soa_path = REPO_ROOT / "docs" / "01_ISMS_Framework" / "05_Statement_of_Applicability_SoA.md"
        cls.catalogs_dir = REPO_ROOT / "mappings" / "catalogs"
        cls.schemas_dir = REPO_ROOT / "schemas"
        cls.adr_dir = REPO_ROOT / "architecture" / "adr"

        # Load canonical objects
        with open(cls.manifest_path, "r", encoding="utf-8") as f:
            cls.manifest_data = yaml.safe_load(f)

        with open(cls.registry_path, "r", encoding="utf-8") as f:
            cls.registry_data = yaml.safe_load(f)

    # =========================================================================
    # SECTION 1: BOUNDARY VALUE ANALYSIS ON COMPLIANCE MANIFEST
    # =========================================================================

    def test_01_manifest_production_file_validity(self):
        """Verify the production compliance_manifest.yaml conforms strictly to schema and policy rules."""
        errors = validate_manifest_dict(self.manifest_data)
        self.assertEqual(errors, [], f"Compliance manifest validation errors: {errors}")

    def test_02_review_policy_max_age_days_boundaries(self):
        """Boundary analysis on review_policy.max_age_days: 0, 1, 365, 366, -1."""
        base = copy.deepcopy(self.manifest_data)

        # Boundary 1: max_age_days = 0 (INVALID)
        base["review_policy"]["max_age_days"] = 0
        self.assertTrue(any("max_age_days" in e for e in validate_manifest_dict(base)))

        # Boundary 2: max_age_days = 1 (VALID minimum)
        base["review_policy"]["max_age_days"] = 1
        self.assertEqual(validate_manifest_dict(base), [])

        # Boundary 3: max_age_days = 365 (VALID maximum)
        base["review_policy"]["max_age_days"] = 365
        self.assertEqual(validate_manifest_dict(base), [])

        # Boundary 4: max_age_days = 366 (INVALID, exceeds annual max)
        base["review_policy"]["max_age_days"] = 366
        self.assertTrue(any("max_age_days" in e for e in validate_manifest_dict(base)))

        # Boundary 5: negative value (INVALID)
        base["review_policy"]["max_age_days"] = -30
        self.assertTrue(any("max_age_days" in e for e in validate_manifest_dict(base)))

    def test_03_exception_window_exact_boundary_values(self):
        """
        Boundary value analysis on security exception duration (<= 90-day window):
        -1 days, 0 days, 1 day, 86 days, 89 days, 90 days, 91 days, 100 days.
        """
        base = copy.deepcopy(self.manifest_data)
        app_date = "2026-10-26"

        test_cases = [
            ("2026-10-25", -1, False, "Expiration before approval date"),
            ("2026-10-26", 0, False, "Zero-day duration (same day)"),
            ("2026-10-27", 1, True, "1-day duration (minimum positive window)"),
            ("2027-01-20", 86, True, "86-day duration (EX-2026-001)"),
            ("2027-01-23", 89, True, "89-day duration (boundary - 1)"),
            ("2027-01-24", 90, True, "90-day duration (exact maximum allowed boundary)"),
            ("2027-01-25", 91, False, "91-day duration (boundary + 1, must be rejected)"),
            ("2027-02-03", 100, False, "100-day duration (over allowable boundary)"),
            ("2027-10-26", 365, False, "365-day annual duration (forbidden for exceptions)"),
        ]

        for exp_date, expected_days, should_pass, desc in test_cases:
            # Calculate actual diff
            d1 = datetime.strptime(app_date, "%Y-%m-%d")
            d2 = datetime.strptime(exp_date, "%Y-%m-%d")
            actual_days = (d2 - d1).days
            self.assertEqual(actual_days, expected_days, f"Date math check failed for {desc}")

            # Inject into test manifest
            base["exceptions"] = [{
                "id": "EX-2026-999",
                "control_id": "CC-AC-02",
                "title": f"Boundary Test {desc}",
                "justification": "Testing exact boundary conditions for 90-day exception window.",
                "approved_by": "CISO",
                "approval_date": app_date,
                "expiration_date": exp_date,
                "risk_level": "Medium",
                "status": "active",
                "compensating_controls": ["Automated continuous telemetry."]
            }]

            errs = validate_manifest_dict(base)
            if should_pass:
                self.assertEqual(errs, [], f"Expected PASS for {desc} ({actual_days} days), but got errors: {errs}")
            else:
                self.assertTrue(len(errs) > 0, f"Expected REJECTION for {desc} ({actual_days} days), but passed unexpectedly!")

    def test_04_exception_calendar_dates_and_leap_years(self):
        """Test calendar validity: valid leap day, invalid leap day in non-leap year, and non-existent dates."""
        base = copy.deepcopy(self.manifest_data)

        # 1. 2028 is a leap year -> 2028-02-29 is VALID
        base["exceptions"][0]["approval_date"] = "2028-01-01"
        base["exceptions"][0]["expiration_date"] = "2028-02-29" # 59 days
        self.assertEqual(validate_manifest_dict(base), [])

        # 2. 2027 is NOT a leap year -> 2027-02-29 is INVALID calendar date
        base["exceptions"][0]["approval_date"] = "2027-01-01"
        base["exceptions"][0]["expiration_date"] = "2027-02-29"
        errs = validate_manifest_dict(base)
        self.assertTrue(any("invalid calendar date" in e for e in errs), f"Expected leap date error, got: {errs}")

        # 3. Non-existent day in month: 2026-04-31 (April has 30 days)
        base["exceptions"][0]["approval_date"] = "2026-03-01"
        base["exceptions"][0]["expiration_date"] = "2026-04-31"
        errs = validate_manifest_dict(base)
        self.assertTrue(any("invalid calendar date" in e for e in errs), f"Expected calendar date error for April 31, got: {errs}")

        # 4. Bad format strings: '2026/10/26' and '26-10-2026'
        base["exceptions"][0]["approval_date"] = "2026/10/26"
        base["exceptions"][0]["expiration_date"] = "2026-11-20"
        errs = validate_manifest_dict(base)
        self.assertTrue(any("bad format" in e for e in errs))

    def test_05_exception_compensating_controls_enforcement(self):
        """Stress: Exception with empty compensating controls list must be rejected."""
        base = copy.deepcopy(self.manifest_data)
        base["exceptions"][0]["compensating_controls"] = []
        errs = validate_manifest_dict(base)
        self.assertTrue(any("compensating_controls" in e for e in errs))

        # Blank string compensating control
        base["exceptions"][0]["compensating_controls"] = ["   "]
        errs = validate_manifest_dict(base)
        self.assertTrue(any("compensating_controls" in e for e in errs))

    def test_06_manifest_exceptions_reference_valid_canonical_controls(self):
        """Verify all exception control_id references exist in the canonical registry."""
        canonical_ids = set(c["id"] for c in self.registry_data.get("controls", []))
        self.assertGreater(len(canonical_ids), 50)

        for ex in self.manifest_data["exceptions"]:
            cid = ex["control_id"]
            self.assertIn(cid, canonical_ids, f"Exception {ex['id']} references unknown control ID: {cid}")

    def test_07_manifest_additional_properties_rejection(self):
        """Verify additionalProperties: false is strictly enforced on root and sub-objects."""
        base = copy.deepcopy(self.manifest_data)
        base["unauthorized_root_field"] = "malicious_payload"
        errs = validate_manifest_dict(base)
        self.assertTrue(any("Unexpected top-level property" in e for e in errs))

        base = copy.deepcopy(self.manifest_data)
        base["exceptions"][0]["backdoor_override"] = True
        errs = validate_manifest_dict(base)
        self.assertTrue(any("Unexpected exceptions[0] property" in e for e in errs))

    # =========================================================================
    # SECTION 2: CATALOG-TO-SOA & FRAMEWORK CONSISTENCY CROSS-CHECKS
    # =========================================================================

    def test_08_iso_27001_catalog_matches_soa_exactly(self):
        """
        Cross-check: Verify all 93 ISO 27001:2022 controls in catalog match the SoA controls.
        Ensures zero omitted, zero invented, and zero mismatched control IDs.
        """
        iso_cat_path = self.catalogs_dir / "iso_27001_2022.yaml"
        self.assertTrue(iso_cat_path.exists())

        with open(iso_cat_path, "r", encoding="utf-8") as f:
            iso_cat = yaml.safe_load(f)

        cat_controls = {c["id"]: c["title"].strip() for c in iso_cat["controls"]}
        self.assertEqual(len(cat_controls), 93, f"Expected 93 controls in catalog, got {len(cat_controls)}")
        self.assertEqual(iso_cat["total_controls"], 93)

        # Extract controls and titles from Statement of Applicability
        soa_text = self.soa_path.read_text(encoding="utf-8")
        matches = re.findall(r"^\|\s*(A\.[5-8]\.\d+)\s*\|\s*([^\|]+?)\s*\|", soa_text, re.MULTILINE)
        soa_controls = {m[0]: m[1].strip() for m in matches}
        self.assertEqual(len(soa_controls), 93, f"Expected 93 controls in SoA, found {len(soa_controls)}")

        # Bidirectional set equality
        diff_cat_minus_soa = set(cat_controls.keys()) - set(soa_controls.keys())
        diff_soa_minus_cat = set(soa_controls.keys()) - set(cat_controls.keys())
        self.assertEqual(diff_cat_minus_soa, set(), f"In catalog but missing in SoA: {diff_cat_minus_soa}")
        self.assertEqual(diff_soa_minus_cat, set(), f"In SoA but missing in catalog: {diff_soa_minus_cat}")

        # Exact title conformance check
        for cid, ctitle in cat_controls.items():
            stitle = soa_controls[cid]
            self.assertEqual(ctitle.lower(), stitle.lower(), f"Title mismatch for {cid}: catalog '{ctitle}' vs SoA '{stitle}'")

    def test_09_soc2_tsc_criteria_complete_and_valid(self):
        """
        Cross-check: Verify all 61 SOC 2 criteria are valid in catalog,
        and that all SOC 2 references in SoA and framework_registry are valid catalog criteria.
        """
        soc2_cat_path = self.catalogs_dir / "soc2_tsc_2017.yaml"
        self.assertTrue(soc2_cat_path.exists())

        with open(soc2_cat_path, "r", encoding="utf-8") as f:
            soc2_cat = yaml.safe_load(f)

        criteria_list = soc2_cat["controls"]
        self.assertEqual(len(criteria_list), 61, f"Expected 61 SOC 2 criteria, got {len(criteria_list)}")
        self.assertEqual(soc2_cat["total_controls"], 61)

        valid_soc2_ids = set(c["id"] for c in criteria_list)

        # Check breakdown
        cc_ids = [cid for cid in valid_soc2_ids if cid.startswith("CC")]
        a_ids = [cid for cid in valid_soc2_ids if cid.startswith("A1")]
        c_ids = [cid for cid in valid_soc2_ids if cid.startswith("C1")]
        pi_ids = [cid for cid in valid_soc2_ids if cid.startswith("PI")]
        p_ids = [cid for cid in valid_soc2_ids if cid.startswith("P") and not cid.startswith("PI")]

        self.assertEqual(len(cc_ids), 33, f"Expected 33 Common Criteria, got {len(cc_ids)}")
        self.assertEqual(len(a_ids), 3, f"Expected 3 Availability criteria, got {len(a_ids)}")
        self.assertEqual(len(c_ids), 2, f"Expected 2 Confidentiality criteria, got {len(c_ids)}")
        self.assertEqual(len(pi_ids), 5, f"Expected 5 Processing Integrity criteria, got {len(pi_ids)}")
        self.assertEqual(len(p_ids), 18, f"Expected 18 Privacy criteria, got {len(p_ids)}")

        # Verify SoA SOC 2 references
        soa_text = self.soa_path.read_text(encoding="utf-8")
        soa_lines = [l for l in soa_text.splitlines() if l.strip().startswith("| A.")]
        for line in soa_lines:
            cols = [c.strip() for c in line.split("|")]
            if len(cols) >= 10:
                soc2_col = cols[8]
                tokens = [t.strip() for t in re.split(r"[,;]", soc2_col) if t.strip()]
                for tok in tokens:
                    if tok in ["Privacy Category", "None"]:
                        continue
                    self.assertIn(tok, valid_soc2_ids, f"SoA line '{cols[1]}' has invalid SOC 2 citation: {tok}")

        # Verify framework_registry SOC 2 references
        for control in self.registry_data.get("controls", []):
            m = control.get("mappings", {})
            for key in ["soc2_tsc", "soc2_tsc_2017"]:
                for ref in m.get(key, []):
                    ref_id = ref.get("id") if isinstance(ref, dict) else ref
                    if ref_id and ref_id not in ["None", "None (New 2022)"]:
                        self.assertIn(ref_id, valid_soc2_ids, f"Control {control['id']} mapped invalid SOC 2 ID: {ref_id}")

    def test_10_all_six_reference_catalogs_conformance(self):
        """Verify all 6 reference catalogs conform to schema, counts, and authorities."""
        with open(self.schemas_dir / "catalog.schema.json", "r", encoding="utf-8") as f:
            cat_schema = json.load(f)

        allowed_catalog_ids = set(cat_schema["properties"]["id"]["enum"])
        expected_catalogs = {
            "iso_27001_2022": 93,
            "soc2_tsc_2017": 61,
            "nist_csf_2_0": 106,
            "gdpr": 26,
            "nist_sp_800_53_rev5": 177,
            "asd_essential_eight": 24,
        }

        self.assertEqual(set(expected_catalogs.keys()), allowed_catalog_ids)

        found_catalogs = list(self.catalogs_dir.glob("*.yaml"))
        self.assertEqual(len(found_catalogs), 6, f"Expected 6 catalog YAML files, found: {len(found_catalogs)}")

        for cat_file in found_catalogs:
            with open(cat_file, "r", encoding="utf-8") as f:
                cat = yaml.safe_load(f)

            cid = cat.get("id")
            self.assertIn(cid, expected_catalogs, f"Unexpected catalog ID in {cat_file}: {cid}")
            self.assertTrue(cat.get("name"), f"Missing name in {cat_file}")
            self.assertTrue(cat.get("version"), f"Missing version in {cat_file}")
            self.assertTrue(cat.get("authority"), f"Missing authority in {cat_file}")
            self.assertEqual(cat.get("total_controls"), len(cat.get("controls", [])), f"Count mismatch in {cat_file}")
            self.assertEqual(cat.get("total_controls"), expected_catalogs[cid], f"Catalog {cid} count mismatch")

            # Check individual entries
            for entry in cat["controls"]:
                self.assertTrue(entry.get("id"), f"Missing entry id in {cat_file}")
                self.assertTrue(entry.get("title"), f"Missing entry title in {cat_file}")

            # Specific check for Essential Eight
            if cid == "asd_essential_eight":
                for entry in cat["controls"]:
                    self.assertIn(entry.get("maturity_level"), ["ML1", "ML2", "ML3"])
                    self.assertTrue(isinstance(entry.get("mapped_ism_ids"), list))
                    self.assertGreater(len(entry["mapped_ism_ids"]), 0)

            # Specific check for NIST 800-53
            if cid == "nist_sp_800_53_rev5":
                families = set(entry["family"] for entry in cat["controls"])
                self.assertEqual(len(families), 20, f"Expected 20 NIST 800-53 families, got {len(families)}")

    # =========================================================================
    # SECTION 3: ARCHITECTURE DECISION RECORDS (ADR) INTEGRITY & MKDOCS
    # =========================================================================

    def test_11_adr_directory_isolation(self):
        """
        Verify ADRs are isolated in architecture/adr/ and zero ADRs exist in docs/.
        This prevents pollution of the public documentation portal and strict navigation assertions.
        """
        self.assertTrue(self.adr_dir.exists(), "architecture/adr/ must exist")
        adr_files = list(self.adr_dir.glob("ADR-*.md"))
        self.assertEqual(len(adr_files), 3, f"Expected 3 ADR files in architecture/adr, found: {len(adr_files)}")

        # Verify docs/ contains zero ADR files
        docs_adrs = list((REPO_ROOT / "docs").rglob("*ADR*")) + list((REPO_ROOT / "docs").rglob("*adr*"))
        self.assertEqual(docs_adrs, [], f"ADR files improperly placed inside docs/: {docs_adrs}")

    def test_12_adr_headers_structure_and_mandatory_sections(self):
        """
        Verify every ADR has:
        - Valid H1 title (# ADR-XXX: ...)
        - Metadata: Status, Date, Deciders, Technical Context
        - Sections: Context and Problem Statement, Decision Drivers, Considered Options,
                    Decision Outcome, Pros and Cons, References
        """
        expected_adrs = [
            "ADR-001-yaml-sot-and-oscal-export.md",
            "ADR-002-mkdocs-zensical-migration.md",
            "ADR-003-essential-eight-and-nist-800-53-mapping.md"
        ]

        mandatory_sections = [
            "## Context and Problem Statement",
            "## Decision Drivers",
            "## Considered Options",
            "## Decision Outcome",
            "## Pros and Cons",
            "## References"
        ]

        for fname in expected_adrs:
            fpath = self.adr_dir / fname
            self.assertTrue(fpath.exists(), f"Missing ADR: {fname}")
            content = fpath.read_text(encoding="utf-8")

            # Check title
            self.assertTrue(re.search(r"^# ADR-\d{3}: .+", content, re.MULTILINE), f"Missing valid H1 title in {fname}")

            # Check metadata
            self.assertTrue(re.search(r"[-*]\s*\*\*Status\*\*", content), f"Missing Status in {fname}")
            self.assertTrue(re.search(r"[-*]\s*\*\*Date\*\*", content), f"Missing Date in {fname}")
            self.assertTrue(re.search(r"[-*]\s*\*\*Deciders\*\*", content), f"Missing Deciders in {fname}")
            self.assertTrue(re.search(r"[-*]\s*\*\*Technical Context\*\*", content), f"Missing Technical Context in {fname}")

            # Check sections
            for sec in mandatory_sections:
                self.assertIn(sec, content, f"Missing section '{sec}' in {fname}")

    def test_13_adr_substantive_content_validation(self):
        """Verify substantive technical content in each ADR."""
        adr1 = (self.adr_dir / "ADR-001-yaml-sot-and-oscal-export.md").read_text(encoding="utf-8")
        self.assertIn("OSCAL v1.2.0", adr1)
        self.assertIn("UUIDv5", adr1)
        self.assertIn("mappings/framework_registry.yaml", adr1)

        adr2 = (self.adr_dir / "ADR-002-mkdocs-zensical-migration.md").read_text(encoding="utf-8")
        self.assertIn("May 5, 2027", adr2)
        self.assertIn("NO_MKDOCS_2_WARNING=1", adr2)
        self.assertIn("Zensical", adr2)

        adr3 = (self.adr_dir / "ADR-003-essential-eight-and-nist-800-53-mapping.md").read_text(encoding="utf-8")
        self.assertIn("Essential Eight", adr3)
        self.assertIn("ML1", adr3)
        self.assertIn("ML2", adr3)
        self.assertIn("NIST SP 800-53 Rev. 5", adr3)
        self.assertIn("Moderate", adr3)

    def test_14_mkdocs_strict_build_unaffected_and_zero_warnings(self):
        """Verify mkdocs build --strict succeeds with code 0 and zero warnings with NO_MKDOCS_2_WARNING=1."""
        env = os.environ.copy()
        env["NO_MKDOCS_2_WARNING"] = "1"

        res = subprocess.run(
            [self.mkdocs_bin, "build", "--strict"],
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True
        )

        self.assertEqual(
            res.returncode, 0,
            f"mkdocs build --strict failed!\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
        )
        self.assertTrue((REPO_ROOT / "site" / "index.html").exists(), "Site output index.html was not created")

    # =========================================================================
    # SECTION 4: REPOSITORY HYGIENE & OPEN-SOURCE LICENSING
    # =========================================================================

    def test_15_root_license_file_apache_2(self):
        """Verify root LICENSE file exists and specifies Apache License Version 2.0 with copyright notice."""
        license_path = REPO_ROOT / "LICENSE"
        self.assertTrue(license_path.exists(), "Root LICENSE file missing")
        content = license_path.read_text(encoding="utf-8")
        self.assertIn("Apache License", content)
        self.assertIn("Version 2.0", content)
        self.assertIn("Copyright 2026 Information Security Team / security-standards-template contributors", content)

    def test_16_no_untracked_serve_logs_or_garbage(self):
        """Verify no serve_*.txt, zserve_*.txt, or temp debug files exist in the working directory."""
        serve_files = list(REPO_ROOT.glob("*serve_*.txt"))
        self.assertEqual(serve_files, [], f"Found untracked serve log files: {serve_files}")

    def test_17_gitignore_protection_patterns(self):
        """Verify .gitignore contains patterns for serve logs, sarif reports, and dist/."""
        gi_path = REPO_ROOT / ".gitignore"
        self.assertTrue(gi_path.exists())
        content = gi_path.read_text(encoding="utf-8")
        self.assertIn("serve_*.txt", content)
        self.assertIn("zserve_*.txt", content)
        self.assertIn("*.sarif", content)
        self.assertIn("dist/", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
