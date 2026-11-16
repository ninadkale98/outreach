"""queue.json + config.json + log.md helpers shared by sync_db.py and signups.py. Stdlib only."""

import datetime
import json
import os
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(HERE, 'queue.json')
CONFIG = os.path.join(HERE, 'config.json')
LOG = os.path.join(HERE, 'log.md')
PT = ZoneInfo('America/Los_Angeles')


def now_pt():
    return datetime.datetime.now(PT).isoformat(timespec='seconds')


def load():
    items = json.load(open(QUEUE)) if os.path.exists(QUEUE) else []
    return {'items': items, 'config': json.load(open(CONFIG))}


def save(state):
    tmp = QUEUE + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(state['items'], f, indent=2, default=str)
    os.replace(tmp, QUEUE)


def log(line):
    with open(LOG, 'a') as f:
        f.write(f"- {datetime.datetime.now(PT):%Y-%m-%d %H:%M} PT — {line}\n")
