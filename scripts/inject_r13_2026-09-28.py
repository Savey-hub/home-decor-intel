"""Round 13 full-refresh public intelligence through 2026-09-28."""
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASOF = "2026-09-28"
WINDOW_START = "2026-08-30"
ROUND = 13
METHOD = "浏览器核验 (Quark)"
PATHS = {
    "macro": os.path.join(ROOT, "data", "macro_realestate.json"),
    "platform": os.path.join(ROOT, "data", "platform_dynamics.json"),
    "policy": os.path.join(ROOT, "data", "industry_policy.json"),
    "monthly": os.path.join(ROOT, "data", "v2", "monthly_highlights.json"),
    "sources": os.path.join(ROOT, "data", "v2", "data_sources_index.json"),
    "inventory": os.path.join(ROOT, "data", "v2", "url_inventory.json"),
}


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


def update_source_index(sources):
    updates = [
        ("国家统计局（", 3, "新增1—8月全国规模以上工业企业利润同比增速；房地产页未发现口径完整的新全国指标。"),
        ("京准通·学堂", 3, "夸克进入列表并下钻正文，核验9月28日统一报表入口、AI查数与智能诊断升级。"),
        ("千瓜数据·行业流量大盘", 2, "夸克进入工作台并核验9月24日《AI生活，在红书的“101种打开方式”》标题、日期与公开摘要。"),
        ("奥维云网 AVC 官网原始报告页", 1, "夸克核验9月24日高端建材渠道家电趋势与智能安防峰会议程标题；未获得可公开引用的报告数值或议程正文。"),
        ("奥维云网 AVC（", 3, "夸克复核官网资讯流；Round 13新增仅采用标题、日期层证据，不推断报告数值。"),
        ("新浪家居 jiaju", 2, "夸克核验页面与可见资讯，取得9月28日家居行业案例线索；无可比量化指标。"),
        ("三个皮匠报告", 1, "夸克核验家装搜索结果页，取得报告标题、日期与页数等索引信息；正文仍受会员权限限制。"),
        ("艾瑞咨询报告库", 2, "夸克核验报告列表及公开摘要；窗口内未发现9月24日至28日新增家装主题报告。"),
        ("第一财经数据 CBNData", 2, "夸克核验报告与看点列表；窗口内未发现9月24日至28日新增家装主题内容。"),
        ("艾媒咨询", 2, "夸克核验报告列表与公开摘要；空气能白皮书为邻近领域信息，未作为核心家装新增。"),
        ("克而瑞 CRIC 官网", 1, "夸克核验首页可见数据，但城市与统计口径缺失，未纳入正式指标。"),
    ]
    for source in sources["sources"]:
        name = source.get("name", "")
        for needle, depth, blocker in updates:
            if needle in name:
                source["depth"] = depth
                source["timestamp"] = ASOF
                source["blocker"] = blocker
                if depth == 1:
                    source["count"] = "标题/索引级核验"
                elif "京准通" in needle:
                    source["count"] = "1条正文级更新"
                else:
                    source["count"] = "本轮已复核"
                break

    depth_counts = collections.Counter(int(x.get("depth", 0) or 0) for x in sources["sources"])
    sources["asOf"] = ASOF
    sources["summary"].update({
        "totalSources": len(sources["sources"]),
        "depth3": depth_counts[3],
        "depth2": depth_counts[2],
        "depth1": depth_counts[1],
        "depth0_blocked": depth_counts[0],
        "publicItemsCollected": "Round 13新增9条结构化记录，覆盖宏观、平台、行业与商家动态；其余板块均完成本轮核验。",
        "newThisRound": "Round 13：1—8月规上工业企业利润、京准通报表与AI查数升级、小红书AI生活趋势、米家全屋智能体验店、整装S2B2C模式与直播电商低价品控风险。",
        "blockedNote": "拼多多、微信小店、快手、淘宝天猫未取得可独立核验的家装垂类新增；CRIC首页数据因城市与统计口径缺失未采用。",
    })


def update_inventory(inventory):
    groups = {
        "ok_yield": {2, 3, 4, 6, 7, 8, 9, 11, 13, 14, 15, 16, 18, 19, 20, 24, 27, 30, 31, 33, 35, 42, 45, 48, 52},
        "ok_empty": {5, 10, 17, 21, 22, 25, 32, 36, 37, 38, 39, 40, 41, 46, 47, 49, 50, 51, 56},
        "need_login_browser": {23, 26, 28, 53},
        "ok_empty_internal": {54, 55, 57},
    }
    conclusions = {
        "ok_yield": "夸克完成页面、栏目与可见详情核验；取得本轮可追溯内容。",
        "ok_empty": "夸克完成页面与可见栏目核验；本轮未取得可公开披露的有效新增。",
        "need_login_browser": "夸克核验后仍受登录或权限门槛限制；本轮未取得可公开披露的有效新增。",
        "ok_empty_internal": "仅保留匿名来源占位，未形成可公开披露的有效产出。",
    }
    specific = {
        4: "夸克进入千瓜工作台，核验9月24日AI生活趋势文章的标题、日期与公开摘要。",
        9: "夸克进入京准通学堂并下钻正文，核验9月28日报表入口统一、AI查数与智能诊断升级。",
        19: "夸克核验奥维云网资讯流，取得两条9月24日标题与日期证据；未推断报告数值。",
        20: "夸克核验国家统计局，取得9月28日发布的1—8月规上工业企业利润同比增速。",
        24: "夸克核验新浪家居可见资讯，取得9月28日家居行业案例线索。",
        31: "夸克核验家装报告索引，取得标题、日期与页数信息；未读取会员正文。",
        52: "夸克核验CRIC首页；因城市与统计口径缺失，未采用可见数值。",
    }
    labels = {
        "ok_yield": "夸克核验完成·取得有效内容",
        "ok_empty": "夸克核验完成·本轮无有效新增",
        "need_login_browser": "登录或权限门槛未通过",
        "ok_empty_internal": "受限来源占位·本轮无公开产出",
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
        "note": "Round 13完成51个活跃入口的夸克复核；25个入口取得有效内容，受限来源仅保留匿名占位。",
        "yieldedCount": status_counts.get("ok_yield", 0),
    }
    return updated


def main():
    macro = load(PATHS["macro"])
    platform = load(PATHS["platform"])
    policy = load(PATHS["policy"])
    monthly = load(PATHS["monthly"])
    sources = load(PATHS["sources"])
    inventory = load(PATHS["inventory"])
    counts = collections.Counter()

    stats_url = "https://www.stats.gov.cn/"
    jzt_detail_url = "https://jzt.jd.com/school/course/detail?contentId=19430"
    qian_gua_url = "https://app.qian-gua.com/#/workbench/red"
    retail_url = "https://www.100ec.cn/DigitalRetail/#/broadcast"
    avc_url = "https://www.avc-mr.com/home"
    sina_home_url = "https://jiaju.sina.com.cn/"

    counts["macro"] += add_unique(macro["macro"]["wholesale"], [{
        "metric": "全国规模以上工业企业利润总额（1—8月累计）",
        "period": "2026年1—8月",
        "value": "—",
        "yoy": "+15.7%",
        "source": "国家统计局",
        "publishDate": ASOF,
        "url": stats_url,
        "note": "全国规上工业企业总体口径，不代表家具或建材细分行业利润。",
    }], ("metric", "period"))
    macro["asOf"] = ASOF
    macro["coverage"] = f"近30天公开信息窗口：{WINDOW_START}至{ASOF}；覆盖消费、线上零售、工业供应链、房地产与信心指标，本轮无新增全国可比房地产指标。"
    counts["macro_gap"] += add_text_unique(macro["gaps"], "Round 13（2026-09-28）核验未发现新的全国可比房地产销售、投资、新开工、竣工或价格指标；CRIC首页可见数值缺少城市与统计口径，未纳入正式数据。")
    counts["macro_conflict"] += add_text_unique(macro["conflicts"], "国家统计局1—8月全国规上工业企业利润同比+15.7%为全部规上工业总体口径，不能与家具制造业或建材细分利润直接比较，也不能据此推断家居制造业利润已经修复。")

    jd_item = {
        "title": "京准通报表全新升级：入口统一，AI查数更便捷",
        "date": ASOF,
        "publishDate": ASOF,
        "category": "营销工具",
        "type": "产品升级",
        "summary": "京准通将分散报表入口统一，并新增AI查数与智能诊断能力，降低商家投放数据查询和问题定位成本。",
        "source": "京准通·京点书院",
        "url": jzt_detail_url,
        "firsthand": True,
    }
    xhs_item = {
        "title": "AI生活，在红书的“101种打开方式”",
        "date": "2026-09-24",
        "publishDate": "2026-09-24",
        "category": "消费趋势",
        "type": "平台内容趋势",
        "summary": "千瓜公开摘要显示，AI眼镜、机器人等产品正进入更具体的生活化种草场景；该条仅采用标题、日期与公开摘要，不外推量化规模。",
        "source": "千瓜行研",
        "url": qian_gua_url,
        "firsthand": False,
    }
    cross_item = {
        "title": "多平台发布双11招商政策与商家经营要点",
        "date": "2026-09-24",
        "publishDate": "2026-09-24",
        "category": "大促",
        "type": "政策汇总",
        "summary": "公开快讯标题覆盖淘宝天猫、京东、抖音、快手、拼多多、微信小店和小红书；本轮仅完成标题与日期层核验，具体招商条款以各平台原文为准。",
        "source": "网经社·数字零售快讯",
        "url": retail_url,
        "firsthand": False,
    }
    counts["platform"] += add_unique(platform["platforms"]["jd"], [jd_item], ("title", "date"))
    platform["platforms"]["xhs"] = [x for x in platform["platforms"].get("xhs", []) if x.get("date") != "待核实"]
    counts["platform"] += add_unique(platform["platforms"]["xhs"], [xhs_item], ("title", "date"))
    counts["platform"] += add_unique(platform["crossPlatform"], [cross_item], ("title", "date"))
    platform.update({
        "asOf": ASOF,
        "windowStart": WINDOW_START,
        "windowEnd": ASOF,
        "windowNote": f"近30天公开动态窗口：{WINDOW_START}至{ASOF}；仅采用已核验标题、摘要或正文，登录源无新增时不沿用旧值冒充本轮更新。",
    })
    counts["platform_gap"] += add_text_unique(platform["gaps"], "Round 13（2026-09-28）已核验拼多多、微信小店/视频号、快手与淘宝天猫相关入口，未取得可独立核验的家装家居垂类新增；9月24日双11条目仅作为跨平台标题与日期层线索，不推断具体条款。")

    industry_additions = [{
        "title": "平台化是整装模式发展方向，居魔方S2B2C生态模式的行业观察",
        "date": ASOF,
        "publishDate": ASOF,
        "topic": "整装模式",
        "issuer": "新浪家居",
        "summary": "文章讨论以S2B2C平台连接供应链、装企与消费者的整装协作模式；本条为行业案例观察，不代表模式已形成全行业共识。",
        "source": "新浪家居",
        "url": sina_home_url,
        "subIndustry": ["装修", "全屋定制", "建材装潢"],
    }, {
        "title": "89.9元溜溜椅案例提示直播电商低价商品品控风险",
        "date": ASOF,
        "publishDate": ASOF,
        "topic": "直播电商品控",
        "issuer": "新浪家居",
        "summary": "公开案例反映低价直播商品可能面临质量、售后与供应链治理压力；仅作为单一案例风险提示，不用于推断行业不良率。",
        "source": "新浪家居",
        "url": sina_home_url,
        "subIndustry": ["家具", "电商运营"],
    }, {
        "title": "2026年8月中国高端建材渠道家电销售趋势",
        "date": "2026-09-24",
        "publishDate": "2026-09-24",
        "topic": "渠道趋势",
        "issuer": "奥维云网",
        "summary": "本轮仅核验到报告标题与发布日期，未取得可公开引用的报告数值，保留为后续深挖线索。",
        "source": "奥维云网",
        "url": avc_url,
        "subIndustry": ["建材装潢", "卫浴厨房", "全屋智能"],
    }, {
        "title": "首届智能安防行业峰会最新议程发布",
        "date": "2026-09-24",
        "publishDate": "2026-09-24",
        "topic": "智能安防",
        "issuer": "奥维云网",
        "summary": "本轮仅核验到峰会议程标题与发布日期，未取得议程正文，不推断参会机构、议题或数据。",
        "source": "奥维云网",
        "url": avc_url,
        "subIndustry": ["全屋智能", "智能摄像头"],
    }]
    merchant_additions = [{
        "title": "河南首家米家智能家电体验店开业",
        "date": ASOF,
        "publishDate": ASOF,
        "category": "全屋智能",
        "type": "渠道拓展",
        "brand": "小米/米家",
        "summary": "河南首家米家智能家电体验店开业，以全屋智能场景体验为核心，并释放逐步向全国拓展新模式的信号。",
        "impact": "全屋智能竞争从单品销售进一步转向线下场景体验与成套方案交付。",
        "source": "新浪家居",
        "url": sina_home_url,
        "firsthand": False,
    }]
    counts["industry"] += add_unique(policy["industry"], industry_additions, ("title", "date"))
    counts["merchant"] += add_unique(policy["merchant"], merchant_additions, ("title", "date"))
    policy.update({
        "asOf": ASOF,
        "windowStart": WINDOW_START,
        "windowEnd": ASOF,
        "windowNote": f"近30天窗口：{WINDOW_START}至{ASOF}；仅收录带来源、发布日期和URL的公开条目；标题级证据明确标注，不推断正文。",
    })
    counts["policy_gap"] += add_text_unique(policy["gaps"], "Round 13（2026-09-24至2026-09-28）未发现可核实的新国家级家装政策、标准、补贴或以旧换新措施；本轮不以旧政策补位。")
    if not any(x.get("item") == "直播电商低价品控案例的外推边界" for x in policy["conflicts"]):
        policy["conflicts"].append({
            "item": "直播电商低价品控案例的外推边界",
            "detail": "89.9元溜溜椅为单一公开案例，只能用于提示低价商品的质量、售后与供应链治理风险，不能推断家具行业整体质量水平或不良率。",
        })
        counts["policy_conflict"] += 1

    monthly.update({
        "asOf": ASOF,
        "monthLabel": "2026年9月（Round 13 刷新）",
        "intro": "本页聚焦2026年9月已核实的宏观、平台、政策、行业与头部商家动态；9月24日至28日新增重点为工业利润、投放工具升级、AI生活种草与全屋智能线下体验。",
        "monthlySummary": "9月末的新增主线有三条：全国规上工业利润改善但不能外推到家居细分；平台侧进入双11准备期并加速AI查数与经营诊断；家居行业从单品竞争进一步转向全屋智能体验、整装协同，同时低价直播商品的品控与售后风险需要前置治理。",
    })
    monthly_additions = {
        "macro": [{"date": ASOF, "publishDate": ASOF, "title": "1—8月全国规上工业企业利润同比增长15.7%", "impact": "中", "source": "国家统计局（2026-09-28）", "cat": "工业利润", "detail": "工业利润总体改善，但该口径不代表家具或建材细分行业，不能直接推断家居制造业修复。", "url": stats_url}],
        "platform": [
            {"date": ASOF, "publishDate": ASOF, "title": "京准通统一报表入口并上线AI查数与智能诊断", "impact": "高", "source": "京准通·京点书院（2026-09-28）", "cat": "平台/AI", "detail": "投放数据查询、诊断与决策链路继续被AI工具压缩，家装商家需同步升级报表和投放复盘方法。", "url": jzt_detail_url},
            {"date": "2026-09-24", "publishDate": "2026-09-24", "title": "千瓜观察：AI产品进入小红书生活化种草场景", "impact": "中", "source": "千瓜行研（2026-09-24）", "cat": "小红书/AI生活", "detail": "AI眼镜、机器人等从技术话题转向日常体验叙事，为智能家居与硬件内容表达提供场景化参考。", "url": qian_gua_url},
        ],
        "merchant": [
            {"date": ASOF, "publishDate": ASOF, "title": "河南首家米家智能家电体验店开业，强化全屋智能场景", "impact": "高", "source": "新浪家居（2026-09-28）", "cat": "全屋智能/渠道", "detail": "线下门店由单品陈列转向完整空间体验，竞争重点进一步落到成套方案、体验与交付。", "url": sina_home_url},
            {"date": ASOF, "publishDate": ASOF, "title": "89.9元溜溜椅案例暴露直播低价商品品控风险", "impact": "中", "source": "新浪家居（2026-09-28）", "cat": "家具/风险", "detail": "该案例提示平台和商家要前置治理低价商品的质量、售后与供应链责任，但不可外推为行业整体不良率。", "url": sina_home_url},
        ],
    }
    for group, items in monthly_additions.items():
        counts["monthly"] += add_unique(monthly["highlights"][group], items, ("title", "date"))

    update_source_index(sources)
    updated_inventory = update_inventory(inventory)

    for key, obj in (("macro", macro), ("platform", platform), ("policy", policy), ("monthly", monthly), ("sources", sources), ("inventory", inventory)):
        save(PATHS[key], obj)
    print("R13_COUNTS", json.dumps(counts, ensure_ascii=False, sort_keys=True))
    print("R13_INVENTORY_UPDATED", updated_inventory)


if __name__ == "__main__":
    main()
