# Official App Smoke Test Checklist

Run this checklist before adding or updating an official Djux app in the registry.

## Manifest and package

- [ ] `djux.json` parses as valid JSON.
- [ ] Required manifest fields are present.
- [ ] `version` matches the registry entry.
- [ ] `author` is `djuxhq` for official apps.
- [ ] `repo` and `download` point to `https://github.com/djuxhq/...`.
- [ ] `app/` contains `__init__.py`, `apps.py`, `models.py`, `views.py`, and `urls.py`.
- [ ] `app/migrations/__init__.py` exists.

## Install test

- [ ] Create a fresh project with `djux new smokeproject`.
- [ ] Run `djux add <app>`.
- [ ] Confirm app files exist under `apps/<app>/`.
- [ ] Confirm `config/settings.py` has the expected `INSTALLED_APPS` entries.
- [ ] Confirm `config/urls.py` has the expected route include.
- [ ] Confirm `djux.project.json` records the installed app.

## Django verification

- [ ] `python manage.py check` passes.
- [ ] `python manage.py migrate` passes when the app has migrations.
- [ ] `python manage.py showmigrations <app_label>` shows expected migrations.

## API verification

For API apps, test the happy path and one failure path.

Auth example:

- [ ] `POST /api/auth/register/` returns `201`.
- [ ] `POST /api/auth/login/` returns `200`.
- [ ] `GET /api/auth/me/` returns `200` with a bearer token.
- [ ] `POST /api/auth/refresh/` returns `200`.
- [ ] `POST /api/auth/logout/` returns `205`.
- [ ] Invalid credentials return `401` or `400` as expected.

## Cleanup

- [ ] No generated databases, virtual environments, caches, or local smoke projects are committed.
- [ ] Registry entry is updated after the app repo is ready.
- [ ] README documents install notes, endpoints, environment variables, and known limitations.
