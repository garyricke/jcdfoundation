# JCD application admin + review tool — spec (draft)

**Date:** October 13, 2026 · **Author:** Gary Ricke (Orbis Design) · **Status:** draft for Bob's input, nothing built yet
**Source:** Oct 6 meeting with Bob (`JCD-Foundation-6-october-2026-meeting-notes.md` §2.5 and §4D, plus the raw transcript)

---

## 1. What this is

A private web screen where Bob, Gary and a small group of volunteer reviewers can read, filter, annotate and sort the applications that come in through `/apply`. It replaces "open each Netlify email and keep a spreadsheet."

Bob's words: "I want to be able to query." "When they review them, they want to add notes." "Let me see all now the tier ones … What haven't been reviewed yet?"

Two rules sit over everything:

1. **People decide, Bob makes the final call.** "At the end of the day, I'll make the decision."
2. **AI suggests reading order and never decides.** "AI is not going to make a decision. But it'll help flag." Bob: "I like that. A lot."

The first cycle is a pilot: "We'll make modifications." The spec is sized for that.

---

## 2. Who uses it

| Role | Who | Can do |
|---|---|---|
| **Final decision-maker** | Bob | Everything: see all applications, set the final decision, mark urgent/early decision, manage reviewers |
| **Admin / support** | Gary (Orbis) | Everything Bob can, except the final decision. Fixes data, runs exports, keeps the tool running |
| **Reviewer** | Volunteers: a nurse, a manufacturer, tradespeople, educators, a coach (per Bob) | Read assigned or all applications, add notes, set their own review status / tier recommendation |
| **Read-only** (optional) | e.g. Jack | View and filter, no edits |

Reviewers are volunteers, and the season falls right after the holidays ("it's seasoning during the holidays … in February, it probably would be"). Making their job easy is the success measure. Each reviewer should be able to open the tool, see "here are the ones waiting for you," read one, click a button, and move on, with no training session needed.

---

## 3. Data source

### What /apply sends today

`apply.html` posts to **Netlify Forms** as form `jcd-application` (multipart, with file uploads). Recommendation letters come in separately through `/recommend` as form `jcd-recommendation`.

**Application fields (`jcd-application`):**

| Group | Field names |
|---|---|
| ID / meta | `app_id` (generated in the browser, format `JCD-27-XXXXXX`), `submitted_at` |
| Identity / contact | `first`, `middle`, `last`, `email`, `phone`, `addr1`, `city`, `state`, `zip` |
| School | `school` (one of 13 schools, "Homeschooled", or "My school isn't listed"), `homeschool_area` (which public school's area, for homeschool/other), `grad_date` |
| Activities | `activities_school`, `activities_community` (this is where jobs show up, e.g. "Part-time at a body shop") |
| Career | `focus_area` (Health Sciences / Advanced Manufacturing / Building Trades), `profession`, `career_goal` (under 300 words) **or** `career_goal_file` (upload) |
| Study plan | `study_level` (Community college / Vocational training / Undergraduate / Graduate), `study_year`, `start_date`, `institution`, `annual_cost`, `cost_estimate_file` (upload) |
| Financial aid office | `aid_contact`, `aid_email`, `aid_address`, `aid_city`, `other_aid` (free text, e.g. FAFSA/MAP mentions) |
| Letters | `letter1_name`, `letter1_role` (Teacher / Employment supervisor / Other), `letter1_email`, and the same for `letter2_*` |
| Transcripts | `transcript_requested` (date), `colleges_attended`. Transcripts themselves are emailed by schools to info@ and are **not** in the form data |
| Sign-off | `certify`, `signature` |

**Letter fields (`jcd-recommendation`):** `ref` (presumably the student's `app_id` [TK — confirm it's the same ID]), `student_name`, `rec_name`, `rec_role`, `rec_org`, `rec_email`, `letter_file`, `submitted_at`.

**What the tool will not have unless we add it:** transcripts (they arrive by email), grades/GPA/ACT/class rank (we don't ask for them, and that's deliberate), and any income or FAFSA data beyond what the student types in `other_aid`.

### Where the data should live: options

Netlify Forms is fine for **collecting** submissions. It isn't a place to keep reviewer notes, statuses or an audit trail. Something has to hold that.

| Option | How it works | Pros | Cons |
|---|---|---|---|
| **A. Netlify Forms + a Supabase "review layer"** | Applications stay in Netlify. The admin screen reads them through the Netlify API. Notes, statuses and AI flags are stored in Supabase keyed by `app_id`. | Least new plumbing. Netlify stays the single copy of what the student sent. | Two systems to keep in sync. Netlify's API, file-URL access and plan limits [TK] become a dependency during review season. |
| **B. Copy every submission into Supabase** (recommended to evaluate first) | A Netlify submission-created hook / function copies each application into a Supabase table, and its files into a **private** Supabase Storage bucket. The admin tool reads only Supabase. | One place for everything: filtering, notes, status, audit. Supabase is **already used in this repo** for the annotation layer (`supabase/schema.sql`, `netlify/functions/comments.mjs`, service-role key server-side, RLS on with no public policies). Same pattern, known quantity. | More to build up front. Must make sure the copy step can't silently drop a submission (keep Netlify as backup, run a nightly count check). |
| **C. Airtable** | Push submissions to an Airtable base (the 2026 marketing plan mentioned an Airtable GMS). | Bob can see a familiar grid. Filtering comes free. | Per-seat cost for reviewers [TK]. AI flagging and the audit log are harder to control. Minors' data sits in another vendor. |

**Recommendation (not a decision):** B, built on the existing Supabase + Netlify Function pattern, with Netlify Forms kept as the untouched backup copy. Decide by **Nov 15** so capture is proven before Dec 1.

**Check before Dec 1 regardless of option:**
- Netlify Forms plan limits on submissions per month and file-upload storage [TK]. A 300+ application goal [TK] in a 3-month window could hit a free-tier cap.
- How long Netlify keeps uploaded files, and whether their URLs are private [TK].
- That `app_id` is unique enough. It's 6 random characters generated in the browser, so collisions are unlikely but not impossible. The tool should detect duplicates and re-submissions from the same email.

---

## 4. Features

### 4.1 List + filter (the "query" screen)

A table of applications, one row each: ID, name (or hidden; see 4.6), ZIP, high school, focus area, study level, submitted date, letters received (0/1/2), transcript received (manual checkbox), AI flag, review count, current status, urgent marker.

**Filters (combinable):**
- **ZIP** ("give me all 60510"), single or list
- **High school**, including Homeschooled (with `homeschool_area`) and "not listed"
- **Focus area**: Health Sciences / Advanced Manufacturing / Building Trades
- **Status**: not yet reviewed / reviewed / tier 1 / tier 2 / rejected / final decision
- **"Not yet reviewed"** as a one-click shortcut, plus "not yet reviewed **by me**" for each reviewer
- **Distance tier** (core / edge; see 4.4)
- **AI flag** (read first / standard / needs a human look)
- **Urgent / early decision**
- **Completeness**: missing letters, missing transcript, missing cost estimate

Plus free-text search across name, school, profession, institution and career goal. Plus **Export to CSV** of the current filtered view, for Bob or the accountant.

The focus-area filter also gives Bob his "buckets": "we put them in the buckets so that my health sciences team…" Reviewers can default to their own field.

### 4.2 Application detail view

One screen per applicant: all fields grouped the way the form groups them; the career goal in full; uploaded files (career goal doc, cost estimate) opened in-browser; linked recommendation letters matched by `ref`; activities shown prominently (Bob cares most about these, along with the story).

### 4.3 Reviewer notes + status buttons

- **Notes:** free text, timestamped, signed with the reviewer's name. Every reviewer sees every note (simplest for a pilot) [TK — Bob may prefer independent reads first; see open questions].
- **Status buttons** (Bob's list): **Reviewed · Tier 1 · Tier 2 · Rejected**.

Suggested model, so the buttons mean one thing each:
- Each reviewer gives their own **recommendation**: Tier 1 / Tier 2 / Reject (or "Reviewed, no recommendation"). Clicking any of these also marks the application *reviewed by that person*.
- The list shows the spread, e.g. "3 reviews: T1, T1, T2."
- **Final decision** is a separate field only Bob can set: Fund / Fund (tier 2) / Decline / Hold. It records the award amount and the payee (institution / employer) for his records, with no published cap, per the Oct 6 "case by case" decision.
- "Rejected" from a reviewer is a **recommendation**, not an outcome. Nothing reaches a student without Bob's final decision.

### 4.4 Distance tiers

Bob: students at the edge of the service area (his example was the far side of Oswego, "way the heck out") "are going to be in the second tier." The Waubonsee/COD "serving our residents first" comparison suggests the idea is in-area students first, edge students second.

**How distance could be determined (pick one):**

| Method | How | Notes |
|---|---|---|
| **ZIP list (recommended for pilot)** | Bob approves two lists: *core ZIPs* and *edge ZIPs*. Anything else is "outside, review by hand." Tier is assigned automatically from `zip`. | Simple, explainable, editable. ZIPs don't follow school-district lines, so a few students will need a manual override. |
| School + ZIP combo | Core = attends a qualifying school **and** lives in a core ZIP. Edge = qualifying school but an edge ZIP. | Catches the Oswego case precisely. |
| Drive distance | Geocode `addr1`+`zip` and measure miles from a center point. | More precise but less explainable. Geocoding means sending home addresses of minors to a mapping service. Not recommended for the pilot. |

**Bob needs to give the boundary:** which ZIPs (or which parts of which districts) are core and which are edge. Without that list, the tool can only show ZIP, not tier. **Due by Dec 1.**

Distance tier is a separate label from the reviewer's Tier 1/Tier 2 recommendation. Whether an edge student can be recommended Tier 1 on merit is an open question (see §8).

**Note on need:** Bob said he'll judge need partly by where a student lives and goes to school, since we're not collecting FAFSA. The tool will **show** ZIP and school so Bob and reviewers can apply that judgment. The AI flag will **not** use ZIP, school or address as a signal (see 4.5). That judgment stays visible and human.

### 4.5 AI flagging: suggests reading order, never decides

**What it does:** After each application arrives, an AI model reads the free-text parts and assigns one of three **reading-priority flags**, with 2–3 short reasons that quote the application:

- **Read first:** strong signals of what Bob looks for, or an urgent situation
- **Standard:** read in normal order
- **Needs a human look:** incomplete, unclear, uploaded file couldn't be read, possible duplicate, or text that looks pasted/generated [TK — keep this as a "look closer" note, never a penalty]

**Signals it looks for, from Bob's own criteria:**

| Signal | Where it reads it | Bob, Oct 6 |
|---|---|---|
| A clear story and a specific career goal | `career_goal` / `career_goal_file`, `profession` | "I want to hear their story … What they want to do" |
| A concrete plan | `institution`, `study_level`, `start_date`, `annual_cost`, `cost_estimate_file` | "What's your career path?" |
| Active in school | `activities_school` | "Have they been active … or did they just walk in the door at 7:30 and walk out … at 2:30?" |
| Held a job while in school | `activities_community` (and mentions in `career_goal`) | "If you held a job and you went to school, God bless you." |
| Community / family responsibility, volunteering | `activities_community` | "Do you do anything?" |
| Recommendation letters received, and from whom (teacher / employment supervisor) | `jcd-recommendation` matched by `ref` | |
| **Urgency** (about to drop out, can't pay next semester, already mid-program) | `career_goal`, `other_aid`, `study_year`, `colleges_attended` | the mid-program Waubonsee example |

**Signals it must not use:**
- Grades, GPA, ACT/SAT, class rank. We don't collect them, and the AI should ignore them if a student mentions them. "If a kid's got a C average, I don't care."
- Writing polish, grammar, spelling or length. The form says "no essay voice needed," so a short, plain, honest answer must not score lower than a polished one.
- Name, address, ZIP, high school, gender, race/ethnicity, religion, immigration status, or anything that could stand in for them.

**Guardrails:**
1. **Explainable.** Every flag shows its reasons as quotes from the application. No bare score.
2. **Advisory only.** No auto-reject and no auto-advance. Flags change sort order and nothing else. Every application stays in the list and every one gets a human read before a decision.
3. **Human override.** Any reviewer can mark a flag as "disagree" with one click. That's logged and feeds the pilot write-up.
4. **Audit log.** Record who changed what and when: status changes, notes, final decisions, flag overrides, and which AI model/version and instructions produced each flag.
5. **Minors' data.** Many applicants will be under 18.
   - Send the AI only the text it needs. Strip name, email, phone, address, ZIP and school before the call.
   - Use an API setting that doesn't keep or train on the data [TK — confirm terms for the chosen provider].
   - Store everything in a private database and private file bucket. No public links.
   - Individual reviewer logins (not the shared `goodkids` site cookie), so access is per person and can be revoked.
   - Set a retention rule: e.g. delete declined applications' files after a set period [TK — Bob/accountant to set]. Keep award records as long as the foundation needs them for the 990/audit [TK].
6. **Check for drift.** At the end of the pilot, compare flags to the committee's final picks. If "Read first" isn't tracking what reviewers value, change the instructions or drop the feature.

**Word cap:** Gary raised that with AI doing the first read, the 300-word cap on the career goal could loosen. **Recommend keeping 300 for the pilot.** The form is built and the cap keeps reviewer reading time sane. Revisit for cycle 2.

### 4.6 Name-blind option

Bob: "pull up who they are … Irrespective of their name. I don't even know what their address is." Offer a toggle (on by default for reviewers, off for Bob/Gary) that hides name, email, phone and street address in the reviewer view and shows only the ID, ZIP, school and the content. [TK — Bob to confirm he wants this.]

### 4.7 Urgent / early decision

Bob: a student mid-program who's about to drop out can be decided and paid early: "he'll get payment the same time he gets notified … We don't want to interrupt anything."

- An **Urgent** marker, which Bob, Gary or the AI flag can set. Only a human can confirm it.
- Urgent applications sit at the top of every reviewer's queue and send Bob an email alert.
- An early final decision is allowed any time from Dec 1, outside the February review window.
- Track the date notified and the date paid, so early cases can be shown to be handled.

### 4.8 Notifications (light)

- Email Bob/Gary a daily digest during the open window: new count, urgent count.
- Email each reviewer a weekly "N waiting for you" during February.
- **Applicant notification emails are not sent from the tool in the pilot.** Bob or Gary sends decision letters by hand, and every message gets reviewed before sending.

---

## 5. MVP vs later

| MVP: pilot cycle (Dec 2026 – Mar 2027) | Later: cycle 2+ |
|---|---|
| Submissions reliably captured + backed up (Netlify + chosen store) | Application form changes based on pilot learnings (e.g. word cap, new prompts) |
| Individual logins for Bob, Gary, reviewers | Reviewer assignment / load-balancing (e.g. 3 reviews per app) |
| List + filters: ZIP, school, focus area, status, not-yet-reviewed, urgent, completeness | Rubric scoring per criterion |
| Detail view with files and matched letters | Applicant-facing status page ("received / under review") |
| Notes + Reviewed / Tier 1 / Tier 2 / Rejected + Bob's final decision | Decision letters generated from the tool (still human-approved) |
| Distance tier from Bob's ZIP list | Payment tracking to institutions/employers (ACH reference, amount, date) |
| Urgent marker + alert | Multi-year history (returning applicants) |
| AI reading-priority flag with quoted reasons + override + audit log | Transcript intake into the tool (instead of info@ email) |
| CSV export | Dashboards (counts by school/area/ZIP), board-ready summary |
| Transcript-received checkbox (manual) | |

---

## 6. Rough timeline

Key dates: site live **Nov 1, 2026** · application opens **Dec 1, 2026** · closes **Feb 28, 2027** · review mostly **February** · decisions by **Mar 31, 2027**.

| By | Milestone |
|---|---|
| **Oct 27** | Bob answers the open questions below, especially the ZIP boundary, reviewer list and the name-blind view |
| **Nov 15** | Data-store decision made. Capture pipeline built and tested with dummy submissions (including file uploads and a letter matched by `ref`) |
| **Dec 1** | **Application opens.** Capture is live and verified with a real test submission end-to-end. Netlify backup confirmed. Bob can see a basic list (even if just a filtered table) |
| **Dec 15** | Admin MVP: filters, detail view, notes, status buttons, urgent marker. Early-decision cases can be handled from here on |
| **Jan 15** | Distance tiers live from Bob's ZIP list. AI flagging running on everything received so far. Gary + Bob spot-check flags against their own reads |
| **Jan 25** | Reviewer accounts created. 15-minute walkthrough (recorded) for volunteers |
| **Feb 1 – Feb 28** | Rolling review of applications received so far. Weekly reminders to reviewers |
| **Feb 28** | Application closes |
| **Mar 1 – Mar 20** | Final reviews of late arrivals. Bob makes final decisions |
| **by Mar 31** | Decisions out (sent by hand, reviewed before sending) |
| **April** | Pilot debrief: what reviewers used, flag accuracy, what to change for cycle 2 |

Ongoing admin and support during the cycle is part of the separate retainer proposal Gary owes Bob. This spec doesn't price it.

---

## 7. Risks

- **Late or lost submissions** if the capture step fails. Mitigation: keep Netlify as the untouched backup and run a daily count check.
- **Reviewers don't log in** (volunteers, February). Mitigation: one-click email links, a tiny queue, no training needed, and Bob or Gary can enter notes on a reviewer's behalf.
- **AI flag read as a verdict.** Mitigation: label it "Suggested reading order", show reasons, offer no reject path, and track overrides.
- **Minors' personal data exposure.** Mitigation: private store, per-person logins, minimal data sent to the AI, retention rule.

---

## 8. Open questions for Bob

1. **Service-area boundary:** which ZIPs (or parts of districts) are core and which are edge/tier 2? Does a student at a qualifying school who lives outside those ZIPs count as edge?
2. **Tiers:** is "Tier 2" one thing (edge of area **and/or** a weaker application) or two separate labels? Can an edge-of-area student still be Tier 1 on merit?
3. **Reviewers:** names and emails of the volunteers (nurse, manufacturer, tradespeople, educators, coach). Does each read only their own focus area, or all applications?
4. **Independent reads:** should reviewers see each other's notes and tiers, or read independently first so they don't anchor on each other?
5. **Name-blind:** should reviewers see names and addresses, or just ID, ZIP, school and content?
6. **How many reviews per application** before it comes to you? (Suggest 2 for the pilot.)
7. **AI flagging:** OK to send application text (with name/contact stripped) to an AI service? Any signals to add or remove from §4.5?
8. **Urgent cases:** who can flag one (reviewers, school contacts via you, the student)? Do you want a phone/text alert or is email enough?
9. **Records:** how long do we keep declined applications? Does your accountant need anything recorded per award (payee, ACH reference, 1099 status)?
10. **Word cap:** keep the 300-word career goal for the pilot (recommended), or open it up now?
11. **Transcripts:** they arrive at info@. Who checks that inbox and ticks "transcript received"? (Ties to the open info@ question.)

---

## 9. Not in scope for this spec

Pricing, the retainer, the public application form itself (already live at `/apply`), and decision-letter wording.
