# Growth Institute — Codex Handoff 01
## Locked dashboard design and data-population system

Version 1.0 · 3 November 2026 · Prepared by Aurelian for Codex

Status: design scope accepted. This is a build brief, not a completed implementation. The actual dataset and exact source-field mapping belong in Handoff 02.

## 1. Intention

Build Assignment A: a separate company-sponsor dashboard showing how enrolled employees are progressing and participating without entering the student platform. Help the sponsor see group patterns and inspect individual recorded activity to support follow-up conversations.

The assignment allows four hours of working time. Keep implementation small and runnable; document actual time and any limitations honestly. Do not add product scope to make the result appear more sophisticated.

## 2. Persona and tone

Act as a practical product engineer implementing an accepted design. Use calm, factual, supportive language. Completion and attendance measure recorded activity; they do not establish motivation, understanding, retention, workplace application or business results. Avoid rankings, awards, invented engagement scores and unsupported risk labels.

## 3. Context and architecture boundary

Create three distinct, connected parts:

| Part | Responsibility |
|---|---|
| Dashboard template | Reusable visual components and interactions; no hardcoded learner names or metric values |
| Data file | Replaceable structured source records, delivered separately in Handoff 02 |
| Population system | Load, validate, sanitize, calculate and bind records to the template |

Pipeline: source file → server-side validation and permitted-field projection → calculations → sponsor-safe view model → dashboard.

Use the simplest stack consistent with the existing project. Keep parsing and calculations separate from rendering. Do not build a generic ingestion platform, database, CMS, AI analysis service or multi-company administration tool. A file-backed demonstration is sufficient; a live API adapter is optional only if required by the original challenge and affordable within the time limit.

Handoff 02 must settle exact source fields, timestamp semantics, data coverage and fixtures. Until it arrives, build the template and interface boundary using clearly labelled synthetic fixtures. Do not claim integration with the supplied dataset is complete. Do not fabricate missing records.

## 4. Locked visual design

Use the approved screenshot supplied with this conversation as the visual baseline. If it is not available in the receiving workspace, follow this specification and request the screenshot only if needed for exact visual matching.

- Deep purple dashboard surface, slightly lighter purple cards, lavender chart bars and accents, white primary text and muted secondary text.
- Rounded outer container and cards, subtle borders, generous readable spacing, restrained typography.
- Desktop: three summary cards in one row; two equally weighted charts beneath; full-width collapsible team section below them.
- Narrow screens: stack cards and charts; preserve readable labels and usable team details.
- Use centralized color/spacing tokens. Exact brand hex values have not been verified; do not describe inferred colors as official brand specifications.

| Area | Required content |
|---|---|
| Header | Growth Institute / Sponsor View; company name; program name; current week of total weeks; sponsor name and role |
| Summary 1 | Active learner count, total enrolled count, withdrawn count |
| Summary 2 | Released modules completed by current active learners; percentage, progress bar and numerator/denominator |
| Summary 3 | Latest finished session: joined/eligible, session number and date |
| Left chart | Live session participation over finished sessions; joined counts, week/session labels and eligible denominators |
| Right chart | Completion by released module for current active learners; module titles on accessible detail, release context, upcoming modules distinguished |
| Team section | Expand/Collapse control; Active and Withdrawn tabs with counts; table and individual details |
| Footer | Mock-data label when applicable; snapshot timestamp with timezone; “Participation measures · Learning impact not measured” |

Approved screenshot reference values are examples for QA, never template constants: Northwind Logistics; Scale-Up Operating System; week 6 of 8; 11 active / 12 enrolled / 1 withdrawn; 44/66 = 67%; latest session 5/11; session joined counts 11,10,9,6,6,5; module completed counts 10,10,8,7,7,2. Confirm these against Handoff 02 before using them as fixture expectations.

## 5. Team and individual interactions

Start the Team participation block collapsed, matching the approved screenshot. Expand reveals the selected tab's table; Collapse hides it. Tabs must remain operable and counts accurate. Use keyboard-accessible controls with visible focus and aria-expanded/state labels.

Table: learner name and job role, unique modules completed/eligible released modules, unique eligible sessions joined/finished eligible sessions, latest recorded participation date or “None recorded”.

Selecting a learner reveals a compact detail panel or expanded row containing:

- Module checklist/history with titles, release dates and completion dates; future modules marked Upcoming.
- Session history with joined/no record/not eligible/upcoming states and minutes connected within the scheduled session.
- Weekly recorded activity: module completions and classes joined shown separately, plus their average per completed eligible week with the denominator visible.

Withdrawn learners have their withdrawal date and historical activity displayed separately. Do not mark sessions after withdrawal as missed. Avoid adding more top-level cards or charts; group patterns are already represented by the two overview charts. The weekly activity and duration additions belong within the expandable details.

## 6. Calculation and presentation contract

Use one explicit as-of timestamp throughout. For fixture rendering use the supplied snapshot timestamp; do not silently mix it with the computer clock. Derive dates, week labels and counts from data. Format display dates consistently with an explicit timezone.

1. Deduplicate module completions by learner/module pair. Use earliest valid completion timestamp for first-completion history; flag malformed or contradictory records rather than silently changing facts.
2. Overall completion percentage = unique eligible released-module completions for currently active learners / eligible released learner-module opportunities. Exclude future modules. A zero denominator displays “Not available”, never NaN or a misleading 0%.
3. No module deadlines are supplied. Released but unfinished does not mean overdue. Show release dates; contextualize recently released modules without fixed date strings.
4. Session eligibility respects enrollment and withdrawal dates. “Finished” means scheduled end is at or before as-of. Future sessions do not count as missed; treat an in-progress session separately.
5. Attendance counts unique learner/session pairs, never raw connection records. Use valid positive overlap with the scheduled session window; surface any supplied records that contradict this rule during integration.
6. Duration = overlap of connection interval with scheduled start/end. Merge overlapping reconnect intervals before summing to avoid double-counting; cap at session length. Missing duration is unknown, not automatically zero.
7. Average attendance duration is among attendees with valid measurable duration; show that denominator. Do not include non-attendees as zero in that average. Minutes connected do not measure attention.
8. Weekly activity uses program-aligned seven-day weeks. Count unique module completions by completion timestamp and unique session joins by scheduled session week. Keep these two measures separate, without combining them into an engagement score.
9. Exclude ongoing and future weeks from full-week averages. Expose the eligible completed-week denominator for individual averages. For the current-active cohort summary use that fixed cohort consistently and label it; historical attendance charts instead use enrollment eligibility at each session. Do not mix those populations without labels.
10. The source does not establish a universal late-enrollment module policy. All supplied learners reportedly enrolled before the program started; if that changes, document and resolve the module eligibility policy instead of inventing penalties.
11. Latest activity = latest valid recorded completion or eligible attendance activity at/before as-of. Explain this scope; no login or recording-view activity is available.

## 7. Privacy and data handling

The sponsor-facing response must allowlist needed fields. Exclude coach notes, learner/sponsor emails, join/recording URLs, study-time estimates and minutesSpent, learner timezones, company industry/headcount, coach names and long program descriptions. Sponsor name/title are permitted. Keep IDs only where necessary for matching and UI keys; IDs do not provide authorization.

Do not bundle raw source JSON into browser assets, send it to the client and hide fields, or log private records. Process raw files on the server. A safe view model may contain only the permitted fields and derived values.

Check sponsor/company authorization server-side before returning data. This mock dataset has no source authentication and only one company: that does not prove tenant isolation. If production identity is outside the assignment, use an explicitly documented demo session boundary and disclose that production authentication is not implemented. Never claim a browser-side filter provides access control.

Render source text safely as text, not executable HTML. Show clear loading, empty, invalid-data and error states. Do not silently substitute fixture numbers after a load failure.

## 8. Acceptance and delivery

Deliver source, replaceable data-file interface, population/calculation functions, runnable instructions and a short README explaining assumptions, privacy boundary, demo limitations and how to replace data. Keep the real data handoff separate from this design document.

Verify:

- Approved visual hierarchy, colors and responsive behavior are preserved.
- Expand/Collapse, Active/Withdrawn tabs and learner selection work by mouse and keyboard.
- Replacing a valid fixture changes names, metrics, charts and histories without editing template code.
- Duplicate completions do not inflate counts; future requirements and post-withdrawal sessions do not create penalties.
- Partial weeks, reconnects, duration clipping and zero denominators behave correctly.
- Excluded fields never appear in browser network responses or generated assets.
- Loading, empty and malformed-file states are understandable.

Use focused tests for calculation and privacy boundaries plus a visual/interaction check. Report what actually passed and what remains incomplete. Within the four-hour constraint, prioritize this accepted scope and document omissions; do not silently expand the product or present an unfinished integration as complete.

## 9. Next input: Handoff 02

Expected separately: authoritative data file, exact schema/mapping, snapshot timestamp, known anomalies and numeric expectations. This document defines what to build and how it must behave; Handoff 02 supplies the records that populate it.
