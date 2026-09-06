# Asset Management Policy

| Attribute | Value |
| :--- | :--- |
| **Document ID** | POL-02 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / IT Operations Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.5.9, A.5.10, A.5.11, A.5.12, A.5.13, A.7.14, A.8.1, A.8.10), SOC 2 TSC (CC6.1, CC6.5, CC6.7, C1.1), NIST CSF 2.0 (ID.AM-01, ID.AM-05, PR.AA-01, PR.DS-01, PR.DS-03, PR.DS-11), GDPR (Art. 30, 32) |

## 1. Purpose
To ensure that all information assets are identified, cryptographically protected, and actively managed throughout their lifecycle in accordance with their value to [COMPANY_NAME]. *(ISO/IEC 27001:2022 A.5.9, SOC 2 CC6.1, NIST CSF 2.0 ID.AM-01)*

## 2. Scope
This policy applies to all hardware, software, information, and physical assets owned, managed, or utilized by [COMPANY_NAME].

## 3. Policy Statements

### 3.1 Automated Inventory and MDM
* **Device Management:** All corporate-issued devices must be enrolled in a Mobile Device Management (MDM) solution (e.g., Intune, Jamf) prior to deployment.
* **Continuous Discovery:** An agent-based asset discovery tool must be deployed to maintain a real-time, automated inventory of all endpoints and cloud servers. *(ISO/IEC 27001:2022 A.5.9, SOC 2 CC6.1, NIST CSF 2.0 ID.AM-01)*

### 3.2 Endpoint Protection and Acceptable Use
* **Disk Encryption:** Full Disk Encryption (FDE) (e.g., BitLocker, FileVault 2) is enforced by policy and monitored via MDM.
* **Remote Wipe:** The Security team must retain the ability to remotely wipe any corporate device in the event of loss or theft. *(ISO/IEC 27001:2022 A.5.10, A.8.1, SOC 2 CC6.1, NIST CSF 2.0 PR.AA-01)*

### 3.3 Return and Destruction of Assets
* **Offboarding:** All physical assets must be returned within 3 days of employment termination.
* **Data Sanitization:** Media designated for disposal must be cryptographically wiped or purged in accordance with NIST SP 800-88 Rev. 1 and IEEE 2883-2022 standards, or physically destroyed by a certified e-waste contractor. *(ISO/IEC 27001:2022 A.5.11, A.7.14, A.8.10, SOC 2 CC6.5, NIST CSF 2.0 PR.DS-03, PR.DS-11)*

### 3.4 Information Classification and Labeling
* **Default Classification:** All newly generated documents, spreadsheets, repositories, and workspace artifacts receive a default metadata classification of **Internal** via automated DLP and workspace tooling.
* **Visual Markings:** Assets classified as **Confidential** or **Restricted** must bear visible markings (headers, footers, or watermarks) denoting their sensitivity and handling restrictions. *(ISO/IEC 27001:2022 A.5.12, A.5.13, SOC 2 CC6.1, CC6.7, C1.1, NIST CSF 2.0 ID.AM-05, PR.DS-01)*

## 4. Roles and Responsibilities
- **[CISO_NAME]**: Defines asset management requirements, data classification baselines, and approves sanitization protocols.
- **IT Operations / Systems Engineering**: Responsible for maintaining MDM configurations, hardware asset inventories, and executing decommissioning workflows.
- **Asset Custodians**: Responsible for maintaining accurate metadata, designating asset criticality, and conducting quarterly asset validations.
- **All Employees & Contractors**: Responsible for protecting company equipment, reporting loss or theft within 1 hour, and adhering to asset handling rules.

## 5. Compliance and Exceptions
- **Compliance:** Asset tracking and protection are mandatory across all corporate systems. Unregistered or non-compliant devices will be automatically blocked by zero-trust network access controls.
- **Exceptions:** Hardware or software that cannot support standard MDM or encryption agents must be granted an approved exception documented in the [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md) under the Security Exception & Risk Acceptance Log with compensating controls (e.g., network isolation).

## 6. Related Documents
- [Information Asset Register](../04_Templates_and_Registers/01_Information_Asset_Register.md)
- [Data Classification and Handling Standard](../03_Standards_and_Procedures/02_Data_Classification_and_Handling_Standard.md)
- [Data Retention and Destruction Standard](../03_Standards_and_Procedures/03_Data_Retention_and_Destruction_Standard.md)
- [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md)

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Initial release and harmonization |
