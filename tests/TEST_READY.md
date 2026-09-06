# TEST_READY: Compliance-as-Code E2E Test Suite

**Repository**: `security-standards-template`  
**Date**: 2026-10-26  
**Status**: **READY FOR EXECUTION & MILESTONE VERIFICATION**  
**Author**: `test_writer_e2e`  

---

## 1. Executive Summary

The comprehensive, opaque-box End-to-End (E2E) Test Suite for `security-standards-template` is fully implemented and operational in `tests/e2e/`.

The test suite provides **33 automated test methods** structured across **four sequential tiers** designed to validate repository consolidation, strict documentation builds, CLI automation tooling, ISO/IEC 27001:2022 governance completeness (all 93 controls), SOC 2 TSC / NIST CSF 2.0 / GDPR mappings, and internal policy harmonization.

All test modules are self-contained, deterministic, and runnable directly via Python `unittest` or through the unified master runner `tests/e2e/run_all_tests.py`.

---

## 2. Test Architecture & File Manifest

| File Path | Role / Description | Test Class | Test Count |
|---|---|---|---|
| `tests/e2e/test_tier1_static.py` | Tier 1: Static checks, file existence, syntax, header/footer tables | `TestTier1Static` | 9 |
| `tests/e2e/test_tier2_mkdocs_build.py` | Tier 2: MkDocs strict build, bidirectional nav/file parity, theme config | `TestTier2MkDocsBuild` | 4 |
| `tests/e2e/test_tier3_automation.py` | Tier 3: CLI automation (`fill_placeholders.py`, `validate_isms.py`) | `TestTier3Automation` | 6 |
| `tests/e2e/test_tier4_governance_audit.py` | Tier 4: Governance audit, 93-control SoA, citation scanning, 6 contradictions | `TestTier4GovernanceAudit` | 14 |
| `tests/e2e/run_all_tests.py` | Master E2E runner across all 4 tiers with formatted table reporting | CLI Runner | 33 total |
| `TEST_INFRA.md` | Test infrastructure specification and feature-to-tier matrix | Reference Doc | — |

---

## 3. How to Run the Tests

Whenever executing commands in PowerShell/pwsh, **ALWAYS use the `-NoProfile` flag**.

### A. Run Master E2E Test Suite (All 4 Tiers)
```powershell
pwsh -NoProfile -Command "& 'C:\Users\andre\.gemini\antigravity\worktrees\security-standards-template\swift_axis_crosses_22h57\.venv\Scripts\python.exe' tests/e2e/run_all_tests.py"
```

### B. Run Individual Test Tiers
```powershell
# Tier 1: Static Checks, Syntax & Structure
pwsh -NoProfile -Command "& 'C:\Users\andre\.gemini\antigravity\worktrees\security-standards-template\swift_axis_crosses_22h57\.venv\Scripts\python.exe' tests/e2e/run_all_tests.py --tier 1"

# Tier 2: MkDocs Strict Build & Navigation Parity
pwsh -NoProfile -Command "& 'C:\Users\andre\.gemini\antigravity\worktrees\security-standards-template\swift_axis_crosses_22h57\.venv\Scripts\python.exe' tests/e2e/run_all_tests.py --tier 2"

# Tier 3: Automation Tooling Validation
pwsh -NoProfile -Command "& 'C:\Users\andre\.gemini\antigravity\worktrees\security-standards-template\swift_axis_crosses_22h57\.venv\Scripts\python.exe' tests/e2e/run_all_tests.py --tier 3"

# Tier 4: Governance, Auditing & Harmonization
pwsh -NoProfile -Command "& 'C:\Users\andre\.gemini\antigravity\worktrees\security-standards-template\swift_axis_crosses_22h57\.venv\Scripts\python.exe' tests/e2e/run_all_tests.py --tier 4"
```

### C. Run via Standard Python unittest
```powershell
pwsh -NoProfile -Command "& 'C:\Users\andre\.gemini\antigravity\worktrees\security-standards-template\swift_axis_crosses_22h57\.venv\Scripts\python.exe' -m unittest discover -s tests/e2e -p 'test_*.py' -v"
```

---

## 4. Tier-by-Tier Test Coverage Breakdown

### Tier 1: Static Checks, Syntax & Structure (9 tests)
- `test_repository_files_exist`: Verifies all core repository root files (`mkdocs.yml`, `README.md`, `.gitignore`, `requirements.txt`, `TEST_INFRA.md`, `scripts/fill_placeholders.py`, `scripts/validate_isms.py`, `mappings/framework_registry.yaml`).
- `test_all_documentation_files_exist`: Verifies existence of all 39 documentation files across `docs/01_ISMS_Framework/` (7), `docs/02_Policies/` (13), `docs/03_Standards_and_Procedures/` (9), `docs/04_Templates_and_Registers/` (8), and `docs/index.md` (1).
- `test_python_scripts_syntax`: Validates clean compilation (`py_compile.compile`) of all Python scripts.
- `test_yaml_files_syntax`: Validates parsing of `mkdocs.yml` and `mappings/framework_registry.yaml`.
- `test_markdown_relative_links`: Recursively parses all local relative Markdown links and verifies targets exist on disk.
- `test_document_control_header_tables`: Verifies 2-column key-value Document Control Header Table under title for all 38 documents, rejecting deprecated collapsed single-line bold metadata.
- `test_document_history_tables`: Verifies 5-column Document History Table at bottom for all 38 documents.
- `test_policy_mandatory_sections`: Verifies `Roles and Responsibilities`, `Compliance and Exceptions`, and `Related Documents` sections in all 13 policies.
- `test_repository_infrastructure_metadata`: Verifies comprehensive `README.md`, `.gitignore` entries, and `requirements.txt`.

### Tier 2: MkDocs Strict Build & Navigation Parity (4 tests)
- `test_mkdocs_configuration_exists`: Verifies `mkdocs.yml` is present.
- `test_material_theme_configuration`: Validates Material theme name, dark/light palette toggle, navigation features (`navigation.instant`, `navigation.sections`, `navigation.tabs`, `navigation.top`), search plugin, and Markdown extensions (`admonition`, `tables`).
- `test_bidirectional_nav_file_parity`: Verifies 100% bidirectional parity (zero orphaned docs in filesystem, zero dead links in `mkdocs.yml` `nav`).
- `test_mkdocs_strict_build`: Executes `mkdocs build --strict` using virtual environment binary, verifying exit code `0`, zero warnings, and `site/index.html` generation.

### Tier 3: Automation Tooling Validation (6 tests)
- `test_fill_placeholders_help`: Verifies `--help` runs with exit code 0.
- `test_fill_placeholders_dry_run_execution`: Tests `--dry-run` with `--company-name`, `--ciso-name`, `--author-name`, `--dpo-name`, `--insert-date`, `--min-password-length`, asserting exit code 0 and verifying zero mutation of target files.
- `test_fill_placeholders_list_remaining`: Verifies `--list-remaining` lists unpopulated placeholder tokens.
- `test_validate_isms_help`: Verifies `--help` runs with exit code 0.
- `test_validate_isms_strict_mode`: Runs `python scripts/validate_isms.py --strict`, asserting exit code 0.
- `test_validate_isms_coverage_report`: Runs `python scripts/validate_isms.py --coverage-report`, asserting exit code 0 and parsing framework coverage metrics.

### Tier 4: Governance, Auditing & Harmonization (14 tests)
- `test_soa_93_controls_completeness_and_links`: Asserts all 93 ISO/IEC 27001:2022 controls (`A.5.1`–`A.5.37`, `A.6.1`–`A.6.8`, `A.7.1`–`A.7.14`, `A.8.1`–`A.8.34`) are present in `05_Statement_of_Applicability_SoA.md`, and that every implementing link resolves to an existing file.
- `test_zero_deprecated_iso_2013_citations`: Scans `docs/` for obsolete ISO 2013 controls (`A.9.` to `A.18.`, `A.5.1.1`, etc.), asserting 0 occurrences outside designated legacy crosswalk columns.
- `test_zero_invalid_and_deprecated_standards`: Asserts 0 occurrences of `SOC 2 DC3.1` and `DoD 5220.22-M`.
- `test_contradiction_1_authentication_standard`: Verifies 14-char min length (`[MIN_PASSWORD_LENGTH]`), passphrases, blocklist check, no expiration, and phishing-resistant MFA (FIDO2/WebAuthn).
- `test_contradiction_2_code_review_and_supply_chain`: Verifies 1 approval standard, 2 approvals Tier-1, SBOM, secret scanning, and Cosign artifact signing.
- `test_contradiction_3_data_classification`: Verifies default `Internal` metadata classification via DLP, and visual markings on `Confidential` and `Restricted`.
- `test_contradiction_4_incident_slas_and_breach_matrix`: Verifies 5d/10d post-mortem SLAs and 7-jurisdiction breach notification matrix (GDPR 72h, SEC 4d, etc.).
- `test_contradiction_5_log_retention_and_sanitization`: Verifies 90d hot + 365d cold archive log retention, debug max 30d, and sanitization via NIST SP 800-88 Rev. 1 / IEEE 2883-2022.
- `test_contradiction_6_access_reviews_vulnerability_and_risk`: Verifies access review cadences (monthly/quarterly/semi-annual), CVSS v4.0 / KEV / EPSS, and 5x5 (1-25) risk matrix in `03_Risk_Management_Methodology.md`.
- `test_governance_document_clauses`: Verifies `06_ISMS_Governance_Audit_and_Improvement.md` covers Clauses 6.3, 7.1-7.5, 8.1, 9.1-9.3, 10.1-10.2.
- `test_acceptable_use_and_ai_security_policy`: Verifies `13_Acceptable_Use_and_AI_Security_Policy.md` covers endpoint encryption, MDM, BYOD remote work, and Generative AI / LLM governance (ISO 42001 & NIST AI RMF).
- `test_internal_audit_and_capa_register`: Verifies `08_Internal_Audit_and_CAPA_Register.md` includes audit schedule, findings log, CAPA log, and management review minutes.
- `test_risk_register_security_exceptions_section`: Verifies `02_Risk_Register.md` includes Security Exception & Risk Acceptance Log with compensating controls and expiration.
- `test_framework_registry_schema_and_canonical_controls`: Verifies `mappings/framework_registry.yaml` schema, at least 55 canonical controls, and mapping to all 93 ISO 27001:2022 controls.

---

## 5. Feature Verification Matrix

| Feature # | Feature Name | Test Module | Verification Method | Status |
|---|---|---|---|---|
| F01 | Worktree File Consolidation | `test_tier1_static.py` | `test_all_documentation_files_exist` | Verified in T1 |
| F02 | Repository Infrastructure | `test_tier1_static.py` | `test_repository_infrastructure_metadata` | Verified in T1 |
| F03 | Modernize mkdocs.yml | `test_tier2_mkdocs_build.py` | `test_material_theme_configuration` | Verified in T2 |
| F04 | Fix fill_placeholders.py | `test_tier3_automation.py` | `test_fill_placeholders_dry_run_execution` | Verified in T3 |
| F05 | Extend fill_placeholders.py | `test_tier3_automation.py` | `test_fill_placeholders_list_remaining` | Verified in T3 |
| F06 | Migrate ISO Citations | `test_tier4_governance_audit.py` | `test_zero_deprecated_iso_2013_citations` | Verified in T4 |
| F07 | Fix SOC 2 Citation | `test_tier4_governance_audit.py` | `test_zero_invalid_and_deprecated_standards` | Verified in T4 |
| F08 | Fix Media Sanitization Citation | `test_tier4_governance_audit.py` | `test_zero_invalid_and_deprecated_standards` | Verified in T4 |
| F09 | NIST CSF 2.0 Crosswalk | `test_tier4_governance_audit.py` | `test_framework_registry_schema_and_canonical_controls` | Verified in T4 |
| F10 | 93-Control SoA Expansion | `test_tier4_governance_audit.py` | `test_soa_93_controls_completeness_and_links` | Verified in T4 |
| F11 | Document Control Header Tables | `test_tier1_static.py` | `test_document_control_header_tables` | Verified in T1 |
| F12 | Document History Tables | `test_tier1_static.py` | `test_document_history_tables` | Verified in T1 |
| F13 | Policy Section Completeness | `test_tier1_static.py` | `test_policy_mandatory_sections` | Verified in T1 |
| F14 | Contradiction 1: Authentication | `test_tier4_governance_audit.py` | `test_contradiction_1_authentication_standard` | Verified in T4 |
| F15 | Contradiction 2: Code Review & Supply Chain | `test_tier4_governance_audit.py` | `test_contradiction_2_code_review_and_supply_chain` | Verified in T4 |
| F16 | Contradiction 3: Data Classification | `test_tier4_governance_audit.py` | `test_contradiction_3_data_classification` | Verified in T4 |
| F17 | Contradiction 4: Incident Response | `test_tier4_governance_audit.py` | `test_contradiction_4_incident_slas_and_breach_matrix` | Verified in T4 |
| F18 | Contradiction 5: Log Retention & Sanitization | `test_tier4_governance_audit.py` | `test_contradiction_5_log_retention_and_sanitization` | Verified in T4 |
| F19 | Contradiction 6: Access Reviews & Risk | `test_tier4_governance_audit.py` | `test_contradiction_6_access_reviews_vulnerability_and_risk` | Verified in T4 |
| F20 | Author Governance Document | `test_tier4_governance_audit.py` | `test_governance_document_clauses` | Verified in T4 |
| F21 | Author Acceptable Use & AI Policy | `test_tier4_governance_audit.py` | `test_acceptable_use_and_ai_security_policy` | Verified in T4 |
| F22 | Author Internal Audit & CAPA Register | `test_tier4_governance_audit.py` | `test_internal_audit_and_capa_register` | Verified in T4 |
| F23 | Update Risk Register Exceptions | `test_tier4_governance_audit.py` | `test_risk_register_security_exceptions_section` | Verified in T4 |
| F24 | Author Onboarding Guide | `test_tier1_static.py` | `test_all_documentation_files_exist` | Verified in T1 |
| F25 | Author Framework Registry | `test_tier4_governance_audit.py` | `test_framework_registry_schema_and_canonical_controls` | Verified in T4 |
| F26 | Author ISMS Validator CLI | `test_tier3_automation.py` | `test_validate_isms_strict_mode` | Verified in T3 |
| F27 | Update mkdocs.yml Nav | `test_tier2_mkdocs_build.py` | `test_bidirectional_nav_file_parity` | Verified in T2 |
| F28 | E2E Test Suite Track | `run_all_tests.py` | Master Runner across Tiers 1-4 | Ready |
| F29 | 100% E2E Test Verification | `run_all_tests.py` | Master Runner exit code 0 | Milestone 6 |
| F30 | Adversarial Coverage Hardening | `test_tier4_governance_audit.py` | Deprecated citation & edge-case scans | Ready |
