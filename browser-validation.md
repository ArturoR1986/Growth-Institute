# Browser verification — 3 November 2026

This record separates the original local checks from the later public deployment checks. Original local target: http://127.0.0.1:8765/.

Prior layout check: 1280×900 desktop produced three summary columns and two chart columns without page overflow. At 390×844, cards/charts stacked; the document had no horizontal overflow and table overflow stayed in its own scroll container. Original narrow browser view was also inspected. Temporary viewport settings were reset.

Updated page: Latest session attendance heading confirmed. M6 context visibly reads “M6 · Released 2 Nov · Current week”. Learner rows visibly offer View details ▾, switching to Hide details ▴ on selection.

Expanded the team table, checked Active (11) and Withdrawn (1), and opened every learner panel: Mariana Ocampo, Diego Ferreyra, Lucía Benítez, Tomás Aguilar, Valentina Ruiz, Andrés Molina, Camila Torres, Florencia Paz, Martín Sosa, Renata Castillo, Joaquín Herrera, Sebastián Vega. Every panel included Module history, Session history with measured duration or explicit no-attendance/not-eligible state, and Weekly recorded activity. Andrés has no recorded attendance; no zero-minute attendance was invented. Sebastián's panel displayed withdrawal on 14 October, historical durations, and post-withdrawal Not eligible states.

Keyboard Enter opened learner details. Prior checks also verified Enter/Space team collapse/reopen and keyboard tab selection. Collapse/reopen preserved the selected tab/detail state; switching cohort cleared the prior learner panel. Source-string injection safety is checked by tests and textContent rendering, not by executing a script payload in the browser.

Limitations: no approved reference screenshot available; no full accessibility audit or cross-browser matrix; loading/empty/error response contracts tested by HTTP, but no browser fault-injection screenshots. No saved browser screenshot artifact was generated during this check.

## Live-source and access follow-up

Actual browser check after server access integration: anonymous reload redirected to /login; the provisioned local sponsor account successfully signed in and populated the live dashboard, including Sign out, fixed layout, 11 active learners, 44/66 completions and generatedAt 2026-11-03T20:29:44.784Z. Automated HTTP tests separately cover logout invalidation, expiry, forged sessions, rate limiting and cross-origin denial. A temporary 120-person browser preview verified six Active pages with row counts 20/20/20/20/20/10, disabled Next on the final page and keyboard Previous. The preview was closed and its server stopped. Browser Sign out returned to /login.


## Public hosted deployment

Target: https://growth-institute-sponsor-review.grand-bud-6088.chatgpt.site/ (hosted version 5).

Verified on 3 November 2026 in the connected browser: anonymous page requests reached /login; reviewer sign-in succeeded; the live API populated 11 active / 12 enrolled / 1 withdrawn and 44/66 completions, with generatedAt 2026-11-03T21:20:38Z. The layout and labels were preserved. Expand showed the 11 active learners. Mariana's details included module history, measured session duration and weekly activity. Withdrawn selected Sebastián's separate history entry. Sign out returned to /login; navigating to /api/dashboard afterward returned the sign-in-required error. The tab was left at the reviewer sign-in page.

Earlier hosted compatibility failures (default-cache access and unsupported Fetch redirect mode) were fixed before these successful checks. The final runtime uses D1 sessions and manual redirect handling. The public flow checks supplement the local all-12-learner and responsive/120-person checks above; they do not claim every earlier browser check was repeated against the public host. Hosted automated tests check complete-model parity, access boundaries and logout revocation.
