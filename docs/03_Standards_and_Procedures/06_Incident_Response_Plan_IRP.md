# Incident Response Plan (IRP)

| Attribute | Value |
| :--- | :--- |
| **Document ID** | SOP-01 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Incident Commander |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.5.24, A.5.25, A.5.26, A.5.27, A.5.28), SOC 2 TSC (CC7.3), NIST CSF 2.0 (RS.MA-01, RS.RP-01) |

## 1. Purpose
This Incident Response Plan (IRP) establishes the framework and structured methodology for responding to cybersecurity incidents at [COMPANY_NAME]. The goal is to minimize damage, reduce recovery time and costs, and maintain business operations.

## 2. Scope
This plan covers all information systems, networks, and data managed by [COMPANY_NAME] and applies to all personnel involved in incident response.

## 3. Phases of Incident Response
*(ISO/IEC 27001:2022 A.5.24, A.5.25, A.5.26, A.5.27, A.5.28, SOC 2 CC7.3, NIST CSF 2.0 RS.MA-01, RS.RP-01)*

### 3.1 Preparation
- Establish and train the Computer Security Incident Response Team (CSIRT).
- Maintain incident response tools, communication channels, and contact lists.
- Conduct regular tabletop exercises (at least annually) to test the IRP.

### 3.2 Identification
- Monitor systems for indicators of compromise (IoCs) using SIEM, EDR, and other security tools.
- Triage alerts and reports from internal staff or external parties.
- Determine if an event qualifies as a security incident and activate the CSIRT.
- Record all details in the [Security Incident Log](../04_Templates_and_Registers/03_Security_Incident_Log.md).

### 3.3 Containment
- **Short-Term:** Immediate actions to prevent the incident from spreading (e.g., isolating affected hosts from the network, disabling compromised accounts).
- **Long-Term:** Implement temporary fixes to restore normal operations safely while full remediation is planned.
- Ensure volatile data and evidence are preserved before making systemic changes.

### 3.4 Eradication
- Identify the root cause of the incident.
- Remove malware, threat actors, and malicious artifacts from the environment.
- Patch vulnerabilities and close entry points exploited by the attacker.

### 3.5 Recovery
- Restore systems and data from known clean backups.
- Carefully monitor restored systems to ensure the threat has been fully eradicated and normal operations are stable.
- Formally declare the incident resolved.

### 3.6 Lessons Learned and Post-Mortem SLAs
*(ISO/IEC 27001:2022 A.5.27, A.5.28)*
A blameless post-mortem review must be conducted, and a completed Post-Incident Report / Root Cause Analysis (RCA) must be published within the following strict Service Level Agreements (SLAs):
- **Severity 1 (Critical) and Severity 2 (High):** Post-mortem completed and published within **5 business days** of incident closure.
- **Severity 3 (Medium) and Severity 4 (Low):** Post-mortem completed and published within **10 business days** of incident closure.
- Document what went well, root causes, detection gaps, and preventive CAPA items.
- If the incident involves a confirmed or suspected personal data breach, immediately execute the [Data Breach Notification Procedure](09_Data_Breach_Notification_Procedure.md).

## 4. Roles and Responsibilities
- **[CISO_NAME]:** Oversees the incident response process and acts as the final decision-maker.
- **CSIRT:** Responsible for the technical execution of this plan.
- **Legal/PR:** Handles external communications and regulatory notifications.

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | Information Security | [CISO_NAME] | Initial release and modernization with 5-day / 10-day post-mortem SLAs |
