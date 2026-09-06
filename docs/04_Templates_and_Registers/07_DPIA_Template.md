# Data Protection Impact Assessment (DPIA)

| Attribute | Value |
| :--- | :--- |
| **Document ID** | TMP-03 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Data Protection Officer |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | GDPR (Art. 35), ISO/IEC 27001:2022 (A.5.8), SOC 2 TSC (CC6.1) |

*(GDPR Article 35)*

**Purpose**: To systematically analyze, identify, and minimize the data protection risks of a project or system at [COMPANY_NAME].

## 1. Project / System Overview
- **Project Name**: ________________________
- **Project Owner**: ________________________
- **Assessment Date**: [INSERT_DATE]
- **Brief Description**: (Describe what the project aims to achieve and why personal data processing is necessary).

## 2. Necessity and Proportionality
- **Lawful Basis for Processing**: (e.g., Consent, Contract, Legitimate Interest)
- **Data Minimization**: How are you ensuring that only necessary data is collected?
- **Data Quality and Retention**: How will data be kept accurate and when will it be deleted?

## 3. Data Flow & Processing
- (Provide a diagram or description of how data flows into, through, and out of the system).

## 4. Risk Assessment
| Privacy Risk Identified | Likelihood | Severity | Overall Risk | Mitigating Controls / Planned Actions | Residual Risk |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Unauthorized access to DB | Medium | High | High | Enforce MFA, encrypt data at rest, strong RBAC | Low |
| Data sent to wrong recipient | Low | Medium | Low | Automated processes, manual QA steps | Low |

## 5. DPO Advice & Sign-off
- **DPO Comments / Recommendations**: ________________________
- **Approved by**: ________________________
- **Date**: ________________________

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | Information Security / Legal | [CISO_NAME] | Initial release and modernization |
