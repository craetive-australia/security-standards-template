# Data Classification and Handling Standard

| Attribute | Value |
| :--- | :--- |
| **Document ID** | STD-02 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Data Governance Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.5.12, A.5.13, A.8.11, A.8.12), SOC 2 TSC (CC6.1, CC6.7, C1.1), NIST CSF 2.0 (ID.AM-05, PR.DS-01), GDPR (Art. 5, 25, 32) |

## 1. Purpose
The purpose of this standard is to establish a framework for classifying data based on its sensitivity and criticality to [COMPANY_NAME], and to define the minimum security controls for handling data at each classification level.
*(ISO/IEC 27001:2022 A.5.12, A.5.13, SOC 2 CC6.1, CC6.7, C1.1, NIST CSF 2.0 ID.AM-05, PR.DS-01)*

## 2. Scope
This standard applies to all data generated, processed, stored, or transmitted by [COMPANY_NAME], across all formats (electronic, physical, verbal).

## 3. Data Classification Levels

[COMPANY_NAME] classifies data into the following four tiers, in increasing order of sensitivity:

### 3.1 Public
*   **Description:** Information approved for public distribution. Unauthorized disclosure poses no risk to the organization.
*   **Examples:** Marketing materials, published website content, press releases, public open-source documentation.

### 3.2 Internal (Default Classification)
*   **Description:** Default baseline classification. All newly created documents, spreadsheets, emails, source code repositories, and communications automatically receive a **default Internal metadata classification** applied via workspace tooling (Google Workspace / Microsoft 365 / GitHub) and Data Loss Prevention (DLP) systems. Unauthorized disclosure may cause operational disruption or moderate embarrassment.
*   **Examples:** Internal operational notes, organizational charts, company policies, general Slack channels.

### 3.3 Confidential
*   **Description:** Sensitive business, customer, or employee information requiring restricted access. Unauthorized disclosure could cause significant financial, legal, or reputational damage.
*   **Examples:** Financial records, non-public source code, customer contracts, pricing sheets, employee PII.

### 3.4 Restricted
*   **Description:** Highly confidential information subject to strict legal or regulatory penalties and access on a strict "need-to-know" basis. Unauthorized disclosure would cause severe, catastrophic harm to the organization or its customers.
*   **Examples:** Production credentials, private encryption keys, payment cardholder data (PCI DSS), Protected Health Information (PHI), merger and acquisition materials.

## 4. Data Handling and Labeling Requirements

### 4.1 Labeling and Visual Markings
*   **Default Metadata Classification:** DLP agents and cloud workspace configurations must automatically tag all new content with the **default Internal** metadata label.
*   **Public Data:** May be labeled "Public" upon formal marketing or legal review.
*   **Explicit Visual Markings on Confidential and Restricted:** Documents, PDFs, presentations, and printed media classified as **Confidential** or **Restricted** must feature explicit visual markings. This includes clear header or footer text (e.g., `CONFIDENTIAL - [COMPANY_NAME]` or `RESTRICTED - DO NOT DISTRIBUTE`) or prominent watermarks across all pages. Email communications carrying Confidential or Restricted content must include classification indicators in the subject line or message banner.

### 4.2 Storage and Encryption
*   **Public:** Standard cloud storage. Encryption optional.
*   **Internal:** Access restricted to authenticated personnel. AES-256 encryption at rest.
*   **Confidential:** Role-based access control (RBAC). Encrypted at rest (AES-256) and segregated from general employee access.
*   **Restricted:** Least privilege, just-in-time access only. Encrypted at rest (AES-256 with customer-managed KMS keys) and isolated in dedicated encrypted datastores.

### 4.3 Transmission
*   **Public:** Standard web transfer (HTTPS recommended).
*   **Internal / Confidential / Restricted:** Must be transmitted over encrypted network channels (TLS 1.2 or higher, SFTP, corporate VPN). Sensitive attachments must be protected via encrypted portals or DLP controls.

### 4.4 Destruction
*   Refer to the *Data Retention and Destruction Standard* for requirements regarding cryptographic wiping and physical disposal in accordance with NIST SP 800-88 Rev. 1 and IEEE 2883-2022.

## 5. Roles and Responsibilities
*   **Data Owners:** Determine classification tier and approve access authorizations.
*   **Data Custodians:** Configure DLP tagging, encryption baselines, and access permissions.
*   **All Users:** Ensure documents bear required visual markings and respect classification tiers.

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Initial release and default Internal / visual marking harmonization |
