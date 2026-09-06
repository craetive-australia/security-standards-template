# Physical and Environmental Security Policy

| Attribute | Value |
| :--- | :--- |
| **Document ID** | POL-04 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Facilities & Physical Security Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.7.1, A.7.2, A.7.3, A.7.4, A.7.5, A.7.6, A.7.7, A.7.8, A.7.11, A.7.14), SOC 2 TSC (CC6.1, CC6.4, CC6.5), NIST CSF 2.0 (PR.PS-01, PR.PS-02, PR.PS-03, PR.PS-04, PR.PS-05, PR.PS-07, PR.DS-03), GDPR (Art. 32) |

## 1. Purpose
To prevent unauthorized physical access, damage, and interference to [COMPANY_NAME]'s information and information processing facilities using robust physical security controls. *(ISO/IEC 27001:2022 A.7.1, A.7.2, SOC 2 CC6.4, NIST CSF 2.0 PR.PS-01)*

## 2. Scope
Applies to all [COMPANY_NAME] offices, leased facilities, data centers, and physical locations housing critical infrastructure.

## 3. Policy Statements

### 3.1 Physical Entry Controls (Tiered by Facility Type)
* **Corporate & Co-Working Offices:** Access to physical office spaces requires electronic badge/keycard authentication. Visitors must be verified via a digital visitor log, sign an NDA, wear visible visitor identification, and be continuously escorted by authorized personnel. *(ISO/IEC 27001:2022 A.7.2, SOC 2 CC6.4, NIST CSF 2.0 PR.PS-02)*
* **Dedicated Server Rooms & Data Centers:** Access to critical zones housing on-premise production hardware requires multi-factor physical authentication (badge plus PIN or biometric verification) and anti-tailgating controls (e.g., mantrap doors or optical turnstile sensors).

### 3.2 Securing Offices and Facilities
* **Surveillance:** CCTV cameras must monitor all facility ingress/egress points and critical equipment areas, with footage retained for a minimum of 90 days. *(ISO/IEC 27001:2022 A.7.4, SOC 2 CC6.4, NIST CSF 2.0 PR.PS-04)*
* **Alarm Systems:** Direct-managed facilities must be equipped with monitored intrusion detection alarms active during non-business hours.

### 3.3 Equipment Siting, Environmental Protection, & Cloud Inheritance
* **On-Premise Data Centers:** Dedicated server rooms must feature uninterruptible power supplies (UPS), backup generators, HVAC environmental monitoring, and gas-based fire suppression systems. *(ISO/IEC 27001:2022 A.7.5, A.7.8, A.7.11, SOC 2 CC6.4, NIST CSF 2.0 PR.PS-05)*
* **Cloud Service Provider (CSP) Facilities (Inherited Controls):** Where production infrastructure is hosted in public cloud environments (e.g., AWS, Google Cloud, Microsoft Azure) or tier-1 colocation facilities, physical and environmental controls are inherited under the shared responsibility model and validated annually via the provider's SOC 2 Type II and ISO/IEC 27001 certification reports in accordance with the [Supplier Security Policy](07_Supplier_Security_Policy.md).

### 3.4 Clear Desk and Clear Screen
* **Automated Lock:** All endpoints must be configured via MDM/GPO to automatically lock screens after 5 minutes of inactivity.
* **Secure Disposal:** Locked, confidential shredding bins must be used for all physical documents. A clean-desk policy will be enforced via unannounced monthly walk-throughs. *(ISO/IEC 27001:2022 A.7.7, A.7.14, SOC 2 CC6.1, CC6.5, NIST CSF 2.0 PR.PS-07, PR.DS-03)*

## 4. Roles and Responsibilities
- **[CISO_NAME]**: Defines physical security requirements, perimeter control standards, and oversees annual physical risk reviews.
- **Facilities & Physical Security Team**: Manages badge access systems, maintenance of surveillance/fire suppression equipment, and visitor badge logs.
- **Local Office Managers**: Oversees daily physical access enforcement and escorts visitors and maintenance vendors.
- **All Personnel**: Mandated to badge in individually, challenge unescorted strangers, and maintain clear desk/screen standards.

## 5. Compliance and Exceptions
- **Compliance:** Physical security controls are subject to automated audit trails and unannounced quarterly inspections. Non-compliance (e.g., tailgating, leaving sensitive records exposed) triggers formal retraining or disciplinary action.
- **Exceptions:** Requests for physical access exemptions (e.g., specialized lab equipment or external maintenance events) must be submitted via the [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md) under the Security Exception & Risk Acceptance Log and approved by the [CISO_NAME].

## 6. Related Documents
- [Asset Management Policy](02_Asset_Management_Policy.md)
- [Data Retention and Destruction Standard](../03_Standards_and_Procedures/03_Data_Retention_and_Destruction_Standard.md)
- [Information Security Policy](../01_ISMS_Framework/01_Information_Security_Policy.md)
- [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md)

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Initial release and harmonization |
