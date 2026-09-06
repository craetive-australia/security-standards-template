# Data Breach Notification Procedure

| Attribute | Value |
| :--- | :--- |
| **Document ID** | SOP-04 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Data Protection Officer |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.5.24, A.5.26), SOC 2 TSC (CC7.3), NIST CSF 2.0 (RS.MA-01, RS.CO-02), GDPR (Art. 33, 34) |

## 1. Purpose
To define the mandatory procedures for identifying, escalating, assessing, and notifying regulatory authorities, affected customers, and data subjects in the event of a confirmed or suspected personal data breach or material cybersecurity incident involving systems operated by [COMPANY_NAME].

## 2. Scope
This procedure applies to all personal data, confidential customer records, and sensitive business information processed, stored, or transmitted across [COMPANY_NAME] infrastructure, applications, and third-party vendor integrations.

## 3. Incident Severity, Post-Mortem SLAs, and Escalation
*(ISO/IEC 27001:2022 A.5.24, A.5.26, A.5.28)*

Upon detecting a potential breach, the Incident Commander and Data Protection Officer (DPO) must immediately triage the incident. Following containment and recovery:
- **Severity 1 (Critical) & Severity 2 (High) Incidents:** The root-cause investigation, corrective action plan, and formal post-mortem report must be published within **5 business days** of incident closure.
- **Severity 3 (Medium) Incidents:** The post-mortem report must be completed and logged within **10 business days** of incident closure.
- All incidents and notifications must be formally recorded in the [Security Incident Log](../04_Templates_and_Registers/03_Security_Incident_Log.md).

## 4. Multi-Jurisdictional Breach Notification Matrix

When a breach involves personal data or critical infrastructure, [COMPANY_NAME] must comply with the statutory notification timelines defined in the multi-jurisdiction matrix below:

| Jurisdiction / Regulation | Regulatory Authority | Trigger Threshold | Regulatory Notification Deadline | Individual / Data Subject Notification Deadline |
| :--- | :--- | :--- | :--- | :--- |
| **EU GDPR** | Lead Supervisory Authority (SA) | Risk to the rights and freedoms of natural persons | Within **72 hours** of becoming aware | Without undue delay where a high risk to rights and freedoms is identified |
| **UK GDPR & DPA 2018** | Information Commissioner's Office (ICO) | Risk to the rights and freedoms of individuals | Within **72 hours** of becoming aware | Without undue delay where high risk exists |
| **EU NIS2 Directive** | National CSIRT / Competent Authority | Significant incident affecting essential or important entities | **Early warning within 24 hours**; Incident notification within **72 hours**; Final report within 1 month | Without undue delay if incident is likely to adversely affect service provision |
| **US CIRCIA** | CISA (Cybersecurity & Infrastructure Security Agency) | Covered cyber incident affecting critical infrastructure; or ransom payment | Within **72 hours** for covered cyber incidents; within **24 hours** for ransom payments | Per applicable state or sector-specific rules |
| **US SEC Rules** | Securities and Exchange Commission (SEC) | Material cybersecurity incident (publicly traded entities) | Form 8-K Item 1.05 within **4 business days** after determining materiality | Public filing disclosure |
| **US State Laws (CCPA / CPRA)** | California Privacy Protection Agency / AG & Residents | Unauthorized acquisition of unencrypted personal information | Most expedient time possible and without unreasonable delay | Without unreasonable delay (typically within 30 to 45 calendar days) |
| **Australia Privacy Act (NDB Scheme)** | OAIC (Office of the Australian Information Commissioner) | Eligible data breach likely to result in serious harm | As soon as practicable within **30 calendar days** of initiating assessment | As soon as practicable to notify affected individuals |

## 5. Notification Content Requirements
Regulatory and data subject notifications must contain, at minimum:
1. Nature of the security incident and categories of affected records/individuals.
2. Contact details of the Data Protection Officer or incident lead.
3. Likely consequences and assessed impact of the breach.
4. Mitigation, containment, and remediation measures undertaken or planned.
5. Recommended protective actions that affected individuals can take (e.g., credential resets, credit monitoring).

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | Information Security / Legal | [CISO_NAME] | Initial release and harmonization with 5-day post-mortem SLA and 7-jurisdiction breach notification matrix |
