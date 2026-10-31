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
6. Framework Control Registry & JSON Schema Validation
7. Authoritative Reference Catalog Integrity (all 6 frameworks)
8. Framework & Documentation Drift (--check-drift)
9. Framework Control Registry & 6-Framework Coverage Reporting (--coverage-report)
10. Multi-format output (--format {text,json,sarif,markdown})
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

try:
    import yaml
except ModuleNotFoundError:
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

E8_STRATEGY_NAMES = {
    "application_control": "Application Control",
    "patch_applications": "Patch Applications",
    "configure_office_macros": "Configure Microsoft Office Macro Settings",
    "user_application_hardening": "User Application Hardening",
    "restrict_admin_privileges": "Restrict Administrative Privileges",
    "patch_operating_systems": "Patch Operating Systems",
    "multi_factor_authentication": "Multi-Factor Authentication",
    "regular_backups": "Regular Backups",
}

E8_PREFIX_TO_STRATEGY = {
    "E8-AC": "application_control",
    "E8-PA": "patch_applications",
    "E8-OM": "configure_office_macros",
    "E8-AH": "user_application_hardening",
    "E8-UH": "user_application_hardening",
    "E8-AP": "restrict_admin_privileges",
    "E8-PO": "patch_operating_systems",
    "E8-MF": "multi_factor_authentication",
    "E8-RB": "regular_backups",
}


def get_rel_path(p: Path) -> str:
    """Safely return path relative to REPO_ROOT, or full path if outside."""
    try:
        return p.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def extract_nav_targets(nav_item: Any, collected: List[str]) -> None:
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
    errors: List[str] = []
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
    errors: List[str] = []
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    for md_file in sorted(docs_dir.rglob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"Cannot read {md_file}: {e}")
            continue

        rel_src = get_rel_path(md_file)
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
    errors: List[str] = []
    iso_2013_re = re.compile(
        r"\bA\.(?:9|1[0-8])\.\d+(?:\.\d+)?|\bA\.(?:5|6|7)\.\d+\.\d+",
        re.IGNORECASE,
    )

    for md_file in sorted(docs_dir.rglob("*.md")):
        rel_path = get_rel_path(md_file)
        content = md_file.read_text(encoding="utf-8")
        lines = content.splitlines()

        is_soa = "05_Statement_of_Applicability_SoA.md" in rel_path
        is_onboarding = "07_Framework_and_Domain_Onboarding_Guide.md" in rel_path
        is_crosswalk = "08_Multi_Framework_Crosswalk_and_OSCAL_Matrix.md" in rel_path

        for idx, line in enumerate(lines, 1):
            match = iso_2013_re.search(line)
            if match:
                if (is_soa or is_onboarding or is_crosswalk) and (
                    "legacy" in line.lower()
                    or "2013" in line
                    or "crosswalk" in line.lower()
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
    errors: List[str] = []
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
    errors: List[str] = []
    collapsed_bold_re = re.compile(
        r"^\*\*(?:Document ID|Version|Effective Date|Document Owner|Classification)\*\*:",
        re.MULTILINE,
    )

    for md_file in sorted(docs_dir.rglob("*.md")):
        rel_path = get_rel_path(md_file)
        if rel_path == "docs/index.md" or md_file.name == "index.md":
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


def validate_registry_schema_and_files(
    registry_path: Path, schema_path: Optional[Path] = None
) -> Tuple[List[str], Dict]:
    """Module 6: Validate framework registry YAML against JSON schema and check file references."""
    errors: List[str] = []
    if not registry_path.exists():
        return [f"Framework registry file not found: {registry_path}"], {}

    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        return [f"Failed to parse framework registry YAML: {e}"], {}

    if not isinstance(data, dict):
        return [f"Registry root must be a dictionary, got {type(data)}"], {}

    # JSON Schema validation
    if schema_path is not None:
        if not schema_path.exists():
            errors.append(f"Framework registry schema file not found: {schema_path}")
        elif not schema_path.is_file():
            errors.append(f"Framework registry schema path is not a file: {schema_path}")
        else:
            try:
                import jsonschema

                with open(schema_path, "r", encoding="utf-8") as sf:
                    schema_data = json.load(sf)
                validator_cls = jsonschema.validators.validator_for(schema_data)
                validator_cls.check_schema(schema_data)
                validator = validator_cls(schema_data)
                for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
                    path_str = " -> ".join(str(p) for p in err.path) if err.path else "root"
                    errors.append(f"Registry schema validation error at '{path_str}': {err.message}")
            except ModuleNotFoundError:
                # Fallback structural validation
                req_top = ["schema_version", "version", "metadata", "frameworks", "domains", "controls"]
                for k in req_top:
                    if k not in data:
                        errors.append(f"Registry missing required key: {k}")
            except Exception as e:
                errors.append(f"Registry schema validation error: {e}")
    else:
        # Fallback structural validation when no schema path is provided
        req_top = ["schema_version", "version", "metadata", "frameworks", "domains", "controls"]
        for k in req_top:
            if k not in data:
                errors.append(f"Registry missing required key: {k}")

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


def validate_catalog_integrity(registry_data: Dict, catalogs_dir: Path) -> List[str]:
    """Module 7: Verify all mapped control IDs across all 6 frameworks exist in mappings/catalogs/*.yaml."""
    errors: List[str] = []
    if not catalogs_dir.exists():
        return [f"Catalogs directory not found: {catalogs_dir}"]

    catalog_mapping = {
        "iso_27001_2022": ("iso_27001_2022.yaml", "iso_27001_2022"),
        "soc2_tsc_2017": ("soc2_tsc_2017.yaml", "soc2_tsc_2017"),
        "nist_csf_2_0": ("nist_csf_2_0.yaml", "nist_csf_2_0"),
        "gdpr": ("gdpr.yaml", "gdpr_articles"),
        "nist_sp_800_53_rev5": ("nist_sp_800_53_rev5.yaml", "nist_sp_800_53_rev5"),
        "asd_essential_eight": ("asd_essential_eight.yaml", "asd_essential_eight"),
    }

    catalog_controls: Dict[str, Set[str]] = {}

    for fw_key, (cat_filename, reg_key) in catalog_mapping.items():
        cat_file = catalogs_dir / cat_filename
        if not cat_file.exists():
            errors.append(f"Catalog file missing: {cat_file}")
            continue
        try:
            with open(cat_file, "r", encoding="utf-8") as f:
                cat_data = yaml.safe_load(f)
            ctrl_ids = {c["id"] for c in cat_data.get("controls", []) if isinstance(c, dict) and "id" in c}
            catalog_controls[fw_key] = ctrl_ids
        except Exception as e:
            errors.append(f"Failed to load catalog {cat_file}: {e}")

    controls = registry_data.get("controls") or registry_data.get("canonical_controls", [])

    for ctrl in controls:
        ctrl_id = ctrl.get("id", "UNKNOWN")
        mappings = ctrl.get("mappings", {})

        for fw_key, (cat_filename, reg_key) in catalog_mapping.items():
            valid_ids = catalog_controls.get(fw_key, set())
            mapped_items = mappings.get(reg_key, [])
            # Also allow fallback alternate keys
            if not mapped_items and fw_key == "gdpr":
                mapped_items = mappings.get("gdpr", [])
            elif not mapped_items and fw_key == "soc2_tsc_2017":
                mapped_items = mappings.get("soc2_tsc", [])

            for item in mapped_items:
                target_id = item if isinstance(item, str) else (item.get("id") if isinstance(item, dict) else None)
                if not target_id:
                    errors.append(f"Control {ctrl_id} has invalid empty {fw_key} mapping entry")
                    continue
                if target_id not in valid_ids:
                    errors.append(
                        f"Control {ctrl_id} maps unknown {fw_key} ID '{target_id}' not found in catalog {cat_filename}"
                    )

    return errors


def validate_drift(registry_data: Dict, soa_path: Path, docs_dir: Path) -> List[str]:
    """Module 8: Verify bidirectional consistency between framework registry and SoA / documentation."""
    errors: List[str] = []
    if not soa_path.exists():
        return [f"SoA document not found at {soa_path}"]

    controls = registry_data.get("controls") or registry_data.get("canonical_controls", [])

    # Map each ISO 27001:2022 control to its canonical control and implementing docs in registry
    reg_iso_to_docs: Dict[str, Set[str]] = {}
    for ctrl in controls:
        ctrl_docs = set(ctrl.get("implementing_docs") or ctrl.get("implementing_documents") or [])
        iso_items = ctrl.get("mappings", {}).get("iso_27001_2022", [])
        for item in iso_items:
            iso_id = item if isinstance(item, str) else item.get("id")
            if iso_id:
                reg_iso_to_docs.setdefault(iso_id, set()).update(ctrl_docs)

    # Parse SoA controls and implementing links
    content = soa_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    soa_iso_controls: Set[str] = set()

    for line in lines:
        if not line.strip().startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) >= 6:
            m = re.match(r"^(?:(?:\*\*)?(A\.\d+\.\d+)(?:\*\*)?)$", parts[0])
            if m:
                ctrl_id = m.group(1)
                soa_iso_controls.add(ctrl_id)
                links = link_pattern.findall(parts[5])
                soa_docs: Set[str] = set()
                for label, target in links:
                    if target.startswith("http") or target.startswith("#"):
                        continue
                    file_target = target.split("#")[0].strip()
                    if file_target:
                        resolved = (soa_path.parent / file_target).resolve()
                        rel = get_rel_path(resolved)
                        soa_docs.add(rel)

                reg_docs = reg_iso_to_docs.get(ctrl_id, set())
                if reg_docs and soa_docs and not soa_docs.intersection(reg_docs):
                    errors.append(
                        f"Drift detected for {ctrl_id}: SoA implementing docs {soa_docs} do not match registry {reg_docs}"
                    )

    # Bidirectional presence check
    missing_in_soa = set(reg_iso_to_docs.keys()) - soa_iso_controls
    for m in sorted(missing_in_soa):
        errors.append(f"Drift: ISO control {m} mapped in registry but missing from SoA table")

    missing_in_reg = soa_iso_controls - set(reg_iso_to_docs.keys())
    for m in sorted(missing_in_reg):
        errors.append(f"Drift: ISO control {m} present in SoA table but unmapped in registry")

    # Optional crosswalk doc 08 drift check if file exists
    crosswalk_doc = docs_dir / "01_ISMS_Framework" / "08_Multi_Framework_Crosswalk_and_OSCAL_Matrix.md"
    if crosswalk_doc.exists():
        cw_content = crosswalk_doc.read_text(encoding="utf-8")
        for ctrl in controls:
            cid = ctrl.get("id")
            if cid and cid not in cw_content:
                errors.append(f"Drift: Canonical control {cid} missing from crosswalk doc {crosswalk_doc.name}")

    return errors


def compute_coverage_metrics(registry_data: Dict, catalogs_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Compute exact coverage metrics across all 6 frameworks."""
    controls = registry_data.get("controls") or registry_data.get("canonical_controls", [])

    mapped_iso: Set[str] = set()
    mapped_soc2: Set[str] = set()
    mapped_nist_csf: Set[str] = set()
    mapped_gdpr: Set[str] = set()
    mapped_nist800: Set[str] = set()
    mapped_e8_strategies: Set[str] = set()
    mapped_e8_controls: Set[str] = set()

    # Load E8 strategy mappings from catalog if available
    e8_control_to_strategy: Dict[str, str] = {}
    if catalogs_dir is not None:
        e8_cat_file = catalogs_dir / "asd_essential_eight.yaml"
        if e8_cat_file.exists():
            try:
                with open(e8_cat_file, "r", encoding="utf-8") as f:
                    e8_cat_data = yaml.safe_load(f)
                for c in e8_cat_data.get("controls", []):
                    if isinstance(c, dict) and "id" in c and "strategy" in c:
                        e8_control_to_strategy[c["id"]] = c["strategy"]
            except Exception:
                pass

    for ctrl in controls:
        mappings = ctrl.get("mappings", {})

        # 1. ISO 27001:2022
        for i in mappings.get("iso_27001_2022") or mappings.get("iso27001_2022") or []:
            mapped_iso.add(i if isinstance(i, str) else i.get("id"))

        # 2. SOC 2 TSC
        for s in mappings.get("soc2_tsc_2017") or mappings.get("soc2_tsc") or []:
            mapped_soc2.add(s if isinstance(s, str) else s.get("id"))

        # 3. NIST CSF 2.0
        for n in mappings.get("nist_csf_2_0") or mappings.get("nist_csf") or []:
            mapped_nist_csf.add(n if isinstance(n, str) else n.get("id"))

        # 4. GDPR
        for g in mappings.get("gdpr_articles") or mappings.get("gdpr") or []:
            mapped_gdpr.add(g if isinstance(g, str) else g.get("id"))

        # 5. NIST SP 800-53 Rev. 5
        for sp in mappings.get("nist_sp_800_53_rev5") or []:
            sp_id = sp if isinstance(sp, str) else sp.get("id")
            if sp_id:
                mapped_nist800.add(sp_id)

        # 6. ASD Essential Eight
        for e8 in mappings.get("asd_essential_eight") or []:
            e8_id = e8 if isinstance(e8, str) else e8.get("id")
            if e8_id:
                mapped_e8_controls.add(e8_id)
                # Resolve strategy from catalog or prefix
                strat = e8_control_to_strategy.get(e8_id)
                if not strat:
                    for prefix, pstrat in E8_PREFIX_TO_STRATEGY.items():
                        if e8_id.startswith(prefix):
                            strat = pstrat
                            break
                if strat:
                    mapped_e8_strategies.add(strat)

    total_iso_target = 93
    total_soc2_target = 38
    total_nist_target = 45
    total_gdpr_target = 13
    total_nist800_target = 85
    total_e8_target = 8

    iso_pct = (len(mapped_iso) / total_iso_target) * 100.0 if total_iso_target else 100.0
    soc2_pct = min(100.0, (len(mapped_soc2) / total_soc2_target) * 100.0) if total_soc2_target else 100.0
    nist_pct = min(100.0, (len(mapped_nist_csf) / total_nist_target) * 100.0) if total_nist_target else 100.0
    gdpr_pct = min(100.0, (len(mapped_gdpr) / total_gdpr_target) * 100.0) if total_gdpr_target else 100.0
    nist800_pct = min(100.0, (len(mapped_nist800) / total_nist800_target) * 100.0) if total_nist800_target else 100.0
    e8_pct = min(100.0, (len(mapped_e8_strategies) / total_e8_target) * 100.0) if total_e8_target else 100.0

    return {
        "canonical_controls_count": len(controls),
        "frameworks": {
            "iso_27001_2022": {
                "name": "ISO/IEC 27001:2022 Annex A",
                "version": "2022",
                "mapped": len(mapped_iso),
                "benchmark": total_iso_target,
                "percentage": round(iso_pct, 1),
                "status": "COMPLIANT" if iso_pct >= 100.0 else "PARTIAL",
            },
            "soc2_tsc": {
                "name": "AICPA SOC 2 (2017/2022 TSC)",
                "version": "2017/2022",
                "mapped": len(mapped_soc2),
                "benchmark": total_soc2_target,
                "percentage": round(soc2_pct, 1),
                "status": "COMPLIANT" if soc2_pct >= 100.0 else "PARTIAL",
            },
            "nist_csf_2_0": {
                "name": "NIST Cybersecurity Framework 2.0",
                "version": "2.0",
                "mapped": len(mapped_nist_csf),
                "benchmark": total_nist_target,
                "percentage": round(nist_pct, 1),
                "status": "COMPLIANT" if nist_pct >= 100.0 else "PARTIAL",
            },
            "gdpr": {
                "name": "General Data Protection Regulation (GDPR)",
                "version": "2016/679",
                "mapped": len(mapped_gdpr),
                "benchmark": total_gdpr_target,
                "percentage": round(gdpr_pct, 1),
                "status": "COMPLIANT" if gdpr_pct >= 100.0 else "PARTIAL",
            },
            "nist_sp_800_53_rev5": {
                "name": "NIST SP 800-53 Rev. 5",
                "version": "Rev. 5",
                "mapped": len(mapped_nist800),
                "benchmark": total_nist800_target,
                "percentage": round(nist800_pct, 1),
                "status": "COMPLIANT" if nist800_pct >= 100.0 else "PARTIAL",
            },
            "asd_essential_eight": {
                "name": "ASD Essential Eight",
                "version": "ML1-ML3",
                "mapped": len(mapped_e8_strategies),
                "benchmark": total_e8_target,
                "percentage": round(e8_pct, 1),
                "status": "COMPLIANT" if e8_pct >= 100.0 else "PARTIAL",
            },
        },
    }


def generate_coverage_report(
    registry_data: Dict, catalogs_dir: Optional[Path] = None
) -> Tuple[str, bool]:
    """Module 9: Compute and format coverage report across all 6 frameworks preserving exact banner."""
    metrics = compute_coverage_metrics(registry_data, catalogs_dir)
    fws = metrics["frameworks"]
    ctrl_count = metrics["canonical_controls_count"]

    iso = fws["iso_27001_2022"]
    soc2 = fws["soc2_tsc"]
    csf = fws["nist_csf_2_0"]
    gdpr = fws["gdpr"]
    nist800 = fws["nist_sp_800_53_rev5"]
    e8 = fws["asd_essential_eight"]

    report_lines = [
        "================================================================================",
        "          ISMS FRAMEWORK COMPLIANCE & CONTROL COVERAGE REPORT",
        "================================================================================",
        f"Total Canonical Controls Defined: {ctrl_count}",
        "",
        "| Framework / Standard | Version | Mapped / Benchmark | Coverage % | Status |",
        "| :--- | :--- | :---: | :---: | :---: |",
        f"| {iso['name']} | {iso['version']} | {iso['mapped']} / {iso['benchmark']} | {iso['percentage']:.1f}% | {iso['status']} |",
        f"| {soc2['name']} | {soc2['version']} | {soc2['mapped']} / {soc2['benchmark']} | {soc2['percentage']:.1f}% | {soc2['status']} |",
        f"| {csf['name']} | {csf['version']} | {csf['mapped']} / {csf['benchmark']} | {csf['percentage']:.1f}% | {csf['status']} |",
        f"| {gdpr['name']} | {gdpr['version']} | {gdpr['mapped']} / {gdpr['benchmark']} | {gdpr['percentage']:.1f}% | {gdpr['status']} |",
        f"| {nist800['name']} | {nist800['version']} | {nist800['mapped']} / {nist800['benchmark']} | {nist800['percentage']:.1f}% | {nist800['status']} |",
        f"| {e8['name']} | {e8['version']} | {e8['mapped']} / {e8['benchmark']} | {e8['percentage']:.1f}% | {e8['status']} |",
        "================================================================================",
    ]

    all_compliant = all(f["status"] == "COMPLIANT" for f in fws.values()) and ctrl_count >= 55
    return "\n".join(report_lines), all_compliant


def generate_sarif_report(
    all_errors: List[str], metrics: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format validation results as SARIF v2.1.0 payload."""
    rules = [
        {
            "id": "ISMS001",
            "name": "NavParity",
            "shortDescription": {"text": "MkDocs navigation and filesystem parity mismatch"},
        },
        {
            "id": "ISMS002",
            "name": "LinkIntegrity",
            "shortDescription": {"text": "Broken relative markdown link"},
        },
        {
            "id": "ISMS003",
            "name": "DeprecatedCitation",
            "shortDescription": {"text": "Deprecated ISO 27001:2013 or banned standard citation"},
        },
        {
            "id": "ISMS004",
            "name": "SoACompleteness",
            "shortDescription": {"text": "Statement of Applicability completeness or missing control"},
        },
        {
            "id": "ISMS005",
            "name": "HeaderFooterStandard",
            "shortDescription": {"text": "Standard Document Control Header or History Table invalid"},
        },
        {
            "id": "ISMS006",
            "name": "RegistryAndCatalogIntegrity",
            "shortDescription": {"text": "Framework registry schema or catalog integrity violation"},
        },
        {
            "id": "ISMS007",
            "name": "DriftViolation",
            "shortDescription": {"text": "Drift between framework registry and documentation/SoA"},
        },
    ]

    def classify_error(err_msg: str) -> Tuple[str, str, int]:
        line_num = 1
        uri = "mappings/framework_registry.yaml"

        line_match = re.match(r"^([^:]+):(\d+):\s*(.*)$", err_msg)
        if line_match:
            uri = line_match.group(1).strip()
            line_num = int(line_match.group(2))
            clean_msg = line_match.group(3).strip()
        else:
            clean_msg = err_msg

        if "navigation" in err_msg.lower() or "orphaned" in err_msg.lower() or "dead" in err_msg.lower():
            rule_id = "ISMS001"
            uri = "mkdocs.yml"
        elif "broken relative link" in err_msg.lower() or "cannot read" in err_msg.lower():
            rule_id = "ISMS002"
        elif "deprecated" in err_msg.lower() or "invalid citation" in err_msg.lower() or "banned" in err_msg.lower():
            rule_id = "ISMS003"
        elif "soa" in err_msg.lower() and "drift" not in err_msg.lower():
            rule_id = "ISMS004"
            uri = "docs/01_ISMS_Framework/05_Statement_of_Applicability_SoA.md"
        elif "header" in err_msg.lower() or "history" in err_msg.lower() or "policy missing" in err_msg.lower():
            rule_id = "ISMS005"
        elif "drift" in err_msg.lower():
            rule_id = "ISMS007"
        else:
            rule_id = "ISMS006"

        return rule_id, clean_msg, line_num, uri

    results = []
    for err in all_errors:
        rule_id, clean_msg, line_num, uri = classify_error(err)
        results.append(
            {
                "ruleId": rule_id,
                "level": "error",
                "message": {"text": clean_msg},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": uri},
                            "region": {"startLine": line_num},
                        }
                    }
                ],
            }
        )

    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "validate_isms",
                        "version": "2.0.0",
                        "informationUri": "https://github.com/security-standards-template",
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }


def generate_markdown_report(
    all_errors: List[str], metrics: Optional[Dict[str, Any]] = None
) -> str:
    """Format validation results as GitHub-Flavored Markdown report."""
    status = "PASS" if not all_errors else "FAIL"
    ctrl_count = metrics["canonical_controls_count"] if metrics else 0
    fws = metrics["frameworks"] if metrics else {}

    lines = [
        "# ISMS Framework Compliance & Integrity Validation Report",
        "",
        f"- **Status**: `{status}`",
        f"- **Total Canonical Controls**: {ctrl_count}",
        f"- **Total Violations**: {len(all_errors)}",
        "",
        "## Framework Coverage Overview",
        "",
        "| Framework / Standard | Version | Mapped / Benchmark | Coverage % | Status |",
        "| :--- | :--- | :---: | :---: | :---: |",
    ]

    for fw_key, fw in fws.items():
        lines.append(
            f"| {fw['name']} | {fw['version']} | {fw['mapped']} / {fw['benchmark']} | {fw['percentage']:.1f}% | {fw['status']} |"
        )

    lines.append("")
    if all_errors:
        lines.append("## Violations Detected")
        lines.append("")
        for err in all_errors:
            lines.append(f"- [FAIL] `{err}`")
    else:
        lines.append("## Violations")
        lines.append("")
        lines.append("[PASS] Zero validation violations detected across all ISMS integrity modules.")

    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

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
        help="Path to framework registry YAML (default: mappings/framework_registry.yaml)",
    )
    parser.add_argument(
        "--schema",
        default="schemas/framework_registry.schema.json",
        help="Path to framework registry schema (default: schemas/framework_registry.schema.json)",
    )
    parser.add_argument(
        "--catalogs-dir",
        default="mappings/catalogs",
        help="Path to reference catalogs directory (default: mappings/catalogs)",
    )
    parser.add_argument(
        "--soa",
        default="docs/01_ISMS_Framework/05_Statement_of_Applicability_SoA.md",
        help="Path to Statement of Applicability document",
    )
    parser.add_argument(
        "--check-drift",
        action="store_true",
        default=False,
        help="Verify bidirectional consistency between registry and markdown docs/SoA",
    )
    parser.add_argument(
        "--coverage-report",
        action="store_true",
        help="Generate and display framework coverage report",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "sarif", "markdown"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Treat warnings as fatal errors",
    )

    args = parser.parse_args()

    all_errors: List[str] = []
    output_format = args.format

    # Guard against empty CLI path arguments
    if args.schema is not None and not str(args.schema).strip():
        all_errors.append("Framework registry schema path cannot be empty")
        schema_file = None
    elif args.schema:
        schema_file = (REPO_ROOT / args.schema).resolve()
    else:
        schema_file = None

    docs_dir = (REPO_ROOT / args.docs_dir).resolve()
    mkdocs_file = (REPO_ROOT / args.config).resolve()
    registry_file = (REPO_ROOT / args.registry).resolve()
    catalogs_dir = (REPO_ROOT / args.catalogs_dir).resolve()
    soa_file = (REPO_ROOT / args.soa).resolve()

    def log(msg: str) -> None:
        if output_format == "text":
            print(msg)

    # Run validation modules
    log(f"[*] Validating MkDocs Navigation Parity against {docs_dir.name}/ ...")
    nav_errors = validate_nav_parity(docs_dir, mkdocs_file)
    all_errors.extend(nav_errors)

    log("[*] Validating Relative Markdown Links ...")
    link_errors = validate_relative_links(docs_dir)
    all_errors.extend(link_errors)

    log("[*] Scanning for Deprecated ISO 2013 & Invalid Standard Citations ...")
    citation_errors = validate_deprecated_citations(docs_dir)
    all_errors.extend(citation_errors)

    log("[*] Validating Statement of Applicability (93 controls) ...")
    soa_errors = validate_soa_completeness(soa_file)
    all_errors.extend(soa_errors)

    log("[*] Validating Document Control Header and History Tables ...")
    hf_errors = validate_document_headers_footers(docs_dir)
    all_errors.extend(hf_errors)

    log("[*] Validating Canonical Control Registry Schema & Files ...")
    reg_errors, registry_data = validate_registry_schema_and_files(registry_file, schema_file)
    all_errors.extend(reg_errors)

    log("[*] Validating Reference Catalog Integrity (6 frameworks) ...")
    if registry_data:
        cat_errors = validate_catalog_integrity(registry_data, catalogs_dir)
        all_errors.extend(cat_errors)

    if args.check_drift and registry_data:
        log("[*] Checking Framework & SoA Drift ...")
        drift_errors = validate_drift(registry_data, soa_file, docs_dir)
        all_errors.extend(drift_errors)
    else:
        drift_errors = []

    # Compute metrics if registry data is available
    metrics = compute_coverage_metrics(registry_data, catalogs_dir) if registry_data else None

    # Coverage report across all output formats
    if args.coverage_report and registry_data:
        report_text, report_ok = generate_coverage_report(registry_data, catalogs_dir)
        if output_format == "text":
            print("\n" + report_text + "\n")
        if not report_ok:
            all_errors.append(
                "Coverage report indicates incomplete coverage or insufficient canonical controls across 6 frameworks."
            )

    # Format specific output rendering
    if output_format == "json":
        json_payload = {
            "status": "PASS" if not all_errors else "FAIL",
            "exit_code": 0 if not all_errors else 1,
            "metrics": {
                "canonical_controls": metrics["canonical_controls_count"] if metrics else 0,
                "broken_links": len(link_errors),
                "orphaned_nav": len(nav_errors),
                "drift_violations": len(drift_errors),
            },
            "frameworks": metrics["frameworks"] if metrics else {},
            "violations": all_errors,
        }
        print(json.dumps(json_payload, indent=2, sort_keys=True, ensure_ascii=False))
    elif output_format == "sarif":
        sarif_payload = generate_sarif_report(all_errors, metrics)
        print(json.dumps(sarif_payload, indent=2, sort_keys=True, ensure_ascii=False))
    elif output_format == "markdown":
        md_report = generate_markdown_report(all_errors, metrics)
        print(md_report)
    else:
        # text mode result evaluation
        if all_errors:
            print(f"\n[FAIL] Found {len(all_errors)} validation violation(s):")
            for err in all_errors:
                print(f"  - {err}")
            return 1
        print("\n[PASS] All ISMS validation checks passed cleanly (0 errors).")

    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
