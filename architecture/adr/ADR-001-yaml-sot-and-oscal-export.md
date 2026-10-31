# ADR-001: YAML Single Source of Truth (SSOT) and OSCAL v1.2.0 Export Engine

- **Status**: Accepted
- **Date**: 2026-10-31
- **Deciders**: Information Security Architecture Team, Compliance Engineering
- **Technical Context**: Modernization Roadmap v2.0, Multi-Framework Compliance-as-Code

## Context and Problem Statement

The `security-standards-template` repository manages 98 canonical controls (`CC-GV-01` through `CC-AU-07`) spanning 14 security domains. Under the v2.0 modernization roadmap, these controls map across six disparate regulatory and cybersecurity frameworks:
1. ISO/IEC 27001:2022 (Annex A, 93 controls)
2. AICPA SOC 2 (2017/2022 Trust Services Criteria, 61 criteria)
3. NIST Cybersecurity Framework (CSF) 2.0 (106 official subcategories)
4. European Union General Data Protection Regulation (GDPR, core articles)
5. NIST SP 800-53 Rev. 5 (Moderate baseline across all 20 families `AC` through `SR`)
6. Australian Cyber Security Centre (ACSC) ASD Essential Eight (Maturity Levels 1–3, 8 strategies, and mapped ASD Information Security Manual controls)

Historically, crosswalk matrices and control mapping tables were authored and updated manually within static Markdown policy documents. This approach suffered from critical operational drawbacks:
- **Documentation Drift**: Control edits in individual policy files frequently diverged from the Statement of Applicability (SoA) and framework crosswalks.
- **Audit Overhead**: External auditors and compliance assessors required manual reconciliation between policy text and external audit checklists.
- **Lack of Programmatic Interoperability**: Modern GRC platforms, FedRAMP assessment pipelines, and automated intake tooling require standardized, machine-readable representations adhering to the NIST Open Security Controls Assessment Language (OSCAL) v1.2.0 standard.

## Decision Drivers

- Establish a single, authoritative, machine-readable definition for every security control and framework crosswalk.
- Enable automated compilation of human-readable documentation without manual copy-paste errors.
- Support deterministic, offline export of official OSCAL v1.2.0 JSON models to interoperate with federal, enterprise, and third-party compliance tooling.
- Provide strict schema validation against modern JSON Schema Draft 2020-12 specifications.

## Considered Options

1. **Markdown-First (Status Quo)**: Author crosswalks directly in Markdown documentation and write parsers to extract structured data.
2. **Database / SaaS GRC Platform**: Shift control management to an external database or commercial GRC API.
3. **YAML Single Source of Truth (SSOT) with Automated Documentation and OSCAL Export Engine**: Store all canonical controls, domain definitions, document links, and crosswalk relationships in a validated YAML registry, generating both Markdown documentation and OSCAL v1.2.0 artifacts programmatically.

## Decision Outcome

Chosen option: **Option 3 — YAML Single Source of Truth (SSOT) with Automated Documentation and OSCAL Export Engine**.

### Specific Architectural Implementations

1. **Authoritative Registry (`mappings/framework_registry.yaml`)**:
   - Upgraded to schema version `2.0.0` with strict validation via `schemas/framework_registry.schema.json`.
   - Defines the canonical control hierarchy across 14 domains (`CC-GV-01` through `CC-AU-07`).
   - Maintains explicit mappings to ISO 27001:2022, ISO 27001:2013 legacy, SOC 2 TSC 2017, NIST CSF 2.0, GDPR, NIST SP 800-53 Rev. 5, and ASD Essential Eight.
   - Eliminates all duplicate keys and replaces null representations with explicit typed structures.

2. **Automated Markdown Crosswalk Generation (`scripts/generate_docs.py`)**:
   - Compiles `mappings/framework_registry.yaml` and reference catalogs into `docs/01_ISMS_Framework/08_Multi_Framework_Crosswalk_and_OSCAL_Matrix.md`.
   - Enforces bidirectional link verification between controls and implementing repository documents.
   - Employs a `--check` flag in CI/CD pipelines to prevent uncommitted documentation drift.

3. **Deterministic OSCAL v1.2.0 Export Engine (`scripts/export_oscal.py`)**:
   - Generates five standardized OSCAL JSON artifacts in `dist/oscal/`:
     - `dist/oscal/catalog.json`: Canonical ISMS control catalog.
     - `dist/oscal/mapping_collection.json`: Multi-framework crosswalk and relationship linkages.
     - `dist/oscal/profile_e8_ml2.json`: ASD Essential Eight Maturity Level 2 baseline profile.
     - `dist/oscal/profile_nist_800_53_moderate.json`: NIST SP 800-53 Rev. 5 Moderate baseline profile.
     - `dist/oscal/component_definition.json`: Implementation components linking repository policies to controls.
   - Enforces 100% byte-determinism using RFC 4122 UUIDv5 hashing based on fixed namespace identifiers (`6ba7b810-9dad-11d1-80b4-00c04fd430c8` or `isms.security-standards-template.local`).
   - Validates generated JSON models against `schemas/oscal_v1_2_0_subset.schema.json`.

4. **Directory Isolation**:
   - ADR files are stored strictly in `architecture/adr/` outside `docs/` to isolate internal architectural governance records from the public-facing MkDocs static documentation build and strict navigation parity tests.

## Pros and Cons of the Selected Option

### Pros
- **Single Source of Truth**: All control updates occur once in `mappings/framework_registry.yaml`, propagating automatically to docs and OSCAL exports.
- **Determinism**: Identical inputs yield bit-for-bit identical OSCAL JSON files, eliminating spurious git diffs.
- **Audit Readiness**: Delivers both human-readable documentation for assessors and machine-readable OSCAL bundles for automated ingestion.
- **Offline Reliability**: OSCAL generation and schema validation require zero external network dependencies.

### Cons
- **Tooling Complexity**: Requires Python automation scripts and schema validation suites in CI/CD.
- **Build Discipline**: Contributors must run `generate_docs.py` and `export_oscal.py` when modifying control metadata.

## References

- NIST OSCAL v1.2.0 Specification: <https://pages.nist.gov/OSCAL/>
- JSON Schema Draft 2020-12: <https://json-schema.org/draft/2020-12/schema>
- ISO/IEC 27001:2022 Information Security Management Systems
- RFC 4122: A Universally Unique Identifier (UUID) URN Namespace
