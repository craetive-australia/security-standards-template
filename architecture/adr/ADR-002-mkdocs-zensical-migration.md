# ADR-002: MkDocs & Material for MkDocs Architecture and Zensical Migration Roadmap

- **Status**: Accepted (Phased Evolution)
- **Date**: 2026-10-31
- **Deciders**: Information Security Architecture Team, DevOps / Tooling Engineering
- **Technical Context**: Documentation Engine Architecture, Material for MkDocs Deprecation, Static Site Generation

## Context and Problem Statement

The `security-standards-template` documentation portal is rendered using `mkdocs` (v1.6.1) with the `mkdocs-material` theme (v9.8.0). This engine produces the static HTML website representing the organization's public and internal Information Security Management System (ISMS) portal across 39+ markdown documents.

The maintainers of Material for MkDocs have formally announced that official support, active development, and maintenance for `mkdocs-material` will reach End-of-Life (EOL) on **May 5, 2027**. Its creator and core team are developing **Zensical**, a next-generation static site generation and documentation framework built for modern performance and web standards.

Currently, invoking `mkdocs build` generates an informational deprecation notice on stderr warning developers of the impending May 2027 transition:
```text
INFO     -  Deprecation warning: mkdocs-material will reach EOL on May 5, 2027...
```
In strict CI/CD environments (`mkdocs build --strict`), stderr output or unhandled deprecation notices can introduce friction or false alarms. The project requires an architectural decision regarding documentation tooling, immediate warning suppression, and the long-term migration plan to Zensical.

## Decision Drivers

- Guarantee 100% backward compatibility with existing v1.0 build pipelines, test suites (`test_tier2_mkdocs_build.py`), and local developer workflows.
- Suppress build-time deprecation warnings cleanly in development and automated CI/CD runs.
- Prevent vendor lock-in to proprietary, non-standard markdown extensions or theme-specific hacks.
- Establish an orderly, risk-free roadmap for adopting Zensical before the May 2027 EOL milestone.

## Considered Options

1. **Immediate Hard Cutover to Zensical**: Replace `mkdocs` with `zensical` immediately for v2.0 release.
   - *Risk*: `zensical` is currently in active pre-1.0 development (`zensical 0.0.72` in `.venv`). Immediate cutover could introduce breaking changes or CLI incompatibilities with third-party CI runners.
2. **Status Quo Without Guardrails**: Continue using `mkdocs-material` without addressing the deprecation notice or planning for migration.
   - *Risk*: Build logs accumulate warnings; emergency migration required near the 2027 deadline.
3. **Phased Evolution**: Retain `mkdocs-material` for v2.0 with standardized warning suppression (`NO_MKDOCS_2_WARNING=1`), author all markdown and configuration strictly compatible with Zensical, and plan formal cutover well in advance of May 2027.

## Decision Outcome

Chosen option: **Option 3 — Phased Evolution**.

### Phase 1: Operational Stability for v2.0 (Immediate)
1. **Engine Retention**: Continue using `mkdocs` 1.6.1 and `mkdocs-material` 9.8.0 as the primary production static documentation generator.
2. **Warning Suppression**: Mandate `NO_MKDOCS_2_WARNING=1` across all build scripts, GitHub Actions workflows, test runners, and developer commands. This cleanly suppresses the EOL banner without masking legitimate warnings or link breakage.
3. **Strict Markdown Standards**: Restrict all markdown features to standard PyMdown extensions:
   - `admonition`
   - `tables`
   - `pymdownx.superfences`
   - `pymdownx.tabbed`
   - `pymdownx.details`
   - `pymdownx.highlight`
   - `pymdownx.snippets`
   Avoid proprietary JavaScript overrides or non-portable theme hooks.

### Phase 2: Dual Compatibility & Soak Testing (2026 Q4 – 2027 Q1)
1. Maintain experimental evaluation testing using `zensical` (installed as a dev dependency).
2. Validate that navigation structure (`nav` in `mkdocs.yml`), relative markdown link graphs, and header/footer tables render equivalently under Zensical.
3. Track Zensical upstream releases as it approaches 1.0 General Availability.

### Phase 3: Production Cutover (Target: 2027 Q1)
1. Complete formal cutover to Zensical well before the May 5, 2027 EOL deadline.
2. Update CI/CD pipelines and deployment scripts with zero impact to documentation source files (`docs/**/*.md`).

## Pros and Cons of the Selected Option

### Pros
- **Zero Disruption**: Existing CI/CD workflows, automated link validators, and developer habits remain completely unbroken.
- **Clean Builds**: Setting `NO_MKDOCS_2_WARNING=1` ensures `mkdocs build --strict` runs with zero stderr noise.
- **Future-Proof**: Adhering to portable markdown standards ensures the upcoming cutover to Zensical will require only configuration adjustments, not content rewrites.

### Cons
- **Dual Dependency Maintenance**: Development environments will temporarily carry both `mkdocs-material` and `zensical` packages until cutover.

## References

- Material for MkDocs Deprecation & EOL Notice: <https://squidfunk.github.io/mkdocs-material/>
- Zensical Documentation Platform: <https://zensical.org/>
- MkDocs User Guide: <https://www.mkdocs.org/>
