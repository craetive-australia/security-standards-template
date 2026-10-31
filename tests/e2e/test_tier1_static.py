"""
Tier 1: Static Checks, Syntax & Structure E2E Tests
Validates repository infrastructure, file existence, Python/YAML/JSON syntax,
relative Markdown link integrity, Document Control Header tables, and Document History tables.
"""

import json
import os
import py_compile
import re
import sys
import unittest
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

EXPECTED_DOC_FILES = [
    # Index
    "docs/index.md",
    # 01_ISMS_Framework (8 files)
    "docs/01_ISMS_Framework/01_Information_Security_Policy.md",
    "docs/01_ISMS_Framework/02_Context_of_the_Organization.md",
    "docs/01_ISMS_Framework/03_Risk_Management_Methodology.md",
    "docs/01_ISMS_Framework/04_Roles_and_Responsibilities.md",
    "docs/01_ISMS_Framework/05_Statement_of_Applicability_SoA.md",
    "docs/01_ISMS_Framework/06_ISMS_Governance_Audit_and_Improvement.md",
    "docs/01_ISMS_Framework/07_Framework_and_Domain_Onboarding_Guide.md",
    "docs/01_ISMS_Framework/08_Multi_Framework_Crosswalk_and_OSCAL_Matrix.md",
    # 02_Policies (13 files)
    "docs/02_Policies/01_Access_Control_Policy.md",
    "docs/02_Policies/02_Asset_Management_Policy.md",
    "docs/02_Policies/03_Cryptography_Policy.md",
    "docs/02_Policies/04_Physical_Security_Policy.md",
    "docs/02_Policies/05_Operations_Security_Policy.md",
    "docs/02_Policies/06_Communications_Security_Policy.md",
    "docs/02_Policies/07_Supplier_Security_Policy.md",
    "docs/02_Policies/08_HR_Security_Policy.md",
    "docs/02_Policies/09_Data_Privacy_and_Protection_Policy.md",
    "docs/02_Policies/10_Incident_Management_Policy.md",
    "docs/02_Policies/11_Business_Continuity_Policy.md",
    "docs/02_Policies/12_SDLC_and_Change_Management_Policy.md",
    "docs/02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md",
    # 03_Standards_and_Procedures (9 files)
    "docs/03_Standards_and_Procedures/01_Password_and_Authentication_Standard.md",
    "docs/03_Standards_and_Procedures/02_Data_Classification_and_Handling_Standard.md",
    "docs/03_Standards_and_Procedures/03_Data_Retention_and_Destruction_Standard.md",
    "docs/03_Standards_and_Procedures/04_Vulnerability_and_Patch_Management_Standard.md",
    "docs/03_Standards_and_Procedures/05_Secure_Coding_Standard.md",
    "docs/03_Standards_and_Procedures/06_Incident_Response_Plan_IRP.md",
    "docs/03_Standards_and_Procedures/07_Business_Continuity_Plan_BCP.md",
    "docs/03_Standards_and_Procedures/08_Disaster_Recovery_Plan_DRP.md",
    "docs/03_Standards_and_Procedures/09_Data_Breach_Notification_Procedure.md",
    # 04_Templates_and_Registers (8 files)
    "docs/04_Templates_and_Registers/01_Information_Asset_Register.md",
    "docs/04_Templates_and_Registers/02_Risk_Register.md",
    "docs/04_Templates_and_Registers/03_Security_Incident_Log.md",
    "docs/04_Templates_and_Registers/04_Vendor_Risk_Assessment_Template.md",
    "docs/04_Templates_and_Registers/05_Access_Review_Log.md",
    "docs/04_Templates_and_Registers/06_RoPA_Template.md",
    "docs/04_Templates_and_Registers/07_DPIA_Template.md",
    "docs/04_Templates_and_Registers/08_Internal_Audit_and_CAPA_Register.md",
]

EXPECTED_ROOT_FILES = [
    "LICENSE",
    "mkdocs.yml",
    "README.md",
    ".gitignore",
    "requirements.txt",
    "pyproject.toml",
    "tests/TEST_INFRA.md",
    "scripts/fill_placeholders.py",
    "scripts/validate_isms.py",
    "scripts/export_oscal.py",
    "scripts/check_adoption.py",
    "scripts/generate_docs.py",
    "mappings/framework_registry.yaml",
    "mappings/compliance_manifest.yaml",
]


class TestTier1Static(unittest.TestCase):
    """Tier 1: Static verification of repository structure, syntax, and formatting."""

    def test_repository_files_exist(self):
        """Verifies that all required repository root, scripts, and registry files exist."""
        missing = []
        for rel_path in EXPECTED_ROOT_FILES:
            full_path = REPO_ROOT / rel_path
            if not full_path.exists():
                missing.append(rel_path)
        self.assertEqual(
            missing,
            [],
            f"Missing required repository infrastructure files: {missing}",
        )

    def test_all_documentation_files_exist(self):
        """Verifies that all 40 expected Markdown documentation files exist on disk."""
        missing = []
        for rel_path in EXPECTED_DOC_FILES:
            full_path = REPO_ROOT / rel_path
            if not full_path.exists():
                missing.append(rel_path)
        self.assertEqual(
            missing,
            [],
            f"Missing {len(missing)} required documentation files: {missing}",
        )

    def test_python_scripts_syntax(self):
        """Verifies that all 5 Python automation scripts compile cleanly without syntax errors."""
        scripts_to_check = [
            REPO_ROOT / "scripts" / "fill_placeholders.py",
            REPO_ROOT / "scripts" / "validate_isms.py",
            REPO_ROOT / "scripts" / "export_oscal.py",
            REPO_ROOT / "scripts" / "check_adoption.py",
            REPO_ROOT / "scripts" / "generate_docs.py",
        ]
        for script_path in scripts_to_check:
            self.assertTrue(
                script_path.exists(),
                f"Script does not exist for compilation check: {script_path}",
            )
            try:
                py_compile.compile(str(script_path), doraise=True)
            except py_compile.PyCompileError as e:
                self.fail(f"Python syntax compilation failed for {script_path}: {e}")

    def test_yaml_files_syntax(self):
        """Verifies that mkdocs.yml, registries, catalogs, and GitHub workflows parse cleanly as valid YAML."""
        yaml_files = [
            REPO_ROOT / "mkdocs.yml",
            REPO_ROOT / "mappings" / "framework_registry.yaml",
            REPO_ROOT / "mappings" / "compliance_manifest.yaml",
            REPO_ROOT / "mappings" / "catalogs" / "iso_27001_2022.yaml",
            REPO_ROOT / "mappings" / "catalogs" / "soc2_tsc_2017.yaml",
            REPO_ROOT / "mappings" / "catalogs" / "nist_csf_2_0.yaml",
            REPO_ROOT / "mappings" / "catalogs" / "gdpr.yaml",
            REPO_ROOT / "mappings" / "catalogs" / "nist_sp_800_53_rev5.yaml",
            REPO_ROOT / "mappings" / "catalogs" / "asd_essential_eight.yaml",
            REPO_ROOT / ".github" / "dependabot.yml",
            REPO_ROOT / ".github" / "workflows" / "isms-compliance-ci.yml",
            REPO_ROOT / ".github" / "workflows" / "scheduled-governance-audit.yml",
            REPO_ROOT / ".github" / "workflows" / "docs-publish.yml",
        ]
        for yml_path in yaml_files:
            self.assertTrue(
                yml_path.exists(),
                f"YAML file does not exist: {yml_path}",
            )
            with open(yml_path, "r", encoding="utf-8") as f:
                try:
                    data = yaml.safe_load(f)
                    self.assertIsInstance(
                        data,
                        dict,
                        f"Parsed YAML root must be a dictionary in {yml_path}",
                    )
                except yaml.YAMLError as e:
                    self.fail(f"YAML parsing error in {yml_path}: {e}")

    def test_json_schemas_and_oscal_artifacts_syntax(self):
        """Verifies that all Draft 2020-12 JSON Schemas and OSCAL v1.2.0 artifacts parse cleanly."""
        schema_files = [
            REPO_ROOT / "schemas" / "framework_registry.schema.json",
            REPO_ROOT / "schemas" / "catalog.schema.json",
            REPO_ROOT / "schemas" / "compliance_manifest.schema.json",
            REPO_ROOT / "schemas" / "oscal_v1_2_0_subset.schema.json",
        ]
        for s_path in schema_files:
            self.assertTrue(s_path.exists(), f"JSON schema missing: {s_path}")
            data = json.loads(s_path.read_text(encoding="utf-8"))
            self.assertIn("$schema", data, f"{s_path.name} missing $schema")
            self.assertIn("2020-12", data["$schema"], f"{s_path.name} must use Draft 2020-12")

        oscal_files = [
            REPO_ROOT / "dist" / "oscal" / "catalog.json",
            REPO_ROOT / "dist" / "oscal" / "mapping_collection.json",
            REPO_ROOT / "dist" / "oscal" / "profile_e8_ml2.json",
            REPO_ROOT / "dist" / "oscal" / "profile_nist_800_53_moderate.json",
            REPO_ROOT / "dist" / "oscal" / "component_definition.json",
        ]
        for o_path in oscal_files:
            self.assertTrue(o_path.exists(), f"OSCAL artifact missing: {o_path}")
            data = json.loads(o_path.read_text(encoding="utf-8"))
            self.assertIsInstance(data, dict)

    def test_adr_and_github_governance_files_exist(self):
        """Verifies ADRs in architecture/adr/ (outside docs/) and .github governance files exist."""
        adrs = [
            REPO_ROOT / "architecture" / "adr" / "ADR-001-yaml-sot-and-oscal-export.md",
            REPO_ROOT / "architecture" / "adr" / "ADR-002-mkdocs-zensical-migration.md",
            REPO_ROOT / "architecture" / "adr" / "ADR-003-essential-eight-and-nist-800-53-mapping.md",
        ]
        for adr in adrs:
            self.assertTrue(adr.exists(), f"Missing ADR: {adr}")

        # Verify no ADR files leaked into docs/
        docs_adrs = list((REPO_ROOT / "docs").rglob("ADR-*.md"))
        self.assertEqual(docs_adrs, [], f"ADRs must not reside inside docs/: {docs_adrs}")

        gov_files = [
            REPO_ROOT / ".github" / "CODEOWNERS",
            REPO_ROOT / ".github" / "dependabot.yml",
            REPO_ROOT / ".github" / "pull_request_template.md",
        ]
        for gf in gov_files:
            self.assertTrue(gf.exists(), f"Missing GitHub governance file: {gf}")

    def test_markdown_relative_links(self):
        """Verifies that all local relative Markdown links across docs resolve to existing files."""
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        broken_links = []
        docs_dir = REPO_ROOT / "docs"
        if not docs_dir.exists():
            self.fail(f"Docs directory does not exist: {docs_dir}")

        for md_file in docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            for match in link_pattern.finditer(content):
                target = match.group(2).strip()
                # Skip anchors, external urls, mailto, template placeholders
                if (
                    not target
                    or target.startswith("#")
                    or target.startswith("http://")
                    or target.startswith("https://")
                    or target.startswith("mailto:")
                    or "[" in target
                ):
                    continue

                # Strip anchor fragment
                file_target = target.split("#")[0].strip()
                if not file_target:
                    continue

                resolved = (md_file.parent / file_target).resolve()
                if not resolved.exists():
                    rel_src = md_file.relative_to(REPO_ROOT)
                    broken_links.append(f"{rel_src} -> {target} (resolved: {resolved})")

        self.assertEqual(
            broken_links,
            [],
            f"Found {len(broken_links)} broken relative Markdown links:\n"
            + "\n".join(broken_links[:20]),
        )

    def test_document_control_header_tables(self):
        """Verifies that all 39 documents in 01-04 have a standardized Document Control Header Table."""
        required_keys = [
            "Document ID",
            "Version",
            "Effective Date",
            "Document Owner",
            "Review Cycle",
            "Classification",
            "Framework Mappings",
        ]
        collapsed_bold_re = re.compile(
            r"^\*\*(?:Document ID|Version|Effective Date|Document Owner|Classification)\*\*:",
            re.MULTILINE,
        )

        invalid_headers = []

        # Check all markdown files except docs/index.md
        for rel_doc in EXPECTED_DOC_FILES:
            if rel_doc == "docs/index.md":
                continue
            doc_path = REPO_ROOT / rel_doc
            if not doc_path.exists():
                invalid_headers.append(f"{rel_doc}: File does not exist")
                continue

            content = doc_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            # Inspect first 25 lines for title and header table
            header_sample = "\n".join(lines[:25])

            # Check for forbidden collapsed bold metadata
            if collapsed_bold_re.search(header_sample):
                invalid_headers.append(
                    f"{rel_doc}: Contains deprecated collapsed single-line bold metadata"
                )
                continue

            # Verify presence of all required metadata keys in table
            missing_keys = [k for k in required_keys if k not in header_sample]
            if missing_keys:
                invalid_headers.append(
                    f"{rel_doc}: Header table missing required keys: {missing_keys}"
                )

        self.assertEqual(
            invalid_headers,
            [],
            f"Found {len(invalid_headers)} documents with invalid Document Control Header Tables:\n"
            + "\n".join(invalid_headers),
        )

    def test_document_history_tables(self):
        """Verifies that all 39 documents in 01-04 have a standardized 5-column Document History Table."""
        required_columns = ["Version", "Date", "Author", "Approved By", "Description"]
        invalid_footers = []

        for rel_doc in EXPECTED_DOC_FILES:
            if rel_doc == "docs/index.md":
                continue
            doc_path = REPO_ROOT / rel_doc
            if not doc_path.exists():
                invalid_footers.append(f"{rel_doc}: File does not exist")
                continue

            content = doc_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            # Inspect bottom 35 lines
            footer_sample = "\n".join(lines[-35:])

            if "Document History" not in footer_sample:
                invalid_footers.append(
                    f"{rel_doc}: Missing '## Document History' section at document end"
                )
                continue

            missing_cols = [c for c in required_columns if c not in footer_sample]
            if missing_cols:
                invalid_footers.append(
                    f"{rel_doc}: Document History table missing columns: {missing_cols}"
                )

        self.assertEqual(
            invalid_footers,
            [],
            f"Found {len(invalid_footers)} documents with invalid Document History Tables:\n"
            + "\n".join(invalid_footers),
        )

    def test_policy_mandatory_sections(self):
        """Verifies that all 13 policies contain mandatory sections."""
        policy_files = [p for p in EXPECTED_DOC_FILES if p.startswith("docs/02_Policies/")]
        missing_sections = []

        for rel_doc in policy_files:
            doc_path = REPO_ROOT / rel_doc
            if not doc_path.exists():
                missing_sections.append(f"{rel_doc}: File does not exist")
                continue

            content = doc_path.read_text(encoding="utf-8")
            # Check for Roles and Responsibilities
            has_roles = bool(re.search(r"##\s+.*Roles and Responsibilities", content, re.IGNORECASE))
            # Check for Compliance / Exceptions
            has_compliance = bool(
                re.search(r"##\s+.*(?:Compliance|Exceptions|Enforcement)", content, re.IGNORECASE)
            )
            # Check for Related Documents
            has_related = bool(re.search(r"##\s+.*Related Documents", content, re.IGNORECASE))

            missing = []
            if not has_roles:
                missing.append("Roles and Responsibilities")
            if not has_compliance:
                missing.append("Compliance and Exceptions")
            if not has_related:
                missing.append("Related Documents")

            if missing:
                missing_sections.append(f"{rel_doc} missing: {missing}")

        self.assertEqual(
            missing_sections,
            [],
            f"Policies missing mandatory sections:\n" + "\n".join(missing_sections),
        )

    def test_repository_infrastructure_metadata(self):
        """Verifies README.md, .gitignore, LICENSE, and requirements.txt contents."""
        license_file = REPO_ROOT / "LICENSE"
        self.assertTrue(license_file.exists(), "LICENSE must exist")
        self.assertIn("Apache License", license_file.read_text(encoding="utf-8"))

        readme = REPO_ROOT / "README.md"
        self.assertTrue(readme.exists(), "README.md must exist")
        readme_content = readme.read_text(encoding="utf-8")
        self.assertGreater(
            len(readme_content),
            500,
            "README.md must be a comprehensive guide, not a 1-line stub",
        )
        self.assertIn("mkdocs", readme_content.lower())
        self.assertIn("fill_placeholders.py", readme_content)
        self.assertIn("export_oscal.py", readme_content)
        self.assertIn("check_adoption.py", readme_content)
        self.assertIn("uv", readme_content)

        gitignore = REPO_ROOT / ".gitignore"
        self.assertTrue(gitignore.exists(), ".gitignore must exist")
        gi_content = gitignore.read_text(encoding="utf-8")
        self.assertIn(".venv", gi_content)
        self.assertIn("site/", gi_content)
        self.assertIn("__pycache__", gi_content)
        self.assertIn("serve_*.txt", gi_content)
        self.assertIn("*.sarif", gi_content)

        reqs = REPO_ROOT / "requirements.txt"
        self.assertTrue(reqs.exists(), "requirements.txt must exist")
        req_content = reqs.read_text(encoding="utf-8")
        self.assertIn("mkdocs", req_content)
        self.assertIn("mkdocs-material", req_content)
        self.assertIn("pyyaml", req_content)

        pyproject = REPO_ROOT / "pyproject.toml"
        self.assertTrue(pyproject.exists(), "pyproject.toml must exist")
        pyproj_content = pyproject.read_text(encoding="utf-8")
        self.assertIn("mkdocs", pyproj_content)
        self.assertIn("mkdocs-material", pyproj_content)
        self.assertIn("PyYAML", pyproj_content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
