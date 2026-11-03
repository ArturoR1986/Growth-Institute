# Growth Institute — Handoff 02: Data integration

3 November 2026 · Completes Handoff 01; no additional data handoff is required.

## Authorized workspace

Work exclusively inside `C:\Users\me_ar\Documents\Job Applications\Growth Institute\Application Assignment` and its subfolders. Do not inspect or modify other folders. Keep project data, dependencies, caches, temporary files and outputs here. If execution cannot respect this boundary, explain the specific blocker. Do not search outside it for missing materials.

## Input and timestamp semantics

Use `Growth_Institute_Dashboard_Data.json`, already provided. UTF-8 JSON with schemaVersion `1.0`; fictional challenge records, projected to the agreed permitted fields. It is an input dataset, not precomputed dashboard values. Do not require a second raw export.

Use generatedAt `2026-11-03T19:13:00.151Z` as the fixed as-of timestamp for this file. Every source date/time is ISO 8601 UTC; Z means UTC. Display the snapshot with an explicit timezone. Derive week 6 of 8 from program dates and as-of. Do not replace as-of with the machine clock. Session end = scheduledAt + durationMinutes. Use finished sessions only for attendance denominators; ongoing weeks are excluded from completed-week averages.

## Field mapping

| JSON path | Dashboard/calculation use |
|---|---|
| company.id, company.name | Company context; company name in header |
| company.sponsor.name, .title | Sponsor identity display; not proof of authentication |
| program.id, .name, .weeks, .startsAt, .endsAt | Program title, stage and program-aligned weeks |
| learners[].id, .name, .title | Matching key, learner display name and job role |
| learners[].status | Active or withdrawn tab and cohort membership |
| learners[].enrolledAt, .withdrawnAt | Eligibility; withdrawnAt is present only for withdrawn learner |
| modules[].id, .order, .title, .releasedAt | Ordered checklist, released-module denominator and future states |
| completions[].learnerId, .moduleId, .completedAt | Unique completions, completion history and weekly counts |
| sessions[].id, .week, .moduleId, .title | Session matching, labels and topic linkage |
| sessions[].scheduledAt, .durationMinutes | Finished/upcoming status and duration window |
| attendance[].learnerId, .sessionId | Learner/session join matching |
| attendance[].joinedAt, .leftAt | Connection intervals; clip to scheduled session and merge overlapping reconnects |

There is one company/program. The file has no explicit learner-to-company field because all its learners belong to this supplied company/program. Do not infer that this structure implements multi-tenant authorization. Follow the demo/production boundary in Handoff 01.

## Known facts and anomaly handling

- 12 learner records, 8 modules, 8 sessions, 47 completion rows and 47 attendance rows.
- 11 learners currently active; Sebastián Vega withdrew at `2026-10-14T00:00:00.000Z`.
- Duplicate completion pair: learner `lrn_10` (Martín Sosa), module `mod_03`, appears twice. Count it once and retain earliest valid timestamp for first-completion history. There are 46 unique learner/module completions, 44 belonging to current active learners.
- All learners enrolled before the program started. No late-enrollment module policy is needed for this fixture.
- Six modules released and six sessions finished at as-of. Modules 7–8 and sessions 7–8 are upcoming.
- Module 6 released 2 November. Its lower count is not evidence of difficulty or lateness; no module deadlines exist.
- Some connection intervals extend outside scheduled class time. Clip durations before reporting averages; do not use raw interval length as in-class duration.
- No attendance record means “No attendance recorded” for an eligible finished session. It is not a claim about motivation, recording views or learning.
- Private notes, emails, media URLs and other excluded fields have already been removed. Preserve server-side allowlisting if another source adapter is later added.

## Expected checks for this snapshot

| Measure | Expected |
|---|---|
| Active / withdrawn / enrolled | 11 / 1 / 12 |
| Active released-module completion | 44 / 66 = 66.67%, display 67% |
| Completion by module, current active cohort | 10, 10, 8, 7, 7, 2 |
| Historical joined counts by finished session | 11, 10, 9, 6, 6, 5 |
| Historical eligible counts by session | 12, 12, 12, 11, 11, 11 |
| Latest finished session | Session 6, 3 November, 5/11 joined |
| Active-cohort weekly module completions, weeks 1–6 | 10, 10, 8, 7, 7, 2 |
| Active-cohort weekly sessions joined, weeks 1–6 | 10, 9, 9, 6, 6, 5 |
| Active-cohort weekly people with either activity | 10, 10, 10, 8, 8, 5 |
| Average module completions per active learner per completed week | 42 / (11 × 5) = 0.76 |
| Average classes joined per active learner per completed week | 40 / (11 × 5) = 0.73 |
| Average in-class duration among attendees, sessions 1–6, minutes rounded to 1 decimal | 83.5, 81.8, 78.1, 81.5, 83.7, 82.0 |

Week 6 is ongoing. The current-active cohort weekly figures intentionally exclude Sebastián in every week; historical session figures include him while eligible. Label those populations and do not interchange the counts.

## Design reference and instruction to proceed

The approved purple dashboard screenshot should be placed in the authorized directory. Use it when available. If it is absent, proceed using the detailed visual specification in Handoff 01 and mark exact screenshot matching as pending; do not block implementation merely for the missing image. The user has already accepted the layout and scope. Do not add new top-level sections.

Read Handoff 01 together with this document and the JSON file. This document supplies the previously deferred mapping, timestamp semantics and anomaly guidance. Proceed with the reusable dashboard template and population system, verify the numeric expectations, and report actual results and remaining limitations.
