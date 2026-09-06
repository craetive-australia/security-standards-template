# Communications Security Policy

| Attribute | Value |
| :--- | :--- |
| **Document ID** | POL-06 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Network Security Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.5.14, A.7.12, A.8.20, A.8.21, A.8.22, A.8.26), SOC 2 TSC (CC6.6, CC6.7), NIST CSF 2.0 (PR.IR-01, PR.IR-02, PR.IR-03, PR.DS-02, PR.DS-07), GDPR (Art. 32) |

## 1. Purpose
To ensure the protection of information traversing networks and its supporting infrastructure through advanced network security controls and segmentation. *(ISO/IEC 27001:2022 A.8.20, SOC 2 CC6.6, NIST CSF 2.0 PR.IR-01)*

## 2. Scope
Applies to all internal, external, and cloud networks operated by or on behalf of [COMPANY_NAME].

## 3. Policy Statements

### 3.1 Network Controls and Boundary Defense
* **Next-Gen Firewalls:** Network boundaries must be protected by Next-Generation Firewalls (NGFW) with deep packet inspection and Intrusion Prevention Systems (IPS) enabled.
* **Web Application Firewall (WAF):** All external-facing web applications and APIs must be shielded by a WAF configured to block OWASP Top 10 attacks. *(ISO/IEC 27001:2022 A.8.20, A.8.26, SOC 2 CC6.6, NIST CSF 2.0 PR.IR-01, PR.DS-07)*

### 3.2 Secure Remote Access
* **Zero Trust / VPN:** Remote access to the internal network must be brokered through a Zero Trust Network Access (ZTNA) solution or a VPN requiring SSO and MFA. Direct SSH or RDP exposure to the internet is strictly forbidden.

### 3.3 Segregation in Networks
* **Micro-segmentation:** Networks must be strictly segmented (e.g., using VPCs, subnets, and security groups). Production environments must be completely isolated from Development, Staging, and Corporate IT networks.
* **Default Deny:** All network access control lists (ACLs) and firewall rules must enforce a "default deny" policy for ingress and egress traffic. *(ISO/IEC 27001:2022 A.8.20, A.8.22, SOC 2 CC6.6, NIST CSF 2.0 PR.IR-01, PR.IR-03)*

### 3.4 Information Transfer
* **Secure Protocols:** The transfer of sensitive data with third parties must utilize secure, encrypted protocols (e.g., SFTP, HTTPS). Data sent via email must be protected via encrypted email portals or encrypted attachments. *(ISO/IEC 27001:2022 A.5.14, SOC 2 CC6.6, CC6.7, NIST CSF 2.0 PR.DS-02)*

## 4. Roles and Responsibilities
- **[CISO_NAME]**: Defines perimeter defense requirements and reviews quarterly network architecture audits.
- **Network Security Lead / Infrastructure Engineering**: Manages VPC topologies, firewall rule sets, WAF profiles, and ensures zero-trust compliance.
- **SecOps / Threat Detection**: Monitors network anomaly alerts, intrusion detection sensors, and investigates egress spikes.
- **All Personnel**: Mandated to use corporate ZTNA/VPN when connecting remotely and prohibited from establishing unauthorized network bridges.

## 5. Compliance and Exceptions
- **Compliance:** Network configurations are validated continuously via automated posture checkers and IaC linters. Unapproved open ports or permissive firewall rules are automatically terminated.
- **Exceptions:** Temporary network openings for debugging or third-party integration must be formally requested in the [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md) under the Security Exception & Risk Acceptance Log, restricted by source IP, and approved by the [CISO_NAME] for a maximum of 14 days.

## 6. Related Documents
- [Access Control Policy](01_Access_Control_Policy.md)
- [Operations Security Policy](05_Operations_Security_Policy.md)
- [Information Security Policy](../01_ISMS_Framework/01_Information_Security_Policy.md)
- [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md)

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Initial release and harmonization |
