# Secure Coding Standard

| Attribute | Value |
| :--- | :--- |
| **Document ID** | STD-05 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Head of Engineering |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.8.25, A.8.28), SOC 2 TSC (CC7.1, CC8.1), NIST CSF 2.0 (PR.DS-07) |

## 1. Purpose
To define the minimum security requirements and practices for developing, testing, and maintaining software applications at [COMPANY_NAME] to prevent vulnerabilities and ensure code integrity.
*(ISO/IEC 27001:2022 A.8.25, A.8.28, SOC 2 CC7.1, CC8.1, NIST CSF 2.0 PR.DS-07)*

## 2. Scope
Applies to all software development activities (internal or contracted) for applications, APIs, scripts, and infrastructure-as-code used or produced by [COMPANY_NAME].

## 3. Secure Development Lifecycle (SDLC) Integration

Security must be integrated at every phase of the software development lifecycle:
*   **Requirements:** Security and compliance requirements must be defined for all new projects.
*   **Design:** Threat modeling should be conducted for critical applications to identify potential design flaws.
*   **Development:** Developers must adhere to secure coding guidelines (e.g., OWASP Top 10).
*   **Testing:** Security testing (SAST, DAST, SCA) must be performed before release.
*   **Deployment:** Changes must go through a formal Change Management process.

## 4. Secure Coding Principles

Developers must adhere to recognized secure coding standards, such as the OWASP Secure Coding Practices. Key areas include:

### 4.1 Input Validation and Output Encoding
*   **Validation:** All user input (form fields, API parameters, headers) must be strictly validated against an allowlist of expected characters, types, and lengths.
*   **Encoding:** All data output to a browser or interpreter must be properly context-encoded to prevent Cross-Site Scripting (XSS) and injection attacks.

### 4.2 Authentication and Session Management
*   Implement secure password storage using strong, salted hashes (e.g., Argon2, bcrypt).
*   Do not hardcode credentials or API keys in source code. Use a secure secrets management solution (e.g., AWS Secrets Manager, HashiCorp Vault).
*   Ensure session tokens are securely generated, transmitted over HTTPS, marked as `HttpOnly` and `Secure`, and invalidated upon logout or timeout.

### 4.3 Access Control
*   Enforce Principle of Least Privilege: Code should only have the permissions necessary to perform its function.
*   Implement robust authorization checks at the server side for every request to sensitive resources (prevent Insecure Direct Object References - IDOR).

### 4.4 Error Handling and Logging
*   Do not expose sensitive information (e.g., stack traces, database queries) to end-users in error messages.
*   Log security-relevant events (logins, failures, access to sensitive data, administrative actions) centrally, ensuring sensitive data (e.g., passwords, PII) is scrubbed or masked from logs.

## 5. Code Review and Supply Chain Security

### 5.1 Peer Review and Approval Matrix
*(ISO/IEC 27001:2022 A.8.28, A.8.32)*
- **Standard Changes:** Must have at least 1 peer approval from an authorized engineer before merging into protected branches.
- **Tier-1 / High-Risk / Security Changes:** Must mandate 2 approvals, including at least one designated security engineer or authorized owner from `CODEOWNERS` before promotion to production. Direct commits to production branches are strictly blocked by branch protection rules.

### 5.2 Secret Scanning
- Pre-commit secret scanning hooks and automated CI/CD secret scanning (e.g., Gitleaks, Trufflehog) must run on all commits and pull requests to detect credentials, tokens, and private keys before code merge.

### 5.3 Software Supply Chain Security and SBOM
- **Software Composition Analysis (SCA):** Automated SCA scanning must run on all third-party dependencies in CI/CD pipelines.
- **Software Bill of Materials (SBOM):** An automated SBOM generation process (conforming to CycloneDX or SPDX standards) must be triggered on every production release to catalog all runtime and compile-time dependencies.

### 5.4 Build Provenance and Artifact Signing
- **Artifact Signing:** All production artifacts, containers, and deployment packages must undergo cryptographic artifact signing using Cosign (Sigstore) with verification enforced by admission controllers prior to deployment.

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | Engineering & Security | [CISO_NAME] | Initial release and modernization with peer review, Tier-1 CODEOWNERS, SBOM, secret scanning, and Cosign signing |
