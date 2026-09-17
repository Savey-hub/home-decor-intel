"""Round 9 weekly public intelligence refresh through 2026-09-16."""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASOF = "2026-09-16"
WINDOW_START = "2026-08-18"
PATHS = {
    "macro": os.path.join(ROOT, "data", "macro_realestate.json"),
    "platform": os.path.join(ROOT, "data", "platform_dynamics.json"),
    "policy": os.path.join(ROOT, "data", "industry_policy.json"),
    "monthly": os.path.join(ROOT, "data", "v2", "monthly_highlights.json"),
    "sources": os.path.join(ROOT, "data", "v2", "data_sources_index.json"),
    "doudian": os.path.join(ROOT, "data", "sources", "layerC_doudian_compass.json"),
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, value):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)


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


def main():
    macro = load(PATHS["macro"])
    platform = load(PATHS["platform"])
    policy = load(PATHS["policy"])
    monthly = load(PATHS["monthly"])
    sources = load(PATHS["sources"])
    doudian = load(PATHS["doudian"])
    counts = {"macro": 0, "platform": 0, "policy": 0, "merchant": 0}

    nbs_url = "https://finance.cnr.cn/ycbd/20260915/t20260915_527814214.shtml"
    bhi_url = "https://www.bjnews.com.cn/detail/1789520087169009.html"
    policy_url = "https://www.mofcom.gov.cn/zwgk/zcfb/art/2026/art_98f578b88d3f47538d7b516745faf230.html"
    jd_url = "https://finance.sina.com.cn/stock/t/2026-09-09/doc-inirfivs8953351.shtml"
    ciff_url = "http://www.sh.chinanews.com.cn/shms/2026-09-09/149096.shtml"
    furniture_url = "https://www.sohu.com/a/1072818873_100175166/"

    counts["macro"] += add_unique(macro["macro"]["retailSales"], [{
        "metric": "社会消费品零售总额（8月单月）", "period": "2026年8月", "value": "39668亿元", "yoy": "+0.4%",
        "source": "国家统计局（央广网转载）", "publishDate": "2026-09-15", "url": nbs_url,
        "note": "增速较7月继续放缓，家具和建材需求仍处弱复苏环境。"
    }, {
        "metric": "社会消费品零售总额（1—8月累计）", "period": "2026年1—8月", "value": "329915亿元", "yoy": "+1.1%",
        "source": "国家统计局（央广网转载）", "publishDate": "2026-09-15", "url": nbs_url,
        "note": "总量保持增长，但升级类和必需类分化明显。"
    }, {
        "metric": "限额以上单位家具类零售额（8月单月）", "period": "2026年8月", "value": "待核实", "yoy": "-7.9%",
        "source": "国家统计局数据（腾讯新闻转载）", "publishDate": "2026-09-15",
        "url": "https://news.qq.com/rain/a/20260915A04PUU00", "note": "单月金额未在可访问正文中完整核实，保留待核实。"
    }, {
        "metric": "限额以上单位建筑及装潢材料类零售额（8月单月）", "period": "2026年8月", "value": "待核实", "yoy": "-11.8%",
        "source": "国家统计局数据（腾讯新闻转载）", "publishDate": "2026-09-15",
        "url": "https://news.qq.com/rain/a/20260915A04PUU00", "note": "单月金额未在可访问正文中完整核实，保留待核实。"
    }], ("metric", "period"))
    counts["macro"] += add_unique(macro["macro"]["wholesale"], [{
        "metric": "全国规模以上建材家居卖场销售额（8月）", "period": "2026年8月", "value": "1121.23亿元", "yoy": "+6.13%",
        "source": "中国建筑材料流通协会（新京报转载）", "publishDate": "2026-09-16", "url": bhi_url,
        "note": "环比下降1.30%；1—8月累计8897.59亿元，同比下降2.65%。"
    }, {
        "metric": "全国建材家居景气指数BHI（8月）", "period": "2026年8月", "value": "112.73", "yoy": "+2.67点",
        "source": "中国建筑材料流通协会（新京报转载）", "publishDate": "2026-09-16", "url": bhi_url,
        "note": "环比上升2.42点，经理人信心指数165.52，金九银十预期升温。"
    }], ("metric", "period"))
    macro["asOf"] = ASOF
    macro["coverage"] = f"近30天公开信息窗口：{WINDOW_START}至{ASOF}；宏观统计采用最新可得官方月份。"
    macro.setdefault("gaps", []).append("2026年8月家具类、建筑及装潢材料类单月零售额金额未在可访问官方正文中完整核实，仅保留同比，金额标注待核实。")

    counts["platform"] += add_unique(platform["platforms"]["jd"], [{
        "title": "京东家电家居闪电新品季启动，超千款新品全渠道上新",
        "date": "2026-09-09", "publishDate": "2026-09-09", "category": "家电家居", "type": "新品季",
        "summary": "覆盖大家电、小家电、家具和家装，超1000款新品在线上线下渠道集中上新；部分商品接入秒送最快1小时达，并可叠加国补和以旧换新优惠。",
        "source": "新浪财经（2026-09-09）", "url": jd_url, "firsthand": False
    }], ("title", "date"))
    platform["asOf"] = ASOF
    platform["windowStart"] = WINDOW_START
    platform["windowEnd"] = ASOF
    platform["windowNote"] = f"近30天公开动态窗口：{WINDOW_START}至{ASOF}；登录源无法核实新值时沿用上期并披露。"

    counts["policy"] += add_unique(policy["policy"], [{
        "title": "商务部等8部门印发《促进智能家居消费行动方案》",
        "issueDate": "2026-09-02", "publishDate": "2026-09-14", "effectiveDate": "2026-09-02",
        "issuer": "商务部等8部门", "scope": "全国智能家居产业与消费市场", "category": "促消费/以旧换新/标准",
        "subIndustry": ["智能家居", "全屋智能", "适老化", "家装", "家具回收"],
        "summary": "支持卖场和购物中心建设智能家居体验中心、全屋智能与数字家庭样板间；加快互联互通强制性国家标准；支持地方自主确定智能家居补贴品类和标准，统筹支持全屋智能购新，并完善送新收旧和回收服务。",
        "impact": "全屋智能、适老化、互联互通和以旧换新形成政策合力，平台应同步完善补贴商品池、体验场景和回收履约。",
        "source": "商务部消费促进司", "url": policy_url, "firsthand": True
    }], ("title", "issueDate"))
    counts["policy"] += add_unique(policy["industry"], [{
        "title": "8月BHI升至112.73，规模以上卖场单月销售额同比增长6.13%",
        "date": "2026-09-16", "publishDate": "2026-09-16", "topic": "行业景气/建材家居卖场", "issuer": "中国建筑材料流通协会",
        "summary": "8月BHI环比上升2.42点、同比上升2.67点；规模以上建材家居卖场销售额1121.23亿元，同比增6.13%，但1—8月累计仍同比下降2.65%。",
        "source": "中国建筑材料流通协会（新京报转载）", "url": bhi_url,
        "subIndustry": ["建材", "家具", "家居卖场"]
    }], ("title", "date"))
    counts["merchant"] += add_unique(policy["merchant"], [{
        "title": "65家上市家居企业中报显示行业营收利润分化，头部寻求结构性增长",
        "date": "2026-09-04", "publishDate": "2026-09-04", "category": "家居上市公司", "type": "中报综述", "brand": "家居上市公司",
        "summary": "行业媒体汇总65家上市家居企业中报，覆盖定制、软体、建材和智能家居等板块；部分原始页面访问受限，本轮仅采用行业分化结论，不转录无法逐项核验的企业数字。",
        "impact": "需求收缩下现金流、渠道效率、出海和智能化成为判断企业韧性的核心指标。",
        "source": "今日家居（搜狐转载，2026-09）", "url": furniture_url, "firsthand": False
    }], ("brand", "date", "type"))
    policy["asOf"] = ASOF
    policy["windowStart"] = WINDOW_START
    policy["windowEnd"] = ASOF
    policy["windowNote"] = f"近30天窗口：{WINDOW_START}至{ASOF}；仅收录带来源、发布日期和URL的公开条目。"

    monthly.update({
        "asOf": ASOF,
        "monthLabel": "2026年9月（自然月至今）",
        "intro": "本页聚焦2026年9月1日至9月16日已核实的宏观、平台、政策与头部商家/行业要闻；8月下旬事项保留在近30天专题数据中。",
        "monthlySummary": "9月中旬主线由需求弱复苏与政策加码并行：8月社零增速放缓、家具和建材仍负增长，但BHI与卖场单月销售额回升；智能家居行动方案把全屋智能、互联互通、补贴和回收服务推向统一政策框架。",
        "highlights": {
            "macro": [{"date": "2026-09-15", "title": "8月社零同比增长0.4%，家具和建筑装潢材料分别下降7.9%和11.8%", "impact": "高", "source": "国家统计局数据（央广网/腾讯新闻，2026-09-15）", "cat": "宏观消费", "detail": "8月社零增速较7月继续放缓；家具与建材仍显著承压，行业不能依赖总量自然回暖，应优先争夺存量翻新和政策补贴需求。", "url": nbs_url}, {"date": "2026-09-16", "title": "8月BHI升至112.73，规模以上建材家居卖场销售额同比增长6.13%", "impact": "中", "source": "中国建筑材料流通协会（新京报，2026-09-16）", "cat": "行业景气", "detail": "单月卖场销售改善但1—8月累计仍下降2.65%，体现旺季预期改善与全年需求压力并存。", "url": bhi_url}],
            "platform": [{"date": "2026-09-09", "title": "京东闪电新品季超千款家电家居新品全渠道上新", "impact": "中", "source": "新浪财经（2026-09-09）", "cat": "新品/履约", "detail": "新品覆盖家具、家装和家电，叠加国补与以旧换新，部分商品最快1小时达，竞争焦点由价格进一步延伸到新品首发和即时履约。", "url": jd_url}],
            "policy": [{"date": "2026-09-14", "title": "八部门发布促进智能家居消费行动方案", "impact": "高", "source": "商务部消费促进司（2026-09-14公开）", "cat": "智能家居/国补以旧换新", "detail": "政策支持全屋智能体验场景、互联互通强制标准、地方自主补贴、适老化产品和送新收旧，智能家居从单品补贴转向场景与服务体系建设。", "url": policy_url}],
            "merchant": [{"date": "2026-09-09", "title": "上海家博会与建博会闭幕，家居品牌集中展示智能化与场景化供给", "impact": "中", "source": "中新社上海（2026-09-09）", "cat": "展会/品牌", "detail": "展会为家具、建材、设计和智能家居品牌提供集中展示与渠道连接，品牌获客继续向场景体验、设计协同和全球采购延伸。", "url": ciff_url}]
        }
    })

    doudian["carryForward"] = True
    doudian["carryForwardNote"] = "2026-09-16未获得可核实的新周期抖店罗盘核心指标；按登录源规则沿用2026-08-13已核实数据，不改写任何数值，并将缺口保留在公开说明。"
    doudian["loginMethod"] = "本机夸克既有授权状态；本轮无可核实新指标"
    doudian["scrapeMethod"] = "沿用上期已核实抖店罗盘数据，未编造新周期数值"

    sources["asOf"] = ASOF
    for src in sources["sources"]:
        if src.get("name", "").startswith("抖店罗盘·类目概览"):
            src.update(timestamp=ASOF, blocker="2026-09-16未取得可核实新周期指标，沿用2026-08-13已核实数据；未写入新数值。")
    sources["sources"].append({
        "name": "2026-09-16公开源周更（国家统计局/商务部/中建材流通协会/京东与行业媒体）",
        "layer": "A", "url": policy_url, "login": "免登录", "depth": 3,
        "count": f"新增{sum(counts.values())}条结构化记录+5条月度亮点", "timestamp": ASOF,
        "blocker": "抖店罗盘无可核实新周期指标；65家家居企业汇总原站403，仅保留可验证的行业层结论；家具/建材8月单月金额待核实。"
    })
    depths = [int(s.get("depth", 0)) for s in sources["sources"]]
    sources["summary"].update({
        "totalSources": len(sources["sources"]), "depth3": depths.count(3), "depth2": depths.count(2),
        "depth1": depths.count(1), "depth0_blocked": depths.count(0),
        "publicItemsCollected": f"本轮新增{sum(counts.values())}条近30天结构化记录，并更新9月自然月至今四组亮点共5条。",
        "newThisRound": "2026-09-16刷新：8月社零与家具/建材同比、8月BHI及卖场销售、智能家居消费行动方案、京东闪电新品季、家居上市公司中报行业结论。",
        "blockedNote": "抖店罗盘无可核实新周期指标，沿用旧值；家居企业汇总原站403；家具/建材8月单月金额未完整核实，标待核实。"
    })

    for record in policy["policy"]:
        if not isinstance(record.get("subIndustry"), list):
            raise SystemExit(f"policy.subIndustry must be list: {record.get('title')}")
    required = {"date", "title", "impact", "source", "cat", "detail", "url"}
    for group, items in monthly["highlights"].items():
        if not items:
            raise SystemExit(f"empty highlight group: {group}")
        for item in items:
            if set(item) != required:
                raise SystemExit(f"highlight schema error: {group} {set(item)}")

    for key, obj in (("macro", macro), ("platform", platform), ("policy", policy), ("monthly", monthly), ("sources", sources), ("doudian", doudian)):
        save(PATHS[key], obj)
    print("R9_COUNTS", json.dumps(counts, ensure_ascii=False))
    print("R9_TOTAL", sum(counts.values()))
    print("DOUDIAN_CARRY_FORWARD", doudian["carryForward"])


if __name__ == "__main__":
    main()
