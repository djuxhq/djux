# Contributing

Thanks for helping build Djux.

Djux is a CLI and registry for installing reusable Django app templates. Installed apps are copied into the user's project so developers can inspect and customize the code.

## Ways to help

- Build official app templates.
- Improve CLI commands.
- Test apps in real Django projects.
- Improve documentation.
- Review app manifests and registry entries.

## Local setup

```bash
git clone https://github.com/djuxhq/djux.git
cd djux
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e .
pip install pytest
pytest
```

## App contribution flow

1. Pick an existing issue or propose an app.
2. Create a repo named `djux-app-<name>`.
3. Follow `docs/app-conventions.md`.
4. Add a valid `djux.json` manifest.
5. Run the smoke-test checklist in `docs/smoke-test-checklist.md`.
6. Open a PR to `djuxhq/djux-registry` when the app is ready.

## CLI contribution flow

1. Open or claim an issue.
2. Keep changes scoped.
3. Add or update tests when behavior changes.
4. Run `pytest` before opening a PR.
5. Explain the user-facing impact in the PR body.

## Contribution scope rules

- Claim one issue at a time unless a maintainer agrees to broader scope.
- Open one focused PR per issue.
- Target the current codebase: Djux is a Python package, and CLI changes should modify files under `djux/`.
- Do not add unrelated language stacks, generated scaffolds, or placeholder code.
- Do not include payment wallet requests, bounty claims, or unrelated promotion in issues or PRs.
- If a PR does not match the issue scope or project stack, maintainers may close it without review.

## Quality bar for official apps

Official apps should include:

- `djux.json` manifest.
- README with endpoints and install notes.
- Passing Django system check after install.
- Migration verification when models exist.
- API smoke tests when endpoints exist.
- Registry entry pointing to `djuxhq` URLs.
