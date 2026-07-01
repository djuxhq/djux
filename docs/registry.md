# Registry

The djux registry is a single `registry.json` file hosted on GitHub. It lists every app available to install.

## Default registry

```text
https://raw.githubusercontent.com/djuxhq/djux-registry/main/registry.json
```

This is the URL `djux list` and `djux add` use by default.

## registry.json format

```json
{
  "version": "1",
  "apps": {
    "auth": {
      "version": "0.1.0",
      "description": "JWT authentication - register, login, logout, refresh, me endpoint",
      "tags": ["auth", "jwt", "api"],
      "author": "djuxhq",
      "official": true,
      "repo": "https://github.com/djuxhq/djux-app-auth",
      "download": "https://github.com/djuxhq/djux-app-auth/archive/refs/heads/main.zip"
    }
  }
}
```

## Top-level fields

| Field | Type | Description |
|---|---|---|
| `version` | string | Registry schema version. Currently `"1"`. |
| `apps` | object | Map of app name to app entry. |

## App entry fields

| Field | Type | Description |
|---|---|---|
| `version` | string | Current version of the app. Informational and shown in `djux list` and `djux add` output. |
| `description` | string | One-line description shown in `djux list`. |
| `tags` | string[] | Discovery tags. |
| `author` | string | Publisher name or GitHub username. Official apps use `djuxhq`. |
| `official` | boolean | `true` for apps maintained by the djux team. |
| `repo` | string | URL of the app's GitHub repository. |
| `download` | string | URL of the zip archive that `djux add` downloads. |

For GitHub repos, use the archive URL format:

```text
https://github.com/<owner>/<repo>/archive/refs/heads/main.zip
```

## Caching

The CLI caches the registry locally to keep `djux add` fast and work offline.

Cache location: `~/.djux/registry.json`
Cache TTL: 1 hour
Metadata: `~/.djux/registry.meta.json`

| Situation | What happens |
|---|---|
| Cache exists and is less than 1 hour old | Served from cache; no network request. |
| Cache exists but is older than 1 hour | Fetched fresh; cache updated. |
| Network fails, cache exists | Warning printed to stderr; stale cache used. |
| Network fails, no cache | Fatal error. |

Force a fresh fetch:

```bash
djux list --refresh
```

## Using a custom registry

Both `djux add` and `djux list` accept a `--registry` option:

```bash
djux list --registry https://example.com/my-registry.json
djux add myapp --registry https://example.com/my-registry.json
```

A local file URL also works during development:

```bash
djux add myapp --registry file:///path/to/local-registry.json
```

## Adding an app to the registry

Apps are added to the registry by opening a pull request to [djuxhq/djux-registry](https://github.com/djuxhq/djux-registry).

See [creating-apps.md](creating-apps.md) for the full submission process, including how to run `djux publish` to validate your app before opening the PR.

## Official apps

Apps marked `"official": true` are maintained by the djux team and reviewed more strictly. Community apps are welcome and reviewed for basic safety: public repo, valid manifest, and working download URL.
