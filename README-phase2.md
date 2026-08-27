# Hesed Church — Phase 2 (REST API + Flutter app)

Built on top of the Phase 1 Django project — same database, same models
extended in place. A sermon or event created once in `/admin/` shows up on
both the website and the Flutter app immediately.

## What's new in Phase 2

- **`devotionals` app** — `Devotional` model + a daily push, scheduled via a
  plain cron job (no Celery/Redis needed — see below).
- **`api` app** — DRF serializers/viewsets/views for everything below.
- **`events.Event`** extended with `poster_url` / `cloudinary_id`, plus a new
  `EventRSVP` through-model.
- **`sermons.Sermon`** extended with `thumbnail_url`, `file_size_mb`,
  `cloudinary_id` (the model field is still named `speaker`; the API alone
  exposes it as `preacher` so Phase 1 templates referencing `sermon.speaker`
  keep working untouched).
- **`core.Profile`** — one-to-one with `auth.User` (see "user identity"
  below), plus `saved_sermons` (M2M) and a `DeviceToken` model for FCM.
- Custom Cloudinary-backed upload flow (in both `/admin/` and the `/manage/`
  dashboard) for sermon audio and event posters (compress locally, upload to
  Cloudinary, store only the URL + public_id — nothing raw is kept in
  Postgres or on disk).
- Firebase Cloud Messaging pushes (daily devotional + new-sermon-uploaded),
  and a Flutter app for the four user-facing flows.

## Decision: user identity model

The spec asked me to decide between a custom `AUTH_USER_MODEL` or a
`core.Profile` one-to-one with the default `auth.User` before running any
Phase 2 migrations. **I went with `Profile`** — Phase 1 migrations already
exist against the default user model, and swapping `AUTH_USER_MODEL`
afterward would require a full database reset. `Profile` gets you
`saved_sermons` and Google-account linking (`google_sub`) without that risk.
If you'd rather have a custom user model, that's a clean rebuild from
scratch — let me know and I'll redo this part.

## Decision: sermon playback

Went with **download-then-play** (`flutter_downloader` + `just_audio`),
matching the `[Download {file_size_mb}MB]` button described in the spec —
users see the file size up front and listen offline once downloaded, rather
than streaming directly from the Cloudinary URL.

## Decision: Celery/Redis vs. plain cron

The spec's tech stack recap lists Celery + Celery Beat. In practice, this
project uses a scheduled job for exactly one thing — the 6 AM devotional
push — and nothing else runs as a background task (Cloudinary uploads and
form emails already happen synchronously, in the request). Celery/Redis
earn their complexity when you have many background jobs, need automatic
retries, or need to scale workers across machines; a single daily task
doesn't need any of that.

**I used a plain cron job** calling `python manage.py send_devotional_push`
instead (see "Scheduling the daily devotional push" below). The Celery
plumbing (`hesed_church/celery.py`, `devotionals/tasks.py`) is still in the
project and works if you install `celery`/`redis`/`django-celery-beat`
later for other background work — but it's entirely optional and nothing
breaks if those packages aren't installed at all.

## Environment variables (Phase 2 additions)

```bash
# Cloudinary
export CLOUDINARY_CLOUD_NAME="your-cloud-name"
export CLOUDINARY_API_KEY="your-api-key"
export CLOUDINARY_API_SECRET="your-api-secret"

# Firebase (path to the service account JSON — keep this file out of git)
export FIREBASE_SERVICE_ACCOUNT_JSON="/secure/path/firebase-service-account.json"

# Google Sign-In (the OAuth client ID Flutter uses)
export GOOGLE_OAUTH_CLIENT_ID="xxxxx.apps.googleusercontent.com"
```

(Celery/Redis env vars only apply if you opt into that setup — see the
decision note above.)

System dependency: **ffmpeg** must be installed on the server for audio
compression (`apt-get install ffmpeg`).

## Install

```bash
pip install -r requirements.txt -r requirements-phase2.txt
python manage.py migrate
```

## Scheduling the daily devotional push (cron — no Celery/Redis needed)

Add a line to the server's crontab (`crontab -e`) that runs once a day at
6 AM in whatever timezone the server is set to (set the server's timezone
to Africa/Kampala, or adjust the hour accordingly):

```cron
0 6 * * * cd /path/to/hesed_church && /path/to/venv/bin/python manage.py send_devotional_push >> /var/log/hesed_devotional_push.log 2>&1
```

That's it — one line, no worker process, no broker to keep running.

### If you'd rather use Celery Beat instead

The project still supports it if you prefer that route (e.g. you're already
running Celery for other things). Install the optional packages:

```bash
pip install celery redis django-celery-beat
```

Uncomment `"django_celery_beat"` in `INSTALLED_APPS` and the
`CELERY_BEAT_SCHEDULER` line in `settings.py`, then run migrations and start
a worker + beat process:

```bash
celery -A hesed_church worker -l info
celery -A hesed_church beat -l info
```

The beat schedule is defined in `hesed_church/celery.py`:

```python
app.conf.beat_schedule = {
    "send-daily-devotional-push": {
        "task": "devotionals.tasks.send_daily_devotional_push",
        "schedule": crontab(hour=6, minute=0),
    },
}
```

## Testing the push flow without waiting for 6 AM

Make sure a `Devotional` exists for today's date (add one via `/manage/` or
`/admin/`), then run the same command cron would run:

```bash
python manage.py send_devotional_push
```

If `FIREBASE_SERVICE_ACCOUNT_JSON` isn't set, the push is skipped silently
(useful for local dev without Firebase configured) — check the logs for a
`FCM pushes are disabled` message to confirm, rather than an error.

The new-sermon push fires automatically the moment you upload an MP3 to a
Sermon in `/manage/` or `/admin/` — no need to wait for anything.

## API endpoints

| Method | Path                          | Notes |
|--------|-------------------------------|-------|
| POST   | `/api/auth/google/`           | `{"id_token": "..."}` → verifies with Google, creates/logs in the user, returns a DRF token |
| GET    | `/api/devotionals/today/`     | 404 if none published yet |
| GET    | `/api/sermons/`               | Paginated — `preacher`, `date`, `audio_url`, `thumbnail_url`, `file_size_mb` |
| GET    | `/api/events/upcoming/`       | Paginated — upcoming, published events with `poster_url` |
| POST   | `/api/events/<id>/rsvp/`      | Auth required (`Authorization: Token <token>`), idempotent |
| POST   | `/api/devices/register/`      | `{"token": "..."}`, auth optional |

All verified working end-to-end against a live Postgres-backed server in
this build (see conversation for the test transcript): devotional 404/200
behavior, sermon `preacher` mapping, RSVP 401→201→200 idempotency, device
registration, and the audio/image compression pipelines.

## Flutter app

See `flutter_app/README.md` for setup. Implements four tabs against the API
above: Devotional (auto-fetch + Hive offline cache), Sermons
(download-then-play), Events (poster grid, Add to Calendar, Share, RSVP),
and Google Sign-In + FCM registration.

**Note on this build environment:** the Flutter SDK and `pub.dev` aren't
reachable from this sandbox (no network egress to `pub.dev`), so the Flutter
code here is complete source but hasn't been `flutter run` or `flutter build`
tested. Run `flutter pub get && flutter run` locally to build it.
