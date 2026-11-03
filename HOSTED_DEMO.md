# Hosted reviewer demo

URL: https://growth-institute-sponsor-review.grand-bud-6088.chatgpt.site/

Reviewer credentials are delivered separately to the applicant, not committed to source. No installation or ChatGPT account is required. The application has its own reviewer sign-in. The reviewer account grants only the configured fictional Northwind company/program context.

## Implementation

The local Python implementation remains runnable using the root README. Sites hosts the equivalent JavaScript ESM Worker under hosted-dashboard/worker/index.js, using the same dashboard HTML. generate_worker.py embeds app/index.html and the sign-in page in the server artifact. worker/logic.js is the authored hosted calculation/access adapter. Full-model parity against the Python output is checked in tests/worker.test.mjs.

The live mock API is fetched on the server. Unknown/private source fields are projected out before caching or rendering. No fixture is substituted on API failure. Browser assets contain neither the raw API response nor access secrets.

Hosting secrets: REVIEWER_USERNAME, REVIEWER_PASSWORD_HASH, REVIEWER_PASSWORD_SALT, SESSION_SECRET, SPONSOR_COMPANY_ID, SPONSOR_PROGRAM_ID. Password hashes use PBKDF2-SHA256 (100,000 iterations, compatible with Worker WebCrypto), per-account salt and timing-safe comparison. Session tokens combine random nonces, one-hour expiry, HMAC signatures and server-owned company/program scope. Cookies are Secure, HttpOnly, SameSite=Strict and use the __Host- prefix.

Cloudflare D1 stores only hashed session tokens with expiry and HMAC-obscured source-IP keys for login attempt limits. Sign-out deletes the session record; the same token cannot continue to access the API. Attempts are counted with an atomic SQL upsert. Expired records are pruned during sign-in. No learner profile or coach note is stored in D1. Database schema is in drizzle/0000_reviewer_access.sql; hosting applies schema-only migrations at deployment.

The API source cache is safe in-process data with a 60-second TTL. No default Worker cache access is required. Fetch uses redirect:'manual' and rejects non-success responses because the hosted Worker runtime does not implement redirect:'error'.

## Validation

From hosted-dashboard, using Node 22+:

    node tests/worker.test.mjs
    node scripts/build.mjs
    node scripts/validate-artifact.mjs

No npm install is needed. Tests compare the complete hosted view model with the Python fixture output and check duplicates, duration clipping/reconnects, empty and ongoing-week states, private-field exclusion, login, origin protection, signed scope, Secure cookies, expiry, rate limits, route denial and logout revocation. The migration and atomic attempt query were independently checked with SQLite. D1 behavior was then verified on the actual public deployment.

Public browser check on 3 November 2026: successful reviewer sign-in; live API populated 11 active / 12 enrolled / 1 withdrawn and 44/66 completions; Team expansion, active learner module/session-duration/weekly details and Withdrawn tab passed; sign-out returned to sign-in and the API then denied access. This is a focused review flow, not an exhaustive security audit or concurrency/load certification.

## Hosting limitations

This uses one shared reviewer account for an intentionally fictional challenge dataset. It has no account recovery, invitation workflow, MFA or multiple-tenant administration. The public endpoint is a review demonstration. A production rollout should use managed individual identity and durable organization membership, stronger centralized security monitoring and deployment-specific load/accessibility checks.

The hosting source project ID and schema are tracked in .openai/hosting.json. Credentials and environment values are not. Reproduction of hosting requires an authorized Sites account; reviewers can use the public link or run the dependency-free Python app locally.
