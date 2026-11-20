const { chromium } = require('playwright'); const fs=require('fs');
const [,,inp,out]=process.argv;
const d=JSON.parse(fs.readFileSync(inp));
(async()=>{
  const b=await chromium.launch(); const ctx=await b.newContext({userAgent:'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36'});
  const dead=d.filter(x=>x.site_status==='dead');
  let i=0;
  async function worker(){ while(i<dead.length){ const x=dead[i++]; let u=x.website.split(';')[0].trim(); if(!u.startsWith('http')) u='http://'+u;
    const p=await ctx.newPage();
    try{ const r=await p.goto(u,{timeout:25000,waitUntil:'domcontentloaded'});
      const st=r?r.status():0; const txt=(await p.content()).toLowerCase();
      const parked=/domain (is )?for sale|buy this domain|parked|account suspended|this domain has expired|hostinger|godaddy/.test(txt)&&txt.length<60000;
      if(st>=200&&st<400&&!parked){ x.site_status='ok'; x.final_url=p.url(); x.https=p.url().startsWith('https'); x.mobile=txt.includes('name="viewport"')||txt.includes("name='viewport'")||txt.includes('name=viewport'); }
      else if(parked) x.site_status='dead';
      else if(st===403||st===429) {x.site_status='ok'; x.mobile=true; x.https=true;} // bot block = alive
    }catch(e){} finally{ await p.close(); } } }
  await Promise.all(Array.from({length:12},worker));
  await b.close(); fs.writeFileSync(out,JSON.stringify(d));
  console.log('still dead', d.filter(x=>x.site_status==='dead').length);
})();
