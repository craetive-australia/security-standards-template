# Test Infrastructure Specification: Compliance-as-Code E2E Test Suite

## 1. Test Philosophy & Design Principles

The `security-standards-template` test suite is designed as an **opaque-box, requirement-driven, zero-coupling** verification harness for modern Compliance-as-Code repositories.

1. **Opaque-Box Verification**: The test suite evaluates the repository strictly through its external contracts, file artifacts, CLI interfaces, and rendered documentation. Tests never assume internal function structures or private helper routines.
2. **Authoritative Specification Alignment**: Every test assertion maps directly to documented requirements in `ORIGINAL_REQUEST.md` and `PROJECT.md`, adhering to ISO/IEC 27001:2022, AICPA SOC 2 (2017/2022 TSC), NIST CSF 2.0, and GDPR.
3. **Progressive Testability & Determinism**: Tests are organized into four deterministic tiers that can be evaluated progressively as repository components are consolidated and implemented.
4. **Zero Residual State & Side-Effect Freedom**: Automated operations tested in Tier 3 (such as `fill_placeholders.py`) operate via `--dry-run` or temporary isolated sandboxes, ensuring that test runs leave no dirty git worktree state.
5. **No Facade or Dummy Tests**: Tests execute genuine validation routines (e.g. actual `py_compile`, real `mkdocs build --strict`, YAML schema parsing, exhaustive regex and link resolution checks) rather than mocking results.

---

## 2. Directory Layout & Test Suite Architecture

```
security-standards-template/
├── TEST_INFRA.md                           # This infrastructure specification
├── TEST_READY.md                           # Test suite readiness summary & checklist
├── mkdocs.yml                              # MkDocs documentation site configuration
├── requirements.txt                        # Python dependencies
├── mappings/
│   └── framework_registry.yaml             # Canonical control & framework crosswalk registry
├── scripts/
│   ├── fill_placeholders.py                # Automated placeholder replacement CLI
│   └── validate_isms.py                    # Automated ISMS integrity & coverage validator CLI
├── docs/                                   # 39 Markdown files across ISMS hierarchy
│   ├── index.md
│   ├── 01_ISMS_Framework/                  # 7 Governance documents (including SoA)
│   ├── 02_Policies/                        # 13 Organizational security policies
│   ├── 03_Standards_and_Procedures/        # 9 Operational standards & SOPs
│   └── 04_Templates_and_Registers/         # 8 Evidence templates, logs & registers
└── tests/
    └── e2e/
        ├── run_all_tests.py                # Master unified test runner across all 4 tiers
        ├── test_tier1_static.py            # Tier 1: Static checks, syntax & link integrity
        ├── test_tier2_mkdocs_build.py      # Tier 2: MkDocs strict build & nav parity
        ├── test_tier3_automation.py        # Tier 3: CLI automation scripts validation
        └── test_tier4_governance_audit.py  # Tier 4: Governance audit, 93-ctrl SoA & harmonization
```

---

## 3. Feature Inventory & Test Tier Mapping

All 30 project features from `PROJECT.md` map to the 4 test tiers:

| # | Feature Name | Target Milestone | Primary Test Tier | Test Module | Verification Method |
|---|--------------|------------------|-------------------|-------------|---------------------|
| 1 | Worktree File Consolidation | M1 | Tier 1 | `test_tier1_static.py` | Verify all expected root and docs files exist on disk |
| 2 | Repository Infrastructure | M1 | Tier 1 | `test_tier1_static.py` | Verify `.gitignore`, `requirements.txt`, and `README.md` contents |
| 3 | Modernize mkdocs.yml | M1 | Tier 2 | `test_tier2_mkdocs_build.py` | Verify Material theme, palette, search, PyMdown extensions |
| 4 | Fix fill_placeholders.py | M1 | Tier 3 | `test_tier3_automation.py` | Verify `--help` and dry-run execution without `args.ciso-name` error |
| 5 | Extend fill_placeholders.py | M1 | Tier 3 | `test_tier3_automation.py` | Test `--company-name`, `--ciso-name`, `--author-name`, `--dpo-name`, `--insert-date`, `--list-remaining`, `--dry-run` |
| 6 | Migrate ISO Citations | M2 | Tier 4 | `test_tier4_governance_audit.py` | Zero ISO 2013 citations (`A.9.`, `A.10.`, etc.) outside legacy crosswalks |
| 7 | Fix SOC 2 Citation | M2 | Tier 4 | `test_tier4_governance_audit.py` | Zero `SOC 2 DC3.1` occurrences; verify replacement with CC6.1, CC6.7, C1.1 |
| 8 | Fix Media Sanitization Citation | M2 | Tier 4 | `test_tier4_governance_audit.py` | Zero `DoD 5220.22-M`; verify `NIST SP 800-88 Rev. 1` & `IEEE 2883-2022` |
| 9 | NIST CSF 2.0 Crosswalk | M2 | Tier 4 | `test_tier4_governance_audit.py` | Verify NIST CSF 2.0 citations and crosswalk coverage |
| 10 | 93-Control SoA Expansion | M2 | Tier 4 | `test_tier4_governance_audit.py` | Verify all 93 ISO 27001:2022 controls present with valid relative links |
| 11 | Document Control Header Tables | M3 | Tier 1 | `test_tier1_static.py` | Verify 2-column key-value header table under title across all 38 docs |
| 12 | Document History Tables | M3 | Tier 1 | `test_tier1_static.py` | Verify 5-column Document History table at the bottom of all 38 docs |
| 13 | Policy Section Completeness | M3 | Tier 1 | `test_tier1_static.py` | Verify Roles/Resp, Compliance/Exceptions, Related Docs in all policies |
| 14 | Contradiction 1: Authentication | M3 | Tier 4 | `test_tier4_governance_audit.py` | 14-char min, passphrases, blocklist, no expiration, phishing-resistant MFA |
| 15 | Contradiction 2: Code Review & Supply Chain | M3 | Tier 4 | `test_tier4_governance_audit.py` | 1 peer approval standard, 2 approvals Tier-1, SBOM, secrets scan, signing |
| 16 | Contradiction 3: Data Classification | M3 | Tier 4 | `test_tier4_governance_audit.py` | Default Internal metadata, visual marking on Confidential/Restricted |
| 17 | Contradiction 4: Incident Response | M3 | Tier 4 | `test_tier4_governance_audit.py` | 5d Sev1/2, 10d Sev3 post-mortem SLAs, multi-jurisdiction breach SLA matrix |
| 18 | Contradiction 5: Log Retention & Sanitization | M3 | Tier 4 | `test_tier4_governance_audit.py` | 90d hot + 365d cold archive, debug max 30d, NIST SP 800-88 / IEEE 2883 |
| 19 | Contradiction 6: Access Reviews & Risk | M3 | Tier 4 | `test_tier4_governance_audit.py` | Monthly priv, quarterly crit, semi-annual std; CVSS v4, KEV, EPSS; 5x5 matrix |
| 20 | Author Governance Document | M4 | Tier 1, 4 | `test_tier1_static.py`, `test_tier4_governance_audit.py` | Existence, syntax, and ISO 27001 clauses (6.3, 7.1-7.5, 8.1, 9.1-9.3, 10.1-10.2) |
| 21 | Author Acceptable Use & AI Policy | M4 | Tier 1, 4 | `test_tier1_static.py`, `test_tier4_governance_audit.py` | Endpoint security, BYOD remote work, AI tiering, DLP, ISO 42001 & AI RMF |
| 22 | Author Internal Audit & CAPA Register | M4 | Tier 1, 4 | `test_tier1_static.py`, `test_tier4_governance_audit.py` | Audit schedule, audit findings log, CAPA log, management review minutes |
| 23 | Update Risk Register Exceptions | M4 | Tier 4 | `test_tier4_governance_audit.py` | Security Exception & Risk Acceptance Log section in `02_Risk_Register.md` |
| 24 | Author Onboarding Guide | M5 | Tier 1, 4 | `test_tier1_static.py`, `test_tier4_governance_audit.py` | Hub-and-spoke model, 5-step SOP, 4-tier domain pattern, 3-horizon roadmap |
| 25 | Author Framework Registry | M5 | Tier 1, 4 | `test_tier1_static.py`, `test_tier4_governance_audit.py` | YAML syntax, 55 canonical controls, mappings to ISO, SOC 2, NIST, GDPR |
| 26 | Author ISMS Validator CLI | M5 | Tier 1, 3 | `test_tier1_static.py`, `test_tier3_automation.py` | Python compile check, `--coverage-report`, and `--strict` mode execution |
| 27 | Update mkdocs.yml Nav | M5 | Tier 2 | `test_tier2_mkdocs_build.py` | Bidirectional nav/file parity: all 4 new docs present in navigation |
| 28 | E2E Test Suite Track | E2E | All Tiers | `run_all_tests.py` | Full test harness across Tiers 1-4 with unified reporting |
| 29 | 100% E2E Test Verification | M6 | Master | `run_all_tests.py` | 100% test pass rate with exit code 0 |
| 30 | Adversarial Coverage Hardening | M6 | Tier 4 | `test_tier4_governance_audit.py` | Stress tests for edge cases, escaping, broken links, conflicting numbers |

---

## 4. Test Tier Specifications & Coverage Thresholds

### Tier 1: Static Checks, Syntax & Structure (`test_tier1_static.py`)
- **Scope**:
  - File existence: checks all required repository files (`mkdocs.yml`, `README.md`, `.gitignore`, `requirements.txt`, `scripts/fill_placeholders.py`, `scripts/validate_isms.py`, `mappings/framework_registry.yaml`, and all 39 Markdown files).
  - Python scripts syntax validation via `py_compile.compile(doraise=True)`.
  - YAML syntax validation for `mkdocs.yml` and `mappings/framework_registry.yaml`.
  - Relative Markdown link resolution across all Markdown documents (no dead local relative links).
  - Document Control Header Table check across all 38 documents in 01, 02, 03, 04:
    - 2-column table directly under `# <Document Title>`.
    - Mandatory keys: `Document ID`, `Version`, `Effective Date`, `Document Owner`, `Review Cycle`, `Classification`, `Framework Mappings`.
    - Absence of collapsed bold metadata (e.g. `**Document Owner:**`).
  - Document History Table check across all 38 documents in 01, 02, 03, 04:
    - 5-column table at bottom: `Version`, `Date`, `Author`, `Approved By`, `Description`.
  - Mandatory policy sections check across all `docs/02_Policies/*.md`:
    - `Roles and Responsibilities`, `Compliance and Exceptions`, `Related Documents`.
- **Threshold**: 100% pass on all static checks. Minimum 8 test methods.

### Tier 2: MkDocs Strict Build & Navigation Parity (`test_tier2_mkdocs_build.py`)
- **Scope**:
  - Invokes `mkdocs build --strict` using the project's virtual environment executable.
  - Verifies exit code `0`, zero warnings, and clean HTML artifact generation under `site/`.
  - Bidirectional Nav/File Parity:
    - Every `.md` file under `docs/` is referenced in `mkdocs.yml` `nav`.
    - Every file referenced in `mkdocs.yml` `nav` exists on disk under `docs/`.
  - Material Theme Configuration:
    - Theme name is `material`.
    - Light/dark color palette toggle configured.
    - Navigation features: `navigation.instant`, `navigation.sections`, `navigation.tabs`, `navigation.top`.
    - Search plugin configured.
    - Markdown extensions: `admonition`, `codehilite` or `pymdownx.highlight`, `pymdownx.superfences`, `tables`.
- **Threshold**: Exit code 0, 0 build warnings, 0 orphaned or dead nav items. Minimum 4 test methods.

### Tier 3: Automation Tooling Validation (`test_tier3_automation.py`)
- **Scope**:
  - `fill_placeholders.py` CLI testing:
    - Verifies `--help` returns exit code 0.
    - Tests `--dry-run` with sample arguments (`--company-name`, `--ciso-name`, `--author-name`, `--dpo-name`, `--insert-date`) without mutating files on disk.
    - Verifies absence of the `args.ciso-name` syntax bug.
    - Tests `--list-remaining` lists unpopulated placeholder tokens.
    - Verifies both `docs/**/*.md` and `mkdocs.yml` are targeted.
  - `validate_isms.py` CLI testing:
    - Verifies `--help` returns exit code 0.
    - Executes `python scripts/validate_isms.py --strict`, asserting exit code 0.
    - Executes `python scripts/validate_isms.py --coverage-report`, asserting exit code 0 and parsing output for ISO 27001:2022 (93 controls / 100%), SOC 2, NIST CSF 2.0, and GDPR coverage metrics.
- **Threshold**: All CLI invocations exit with code 0 and correct outputs. Minimum 5 test methods.

### Tier 4: Governance, Auditing & Harmonization (`test_tier4_governance_audit.py`)
- **Scope**:
  - 93-Control Statement of Applicability (`docs/01_ISMS_Framework/05_Statement_of_Applicability_SoA.md`):
    - Asserts presence of all 93 controls: `A.5.1`–`A.5.37`, `A.6.1`–`A.6.8`, `A.7.1`–`A.7.14`, `A.8.1`–`A.8.34`.
    - Asserts every row contains an applicability decision, justification, and a valid relative markdown link to an existing document.
  - Deprecated Citation Scanner:
    - Asserts 0 occurrences of deprecated ISO 27001:2013 Annex A controls (`A.9.`, `A.10.`, `A.11.`, `A.12.`, `A.13.`, `A.14.`, `A.15.`, `A.16.`, `A.17.`, `A.18.`, `A.5.1.1`–`A.5.1.2`, etc.) outside explicit Legacy 2013 Crosswalk columns.
    - Asserts 0 occurrences of `SOC 2 DC3.1` and `DoD 5220.22-M`.
  - Six Policy Harmonization & Currency Checks:
    - 1. Authentication: 14-char min (`[MIN_PASSWORD_LENGTH]`), passphrases, blocklist check, no arbitrary composition or periodic expiration (NIST SP 800-63B), phishing-resistant MFA.
    - 2. Code Review & Supply Chain: 1 approval standard, 2 approvals (inc Security/CODEOWNERS) Tier-1, SBOM, secret scanning, Cosign/artifact signing.
    - 3. Data Classification: Default Internal metadata via DLP, visual markings on Confidential/Restricted.
    - 4. Incident Response: SLAs 5d Sev1/Sev2, 10d Sev3 post-mortems; multi-jurisdiction breach SLA matrix (GDPR 72h, SEC 4d, etc.).
    - 5. Log Retention & Sanitization: 90d hot + 365d cold archive, debug max 30d; sanitization via NIST SP 800-88 Rev 1 & IEEE 2883-2022.
    - 6. Access Reviews & Risk: Monthly privileged, quarterly critical, semi-annual standard; CVSS v4.0, CISA KEV, EPSS; KMS annual symmetric, <=90d TLS/secrets, PQC; explicit 1-5 scales and 5x5 matrix in `03_Risk_Management_Methodology.md`.
  - Machine-Readable Control Registry (`mappings/framework_registry.yaml`):
    - Valid schema structure (`schema_version`, `metadata`, `frameworks`, `domains`, `controls`).
    - At least 55 canonical controls defined.
    - 100% of the 93 ISO 27001:2022 controls mapped.
    - Implementing documents exist on disk.
- **Threshold**: 100% compliance across all governance and audit criteria. Minimum 8 test methods.

---

## 5. Master Test Runner (`tests/e2e/run_all_tests.py`)

The master runner executes all four test tiers sequentially:
1. Runs each tier's test cases using `unittest.TextTestRunner`.
2. Collects pass/fail/error counts and test durations.
3. Renders a unified Markdown/ASCII summary table.
4. Exits with code `0` if and only if 100% of tests pass across all tiers, and exit code `1` if any test fails.

### CLI Execution Command
```powershell
pwsh -NoProfile -Command "& 'C:\Users\andre\.gemini\antigravity\worktrees\security-standards-template\swift_axis_crosses_22h57\.venv\Scripts\python.exe' tests/e2e/run_all_tests.py"
```
