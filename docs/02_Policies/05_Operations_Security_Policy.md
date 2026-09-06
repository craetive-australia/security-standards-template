# Operations Security Policy

| Attribute | Value |
| :--- | :--- |
| **Document ID** | POL-05 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / VP Engineering |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.5.37, A.8.6, A.8.7, A.8.9, A.8.13, A.8.15, A.8.16, A.8.17, A.8.19, A.8.32, A.8.34), SOC 2 TSC (CC7.1, CC7.2, CC7.3, CC7.5, CC8.1), NIST CSF 2.0 (PR.PS-01, DE.AE-03, DE.CM-01, DE.CM-04, PR.DS-09), GDPR (Art. 32) |

## 1. Purpose
To ensure correct, secure, and resilient operations of [COMPANY_NAME]'s information processing facilities through automated controls and proactive monitoring. *(ISO/IEC 27001:2022 A.5.37, SOC 2 CC7.1, NIST CSF 2.0 PR.PS-01)*

## 2. Scope
Applies to all production IT systems, cloud infrastructure, endpoints, and operations personnel.

## 3. Policy Statements

### 3.1 Automated Change Management
* **Infrastructure as Code (IaC):** All infrastructure changes must be managed via IaC (e.g., Terraform), reviewed via pull requests, and deployed through automated CI/CD pipelines. Manual production changes are strictly prohibited outside of declared incidents. *(ISO/IEC 27001:2022 A.8.9, A.8.32, SOC 2 CC8.1, NIST CSF 2.0 PR.PS-01)*

### 3.2 Capacity Management
* **Auto-Scaling:** Cloud environments must utilize auto-scaling groups and automated performance alerting (e.g., Datadog, CloudWatch) for CPU, memory, and storage utilization to ensure uninterrupted service availability. *(ISO/IEC 27001:2022 A.8.6, SOC 2 CC7.1, NIST CSF 2.0 PR.PS-01)*

### 3.3 Protection Against Malware
* **Endpoint Detection and Response (EDR):** Next-generation EDR agents (e.g., CrowdStrike, SentinelOne) must be deployed on all workstations and servers, configured to automatically block and quarantine malicious activity. *(ISO/IEC 27001:2022 A.8.7, SOC 2 CC6.8, NIST CSF 2.0 DE.CM-04)*

### 3.4 Immutable Backups
* **Backup Architecture:** Daily automated backups of critical databases must be encrypted and stored in an immutable, logical air-gapped vault or separate cloud account.
* **Restore Testing:** Automated restore tests must be conducted quarterly to validate RPO and RTO compliance. *(ISO/IEC 27001:2022 A.8.13, SOC 2 CC7.3, CC7.5, NIST CSF 2.0 PR.DS-09)*

### 3.5 Centralized Logging and Monitoring
* **SIEM Integration:** All OS, application, firewall, and access logs must be forwarded in real-time to a centralized SIEM platform.
* **Log Retention Tiers:** Security and audit logs (with PII masked or tokenized prior to ingestion) must be retained for at least 90 days active/hot (searchable in SIEM) and 365 days in an immutable cold archive (WORM storage). Ephemeral debug logs must be retained for a maximum of 30 days and are prohibited from capturing production credentials or PII. *(ISO/IEC 27001:2022 A.8.15, SOC 2 CC7.2, NIST CSF 2.0 DE.AE-03)*

## 4. Roles and Responsibilities
- **[CISO_NAME]**: Defines operations security policies, approves logging architecture, and oversees SIEM alert escalations.
- **VP Engineering / DevOps Lead**: Enforces IaC change pipelines, capacity planning, and zero-touch production controls.
- **Site Reliability Engineering (SRE)**: Manages automated backup pipelines, verifies quarterly restore drills, and monitors cloud health.
- **Security Operations Center (SOC)**: Monitors real-time SIEM alerts, conducts initial triage of anomalies, and investigates EDR detections.

## 5. Compliance and Exceptions
- **Compliance:** Operational controls are enforced via continuous CI/CD policy-as-code checks and cloud posture management tools. Direct manual access to production servers is strictly audited and disabled by default.
- **Exceptions:** Emergency operational interventions outside IaC must be approved by the Incident Commander, logged in an incident ticket, and reconciled via code within 24 hours. Formal architectural exceptions are recorded in the [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md) under the Security Exception & Risk Acceptance Log.

## 6. Related Documents
- [Data Retention and Destruction Standard](../03_Standards_and_Procedures/03_Data_Retention_and_Destruction_Standard.md)
- [Incident Response Plan](../03_Standards_and_Procedures/06_Incident_Response_Plan_IRP.md)
- [Information Security Policy](../01_ISMS_Framework/01_Information_Security_Policy.md)
- [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md)

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Initial release and harmonization |
