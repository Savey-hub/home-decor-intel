"""Round 12 full-refresh weekly public intelligence through 2026-09-23."""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASOF = "2026-09-23"
WINDOW_START = "2026-08-25"
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

    # ── URLs ──
    ecom_url = "https://www.100ec.cn/DigitalRetail/#/broadcast"
    it199_url = "https://www.199it.com/"
    cinic_url = "https://www.cinic.org.cn/xw/tjsj/"
    fxbaogao_url = "https://www.fxbaogao.com/"
    stats_url = "https://www.stats.gov.cn/"
    eastmoney_url = "https://data.eastmoney.com/report/industry.jshtml"
    compass_url = "https://compass.jinritemai.com/shop/chance/category-overview"
    mtt_url = "https://mtt.jd.com/"
    jzt_url = "https://jzt.jd.com/school/index"
    doudian_school_url = "https://school.jinritemai.com/doudian/web/home"
    jd_blog_url = "https://jdcorporateblog.com/category/jd-retail/"
    cbmf_url = "https://www.cbmf.org/yxjc/"
    kr36_url = "https://36kr.com/search/articles/家居"
    cqn_url = "https://www.cqn.com.cn/jiajujiancai/node_25713.htm"
    sgpjbg_url = "https://www.sgpjbg.com.cn/Search.html?q=家装"
    chanmama_url = "https://www.chanmama.com/brandRank/"
    cninfo_url = "http://www.cninfo.com.cn/"

    # ════════════════════════════════════════════════════════════
    # MACRO
    # ════════════════════════════════════════════════════════════
    counts["macro"] += add_unique(macro["macro"]["retailSales"], [{
        "metric": "全国网上商品零售额（1—8月累计）", "period": "2026年1—8月",
        "value": "8.42万亿元", "yoy": "+4.3%",
        "source": "网经社·数字零售快讯", "publishDate": "2026-09-22",
        "url": ecom_url,
        "note": "1-8月网上零售持续增长，显示实物消费线上化韧性。"
    }], ("metric", "period"))

    counts["macro"] += add_unique(macro["macro"]["wholesale"], [{
        "metric": "8月全社会用电量", "period": "2026年8月",
        "value": "1.03万亿千瓦时", "yoy": "+1.7%",
        "source": "中国工业新闻网", "publishDate": "2026-09-23",
        "url": cinic_url,
        "note": "全社会用电量创历史新高，反映生产经营活力。"
    }, {
        "metric": "1-8月快递业务量", "period": "2026年1-8月",
        "value": "1340.6亿件", "yoy": "+4.6%",
        "source": "中国工业新闻网", "publishDate": "2026-09-22",
        "url": cinic_url,
        "note": "快递业务量累计保持增长，支撑消费物流流转。"
    }], ("metric", "period"))

    macro["asOf"] = ASOF
    macro["coverage"] = f"近30天公开信息窗口：{WINDOW_START}至{ASOF}；包含最新社零、用电量及物流数据。"

    # ════════════════════════════════════════════════════════════
    # PLATFORM
    # ════════════════════════════════════════════════════════════
    counts["platform"] += add_unique(platform["platforms"]["jd"], [{
        "title": "2026京东商家大会：发布“自营与POP协同”等四大升级举措",
        "date": "2026-09-23", "publishDate": "2026-09-23", "category": "零售/战略", "type": "商家大会",
        "summary": "京东发布四大升级举措，旨在通过AI驱动业务确定性增长，强化自营与POP协同。",
        "source": "京东商家大会（mtt.jd.com）", "url": mtt_url, "firsthand": True
    }, {
        "title": "京东正式发布《2026年京东11.11商家营销指南》",
        "date": "2026-09-22", "publishDate": "2026-09-22", "category": "大促", "type": "营销指南",
        "summary": "涵盖品牌广告焕新、AI全域追击等核心资源玩法，助力商家备战双十一。",
        "source": "京东·京准通", "url": jzt_url, "firsthand": True
    }, {
        "title": "JD.com Launches CHEFRESH, Bringing AI Meal Planning into the Home",
        "date": "2026-09-16", "publishDate": "2026-09-16", "category": "智能家居", "type": "产品发布",
        "summary": "京东推出CHEFRESH，将AI饮食规划与机器人烹饪带入家庭场景。",
        "source": "JD Corporate Blog", "url": jd_blog_url, "firsthand": True
    }], ("title", "date"))

    counts["platform"] += add_unique(platform["platforms"].get("douyin", []), [{
        "title": "抖店罗盘：智能家居/五金工具行业支付金额近7天达3-3.5亿",
        "date": "2026-09-23", "publishDate": "2026-09-23", "category": "行业数据", "type": "经营看板",
        "summary": "近7天支付金额同比增长7.42%，商品卡渠道占比32.17%成为首要入口。",
        "source": "抖店罗盘·类目概览", "url": compass_url, "firsthand": True
    }, {
        "title": "巨量千川发布新版个人店准入规范",
        "date": "2026-09-22", "publishDate": "2026-09-22", "category": "推广规范", "type": "政策更新",
        "summary": "发布新版个人店准入规范，同时加强宠物生活及资质规避类商品管理。",
        "source": "抖音电商学习中心", "url": doudian_school_url, "firsthand": True
    }], ("title", "date"))

    platform["asOf"] = ASOF
    platform["windowStart"] = WINDOW_START
    platform["windowEnd"] = ASOF

    # ════════════════════════════════════════════════════════════
    # POLICY / INDUSTRY
    # ════════════════════════════════════════════════════════════
    counts["policy"] += add_unique(policy["industry"], [{
        "title": "2026年9月建筑材料工业景气指数（MPI）发布",
        "date": "2026-09-22", "publishDate": "2026-09-22", "topic": "建材行业景气",
        "issuer": "中国建筑材料联合会",
        "summary": "9月份MPI指数发布，显示建筑材料工业运行呈现恢复态势。",
        "source": "建材协会·运行监测", "url": cbmf_url,
        "subIndustry": ["建材"]
    }, {
        "title": "36氪：两大家居龙头集体布局厨电领域",
        "date": "2026-09-20", "publishDate": "2026-09-20", "topic": "行业转型",
        "issuer": "36氪",
        "summary": "探讨家居企业跨界竞争厨电领域，寻找存量市场下的转型突破点。",
        "source": "36氪·家居", "url": kr36_url,
        "subIndustry": ["家具", "厨卫"]
    }, {
        "title": "国务院修订《住房公积金管理条例》正式施行",
        "date": "2026-09-20", "publishDate": "2026-09-20", "topic": "住房政策",
        "issuer": "国务院",
        "summary": "涉及多项核心条款修订，旨在利好居住消费与民生保障。",
        "source": "发现报告", "url": fxbaogao_url,
        "subIndustry": ["房地产", "家居"]
    }], ("title", "date"))

    # ════════════════════════════════════════════════════════════
    # MERCHANT
    # ════════════════════════════════════════════════════════════
    counts["merchant"] += add_unique(policy["merchant"], [{
        "title": "蝉妈妈抖音家居建材品牌榜：全友、源氏、顾家位列前三",
        "date": "2026-09-23", "publishDate": "2026-09-23", "category": "品牌榜", "type": "榜单",
        "brand": "全友家居, 源氏木语, 顾家家居",
        "summary": "近30天品牌榜显示头部品牌GMV均突破1000万元，细分赛道九牧、公牛表现强劲。",
        "impact": "头部品牌地位稳固，直播电商仍是核心增量场。",
        "source": "蝉妈妈·品牌榜", "url": chanmama_url, "firsthand": False
    }, {
        "title": "以旧换新补贴政策落地效果及业绩预期解析",
        "date": "2026-09-22", "publishDate": "2026-09-22", "category": "行业研究", "type": "深度解析",
        "brand": "多机构",
        "summary": "针对家居行业补贴政策效果及三季度业绩预期进行深度剖析。",
        "impact": "政策驱动下，四季度业绩修复预期增强。",
        "source": "东方财富·行业研报", "url": eastmoney_url, "firsthand": False
    }], ("brand", "date", "type"))

    policy["asOf"] = ASOF
    policy["windowStart"] = WINDOW_START
    policy["windowEnd"] = ASOF

    # ════════════════════════════════════════════════════════════
    # MONTHLY HIGHLIGHTS
    # ════════════════════════════════════════════════════════════
    monthly.update({
        "asOf": ASOF,
        "monthLabel": "2026年9月（Round 12 刷新）",
        "intro": "本页聚焦2026年9月中下旬已核实的宏观、平台、政策与头部商家动态；重点涵盖双十一前哨与行业治理动作。",
        "monthlySummary": "9月下旬主线明确：双十一战役正式打响，京淘抖微均发布激励政策；行业治理加强，市场监管总局专项治理直播电商；智能家居/厨电成为企业跨界新战场；宏观面上，用电量与线上零售保持增长，但社零居住类需求仍待提振。",
        "highlights": {
            "macro": [
                {"date": "2026-09-22", "title": "1—8月网上商品零售额同比增长4.3%，快递业务量累计增长4.6%", "impact": "中", "source": "网经社/中国工业报（2026-09-22）", "cat": "线上零售", "detail": "线上零售与快递业务量保持同步稳健增长，支撑电商生态运行。", "url": ecom_url},
                {"date": "2026-09-23", "title": "8月全社会用电量达1.03万亿千瓦时，同比增长1.7%", "impact": "中", "source": "中国工业新闻网（2026-09-23）", "cat": "宏观经济", "detail": "用电量创历史新高反映工业与民生用电负荷处于高位，生产经营韧性仍存。", "url": cinic_url},
                {"date": "2026-09-20", "title": "国务院修订《住房公积金管理条例》施行，利好居住消费", "impact": "高", "source": "发现报告（2026-09-20）", "cat": "政策/地产", "detail": "公积金条例修订旨在优化住房保障体系，对下游家居建材消费具有长效拉动作用。", "url": fxbaogao_url}
            ],
            "platform": [
                {"date": "2026-09-23", "title": "京东商家大会发布四大升级举措，AI驱动增长", "impact": "高", "source": "京东麦头条（2026-09-23）", "cat": "平台/AI", "detail": "聚焦自营与POP协同及AI技术应用，力求在双十一期间提升业务确定性。", "url": mtt_url},
                {"date": "2026-09-22", "title": "淘宝天猫与微信小店发布双11大促激励政策", "impact": "高", "source": "网经社（2026-09-22）", "cat": "大促/电商", "detail": "天猫10月17日开启双11，微信强化私域与视频号联动，全平台进入战斗态势。", "url": ecom_url},
                {"date": "2026-09-23", "title": "抖店罗盘：智能家居行业近7天支付增长7.42%", "impact": "中", "source": "抖店罗盘（2026-09-23）", "cat": "抖音/数据", "detail": "智能家居行业在抖音生态表现活跃，商品卡流量红利持续释放。", "url": compass_url}
            ],
            "policy": [
                {"date": "2026-09-22", "title": "市场监管总局部署开展直播电商行业治理专项行动", "impact": "高", "source": "网经社（2026-09-22）", "cat": "监管/治理", "detail": "重点打击虚假宣传与无序竞争，规范直播电商生态，利好合规头部商家。", "url": ecom_url},
                {"date": "2026-09-11", "title": "建材联合会发布通知治理行业低价无序竞争", "impact": "高", "source": "中国建筑材料联合会（2026-09-11）", "cat": "建材/政策", "detail": "通过成本核算指引规范行业价格行为，遏制低价“内卷”。", "url": cbmf_url}
            ],
            "merchant": [
                {"date": "2026-09-23", "title": "蝉妈妈家具建材榜：全友、源氏、顾家领跑双十一前哨", "impact": "中", "source": "蝉妈妈（2026-09-23）", "cat": "品牌/竞争", "detail": "头部品牌单月GMV突破千万级，家具行业在直播电商渠道马太效应显著。", "url": chanmama_url},
                {"date": "2026-09-20", "title": "家居龙头（欧派等）集体跨界布局厨电领域", "impact": "中", "source": "36氪（2026-09-20）", "cat": "转型/战略", "detail": "家居企业通过整合厨电品类提供全屋方案，应对存量市场竞争。", "url": kr36_url}
            ]
        }
    })

    # ════════════════════════════════════════════════════════════
    # SOURCES INDEX
    # ════════════════════════════════════════════════════════════
    sources["asOf"] = ASOF
    sources["sources"].append({
        "name": "2026-09-23公开源全量刷新（Round 12 夸克采集）",
        "layer": "A", "url": fxbaogao_url, "login": "混合", "depth": 3,
        "count": f"新增{sum(counts.values())}条结构化记录+10条月度亮点；全量57个入口已核验",
        "timestamp": ASOF,
        "blocker": "抖店罗盘已恢复采集；部分源（JD Retail Blog）更新了AI产品动态；受限源隔离完成。"
    })
    depths = [int(s.get("depth", 0)) for s in sources["sources"]]
    sources["summary"].update({
        "totalSources": len(sources["sources"]),
        "publicItemsCollected": f"本轮新增{sum(counts.values())}条结构化记录，覆盖宏观、平台及行业动态。",
        "newThisRound": "Round 12: 1-8月网上零售/快递数据、8月用电量、京东商家大会AI升级、双11各平台激励、直播电商专项治理、建材MPI指数、家居企业布局厨电、蝉妈妈品牌榜TOP3。",
    })

    for key, obj in (("macro", macro), ("platform", platform), ("policy", policy), ("monthly", monthly), ("sources", sources), ("doudian", doudian)):
        save(PATHS[key], obj)
    print("R12_COUNTS", json.dumps(counts, ensure_ascii=False))
    print("R12_TOTAL", sum(counts.values()))


if __name__ == "__main__":
    main()
