# Information Asset Register

| Attribute | Value |
| :--- | :--- |
| **Document ID** | REG-01 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Asset Management Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.5.9), SOC 2 TSC (CC6.1), NIST CSF 2.0 (ID.AM-01) |

*(ISO/IEC 27001:2022 A.5.9, SOC 2 CC6.1, NIST CSF 2.0 ID.AM-01)*

**Purpose**: To maintain an accurate and up-to-date inventory of all information assets associated with [COMPANY_NAME]'s information and processing facilities.

**Instructions**:
- **Asset ID**: Unique identifier for the asset.
- **Asset Name**: Name or title of the asset.
- **Description**: Brief description of the asset and its function.
- **Owner**: The individual or role responsible for the asset.
- **Classification**: Data classification level (e.g., Public, Internal, Confidential, Restricted).
- **Location/System**: Where the asset is physically or logically located.
- **C-I-A Requirements**: Confidentiality, Integrity, and Availability requirements (Low, Medium, High).
- **Risk Status**: Reference to the Risk Register if applicable.

| Asset ID | Asset Name | Description | Owner | Classification | Location/System | C-I-A Requirements | Risk Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| AST-001 | Customer Database | Primary database containing customer PII | CTO | Restricted | AWS RDS (us-east-1) | C: High, I: High, A: High | Mitigated (RR-001) |
| AST-002 | Public Website | [COMPANY_NAME] marketing website | Marketing | Public | Vercel | C: Low, I: Medium, A: Medium | Acceptable |
| AST-003 | Source Code Repositories | Core intellectual property | VPE | Confidential | GitHub | C: High, I: High, A: High | Mitigated (RR-002) |

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | Information Security | [CISO_NAME] | Initial release and modernization |
