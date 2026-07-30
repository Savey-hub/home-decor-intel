# -*- coding: utf-8 -*-
"""第4期补充·07-16~07-29窗口缺口深挖整合 (2026-07-30)
针对用户反馈"7.16-7.29宏观/行业动态/平台动态更新不足"，补入本轮联网深挖并逐条WebFetch核实的窗口内增量。
所有条目均带 source+date+url；窗口结构性偏薄的原因写入各文件 gaps。
"""
import json, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p):
    return json.load(io.open(os.path.join(ROOT, p), encoding='utf-8'))
def save(p, d):
    json.dump(d, io.open(os.path.join(ROOT, p), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------------- platform_dynamics.json ----------------
pd = load('data/platform_dynamics.json')
jd_new = {
    "title": "京东『春晓计划』2026上半年成绩单：家电家居近2.5万商家销售额同比增超50%、超5800家增超200%",
    "date": "2026-07-22",
    "category": "通用",
    "type": "战报/商家扶持",
    "summary": "京东春晓计划加码投入350亿专项扶持资源，2026上半年超22万产业带商家销售额同比翻倍；家电家居领域近2.5万商家销售额同比增超50%、超5800家增超200%（未披露GMV绝对值，家装建材仅见于『家具建材新商榜』品牌名单）。",
    "url": "https://finance.sina.cn/stock/jdts/2026-07-22/detail-iniirwqk8049446.d.html",
    "source": "新浪财经（转环球网）"
}
if not any(x.get('date') == '2026-07-22' and '春晓' in x.get('title', '') for x in pd['platforms']['jd']):
    pd['platforms']['jd'].append(jd_new)

# 更新仍受限平台的待核实说明（第2轮补采仍受JS/登录门槛限制）
gate_note = {
    'pdd': "第2轮07-16~07-29窗口补采仍受限：拼多多家居家装官方战报/招商页JS动态渲染，公开面未检索到窗口内可溯源动态，待强登录商家后台陪跑补采",
    'xhs': "第2轮补采仍受限：小红书家生活垂类蒲公英/千帆商业化新政为登录态页面，公开面无窗口内可溯源官方动态，待强登录后台补采",
    'shipinhao': "第2轮补采仍受限：视频号/微信小店家居家装成长中心为登录态，公开面无窗口内可溯源专项战报/新政",
    'kuaishou': "第2轮补采仍受限：快手磁力金牛家居家装招商页需登录，公开面无窗口内可溯源专项战报",
    'tmall_taobao': "第2轮补采仍受限：天猫/淘宝大学818暑期家装节2026规则页JS动态渲染，公开面无法核验窗口内正文与日期，待商家后台陪跑补采",
}
for k, msg in gate_note.items():
    lst = pd['platforms'].get(k, [])
    for x in lst:
        if str(x.get('date')) == '待核实' or '待核实' in str(x.get('title', '')):
            x['title'] = "待核实：" + msg
            x['summary'] = msg
            break

pd['asOf'] = '2026-07-30'
pd.setdefault('gaps', [])
gapmsg_pf = "【第2轮07-16~07-29窗口深挖说明】该窗口在电商平台公开面客观偏薄：各平台官方规则/招商页(抖店学习中心、淘宝大学、微信小店成长中心、磁力金牛)均为JS动态渲染或需登录态，WebFetch无法取正文；本轮仅京东『春晓计划』半年战报(07-22,新浪财经)达『实开+日期在窗口+可溯源』标准并入库。pdd/xhs/视频号/快手/天猫窗口内公开可溯源动态稀少，需强登录商家后台陪跑补采。"
if gapmsg_pf not in pd['gaps']:
    pd['gaps'].append(gapmsg_pf)
save('data/platform_dynamics.json', pd)

# ---------------- industry_policy.json ----------------
ip = load('data/industry_policy.json')
policy_new = [
    {
        "title": "福州市扩大2026年智能家居产品购新补贴品类：与省级同步扩围至约10类",
        "issueDate": "2026-07-22",
        "effectiveDate": "2026-07-22",
        "issuer": "福州市商务局",
        "scope": "福州市个人消费者，与福建省级公告同步（销售价15%、每件上限1500元、每人每类限1件，有效期至2026-12-31）",
        "category": "补贴/以旧换新",
        "subIndustry": ["家具", "卫浴洁具", "五金建材"],
        "summary": "福州市同步福建省级扩围，将智能吸油烟机/燃气灶(含集成灶)/洗碗机/干衣机等纳入智能家居购新补贴，并把『智能沙发』纳入智能按摩椅补贴范畴，品类扩大至约10类。软体家具/智能卫浴终端零售直接受益。",
        "impact": "地方补贴由省到市逐级落地，软体家具与智能卫浴C端零售获价格侧刺激。",
        "url": "https://swj.fuzhou.gov.cn/zwgk/tzgg_5914/202607/t20260722_5349440.htm",
        "source": "福州市商务局"
    },
    {
        "title": "重庆市对2026年智能家居（含适老化家居）购新补贴垫付超50万元单位预拨付资金",
        "issueDate": "2026-07-24",
        "effectiveDate": "2026-07-24",
        "issuer": "重庆市商务委（渝商务〔2026〕105/106号）/重庆市会展服务中心",
        "scope": "重庆市参与智能家居（含适老化家居）购新补贴的销售单位",
        "category": "补贴/以旧换新",
        "subIndustry": ["家具", "适老化家居", "卫浴洁具"],
        "summary": "重庆对垫付资金超50万元的参与单位进行预拨付以缓解垫资压力，数据截至7月24日以银联统计为依据。反映智能家居/适老化补贴资金已进入实际拨付、终端零售放量阶段。",
        "impact": "补贴资金侧实际落地的直接证据，佐证适老化家居/智能家居终端销售放量。",
        "url": "https://sww.cq.gov.cn/zwgk_247/zfxxgkml/qtfdxx/tzgg/202607/t20260724_15852635.html",
        "source": "重庆市商务委"
    },
]
for it in policy_new:
    if not any(x.get('issueDate') == it['issueDate'] and x.get('issuer') == it['issuer'] for x in ip['policy']):
        ip['policy'].append(it)

industry_new = {
    "title": "国家统计局：上半年社零24.87万亿(+1.3%)，以旧换新带动高能效家电增速超30%",
    "date": "2026-07-16",
    "topic": "宏观消费/以旧换新解读",
    "issuer": "国家统计局（新闻发言人解读）",
    "summary": "2026上半年社零总额约24.87万亿元、同比+1.3%（6月+1.0%）；以旧换新带动绿色智能商品销售快速增长，高能效家电增速超30%。但家具类(1-6月-3.7%)、建筑及装潢材料类(1-6月-8.8%)零售仍全线负增长，后周期需求偏弱。",
    "url": "https://www.stats.gov.cn/sj/zxfbhjd/202607/t20260716_1964146.html",
    "source": "国家统计局"
}
if not any(x.get('date') == '2026-07-16' and '以旧换新带动高能效家电' in x.get('title', '') for x in ip['industry']):
    ip['industry'].append(industry_new)

merchant_new = [
    {
        "brand": "爱丽家居(603221)",
        "date": "2026-07-23",
        "type": "重大资产收购意向",
        "summary": "PVC弹性地板龙头拟收购半导体存储测试设备企业欧康诺不低于77.08%股权，欧康诺100%股权整体估值不超6.5亿元；受让方承诺2026-2029四年扣非净利累计不低于2.3亿元。地板主业外跨界并购。",
        "url": "https://finance.sina.com.cn/wm/2026-07-28/doc-inikimee8197877.shtml",
        "source": "新浪财经（引述公司公告）"
    },
    {
        "brand": "爱丽家居(603221)",
        "date": "2026-07-27",
        "type": "股价异动/风险提示",
        "summary": "7月21-27日连续5涨停累计涨幅61.09%、走出6连板（7/28报16.94元、市值41.04亿）；公司提示收购协议未签、业绩承诺达成存不确定性、静态市盈率显著高于行业。地板板块个股因跨界并购炒作异动。",
        "url": "https://finance.sina.com.cn/wm/2026-07-28/doc-inikimee8197877.shtml",
        "source": "新浪财经（引述公司公告）"
    },
]
for it in merchant_new:
    if not any(x.get('brand') == it['brand'] and x.get('date') == it['date'] for x in ip['merchant']):
        ip['merchant'].append(it)

ip.setdefault('gaps', [])
gapmsg_ip = "【第2轮07-16~07-29窗口深挖说明】本轮补入窗口内可溯源增量：智能家居购新补贴地方扩围潮(福建/福州07-22、重庆适老化07-24)、统计局上半年社零及以旧换新解读(07-16)、爱丽家居跨界并购与异动(07-23/07-27)。需说明：A股2026半年报业绩预告强制披露截止在07-14/15，欧派/慕思/箭牌/索菲亚/志邦/金牌等家居建材业绩预告簇集中在07-14~07-15(已入库)，恰在本窗口前1-2天，故窗口内『业绩预告』新增有限。"
if gapmsg_ip not in ip['gaps']:
    ip['gaps'].append(gapmsg_ip)
save('data/industry_policy.json', ip)

# ---------------- macro_realestate.json ----------------
mr = load('data/macro_realestate.json')
# 1) 解析CBMI待核实 -> 已核实 6月101.3
for x in mr['macro'].get('supplyChain', []):
    if 'CBMI' in x.get('metric', '') or '建材工业景气' in x.get('metric', ''):
        x['value'] = "101.3点"
        x['yoy'] = "环比+0.5点（高于临界点、处景气区间；价格指数98.9仍在非景气区间；上半年建材总需求同比约-10%）"
        x['source'] = "中国建筑材料联合会"
        x['url'] = "http://wap.sasac.gov.cn/n16582853/n16582898/c35523332/content.html"
        x['publishDate'] = "2026-07-03"
        x['note'] = "已核实：6月CBMI 101.3点、景气区间但价格分项仍偏弱，印证建材需求承压。"
        break
# 2) 追加 7月上旬建材周度价格
sc_new = {
    "metric": "流通领域重要生产资料·建材价格（水泥/浮法玻璃/螺纹钢）",
    "period": "2026年7月上旬",
    "value": "普通硅酸盐水泥256.0元/吨、浮法平板玻璃1108.2元/吨、螺纹钢3145.9元/吨",
    "yoy": "环比 水泥-1.2%、玻璃-0.5%、螺纹钢-0.8%",
    "source": "国家统计局",
    "url": "https://www.stats.gov.cn/sj/zxfb/202607/t20260713_1964100.html",
    "publishDate": "2026-07-13",
    "note": "窗口内最新高频建材价格信号：7月主要建材品种价格延续下行，反映地产后周期需求偏弱。"
}
if not any(x.get('period') == '2026年7月上旬' and '建材价格' in x.get('metric', '') for x in mr['macro']['supplyChain']):
    mr['macro']['supplyChain'].append(sc_new)

mr['asOf'] = '2026-07-30'
mr.setdefault('gaps', [])
gapmsg_mr = "【第2轮07-16~07-29窗口深挖说明】宏观/地产官方月度数据统一在07-15发布(6月及上半年社零、房地产投资/销售/新开工、70城房价均已入库)，恰在本窗口前1天；本轮窗口内新增高频建材价格(7月上旬水泥/玻璃/螺纹钢,07-13发布)并核实6月CBMI(101.3)。仍待窗口：7月社零/地产/工业增加值官方月度数据预计08-15前后发布；2026年7月百强房企销售榜(克而瑞/中指全口径)预计08-01发布——届时需二次补采。"
if gapmsg_mr not in mr['gaps']:
    mr['gaps'].append(gapmsg_mr)
save('data/macro_realestate.json', mr)

# ---------------- monthly_highlights.json (dashboard 亮点) ----------------
# 注意：highlights.* 每项必须是 dict(date/title/impact/source/cat/detail/url)，gen_word.py 与 dashboard 均依赖此结构，切勿追加纯字符串。
mh = load('data/v2/monthly_highlights.json')
hl = mh.setdefault('highlights', {}).setdefault('policy', [])
new_policy_hl = {
    "date": "2026-07-24",
    "title": "智能家居购新补贴地方扩围潮：福建/福州(07-22)纳入智能沙发、重庆(07-24)补贴资金预拨付",
    "impact": "高", "cat": "补贴",
    "detail": "福建/福州07-22将智能吸油烟机/燃气灶/洗碗机/干衣机等纳入、把智能沙发纳入智能按摩椅补贴，按售价15%每件上限1500元；重庆07-24对垫资超50万元单位预拨付，补贴资金实际放量，软体家具/智能卫浴/适老化家居终端受益。",
    "url": "https://sww.cq.gov.cn/zwgk_247/zfxxgkml/qtfdxx/tzgg/202607/t20260724_15852635.html",
    "source": "福建省/福州市/重庆市商务部门"
}
if not any(isinstance(x, dict) and x.get('title') == new_policy_hl['title'] for x in hl):
    hl.append(new_policy_hl)
plat_hl = mh['highlights'].setdefault('platform', [])
new_plat_hl = {
    "date": "2026-07-22",
    "title": "京东『春晓计划』2026上半年半年战报：家电家居超5800家商家销售额同比增超200%",
    "impact": "中", "cat": "平台",
    "detail": "京东春晓计划加码350亿专项扶持，2026上半年超22万产业带商家销售额同比翻倍；家电家居领域近2.5万商家销售额同比增超50%、超5800家增超200%（未披露GMV绝对值，家装建材仅见于家具建材新商榜）。",
    "url": "https://finance.sina.cn/stock/jdts/2026-07-22/detail-iniirwqk8049446.d.html",
    "source": "新浪财经（转环球网）"
}
if not any(isinstance(x, dict) and x.get('title') == new_plat_hl['title'] for x in plat_hl):
    plat_hl.append(new_plat_hl)
save('data/v2/monthly_highlights.json', mh)

# ---------------- 汇总打印 ----------------
print('platform.jd count =', len(pd['platforms']['jd']))
print('policy count =', len(ip['policy']), '| industry =', len(ip['industry']), '| merchant =', len(ip['merchant']))
print('macro.supplyChain count =', len(mr['macro']['supplyChain']))
print('highlights policy =', len(hl), '| platform =', len(plat_hl))
print('DONE gapfill')
