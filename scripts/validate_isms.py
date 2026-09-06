#!/usr/bin/env python3
"""
scripts/validate_isms.py
Compliance and Integrity Validator for security-standards-template ISMS.

Validates:
1. Navigation and Filesystem Parity (mkdocs.yml vs docs/**/*.md)
2. Relative Markdown Link Integrity
3. Deprecated ISO 2013 and Invalid Citations Detector
4. 93-Control Statement of Applicability (SoA) Completeness & Implementing Links
5. Document Control Header and History Footer Table Standardization
6. Framework Control Registry & Coverage Reporting (--coverage-report)
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

try:
    import yaml
except ModuleNotFoundError:
    # Automatically delegate to local .venv Python if PyYAML is not in the global Python
    candidate_venvs = [
        REPO_ROOT / ".venv" / "Scripts" / "python.exe",
        REPO_ROOT / ".venv" / "bin" / "python",
    ]
    for venv_py in candidate_venvs:
        if venv_py.exists() and Path(sys.executable).resolve() != venv_py.resolve():
            sys.exit(subprocess.call([str(venv_py), *sys.argv]))
    raise

# 93 ISO/IEC 27001:2022 controls
EXPECTED_ISO_2022_CONTROLS = (
    [f"A.5.{i}" for i in range(1, 38)]
    + [f"A.6.{i}" for i in range(1, 9)]
    + [f"A.7.{i}" for i in range(1, 15)]
    + [f"A.8.{i}" for i in range(1, 35)]
)

REQUIRED_HEADER_KEYS = [
    "Document ID",
    "Version",
    "Effective Date",
    "Document Owner",
    "Review Cycle",
    "Classification",
    "Framework Mappings",
]

REQUIRED_FOOTER_COLUMNS = [
    "Version",
    "Date",
    "Author",
    "Approved By",
    "Description",
]


def extract_nav_targets(nav_item, collected: List[str]):
    """Recursively extract target markdown files from mkdocs nav structure."""
    if isinstance(nav_item, str):
        collected.append(nav_item.replace("\\", "/").lstrip("/"))
    elif isinstance(nav_item, dict):
        for val in nav_item.values():
            extract_nav_targets(val, collected)
    elif isinstance(nav_item, list):
        for item in nav_item:
            extract_nav_targets(item, collected)


def validate_nav_parity(docs_dir: Path, mkdocs_file: Path) -> List[str]:
    """Module 1: Verify 100% bidirectional parity between mkdocs.yml and docs/."""
    errors = []
    if not mkdocs_file.exists():
        return [f"Configuration file not found: {mkdocs_file}"]
    if not docs_dir.exists():
        return [f"Documentation directory not found: {docs_dir}"]

    try:
        with open(mkdocs_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        return [f"Failed to parse {mkdocs_file}: {e}"]

    nav = config.get("nav", [])
    if not nav:
        return [f"No 'nav' section found in {mkdocs_file}"]

    nav_targets: List[str] = []
    extract_nav_targets(nav, nav_targets)
    nav_set = set(nav_targets)

    disk_files = [
        p.relative_to(docs_dir).as_posix()
        for p in docs_dir.rglob("*.md")
    ]
    disk_set = set(disk_files)

    orphaned = disk_set - nav_set
    dead = nav_set - disk_set

    for o in sorted(orphaned):
        errors.append(f"Orphaned documentation file not in navigation: docs/{o}")
    for d in sorted(dead):
        errors.append(f"Dead navigation target not found on disk: {d}")

    return errors


def validate_relative_links(docs_dir: Path) -> List[str]:
    """Module 2: Verify all relative markdown links resolve to existing files."""
    errors = []
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    for md_file in sorted(docs_dir.rglob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"Cannot read {md_file}: {e}")
            continue

        rel_src = md_file.relative_to(REPO_ROOT).as_posix()
        lines = content.splitlines()

        for line_num, line in enumerate(lines, 1):
            for match in link_pattern.finditer(line):
                target = match.group(2).strip()
                if (
                    not target
                    or target.startswith("#")
                    or target.startswith("http://")
                    or target.startswith("https://")
                    or target.startswith("mailto:")
                    or "[" in target
                ):
                    continue

                file_target = target.split("#")[0].strip()
                if not file_target:
                    continue

                resolved = (md_file.parent / file_target).resolve()
                if not resolved.exists():
                    errors.append(
                        f"{rel_src}:{line_num}: Broken relative link '{target}' -> {resolved}"
                    )

    return errors


def validate_deprecated_citations(docs_dir: Path) -> List[str]:
    """Module 3: Check for obsolete ISO 2013 Annex A IDs and banned standards."""
    errors = []
    iso_2013_re = re.compile(
        r"\bA\.(?:9|1[0-8])\.\d+(?:\.\d+)?|\bA\.(?:5|6|7)\.\d+\.\d+",
        re.IGNORECASE,
    )

    for md_file in sorted(docs_dir.rglob("*.md")):
        rel_path = md_file.relative_to(REPO_ROOT).as_posix()
        content = md_file.read_text(encoding="utf-8")
        lines = content.splitlines()

        is_soa = "05_Statement_of_Applicability_SoA.md" in rel_path
        is_onboarding = "07_Framework_and_Domain_Onboarding_Guide.md" in rel_path

        for idx, line in enumerate(lines, 1):
            match = iso_2013_re.search(line)
            if match:
                if is_soa and ("legacy" in line.lower() or "2013" in line):
                    continue
                if is_onboarding and (
                    "crosswalk" in line.lower()
                    or "2013" in line
                    or "legacy" in line.lower()
                ):
                    continue

                errors.append(
                    f"{rel_path}:{idx}: Found deprecated ISO 2013 citation '{match.group(0)}' outside legacy crosswalk"
                )

            if "SOC 2 DC3.1" in line or "DC3.1" in line:
                errors.append(f"{rel_path}:{idx}: Contains invalid citation 'SOC 2 DC3.1'")
            if "DoD 5220.22-M" in line or "DoD 5220" in line:
                errors.append(f"{rel_path}:{idx}: Contains deprecated standard 'DoD 5220.22-M'")

    return errors


def validate_soa_completeness(soa_path: Path) -> List[str]:
    """Module 4: Verify 93 ISO 27001:2022 controls and implementing links in SoA."""
    errors = []
    if not soa_path.exists():
        return [f"SoA document not found at {soa_path}"]

    content = soa_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    found_controls: Set[str] = set()
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    for line in lines:
        if not line.strip().startswith("|"):
            continue
        for ctrl in EXPECTED_ISO_2022_CONTROLS:
            pattern = rf"\|\s*(?:\*\*)?{re.escape(ctrl)}(?:\*\*)?\s*\|"
            if re.search(pattern, line):
                found_controls.add(ctrl)
                links = link_pattern.findall(line)
                if not links:
                    errors.append(f"SoA control {ctrl} has no implementing document link")
                else:
                    for label, target in links:
                        if target.startswith("http") or target.startswith("#"):
                            continue
                        file_target = target.split("#")[0].strip()
                        if file_target:
                            resolved = (soa_path.parent / file_target).resolve()
                            if not resolved.exists():
                                errors.append(
                                    f"SoA control {ctrl} link '{target}' resolves to non-existent file: {resolved}"
                                )

    missing = set(EXPECTED_ISO_2022_CONTROLS) - found_controls
    for m in sorted(missing):
        errors.append(f"SoA is missing mandatory ISO 27001:2022 control: {m}")

    return errors


def validate_document_headers_footers(docs_dir: Path) -> List[str]:
    """Module 5: Validate Document Control Header & History Table standardization."""
    errors = []
    collapsed_bold_re = re.compile(
        r"^\*\*(?:Document ID|Version|Effective Date|Document Owner|Classification)\*\*:",
        re.MULTILINE,
    )

    for md_file in sorted(docs_dir.rglob("*.md")):
        rel_path = md_file.relative_to(REPO_ROOT).as_posix()
        # Skip top-level index.md
        if rel_path == "docs/index.md":
            continue

        content = md_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        header_sample = "\n".join(lines[:25])
        footer_sample = "\n".join(lines[-35:])

        # Header checks
        if collapsed_bold_re.search(header_sample):
            errors.append(
                f"{rel_path}: Contains deprecated collapsed single-line bold metadata in header"
            )

        missing_keys = [k for k in REQUIRED_HEADER_KEYS if k not in header_sample]
        if missing_keys:
            errors.append(
                f"{rel_path}: Header table missing required keys: {missing_keys}"
            )

        # Footer checks
        if "Document History" not in footer_sample:
            errors.append(
                f"{rel_path}: Missing '## Document History' section at document end"
            )
        else:
            missing_cols = [c for c in REQUIRED_FOOTER_COLUMNS if c not in footer_sample]
            if missing_cols:
                errors.append(
                    f"{rel_path}: Document History table missing columns: {missing_cols}"
                )

        # Policy mandatory sections
        if "02_Policies/" in rel_path:
            has_roles = bool(re.search(r"##\s+.*Roles and Responsibilities", content, re.IGNORECASE))
            has_compliance = bool(
                re.search(r"##\s+.*(?:Compliance|Exceptions|Enforcement)", content, re.IGNORECASE)
            )
            has_related = bool(re.search(r"##\s+.*Related Documents", content, re.IGNORECASE))

            missing_sections = []
            if not has_roles:
                missing_sections.append("Roles and Responsibilities")
            if not has_compliance:
                missing_sections.append("Compliance and Exceptions")
            if not has_related:
                missing_sections.append("Related Documents")

            if missing_sections:
                errors.append(f"{rel_path}: Policy missing mandatory sections: {missing_sections}")

    return errors


def validate_registry_schema_and_files(registry_path: Path) -> Tuple[List[str], Dict]:
    """Module 6A: Validate framework registry YAML schema and file references."""
    errors = []
    if not registry_path.exists():
        return [f"Framework registry file not found: {registry_path}"], {}

    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        return [f"Failed to parse framework registry YAML: {e}"], {}

    if not isinstance(data, dict):
        return [f"Registry root must be a dictionary, got {type(data)}"], {}

    controls = data.get("controls") or data.get("canonical_controls", [])
    if len(controls) < 55:
        errors.append(
            f"Framework registry must define at least 55 canonical controls, found {len(controls)}"
        )

    for ctrl in controls:
        ctrl_id = ctrl.get("id", "UNKNOWN")
        doc_list = ctrl.get("implementing_documents") or ctrl.get("implementing_docs") or []
        if not doc_list:
            errors.append(f"Control {ctrl_id} has no implementing documents")
        for doc in doc_list:
            doc_file = REPO_ROOT / doc
            if not doc_file.exists():
                errors.append(
                    f"Control {ctrl_id} references non-existent implementing document: {doc}"
                )

    return errors, data


def generate_coverage_report(registry_data: Dict) -> Tuple[str, bool]:
    """Module 6B: Compute and format coverage report across all frameworks."""
    controls = registry_data.get("controls") or registry_data.get("canonical_controls", [])

    mapped_iso: Set[str] = set()
    mapped_soc2: Set[str] = set()
    mapped_nist: Set[str] = set()
    mapped_gdpr: Set[str] = set()

    for ctrl in controls:
        mappings = ctrl.get("mappings", {})
        # ISO 27001:2022
        iso_items = (
            mappings.get("iso_27001_2022")
            or mappings.get("iso27001_2022")
            or mappings.get("iso_27001")
            or []
        )
        for i in iso_items:
            mapped_iso.add(i)

        # SOC 2 TSC
        soc2_items = (
            mappings.get("soc2_tsc")
            or mappings.get("soc2_tsc_2017")
            or mappings.get("soc2")
            or []
        )
        for s in soc2_items:
            mapped_soc2.add(s)

        # NIST CSF 2.0
        nist_items = (
            mappings.get("nist_csf_2_0")
            or mappings.get("nist_csf")
            or mappings.get("nist")
            or []
        )
        for n in nist_items:
            mapped_nist.add(n)

        # GDPR
        gdpr_items = (
            mappings.get("gdpr")
            or mappings.get("gdpr_articles")
            or []
        )
        for g in gdpr_items:
            mapped_gdpr.add(g)

    total_iso_target = 93
    total_soc2_target = 38
    total_nist_target = 42
    total_gdpr_target = 13

    iso_pct = (len(mapped_iso) / total_iso_target) * 100.0
    soc2_pct = min(100.0, (len(mapped_soc2) / total_soc2_target) * 100.0)
    nist_pct = min(100.0, (len(mapped_nist) / total_nist_target) * 100.0)
    gdpr_pct = min(100.0, (len(mapped_gdpr) / total_gdpr_target) * 100.0)

    report_lines = [
        "================================================================================",
        "          ISMS FRAMEWORK COMPLIANCE & CONTROL COVERAGE REPORT",
        "================================================================================",
        f"Total Canonical Controls Defined: {len(controls)}",
        "",
        "| Framework / Standard | Version | Mapped / Benchmark | Coverage % | Status |",
        "| :--- | :--- | :---: | :---: | :---: |",
        f"| ISO/IEC 27001:2022 Annex A | 2022 | {len(mapped_iso)} / {total_iso_target} | {iso_pct:.1f}% | {'COMPLIANT' if iso_pct >= 100.0 else 'PARTIAL'} |",
        f"| AICPA SOC 2 (2017/2022 TSC) | 2017/2022 | {len(mapped_soc2)} / {total_soc2_target} | {soc2_pct:.1f}% | {'COMPLIANT' if soc2_pct >= 100.0 else 'PARTIAL'} |",
        f"| NIST Cybersecurity Framework 2.0 | 2.0 | {len(mapped_nist)} / {total_nist_target} | {nist_pct:.1f}% | {'COMPLIANT' if nist_pct >= 100.0 else 'PARTIAL'} |",
        f"| General Data Protection Regulation (GDPR) | 2016/679 | {len(mapped_gdpr)} / {total_gdpr_target} | {gdpr_pct:.1f}% | {'COMPLIANT' if gdpr_pct >= 100.0 else 'PARTIAL'} |",
        "================================================================================",
    ]

    all_compliant = iso_pct >= 100.0 and len(controls) >= 55
    return "\n".join(report_lines), all_compliant


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ISMS Compliance and Integrity Validator"
    )
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Path to documentation directory (default: docs)",
    )
    parser.add_argument(
        "--config",
        default="mkdocs.yml",
        help="Path to mkdocs.yml (default: mkdocs.yml)",
    )
    parser.add_argument(
        "--registry",
        default="mappings/framework_registry.yaml",
        help="Path to framework registry YAML",
    )
    parser.add_argument(
        "--soa",
        default="docs/01_ISMS_Framework/05_Statement_of_Applicability_SoA.md",
        help="Path to Statement of Applicability document",
    )
    parser.add_argument(
        "--coverage-report",
        action="store_true",
        help="Generate and display framework coverage report",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Treat warnings as fatal errors",
    )

    args = parser.parse_args()

    docs_dir = (REPO_ROOT / args.docs_dir).resolve()
    mkdocs_file = (REPO_ROOT / args.config).resolve()
    registry_file = (REPO_ROOT / args.registry).resolve()
    soa_file = (REPO_ROOT / args.soa).resolve()

    all_errors: List[str] = []

    # Run validation modules
    print(f"[*] Validating MkDocs Navigation Parity against {docs_dir.name}/ ...")
    nav_errors = validate_nav_parity(docs_dir, mkdocs_file)
    all_errors.extend(nav_errors)

    print("[*] Validating Relative Markdown Links ...")
    link_errors = validate_relative_links(docs_dir)
    all_errors.extend(link_errors)

    print("[*] Scanning for Deprecated ISO 2013 & Invalid Standard Citations ...")
    citation_errors = validate_deprecated_citations(docs_dir)
    all_errors.extend(citation_errors)

    print("[*] Validating Statement of Applicability (93 controls) ...")
    soa_errors = validate_soa_completeness(soa_file)
    all_errors.extend(soa_errors)

    print("[*] Validating Document Control Header and History Tables ...")
    hf_errors = validate_document_headers_footers(docs_dir)
    all_errors.extend(hf_errors)

    print("[*] Validating Canonical Control Registry ...")
    reg_errors, registry_data = validate_registry_schema_and_files(registry_file)
    all_errors.extend(reg_errors)

    # Coverage report
    if args.coverage_report and registry_data:
        report_text, report_ok = generate_coverage_report(registry_data)
        print("\n" + report_text + "\n")
        if not report_ok:
            all_errors.append("Coverage report indicates missing ISO 27001:2022 controls or insufficient canonical controls.")

    # Result evaluation
    if all_errors:
        print(f"\n[FAIL] Found {len(all_errors)} validation violation(s):")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("\n[PASS] All ISMS validation checks passed cleanly (0 errors).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
