# Repository consistency audit — 3 November 2026

## Result

The repository describes both the deployed reviewer app and the independently runnable local prototype. The public review link is https://growth-institute-sponsor-review.grand-bud-6088.chatgpt.site/. Hosted credentials are supplied separately and remain outside the repository.

Before this audit, all 38 published file blobs matched their corresponding local files (accounting for UTF-8 BOM/newline representation). The audited changes update documentation and ignore rules; application behavior and the deployed runtime are unchanged.

## Corrected documentation

- README.md now leads with the public reviewer flow, distinguishes Cloudflare Workers/D1 from local Python, and provides separate local and hosted verification commands.
- HOSTED_DEMO.md identifies the hosted files and deployed-source provenance. It distinguishes hosted credentials from local accounts and documents durable logout, rate limiting, HTTPS cookies and known limits.
- DELIVERY.md now reports the current 278-word decision note and hosted delivery status.
- browser-validation.md includes the successful public sign-in, live metrics, team/details, Withdrawn selection, logout and post-logout API-denial checks, separately from earlier local responsive/all-learner/120-person checks.
- .gitignore excludes additional audit/package scratch artifacts.
- The original design/data handoffs and BRIEF.md remain source briefs; README.md identifies them as inputs rather than current implementation-status reports.

## Source and reproducibility checks

The hosted version 5 source commit in the Sites source repository is `d1df27f52f88af1b253abf1c6a462f38368236f1`. It is separate from the GitHub submission commit. Local Worker source (`worker/index.js` and `worker/logic.js`), `.openai/hosting.json`, and the schema migration were compared with that exact commit and matched. The same files in the GitHub submission matched the audited local files.

The generated hosted Worker was independently reconstructed in memory from `app/index.html`, the sign-in template and authored hosted logic and matched exactly. The dashboard HTML and deployed server artifact are therefore current; no new deployment is needed for these documentation changes.

A clean copy containing only published repository files, without local accounts/configuration, passed:

- 24 Python unit tests, including scope/privacy/session boundaries and a 120-person calculation.
- The standalone HTTP smoke check.
- Hosted full-fixture model parity and access/security assertions.
- The hosted artifact build and ESM validation.

See audit-validation.txt for the current check output. Older validation logs remain historical evidence, not claims of newly repeated production/browser checks. No new browser interactions or live API calls were needed for this documentation/source audit; the successful public flow verification is recorded in browser-validation.md.

## Delivery limits retained

The app supports one shared reviewer account and one fictional company/program. It is not a production identity service or a general tenant-isolation demonstration. Full accessibility/browser coverage, realistic concurrent load testing, account recovery and invitations remain outside scope. No exact match to a missing design image is claimed. The 278-word decision note retains the AI-use and untracked-working-time disclosure; measured compliance with the four-hour limit is not claimed. No application email or final submission has been sent.
