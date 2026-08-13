# -*- coding: utf-8 -*-
import urllib.request, ssl, json, re, sys
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0'
def get(u):
    r=urllib.request.Request(u,headers={'User-Agent':UA,'Referer':'https://data.eastmoney.com/'})
    return urllib.request.urlopen(r,timeout=45,context=ctx).read().decode('utf-8','replace')
anns=json.load(open('_work/ann_recent.json',encoding='utf-8'))
targets=[a for a in anns if a['date']=='2026-08-13']
for a in targets:
    u='https://np-cnotice-stock.eastmoney.com/api/content/ann?art_code=%s&client_source=web&page_index=1'%a['art_code']
    try:
        j=json.loads(get(u)); d=j.get('data') or {}
        txt=re.sub(r'<[^>]+>','',d.get('notice_content') or '')
        txt=re.sub(r'\s+',' ',txt).strip()
        print('='*100); print(a['date'],a['code'],a['name'],'|',a['title'])
        print('URL:',a['url'])
        print('EM_ATTACH:',d.get('attach_url') or '-')
        print('TEXT[0:2600]:',txt[:2600])
    except Exception as e:
        print('ERR',a['code'],a['title'],type(e).__name__,e)
