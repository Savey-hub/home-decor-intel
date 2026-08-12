# -*- coding: utf-8 -*-
"""周四刷新 2026-08-06：滚动窗口前移至 近30天(2026-07-07~2026-08-06)。
- 删除掉出窗口(<07-07)/已被更新口径取代的条目
- 注入 2026-07-30 之后联网核实到的新增条目(均带真实URL)
数据铁律：不编造，每条可溯源；无法核实入 gaps。
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
ASOF = "2026-08-06"
WSTART = "2026-07-07"
WEND = "2026-08-06"

def load(p):
    with open(os.path.join(D, p), encoding="utf-8") as f:
        return json.load(f)

def save(p, obj):
    with open(os.path.join(D, p), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    print("saved", p)

# ============ 1) macro_realestate.json ============
m = load("macro_realestate.json")
m["asOf"] = ASOF
m["coverage"] = ("近30天(2026-07-07~2026-08-06)。本期新增：国家统计局7月PMI(07-31发布，制造业49.2%/建筑业47.0%)、"
                 "中指院7月百城房价(08-01)、中指院1-7月百强房企销售(08-03)、7月下旬流通领域建材价格(08-04)、"
                 "中国建材联合会7月建材工业景气指数MPI 95.3(08-03)。6月/1-6月社零、工业增加值、房地产投资/新开工/竣工"
                 "仍为最新官方口径(07-15发布)且落在近30天窗口内予以沿用；7月社零/工业增加值/房地产投资预计08-15前后发布，"
                 "届时二次补采(见gaps)。6月PMI、6月CBMI、7月上旬建材价格因已被7月口径取代或滚出窗口而移除。")

# supplyChain: 移除6月PMI(06-30)、6月CBMI(07-03)、7月上旬价格；保留7月15日口径与待核实项
sc = m["macro"]["supplyChain"]
sc = [x for x in sc if not (str(x.get("publishDate","")) < WSTART and str(x.get("publishDate","")).startswith("2026"))]
sc = [x for x in sc if "上旬" not in str(x.get("period",""))]
sc += [
 {"metric":"制造业PMI","period":"2026年7月","value":"49.2%","yoy":"环比-1.1个百分点(临界点下方)",
  "source":"国家统计局/中国物流与采购联合会","url":"https://www.stats.gov.cn/sj/zxfb/202607/t20260731_1964253.html",
  "publishDate":"2026-07-31","note":"四大分类指数环比全部下滑，制造业景气回落"},
 {"metric":"建筑业商务活动指数","period":"2026年7月","value":"47.0%","yoy":"环比-2.0个百分点",
  "source":"国家统计局","url":"https://www.stats.gov.cn/sj/zxfb/202607/t20260731_1964253.html",
  "publishDate":"2026-07-31","note":"与家装建材需求高度相关的先行指标明显走弱"},
 {"metric":"非制造业商务活动指数","period":"2026年7月","value":"49.0%","yoy":"环比-1.2个百分点",
  "source":"国家统计局","url":"https://www.stats.gov.cn/sj/zxfb/202607/t20260731_1964253.html",
  "publishDate":"2026-07-31","note":"服务业商务活动49.3%(-1.1pt)、新订单44.4%(-3.6pt)"},
 {"metric":"综合PMI产出指数","period":"2026年7月","value":"49.3%","yoy":"环比-1.3个百分点",
  "source":"国家统计局","url":"https://www.stats.gov.cn/sj/zxfb/202607/t20260731_1964253.html",
  "publishDate":"2026-07-31","note":"跌破临界点，企业生产经营总体放缓"},
 {"metric":"建材工业景气指数MPI","period":"2026年7月","value":"95.3点","yoy":"环比-6.0点(非景气区间)",
  "source":"中国建筑材料联合会(经国资委网站转载)","url":"http://wap.sasac.gov.cn/n16582853/n16582898/c35725911/content.html",
  "publishDate":"2026-08-03","note":"生产指数96.3(-6.2)、投资需求指数94.9、工业消费96.2；投资需求今年累计同比约-10%，7月季节性回落"},
 {"metric":"流通领域重要生产资料价格(水泥/浮法玻璃/螺纹钢)","period":"2026年7月下旬",
  "value":"水泥P.O42.5散装246.4元/吨(环比-1.4%)、浮法平板玻璃1098.9元/吨(-0.1%)、螺纹钢3123.4元/吨(-0.8%)",
  "yoy":"环比全线小幅下行","source":"国家统计局(经兰格钢铁网转载)","url":"http://info.lgmi.com/html/202608/04/8735.htm",
  "publishDate":"2026-08-04","note":"7月下旬50种生产资料20涨27降3平，建材上游延续弱势"},
]
m["macro"]["supplyChain"] = sc

# realEstate.sales: 移除<07-07(克而瑞6月/百强口径)，新增百强1-7月
rs = m["realEstate"]["sales"]
rs = [x for x in rs if not (str(x.get("publishDate","")) < WSTART and str(x.get("publishDate","")).startswith("2026"))]
rs.append({"metric":"TOP100房企销售总额(全口径,1-7月累计)","period":"2026年1-7月","value":"18042.1亿元",
  "yoy":"同比仍降，降幅较1-6月收窄0.6pct(连续五个月收窄)","source":"中指研究院(经财联社转载)",
  "url":"https://www.cls.cn/detail/2444122","publishDate":"2026-08-03",
  "note":"前五：保利1500亿/中海1494.6亿/华润1306亿/招商1098.6亿/绿城1070亿；千亿房企5家、百亿房企39家(同比减10家)"})
m["realEstate"]["sales"] = rs

# realEstate.pricing: 移除百城6月(07-03)，新增百城7月新房/二手
rp = m["realEstate"]["pricing"]
rp = [x for x in rp if not (str(x.get("publishDate","")) < WSTART and str(x.get("publishDate","")).startswith("2026"))]
rp += [
 {"metric":"百城新建住宅价格(7月)","period":"2026年7月","value":"均价17229元/㎡，环比+0.26%","yoy":"同比+2.09%",
  "source":"中指研究院(经新浪财经转载)","url":"https://finance.sina.com.cn/jjxw/2026-08-01/doc-inikumqh8984172.shtml",
  "publishDate":"2026-08-01","note":"新房延续结构性上涨(杭州/成都等为主力)"},
 {"metric":"百城二手住宅价格(7月)","period":"2026年7月","value":"均价12584元/㎡，环比-0.44%","yoy":"跌幅较上月扩大0.02pct",
  "source":"中指研究院(经新浪财经转载)","url":"https://finance.sina.com.cn/jjxw/2026-08-01/doc-inikumqh8984172.shtml",
  "publishDate":"2026-08-01","note":"二手房持续承压，二次装修需求偏弱；50城住宅平均租金环比+0.13%/同比-2.62%"},
]
m["realEstate"]["pricing"] = rp

# gaps 更新：移除已被7月口径覆盖的旧gap，追加新gap
gaps = [g for g in m["gaps"] if "07-27~07-30" not in str(g)]
gaps += [
 "7月社会消费品零售总额/工业增加值/房地产开发投资/新开工/竣工面积：国家统计局预计2026-08-15前后发布，本窗口内尚未发布，届时二次补采。",
 "财新中国7月制造业PMI：多次检索未命中2026年7月可访问的溯源页面(caixin正文疑需订阅)，暂不作为正式数据，待核实。",
 "克而瑞7月百强房企单月/累计口径：不同转载表述不一(如操盘口径15918.2亿、同比-14.6%)，需CRIC登录核实，暂以中指院1-7月全口径为准。",
]
m["gaps"] = gaps
save("macro_realestate.json", m)

# ============ 2) platform_dynamics.json ============
p = load("platform_dynamics.json")
p["asOf"] = ASOF; p["windowStart"] = WSTART; p["windowEnd"] = WEND
p["windowNote"] = ("本期为近30天滚动窗口(2026-07-07~2026-08-06)。618大促已滚出窗口；当前处于618与818/暑期家装节之间，"
 "8月初仅京东MALL『冷风暖水秋季家装节』(08-05发布、08-08开闸)为可溯源垂类新动态。天猫88会员节·家装节、抖音818好物节、"
 "微信小店/快手家居类目公告等官方规则页均为JS单页应用，WebFetch无法机读发布日期，相关线索列入gaps待浏览器陪跑核实。")
jd = p["platforms"]["jd"]
jd = [x for x in jd if x.get("date") != "2026-07-03"]  # 京东MALL 30家(07-03)滚出窗口
jd.append({"title":"京东MALL/京东电器城市旗舰店启动『冷风暖水秋季家装节』，中央空调安装费直降约30%",
 "date":"2026-08-05","category":"装修","type":"活动",
 "summary":"8月8日至9月14日开展『家气候定制·冷风暖水秋季家装节』，聚焦中央空调/全屋净水/新风等舒适家居系统：中央空调『999元/风口』一口价(较市场价约降30%)、3匹机型低至3699元；配『十免』增值服务(量房/设计/送货/打孔/调试等)；全屋整装套餐性价比款36999元、高端款68999元；品牌含3M/菲斯曼/海尔/松下/怡口等。",
 "url":"https://m.sohu.com/a/1059103866_121002798","source":"搜狐(IT168 2026-08-05同步报道佐证)"})
p["platforms"]["jd"] = jd
# gaps 追加(去重)
extra_gaps = ["8月初818/暑期家装节：京东818家电家居招商/规则页、天猫88会员节·家装节玩法、抖音818好物节【家居家电】招商规则均为JS单页应用，WebFetch读不到窗口内发布日期，本期未采信，待浏览器陪跑核实。"]
p["gaps"] = list(p.get("gaps", [])) + [g for g in extra_gaps if g not in p.get("gaps", [])]
save("platform_dynamics.json", p)

# ============ 3) industry_policy.json ============
y = load("industry_policy.json")
y["asOf"] = ASOF; y["windowStart"] = WSTART; y["windowEnd"] = WEND
# industry: 追加 CBMF 7月MPI
y["industry"].append({"title":"2026年7月建材工业景气指数MPI 95.3点，环比降6.0点处非景气区间",
 "date":"2026-08-03","topic":"景气指数","issuer":"中国建筑材料联合会",
 "summary":"7月MPI 95.3点(环比-6.0)：价格指数98.9(持平)、生产指数96.3(-6.2)、投资需求指数94.9、工业消费96.2、国际贸易97.1，均低于临界点；投资需求今年累计同比约-10%。7月市场需求季节性回落，多数指标环比下滑但同比仍高于去年同期。",
 "url":"http://wap.sasac.gov.cn/n16582853/n16582898/c35725911/content.html","source":"中国建筑材料联合会(国资委网转载)"})
# policy: 追加 8月1日实施国标(家居间接相关，如实标注)
y["policy"].append({"title":"8月1日起一批国家标准实施(含甲醛单位产品能耗限额GB 46029-2025)",
 "issueDate":"2026-07-31","effectiveDate":"2026-08-01","issuer":"国家市场监管总局/国标委",
 "scope":"全国","category":"国标","subIndustry":"建材上游/绿色能耗",
 "summary":"新华社梳理8月1日起实施的一批国标。与家居建材间接相关：强制性国标《甲醛 单位产品能源消耗限额》(GB 46029-2025)规定甲醛(人造板/胶黏剂主要原料)生产能耗等级与限定值，影响上游成本；《家用太阳能热水系统能效限定值及能效等级》(GB 26969-2025)。该批以能耗/绿色发展为主，非家具/卫浴/照明产品安全类新国标，直接相关度有限。",
 "impact":"中","url":"https://www.news.cn/politics/20260731/b4873b5e832f4ce1b69b261bc65bdb52/c.html","source":"新华社"})
# merchant: 移除<07-07(2条07-06)
mc = y["merchant"]
before = len(mc)
mc = [x for x in mc if not (str(x.get("date","")) < WSTART and str(x.get("date","")).startswith("2026"))]
print("merchant dropped:", before-len(mc))
y["merchant"] = mc
# gaps 追加
extra = [
 "17家头部公司2026H1正式中报：窗口内(07-30~08-06)未见任一家正式披露；A股中报排期集中在8月中下旬(如箭牌家居定于2026-08-27)，届时补采营收/净利终值。",
 "头部公司2026H1业绩预告(欧派/索菲亚/慕思/志邦/红星/箭牌等)发布于07-14~07-16，属上一期已收录，非本窗口新增。",
 "以旧换新/家装消费补贴地方新扩围：本窗口(08-01~08-06)未检索到可核实的新扩围公告(北京07-23/深圳05-22等均在窗口前)。",
 "7月全国建材家居景气指数BHI(CBMCA)、立邦(NPHD)2026H1业绩：预计8月中旬前后发布，本窗口内尚未公布，待核实。",
]
y["gaps"] = list(y.get("gaps", [])) + [g for g in extra if g not in y.get("gaps", [])]
save("industry_policy.json", y)

print("\n--- DONE refresh 2026-08-06 ---")
print("macro: supplyChain=%d sales=%d pricing=%d gaps=%d" % (
    len(m["macro"]["supplyChain"]), len(m["realEstate"]["sales"]), len(m["realEstate"]["pricing"]), len(m["gaps"])))
print("platform: jd=%d gaps=%d" % (len(p["platforms"]["jd"]), len(p["gaps"])))
print("policy: policy=%d industry=%d merchant=%d gaps=%d" % (
    len(y["policy"]), len(y["industry"]), len(y["merchant"]), len(y["gaps"])))
