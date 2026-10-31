# Secure Software Development Life Cycle (SDLC) & Change Management Policy

| Attribute | Value |
| :--- | :--- |
| **Document ID** | POL-12 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / VP Engineering & AppSec Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (A.8.25, A.8.26, A.8.27, A.8.28, A.8.29, A.8.31, A.8.32, A.8.33), SOC 2 TSC (CC8.1), NIST CSF 2.0 (PR.PS-06, PR.PS-01), GDPR (Art. 25, 32) |

## 1. Purpose
To ensure that strict technical security controls, vulnerability scanning, tiered peer reviews, and supply chain integrity are embedded into the SDLC CI/CD pipeline, and that all production changes are securely managed. *(ISO/IEC 27001:2022 A.8.25, A.8.32, SOC 2 CC8.1, NIST CSF 2.0 PR.PS-06, PR.PS-01)*

## 2. Scope
Applies to all software engineering, internal and outsourced development, and all infrastructure or application changes deployed to [COMPANY_NAME] production environments.

## 3. Policy Statements

### 3.1 Secure Software Development (SDLC)
* **Threat Modeling:** Significant architectural changes require documented threat modeling (e.g., using STRIDE) during the design phase. *(ISO/IEC 27001:2022 A.8.26, SOC 2 CC8.1, NIST CSF 2.0 PR.PS-06)*
* **Tiered Peer Reviews & Branch Protections:** Branch protection rules must be strictly enforced on all code repositories. Direct commits or force pushes to protected branches (`main`, `release/*`) are strictly prohibited.
  * **Standard Changes:** All standard pull requests require a minimum of at least one (1) peer approval from an authorized engineer before merging.
  * **Tier-1 Production & Security Changes:** Changes affecting Tier-1 production systems, core infrastructure, authentication services, or security configurations require a minimum of two (2) approvals, including designated Security / CODEOWNERS. *(SOC 2 CC8.1, NIST CSF 2.0 PR.PS-06)*
* **Software Supply Chain Security:**
  * **Software Bill of Materials (SBOM):** Automated generation of machine-readable SBOMs (CycloneDX or SPDX format) is mandatory for every production release and build artifact.
  * **Secret Scanning:** Mandatory pre-commit hooks and CI/CD automated secret scanning must run across all repositories, automatically blocking commits or builds containing tokens, API keys, or certificates.
  * **Artifact Signing:** Container images, binaries, and release packages must be cryptographically signed via Sigstore / Cosign in the CI pipeline prior to deployment into production clusters.
* **Automated Security Testing in CI/CD:**
  * **SAST & DAST:** Static Application Security Testing (SAST) and Dynamic Application Security Testing (DAST) must run on every pull request. Builds must fail automatically if Critical or High vulnerabilities are identified.
  * **SCA:** Software Composition Analysis (SCA) must continuously inventory and scan third-party dependencies for known vulnerabilities and unapproved licenses.
  * **Container Security:** Container base images must be scanned for CVEs and configuration flaws prior to pushing to container registries. *(ISO/IEC 27001:2022 A.8.25, A.8.28, SOC 2 CC8.1, NIST CSF 2.0 PR.PS-06)*
* **Environment Segregation:** Development, testing/staging, and production environments must run in completely isolated VPCs and cloud accounts. Production data must never be used in lower environments without automated anonymization or pseudonymization. *(ISO/IEC 27001:2022 A.8.31, SOC 2 CC8.1, NIST CSF 2.0 PR.PS-06)*

### 3.2 Change Management
* **Infrastructure as Code (IaC):** All infrastructure changes must be version-controlled, peer-reviewed, and deployed automatically via CI/CD platforms. Manual changes to production servers are strictly prohibited. *(ISO/IEC 27001:2022 A.8.32, A.8.9, SOC 2 CC8.1, NIST CSF 2.0 PR.PS-01)*
* **Ticketing and Traceability:** Every deployment must be traceable to an approved Jira issue containing business justification, risk assessment, and automated rollback plan.
* **Emergency Changes:** "Break-glass" procedures for emergency hotfixes are permitted but must still traverse an automated CI pipeline and require retrospective approval from the Change Advisory Board (CAB) within 48 hours.

## 4. Roles and Responsibilities
- **[CISO_NAME] / AppSec Lead:** Establishes secure coding policies, sets vulnerability blocking thresholds in CI/CD, and reviews Tier-1 CODEOWNERS pull requests.
- **VP Engineering & Development Teams:** Responsible for adhering to secure coding guidelines, participating in peer reviews, and remediating identified flaws.
- **DevSecOps / Release Engineering:** Maintains automated CI/CD security pipelines, SBOM generators, Cosign signing keys, and repository branch protections.
- **Change Advisory Board (CAB):** Reviews high-risk architectural deployments, evaluates infrastructure risk assessments, and audits emergency changes.

## 5. Compliance and Exceptions
- **Compliance:** Enforced programmatically via automated GitHub branch protection rules, mandatory status checks, and Cosign admission controllers in production Kubernetes clusters. Changes bypassing pipeline gates cannot be deployed.
- **Exceptions:** Temporary overrides of CI/CD blocking rules require written justification, documented compensating controls, logging in the [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md) under the Security Exception & Risk Acceptance Log, and approval by both the VP Engineering and the [CISO_NAME].

## 6. Related Documents
- [Secure Coding Standard](../03_Standards_and_Procedures/05_Secure_Coding_Standard.md)
- [Operations Security Policy](05_Operations_Security_Policy.md)
- [Information Security Policy](../01_ISMS_Framework/01_Information_Security_Policy.md)
- [Risk Register](../04_Templates_and_Registers/02_Risk_Register.md)

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Initial release and harmonization |
