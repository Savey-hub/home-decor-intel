# -*- coding: utf-8 -*-
import urllib.request, ssl, json
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0'
def get(u):
    r=urllib.request.Request(u,headers={'User-Agent':UA,'Referer':'https://data.eastmoney.com/'})
    return json.loads(urllib.request.urlopen(r,timeout=40,context=ctx).read().decode('utf-8','replace'))

WATCH = {
 '603833':'欧派家居','002572':'索菲亚','603801':'志邦家居','603816':'顾家家居','001323':'慕思股份',
 '000785':'居然智家','601828':'红星美凯龙','001322':'箭牌家居','603385':'惠达卫浴','003012':'东鹏控股',
 '603195':'公牛集团','603515':'欧普照明','603737':'三棵树','002372':'伟星新材','301339':'悍高集团',
 '601886':'江河集团','603008':'喜临门','002853':'皮阿诺','603180':'金牌厨柜','603898':'好莱客',
 '300616':'尚品宅配','002918':'蒙娜丽莎','002798':'帝欧家居','002043':'兔宝宝','000910':'大亚圣象',
 '603313':'梦百合','002084':'海鸥住工','603992':'松霖科技','002790':'瑞尔特','603408':'建霖家居',
 '603610':'麒盛科技','301061':'匠心家居','603600':'永艺股份','603661':'恒林股份','603818':'曲美家居',
 '002631':'德尔未来','000786':'北新建材','300599':'雄塑科技','603221':'爱丽家居','301227':'森鹰窗业',
 '603378':'亚士创能','603389':'亚振家居','002271':'东方雨虹','300715':'凯伦股份','605268':'王力安防',
 '002035':'华帝股份','002242':'九阳股份','603579':'荣泰健康','002078':'太阳纸业','600885':'宏发股份',
 '002032':'苏泊尔','000921':'海信家电','000333':'美的集团','000651':'格力电器','603355':'莱克电气',
 '301075':'多瑞医药','002444':'巨星科技','603338':'浙江鼎力','002791':'坚朗五金','002734':'利民股份',
 '300824':'北鼎股份','605365':'立达信','002518':'科士达','300911':'亿田智能','301061x':'x',
 '002403':'爱仕达','603657':'春光科技','301300':'远翔新材','002741':'光华科技','603801x':'x',
 '000509':'华塑控股','002163':'海南发展','600876':'凯盛新材','000672':'上峰水泥','600585':'海螺水泥',
 '002233':'塔牌集团','600801':'华新水泥','000401':'冀东水泥','600720':'祁连山','000877':'天山股份',
 '002062':'宏润建设','002307':'北新路桥','601668':'中国建筑','601390':'中国中铁','601186':'中国铁建',
 '300117':'嘉寓股份','002718':'友邦吿','002822':'中装建设','002941':'新疆交建','603030':'全筑股份',
 '002323':'雅博股份','300506':'名家汇','002879':'长缆科技','603332':'苏州龙杰','605138':'德邦科技',
 '002612':'朗姿股份','603983':'丸美生物','001322x':'x','300749':'顶固集创','002803':'吉宏股份',
 '605009':'豪悦护理','301117':'佳缘科技','002853x':'x','300749x':'x','002110':'三钢闽光',
}
WATCH={k:v for k,v in WATCH.items() if not k.endswith('x')}
rows={}
for page in (1,2,3):
    u=("https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_LICO_FN_CPD&columns=ALL"
       "&pageSize=500&pageNumber=%d&sortColumns=UPDATE_DATE&sortTypes=-1"
       "&filter=(REPORTDATE%%3D'2026-06-30')") % page
    j=get(u); res=j.get('result')
    if not res or not res.get('data'): break
    for d in res['data']:
        if d.get('SECURITY_CODE') in WATCH: rows[d['SECURITY_CODE']]=d
    if page>=res.get('pages',1): break
print('watch size',len(WATCH),'matched',len(rows))
out=[]
for c,d in sorted(rows.items(), key=lambda kv:str(kv[1].get('NOTICE_DATE') or ''),reverse=True):
    out.append({'code':c,'name':d.get('SECURITY_NAME_ABBR'),'notice':(d.get('NOTICE_DATE') or '')[:10],
      'rev':d.get('TOTAL_OPERATE_INCOME'),'rev_yoy':d.get('YSTZ'),'np':d.get('PARENT_NETPROFIT'),
      'np_yoy':d.get('SJLTZ'),'eps':d.get('BASIC_EPS'),'gross':d.get('XSMLL'),'roe':d.get('WEIGHTAVG_ROE'),
      'div':d.get('ASSIGNDSCRPT'),'board':d.get('BOARD_NAME'),'type':d.get('DATATYPE')})
json.dump(out,open('_work/em_h1.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for o in out:
    print('%s %s %-8s rev=%.2f亿 (%+.2f%%) np=%.2f亿 (%+.2f%%) gross=%s%%'%(
      o['notice'],o['code'],o['name'],(o['rev'] or 0)/1e8,(o['rev_yoy'] or 0),(o['np'] or 0)/1e8,(o['np_yoy'] or 0),
      round(o['gross'],2) if o['gross'] else '-'))
