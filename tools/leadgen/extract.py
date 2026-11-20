import osmium, json, sys
CATS={'amenity':{'cafe','restaurant','bar','fast_food','pub','dentist','clinic','beauty'},
      'tourism':{'hotel','guest_house','hostel','apartment','motel'},
      'shop':{'beauty','hairdresser','bakery','clothes','florist','cosmetics'},'leisure':{'fitness_centre'}}
out=[]
def g(t,*ks):
    for k in ks:
        if k in t: return t[k]
    return ''
class H(osmium.SimpleHandler):
    def handle(self,o,lat,lon):
        t={k.k:k.v for k in o.tags}
        cat=None
        for k,vs in CATS.items():
            if t.get(k) in vs: cat=f"{k}={t[k]}";break
        if not cat or not ('name' in t or 'name:en' in t): return
        out.append(dict(id=f"{o.__class__.__name__[0].lower()}{o.id}",cat=cat,
          name=t.get('name',''),name_en=t.get('name:en',''),
          city=g(t,'addr:city','addr:city:en'),street=g(t,'addr:street'),
          phone=g(t,'phone','contact:phone','contact:mobile','mobile'),
          email=g(t,'email','contact:email'),website=g(t,'website','contact:website','url'),
          instagram=g(t,'contact:instagram','instagram'),facebook=g(t,'contact:facebook','facebook'),
          whatsapp=g(t,'contact:whatsapp','whatsapp'),lat=lat,lon=lon))
    def node(self,n):
        if n.location.valid(): self.handle(n,n.location.lat,n.location.lon)
    def area(self,a):
        try:
            r=next(iter(a.outer_rings())); n=next(iter(r)); self.handle(a,n.lat,n.lon)
        except Exception: self.handle(a,None,None)
h=H(); h.apply_file(sys.argv[1],locations=True)
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False)
print(len(out))
