"""Appends enriched people (output of parse_enrich.py) to targets.json and queue.json.
Skips: Qualcomm history, unverified emails, anyone already in targets/queue.
  python3 add_targets.py enriched.json [more.json ...]"""
import json
import sys

from templates import render

targets = json.load(open('targets.json'))
queue = json.load(open('queue.json'))
known = {t['email'].lower() for t in targets} | {q['email'].lower() for q in queue}
added, skipped = 0, []
for path in sys.argv[1:]:
    for t in json.load(open(path)):
        email = (t.get('email') or '').lower()
        if t.get('qualcomm') or any('qualcomm' in (h or '').lower() for h in t.get('history', [])):
            skipped.append((t['name'], 'qualcomm'))
            continue
        if t.get('email_status') != 'verified' or not email:
            skipped.append((t['name'], 'no verified email'))
            continue
        if email in known:
            skipped.append((t['name'], 'already queued'))
            continue
        subject, body = render(t)
        targets.append(t)
        queue.append(dict(name=t['name'], email=t['email'], org=t['org'], title=t['title'], segment=t['segment'],
                          subject=subject, body=body, status='queued', sent_at=None, thread_id=None, reply=None))
        known.add(email)
        added += 1
json.dump(targets, open('targets.json', 'w'), indent=1)
json.dump(queue, open('queue.json', 'w'), indent=1)
print('added', added, '| queued now', sum(q['status'] == 'queued' for q in queue), '| skipped', skipped)
