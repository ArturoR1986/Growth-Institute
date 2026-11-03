# Growth Institute — Sponsor dashboard

**[Open the hosted reviewer demo](https://growth-institute-sponsor-review.grand-bud-6088.chatgpt.site/)** · **[Decision note](DECISION_NOTE.md)**

No installation or ChatGPT account is needed. Use the reviewer credentials supplied with the application, expand **Team participation**, and choose **View details**. The sign-in page is public; dashboard data requires an authenticated reviewer session. The demo stays available independently of the applicant's computer.

## What this solves

Challenge A: a company sponsor needs to see employees' program participation without entering the learner platform. The dashboard presents active enrollment, released-module completion and the latest finished session's attendance, two group charts, and individual module/session/weekly histories. Active and withdrawn learners are separate. It reports recorded participation without inferring motivation, understanding or learning impact.

## Two runtimes, one dashboard

| | Hosted reviewer app | Local development app |
| --- | --- | --- |
| Source | `hosted-dashboard/worker/` | `app/` |
| Runtime | JavaScript on Cloudflare Workers through Sites | Python standard library |
| UI | Generated from `app/index.html` | `app/index.html` |
| Source data | Live challenge API, fetched on the server | Live API by default; explicit offline fixture option |
| Sponsor account | Shared reviewer account; credentials supplied separately | Account provisioned by the person running it |
| Sessions and login limits | Cloudflare D1; signed, random, one-hour sessions | In-process storage; sessions end on server restart |
| Cookies | `__Host-` prefix, Secure, HttpOnly, SameSite=Strict | HttpOnly and SameSite=Strict; HTTP on loopback |
| Password hashing | PBKDF2-SHA256, 100,000 iterations | PBKDF2-SHA256, 600,000 iterations |

The hosted calculation model is checked against the complete Python fixture output. D1 stores access records, not learner profiles or private source records. See [HOSTED_DEMO.md](HOSTED_DEMO.md) for hosted source, environment key names, migrations, checks and deployment limitations.

## Run locally (optional)

Requirements: Python 3.10+ and a browser. Live mode also needs outbound HTTPS to `jobs.growthinstitute.com`. No dependency installation, database or build is needed for the local Python app. From a fresh checkout:

```sh
python -B app/manage.py setup
python -B app/server.py
```

Choose a sponsor username and password of at least 12 characters at the setup prompts. Open http://127.0.0.1:8765/ and use that account. On systems where the interpreter is called `python3`, substitute it for `python`. Stop the server with Ctrl+C. If the port is occupied, use `python -B app/server.py --port 8766` and open the corresponding URL.

For deterministic offline review, start with:

```sh
python -B app/server.py --source fixture
```

Live errors never silently select fixture mode. Setup creates a gitignored `.local-config.json` containing a salt and password hash; no credentials are bundled in the repository. Local accounts and sessions are separate from the hosted reviewer account.

## Source data, privacy and access

Both adapters use the original read-only [challenge API](https://jobs.growthinstitute.com/api/challenge), specifically `/all`. Its dates move with the calendar. `generatedAt` is the single explicit as-of timestamp; displayed dates are UTC. The bundled fixture is pinned to 3 November 2026. [Handoff 02](Growth_Institute_Codex_Handoff_02_Data_Integration.md) documents its schema and numeric expectations.

The server projects permitted fields before caching and returning a calculated view. Coach notes, emails, media URLs, estimated study time, `minutesSpent`, learner timezones, industry/headcount, coach names and long descriptions are excluded. Raw external records are not saved or logged by application code, embedded in HTML, or returned to the browser. Source text is rendered with `textContent`.

The safe source cache lasts 60 seconds; upstream advertises five-minute caching. Fetches have a 15-second timeout and a response-size check. Network failure produces a Retry state and HTTP 503; invalid data produces HTTP 422 without private exception details. No stale/fixture substitution occurs. Empty records and zero denominators have explicit states.

Protected routes require a valid server-checked session. Company/program membership is server-owned; learner IDs and query parameters cannot grant access. Mismatched source scope receives HTTP 403. Login/logout require the correct request origin; login attempts are limited. Raw files, configuration, source-code and traversal routes are not served.

## Calculations and scale

Unique learner/module completions use the earliest valid timestamp. Only released modules count toward completion. Attendance is a unique eligible learner/session pair with positive scheduled overlap. Connection intervals are clipped to session/enrollment/withdrawal/as-of bounds and overlapping reconnects are merged. Duration averages include measured attendees only, with their denominator shown. Missing endpoints reject the source rather than inventing zero duration.

Historical session eligibility and the fixed current-active completion cohort are labeled separately. Future requirements and post-withdrawal sessions do not create penalties. Individual averages include completed eligible program weeks only. Late enrollment is rejected until its module eligibility policy is agreed. Latest activity covers recorded completions and eligible session connections, not login or recording views.

Calculations index activity by learner/session; the table renders 20 learners per page. A 120-person fixture produced 110 active learners, 440/660 completions and attendance 110/100/90/60/60/50. The Python calculation took approximately 0.012 seconds in an earlier run; the full safe response was approximately 366 KB. These are small-fixture observations, not a concurrency or load certification. Browser checks walked all six Active pages. At larger scale, server-side pagination and learner details fetched on demand would replace the full-response approach.

## Verify

Local Python suite and HTTP smoke check (no external network or reviewer setup required):

```sh
python -B -m unittest discover -s app -p 'test_*.py' -v
python -B app/check_http.py
```

Optional real API check, requiring internet:

```sh
python -B app/check_live.py
```

Hosted calculation/access checks and artifact build, using Node 22+ (no npm install):

```sh
cd hosted-dashboard
node tests/worker.test.mjs
node scripts/build.mjs
node scripts/validate-artifact.mjs
```

When changing `app/index.html` or `hosted-dashboard/worker/logic.js`, regenerate the committed Worker before running hosted checks/builds:

```sh
cd hosted-dashboard
python -B generate_worker.py
```

`generate_worker.py` also regenerates parity fixtures from the Python reference. Existing fixture tests keep the expected snapshot metrics independently pinned. Do not change an expected result solely to make a failing parity check pass.

Results and scope: [repository audit](REPOSITORY_AUDIT.md), [current check output](audit-validation.txt), [browser verification](browser-validation.md), [hosted notes](HOSTED_DEMO.md). Earlier logs (`validation.txt`, `fresh-validation.txt`, `live-validation.txt`, `hosted-validation.txt`) record prior check runs.

## Limits and delivery

This is a fictional-data review demo with one shared reviewer account and one company/program. Managed individual identity/MFA, invitations, recovery, tenant administration, exhaustive accessibility/browser testing and realistic concurrency testing remain outside scope. The public app uses HTTPS, Secure cookies and durable session revocation; those controls do not make it a production identity system.

No notifications, learner portal, rankings, overdue labels or invented engagement scores were added. The approved design image was never available, so exact screenshot matching is unverified. The design/data handoffs are original input briefs; current implementation and delivery status are described here, in HOSTED_DEMO.md and DELIVERY.md.

The [decision note](DECISION_NOTE.md) contains 278 words. Work was AI-assisted and refined after the first prototype. Active working time was not reliably tracked; measured compliance with the four-hour limit is not claimed. No application email or submission has been sent. The [submission checklist](SUBMISSION_CHECKLIST.md) retains the applicant's final review step.
