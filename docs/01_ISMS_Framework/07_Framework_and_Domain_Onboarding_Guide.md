# Framework and Domain Onboarding Guide

| Attribute | Value |
| :--- | :--- |
| **Document ID** | ISMS-GD-01 |
| **Version** | 2.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Compliance Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (Clause 4.1, 4.2, 4.3), SOC 2 TSC (CC1.1, CC2.1), NIST CSF 2.0 (GV.OC-01, GV.PO-01), GDPR (Art. 24), NIST SP 800-53 Rev. 5 (PM-1, PL-2), ASD Essential Eight (ML1–ML3) |

## 1. Overview and Architecture
This guide defines [COMPANY_NAME]'s Compliance-as-Code onboarding architecture and operational roadmap for rapidly expanding the Information Security Management System (ISMS) across emerging regulatory frameworks and security domains.

### 1.1 Canonical Control Hub-and-Spoke Model
Rather than maintaining siloed, duplicated policies for each audit framework (e.g. ISO 27001, SOC 2, NIST CSF, NIST SP 800-53, ASD Essential Eight), [COMPANY_NAME] employs a centralized **Canonical Control Hub-and-Spoke** architecture:
- **Canonical Control Hub (`CC-XX-YY`):** Internal, unified controls (`98` canonical controls) representing the organization's definitive operational security mandates across 14 domains (`GV`, `AM`, `AC`, `CR`, `PS`, `OP`, `CS`, `SR`, `HR`, `DP`, `IR`, `BC`, `SD`, `AU`) defined in `mappings/framework_registry.yaml` (`schema_version: "2.0.0"`).
- **Authoritative External Framework Spokes (`mappings/catalogs/`):** Machine-verified mappings from canonical controls to six reference control catalogs (`iso_27001_2022.yaml`, `soc2_tsc_2017.yaml`, `nist_csf_2_0.yaml`, `gdpr.yaml`, `nist_sp_800_53_rev5.yaml`, and `asd_essential_eight.yaml`) with explicit OSCAL v1.2.0 relationship semantics (`equivalent-to`, `subset-of`, `superset-of`, `intersects-with`).
- **Deterministic OSCAL v1.2.0 Export Layer (`scripts/export_oscal.py`):** Compiles the canonical control registry into five deterministic NIST OSCAL v1.2.0 JSON models (`catalog.json`, `mapping_collection.json`, `profile_e8_ml2.json`, `profile_nist_800_53_moderate.json`, `component_definition.json`) validated against `schemas/oscal_v1_2_0_subset.schema.json`.
- **Repository Implementing Layer:** Direct linkages to the authoritative Markdown policies, standards, procedures, and evidence registers within `docs/`, summarized in the automatically generated [Multi-Framework Crosswalk and OSCAL Implementation Matrix](08_Multi_Framework_Crosswalk_and_OSCAL_Matrix.md).

```mermaid
flowchart LR
    subgraph Frameworks["External Control Frameworks (Spokes)"]
        ISO["ISO/IEC 27001:2022 (93 Controls)"]
        SOC2["AICPA SOC 2 TSC (2017/2022)"]
        GDPR["GDPR / Privacy Laws"]
        NIST["NIST CSF 2.0 & SP 800-53 Rev. 5"]
        E8["ASD Essential Eight (ML1–ML3)"]
        SECTOR["Sector Frameworks (PCI DSS 4.0.1, HIPAA, NIS2, DORA, ISO 42001)"]
    end

    subgraph Hub["Canonical Control Registry & Tooling (Hub)"]
        CATS["mappings/catalogs/*.yaml"]
        YAML["mappings/framework_registry.yaml (v2.0)"]
        VAL["scripts/validate_isms.py & check_adoption.py"]
        OSCAL["scripts/export_oscal.py (OSCAL v1.2.0)"]
        GENDOC["scripts/generate_docs.py"]
    end

    subgraph Docs["4-Tier ISMS Documentation"]
        T1["Tier 1: ISMS Framework, SoA & Crosswalk (01_ISMS_Framework)"]
        T2["Tier 2: Domain Policies (02_Policies)"]
        T3["Tier 3: Technical Standards & Playbooks (03_Standards_and_Procedures)"]
        T4["Tier 4: Operational Evidence Registers (04_Templates_and_Registers)"]
    end

    Frameworks --> CATS --> YAML
    YAML --> VAL
    YAML --> OSCAL
    YAML --> GENDOC --> T1
    VAL --> T1
    T1 --> T2
    T2 --> T3
    T3 --> T4
```

## 2. 5-Step SOP for Onboarding New Control Frameworks
When expanding compliance scope to integrate a new standard (e.g., CIS Controls v8.1, PCI DSS v4.0.1, HIPAA Security Rule, EU NIS2/DORA, or ISO/IEC 42001):

```mermaid
flowchart TD
    S1["Step 1: Ingest Reference Catalog\nCreate mappings/catalogs/<framework>.yaml & validate against schemas/catalog.schema.json"]
    S2["Step 2: Crosswalk to Canonical Controls\nMap external controls with OSCAL relationships in mappings/framework_registry.yaml"]
    S3["Step 3: Automated Gap & Adoption Audit\nRun validate_isms.py --coverage-report & check_adoption.py --strict"]
    S4{"Step 4: Classify & Remediate Gaps"}
    S4A["Type A: Parameter Tightening\n(e.g., 48h critical exploit patch SLA, phishing-resistant MFA)\n-> Update 03_Standards threshold"]
    S4B["Type B: Control Extension\n(New clause in existing domain)\n-> Add section to 02_Policies / 03_Standards"]
    S4C["Type C: Net-New Security Domain\n(e.g., AI Governance, Physical CDE)\n-> Execute 4-Tier Domain Onboarding"]
    S5["Step 5: Regenerate Crosswalk, Export OSCAL & Validate Build\nRun generate_docs.py --write, export_oscal.py --validate & mkdocs build --strict"]

    S1 --> S2 --> S3 --> S4
    S4 -->|"Threshold Delta"| S4A
    S4 -->|"Sub-Control Gap"| S4B
    S4 -->|"New Domain"| S4C
    S4A --> S5
    S4B --> S5
    S4C --> S5
```

### Step 1: Framework Intake and Reference Catalog Authoring
- Author an authoritative reference catalog in `mappings/catalogs/<framework>.yaml` conforming to `schemas/catalog.schema.json`.
- Register the framework adoption targets and minimum coverage thresholds in `mappings/compliance_manifest.yaml`.

### Step 2: Gap Analysis & Canonical Mapping
- Map each external requirement against existing canonical controls in `mappings/framework_registry.yaml` using structured OSCAL relationship semantics (`equivalent-to`, `subset-of`, `superset-of`, `intersects-with`).
- Identify unmapped or partially met controls ("spokes without hubs") and classify every delta into one of three remediation types:

| Gap Type | Description | Example | Required Action |
| :--- | :--- | :--- | :--- |
| **Type A: Parameter Tightening** | Control exists in the ISMS, but the new framework mandates a stricter numeric threshold or cadence. | ASD Essential Eight ML2 requiring 48-hour patching for critical actively exploited vulnerabilities; PCI DSS v4.0.1 requiring 90-day inactive account disablement. | Tighten the baseline threshold in `03_Standards_and_Procedures/` to the **"Strictest Common Denominator" (Watermarking)** or add a tiered parameter row. |
| **Type B: Control Extension** | Requirement fits naturally within an existing ISMS policy domain but adds a new sub-clause. | ASD Essential Eight Microsoft Office macro blocking and browser hardening under Operations Security (`05_Operations_Security_Policy.md`). | Add a numbered subsection (`3.x`) to the existing policy/standard and map it in `mappings/framework_registry.yaml`. |
| **Type C: Net-New Security Domain** | Framework introduces an entirely new domain not covered by an existing policy. | AI Management System (`ISO/IEC 42001`), Cardholder Data Environment (`PCI DSS`), or OT/IoT Security. | Execute the **4-Tier Security Domain Onboarding Pattern** in Section 3 below. |

### Step 3: Policy and Standard Authoring / Amendment
- Amend existing policies or author new domain standards to fulfill identified control gaps.
- Ensure all new documents incorporate standardized Document Control Header Tables and Document History Tables.

### Step 4: Statement of Applicability, Crosswalk & OSCAL Generation
- Update the [Statement of Applicability (SoA)](05_Statement_of_Applicability_SoA.md) if ISO/IEC 27001:2022 controls are affected.
- Run `python scripts/generate_docs.py --write` to regenerate the [Multi-Framework Crosswalk and OSCAL Implementation Matrix](08_Multi_Framework_Crosswalk_and_OSCAL_Matrix.md).
- Run `python scripts/export_oscal.py --validate` to regenerate the deterministic NIST OSCAL v1.2.0 JSON artifacts in `dist/oscal/`.

### Step 5: Automated Verification and CI Gate
- Execute `python scripts/validate_isms.py --strict --coverage-report --check-drift`, `python scripts/check_adoption.py --manifest mappings/compliance_manifest.yaml --strict`, and `mkdocs build --strict` to verify link integrity, nav parity, schema validity, and 100% control mapping.

## 3. 4-Tier Pattern for Onboarding New Security Domains
When introducing a new technical domain (e.g., Artificial Intelligence / LLM Security, Cloud-Native Container Security, OT/IoT Security), every domain must be onboarded across all four ISMS tiers so management intent, technical baselines, and audit evidence remain coupled:

| ISMS Tier | Directory | Artifact to Create / Update | Purpose & Audit Role |
| :--- | :--- | :--- | :--- |
| **Tier 1: Governance & Risk** | `docs/01_ISMS_Framework/` | [Context of the Organization](02_Context_of_the_Organization.md), [Roles and Responsibilities](04_Roles_and_Responsibilities.md), [Statement of Applicability (SoA)](05_Statement_of_Applicability_SoA.md), and [Multi-Framework Crosswalk](08_Multi_Framework_Crosswalk_and_OSCAL_Matrix.md) | Defines why the domain is in scope, who owns it, and how its controls map to the SoA and external frameworks. |
| **Tier 2: Policy ("What & Why")** | `docs/02_Policies/` | `NN_<Domain>_Security_Policy.md` (e.g., [Acceptable Use and AI Security Policy](../02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md)) | High-level management mandate (technology-agnostic, reviewed annually). |
| **Tier 3: Standard / Procedure ("How & Thresholds")** | `docs/03_Standards_and_Procedures/` | `NN_<Domain>_Standard.md` or `NN_<Domain>_Procedure.md` | Measurable technical baselines, SLAs, architecture rules, and step-by-step runbooks. |
| **Tier 4: Register / Template ("Audit Evidence")** | `docs/04_Templates_and_Registers/` | `NN_<Domain>_Register.md` or extend [Information Asset Register](../04_Templates_and_Registers/01_Information_Asset_Register.md) / [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md) | Captures recurring operational records required by external auditors. |

## 4. 3-Horizon Compliance Roadmap

| Horizon | Timeline | Objectives & Overlap | Target Frameworks & Domains |
| :--- | :--- | :--- | :--- |
| **Horizon 1 (Core Baseline)** | Implemented (v1.0 Baseline) | Foundation ISMS with full CI/CD validation, 93-control SoA, AI Acceptable Use, and Internal Audit/CAPA governance. | **ISO/IEC 27001:2022**, **AICPA SOC 2 (2017/2022 TSC)**, **NIST CSF 2.0**, **EU/UK GDPR**, **NIST SP 800-63B & 800-88 Rev. 1** |
| **Horizon 2 (Federal & Cyber Resilience)** | Implemented (v2.0 Release) | Federal control catalog alignment, endpoint application control, macro blocking, 48h critical exploit patch SLAs, and NIST OSCAL v1.2.0 export. | **NIST SP 800-53 Rev. 5 (Moderate Baseline)**, **ASD Essential Eight (ML1–ML3)**, **NIST OSCAL v1.2.0** |
| **Horizon 3 (Sector & Specialized)** | Modular Opt-In Packs | Sector-specific and specialized management system overlays (`docs/05_Sector_Modules/`). | **CIS Controls v8.1**, **ISO/IEC 42001:2023 & NIST AI RMF**, **ISO/IEC 27701 (PIMS)**, **PCI DSS v4.0.1**, **HIPAA**, **EU NIS2 & DORA** |

## 5. Related Documents
- [Multi-Framework Crosswalk and OSCAL Implementation Matrix](08_Multi_Framework_Crosswalk_and_OSCAL_Matrix.md)
- [Statement of Applicability (SoA)](05_Statement_of_Applicability_SoA.md)
- [ISMS Governance, Audit, and Continual Improvement](06_ISMS_Governance_Audit_and_Improvement.md)
- [Risk Management Methodology](03_Risk_Management_Methodology.md)
- [Acceptable Use and AI Security Policy](../02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md)

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Initial release and harmonization |
| 2.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Upgraded to v2.0 6-framework architecture with NIST SP 800-53 Rev. 5, ASD Essential Eight ML1–ML3, and OSCAL v1.2.0 export pipeline |
