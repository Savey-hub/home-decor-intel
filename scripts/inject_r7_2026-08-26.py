"""r7 (2026-08-26) refresh injector.

Root cause of user's '还是6月' complaint: the structured KPI arrays
(macro.retailSales / macro.wholesale / realEstate.investment) still held
June figures, and the template filter + retail chart were hard-pinned to
June. r5 injected the July NARRATIVE into highlights/supplyChain but never
touched these arrays, so the 大盘数据 cards kept showing 6月.

This script (idempotent, dedup by key) adds the July / 1-7月 official NBS
figures to those arrays plus a batch of 8月下旬 sourced news highlights and
merchant items. Template filter + chart are patched separately in
index.template.html. Every record carries source + publishDate + url.
No intranet (魔镜/Rune/FBI/纷析) values touched.
"""
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, '_work')

MR = os.path.join(ROOT, 'data', 'macro_realestate.json')
IP = os.path.join(ROOT, 'data', 'industry_policy.json')
MH = os.path.join(ROOT, 'data', 'v2', 'monthly_highlights.json')

NBS_MAIN = 'https://www.stats.gov.cn/sj/zxfb/202608/t20260817_1965052.html'
NBS_RE = 'https://www.stats.gov.cn/sj/zxfb/202608/t20260817_1965053.html'
NBS_IND = 'https://www.stats.gov.cn/sj/zxfb/202608/t20260817_1965055.html'
SRC_NBS = '国家统计局(2026-08-17)'
PD = '2026-08-17'


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def save(p, o):
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(o, f, ensure_ascii=False, indent=2)


def norm(s):
    return ''.join(str(s).split()).lower()


def add_unique(lst, items, keys, label):
    existing = {tuple(norm(x.get(k, '')) for k in keys) for x in lst}
    added = 0
    for it in items:
        k = tuple(norm(it.get(kk, '')) for kk in keys)
        if k in existing:
            continue
        existing.add(k)
        lst.append(it)
        added += 1
    print('  %-30s +%d (total %d)' % (label, added, len(lst)))
    return added


def add_strs(lst, items, label):
    existing = {norm(x) for x in lst}
    added = 0
    for s in items:
        if norm(s) in existing:
            continue
        existing.add(norm(s))
        lst.append(s)
        added += 1
    print('  %-30s +%d (total %d)' % (label, added, len(lst)))
    return added


# ---------- July retailSales (metric MUST contain '7月单月' for template filter) ----------
RETAIL_JULY = [
    {"metric": "限额以上单位家具类零售额（7月单月）", "period": "2026年7月", "value": "145亿元",
     "yoy": "-8.8%", "source": SRC_NBS, "url": NBS_MAIN, "publishDate": PD,
     "note": "连续下滑,较6月-6.6%降幅扩大"},
    {"metric": "限额以上单位家具类零售额（1-7月累计）", "period": "2026年1-7月", "value": "1004亿元",
     "yoy": "-4.5%", "source": SRC_NBS, "url": NBS_MAIN, "publishDate": PD, "note": ""},
    {"metric": "限额以上单位建筑及装潢材料类零售额（7月单月）", "period": "2026年7月", "value": "94亿元",
     "yoy": "-14.2%", "source": SRC_NBS, "url": NBS_MAIN, "publishDate": PD,
     "note": "连续多月为家居三品类中最差"},
    {"metric": "限额以上单位建筑及装潢材料类零售额（1-7月累计）", "period": "2026年1-7月", "value": "690亿元",
     "yoy": "-9.5%", "source": SRC_NBS, "url": NBS_MAIN, "publishDate": PD, "note": ""},
    {"metric": "限额以上单位家用电器和音像器材类零售额（7月单月）", "period": "2026年7月", "value": "946亿元",
     "yoy": "-1.9%", "source": SRC_NBS, "url": NBS_MAIN, "publishDate": PD,
     "note": "国补托底,降幅显著好于家具/建材"},
    {"metric": "限额以上单位家用电器和音像器材类零售额（1-7月累计）", "period": "2026年1-7月", "value": "6372亿元",
     "yoy": "-6.6%", "source": SRC_NBS, "url": NBS_MAIN, "publishDate": PD, "note": ""},
    {"metric": "社会消费品零售总额（7月单月）", "period": "2026年7月", "value": "39022亿元",
     "yoy": "+0.6%", "source": SRC_NBS, "url": NBS_MAIN, "publishDate": PD,
     "note": "增速年内最低(6月+1.5%→7月+0.6%)"},
    {"metric": "社会消费品零售总额（1-7月累计）", "period": "2026年1-7月", "value": "287744亿元",
     "yoy": "+1.2%", "source": SRC_NBS, "url": NBS_MAIN, "publishDate": PD, "note": ""},
]

WHOLESALE_JULY = [
    {"metric": "规模以上工业增加值（7月单月）", "period": "2026年7月", "value": "—",
     "yoy": "+4.5%", "source": SRC_NBS, "url": NBS_IND, "publishDate": PD,
     "note": "1-7月累计+5.3%;工业产品销售率7月96.9%(-0.6pp)"},
]

INVEST_JULY = [
    {"metric": "全国房地产开发投资（1-7月）", "period": "2026年1-7月", "value": "43009亿元",
     "yoy": "-19.2%", "source": SRC_NBS, "url": NBS_RE, "publishDate": PD,
     "note": "降幅较1-6月(-18.0%)略扩;销售面积4.50亿㎡(-11.8%)、销售额4.27万亿(-13.1%,降幅收窄0.5pp)"},
]

# ---------- highlights (each item dict; date/title/impact/source/cat/detail/url) ----------
HL = {
    "macro": [
        {"date": "2026-08-18", "title": "50家家居上市公司半年报:仅21家盈利,超半数预亏/下滑——行业深度K型分化",
         "impact": "高", "source": "财经网(2026-08-18)", "cat": "行业景气",
         "detail": "财经网梳理50家家居建材A股半年报/业绩预告:仅21家盈利,近六成利润下滑或预亏,定制家居龙头利润普遍腰斩,而扫地机/智能清洁等新赛道逆势高增,行业进入'出海+AI+整装'驱动的K型深度洗牌期。",
         "url": "https://estate.caijing.com.cn/20260818/5177776.shtml"},
    ],
    "platform": [
        {"date": "2026-08-14", "title": "京东家电家居18周年庆:'送装一体'覆盖超千万家庭,套购/家装成增长引擎",
         "impact": "中", "source": "新浪财经(2026-08-14)", "cat": "平台大促",
         "detail": "京东家电18周年庆以服务体验为核心,'送装一体'服务累计覆盖超千万家庭,套购、家装、以旧换新联动国补形成组合拳,MALL/旗舰店等线下门店同步造势,从'买家电'向'好体验'品牌心智升级。",
         "url": "https://finance.sina.com.cn/roll/2026-08-14/doc-ininhaiu2732905.shtml"},
    ],
    "policy": [
        {"date": "2026-08-25", "title": "第三批国补625亿持续申领至9月底,叠加'开学季'家电换新——补贴延续但边际递减",
         "impact": "中", "source": "多方转商务部/地方政策(2026-08,部分页面标【广告】,待官方口径复核)", "cat": "以旧换新/消费补贴",
         "detail": "第三批625亿元家电以旧换新补贴持续申领(多地窗口延至9月底),叠加8月下旬开学季家电/3C换新需求,对家电品类形成短期托底。注:部分渠道报道带【广告】标识,补贴额度与截止时点以各省商务厅正式公告为准(已列入待核实)。",
         "url": "https://www.stats.gov.cn/sj/zxfb/202608/t20260817_1965052.html"},
    ],
    "merchant": [
        {"date": "2026-08-25", "title": "石头科技H1营收破百亿(100.84亿),净利增超45%、扣非增超60%——清洁电器龙头逆势量利齐升",
         "impact": "高", "source": "第一财经(2026-08-24)", "cat": "财报",
         "detail": "石头科技2026H1营收100.84亿元、同比大增,归母净利增超45%、扣非净利增超60%,以创新+全球化拓宽清洁电器增长路径,与传统家居家具的普遍利润腰斩形成鲜明反差,印证'新赛道逆势高增'的K型分化。",
         "url": "https://www.yicai.com/news/103332786.html"},
        {"date": "2026-08-25", "title": "追觅科技宣布聚焦清洁电器/大家电/厨电/AI四大主业——收缩多元化,回归核心",
         "impact": "中", "source": "亿欧(2026-08-25)", "cat": "战略",
         "detail": "追觅科技对外明确聚焦清洁电器、大家电、厨电与AI四大主业,收敛此前的多元化扩张,集中资源投向智能家居核心品类与出海,是清洁/智能硬件头部在竞争加剧下的战略再聚焦信号。",
         "url": "https://www.iyiou.com/news/202608251139057"},
    ],
}

# ---------- merchant records into industry_policy.merchant ----------
MERCHANT = [
    {"title": "石头科技2026H1营收破百亿:100.84亿元,归母净利增超45%、扣非增超60%",
     "date": "2026-08-24", "category": "业绩", "type": "财报", "brand": "石头科技",
     "summary": "第一财经8-24报道:石头科技2026上半年营收100.84亿元(半年首破百亿),归母净利同比增超45%、扣非净利增超60%,巩固全球扫地机/清洁电器龙头地位。逆势量利齐升,与定制家居龙头利润腰斩形成K型反差,主要靠产品创新与海外市场驱动。",
     "url": "https://www.yicai.com/news/103332786.html", "source": "第一财经(2026-08-24)"},
    {"title": "追觅科技聚焦清洁电器/大家电/厨电/AI四大主业,收缩多元化",
     "date": "2026-08-25", "category": "战略", "type": "战略调整", "brand": "追觅科技",
     "summary": "亿欧8-25报道:追觅科技明确将资源聚焦清洁电器、大家电、厨电、AI四大主业,收敛前期多元化扩张。反映智能硬件头部在竞争与利润压力下向核心品类与出海再聚焦。",
     "url": "https://www.iyiou.com/news/202608251139057", "source": "亿欧(2026-08-25)"},
]

GAPS = [
    "美的集团/老板电器/TCL智家/萤石网络 2026H1半年报要点(营收净利同比、海外占比)已见公开报道但URL未逐一核实,列入待核实,下轮补齐一手来源。",
    "抖店罗盘家居家装类目近7天概览沿用2026-08-06~08-12数据(scrapedAt 2026-08-13):本轮采集窗口用户本机前台为机密会议材料,为不触碰用户活动窗口未做夸克自动化重抓,待机器空闲重抓近7天。",
    "国家统计局7月消费者信心指数暂未在数据发布栏公开推送,confidence沿用最近可得值并标注,待官方发布补齐。",
]


def main():
    for p in (MR, IP, MH):
        bak = os.path.join(WORK, 'bak_%s_before_r7.json' % os.path.basename(p).replace('.json', ''))
        if not os.path.exists(bak):
            shutil.copyfile(p, bak)

    mr = load(MR)
    ip = load(IP)
    mh = load(MH)
    total = 0

    print('[macro_realestate.json]')
    total += add_unique(mr['macro']['retailSales'], RETAIL_JULY, ('metric', 'period'), 'macro.retailSales')
    total += add_unique(mr['macro']['wholesale'], WHOLESALE_JULY, ('metric', 'period'), 'macro.wholesale')
    total += add_unique(mr['realEstate']['investment'], INVEST_JULY, ('metric', 'period'), 'realEstate.investment')
    mr['asOf'] = '2026-08-26'

    print('[industry_policy.json]')
    total += add_unique(ip['merchant'], MERCHANT, ('brand', 'date', 'type'), 'merchant')
    total += add_strs(ip['gaps'], GAPS, 'gaps')

    print('[monthly_highlights.json]')
    for cat in ('macro', 'platform', 'policy', 'merchant'):
        items = HL.get(cat, [])
        for x in items:
            if not isinstance(x, dict):
                raise SystemExit('highlights.%s non-dict' % cat)
            for req in ('date', 'title', 'impact', 'source', 'cat', 'detail', 'url'):
                x.setdefault(req, '')
        total += add_unique(mh['highlights'][cat], items, ('title',), 'highlights.' + cat)

    # ---- schema guards ----
    for p in ip['policy']:
        if not isinstance(p.get('subIndustry'), list):
            raise SystemExit('policy.subIndustry must be list: %s' % p.get('title'))
    for g in ip['gaps']:
        if not isinstance(g, str):
            raise SystemExit('gaps must be strings')

    save(MR, mr)
    save(IP, ip)
    save(MH, mh)
    print('\nTOTAL new records injected: %d' % total)


if __name__ == '__main__':
    main()
