# -*- coding: utf-8 -*-
import json, io, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p):
    with io.open(os.path.join(ROOT, p), encoding='utf-8') as f:
        return json.load(f)
def save(p, d, indent=1):
    with io.open(os.path.join(ROOT, p), 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=indent)
    print('WROTE', p)

# ---------------- monthly_highlights ----------------
h = load('data/v2/monthly_highlights.json')
h['asOf'] = '2026-07-30'
h['monthLabel'] = '2026年7月（自然月：2026-07-01 至 2026-07-30）'
h['intro'] = ('本区块聚焦当前自然月（7月）内发生的高优先级信号，独立于近30天滚动窗口，供管理层快速把握本月最新动向。'
    '共 4 个维度：宏观数据、平台大事、政策标准、头部商家。')

# 新增商家要闻：卫浴陶瓷板块分化(出口高增 vs 内销转亏)
h['highlights']['merchant'].append({
    "date": "2026-07-20",
    "title": "卫浴陶瓷板块H1分化加剧：科达制造+69~82%、松霖科技+50~98%逆势领跑，瑞尔特/海鸥住工转亏扩大",
    "detail": ("潮新闻2026-07-20行业汇总披露：陶瓷建材/卫浴板块H1呈『出口链高增、内销链探底』分化——科达制造(陶机+海外+锂电)净利12.6-13.6亿(+69~82%)、"
        "松霖科技(卫浴ODM出口)1.4-1.85亿(+50~98%)领跑；而内需驱动的瑞尔特由盈转亏(预亏1100-1600万)、海鸥住工亏损扩大至3700-4700万、"
        "帝欧家居减亏(亏2300-3500万)。分化核心在于是否绑定海外补库/出口景气，天猫家装需关注具备出口对冲能力的卫浴品牌竞争位次变化。"),
    "impact": "中",
    "url": "https://tidenews.com.cn/tmh_news.html?id=6a5dc07af2c7840001941a2c",
    "source": "潮新闻(引自各公司业绩预告)",
    "cat": "卫浴陶瓷"
})

# monthlySummary 末尾补一句本期滚动更新
h['monthlySummary'] = h['monthlySummary'].rstrip() + (
    ' 【07-30周度更新】卫浴陶瓷板块进一步验证『出口链高增(科达制造+69~82%、松霖科技+50~98%)vs 内销链探底(瑞尔特转亏、海鸥住工亏损扩大)』的深度分化，'
    '是否具备出口/多元化对冲成为本轮周期头部与腰部拉开身位的关键变量。')
save('data/v2/monthly_highlights.json', h)
print('merchant highlights now', len(h['highlights']['merchant']))

# ---------------- data_sources_index ----------------
s = load('data/v2/data_sources_index.json')
s['asOf'] = '2026-07-30 12:00'
# 新增本期数据源
s['sources'].append({
    "name": "潮新闻/经济观察网(陶瓷卫浴板块H1业绩汇总·多公司交叉)",
    "layer": "A",
    "url": "https://tidenews.com.cn/tmh_news.html?id=6a5dc07af2c7840001941a2c",
    "login": "免登录",
    "depth": 2,
    "count": "5家新增(科达制造/松霖科技/瑞尔特/海鸥住工/帝欧家居)H1业绩预告数值",
    "timestamp": "2026-07-30",
    "blocker": "汇总媒体口径，个股精确数值以巨潮cninfo原始PDF为准复核，已在gaps标注"
})
# 更新 summary
summ = s['summary']
summ['totalSources'] = len(s['sources'])
summ['depth2'] = summ.get('depth2', 9) + 1
summ['newThisRound'] = ('本轮(2026-07-27~07-30)周度刷新：滚动窗口前移至近30天(07-01~07-30)，滚出06月边缘条目(天猫618收官榜/欧派618发布会/顾家财务负责人变更/CBMF 6月转载)；'
    '新增核实卫浴陶瓷板块H1业绩预告5家(科达制造+69~82%/松霖科技+50~98%/瑞尔特转亏/海鸥住工亏损扩大/帝欧家居减亏，源自潮新闻2026-07-20汇总+经济观察网)。'
    '宏观(NBS 6月/H1)沿用(下期约08-15发布)；抖店罗盘登录态非交互环境不可验证，沿用上期07/09-07/15快照并经小Q提醒扫码。')
summ['blockedNote'] = ('本窗口(07-27~07-30)国家统计局无新月度数据、7月BHI/MPI未到发布期，沿用6月最新口径并标注；深圳国补(05-22)已滚出窗口不计入；'
    '508国标逐项标准号、慕思/金牌及本轮新增5家PDF数值待二次核验(已入gaps)；抖店罗盘、内网源、4个强登录源(蝉妈妈/千瓜尊享/京麦/京准通)仍待用户扫码陪跑，按阻塞透明规则标注。')
save('data/v2/data_sources_index.json', s)
print('sources now', summ['totalSources'])
