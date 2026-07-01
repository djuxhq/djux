# Djux App Manifest Spec

This is the Phase 1 baseline for `djux.json`. App manifests should stay small, explicit, and safe to apply repeatedly.

## Required fields

| Field | Type | Rule |
|---|---|---|
| `name` | string | Registry key. Lowercase letters, digits, and hyphens only. |
| `version` | string | Semver, for example `0.1.0`. |
| `description` | string | One-line summary shown in registry listings. |
| `installed_apps` | string[] | Django `INSTALLED_APPS` entries to add. |
| `url_prefix` | string | URL prefix where `app/urls.py` is included. |
| `dependencies` | string[] | pip requirements with sensible lower bounds. |

## Optional fields

| Field | Type | Rule |
|---|---|---|
| `migrations` | boolean | If true, `djux add` runs `python manage.py migrate`. |
| `settings_patch` | string | Valid Python inserted above `# djux:settings`. |
| `env_vars` | string[] | Environment variable names displayed after install. |
| `notes` | string | Post-install message. |
| `requires_apps` | string[] | Djux apps that must already be installed. |
| `requires_djux` | string | Minimum Djux CLI version. |
| `tags` | string[] | Discovery tags. |
| `author` | string | Maintainer or organization. Official apps use `djuxhq`. |
| `update_notes` | string | Human-readable notes for future update tooling. |

## Versioning rules

- Use semver: `MAJOR.MINOR.PATCH`.
- Patch versions are bug fixes that should not require manual migration work.
- Minor versions can add endpoints, fields, settings, or migrations.
- Major versions can include breaking API, model, or settings changes.
- Every registry entry must match the app repo's `djux.json` version.

## Update behavior baseline

Existing installs are vendored into the user's project. Future update tooling must not overwrite user-modified files blindly.

`djux update <app>` should eventually:

1. Read installed app name and version from `djux.project.json`.
2. Fetch the latest registry entry and manifest.
3. Compare versions.
4. Download the new package.
5. Apply dependency, settings, URL, and migration changes idempotently.
6. Copy unchanged files directly.
7. Write `.new` files or a conflict report for locally modified files.
8. Record the new installed version only after a successful update.

## Official app registry rules

Official app registry entries should use:

- `author`: `djuxhq`
- `repo`: `https://github.com/djuxhq/<repo>`
- `download`: `https://github.com/djuxhq/<repo>/archive/refs/heads/main.zip`
