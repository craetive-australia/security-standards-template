# Acceptable Use and AI Security Policy

| Attribute | Value |
| :--- | :--- |
| **Document ID** | POL-13 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / AI Governance & IT Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.5.10, A.6.7, A.8.1, A.8.23), ISO/IEC 42001:2023, NIST AI RMF 1.0, SOC 2 TSC (CC6.1, CC6.6, CC6.7), NIST CSF 2.0 (PR.AA-01, PR.AA-05, PR.PS-01), NIST SP 800-53 Rev. 5 (AC-18, CM-7, SI-3, PL-4), ASD Essential Eight (E8-OM-ML2, E8-AH-ML2, E8-AC-ML2) |

## 1. Purpose
To establish acceptable use standards for [COMPANY_NAME] information assets, communications systems, endpoint devices, and Artificial Intelligence (AI) technologies, ensuring the protection of company data, employee privacy, and intellectual property. *(ISO/IEC 27001:2022 A.5.10, A.8.1, SOC 2 CC6.1, NIST CSF 2.0 PR.AA-01)*

## 2. Scope
Applies to all employees, contractors, temporary staff, and third parties utilizing [COMPANY_NAME] endpoints, networks, cloud workspaces, or deploying Artificial Intelligence (AI) and Generative AI / Large Language Model (LLM) tools.

## 3. Policy Statements

### 3.1 Endpoint Security and Device Management
* **Mobile Device Management (MDM):** All corporate-owned and BYOD endpoints accessing company resources must be enrolled in [COMPANY_NAME]'s centralized MDM platform (e.g., Microsoft Intune, Jamf). Unmanaged devices are barred from accessing corporate email, Slack, and cloud repositories. *(ISO/IEC 27001:2022 A.8.1, SOC 2 CC6.1, NIST CSF 2.0 PR.AA-05)*
* **Full Disk Encryption (FDE):** Full Disk Encryption (e.g., BitLocker with TPM on Windows, FileVault 2 on macOS) must be enabled on all endpoints. MDM automated compliance policies must verify encryption status prior to granting network access.
* **Endpoint Protection & Patching:** Next-generation EDR agents must remain running with real-time behavioral protection active. Automated OS and browser security updates must install within 7 days of release.
* **Screen Locking & Clean Desk:** Endpoints must lock automatically after a maximum of 5 minutes of inactivity. Physical screens must be positioned away from public observation.

### 3.1.1 Microsoft Office Macro Security (Essential Eight ML2/ML3)
* **Internet Macro Blocking:** Macros inside Microsoft Office files originating from the internet (email attachments, web downloads, external messaging) must be strictly blocked from executing.
* **Default Disable:** Macro execution is disabled by default across all productivity suites for all users without a formally approved, documented security exception.
* **Trusted Publishers & Signatures:** Only digitally signed macros from vetted, trusted publishers located in read-only administrative paths (e.g., Trusted Locations) are permitted to run.
* **No User Bypasses:** End-users are strictly prohibited from bypassing macro security warnings or enabling macros in documents originating from untrusted locations. *(ASD Essential Eight E8-OM-ML2, E8-OM-ML3, NIST SP 800-53 Rev. 5 CM-7)*

### 3.1.2 User Application Hardening (Essential Eight ML2/ML3)
* **Web Browser Hardening:** Corporate web browsers must be configured via enterprise policy to block or disable web advertisements and web advertising, obsolete browser plug-ins (Flash, Silverlight), and browser-based Java runtime environments.
* **Browser Extension Control:** Endpoints must prevent users from installing unapproved browser extensions or add-ons; only extensions in the centrally managed allowlist are permitted.
* **Child Process Protection:** Productivity applications and PDF readers must be hardened via exploit protection policies to prevent spawning child processes (e.g., PDF readers and Office suites are strictly blocked from executing `cmd.exe`, `powershell.exe`, or scripting runtimes). *(ASD Essential Eight E8-AH-ML2, E8-AH-ML3, NIST SP 800-53 Rev. 5 SI-3, CM-7)*

### 3.2 Remote Working and BYOD Security
* **Secure Networks:** Remote personnel must connect to corporate resources exclusively via approved Zero Trust Network Access (ZTNA) or corporate VPN tunnels. Conducting work over unencrypted public Wi-Fi without VPN is prohibited. *(ISO/IEC 27001:2022 A.6.7, SOC 2 CC6.6, CC6.7, NIST CSF 2.0 PR.AA-05)*
* **Peripherals and Removable Media:** Connecting personal USB drives, mass storage media, or unauthorized peripherals to company endpoints is blocked via MDM policy.

### 3.3 Artificial Intelligence (AI) & Generative AI Governance
In alignment with **ISO/IEC 42001:2023** (Artificial Intelligence Management System) and the **NIST AI Risk Management Framework (NIST AI RMF 1.0)**:
* **Approved AI Platforms:** Personnel may only utilize corporate-sanctioned enterprise AI accounts (e.g., enterprise ChatGPT, GitHub Copilot Enterprise, Google Vertex AI) governed by agreements that explicitly prohibit the model provider from using [COMPANY_NAME] data for model retraining.
* **Prohibited AI Prompts and Data Submissions:**
  * Submitting customer data, Personal Identifiable Information (PII), or confidential HR data into any AI or Large Language Model (LLM) is strictly forbidden unless covered by an executed Data Processing Agreement with zero-retention logging.
  * Pasting unreleased proprietary source code, cryptographic private keys, API credentials, or internal trade secrets into public consumer AI tools is strictly prohibited.
* **AI Output Verification:** Outputs generated by Generative AI / LLM tools (including code suggestions, documentation, and analytical summaries) must be human-reviewed for accuracy, bias, security vulnerabilities, and licensing compliance prior to deployment into production.
* **AI Risk Tiering & Documentation:** Internal engineering initiatives incorporating machine learning or LLM APIs must undergo an AI Risk Assessment evaluating safety, explainability, data provenance, and adversarial robustness.

### 3.4 Web Filtering and Network Acceptable Use
* **Web Filtering:** Corporate devices and DNS resolvers must enforce automated web filtering blocking known malicious domains, phishing gateways, command-and-control servers, and unauthorized file-sharing utilities. *(ISO/IEC 27001:2022 A.8.23, SOC 2 CC6.6, NIST CSF 2.0 PR.PS-01)*

## 4. Roles and Responsibilities
- **[CISO_NAME] / AI Governance Lead:** Defines acceptable use baselines, oversees enterprise AI tool approvals, and evaluates emerging AI security risks.
- **IT Operations / MDM Engineering:** Maintains endpoint configuration baselines, monitors BitLocker/FileVault encryption compliance, and enforces remote wipe capabilities.
- **AppSec & Engineering Leads:** Review AI-generated code contributions, manage GitHub Copilot enterprise policies, and ensure third-party AI APIs comply with data protection standards.
- **All Personnel**: Responsible for safeguarding issued devices, verifying AI output integrity, and adhering to strict prompt sanitization rules.

## 5. Compliance and Exceptions
- **Compliance:** Device compliance and AI data flow monitoring are tracked automatically via MDM, DLP, and CASB proxy gateways. Unauthorized data transmission to unapproved AI platforms constitutes a severe data protection breach and may lead to disciplinary termination.
- **Exceptions:** Requests for BYOD exemptions or research access to specialized AI tools must be submitted via the [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md) under the Security Exception & Risk Acceptance Log and approved in writing by the [CISO_NAME].

## 6. Related Documents
- [Information Security Policy](../01_ISMS_Framework/01_Information_Security_Policy.md)
- [Data Classification and Handling Standard](../03_Standards_and_Procedures/02_Data_Classification_and_Handling_Standard.md)
- [Asset Management Policy](02_Asset_Management_Policy.md)
- [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md)

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Initial release and harmonization |
