# Djux App Conventions

These conventions keep official apps predictable and easy to install, update, and test.

## Naming

- Registry names use lowercase letters, digits, and hyphens: `ai-chat`, `api-keys`.
- Python package folders use underscores when needed: `api_keys`, `ai_chat`.
- The install folder defaults to the registry name unless the user chooses a different folder during a collision prompt.
- Django app labels must avoid collisions with built-in Django apps where possible.
- Official repositories use `djux-app-<name>` for app packages and `djux-registry` for the registry.

## Repository layout

```text
djux-app-example/
  djux.json
  README.md
  app/
    __init__.py
    apps.py
    models.py
    serializers.py
    views.py
    urls.py
    admin.py
    migrations/
      __init__.py
```

The `app/` directory is copied into the user's project. Keep packaging, docs, and development-only files outside `app/`.

## Django app config

`apps.py` must declare a stable app label. If the folder name is generic or conflicts with Django, use a label that is safe for migrations.

```python
from django.apps import AppConfig


class ExampleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "example"
    label = "example_app"
```

If `label` is used, any `AUTH_USER_MODEL`, foreign keys, or migration dependencies must refer to that label.

## API conventions

- Prefer DRF serializers and class-based views for API apps.
- Keep endpoint names stable once released.
- Use plural resource endpoints unless the app is an action-style utility.
- Put all app routes in `app/urls.py`; Djux mounts them at `url_prefix`.

## Settings conventions

- Use `settings_patch` only for settings the app truly needs.
- Settings patches must be valid Python and idempotent when possible.
- Do not overwrite global project settings unless unavoidable.
- Prefer app-specific setting names for optional behavior.

## Migration conventions

- Include `app/migrations/__init__.py` in every app.
- Set `migrations` to `true` when the app creates or changes database tables.
- Avoid data migrations in early template apps unless the behavior is essential.

## Quality conventions

Every official app needs a README, valid manifest, passing Django system check after install, migration verification, and an API smoke test when it exposes endpoints.
