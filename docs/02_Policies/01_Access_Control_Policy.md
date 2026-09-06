# Access Control Policy

| Attribute | Value |
| :--- | :--- |
| **Document ID** | POL-01 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Identity & Access Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.5.15, A.5.16, A.5.17, A.5.18, A.6.5, A.8.2, A.8.3, A.8.5), SOC 2 TSC (CC6.1, CC6.2, CC6.3), NIST CSF 2.0 (PR.AA-01, PR.AA-02, PR.AA-03, PR.AA-04, PR.AA-06), GDPR (Art. 25, 32) |

## 1. Purpose
The purpose of this policy is to establish rules for the granting, review, and revocation of access to [COMPANY_NAME] systems and data, ensuring compliance with strict security frameworks. *(ISO/IEC 27001:2022 A.5.15, SOC 2 CC6.1, NIST CSF 2.0 PR.AA-01)*

## 2. Scope
This policy applies to all employees, contractors, and third-party users who require access to [COMPANY_NAME] information systems.

## 3. Policy Statements

### 3.1 Principle of Least Privilege and RBAC
* **Role-Based Access Control (RBAC):** Access rights must be strictly managed through RBAC models. Permissions are granted based on predefined roles rather than individual user assignments. *(ISO/IEC 27001:2022 A.5.15, A.5.18, SOC 2 CC6.1, NIST CSF 2.0 PR.AA-01)*
* **Just-In-Time (JIT) Access:** Access to production environments must require JIT provisioning, temporary credentials, and documented approval via a ticketing system.

### 3.2 User Registration and De-registration
* **Automated Provisioning:** Accounts must be provisioned through a centralized Identity Provider (IdP) supporting SAML/OIDC.
* **Termination:** Automated offboarding scripts must immediately revoke SSO access and invalidate active session tokens within 1 hour of HR termination notification. *(ISO/IEC 27001:2022 A.5.16, A.5.18, A.6.5, SOC 2 CC6.2, NIST CSF 2.0 PR.AA-06)*

### 3.3 Password Management and Authentication
* **Multi-Factor Authentication (MFA):** Phishing-resistant MFA (FIDO2 / WebAuthn / Passkeys) or number-matching push authentication is strictly enforced for all user, administrative, and external system access. SMS-based and voice-call MFA are strictly prohibited across all accounts.
* **Password Standards:** Where centralized SSO is not applicable, passwords must be at least 14 characters (`[MIN_PASSWORD_LENGTH]`). Long, memorable passphrases are encouraged. In alignment with NIST SP 800-63B, arbitrary character-composition complexity rules and periodic password expiration are prohibited; credentials are checked continuously against compromised/breached password blocklists and forced to change only upon suspected breach. *(ISO/IEC 27001:2022 A.5.17, A.8.5, SOC 2 CC6.1, NIST CSF 2.0 PR.AA-03)*

### 3.4 Access Review Cadence
* **Privileged Accounts:** Privileged accounts (e.g., cloud root/IAM Admin, database administrator, production SSH) must be reviewed monthly.
* **Critical Systems:** Access to critical systems, production infrastructure, and customer data repositories must be reviewed quarterly.
* **Standard Systems:** Standard employee access to non-critical internal business applications must be reviewed at least semi-annually. *(ISO/IEC 27001:2022 A.5.18, A.8.2, SOC 2 CC6.2, CC6.3, NIST CSF 2.0 PR.AA-04)*

## 4. Roles and Responsibilities
- **[CISO_NAME]**: Responsible for maintaining this policy, defining access control baselines, and reviewing privileged access logs.
- **System & Data Owners**: Responsible for authorizing access requests on a strict need-to-know basis and executing quarterly/semi-annual access certifications.
- **Identity & Access Engineering Team**: Responsible for configuring IdP SSO, enforcing MFA, and maintaining automated provisioning/de-provisioning integrations.
- **Human Resources (HR)**: Responsible for immediately notifying IT and Security of all personnel role changes, leaves, and terminations.
- **All Users**: Responsible for safeguarding authentication credentials and immediately reporting lost devices or unauthorized access attempts.

## 5. Compliance and Exceptions
- **Compliance:** Adherence to this policy is mandatory for all personnel. Compliance is audited continuously through automated IdP logs and periodic internal audits. Violations may result in disciplinary action up to and including termination of employment or contract.
- **Exceptions:** Any exception to this policy (e.g., temporary access for emergency maintenance or non-SSO legacy systems) must be formally submitted, accompanied by robust compensating controls, documented in the [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md) under the Security Exception & Risk Acceptance Log, and approved by the [CISO_NAME]. Exceptions are granted for a maximum duration of 90 days.

## 6. Related Documents
- [Password and Authentication Standard](../03_Standards_and_Procedures/01_Password_and_Authentication_Standard.md)
- [Access Review Log](../04_Templates_and_Registers/05_Access_Review_Log.md)
- [Information Security Policy](../01_ISMS_Framework/01_Information_Security_Policy.md)
- [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md)

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Initial release and harmonization |
