"""Builds queue.json (one rendered email per target) from targets.json. Wording follows Ninad's
visa-safe InMail: problem -> "started as a tool for friends' hiring agencies" -> "thinking whether to
build a company" -> short meeting ask. Never says founder, clients or revenue."""
import json

VC_SUBJECT = "Advice on something we built (in SF till Nov 7)"
VC_BODY = """Hi {first},

I'm Ninad. AI has made cheating in technical assessments easy. Companies that hire on their own have to write questions, run proctoring and manage every round. The other option is an agency, which usually costs about one month's salary per hire and takes close to two months. Either way, hiring ends up slow and expensive.

We created a platform called CodePraxis. It started as a tool to help some friends who run hiring agencies with their technical screening, and it has saved them a lot of time and money. The assessments are the core of it: they hold up against AI-assisted cheating, and each candidate gets one detailed report. We're also organizing a hackathon for 50,000 students.

Now we're thinking about whether we can build a company out of it, and I could use some advice. I'm in San Francisco until November 7. Would you be open to a 20-minute coffee or call?

Thanks,
Ninad
codepraxis.co
"""

FOUNDER_SUBJECT = "How do you screen engineers at {company}?"
FOUNDER_BODY = """Hi {first},

I'm Ninad. I saw {company} is hiring engineers.

AI has made cheating in technical assessments easy. Teams that hire on their own end up writing questions, running proctoring and spending engineers' hours on every round. An agency usually costs about a month's salary per hire and takes close to two months.

We created a platform called CodePraxis. It started as a tool to help some friends who run hiring agencies with their technical screening, and it has saved them a lot of time and money. Candidates work in a real codebase with AI allowed, explain their own code, and do an AI interview that asks follow-ups like a senior engineer. Each candidate gets one detailed report.

Now we're thinking about whether we can build a company out of it. I'm in San Francisco until November 7. Would you have 20 minutes to tell me how you screen engineers today and give me honest feedback on what we built?

Thanks,
Ninad
codepraxis.co
"""

COMPANY = {'OpenArt AI': 'OpenArt', 'Broccoli AI': 'Broccoli'}
FIRST_VCS = ['Elizabeth Yin', 'Charles Hudson', 'Gaurav Jain', 'Christy Canida', 'Pavla Bobosikova', 'Tom Drummond']

targets = json.load(open('targets.json'))
vcs = sorted([t for t in targets if t['segment'] == 'vc'],
             key=lambda t: FIRST_VCS.index(t['name']) if t['name'] in FIRST_VCS else 99)
founders = [t for t in targets if t['segment'] == 'founder']

# Batches of 6: VCs first (meeting-ask), then founders, alternating so each batch mixes both.
order = []
while vcs or founders:
    order += vcs[:3] + founders[:3]
    vcs, founders = vcs[3:], founders[3:]

queue = []
for t in order:
    company = COMPANY.get(t['org'], t['org'])
    if t['segment'] == 'vc':
        subject, body = VC_SUBJECT, VC_BODY.format(first=t['first'])
    else:
        subject, body = FOUNDER_SUBJECT.format(company=company), FOUNDER_BODY.format(first=t['first'], company=company)
    queue.append(dict(name=t['name'], email=t['email'], org=t['org'], title=t['title'], segment=t['segment'],
                      subject=subject, body=body, status='queued', sent_at=None, thread_id=None, reply=None))
json.dump(queue, open('queue.json', 'w'), indent=1)
print(len(queue), 'queued')
for i, q in enumerate(queue):
    print(i, q['segment'], q['name'], '|', q['org'], '|', q['subject'])
