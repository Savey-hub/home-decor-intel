# -*- coding: utf-8 -*-
"""R14b: merge backend/cninfo/platform audits into dashboard data."""
import json, sys, os, re, collections
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH = r"C:\Users\Savey\.qwenworkcn\workspace\4e65294c-44ea-48f6-b210-5150275eee96"
ASOF = "2026-11-25"
def load(p):
    with open(p, encoding="utf-8") as f: return json.load(f)
def save(p, v):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2); f.write("\n")
def rp(name): return os.path.join(RESEARCH, name)
def norm(s): return "".join(str(s).split()).lower()
def add_unique(items, adds, keys):
    ex = {tuple(norm(x.get(k,"")) for k in keys) for x in items}
    n = 0
    for it in adds:
        k = tuple(norm(it.get(k,"")) for k in keys)
        if k not in ex:
            items.append(it); ex.add(k); n += 1
    return n

platform = load("data/platform_dynamics.json")
policy = load("data/industry_policy.json")
monthly = load("data/v2/monthly_highlights.json")
inv = load("data/v2/url_inventory.json")
sources = load("data/v2/data_sources_index.json")
r_be = load(rp("research_backends.json"))
r_cn = load(rp("research_cninfo.json"))
counts = {}

def dyn(it, cat, typ):
    return {"title": it["title"], "date": it.get("publishDate", ASOF), "publishDate": it.get("publishDate", ASOF),
            "category": cat, "type": typ, "summary": (it.get("summary","") or "")[:200],
            "source": it.get("source",""), "url": it["url"], "firsthand": False}

dy_adds, jd_adds, xhs_adds = [], [], []
for en in r_be["entries"]:
    s = en.get("source","") + en["title"]
    if any(k in s for k in ("抖店大学","年终狂欢季","招商规则","新规速递","罗盘","店铺榜单","蝉妈妈","品牌榜","千川")):
        dy_adds.append(dyn(en, "抖音/平台", "规则与数据"))
    elif any(k in s for k in ("京准通","白皮书","激励","麦头条","规则动态","店铺星级")):
        jd_adds.append(dyn(en, "京东/平台", "规则与工具"))
    elif any(k in s for k in ("种草学","小红书")):
        xhs_adds.append(dyn(en, "小红书", "内容生态"))
counts["platform"] = add_unique(platform["platforms"]["douyin"], dy_adds, ("title","date"))
counts["platform"] += add_unique(platform["platforms"]["jd"], jd_adds, ("title","date"))
counts["platform"] += add_unique(platform["platforms"]["xhs"], xhs_adds, ("title","date"))

mer_adds = [{"brand": en.get("company",""), "date": en.get("publishDate", ASOF), "publishDate": en.get("publishDate", ASOF),
             "type": "三季报披露", "title": en["title"],
             "summary": (en.get("summary","") or "")[:200],
             "impact": "三季报披露确认（巨潮逐家核验）；财务明细需读公告PDF。",
             "url": en["url"], "source": "巨潮资讯网", "firsthand": True} for en in r_cn["entries"]]
counts["merchant"] = add_unique(policy["merchant"], mer_adds, ("title","date"))

mh = {
 "platform": [
  {"date":"2026-11-25","publishDate":"2026-11-25","title":"抖店大学发布《2026年终狂欢季招商规则》：12月大促启动",
   "impact":"高","source":"抖店大学（2026-11-24更新）","cat":"抖音/大促",
   "detail":"报名11/12-12/31、活动12/05-12/31；立减折扣所有类目15%商家出资；体验分≥70准入。","url":"https://school.jinritemai.com/doudian/web/home"},
  {"date":"2026-11-22","publishDate":"2026-11-22","title":"麦头条：店铺星级三维度评定11/25生效，售后新增上门换新/检修",
   "impact":"中","source":"京东麦头条","cat":"京东/规则",
   "detail":"商标失效品牌清退、违规总则第25条同步生效；家装商家合规与服务成本上升。","url":"https://mtt.jd.com/"},
  {"date":"2026-11-24","publishDate":"2026-11-24","title":"抖店罗盘（11/18-11/24）：智能家居家装支付金额较上周期+42.11%，直播占74.45%",
   "impact":"高","source":"抖店罗盘·类目概览","cat":"抖音/品类数据",
   "detail":"支付金额¥1.5亿-¥2亿；件单价+25.48%、客单价+34.92%；智能马桶/摄像头/门锁各占约两成；385元以上价格带占65%-70%。","url":"https://compass.jinritemai.com/shop/chance/category-overview"},
  {"date":"2026-11-25","publishDate":"2026-11-25","title":"蝉妈妈近30天家具建材榜：顾家/全友/源氏木语居前",
   "impact":"中","source":"蝉妈妈品牌榜","cat":"抖音/品牌榜",
   "detail":"顾家28,872,847、全友28,162,489、源氏木语20,172,419、林氏16,838,901、九牧11,485,529（销售指数区间口径）。","url":"https://www.chanmama.com/brandRank/?category_id=7"},
 ],
 "merchant": [
  {"date":"2026-10-31","publishDate":"2026-10-31","title":"13家家装上市公司三季报全部披露完毕（巨潮逐家核验）",
   "impact":"高","source":"巨潮资讯网","cat":"三季报",
   "detail":"欧派/索菲亚/志邦/顾家/慕思/箭牌/东鹏/公牛/欧普/三棵树/惠达/悍高/江河，披露窗口10-23至10-31；志邦亏损已获中诚信关注公告(11-05)。","url":"http://www.cninfo.com.cn/"},
 ],
}
for g, items in mh.items():
    counts["monthly"] = add_unique(monthly["highlights"][g], items, ("title","date"))
def date_of(it):
    m = re.search(r"2026-\d\d-\d\d", str(it.get("date","")))
    return m.group(0) if m else "0000-00-00"
for g in ("macro","platform","policy","merchant"):
    monthly["highlights"][g] = sorted(monthly["highlights"][g], key=date_of, reverse=True)

updates = {
  2:("ok_yield","夸克实测：蝉妈妈无登录墙，切家具建材+近30天，采到TOP50品牌榜区间值。"),
  3:("ok_yield","夸克实测：抖店登录态有效，自动进入商家后台首页。"),
  6:("ok_yield","夸克实测：罗盘登录态有效，采得11/18-11/24类目概览与店铺榜单。"),
  7:("ok_yield","夸克实测：京麦已登录（jiazhuang小店L6），可报名活动55个。"),
  8:("ok_yield","夸克实测：种草学未登录可浏览，采到双11直播课与家居家装讲师。"),
  9:("ok_yield","夸克实测：京准通学堂公开可读，下钻家电家居频道白皮书与激励政策。"),
  10:("need_login_browser","夸克实测：千川帮助框架可开但正文持续报文档权限校验失败；rule-center 404。"),
  4:("need_login_browser","夸克实测：千瓜工作台未登录，仅公开行研列表可见。"),
  56:("ok_empty","夸克实测：千瓜官网正常，纯产品页无行业数据。"),
  53:("ok_yield","夸克实测：抖店大学已登录完全可用，采得年终狂欢季招商规则全文。"),
  30:("ok_yield","夸克实测：麦头条已登录，采得11/16-11/22规则动态全文。"),
  21:("ok_yield","夸克实测：巨潮13家Q3公告逐家搜索命中，标题+日期+链接齐备。"),
  25:("ok_empty","夸克实测：沙利文洞察10-11月无家装专题；高定美学白皮书弱相关。"),
  31:("need_login_browser","夸克实测：三个皮匠家装搜索被登录墙拦截。"),
  32:("ok_empty","夸克实测：发现报告榜单无窗口内家装相关。"),
  36:("ok_empty","夸克实测：慧博首页无直接相关；建材周报为相邻弱相关。"),
  37:("ok_empty","夸克实测：顶级研报热榜/上新/月榜无相关。"),
  46:("ok_empty","夸克实测：QuestMobile双十一洞察间接参考，无家装专题。"),
  47:("ok_empty","夸克实测：亿欧消费生活窗口内仅消费AI硬件一条。"),
  41:("ok_empty","夸克实测：麦肯锡11月洞见无家装；材料展望弱相关。"),
  40:("ok_empty","夸克实测：世界银行纯宏观指标。"),
  43:("noise","夸克实测：微软研究院为AI科研，与家装无关，确认噪声。"),
  44:("noise","夸克实测：英伟达为数据中心产品页，与家装无关，确认噪声。"),
  1:("noise","夸克实测：百度热搜为航天/流感/社会新闻，确认噪声入口。"),
  29:("dead","夸克实测：微信文档被登录墙拦截，仅显示企业身份登录。"),
  11:("ok_empty","夸克实测：飞书wiki可公开访问，为抖音电商方法论文档，窗口外无家装内容。"),
  12:("ok_empty","夸克实测：飞书wiki可公开访问，全域经营图书馆，7-16后未更新。"),
  5:("need_login_browser","夸克实测：飞瓜Plus仍需登录+会员。"),
  49:("ok_empty","夸克实测：沙利文主站无窗口内家装内容。"),
  35:("ok_empty","夸克实测：艾瑞报告库窗口内无家居专项新报告。"),
}
labels = {"ok_yield":"夸克核验完成·取得有效内容","ok_empty":"夸克核验完成·本轮无有效新增",
          "need_login_browser":"登录或权限门槛未通过","dead":"链接失效/域名拦截·已确认","noise":"噪声源·已剔除"}
for item in inv["urls"]:
    uid = item["id"]
    if uid in updates:
        v, concl = updates[uid]
        item["status"] = v
        item["testResult"] = {"testedAt": ASOF, "verdict": v, "verdictLabel": labels[v],
                              "yielded": v == "ok_yield", "conclusion": concl, "round": 14, "method": "浏览器核验 (Quark)"}
sc = collections.Counter(i.get("status","?") for i in inv["urls"])
inv["auditSummary"] = {"testedAt": ASOF, "statusCounts": dict(sorted(sc.items())),
    "note": "Round 14b补跑：全部57入口均在夸克实际访问核验（含登录后台、研报平台、巨潮、噪声源）；罗盘/蝉妈妈/抖店大学/麦头条/京准通/京麦/巨潮取得有效内容。",
    "yieldedCount": sc.get("ok_yield", 0)}

for s in sources["sources"]:
    n = s.get("name","")
    if "蝉妈妈" in n: s.update({"depth":3,"timestamp":ASOF,"count":"Round 14b已复核","blocker":"近30天TOP50品牌榜快照。"})
    elif "罗盘" in n: s.update({"depth":3,"timestamp":ASOF,"count":"Round 14b已复核","blocker":"11/18-11/24类目概览+店铺榜单。"})
    elif "抖店大学" in n: s.update({"depth":3,"timestamp":ASOF,"count":"Round 14b已复核","blocker":"年终狂欢季招商规则全文。"})
    elif "麦头条" in n: s.update({"depth":3,"timestamp":ASOF,"count":"Round 14b已复核","blocker":"11/16-22规则动态全文。"})
    elif "京准通" in n: s.update({"depth":3,"timestamp":ASOF,"count":"Round 14b已复核","blocker":"家电家居广告白皮书+激励政策。"})
    elif "巨潮" in n: s.update({"depth":3,"timestamp":ASOF,"count":"Round 14b已复核","blocker":"13家Q3公告逐家核验。"})
sources["summary"]["newThisRound"] = "Round 14b：抖店罗盘11/18-24快照(+42.11%)、蝉妈妈TOP50、抖店年终狂欢季招商规则、麦头条规则、京准通白皮书、巨潮13家Q3、研报平台14源审计。"

for p, o in (("data/platform_dynamics.json",platform),("data/industry_policy.json",policy),
             ("data/v2/monthly_highlights.json",monthly),("data/v2/url_inventory.json",inv),
             ("data/v2/data_sources_index.json",sources)):
    save(p, o)
print("R14B_COUNTS", json.dumps(counts))
print("inventory yielded", sc.get("ok_yield", 0))
