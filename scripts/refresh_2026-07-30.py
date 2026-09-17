# -*- coding: utf-8 -*-
"""周度刷新脚本 2026-07-30 (第3期)。
滚动窗口 近30天(07-01~07-30)。遵循不编造原则：仅新增已核实URL条目，
滚出窗口(<07-01)的边缘条目移除或转入gaps，日期字段整体前移。
"""
import json, io, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p):
    with io.open(os.path.join(ROOT, p), encoding='utf-8') as f:
        return json.load(f)
def save(p, d, indent=2):
    with io.open(os.path.join(ROOT, p), 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=indent)
    print('WROTE', p)

NEW_ASOF = '2026-07-30'
WSTART = '2026-07-01'
WEND = '2026-07-30'

# ---------------- 1. MACRO ----------------
m = load('data/macro_realestate.json')
m['asOf'] = NEW_ASOF
m['coverage'] = ('近30天(2026-07-01~07-30) + 2026年7月15日发布口径的6月/1-6月数据。'
    '本期(07-27~07-30)国家统计局无新的月度数据发布，6月/上半年数据仍为最新官方口径且落在近30天窗口内，故予沿用；'
    '下一次月度数据(7月社零/工业增加值)预计2026-08-15前后发布。')
# 更新gaps首条以反映新窗口
m['gaps'][0] = ('本期(2026-07-27~07-30)国家统计局未发布新的月度宏观数据；'
    '克而瑞/中指院7月房价与百强销售数据通常于2026-08-01前后发布，本期窗口内暂无7月新增，仍以6月口径为准')
save('data/macro_realestate.json', m)

# ---------------- 2. PLATFORM ----------------
p = load('data/platform_dynamics.json')
p['asOf'] = NEW_ASOF
p['windowStart'] = WSTART
p['windowEnd'] = WEND
p['windowNote'] = ('本期为近30天滚动窗口(07-01~07-30)。618大促战报已滚出窗口(见首期2026-07-16归档看板)；'
    '当前处于618与818之间的传统淡季，天猫/淘宝818暑期家装节尚未正式开闸，各平台官方规则页(抖音电商学习中心/微信小店成长中心/淘宝大学)为JS单页应用，'
    'WebFetch无法机读发布日期，相关线索列入gaps待浏览器陪跑核实。本期(07-27~07-30)未检索到平台侧新增可核实的家装家居垂类战报/新政。')
# 移除滚出窗口(06-29)的天猫618收官榜边缘条目
p['platforms']['tmall_taobao'] = [x for x in p['platforms']['tmall_taobao']
    if not str(x.get('date','')).startswith('2026-06')]
# gaps补充说明
p['gaps'].insert(0, '本期(07-27~07-30)平台侧无新增可核实的家装家居垂类营销活动/榜单/新政；天猫618全周期家装/家居收官榜(06-29)已随窗口前移滚出，见首期(2026-07-16)归档看板')
save('data/platform_dynamics.json', p)

# ---------------- 3. POLICY (含 merchant 新增) ----------------
y = load('data/industry_policy.json')
y['asOf'] = NEW_ASOF
y['windowStart'] = WSTART
y['windowEnd'] = WEND

# 3a. 移除滚出窗口(<07-01)的 merchant / industry 边缘条目
def in_window(item, key='date'):
    d = str(item.get(key, ''))
    # 仅按 YYYY-MM 粗判：保留 2026-07 及之后；移除 2026-06 及更早的『事件型』边缘条目
    if d.startswith('2026-06'):
        return False
    return True
# industry: 移除 06-26 / 06-30 CBMF 边缘转载与 06-01 华为(均在06月，滚出)
y['industry'] = [x for x in y['industry'] if in_window(x)]
# merchant: 移除 06-28 欧派发布会 / 06-30 顾家财务负责人变更(06月，滚出)
y['merchant'] = [x for x in y['merchant'] if in_window(x)]

# 3b. 新增本期核实到的卫浴陶瓷/建材 H1 业绩预告(汇总源 tidenews 2026-07-20，个股预告多为07-15披露)
new_merchants = [
    {
        "brand": "科达制造(600499)",
        "date": "2026-07-20",
        "type": "半年报预告(大幅预增)",
        "summary": "预计2026H1归母净利润12.60亿-13.60亿元，同比增长69.11%-82.53%，为陶瓷建材产业链盈利标杆。主因海外建材业务与锂电材料业务贡献，叠加建材机械(陶机)出口景气。在陶瓷卫浴板块整体探底背景下逆势高增，凸显『陶机+海外+锂电』多元化对冲国内地产下行的结构性韧性。",
        "url": "https://tidenews.com.cn/tmh_news.html?id=6a5dc07af2c7840001941a2c",
        "source": "潮新闻(引自科达制造业绩预告)"
    },
    {
        "brand": "松霖科技(603992)",
        "date": "2026-07-20",
        "type": "半年报预告(预增)",
        "summary": "预计2026H1归母净利润1.40亿-1.85亿元，同比增长50.40%-98.74%。卫浴五金/花洒ODM出口龙头，受益海外补库与自有品牌拓展，为卫浴板块少数高增标的，与国内需求驱动的东鹏/箭牌/惠达形成鲜明分化——出口链与内销链景气度背离。",
        "url": "https://tidenews.com.cn/tmh_news.html?id=6a5dc07af2c7840001941a2c",
        "source": "潮新闻(引自松霖科技业绩预告)"
    },
    {
        "brand": "瑞尔特(002790)",
        "date": "2026-07-15",
        "type": "半年报预告(预亏/转亏)",
        "summary": "预计2026H1归母净利润亏损1100万-1600万元，由盈转亏(上年同期盈利5166.62万元)。主因家居卫浴行业需求偏弱、竞争激烈、产品单价下滑。智能盖板/水箱配件供应商转亏，进一步印证卫浴配件环节同步承压。",
        "url": "http://www.eeo.com.cn/2026/0723/970582.shtml",
        "source": "经济观察网(引自瑞尔特业绩预告)"
    },
    {
        "brand": "海鸥住工(002084)",
        "date": "2026-07-20",
        "type": "半年报预告(预亏扩大)",
        "summary": "预计2026H1归母净利润亏损3700万-4700万元，亏损较上年同期进一步扩大。卫浴龙头配件/整装卫浴代工需求走弱，亏损扩大反映卫浴产业链中游代工环节压力大于品牌端。",
        "url": "https://tidenews.com.cn/tmh_news.html?id=6a5dc07af2c7840001941a2c",
        "source": "潮新闻(引自海鸥住工业绩预告)"
    },
    {
        "brand": "帝欧家居(002798)",
        "date": "2026-07-20",
        "type": "半年报预告(减亏)",
        "summary": "预计2026H1归母净利润亏损2300万-3500万元，同比大幅减亏。瓷砖(欧神诺)+卫浴双主业，通过收缩工程大宗、压降费用、聚焦零售与经销实现减亏，与蒙娜丽莎扭亏、东鹏净增门店同属『收缩工程/做强零售』自救路径的验证。",
        "url": "https://tidenews.com.cn/tmh_news.html?id=6a5dc07af2c7840001941a2c",
        "source": "潮新闻(引自帝欧家居业绩预告)"
    }
]
# 去重(按 brand+date)后追加
exist = {(x.get('brand'), x.get('date')) for x in y['merchant']}
for nm in new_merchants:
    if (nm['brand'], nm['date']) not in exist:
        y['merchant'].append(nm)

# 3c. gaps 更新：新增窗口滚动说明 + 深圳国补(05-22, 窗口外)不计入
if isinstance(y['gaps'], list):
    y['gaps'].insert(0, '本期(07-27~07-30)未检索到住建部/工信部/市场监管总局新发的家居家装政策或国标；地方国补方面深圳(2026-05-22 智能马桶/智能床)已在近30天窗口外，不计入本期；北京(07-23)/福建(07-22)扩围仍在窗口内并保留')
    y['gaps'].append('本期新增卫浴陶瓷/建材H1业绩预告(科达制造+69~82%/松霖科技+50~98%/瑞尔特转亏/海鸥住工亏损扩大/帝欧家居减亏)源自潮新闻2026-07-20行业汇总及经济观察网，个股预告多为07-15前后披露，精确PDF数值以巨潮cninfo原文为准复核')

save('data/industry_policy.json', y)
print('MERCHANT count now', len(y['merchant']))
print('INDUSTRY count now', len(y['industry']))
