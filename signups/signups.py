"""Queue commands for the signup job. Never hand-edit queue.json; use these.

    python3 signups.py due                       emails to send now (JSON), within the send window and caps
    python3 signups.py sent EMAIL STEP THREAD_ID MESSAGE_ID
    python3 signups.py active                    emails to check for replies (JSON: email, kind, status, handled_ids)
    python3 signups.py handled EMAIL MESSAGE_ID  mark a reply message as dealt with
    python3 signups.py set EMAIL key=value ...   status / reply / meeting (logged)
    python3 signups.py status                    counts per status
"""

import collections
import datetime
import json
import sys
from zoneinfo import ZoneInfo

from store import load, save, log, now_pt, PT
from templates import render

FOLLOW_UP_DAYS = {1: 3, 2: 7}   # step -> days after the first email
GIVE_UP_DAYS = 14               # no reply this long after the first email -> no_reply
ACTIVE = ('sent', 'meeting_proposed', 'needs_ninad', 'replied')


def find(state, email):
    for item in state['items']:
        if item['email'] == email.lower():
            return item
    sys.exit(f"not in queue: {email}")


def due(state):
    cfg = state['config']
    now = datetime.datetime.now(PT)
    window = cfg['send_window']
    local = datetime.datetime.now(ZoneInfo(window['tz']))
    if not window['start_hour'] <= local.hour < window['end_hour']:
        return []
    out = []
    for item in state['items']:
        if item['kind'] == 'developer' and not cfg.get('developers_enabled'):
            continue
        if item['status'] == 'queued':
            step = 0
        elif item['status'] == 'sent' and item['steps']:
            first = datetime.datetime.fromisoformat(item['steps'][0]['sent_at'])
            step = len(item['steps'])
            if step > 2 or now < first + datetime.timedelta(days=FOLLOW_UP_DAYS[step]):
                continue
        else:
            continue
        subject, body = render(item, step)
        action = dict(email=item['email'], step=step, subject=subject, body=body)
        if step:
            action['replyThreadId'] = item['thread_id']
        out.append(action)
        if len(out) >= cfg['max_per_run']:
            break
    return out


def expire(state):
    """Sent items with no reply GIVE_UP_DAYS after the first email become no_reply."""
    now = datetime.datetime.now(PT)
    changed = False
    for item in state['items']:
        if item['status'] == 'sent' and len(item['steps']) >= 3:
            first = datetime.datetime.fromisoformat(item['steps'][0]['sent_at'])
            if now > first + datetime.timedelta(days=GIVE_UP_DAYS):
                item['status'] = 'no_reply'
                log(f"{item['email']}: no reply after 3 emails, stopped")
                changed = True
    return changed


def main():
    cmd, args = sys.argv[1], sys.argv[2:]
    state = load()
    if cmd == 'due':
        if expire(state):
            save(state)
        print(json.dumps(due(state), indent=2))
    elif cmd == 'sent':
        email, step, thread_id, message_id = args
        item = find(state, email)
        item['steps'].append(dict(step=int(step), sent_at=now_pt(), message_id=message_id))
        item['thread_id'] = item['thread_id'] or thread_id
        item['status'] = 'sent'
        save(state)
        log(f"{item['email']}: sent email {step} ({item['kind']})")
    elif cmd == 'active':
        print(json.dumps([dict(email=i['email'], kind=i['kind'], first=i['first'], status=i['status'],
                               thread_id=i['thread_id'], handled_ids=i['handled_ids'])
                          for i in state['items'] if i['status'] in ACTIVE], indent=2))
    elif cmd == 'handled':
        email, message_id = args
        item = find(state, email)
        if message_id not in item['handled_ids']:
            item['handled_ids'].append(message_id)
        save(state)
    elif cmd == 'set':
        item = find(state, args[0])
        for kv in args[1:]:
            key, value = kv.split('=', 1)
            if key not in ('status', 'reply', 'meeting'):
                sys.exit(f"can't set {key}")
            item[key] = value
        save(state)
        log(f"{item['email']}: " + '; '.join(args[1:]))
    elif cmd == 'status':
        print(dict(collections.Counter((i['kind'], i['status']) for i in state['items'])))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
