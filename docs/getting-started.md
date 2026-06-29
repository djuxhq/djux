# Getting started

This guide takes you from a fresh machine to a running Django project with a JWT auth app installed — in under five minutes.

---

## Prerequisites

- Python 3.10 or later
- pip

That's it. Django, DRF, and everything else get installed automatically.

---

## 1. Install djx

```bash
pip install djx
```

Verify the installation:

```bash
djx --version
```

---

## 2. Create a project

```bash
djx new myproject
```

This copies the djx project template into a new `myproject/` directory and replaces all `{{project_name}}` placeholders. You'll see:

```
Creating project: myproject

╭─────────────── Ready ───────────────╮
│ ✓ Project created: myproject/       │
│                                     │
│   cd myproject                      │
│   python -m venv .venv              │
│   ...                               │
╰─────────────────────────────────────╯
```

---

## 3. Set up the environment

```bash
cd myproject

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install Django and python-dotenv
pip install -r requirements.txt

# Copy the example env file
cp .env.example .env
```

The `.env` file starts with safe development defaults:

```
SECRET_KEY=change-me-to-a-long-random-string
DEBUG=True
ALLOWED_HOSTS=localhost 127.0.0.1
```

Change `SECRET_KEY` before deploying to production.

---

## 4. Run the first migration and start the server

```bash
python manage.py migrate
python manage.py runserver
```

Visit `http://localhost:8000/admin/` to confirm Django is running.

---

## 5. Add an app

```bash
djx add auth
```

Watch the output:

```
✓ Found auth v0.1.0
✓ Downloaded
✓ App files copied to apps/auth/
✓ settings.py updated
✓ urls.py updated
✓ Dependencies installed
✓ Migrations applied

✓ auth added successfully!

Notes: Endpoints: POST /api/auth/register/ /api/auth/login/ ...
```

The `auth` app is now fully wired into your project. No manual edits required.

---

## 6. What just changed

djx made four automatic changes to your project:

**`config/settings.py`** — three entries added to `INSTALLED_APPS`:
```python
"auth_app",
"rest_framework",
"rest_framework_simplejwt",
```

And a settings block injected at the bottom:
```python
from datetime import timedelta

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

**`config/urls.py`** — one URL include added:
```python
path("api/auth/", include("auth.urls")),
```

**`apps/auth/`** — the full Django app copied here, importable as `auth` because `apps/` is on `sys.path`.

**`djx.project.json`** — updated to track the installation:
```json
{
  "installed_apps": ["auth"]
}
```

---

## 7. Try the auth endpoints

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "username": "you", "password": "secret123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "secret123"}'

# Get current user (replace TOKEN with the access token from login)
curl http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer TOKEN"
```

---

## Next steps

- Browse available apps: `djx list`
- Remove an app: `djx remove auth`
- Full command reference: [cli-reference.md](cli-reference.md)
- Build your own app: [creating-apps.md](creating-apps.md)
