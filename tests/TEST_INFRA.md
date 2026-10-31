# Test Infrastructure Specification: Compliance-as-Code E2E Test Suite (v2.0)

## 1. Test Philosophy & Design Principles

The `security-standards-template` v2.0 test suite is designed as an **opaque-box, requirement-driven, zero-coupling** verification harness for modern Compliance-as-Code repositories.

1. **Opaque-Box Verification**: Evaluates the repository strictly through its external contracts, file artifacts, JSON Schemas (Draft 2020-12), OSCAL v1.2.0 exports, CLI interfaces, and rendered documentation.
2. **Authoritative 6-Framework Alignment**: Every test assertion maps directly to documented requirements across **ISO/IEC 27001:2022**, **AICPA SOC 2 TSC**, **NIST CSF 2.0**, **EU/UK GDPR**, **NIST SP 800-53 Rev. 5 (Moderate Baseline)**, and **ASD Essential Eight (ML1–ML3)**.
3. **Progressive Testability & Determinism**: Organized into 5 deterministic tiers (Tiers 1–4 E2E + Tier 5 Adversarial & Stress Challenger suites).
4. **Zero Residual State & Side-Effect Freedom**: Automated operations tested in Tiers 3 and 5 operate via `--dry-run`, `--check`, or temporary isolated sandboxes.
5. **No Facade or Dummy Tests**: Executes real `py_compile`, `mkdocs build --strict`, JSON Schema validation, SHA-256 byte-determinism checks, and negative CLI exit-code verification.

---

## 2. Directory Layout & Test Suite Architecture

```
security-standards-template/
├── .github/                                # CI/CD workflows, CODEOWNERS, dependabot, PR template
├── architecture/adr/                       # Architectural Decision Records (ADR-001..ADR-003)
├── dist/oscal/                             # Deterministic NIST OSCAL v1.2.0 JSON models (5 files)
├── schemas/                                # Draft 2020-12 JSON Schemas (4 files)
├── mappings/
│   ├── framework_registry.yaml             # Canonical control & 6-framework crosswalk registry (v2.0.0)
│   ├── compliance_manifest.yaml            # Adopted frameworks, thresholds, cadences & exceptions
│   └── catalogs/                           # 6 authoritative reference catalogs (*.yaml)
├── scripts/
│   ├── fill_placeholders.py                # Automated placeholder replacement CLI
│   ├── validate_isms.py                    # Schema, catalog, link, drift & 6-framework validator CLI
│   ├── export_oscal.py                     # Deterministic NIST OSCAL v1.2.0 exporter CLI
│   ├── check_adoption.py                   # Compliance adoption, cadence & exception auditor CLI
│   └── generate_docs.py                    # Automated Multi-Framework Crosswalk Markdown generator CLI
├── docs/                                   # 40 Markdown files across 4-tier ISMS hierarchy
└── tests/
    ├── TEST_INFRA.md                       # This infrastructure specification
    ├── TEST_READY.md                       # Test suite readiness summary & checklist
    ├── test_m1_stress_challenger.py        # Stress challenger for placeholder & MkDocs edge cases
    ├── test_tier5_adversarial_challenger.py # Tier 5 adversarial challenger (link graph, OSCAL, negative tests)
    └── e2e/
        ├── run_all_tests.py                # Master unified test runner across Tiers 1-4
        ├── test_tier1_static.py            # Tier 1: Static checks, syntax, schemas, ADRs & headers
        ├── test_tier2_mkdocs_build.py      # Tier 2: MkDocs strict build & 40-doc nav parity
        ├── test_tier3_automation.py        # Tier 3: CLI automation scripts validation (all 5 scripts)
        └── test_tier4_governance_audit.py  # Tier 4: Governance audit, 93-ctrl SoA, CSF 2.0 & 6-framework audit
```

---

## 3. Test Tier Specifications & Coverage Thresholds

- **Tier 1 (`test_tier1_static.py` — 11 tests)**: Verifies all root files (`LICENSE`, scripts, manifests), all 40 Markdown documents, compilation of all 5 Python CLI tools, YAML syntax across `mkdocs.yml`, `framework_registry.yaml`, `compliance_manifest.yaml`, 6 catalogs, and `.github/workflows/*.yml`, Draft 2020-12 JSON Schemas and OSCAL JSON files, ADR isolation outside `docs/`, relative link integrity, 7-key Document Control Header tables, 5-column Document History tables, and mandatory policy sections.
- **Tier 2 (`test_tier2_mkdocs_build.py` — 4 tests)**: Verifies Material theme configuration, 100% bidirectional nav/file parity across all 40 documents, and `mkdocs build --strict` with `NO_MKDOCS_2_WARNING=1`.
- **Tier 3 (`test_tier3_automation.py` — 10 tests)**: Verifies CLI flags, dry-run hash safety, JSON/SARIF output formats, and zero-error execution across `fill_placeholders.py`, `validate_isms.py`, `export_oscal.py`, `check_adoption.py`, and `generate_docs.py`.
- **Tier 4 (`test_tier4_governance_audit.py` — 15 tests)**: Verifies 93-control SoA completeness, zero deprecated ISO 2013 or banned standards (`SOC 2 DC3.1`, `DoD 5220.22-M`), zero retired NIST CSF 2.0 IDs (all 13 remediated), all 6 policy contradiction resolutions, and v2.0 6-framework registry coverage (`>= 45` CSF 2.0 subcategories, `>= 85` NIST 800-53 controls across all 20 families, all 24 Essential Eight ML1–ML3 capabilities).
- **Tier 5 (`test_tier5_adversarial_challenger.py` — 20 tests) & Stress (`test_m1_stress_challenger.py` — 9 tests)**: Exhaustive link/anchor verification (350+ links), OSCAL SHA-256 byte-determinism across runs, negative CLI tests for expired/invalid exceptions and doc drift, and workflow least-privilege `permissions:` verification.
