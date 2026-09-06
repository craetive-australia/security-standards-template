# Human Resources Security Policy

| Attribute | Value |
| :--- | :--- |
| **Document ID** | POL-08 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / People Operations Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.5.11, A.6.1, A.6.2, A.6.3, A.6.4, A.6.5, A.6.6), SOC 2 TSC (CC1.1, CC1.2, CC2.2, CC6.2), NIST CSF 2.0 (PR.AT-01, PR.AT-02, PR.AA-06), GDPR (Art. 24, 29, 32) |

## 1. Purpose
To ensure that all employees, contractors, and third-party users are vetted, trained, and effectively managed to minimize insider threats and human-error vulnerabilities. *(ISO/IEC 27001:2022 A.6.1, A.6.2, A.6.3, A.6.4, A.6.5, A.6.6, SOC 2 CC1.1, CC1.2, NIST CSF 2.0 PR.AT-01)*

## 2. Scope
Applies to all prospective and current employees, contractors, temporary staff, and third-party users of [COMPANY_NAME].

## 3. Policy Statements

### 3.1 Prior to Employment
* **Comprehensive Screening:** Criminal background, employment history, and education verification checks must be completed by a designated third-party background screening service for all new hires prior to their start date. *(ISO/IEC 27001:2022 A.6.1, SOC 2 CC1.2, NIST CSF 2.0 PR.AT-01)*
* **NDAs and Contracts:** All personnel must sign a Non-Disclosure Agreement (NDA) and an Acceptable Use Policy acknowledgment before accessing any corporate systems. *(ISO/IEC 27001:2022 A.6.2, A.6.6, SOC 2 CC1.1, NIST CSF 2.0 PR.AT-01)*

### 3.2 During Employment
* **Security Awareness Training:** Mandatory security awareness training must be completed within 14 days of hire and annually thereafter. Training must include modules on secure coding (for engineering), data privacy, and social engineering. *(ISO/IEC 27001:2022 A.6.3, SOC 2 CC2.2, NIST CSF 2.0 PR.AT-02)*
* **Phishing Simulations:** Unannounced phishing simulations must be conducted monthly. Personnel failing multiple simulations must undergo mandatory remedial training.
* **Disciplinary Process:** Information security policy violations will trigger a formal disciplinary process, up to and including termination and legal action. *(ISO/IEC 27001:2022 A.6.4, SOC 2 CC1.1, NIST CSF 2.0 PR.AT-01)*

### 3.3 Termination and Change of Employment
* **Automated Offboarding:** IT must employ automated workflows integrated with the HRIS system to immediately revoke all SSO, VPN, and physical badge access upon the precise time of termination. *(ISO/IEC 27001:2022 A.6.5, A.5.18, SOC 2 CC6.2, NIST CSF 2.0 PR.AA-06)*
* **Asset Recovery:** IT is responsible for locking remote endpoints immediately and enforcing the return of all hardware assets via prepaid shipping methods. *(ISO/IEC 27001:2022 A.5.11, SOC 2 CC6.2, NIST CSF 2.0 PR.AA-06)*

## 4. Roles and Responsibilities
- **[CISO_NAME]**: Defines security awareness curricula, establishes phishing simulation schedules, and reviews significant insider threat incidents.
- **People Operations (HR) Lead**: Enforces pre-employment screening, coordinates NDA signatures, and initiates automated offboarding triggers in the HRIS.
- **Hiring Managers**: Ensures newly hired personnel complete required onboarding training within 14 days and monitors contractor access requirements.
- **All Personnel**: Mandated to complete annual awareness training, participate in simulated phishing tests, and protect company confidentiality post-employment.

## 5. Compliance and Exceptions
- **Compliance:** Completion of annual security awareness training is a condition of ongoing employment (target: 100% completion across all active personnel). Failure to complete training within required timeframes results in automated credential suspension.
- **Exceptions:** Rare exceptions regarding background screening adjustments for specific international jurisdictions must be documented in the [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md) under the Security Exception & Risk Acceptance Log and approved jointly by Legal Counsel and the [CISO_NAME].

## 6. Related Documents
- [Information Security Policy](../01_ISMS_Framework/01_Information_Security_Policy.md)
- [Roles and Responsibilities](../01_ISMS_Framework/04_Roles_and_Responsibilities.md)
- [Asset Management Policy](02_Asset_Management_Policy.md)
- [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md)

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Initial release and harmonization |
