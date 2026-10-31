# ADR-003: ASD Essential Eight (ML1–ML3) and NIST SP 800-53 Rev. 5 Moderate Baseline Integration

- **Status**: Accepted
- **Date**: 2026-10-31
- **Deciders**: Chief Information Security Officer (CISO), Compliance Engineering, Security Operations
- **Technical Context**: Multi-Framework Expansion, Defense-in-Depth Baselines, FedRAMP & ACSC Alignment

## Context and Problem Statement

The initial release (v1.0) of `security-standards-template` established comprehensive crosswalks across four foundational frameworks:
1. ISO/IEC 27001:2022 Annex A
2. AICPA SOC 2 (2017/2022 Trust Services Criteria)
3. NIST Cybersecurity Framework (CSF) 2.0
4. European Union General Data Protection Regulation (GDPR)

While this met the baseline requirements for commercial SaaS audits, modern enterprise customers, regulated industries, defense supply chain partners, and government entities demand alignment with two rigorous government-backed cybersecurity standards:
- **Australian Signals Directorate (ASD) Essential Eight**: Mandated for Australian government departments, critical infrastructure entities, and defense suppliers under the Protective Security Policy Framework (PSPF) and Information Security Manual (ISM).
- **NIST Special Publication 800-53 Rev. 5 (Security and Privacy Controls for Information Systems and Organizations)**: The definitive US federal catalog mandated for FedRAMP authorizations, Department of Defense (DoD) supply chains (CMMC Level 2/3), and federal agency civilian systems.

Expanding the repository to cover these frameworks requires a formal architectural model for multi-tier maturity levels (Essential Eight ML1, ML2, ML3), comprehensive catalog family coverage (NIST 800-53 families AC through SR at the Moderate baseline), and semantic mapping relationships.

## Decision Drivers

- Provide ready-to-audit compliance coverage for Australian government (ACSC Essential Eight) and US Federal/FedRAMP (NIST 800-53 Rev. 5 Moderate baseline).
- Represent progressive maturity requirements (ML1, ML2, ML3) in machine-readable catalogs and compliance manifests.
- Map all 20 NIST SP 800-53 Rev. 5 control families (`AC`–`SR`) covering at least 85 distinct controls.
- Provide explicit, quantitative thresholds in policies and operational standards (e.g., 48-hour patching SLAs for actively exploited vulnerabilities, mandatory phishing-resistant MFA, Office macro hardening).
- Support formal OSCAL mapping relationship semantics (`equivalent-to`, `subset-of`, `superset-of`, `intersects-with`).

## Considered Options

1. **Standalone Framework Overlays**: Maintain separate policy documents and catalogs for Essential Eight and NIST 800-53.
   - *Risk*: Causes severe documentation fragmentation, duplicate policies, and unmanageable maintenance overhead.
2. **Text-Only Citations**: Mention Essential Eight and NIST 800-53 in document headers without structured catalog modeling or automated validation.
   - *Risk*: Fails machine-readable audit requirements, cannot generate OSCAL profiles, and lacks automated coverage validation.
3. **Canonical Control Hub-and-Spoke Integration with Machine-Readable Catalogs**: Author authoritative reference catalogs (`asd_essential_eight.yaml` and `nist_sp_800_53_rev5.yaml`), map them to the 98 canonical controls in `mappings/framework_registry.yaml`, and enforce target baselines via `mappings/compliance_manifest.yaml`.

## Decision Outcome

Chosen option: **Option 3 — Canonical Control Hub-and-Spoke Integration with Machine-Readable Catalogs**.

### Key Architectural Provisions

1. **Authoritative Reference Catalogs (`mappings/catalogs/`)**:
   - `asd_essential_eight.yaml`: Models all 8 mitigation strategies across Maturity Levels 1, 2, and 3, defining 24 discrete capability identifiers (`E8-AC-ML1..3` through `E8-RB-ML1..3`) and linking to mapped ASD Information Security Manual (ISM) control IDs.
   - `nist_sp_800_53_rev5.yaml`: Models controls across all 20 families (`AC` through `SR`), establishing an authoritative reference dictionary for the Moderate baseline (encompassing >= 85 distinct controls).

2. **Semantic Relationship Mapping**:
   In `mappings/framework_registry.yaml`, mappings support both simple string identifiers and enriched semantic relationship objects conforming to OSCAL mapping conventions:
   - `equivalent-to`: Direct functional equivalence between the canonical control and the framework requirement.
   - `subset-of`: The framework requirement covers a subset of the canonical control.
   - `superset-of`: The framework requirement encompasses broader obligations than the canonical control.
   - `intersects-with`: Partial overlap requiring complementary controls.

3. **Baseline Adoption Target in Compliance Manifest (`mappings/compliance_manifest.yaml`)**:
   - **ASD Essential Eight Target**: Configured at **Maturity Level 2 (ML2)** across all 8 strategies.
   - **NIST SP 800-53 Rev. 5 Target**: Configured at the **Moderate Baseline** (`target_baseline: "Moderate"`).

4. **Harmonized Technical Thresholds**:
   Repository policies and standards reflect explicit Essential Eight ML2/ML3 technical controls:
   - *Application Control*: Executable and script control on workstations and servers (`05_Operations_Security_Policy.md`).
   - *Office Macros*: Internet-origin macros blocked; only signed macros from trusted locations permitted (`13_Acceptable_Use_and_AI_Security_Policy.md`).
   - *User Application Hardening*: Web browsers block untrusted extensions; PowerShell constrained language mode enforced (`05_Operations_Security_Policy.md`).
   - *Patching SLAs*: Critical vulnerabilities with active exploits (CISA KEV / EPSS > 0.36) patched within **48 hours**; non-exploited criticals within 14 days (`04_Vulnerability_and_Patch_Management_Standard.md`).
   - *Authentication & Privilege Separation*: Phishing-resistant MFA (FIDO2/WebAuthn) for remote and administrative access; dedicated admin accounts barred from internet/email (`01_Password_and_Authentication_Standard.md`).

## Pros and Cons of the Selected Option

### Pros
- **Expansive Regulatory Coverage**: Single ISMS repository satisfies ISO 27001, SOC 2, NIST CSF 2.0, GDPR, NIST 800-53 Rev. 5 Moderate, and ASD Essential Eight ML2.
- **Automated OSCAL Export**: Enables automated generation of `profile_e8_ml2.json` and `profile_nist_800_53_moderate.json`.
- **Rigorous Technical Standards**: Eliminates ambiguous policy language with quantifiable technical requirements.

### Cons
- **Higher Implementation Rigor**: Demands stricter administrative and technical controls from adopting organizations.
- **Schema Complexity**: Registry schema must validate expanded mapping arrays and semantic relationship objects.

## References

- ASD Essential Eight Maturity Model (ACSC, November 2023): <https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight>
- Australian Government Information Security Manual (ISM): <https://www.cyber.gov.au/resources-business-and-government/ism>
- NIST SP 800-53 Rev. 5: Security and Privacy Controls for Information Systems and Organizations: <https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final>
- NIST SP 800-53B: Control Baselines for Information Systems and Organizations: <https://csrc.nist.gov/publications/detail/sp/800-53b/final>
