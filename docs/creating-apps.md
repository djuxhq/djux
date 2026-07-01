# Creating apps

This guide explains how to build a djux-compatible app and submit it to the registry.

## Overview

A djux app is a standard Django app packaged with a `djux.json` manifest. When someone runs `djux add yourapp`, the CLI downloads your app, copies it into their `apps/` directory, and uses the manifest to wire everything up automatically.

## Directory structure

See [App Conventions](app-conventions.md) for naming, layout, Django app config, settings, migration, and API conventions.

```text
your-app/                  # GitHub repo root
|-- djux.json              # Manifest (required)
|-- app/                   # The Django app (required)
|   |-- __init__.py
|   |-- apps.py
|   |-- models.py
|   |-- views.py
|   |-- urls.py
|   |-- admin.py
|   |-- serializers.py     # If DRF-based
|   `-- migrations/
|       `-- __init__.py
|-- README.md              # Required for registry submission
`-- requirements.txt       # Optional, same content as djux.json dependencies
```

The `app/` directory is what gets copied into the user's project. Everything else stays in your repo.

## The djux.json manifest

See [Manifest Spec](manifest-spec.md) for the Phase 1 baseline manifest contract, update behavior, and versioning rules.

`djux.json` is the single source of truth for how the CLI installs your app.

### Required fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Unique identifier. Lowercase, hyphens allowed. Must match your registry entry. |
| `version` | string | Semver string, e.g. `"0.1.0"`. |
| `description` | string | One-line description shown in `djux list`. |
| `installed_apps` | string[] | Entries to add to Django's `INSTALLED_APPS`. |
| `url_prefix` | string | URL prefix for the app's routes, e.g. `"api/auth/"`. |
| `dependencies` | string[] | pip packages to install, with version specifiers. |

### Optional fields

| Field | Type | Description |
|---|---|---|
| `migrations` | boolean | If `true`, runs `python manage.py migrate` after install. Default `false`. |
| `settings_patch` | string | Raw Python code injected into `config/settings.py`. |
| `env_vars` | string[] | Environment variable names the user must set. Shown post-install. |
| `notes` | string | Message shown to the user after successful install. |
| `requires_apps` | string[] | Other djux apps that must be installed first. |
| `requires_djux` | string | Minimum djux version required. |
| `tags` | string[] | Tags for discovery, e.g. `["auth", "jwt", "api"]`. |
| `author` | string | Your name or GitHub username. Official apps use `djuxhq`. |

### Minimal example

```json
{
  "name": "myapp",
  "version": "0.1.0",
  "description": "Does something useful",
  "installed_apps": ["myapp"],
  "url_prefix": "api/myapp/",
  "dependencies": []
}
```

### Full example - the auth app

```json
{
  "name": "auth",
  "version": "0.1.0",
  "description": "JWT authentication - register, login, logout, refresh, me endpoint",
  "installed_apps": [
    "auth",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist"
  ],
  "url_prefix": "api/auth/",
  "dependencies": [
    "djangorestframework>=3.15",
    "djangorestframework-simplejwt>=5.3"
  ],
  "migrations": true,
  "tags": ["auth", "jwt", "api"],
  "author": "djuxhq",
  "notes": "Endpoints: POST /api/auth/register/ /api/auth/login/ /api/auth/refresh/ /api/auth/logout/ GET /api/auth/me/",
  "settings_patch": "from datetime import timedelta\n\nREST_FRAMEWORK = {\n    \"DEFAULT_AUTHENTICATION_CLASSES\": [\n        \"rest_framework_simplejwt.authentication.JWTAuthentication\",\n    ]\n}\nSIMPLE_JWT = {\n    \"ACCESS_TOKEN_LIFETIME\": timedelta(minutes=60),\n    \"REFRESH_TOKEN_LIFETIME\": timedelta(days=7),\n}\nAUTH_USER_MODEL = \"auth_app.User\""
}
```

## The settings_patch field

If your app needs extra settings beyond `INSTALLED_APPS` entries, such as `REST_FRAMEWORK`, `SIMPLE_JWT`, or `CELERY_BROKER_URL`, use `settings_patch`.

The value is a string of raw Python code. djux injects it into `config/settings.py` above the `# djux:settings` anchor. It is injected verbatim, so it must be valid Python.

```json
{
  "settings_patch": "MYAPP_SETTING = 'value'\nMYAPP_TIMEOUT = 30"
}
```

Result in `settings.py`:

```python
MYAPP_SETTING = 'value'
MYAPP_TIMEOUT = 30

# djux:settings
```

When `djux remove` is run, the block is removed automatically.

## The app/ directory

The `app/` folder is a standard Django app. A few conventions to follow:

`apps.py` should set `name` to the importable Django app module and optionally set `label` when needed for migration-safe names:

```python
from django.apps import AppConfig


class MyAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "myapp"
```

`urls.py` should define a `urlpatterns` list; these routes are included at the prefix from `djux.json`.

Always include `migrations/__init__.py`, even if your app has no models. Set `"migrations": false` in `djux.json` if you have no models.

## installed_apps vs the folder name

The entries in `installed_apps` are Django app labels/modules. These are independent of the folder name in `apps/`.

When a user installs your app under a custom name because of a collision, the folder name changes but your `installed_apps` entries stay the same. Make sure your `apps.py` config matches what you declare in `djux.json`.

## Testing locally

Use the [Official App Smoke Test Checklist](smoke-test-checklist.md) before publishing an official app.

Before submitting to the registry, test your app against a real djux project:

```bash
# In a djux project, use --registry to point at a local JSON file
djux add myapp --registry file:///path/to/local-registry.json
```

Or use the dev path directly: copy your `app/` folder into `apps/myapp/`, manually add entries to `settings.py` and `urls.py`, and run `python manage.py migrate`.

## Validating before submission

Run `djux publish` from your app directory:

```bash
cd your-app/
djux publish
```

This checks:

- `djux.json` has all required fields with the correct types.
- `app/` exists with `__init__.py`, `apps.py`, `models.py`, `views.py`, and `urls.py`.
- `README.md` is present.

Fix any reported errors before opening a PR.

## Submitting to the registry

1. Push your app to a public GitHub repository.
2. Run `djux publish` to confirm everything is valid.
3. Open a PR to [djuxhq/djux-registry](https://github.com/djuxhq/djux-registry) adding your app to `registry.json`.

```json
{
  "version": "1",
  "apps": {
    "existing-app": { "...": "..." },
    "your-app": {
      "version": "0.1.0",
      "description": "Short description",
      "tags": ["tag1", "tag2"],
      "author": "your-github-username",
      "official": false,
      "repo": "https://github.com/you/your-app",
      "download": "https://github.com/you/your-app/archive/refs/heads/main.zip"
    }
  }
}
```

The `download` URL must point to a zip that contains `djux.json` and `app/` at its root after GitHub's wrapper folder is stripped.

### PR checklist

- [ ] App repo is public.
- [ ] `djux publish` passes with no errors.
- [ ] `README.md` exists and explains what the app does.
- [ ] At least one passing test exists in the app repo.
- [ ] `download` URL resolves to a valid zip.

## Versioning

See [Update Design](update-design.md) for the planned `djux outdated` and `djux update <app>` workflow.

Update the `version` field in `djux.json` and your registry entry when you release changes. djux does not currently enforce version pinning; early `djux add` installs may download the latest `main` branch. The registry entry version is shown in `djux list` and `djux add` output.
