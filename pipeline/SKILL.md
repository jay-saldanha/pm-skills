# Job Search Skill

Runs the automated job search workflow for Jayana. Searches for new roles, scores them against the candidate profile, generates tailored cover letters + CV headlines, updates the tracker and dedup index.

## Trigger

Use this skill when the user says any of:
- `/pipeline`
- "run a job search"
- "find new jobs"
- "search for jobs"
- "check for new roles"
- "here are my saved LinkedIn jobs" / pastes a list of LinkedIn URLs or job titles
- "process these jobs" / "score these"

---

## Workflow

### Entry point: Detect mode

Before Step 0, determine which mode to run:

| Mode | When | What to do |
|---|---|---|
| **Search mode** | User runs `/pipeline` with no additional input | Run full search workflow (Steps 0–7) |
| **LinkedIn intake mode** | User pastes LinkedIn URLs, job titles, or a saved-jobs list | Skip search (Step 1); go directly to dedup + score (Steps 0, 2–7) |

**LinkedIn intake mode — accepted formats:**
- One or more `linkedin.com/jobs/view/...` URLs (one per line)
- A pasted list of "Job Title — Company" lines (with or without URLs)
- A mix of both

If the format is ambiguous (e.g. just company + title, no URL), WebSearch for the exact posting to get the canonical URL before deduping.

---

### Step 0 — Load context (do this first, every time)

Read these four files before doing anything else:

1. **Profile:** `/Users/jayana/UMD Docs/Job related/Background.md`
   - Target titles, domains, salary floor ($160k), location (remote PST)

2. **Seen jobs index:** `/Users/jayana/UMD Docs/Job related/seen_jobs.md`
   - All URLs ever processed. Skip any job whose URL appears here.

3. **Current pipeline:** `/Users/jayana/UMD Docs/Job related/Pipeline.md`
   - Check current Researching count and weekly log for context.

4. **Review log:** `/Users/jayana/UMD Docs/Job related/Review_Log.md`
   - User's manual review history. Use this to spot patterns (e.g. consistently rejecting a domain or company type) and factor into scoring notes.

---

### Step 1 — Search (run all queries in parallel)

Run WebSearch for each query below. Collect all result URLs and titles.

**Query set A — Core PM/PgM roles:**
```
"Principal Product Manager" OR "Staff Product Manager" OR "Senior Program Manager" "content" OR "enablement" OR "onboarding" remote site:greenhouse.io April 2026
```
```
"Staff Product Manager" OR "Principal Program Manager" "content tooling" OR "product enablement" OR "product onboarding" remote PST $160,000 site:lever.co OR site:jobs.ashbyhq.com
```

**Query set B — Technical Product Marketing / Content Marketing:**
```
"Principal Technical Product Marketing Manager" OR "Staff Content Marketing Manager" OR "Senior Technical PMM" remote "west coast" OR PST 2026 site:greenhouse.io OR site:lever.co
```
```
"Senior Product Marketing Manager" OR "Principal PMM" "technical" OR "developer" OR "API" OR "platform" remote $160,000 April 2026
```

**Query set C — Civic tech:**
```
"Senior Product Manager" OR "Principal Program Manager" "civic tech" OR "government" OR "public sector" OR "digital services" remote 2026 site:greenhouse.io OR site:lever.co
```
```
site:skylight.digital OR site:navapbc.com OR site:usds.gov "product manager" OR "program manager" senior remote 2026
```

**Query set D — General board sweep:**
```
site:himalayas.app "Staff Product Manager" OR "Principal Product Manager" "content" OR "enablement" OR "onboarding" remote 2026
```
```
site:wellfound.com "Principal" OR "Staff" "product manager" "content" OR "enablement" remote 2026
```
```
site:linkedin.com/jobs "Principal Product Manager" OR "Staff Product Manager" OR "Principal Program Manager" "content" OR "enablement" OR "onboarding" remote 2026
```
```
site:linkedin.com/jobs "Principal Technical Product Marketing Manager" OR "Staff Content Marketing Manager" OR "Senior PMM" "developer" OR "platform" OR "API" remote 2026
```

**Query set E — First-party career portals (big tech + relevant platforms):**
```
site:careers.google.com "product manager" OR "program manager" "content" OR "enablement" OR "developer experience" remote 2026
```
```
site:jobs.microsoft.com "principal product manager" OR "senior program manager" "content" OR "enablement" OR "developer" remote 2026
```
```
site:openai.com/careers "product manager" OR "program manager" remote 2026
```
```
site:anthropic.com/careers "product manager" OR "program manager" remote 2026
```
```
site:figma.com/careers "product manager" OR "program manager" "content" OR "enablement" remote 2026
```
```
site:notion.so/careers OR site:grnh.se "product manager" "content" OR "platform" OR "onboarding" remote 2026
```
```
site:stripe.com/jobs "product manager" OR "program manager" "content" OR "enablement" OR "developer" remote 2026
```
```
site:salesforce.com/careers "principal product manager" OR "staff product manager" "content" OR "enablement" remote 2026
```
```
site:adobe.com/careers "principal product manager" OR "senior program manager" "content" OR "enablement" remote 2026
```

**Query set F — Pre-IPO companies (late-stage, well-funded, domain-adjacent):**
```
"product manager" OR "program manager" "content" OR "enablement" OR "onboarding" remote site:jobs.ashbyhq.com OR site:lever.co (Perplexity OR Cohere OR Harvey OR "Scale AI" OR Rippling OR Airtable OR Linear OR Anduril OR Databricks OR Intercom OR Loom) 2026
```
```
"Perplexity" OR "Cohere" OR "Harvey" "product manager" OR "program manager" "content" OR "enablement" remote $160,000 2026
```
```
"Rippling" OR "Airtable" OR "Linear" OR "Intercom" "principal product manager" OR "staff product manager" OR "senior program manager" remote 2026 content OR enablement OR onboarding
```
```
"Databricks" OR "Anduril" OR "Scale AI" OR "Anthropic" OR "OpenAI" "principal" OR "staff" "product manager" OR "program manager" "content" OR "technical" OR "enablement" remote 2026
```

---

### Step 2 — Deduplicate

For each URL found in search results:
- Check against `seen_jobs.md`
- If URL already exists → skip, do not score
- If URL is new → proceed to scoring

---

### Step 3 — Score each new job (0–100)

Use this rubric for every new job:

| Criterion | Max pts |
|---|---|
| Role title matches seniority target (Principal/Senior/Staff PM, PgM, or Technical PMM) | 25 |
| Domain overlap (content tooling, enablement, onboarding, product marketing, civic tech) | 30 |
| Location fit: Remote = 15pts · Hybrid/onsite in Seattle/Redmond/Kirkland/Bellevue/Bothell = 12pts · Hybrid elsewhere PST = 6pts · Onsite outside these cities or EST-only = 0pts | 15 |
| Company fit (tech/SaaS/civic, well-funded, good culture signals) | 20 |
| Salary signals ≥ $160k (explicit range, company benchmarks, or strong inference) | 10 |

**Recency filter:**
- Score < 75 → must be posted within 5 days, otherwise skip
- Score ≥ 75 → accept if posted within 15 days
- Older than 15 days → reject regardless of score

**Threshold:** Only proceed with jobs scoring **70 or above**.

---

### Step 4 — For each qualifying job

Do all of these in order:

**a. Research the company**
WebSearch: `[Company] culture remote work product team 2025 2026 Glassdoor`

**b. Generate cover letter**
3 paragraphs, 250–350 words:
1. Hook — reference specific company/product detail from research
2. Fit — map Jayana's actual experience (Sardine → Square → AWS) to JD requirements with real metrics
3. Close — enthusiasm + clear ask

Never use generic openers. Always use her real titles and companies. Pull from Background.md for specific bullets and numbers.

**c. Generate tailored CV**

Read the master resume at `Background.md`. Produce a role-specific overlay with these four components, mirroring the JD's exact language and terminology throughout:

1. **Headline** — pick from the Headline Variants table in `Background.md`, or write a new variant using the JD's own title language
2. **Summary** (3–4 sentences) — rewrite using JD terminology: adopt their nouns (e.g. "onboarding systems", "GTM strategy", "content tooling"), their action verbs, and their framing of the problem
3. **Core Impacts** (5 bullets) — rewrite the top quantified achievements using JD language and priority order. Lead with the metrics and outcomes the JD cares most about. Do not invent new achievements. Do not remove metrics.
4. **Experience bullets** (per role: Sardine → Square → AWS) — reword 3–4 bullets per company to front-load JD keywords while keeping all real metrics intact. Do not invent new achievements. Do not remove metrics.
5. **Skills emphasis line** — list the specific skills from the JD that Jayana holds, in JD terminology

Append the tailored CV to `/Users/jayana/UMD Docs/Job related/Tailored_CVs.md` under a new `## [#]. [Company] — [Role]` heading.

Reference file for all existing tailored CVs: `/Users/jayana/UMD Docs/Job related/Tailored_CVs.md`

**d. Draft application email**
Short, 3 sentences max:
- Line 1: Role name + interest signal
- Line 2: One specific reason this company/team
- Line 3: CTA + contact (jayana.saldanha@outlook.com)

**e. Update Pipeline.md**
Add a new row to the Opportunities table:
```
| [next #] | [Company] | [Role] | Researching | [Score] | [Salary] | — | [Today + 7 days] | [URL] | [Notes] |
```

Add cover letter + email draft to the Cover Letters and Draft Application Emails sections.

**f. Log to seen_jobs.md**
Append a new row regardless of outcome (pass or fail):
```
| [URL] | [Company] | [Role] | [Today's date] | [Disposition] |
```

---

### Step 5 — Also log rejected/skipped jobs to seen_jobs.md

For every job that was found but did NOT qualify (wrong domain, too old, below salary floor, below score threshold), still add it to `seen_jobs.md` with disposition "Rejected (reason)" or "Skipped (reason)". This prevents re-surfacing.

---

### Step 6 — Update Pipeline.md weekly log

Append a row to the Weekly Log table:
```
| [Today's date] | Run #N: Found X jobs, Y new (not in index), Z qualified (scores). Top match: [Company] #[score]. Cover letters drafted for [list]. |
```

Update the Stats table: increment Jobs Found, Researching count.

---

### Step 7 — Report to user

Output a clean summary table:

**Qualifying jobs this run:**
| Company | Role | Score | Salary | URL |
|---|---|---|---|---|

**Filtered out:** X jobs (reason breakdown)
**Action needed:** List any jobs with urgent deadlines or unconfirmed salaries.

After presenting results, prompt the user to fill in the Review Log:

> "Please review the jobs above and update your Review Log. For each one, note: Did the job exist when you clicked? Is it a fit? Why or why not?"
>
> Template row to copy:
> ```
> | [Today's date] | [Company] | [Role] | Yes / No | Fit / Not Fit | [Your reason] |
> ```
> File: `/Users/jayana/UMD Docs/Job related/Review_Log.md`

If the user provides review feedback directly in chat, append it to `Review_Log.md` automatically.

---

## Profile Quick Reference

| Field | Value |
|---|---|
| Name | Jayana Saldanha |
| Location | Redmond, WA — Remote preferred; hybrid/onsite OK in Seattle, Redmond, Kirkland, Bellevue, Bothell |
| Current | Content & Enablement Leader, Sardine (reporting to CPO) |
| Prior | PM Developer Content Experience, Square · Product Content PM, AWS |
| Target titles | Principal / Senior / Staff PM · PgM · Technical PMM · Content Marketing Mgr |
| Domains | Content tooling · Content mgmt · Product enablement · Product marketing · Product onboarding · Civic tech |
| Salary floor | $160,000 base |
| Email | jayana.saldanha@outlook.com |
| CV | `/Users/jayana/UMD Docs/Job related/Background.md` |
| Tailored CVs | `/Users/jayana/UMD Docs/Job related/Tailored_CVs.md` |
| Tracker | `/Users/jayana/UMD Docs/Job related/Pipeline.md` |
| Seen index | `/Users/jayana/UMD Docs/Job related/seen_jobs.md` |

---

## Rules (applied every run)

1. **Never re-surface a seen URL.** Check seen_jobs.md first.
2. **Tailor every cover letter** to the specific JD — no generic paragraphs.
3. **Swap CV headline** to match the target role type (variants in Background.md).
4. **Salary floor is hard:** $160k base minimum. Flag if unconfirmed; don't auto-reject but note the risk.
5. **Recency is enforced:** 5-day default, 15-day relaxed only for score ≥ 75.
6. **Cover letter uses real data:** Sardine TTV program (20% friction reduction), Square portal consolidation (50% efficiency gain), AWS DevCon (1,000+ attendees), Devin AI integration (40% automation, 25% velocity).
