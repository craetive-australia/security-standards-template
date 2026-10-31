# Welcome to the [COMPANY_NAME] ISMS

This repository contains the Information Security Management System (ISMS) documentation, policies, procedures, and templates for **[COMPANY_NAME]**.

Our ISMS is engineered on a **Compliance-as-Code** architecture aligned with six major regulatory and cybersecurity frameworks—**ISO/IEC 27001:2022** (all 93 Annex A controls), **AICPA SOC 2 TSC**, **NIST CSF 2.0**, **EU/UK GDPR**, **NIST SP 800-53 Rev. 5** (Moderate Baseline), and the **ASD Essential Eight** (Maturity Levels 1–3)—ensuring the Confidentiality, Integrity, and Availability of our information assets.

## How to Use This Repository

This documentation is generated using [MkDocs](https://www.mkdocs.org/) with the Material theme and backed by a machine-readable canonical control registry (`mappings/framework_registry.yaml`) with deterministic **NIST OSCAL v1.2.0** JSON export.

### Customizing the Templates

All documents contain placeholders such as `[COMPANY_NAME]`, `[CISO_NAME]`, and `[INSERT_DATE]`. You can manually replace these or use the provided script to batch replace them:

```bash
python scripts/fill_placeholders.py --company-name "Acme Corp" --ciso-name "Jane Doe" --insert-date "2026-10-31"
```

### Viewing Locally

To view the documentation locally, ensure you have Python installed, then run:

```bash
pip install -r requirements.txt
mkdocs serve
```
Navigate to `http://127.0.0.1:8000/` in your browser.

### Automated Compliance Verification & OSCAL Export

```bash
# Validate links, schemas, catalog integrity, and 6-framework coverage
python scripts/validate_isms.py --strict --coverage-report --check-drift

# Audit compliance adoption targets, review cadences, and active exceptions
python scripts/check_adoption.py --manifest mappings/compliance_manifest.yaml --strict

# Export and validate deterministic NIST OSCAL v1.2.0 JSON models
python scripts/export_oscal.py --validate --check
```

## Structure

- **ISMS Framework**: Governance, risk methodology, [Statement of Applicability (SoA)](01_ISMS_Framework/05_Statement_of_Applicability_SoA.md), [Framework & Domain Onboarding Guide](01_ISMS_Framework/07_Framework_and_Domain_Onboarding_Guide.md), and the [Multi-Framework Crosswalk & OSCAL Matrix](01_ISMS_Framework/08_Multi_Framework_Crosswalk_and_OSCAL_Matrix.md).
- **Policies**: High-level directives from management (e.g., Information Security Policy, Access Control Policy).
- **Procedures & Standards**: Step-by-step instructions and technical baselines for security operations (e.g., Password & Authentication Standard, Vulnerability Management, Incident Response Plan).
- **Templates and Registers**: Operational logs and templates for risk assessments, assets, incidents, and audits.

## Responsibilities

Security is everyone's responsibility. Please review the policies applicable to your role. For any questions, contact the Security Team or the CISO.
