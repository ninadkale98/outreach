import json,sys,datetime as d,zoneinfo
em,tid,mid=sys.argv[1:4]
q=json.load(open('queue.json'))
now=d.datetime.now(zoneinfo.ZoneInfo('America/Los_Angeles')).isoformat(timespec='seconds')
for i in q:
    if i['email']==em:
        i.update(status='sent',sent_at=now,thread_id=tid,message_id=mid)
        open('log.md','a').write(f"| {now} | sent | {i['name']} | {i['org']} | {em} |\n")
json.dump(q,open('queue.json','w'),indent=2)
