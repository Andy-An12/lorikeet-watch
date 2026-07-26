# lorikeet-watch

A small internal dashboard for [lorikeet](https://github.com/Andy-An12/lorikeet)
cron results: shows pass/fail history per host, and emails/texts the admin
when a run fails.

## What this is

lorikeet is a CLI health-check runner — cron on each of your servers runs
it every few minutes to check things like disk space, memory, SSH config,
pending security patches, and so on, and reports pass/fail per check.
lorikeet-watch is the single place all of those servers report to: a
dashboard where you can see, at a glance, which hosts are currently
healthy and which aren't, drill into a host's check history when
something's wrong, and get emailed or texted the moment a run starts
failing — instead of having to SSH into every box or read cron output by
hand. It's built for a small ops team running their own fleet, not a
multi-tenant or public-facing product: one admin account, one dashboard,
every server you point at it shows up automatically.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Build the frontend (requires Node.js 20+):

```bash
cd frontend
npm install
npm run build
cd ..
```

```bash
export LORIKEET_WATCH_DB=/var/lib/lorikeet-watch/data.sqlite
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

.venv/bin/flask --app wsgi init-db
.venv/bin/flask --app wsgi create-admin admin '<a-strong-password>'
```

Run it (dev):

```bash
.venv/bin/flask --app wsgi run
```

Run it (production):

```bash
.venv/bin/gunicorn -w 2 -b 0.0.0.0:8000 wsgi:app
```

## First-time configuration

1. Log in at `/login` with the admin credentials created above.
2. Go to **Settings**, click **Regenerate token**, and copy the ingest
   token into your lorikeet crontab (see below).
3. Fill in SMTP and/or Twilio details and toggle on the channels you want.

## Wiring up lorikeet's cron job

lorikeet already supports pushing results via `--webhook`, no changes to
lorikeet itself are needed. On each server running lorikeet:

```
*/5 * * * * lorikeet --webhook "https://lorikeet-watch.internal/internal/results?token=YOUR_TOKEN" /etc/lorikeet/config.yml
```

Note: the ingest token travels as a URL query parameter because lorikeet's
`--webhook` flag has no option for custom headers. This is a known tradeoff,
not an oversight — query-string tokens can end up in server access logs, so
if that matters in your environment: serve lorikeet-watch over HTTPS so the
URL isn't exposed in transit, and if you run nginx/apache in front of
gunicorn, keep the query string out of the access log (e.g. an nginx
`log_format` that omits `$request_uri`'s query part) or otherwise redact it.
You can also rotate the token periodically via the Settings page's
**Regenerate token** button.

## How results from multiple servers are grouped

Every check run lorikeet's `--webhook` payload includes the reporting
machine's own hostname (`{"hostname": "...", "has_errors": ..., "tests": [...]}`).
Each POST to `/internal/results` is stored independently, keyed by that
hostname — there's no separate registration step, and servers running
different `config.yml` files (different checks entirely) work fine, since
each server's results are stored under its own hostname regardless of what
other servers report.

The dashboard groups runs by hostname and shows each host's latest status
as one row; click a host to see its full run history. Results from
different servers are never merged or overwritten — they only ever show up
grouped under the same host if they genuinely report the same hostname.

Note this is the OS-level hostname (whatever the `hostname` command returns
on that machine), not a FQDN or a domain you assign — if two servers happen
to share a hostname, their results will appear as one host on the
dashboard. Keep hostnames unique across your fleet.
