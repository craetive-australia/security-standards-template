# Internal Audit and CAPA Register

| Attribute | Value |
| :--- | :--- |
| **Document ID** | REG-05 |
| **Version** | 1.0 |
| **Effective Date** | [INSERT_DATE] |
| **Document Owner** | [CISO_NAME] / Internal Audit Lead |
| **Review Cycle** | Annual |
| **Classification** | Internal |
| **Framework Mappings** | ISO/IEC 27001:2022 (9.2, 9.3, 10.1, 10.2), SOC 2 TSC (CC2.1, CC5.3), NIST CSF 2.0 (GV.OC-01) |

*(ISO/IEC 27001:2022 Clauses 9.2, 9.3, 10.1, 10.2; SOC 2 CC2.1, CC5.3; NIST CSF 2.0 GV.OC-01)*

**Purpose**: To plan, document, and track the execution of internal audits across [COMPANY_NAME], record nonconformities and audit findings, monitor Corrective and Preventive Actions (CAPA), and record executive Management Review minutes and action items.

---

## 1. Annual Internal Audit Schedule

The internal audit program ensures that all ISMS domains, clauses (ISO 27001:2022 Clauses 4–10), and Statement of Applicability controls (Annex A.5–A.8) are audited across an annual cycle by qualified, objective auditors independent of the area being audited.

| Audit ID | Planned Quarter | Target Domain / Standard Area | Scope & Objectives | Lead Auditor | Audit Status | Report Date |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| AUD-202X-Q1 | Q1 | Organizational Controls & Governance | ISO 27001 Clauses 4–10, Annex A.5 (Policies, Asset Mgt, Supplier) | Lead Auditor | Completed | YYYY-03-15 |
| AUD-202X-Q2 | Q2 | People & Physical Security | Annex A.6 (HR Security, Remote Work), Annex A.7 (Physical) | Lead Auditor | Completed | YYYY-06-20 |
| AUD-202X-Q3 | Q3 | Technological Controls & SDLC | Annex A.8 (Access, Crypto, Network, Secure Coding, Vulnerability) | Lead Auditor | Scheduled | YYYY-09-25 |
| AUD-202X-Q4 | Q4 | Incident Management & Business Continuity | Annex A.5.24–A.5.30 (IRP, BCP, DRP, Breach Notification) | Lead Auditor | Scheduled | YYYY-12-10 |

---

## 2. Internal Audit Findings Log

All observations, nonconformities (Major and Minor), and Opportunities for Improvement (OFI) identified during internal audits are cataloged below.

| Finding ID | Audit Ref | Clause / Control Ref | Finding Classification | Detailed Description of Deficiency | Identified By | Identified Date | CAPA Assigned | Target Closure Date | Finding Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| FND-202X-01 | AUD-202X-Q1 | ISO 27001:2022 A.5.18 | Minor Nonconformity | Monthly access reviews for privileged AWS roles missing documentation for 2 consecutive months | Lead Auditor | YYYY-03-10 | CAPA-202X-01 | YYYY-04-15 | Closed |
| FND-202X-02 | AUD-202X-Q2 | ISO 27001:2022 A.6.3 | OFI (Opportunity for Improvement) | Security awareness training completion rates for contractors tracked in disparate spreadsheets | Lead Auditor | YYYY-06-18 | CAPA-202X-02 | YYYY-07-31 | Closed |
| FND-202X-03 | AUD-202X-Q3 | ISO 27001:2022 A.8.28 | Minor Nonconformity | Two pull requests to infrastructure repository merged without second CODEOWNERS security review | Lead Auditor | YYYY-09-22 | CAPA-202X-03 | YYYY-10-30 | In Progress |

---

## 3. Corrective and Preventive Action (CAPA) Log

Every identified nonconformity, security incident root cause, or control failure triggers a structured CAPA investigation utilizing root-cause analysis (e.g., 5-Whys).

| CAPA ID | Finding / Incident Ref | Root Cause Analysis | Corrective Action Description (Immediate Fix) | Preventive Action Description (Systemic Fix) | Action Owner | Target Due Date | Verification Method | Status | Sign-off Date |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| CAPA-202X-01 | FND-202X-01 | Manual reminder process failed during staffing transition | Re-executed privileged access review immediately and evidenced removals | Automated Jira ticket generation on the 1st of each month with automated escalations | IAM Lead | YYYY-04-15 | Verification of ticket logs and approvals | Closed | YYYY-04-14 |
| CAPA-202X-02 | FND-202X-02 | Contractor onboarding LMS integration was not centralized | Centralized contractor list imported into primary HR LMS | Webhook sync between Contractor VMS and Security Training LMS | HR Lead | YYYY-07-31 | LMS report showing 100% contractor completion | Closed | YYYY-07-28 |
| CAPA-202X-03 | FND-202X-03 | Branch protection rules bypassed via admin override during emergency hotfix | Re-reviewed hotfix code retrospectively; verified no vulnerabilities | Restricted branch protection bypass permissions; mandated emergency exception log | DevOps Lead | YYYY-10-30 | GitHub audit log review | Open | — |

---

## 4. Management Review Minutes Template

Executive management conducts formal ISMS reviews at least annually (and following significant incidents) in accordance with ISO/IEC 27001:2022 Clause 9.3.

### 4.1 Meeting Details
- **Meeting Date:** [INSERT_DATE]
- **Chairperson:** [CISO_NAME]
- **Attendees:** Chief Executive Officer, Chief Technology Officer, VP of Engineering, Head of Legal & Compliance, Lead Internal Auditor
- **Secretary / Minutes Recorder:** ISMS Governance Lead

### 4.2 Agenda & Discussion Topics
1. **Status of Actions from Previous Reviews:** Status of prior CAPAs and management review commitments.
2. **Changes in External & Internal Context:** Regulatory shifts (e.g., NIS2, SEC rules, DORA), organizational growth, new technology adoption (e.g., Generative AI).
3. **Information Security Performance & Feedback:**
   - Security incident trends and metrics (Sev1/Sev2 post-mortem SLAs compliance).
   - Internal audit findings and nonconformity resolution rates.
   - Vulnerability and patch management metrics (CISA KEV and CVSS SLAs).
   - Results of annual penetration testing and tabletop exercises.
4. **Stakeholder Feedback & Compliance Obligations:** Customer questionnaire responses, contractual compliance, regulatory audits.
5. **Risk Assessment Results & Risk Treatment Plan Status:** Review of [Risk Register](02_Risk_Register.md) changes, residual risks, and active exceptions.
6. **Opportunities for Continual Improvement:** Resource allocation, automation enhancements, tooling investments.

### 4.3 Executive Decisions and Action Items

| Action ID | Decision / Action Item Summary | Responsible Owner | Target Completion Date | Resource / Budget Allocation |
| :--- | :--- | :--- | :--- | :--- |
| MR-ACT-01 | Approved procurement of automated secret scanning and Cosign signing tooling | VP Engineering | YYYY-11-30 | Allocated in Q4 Engineering Budget |
| MR-ACT-02 | Approved 202X+1 ISMS objectives and updated Statement of Applicability | [CISO_NAME] | YYYY-12-15 | Existing staff capacity |
| MR-ACT-03 | Executive approval of updated Risk Treatment Plan and residual risk posture | CEO | YYYY-10-15 | Approved without conditions |

---

## Document History

| Version | Date | Author | Approved By | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [INSERT_DATE] | Internal Audit & Quality | [CISO_NAME] | Initial release and standardization of Audit Schedule, Findings, CAPA, and Management Review |
