# Signup outreach runbook

Goal: every person who signs up on CodePraxis gets a personal email from Ninad.
- **Companies** (`company_held`, `company_unfinished`): get a call with Ninad. No calendar invites, no
  links; just ask what they're hiring for and when suits them for a call. Ninad approves accounts by hand.
- **Developers** (`developer`): get them into the Discord community (https://discord.gg/Sh6jk3Hac).

Approved by Ninad 2026-10-31. Runs **headless** every hour: launchd → `run.sh` → `sync_db.py` (adds new
signups from the database) → `claude -p` with this file. Nobody watches the run: when unsure, don't send;
log it and notify Ninad. Work in this folder only.

## Hard rules
- Send only from Gmail = ninad@trycodepraxis.com, plain `body`, `includeSignature: false`.
- Never write "founder", "our clients", "revenue", "our company". Never send calendar invites or links
  other than the Discord link. Never promise pricing, features or dates; never approve accounts.
- Only touch people in `queue.json`. Change queue.json only through `python3 signups.py ...`.
- If a send fails or Gmail errors: stop, `python3 signups.py set <email> status=needs_ninad reply="send failed: ..."`,
  and `./notify.sh "Signup outreach stopped" "<reason>"`.
- Notify Ninad only with `./notify.sh "<title>" "<one line>"` (Pushover to his phone).

## 1. Send due emails
1. `python3 signups.py due` prints the emails to send now (send window and caps already applied).
2. For each: `send_message(to=[email], subject, body, includeSignature=false)` with subject/body exactly
   as given; for step 1 and 2 also pass `replyThreadId`. Right after each send:
   `python3 signups.py sent <email> <step> <threadId> <id>`. Wait ~30 s between sends
   (`python3 -c "import time; time.sleep(30)"`).

## 2. Reply check
1. `python3 signups.py active` lists who to check. Search Gmail:
   `in:inbox newer_than:14d from:(a@x.com OR b@y.com ...)`, plus
   `from:(mailer-daemon OR postmaster) newer_than:2d` for bounces of these addresses.
2. Skip messages whose id is in that person's `handled_ids`. For each new one, `get_thread` (PLAIN_TEXT),
   decide as below, then `python3 signups.py handled <email> <message id>`. Reply in the thread with
   `reply(messageId=<their message id>, body=..., includeSignature=false)`; short, plain, ending
   "Thanks,\nNinad". Use their first name.

### Companies
| Their reply | Do |
|---|---|
| Any interest: roles, numbers, "sure", a question about the product or price | Reply asking for a call: "Thanks {first}. Should we set up a quick call? Tell me a day and time that works for you, and the roles you're hiring for, so I come prepared." Drop the roles part if they already said. For a product/price question say Ninad will go through it on the call; don't answer it. `set status=meeting_proposed reply="<one-line summary>"`. Notify "Signup replied: <email>" with the summary. |
| Proposes a specific time | If it falls inside `call_window` in config.json (convert time zones; ask nothing else), confirm in one or two lines stating the time in their zone and in PT, e.g. "Tuesday 4pm IST (3:30am PT) works, talk then." Ask how they'd like to talk (phone or Google Meet) only if they didn't say. `set status=meeting_booked meeting="<their time> = <PT time>, <how>"`. Notify "MEETING: <name> (<company>) <time PT>". Outside the window: don't reply; `set status=needs_ninad`, notify "Signup wants <time>, outside your window". |
| Asks for a calendar invite / Calendly | Don't send one. Say Ninad will send the invite himself, `set status=needs_ninad`, notify. |
| Not hiring / not interested / unsubscribe | Don't reply. `set status=declined`. Notify. |
| Out of office | Nothing; keep status. |

### Developers
| Their reply | Do |
|---|---|
| Joined / thanks / will join | Reply one line: "Great, see you there. Post the role you want in the Discord so I can keep you in mind." `set status=done reply="<summary>"`. No notify. |
| Link doesn't work / asks how to join | Reply with the link again (https://discord.gg/Sh6jk3Hac). `set status=replied`. |
| Anything else (resume, job question, wants a call) | Don't reply. `set status=needs_ninad reply="<summary + suggested answer>"`. Notify "Developer replied: <email>". |
| Unsubscribe / not interested | `set status=declined`. No reply. |

### Bounces
`set status=bounced`. Notify if 2+ bounce in one run.

## 3. HubSpot (companies only, meeting_booked)
Search the contact by email (`search_crm_objects`); create it if missing. Create a deal "<Company or email>
- signup" in the default pipeline, stage Meeting booked (4425687786), owner 100915004, with a note
summarising the thread. One at a time.

## Files
`queue.json` everyone + status · `config.json` send/call windows, developers on/off, skip list ·
`templates.py` every email · `log.md` human log · `runs.log` raw run output · `launchd/` schedule
