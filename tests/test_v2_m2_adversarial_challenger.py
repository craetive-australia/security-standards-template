#!/usr/bin/env python3
"""
tests/test_v2_m2_adversarial_challenger.py
Adversarial Stress Test Suite for Milestone 2 Deliverables:
- Repo-wide elimination of all 13 retired/invalid NIST CSF 2.0 IDs
- Authoritative reference catalog membership across all frameworks
- Distinct count assertions: >= 45 CSF 2.0, >= 85 NIST SP 800-53 across all 20 families, all 8 Essential Eight strategies across ML1-ML3
- OSCAL relationship semantics conformance (equivalent-to, subset-of, superset-of, intersects-with)
- Registry v2.0 schema conformance and negative mutation attacks
- Policy & Standard Essential Eight ML2/ML3 technical threshold harmonization
- Empirical citation integrity across docs/ against authoritative reference catalogs
"""

import copy
import glob
import json
import re
import sys
import unittest
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tests"))
from test_v2_m1_adversarial_challenger import validate_against_schema


class TestMilestone2AdversarialChallenger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry_path = REPO_ROOT / "mappings" / "framework_registry.yaml"
        with open(cls.registry_path, "r", encoding="utf-8") as f:
            cls.registry_raw = f.read()
            cls.registry = yaml.safe_load(cls.registry_raw)

        cls.schema_path = REPO_ROOT / "schemas" / "framework_registry.schema.json"
        with open(cls.schema_path, "r", encoding="utf-8") as f:
            cls.registry_schema = json.load(f)

        # Catalogs
        with open(REPO_ROOT / "mappings" / "catalogs" / "nist_csf_2_0.yaml", "r", encoding="utf-8") as f:
            cls.cat_csf = yaml.safe_load(f)
            cls.valid_csf_ids = {c["id"] for c in cls.cat_csf["controls"]}

        with open(REPO_ROOT / "mappings" / "catalogs" / "nist_sp_800_53_rev5.yaml", "r", encoding="utf-8") as f:
            cls.cat_53 = yaml.safe_load(f)
            cls.valid_53_ids = {c["id"] for c in cls.cat_53["controls"]}

        with open(REPO_ROOT / "mappings" / "catalogs" / "asd_essential_eight.yaml", "r", encoding="utf-8") as f:
            cls.cat_e8 = yaml.safe_load(f)
            cls.valid_e8_ids = {c["id"] for c in cls.cat_e8["controls"]}

        with open(REPO_ROOT / "mappings" / "catalogs" / "iso_27001_2022.yaml", "r", encoding="utf-8") as f:
            cls.cat_iso = yaml.safe_load(f)
            cls.valid_iso_ids = {c["id"] for c in cls.cat_iso["controls"]}

        with open(REPO_ROOT / "mappings" / "catalogs" / "soc2_tsc_2017.yaml", "r", encoding="utf-8") as f:
            cls.cat_soc2 = yaml.safe_load(f)
            cls.valid_soc2_ids = {c["id"] for c in cls.cat_soc2["controls"]}

        with open(REPO_ROOT / "mappings" / "catalogs" / "gdpr.yaml", "r", encoding="utf-8") as f:
            cls.cat_gdpr = yaml.safe_load(f)
            cls.valid_gdpr_ids = {c["id"] for c in cls.cat_gdpr["controls"]}

    # -------------------------------------------------------------------------
    # 1. Retired & Invalid NIST CSF 2.0 IDs Repo-Wide Scan
    # -------------------------------------------------------------------------
    def test_01_repo_wide_exhaustion_13_retired_csf_ids(self):
        """
        Adversarially search the entire repository (excluding git/venv/agents metadata)
        for the 13 retired/invalid CSF IDs:
        GV.CO-01, GV.CO-02, PR.DS-03, PR.DS-05, PR.DS-07, PR.DS-09,
        PR.PS-07, PR.PS-08, PR.PS-09, DE.CM-04, RS.AN-04, RS.AN-05, RS.RP-01.
        Must return exactly 0 matches across all .md, .yaml, .yml, .json, .py, .txt.
        """
        retired_pattern = re.compile(
            r"\b(GV\.CO-0[12]|PR\.DS-0[3579]|PR\.PS-0[789]|DE\.CM-04|RS\.AN-0[45]|RS\.RP-01)\b"
        )
        found_matches = []
        extensions = (".md", ".yaml", ".yml", ".json", ".py", ".txt")

        for p in REPO_ROOT.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in extensions:
                continue
            # Skip virtual environments, git metadata, and agent orchestration scratch folders
            rel_str = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
            if rel_str.startswith(".venv/") or rel_str.startswith(".git/") or rel_str.startswith(".agents/") or rel_str.startswith("site/"):
                continue

            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                for i, line in enumerate(content.splitlines(), 1):
                    # Exclude test files that define the retired IDs list for negative scanning
                    if "test_v2_m2_adversarial_challenger.py" in rel_str or "test_tier4_governance_audit.py" in rel_str:
                        continue
                    if retired_pattern.search(line):
                        found_matches.append((rel_str, i, line.strip()))
            except Exception as e:
                self.fail(f"Failed to read file {rel_str}: {e}")

        self.assertEqual(
            len(found_matches), 0,
            f"Adversarial scan detected retired NIST CSF 2.0 IDs: {found_matches}"
        )

    def test_02_all_registry_csf_ids_in_official_catalog(self):
        """Verify 100% of mapped CSF 2.0 IDs in registry exist in mappings/catalogs/nist_csf_2_0.yaml."""
        invalid_ids = []
        for c in self.registry.get("controls", []):
            cid = c["id"]
            for csf_id in c.get("mappings", {}).get("nist_csf_2_0", []):
                if csf_id not in self.valid_csf_ids:
                    invalid_ids.append((cid, csf_id))

        self.assertEqual(
            len(invalid_ids), 0,
            f"Registry contains CSF IDs not in authoritative catalog: {invalid_ids}"
        )

    def test_03_csf_subcategory_distinct_count_and_function_spread(self):
        """
        Verify distinct valid CSF 2.0 subcategories in registry >= 45,
        and all 6 CSF 2.0 functions (GV, ID, PR, DE, RS, RC) are represented.
        """
        distinct_csf = set()
        functions = set()
        for c in self.registry.get("controls", []):
            for csf_id in c.get("mappings", {}).get("nist_csf_2_0", []):
                distinct_csf.add(csf_id)
                functions.add(csf_id.split(".")[0])

        self.assertGreaterEqual(
            len(distinct_csf), 45,
            f"Expected >= 45 distinct CSF 2.0 subcategories, found {len(distinct_csf)}"
        )
        expected_functions = {"GV", "ID", "PR", "DE", "RS", "RC"}
        self.assertEqual(
            functions, expected_functions,
            f"Expected all 6 CSF 2.0 functions, found {functions}"
        )

    # -------------------------------------------------------------------------
    # 2. NIST SP 800-53 Rev. 5 & ASD Essential Eight Mappings
    # -------------------------------------------------------------------------
    def test_04_nist_800_53_count_and_all_20_families_covered(self):
        """
        Verify distinct mapped NIST SP 800-53 Rev. 5 controls >= 85,
        and all 20 control families (AC-SR) are represented with at least 1 control.
        """
        distinct_53 = set()
        families = set()
        for c in self.registry.get("controls", []):
            for m in c.get("mappings", {}).get("nist_sp_800_53_rev5", []):
                cid = m["id"]
                distinct_53.add(cid)
                families.add(cid.split("-")[0])

        self.assertGreaterEqual(
            len(distinct_53), 85,
            f"Expected >= 85 distinct NIST 800-53 controls, found {len(distinct_53)}"
        )
        expected_families = {
            "AC", "AT", "AU", "CA", "CM", "CP", "IA", "IR", "MA", "MP",
            "PE", "PL", "PM", "PS", "PT", "RA", "SA", "SC", "SI", "SR"
        }
        self.assertEqual(
            families, expected_families,
            f"Missing NIST 800-53 families: {expected_families - families}"
        )

    def test_05_all_mapped_800_53_controls_in_catalog(self):
        """Verify 100% of mapped NIST 800-53 controls exist in mappings/catalogs/nist_sp_800_53_rev5.yaml."""
        invalid_53 = []
        for c in self.registry.get("controls", []):
            cid = c["id"]
            for m in c.get("mappings", {}).get("nist_sp_800_53_rev5", []):
                mid = m["id"]
                if mid not in self.valid_53_ids:
                    invalid_53.append((cid, mid))

        self.assertEqual(
            len(invalid_53), 0,
            f"Registry contains NIST 800-53 controls not in catalog: {invalid_53}"
        )

    def test_06_essential_eight_all_8_strategies_and_ml_levels(self):
        """
        Verify ASD Essential Eight mappings cover all 8 strategies:
        AC, AH, AP, MF, OM, PA, PO, RB across ML1, ML2, and ML3.
        """
        strategies = set()
        ml_levels = set()
        for c in self.registry.get("controls", []):
            for m in c.get("mappings", {}).get("asd_essential_eight", []):
                mid = m["id"]  # Format: E8-XX-ML[1-3]
                parts = mid.split("-")
                strategies.add(parts[1])
                ml_levels.add(parts[2])

        expected_strategies = {"AC", "AH", "AP", "MF", "OM", "PA", "PO", "RB"}
        self.assertEqual(
            strategies, expected_strategies,
            f"Missing Essential Eight strategies: {expected_strategies - strategies}"
        )
        expected_ml = {"ML1", "ML2", "ML3"}
        self.assertEqual(
            ml_levels, expected_ml,
            f"Missing Essential Eight maturity levels: {expected_ml - ml_levels}"
        )

    def test_07_all_mapped_essential_eight_controls_in_catalog(self):
        """Verify 100% of mapped Essential Eight controls exist in mappings/catalogs/asd_essential_eight.yaml."""
        invalid_e8 = []
        for c in self.registry.get("controls", []):
            cid = c["id"]
            for m in c.get("mappings", {}).get("asd_essential_eight", []):
                mid = m["id"]
                if mid not in self.valid_e8_ids:
                    invalid_e8.append((cid, mid))

        self.assertEqual(
            len(invalid_e8), 0,
            f"Registry contains Essential Eight controls not in catalog: {invalid_e8}"
        )

    def test_08_oscal_relationship_semantics_validity(self):
        """
        Verify every mapped NIST 800-53 and Essential Eight control uses valid OSCAL semantics:
        'equivalent-to', 'subset-of', 'superset-of', 'intersects-with'.
        """
        valid_rels = {"equivalent-to", "subset-of", "superset-of", "intersects-with"}
        invalid_rels = []

        for c in self.registry.get("controls", []):
            cid = c["id"]
            for m in c.get("mappings", {}).get("nist_sp_800_53_rev5", []):
                rel = m.get("relationship")
                if rel not in valid_rels:
                    invalid_rels.append((cid, m.get("id"), rel))
            for m in c.get("mappings", {}).get("asd_essential_eight", []):
                rel = m.get("relationship")
                if rel not in valid_rels:
                    invalid_rels.append((cid, m.get("id"), rel))

        self.assertEqual(
            len(invalid_rels), 0,
            f"Invalid OSCAL relationships detected: {invalid_rels}"
        )

    def test_09_legacy_mappings_backward_compatibility(self):
        """
        Verify backward compatibility:
        iso_27001_2022, iso_27001_2013_legacy, soc2_tsc_2017, nist_csf_2_0, gdpr_articles
        must remain lists of strings (not objects).
        Verify ZERO 'None' string literals or None values in iso_27001_2013_legacy.
        """
        for c in self.registry.get("controls", []):
            cid = c["id"]
            m = c.get("mappings", {})
            for key in ["iso_27001_2022", "iso_27001_2013_legacy", "soc2_tsc_2017", "nist_csf_2_0", "gdpr_articles"]:
                val = m.get(key)
                self.assertIsInstance(val, list, f"Mapping {key} in {cid} is not a list")
                for item in val:
                    self.assertIsInstance(item, str, f"Item in {key} of {cid} is not a string: {item}")
                    self.assertNotEqual(item, "None", f"Found 'None' literal in {key} of {cid}")
                    self.assertNotEqual(item, "", f"Found empty string in {key} of {cid}")

    # -------------------------------------------------------------------------
    # 3. Registry v2.0 Schema & Structure Integrity
    # -------------------------------------------------------------------------
    def test_10_registry_syntactic_purity(self):
        """
        Verify raw text of mappings/framework_registry.yaml:
        - schema_version is '2.0.0'
        - ZERO occurrences of YAML anchors or aliases (*id001, &id001)
        - ZERO occurrences of '- None'
        - ZERO duplicate legacy keys: implementing_documents, soc2_tsc, gdpr, canonical_controls
        """
        self.assertEqual(self.registry.get("schema_version"), "2.0.0")
        self.assertNotIn("*id001", self.registry_raw)
        self.assertNotIn("&id001", self.registry_raw)
        self.assertNotIn("- None", self.registry_raw)
        self.assertNotIn("canonical_controls:", self.registry_raw)

        # Check duplicate keys inside control dicts
        for c in self.registry.get("controls", []):
            cid = c["id"]
            self.assertNotIn("implementing_documents", c, f"Found deprecated implementing_documents in {cid}")
            self.assertNotIn("soc2_tsc", c.get("mappings", {}), f"Found deprecated soc2_tsc in {cid}")
            self.assertNotIn("gdpr", c.get("mappings", {}), f"Found deprecated gdpr in {cid}")

    def test_11_registry_controls_count_and_uniqueness(self):
        """Verify exactly 98 unique canonical controls exist in registry."""
        controls = self.registry.get("controls", [])
        self.assertEqual(len(controls), 98, f"Expected 98 canonical controls, got {len(controls)}")
        ids = [c["id"] for c in controls]
        self.assertEqual(len(ids), len(set(ids)), f"Duplicate canonical control IDs found: {len(ids) - len(set(ids))}")

    def test_12_implementing_docs_exist_on_disk(self):
        """Verify all implementing_docs referenced across all 98 controls exist on disk."""
        missing_docs = []
        for c in self.registry.get("controls", []):
            cid = c["id"]
            for doc in c.get("implementing_docs", []):
                doc_path = REPO_ROOT / doc
                if not doc_path.is_file():
                    missing_docs.append((cid, doc))

        self.assertEqual(
            len(missing_docs), 0,
            f"Registry references non-existent implementing_docs: {missing_docs}"
        )

    def test_13_registry_validates_against_draft_2020_12_schema(self):
        """Verify framework_registry.yaml strictly validates against schemas/framework_registry.schema.json."""
        validate_against_schema(self.registry_schema, self.registry)

    def test_14_registry_schema_negative_mutation_attacks(self):
        """
        Adversarially inject negative mutations to verify framework_registry.schema.json rejects:
        - Invalid schema_version
        - Invalid OSCAL relationship
        - Disallowed additional properties
        - Invalid control ID format
        """
        # Mutation 1: Invalid schema_version
        bad_ver = copy.deepcopy(self.registry)
        bad_ver["schema_version"] = "1.0.0"
        with self.assertRaises(AssertionError, msg="Failed to reject schema_version 1.0.0"):
            validate_against_schema(self.registry_schema, bad_ver)

        # Mutation 2: Disallowed additional property at root
        bad_root = copy.deepcopy(self.registry)
        bad_root["malicious_extra_property"] = True
        with self.assertRaises(AssertionError, msg="Failed to reject extra root property"):
            validate_against_schema(self.registry_schema, bad_root)

        # Mutation 3: Invalid OSCAL relationship
        bad_rel = copy.deepcopy(self.registry)
        bad_rel["controls"][0]["mappings"]["nist_sp_800_53_rev5"][0]["relationship"] = "part-of"
        with self.assertRaises(AssertionError, msg="Failed to reject invalid OSCAL relationship 'part-of'"):
            validate_against_schema(self.registry_schema, bad_rel)

        # Mutation 4: Missing required relationship on mappedItem object
        bad_item = copy.deepcopy(self.registry)
        bad_item["controls"][0]["mappings"]["asd_essential_eight"].append({
            "id": "E8-AC-ML1"
            # Missing "relationship"
        })
        with self.assertRaises(AssertionError, msg="Failed to reject missing relationship on mappedItem"):
            validate_against_schema(self.registry_schema, bad_item)

    # -------------------------------------------------------------------------
    # 4. Policy & Standard Essential Eight Harmonization
    # -------------------------------------------------------------------------
    def test_15_operations_security_policy_e8_thresholds(self):
        """
        Verify docs/02_Policies/05_Operations_Security_Policy.md contains:
        - Application Control allowlisting (blocking %APPDATA%, %TEMP%, Downloads)
        - EDR agent tamper resistance
        - Immutable backups with quarterly automated restoration drills
        """
        path = REPO_ROOT / "docs" / "02_Policies" / "05_Operations_Security_Policy.md"
        content = path.read_text(encoding="utf-8")

        self.assertIn("Application Control", content)
        self.assertIn("%APPDATA%", content)
        self.assertIn("%TEMP%", content)
        self.assertIn("tamper resistance", content)
        self.assertIn("Immutable Backups", content)
        self.assertIn("quarterly", content)

    def test_16_acceptable_use_ai_policy_e8_thresholds(self):
        """
        Verify docs/02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md contains:
        - Default blocking of Microsoft Office macros from the Internet
        - Cryptographic signing for approved internal macros
        - User application hardening (blocking web advertisements, flash/java, extensions, child processes)
        """
        path = REPO_ROOT / "docs" / "02_Policies" / "13_Acceptable_Use_and_AI_Security_Policy.md"
        content = path.read_text(encoding="utf-8")

        self.assertIn("Microsoft Office Macro", content)
        self.assertIn("digitally signed", content)
        self.assertIn("User Application Hardening", content)
        self.assertIn("advertisements", content)

    def test_17_password_authentication_standard_e8_thresholds(self):
        """
        Verify docs/03_Standards_and_Procedures/01_Password_and_Authentication_Standard.md contains:
        - Phishing-resistant MFA (FIDO2/WebAuthn)
        - Privileged account separation (Section 3.5: dedicated unprivileged accounts, PAWs, bastion hosts)
        """
        path = REPO_ROOT / "docs" / "03_Standards_and_Procedures" / "01_Password_and_Authentication_Standard.md"
        content = path.read_text(encoding="utf-8")

        self.assertIn("FIDO2", content)
        self.assertIn("WebAuthn", content)
        self.assertIn("Privileged Account Separation", content)
        self.assertIn("PAW", content)

    def test_18_vulnerability_patch_management_standard_e8_thresholds(self):
        """
        Verify docs/03_Standards_and_Procedures/04_Vulnerability_and_Patch_Management_Standard.md contains:
        - 48-hour critical exploit patch SLA
        - Fortnightly (14d) and weekly (7d) scanning cadences
        - Decommissioning unsupported EOL software within 30 days
        """
        path = REPO_ROOT / "docs" / "03_Standards_and_Procedures" / "04_Vulnerability_and_Patch_Management_Standard.md"
        content = path.read_text(encoding="utf-8")

        self.assertIn("48 hours", content)
        self.assertIn("fortnightly", content)
        self.assertIn("End-of-Life", content)
        self.assertIn("30 days", content)

    # -------------------------------------------------------------------------
    # 5. Empirical Citation Integrity Audit (docs/ vs Catalogs)
    # -------------------------------------------------------------------------
    def test_19_docs_essential_eight_citations_must_exist_in_catalog(self):
        """
        AUDIT / CHALLENGE CHECK:
        Every Essential Eight control citation in docs/**/*.md (matching E8-[A-Za-z0-9-]+)
        MUST strictly exist in mappings/catalogs/asd_essential_eight.yaml.
        Flags invalid informal prefixes like E8-MO, E8-UH, E8-MFA, E8-RA.
        """
        e8_pattern = re.compile(r"\b(E8-[A-Za-z0-9-]+)\b")
        invalid_citations = []

        for p in (REPO_ROOT / "docs").rglob("*.md"):
            rel_str = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
            content = p.read_text(encoding="utf-8")
            matches = e8_pattern.findall(content)
            for m in matches:
                if m not in self.valid_e8_ids:
                    invalid_citations.append((rel_str, m))

        self.assertEqual(
            len(invalid_citations), 0,
            f"Found invalid Essential Eight citations in documentation not in authoritative catalog: {invalid_citations}"
        )

    def test_20_docs_nist_800_53_citations_must_exist_in_catalog(self):
        """
        AUDIT / CHALLENGE CHECK:
        Every standalone NIST SP 800-53 control citation in docs/**/*.md
        MUST strictly exist in mappings/catalogs/nist_sp_800_53_rev5.yaml.
        """
        pattern = re.compile(r"(?<![A-Z]{2}[.-])\b([A-Z]{2}-\d+)\b")
        known_families = {
            "AC", "AT", "AU", "CA", "CM", "CP", "IA", "IR", "MA", "MP",
            "PE", "PL", "PM", "PS", "PT", "RA", "SA", "SC", "SI", "SR"
        }
        invalid_citations = []

        for p in (REPO_ROOT / "docs").rglob("*.md"):
            rel_str = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
            content = p.read_text(encoding="utf-8")
            matches = pattern.findall(content)
            for m in matches:
                if m.split("-")[0] in known_families and m not in self.valid_53_ids:
                    invalid_citations.append((rel_str, m))

        self.assertEqual(
            len(invalid_citations), 0,
            f"Found invalid NIST SP 800-53 citations in documentation not in authoritative catalog: {invalid_citations}"
        )


if __name__ == "__main__":
    unittest.main()
