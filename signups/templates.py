"""Emails to platform signups. Step 0 is the first email, steps 1 and 2 are follow-ups in the same thread
(day 3 and day 7). Plain text, no signature block, no calendar links."""

DISCORD = "https://discord.gg/Sh6jk3Hac"  # expires 2026-12-01: replace with a never-expiring invite before then
SIGN = "\n\nThanks,\nNinad"

TEMPLATES = {
    # Submitted company details; held until Ninad approves after a call.
    'company_held': [
        ("Your CodePraxis account",
         "Hi {first},\n\nThanks for signing up for CodePraxis. I'm Ninad, and I'll be setting up your account.\n\n"
         "Before I switch it on, I'd like to understand what you're hiring for, so the assessments match your "
         "roles. Which roles are you hiring for right now, and roughly how many candidates do you screen a "
         "month?\n\nIf a quick call is easier, just tell me a time that works for you." + SIGN),
        (None, "Hi {first}, just checking if you saw my note. What roles are you hiring for right now? A one-line "
               "reply is enough." + SIGN),
        (None, "Hi {first}, last note from me. If you're still hiring engineers, reply with the role and I'll set "
               "up your account and a first assessment for it." + SIGN),
    ],
    # Signed in on the company page but never submitted company details.
    'company_unfinished': [
        ("Finishing your CodePraxis signup",
         "Hi {first},\n\nI saw you signed in to CodePraxis but didn't finish setting up your company. I'm Ninad. "
         "I can set it up for you and build your first assessment.\n\nWhat roles are you hiring for? Happy to do "
         "a quick call if that's easier. Just tell me a time that works." + SIGN),
        (None, "Hi {first}, just checking if you saw my note. What roles are you hiring for right now? A one-line "
               "reply is enough." + SIGN),
        (None, "Hi {first}, last note from me. If you're still hiring engineers, reply with the role and I'll set "
               "up your account and a first assessment for it." + SIGN),
    ],
    # Developer waitlist / developer sign-in. Goal: get them into the Discord community.
    'developer': [
        ("Your CodePraxis waitlist spot",
         "Hi {first},\n\nThanks for joining the CodePraxis developer waitlist. I'm Ninad.\n\nWe want to help you "
         "get a job. We're building our developer community on Discord, and that's where we'll share openings "
         "and help you get hired.\n\nJoin here: " + DISCORD + "\n\nOnce you're in, post your name and the role "
         "you want{positions_hint}, so I can keep you in mind for openings." + SIGN),
        (None, "Hi {first}, in case this got buried, here's the Discord link again: " + DISCORD + "\n\nOnce you "
               "join, post the role you want and I'll keep you in mind for openings." + SIGN),
        (None, "Hi {first}, last note from me. If you're still looking for a job, join us here: " + DISCORD + SIGN),
    ],
}

# Reply templates the reply-check job adapts (see RUNBOOK.md).
COMPANY_CALL_ASK = ("Thanks {first}. Should we set up a quick call? Tell me a day and time that works for you, "
                    "and the roles you're hiring for, so I come prepared." + SIGN)

BANNED = ['founder', 'our clients', 'revenue', 'our company', 'calendly', 'invite']


def render(item, step):
    subject, body = TEMPLATES[item['kind']][step]
    positions = (item.get('positions') or '').strip()
    body = body.format(first=item['first'], positions_hint=f" ({positions})" if positions else "")
    subject = subject or "Re: " + TEMPLATES[item['kind']][0][0]
    lowered = (subject + body).lower()
    assert not any(b in lowered for b in BANNED), f"banned wording for {item['email']}"
    return subject, body
