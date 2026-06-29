# CLI reference

Complete reference for all `djux` commands.

---

## Global options

```
djux [OPTIONS] COMMAND [ARGS]...
```

| Option | Description |
|---|---|
| `--version` | Show the installed djux version and exit |
| `--help` | Show help for any command |

---

## djux new

Scaffold a new djux Django project.

```
djux new <project_name>
```

### What it does

1. Checks that `<project_name>/` does not already exist in the current directory
2. Copies the built-in project template to `./<project_name>/`
3. Replaces `{{project_name}}` in every file
4. Prints next-step instructions

### Arguments

| Argument | Description |
|---|---|
| `project_name` | Name of the project directory to create |

### Output

```
Creating project: myproject

╭─────────────── Ready ───────────────╮
│ ✓ Project created: myproject/       │
│                                     │
│   cd myproject                      │
│   python -m venv .venv              │
│   source .venv/bin/activate         │
│   pip install -r requirements.txt   │
│   cp .env.example .env              │
│   python manage.py migrate          │
│   python manage.py runserver        │
│                                     │
│   Then add apps:  djux add auth      │
╰─────────────────────────────────────╯
```

### Errors

| Condition | Message |
|---|---|
| Directory already exists | `✗ Directory 'myproject' already exists.` |

### Generated project structure

```
myproject/
├── config/
│   ├── __init__.py
│   ├── settings.py        ← reads SECRET_KEY, DEBUG, ALLOWED_HOSTS from .env
│   ├── urls.py            ← contains # djux:urls anchor
│   ├── wsgi.py
│   └── asgi.py
├── apps/                  ← djux drops app folders here; on sys.path
├── templates/
├── static/
├── manage.py
├── djux.project.json       ← project marker + installed app tracking
├── requirements.txt       ← Django>=4.2, python-dotenv>=1.0
├── .env.example
└── .gitignore
```

---

## djux add

Download and install an app from the registry into the current project.

```
djux add <app_name> [--registry <url>]
```

### Arguments

| Argument | Description |
|---|---|
| `app_name` | Name of the app to install (must exist in the registry) |

### Options

| Option | Default | Description |
|---|---|---|
| `--registry <url>` | Official registry | Use a custom registry URL |

### What it does

Steps run in this order:

1. Walks up from the current directory to find `djux.project.json` (project root)
2. Checks `djux.project.json` — warns and exits if the app is already installed
3. Fetches the registry (uses 1-hour cache; falls back to cache if offline)
4. Downloads the app zip from the registry's `download` URL
5. Extracts the zip, unwrapping GitHub's top-level folder automatically
6. Validates `djux.json` — checks all required fields
7. Checks `requires_apps` — errors if a dependency app is not yet installed
8. Copies the `app/` folder to `<project_root>/apps/<app_name>/`
9. Patches `config/settings.py` — adds `installed_apps` entries above `# djux:installed_apps`
10. Patches `config/settings.py` — injects `settings_patch` block above `# djux:settings` (if present)
11. Patches `config/urls.py` — adds URL include above `# djux:urls`
12. Runs `pip install` for each entry in `dependencies`
13. Runs `python manage.py migrate` if `migrations: true` in the manifest
14. Updates `djux.project.json` to record the installed app

All patching is idempotent — running `djux add auth` twice is safe.

### Naming collision

If `apps/<app_name>/` already exists, djux prompts you instead of overwriting:

```
Warning: Directory 'apps/auth' already exists.
  Enter a new name to install as (or leave empty to cancel): auth_v2
  Installing as 'auth_v2'
```

Rules for the alternate name:
- Lowercase letters, digits, and underscores only
- Must start with a letter
- Pattern: `^[a-z][a-z0-9_]*$`

Pressing Enter (empty input) cancels the installation.

When installed under a different name, the URL include and `djux.project.json` use the new name. The `INSTALLED_APPS` entries (declared in `djux.json`) stay unchanged because they're Django app labels, not folder names.

### Output

```
✓ Found auth v0.1.0
✓ Downloaded
✓ App files copied to apps/auth/
✓ settings.py updated
✓ urls.py updated
✓ Dependencies installed
✓ Migrations applied

✓ auth added successfully!

Notes: Endpoints: POST /api/auth/register/ ...
```

### Errors

| Condition | Message |
|---|---|
| Not inside a djux project | `✗ No djux project found. Run this inside a djux project.` |
| App already installed | `⚠ App 'auth' is already installed.` |
| App not found in registry | `✗ App 'xyz' not found in registry. Run djux list to see available apps.` |
| Missing djux.json in download | `✗ App is missing djux.json manifest.` |
| Missing required field in djux.json | `✗ djux.json is missing required field: 'version'` |
| Dependency app not installed | `✗ App 'chat' requires 'auth' to be installed first. Run: djux add auth` |
| Missing app/ directory | `✗ App package is missing the 'app/' directory.` |
| pip install failed | `✗ pip install failed:` + stderr |
| migrate failed | `✗ migrate failed:` + stderr |
| Network error, no cache | `✗ Network error: could not reach registry.` |
| Network error, cache available | Warning printed to stderr; cached registry is used |

---

## djux remove

Remove an installed app from the project.

```
djux remove <app_name> [--yes]
```

### Arguments

| Argument | Description |
|---|---|
| `app_name` | Name of the installed app to remove (must match the folder name in `apps/`) |

### Options

| Option | Description |
|---|---|
| `--yes` | Skip the confirmation prompt |

### What it does

1. Finds the project root
2. Checks that `apps/<app_name>/` exists
3. Prompts for confirmation (skipped with `--yes`)
4. Reads `djux.json` from `apps/<app_name>/` before deleting (to know what to unpatch)
5. Deletes `apps/<app_name>/` recursively
6. Removes `INSTALLED_APPS` entries from `config/settings.py`
7. Removes the `settings_patch` block from `config/settings.py` (if one exists)
8. Removes the URL include from `config/urls.py`
9. Removes the app from `djux.project.json`

> **Note:** `djux remove` does **not** run `python manage.py migrate`. If the app added database tables, run it yourself after removal to clean up the schema.

### Output

```
✓ settings.py updated
✓ urls.py updated

✓ auth removed.

Note: If this app had database models, run python manage.py migrate to clean up the database.
```

### Errors

| Condition | Message |
|---|---|
| Not inside a djux project | `✗ No djux project found. Run this inside a djux project.` |
| App not found | `✗ App 'auth' is not installed (no directory at apps/auth/).` |
| Confirmation declined | Exits cleanly with no changes |

---

## djux list

Show all apps available in the registry.

```
djux list [--registry <url>] [--refresh]
```

### Options

| Option | Description |
|---|---|
| `--registry <url>` | Use a custom registry URL |
| `--refresh` | Bypass the 1-hour cache and fetch a fresh copy |

### Output

```
┌──────────────────── Available djux apps ─────────────────────┐
│ Name     Version  Description                          Tags  │
│ auth ★   0.1.0    JWT authentication — register, ...  auth  │
└─────────────────────────────────────────────────────────────┘

  Install any app:  djux add <name>
  ★ = official djux app
```

Official apps (marked `★`) are maintained by the djux team.

---

## djux publish

Validate your app directory and generate a registry PR template.

```
djux publish
```

Run this from the root of your app directory (the folder containing `djux.json`).

### What it validates

1. `djux.json` exists and all required fields are present and correctly typed
2. `app/` directory exists with `__init__.py`, `apps.py`, `models.py`, `views.py`, `urls.py`
3. `README.md` exists

### Output on success

```
✓ Manifest valid — myapp v0.1.0
✓ app/ directory looks good
✓ README.md found

Your app is ready to submit!

1. Push your app to a public GitHub repo
2. Open a PR to the djux registry:
   https://github.com/browndevv/djux-registry/compare

PR body template:
---
## New app: myapp
...
---
```

### Errors

| Condition | Message |
|---|---|
| Missing or invalid `djux.json` | `✗ djux.json is missing required field: 'version'` |
| Missing `app/` directory | `✗ Missing 'app/' directory.` |
| Missing files inside `app/` | `✗ Missing required files in app/: admin.py, serializers.py` |
| Missing `README.md` | `✗ Missing README.md — required for registry submission.` |

---

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Error (message printed to stdout) |

`djux add` also exits `0` when the user cancels a naming collision prompt.
