# Deploying Wolves Sports Academy (Supabase database)

The app runs on SQLite on a laptop, and on **Supabase Postgres** when `DATABASE_URL` is set.
Tables are created automatically on first start. No data is shared with any other academy.

## 1. Supabase
1. Create a project (region close to Jordan, e.g. Frankfurt `eu-central-1`).
2. Project Settings → Database → Connection string → **Transaction pooler** (port 6543).
   Copy the URI and put your database password in it.
   (The app already disables prepared statements, which the transaction pooler requires.)

## 2. Environment variables (on the host)
| Name | Value |
|---|---|
| `DATABASE_URL` | the pooler URI from step 1 |
| `WSA_SECRET` | any long random string (keeps logins secure) |

## 3. Vercel
1. Push this repo to GitHub.
2. vercel.com → Add New → Project → import the repo. Vercel detects Flask from `app.py`; no settings to change.
3. Add the environment variables above (Settings → Environment Variables), then Deploy.
4. Settings → Functions → set the region to Frankfurt (`fra1`), next to the Supabase database:
   the app talks to the database many times per page. Jordan time is set by the app itself.

## 4. First login
Admin PIN is `0000`. Change it in Settings straight away, then create each coach in **Coaches**
(each coach gets a personal login code).

## Install on phones
Open the site in Chrome (Android) and tap **Install**, or in Safari (iPhone) tap Share → **Add to Home Screen**.

## Updating
Push to GitHub; the host redeploys automatically.

## Tests
```
python tests/test_app.py all                                      # SQLite
DATABASE_URL=<throwaway postgres> python tests/test_app.py all    # Postgres (wipes that database!)
```
