import json, re, sys, concurrent.futures as cf, urllib.request, ssl
d=json.load(open(sys.argv[1]))
def occupied(x):
    la,lo=x['lat'],x['lon']
    if la is None: return False
    if lo<41.6 and la>42.42: return True          # Abkhazia + Sochi
    if 43.4<lo<44.5 and 42.15<la<42.75: return True # South Ossetia (rough)
    return False
d=[x for x in d if not occupied(x)]
EM=re.compile(r'^[\w.+-]+@[\w-]+(\.[\w-]+)+$')
for x in d:
    x['email']=x['email'].split(';')[0].strip()
    if x['email'] and not EM.match(x['email']): x['email']=''
def chk(x):
    u=x['website'].split(';')[0].strip()
    if not u: return x
    if not u.startswith('http'): u='http://'+u
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=15)
        html=r.read(300000).decode('utf-8','ignore').lower()
        x['site_status']='ok'; x['final_url']=r.geturl()
        x['https']=r.geturl().startswith('https')
        x['mobile']='name="viewport"' in html or "name='viewport'" in html or 'name=viewport' in html
        x['social_only']=any(s in r.geturl() for s in ['facebook.com','instagram.com','booking.com','tripadvisor'])
    except Exception as e:
        x['site_status']='dead'
    return x
with cf.ThreadPoolExecutor(48) as ex: d=list(ex.map(chk,d))
json.dump(d,open(sys.argv[2],'w'),ensure_ascii=False)
import collections
print(len(d), collections.Counter(x.get('site_status','none') for x in d))
