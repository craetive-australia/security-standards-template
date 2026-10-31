# Information Security Management System (ISMS) — Standards Template (v2.0)

[![Standard: ISO/IEC 27001:2022](https://img.shields.io/badge/ISO%2FIEC%2027001-2022%20Aligned-blue.svg)](https://www.iso.org/standard/27001)
[![Standard: SOC 2 Type II](https://img.shields.io/badge/AICPA%20SOC%202-2017%2F2022%20TSC-green.svg)](https://www.aicpa.org/soc4so)
[![Standard: NIST CSF 2.0](https://img.shields.io/badge/NIST%20CSF-2.0-orange.svg)](https://www.nist.gov/cyberframework)
[![Standard: GDPR](https://img.shields.io/badge/EU%20GDPR-Compliant-darkblue.svg)](https://gdpr.eu/)
[![Standard: NIST SP 800-53 Rev. 5](https://img.shields.io/badge/NIST%20SP%20800--53-Rev.%205%20Moderate-blueviolet.svg)](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
[![Standard: ASD Essential Eight](https://img.shields.io/badge/ASD%20Essential%20Eight-ML1--ML3-008080.svg)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight)
[![Export: NIST OSCAL v1.2.0](https://img.shields.io/badge/OSCAL-v1.2.0%20JSON-success.svg)](https://pages.nist.gov/OSCAL/)
[![Built with MkDocs Material](https://img.shields.io/badge/Docs-MkDocs%20Material-teal.svg)](https://squidfunk.github.io/mkdocs-material/)

A production-grade, audit-ready **Compliance-as-Code** Information Security Management System (ISMS) documentation and automation platform. Designed for modern engineering organizations, cloud-native technology companies, and regulated enterprises that maintain their governance, security policies, and machine-readable control mappings in version control.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture & Directory Structure](#architecture--directory-structure)
- [Prerequisites & Setup](#prerequisites--setup)
- [Quickstart Guide](#quickstart-guide)
  - [1. Python & Virtual Environment Setup](#1-python--virtual-environment-setup)
  - [2. Automated Placeholder Population](#2-automated-placeholder-population)
  - [3. Local Preview](#3-local-preview)
  - [4. Production Build](#4-production-build)
  - [5. Automated ISMS Validation, OSCAL Export & Adoption Auditing](#5-automated-isms-validation-oscal-export--adoption-auditing)
- [Harmonized Standards Summary](#harmonized-standards-summary)
- [Framework & Domain Onboarding Architecture](#framework--domain-onboarding-architecture)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Maintaining security policies in fragmented word processor files or disparate wiki pages leads to policy drift, out-of-date citations, internal contradictions, and painful audit cycles.

This repository implements a **Compliance-as-Code (v2.0)** model:
- **Canonical Control Hub-and-Spoke**: Core organizational requirements are defined once across **98 canonical controls** (`mappings/framework_registry.yaml` v2.0.0) and mapped across six authoritative reference catalogs (`mappings/catalogs/*.yaml`): **ISO/IEC 27001:2022**, **AICPA SOC 2 TSC**, **NIST CSF 2.0**, **EU/UK GDPR**, **NIST SP 800-53 Rev. 5 (Moderate Baseline)**, and **ASD Essential Eight (ML1–ML3)**.
- **Deterministic NIST OSCAL v1.2.0 Export**: `scripts/export_oscal.py` compiles the YAML Single Source of Truth into five deterministic OSCAL v1.2.0 JSON models (`catalog.json`, `mapping_collection.json`, `profile_e8_ml2.json`, `profile_nist_800_53_moderate.json`, and `component_definition.json`) using RFC 4122 UUIDv5 identifiers.
- **Automated Policy Adoption & Exception Governance**: `scripts/check_adoption.py` audits organizational framework coverage targets, Essential Eight Maturity Level 2 (`ML2`) compliance, annual document review cadences (`<= 365` days), and time-bound security exceptions (`<= 90` days) declared in `mappings/compliance_manifest.yaml`.
- **Automated Crosswalk Documentation Generation**: `scripts/generate_docs.py` generates `docs/01_ISMS_Framework/08_Multi_Framework_Crosswalk_and_OSCAL_Matrix.md` directly from the registry and verifies zero documentation drift in CI.
- **Modern Documentation Portal**: Powered by MkDocs Material with dark/light mode toggles, instant navigation, search indexing, and rich callout extensions.

---

## Key Features

- **ISO/IEC 27001:2022 Annex A Coverage**: Full 93-control Statement of Applicability (SoA) covering Organizational (37), People (8), Physical (14), and Technological (34) controls.
- **6-Framework Hub-and-Spoke Alignment**: Pre-mapped and schema-validated against ISO/IEC 27001:2022 (93 controls), AICPA SOC 2 TSC (61 criteria), NIST CSF 2.0 (106 subcategories), GDPR, NIST SP 800-53 Rev. 5 Moderate Baseline (177 controls across all 20 families `AC`–`SR`), and ASD Essential Eight (all 8 strategies across ML1, ML2, and ML3 + ASD ISM mappings).
- **ASD Essential Eight ML2/ML3 Technical Baselines**: Explicit technical mandates for workstation/server application control (`E8-AC`), 48-hour critical exploit patching (`E8-PA`/`E8-PO`), Microsoft Office internet macro blocking and AMSI inspection (`E8-OM`), browser hardening (`E8-AH`), dedicated unprivileged/privileged account separation (`E8-AP`), phishing-resistant FIDO2/WebAuthn MFA (`E8-MF`), and immutable backups (`E8-RB`).
- **NIST SP 800-63B Authentication**: Passphrase support, 14-character minimum length (`[MIN_PASSWORD_LENGTH]`), credential stuffing defense, no arbitrary expiration, and phishing-resistant MFA (FIDO2/WebAuthn).
- **Modern DevSecOps & Supply Chain**: Multi-tier pull request review gates, Software Bill of Materials (SBOM), secret scanning in CI/CD, and cryptographic artifact signing (Sigstore/Cosign).
- **Clear Incident & Breach SLAs**: Severity-driven incident classification with strict post-mortem timelines and multi-jurisdictional breach notification timelines (GDPR 72h, NIS2 24h/72h, CIRCIA 72h, SEC 4 days).
- **Modern Media Sanitization**: Fully aligned with NIST SP 800-88 Rev. 1 (Clear, Purge, Destroy) and IEEE 2883-2022, replacing deprecated DoD standards.

---

## Architecture & Directory Structure

```
security-standards-template/
├── .github/
│   ├── CODEOWNERS                  # Mandatory security/CISO review boundaries
│   ├── dependabot.yml              # Automated dependency & GitHub Actions updates
│   ├── pull_request_template.md    # Compliance-as-Code PR verification checklist
│   └── workflows/                  # CI/CD validation, scheduled audit, and Pages deploy
├── architecture/
│   └── adr/                        # Architectural Decision Records (ADR-001..ADR-003)
├── dist/
│   └── oscal/                      # Deterministic NIST OSCAL v1.2.0 JSON artifacts
├── docs/
│   ├── index.md                    # ISMS portal homepage and executive overview
│   ├── 01_ISMS_Framework/          # Governance, context, risk, SoA, onboarding & crosswalk
│   │   ├── 01_Information_Security_Policy.md
│   │   ├── 02_Context_of_the_Organization.md
│   │   ├── 03_Risk_Management_Methodology.md
│   │   ├── 04_Roles_and_Responsibilities.md
│   │   ├── 05_Statement_of_Applicability_SoA.md
│   │   ├── 06_ISMS_Governance_Audit_and_Improvement.md
│   │   ├── 07_Framework_and_Domain_Onboarding_Guide.md
│   │   └── 08_Multi_Framework_Crosswalk_and_OSCAL_Matrix.md
│   ├── 02_Policies/                # Mandatory organizational policies (01..13)
│   ├── 03_Standards_and_Procedures/ # Operational technical standards and SOPs (01..09)
│   └── 04_Templates_and_Registers/ # Operational registers and audit templates (01..08)
├── mappings/
│   ├── framework_registry.yaml     # Canonical control mapping database (v2.0.0)
│   ├── compliance_manifest.yaml    # Adopted frameworks, thresholds, cadences & exceptions
│   └── catalogs/                   # Authoritative reference catalogs (6 frameworks)
├── schemas/                        # Draft 2020-12 JSON Schemas (registry, catalog, manifest, OSCAL)
├── scripts/
│   ├── fill_placeholders.py        # Automated placeholder replacement & discovery tool
│   ├── validate_isms.py            # Schema, catalog, link, drift & 6-framework validator
│   ├── export_oscal.py             # Deterministic NIST OSCAL v1.2.0 JSON exporter
│   ├── check_adoption.py           # Manifest threshold, review cadence & exception auditor
│   └── generate_docs.py            # Automated Multi-Framework Crosswalk Markdown generator
└── tests/                          # 5-Tier E2E, Stress & Adversarial Challenger suites
```

---

## Prerequisites & Setup

- **[uv](https://docs.astral.sh/uv/)** (Recommended): Fast Python package and version manager
  - Install on Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
  - Install on macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Python**: 3.10 or newer (automatically installed and managed by `uv python` if using `uv`)
- **Git**: 2.30+
- **Modern Web Browser**: Chrome, Firefox, Safari, or Edge

---

## Quickstart Guide

### 1. Python & Virtual Environment Setup

#### Option A: Using `uv` (Recommended)

With [`uv`](https://docs.astral.sh/uv/), Python versions and virtual environments are controlled automatically without manual activation:

```bash
# 1. Install and pin a specific Python version (e.g., Python 3.12)
uv python install 3.12
uv python pin 3.12

# 2. Sync dependencies into the virtual environment (.venv)
uv sync

# Alternatively, if installing directly from requirements.txt:
# uv venv && uv pip install -r requirements.txt
```

> [!TIP]
> **No manual environment activation required**: When using `uv`, you can execute any tool directly via `uv run` (e.g., `uv run mkdocs serve` or `uv run python scripts/validate_isms.py`). It will automatically discover and run inside `.venv`.
>
> If you still prefer activating the virtual environment manually in your shell:
> - **Linux/macOS**: `source .venv/bin/activate`
> - **Windows (PowerShell)**: `.\.venv\Scripts\Activate.ps1`

#### Option B: Standard `venv` + `pip` (Fallback)

```bash
# Create virtual environment
python -m venv .venv

# Activate on Linux/macOS:
source .venv/bin/activate

# Activate on Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Automated Placeholder Population

The template includes placeholder tags (such as `[COMPANY_NAME]`, `[CISO_NAME]`, `[AUTHOR_NAME]`, `[DPO_NAME]`, and `[INSERT_DATE]`) across documentation files and `mkdocs.yml`.

Use `scripts/fill_placeholders.py` (via `uv run`) to inspect and populate them:

```bash
# 1. Preview changes without modifying files (Dry Run)
uv run python scripts/fill_placeholders.py \
  --company-name "Acme Corporation" \
  --ciso-name "Jane Doe" \
  --author-name "Security Engineering Team" \
  --dpo-name "Alex Rivera" \
  --insert-date "2026-10-31" \
  --dry-run

# 2. Apply replacements across docs/ and mkdocs.yml
uv run python scripts/fill_placeholders.py \
  --company-name "Acme Corporation" \
  --ciso-name "Jane Doe" \
  --author-name "Security Engineering Team" \
  --dpo-name "Alex Rivera" \
  --insert-date "2026-10-31"

# 3. Or apply from a configuration file (YAML or JSON)
uv run python scripts/fill_placeholders.py --config config.yaml

# 4. Discover remaining unpopulated placeholders
uv run python scripts/fill_placeholders.py --list-remaining
```

#### CLI Options for `scripts/fill_placeholders.py`:
| Option | Description | Example |
|---|---|---|
| `--config <path>` | Path to YAML or JSON placeholder configuration file | `--config isms_vars.yaml` |
| `--company-name <str>` | Replaces `[COMPANY_NAME]` | `--company-name "Acme Corp"` |
| `--ciso-name <str>` | Replaces `[CISO_NAME]` | `--ciso-name "Jane Doe"` |
| `--author-name <str>` | Replaces `[AUTHOR_NAME]` | `--author-name "SecOps"` |
| `--dpo-name <str>` | Replaces `[DPO_NAME]` | `--dpo-name "Alex Rivera"` |
| `--insert-date <str>` | Replaces `[INSERT_DATE]` | `--insert-date "2026-10-31"` |
| `--applicable-regulations <str>` | Replaces `[APPLICABLE_REGULATIONS]` | `--applicable-regulations "GDPR, SOC 2, ISO 27001"` |
| `--industry-sector <str>` | Replaces `[INDUSTRY_SECTOR]` | `--industry-sector "Cloud FinTech"` |
| `--org-structure <str>` | Replaces `[ORG_STRUCTURE]` | `--org-structure "Remote-first global engineering organization"` |
| `--isms-scope <str>` | Replaces `[ISMS_SCOPE]` | `--isms-scope "Core SaaS platform and cloud infrastructure"` |
| `--min-password-length <int>` | Replaces `[MIN_PASSWORD_LENGTH]` (default: 14) | `--min-password-length 16` |
| `--docs-dir <path>` | Root documentation folder (default: `docs`) | `--docs-dir docs` |
| `--dry-run` | Prints planned replacements without writing to disk | `--dry-run` |
| `--list-remaining` | Scans and lists remaining bracketed placeholder tags | `--list-remaining` |

### 3. Local Preview

Start the MkDocs live-reloading development server:

```bash
uv run mkdocs serve
# (or with manual venv activation: mkdocs serve)
```

Open your browser to `http://127.0.0.1:8000` to review the rendered documentation portal.

### 4. Production Build

To verify that all internal links, anchors, and configurations are strictly valid with zero warnings:

```bash
uv run mkdocs build --strict
# (or with manual venv activation: mkdocs build --strict)
```

The compiled static site will be generated in `site/` ready for hosting on GitHub Pages, Cloudflare Pages, AWS S3/CloudFront, or any internal web server.

### 5. Automated ISMS Validation, OSCAL Export & Adoption Auditing

Run the v2.0 Compliance-as-Code verification suite:

```bash
# 1. Validate link integrity, JSON schemas, catalog integrity, drift, and 6-framework coverage
uv run python scripts/validate_isms.py --strict --coverage-report --check-drift

# 2. Export and verify deterministic NIST OSCAL v1.2.0 JSON models (dist/oscal/*.json)
uv run python scripts/export_oscal.py --validate --check

# 3. Verify or regenerate the Multi-Framework Crosswalk & OSCAL Matrix document
uv run python scripts/generate_docs.py --check

# 4. Audit framework adoption thresholds, Essential Eight ML2 maturity, review cadences & exceptions
uv run python scripts/check_adoption.py --manifest mappings/compliance_manifest.yaml --strict

# 5. Run the full 5-tier E2E and adversarial test suites
uv run python tests/e2e/run_all_tests.py
uv run python tests/test_tier5_adversarial_challenger.py
uv run python tests/test_m1_stress_challenger.py
```

---

## Harmonized Standards Summary

This template resolves common contradictions between corporate security policies and modern technical standards:

| Security Domain | Legacy / Problematic Pattern | Modern Harmonized Standard in Template |
|---|---|---|
| **Passwords** | 8–12 chars, forced complex characters, mandatory 90-day resets | **NIST SP 800-63B**: Min 14 chars (`[MIN_PASSWORD_LENGTH]`), passphrases supported, no arbitrary rotation, breach list verification |
| **MFA** | SMS or email OTP | **ASD Essential Eight ML2/ML3 & NIST SP 800-63B**: Phishing-resistant MFA (FIDO2/WebAuthn) required for all users and administrative access |
| **Endpoint & Macros** | Unmanaged local execution and enabled Office macros | **ASD Essential Eight ML2/ML3**: Workstation/server application control (`E8-AC`), internet macro blocking + AMSI inspection (`E8-OM`), browser hardening (`E8-AH`) |
| **Vulnerability SLA**| CVSS v3.x base score only; 30-day critical patching | **CVSS v4.0 + CISA KEV + EPSS + Essential Eight ML2**: **48-hour patch SLA** for critical/actively exploited vulnerabilities; fortnightly critical patching |
| **Code Review** | Vague peer review mandates | Tiered approvals: 1 approval for standard changes; **2 approvals** (including Security/CODEOWNERS) for Tier-1 production and security configurations |
| **Supply Chain** | Periodic questionnaire | Continuous verification: Software Bill of Materials (SBOM), pre-commit secret scanning, and cryptographic artifact signing (Cosign) |
| **Classification** | Manual tagging burden on users | **Default `Internal`** metadata tagging; explicit visual banners only required on `Confidential` and `Restricted` assets |
| **Incident SLAs** | Open-ended post-mortems | Post-mortems required within **5 business days** for Sev1/Sev2, **10 business days** for Sev3; multi-jurisdictional breach matrix (GDPR 72h, NIS2 24h/72h, CIRCIA 72h, SEC 4d) |
| **Media Sanitization** | Obsolete `DoD 5220.22-M` wipe | **NIST SP 800-88 Rev. 1** (Clear, Purge, Destroy) and **IEEE 2883-2022** for modern solid-state and cloud storage |
| **Log Retention** | Unspecified retention | Security/audit logs (PII masked): **90 days hot** + **365 days immutable cold archive**; debug logs: max **30 days** |
| **Access Reviews** | Ad-hoc or annual reviews | Privileged accounts reviewed **monthly** (with separate unprivileged daily-driver accounts per `E8-AP`), critical systems **quarterly**, standard access **semi-annually** |
| **Key Management** | Undefined rotation schedules | Master KMS keys rotated **annually**; TLS certificates and API secrets rotated **<= 90 days**; post-quantum cryptography (PQC) readiness (FIPS 203, FIPS 204, FIPS 205) |

---

## Framework & Domain Onboarding Architecture

To scale compliance across multiple frameworks and growing engineering domains without duplicating documentation, this template uses a **Hub-and-Spoke Canonical Control Model**:

1. **Hub**: 98 Canonical Controls defined in `mappings/framework_registry.yaml` (`CC-GV-xx`, `CC-AC-xx`, `CC-CR-xx`, etc.).
2. **Spokes**: Authoritative reference catalogs in `mappings/catalogs/*.yaml` (ISO/IEC 27001:2022, SOC 2 TSC, NIST CSF 2.0, GDPR, NIST SP 800-53 Rev. 5, ASD Essential Eight).
3. **5-Step Onboarding SOP**:
   1. Author reference catalog in `mappings/catalogs/<framework>.yaml` and register targets in `mappings/compliance_manifest.yaml`.
   2. Map to existing canonical controls with OSCAL relationships in `mappings/framework_registry.yaml`.
   3. Update implementing policies or standards in `docs/`.
   4. Regenerate `docs/01_ISMS_Framework/08_Multi_Framework_Crosswalk_and_OSCAL_Matrix.md` (`generate_docs.py --write`) and OSCAL artifacts (`export_oscal.py --validate`).
   5. Run `uv run python scripts/validate_isms.py --strict --coverage-report --check-drift` and `uv run python scripts/check_adoption.py --strict` to verify 100% coverage.

Detailed guidelines and architectural roadmaps are documented in `docs/01_ISMS_Framework/07_Framework_and_Domain_Onboarding_Guide.md` and `architecture/adr/`.

---

## Contributing

1. Create a feature branch (`git checkout -b feature/my-change`).
2. Make your documentation, mapping, or script adjustments.
3. Regenerate crosswalk and OSCAL artifacts if `mappings/framework_registry.yaml` changed (`uv run python scripts/generate_docs.py --write && uv run python scripts/export_oscal.py --validate`).
4. Verify formatting and links (`uv run mkdocs build --strict`).
5. Run compliance and adoption validation (`uv run python scripts/validate_isms.py --strict --check-drift && uv run python scripts/check_adoption.py --strict`).
6. Run the automated test suite (`uv run python tests/e2e/run_all_tests.py`).
7. Submit a pull request with an updated `Document History` table in affected files.

---

## License

This project is licensed under the Apache License 2.0. See the `LICENSE` file for details.
