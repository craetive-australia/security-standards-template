# Cryptography Policy

| Attribute | Value |
| :--- | :--- |
| **Document ID** | POL-03 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Security Engineering Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.8.24), SOC 2 TSC (CC6.1, CC6.7), NIST CSF 2.0 (PR.DS-01, PR.DS-02), GDPR (Art. 32) |

## 1. Purpose
To define strict technical standards for the use of cryptographic controls to protect the confidentiality, integrity, and authenticity of [COMPANY_NAME] data. *(ISO/IEC 27001:2022 A.8.24, SOC 2 CC6.1, NIST CSF 2.0 PR.DS-01)*

## 2. Scope
Applies to all systems, applications, databases, and networks storing, processing, or transmitting sensitive data belonging to [COMPANY_NAME].

## 3. Policy Statements

### 3.1 Encryption in Transit
* **Protocols:** All network communications involving sensitive data must use TLS 1.2 or higher (TLS 1.3 preferred). SSL and TLS 1.0/1.1 are explicitly disabled.
* **Cipher Suites:** Only strong cipher suites supporting Forward Secrecy (e.g., ECDHE-RSA-AES256-GCM-SHA384) are permitted. *(ISO/IEC 27001:2022 A.8.24, SOC 2 CC6.7, NIST CSF 2.0 PR.DS-01, PR.DS-02)*

### 3.2 Encryption at Rest
* **Algorithms:** All sensitive data at rest, including production databases, object storage (e.g., S3, GCS), and backup media, must be encrypted using AES-256 or superior algorithms.
* **Transparent Data Encryption (TDE):** TDE must be enabled on all relational database instances. *(ISO/IEC 27001:2022 A.8.24, SOC 2 CC6.1, NIST CSF 2.0 PR.DS-01)*

### 3.3 Key and Secrets Management
* **Centralized Vault:** Cryptographic keys and application secrets (e.g., API keys, service tokens) must be managed using a centralized secrets management platform (e.g., HashiCorp Vault, AWS KMS). Hardcoding secrets in source code is strictly prohibited.
* **Key Rotation:** In accordance with NIST SP 800-57, symmetric root and master encryption keys managed within KMS must be rotated annually (365 days). Ephemeral application secrets, API tokens, and TLS certificates must be rotated at intervals not exceeding 90 days. Revoked keys must be archived securely for data recovery purposes only. *(ISO/IEC 27001:2022 A.8.24, SOC 2 CC6.1, NIST CSF 2.0 PR.DS-01)*
* **Post-Quantum Cryptography (PQC) Readiness:** System architectures must plan for agility in adopting post-quantum cryptographic standards aligned with NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), and FIPS 205 (SLH-DSA), utilizing hybrid classical-quantum key encapsulation where available.

## 4. Roles and Responsibilities
- **[CISO_NAME]**: Approving acceptable cryptographic algorithms, minimum key lengths, and key management architecture.
- **Security Engineering / Cryptographic Custodians**: Maintaining the centralized key vault, monitoring key lifecycle states, and executing rotation schedules.
- **DevOps / SRE**: Enforcing encryption configurations across cloud infrastructure via Infrastructure as Code (IaC) and automating certificate renewals.
- **Software Engineers**: Ensuring application code retrieves secrets at runtime via vault APIs and never commits plaintext credentials.

## 5. Compliance and Exceptions
- **Compliance:** All systems storing or transmitting [COMPANY_NAME] data must employ approved cryptography. Deprecated algorithms (e.g., DES, 3DES, MD5, SHA-1) are strictly prohibited.
- **Exceptions:** Legacy systems unable to support modern TLS or AES-256 must obtain an approved exception in the [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md) under the Security Exception & Risk Acceptance Log with compensating controls (e.g., dedicated IPSec/VPN tunneling).

## 6. Related Documents
- [Secure Coding Standard](../03_Standards_and_Procedures/05_Secure_Coding_Standard.md)
- [Information Security Policy](../01_ISMS_Framework/01_Information_Security_Policy.md)
- [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md)

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Initial release and harmonization |
