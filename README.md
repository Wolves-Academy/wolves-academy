# Wolves Sports Academy Manager

Academy management app for Wolves Sports Academy: players, attendance, packages,
payments, coaches (own logins, QR / WhatsApp check-in, salaries), finance, reports.
English and Jordanian Arabic. Installs on phones as an app (PWA).

**Open the app: https://wolves-academy1.vercel.app**

## Where it runs

| Part | Service |
|---|---|
| App (Python / Flask) | **Vercel**, deployed automatically on every push to `main` |
| Database | **Supabase** Postgres, via the `DATABASE_URL` environment variable |

GitHub Pages can't run this app; it only serves static files. Use the Vercel link.
Setup steps: [DEPLOY.md](DEPLOY.md).

## Environment variables (Vercel)

| Name | Value |
|---|---|
| `DATABASE_URL` | Supabase **Transaction pooler** URI (port 6543) with the database password |
| `WSA_SECRET` | any long random text (keeps logins secure) |

Tables are created automatically on first start.

## Sign in

- **Admin:** PIN `0000` on first start. Change it right away in Settings.
- **Coaches:** each coach signs in with a personal code the admin sets in **Coaches**.

## Admin guide

Everything the admin can do, step by step: [docs/Wolves-Admin-Guide.pdf](docs/Wolves-Admin-Guide.pdf)

## Local development

Without `DATABASE_URL` the app uses a local SQLite file (`academy.db`).
`start.bat` runs it on the laptop. Tests: `python tests/test_app.py all`.

## Styling

Tailwind is pre-built into `static/app.css` (no in-browser compile, so phones load faster).
After changing classes in `templates/`, rebuild it:

```
npx tailwindcss@3.4.17 -c tailwind.config.cjs -i static/src/tw.css -o static/app.css --minify
```

Phone layout check (demo server running: `python tests/serve_demo.py`): `node tests/phone_check.cjs`
