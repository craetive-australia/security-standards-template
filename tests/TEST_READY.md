# TEST_READY: Compliance-as-Code E2E & Adversarial Test Suite (v2.0)

**Repository**: `security-standards-template`  
**Date**: 2026-10-31  
**Status**: **READY & 100% PASSING (v2.0 Modernization Complete)**  

---

## 1. Executive Summary

The End-to-End (E2E) and Adversarial Test Suite for `security-standards-template` v2.0 validates all **40 ISMS Markdown documents**, **5 CLI automation tools**, **4 Draft 2020-12 JSON Schemas**, **6 authoritative reference catalogs**, **5 deterministic NIST OSCAL v1.2.0 JSON models**, and **3 GitHub Actions CI/CD workflows**.

---

## 2. Test Architecture & File Manifest

| File Path | Role / Description | Test Class(es) | Test Count |
|---|---|---|---|
| `tests/e2e/test_tier1_static.py` | Tier 1: Static checks, file existence, Python/YAML/JSON syntax, ADRs, header/footer tables | `TestTier1Static` | 11 |
| `tests/e2e/test_tier2_mkdocs_build.py` | Tier 2: MkDocs strict build, 40-doc bidirectional nav/file parity, theme config | `TestTier2MkDocsBuild` | 4 |
| `tests/e2e/test_tier3_automation.py` | Tier 3: CLI automation (`fill_placeholders`, `validate_isms`, `export_oscal`, `check_adoption`, `generate_docs`) | `TestTier3Automation` | 10 |
| `tests/e2e/test_tier4_governance_audit.py` | Tier 4: 93-control SoA, zero retired CSF 2.0 / ISO 2013 citations, 6-framework v2.0 registry | `TestTier4GovernanceAudit` | 15 |
| `tests/e2e/run_all_tests.py` | Master E2E runner across Tiers 1–4 with formatted table reporting | CLI Runner | 40 E2E tests |
| `tests/test_tier5_adversarial_challenger.py` | Tier 5: Exhaustive link/anchor oracle, OSCAL determinism, negative adoption/drift tests, CI permissions | 4 Test Classes | 20 |
| `tests/test_m1_stress_challenger.py` | Stress Challenger: 40/40 placeholder dry-run, Unicode cp1252 resilience, negative MkDocs builds | `TestMilestone1AdversarialStress` | 9 |

---

## 3. How to Run the Verification Suite

Whenever executing commands in PowerShell/pwsh, **ALWAYS use the `-NoProfile` flag**.

```powershell
# 1. Run Master 4-Tier E2E Test Suite (40 tests)
.\.venv\Scripts\python.exe tests/e2e/run_all_tests.py

# 2. Run Tier 5 Adversarial Challenger Suite (20 tests)
.\.venv\Scripts\python.exe tests/test_tier5_adversarial_challenger.py

# 3. Run Milestone 1 Stress Challenger Suite (9 tests)
.\.venv\Scripts\python.exe tests/test_m1_stress_challenger.py

# 4. Run All v2.0 CLI Verification Gates
.\.venv\Scripts\python.exe scripts/validate_isms.py --strict --coverage-report --check-drift
.\.venv\Scripts\python.exe scripts/export_oscal.py --validate --check
.\.venv\Scripts\python.exe scripts/generate_docs.py --check
.\.venv\Scripts\python.exe scripts/check_adoption.py --manifest mappings/compliance_manifest.yaml --strict
$env:NO_MKDOCS_2_WARNING='1'; .\.venv\Scripts\mkdocs.exe build --strict
```
