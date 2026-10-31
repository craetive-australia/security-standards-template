# Disaster Recovery Plan (DRP)

| Attribute | Value |
| :--- | :--- |
| **Document ID** | SOP-03 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Disaster Recovery Coordinator |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.5.30, A.8.14), SOC 2 TSC (CC9.1), NIST CSF 2.0 (RC.RP-02, PR.DS-11) |

## 1. Purpose
The Disaster Recovery Plan (DRP) provides the technical procedures and guidelines to recover [COMPANY_NAME]'s critical IT infrastructure, systems, and data following a catastrophic failure, cyberattack, or natural disaster.
*(ISO/IEC 27001:2022 A.5.30, A.8.14, SOC 2 CC9.1, NIST CSF 2.0 RC.RP-02, PR.DS-11)*

## 2. Scope
This plan applies to all IT systems, applications, and networks deemed critical in the Business Impact Analysis (BIA), including on-premise hardware, cloud environments, and data backups.

## 3. Recovery Objectives

Based on the BIA, the following metrics guide IT recovery efforts:
*   **Recovery Time Objective (RTO):** The maximum acceptable delay between the interruption of service and the restoration of service.
    *   *Tier 1 Systems (e.g., Core Application, Database):* RTO = [4 hours]
    *   *Tier 2 Systems (e.g., Internal Wiki, HR Systems):* RTO = [24 hours]
    *   *Tier 3 Systems (e.g., Archival Storage):* RTO = [7 days]
*   **Recovery Point Objective (RPO):** The maximum acceptable amount of data loss measured in time.
    *   *Tier 1 Systems:* RPO = [1 hour]
    *   *Tier 2 Systems:* RPO = [12 hours]

## 4. Backup Strategy
*   **Frequency:** Critical databases and systems are backed up at least [daily / hourly].
*   **Storage:** Backups are stored in an offsite, geographically isolated, and logically separated environment (e.g., immutable cloud storage).
*   **Testing:** Backup restoration is tested continuously via automated processes and validated manually at least [quarterly].

## 5. Disaster Recovery Roles
*   **Disaster Recovery Coordinator:** [Name/Role] - Manages the execution of the DRP.
*   **Infrastructure Recovery Team:** Restores network connectivity, cloud environments, and hardware.
*   **Application Recovery Team:** Restores applications, databases, and ensures data integrity.

## 6. Recovery Procedures

### 6.1 Phase 1: Assessment and Declaration
*   The IT team assesses the damage and determines if system recovery is required.
*   The Disaster Recovery Coordinator, in conjunction with the Crisis Management Team, formally declares a disaster.

### 6.2 Phase 2: System Recovery (Failover)
*   **Cloud Infrastructure:** Initiate automated failover scripts (Infrastructure as Code) to provision redundant environments in the secondary region (e.g., AWS us-west-2 to us-east-1).
*   **Data Restoration:** Restore databases from the most recent secure backup meeting the RPO.
*   **Network Routing:** Update DNS records and load balancers to route traffic to the recovered environment.

### 6.3 Phase 3: Validation
*   The Application Recovery Team conducts tests to verify system functionality and data integrity.
*   Security tools (firewalls, EDR) are confirmed to be active and properly configured in the new environment.

### 6.4 Phase 4: Restoration (Failback)
*   Once the primary environment is stabilized and secured, a controlled failback procedure will be scheduled during a maintenance window to return operations to normal.

## 7. Training and Testing
*   The DRP must be tested (at minimum via a tabletop exercise, ideally via a technical failover test) at least [annually].
*   Results and lessons learned must be documented and used to improve the plan.

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | IT & Security | [CISO_NAME] | Initial release and modernization |
