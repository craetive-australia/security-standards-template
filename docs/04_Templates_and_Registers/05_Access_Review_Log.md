# Access Review Log

| Attribute | Value |
| :--- | :--- |
| **Document ID** | REG-04 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / IAM Administrator |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.5.18, A.8.2), SOC 2 TSC (CC6.3), NIST CSF 2.0 (PR.AA-04) |

*(ISO/IEC 27001:2022 A.5.18, A.8.2, SOC 2 CC6.3, NIST CSF 2.0 PR.AA-04)*

**Purpose**: To provide a historical record of periodic user access reviews conducted for [COMPANY_NAME] systems to ensure enforcement of the principle of least privilege.

**Cadence Requirements**:
- **Monthly**: Privileged accounts, domain/cloud admins, root/break-glass access, and sensitive infrastructure.
- **Quarterly**: Critical systems, production databases, customer data repositories, and source code repositories.
- **Semi-Annually**: Standard business applications, SaaS tools, and internal communication systems.

| Review ID | Date Conducted | System / Application | Reviewer | Review Cadence | Total Users Reviewed | Revocations / Changes Made | Remediation Ticket | Sign-off |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| AR-001 | YYYY-MM-DD | AWS Production | [CISO_NAME] | Monthly (Privileged) | 25 | 2 users removed (transferred dept) | IT-402 | Done |
| AR-002 | YYYY-MM-DD | GitHub Enterprise | VPE | Quarterly (Critical) | 50 | 1 external contractor access removed | IT-403 | Done |
| AR-003 | YYYY-MM-DD | Google Workspace | IT Support | Semi-Annual (Standard) | 120 | 3 stale user accounts deprovisioned | IT-408 | Done |

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | Information Security | [CISO_NAME] | Initial release and modernization with monthly privileged, quarterly critical, and semi-annual cadences |
