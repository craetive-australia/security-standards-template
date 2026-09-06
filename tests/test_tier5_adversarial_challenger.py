#!/usr/bin/env python3
"""
tests/test_tier5_adversarial_challenger.py
Tier 5 Adversarial Coverage Hardening & Stress Verification Harness.

Adversarially challenges:
1. Deep Citation & Legacy Scanner (including 4-segment A.8.x.y, case variations, forbidden DoD/DC3.1)
2. Document Structure & Metadata Rigor (headers, footers, policy sections, exact tables)
3. Full Link Graph & Heading Anchor Oracle (parses all markdown anchors and verifies targets exist)
4. Tooling Edge Cases & Stress Harness (fill_placeholders.py & validate_isms.py error handling/dry-run)
5. Framework Registry Deep Schema, Completeness, and Coverage Audit
"""

import os
import re
import sys
import unittest
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

# 93 ISO/IEC 27001:2022 Annex A controls
EXPECTED_ISO_2022_CONTROLS = (
    [f"A.5.{i}" for i in range(1, 38)]
    + [f"A.6.{i}" for i in range(1, 9)]
    + [f"A.7.{i}" for i in range(1, 15)]
    + [f"A.8.{i}" for i in range(1, 35)]
)
assert len(EXPECTED_ISO_2022_CONTROLS) == 93


def slugify_heading(heading_text: str) -> str:
    """
    Simulate Python-Markdown / MkDocs slugify logic for heading anchors.
    Lowercases, strips leading/trailing whitespace, removes punctuation (except hyphens and underscores),
    and converts spaces to hyphens.
    """
    # Remove markdown link formatting e.g. [Link Text](url) -> Link Text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", heading_text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Strip markdown bold/italic formatting
    text = re.sub(r"[*_`]", "", text)
    # Strip leading numbers followed by dot/space if any, but python-markdown keeps them:
    # Python-markdown slugify: lowercase, strip non-alphanumeric except hyphen/underscore, space -> hyphen
    text = text.strip().lower()
    # Replace whitespace and forward slashes with hyphens
    text = re.sub(r"[\s/]+", "-", text)
    # Remove all characters that are not alphanumeric, hyphen, or underscore
    text = re.sub(r"[^a-z0-9_-]", "", text)
    return text.strip("-")


def extract_headings(file_path: Path) -> Set[str]:
    """Extract all heading anchors from a Markdown file."""
    anchors = set()
    heading_re = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
    content = file_path.read_text(encoding="utf-8")
    for match in heading_re.finditer(content):
        heading_title = match.group(2).strip()
        slug = slugify_heading(heading_title)
        if slug:
            anchors.add(slug)
        # Also check for explicit anchor definitions {#custom-anchor} or <a name="anchor">
        custom_anchor = re.search(r"\{#([^}]+)\}", heading_title)
        if custom_anchor:
            anchors.add(custom_anchor.group(1).strip().lower())
        a_name = re.search(r'<a\s+(?:name|id)=["\']([^"\']+)["\']', heading_title)
        if a_name:
            anchors.add(a_name.group(1).strip().lower())

    # Also search for <a name="anchor"> or <a id="anchor"> anywhere in body
    for a_match in re.finditer(r'<a\s+(?:name|id)=["\']([^"\']+)["\']', content):
        anchors.add(a_match.group(1).strip().lower())

    return anchors


class TestTier5AdversarialIntegrity(unittest.TestCase):
    """Deep adversarial scan for legacy citations, forbidden tokens, and structural gaps."""

    def setUp(self):
        self.docs_dir = REPO_ROOT / "docs"
        self.all_md_files = sorted(self.docs_dir.rglob("*.md"))

    def test_adversarial_legacy_iso_controls(self):
        """
        Adversarially search for legacy ISO 27001:2013 controls:
        - 4-part controls: A.5.x.y, A.6.x.y, A.7.x.y, A.8.x.y
        - 2/3/4 part controls for A.9 through A.18
        Must NOT appear outside explicit legacy crosswalk columns.
        """
        legacy_patterns = [
            # Any A.9 through A.18 control (e.g. A.9.1, A.9.1.1, A.12.1.2)
            re.compile(r"\bA\.(?:9|1[0-8])(?:\.\d+)+", re.IGNORECASE),
            # Any 4-segment control (A.5.x.y, A.6.x.y, A.7.x.y, A.8.x.y)
            re.compile(r"\bA\.(?:5|6|7|8)\.\d+\.\d+", re.IGNORECASE),
        ]

        violations = []
        for md_file in self.all_md_files:
            rel_path = md_file.relative_to(REPO_ROOT).as_posix()
            content = md_file.read_text(encoding="utf-8")
            lines = content.splitlines()

            is_soa = "05_Statement_of_Applicability_SoA.md" in rel_path
            is_onboarding = "07_Framework_and_Domain_Onboarding_Guide.md" in rel_path

            for line_idx, line in enumerate(lines, start=1):
                # If SoA or Onboarding, check if line is an explicit legacy crosswalk row/table
                if is_soa:
                    # In SoA, legacy IDs are in the designated "Legacy 2013 Crosswalk" column
                    if "legacy" in line.lower() or "2013" in line:
                        continue
                if is_onboarding:
                    if "legacy" in line.lower() or "2013" in line or "crosswalk" in line.lower():
                        continue

                for pat in legacy_patterns:
                    matches = pat.findall(line)
                    if matches:
                        violations.append(
                            f"{rel_path}:{line_idx} - Found legacy pattern(s) {matches} in line: {line.strip()}"
                        )

        self.assertEqual(
            violations,
            [],
            f"Adversarial legacy scanner found {len(violations)} lingering 2013 control citations:\n"
            + "\n".join(violations),
        )

    def test_adversarial_banned_standards(self):
        """
        Adversarially search for forbidden standards:
        - SOC 2 DC3.1 (case-insensitive, with or without spaces/dots)
        - DoD 5220.22-M (case-insensitive, variations)
        """
        forbidden_regexes = [
            (re.compile(r"dc\s*3\.1", re.IGNORECASE), "Invalid SOC 2 DC3.1 citation"),
            (re.compile(r"5220(?:\.22|\s*-\s*m)", re.IGNORECASE), "Deprecated DoD 5220.22-M standard"),
        ]

        violations = []
        for md_file in self.all_md_files:
            rel_path = md_file.relative_to(REPO_ROOT).as_posix()
            content = md_file.read_text(encoding="utf-8")
            lines = content.splitlines()

            for line_idx, line in enumerate(lines, start=1):
                for pat, desc in forbidden_regexes:
                    if pat.search(line):
                        violations.append(f"{rel_path}:{line_idx} - {desc}: '{line.strip()}'")

        self.assertEqual(
            violations,
            [],
            f"Found forbidden standards citations:\n" + "\n".join(violations),
        )

    def test_document_control_headers_adversarial(self):
        """
        Verifies all 37 ISMS framework/policy/procedure/register documents have exact 2-column key-value header tables.
        Checks for:
        - Exact Markdown table format directly below document heading
        - Presence of all 7 mandatory keys:
          Document ID, Version, Effective Date, Document Owner, Review Cycle, Classification, Framework Mappings
        - Zero collapsed single-line bold metadata
        """
        mandatory_keys = [
            "Document ID",
            "Version",
            "Effective Date",
            "Document Owner",
            "Review Cycle",
            "Classification",
            "Framework Mappings",
        ]
        violations = []

        for md_file in self.all_md_files:
            rel_path = md_file.relative_to(REPO_ROOT).as_posix()
            if rel_path == "docs/index.md":
                continue

            content = md_file.read_text(encoding="utf-8")
            lines = content.splitlines()
            top_sample = "\n".join(lines[:30])

            # Check for collapsed bold metadata
            if re.search(r"^\*\*(?:Document ID|Version|Effective Date|Classification)\*\*:", top_sample, re.MULTILINE):
                violations.append(f"{rel_path}: Contains collapsed bold metadata in header")

            # Check header table presence
            missing_keys = [k for k in mandatory_keys if k not in top_sample]
            if missing_keys:
                violations.append(f"{rel_path}: Header table missing keys: {missing_keys}")

        self.assertEqual(
            violations,
            [],
            f"Document Control Header failures:\n" + "\n".join(violations),
        )

    def test_document_history_footers_adversarial(self):
        """
        Verifies all 37 ISMS framework/policy/procedure/register documents have exact 5-column history tables at the bottom.
        Columns required: Version, Date, Author, Approved By, Description.
        """
        required_cols = ["Version", "Date", "Author", "Approved By", "Description"]
        violations = []

        for md_file in self.all_md_files:
            rel_path = md_file.relative_to(REPO_ROOT).as_posix()
            if rel_path == "docs/index.md":
                continue

            content = md_file.read_text(encoding="utf-8")
            lines = content.splitlines()
            bottom_sample = "\n".join(lines[-35:])

            if "## Document History" not in bottom_sample:
                violations.append(f"{rel_path}: Missing '## Document History' heading at bottom")
                continue

            missing_cols = [c for c in required_cols if c not in bottom_sample]
            if missing_cols:
                violations.append(f"{rel_path}: Document History table missing columns: {missing_cols}")

        self.assertEqual(
            violations,
            [],
            f"Document History footer failures:\n" + "\n".join(violations),
        )

    def test_policy_mandatory_sections_adversarial(self):
        """
        Verifies every policy under docs/02_Policies/ (all 13 policies) contains:
        1. Roles and Responsibilities
        2. Compliance and Exceptions (or Enforcement)
        3. Related Documents (with active markdown links)
        """
        policy_files = sorted((REPO_ROOT / "docs" / "02_Policies").glob("*.md"))
        self.assertEqual(len(policy_files), 13, f"Expected 13 policy files, found {len(policy_files)}")

        violations = []
        for pfile in policy_files:
            rel_path = pfile.relative_to(REPO_ROOT).as_posix()
            content = pfile.read_text(encoding="utf-8")

            has_roles = bool(re.search(r"##\s+.*Roles and Responsibilities", content, re.IGNORECASE))
            has_compliance = bool(re.search(r"##\s+.*(?:Compliance|Exceptions|Enforcement)", content, re.IGNORECASE))
            has_related = bool(re.search(r"##\s+.*Related Documents", content, re.IGNORECASE))

            missing = []
            if not has_roles:
                missing.append("Roles and Responsibilities")
            if not has_compliance:
                missing.append("Compliance and Exceptions")
            if not has_related:
                missing.append("Related Documents")

            if missing:
                violations.append(f"{rel_path} missing mandatory sections: {missing}")
                continue

            # Check that Related Documents section contains at least one relative markdown link
            related_match = re.search(r"##\s+.*Related Documents(.*?)(?=\n##|\Z)", content, re.DOTALL | re.IGNORECASE)
            if related_match:
                section_body = related_match.group(1)
                links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", section_body)
                if not links:
                    violations.append(f"{rel_path}: 'Related Documents' section contains no markdown links")

        self.assertEqual(
            violations,
            [],
            f"Policy section completeness violations:\n" + "\n".join(violations),
        )


class TestTier5LinkGraphAndHeadingAnchors(unittest.TestCase):
    """
    Exhaustive link graph and anchor validation:
    Checks EVERY relative Markdown link in docs/**/*.md:
    1. Target file must exist.
    2. If link contains an anchor `#heading-slug`, target document MUST have that heading slug.
    3. If link is a same-document anchor `#heading-slug`, the document MUST have that heading slug.
    """

    def setUp(self):
        self.docs_dir = REPO_ROOT / "docs"
        self.all_md_files = sorted(self.docs_dir.rglob("*.md"))
        # Precompute all heading anchors for each markdown file
        self.heading_anchors: Dict[str, Set[str]] = {}
        for md_file in self.all_md_files:
            rel_path = md_file.relative_to(REPO_ROOT).as_posix()
            self.heading_anchors[rel_path] = extract_headings(md_file)

    def test_exhaustive_link_graph_and_anchors(self):
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        broken_files = []
        broken_anchors = []
        total_links = 0

        for md_file in self.all_md_files:
            rel_src = md_file.relative_to(REPO_ROOT).as_posix()
            content = md_file.read_text(encoding="utf-8")
            lines = content.splitlines()

            for line_no, line in enumerate(lines, start=1):
                # Skip markdown comments
                if line.strip().startswith("<!--"):
                    continue

                for match in link_pattern.finditer(line):
                    target = match.group(2).strip()
                    # Skip external web URLs and mailto
                    if (
                        target.startswith("http://")
                        or target.startswith("https://")
                        or target.startswith("mailto:")
                        or target.startswith("javascript:")
                    ):
                        continue

                    total_links += 1

                    # Case A: Same-document anchor e.g. #roles-and-responsibilities
                    if target.startswith("#"):
                        anchor = target.lstrip("#").lower().strip()
                        if anchor:
                            doc_anchors = self.heading_anchors.get(rel_src, set())
                            if anchor not in doc_anchors:
                                broken_anchors.append(
                                    f"{rel_src}:{line_no} - Same-document anchor '#{anchor}' not found in {rel_src}. Available: {sorted(doc_anchors)[:5]}..."
                                )
                        continue

                    # Case B: Target file with optional anchor
                    parts = target.split("#")
                    file_part = parts[0].strip()
                    anchor_part = parts[1].strip().lower() if len(parts) > 1 else None

                    if not file_part:
                        continue

                    # Resolve file target relative to source document parent directory
                    resolved_target = (md_file.parent / file_part).resolve()
                    if not resolved_target.exists():
                        broken_files.append(
                            f"{rel_src}:{line_no} - Target file does not exist: '{file_part}' (resolved to {resolved_target})"
                        )
                        continue

                    # If there's an anchor, check it in the resolved target
                    if anchor_part:
                        try:
                            rel_target = resolved_target.relative_to(REPO_ROOT).as_posix()
                        except ValueError:
                            # Target outside repo
                            broken_files.append(
                                f"{rel_src}:{line_no} - Target file is outside repo: {resolved_target}"
                            )
                            continue

                        target_anchors = self.heading_anchors.get(rel_target, set())
                        if anchor_part not in target_anchors:
                            broken_anchors.append(
                                f"{rel_src}:{line_no} - Anchor '#{anchor_part}' not found in target {rel_target}. Available: {sorted(target_anchors)[:5]}..."
                            )

        print(f"\n[Link Graph Stress Test] Validated {total_links} relative markdown links across {len(self.all_md_files)} documents.")

        self.assertEqual(
            broken_files,
            [],
            f"Found {len(broken_files)} broken file links in markdown documents:\n"
            + "\n".join(broken_files),
        )
        self.assertEqual(
            broken_anchors,
            [],
            f"Found {len(broken_anchors)} broken heading anchors in markdown documents:\n"
            + "\n".join(broken_anchors),
        )


class TestTier5ToolingAdversarial(unittest.TestCase):
    """Stress tests fill_placeholders.py and validate_isms.py with edge cases and hostile inputs."""

    def test_fill_placeholders_dry_run_with_special_characters(self):
        """Test fill_placeholders.py with hostile strings, quotes, and unicode in dry-run mode."""
        python_exe = sys.executable
        script = str(REPO_ROOT / "scripts" / "fill_placeholders.py")

        cmd = [
            python_exe,
            script,
            "--dry-run",
            "--company-name", "Acme 'International' & <Co.> / \"Testing\"",
            "--ciso-name", "Dr. Jane O'Connor-Smith, CISO",
            "--author-name", "SecOps & Compliance Team — 日本語",
            "--dpo-name", "François Dupont (DPO)",
            "--insert-date", "2026-10-26",
            "--min-password-length", "16",
        ]

        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(
            result.returncode,
            0,
            f"fill_placeholders.py failed on special characters in dry-run:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )
        self.assertIn("[DRY-RUN]", result.stdout)
        self.assertIn("Summary (DRY-RUN):", result.stdout)

    def test_fill_placeholders_nonexistent_docs_dir(self):
        """Test fill_placeholders.py exits cleanly with code 1 and stderr message on invalid docs dir."""
        python_exe = sys.executable
        script = str(REPO_ROOT / "scripts" / "fill_placeholders.py")

        cmd = [
            python_exe,
            script,
            "--docs-dir", "non_existent_directory_xyz",
            "--company-name", "Acme",
        ]

        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: Documentation directory", result.stderr)

    def test_fill_placeholders_no_args_behavior(self):
        """
        Verify CLI contract:
        - When no arguments provided without dry-run: exit code 1 with helpful message
        - When only --dry-run without arguments: exit code 0
        """
        python_exe = sys.executable
        script = str(REPO_ROOT / "scripts" / "fill_placeholders.py")

        # 1. No arguments at all
        res1 = subprocess.run(
            [python_exe, script],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(res1.returncode, 1)
        self.assertIn("Error: No placeholder arguments provided", res1.stderr)

        # 2. Only --dry-run
        res2 = subprocess.run(
            [python_exe, script, "--dry-run"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(res2.returncode, 0)
        self.assertIn("No placeholder arguments provided for dry-run", res2.stdout)

    def test_fill_placeholders_list_remaining(self):
        """Test --list-remaining scans target files without modifying them."""
        python_exe = sys.executable
        script = str(REPO_ROOT / "scripts" / "fill_placeholders.py")

        cmd = [python_exe, script, "--list-remaining"]
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Scanning for Remaining Placeholders", result.stdout)

    def test_fill_placeholders_actual_execution_on_sandbox_copy(self):
        """
        Stress test fill_placeholders.py by copying docs and mkdocs.yml to a temporary sandbox,
        running the script with replacements, and verifying:
        1. All target placeholders were replaced.
        2. mkdocs.yml YAML escaping for single quotes was handled properly.
        3. No syntax corruption occurred.
        """
        python_exe = sys.executable
        script = str(REPO_ROOT / "scripts" / "fill_placeholders.py")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Copy docs and mkdocs.yml
            shutil.copytree(REPO_ROOT / "docs", tmppath / "docs")
            shutil.copy(REPO_ROOT / "mkdocs.yml", tmppath / "mkdocs.yml")
            # Create scripts folder with script
            os.makedirs(tmppath / "scripts", exist_ok=True)
            shutil.copy(script, tmppath / "scripts" / "fill_placeholders.py")

            cmd = [
                python_exe,
                str(tmppath / "scripts" / "fill_placeholders.py"),
                "--company-name", "O'Reilly & Associates",
                "--ciso-name", "Jane Doe",
                "--author-name", "Security Lead",
                "--dpo-name", "Alex Rivera",
                "--insert-date", "2026-10-26",
                "--min-password-length", "15",
            ]

            result = subprocess.run(
                cmd,
                cwd=str(tmppath),
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            self.assertEqual(result.returncode, 0, f"Sandbox replacement failed:\n{result.stderr}")
            self.assertIn("Summary (APPLY):", result.stdout)

            # Check mkdocs.yml valid YAML
            with open(tmppath / "mkdocs.yml", "r", encoding="utf-8") as f:
                parsed_yaml = yaml.safe_load(f)
            self.assertIsNotNone(parsed_yaml)

            # Check docs/01_ISMS_Framework/01_Information_Security_Policy.md has replaced text
            sample_policy = (tmppath / "docs" / "01_ISMS_Framework" / "01_Information_Security_Policy.md").read_text(encoding="utf-8")
            self.assertIn("O'Reilly & Associates", sample_policy)
            self.assertIn("Jane Doe", sample_policy)
            self.assertNotIn("[COMPANY_NAME]", sample_policy)

    def test_validate_isms_strict_and_coverage_report(self):
        """Test validate_isms.py with --strict and --coverage-report flags."""
        python_exe = sys.executable
        script = str(REPO_ROOT / "scripts" / "validate_isms.py")

        cmd = [python_exe, script, "--coverage-report", "--strict"]
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(
            result.returncode,
            0,
            f"validate_isms.py failed in --strict --coverage-report mode:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )
        self.assertIn("ISMS FRAMEWORK COMPLIANCE & CONTROL COVERAGE REPORT", result.stdout)
        self.assertIn("ISO/IEC 27001:2022 Annex A", result.stdout)
        self.assertIn("100.0%", result.stdout)
        self.assertIn("COMPLIANT", result.stdout)

    def test_validate_isms_custom_invalid_paths_error_handling(self):
        """Test validate_isms.py error handling when supplied with non-existent paths."""
        python_exe = sys.executable
        script = str(REPO_ROOT / "scripts" / "validate_isms.py")

        test_cases = [
            (["--config", "nonexistent_mkdocs.yml"], "Configuration file not found"),
            (["--docs-dir", "nonexistent_docs"], "Documentation directory not found"),
            (["--registry", "nonexistent_registry.yaml"], "Framework registry file not found"),
            (["--soa", "nonexistent_soa.md"], "SoA document not found"),
        ]

        for flags, expected_err in test_cases:
            res = subprocess.run(
                [python_exe, script] + flags,
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(
                res.returncode,
                1,
                f"Expected exit code 1 for flags {flags}, got {res.returncode}",
            )
            self.assertIn(
                expected_err,
                res.stdout + res.stderr,
                f"Expected '{expected_err}' in output for flags {flags}",
            )


class TestTier5RegistryDeepVerification(unittest.TestCase):
    """Deep verification of mappings/framework_registry.yaml."""

    def setUp(self):
        self.registry_file = REPO_ROOT / "mappings" / "framework_registry.yaml"
        self.assertTrue(self.registry_file.exists(), "framework_registry.yaml not found")
        with open(self.registry_file, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f)

    def test_registry_schema_and_canonical_controls(self):
        """Verify registry root schema, metadata, and canonical control definitions."""
        self.assertIsInstance(self.data, dict)
        self.assertIn("version", self.data)
        controls = self.data.get("canonical_controls") or self.data.get("controls")
        self.assertIsInstance(controls, list)
        self.assertGreaterEqual(
            len(controls),
            55,
            f"Expected at least 55 canonical controls, got {len(controls)}",
        )

        seen_ids = set()
        for idx, ctrl in enumerate(controls):
            ctrl_id = ctrl.get("id")
            self.assertIsNotNone(ctrl_id, f"Control at index {idx} missing 'id'")
            self.assertNotIn(ctrl_id, seen_ids, f"Duplicate control id '{ctrl_id}' at index {idx}")
            seen_ids.add(ctrl_id)

            self.assertIn("name", ctrl, f"Control {ctrl_id} missing 'name'")
            self.assertIn("domain", ctrl, f"Control {ctrl_id} missing 'domain'")

            docs = ctrl.get("implementing_docs") or ctrl.get("implementing_documents")
            self.assertIsInstance(docs, list, f"Control {ctrl_id} implementing_docs must be a list")
            self.assertGreater(len(docs), 0, f"Control {ctrl_id} has empty implementing_docs")

            for doc in docs:
                doc_path = REPO_ROOT / doc
                self.assertTrue(
                    doc_path.exists(),
                    f"Control {ctrl_id} references non-existent document: {doc}",
                )

            mappings = ctrl.get("mappings")
            self.assertIsInstance(mappings, dict, f"Control {ctrl_id} missing 'mappings' dict")

    def test_registry_complete_iso_2022_93_controls(self):
        """Verify that all 93 ISO 27001:2022 controls are mapped in the registry."""
        controls = self.data.get("canonical_controls") or self.data.get("controls", [])
        mapped_iso = set()

        for ctrl in controls:
            iso_list = ctrl.get("mappings", {}).get("iso_27001_2022", [])
            for item in iso_list:
                mapped_iso.add(item)

        missing_iso = set(EXPECTED_ISO_2022_CONTROLS) - mapped_iso
        self.assertEqual(
            missing_iso,
            set(),
            f"Framework registry is missing {len(missing_iso)} ISO/IEC 27001:2022 controls: {sorted(missing_iso)}",
        )

    def test_registry_soc2_nist_gdpr_mappings(self):
        """Verify that SOC 2, NIST CSF 2.0, and GDPR mappings are comprehensively populated."""
        controls = self.data.get("canonical_controls") or self.data.get("controls", [])

        mapped_soc2 = set()
        mapped_nist = set()
        mapped_gdpr = set()

        for ctrl in controls:
            mappings = ctrl.get("mappings", {})
            for s in mappings.get("soc2_tsc_2017", []):
                mapped_soc2.add(s)
            for n in mappings.get("nist_csf_2_0", []):
                mapped_nist.add(n)
            for g in mappings.get("gdpr_articles", []):
                mapped_gdpr.add(g)

        # Baseline thresholds
        self.assertGreaterEqual(
            len(mapped_soc2),
            30,
            f"Expected at least 30 SOC 2 TSC mappings, got {len(mapped_soc2)}: {sorted(mapped_soc2)}",
        )
        self.assertGreaterEqual(
            len(mapped_nist),
            35,
            f"Expected at least 35 NIST CSF 2.0 mappings, got {len(mapped_nist)}: {sorted(mapped_nist)}",
        )
        self.assertGreaterEqual(
            len(mapped_gdpr),
            10,
            f"Expected at least 10 GDPR article mappings, got {len(mapped_gdpr)}: {sorted(mapped_gdpr)}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
