"""Appends senior tech leaders  to queue.json without touching existing entries.
Same visa-safe wording; the ask is advice from someone who builds and hires engineering teams."""
import json

SUBJECT = "Advice from someone who hires a lot of engineers?"
BODY = """Hi {first},

I'm Ninad. AI has made cheating in technical assessments easy. Companies that hire on their own have to write questions, run proctoring and manage every round. The other option is an agency, which usually costs about one month's salary per hire and takes close to two months. Either way, hiring ends up slow and expensive.

We created a platform called CodePraxis. It started as a tool to help some friends who run hiring agencies with their technical screening, and it has saved them a lot of time and money. Candidates work in a real codebase with AI allowed, explain their own code, and do an AI interview that asks follow-ups like a senior engineer. Each candidate gets one detailed report.

Now we're thinking about whether we can build a company out of it, and I could use advice from someone who has built and hired engineering teams. I'm in the Bay Area until November 7. Would you be open to a 20-minute coffee or call?

Thanks,
Ninad
codepraxis.co
"""

queue = json.load(open('queue.json'))
known = {q['email'] for q in queue}
leaders = json.load(open('leaders_batch1.json')) + json.load(open('leaders_batch2.json'))
added = 0
for t in leaders:
    if t['qualcomm'] or t['email_status'] != 'verified' or t['email'] in known:
        continue
    queue.append(dict(name=t['name'], email=t['email'], org=t['org'], title=t['title'], segment='leader',
                      subject=SUBJECT, body=BODY.format(first=t['first']), status='queued', sent_at=None,
                      thread_id=None, reply=None))
    added += 1
json.dump(queue, open('queue.json', 'w'), indent=1)
targets = json.load(open('targets.json'))
json.dump(targets + [t for t in leaders if t['email'] not in {x['email'] for x in targets}], open('targets.json', 'w'), indent=1)
print('added', added, 'queue now', len(queue), 'queued', sum(q['status'] == 'queued' for q in queue))
