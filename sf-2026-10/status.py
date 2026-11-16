"""Quick status: python3 status.py"""
import collections
import json

queue = json.load(open('queue.json'))
by = collections.Counter(q['status'] for q in queue)
print('total', len(queue), dict(by))
for q in queue:
    if q['status'] not in ('queued', 'sent'):
        print(f"- {q['status']:16s} {q['name']} ({q['org']}): {q.get('reply') or ''}")
sent_today = [q for q in queue if (q.get('sent_at') or '').startswith(__import__('datetime').date.today().isoformat())]
print('sent today', len(sent_today))
