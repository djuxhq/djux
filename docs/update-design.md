# Djux Update Design

Djux apps are vendored into the user's project. That gives developers full control, but updates require careful merge behavior.

## Commands

```bash
djux outdated
djux update <app>
djux update --all
```

## Project state

`djux.project.json` should eventually store structured app metadata instead of only a list of names.

```json
{
  "djux_version": "0.1.0",
  "project": "example",
  "installed_apps": ["auth"],
  "apps": {
    "auth": {
      "version": "0.1.0",
      "installed_as": "auth",
      "source": "https://github.com/djuxhq/djux-app-auth",
      "manifest_hash": "sha256:..."
    }
  }
}
```

## Update algorithm

1. Resolve the installed app from `djux.project.json`.
2. Fetch the registry and latest manifest.
3. Compare installed and latest versions.
4. Download and validate the latest app archive.
5. Build a file manifest for the installed copy and the new copy.
6. For unchanged local files, replace with the new version.
7. For locally modified files, write `<file>.new` and record a conflict.
8. Patch settings and URLs idempotently.
9. Install or upgrade dependencies.
10. Run migrations when required.
11. Update `djux.project.json` only after all required steps pass.

## Conflict policy

Never silently overwrite a file that differs from the version Djux originally installed. For conflicts, prefer explicit user action over clever merging.

Recommended conflict output:

```text
apps/auth/views.py was modified locally.
Wrote apps/auth/views.py.new with the latest upstream version.
Review and merge manually, then delete the .new file.
```

## Registry requirements for update support

The registry should eventually include immutable release URLs and checksums. Main-branch zip URLs are acceptable for early development, but releases are safer for update tooling.
