"""
Tier 4: Governance, Auditing & Harmonization E2E Tests
Validates the 93-control ISO 27001:2022 Statement of Applicability (with link verification),
scans for deprecated ISO 2013 and invalid citations, verifies resolution of all 6 policy contradictions,
verifies new governance/AI policies and registers, and validates the canonical control registry.
"""

import os
import re
import sys
import unittest
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Complete set of all 93 ISO/IEC 27001:2022 Annex A controls
EXPECTED_ISO_2022_CONTROLS = (
    [f"A.5.{i}" for i in range(1, 38)]  # 37 controls
    + [f"A.6.{i}" for i in range(1, 9)]   # 8 controls
    + [f"A.7.{i}" for i in range(1, 15)]  # 14 controls
    + [f"A.8.{i}" for i in range(1, 35)]  # 34 controls
)
assert len(EXPECTED_ISO_2022_CONTROLS) == 93


class TestTier4GovernanceAudit(unittest.TestCase):
    """Tier 4: Governance audit, 93-control SoA completeness, citation scanner, and policy harmonization."""

    def test_soa_93_controls_completeness_and_links(self):
        """Verifies docs/01_ISMS_Framework/05_Statement_of_Applicability_SoA.md contains all 93 controls with working relative links."""
        soa_path = REPO_ROOT / "docs" / "01_ISMS_Framework" / "05_Statement_of_Applicability_SoA.md"
        self.assertTrue(soa_path.exists(), f"SoA document not found at {soa_path}")

        soa_content = soa_path.read_text(encoding="utf-8")
        soa_lines = soa_content.splitlines()

        missing_controls = []
        broken_soa_links = []
        found_controls = set()

        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

        for line in soa_lines:
            if not line.strip().startswith("|"):
                continue
            for ctrl in EXPECTED_ISO_2022_CONTROLS:
                # Check for control ID in table line (e.g. | A.5.1 | or | **A.5.1** |)
                pattern = rf"\|\s*(?:\*\*)?{re.escape(ctrl)}(?:\*\*)?\s*\|"
                if re.search(pattern, line):
                    found_controls.add(ctrl)
                    # Check for implementing document link in this row
                    links = link_pattern.findall(line)
                    if not links:
                        broken_soa_links.append(f"{ctrl}: No markdown link found in row: {line.strip()}")
                    else:
                        for label, target in links:
                            if target.startswith("http") or target.startswith("#"):
                                continue
                            file_target = target.split("#")[0].strip()
                            if file_target:
                                resolved = (soa_path.parent / file_target).resolve()
                                if not resolved.exists():
                                    broken_soa_links.append(
                                        f"{ctrl}: Link '{target}' resolves to non-existent file: {resolved}"
                                    )

        for ctrl in EXPECTED_ISO_2022_CONTROLS:
            if ctrl not in found_controls:
                missing_controls.append(ctrl)

        self.assertEqual(
            missing_controls,
            [],
            f"SoA is missing {len(missing_controls)} ISO/IEC 27001:2022 controls: {missing_controls}",
        )
        self.assertEqual(
            broken_soa_links,
            [],
            f"Found broken implementing links in SoA table:\n" + "\n".join(broken_soa_links[:20]),
        )

    def test_zero_deprecated_iso_2013_citations(self):
        """Scans docs/ for obsolete ISO 27001:2013 Annex A citations outside designated legacy crosswalks."""
        # Deprecated 2013 patterns: A.9 to A.18, and 4-segment IDs like A.5.1.1, A.6.1.1, A.7.1.1
        iso_2013_re = re.compile(
            r"\bA\.(?:9|1[0-8])\.\d+(?:\.\d+)?|\bA\.(?:5|6|7)\.\d+\.\d+",
            re.IGNORECASE,
        )

        docs_dir = REPO_ROOT / "docs"
        self.assertTrue(docs_dir.exists(), "docs/ directory not found")

        violations = []
        for md_file in docs_dir.rglob("*.md"):
            rel_path = md_file.relative_to(REPO_ROOT).as_posix()
            content = md_file.read_text(encoding="utf-8")
            lines = content.splitlines()

            # Determine whether file is allowed to contain legacy crosswalk column
            is_soa = "05_Statement_of_Applicability_SoA.md" in rel_path
            is_onboarding = "07_Framework_and_Domain_Onboarding_Guide.md" in rel_path

            for idx, line in enumerate(lines, 1):
                match = iso_2013_re.search(line)
                if match:
                    # Allow only within explicit legacy crosswalk columns or sections
                    if is_soa and ("legacy" in line.lower() or "2013" in line):
                        continue
                    if is_onboarding and ("crosswalk" in line.lower() or "2013" in line or "legacy" in line.lower()):
                        continue

                    violations.append(
                        f"{rel_path}:{idx}: Found deprecated ISO 2013 citation '{match.group(0)}' in line: {line.strip()}"
                    )

        self.assertEqual(
            violations,
            [],
            f"Found {len(violations)} obsolete ISO 27001:2013 citations outside legacy crosswalks:\n"
            + "\n".join(violations[:20]),
        )

    def test_zero_invalid_and_deprecated_standards(self):
        """Asserts zero occurrences of SOC 2 DC3.1 or DoD 5220.22-M across docs/."""
        docs_dir = REPO_ROOT / "docs"
        self.assertTrue(docs_dir.exists(), "docs/ directory not found")

        violations = []
        for md_file in docs_dir.rglob("*.md"):
            rel_path = md_file.relative_to(REPO_ROOT).as_posix()
            content = md_file.read_text(encoding="utf-8")

            if "SOC 2 DC3.1" in content or "DC3.1" in content:
                violations.append(f"{rel_path}: Contains invalid citation 'SOC 2 DC3.1'")
            if "DoD 5220.22-M" in content or "DoD 5220" in content:
                violations.append(f"{rel_path}: Contains deprecated standard 'DoD 5220.22-M'")

        self.assertEqual(
            violations,
            [],
            f"Found invalid/deprecated standard citations:\n" + "\n".join(violations),
        )

    def test_contradiction_1_authentication_standard(self):
        """Verifies 01_Password_and_Authentication_Standard.md implements modern NIST SP 800-63B guidelines."""
        std_path = (
            REPO_ROOT
            / "docs"
            / "03_Standards_and_Procedures"
            / "01_Password_and_Authentication_Standard.md"
        )
        self.assertTrue(std_path.exists(), f"File not found: {std_path}")
        content = std_path.read_text(encoding="utf-8")

        # 14-char min
        self.assertTrue(
            "14" in content or "[MIN_PASSWORD_LENGTH]" in content,
            "Must mandate 14-character minimum password length",
        )
        # Passphrases encouraged
        self.assertTrue(
            bool(re.search(r"passphrase", content, re.IGNORECASE)),
            "Must encourage passphrases",
        )
        # Compromised password check
        self.assertTrue(
            bool(re.search(r"compromised|blocklist|breached", content, re.IGNORECASE)),
            "Must mandate checking against compromised/breached password blocklists",
        )
        # Phishing-resistant MFA (FIDO2/WebAuthn)
        self.assertTrue(
            bool(re.search(r"FIDO2|WebAuthn|phishing-resistant|number-matching", content, re.IGNORECASE)),
            "Must require phishing-resistant MFA or number-matching push",
        )
        # NIST SP 800-63B reference
        self.assertTrue(
            "800-63B" in content or "800-63" in content,
            "Must reference NIST SP 800-63B authentication guidelines",
        )

    def test_contradiction_2_code_review_and_supply_chain(self):
        """Verifies 05_Secure_Coding_Standard.md enforces 1-peer / 2-peer Tier 1 approvals and supply chain controls."""
        std_path = (
            REPO_ROOT
            / "docs"
            / "03_Standards_and_Procedures"
            / "05_Secure_Coding_Standard.md"
        )
        self.assertTrue(std_path.exists(), f"File not found: {std_path}")
        content = std_path.read_text(encoding="utf-8")

        # Approvals
        self.assertTrue(
            bool(re.search(r"1\s+peer|one\s+peer|at\s+least\s+1", content, re.IGNORECASE)),
            "Must mandate at least 1 peer approval for standard changes",
        )
        self.assertTrue(
            bool(re.search(r"2\s+approv|two\s+approv|CODEOWNERS", content, re.IGNORECASE)),
            "Must mandate 2 approvals (including security/CODEOWNERS) for Tier-1/security changes",
        )
        # SBOM, secret scanning, artifact signing
        self.assertTrue(
            bool(re.search(r"SBOM|Software Bill of Materials", content, re.IGNORECASE)),
            "Must mandate SBOM generation",
        )
        self.assertTrue(
            bool(re.search(r"secret\s+scan", content, re.IGNORECASE)),
            "Must mandate pre-commit or CI secret scanning",
        )
        self.assertTrue(
            bool(re.search(r"signing|Cosign|artifact\s+sign", content, re.IGNORECASE)),
            "Must mandate cryptographic artifact signing",
        )

    def test_contradiction_3_data_classification(self):
        """Verifies 02_Data_Classification_and_Handling_Standard.md mandates default Internal metadata and visual markings."""
        std_path = (
            REPO_ROOT
            / "docs"
            / "03_Standards_and_Procedures"
            / "02_Data_Classification_and_Handling_Standard.md"
        )
        self.assertTrue(std_path.exists(), f"File not found: {std_path}")
        content = std_path.read_text(encoding="utf-8")

        # Default Internal
        self.assertTrue(
            bool(re.search(r"default.*Internal|Internal.*default", content, re.IGNORECASE)),
            "Must mandate default 'Internal' metadata classification",
        )
        # Visual markings on Confidential and Restricted
        self.assertTrue(
            bool(re.search(r"visual|marking|header|labeling", content, re.IGNORECASE)),
            "Must require explicit markings for Confidential and Restricted assets",
        )

    def test_contradiction_4_incident_slas_and_breach_matrix(self):
        """Verifies post-mortem SLAs (5d/10d) and multi-jurisdiction breach notification matrix."""
        sop_path = (
            REPO_ROOT
            / "docs"
            / "03_Standards_and_Procedures"
            / "09_Data_Breach_Notification_Procedure.md"
        )
        self.assertTrue(sop_path.exists(), f"File not found: {sop_path}")
        content = sop_path.read_text(encoding="utf-8")

        # SLAs
        self.assertTrue(
            bool(re.search(r"5\s+(?:business\s+)?days?", content, re.IGNORECASE)),
            "Must specify 5 business days post-mortem SLA for critical/high severity",
        )
        # Jurisdictions in matrix
        for jurisdiction in ["GDPR", "72", "CIRCIA", "SEC"]:
            self.assertTrue(
                jurisdiction.lower() in content.lower(),
                f"Breach matrix must reference jurisdiction/timeline: {jurisdiction}",
            )

    def test_contradiction_5_log_retention_and_sanitization(self):
        """Verifies log retention (90d hot + 365d cold archive) and NIST SP 800-88 / IEEE 2883 sanitization."""
        std_path = (
            REPO_ROOT
            / "docs"
            / "03_Standards_and_Procedures"
            / "03_Data_Retention_and_Destruction_Standard.md"
        )
        self.assertTrue(std_path.exists(), f"File not found: {std_path}")
        content = std_path.read_text(encoding="utf-8")

        # 90 days hot and 365 days cold/archive
        self.assertTrue("90" in content, "Must specify 90 days active/hot log retention")
        self.assertTrue("365" in content, "Must specify 365 days archive/cold log retention")
        # NIST SP 800-88 Rev. 1 and IEEE 2883-2022
        self.assertTrue(
            "800-88" in content,
            "Must reference NIST SP 800-88 Rev. 1 for media sanitization",
        )
        self.assertTrue(
            "2883" in content,
            "Must reference IEEE 2883-2022 for modern storage sanitization",
        )

    def test_contradiction_6_access_reviews_vulnerability_and_risk(self):
        """Verifies access review cadences, vulnerability scoring (CVSS v4, KEV, EPSS), and 5x5 risk matrix."""
        # Access policy
        access_pol = REPO_ROOT / "docs" / "02_Policies" / "01_Access_Control_Policy.md"
        self.assertTrue(access_pol.exists(), f"File not found: {access_pol}")
        acc_content = access_pol.read_text(encoding="utf-8")
        self.assertTrue(
            bool(re.search(r"monthly|quarterly", acc_content, re.IGNORECASE)),
            "Access Control Policy must specify monthly privileged and quarterly critical review cadences",
        )

        # Vulnerability standard
        vuln_std = (
            REPO_ROOT
            / "docs"
            / "03_Standards_and_Procedures"
            / "04_Vulnerability_and_Patch_Management_Standard.md"
        )
        self.assertTrue(vuln_std.exists(), f"File not found: {vuln_std}")
        vuln_content = vuln_std.read_text(encoding="utf-8")
        self.assertTrue(
            "CVSS" in vuln_content,
            "Vulnerability standard must reference CVSS scoring",
        )
        self.assertTrue(
            "KEV" in vuln_content or "EPSS" in vuln_content,
            "Vulnerability standard must incorporate CISA KEV or EPSS risk prioritization",
        )

        # Risk methodology
        risk_meth = (
            REPO_ROOT
            / "docs"
            / "01_ISMS_Framework"
            / "03_Risk_Management_Methodology.md"
        )
        self.assertTrue(risk_meth.exists(), f"File not found: {risk_meth}")
        risk_content = risk_meth.read_text(encoding="utf-8")
        self.assertTrue(
            "5x5" in risk_content or "5 x 5" in risk_content or "25" in risk_content,
            "Risk Management Methodology must define an explicit 5x5 (1-25) risk matrix",
        )

    def test_governance_document_clauses(self):
        """Verifies 06_ISMS_Governance_Audit_and_Improvement.md covers mandatory ISO 27001 clauses."""
        gov_path = (
            REPO_ROOT
            / "docs"
            / "01_ISMS_Framework"
            / "06_ISMS_Governance_Audit_and_Improvement.md"
        )
        self.assertTrue(gov_path.exists(), f"File not found: {gov_path}")
        content = gov_path.read_text(encoding="utf-8")

        required_topics = [
            ("6.3", "Planning of changes"),
            ("7.2", "Competence"),
            ("7.3", "Awareness"),
            ("7.4", "Communication"),
            ("7.5", "Documented Information"),
            ("8.1", "Operational Planning"),
            ("9.1", "Monitoring"),
            ("9.2", "Internal Audit"),
            ("9.3", "Management Review"),
            ("10.1", "Continual Improvement"),
            ("10.2", "Nonconformity"),
        ]

        for clause, keyword in required_topics:
            self.assertTrue(
                clause in content or keyword.lower() in content.lower(),
                f"Governance document missing coverage of Clause {clause} ({keyword})",
            )

    def test_acceptable_use_and_ai_security_policy(self):
        """Verifies 13_Acceptable_Use_and_AI_Security_Policy.md covers endpoint security, BYOD, and AI governance."""
        ai_path = (
            REPO_ROOT
            / "docs"
            / "02_Policies"
            / "13_Acceptable_Use_and_AI_Security_Policy.md"
        )
        self.assertTrue(ai_path.exists(), f"File not found: {ai_path}")
        content = ai_path.read_text(encoding="utf-8")

        # Endpoint security
        self.assertTrue(
            bool(re.search(r"encryption|FDE|BitLocker|FileVault", content, re.IGNORECASE)),
            "AI & Acceptable Use policy must mandate full disk encryption",
        )
        self.assertTrue(
            bool(re.search(r"MDM|Mobile Device Management", content, re.IGNORECASE)),
            "AI & Acceptable Use policy must mandate MDM enrollment",
        )
        # AI governance
        self.assertTrue(
            bool(re.search(r"Generative AI|LLM|Artificial Intelligence", content, re.IGNORECASE)),
            "AI & Acceptable Use policy must govern Generative AI / LLMs",
        )
        self.assertTrue(
            bool(re.search(r"ISO/IEC 42001|42001|NIST AI RMF", content)),
            "AI & Acceptable Use policy must align with ISO/IEC 42001 or NIST AI RMF",
        )

    def test_internal_audit_and_capa_register(self):
        """Verifies 08_Internal_Audit_and_CAPA_Register.md includes audit schedule, findings, CAPA, and management review."""
        reg_path = (
            REPO_ROOT
            / "docs"
            / "04_Templates_and_Registers"
            / "08_Internal_Audit_and_CAPA_Register.md"
        )
        self.assertTrue(reg_path.exists(), f"File not found: {reg_path}")
        content = reg_path.read_text(encoding="utf-8")

        self.assertTrue(
            bool(re.search(r"Internal Audit Schedule", content, re.IGNORECASE)),
            "Must include Annual Internal Audit Schedule",
        )
        self.assertTrue(
            bool(re.search(r"Findings Log", content, re.IGNORECASE)),
            "Must include Internal Audit Findings Log",
        )
        self.assertTrue(
            bool(re.search(r"CAPA|Corrective and Preventive Action", content, re.IGNORECASE)),
            "Must include CAPA Log",
        )
        self.assertTrue(
            bool(re.search(r"Management Review", content, re.IGNORECASE)),
            "Must include Management Review Minutes Template",
        )

    def test_risk_register_security_exceptions_section(self):
        """Verifies 02_Risk_Register.md includes a Security Exception & Risk Acceptance Log section."""
        risk_path = (
            REPO_ROOT
            / "docs"
            / "04_Templates_and_Registers"
            / "02_Risk_Register.md"
        )
        self.assertTrue(risk_path.exists(), f"File not found: {risk_path}")
        content = risk_path.read_text(encoding="utf-8")

        self.assertTrue(
            bool(re.search(r"Security Exception|Risk Acceptance", content, re.IGNORECASE)),
            "Risk Register must contain a Security Exception & Risk Acceptance Log section",
        )
        self.assertTrue(
            bool(re.search(r"Compensating Control", content, re.IGNORECASE)),
            "Security Exception log must mandate compensating controls",
        )
        self.assertTrue(
            bool(re.search(r"Expiration|Expiry", content, re.IGNORECASE)),
            "Security Exception log must enforce time-bound expiration",
        )

    def test_framework_registry_schema_and_canonical_controls(self):
        """Verifies mappings/framework_registry.yaml schema, 55 canonical controls, and mapping to all 93 ISO controls."""
        reg_path = REPO_ROOT / "mappings" / "framework_registry.yaml"
        self.assertTrue(reg_path.exists(), f"File not found: {reg_path}")

        with open(reg_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertIsInstance(data, dict, "Registry root must be a dict")
        controls = data.get("controls") or data.get("canonical_controls", [])
        self.assertGreaterEqual(
            len(controls),
            55,
            f"Framework registry must define at least 55 canonical controls, found {len(controls)}",
        )

        mapped_iso_controls = set()
        for ctrl in controls:
            mappings = ctrl.get("mappings", {})
            iso_list = (
                mappings.get("iso_27001_2022")
                or mappings.get("iso27001_2022")
                or mappings.get("iso_27001")
                or []
            )
            for c in iso_list:
                mapped_iso_controls.add(c)

        unmapped = set(EXPECTED_ISO_2022_CONTROLS) - mapped_iso_controls
        self.assertEqual(
            unmapped,
            set(),
            f"Framework registry fails to map {len(unmapped)} ISO/IEC 27001:2022 controls: {sorted(unmapped)}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
