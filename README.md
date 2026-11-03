# Growth Institute — Sponsor program dashboard

Challenge A: a company sponsor sees team progress without entering the learning platform. The sponsor is a separately provisioned account, not a learner. A small Python standard-library server serves a responsive dashboard and a sponsor-safe API.

## Quick start (fresh checkout)

Requirements: Python 3.10 or newer; a browser; outbound HTTPS to jobs.growthinstitute.com for live mode. No pip/npm install, database, environment file or build step is needed.

From the repository directory, in PowerShell, cmd, macOS or Linux shell:

    python -B app/manage.py setup

Choose a username and password (12+ characters) at the prompts. This creates only .local-config.json in this directory, storing a random salt and PBKDF2 password hash, not the plaintext password. On systems where Python is named python3, substitute python3 for python in every command.

    python -B app/server.py

Open http://127.0.0.1:8765/, sign in with the account you created, and expand Team participation. Select View details on a learner; use the Active/Withdrawn controls. Sign out ends the session. Ctrl+C stops the server. If port 8765 is occupied, run `python -B app/server.py --port 8766` and open that port instead.

For deterministic offline review, explicitly choose:

    python -B app/server.py --source fixture

Live mode is the default. Fixture mode is never selected automatically after a network error. On this already-prepared local workspace only, credentials for the provisioned reviewer account are in the gitignored .local-access.txt. That file is excluded from delivery. Fresh-checkout reviewers create their own account using setup.

## Data source and error behavior

The adapter calls only the original read-only endpoint https://jobs.growthinstitute.com/api/challenge/all. Its schema was verified against https://jobs.growthinstitute.com/api/challenge. Program/company/learner/module/completion/session/attendance fields map to the supplied handoffs. Every response includes generatedAt; it is the single explicit as-of time used throughout. The API dates move with the calendar; the bundled fixture remains pinned to 3 November 2026. All display dates are UTC.

The upstream response is projected on the server before caching or calculation: coach notes, email addresses, media URLs, coach names, estimated study time, minutesSpent, timezones, industry/headcount and long descriptions are never copied into the sponsor view. Raw external records remain in memory only and are never saved or logged. The safe source is cached for 60 seconds in-process; upstream itself advertises five-minute response caching. A 15-second fetch timeout and 2 MB response limit bound external loading. Cache expiry followed by failure produces HTTP 503 and a Retry control, without stale/fixture substitution. Invalid source records produce HTTP 422 with no private error detail. Empty valid records show the empty state; zero denominators show Not available.

To replace the fixture, keep the Handoff 02 schema and schemaVersion 1.0 in Growth_Institute_Dashboard_Data.json, then reload in fixture mode. No template edits are required for names, metrics, charts or histories. Different company/program IDs must be explicitly provisioned in server-side configuration, never selected through a browser query.

## Sponsor access and security boundary

The provisioned account has server-owned companyId/programId membership. A successful password check creates a cryptographically random, server-held one-hour session; the cookie is HttpOnly and SameSite=Strict. Unknown, forged, expired and logged-out sessions receive HTTP 401 at the API and a sign-in redirect at the page. Source company/program mismatches receive HTTP 403 even if the browser supplies allowed IDs. Learner IDs, sponsor names and client filters do not grant access.

Password hashing uses PBKDF2-HMAC-SHA256 with 600,000 iterations and a per-account random salt; comparison is timing-safe. Five sign-in attempts per source IP per minute are allowed. Login/logout POSTs require a matching Origin/Host, and sign-in bodies are size-limited. The server exposes explicit routes only; raw files, local configuration, source and traversal paths return 404. Text is rendered with textContent.

This is a local challenge implementation, not an internet-ready identity system. It binds only to 127.0.0.1. HTTP cookies deliberately omit Secure on local HTTP; a public deployment needs TLS, Secure cookies, trusted Host/origin configuration, a maintained production web server, managed identity/MFA or invitation login, durable/revocable membership and shared session/rate-limit storage. Sessions currently disappear on restart. Only one sponsor and company/program are supported; this does not prove general tenant isolation. Password recovery and account administration were intentionally omitted.

## Product and calculation decisions

The initial view preserves three summary cards, two charts and a collapsed team section. It displays active enrollment, current-active released-module completion and latest finished-session attendance. Historical session eligibility and the fixed current-active completion cohort are labeled separately. Current-week release context explains a newly released module without inventing deadlines or risk scores. Detail controls are visibly labeled.

Module completions are deduplicated by learner/module using the earliest valid timestamp. Connection intervals are clipped to scheduled session/enrollment/withdrawal/as-of bounds and unioned before summing. Positive overlap establishes recorded attendance; reconnect rows do not inflate counts. Average duration includes measured attendees only, with its denominator exposed. Missing endpoints reject this source contract rather than inventing attendance or zero duration.

Individual details include all module release/completion dates, session status and minutes connected, and separate weekly module/class counts. Only fully completed eligible program weeks enter weekly averages; ongoing/future weeks do not. Withdrawn history is separated and post-withdrawal sessions are Not eligible. Late enrollment fails explicitly until a module eligibility policy is agreed. Latest activity covers recorded completion and eligible connection activity, not login or recording views. Participation is not evidence of learning impact.

## Ten times the data

Calculation maps index completions/joins by learner and attendance by session, avoiding repeated whole-cohort scans for individual histories. Team rows are paginated in groups of 20, without adding top-level sections. Tests clone the fixture to 120 learners / 470 completion rows / 470 attendance rows: 110 active, 440/660 completions and attendance series 110/100/90/60/60/50. The observed calculation time was about 0.012 seconds and the full safe response about 366 KB on this machine; these are observations, not a performance guarantee or concurrency/load test.

For this size, a full safe snapshot is acceptable. At substantially larger scale, use server-side team pagination and a lazy learner-detail endpoint; upstream currently has no pagination. With another day, add persistent indexed storage only if freshness/scale requirements justify it, conditional fetching, a production identity provider, automated browser/accessibility tests and realistic load tests. No generic ingestion platform, notifications, learner portal, rankings or inferred learning scores were built.

## Tests and evidence

    python -B -m unittest discover -s app -p 'test_*.py' -v
    python -B app/check_http.py
    python -B app/check_live.py

The first two commands need no external network or configured reviewer account: they create in-memory test accounts and bind temporary loopback ports. check_live needs internet access and validates the real API without saving raw records. The -B option prevents bytecode caches.

24 automated tests passed. They cover pinned counts and weekly totals, all 12 histories, date-driven release context, duplicates/earliest timestamps, overlapping/disjoint reconnects and clipping, in-progress sessions, no completed weeks/releases/attendees, empty/malformed/missing files, contradictory withdrawals/late enrollment, private-field projection, server-side scope rejection, raw route denial, login/logout/session expiry/forgery and rate limiting, adapter cache/failure behavior and a 120-person calculation. See validation.txt and live-validation.txt.

Browser checks verified desktop/mobile layout, team tabs, collapse/reopen, keyboard activation and all 12 learner panels before access integration. After integration, anonymous page access redirected to the sponsor sign-in page, and actual sign-in loaded the live API dashboard with 44/66 completion. Details of earlier browser checks are in browser-validation.md. The 120-person browser preview was also checked: six Active pages showed 20/20/20/20/20/10 rows, final Next was disabled and keyboard Previous worked. Browser logout returned to sign-in. No exhaustive browser matrix, accessibility audit, browser error-state fault injection or concurrent-user load test is claimed. The approved design screenshot was never present, so exact image matching is unverified.

## Delivery and scope honesty

DECISION_NOTE.md is the Spanish decision note (under 300 words). SUBMISSION_CHECKLIST.md tracks delivery readiness. The repository intentionally excludes credentials, local configuration and logs. No external deployment is required by the brief and none is claimed. Work was AI-assisted. Active work time was not reliably tracked across the successive refinements; measured compliance with the four-hour limit is not claimed. Later hardening and live-source work should be disclosed as follow-up improvements, not presented as a timed initial attempt.

