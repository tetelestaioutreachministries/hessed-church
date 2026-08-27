# Hesed Church — Phase 1 (Django website)

A working Django backend for the Hesed Church website. The original static
HTML/CSS/JS from the "Hesed" purple template is untouched — it's now served
through Django templates, with staff managing all content from `/admin/`.

## What's included

| App          | Purpose |
|--------------|---------|
| `core`       | Home page, About page, shared "church info" context processor |
| `events`     | `Event` model, paginated upcoming list + detail page |
| `sermons`    | `Series` (current-series homepage feature) + `Sermon` models |
| `groups`     | `ConnectGroup` + `GroupInquiry` (routes to group leader or general email) |
| `volunteer`  | `Department` + `VolunteerApplication` (routes to department contact) |
| `contactus`  | `ContactMessage` — general contact form |

All forms save to the database **and** send email. Every existing CSS class
and HTML structure from the template was preserved exactly — only the
lorem-ipsum/hardcoded bits were swapped for template variables and real
Django form rendering.

## Requirements

- Python 3.11+
- PostgreSQL (the project uses Postgres from the start, not SQLite)

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a Postgres database and user (adjust names/password as you like):

```bash
sudo -u postgres psql -c "CREATE USER hesed WITH PASSWORD 'hesed';"
sudo -u postgres psql -c "CREATE DATABASE hesed_church OWNER hesed;"
```

Set environment variables (a `.env` file works fine with `python-decouple`,
or just export them):

```bash
export DATABASE_URL="postgres://hesed:hesed@localhost:5432/hesed_church"
export DJANGO_SECRET_KEY="change-me-in-production"
export DJANGO_DEBUG=True
export CHURCH_NAME="Hesed Church"
export CHURCH_ADDRESS="1600 Amphitheatre Parkway, Mountain View, CA 94043"
export CHURCH_PHONE="+1 975 432 345"
export CHURCH_GENERAL_EMAIL="info@hesedchurch.org"
```

Run migrations, seed the 8 volunteer departments, and create an admin user:

```bash
python manage.py migrate
python manage.py seed_departments
python manage.py createsuperuser
```

Start the dev server:

```bash
python manage.py runserver
```

Visit `http://localhost:8000/` for the site and `http://localhost:8000/admin/`
to manage content.

## How to switch email to real SMTP

By default, `DJANGO_EMAIL_BACKEND` is unset, so Django uses the **console
backend** — emails print to the terminal instead of sending. To send real
email in production, set these environment variables (no code changes
needed):

```bash
export DJANGO_EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
export DJANGO_EMAIL_HOST="smtp.yourprovider.com"
export DJANGO_EMAIL_PORT=587
export DJANGO_EMAIL_USE_TLS=True
export DJANGO_EMAIL_HOST_USER="you@yourdomain.com"
export DJANGO_EMAIL_HOST_PASSWORD="your-smtp-password"
export DJANGO_DEFAULT_FROM_EMAIL="no-reply@yourdomain.com"
```

## Adding content via /admin/

- **Events** → Events app → Event → fill in title, date, summary, etc.
  `is_published` controls whether it shows on the site; the homepage and
  events list only show upcoming, published events.
- **Sermons** → Sermons app → Series → create a series and check
  "is_current" to feature it on the homepage "Current Series" section
  (only one series can be current — checking it on a new one automatically
  un-checks any other). Add individual Sermons underneath a Series.
- **Connect Groups** → Groups app → Connect Group → add each group's leader,
  meeting time, and location so it shows on the Connect Groups page.
- **Volunteer Departments** → Volunteer app → Department → the 8 standard
  ministries are pre-seeded with blank `contact_email`. **Fill in each
  department's contact email in /admin/** so applications route correctly.

## A friendlier upload page: /manage/

Django's `/admin/` is powerful but not the friendliest thing to hand church
staff who just want to drop in this week's devotional or upload a sermon.
`/manage/` is a much simpler, purpose-built alternative covering the things
staff do most often:

- **Devotionals** — add/edit today's or an upcoming devotional.
- **Sermons** — add a sermon and upload the raw MP3 directly on the same
  page; it's compressed and pushed to Cloudinary automatically (Phase 2).
- **Events** — add an event and upload the poster JPG directly; same
  automatic compress-and-upload flow (Phase 2).
- **Connect Groups** and **Volunteer Ministries** — edit names, leaders,
  and (importantly) each ministry's contact email for routing.
- **Inbox** — every Contact/Volunteer/Connect-Group form submission in one
  place, with a one-click "mark handled" toggle.

Only staff users (`is_staff=True`, same flag `/admin/` uses) can reach
`/manage/` — anyone else is redirected to the login page. Logged-in staff
also see a small "Manage Content" link in the site header. `/admin/` still
exists underneath for anything not covered here (e.g. bulk edits, deleting
records, permissions).

If Cloudinary isn't configured yet (see Phase 2 env vars below), uploading
an MP3 or poster through `/manage/` still saves the sermon/event — it just
shows a message explaining the upload itself didn't go through, rather than
failing with an error page.

## How ministry email routing works

- **Volunteer applications**: emailed to the chosen `Department.contact_email`
  (reply-to set to the applicant), falling back to `CHURCH_GENERAL_EMAIL` if
  the department has no contact email set. The applicant also gets a short
  confirmation email.
- **Connect Group inquiries**: emailed to the chosen group's `leader_email`,
  falling back to `CHURCH_GENERAL_EMAIL` if no group was picked or the group
  has no leader email set.
- **Contact form**: always emails `CHURCH_GENERAL_EMAIL`.

## What's next

This is Phase 1 only — the website backend. Phase 2 adds a REST API,
Celery/Cloudinary/Firebase integration, and the Flutter app on top of this
same project.
