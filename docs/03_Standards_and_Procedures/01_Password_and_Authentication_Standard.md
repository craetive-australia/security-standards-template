# Password and Authentication Standard

| Attribute | Value |
| :--- | :--- |
| **Document ID** | STD-01 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Security Engineering Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.5.17, A.8.5), SOC 2 TSC (CC6.1), NIST CSF 2.0 (PR.AA-03), NIST SP 800-63B |

## 1. Purpose
This document establishes the technical requirements for password and authentication mechanisms at [COMPANY_NAME] to protect information systems, in full alignment with modern NIST SP 800-63B guidelines.

## 2. Scope
This standard applies to all employees, contractors, and third parties accessing [COMPANY_NAME] systems, cloud environments, applications, and networks.

## 3. Standard Specifications

### 3.1 Password Requirements *(NIST SP 800-63B Section 5.1.1)*
*(ISO/IEC 27001:2022 A.5.17, A.8.5, SOC 2 CC6.1, NIST CSF 2.0 PR.AA-03)*
- **Length:** Passwords must be a minimum of 14 characters in length (`[MIN_PASSWORD_LENGTH]`).
- **Passphrases Encouraged:** Users are strongly encouraged to create long, memorable multi-word passphrases (e.g., four or more unrelated dictionary words).
- **No Arbitrary Composition Rules:** In accordance with NIST SP 800-63B, arbitrary character-composition rules (e.g., requiring mandatory uppercase, lowercase, numbers, and special symbols) are eliminated, as they encourage predictable substitution patterns without improving entropy.
- **No Periodic Expiration:** Periodic password expiration (e.g., forced rotation every 60 or 90 days) is prohibited per NIST SP 800-63B. Passwords shall only be forced to rotate upon evidence of actual or suspected account compromise.
- **Compromised Password Blocklist Check:** Passwords must be continuously checked against known compromised/breached password blocklists (e.g., HaveIBeenPwned API or centralized directory password filters) during initial creation and any password reset. Passwords appearing on compromised blocklists are automatically rejected.
- **History:** Systems must prevent the reuse of the last 12 passwords.

### 3.2 Multi-Factor Authentication (MFA) *(NIST SP 800-63B Section 5.1.3)*
*(ISO/IEC 27001:2022 A.5.17, A.8.5, SOC 2 CC6.1, NIST CSF 2.0 PR.AA-03)*
- **Mandatory Enforcement:** Multi-Factor Authentication (MFA) is strictly enforced across 100% of internal, external, cloud console, and administrative access to [COMPANY_NAME] networks and resources.
- **Phishing-Resistant MFA:** Phishing-resistant MFA protocols (FIDO2 / WebAuthn / Passkeys or hardware security keys like YubiKey) or number-matching push notifications are mandatory.
- **SMS Prohibition:** SMS-based MFA and voice-call verification are strictly prohibited across all accounts due to vulnerability to SIM-swapping and SS7 interception.

### 3.3 Account Lockout and Rate Limiting
- Accounts will be locked out for a minimum of 15 minutes after 5 consecutive failed login attempts.
- Automated CAPTCHA or cryptographic challenge-response mechanisms must be deployed on all public login endpoints to prevent brute-force credential stuffing.

### 3.4 Service Accounts and Machine Identities
- Service accounts and machine identities must use high-entropy credentials of at least 24 characters or utilize IAM workload identity federation (e.g., AWS IAM Roles for Service Accounts, GCP Workload Identity).
- Service accounts are strictly prohibited from interactive user logins.

## 4. Compliance and Exceptions
- **Compliance:** Authentication policies are programmatically enforced via the centralized Identity Provider (IdP). Non-compliant accounts are automatically flagged and blocked.
- **Exceptions:** Any system incapable of supporting phishing-resistant MFA or 14-character passwords must have an approved exception in the [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md) under the Security Exception & Risk Acceptance Log with compensating controls (e.g., network micro-segmentation, client certificate validation) approved by the [CISO_NAME].

## 5. Related Documents
- [Access Control Policy](../02_Policies/01_Access_Control_Policy.md)
- [Information Security Policy](../01_ISMS_Framework/01_Information_Security_Policy.md)
- [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md)

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Initial release and NIST SP 800-63B modernization |
