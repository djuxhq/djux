# djux

**djux** is a CLI and registry for adding production-ready Django app templates to a project in one command. It handles the repetitive setup work: app files, Django settings, URL wiring, pip dependencies, and migrations.

```bash
pip install djux

djux new myproject
cd myproject

djux add auth
```

Think of it as a Django app installer where the installed code is copied into your project so you can own it, edit it, and ship it like normal Django code.

## Vision

Djux aims to make reusable Django app templates easier to discover, install, inspect, and customize. The project is intentionally open to community feedback: the registry should grow around apps Django developers actually want, with a safe update story for vendored app code.

Current focus:

- Core app templates such as `auth`, `users`, `api-keys`, and `files`.
- AI-ready templates such as `ai-models`, `ai-prompts`, `ai-chat`, `ai-usage`, and `ai-rag`.
- A safer update workflow for copied app code: `djux outdated` and `djux update <app>`.

See [APP_ROADMAP.md](APP_ROADMAP.md) for the full roadmap.

## Installation

Requires Python 3.10+.

```bash
pip install djux
```

Verify:

```bash
djux --version
```

## Quick start

```bash
# 1. Create a new project
djux new myproject
cd myproject

# 2. Set up your environment
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# 3. Run initial migrations and start the server
python manage.py migrate
python manage.py runserver

# 4. Add apps
djux add auth
```

See [docs/getting-started.md](docs/getting-started.md) for a full walkthrough.

## Available apps

| Name | Description | Tags |
|---|---|---|
| `auth` | JWT authentication: register, login, logout, refresh, me | `auth` `jwt` `api` |
| `users` | User profiles, avatars, preferences | planned |
| `api-keys` | API keys, scopes, rotation, revocation | planned |
| `ai-chat` | Basic chat API with conversation history | planned `ai` |
| `ai-models` | Provider/model registry and model selection | planned `ai` |

```bash
djux list
```

## How it works

`djux add <app>` currently:

1. Looks up the app in the registry.
2. Downloads and extracts the app zip from GitHub.
3. Validates the `djux.json` manifest.
4. Copies the `app/` folder into your project's `apps/` directory.
5. Patches `config/settings.py` with `INSTALLED_APPS` entries and settings blocks.
6. Patches `config/urls.py` with the route include.
7. Runs `pip install` for declared dependencies.
8. Runs `python manage.py migrate` if the app has migrations.
9. Records the installed app in `djux.project.json`.

Installed apps are vendored into the project. That means developers fully own the copied code after install.

## Project layout

```text
myproject/
|-- config/
|   |-- settings.py        # djux patches INSTALLED_APPS here
|   `-- urls.py            # djux adds URL includes here
|-- apps/                  # all Django apps land here
|-- templates/
|-- static/
|-- manage.py
|-- djux.project.json      # tracks installed apps
`-- requirements.txt
```

## Documentation

| Document | Contents |
|---|---|
| [Getting started](docs/getting-started.md) | Install, scaffold, first app, what changed |
| [CLI reference](docs/cli-reference.md) | Commands, options, errors |
| [Creating apps](docs/creating-apps.md) | Build and publish a djux app |
| [Manifest spec](docs/manifest-spec.md) | `djux.json` contract and versioning rules |
| [App conventions](docs/app-conventions.md) | Naming, layout, settings, migrations |
| [Update design](docs/update-design.md) | Planned `djux outdated` and `djux update <app>` flow |
| [Smoke test checklist](docs/smoke-test-checklist.md) | Quality checklist for official apps |
| [Registry](docs/registry.md) | Registry format, caching, custom registries |

## Repositories

| Repo | Purpose |
|---|---|
| [djuxhq/djux](https://github.com/djuxhq/djux) | CLI and project template |
| [djuxhq/djux-registry](https://github.com/djuxhq/djux-registry) | Registry index |
| [djuxhq/djux-app-auth](https://github.com/djuxhq/djux-app-auth) | Official auth app |

## Contributing

Contributors and testers are welcome. Useful ways to help:

- Build official app templates.
- Test Djux in real Django projects.
- Improve the CLI and update workflow.
- Review app manifests and registry entries.
- Improve documentation.

Start with [CONTRIBUTING.md](CONTRIBUTING.md), then check the roadmap and open issues.

## License

MIT