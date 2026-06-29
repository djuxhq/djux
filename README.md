# djx

**djx** is a CLI tool that adds production-ready Django apps to your project in a single command — handling settings, URLs, pip dependencies, and migrations automatically.

```bash
pip install djx

djx new myproject          # scaffold a new Django project
cd myproject

djx add auth               # JWT auth: register, login, refresh, me endpoint
djx add chat               # WebSocket chat with rooms
djx list                   # browse all available apps
djx remove auth            # cleanly removes app + wiring
```

Think of it as `npm install` for Django apps, combined with an opinionated project scaffold.

---

## Installation

Requires Python 3.10+.

```bash
pip install djx
```

Verify:

```bash
djx --version
```

---

## Quick start

```bash
# 1. Create a new project
djx new myproject
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
djx add auth
```

See [docs/getting-started.md](docs/getting-started.md) for a full walkthrough.

---

## Available apps

| Name | Description | Tags |
|---|---|---|
| `auth` | JWT authentication — register, login, logout, refresh, me | `auth` `jwt` `api` |
| `chat` | WebSocket chat with rooms and presence *(coming soon)* | `chat` `ws` |
| `support` | Support ticket system with admin integration *(coming soon)* | `support` |
| `notifications` | In-app notifications with SSE push *(coming soon)* | `notifications` `sse` |

```bash
djx list           # always shows the current registry
```

---

## How it works

`djx add <app>` runs 14 steps automatically:

1. Looks up the app in the registry
2. Downloads and extracts the app zip from GitHub
3. Validates the `djx.json` manifest
4. Copies the `app/` folder into your project's `apps/` directory
5. Patches `config/settings.py` — injects `INSTALLED_APPS` entries
6. Patches `config/urls.py` — adds the URL include
7. Runs `pip install` for all declared dependencies
8. Runs `python manage.py migrate` if the app has models

Everything is idempotent. Running `djx add auth` twice is safe.

---

## Project layout

djx projects have a fixed layout so the CLI always knows where to look:

```
myproject/
├── config/
│   ├── settings.py        ← djx patches INSTALLED_APPS here
│   └── urls.py            ← djx adds URL includes here
├── apps/                  ← all Django apps land here
├── templates/
├── static/
├── manage.py
├── djx.project.json       ← tracks installed apps
└── requirements.txt
```

---

## Documentation

| Document | Contents |
|---|---|
| [Getting started](docs/getting-started.md) | Install, scaffold, first app, what changed |
| [CLI reference](docs/cli-reference.md) | Every command, every option, every error message |
| [Creating apps](docs/creating-apps.md) | Build and publish your own djx app |
| [Registry](docs/registry.md) | How the registry works, caching, custom registries |

---

## Repositories

| Repo | Purpose |
|---|---|
| [browndevv/djx](https://github.com/browndevv/djx) | This repo — CLI and project template |
| [browndevv/djx-registry](https://github.com/browndevv/djx-registry) | Registry index (`registry.json`) |
| [browndevv/djx-app-auth](https://github.com/browndevv/djx-app-auth) | Official auth app |

---

## Contributing

To contribute an app to the registry, build it following the [app spec](docs/creating-apps.md), then run `djx publish` from your app directory for a ready-to-submit PR template.

To contribute to the CLI itself, open a PR against [browndevv/djx](https://github.com/browndevv/djx).

---

## License

MIT
