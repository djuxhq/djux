# Registry

The djux registry is a single `registry.json` file hosted on GitHub. It lists every app available to install.

---

## Default registry

```
https://raw.githubusercontent.com/browndevv/djx-registry/main/registry.json
```

This is the URL `djux list` and `djux add` use by default.

---

## registry.json format

```json
{
  "version": "1",
  "apps": {
    "auth": {
      "version": "0.1.0",
      "description": "JWT authentication — register, login, logout, refresh, me endpoint",
      "tags": ["auth", "jwt", "api"],
      "author": "djx-dev",
      "official": true,
      "repo": "https://github.com/browndevv/djx-app-auth",
      "download": "https://github.com/browndevv/djx-app-auth/archive/refs/heads/main.zip"
    }
  }
}
```

### Top-level fields

| Field | Type | Description |
|---|---|---|
| `version` | string | Registry schema version. Currently `"1"`. |
| `apps` | object | Map of app name → app entry. |

### App entry fields

| Field | Type | Description |
|---|---|---|
| `version` | string | Current version of the app. Informational — shown in `djux list` and `djux add` output. |
| `description` | string | One-line description shown in `djux list`. |
| `tags` | string[] | Discovery tags. |
| `author` | string | Publisher name or GitHub username. |
| `official` | boolean | `true` for apps maintained by the djux team. Shown with ★ in `djux list`. |
| `repo` | string | URL of the app's GitHub repository. |
| `download` | string | URL of the zip archive that `djux add` downloads. |

The `download` URL is passed directly to the downloader. For GitHub repos, use the archive URL format:

```
https://github.com/<owner>/<repo>/archive/refs/heads/main.zip
```

---

## Caching

The CLI caches the registry locally to keep `djux add` fast and work offline.

**Cache location:** `~/.djux/registry.json`  
**Cache TTL:** 1 hour  
**Metadata:** `~/.djux/registry.meta.json` (stores the fetch timestamp)

### Cache behaviour

| Situation | What happens |
|---|---|
| Cache exists and is less than 1 hour old | Served from cache; no network request |
| Cache exists but is older than 1 hour | Fetched fresh; cache updated |
| Network fails, cache exists | Warning printed to stderr; stale cache used |
| Network fails, no cache | Fatal error |

### Force a fresh fetch

```bash
djux list --refresh
```

This bypasses the cache for that one invocation. The cache is then updated with the fresh data.

---

## Using a custom registry

Both `djux add` and `djux list` accept a `--registry` option:

```bash
djux list --registry https://example.com/my-registry.json
djux add myapp --registry https://example.com/my-registry.json
```

The custom URL must serve a JSON file in the standard `registry.json` format. Caching applies to custom registries too, keyed on the default cache path (so mixing registries in the same session will use whichever was cached last — use `--refresh` to force a fetch when switching).

A local file URL also works during development:

```bash
djux add myapp --registry file:///path/to/local-registry.json
```

---

## Adding an app to the registry

Apps are added to the registry by opening a pull request to [browndevv/djx-registry](https://github.com/browndevv/djx-registry).

See [creating-apps.md](creating-apps.md) for the full submission process, including how to run `djux publish` to validate your app before opening the PR.

### Official apps

Apps marked `"official": true` are maintained by the djux team and reviewed more strictly. Community apps are welcome and reviewed for basic safety (public repo, valid manifest, working download URL) but are not otherwise audited.
