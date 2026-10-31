## Summary of Changes
<!-- Describe the policy, standard, control mapping, or tooling changes and reference applicable canonical control IDs (e.g., CC-AC-02) -->

## Compliance-as-Code Verification Checklist
- [ ] **Metadata Headers**: Document Control Header Tables verified across all modified `.md` files (7 required keys, no collapsed inline bold metadata).
- [ ] **Revision History**: `## Document History` tables updated with the new version, date, author, approver, and change description.
- [ ] **Link & Citation Integrity**: Relative Markdown links and heading anchors verified; zero deprecated ISO 27001:2013 or retired NIST CSF 2.0 IDs introduced.
- [ ] **ISMS Validator & Drift Check**: `python scripts/validate_isms.py --strict --coverage-report --check-drift` exits with code `0`.
- [ ] **Deterministic OSCAL v1.2.0 Export**: `python scripts/export_oscal.py --validate --check` exits with code `0`.
- [ ] **Crosswalk Documentation Sync**: `python scripts/generate_docs.py --check` exits with code `0`.
- [ ] **Adoption & Exception Audit**: `python scripts/check_adoption.py --manifest mappings/compliance_manifest.yaml --strict` exits with code `0`.
- [ ] **Strict Portal Build**: `mkdocs build --strict` passes with `0` warnings and `0` errors.
- [ ] **Test Suites**: `python tests/e2e/run_all_tests.py`, `python tests/test_tier5_adversarial_challenger.py`, and `python tests/test_m1_stress_challenger.py` pass 100%.

## Approvals
- [ ] Peer technical/compliance review completed.
- [ ] Tier-1 governance / CISO approval (`CODEOWNERS`) obtained where applicable.
