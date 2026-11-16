# outreach

Claude-run outreach daemons I built for my startup, CodePraxis.

- **`sf-2026-10/`**: a cold-email campaign. People are enriched through Apollo, deduplicated and filtered, then queued with segment-specific templates (`templates.py`). launchd jobs run `claude -p` against `RUNBOOK.md` to send on a schedule, refill the queue, check replies and propose meeting times, and notify me on my phone.
- **`signups/`**: follows up with every platform signup in a three-step email thread, syncs signups from the product database, handles replies (including scheduling calls inside a set window) and escalates anything unusual.
- **`ot.py`**: a small CLI that tracks every touch, task and reply per person.

No contact lists, queues or logs are included; the scripts expect their own local `queue.json`, `targets.json` and `config.json`.
