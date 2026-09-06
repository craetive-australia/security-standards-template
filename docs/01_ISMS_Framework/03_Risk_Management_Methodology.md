# Risk Management Methodology

| Attribute | Value |
| :--- | :--- |
| **Document ID** | ISMS-STD-01 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Chief Information Security Officer |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (Clause 6.1.2, 6.1.3), SOC 2 TSC (CC3.1, CC3.2), NIST CSF 2.0 (ID.RA-01, ID.RA-02, ID.RA-03), GDPR (Art. 32, 35) |

## 1. Purpose *(ISO 27001 6.1.2, SOC 2 CC3.1, CC3.2)*
This document establishes [COMPANY_NAME]'s methodology for identifying, assessing, evaluating, and treating information security risks. The goal is to ensure risks are managed proactively and kept within acceptable levels.

## 2. Risk Assessment Process *(ISO 27001 6.1.2)*
The risk assessment process is conducted at least annually or upon significant changes to the environment.

### 2.1 Asset Identification
Identify critical assets (hardware, software, data, personnel) within the ISMS scope.

### 2.2 Threat and Vulnerability Identification
Identify potential threats (e.g., malware, insider threats, natural disasters) and vulnerabilities that could be exploited.

### 2.3 Risk Calculation
Risk is evaluated as a function of the likelihood of threat exploitation and the resulting business impact across confidentiality, integrity, and availability.

**Risk Score = Likelihood × Impact (Scale 1–25)**

#### Likelihood Scale (1–5)
| Level | Rating | Probability | Description |
| :---: | :--- | :--- | :--- |
| **1** | **Rare** | < 10% annual | Highly improbable; exceptional circumstances only; no known industry exploits. |
| **2** | **Unlikely** | 10% – 30% annual | Improbable but conceivable; threat exists but significant barriers prevent exploitation. |
| **3** | **Possible** | 31% – 60% annual | Reasonable probability; threat has occurred elsewhere in industry; moderate barriers. |
| **4** | **Likely** | 61% – 85% annual | High probability; frequent threat attempts observed; weak barriers exist. |
| **5** | **Almost Certain** | > 85% annual | Expected to occur routinely; continuous active targeting or known public exploit. |

#### Impact Scale (1–5)
| Level | Rating | Financial / Operational Impact | Regulatory / Reputational Impact |
| :---: | :--- | :--- | :--- |
| **1** | **Insignificant** | Negligible disruption (< 1 hour); minimal financial loss (< $5k). | No regulatory notification; no brand impact. |
| **2** | **Minor** | Localized disruption (< 4 hours); low financial loss ($5k – $25k). | Minor internal policy violation; no external reporting. |
| **3** | **Moderate** | Partial service outage (< 1 business day); loss ($25k – $100k). | Reportable regulatory breach without fines; localized press. |
| **4** | **Major** | Critical service outage (> 24 hours); severe loss ($100k – $1M). | Major statutory fine (GDPR/SEC); loss of key customer trust. |
| **5** | **Catastrophic** | Systemic multi-day collapse; catastrophic financial loss (> $1M). | Existential regulatory sanctions, license revocation, class action. |

#### 5x5 Risk Matrix Table
The 5x5 matrix combines Likelihood and Impact into a composite Risk Score ranging from 1 to 25:

| Likelihood \ Impact | 1 - Insignificant | 2 - Minor | 3 - Moderate | 4 - Major | 5 - Catastrophic |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **5 - Almost Certain** | 5 (Low) | 10 (Medium) | 15 (High) | 20 (Critical) | 25 (Critical) |
| **4 - Likely** | 4 (Low) | 8 (Medium) | 12 (High) | 16 (High) | 20 (Critical) |
| **3 - Possible** | 3 (Low) | 6 (Medium) | 9 (Medium) | 12 (High) | 15 (High) |
| **2 - Unlikely** | 2 (Low) | 4 (Low) | 6 (Medium) | 8 (Medium) | 10 (Medium) |
| **1 - Rare** | 1 (Low) | 2 (Low) | 3 (Low) | 4 (Low) | 5 (Low) |

#### Risk Level Severity Bands
| Risk Score | Level | Action Required & Treatment SLA |
| :---: | :--- | :--- |
| **1 – 5** | **Low** | Acceptable risk; routine monitoring via standard operational controls. |
| **6 – 11** | **Medium** | Tolerable risk; remediation plan required within 90 days; compensating controls recommended. |
| **12 – 19** | **High** | Unacceptable risk; CISO notification; formal remediation plan executed within 30 days. |
| **20 – 25** | **Critical** | Unacceptable severe emergency; immediate executive escalation; containment within 24–48 hours. |

## 3. Risk Treatment *(ISO 27001 6.1.3)*
For risks exceeding the acceptable threshold (Medium, High, and Critical), [COMPANY_NAME] applies one of the following treatment options:
- **Mitigate:** Apply security controls to reduce likelihood or impact.
- **Transfer:** Shift the risk to a third party (e.g., cyber insurance, managed security services).
- **Avoid:** Discontinue the activity, technology, or business process causing the risk.
- **Accept:** Formal risk acceptance approved by the [CISO_NAME] and Executive Management, logged in the Security Exception & Risk Acceptance Log.

## 4. Risk Reporting and Review
A Risk Register shall be maintained detailing all identified risks, their scores, assigned owners, and treatment plans. Executive management will review the Risk Register quarterly.

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | [AUTHOR_NAME] | [CISO_NAME] | Initial release and harmonization |
