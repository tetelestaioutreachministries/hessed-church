# Deploying to Render (fully free)

This covers deploying the whole project — website, API, and the daily
devotional push — for **$0/month**: [Render](https://render.com)'s free
web service + [Neon](https://neon.tech)'s free PostgreSQL + a free external
scheduler ([cron-job.org](https://cron-job.org)) for the daily devotional
push. No Celery/Redis needed (see README-phase2.md); no server to manage.

**The trade-off of free:** Render's free web service goes to sleep after 15
minutes with no traffic, and takes roughly 30 seconds to wake up for the
next visitor. For a small church site this is usually a fair trade for
$0/month — you can always upgrade to Render's `starter` plan (~$7/month)
later for an always-on site with no code changes needed.

## What gets created

`render.yaml` in the project root defines one thing Render will create:

- **hesed-church-web** — the Django site (gunicorn) on Render's free plan,
  running `collectstatic` and `migrate` automatically on every deploy.

There's no Render Cron Job (that's a paid feature) — instead, the daily
devotional push runs via a small authenticated endpoint
(`/devotionals/trigger-push/?token=...`) that you'll have a free external
scheduler call once a day. Covered in Step 5.

**The database is not Render's managed Postgres.** Render's free Postgres
expires 30 days after creation and gets deleted — fine for a demo, not for
a real site. Instead this uses Neon, which has a genuinely permanent free
PostgreSQL tier (no card required, 0.5GB storage, scales to zero when idle
— a good fit for a low-traffic church site).

## Step 0 — Create your free Neon database

1. Go to [neon.tech](https://neon.tech) → sign up (GitHub login works).
2. Create a new project, e.g. "hesed-church".
3. On the project dashboard, find the **Connection string** (usually shown
   immediately after creation, or under **Connect** → **Connection string**).
   It looks like:
   ```
   postgresql://neondb_owner:AbCdEf123@ep-cool-name-12345.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. Copy this whole string — you'll paste it into Render as `DATABASE_URL` in
   Step 3. (Neon's free tier scales the database to zero after 5 minutes of
   inactivity and wakes up automatically on the next query — the first
   request after a quiet period takes a second or two longer, nothing to
   configure for.)

## Step 1 — Push your code to GitHub

Render deploys from a Git repository.

```powershell
cd "C:\Users\zack marvin\Desktop\my projects\hesed_church_phase1\repo"
git init
git add .
git commit -m "Initial commit"
```

Create a new repository on [github.com/new](https://github.com/new), then:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/hesed-church.git
git branch -M main
git push -u origin main
```

**Before committing**, make sure `.gitignore` excludes `.env`, `venv/`,
`__pycache__/`, `staticfiles/`, and `media/` (the project's `.gitignore`
already covers these) — you never want your local secrets or virtual
environment pushed to GitHub.

## Step 2 — Create the Render Blueprint

1. Go to [dashboard.render.com](https://dashboard.render.com) → sign up /
   log in (GitHub login is simplest).
2. Click **New +** → **Blueprint**.
3. Connect your GitHub account if prompted, then select the repository you
   just pushed.
4. Render reads `render.yaml` automatically and shows you the one resource
   it's about to create (the free web service). Click **Apply**.
5. Wait for the first deploy — it will fail health checks until you've set
   `DATABASE_URL` and the remaining environment variables below, that's
   expected.

## Step 3 — Set the remaining environment variables

Go to the **hesed-church-web** service → **Environment** tab, and add:

```
DATABASE_URL=postgresql://neondb_owner:...@ep-....neon.tech/neondb?sslmode=require
```

(the exact string you copied from Neon in Step 0), then:

```
CHURCH_NAME=Hesed Church
CHURCH_ADDRESS=Your real church address
CHURCH_PHONE=Your real phone number
CHURCH_GENERAL_EMAIL=info@yourchurch.org

SITE_BASE_URL=https://hesed-church-web.onrender.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://hesed-church-web.onrender.com
```

(Replace the URL with whatever Render actually assigned — shown at the top
of the service page — or your custom domain once you've set one up, see
Step 7.)

Then the email/Cloudinary/Firebase/Google values from README-phase2.md:

```
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
DJANGO_EMAIL_HOST=smtp.yourprovider.com
DJANGO_EMAIL_PORT=587
DJANGO_EMAIL_USE_TLS=True
DJANGO_EMAIL_HOST_USER=you@yourdomain.com
DJANGO_EMAIL_HOST_PASSWORD=your-smtp-password

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

GOOGLE_OAUTH_CLIENT_ID=xxxxx.apps.googleusercontent.com
```

`CRON_SECRET_TOKEN` is already set for you — `render.yaml` tells Render to
auto-generate a random one. You'll need its actual value in Step 5, so:
Environment tab → find `CRON_SECRET_TOKEN` → click the eye icon to reveal
it → copy it somewhere.

## Step 4 — Firebase service account (Secret Files)

Don't paste the Firebase JSON contents as a plain env var — Render has a
purpose-built feature for this:

1. On **hesed-church-web** → **Environment** tab → scroll to **Secret
   Files** → **Add Secret File**.
2. Filename: `firebase-service-account.json`
3. Contents: paste the full contents of the JSON file you downloaded from
   Firebase.
4. Add the env var `FIREBASE_SERVICE_ACCOUNT_JSON` with value
   `/etc/secrets/firebase-service-account.json` (Render always mounts
   Secret Files at that path).

## Step 5 — Free daily devotional trigger (cron-job.org)

The project exposes `/devotionals/trigger-push/?token=...` — hitting this
URL with the correct token does exactly what `manage.py send_devotional_push`
does (same underlying code), but as a plain HTTP request instead of a shell
command, so a free scheduler can call it.

1. Go to [cron-job.org](https://cron-job.org) → sign up (free, no card).
2. Click **Create cronjob**.
3. **Title:** "Hesed Church devotional push" (anything you like).
4. **URL:**
   ```
   https://hesed-church-web.onrender.com/devotionals/trigger-push/?token=PASTE_YOUR_TOKEN_HERE
   ```
   (your real Render URL + the `CRON_SECRET_TOKEN` value from Step 3).
5. **Schedule:** every day, at **03:00** — cron-job.org's schedule times are
   in UTC, and Africa/Kampala is UTC+3 year-round (no daylight saving), so
   03:00 UTC = 6:00 AM there.
6. Under **Advanced** (or similar, depending on cron-job.org's current UI),
   set the request timeout to at least 30 seconds — the free Render service
   may need to wake up from sleep first, which takes a few seconds longer
   than a normal request.
7. Save. You can click **Run now** / check the job's execution history on
   cron-job.org to confirm it gets a `200 OK` back (the response body will
   say something like "Devotional push sent for 2026-08-26", or "No
   devotional published for today" if you haven't added one yet).

**Optional but recommended:** add a second cron-job.org job hitting your
plain homepage (`https://hesed-church-web.onrender.com/`) every 10–14
minutes. This isn't required, but keeps the free service from fully
sleeping between visits during the day, so real visitors don't hit the
~30-second cold-start delay as often. (It will still sleep overnight when
nobody's pinging it or visiting — that's fine, the devotional push job
above will simply wake it up when it runs.)

## Step 6 — Create your superuser

Once the web service is deployed and green, open a shell to it:

Dashboard → **hesed-church-web** → **Shell** tab, then:

```bash
python manage.py createsuperuser
python manage.py seed_departments
```

## Step 7 — Custom domain (optional)

Dashboard → **hesed-church-web** → **Settings** → **Custom Domains** → add
your domain, follow Render's DNS instructions (usually a CNAME record).
Once that's live, update `SITE_BASE_URL` and `DJANGO_CSRF_TRUSTED_ORIGINS`
to your real domain instead of the `.onrender.com` one, add your real
domain to `DJANGO_ALLOWED_HOSTS`, and update the URL in your cron-job.org
job from Step 5 to match.

## Verifying it worked

- Visit your Render URL — homepage, `/sermons/`, `/devotionals/`, `/events/`
  should all load with images/CSS intact (the first request might take
  ~30 seconds if the service was asleep — that's expected on the free plan).
- Log in at `/login/`, confirm `/manage/` works.
- Add a test Event through `/manage/` and confirm you (if subscribed) get
  the notification email.
- Test the devotional trigger without waiting for 03:00 UTC: paste the same
  URL from Step 5 straight into your browser. You should see a plain-text
  response confirming the push ran (or that there's no devotional for
  today yet).

## A note on cost

- **Database (Neon):** $0/month — permanent free tier, no card required.
- **Web service (Render, free plan):** $0/month — sleeps after 15 minutes
  idle, ~30 second cold start for the next visitor.
- **Daily devotional trigger (cron-job.org):** $0/month.

**Total: $0/month.**

### Upgrading later

When you're ready to pay for an always-on site (no cold starts), two
changes get you there with no code changes:
1. On Render: **hesed-church-web** → **Settings** → change the plan from
   Free to Starter (~$7/month).
2. Optional: switch the daily push from cron-job.org to a real Render Cron
   Job (~$1/month) running `python manage.py send_devotional_push` on
   schedule `0 3 * * *` — ask if you want me to add that service back to
   `render.yaml` when you get there.
