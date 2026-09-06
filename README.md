# Information Security Management System (ISMS) — Standards Template

[![Standard: ISO/IEC 27001:2022](https://img.shields.io/badge/ISO%2FIEC%2027001-2022%20Aligned-blue.svg)](https://www.iso.org/standard/27001)
[![Standard: SOC 2 Type II](https://img.shields.io/badge/AICPA%20SOC%202-2017%2F2022%20TSC-green.svg)](https://www.aicpa.org/soc4so)
[![Standard: NIST CSF 2.0](https://img.shields.io/badge/NIST%20CSF-2.0-orange.svg)](https://www.nist.gov/cyberframework)
[![Standard: GDPR](https://img.shields.io/badge/EU%20GDPR-Compliant-darkblue.svg)](https://gdpr.eu/)
[![Built with MkDocs Material](https://img.shields.io/badge/Docs-MkDocs%20Material-teal.svg)](https://squidfunk.github.io/mkdocs-material/)

A production-grade, audit-ready **Compliance-as-Code** Information Security Management System (ISMS) documentation template. Designed for modern engineering organizations, cloud-native technology companies, and regulated enterprises that maintain their governance and security policies in version control.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture & Directory Structure](#architecture--directory-structure)
- [Prerequisites & Setup](#prerequisites--setup)
- [Quickstart Guide](#quickstart-guide)
  - [1. Virtual Environment Setup](#1-virtual-environment-setup)
  - [2. Automated Placeholder Population](#2-automated-placeholder-population)
  - [3. Local Preview](#3-local-preview)
  - [4. Production Build](#4-production-build)
  - [5. Automated ISMS Validation & Coverage](#5-automated-isms-validation--coverage)
- [Harmonized Standards Summary](#harmonized-standards-summary)
- [Framework & Domain Onboarding Architecture](#framework--domain-onboarding-architecture)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Maintaining security policies in fragmented word processor files or disparate wiki pages leads to policy drift, out-of-date citations, internal contradictions, and painful audit cycles.

This repository implements a **Compliance-as-Code** model:
- **Canonical Control Hub-and-Spoke**: Core organizational requirements are defined once in canonical controls and mapped across external regulatory frameworks (ISO/IEC 27001:2022, SOC 2 TSC, NIST CSF 2.0, and GDPR).
- **Audit-Ready Documentation**: Every policy, standard, and template includes standardized metadata headers, revision histories, defined roles, exception workflows, and cross-references.
- **Automated Tooling**: Includes CLI utilities to populate organizational placeholders and validate policy syntax, cross-references, and framework coverage before committing.
- **Modern Documentation Portal**: Powered by MkDocs Material with dark/light mode toggles, instant navigation, search indexing, and rich callout extensions.

---

## Key Features

- **ISO/IEC 27001:2022 Annex A Coverage**: Full 93-control Statement of Applicability (SoA) covering Organizational (37), People (8), Physical (14), and Technological (34) controls.
- **Multi-Framework Alignment**: Pre-mapped to AICPA SOC 2 (Trust Services Criteria CC1–CC9, Availability, Confidentiality, Privacy), NIST CSF 2.0 (Govern, Identify, Protect, Detect, Respond, Recover), and GDPR.
- **NIST SP 800-63B Authentication**: Passphrase support, 14-character minimum length (`[MIN_PASSWORD_LENGTH]`), credential stuffing defense, no arbitrary expiration, and phishing-resistant MFA (FIDO2/WebAuthn).
- **Modern DevSecOps & Supply Chain**: Multi-tier pull request review gates, Software Bill of Materials (SBOM), secret scanning in CI/CD, and cryptographic artifact signing (Sigstore/Cosign).
- **Clear Incident & Breach SLAs**: Severity-driven incident classification with strict post-mortem timelines and multi-jurisdictional breach notification timelines (GDPR 72h, NIS2 24h/72h, CIRCIA 72h, SEC 4 days).
- **Modern Media Sanitization**: Fully aligned with NIST SP 800-88 Rev. 1 (Clear, Purge, Destroy) and IEEE 2883-2022, replacing deprecated DoD standards.

---

## Architecture & Directory Structure

```
security-standards-template/
├── .gitignore                      # Git ignore rules for build artifacts, venv, caches
├── pyproject.toml                  # Python project specification and dependencies for uv / pip
├── requirements.txt                # Pinned Python dependencies for build tooling
├── README.md                       # Repository guide and usage documentation
├── mkdocs.yml                      # MkDocs Material configuration with modern theme & nav
├── docs/
│   ├── index.md                    # ISMS portal homepage and executive overview
│   ├── 01_ISMS_Framework/          # Governance, context, risk, SoA, and onboarding
│   │   ├── 01_Information_Security_Policy.md
│   │   ├── 02_Context_of_the_Organization.md
│   │   ├── 03_Risk_Management_Methodology.md
│   │   ├── 04_Roles_and_Responsibilities.md
│   │   ├── 05_Statement_of_Applicability_SoA.md
│   │   ├── 06_ISMS_Governance_Audit_and_Improvement.md
│   │   └── 07_Framework_and_Domain_Onboarding_Guide.md
│   ├── 02_Policies/                # Mandatory organizational policies
│   │   ├── 01_Access_Control_Policy.md
│   │   ├── 02_Asset_Management_Policy.md
│   │   ├── 03_Cryptography_Policy.md
│   │   ├── 04_Physical_Security_Policy.md
│   │   ├── 05_Operations_Security_Policy.md
│   │   ├── 06_Communications_Security_Policy.md
│   │   ├── 07_Supplier_Security_Policy.md
│   │   ├── 08_HR_Security_Policy.md
│   │   ├── 09_Data_Privacy_and_Protection_Policy.md
│   │   ├── 10_Incident_Management_Policy.md
│   │   ├── 11_Business_Continuity_Policy.md
│   │   ├── 12_SDLC_and_Change_Management_Policy.md
│   │   └── 13_Acceptable_Use_and_AI_Security_Policy.md
│   ├── 03_Standards_and_Procedures/ # Operational technical standards and SOPs
│   │   ├── 01_Password_and_Authentication_Standard.md
│   │   ├── 02_Data_Classification_and_Handling_Standard.md
│   │   ├── 03_Data_Retention_and_Destruction_Standard.md
│   │   ├── 04_Vulnerability_and_Patch_Management_Standard.md
│   │   ├── 05_Secure_Coding_Standard.md
│   │   ├── 06_Incident_Response_Plan_IRP.md
│   │   ├── 07_Business_Continuity_Plan_BCP.md
│   │   ├── 08_Disaster_Recovery_Plan_DRP.md
│   │   └── 09_Data_Breach_Notification_Procedure.md
│   └── 04_Templates_and_Registers/ # Operational registers and audit templates
│       ├── 01_Information_Asset_Register.md
│       ├── 02_Risk_Register.md
│       ├── 03_Security_Incident_Log.md
│       ├── 04_Vendor_Risk_Assessment_Template.md
│       ├── 05_Access_Review_Log.md
│       ├── 06_RoPA_Template.md
│       ├── 07_DPIA_Template.md
│       └── 08_Internal_Audit_and_CAPA_Register.md
├── mappings/
│   └── framework_registry.yaml     # Machine-readable canonical control mapping database
└── scripts/
    ├── fill_placeholders.py        # Automated placeholder replacement & discovery tool
    └── validate_isms.py            # Automated link, citation, and coverage validator
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
  --insert-date "2026-10-26" \
  --dry-run

# 2. Apply replacements across docs/ and mkdocs.yml
uv run python scripts/fill_placeholders.py \
  --company-name "Acme Corporation" \
  --ciso-name "Jane Doe" \
  --author-name "Security Engineering Team" \
  --dpo-name "Alex Rivera" \
  --insert-date "2026-10-26"

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
| `--insert-date <str>` | Replaces `[INSERT_DATE]` | `--insert-date "2026-10-26"` |
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

### 5. Automated ISMS Validation & Coverage

Run the automated ISMS compliance validator:

```bash
# Validate link integrity, SoA 93-control completeness, and header/footer metadata
uv run python scripts/validate_isms.py --strict

# Generate framework coverage report (ISO 27001:2022, SOC 2, NIST CSF 2.0, GDPR)
uv run python scripts/validate_isms.py --coverage-report

# Run full E2E test suite
uv run python tests/e2e/run_all_tests.py
```

---

## Harmonized Standards Summary

This template resolves common contradictions between corporate security policies and modern technical standards:

| Security Domain | Legacy / Problematic Pattern | Modern Harmonized Standard in Template |
|---|---|---|
| **Passwords** | 8–12 chars, forced complex characters, mandatory 90-day resets | **NIST SP 800-63B**: Min 14 chars (`[MIN_PASSWORD_LENGTH]`), passphrases supported, no arbitrary rotation, breach list verification |
| **MFA** | SMS or email OTP | Phishing-resistant MFA (FIDO2/WebAuthn) or number-matching push required for all corporate access |
| **Code Review** | Vague peer review mandates | Tiered approvals: 1 approval for standard changes; **2 approvals** (including Security/CODEOWNERS) for Tier-1 production and security configurations |
| **Supply Chain** | Periodic questionnaire | Continuous verification: Software Bill of Materials (SBOM), pre-commit secret scanning, and cryptographic artifact signing (Cosign) |
| **Classification** | Manual tagging burden on users | **Default `Internal`** metadata tagging; explicit visual banners only required on `Confidential` and `Restricted` assets |
| **Incident SLAs** | Open-ended post-mortems | Post-mortems required within **5 business days** for Sev1/Sev2, **10 business days** for Sev3; multi-jurisdictional breach matrix (GDPR 72h, NIS2 24h/72h, CIRCIA 72h, SEC 4d) |
| **Media Sanitization** | Obsolete `DoD 5220.22-M` wipe | **NIST SP 800-88 Rev. 1** (Clear, Purge, Destroy) and **IEEE 2883-2022** for modern solid-state and cloud storage |
| **Log Retention** | Unspecified retention | Security/audit logs (PII masked): **90 days hot** + **365 days immutable cold archive**; debug logs: max **30 days** |
| **Access Reviews** | Ad-hoc or annual reviews | Privileged accounts reviewed **monthly**, critical systems **quarterly**, standard access **semi-annually** |
| **Vulnerability SLA**| CVSS v3.x base score only | Triage incorporates **CVSS v4.0**, **CISA KEV** (Known Exploited Vulnerabilities), and **EPSS** probability percentiles |
| **Key Management** | Undefined rotation schedules | Master KMS keys rotated **annually**; TLS certificates and API secrets rotated **≤90 days**; post-quantum cryptography (PQC) readiness |

---

## Framework & Domain Onboarding Architecture

To scale compliance across multiple frameworks and growing engineering domains without duplicating documentation, this template uses a **Hub-and-Spoke Canonical Control Model**:

1. **Hub**: Canonical Controls defined in `mappings/framework_registry.yaml` (`CC-GV-xx`, `CC-AC-xx`, `CC-CR-xx`, etc.).
2. **Spokes**: External framework controls (e.g., ISO 27001:2022, SOC 2 TSC, NIST CSF 2.0, GDPR, PCI DSS v4.0.1, HIPAA, CIS Controls v8.1).
3. **5-Step Onboarding SOP**:
   1. Ingest new framework controls into `mappings/framework_registry.yaml`.
   2. Map to existing canonical controls or define new canonical controls.
   3. Update implementing policies or standards in `docs/`.
   4. Update Statement of Applicability or dedicated crosswalk register.
   5. Run `uv run python scripts/validate_isms.py --coverage-report` to verify 100% coverage.

Detailed guidelines and architectural roadmaps are documented in `docs/01_ISMS_Framework/07_Framework_and_Domain_Onboarding_Guide.md`.

---

## Contributing

1. Create a feature branch (`git checkout -b feature/my-change`).
2. Make your documentation or script adjustments.
3. Verify formatting and links (`uv run mkdocs build --strict`).
4. Run compliance validation (`uv run python scripts/validate_isms.py --strict`).
5. Run the automated test suite (`uv run python tests/e2e/run_all_tests.py`).
6. Submit a pull request with an updated `Document History` table in affected files.

---

## License

This project is licensed under the Apache License 2.0. See the `LICENSE` file for details.