"""Add new platform signups to queue.json. Read-only against the prod database.

Who is added (once, keyed by email):
  developer           every verified developer_waitlist row, and self sign-up users with account_type developer
  company_held        self sign-up company users whose company membership is not verified yet
  company_unfinished  self sign-up company users with no membership (never submitted company details)
Skipped: team / platform-company users, invited users, candidates (see backend/scripts/export_signups.py),
blocked users, `.local` addresses, anyone in config.json "skip". A developer email wins over a company one.

Run with the backend venv (psycopg2 + dotenv):
    ../../backend/.venv/bin/python sync_db.py
"""

import datetime
import json
import os
import sys

import psycopg2
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(HERE, '..', '..', 'backend')
sys.path.insert(0, os.path.join(BACKEND, 'scripts'))
import export_signups as es  # noqa: E402  (shared signup classification)

from store import load, save, log, now_pt  # noqa: E402

WAITLIST_SQL = """SELECT email, name, positions, created_at FROM developer_waitlist
                  WHERE email_verified ORDER BY created_at"""
HELD_SQL = """SELECT DISTINCT m.user_id, c.name FROM memberships m JOIN companies c ON c.company_id = m.company_id
              WHERE m.company_id <> 1 AND NOT m.verified"""


def first_name(name, email):
    name = (name or '').strip()
    if not name or '@' in name:
        return 'there'
    return name.split()[0].capitalize()


def main():
    load_dotenv(os.path.join(BACKEND, '.env'))
    conn = psycopg2.connect(
        host=os.environ["PGHOST"], port=os.environ.get("PGPORT", 5432), dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"], password=os.environ["PGPASSWORD"], sslmode="require", connect_timeout=15,
    )
    conn.set_session(readonly=True)
    with conn, conn.cursor() as cur:
        cur.execute(es.SQL, {"platform": list(es.PLATFORM_COMPANIES)})
        cols = [d[0] for d in cur.description]
        users = [dict(zip(cols, r)) for r in cur.fetchall()]
        cur.execute(WAITLIST_SQL)
        waitlist = cur.fetchall()
        cur.execute(HELD_SQL)
        held = dict(cur.fetchall())
    conn.close()

    found = {}
    for email, name, positions, created in waitlist:
        found[email.lower()] = dict(kind='developer', first=first_name(name, email), name=name,
                                    positions=positions, company=None, signed_up=created.isoformat())
    for u in users:
        email = (u['email'] or '').lower()
        if not email or email in found or email.endswith('.local') or u['is_blocked']:
            continue
        if es.source(u) != 'self sign-up':
            continue
        base = dict(first=first_name(u['display_name'], email), name=u['display_name'], positions=None,
                    signed_up=u['created_at'].isoformat())
        if u['account_type'] == 'developer':
            found[email] = dict(base, kind='developer', company=None)
        elif u['user_id'] in held:
            found[email] = dict(base, kind='company_held', company=held[u['user_id']])
        elif not u['companies']:
            found[email] = dict(base, kind='company_unfinished', company=None)

    state = load()
    skip = {e.lower() for e in state['config'].get('skip', {})}
    known = {i['email'] for i in state['items']}
    added = []
    for email, info in found.items():
        if email in known or email in skip:
            continue
        state['items'].append(dict(email=email, status='queued', added_at=now_pt(), steps=[], thread_id=None,
                                   handled_ids=[], reply='', meeting='', **info))
        added.append(f"{email} ({info['kind']})")
    if added:
        save(state)
        log(f"sync: queued {len(added)}: " + ', '.join(added))
    print(f"sync {datetime.datetime.now():%F %T}: {len(found)} signups found, {len(added)} new")


if __name__ == '__main__':
    main()
