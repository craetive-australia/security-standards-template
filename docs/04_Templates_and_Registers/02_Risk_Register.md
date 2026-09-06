# Risk Register

| Attribute | Value |
| :--- | :--- |
| **Document ID** | REG-02 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Risk Manager |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (6.1.2, 6.1.3), SOC 2 TSC (CC3.1, CC3.2), NIST CSF 2.0 (ID.RA-01) |

*(ISO/IEC 27001:2022 6.1.2, 6.1.3; SOC 2 CC3.1, CC3.2; NIST CSF 2.0 ID.RA-01)*

## 1. Information Security Risk Register

**Purpose**: To document, track, and manage information security risks identified within [COMPANY_NAME].

**Instructions**:
- **Likelihood & Impact**: Scored 1 (Low) to 5 (High) per the [Risk Management Methodology](../01_ISMS_Framework/03_Risk_Management_Methodology.md).
- **Risk Score**: Likelihood × Impact (Scale 1–25).
- **Treatment Plan**: Accept, Mitigate, Transfer, or Avoid.

| Risk ID | Date Identified | Description | Asset Affected | Threat/Vulnerability | Likelihood | Impact | Risk Score | Treatment Plan | Owner | Target Date | Residual Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| RR-001 | [INSERT_DATE] | Unauthorized access to DB | AST-001 | Weak access controls / Credential stuffing | 3 | 5 | 15 | Mitigate: Implement MFA and IP allowlisting | [CISO_NAME] | YYYY-MM-DD | 3 (Low) |
| RR-002 | [INSERT_DATE] | Source code leak | AST-003 | Insider threat / Misconfigured repo | 2 | 4 | 8 | Mitigate: Enforce branch protections and audit logs | VPE | YYYY-MM-DD | 2 (Low) |

## 2. Security Exception and Risk Acceptance Log

Any deviation from approved security policies, standards, or architectural guidelines requires a formalized Security Exception and Risk Acceptance record approved by [CISO_NAME]. Exceptions are granted on a time-limited basis and must mandate robust compensating controls and an explicit expiration date.

| Exception ID | Date Requested | Requestor | Policy / Standard Ref | Justification & Risk Description | Compensating Controls | Expiration Date | Approval Status | Approved By |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| EXC-001 | [INSERT_DATE] | DevOps Lead | POL-01 / STD-01 | Legacy reporting service unable to support FIDO2 MFA | Network isolation via private VPC, strict IP allowlisting, and enhanced SIEM alerting | [INSERT_DATE + 90 DAYS] | Approved | [CISO_NAME] |
| EXC-002 | [INSERT_DATE] | Data Science Lead | POL-02 / STD-02 | Unsanitized training dataset retention beyond standard 30-day window | Air-gapped cloud storage with KMS encryption, access restricted to named researchers | [INSERT_DATE + 60 DAYS] | Approved | [CISO_NAME] |

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | Information Security | [CISO_NAME] | Initial release and modernization with Security Exception & Risk Acceptance Log |
