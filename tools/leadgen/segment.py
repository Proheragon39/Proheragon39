import json, csv, re, sys, collections
d=json.load(open(sys.argv[1]))
PRI={'tourism=hotel':3,'tourism=guest_house':3,'amenity=dentist':3,'amenity=clinic':3,'amenity=restaurant':3,
     'shop=beauty':2,'shop=hairdresser':2,'leisure=fitness_centre':2,'tourism=hostel':2,'tourism=apartment':2,
     'amenity=cafe':2,'amenity=bar':2,'amenity=pub':2,'tourism=motel':2,'shop=bakery':1,'shop=florist':1,
     'shop=cosmetics':1,'shop=clothes':1,'amenity=fast_food':1}
def mob(p):
    for q in re.split(r'[;,]',p):
        n=re.sub(r'\D','',q)
        if n.startswith('995'): n=n[3:]
        if len(n)==9 and n[0]=='5': return '+995'+n
    return ''
rows=[]
for x in d:
    st=x.get('site_status','none')
    if re.search(r'booking\.com|airbnb|tripadvisor|facebook\.com|instagram\.com',x['website']): prob='Нет своего сайта (только Booking/Airbnb/соцсети)'
    elif st=='none' or x.get('social_only'): prob='Нет сайта'+(' (только соцсети)' if (x['instagram'] or x['facebook'] or x.get('social_only')) else '')
    elif st=='dead': prob='Сайт не открывается'
    elif not x.get('mobile'): prob='Сайт не адаптирован под телефон'
    elif not x.get('https'): prob='Сайт без HTTPS (браузер пишет «небезопасно»)'
    else: continue
    m=mob(x['phone'])
    if not (x['email'] or m): continue
    score=PRI.get(x['cat'],1)*10 + (5 if x['email'] else 0) + (3 if prob.startswith('Сайт не открывается') else 0) + (2 if x['instagram'] or x['facebook'] else 0)
    rows.append(dict(score=score,name=x['name_en'] or x['name'],name_local=x['name'],type=x['cat'].split('=')[1],
        city=x['city'],problem=prob,email=x['email'],whatsapp=m,phone=x['phone'],website=x['website'],
        instagram=x['instagram'],facebook=x['facebook'],
        map=f"https://www.openstreetmap.org/?mlat={x['lat']}&mlon={x['lon']}#map=18/{x['lat']}/{x['lon']}" if x['lat'] else '',
        status='new'))
rows.sort(key=lambda r:-r['score'])
seen=set(); uniq=[]
for r in rows:
    k=r['email'] or r['whatsapp']
    if k in seen: continue
    seen.add(k); uniq.append(r)
with open(sys.argv[2],'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(uniq[0].keys())); w.writeheader(); w.writerows(uniq)
print('total',len(uniq),'with email',sum(1 for r in uniq if r['email']),'whatsapp only',sum(1 for r in uniq if not r['email']))
print(collections.Counter(r['problem'] for r in uniq if r['email']))
print(collections.Counter(r['type'] for r in uniq if r['email']).most_common(12))
