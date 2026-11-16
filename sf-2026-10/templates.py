"""Visa-safe email templates, one per segment. Wording follows Ninad's own InMail: problem ->
"started as a tool for friends who run hiring agencies" -> "thinking whether to build a company" ->
short meeting ask. Never: founder, clients, revenue, our company."""

PROBLEM = ("AI has made cheating in technical assessments easy. Companies that hire on their own have to write "
           "questions, run proctoring and manage every round. The other option is an agency, which usually costs "
           "about one month's salary per hire and takes close to two months. Either way, hiring ends up slow and "
           "expensive.")
ORIGIN = ("We created a platform called CodePraxis. It started as a tool to help some friends who run hiring "
          "agencies with their technical screening, and it has saved them a lot of time and money.")
PRODUCT = ("Candidates work in a real codebase with AI allowed, explain their own code, and do an AI interview that "
           "asks follow-ups like a senior engineer. Each candidate gets one detailed report.")
SIGN = "\n\nThanks,\nNinad\ncodepraxis.co\n"

TEMPLATES = {
    'vc': ("Advice on something we built (in SF till Nov 7)",
           "Hi {first},\n\nI'm Ninad. " + PROBLEM + "\n\n" + ORIGIN + " The assessments are the core of it: they "
           "hold up against AI-assisted cheating, and each candidate gets one detailed report. We're also organizing "
           "a hackathon for 50,000 students.\n\nNow we're thinking about whether we can build a company out of it, "
           "and I could use some advice. I'm in San Francisco until November 7. Would you be open to a 20-minute "
           "coffee or call?" + SIGN),
    'founder': ("How do you screen engineers at {company}?",
                "Hi {first},\n\nI'm Ninad. I saw {company} is hiring engineers.\n\nAI has made cheating in technical "
                "assessments easy. Teams that hire on their own end up writing questions, running proctoring and "
                "spending engineers' hours on every round. An agency usually costs about a month's salary per hire "
                "and takes close to two months.\n\n" + ORIGIN + " " + PRODUCT + "\n\nNow we're thinking about whether "
                "we can build a company out of it. I'm in San Francisco until November 7. Would you have 20 minutes "
                "to tell me how you screen engineers today and give me honest feedback on what we built?" + SIGN),
    'leader': ("Advice from someone who hires a lot of engineers?",
               "Hi {first},\n\nI'm Ninad. " + PROBLEM + "\n\n" + ORIGIN + " " + PRODUCT + "\n\nNow we're thinking "
               "about whether we can build a company out of it, and I could use advice from someone who has built "
               "and hired engineering teams. I'm in the Bay Area until November 7. Would you be open to a 20-minute "
               "coffee or call?" + SIGN),
}

COMPANY_NAMES = {'OpenArt AI': 'OpenArt', 'Broccoli AI': 'Broccoli'}

BANNED = ['founder', 'our clients', 'revenue', 'our company', 'scaling in the us', 'starting in the us']


def render(target):
    subject, body = TEMPLATES[target['segment']]
    company = COMPANY_NAMES.get(target['org'], target['org'])
    subject, body = subject.format(company=company), body.format(first=target['first'], company=company)
    lowered = (subject + body).lower()
    assert not any(b in lowered for b in BANNED), f'visa-unsafe wording for {target["name"]}'
    return subject, body
