# Multi-Framework Crosswalk and OSCAL Implementation Matrix

| Attribute | Value |
| :--- | :--- |
| **Document ID** | ISMS-XW-01 |
| **Version** | 2.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Compliance Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (All 93 Annex A Controls), SOC 2 TSC (CC1–CC9, A1, C1, P1–P8), NIST CSF 2.0 (GV, ID, PR, DE, RS, RC), GDPR (Art. 5–37), NIST SP 800-53 Rev. 5 (AC–SR), ASD Essential Eight (ML1–ML3) |

## 1. Executive Overview & Multi-Framework Coverage Summary

This document serves as the authoritative multi-framework compliance crosswalk and Open Security Controls Assessment Language (**OSCAL v1.2.0**) implementation matrix for **[COMPANY_NAME]**. It is automatically generated from the machine-readable canonical control registry (`mappings/framework_registry.yaml`) and verified against the reference control catalogs in `mappings/catalogs/`.

Rather than maintaining siloed policies per regulation, **[COMPANY_NAME]** operates a centralized **Canonical Control Hub-and-Spoke** model across **98 canonical controls** spanning **14 security domains**, simultaneously satisfying six major international standards and government cybersecurity baselines:

| Framework / Standard | Version / Edition | Reference Catalog | Catalog Controls | Mapped in Registry | Target Baseline / Maturity | Audit Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ISO/IEC 27001:2022** | 2022 Annex A | `iso_27001_2022.yaml` | 93 | 93 / 93 (100.0%) | Full Annex A (93 Controls) | **COMPLIANT** |
| **AICPA SOC 2 TSC** | 2017 / 2022 | `soc2_tsc_2017.yaml` | 61 | 44 Criteria (100.0%) | Security, Availability, Confidentiality, Privacy | **COMPLIANT** |
| **NIST CSF 2.0** | v2.0 (Feb 2024) | `nist_csf_2_0.yaml` | 106 | 47 Subcategories (100.0%) | All 6 Functions (`GV`, `ID`, `PR`, `DE`, `RS`, `RC`) | **COMPLIANT** |
| **EU/UK GDPR** | 2016/679 | `gdpr.yaml` | 26 | 17 Articles (100.0%) | Articles 5–37 Privacy & Security Controls | **COMPLIANT** |
| **NIST SP 800-53 Rev. 5** | Rev. 5.1.1 | `nist_sp_800_53_rev5.yaml` | 177 | 137 Controls (20/20 Families) | Moderate Baseline (`AC` through `SR`) | **COMPLIANT** |
| **ASD Essential Eight** | Nov 2023 | `asd_essential_eight.yaml` | 24 | 24 / 24 Capabilities (8/8 Strategies) | Target **Maturity Level 2 (ML2)** + ML3 Overlays | **COMPLIANT** |

## 2. ASD Essential Eight Maturity Matrix (ML1 – ML3)

The table below maps all eight **Australian Signals Directorate (ASD) Essential Eight** mitigation strategies across Maturity Level 1 (`ML1`), Maturity Level 2 (`ML2` — organizational target baseline), and Maturity Level 3 (`ML3`), including Australian Government Information Security Manual (**ISM**) control identifiers and implementing ISMS documents:

| Mitigation Strategy | Maturity Level 1 (ML1) | Maturity Level 2 (ML2 Target) | Maturity Level 3 (ML3 Enhanced) | Mapped ASD ISM Controls | Canonical Controls | Implementing ISMS Documents |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Application Control** | **E8-AC-ML1**: Application Control on Workstations (User Profiles & Temp) | **E8-AC-ML2**: Application Control on Workstations and Servers | **E8-AC-ML3**: Cryptographic Application Whitelisting and Logging | `ISM-1582`, `ISM-1407`, `ISM-1644` | `CC-OP-02`, `CC-AU-01`, `CC-AU-06` | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md), [Asset Management Policy](../02_Policies/02_Asset_Management_Policy.md), [Acceptable Use and AI Security Policy](../02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md) |
| **Patch Applications** | **E8-PA-ML1**: Monthly Application Patching for Critical Vulnerabilities | **E8-PA-ML2**: Fortnightly Patching and 48-Hour Critical Exploit Patch SLA | **E8-PA-ML3**: Automated Scanning, 48-Hour Patching, and Unsupported Software Removal | `ISM-1657`, `ISM-1507`, `ISM-1698` | `CC-OP-07`, `CC-SD-09` | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md), [SDLC and Change Management Policy](../02_Policies/12_SDLC_and_Change_Management_Policy.md) |
| **Configure Microsoft Office Macro Settings** | **E8-OM-ML1**: Block Internet Macros from Executing | **E8-OM-ML2**: Trusted Locations and Digitally Signed Macros Only | **E8-OM-ML3**: AMSI Runtime Macro Inspection and Centralized Logging | `ISM-1484`, `ISM-1485`, `ISM-1648` | `CC-AU-01`, `CC-AU-02` | [Asset Management Policy](../02_Policies/02_Asset_Management_Policy.md), [Acceptable Use and AI Security Policy](../02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md), [Access Control Policy](../02_Policies/01_Access_Control_Policy.md) |
| **User Application Hardening** | **E8-AH-ML1**: Web Browser Hardening and Flash/Java Disabling | **E8-AH-ML2**: PowerShell Constrained Language Mode and PowerShell 2.0 Removal | **E8-AH-ML3**: Advanced PowerShell Script Block Logging and PDF Hardening | `ISM-1400`, `ISM-1662`, `ISM-1663` | `CC-OP-09`, `CC-AU-01`, `CC-AU-06` | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md), [Asset Management Policy](../02_Policies/02_Asset_Management_Policy.md), [Acceptable Use and AI Security Policy](../02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md) |
| **Restrict Administrative Privileges** | **E8-AP-ML1**: Privilege Request Validation and Web/Email Separation | **E8-AP-ML2**: Dedicated Administrative Accounts and Monthly Audits | **E8-AP-ML3**: Privileged Access Workstations (PAWs) and Credential Isolation | `ISM-0401`, `ISM-1173`, `ISM-1508` | `CC-AC-02`, `CC-AC-03`, `CC-AC-04`, `CC-AC-07` | [Access Control Policy](../02_Policies/01_Access_Control_Policy.md), [Password and Authentication Standard](../03_Standards_and_Procedures/01_Password_and_Authentication_Standard.md) |
| **Patch Operating Systems** | **E8-PO-ML1**: Monthly Operating System Patching | **E8-PO-ML2**: Fortnightly OS Patching and 48-Hour Critical Exploit Patch SLA | **E8-PO-ML3**: 48-Hour Active Exploit Patching and Unsupported OS Replacement | `ISM-1492`, `ISM-1510`, `ISM-1699` | `CC-OP-07`, `CC-SD-09` | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md), [SDLC and Change Management Policy](../02_Policies/12_SDLC_and_Change_Management_Policy.md) |
| **Multi-factor Authentication** | **E8-MF-ML1**: MFA for Remote Access and Sensitive Web Portals | **E8-MF-ML2**: Phishing-Resistant MFA and Universal Administrative MFA | **E8-MF-ML3**: Hardware-Enforced Phishing-Resistant MFA Everywhere | `ISM-1401`, `ISM-1504`, `ISM-1681` | `CC-AC-05`, `CC-AC-06` | [Access Control Policy](../02_Policies/01_Access_Control_Policy.md), [Access Review Log](../04_Templates_and_Registers/05_Access_Review_Log.md) |
| **Regular Backups** | **E8-RB-ML1**: Regular Backups of Critical Data, Software, and Config | **E8-RB-ML2**: Immutable / Offline Backups and Dedicated Backup Accounts | **E8-RB-ML3**: Annual Restoration Rehearsal and Orchestrated DR Testing | `ISM-1511`, `ISM-1512`, `ISM-1701` | `CC-OP-04`, `CC-BC-02` | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md), [Disaster Recovery Plan DRP](../03_Standards_and_Procedures/08_Disaster_Recovery_Plan_DRP.md) |

## 3. NIST SP 800-53 Rev. 5 Control Family Crosswalk (`AC` – `SR`)

All 20 **NIST SP 800-53 Revision 5** control families are mapped across the canonical control registry, providing comprehensive coverage of the NIST SP 800-53 **Moderate Baseline**:

| Family ID | Control Family Name | Catalog Controls | Mapped in Registry | Mapped NIST SP 800-53 Rev. 5 Control IDs | Mapped Canonical Controls |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AC** | Access Control | 16 | 11 | `AC-1`, `AC-2`, `AC-3`, `AC-4`, `AC-5`, `AC-6`, `AC-7`, `AC-14`, `AC-17`, `AC-19`, `AC-20` | `CC-GV-03`, `CC-AM-02`, `CC-AM-05`, `CC-AM-06`, `CC-AC-01`, `CC-AC-02`, `CC-AC-03`, `CC-AC-04`, `CC-AC-05`, `CC-AC-07`, `CC-CM-01`, `CC-CM-03`, `CC-CM-04`, `CC-SP-05`, `CC-AU-01`, `CC-AU-02`, `CC-AU-03`, `CC-AU-04` |
| **AT** | Awareness and Training | 4 | 4 | `AT-1`, `AT-2`, `AT-3`, `AT-4` | `CC-SD-07`, `CC-HR-03` |
| **AU** | Audit and Accountability | 10 | 9 | `AU-1`, `AU-2`, `AU-3`, `AU-4`, `AU-6`, `AU-8`, `AU-9`, `AU-11`, `AU-12` | `CC-OP-05`, `CC-OP-08`, `CC-CM-05`, `CC-IR-05` |
| **CA** | Assessment, Authorization, and Monitoring | 6 | 4 | `CA-1`, `CA-2`, `CA-3`, `CA-7` | `CC-GV-01`, `CC-GV-06`, `CC-AC-04`, `CC-OP-01`, `CC-OP-08`, `CC-CM-02`, `CC-SP-04`, `CC-IR-04` |
| **CM** | Configuration Management | 11 | 9 | `CM-1`, `CM-2`, `CM-3`, `CM-4`, `CM-5`, `CM-7`, `CM-8`, `CM-10`, `CM-11` | `CC-AM-01`, `CC-AC-07`, `CC-OP-02`, `CC-OP-09`, `CC-SD-05`, `CC-SD-06`, `CC-SD-09` |
| **CP** | Contingency Planning | 9 | 9 | `CP-1`, `CP-2`, `CP-3`, `CP-4`, `CP-6`, `CP-7`, `CP-8`, `CP-9`, `CP-10` | `CC-OP-04`, `CC-BC-01`, `CC-BC-02`, `CC-BC-03`, `CC-BC-04` |
| **IA** | Identification and Authentication | 9 | 7 | `IA-1`, `IA-2`, `IA-3`, `IA-4`, `IA-5`, `IA-6`, `IA-8` | `CC-AM-01`, `CC-AC-02`, `CC-AC-05`, `CC-AC-06`, `CC-CR-02` |
| **IR** | Incident Response | 8 | 5 | `IR-1`, `IR-4`, `IR-5`, `IR-6`, `IR-8` | `CC-GV-04`, `CC-IR-01`, `CC-IR-02`, `CC-IR-03`, `CC-IR-04`, `CC-IR-05`, `CC-IR-06` |
| **MA** | Maintenance | 5 | 4 | `MA-1`, `MA-2`, `MA-3`, `MA-4` | `CC-PS-08`, `CC-OP-03` |
| **MP** | Media Protection | 7 | 5 | `MP-2`, `MP-3`, `MP-5`, `MP-6`, `MP-7` | `CC-AM-03`, `CC-AM-04`, `CC-AM-05`, `CC-AM-06`, `CC-CM-06`, `CC-AU-05` |
| **PE** | Physical and Environmental Protection | 16 | 15 | `PE-1`, `PE-2`, `PE-3`, `PE-4`, `PE-5`, `PE-6`, `PE-8`, `PE-10`, `PE-11`, `PE-12`, `PE-13`, `PE-14`, `PE-15`, `PE-16`, `PE-17` | `CC-PS-01`, `CC-PS-02`, `CC-PS-03`, `CC-PS-04`, `CC-PS-05`, `CC-PS-06`, `CC-PS-07`, `CC-PS-08`, `CC-AU-03`, `CC-AU-04` |
| **PL** | Planning | 6 | 4 | `PL-1`, `PL-2`, `PL-4`, `PL-8` | `CC-GV-01`, `CC-GV-02`, `CC-AM-02`, `CC-SD-03`, `CC-HR-02`, `CC-AU-01` |
| **PM** | Program Management | 8 | 5 | `PM-1`, `PM-2`, `PM-3`, `PM-4`, `PM-16` | `CC-GV-01`, `CC-GV-02`, `CC-GV-04`, `CC-GV-05`, `CC-GV-06` |
| **PS** | Personnel Security | 8 | 8 | `PS-1`, `PS-2`, `PS-3`, `PS-4`, `PS-5`, `PS-6`, `PS-7`, `PS-8` | `CC-GV-03`, `CC-AM-03`, `CC-SP-06`, `CC-HR-01`, `CC-HR-02`, `CC-HR-04`, `CC-HR-05` |
| **PT** | PII Processing and Transparency | 5 | 5 | `PT-1`, `PT-2`, `PT-3`, `PT-4`, `PT-7` | `CC-OP-06`, `CC-CM-06`, `CC-DP-01`, `CC-DP-02`, `CC-DP-03`, `CC-DP-04` |
| **RA** | Risk Assessment | 5 | 3 | `RA-2`, `RA-3`, `RA-5` | `CC-AM-04`, `CC-OP-01`, `CC-OP-07`, `CC-SD-02`, `CC-DP-04`, `CC-AU-06` |
| **SA** | System and Services Acquisition | 9 | 7 | `SA-3`, `SA-4`, `SA-5`, `SA-8`, `SA-9`, `SA-10`, `SA-11` | `CC-GV-06`, `CC-SD-01`, `CC-SD-02`, `CC-SD-03`, `CC-SD-04`, `CC-SD-07`, `CC-SD-08`, `CC-SP-01`, `CC-SP-02`, `CC-SP-05`, `CC-DP-03`, `CC-AU-06` |
| **SC** | System and Communications Protection | 16 | 8 | `SC-1`, `SC-2`, `SC-7`, `SC-8`, `SC-10`, `SC-12`, `SC-13`, `SC-28` | `CC-AM-06`, `CC-CR-01`, `CC-CR-02`, `CC-CR-03`, `CC-OP-06`, `CC-OP-09`, `CC-CM-01`, `CC-CM-02`, `CC-CM-03`, `CC-CM-04`, `CC-CM-05`, `CC-SD-03`, `CC-DP-05`, `CC-AU-07` |
| **SI** | System and Information Integrity | 11 | 8 | `SI-1`, `SI-2`, `SI-3`, `SI-4`, `SI-5`, `SI-10`, `SI-11`, `SI-12` | `CC-GV-05`, `CC-OP-01`, `CC-OP-02`, `CC-OP-07`, `CC-SD-04`, `CC-DP-05`, `CC-IR-02`, `CC-AU-06`, `CC-AU-07` |
| **SR** | Supply Chain Risk Management | 8 | 7 | `SR-1`, `SR-2`, `SR-3`, `SR-5`, `SR-6`, `SR-8`, `SR-9` | `CC-SD-08`, `CC-SD-09`, `CC-SP-01`, `CC-SP-02`, `CC-SP-03`, `CC-SP-04`, `CC-SP-06` |

## 4. Master Canonical Control Hub-and-Spoke Crosswalk Matrix (98 Controls)

The master table below enumerates all **98 canonical controls** (`CC-GV-01` through `CC-AU-07`), their external framework spoke mappings across all six frameworks, and direct relative links to the implementing policies, standards, procedures, and evidence registers:

| Canonical ID | Domain | Control Name | ISO/IEC 27001:2022 | SOC 2 TSC | NIST CSF 2.0 | GDPR | NIST SP 800-53 Rev. 5 | ASD Essential Eight | Implementing Documents |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CC-GV-01** | Governance | Information Security Policy Framework | `A.5.1` | `CC1.1`, `CC5.3`, `CC3.1`, `CC5.1` | `GV.PO-01` | `Art. 24` | `PL-1`, `PM-1`, `CA-1` | — | [Information Security Policy](01_Information_Security_Policy.md), [ISMS Governance Audit and Improvement](06_ISMS_Governance_Audit_and_Improvement.md) |
| **CC-GV-02** | Governance | Security Roles and Responsibilities | `A.5.2` | `CC1.3` | `GV.RR-01` | `Art. 24` | `PM-2`, `PL-2` | — | [Roles and Responsibilities](04_Roles_and_Responsibilities.md) |
| **CC-GV-03** | Governance | Management Responsibilities and Leadership Commitment | `A.5.4` | `CC1.4` | `GV.RR-02` | `Art. 24` | `AC-5`, `PS-7` | — | [Roles and Responsibilities](04_Roles_and_Responsibilities.md), [ISMS Governance Audit and Improvement](06_ISMS_Governance_Audit_and_Improvement.md) |
| **CC-GV-04** | Governance | Contact with Statutory and Regulatory Authorities | `A.5.5` | `CC2.1` | `RS.CO-02` | `Art. 33`, `Art. 34` | `IR-6`, `PM-4` | — | [Incident Response Plan IRP](../03_Standards_and_Procedures/06_Incident_Response_Plan_IRP.md), [Data Breach Notification Procedure](../03_Standards_and_Procedures/09_Data_Breach_Notification_Procedure.md) |
| **CC-GV-05** | Governance | Contact with Special Interest Groups and Threat Forums | `A.5.6` | `CC2.1` | `ID.RA-02` | — | `SI-5`, `PM-16` | — | [Information Security Policy](01_Information_Security_Policy.md) |
| **CC-GV-06** | Governance | Independent Review of Information Security | `A.5.35` | `CC2.3`, `CC4.1`, `CC3.2`, `CC4.2` | `GV.OV-01` | `Art. 24` | `SA-3`, `CA-3`, `PM-3` | — | [Risk Management Methodology](03_Risk_Management_Methodology.md), [ISMS Governance Audit and Improvement](06_ISMS_Governance_Audit_and_Improvement.md), [Internal Audit and CAPA Register](../04_Templates_and_Registers/08_Internal_Audit_and_CAPA_Register.md) |
| **CC-GV-07** | Governance | Compliance with Security Policies and Technical Standards | `A.5.36` | `CC2.2`, `CC5.3`, `CC5.2` | `GV.PO-02` | `Art. 24` | — | — | [Information Security Policy](01_Information_Security_Policy.md), [ISMS Governance Audit and Improvement](06_ISMS_Governance_Audit_and_Improvement.md) |
| **CC-GV-08** | Governance | Documented Operating Procedures | `A.5.37` | `CC7.1` | `PR.PS-01` | — | — | — | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md), [ISMS Governance Audit and Improvement](06_ISMS_Governance_Audit_and_Improvement.md) |
| **CC-AM-01** | Asset Management | Information and Asset Inventory Management | `A.5.9` | `CC6.1` | `ID.AM-01`, `ID.AM-02` | `Art. 30` | `CM-8`, `IA-3` | — | [Asset Management Policy](../02_Policies/02_Asset_Management_Policy.md), [Information Asset Register](../04_Templates_and_Registers/01_Information_Asset_Register.md) |
| **CC-AM-02** | Asset Management | Return of Corporate Assets | `A.5.11` | `CC6.2` | `PR.AA-06` | — | `AC-20`, `PL-4` | — | [HR Security Policy](../02_Policies/08_HR_Security_Policy.md), [Asset Management Policy](../02_Policies/02_Asset_Management_Policy.md) |
| **CC-AM-03** | Asset Management | Information Classification | `A.5.12` | `CC6.1`, `C1.1` | `ID.AM-05` | `Art. 5` | `PS-4`, `MP-6` | — | [Asset Management Policy](../02_Policies/02_Asset_Management_Policy.md), [Data Classification and Handling Standard](../03_Standards_and_Procedures/02_Data_Classification_and_Handling_Standard.md) |
| **CC-AM-04** | Asset Management | Information Labelling and Handling | `A.5.13` | `CC6.1`, `C1.1` | `PR.DS-01` | `Art. 32` | `RA-2`, `MP-2` | — | [Data Classification and Handling Standard](../03_Standards_and_Procedures/02_Data_Classification_and_Handling_Standard.md) |
| **CC-AM-05** | Asset Management | Protection and Retention of Records | `A.5.33` | `CC6.1` | `PR.DS-11` | `Art. 5`, `Art. 30` | `MP-3`, `AC-3` | — | [Data Retention and Destruction Standard](../03_Standards_and_Procedures/03_Data_Retention_and_Destruction_Standard.md) |
| **CC-AM-06** | Asset Management | Removable and Storage Media Management | `A.7.10` | `CC6.1` | `PR.PS-03` | `Art. 32` | `SC-8`, `MP-5`, `AC-4` | — | [Data Retention and Destruction Standard](../03_Standards_and_Procedures/03_Data_Retention_and_Destruction_Standard.md) |
| **CC-AM-07** | Asset Management | Secure Media Sanitization and Equipment Disposal | `A.7.14` | `CC6.5`, `C1.2` | `PR.PS-03` | `Art. 17`, `Art. 32` | — | — | [Data Retention and Destruction Standard](../03_Standards_and_Procedures/03_Data_Retention_and_Destruction_Standard.md) |
| **CC-AC-01** | Access Control | Segregation of Duties and Conflict Avoidance | `A.5.3` | `CC6.1` | `PR.AA-01` | — | `AC-1`, `AC-3` | — | [Access Control Policy](../02_Policies/01_Access_Control_Policy.md) |
| **CC-AC-02** | Access Control | Access Control Architecture and Least Privilege | `A.5.15` | `CC6.1` | `PR.AA-01` | `Art. 32` | `AC-2`, `IA-4` | `E8-AP-ML1` | [Access Control Policy](../02_Policies/01_Access_Control_Policy.md) |
| **CC-AC-03** | Access Control | Identity Lifecycle Management and Account Provisioning | `A.5.16` | `CC6.2` | `PR.AA-02` | `Art. 32` | `AC-6`, `AC-2` | `E8-AP-ML1`, `E8-AP-ML2`, `E8-AP-ML3` | [Access Control Policy](../02_Policies/01_Access_Control_Policy.md) |
| **CC-AC-04** | Access Control | Authentication Information and NIST SP 800-63B Guidelines | `A.5.17` | `CC6.1` | `PR.AA-03` | `Art. 32` | `AC-2`, `CA-7` | `E8-AP-ML2` | [Password and Authentication Standard](../03_Standards_and_Procedures/01_Password_and_Authentication_Standard.md) |
| **CC-AC-05** | Access Control | Access Rights Review and Recertification | `A.5.18` | `CC6.2`, `CC6.3` | `PR.AA-04` | — | `IA-1`, `IA-2`, `IA-8`, `AC-7` | `E8-MF-ML1`, `E8-MF-ML2`, `E8-MF-ML3` | [Access Control Policy](../02_Policies/01_Access_Control_Policy.md), [Access Review Log](../04_Templates_and_Registers/05_Access_Review_Log.md) |
| **CC-AC-06** | Access Control | Privileged Access Management (PAM) | `A.8.2` | `CC6.3` | `PR.AA-04` | `Art. 32` | `IA-5`, `IA-6` | `E8-MF-ML1`, `E8-MF-ML2` | [Access Control Policy](../02_Policies/01_Access_Control_Policy.md) |
| **CC-AC-07** | Access Control | Information Access Restriction and Granular Authorization | `A.8.3` | `CC6.1` | `PR.AA-01` | `Art. 32` | `AC-6`, `CM-7` | `E8-AP-ML2`, `E8-AP-ML3` | [Access Control Policy](../02_Policies/01_Access_Control_Policy.md) |
| **CC-AC-08** | Access Control | Secure Authentication and Phishing-Resistant MFA | `A.8.5` | `CC6.1` | `PR.AA-03` | `Art. 32` | — | — | [Password and Authentication Standard](../03_Standards_and_Procedures/01_Password_and_Authentication_Standard.md) |
| **CC-AC-09** | Access Control | Restriction and Control of Privileged Utility Programs | `A.8.18` | `CC6.3` | `PR.AA-04` | — | — | — | [Access Control Policy](../02_Policies/01_Access_Control_Policy.md) |
| **CC-CR-01** | Cryptography | Cryptographic Controls and Key Management Lifecycle | `A.8.24` | `CC6.1`, `CC6.7` | `PR.DS-01`, `PR.DS-02` | `Art. 32` | `SC-1`, `SC-13` | — | [Cryptography Policy](../02_Policies/03_Cryptography_Policy.md) |
| **CC-CR-02** | Cryptography | Data Encryption in Transit and TLS Configuration | `A.5.14` | `CC6.6`, `CC6.7` | `PR.DS-02` | `Art. 32` | `SC-12`, `IA-3` | — | [Cryptography Policy](../02_Policies/03_Cryptography_Policy.md), [Communications Security Policy](../02_Policies/06_Communications_Security_Policy.md) |
| **CC-CR-03** | Cryptography | Post-Quantum Cryptography Readiness and Ephemeral Secrets | `A.8.24` | `CC6.7` | `PR.DS-01` | `Art. 32` | `SC-28`, `SC-12` | — | [Cryptography Policy](../02_Policies/03_Cryptography_Policy.md) |
| **CC-PS-01** | Physical Security | Physical Security Perimeters and Barriers | `A.7.1` | `CC6.4` | `PR.PS-01` | — | `PE-1`, `PE-3` | — | [Physical Security Policy](../02_Policies/04_Physical_Security_Policy.md) |
| **CC-PS-02** | Physical Security | Physical Entry Controls and Visitor Management | `A.7.2` | `CC6.4` | `PR.PS-02` | — | `PE-2`, `PE-3` | — | [Physical Security Policy](../02_Policies/04_Physical_Security_Policy.md) |
| **CC-PS-03** | Physical Security | Securing Offices, Rooms and Facilities | `A.7.3` | `CC6.4` | `PR.PS-03` | — | `PE-4`, `PE-5` | — | [Physical Security Policy](../02_Policies/04_Physical_Security_Policy.md) |
| **CC-PS-04** | Physical Security | Physical Security Monitoring and Video Surveillance | `A.7.4` | `CC6.4` | `PR.PS-04` | — | `PE-6`, `PE-2` | — | [Physical Security Policy](../02_Policies/04_Physical_Security_Policy.md) |
| **CC-PS-05** | Physical Security | Protection Against Environmental Threats | `A.7.5` | `CC6.4` | `PR.PS-05` | — | `PE-12`, `PE-13`, `PE-14`, `PE-15` | — | [Physical Security Policy](../02_Policies/04_Physical_Security_Policy.md) |
| **CC-PS-06** | Physical Security | Working in Secure Areas | `A.7.6` | `CC6.4` | `PR.PS-06` | — | `PE-5`, `PE-4` | — | [Physical Security Policy](../02_Policies/04_Physical_Security_Policy.md) |
| **CC-PS-07** | Physical Security | Equipment Siting, Placement and Protection | `A.7.8` | `CC6.4` | `PR.IR-02` | — | `PE-16` | — | [Physical Security Policy](../02_Policies/04_Physical_Security_Policy.md) |
| **CC-PS-08** | Physical Security | Supporting Utilities and Power Redundancy | `A.7.11` | `CC6.4` | `PR.PS-05` | — | `PE-8`, `PE-10`, `PE-11`, `MA-3` | — | [Physical Security Policy](../02_Policies/04_Physical_Security_Policy.md) |
| **CC-OP-01** | Operations Security | Threat Intelligence Ingestion and Risk Prioritization | `A.5.7` | `CC7.1` | `ID.RA-02` | — | `RA-3`, `SI-5`, `CA-7` | — | [Vulnerability and Patch Management Standard](../03_Standards_and_Procedures/04_Vulnerability_and_Patch_Management_Standard.md) |
| **CC-OP-02** | Operations Security | Equipment Maintenance and Servicing | `A.7.13` | `CC6.4` | `PR.PS-03` | — | `SI-1`, `SI-3`, `CM-7` | `E8-AC-ML1`, `E8-AC-ML2`, `E8-AC-ML3` | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md) |
| **CC-OP-03** | Operations Security | Capacity Management and Cloud Resource Scaling | `A.8.6` | `CC7.1` | `PR.PS-01` | — | `MA-1`, `MA-2`, `MA-4` | — | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md) |
| **CC-OP-04** | Operations Security | Malware Protection and Endpoint Detection and Response | `A.8.7` | `CC6.8` | `DE.CM-09` | `Art. 32` | `CP-9`, `CP-10` | `E8-RB-ML1`, `E8-RB-ML2`, `E8-RB-ML3` | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md) |
| **CC-OP-05** | Operations Security | Technical Vulnerability Management and Remediation SLAs | `A.8.8` | `CC7.1` | `ID.RA-01` | `Art. 32` | `AU-1`, `AU-2`, `AU-3`, `AU-6`, `AU-12` | — | [Vulnerability and Patch Management Standard](../03_Standards_and_Procedures/04_Vulnerability_and_Patch_Management_Standard.md) |
| **CC-OP-06** | Operations Security | Configuration Management and Infrastructure as Code Baselines | `A.8.9` | `CC8.1` | `PR.PS-01` | — | `SC-28`, `PT-2` | — | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md) |
| **CC-OP-07** | Operations Security | Information Backup and Immutable Storage | `A.8.13` | `CC7.5`, `A1.2` | `PR.DS-11` | `Art. 32` | `RA-5`, `SI-2` | `E8-PA-ML1`, `E8-PA-ML2`, `E8-PA-ML3`, `E8-PO-ML1`, `E8-PO-ML2`, `E8-PO-ML3` | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md) |
| **CC-OP-08** | Operations Security | Audit Logging, SIEM Aggregation and Retention | `A.8.15` | `CC7.2` | `DE.AE-03` | `Art. 32` | `AU-4`, `AU-9`, `AU-11`, `CA-2` | — | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md), [Data Retention and Destruction Standard](../03_Standards_and_Procedures/03_Data_Retention_and_Destruction_Standard.md) |
| **CC-OP-09** | Operations Security | Continuous Security Monitoring and Behavioral Anomaly Detection | `A.8.16` | `CC7.2` | `DE.CM-01` | `Art. 32` | `SC-7`, `CM-7` | `E8-AH-ML1` | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md) |
| **CC-OP-10** | Operations Security | Clock Synchronization via NTP | `A.8.17` | `CC7.2` | `PR.IR-01` | — | — | — | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md) |
| **CC-OP-11** | Operations Security | Software Installation Controls and Application Whitelisting | `A.8.19` | `CC8.1` | `PR.PS-01` | — | — | — | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md) |
| **CC-OP-12** | Operations Security | Protection of Operational Systems During Security Audits | `A.8.34` | `CC2.3` | `PR.PS-01` | — | — | — | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md) |
| **CC-CM-01** | Communications Security | Information Transfer Policies and Agreements | `A.5.14` | `CC6.6`, `CC6.7` | `PR.DS-02` | `Art. 32`, `Art. 44` | `SC-7`, `AC-4` | — | [Communications Security Policy](../02_Policies/06_Communications_Security_Policy.md) |
| **CC-CM-02** | Communications Security | Cabling Security and Telecommunications Protection | `A.7.12` | `CC6.6` | `PR.IR-01` | — | `SC-8`, `CA-3` | — | [Communications Security Policy](../02_Policies/06_Communications_Security_Policy.md) |
| **CC-CM-03** | Communications Security | Network Security Architecture and Boundary Protection | `A.8.20` | `CC6.6` | `PR.IR-01` | `Art. 32` | `SC-7`, `AC-4` | — | [Communications Security Policy](../02_Policies/06_Communications_Security_Policy.md) |
| **CC-CM-04** | Communications Security | Security of Managed Network Services and Connectivity | `A.8.21` | `CC6.6` | `PR.IR-02` | — | `AC-17`, `SC-10` | — | [Communications Security Policy](../02_Policies/06_Communications_Security_Policy.md) |
| **CC-CM-05** | Communications Security | Network Segregation, VPC Isolation and Micro-segmentation | `A.8.22` | `CC6.6` | `PR.IR-03` | `Art. 32` | `SC-8`, `AU-8` | — | [Communications Security Policy](../02_Policies/06_Communications_Security_Policy.md) |
| **CC-CM-06** | Communications Security | Web Filtering, DNS Security and Anti-Phishing Controls | `A.8.23` | `CC6.6` | `PR.PS-01` | — | `MP-6`, `PT-3` | — | [Communications Security Policy](../02_Policies/06_Communications_Security_Policy.md) |
| **CC-SD-01** | Secure Development | Security in Project Management and Agile Lifecycles | `A.5.8` | `CC8.1` | `PR.PS-06` | `Art. 25` | `SA-3`, `SA-8` | — | [SDLC and Change Management Policy](../02_Policies/12_SDLC_and_Change_Management_Policy.md) |
| **CC-SD-02** | Secure Development | Intellectual Property Rights and Source Code Licensing | `A.5.32` | `CC6.1` | `PR.DS-01` | — | `SA-4`, `SA-5`, `RA-3` | — | [SDLC and Change Management Policy](../02_Policies/12_SDLC_and_Change_Management_Policy.md) |
| **CC-SD-03** | Secure Development | Access Control to Source Code Repositories | `A.8.4` | `CC8.1` | `PR.PS-06` | — | `SA-8`, `SC-2`, `PL-8` | — | [SDLC and Change Management Policy](../02_Policies/12_SDLC_and_Change_Management_Policy.md) |
| **CC-SD-04** | Secure Development | Secure Development Lifecycle Governance | `A.8.25` | `CC8.1` | `PR.PS-06` | `Art. 25` | `SA-11`, `SI-10`, `SI-11` | — | [SDLC and Change Management Policy](../02_Policies/12_SDLC_and_Change_Management_Policy.md) |
| **CC-SD-05** | Secure Development | Application Security Requirements and Threat Modeling | `A.8.26` | `CC8.1` | `PR.PS-06` | `Art. 25` | `CM-2`, `CM-5` | — | [Secure Coding Standard](../03_Standards_and_Procedures/05_Secure_Coding_Standard.md) |
| **CC-SD-06** | Secure Development | Secure System Architecture and Engineering Principles | `A.8.27` | `CC8.1` | `PR.PS-06` | `Art. 25` | `CM-1`, `CM-3`, `CM-4` | — | [SDLC and Change Management Policy](../02_Policies/12_SDLC_and_Change_Management_Policy.md) |
| **CC-SD-07** | Secure Development | Secure Coding Standards and Peer Code Review | `A.8.28` | `CC8.1` | `PR.PS-06` | `Art. 25` | `SA-10`, `AT-3` | — | [Secure Coding Standard](../03_Standards_and_Procedures/05_Secure_Coding_Standard.md) |
| **CC-SD-08** | Secure Development | Automated Security Testing in CI/CD (SAST, DAST, SCA) | `A.8.29` | `CC8.1` | `PR.PS-06` | `Art. 25` | `SA-4`, `SR-3` | — | [SDLC and Change Management Policy](../02_Policies/12_SDLC_and_Change_Management_Policy.md) |
| **CC-SD-09** | Secure Development | Separation of Development, Test and Production Environments | `A.8.31` | `CC8.1` | `PR.PS-06` | `Art. 32` | `SR-1`, `SR-8`, `CM-10`, `CM-11` | `E8-PA-ML2`, `E8-PA-ML3`, `E8-PO-ML2` | [SDLC and Change Management Policy](../02_Policies/12_SDLC_and_Change_Management_Policy.md) |
| **CC-SD-10** | Secure Development | Change Management and Release Governance | `A.8.32` | `CC8.1` | `PR.PS-01` | — | — | — | [SDLC and Change Management Policy](../02_Policies/12_SDLC_and_Change_Management_Policy.md) |
| **CC-SD-11** | Secure Development | Test Data Protection and Synthetic Data Generation | `A.8.33` | `CC8.1` | `PR.PS-06` | `Art. 25`, `Art. 32` | — | — | [SDLC and Change Management Policy](../02_Policies/12_SDLC_and_Change_Management_Policy.md) |
| **CC-SP-01** | Supplier Management | Supplier Security Policy and Risk Management | `A.5.19` | `CC9.2` | `GV.SC-04` | `Art. 28` | `SA-9`, `SR-1` | — | [Supplier Security Policy](../02_Policies/07_Supplier_Security_Policy.md), [Vendor Risk Assessment Template](../04_Templates_and_Registers/04_Vendor_Risk_Assessment_Template.md) |
| **CC-SP-02** | Supplier Management | Supplier Security Agreements, SLAs and DPAs | `A.5.20` | `CC9.2` | `GV.SC-06` | `Art. 28` | `SA-4`, `SR-3` | — | [Supplier Security Policy](../02_Policies/07_Supplier_Security_Policy.md) |
| **CC-SP-03** | Supplier Management | ICT Supply Chain Security and Software Bill of Materials (SBOM) | `A.5.21` | `CC9.2` | `GV.SC-07` | — | `SR-2`, `SR-5`, `SR-6` | — | [Supplier Security Policy](../02_Policies/07_Supplier_Security_Policy.md) |
| **CC-SP-04** | Supplier Management | Supplier Service Monitoring, Audits and Review | `A.5.22` | `CC9.2` | `GV.SC-08` | `Art. 28` | `CA-7`, `SR-6` | — | [Supplier Security Policy](../02_Policies/07_Supplier_Security_Policy.md), [Vendor Risk Assessment Template](../04_Templates_and_Registers/04_Vendor_Risk_Assessment_Template.md) |
| **CC-SP-05** | Supplier Management | Cloud Services Security Governance and Shared Responsibility | `A.5.23` | `CC6.6`, `CC9.2` | `PR.DS-01` | `Art. 28` | `SA-9`, `AC-20` | — | [Operations Security Policy](../02_Policies/05_Operations_Security_Policy.md), [Supplier Security Policy](../02_Policies/07_Supplier_Security_Policy.md) |
| **CC-SP-06** | Supplier Management | Outsourced Software Development Governance | `A.8.30` | `CC9.2` | `GV.SC-07` | `Art. 28` | `PS-4`, `SR-9` | — | [Supplier Security Policy](../02_Policies/07_Supplier_Security_Policy.md) |
| **CC-HR-01** | Human Resources | Personnel Screening and Background Checks | `A.6.1` | `CC1.2` | `PR.AT-01` | — | `PS-1`, `PS-2`, `PS-3` | — | [HR Security Policy](../02_Policies/08_HR_Security_Policy.md) |
| **CC-HR-02** | Human Resources | Terms and Conditions of Employment | `A.6.2` | `CC1.1` | `PR.AT-01` | — | `PS-6`, `PL-4` | — | [HR Security Policy](../02_Policies/08_HR_Security_Policy.md) |
| **CC-HR-03** | Human Resources | Security Awareness, Training and Phishing Simulations | `A.6.3` | `CC2.2` | `PR.AT-02` | `Art. 39` | `AT-1`, `AT-2`, `AT-4` | — | [HR Security Policy](../02_Policies/08_HR_Security_Policy.md), [ISMS Governance Audit and Improvement](06_ISMS_Governance_Audit_and_Improvement.md) |
| **CC-HR-04** | Human Resources | Disciplinary Process for Security Policy Violations | `A.6.4` | `CC1.1`, `CC1.5` | `PR.AT-01` | — | `PS-8` | — | [HR Security Policy](../02_Policies/08_HR_Security_Policy.md) |
| **CC-HR-05** | Human Resources | Responsibilities After Termination or Change of Employment | `A.6.5` | `CC6.2` | `PR.AA-06` | — | `PS-4`, `PS-5` | — | [HR Security Policy](../02_Policies/08_HR_Security_Policy.md) |
| **CC-HR-06** | Human Resources | Confidentiality and Non-Disclosure Agreements | `A.6.6` | `CC1.1` | `PR.AT-01` | — | — | — | [HR Security Policy](../02_Policies/08_HR_Security_Policy.md) |
| **CC-DP-01** | Data Privacy | Legal, Statutory, Regulatory and Contractual Compliance | `A.5.31` | `CC2.1` | `GV.OC-03` | `Art. 5`, `Art. 6` | `PT-1`, `PT-2` | — | [Context of the Organization](02_Context_of_the_Organization.md), [Data Privacy and Protection Policy](../02_Policies/09_Data_Privacy_and_Protection_Policy.md) |
| **CC-DP-02** | Data Privacy | Privacy and Protection of Personally Identifiable Information (PII) | `A.5.34` | `P1.1`, `P2.1`, `P3.1`, `P4.1`, `P5.1`, `P6.1`, `P7.1`, `P8.1` | `PR.DS-10` | `Art. 5`, `Art. 6`, `Art. 9`, `Art. 12`, `Art. 15`, `Art. 25`, `Art. 35`, `Art. 37` | `PT-3` | — | [Data Privacy and Protection Policy](../02_Policies/09_Data_Privacy_and_Protection_Policy.md), [RoPA Template](../04_Templates_and_Registers/06_RoPA_Template.md), [DPIA Template](../04_Templates_and_Registers/07_DPIA_Template.md) |
| **CC-DP-03** | Data Privacy | Information Deletion and Right to Erasure | `A.8.10` | `CC6.5`, `P4.1` | `PR.DS-11` | `Art. 17` | `PT-4`, `SA-8` | — | [Data Retention and Destruction Standard](../03_Standards_and_Procedures/03_Data_Retention_and_Destruction_Standard.md), [Data Privacy and Protection Policy](../02_Policies/09_Data_Privacy_and_Protection_Policy.md) |
| **CC-DP-04** | Data Privacy | Data Masking, Pseudonymization and Anonymization | `A.8.11` | `CC6.1`, `C1.1` | `PR.DS-01` | `Art. 25`, `Art. 32` | `PT-7`, `RA-3` | — | [Data Privacy and Protection Policy](../02_Policies/09_Data_Privacy_and_Protection_Policy.md) |
| **CC-DP-05** | Data Privacy | Data Leakage Prevention (DLP) and Exfiltration Safeguards | `A.8.12` | `CC6.7`, `C1.1` | `PR.DS-01` | `Art. 32` | `SC-7`, `SI-12` | — | [Data Classification and Handling Standard](../03_Standards_and_Procedures/02_Data_Classification_and_Handling_Standard.md) |
| **CC-IR-01** | Incident Management | Incident Management Planning, Roles and CSIRT Playbooks | `A.5.24` | `CC7.3` | `RS.MA-01` | `Art. 33` | `IR-1`, `IR-8` | — | [Incident Management Policy](../02_Policies/10_Incident_Management_Policy.md), [Incident Response Plan IRP](../03_Standards_and_Procedures/06_Incident_Response_Plan_IRP.md) |
| **CC-IR-02** | Incident Management | Assessment and Classification of Security Events | `A.5.25` | `CC7.3` | `RS.AN-03` | `Art. 33` | `IR-4`, `SI-4` | — | [Incident Management Policy](../02_Policies/10_Incident_Management_Policy.md) |
| **CC-IR-03** | Incident Management | Incident Containment, Eradication and Response | `A.5.26` | `CC7.3` | `RS.MA-01` | `Art. 33` | `IR-4`, `IR-5` | — | [Incident Response Plan IRP](../03_Standards_and_Procedures/06_Incident_Response_Plan_IRP.md) |
| **CC-IR-04** | Incident Management | Post-Incident Review, Root Cause Analysis and Lessons Learned | `A.5.27` | `CC7.3` | `RS.AN-03` | — | `IR-4`, `CA-7` | — | [Incident Management Policy](../02_Policies/10_Incident_Management_Policy.md), [Security Incident Log](../04_Templates_and_Registers/03_Security_Incident_Log.md) |
| **CC-IR-05** | Incident Management | Collection and Preservation of Forensic Evidence | `A.5.28` | `CC7.4` | `RS.AN-07` | — | `AU-9`, `IR-5` | — | [Incident Response Plan IRP](../03_Standards_and_Procedures/06_Incident_Response_Plan_IRP.md) |
| **CC-IR-06** | Incident Management | Security Event and Anomaly Reporting | `A.6.8` | `CC7.3` | `DE.AE-02` | `Art. 33` | `IR-6` | — | [Incident Management Policy](../02_Policies/10_Incident_Management_Policy.md) |
| **CC-BC-01** | Business Continuity | Information Security During Disruption and Emergency Operations | `A.5.29` | `CC7.5`, `A1.1` | `RC.RP-01` | `Art. 32` | `CP-1`, `CP-2` | — | [Business Continuity Policy](../02_Policies/11_Business_Continuity_Policy.md), [Business Continuity Plan BCP](../03_Standards_and_Procedures/07_Business_Continuity_Plan_BCP.md) |
| **CC-BC-02** | Business Continuity | ICT Readiness for Business Continuity and Disaster Recovery | `A.5.30` | `CC7.5`, `CC9.1`, `A1.2` | `RC.RP-02` | `Art. 32` | `CP-6`, `CP-7`, `CP-8` | `E8-RB-ML1`, `E8-RB-ML2`, `E8-RB-ML3` | [Disaster Recovery Plan DRP](../03_Standards_and_Procedures/08_Disaster_Recovery_Plan_DRP.md) |
| **CC-BC-03** | Business Continuity | Redundancy of Processing Facilities and High Availability | `A.8.14` | `CC7.5`, `A1.3` | `PR.IR-04` | `Art. 32` | `CP-3`, `CP-4` | — | [Business Continuity Policy](../02_Policies/11_Business_Continuity_Policy.md), [Disaster Recovery Plan DRP](../03_Standards_and_Procedures/08_Disaster_Recovery_Plan_DRP.md) |
| **CC-BC-04** | Business Continuity | Business Impact Analysis and Recovery Objectives (RTO/RPO) | `A.5.29`, `A.5.30` | `A1.1` | `RC.RP-01` | `Art. 32` | `CP-2`, `CP-10` | — | [Business Continuity Policy](../02_Policies/11_Business_Continuity_Policy.md), [Business Continuity Plan BCP](../03_Standards_and_Procedures/07_Business_Continuity_Plan_BCP.md) |
| **CC-AU-01** | Acceptable Use | Acceptable Use of Corporate IT Assets | `A.5.10` | `CC6.1` | `PR.AA-01` | — | `PL-4`, `AC-20` | `E8-AC-ML1`, `E8-AC-ML2`, `E8-OM-ML1`, `E8-OM-ML2`, `E8-OM-ML3`, `E8-AH-ML1`, `E8-AH-ML2`, `E8-AH-ML3` | [Asset Management Policy](../02_Policies/02_Asset_Management_Policy.md), [Acceptable Use and AI Security Policy](../02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md) |
| **CC-AU-02** | Acceptable Use | Teleworking and Remote Working Controls | `A.6.7` | `CC6.6`, `CC6.7` | `PR.AA-05` | — | `AC-19`, `AC-20` | `E8-OM-ML1`, `E8-OM-ML2` | [Access Control Policy](../02_Policies/01_Access_Control_Policy.md), [Acceptable Use and AI Security Policy](../02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md) |
| **CC-AU-03** | Acceptable Use | Clear Desk and Clear Screen Controls | `A.7.7` | `CC6.1` | `PR.AA-06` | — | `AC-14`, `PE-5` | — | [Physical Security Policy](../02_Policies/04_Physical_Security_Policy.md), [Acceptable Use and AI Security Policy](../02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md) |
| **CC-AU-04** | Acceptable Use | Security of Off-Premises Corporate Assets | `A.7.9` | `CC6.4` | `PR.PS-01` | — | `AC-17`, `PE-17` | — | [Asset Management Policy](../02_Policies/02_Asset_Management_Policy.md), [Acceptable Use and AI Security Policy](../02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md) |
| **CC-AU-05** | Acceptable Use | User Endpoint Security, Full Disk Encryption and MDM | `A.8.1` | `CC6.1` | `PR.AA-05` | `Art. 32` | `MP-7` | — | [Asset Management Policy](../02_Policies/02_Asset_Management_Policy.md), [Acceptable Use and AI Security Policy](../02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md) |
| **CC-AU-06** | Acceptable Use | Generative AI, Large Language Models and Machine Learning Governance | `A.5.10`, `A.8.1`, `A.8.23` | `CC6.1`, `CC6.6` | `GV.PO-01`, `PR.PS-01` | `Art. 25` | `RA-3`, `SI-3`, `SA-8` | `E8-AC-ML2`, `E8-AH-ML2` | [Acceptable Use and AI Security Policy](../02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md) |
| **CC-AU-07** | Acceptable Use | AI Data Protection, Prompt Security and Shadow AI Prohibition | `A.5.1`, `A.5.10`, `A.8.12` | `CC6.1`, `CC6.7` | `PR.DS-01`, `PR.AT-01` | `Art. 25`, `Art. 32` | `SC-7`, `SI-12` | — | [Acceptable Use and AI Security Policy](../02_Policies/13_Acceptable_Use_and_AI_Security_Policy.md) |

## 5. OSCAL v1.2.0 Machine-Readable Export Artifacts

To support automated GRC ingestion, continuous compliance monitoring, and audit evidence exchange, `scripts/export_oscal.py` compiles `mappings/framework_registry.yaml` into five deterministic **NIST OSCAL v1.2.0** JSON artifacts using RFC 4122 UUIDv5 identifiers:

| OSCAL v1.2.0 Model | Generated Artifact Path | Root JSON Key | Purpose & Audit Role |
| :--- | :--- | :--- | :--- |
| **OSCAL Catalog** | `dist/oscal/catalog.json` | `catalog` | Exports all 14 ISMS control domains as OSCAL groups and all 98 canonical controls (`CC-XX-YY`) with mapped framework properties and document links. |
| **OSCAL Mapping Collection** | `dist/oscal/mapping_collection.json` | `mapping-collection` | Exports fine-grained relationship mappings (`equivalent-to`, `subset-of`, `superset-of`, `intersects-with`) across all 6 target frameworks. |
| **OSCAL Profile (Essential Eight ML2)** | `dist/oscal/profile_e8_ml2.json` | `profile` | Selects the canonical controls satisfying the ASD Essential Eight Maturity Level 2 (`ML2`) target baseline. |
| **OSCAL Profile (NIST 800-53 Moderate)** | `dist/oscal/profile_nist_800_53_moderate.json` | `profile` | Selects the canonical controls satisfying the NIST SP 800-53 Rev. 5 Moderate baseline across all 20 control families (`AC`–`SR`). |
| **OSCAL Component Definition** | `dist/oscal/component_definition.json` | `component-definition` | Maps the repository policy/procedure components and CLI validation scripts to the canonical controls they implement and verify. |

### Verification & Regeneration Commands

```bash
# Regenerate and validate all 5 OSCAL v1.2.0 JSON models
python scripts/export_oscal.py --validate

# Verify deterministic OSCAL artifacts match the current registry (CI gate)
python scripts/export_oscal.py --validate --check

# Regenerate this crosswalk document from mappings/framework_registry.yaml
python scripts/generate_docs.py --write

# Verify zero documentation drift between registry and this crosswalk document
python scripts/generate_docs.py --check
```

## 6. Related Documents

- [Statement of Applicability (SoA)](05_Statement_of_Applicability_SoA.md)
- [Framework and Domain Onboarding Guide](07_Framework_and_Domain_Onboarding_Guide.md)
- [ISMS Governance, Audit, and Continual Improvement](06_ISMS_Governance_Audit_and_Improvement.md)
- [Risk Management Methodology](03_Risk_Management_Methodology.md)

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 2.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Automated multi-framework crosswalk and OSCAL v1.2.0 implementation matrix |
