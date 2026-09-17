"""r8 weekly intelligence refresh for 2026-09-09.

Adds only verifiable public records from the latest 30-day window, refreshes
September month-to-date highlights and source metadata, and records the Quark
Doudian login check without changing carried-forward platform figures.
"""
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "_work")
ASOF = "2026-09-09"
WINDOW_START = "2026-08-11"

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


def save(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def norm(value):
    return "".join(str(value).split()).lower()


def add_unique(items, additions, keys):
    existing = {tuple(norm(x.get(k, "")) for k in keys) for x in items}
    added = 0
    for item in additions:
        missing = [k for k in ("source", "publishDate", "url") if not item.get(k)]
        if missing:
            raise SystemExit(f"new record missing {missing}: {item.get('title') or item.get('metric')}")
        key = tuple(norm(item.get(k, "")) for k in keys)
        if key not in existing:
            items.append(item)
            existing.add(key)
            added += 1
    return added


NBS_70_URL = "https://www.stats.gov.cn/sj/zxfb/202608/t20260817_1965050.html"
NBS_RE_URL = "https://www.stats.gov.cn/sj/zxfbhjd/202608/t20260817_1965053.html"
SH_HOUSING_URL = "https://zjw.sh.gov.cn/jsgl/20260820/82df5e3bf87845ed903492dc5d495574.html"
MOHURD_URL = "https://www.mohurd.gov.cn/gongkai/zc/xzgfxwjk/art/2026/art_105194568.html"
COMMERCE_URL = "https://www.cj.gov.cn/p129/tzgg/20260828/594034.html"
SAMR_URL = "https://www.samr.gov.cn/xw/zj/art/2026/art_26c874532f4c4f318d3dcaf04e7cdfac.html"
QUANZHOU_URL = "https://scjgj.quanzhou.gov.cn/xxgk/flfg/flfggz/202609/t20260907_3325492.htm"
JD_MALL_URL = "https://k.sina.cn/article_5675440730_152485a5a020026qaa.html"
FURNITURE_FAIR_URL = "https://finance.sina.com.cn/jjxw/2026-09-01/doc-iniqitru8344921.shtml"
KUAISHOU_URL = "https://www.prnewswire.com/news-releases/kuaishou-technology-announces-second-quarter-and-interim-2026-unaudited-financial-results-302855081.html"
CAC_URL = "https://www.cac.gov.cn/2026-08/29/c_1789665114197079.htm"
JOMOO_URL = "https://finance.sina.com.cn/tech/roll/2026-08-25/doc-inipnyqu1608594.shtml"
CHEERS_URL = "https://tech.cheaa.com/2026/0825/657819.shtml"


def main():
    os.makedirs(WORK, exist_ok=True)
    for key, path in PATHS.items():
        backup = os.path.join(WORK, f"bak_{key}_before_r8.json")
        if not os.path.exists(backup):
            shutil.copyfile(path, backup)

    macro = load(PATHS["macro"])
    platform = load(PATHS["platform"])
    policy = load(PATHS["policy"])
    monthly = load(PATHS["monthly"])
    sources = load(PATHS["sources"])
    doudian = load(PATHS["doudian"])
    counts = {"macro": 0, "platform": 0, "policy": 0, "merchant": 0}

    counts["macro"] += add_unique(macro["realEstate"]["pricing"], [{
        "metric": "70个大中城市商品住宅价格（7月）",
        "period": "2026年7月",
        "value": "新房环比上涨17城、持平6城、下降47城；二手房上涨5城、持平3城、下降62城",
        "yoy": "新房仅4城上涨；二手房70城全部下降",
        "source": "国家统计局",
        "publishDate": "2026-08-17",
        "url": NBS_70_URL,
        "note": "住房价格继续分化承压，二手房价格弱势抑制存量房装修预算释放。"
    }], ("metric", "period"))
    counts["macro"] += add_unique(macro["realEstate"]["sales"], [{
        "metric": "上海优化房地产政策（沪八条）",
        "period": "2026-08-21起",
        "value": "外环外二套房商贷最低首付15%；符合条件的以旧换新家庭最高补贴8万元",
        "yoy": "政策调整",
        "source": "上海市住房和城乡建设管理委员会等六部门",
        "publishDate": "2026-08-20",
        "url": SH_HOUSING_URL,
        "note": "降低改善型置换门槛，利好上海存量房翻新、家具家电及整装需求。"
    }, {
        "metric": "完善商品住房销售制度",
        "period": "2026-08-28起",
        "value": "预售项目单体原则上主体结构封顶；新供地项目优先现房销售",
        "yoy": "制度调整",
        "source": "住房城乡建设部、自然资源部、金融监管总局",
        "publishDate": "2026-08-28",
        "url": MOHURD_URL,
        "note": "加强预售资金监管并推动交房即交证，长期提升交付确定性，装修需求释放时点更可预期。"
    }], ("metric", "period"))
    macro["asOf"] = ASOF
    macro["coverage"] = "近30天公开信息窗口：2026-08-11至2026-09-09；宏观统计采用最新可得官方月份。"

    platform_additions = {
        "jd": [{
            "title": "京东MALL秋季家博荟覆盖家具、卫浴、照明与家电，强化设计到送装一站式服务",
            "date": "2026-09-02", "publishDate": "2026-09-02", "category": "家居家装", "type": "营销/线下零售",
            "summary": "京东MALL及京东电器城市旗舰店启动秋季家博荟，覆盖床垫、沙发、卫浴、浴霸和照明；披露9个家具品牌单件95折、指定小区满1万元9折及家装三重补贴最高省15%，并提供设计咨询、空间规划、体验与送装衔接。",
            "source": "新华报业网/交汇点（新浪转载，2026-09-02）", "url": JD_MALL_URL, "firsthand": False
        }],
        "kuaishou": [{
            "title": "快手Q2新商家入驻环比近增10%，免费AI经营工具覆盖超85万商家",
            "date": "2026-08-19", "publishDate": "2026-08-19", "category": "商家生态", "type": "财报/AI经营",
            "summary": "快手公告称二季度新商家入驻量环比增长近10%，入驻后第二个月达到经营规模的商家同比增长近30%；上半年超过85万商家使用免费AI经营工具，全站推广净成交ROI产品渗透率由一季度45%升至二季度55%。",
            "source": "快手科技2026Q2公告（PR Newswire，2026-08-19）", "url": KUAISHOU_URL, "firsthand": True
        }]
    }
    for key, additions in platform_additions.items():
        counts["platform"] += add_unique(platform["platforms"][key], additions, ("title", "date"))
    counts["platform"] += add_unique(platform["crossPlatform"], [{
        "title": "《中国新电商发展报告（2026）》发布，AI经营延伸至内容、营销、客服和供应链",
        "date": "2026-08-29", "publishDate": "2026-08-29", "category": "数智零售", "type": "行业报告",
        "summary": "中国网络社会组织联合会发布报告，总结平台和商家的AI应用已延伸至内容制作、精准营销、智能客服和供应链协同，并关注数智零售、服务零售、直播、农村、二手及适老消费电商。",
        "source": "中国网信网（2026-08-29）", "url": CAC_URL, "firsthand": True
    }], ("title", "date"))
    platform["asOf"] = ASOF
    platform["windowStart"] = WINDOW_START
    platform["windowEnd"] = ASOF
    platform["windowNote"] = "近30天公开动态窗口：2026-08-11至2026-09-09；登录源若未成功更新则明确沿用并披露阻塞。"

    policy_additions = [{
        "title": "住房城乡建设部等三部门完善商品住房销售制度",
        "issueDate": "2026-08-28", "publishDate": "2026-08-28", "effectiveDate": "2026-08-28",
        "issuer": "住房城乡建设部、自然资源部、金融监管总局", "scope": "全国商品住房项目", "category": "房地产/交付",
        "subIndustry": ["房地产", "家装", "家具", "建材"],
        "summary": "预售项目单体建筑原则上须主体结构封顶，购房款全部进入监管账户；新供地及尚未取得建设工程规划许可证的项目优先采用现房销售，并推动交房即交证。",
        "impact": "提升住宅交付确定性，利好装修、家具和建材需求从签约向交付节点更稳定转化。",
        "source": "住房城乡建设部（建房规〔2026〕3号）", "url": MOHURD_URL, "firsthand": True
    }, {
        "title": "商务部等7部门推动商品消费扩容升级，明确推广智能家居与全屋智能改造",
        "issueDate": "2026-08-28", "publishDate": "2026-08-28", "effectiveDate": "2026-08-28",
        "issuer": "商务部等7部门", "scope": "全国商品消费", "category": "促消费",
        "subIndustry": ["家具", "家装", "智能家居", "绿色建材", "家电", "旧家具回收"],
        "summary": "提出培育规范化大型家装企业和平台，发展定制及预约服务，建设体验中心、推动全屋智能改造，完善废旧家具送新收旧，扩大绿色建材应用并推进智能家电家居互联互通和数据接口标准。",
        "impact": "为整装平台、绿色建材、智能家居和送新收旧服务带来政策性需求与标准化机会。",
        "source": "商务部消费促进司（昌吉州商务局全文转载）", "url": COMMERCE_URL, "firsthand": True
    }, {
        "title": "9月1日起家居产品与家装建材电商信息描述等国家标准实施",
        "issueDate": "2026-08-31", "publishDate": "2026-08-31", "effectiveDate": "2026-09-01",
        "issuer": "国家市场监督管理总局、国家标准化管理委员会", "scope": "全国", "category": "国家标准",
        "subIndustry": ["家居产品", "家装建材", "家用电器", "电商标准"],
        "summary": "自9月1日起实施的标准包括GB/T 47600.3—2026《电子商务交易产品信息描述 第3部分：家居产品》、GB/T 47600.4—2026《第4部分：家装建材》，以及家电健康、节能环保规范。",
        "impact": "平台商品信息字段、商家素材与家电健康节能宣称需同步校准，降低描述缺失和不一致风险。",
        "source": "国家市场监督管理总局（2026-08-31）", "url": SAMR_URL, "firsthand": True
    }]
    counts["policy"] += add_unique(policy["policy"], policy_additions, ("title", "issueDate"))
    counts["policy"] += add_unique(policy["industry"], [{
        "title": "2026家具家居双展9月在上海启幕，3200余家品牌参与",
        "date": "2026-09-01", "publishDate": "2026-09-01", "topic": "展会/新渠道", "issuer": "中国国际家具展、Maison Shanghai",
        "summary": "两展于9月7日至11日在上海浦东两馆举行，预计超过3200家品牌参展、总面积35万平方米；面向买手、私域团长、达人和跨境采购的新渠道活动有200余家企业参与。",
        "source": "上观新闻（新浪财经转载，2026-09-01）", "url": FURNITURE_FAIR_URL
    }], ("title", "date"))
    merchant_additions = [{
        "title": "天猫优品与九牧启动年度合作，下沉市场目标销售额1亿元",
        "date": "2026-08-25", "publishDate": "2026-08-25", "category": "渠道", "type": "战略合作", "brand": "九牧/天猫优品",
        "summary": "双方围绕专属产品定制、联合营销、服务升级和下沉渠道拓展展开合作；报道明确1亿元为年度销售目标而非投资额，经营结果仍需后续验证。",
        "impact": "卫浴品牌借零售网络下沉，平台店主获得专供货盘与服务能力。",
        "source": "艾肯家电网（新浪科技转载，2026-08-25）", "url": JOMOO_URL, "firsthand": False
    }, {
        "title": "芝华仕京东超级品牌日全渠道成交额同比增长超8倍",
        "date": "2026-08-25", "publishDate": "2026-08-25", "category": "家具", "type": "营销战报", "brand": "芝华仕",
        "summary": "京东口径显示活动期全渠道成交额同比增长超过8倍、线下成交额接近5倍，两场直播累计观看超过30万人次；数据为平台自报，未见独立审计。",
        "impact": "软体家具通过线上流量、线下体验、送装和以旧换新组合，验证全渠道爆发路径。",
        "source": "中国家电网（稿源京东，2026-08-25）", "url": CHEERS_URL, "firsthand": False
    }]
    counts["merchant"] += add_unique(policy["merchant"], merchant_additions, ("brand", "date", "type"))
    policy["asOf"] = ASOF
    policy["windowStart"] = WINDOW_START
    policy["windowEnd"] = ASOF
    policy["windowNote"] = "近30天窗口：2026-08-11至2026-09-09；仅收录带来源、发布日期和可访问URL的公开条目。"

    monthly["asOf"] = ASOF
    monthly["monthLabel"] = "2026年9月（自然月至今）"
    monthly["intro"] = "本页聚焦2026年9月1日至9月9日已核实的宏观、平台、政策与商家/行业要闻；8月下旬事项保留在近30天专题数据中。"
    monthly["monthlySummary"] = "9月上旬主线是房地产交付制度与家居电商信息标准开始传导，线下家博与平台全渠道促销同步承接秋季焕新；需求端仍受房价和地产投资下行约束。"
    monthly["highlights"] = {
        "macro": [{"date": "2026-09-08", "title": "前8个月我国货物贸易进出口增长17.6%，外需保持较快增长", "impact": "中", "source": "海关总署数据（中国食品土畜进出口商会统计快报，2026-09-08）", "cat": "外贸", "detail": "前8个月外贸延续较快增长，为家具、家电和建材出口链提供总量支撑；具体到家居子行业仍需等待分品类海关数据。", "url": "https://www.cccfna.org.cn/maoyitongji/tongjikuaibao/ff808081a012a84501a07f9ee55a0cc0.html"}],
        "platform": [{"date": "2026-09-02", "title": "京东MALL秋季家博荟强化家具建材一站式体验与送装承接", "impact": "中", "source": "新华报业网/交汇点（新浪转载，2026-09-02）", "cat": "全渠道", "detail": "活动覆盖家具、卫浴、照明与家电，以品牌折扣、指定小区优惠、家装补贴和设计送装服务推动线下体验到成交闭环。", "url": JD_MALL_URL}],
        "policy": [{"date": "2026-09-07", "title": "家居产品与家装建材电商信息描述国家标准进入实施期", "impact": "高", "source": "泉州市市场监督管理局（2026-09-07）", "cat": "标准实施", "detail": "监管部门汇总确认GB/T 47600.3—2026家居产品、GB/T 47600.4—2026家装建材电商信息描述标准已于9月1日起实施，平台与商家应检查商品信息字段和宣称一致性。", "url": QUANZHOU_URL}],
        "merchant": [{"date": "2026-09-01", "title": "3200余家品牌齐聚上海家具家居双展，新渠道与数字获客受关注", "impact": "中", "source": "上观新闻（新浪财经转载，2026-09-01）", "cat": "展会/渠道", "detail": "双展总面积35万平方米，面向买手、私域团长、达人和跨境采购的新渠道活动有200余家企业参与，显示品牌获客继续向内容化、私域化与跨境化延伸。", "url": FURNITURE_FAIR_URL}]
    }
    for group, items in monthly["highlights"].items():
        for item in items:
            if not isinstance(item, dict) or set(item) != {"date", "title", "impact", "source", "cat", "detail", "url"}:
                raise SystemExit(f"monthly highlight schema error: {group}")

    doudian["carryForward"] = True
    doudian["carryForwardNote"] = "2026-09-09已用本机夸克打开抖店罗盘类目概览，授权状态有效且页面可进入；自动读取仅得到页面框架、日期2026/09/02-09/08及筛选项，核心指标区显示empty，未能核实新数值，因此沿用2026-08-13已核实数据，不改写指标。"
    doudian["loginMethod"] = "授权浏览器·授权状态有效（2026-09-09复核）"
    doudian["scrapeMethod"] = "本机夸克自动化复核；本轮核心指标区empty，沿用上次已核实数据"

    sources["asOf"] = ASOF
    for source in sources["sources"]:
        if source.get("name", "").startswith("国家统计局"):
            source.update(timestamp=ASOF, count="30项指标", blocker="无阻塞。本轮补充7月70城房价与1-7月房地产市场官方数据；8月全国房地产与社零数据尚未发布。")
        if source.get("name", "").startswith("抖店罗盘·类目概览"):
            source.update(login="已登录（夸克复核）", timestamp=ASOF, blocker="2026-09-09授权访问有效，页面显示日期2026/09/02-09/08；自动读取核心指标区为empty，无法核实新值，故沿用2026-08-13已核实数据并明确标记carryForward。")
    sources["sources"].append({
        "name": "2026-09-09近30天公开源增量（住建部/商务部/市场监管总局/平台与行业媒体）",
        "layer": "A", "url": MOHURD_URL, "login": "免登录", "depth": 3,
        "count": f"新增{sum(counts.values())}条结构化记录+4条9月亮点", "timestamp": ASOF,
        "blocker": "拼多多官方IR与京东部分财报正文抓取受限，未采用未核实数字；抖店罗盘新周期指标区empty，沿用旧值。"
    })
    depths = [int(s.get("depth", 0)) for s in sources["sources"]]
    summary = sources.setdefault("summary", {})
    summary.update({
        "totalSources": len(sources["sources"]),
        "depth3": depths.count(3), "depth2": depths.count(2), "depth1": depths.count(1), "depth0_blocked": depths.count(0),
        "publicItemsCollected": f"本轮新增{sum(counts.values())}条近30天结构化记录，并重置4组9月自然月至今亮点各1条。",
        "newThisRound": "2026-09-09刷新：补充70城房价、上海房地产优化、商品住房销售制度、商品消费扩容、家居/家装建材电商信息标准、京东MALL秋季家博、快手AI经营、家具双展及九牧/芝华仕渠道动作。",
        "blockedNote": "抖店罗盘授权访问有效，但2026/09/02-09/08类目概览核心指标区显示empty，无法核实新值，沿用2026-08-13数据；拼多多IR与京东部分财报正文访问失败，未录入未核实指标。"
    })

    for record in policy["policy"]:
        if not isinstance(record.get("subIndustry"), list):
            raise SystemExit(f"policy.subIndustry must be list: {record.get('title')}")

    for key, obj in (("macro", macro), ("platform", platform), ("policy", policy), ("monthly", monthly), ("sources", sources), ("doudian", doudian)):
        save(PATHS[key], obj)

    print("R8_COUNTS", json.dumps(counts, ensure_ascii=False))
    print("R8_TOTAL", sum(counts.values()))
    print("DOUDIAN_CARRY_FORWARD", doudian["carryForward"], doudian["carryForwardNote"])


if __name__ == "__main__":
    main()
