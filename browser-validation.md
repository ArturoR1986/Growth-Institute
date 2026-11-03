# Browser verification — 3 November 2026

Target: http://127.0.0.1:8765/ in the connected in-app browser.

Prior layout check: 1280×900 desktop produced three summary columns and two chart columns without page overflow. At 390×844, cards/charts stacked; the document had no horizontal overflow and table overflow stayed in its own scroll container. Original narrow browser view was also inspected. Temporary viewport settings were reset.

Updated page: Latest session attendance heading confirmed. M6 context visibly reads “M6 · Released 2 Nov · Current week”. Learner rows visibly offer View details ▾, switching to Hide details ▴ on selection.

Expanded the team table, checked Active (11) and Withdrawn (1), and opened every learner panel: Mariana Ocampo, Diego Ferreyra, Lucía Benítez, Tomás Aguilar, Valentina Ruiz, Andrés Molina, Camila Torres, Florencia Paz, Martín Sosa, Renata Castillo, Joaquín Herrera, Sebastián Vega. Every panel included Module history, Session history with measured duration or explicit no-attendance/not-eligible state, and Weekly recorded activity. Andrés has no recorded attendance; no zero-minute attendance was invented. Sebastián's panel displayed withdrawal on 14 October, historical durations, and post-withdrawal Not eligible states.

Keyboard Enter opened learner details. Prior checks also verified Enter/Space team collapse/reopen and keyboard tab selection. Collapse/reopen preserved the selected tab/detail state; switching cohort cleared the prior learner panel. Source-string injection safety is checked by tests and textContent rendering, not by executing a script payload in the browser.

Limitations: no approved reference screenshot available; no full accessibility audit or cross-browser matrix; loading/empty/error response contracts tested by HTTP, but no browser fault-injection screenshots. No saved browser screenshot artifact was generated during this check.

## Live-source and access follow-up

Actual browser check after server access integration: anonymous reload redirected to /login; the provisioned local sponsor account successfully signed in and populated the live dashboard, including Sign out, fixed layout, 11 active learners, 44/66 completions and generatedAt 2026-11-03T20:29:44.784Z. Automated HTTP tests separately cover logout invalidation, expiry, forged sessions, rate limiting and cross-origin denial. A temporary 120-person browser preview verified six Active pages with row counts 20/20/20/20/20/10, disabled Next on the final page and keyboard Previous. The preview was closed and its server stopped. Browser Sign out returned to /login.

