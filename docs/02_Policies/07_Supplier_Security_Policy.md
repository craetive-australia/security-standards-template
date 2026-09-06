# Supplier Security Policy

| Attribute | Value |
| :--- | :--- |
| **Document ID** | POL-07 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Procurement Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.5.19, A.5.20, A.5.21, A.5.22, A.8.30), SOC 2 TSC (CC9.2), NIST CSF 2.0 (GV.SC-04, GV.SC-06, GV.SC-07, GV.SC-08), GDPR (Art. 28) |

## 1. Purpose
To define strict risk management and technical requirements for third-party suppliers, vendors, and partners who process [COMPANY_NAME] data or interface with its systems. *(ISO/IEC 27001:2022 A.5.19, SOC 2 CC9.2, NIST CSF 2.0 GV.SC-04)*

## 2. Scope
Applies to all external parties (SaaS providers, contractors, hosting facilities) that handle, process, store, or transmit [COMPANY_NAME] data.

## 3. Policy Statements

### 3.1 Supplier Security Assessments and TPRM
* **Certification Requirement:** Critical and high-risk suppliers must provide proof of an active SOC 2 Type II report or ISO 27001 certification prior to onboarding.
* **Annual Reviews:** A formalized Third-Party Risk Management (TPRM) platform must be used to conduct and track annual security questionnaires (e.g., SIG Core or CAIQ) for all critical vendors. *(ISO/IEC 27001:2022 A.5.20, SOC 2 CC9.2, NIST CSF 2.0 GV.SC-06)*

### 3.2 Contractual Security Requirements
* **Data Processing Agreements (DPA):** All vendors processing PII must sign a DPA enforcing compliance with GDPR/CCPA.
* **Breach Notification:** Contracts must stipulate a mandatory Service Level Agreement (SLA) requiring the vendor to notify [COMPANY_NAME] of any security breach within 24 hours of discovery. *(ISO/IEC 27001:2022 A.5.20, A.5.24, SOC 2 CC9.2, NIST CSF 2.0 GV.SC-06, RS.MA-01)*

### 3.3 Access Control for Suppliers
* **Isolated Access:** Vendor access to internal systems must be provisioned via dedicated, isolated VPN profiles or a vendor Privileged Access Management (PAM) solution, restricted to the exact IP ranges and ports required.
* **Time-Bound Access:** Supplier credentials must automatically expire at the end of the contract term or require documented renewal every 90 days. *(ISO/IEC 27001:2022 A.5.18, A.5.22, SOC 2 CC6.1, CC9.2, NIST CSF 2.0 PR.AA-04, GV.SC-08)*

### 3.4 Monitoring and Review
* **Continuous Monitoring:** The security posture of critical vendors must be continuously monitored using external threat intelligence platforms (e.g., SecurityScorecard, BitSight). *(ISO/IEC 27001:2022 A.5.22, SOC 2 CC9.2, NIST CSF 2.0 GV.SC-08)*

## 4. Roles and Responsibilities
- **[CISO_NAME] / Security Team:** Responsible for defining TPRM standards, reviewing supplier risk questionnaires, and approving vendor security risk acceptances.
- **Procurement Team:** Ensuring DPAs, security SLAs, and right-to-audit clauses are legally executed before issuing purchase orders or signing contracts.
- **Vendor Relationship Owners**: Responsible for tracking vendor performance, reviewing annual SOC 2 reports, and notifying IT of vendor contract terminations.
- **Suppliers and Contractors**: Mandated to adhere to contractual security terms and report security incidents within 24 hours.

## 5. Compliance and Exceptions
- **Compliance:** All third parties engaging with [COMPANY_NAME] systems or sensitive data must undergo formal security review. Unassessed vendors will not be approved for procurement or technical integration.
- **Exceptions:** If a business-critical vendor cannot provide an independent SOC 2 Type II or ISO 27001 certification, a formal exception must be documented in the [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md) under the Security Exception & Risk Acceptance Log with compensating technical controls (e.g., client-side encryption, air-gapped sandboxing) and approved by the [CISO_NAME].

## 6. Related Documents
- [Vendor Risk Assessment Template](../04_Templates_and_Registers/04_Vendor_Risk_Assessment_Template.md)
- [Access Control Policy](01_Access_Control_Policy.md)
- [Information Security Policy](../01_ISMS_Framework/01_Information_Security_Policy.md)
- [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md)

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Initial release and harmonization |
