"""Turn a saved apollo_people_bulk_match result into a compact list.  parse_enrich.py RESULT.txt OUT.json SEGMENT"""
import json, sys
raw = json.load(open(sys.argv[1]))
txt = ''.join(r['text'] for r in raw if r.get('type') == 'text')
d, _ = json.JSONDecoder().raw_decode(txt.lstrip())
out = []
for m in d.get('matches', []):
    if not m:
        continue
    hist = [(h.get('organization_name') or '') for h in m.get('employment_history', [])]
    out.append(dict(apollo_id=m['id'], name=m.get('name'), first=m.get('first_name'), title=m.get('title'),
                    org=(m.get('organization') or {}).get('name'), domain=(m.get('organization') or {}).get('primary_domain'),
                    email=m.get('email'), email_status=m.get('email_status'), city=m.get('city'), state=m.get('state'),
                    linkedin=m.get('linkedin_url'), qualcomm=any('qualcomm' in h.lower() for h in hist),
                    history=hist[:8], segment=sys.argv[3]))
for o in out:
    print(f"{o['name']:22s} | {(o['org'] or '')[:22]:22s} | {o['email']} ({o['email_status']}) | {o['city']} | QC={o['qualcomm']}")
json.dump(out, open(sys.argv[2], 'w'), indent=1)
print('credits', d.get('credits_consumed'), 'matched', len(out))
