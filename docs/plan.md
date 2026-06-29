# djx — Detailed Requirements Document

> **Purpose of this document:** Complete specification for building the `djx` CLI tool and ecosystem from scratch. Hand this to Claude Code to implement the full system.

---

## 1. Project Overview

**djx** is a CLI tool and app registry for Django. It lets developers add production-ready, pre-built Django apps into their projects with a single command — handling all the wiring (settings, urls, migrations, dependencies) automatically.

Think of it as `npm` for Django apps, combined with an opinionated project scaffold.

### Core user flow

```bash
pip install djx

djx new myproject        # scaffold a new opinionated Django project
cd myproject

djx add auth             # adds full JWT auth app, wires everything automatically
djx add chat             # adds WebSocket chat app
djx list                 # browse available apps
djx remove auth          # cleanly removes an app
```

### Design principles

- **Convention over configuration** — every djx project has the same layout so the CLI always knows where to look
- **Zero manual wiring** — `djx add` patches `settings.py`, `urls.py`, installs pip deps, runs migrations automatically
- **Open registry** — anyone can publish an app; a curated set of official apps is maintained separately
- **Pure Django underneath** — djx is a scaffold + CLI layer; it does not fork or modify Django itself

---

## 2. Repository Structure

The project lives across multiple GitHub repositories:

```
djx/                        ← Main CLI package (this repo, published to PyPI)
djx-registry/               ← Registry index (registry.json lives here)
djx-app-auth/               ← Official auth app
djx-app-chat/               ← Official chat app
djx-app-support/            ← Official support/tickets app
djx-app-notifications/      ← Official notifications app
```

### CLI repo layout

```
djx/
├── pyproject.toml
├── README.md
├── djx/
│   ├── __init__.py
│   ├── cli.py                    ← Click group, registers all commands
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── new.py                ← `djx new`
│   │   ├── add.py                ← `djx add`
│   │   ├── remove.py             ← `djx remove`
│   │   ├── list.py               ← `djx list`
│   │   └── publish.py            ← `djx publish` (future)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── registry.py           ← Registry fetch/cache logic
│   │   ├── patcher.py            ← settings.py and urls.py patching
│   │   ├── downloader.py         ← Download and extract app zips
│   │   └── manifest.py           ← djx.json parsing and validation
│   └── templates/
│       └── project_template/     ← Copied by `djx new`
│           ├── config/
│           │   ├── __init__.py
│           │   ├── settings.py
│           │   ├── urls.py
│           │   ├── wsgi.py
│           │   └── asgi.py
│           ├── apps/             ← Empty; djx add drops apps here
│           ├── templates/        ← Django HTML templates
│           ├── static/           ← Static files
│           ├── manage.py
│           ├── djx.project.json  ← Project marker + installed app tracking
│           ├── requirements.txt
│           ├── .env.example
│           └── .gitignore
├── apps/
│   └── auth/                     ← Reference app (also lives in djx-app-auth repo)
│       ├── djx.json
│       └── app/
│           ├── __init__.py
│           ├── apps.py
│           ├── models.py
│           ├── serializers.py
│           ├── views.py
│           ├── urls.py
│           └── migrations/
│               └── __init__.py
└── tests/
    ├── test_new.py
    ├── test_add.py
    ├── test_patcher.py
    └── fixtures/
```

---

## 3. Project Template Spec (`djx new`)

When a user runs `djx new myproject`, the CLI copies the `project_template/` directory and replaces `{{project_name}}` in all files.

### 3.1 Directory layout (generated project)

```
myproject/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/               ← All Django apps live here, not root
├── templates/          ← Global HTML templates
├── static/             ← Global static files
├── manage.py
├── djx.project.json    ← djx marker file
├── requirements.txt
├── .env.example
└── .gitignore
```

### 3.2 `config/settings.py` requirements

- `BASE_DIR` points to project root (parent of `config/`)
- `apps/` directory is inserted into `sys.path` so apps inside it are importable without an `apps.` prefix
- `SECRET_KEY` read from environment variable `SECRET_KEY`, with a dev fallback
- `DEBUG` read from environment variable `DEBUG`, default `True`
- `ALLOWED_HOSTS` read from environment variable `ALLOWED_HOSTS`, split on spaces
- `INSTALLED_APPS` contains Django defaults plus an anchor comment `# djx:installed_apps` at the end of the list — the CLI injects above this line
- `DATABASES` defaults to SQLite at `BASE_DIR / db.sqlite3`
- `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT` configured
- `TEMPLATES` configured with `BASE_DIR / templates` as a template directory
- `ROOT_URLCONF = "config.urls"`
- `DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"`

### 3.3 `config/urls.py` requirements

- Imports `path`, `include` from `django.urls`
- Contains `admin/` route
- Contains anchor comment `# djx:urls` inside `urlpatterns` — the CLI injects above this line

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    # djx:urls
]
```

### 3.4 `djx.project.json` (marker file)

```json
{
  "djx_version": "0.1.0",
  "project": "{{project_name}}",
  "installed_apps": []
}
```

This file serves two purposes:
1. Signals to the CLI that this is a djx project root (CLI walks up from cwd to find it)
2. Tracks which djx apps have been installed (CLI updates this on `add`/`remove`)

### 3.5 `requirements.txt`

```
Django>=4.2,<6.0
python-dotenv>=1.0
```

### 3.6 `.env.example`

```
SECRET_KEY=change-me-to-a-long-random-string
DEBUG=True
ALLOWED_HOSTS=localhost 127.0.0.1
```

### 3.7 `.gitignore`

Standard Django gitignore: `__pycache__`, `*.pyc`, `.env`, `db.sqlite3`, `staticfiles/`, `.venv/`

---

## 4. App Package Spec

Every djx app — whether official or community-published — must follow this structure.

### 4.1 Directory layout

```
your-app/
├── djx.json            ← Manifest (required)
├── app/                ← The Django app code (required)
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py  ← If DRF-based
│   ├── admin.py
│   └── migrations/
│       └── __init__.py
├── README.md
└── requirements.txt    ← Optional, supplements djx.json dependencies
```

### 4.2 `djx.json` manifest spec

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | ✅ | Unique app identifier, lowercase, hyphens ok |
| `version` | string | ✅ | Semver e.g. `"0.1.0"` |
| `description` | string | ✅ | One-line description shown in `djx list` |
| `installed_apps` | string[] | ✅ | Values to append to `INSTALLED_APPS` |
| `url_prefix` | string | ✅ | URL prefix e.g. `"api/auth/"` |
| `dependencies` | string[] | ✅ | pip packages to install e.g. `["djangorestframework>=3.15"]` |
| `env_vars` | string[] | ❌ | Env vars the user must set, shown post-install |
| `migrations` | boolean | ❌ | Whether to run `manage.py migrate` after install, default `false` |
| `notes` | string | ❌ | Post-install message shown to user |
| `requires_djx` | string | ❌ | Minimum djx version required |
| `tags` | string[] | ❌ | Tags for discovery e.g. `["auth", "jwt", "api"]` |
| `author` | string | ❌ | Publisher name or GitHub username |
| `requires_apps` | string[] | ❌ | Other djx apps that must be installed first |

**Example:**

```json
{
  "name": "auth",
  "version": "0.1.0",
  "description": "JWT authentication — register, login, logout, refresh, me endpoint",
  "installed_apps": ["auth_app", "rest_framework", "rest_framework_simplejwt"],
  "url_prefix": "api/auth/",
  "dependencies": [
    "djangorestframework>=3.15",
    "djangorestframework-simplejwt>=5.3"
  ],
  "env_vars": [],
  "migrations": true,
  "tags": ["auth", "jwt", "api"],
  "author": "djx-dev",
  "notes": "Endpoints: POST /api/auth/register/ /api/auth/login/ /api/auth/refresh/ GET /api/auth/me/"
}
```

---

## 5. Registry Spec

### 5.1 Structure

The registry is a single `registry.json` file hosted in the `djx-registry` GitHub repository. The raw URL is:

```
https://raw.githubusercontent.com/djx-dev/registry/main/registry.json
```

### 5.2 `registry.json` format

```json
{
  "version": "1",
  "apps": {
    "auth": {
      "version": "0.1.0",
      "description": "JWT authentication — register, login, logout, refresh, me",
      "tags": ["auth", "jwt", "api"],
      "author": "djx-dev",
      "official": true,
      "repo": "https://github.com/djx-dev/djx-app-auth",
      "download": "https://github.com/djx-dev/djx-app-auth/archive/refs/heads/main.zip"
    },
    "chat": { ... },
    "support": { ... }
  }
}
```

### 5.3 Registry caching

- The CLI caches `registry.json` locally at `~/.djx/registry.json`
- Cache TTL: 1 hour
- `djx list --refresh` forces a fresh fetch
- If network is unavailable, fall back to cache with a warning

### 5.4 Community publishing (future)

Anyone can submit a PR to `djx-registry` adding their app. The PR template requires:
- App repo is public
- `djx.json` is valid
- App has a README
- App has at least one passing test

Official apps (marked `"official": true`) are maintained by `djx-dev` and reviewed more strictly.

---

## 6. CLI Commands — Full Spec

### 6.1 `djx new <project_name>`

**Purpose:** Scaffold a new djx Django project.

**Behaviour:**
1. Check that `<project_name>` directory does not already exist in cwd; error if it does
2. Copy `project_template/` to `./<project_name>/`
3. Walk all files, replace `{{project_name}}` placeholder with the actual name
4. Print success panel with next steps

**Output on success:**
```
Creating project: myproject

╭─────────────── 🚀 Ready ───────────────╮
│ ✓ Project created: myproject/          │
│                                        │
│   cd myproject                         │
│   python -m venv .venv                 │
│   source .venv/bin/activate            │
│   pip install -r requirements.txt      │
│   cp .env.example .env                 │
│   python manage.py migrate             │
│   python manage.py runserver           │
│                                        │
│   Then add apps:  djx add auth         │
╰────────────────────────────────────────╯
```

**Errors:**
- Directory already exists → `✗ Directory 'myproject' already exists.`

---

### 6.2 `djx add <app_name>`

**Purpose:** Download an app from the registry and install it into the current project.

**Options:**
- `--registry <url>` — use a custom registry URL (default: official registry)

**Steps (in order):**

1. **Find project root** — walk up from cwd looking for `djx.project.json`; error if not found
2. **Check if already installed** — read `djx.project.json`; warn and exit if app is already listed
3. **Fetch registry** — GET registry URL; parse JSON; error if app name not found
4. **Download zip** — stream download to a temp directory; show spinner
5. **Extract zip** — unzip; handle GitHub's extra top-level folder in zip structure
6. **Validate manifest** — parse `djx.json`; error if required fields are missing
7. **Check dependencies** — if `requires_apps` is set, verify those apps are already installed
8. **Copy app code** — copy `app/` folder to `<project_root>/apps/<app_name>/`
9. **Patch `settings.py`** — append each entry in `installed_apps` above `# djx:installed_apps` if not already present
10. **Patch `urls.py`** — add `path("<prefix>", include("<app_name>.urls")),` above `# djx:urls` if not already present
11. **Install pip dependencies** — run `pip install` for each entry in `dependencies`
12. **Run migrations** — if `migrations: true`, run `python manage.py migrate` from project root
13. **Update `djx.project.json`** — append app name to `installed_apps` array
14. **Print success** — show installed app name, any required env vars, and notes

**Output on success:**
```
⠋ Fetching registry...
✓ Found auth v0.1.0
✓ Downloaded
✓ App files copied to apps/
✓ settings.py updated
✓ urls.py updated
✓ Dependencies installed
✓ Migrations applied

✓ auth added successfully!

Required environment variables:
  • REDIS_URL   (if applicable)

Notes: Endpoints: POST /api/auth/register/ /api/auth/login/ ...
```

**Errors:**
- Not in a djx project → `✗ No djx project found. Run this inside a djx project.`
- App not in registry → `✗ App 'xyz' not found in registry. Run djx list to see available apps.`
- App already installed → `⚠ App 'auth' is already installed.`
- Missing `djx.json` in downloaded package → `✗ App is missing djx.json manifest.`
- Dependency app not installed → `✗ App 'auth' requires 'notifications' to be installed first. Run: djx add notifications`

---

### 6.3 `djx remove <app_name>`

**Purpose:** Remove an installed app from the project.

**Options:**
- `--yes` — skip confirmation prompt

**Steps:**

1. Find project root
2. Check app exists in `apps/<app_name>/`; error if not
3. Prompt for confirmation unless `--yes`
4. Delete `apps/<app_name>/` directory
5. Remove all entries the app added from `INSTALLED_APPS` in `settings.py`
6. Remove the app's URL include line from `urls.py`
7. Remove app from `installed_apps` in `djx.project.json`
8. Print success with migration note

**Note:** Does NOT run `python manage.py migrate` automatically — user must do this manually to handle database cleanup for apps with models.

---

### 6.4 `djx list`

**Purpose:** Show all apps available in the registry.

**Options:**
- `--registry <url>` — use a custom registry URL
- `--refresh` — bypass cache and fetch fresh registry

**Output:**

```
┌─────────────────── Available djx Apps ───────────────────┐
│ Name          Version  Description                  Tags  │
│ auth          0.1.0    JWT authentication — ...     auth  │
│ chat          0.1.0    WebSocket chat with rooms    chat  │
│ support       0.1.0    Support ticket system        ...   │
│ notifications 0.1.0    In-app notifications + SSE   ...   │
└───────────────────────────────────────────────────────────┘

  Install any app:  djx add <name>
```

---

### 6.5 `djx publish` (future — spec only)

**Purpose:** Help developers publish their app to the registry.

**Behaviour:**
1. Validate that cwd contains a valid `djx.json`
2. Validate manifest fields
3. Validate that `app/` directory exists with required files
4. Output a ready-to-submit PR template linking to the registry repo

---

## 7. Core Modules — Implementation Detail

### 7.1 `core/patcher.py`

Responsible for modifying `settings.py` and `urls.py`.

**`patch_installed_apps(settings_path, apps: list[str])`**
- Read file as text
- For each app name, check if it already appears as a quoted string (`"appname"` or `'appname'`)
- If not present, insert `    "appname",` on the line above `# djx:installed_apps`
- Write file back

**`unpatch_installed_apps(settings_path, apps: list[str])`**
- For each app name, remove the line containing the quoted app name
- Write file back

**`patch_urls(urls_path, app_name: str, prefix: str)`**
- Check if `app_name` already appears in file
- If not, insert `    path("<prefix>", include("<app_name>.urls")),` on the line above `# djx:urls`
- Ensure `include` is imported; if not, add it to the import line
- Write file back

**`unpatch_urls(urls_path, app_name: str)`**
- Remove the line containing `include("<app_name>`
- Write file back

**Important:** All patching must be idempotent — running it twice must not duplicate entries.

---

### 7.2 `core/registry.py`

**`fetch_registry(url: str) -> dict`**
- Check cache at `~/.djx/registry.json` and its timestamp
- If cache is fresh (< 1 hour old), return cached version
- Otherwise fetch from URL with 10s timeout
- On success, write to cache with current timestamp
- On network failure, fall back to cache with warning; error if no cache exists

**`get_app(registry: dict, app_name: str) -> dict | None`**
- Return the app entry or None

---

### 7.3 `core/downloader.py`

**`download_and_extract(download_url: str, app_name: str) -> Path`**
- Stream download zip to `tempfile.mkdtemp()`
- Extract with `zipfile.ZipFile`
- GitHub archives wrap contents in a top-level folder (e.g. `djx-app-auth-main/`) — detect and unwrap this automatically
- Return path to the extracted app root (the folder containing `djx.json`)

---

### 7.4 `core/manifest.py`

**`parse_manifest(path: Path) -> dict`**
- Read and parse `djx.json`
- Validate required fields: `name`, `version`, `description`, `installed_apps`, `url_prefix`, `dependencies`
- Raise `InvalidManifestError` with a clear message if any required field is missing or the wrong type

---

## 8. Official Reference Apps

### 8.1 `auth` app

Full JWT authentication system.

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register/` | Create account, returns tokens |
| POST | `/api/auth/login/` | Login with email+password, returns tokens |
| POST | `/api/auth/refresh/` | Refresh access token |
| POST | `/api/auth/logout/` | Blacklist refresh token |
| GET | `/api/auth/me/` | Get current user profile |

**Models:** Custom `User` extending `AbstractUser` with `email` as `USERNAME_FIELD`

**Dependencies:** `djangorestframework`, `djangorestframework-simplejwt`

**Settings injected:**
```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ]
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}
AUTH_USER_MODEL = "auth_app.User"
```

---

### 8.2 `chat` app (spec only — to be built)

WebSocket-based real-time chat.

**Features:** Chat rooms, message history, online presence indicator

**Dependencies:** `channels`, `daphne`

**Required env vars:** `REDIS_URL`

---

### 8.3 `support` app (spec only — to be built)

Support ticket system.

**Features:** Ticket creation, status tracking (open/pending/resolved), admin panel integration, email notifications

**Dependencies:** None beyond Django

---

### 8.4 `notifications` app (spec only — to be built)

In-app notification system.

**Features:** Create notifications, mark read/unread, SSE-based real-time push, notification count badge API

**Dependencies:** None beyond Django

---

## 9. `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "djx"
version = "0.1.0"
description = "Django extensions CLI — add production-ready apps in one command"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
dependencies = [
    "click>=8.1",
    "requests>=2.31",
    "rich>=13.0",
]

[project.scripts]
djx = "djx.cli:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["djx*"]

[tool.setuptools.package-data]
djx = ["templates/**/*", "templates/**/.*"]
```

---

## 10. Error Handling Standards

All user-facing errors must follow this format:

```
✗ <short error message>
  <optional one-line hint>
```

Examples:
```
✗ No djx project found. Run this inside a djx project.

✗ App 'xyz' not found in registry.
  Run djx list to see available apps.

✗ App is missing djx.json manifest.
  The downloaded package at github.com/user/repo does not have a djx.json file.

✗ Network error: could not reach registry.
  Using cached registry from 2 hours ago.
```

All errors exit with a non-zero status code.

---

## 11. Testing Requirements

Tests live in `tests/`. Use `pytest`.

### Required test coverage:

**`test_new.py`**
- `djx new myproject` creates correct directory structure
- `{{project_name}}` is replaced in all files
- Running twice on same name fails with clear error

**`test_patcher.py`**
- `patch_installed_apps` correctly injects app names
- `patch_installed_apps` is idempotent (running twice doesn't duplicate)
- `patch_urls` correctly injects url includes
- `patch_urls` adds `include` import if missing
- `unpatch_installed_apps` correctly removes app names
- `unpatch_urls` correctly removes url lines

**`test_add.py`** (uses mocked registry and download)
- Full `djx add` flow with mocked HTTP completes without error
- `djx.project.json` is updated after install
- Error raised when not in a djx project
- Error raised when app not in registry
- Error raised when manifest is missing required fields

---

## 12. What NOT to Build (Explicit Exclusions)

- Do **not** fork or modify Django itself
- Do **not** build a web UI or dashboard for the registry (CLI only for now)
- Do **not** build a custom authentication system for publishing (GitHub PR flow is sufficient)
- Do **not** implement `djx publish` beyond a validation + PR template generator
- Do **not** support non-djx project layouts — the CLI only works inside projects created by `djx new`

---

## 13. Open Questions (Decide Before Building)

1. **Settings injection for apps that need their own settings block** (e.g. `auth` needs `SIMPLE_JWT = {...}` and `AUTH_USER_MODEL`) — should this be a separate `settings_patch` field in `djx.json`, or a `settings_fragment.py` file in the app package?

2. **App naming collision** — if the user has an existing `auth` folder in their project, should `djx add auth` error, warn-and-overwrite, or install to a different name?

3. **`djx update <app_name>`** — should this be in scope for v0.2? Would require version tracking in `djx.project.json`.

4. **Monorepo vs separate repos** — are the official apps maintained as separate GitHub repos (one per app) or as a monorepo? Separate repos are cleaner for versioning; a monorepo is easier to maintain early on.