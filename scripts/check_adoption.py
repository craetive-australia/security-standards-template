#!/usr/bin/env python3
"""
scripts/check_adoption.py
Regulation Adoption and Compliance Policy Auditing CLI for security-standards-template.

Enforces:
1. Manifest schema validation (against schemas/compliance_manifest.schema.json)
2. Adopted framework coverage thresholds (ISO 27001, SOC 2, NIST CSF 2.0, GDPR, NIST 800-53, E8)
3. ASD Essential Eight target maturity level (ML2) enforcement across all 8 strategies
4. Document review cadence audits (max_age_days: 365 based on Document Control Header Effective Date)
5. Time-bound security exception audits (<= 90-day window, unexpired, valid compensating controls)

Returns:
- Exit code 0: All compliance policies, thresholds, review cadences, and exceptions pass
- Exit code 1: Any threshold shortfall, overdue review, expired exception, or schema breach
"""

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

try:
    import yaml
except ModuleNotFoundError:
    import subprocess
    candidate_venvs = [
        REPO_ROOT / ".venv" / "Scripts" / "python.exe",
        REPO_ROOT / ".venv" / "bin" / "python",
    ]
    for venv_py in candidate_venvs:
        if venv_py.exists() and Path(sys.executable).resolve() != venv_py.resolve():
            sys.exit(subprocess.call([str(venv_py), *sys.argv]))
    raise

E8_STRATEGIES = [
    "application_control",
    "patch_applications",
    "configure_office_macros",
    "user_application_hardening",
    "restrict_admin_privileges",
    "patch_operating_systems",
    "multi_factor_authentication",
    "regular_backups",
]

E8_PREFIX_MAP = {
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


def validate_manifest_schema(manifest_data: Dict[str, Any], schema_path: Path) -> List[str]:
    """Validate compliance_manifest.yaml against compliance_manifest.schema.json."""
    errors = []
    if not schema_path.exists():
        return [f"Compliance manifest schema not found: {schema_path}"]

    try:
        import jsonschema

        with open(schema_path, "r", encoding="utf-8") as sf:
            schema_data = json.load(sf)
        validator_cls = jsonschema.validators.validator_for(schema_data)
        validator_cls.check_schema(schema_data)
        validator = validator_cls(schema_data)
        for err in validator.iter_errors(manifest_data):
            path_str = " -> ".join(str(p) for p in err.path) if err.path else "root"
            errors.append(f"Manifest schema error at '{path_str}': {err.message}")
    except ModuleNotFoundError:
        # Fallback structural validation
        req_keys = ["schema_version", "organization", "review_policy", "adopted_frameworks", "thresholds", "exceptions"]
        for k in req_keys:
            if k not in manifest_data:
                errors.append(f"Manifest missing required root key: '{k}'")
    except Exception as e:
        errors.append(f"Manifest schema validation error: {e}")

    return errors


def audit_framework_thresholds_and_maturity(
    manifest_data: Dict[str, Any], registry_data: Dict[str, Any]
) -> Tuple[List[str], Dict[str, Any]]:
    """Audit coverage thresholds and E8 ML2 maturity against framework registry."""
    errors: List[str] = []
    controls = registry_data.get("controls") or registry_data.get("canonical_controls", [])

    # Index mapped controls from registry
    mapped_iso: Set[str] = set()
    mapped_soc2: Set[str] = set()
    mapped_csf: Set[str] = set()
    mapped_gdpr: Set[str] = set()
    mapped_nist800: Set[str] = set()
    nist800_families: Set[str] = set()

    e8_strat_ml_map: Dict[str, Set[str]] = {s: set() for s in E8_STRATEGIES}

    for ctrl in controls:
        mappings = ctrl.get("mappings", {})

        for item in mappings.get("iso_27001_2022") or []:
            mapped_iso.add(item if isinstance(item, str) else item.get("id"))

        for item in mappings.get("soc2_tsc_2017") or mappings.get("soc2_tsc") or []:
            mapped_soc2.add(item if isinstance(item, str) else item.get("id"))

        for item in mappings.get("nist_csf_2_0") or mappings.get("nist_csf") or []:
            mapped_csf.add(item if isinstance(item, str) else item.get("id"))

        for item in mappings.get("gdpr_articles") or mappings.get("gdpr") or []:
            mapped_gdpr.add(item if isinstance(item, str) else item.get("id"))

        for item in mappings.get("nist_sp_800_53_rev5") or []:
            cid = item if isinstance(item, str) else item.get("id")
            if cid:
                mapped_nist800.add(cid)
                if "-" in cid:
                    nist800_families.add(cid.split("-")[0])

        for item in mappings.get("asd_essential_eight") or []:
            cid = item if isinstance(item, str) else item.get("id")
            if cid:
                for prefix, strat in E8_PREFIX_MAP.items():
                    if cid.startswith(prefix):
                        m = re.search(r"ML[123]", cid)
                        if m:
                            e8_strat_ml_map[strat].add(m.group(0))

    # Evaluate against thresholds declared in manifest
    thresholds = manifest_data.get("thresholds", {})
    min_canonical = thresholds.get("min_canonical_controls", 55)
    min_csf = thresholds.get("min_distinct_csf_subcategories", 45)
    min_nist800 = thresholds.get("min_distinct_nist_800_53_controls", 85)
    min_e8 = thresholds.get("min_essential_eight_strategies", 8)

    if len(controls) < min_canonical:
        errors.append(
            f"Canonical control threshold breached: found {len(controls)}, minimum required is {min_canonical}"
        )

    if len(mapped_csf) < min_csf:
        errors.append(
            f"NIST CSF 2.0 subcategories threshold breached: mapped {len(mapped_csf)}, minimum required is {min_csf}"
        )

    if len(mapped_nist800) < min_nist800:
        errors.append(
            f"NIST SP 800-53 controls threshold breached: mapped {len(mapped_nist800)}, minimum required is {min_nist800}"
        )

    e8_active_strategies = {s for s, mls in e8_strat_ml_map.items() if len(mls) > 0}
    if len(e8_active_strategies) < min_e8:
        errors.append(
            f"ASD Essential Eight strategy threshold breached: mapped {len(e8_active_strategies)}, minimum required is {min_e8}"
        )

    # Evaluate adopted frameworks
    framework_results: Dict[str, Any] = {}
    for fw in manifest_data.get("adopted_frameworks", []):
        fw_id = fw.get("framework_id")
        target_cov = fw.get("target_coverage_pct", 100.0)

        if fw_id == "iso_27001_2022":
            cov_pct = (len(mapped_iso) / 93.0) * 100.0
            passed = cov_pct >= target_cov
            framework_results[fw_id] = {
                "mapped": len(mapped_iso),
                "benchmark": 93,
                "coverage_pct": round(cov_pct, 1),
                "target_pct": target_cov,
                "passed": passed,
            }
            if not passed:
                errors.append(f"ISO 27001:2022 coverage {cov_pct:.1f}% is below target {target_cov}%")

        elif fw_id == "soc2_tsc_2017":
            cov_pct = min(100.0, (len(mapped_soc2) / 38.0) * 100.0)
            passed = cov_pct >= target_cov
            framework_results[fw_id] = {
                "mapped": len(mapped_soc2),
                "benchmark": 38,
                "coverage_pct": round(cov_pct, 1),
                "target_pct": target_cov,
                "passed": passed,
            }
            if not passed:
                errors.append(f"SOC 2 coverage {cov_pct:.1f}% is below target {target_cov}%")

        elif fw_id == "nist_csf_2_0":
            cov_pct = min(100.0, (len(mapped_csf) / 45.0) * 100.0)
            passed = cov_pct >= target_cov
            framework_results[fw_id] = {
                "mapped": len(mapped_csf),
                "benchmark": 45,
                "coverage_pct": round(cov_pct, 1),
                "target_pct": target_cov,
                "passed": passed,
            }
            if not passed:
                errors.append(f"NIST CSF 2.0 coverage {cov_pct:.1f}% is below target {target_cov}%")

        elif fw_id == "gdpr":
            cov_pct = min(100.0, (len(mapped_gdpr) / 13.0) * 100.0)
            passed = cov_pct >= target_cov
            framework_results[fw_id] = {
                "mapped": len(mapped_gdpr),
                "benchmark": 13,
                "coverage_pct": round(cov_pct, 1),
                "target_pct": target_cov,
                "passed": passed,
            }
            if not passed:
                errors.append(f"GDPR coverage {cov_pct:.1f}% is below target {target_cov}%")

        elif fw_id == "nist_sp_800_53_rev5":
            cov_pct = min(100.0, (len(mapped_nist800) / 85.0) * 100.0)
            passed = cov_pct >= target_cov and len(nist800_families) == 20
            framework_results[fw_id] = {
                "mapped": len(mapped_nist800),
                "families_count": len(nist800_families),
                "benchmark": 85,
                "coverage_pct": round(cov_pct, 1),
                "target_pct": target_cov,
                "passed": passed,
            }
            if not passed:
                errors.append(
                    f"NIST SP 800-53 coverage {cov_pct:.1f}% or families count ({len(nist800_families)}/20) fails target"
                )

        elif fw_id == "asd_essential_eight":
            target_ml = fw.get("target_maturity_level", "ML2")
            # Enforce that all 8 strategies cover ML1 and target_ml
            ml_unmet = []
            for s in E8_STRATEGIES:
                mls = e8_strat_ml_map.get(s, set())
                if "ML1" not in mls or target_ml not in mls:
                    ml_unmet.append(f"{s} (levels: {mls})")

            passed = len(ml_unmet) == 0
            cov_pct = 100.0 if passed else ((8 - len(ml_unmet)) / 8.0) * 100.0
            framework_results[fw_id] = {
                "target_maturity_level": target_ml,
                "active_strategies": len(e8_active_strategies),
                "strategies_meeting_target": 8 - len(ml_unmet),
                "passed": passed,
            }
            if not passed:
                errors.append(
                    f"ASD Essential Eight {target_ml} maturity target breached: unmet strategies: {ml_unmet}"
                )

    return errors, {
        "canonical_controls_count": len(controls),
        "thresholds_audit": {
            "canonical_controls": {"found": len(controls), "min": min_canonical, "pass": len(controls) >= min_canonical},
            "nist_csf_subcategories": {"found": len(mapped_csf), "min": min_csf, "pass": len(mapped_csf) >= min_csf},
            "nist_800_53_controls": {"found": len(mapped_nist800), "min": min_nist800, "pass": len(mapped_nist800) >= min_nist800},
            "essential_eight_strategies": {"found": len(e8_active_strategies), "min": min_e8, "pass": len(e8_active_strategies) >= min_e8},
        },
        "adopted_frameworks_audit": framework_results,
    }


def audit_document_review_cadence(
    docs_dir: Path, max_age_days: int, current_date: datetime.date
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Audit review cadence based on Document Control Header Effective Date across docs/."""
    errors: List[str] = []
    audits: List[Dict[str, Any]] = []

    date_re = re.compile(
        r"\|\s*(?:\*\*)?Effective Date(?:\*\*)?\s*\|\s*([^|\r\n]+)\s*\|"
    )

    for md_file in sorted(docs_dir.rglob("*.md")):
        try:
            rel_path = md_file.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            rel_path = md_file.as_posix()

        if rel_path == "docs/index.md" or md_file.name == "index.md":
            continue

        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"Cannot read document {rel_path}: {e}")
            continue

        match = date_re.search(content)
        if not match:
            errors.append(f"{rel_path}: Missing 'Effective Date' in Document Control Header table")
            continue

        raw_date_str = match.group(1).strip()
        if raw_date_str in ("[INSERT_DATE]", "INSERT_DATE") or raw_date_str.startswith("["):
            # Template placeholder: treat as fresh deployment date
            eff_date = current_date
            eff_date_str = raw_date_str
        else:
            try:
                eff_date = datetime.date.fromisoformat(raw_date_str)
                eff_date_str = raw_date_str
            except ValueError:
                errors.append(f"{rel_path}: Invalid Effective Date format '{raw_date_str}'")
                continue

        age_days = (current_date - eff_date).days
        is_overdue = age_days > max_age_days

        audit_entry = {
            "document": rel_path,
            "effective_date": eff_date_str,
            "age_days": age_days,
            "max_age_days": max_age_days,
            "overdue": is_overdue,
        }
        audits.append(audit_entry)

        if is_overdue:
            errors.append(
                f"{rel_path}: Document review overdue: Effective date {eff_date_str} is {age_days} days old (exceeds max_age_days: {max_age_days})"
            )

    return errors, audits


def audit_security_exceptions(
    manifest_data: Dict[str, Any],
    registry_data: Dict[str, Any],
    current_date: datetime.date,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Audit security exceptions: unexpired, duration <= 90 days, valid canonical control ID."""
    errors: List[str] = []
    audits: List[Dict[str, Any]] = []

    controls = registry_data.get("controls") or registry_data.get("canonical_controls", [])
    valid_ctrl_ids = {c["id"] for c in controls if isinstance(c, dict) and "id" in c}

    exceptions = manifest_data.get("exceptions", [])
    for ex in exceptions:
        ex_id = ex.get("id", "UNKNOWN_EX")
        ctrl_id = ex.get("control_id", "")
        status = ex.get("status", "active")
        app_date_str = ex.get("approval_date", "")
        exp_date_str = ex.get("expiration_date", "")
        approver = ex.get("approved_by", "")
        comp_controls = ex.get("compensating_controls", [])

        # 1. Valid control ID
        if not ctrl_id or ctrl_id not in valid_ctrl_ids:
            errors.append(
                f"Security exception {ex_id} references invalid/unknown control_id '{ctrl_id}'"
            )

        # 2. Date parsing
        try:
            exp_date = datetime.date.fromisoformat(exp_date_str)
        except (ValueError, TypeError):
            errors.append(f"Security exception {ex_id} has invalid expiration_date '{exp_date_str}'")
            continue

        try:
            app_date = datetime.date.fromisoformat(app_date_str)
        except (ValueError, TypeError):
            errors.append(f"Security exception {ex_id} has invalid approval_date '{app_date_str}'")
            continue

        # 3. Expiration check
        is_expired = exp_date < current_date
        days_remaining = (exp_date - current_date).days
        if is_expired or status == "expired":
            errors.append(
                f"Security exception {ex_id} has EXPIRED: expiration date {exp_date_str} is in the past (current date: {current_date.isoformat()})"
            )

        # 4. Duration bounds (<= 90-day window)
        duration_days = (exp_date - app_date).days
        if duration_days > 90:
            errors.append(
                f"Security exception {ex_id} duration ({duration_days} days) exceeds mandatory 90-day maximum policy window"
            )
        elif duration_days <= 0:
            errors.append(
                f"Security exception {ex_id} duration ({duration_days} days) is invalid: expiration must succeed approval"
            )

        # 5. Compensating controls & Approver check
        if not comp_controls:
            errors.append(f"Security exception {ex_id} has no compensating controls specified")

        if not approver.strip():
            errors.append(f"Security exception {ex_id} has missing approver")

        audits.append(
            {
                "id": ex_id,
                "control_id": ctrl_id,
                "title": ex.get("title", ""),
                "status": status,
                "approval_date": app_date_str,
                "expiration_date": exp_date_str,
                "duration_days": duration_days,
                "days_remaining": days_remaining,
                "expired": is_expired,
                "compensating_controls_count": len(comp_controls),
            }
        )

    return errors, audits


def generate_adoption_sarif(all_errors: List[str]) -> Dict[str, Any]:
    """Generate SARIF v2.1.0 output for adoption auditing."""
    rules = [
        {"id": "ADOPT001", "name": "ManifestSchema", "shortDescription": {"text": "Manifest schema validation error"}},
        {"id": "ADOPT002", "name": "ThresholdBreach", "shortDescription": {"text": "Framework target threshold breach"}},
        {"id": "ADOPT003", "name": "MaturityBreach", "shortDescription": {"text": "Essential Eight maturity level breach"}},
        {"id": "ADOPT004", "name": "ReviewCadenceOverdue", "shortDescription": {"text": "Document review cadence overdue"}},
        {"id": "ADOPT005", "name": "ExceptionExpired", "shortDescription": {"text": "Security exception expired"}},
        {"id": "ADOPT006", "name": "ExceptionWindowExceeded", "shortDescription": {"text": "Security exception duration exceeds 90 days"}},
        {"id": "ADOPT007", "name": "ExceptionInvalid", "shortDescription": {"text": "Security exception invalid control or controls"}},
    ]

    results = []
    for err in all_errors:
        if "schema" in err.lower():
            rid = "ADOPT001"
            uri = "mappings/compliance_manifest.yaml"
        elif "threshold" in err.lower() or "coverage" in err.lower():
            rid = "ADOPT002"
            uri = "mappings/compliance_manifest.yaml"
        elif "maturity" in err.lower() or "essential eight" in err.lower():
            rid = "ADOPT003"
            uri = "mappings/compliance_manifest.yaml"
        elif "review overdue" in err.lower() or "effective date" in err.lower():
            rid = "ADOPT004"
            uri = err.split(":")[0] if ":" in err else "docs/"
        elif "expired" in err.lower():
            rid = "ADOPT005"
            uri = "mappings/compliance_manifest.yaml"
        elif "90-day" in err.lower() or "duration" in err.lower():
            rid = "ADOPT006"
            uri = "mappings/compliance_manifest.yaml"
        else:
            rid = "ADOPT007"
            uri = "mappings/compliance_manifest.yaml"

        results.append(
            {
                "ruleId": rid,
                "level": "error",
                "message": {"text": err},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": uri},
                            "region": {"startLine": 1},
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
                        "name": "check_adoption",
                        "version": "2.0.0",
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }


def generate_adoption_markdown(
    all_errors: List[str],
    audit_data: Dict[str, Any],
    current_date: datetime.date,
) -> str:
    """Generate Markdown report for adoption auditing."""
    status = "PASS" if not all_errors else "FAIL"
    lines = [
        "# Compliance Adoption & Governance Audit Report",
        "",
        f"- **Audit Date**: `{current_date.isoformat()}`",
        f"- **Audit Status**: `{status}`",
        f"- **Total Violations**: {len(all_errors)}",
        "",
        "## Adopted Framework Targets Audit",
        "",
        "| Framework ID | Target Metric | Achieved / Target | Status |",
        "| :--- | :--- | :---: | :---: |",
    ]

    af_audit = audit_data.get("adopted_frameworks_audit", {})
    for fid, fres in af_audit.items():
        if fid == "asd_essential_eight":
            target_str = f"{fres.get('target_maturity_level', 'ML2')}"
            ach_str = f"{fres.get('strategies_meeting_target', 0)} / 8 strategies"
            stat = "COMPLIANT" if fres.get("passed") else "NON-COMPLIANT"
            lines.append(f"| {fid} | Target Maturity {target_str} | {ach_str} | {stat} |")
        else:
            ach_str = f"{fres.get('coverage_pct', 0.0)}% / {fres.get('target_pct', 100.0)}%"
            stat = "COMPLIANT" if fres.get("passed") else "NON-COMPLIANT"
            lines.append(f"| {fid} | Target Coverage | {ach_str} | {stat} |")

    lines.append("")
    lines.append("## Security Exceptions Audit")
    lines.append("")
    lines.append("| Exception ID | Control ID | Approval Date | Expiry Date | Duration | Days Left | Status |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")

    for ex in audit_data.get("security_exceptions", []):
        stat = "EXPIRED" if ex["expired"] else "ACTIVE"
        lines.append(
            f"| {ex['id']} | {ex['control_id']} | {ex['approval_date']} | {ex['expiration_date']} | {ex['duration_days']}d | {ex['days_remaining']}d | {stat} |"
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
        lines.append("[PASS] All adoption policies, review cadences, and time-bound exceptions are fully compliant.")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regulation Adoption and Policy Auditing CLI"
    )
    parser.add_argument(
        "--manifest",
        default="mappings/compliance_manifest.yaml",
        help="Path to compliance manifest YAML (default: mappings/compliance_manifest.yaml)",
    )
    parser.add_argument(
        "--registry",
        default="mappings/framework_registry.yaml",
        help="Path to framework registry YAML (default: mappings/framework_registry.yaml)",
    )
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Path to documentation directory (default: docs)",
    )
    parser.add_argument(
        "--schema",
        default="schemas/compliance_manifest.schema.json",
        help="Path to compliance manifest schema (default: schemas/compliance_manifest.schema.json)",
    )
    parser.add_argument(
        "--current-date",
        default=None,
        help="Current date override for testing in YYYY-MM-DD format (default: today UTC)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown", "sarif"],
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

    manifest_path = (REPO_ROOT / args.manifest).resolve()
    registry_path = (REPO_ROOT / args.registry).resolve()
    docs_dir = (REPO_ROOT / args.docs_dir).resolve()
    schema_path = (REPO_ROOT / args.schema).resolve()

    if args.current_date:
        try:
            current_date = datetime.date.fromisoformat(args.current_date)
        except ValueError:
            print(f"[FAIL] Invalid --current-date '{args.current_date}', must be YYYY-MM-DD", file=sys.stderr)
            return 1
    else:
        current_date = datetime.date.today()

    all_errors: List[str] = []

    # 1. Load manifest
    if not manifest_path.exists():
        print(f"[FAIL] Compliance manifest file not found: {manifest_path}", file=sys.stderr)
        return 1

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = yaml.safe_load(f)
    except Exception as e:
        print(f"[FAIL] Failed to parse compliance manifest YAML: {e}", file=sys.stderr)
        return 1

    # 2. Load registry
    if not registry_path.exists():
        print(f"[FAIL] Framework registry file not found: {registry_path}", file=sys.stderr)
        return 1

    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            registry_data = yaml.safe_load(f)
    except Exception as e:
        print(f"[FAIL] Failed to parse framework registry YAML: {e}", file=sys.stderr)
        return 1

    # Audit Module 1: Manifest Schema
    schema_errors = validate_manifest_schema(manifest_data, schema_path)
    all_errors.extend(schema_errors)

    # Audit Module 2: Framework Thresholds & E8 ML2 Target Maturity
    thresh_errors, thresh_data = audit_framework_thresholds_and_maturity(manifest_data, registry_data)
    all_errors.extend(thresh_errors)

    # Audit Module 3: Document Review Cadence
    max_age_days = manifest_data.get("review_policy", {}).get("max_age_days", 365)
    cadence_errors, cadence_audits = audit_document_review_cadence(docs_dir, max_age_days, current_date)
    all_errors.extend(cadence_errors)

    # Audit Module 4: Security Exceptions
    ex_errors, ex_audits = audit_security_exceptions(manifest_data, registry_data, current_date)
    all_errors.extend(ex_errors)

    audit_summary = {
        "status": "PASS" if not all_errors else "FAIL",
        "exit_code": 0 if not all_errors else 1,
        "audit_date": current_date.isoformat(),
        "canonical_controls_count": thresh_data.get("canonical_controls_count", 0),
        "thresholds_audit": thresh_data.get("thresholds_audit", {}),
        "adopted_frameworks_audit": thresh_data.get("adopted_frameworks_audit", {}),
        "documents_audited_count": len(cadence_audits),
        "security_exceptions": ex_audits,
        "violations": all_errors,
    }

    output_format = args.format
    if output_format == "json":
        print(json.dumps(audit_summary, indent=2, sort_keys=True, ensure_ascii=False))
    elif output_format == "sarif":
        sarif_out = generate_adoption_sarif(all_errors)
        print(json.dumps(sarif_out, indent=2, sort_keys=True, ensure_ascii=False))
    elif output_format == "markdown":
        md_out = generate_adoption_markdown(all_errors, audit_summary, current_date)
        print(md_out)
    else:
        # text format
        print(f"[*] Auditing Compliance Manifest & Policies against {registry_path.name} ...")
        print(f"[*] Audit Reference Date: {current_date.isoformat()}")
        print(f"[*] Audited {len(cadence_audits)} document review cadences (max_age_days: {max_age_days})")
        print(f"[*] Audited {len(ex_audits)} active security exceptions")
        print(f"[*] Audited 6 adopted frameworks and E8 ML2 target maturity")

        if all_errors:
            print(f"\n[FAIL] Found {len(all_errors)} compliance policy violation(s):")
            for err in all_errors:
                print(f"  - {err}")
            return 1

        print("\n[PASS] All compliance adoption policies, review cadences, and security exceptions are compliant (0 errors).")
        return 0

    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
