# SF outreach runbook (Oct 29 – Nov 7, 2026)

Goal: get Ninad meetings in the Bay Area (weekday daytime) before Nov 7. Ninad approved (2026-10-28/29)
sending without per-email review, many per day (mailbox is warmed up), visa-safe wording only, and
replying to positive replies with time slots.

This runs **headless**: launchd starts `run.sh send|replies|refill`, which runs `claude -p` with this file.
Nobody is watching the run, so be conservative: when unsure, don't send; log it and notify Ninad.
Work in this folder only. Use `date` for the current time (Pacific).

## Hard rules
- Send only from Gmail = ninad@trycodepraxis.com (`mcp__claude_ai_Gmail__send_message`), plain `body`,
  `includeSignature: false`. Never Apollo (its signature says "Founder").
- Visa-safe: never "founder", "our clients", "revenue", "starting/scaling in the US", "our company".
  OK: "we created a platform", "started as a tool for friends who run hiring agencies",
  "thinking about whether we can build a company out of it", asking for advice/feedback/coffee.
- Never contact anyone at or formerly at Qualcomm (incl. Qualcomm Ventures) or Ninad's own contacts.
- Send around the clock, every day including weekends (Ninad's decision 2026-10-29). Max **10 new emails
  per rolling 60 minutes** (count `sent_at` in the last hour), max 240 per day.
- Never email the same person twice from the queue. Never send follow-ups except replies in a thread
  as described below.
- If a send fails, Gmail errors, or 3+ bounces arrive in a day: stop sending, write it in log.md, and
  run `./notify.sh "Outreach stopped" "<reason>"`.
- Notify Ninad only with `./notify.sh "<title>" "<one line>"` (Pushover to his phone).

## Send batch (every hour, 24/7)
1. `date` for the current time.
2. Load `queue.json`. Count items whose `sent_at` is within the last 60 minutes; allowed = 10 minus that
   (stop if 0). Also stop if 240 were sent since midnight PT.
3. Take the next `allowed` items with `status == "queued"`.
4. For each, call `send_message(to=[email], subject, body, includeSignature=false)` with the stored
   subject/body exactly. Immediately after each send, update that item in queue.json:
   `status="sent"`, `sent_at` (ISO, PT), `thread_id`, `message_id`; append a row to log.md.
   Use a small python3 script to edit the JSON (don't hand-edit). Wait ~30–60 s between sends
   (`python3 -c "import time; time.sleep(45)"`).
5. If fewer than 10 are queued, run nothing extra; the refill job handles it.

## Reply check (every hour, 24/7)
1. Build a Gmail query from all queue items with status in sent / meeting_proposed / needs_ninad:
   `in:inbox newer_than:7d from:(a@x.com OR b@y.com ...)` (split into chunks of ~25 addresses).
   Also `from:(mailer-daemon OR postmaster) newer_than:2d` for bounces.
2. Ignore messages already handled (their Gmail message id is in the item's `handled_ids`).
3. For each new reply, `get_thread` (PLAIN_TEXT) and decide:
   - **Wants to meet / open to chat:** reply in the thread with `reply(messageId=<their message>)`,
     short, in Ninad's voice, visa-safe, no signature block, ending "Thanks, Ninad". Offer 3 concrete
     slots on weekdays in the next 7 days before Nov 7, between 10:00 and 16:00 PT (e.g. "Mon Nov 2 at
     11am, Tue Nov 3 at 2pm or Wed Nov 4 at 10am PT"), coffee in SF or a video call, "or any time that
     suits you". Set `status="meeting_proposed"`. Notify Ninad.
   - **They accept a specific time:** confirm it in the thread (one or two lines), set
     `status="meeting_booked"`, `meeting` = time + place. Notify Ninad: "MEETING: <name> (<org>) <time>".
   - **Anything else** (question, wants deck/metrics, intro to someone else, not interested, OOO):
     do NOT reply. Set `status="needs_ninad"` (or `"declined"` / keep `sent` for OOO), write the
     reply summary + a suggested answer in log.md, notify Ninad (skip notifying for OOO).
   - **Bounce:** `status="bounced"`.
   Record the handled Gmail message id in `handled_ids` and a one-line summary in `reply`.
4. HubSpot (only for meeting_proposed / meeting_booked): search the contact by email (inbox sync usually
   created it); if there's no deal "<Org> - intro", create one in pipeline default, stage Replied
   (4425687785) or Meeting booked (4425687786), owner 100915004, with a note summarising the thread.
   One company at a time; never bulk.
5. If nothing new: append nothing, just finish.

## Refill (every 4 hours, 24/7)
If fewer than 30 items are `queued`, add up to 40 new verified targets (≤ 45 Apollo credits per run,
≤ 250 per day). First check credits with `apollo_usage_stats_credit_usage_stats`: if fewer than 100 lead
credits are left, don't refill; notify Ninad once per day ("Apollo credits low") and stop.
- **Investors** (segment `vc`): partners/principals at Bay Area pre-seed/seed funds that back AI,
  developer tools, future of work or B2B software. Use `apollo_mixed_people_api_search` with
  `q_organization_domains_list` of specific funds not yet in targets.json, titles partner/GP/principal.
- **Startup leaders** (segment `founder`): CTO > CEO > VP Eng/founder, one per company, at SF or
  Fremont startups (11–200 people) funded in the last ~12 months with software-engineering jobs posted
  in the last 30 days (`apollo_mixed_companies_search`, then people search by organization_ids).
  Skip companies in recruiting/HR assessment (competitors), robotics/hardware/bio, and subsidiaries.
- **Tech leaders** (segment `leader`): CTO / Chief AI Officer at Bay Area software companies with
  200–5,000 people.
Then: enrich only the chosen people with `apollo_people_bulk_match` (≤ 10 per call). Big results are
saved to a file; run `python3 parse_enrich.py <saved file> new_<date>_<n>.json <segment>`. Check HubSpot
contacts by email (skip anyone found). Then `python3 add_targets.py new_*.json` — it renders the email
from templates.py, drops Qualcomm history / unverified / duplicates. Log the count in log.md.

## Files
- `queue.json` every email + status; `targets.json` enriched people; `log.md` human log; `runs.log` raw run output
- `templates.py` the three email versions; `add_targets.py`, `parse_enrich.py`, `status.py`
- `run.sh` launchd entry point; `notify.sh` phone alert; `launchd/` the schedules
