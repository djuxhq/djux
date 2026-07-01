# Security Policy

## Supported versions

Djux is early-stage. Security fixes should target the latest `main` branch unless a release branch is created later.

## Reporting a vulnerability

Please do not open a public issue for a vulnerability.

For now, report security concerns by contacting the maintainers through GitHub. Include:

- Affected repository and version or commit.
- Steps to reproduce.
- Impact and affected behavior.
- Any suggested fix, if known.

## Scope

Relevant issues include:

- Unsafe code execution during app install.
- Path traversal or unsafe archive extraction.
- Registry download integrity problems.
- Secrets exposed by templates or generated projects.
- Auth or permission bugs in official apps.

## Registry safety

Djux apps are code. Review app repositories before installing them, especially community apps. Official apps should follow the smoke-test checklist and registry conventions, but users should still inspect copied code before production use.