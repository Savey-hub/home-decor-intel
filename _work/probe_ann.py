# -*- coding: utf-8 -*-
import urllib.request, ssl, json, time
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0'
def get(u):
    r=urllib.request.Request(u,headers={'User-Agent':UA,'Referer':'https://data.eastmoney.com/'})
    return json.loads(urllib.request.urlopen(r,timeout=40,context=ctx).read().decode('utf-8','replace'))

WATCH={'603833':'欧派家居','002572':'索菲亚','603801':'志邦家居','603816':'顾家家居','001323':'慕思股份',
 '000785':'居然智家','601828':'红星美凯龙','001322':'箭牌家居','603385':'惠达卫浴','003012':'东鹏控股',
 '603195':'公牛集团','603515':'欧普照明','603737':'三棵树','002372':'伟星新材','301339':'悍高集团',
 '601886':'江河集团','603008':'喜临门','002853':'皮阿诺','603180':'金牌厨柜','603898':'好莱客',
 '300616':'尚品宅配','002918':'蒙娜丽莎','002798':'帝欧家居','002043':'兔宝宝','000910':'大亚圣象',
 '603313':'梦百合','002084':'海鸥住工','603992':'松霖科技','002790':'瑞尔特','603408':'建霖家居',
 '603610':'麒盛科技','301061':'匠心家居','603600':'永艺股份','603661':'恒林股份','603818':'曲美家居',
 '002631':'德尔未来','000786':'北新建材','300599':'雄塑科技','603221':'爱丽家居','301227':'森鹰窗业',
 '603378':'亚士创能','603389':'亚振家居','002271':'东方雨虹','002734':'利民股份','300749':'顶固集创',
 '002791':'坚朗五金','605268':'王力安防','002035':'华帝股份','300911':'亿田智能','603983':'丸美生物'}

found=[]
for code,name in WATCH.items():
    mk = 'SZ' if code[0] in '0123' else 'SH'
    u=('https://np-anotice-stock.eastmoney.com/api/security/ann?cb=&sr=-1&page_size=25&page_index=1'
       '&ann_type=A&client_source=web&stock_list=%s&f_node=0&s_node=0'%code)
    try:
        j=get(u)
    except Exception as e:
        print('ERR',code,name,e); continue
    lst=(j.get('data') or {}).get('list') or []
    for it in lst:
        nd=(it.get('notice_date') or '')[:10]
        if nd >= '2026-08-11':
            found.append({'code':code,'name':name,'date':nd,'title':it.get('title'),
                          'art_code':it.get('art_code'),
                          'url':'https://data.eastmoney.com/notices/detail/%s/%s.html'%(code,it.get('art_code'))})
    time.sleep(0.12)
found.sort(key=lambda x:(x['date'],x['code']),reverse=True)
json.dump(found,open('_work/ann_recent.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('total announcements >=2026-08-11:',len(found))
for f in found: print(f['date'],f['code'],f['name'],'|',f['title'][:78])
