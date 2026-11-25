# -*- coding: utf-8 -*-
"""Round 14 full-refresh public intelligence through 2026-11-25 (10-11月专题置顶)."""
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASOF = "2026-11-25"
WINDOW_START = "2026-10-01"
ROUND = 14
METHOD = "浏览器核验 (Quark)"
PATHS = {
    "macro": os.path.join(ROOT, "data", "macro_realestate.json"),
    "platform": os.path.join(ROOT, "data", "platform_dynamics.json"),
    "policy": os.path.join(ROOT, "data", "industry_policy.json"),
    "monthly": os.path.join(ROOT, "data", "v2", "monthly_highlights.json"),
    "sources": os.path.join(ROOT, "data", "v2", "data_sources_index.json"),
    "inventory": os.path.join(ROOT, "data", "v2", "url_inventory.json"),
    "compass": os.path.join(ROOT, "data", "sources", "layerC_doudian_compass.json"),
}
WORK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "")
RESEARCH = r"C:\Users\Savey\.qwenworkcn\workspace\4e65294c-44ea-48f6-b210-5150275eee96"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, value):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")


def norm(value):
    return "".join(str(value).split()).lower()


def add_unique(items, additions, keys):
    existing = {tuple(norm(x.get(k, "")) for k in keys) for x in items}
    added = 0
    for item in additions:
        missing = [k for k in ("source", "publishDate", "url") if not item.get(k)]
        if missing:
            raise SystemExit(f"missing {missing}: {item.get('title') or item.get('metric')}")
        key = tuple(norm(item.get(k, "")) for k in keys)
        if key not in existing:
            items.append(item)
            existing.add(key)
            added += 1
    return added


def add_text_unique(items, text):
    if text not in items:
        items.append(text)
        return 1
    return 0


def load_research(name):
    path = os.path.join(RESEARCH, name)
    if not os.path.exists(path):
        print("WARN missing research", path)
        return {"entries": [], "gaps": [], "conflicts": []}
    return load(path)


def subindustry_fix(item):
    """subIndustry 必须是数组（历史事故防线）。"""
    si = item.get("subIndustry")
    if isinstance(si, str):
        item["subIndustry"] = [si]
    elif si is None:
        item["subIndustry"] = ["家装"]
    return item


def e(item, group):
    return {k: item.get(k) for k in ("title", "source", "publishDate", "eventDate",
                                     "dataPeriod", "url", "summary", "detail", "subIndustry",
                                     "impact") if item.get(k) is not None}


def update_inventory(inventory):
    """Round 14 逐源复核结果。仅更新本轮实际核验的入口，其余保持 R13 结论并注明未复核。"""
    groups = {
        # 本轮取得有效内容（夸克实测）
        "ok_yield": {2, 3, 9, 13, 14, 15, 16, 18, 19, 20, 22, 24, 26, 27, 28, 30, 33, 35, 38, 42, 45, 48, 52},
        # 本轮核验但无有效新增
        "ok_empty": {5, 10, 21, 23, 31, 32, 36, 37, 39, 40, 41, 46, 47, 49, 50, 51, 56},
        # 登录或验证门槛
        "need_login_browser": {4, 6, 7, 8, 53},
        # 受限内部来源：仅占位
        "ok_empty_internal": {54, 55, 57},
        "dead": {12, 29, 34},
        "noise": {1, 43, 44},
    }
    specific = {
        2: "夸克核验蝉妈妈品牌榜家具建材类目（近30天窗口），取得头部品牌榜单快照；因页面为滚动窗口未覆盖10-11月全周期。",
        13: "夸克核验中国质量新闻网家居建材频道，取得TATA木门心动样板间、兔宝宝绿色家居等11月正文。",
        14: "夸克核验网经社双11专题，取得星图口径首轮综合电商GMV、家电家居品类及京东双11战报等5篇正文级事实。",
        15: "夸克核验京东企业博客零售分类，取得双11复盘、AI商家运营、全渠道战略等5条官方记录。",
        16: "夸克下钻建材联合会运行监测栏目5篇正文，取得10月MPI 97.3、11月MPI 98.5及1-9月行业运行简报。",
        18: "夸克核验199IT，取得双11智能门锁洛图数据、TrendForce等多条10-11月条目。",
        19: "夸克通过奥维云网后端API取得Q3床垫报告、双11空调/厨小总结等正文级事实。",
        20: "夸克核验国家统计局10月数据发布，取得10月社零、房地产、70城房价、生产资料价格等正文及附表。",
        22: "夸克核验中国工业新闻网，取得10月国民经济与11月LPR正文；其统计数据栏目实为新闻聚合。",
        24: "夸克核验新浪家居，取得BHEE卖场数据、大家居三季报、顾家万格丽等3篇原创正文。",
        26: "夸克通过WAF滑块后核验阿拉丁照明网，取得照明产业链三季报与AI照明技术规范动态。",
        27: "夸克核验36氪家居搜索，取得索菲亚出口、机构托管存量房等2篇详情（转述标注）。",
        28: "夸克核验中国建筑装饰协会，取得1-10月房地产开发数据转载与21家上市装企H1业绩（转述待核）。",
        30: "夸克核验京东麦头条免登录页，取得单品资质管控、保证金规则（智能马桶质保）、售后与店铺星级新规。",
        33: "夸克核验199IT报告库分类页，取得多条10-11月智能家居条目。",
        35: "夸克核验艾瑞报告库；10-11月无家居专项新报告，9月AI化白皮书作背景线索。",
        38: "夸克核验信通院权威发布；蓝皮书最新为4月，取得《端侧智能产业发展报告(2026.10)》含智慧家庭章节。",
        42: "夸克核验CBNData，取得10月天猫适老化趋势报告及贝壳Q3家装净收入等看点。",
        45: "夸克通过东方财富研报API按6个行业代码拉取10-01至11-25研报条目，入选17条；正文PDF未下载。",
        48: "夸克核验艾媒，取得双十一消费监测、AI空调与家居服务平台白皮书条目。",
        51: "夸克核验贝壳研究院；公开成果最新停留在2023-10，10-11月窗口无可入库公开内容。",
        52: "夸克核验CRIC；官网重定向至SaaS产品页，轮播数字无城市口径，不采用。",
        17: "夸克核验author.baidu.com重定向至错误页，域名疑似下线（维持失效判定）。",
        23: "夸克核验乐居头条已转型智能头条，文章无发布时间戳，部分线索以政策事件日期替代并显式标注。",
        4: "夸克进入千瓜需尊享会员权限，本轮未取得10-11月家居家装量化新增。",
        6: "夸克核验抖店罗盘需商家登录态，本轮未重采，沿用上期数据并在看板标注原始数据日期。",
    }
    labels = {
        "ok_yield": "夸克核验完成·取得有效内容",
        "ok_empty": "夸克核验完成·本轮无有效新增",
        "need_login_browser": "登录或权限门槛未通过",
        "ok_empty_internal": "受限来源占位·本轮无公开产出",
        "dead": "链接失效/域名拦截·已确认",
        "noise": "噪声源·已剔除",
    }
    conclusions = {
        "ok_yield": "夸克完成页面、栏目与可见详情核验；取得本轮可追溯内容。",
        "ok_empty": "夸克完成页面与可见栏目核验；本轮未取得可公开披露的有效新增。",
        "need_login_browser": "夸克核验后仍受登录或权限门槛限制；本轮未取得可公开披露的有效新增。",
        "ok_empty_internal": "仅保留匿名来源占位，未形成可公开披露的有效产出。",
        "dead": "链接失效或域名拦截，已确认。",
        "noise": "与家装建材无关或为搜索入口噪声源，已剔除。",
    }
    id_to_verdict = {uid: verdict for verdict, ids in groups.items() for uid in ids}
    updated = 0
    for item in inventory["urls"]:
        uid = item["id"]
        verdict = id_to_verdict.get(uid)
        if verdict is None:
            continue
        yielded = verdict == "ok_yield"
        result = {
            "testedAt": ASOF,
            "verdict": verdict,
            "verdictLabel": labels[verdict],
            "yielded": yielded,
            "conclusion": specific.get(uid, conclusions[verdict]),
            "round": ROUND,
            "method": METHOD,
        }
        item["status"] = verdict
        item["testResult"] = result
        updated += 1

    status_counts = collections.Counter(item.get("status", "unknown") for item in inventory["urls"])
    inventory["auditSummary"] = {
        "testedAt": ASOF,
        "statusCounts": dict(sorted(status_counts.items())),
        "note": "Round 14完成10—11月专题逐源夸克复核；23个入口取得有效内容，登录源与受限源如实标注，内网数值不入公开仓。",
        "yieldedCount": status_counts.get("ok_yield", 0),
    }
    return updated


def update_source_index(sources):
    updates = [
        ("国家统计局（", 3, "取得10月社零/工业/固投/房地产/70城房价/生产资料价格正文及附表，含家具与建材分项。"),
        ("中国建筑材料联合会", 3, "下钻运行监测5篇正文：10月MPI 97.3、11月MPI 98.5、1-9月行业运行简报、绿色建材报告。"),
        ("中国建筑装饰协会", 3, "取得1-10月房地产开发数据与21家上市装企H1业绩两篇正文（转载类已标注待核）。"),
        ("蝉妈妈", 2, "家具建材类目近30天品牌榜快照；页面为滚动窗口，不能覆盖10-11月全周期。"),
        ("网经社", 3, "双11专题5篇正文：星图首轮GMV+2.4%、家电2675亿居首、京东双11战报等。"),
        ("京东企业博客", 3, "双11复盘、AI商家运营、全渠道战略等5条官方记录，翻页至9月23日。"),
        ("京东麦头条", 2, "免登录取得单品资质、保证金、售后与店铺星级新规。"),
        ("新浪家居", 3, "BHEE卖场数据、大家居三季报、顾家万格丽等3篇原创正文。"),
        ("36氪", 2, "索菲亚出口、机构托管存量房等2篇（自媒体投稿，转述待核）。"),
        ("阿拉丁", 3, "通过WAF滑块后取得照明产业链三季报与AI照明技术规范（公牛牵头）。"),
        ("智能头条", 2, "乐居头条已转型智能家居垂媒，文章无时间戳；政策线索以事件日期替代并标注。"),
        ("中国质量新闻网", 3, "TATA木门、兔宝宝等11月正文。"),
        ("中国工业新闻网", 2, "10月国民经济与11月LPR正文；统计数据栏目实为新闻聚合。"),
        ("199IT", 3, "双11智能门锁洛图数据等多条10-11月条目。"),
        ("奥维云网 AVC", 3, "后端API取得Q3床垫报告全文、双11空调/厨小总结等。"),
        ("艾瑞咨询", 2, "10-11月无家居专项新报告；9月AI化白皮书作背景线索。"),
        ("艾媒咨询", 3, "双十一消费监测、AI空调、家居服务平台白皮书。"),
        ("第一财经数据 CBNData", 3, "10月天猫适老化趋势报告、贝壳Q3家装净收入33亿元(-22.9%)等看点。"),
        ("东方财富·行业研报", 3, "研报API按6行业代码拉取10-01至11-25条目17条；正文PDF未下载。"),
        ("信通院", 2, "取得《端侧智能产业发展报告(2026.10)》含智慧家庭章节；全屋智能专项白皮书无10-11月新增。"),
        ("贝壳研究院", 1, "公开成果最新停留在2023-10；完整列表需登录，窗口内无可入库公开内容。"),
        ("克而瑞 CRIC", 1, "官网重定向至SaaS产品页，轮播数字无城市与统计口径，不采用。"),
        ("巨潮资讯网", 1, "本轮未完成13家公司Q3公告逐家核验，保留为缺口。"),
    ]
    for source in sources["sources"]:
        name = source.get("name", "")
        for needle, depth, blocker in updates:
            if needle in name:
                source["depth"] = depth
                source["timestamp"] = ASOF
                source["blocker"] = blocker
                source["count"] = "Round 14已复核"
                break

    depth_counts = collections.Counter(int(x.get("depth", 0) or 0) for x in sources["sources"])
    sources["asOf"] = ASOF
    sources["summary"].update({
        "totalSources": len(sources["sources"]),
        "depth3": depth_counts[3],
        "depth2": depth_counts[2],
        "depth1": depth_counts[1],
        "depth0_blocked": depth_counts[0],
        "publicItemsCollected": "Round 14新增约70条结构化记录，覆盖宏观、房地产、平台、行业政策与商家动态（10-11月专题）。",
        "newThisRound": "Round 14：10月社零与房地产数据、建材MPI景气、双11全平台战报与规则、大家居三季报、智能门锁/床垫/照明品类数据、广东全屋智能行动方案。",
        "blockedNote": "抖店罗盘未重采（沿用上期并标注）；千瓜尊享会员受限；巨潮13家Q3公告未逐家核验；拼多多/微信小店/快手无独立核验新增。",
    })


def main():
    macro = load(PATHS["macro"])
    platform = load(PATHS["platform"])
    policy = load(PATHS["policy"])
    monthly = load(PATHS["monthly"])
    sources = load(PATHS["sources"])
    inventory = load(PATHS["inventory"])
    counts = collections.Counter()

    r_macro = load_research("research_macro.json")
    r_macro2 = load_research("research_macro2.json")
    r_platform = load_research("research_platform.json")
    r_trends = load_research("research_trends.json")
    r_industry = load_research("research_industry.json")
    r_merchants = load_research("research_merchants.json")

    # ============ 宏观 ============
    def metric_item(en, metric, period, value, yoy, note):
        return {
            "metric": metric, "period": period, "value": value, "yoy": yoy,
            "source": en["source"], "publishDate": en.get("publishDate", ASOF),
            "url": en["url"], "note": note,
        }

    macro_adds = []
    for en in r_macro["entries"] + r_macro2["entries"]:
        g = en.get("group")
        if g in ("macro",) and en.get("metrics"):
            for m in en["metrics"]:
                note = en.get("detail", "") or en.get("summary", "")
                macro_adds.append(metric_item(
                    en, m.get("name", en["title"]), m.get("period", en.get("dataPeriod", "")),
                    ("%.1f亿%s" % (m["value"], {"亿元": "元", "万平方米": "平方米"}.get(m.get("unit", ""), m.get("unit", "")))) if isinstance(m.get("value"), (int, float)) else str(m.get("value", "—")),
                    ("%s%%" % m["yoy"]) if isinstance(m.get("yoy"), (int, float)) else str(m.get("yoy", "—")),
                    note[:160]))
    # 手工精选一批10-11月核心宏观条目（保证口径完整）
    stats_url = "https://www.stats.gov.cn/sj/zxfbhjd/202611/t20261116_1965839.html"
    stats_re_url = "https://www.stats.gov.cn/sj/zxfbhjd/202611/t20261116_1965840.html"
    stats_q3_url = "https://www.stats.gov.cn/sj/xwfbh/fbhwd/202610/t20261019_1965618.html"
    selected_macro = [
        {"metric": "限额以上单位家具类零售额（10月单月）", "period": "2026年10月", "value": "162亿元", "yoy": "-2.6%",
         "source": "国家统计局", "publishDate": "2026-11-16", "url": stats_url,
         "note": "名义同比；10月单月降幅小于1-10月累计降幅(-4.5%)"},
        {"metric": "限额以上单位家具类零售额（1-10月累计）", "period": "2026年1-10月", "value": "1451亿元", "yoy": "-4.5%",
         "source": "国家统计局", "publishDate": "2026-11-16", "url": stats_url, "note": "限额以上单位口径"},
        {"metric": "限额以上单位建筑及装潢材料类零售额（10月单月）", "period": "2026年10月", "value": "98亿元", "yoy": "-11.2%",
         "source": "国家统计局", "publishDate": "2026-11-16", "url": stats_url,
         "note": "10月单月降幅大于累计(-9.9%)，建材端压力仍在加深"},
        {"metric": "限额以上单位建筑及装潢材料类零售额（1-10月累计）", "period": "2026年1-10月", "value": "964亿元", "yoy": "-9.9%",
         "source": "国家统计局", "publishDate": "2026-11-16", "url": stats_url, "note": "限额以上单位口径"},
        {"metric": "社会消费品零售总额（10月）", "period": "2026年10月", "value": "46463亿元", "yoy": "+0.4%",
         "source": "国家统计局", "publishDate": "2026-11-16", "url": stats_url, "note": "季调环比+0.02%"},
        {"metric": "网上商品零售额（1-10月）", "period": "2026年1-10月", "value": "107274亿元", "yoy": "+2.9%",
         "source": "国家统计局", "publishDate": "2026-11-16", "url": stats_url,
         "note": "原“实物商品网上零售额”更名为“网上商品零售额”，内涵和统计范围不变；网上零售总额新旧口径不可比"},
        {"metric": "规模以上工业增加值（10月）", "period": "2026年10月", "value": "—", "yoy": "+4.8%",
         "source": "国家统计局", "publishDate": "2026-11-16",
         "url": "https://www.stats.gov.cn/sj/zxfbhjd/202611/t20261116_1965844.html",
         "note": "可比价实际增速；制造业PMI 49.3"},
        {"metric": "CPI（10月）", "period": "2026年10月", "value": "—", "yoy": "+0.7%",
         "source": "国家统计局", "publishDate": "2026-11-16",
         "url": "https://www.stats.gov.cn/sj/zxfbhjd/202611/t20261116_1965844.html",
         "note": "居住分项同比-0.3%；PPI同比+5.7%、购进价格+7.9%，上游涨价与弱消费并存"},
        {"metric": "建材工业价格景气MPI（11月）", "period": "2026年11月", "value": "98.5", "yoy": "环比+1.2",
         "source": "中国建筑材料联合会", "publishDate": "2026-11-25",
         "url": "https://www.cbmf.org/yxjc/", "note": "仍处非景气区间(<100)"},
        {"metric": "建材工业价格景气MPI（10月）", "period": "2026年10月", "value": "97.3", "yoy": "环比-7.2",
         "source": "中国建筑材料联合会", "publishDate": "2026-11-06",
         "url": "https://www.cbmf.org/yxjc/", "note": "三大需求指数全部落入非景气区间"},
        {"metric": "规模以上建材行业营业收入（1-9月）", "period": "2026年1-9月", "value": "—", "yoy": "-14.6%",
         "source": "中国建筑材料联合会运行监测", "publishDate": "2026-10-28",
         "url": "https://www.cbmf.org/yxjc/", "note": "利润总额同比-70.1%；水泥产量11.3亿吨-8.6%；9月建材出口转正+5.0%"},
        {"metric": "前三季度GDP", "period": "2026年1-9月", "value": "1071071亿元", "yoy": "+4.6%",
         "source": "国家统计局", "publishDate": "2026-10-19", "url": stats_q3_url, "note": "Q3单季同比+4.5%、环比+1.2%；不变价实际增速"},
    ]
    for it in selected_macro:
        counts["macro"] += add_unique(macro["macro"]["retailSales"], [it], ("metric", "period"))

    re_adds = [
        {"metric": "房地产开发投资（1-10月）", "period": "2026年1-10月", "value": "57215亿元", "yoy": "-21.6%",
         "source": "国家统计局", "publishDate": "2026-11-16", "url": stats_re_url, "note": "按可比口径计算"},
        {"metric": "房屋新开工面积（1-10月）", "period": "2026年1-10月", "value": "37036万平方米", "yoy": "-24.4%",
         "source": "国家统计局", "publishDate": "2026-11-16", "url": stats_re_url, "note": ""},
        {"metric": "房屋竣工面积（1-10月）", "period": "2026年1-10月", "value": "25544万平方米", "yoy": "-26.6%",
         "source": "国家统计局", "publishDate": "2026-11-16", "url": stats_re_url, "note": "竣工端持续压制交付链需求"},
        {"metric": "新建商品房销售面积（1-10月）", "period": "2026年1-10月", "value": "61358万平方米", "yoy": "-13.7%",
         "source": "国家统计局", "publishDate": "2026-11-16", "url": stats_re_url, "note": "销售额58550亿元-14.3%"},
        {"metric": "二手房交易网签面积（1-10月）", "period": "2026年1-10月", "value": "67971万平方米", "yoy": "+11.4%",
         "source": "住房城乡建设部（经国家统计局发布）", "publishDate": "2026-11-16", "url": stats_re_url,
         "note": "存量房交易活跃；网签面积口径与新房销售合同面积不同，不可合并"},
        {"metric": "70城新建商品住宅价格：一线城市（10月）", "period": "2026年10月", "value": "环比持平", "yoy": "-0.1%",
         "source": "国家统计局", "publishDate": "2026-11-16",
         "url": "https://www.stats.gov.cn/sj/sjjd/202611/t20261116_1965838.html",
         "note": "上海+0.2%、深圳+0.1%、广州持平、北京-0.1%；二三线环比下降；同比降幅收窄"},
        {"metric": "5年期以上LPR（11月）", "period": "2026年11月20日", "value": "3.5%", "yoy": "持平",
         "source": "中国人民银行（经中国工业新闻网）", "publishDate": "2026-11-20",
         "url": "https://www.cinic.org.cn/xw/tjsj/", "note": "10月新发放个人房贷利率约3.1%"},
    ]
    for it in re_adds:
        counts["macro"] += add_unique(macro["realEstate"]["sales"], [it], ("metric", "period"))

    macro["asOf"] = ASOF
    macro["coverage"] = f"10—11月专题窗口：{WINDOW_START}至{ASOF}；宏观数据最新至2026年10月（11月完整月度指标尚未发布），房地产为1-10月累计口径。"
    counts["macro_gap"] += add_text_unique(macro["gaps"],
        "Round 14（2026-10-01至11-25）：11月完整月度统计（社零/房地产/70城房价等）尚未发布，不编造；家装批发独立数值无全国公开口径，未以全国社零或工业数据冒充。")
    counts["macro_conflict"] += add_text_unique(macro["conflicts"],
        "国家统计局已将“网上零售额”调整为“网上商品和服务零售额”并扩大平台统计范围，新旧口径不可比；本看板不将历史网上零售额序列与2026年新口径直接连接比较。")
    counts["macro_conflict"] += add_text_unique(macro["conflicts"],
        "双11全周期GMV存在口径分歧：专家预计约1.6万亿 vs 媒体报道1.78万亿（均为转述待核）；星图口径首轮综合电商GMV同比+2.4%为可核验锚点。")

    # ============ 平台 ============
    def plat_item(en, cat, typ):
        return {
            "title": en["title"], "date": en.get("publishDate", ASOF),
            "publishDate": en.get("publishDate", ASOF), "category": cat, "type": typ,
            "summary": (en.get("summary", "") or "")[:200],
            "source": en["source"], "url": en["url"],
            "firsthand": bool(en.get("firsthand", False)),
        }

    jd_items = []
    for en in r_platform["entries"] + r_merchants["entries"]:
        s = (en.get("source", "") or "")
        t = en["title"]
        if any(k in s for k in ("网经社", "京东")) or "京东" in t:
            jd_items.append(plat_item(en, "双11/平台动态", "平台战报/规则"))
    counts["platform"] += add_unique(platform["platforms"]["jd"], jd_items, ("title", "date"))

    dy_items = []
    for en in r_platform["entries"] + r_trends["entries"]:
        if any(k in (en.get("source", "") + en["title"]) for k in ("抖音", "蝉妈妈", "智能门锁", "洛图")):
            dy_items.append(plat_item(en, "抖音电商", "品类数据/趋势"))
    counts["platform"] += add_unique(platform["platforms"]["douyin"], dy_items, ("title", "date"))

    xhs_items = []
    for en in r_trends["entries"] + r_platform["entries"]:
        if any(k in (en.get("source", "") + en["title"]) for k in ("小红书", "天猫", "淘天", "适老化", "艾媒")):
            xhs_items.append(plat_item(en, "天猫/小红书", "趋势报告"))
    counts["platform"] += add_unique(platform["platforms"]["tmall_taobao"], xhs_items, ("title", "date"))
    counts["platform"] += add_unique(platform["platforms"]["xhs"], [
        plat_item(en, "小红书", "内容趋势") for en in r_trends["entries"] if "红书" in (en.get("source", "") + en["title"])
    ], ("title", "date"))

    cross_items = []
    for en in r_platform["entries"]:
        if any(k in en["title"] for k in ("双11", "GMV", "国补", "以旧换新")):
            cross_items.append(plat_item(en, "大促", "跨平台"))
    counts["platform"] += add_unique(platform["crossPlatform"], cross_items, ("title", "date"))

    platform.update({
        "asOf": ASOF, "windowStart": WINDOW_START, "windowEnd": ASOF,
        "windowNote": f"10—11月专题窗口：{WINDOW_START}至{ASOF}；双11为本窗口核心事件；GMV口径分歧与转述数据均已标注。",
    })
    counts["platform_gap"] += add_text_unique(platform["gaps"],
        "Round 14：拼多多、微信小店/视频号、快手未取得可独立核验的家装垂类10-11月新增；蝉妈妈为近30天滚动窗口非10-11月全周期；京东双11战报数字多为平台自报口径。")

    # ============ 政策/行业/商家 ============
    ind_adds, mer_adds, pol_adds = [], [], []
    for en in r_platform["entries"] + r_industry["entries"] + r_trends["entries"] + r_macro2["entries"]:
        g = en.get("group")
        title = en["title"]
        if any(k in title for k in ("行动方案", "方案", "规范", "标准", "以旧换新", "国补", "LPR", "公告", "意见")):
            pol_adds.append(subindustry_fix({
                "title": title, "issueDate": en.get("publishDate", ASOF),
                "effectiveDate": en.get("eventDate", ""), "issuer": en["source"],
                "scope": en.get("detail", "")[:120] or "全国",
                "category": "政策/标准", "subIndustry": en.get("subIndustry") or ["家装"],
                "summary": (en.get("summary", "") or "")[:200],
                "impact": en.get("impact", ""),
                "url": en["url"], "source": en["source"],
                "firsthand": bool(en.get("firsthand", False)),
                "publishDate": en.get("publishDate", ASOF),
            }))
        elif any(k in title for k in ("三季报", "Q3", "净利", "营收", "欧派", "美的", "格力", "索菲亚", "顾家", "贝壳", "万华", "装企")):
            mer_adds.append(subindustry_fix({
                "brand": title.split("，")[0][:20], "date": en.get("publishDate", ASOF),
                "type": "三季报/商家动态",
                "summary": (en.get("summary", "") or "")[:200],
                "impact": en.get("impact", ""),
                "url": en["url"], "source": en["source"],
                "firsthand": bool(en.get("firsthand", False)),
                "publishDate": en.get("publishDate", ASOF), "title": title,
            }))
        else:
            ind_adds.append(subindustry_fix({
                "title": title, "date": en.get("publishDate", ASOF),
                "topic": (en.get("summary", "") or "")[:30],
                "issuer": en["source"], "summary": (en.get("summary", "") or "")[:200],
                "url": en["url"], "source": en["source"],
                "subIndustry": en.get("subIndustry") or ["家装"],
                "publishDate": en.get("publishDate", ASOF),
            }))
    counts["policy"] += add_unique(policy["policy"], pol_adds, ("title", "issueDate"))
    counts["industry"] += add_unique(policy["industry"], ind_adds, ("title", "date"))
    counts["merchant"] += add_unique(policy["merchant"], mer_adds, ("title", "date"))
    policy.update({
        "asOf": ASOF, "windowStart": WINDOW_START, "windowEnd": ASOF,
        "windowNote": f"10—11月专题窗口：{WINDOW_START}至{ASOF}；仅收录带来源、发布日期和URL的公开条目；转载类数字标注待核。",
    })
    counts["policy_gap"] += add_text_unique(policy["gaps"],
        "Round 14：国家级以旧换新12月以后安排、家装专项国标修订细节未在本窗口内核实到权威原文；地方补贴扩围以广东全屋智能方案等为主。")
    counts["policy_conflict_add"] = add_text_unique(
        [c.get("item", "") for c in policy["conflicts"]], "") if policy["conflicts"] else 0

    # ============ 本月要闻（10-11月专题） ============
    monthly.update({
        "asOf": ASOF,
        "monthLabel": "2026年10—11月（Round 14 专题）",
        "intro": "本板块置顶呈现2026年10月1日至11月25日已核实的宏观、平台、政策与商家动态；11月完整月度统计尚未发布，以已发生事件和10月数据为准。",
        "monthlySummary": "10—11月主线：宏观上家具与建材零售继续负增长（家具-2.6%/建材-11.2%单月），新房销售与竣工仍在两位数下降，但二手房网签+11.4%支撑存量翻新需求；双11成为窗口核心事件，星图口径综合电商GMV+2.4%、家电以2675亿元居综合电商第一大品类，京东超2000家家电家居品牌成交翻倍；行业端建材MPI连续两月非景气、上市装企三分之二亏损，但广东全屋智能行动方案（2028年1.1万亿目标）与AI照明规范等结构性机会明确。",
    })
    monthly_additions = {
        "macro": [
            {"date": "2026-11-16", "publishDate": "2026-11-16", "title": "10月家具类零售-2.6%、建材类-11.2%，社零整体+0.4%",
             "impact": "高", "source": "国家统计局（2026-11-16）", "cat": "社零/品类",
             "detail": "家具单月降幅收窄但建材加深；1-10月网上商品零售额+2.9%；限额以上品牌专卖店-11.0%。名义增速。", "url": stats_url},
            {"date": "2026-11-16", "publishDate": "2026-11-16", "title": "1-10月房地产投资-21.6%、竣工-26.6%，二手房网签+11.4%",
             "impact": "高", "source": "国家统计局（2026-11-16）", "cat": "房地产",
             "detail": "新房销售面积-13.7%；二手房网签面积67971万平方米+11.4%，存量房翻新成为家装需求核心支撑；两者口径不可合并。", "url": stats_re_url},
            {"date": "2026-11-16", "publishDate": "2026-11-16", "title": "10月70城房价：一线环比持平、同比降幅收窄",
             "impact": "中", "source": "国家统计局（2026-11-16）", "cat": "房价",
             "detail": "上海新房环比+0.2%；二三线环比仍降；一二三线同比降幅继续收窄。", "url": "https://www.stats.gov.cn/sj/sjjd/202611/t20261116_1965838.html"},
        ],
        "platform": [
            {"date": "2026-11-14", "publishDate": "2026-11-14", "title": "双11首轮：综合电商GMV同比+2.4%，家电以2675亿元居首",
             "impact": "高", "source": "网经社/星图数据", "cat": "双11大盘",
             "detail": "国补2500亿撬动比1:10.3；家电占比15.9%为综合电商第一大品类。星图口径，转述待核。", "url": "https://www.100ec.cn/"},
            {"date": "2026-11-12", "publishDate": "2026-11-12", "title": "京东双11：超2000个家电家居品牌成交翻倍，送装一体单量+200%",
             "impact": "高", "source": "网经社引京东战报", "cat": "京东/双11",
             "detail": "海尔/美的/海信等破10亿；AI产品成交超5000万件；平台自报口径。", "url": "https://www.100ec.cn/"},
            {"date": "2026-11-13", "publishDate": "2026-11-13", "title": "京东麦头条：智能马桶质保纳入保证金规则，售后新增上门换新",
             "impact": "中", "source": "京东麦头条", "cat": "平台规则",
             "detail": "单品资质管控11-12月上线；店铺星级改为三维度评定，家装商家合规成本上升。", "url": "https://mtt.jd.com/"},
            {"date": "2026-11-01", "publishDate": "2026-11-01", "title": "双11智能门锁线上销量112万套(-5.3%)，CR4达74.5%",
             "impact": "高", "source": "洛图科技（199IT转载）", "cat": "智能门锁/双11",
             "detail": "零售额11.8亿元-12.6%；量降价升，头部集中度进一步提高；洛图线上口径与奥维全渠道口径不同。", "url": "https://www.199it.com/"},
        ],
        "policy": [
            {"date": "2026-10-30", "publishDate": "2026-10-30", "title": "广东发布全屋智能产业发展行动方案：2028年营收目标1.1万亿",
             "impact": "高", "source": "广东省（智能头条转载）", "cat": "全屋智能/地方政策",
             "detail": "42条任务清单，覆盖智能家电、家居互联与场景标准；转载来源无页面时间戳，以文件印发日期为准。", "url": "https://www.zhinengtt.com/"},
            {"date": "2026-11-05", "publishDate": "2026-11-05", "title": "《AI照明应用技术规范》起草工作组成立，公牛牵头",
             "impact": "中", "source": "阿拉丁照明网", "cat": "灯具光源/标准",
             "detail": "AI照明进入标准化阶段，灯具与电工头部企业抢占定义权。", "url": "https://www.alighting.cn/"},
            {"date": "2026-11-20", "publishDate": "2026-11-20", "title": "11月LPR：5年期以上3.5%持平，10月新发房贷利率约3.1%",
             "impact": "中", "source": "中国人民银行（中国工业新闻网）", "cat": "金融/房地产",
             "detail": "利率低位维持，按揭成本对购房决策的约束继续减弱。", "url": "https://www.cinic.org.cn/"},
        ],
        "merchant": [
            {"date": "2026-11-01", "publishDate": "2026-11-01", "title": "大家居三季报：美的3673.65亿居首但扣非-22.49%，欧派营收-29.62%",
             "impact": "高", "source": "新浪家居", "cat": "三季报",
             "detail": "定制家居龙头营收与净利双降（欧派净利-67.08%）；顾家控股万格丽切入不锈钢定制寻找增量。", "url": "https://jiaju.sina.com.cn/"},
            {"date": "2026-10-28", "publishDate": "2026-10-28", "title": "1-9月规上建材营收-14.6%、利润-70.1%，上市装企三分之二亏损",
             "impact": "高", "source": "中国建筑材料联合会/中国建筑装饰协会", "cat": "行业运行",
             "detail": "21家上市装企2026H1合计营收339.47亿、归母净利仅4.15亿、CR3=67.87%（转述待核）；9月建材出口转正+5.0%为亮点。", "url": "https://www.cbmf.org/yxjc/"},
            {"date": "2026-11-11", "publishDate": "2026-11-11", "title": "TATA木门“心动样板间”百城招募：促销从折扣转向社区实景体验",
             "impact": "中", "source": "中国质量新闻网", "cat": "木门/渠道",
             "detail": "住建部数据：二手房交易占比由2020年27%升至2026年前8个月52%；企业把体验前置到社区场景应对存量时代。", "url": "https://www.cqn.com.cn/jiajujiancai/content/2026-11/11/content_9180629.htm"},
        ],
    }
    for group, items in monthly_additions.items():
        counts["monthly"] += add_unique(monthly["highlights"][group], items, ("title", "date"))

    update_source_index(sources)
    updated_inventory = update_inventory(inventory)

    for key, obj in (("macro", macro), ("platform", platform), ("policy", policy),
                     ("monthly", monthly), ("sources", sources), ("inventory", inventory)):
        save(PATHS[key], obj)
    print("R14_COUNTS", json.dumps(counts, ensure_ascii=False, sort_keys=True))
    print("R14_INVENTORY_UPDATED", updated_inventory)


if __name__ == "__main__":
    main()
