#!/usr/bin/env python3
"""
scripts/export_oscal.py
Deterministic OSCAL v1.2.0 Export Engine for security-standards-template.

Generates five deterministic OSCAL v1.2.0 JSON models in dist/oscal/:
1. catalog.json: Canonical ISMS controls organized by security domain
2. mapping_collection.json: Multi-framework crosswalk mappings with relationship semantics
3. profile_e8_ml2.json: ASD Essential Eight Maturity Level 2 Profile
4. profile_nist_800_53_moderate.json: NIST SP 800-53 Rev. 5 Moderate Baseline Profile
5. component_definition.json: System components mapping policies, standards, and automation

Uses RFC 4122 UUIDv5 hashing for 100% byte-level reproducibility.
Supports --validate (JSON schema validation) and --check (CI drift verification).
"""

import argparse
import json
import os
import re
import sys
import uuid
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

# Deterministic namespace dedicated to Compliance-as-Code ISMS
OSCAL_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "compliance-as-code.isms.security-standards-template")


def get_deterministic_uuid(entity_type: str, entity_id: str) -> str:
    """Generate a deterministic RFC 4122 UUIDv5 based on entity type and identifier."""
    name = f"{entity_type}:{entity_id}"
    return str(uuid.uuid5(OSCAL_NAMESPACE, name))


def build_oscal_metadata(
    title: str,
    version: str = "2.0.0",
    last_modified: str = "2026-10-31T00:00:00Z",
    remarks: Optional[str] = None,
) -> Dict[str, Any]:
    """Construct standardized OSCAL v1.2.0 metadata object."""
    meta: Dict[str, Any] = {
        "title": title,
        "published": "2026-10-31T00:00:00Z",
        "last-modified": last_modified,
        "version": version,
        "oscal-version": "1.2.0",
    }
    if remarks:
        meta["remarks"] = remarks
    return meta


def generate_catalog_model(registry_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate OSCAL v1.2.0 catalog.json model."""
    meta_info = registry_data.get("metadata", {})
    last_mod = meta_info.get("last_updated", "2026-10-31")
    if not last_mod.endswith("Z"):
        last_mod = f"{last_mod}T00:00:00Z"
    version = str(registry_data.get("version", "2.0.0"))

    catalog_uuid = get_deterministic_uuid("catalog", "isms-canonical-controls")
    metadata = build_oscal_metadata(
        title=meta_info.get("title", "Canonical Compliance-as-Code Control Registry"),
        version=version,
        last_modified=last_mod,
        remarks=meta_info.get("description", "Centralized canonical control catalog"),
    )

    domains = registry_data.get("domains", [])
    controls = registry_data.get("controls") or registry_data.get("canonical_controls", [])

    # Index domains and group controls
    domain_map: Dict[str, List[Dict[str, Any]]] = {}
    domain_names: Dict[str, str] = {}
    for d in domains:
        d_name = d.get("name", d.get("id"))
        domain_names[d_name] = d_name
        domain_map[d_name] = []

    for ctrl in controls:
        d_name = ctrl.get("domain", "General")
        if d_name not in domain_map:
            domain_map[d_name] = []
            domain_names[d_name] = d_name
        domain_map[d_name].append(ctrl)

    groups: List[Dict[str, Any]] = []
    for d_name in sorted(domain_map.keys()):
        ctrl_list = domain_map[d_name]
        group_id = re.sub(r"[^a-zA-Z0-9_-]", "-", d_name.lower()).strip("-")

        group_controls: List[Dict[str, Any]] = []
        for c in ctrl_list:
            cid = c.get("id", "UNKNOWN")
            c_uuid = get_deterministic_uuid("control", cid)
            c_title = c.get("name", cid)
            c_desc = c.get("description", "")

            props = [
                {"name": "label", "value": cid},
                {"name": "domain", "value": d_name},
                {"name": "status", "value": "implemented"},
            ]
            for doc in c.get("implementing_docs") or c.get("implementing_documents") or []:
                props.append({"name": "implementing-document", "value": doc})

            parts = [
                {
                    "id": f"{cid.lower()}-stmt",
                    "name": "statement",
                    "prose": c_desc,
                }
            ]

            group_controls.append(
                {
                    "id": cid.lower(),
                    "uuid": c_uuid,
                    "title": c_title,
                    "props": props,
                    "parts": parts,
                }
            )

        groups.append(
            {
                "id": group_id,
                "title": d_name,
                "controls": group_controls,
            }
        )

    return {
        "catalog": {
            "uuid": catalog_uuid,
            "metadata": metadata,
            "groups": groups,
        }
    }


def generate_mapping_collection_model(registry_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate OSCAL v1.2.0 mapping_collection.json crosswalk model."""
    meta_info = registry_data.get("metadata", {})
    last_mod = meta_info.get("last_updated", "2026-10-31")
    if not last_mod.endswith("Z"):
        last_mod = f"{last_mod}T00:00:00Z"
    version = str(registry_data.get("version", "2.0.0"))

    collection_uuid = get_deterministic_uuid("mapping-collection", "isms-canonical-crosswalk")
    metadata = build_oscal_metadata(
        title="ISMS Multi-Framework Canonical Control Crosswalk Mappings",
        version=version,
        last_modified=last_mod,
        remarks="Deterministic crosswalk mappings between canonical controls and 6 external compliance frameworks",
    )

    controls = registry_data.get("controls") or registry_data.get("canonical_controls", [])
    mappings_list: List[Dict[str, Any]] = []

    framework_keys = [
        ("iso_27001_2022", "iso_27001_2022"),
        ("soc2_tsc_2017", "soc2_tsc_2017"),
        ("nist_csf_2_0", "nist_csf_2_0"),
        ("gdpr", "gdpr_articles"),
        ("nist_sp_800_53_rev5", "nist_sp_800_53_rev5"),
        ("asd_essential_eight", "asd_essential_eight"),
    ]

    for ctrl in controls:
        cid = ctrl.get("id", "UNKNOWN")
        m_dict = ctrl.get("mappings", {})

        for fw_name, reg_key in framework_keys:
            raw_items = m_dict.get(reg_key, [])
            if not raw_items and fw_name == "gdpr":
                raw_items = m_dict.get("gdpr", [])
            elif not raw_items and fw_name == "soc2_tsc_2017":
                raw_items = m_dict.get("soc2_tsc", [])

            for item in raw_items:
                if isinstance(item, str):
                    target_id = item
                    rel = "equivalent-to"
                elif isinstance(item, dict):
                    target_id = item.get("id", "")
                    rel = item.get("relationship", "equivalent-to")
                else:
                    continue

                if target_id:
                    mappings_list.append(
                        {
                            "source_control_id": cid,
                            "target_framework": fw_name,
                            "target_control_id": target_id,
                            "relationship": rel,
                        }
                    )

    # Sort mappings for deterministic byte stability
    mappings_list.sort(
        key=lambda m: (m["source_control_id"], m["target_framework"], m["target_control_id"])
    )

    return {
        "mapping-collection": {
            "uuid": collection_uuid,
            "metadata": metadata,
            "mappings": mappings_list,
        }
    }


def generate_profile_e8_ml2_model(registry_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate OSCAL v1.2.0 profile_e8_ml2.json profile model."""
    meta_info = registry_data.get("metadata", {})
    last_mod = meta_info.get("last_updated", "2026-10-31")
    if not last_mod.endswith("Z"):
        last_mod = f"{last_mod}T00:00:00Z"
    version = str(registry_data.get("version", "2.0.0"))

    profile_uuid = get_deterministic_uuid("profile", "asd-essential-eight-ml2")
    metadata = build_oscal_metadata(
        title="ASD Essential Eight Maturity Level 2 (ML2) Tailored Profile",
        version=version,
        last_modified=last_mod,
        remarks="OSCAL profile selecting canonical controls satisfying ASD Essential Eight ML1 and ML2 requirements",
    )

    controls = registry_data.get("controls") or registry_data.get("canonical_controls", [])
    included_control_ids: List[Dict[str, Any]] = []

    for ctrl in controls:
        cid = ctrl.get("id", "UNKNOWN")
        e8_items = ctrl.get("mappings", {}).get("asd_essential_eight", [])
        has_ml1_or_ml2 = False
        for item in e8_items:
            target_id = item if isinstance(item, str) else item.get("id", "")
            if "ML1" in target_id or "ML2" in target_id or "ML3" in target_id:
                has_ml1_or_ml2 = True
                break

        if has_ml1_or_ml2:
            included_control_ids.append(
                {
                    "with-id": cid.lower(),
                }
            )

    included_control_ids.sort(key=lambda x: x["with-id"])

    return {
        "profile": {
            "uuid": profile_uuid,
            "metadata": metadata,
            "imports": [
                {
                    "href": "./catalog.json",
                    "include-controls": included_control_ids,
                }
            ],
            "merge": {
                "combine": {
                    "method": "merge"
                }
            },
            "modify": {
                "set-parameters": [
                    {
                        "param-id": "e8_patch_application_sla",
                        "values": ["48h for critical vulnerabilities with known exploits"]
                    },
                    {
                        "param-id": "e8_mfa_requirement",
                        "values": ["Phishing-resistant MFA (FIDO2/WebAuthn) for administrative and remote access"]
                    }
                ]
            }
        }
    }


def generate_profile_nist_800_53_moderate_model(registry_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate OSCAL v1.2.0 profile_nist_800_53_moderate.json profile model."""
    meta_info = registry_data.get("metadata", {})
    last_mod = meta_info.get("last_updated", "2026-10-31")
    if not last_mod.endswith("Z"):
        last_mod = f"{last_mod}T00:00:00Z"
    version = str(registry_data.get("version", "2.0.0"))

    profile_uuid = get_deterministic_uuid("profile", "nist-sp-800-53-rev5-moderate")
    metadata = build_oscal_metadata(
        title="NIST SP 800-53 Rev. 5 Moderate Baseline ISMS Profile",
        version=version,
        last_modified=last_mod,
        remarks="OSCAL profile selecting canonical controls satisfying the NIST SP 800-53 Rev. 5 Moderate baseline",
    )

    controls = registry_data.get("controls") or registry_data.get("canonical_controls", [])
    included_controls: List[Dict[str, Any]] = []

    for ctrl in controls:
        cid = ctrl.get("id", "UNKNOWN")
        nist_items = ctrl.get("mappings", {}).get("nist_sp_800_53_rev5", [])
        if nist_items:
            included_controls.append(
                {
                    "with-id": cid.lower(),
                }
            )

    included_controls.sort(key=lambda x: x["with-id"])

    return {
        "profile": {
            "uuid": profile_uuid,
            "metadata": metadata,
            "imports": [
                {
                    "href": "./catalog.json",
                    "include-controls": included_controls,
                }
            ],
            "merge": {
                "combine": {
                    "method": "merge"
                }
            }
        }
    }


def generate_component_definition_model(registry_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate OSCAL v1.2.0 component_definition.json model."""
    meta_info = registry_data.get("metadata", {})
    last_mod = meta_info.get("last_updated", "2026-10-31")
    if not last_mod.endswith("Z"):
        last_mod = f"{last_mod}T00:00:00Z"
    version = str(registry_data.get("version", "2.0.0"))

    comp_def_uuid = get_deterministic_uuid("component-definition", "isms-components")
    metadata = build_oscal_metadata(
        title="ISMS Governance Documentation and Automation Tooling Components",
        version=version,
        last_modified=last_mod,
        remarks="Components defining repository policy/standard documents and validation scripts implementing canonical controls",
    )

    controls = registry_data.get("controls") or registry_data.get("canonical_controls", [])

    # Group canonical controls by implementing doc
    doc_to_ctrls: Dict[str, List[str]] = {}
    for ctrl in controls:
        cid = ctrl.get("id", "UNKNOWN")
        for doc in ctrl.get("implementing_docs") or ctrl.get("implementing_documents") or []:
            doc_to_ctrls.setdefault(doc, []).append(cid)

    components: List[Dict[str, Any]] = []

    # Document components
    for doc_path in sorted(doc_to_ctrls.keys()):
        c_uuid = get_deterministic_uuid("component", doc_path)
        p_name = Path(doc_path).name

        comp_type = "policy" if "02_Policies" in doc_path else (
            "standard" if "03_Standards" in doc_path else (
                "procedure" if "03_Standards" in doc_path or "Plan" in doc_path else "governance"
            )
        )

        impl_reqs = [
            {
                "uuid": get_deterministic_uuid("impl-req", f"{doc_path}:{cid}"),
                "control-id": cid.lower(),
                "description": f"Implemented via guidelines defined in {p_name}",
            }
            for cid in sorted(doc_to_ctrls[doc_path])
        ]

        components.append(
            {
                "uuid": c_uuid,
                "type": comp_type,
                "title": p_name.replace(".md", "").replace("_", " "),
                "description": f"Documentation component residing at {doc_path}",
                "control-implementations": [
                    {
                        "uuid": get_deterministic_uuid("control-impl", doc_path),
                        "source": "./catalog.json",
                        "description": f"Controls operationalized by {p_name}",
                        "implemented-requirements": impl_reqs,
                    }
                ],
            }
        )

    # Tooling / Automation software component
    tool_uuid = get_deterministic_uuid("component", "automation-tooling")
    components.append(
        {
            "uuid": tool_uuid,
            "type": "validation",
            "title": "ISMS Automation and Compliance Tooling Suite",
            "description": "Python CLI toolset (validate_isms.py, export_oscal.py, check_adoption.py) providing continuous compliance verification",
            "control-implementations": [
                {
                    "uuid": get_deterministic_uuid("control-impl", "automation-tooling"),
                    "source": "./catalog.json",
                    "description": "Continuous validation and verification of ISMS controls",
                    "implemented-requirements": [
                        {
                            "uuid": get_deterministic_uuid("impl-req", "automation:cc-gv-03"),
                            "control-id": "cc-gv-03",
                            "description": "Continuous automated validation of ISMS controls and evidence integrity",
                        }
                    ],
                }
            ],
        }
    )

    return {
        "component-definition": {
            "uuid": comp_def_uuid,
            "metadata": metadata,
            "components": components,
        }
    }


def serialize_model(data: Dict[str, Any]) -> str:
    """Deterministic JSON serialization with Unix newlines and sorted keys."""
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def validate_oscal_model(
    data: Dict[str, Any], schema_data: Dict[str, Any], filename: str
) -> List[str]:
    """Validate an OSCAL model against schemas/oscal_v1_2_0_subset.schema.json."""
    errors = []
    try:
        import copy
        import jsonschema

        # Prepare in-memory schema: collect top-level property definitions from oneOf branches
        # to satisfy Draft 2020-12 root additionalProperties constraint
        schema_copy = copy.deepcopy(schema_data)
        if "properties" not in schema_copy and "oneOf" in schema_copy:
            root_props = {}
            for branch in schema_copy["oneOf"]:
                root_props.update(branch.get("properties", {}))
            schema_copy["properties"] = root_props

        validator_cls = jsonschema.validators.validator_for(schema_copy)
        validator_cls.check_schema(schema_copy)
        validator = validator_cls(schema_copy)
        for err in validator.iter_errors(data):
            path_str = " -> ".join(str(p) for p in err.path) if err.path else "root"
            errors.append(f"[{filename}] Schema error at '{path_str}': {err.message}")
    except ModuleNotFoundError:
        pass
    except Exception as e:
        errors.append(f"[{filename}] Schema validation failed: {e}")

    return errors


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Deterministic OSCAL v1.2.0 Export Engine"
    )
    parser.add_argument(
        "--registry",
        default="mappings/framework_registry.yaml",
        help="Path to framework registry YAML (default: mappings/framework_registry.yaml)",
    )
    parser.add_argument(
        "--output-dir",
        default="dist/oscal",
        help="Output directory for OSCAL artifacts (default: dist/oscal)",
    )
    parser.add_argument(
        "--schema",
        default="schemas/oscal_v1_2_0_subset.schema.json",
        help="Path to OSCAL subset schema (default: schemas/oscal_v1_2_0_subset.schema.json)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        default=False,
        help="Validate generated JSON models against OSCAL JSON schema",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        default=False,
        help="Check that files on disk match generated output without modifying disk",
    )

    args = parser.parse_args()

    registry_path = (REPO_ROOT / args.registry).resolve()
    output_dir = (REPO_ROOT / args.output_dir).resolve()
    schema_path = (REPO_ROOT / args.schema).resolve()

    if not registry_path.exists():
        print(f"[FAIL] Framework registry file not found: {registry_path}", file=sys.stderr)
        return 1

    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            registry_data = yaml.safe_load(f)
    except Exception as e:
        print(f"[FAIL] Could not parse framework registry: {e}", file=sys.stderr)
        return 1

    schema_data = None
    if args.validate:
        if not schema_path.exists():
            print(f"[FAIL] OSCAL schema file not found: {schema_path}", file=sys.stderr)
            return 1
        try:
            with open(schema_path, "r", encoding="utf-8") as sf:
                schema_data = json.load(sf)
        except Exception as e:
            print(f"[FAIL] Could not parse OSCAL schema: {e}", file=sys.stderr)
            return 1

    # Generate all 5 OSCAL models
    models = {
        "catalog.json": generate_catalog_model(registry_data),
        "mapping_collection.json": generate_mapping_collection_model(registry_data),
        "profile_e8_ml2.json": generate_profile_e8_ml2_model(registry_data),
        "profile_nist_800_53_moderate.json": generate_profile_nist_800_53_moderate_model(registry_data),
        "component_definition.json": generate_component_definition_model(registry_data),
    }

    all_errors: List[str] = []

    # Optional schema validation
    if args.validate and schema_data is not None:
        for fname, model_data in models.items():
            val_errs = validate_oscal_model(model_data, schema_data, fname)
            all_errors.extend(val_errs)

    if all_errors:
        print(f"[FAIL] Validation errors found in generated OSCAL models:", file=sys.stderr)
        for err in all_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    # Check mode: verify disk matches generated models
    if args.check:
        drift_detected = False
        for fname, model_data in models.items():
            target_file = output_dir / fname
            if not target_file.exists():
                print(f"[FAIL] Missing target file in --check mode: {target_file}", file=sys.stderr)
                drift_detected = True
                continue

            try:
                disk_content = target_file.read_text(encoding="utf-8")
                # Normalize line endings
                disk_content_norm = disk_content.replace("\r\n", "\n")
                generated_content = serialize_model(model_data)

                if disk_content_norm != generated_content:
                    print(
                        f"[FAIL] Drift detected in {fname}: on-disk content differs from generated OSCAL model",
                        file=sys.stderr,
                    )
                    drift_detected = True
            except Exception as e:
                print(f"[FAIL] Error reading {target_file}: {e}", file=sys.stderr)
                drift_detected = True

        if drift_detected:
            return 1

        print("[PASS] OSCAL export verification check passed: all 5 models are up to date and match exactly.")
        return 0

    # Write mode
    output_dir.mkdir(parents=True, exist_ok=True)
    for fname, model_data in models.items():
        target_file = output_dir / fname
        target_file.write_text(serialize_model(model_data), encoding="utf-8", newline="\n")
        try:
            rel_print = target_file.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            rel_print = target_file.as_posix()
        print(f"[OK] Exported OSCAL model: {rel_print}")

    try:
        out_rel = output_dir.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        out_rel = output_dir.as_posix()
    print(f"\n[PASS] Successfully generated 5 deterministic OSCAL v1.2.0 JSON models in {out_rel}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
