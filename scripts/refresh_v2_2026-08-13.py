# -*- coding: utf-8 -*-
"""第6期(2026-08-13) v2 专属数据刷新：
- monthly_highlights.json：monthLabel/自然月窗口推进到08-13，四组各追加08-13新要闻，
  严格保证每项为 dict 且含全部7键 {date,title,impact,source,cat,detail,url}。
- data_sources_index.json：更新asOf与summary计数(本期新增源:微信小店/曲美/江河/北新/南平/武汉/尤溪/CABEE/CBDA)。
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED = {"date", "title", "impact", "source", "cat", "detail", "url"}

def load(p): return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
def save(p, d):
    json.dump(d, open(os.path.join(ROOT, p), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved", p)

# ---------- monthly_highlights ----------
h = load("data/v2/monthly_highlights.json")
h["asOf"] = "2026-08-13"
h["monthLabel"] = "2026年8月（自然月：2026-08-01 至 2026-08-13）"

adds = {
  "merchant": [
    {"date": "2026-08-13",
     "title": "曲美家居把抖音自播带货费率打到平台下限5%：实控人二代『泽龙Z』12个月带货32.44万",
     "impact": "高",
     "source": "上交所/东方财富·曲美家居2026-036号公告(逐字核验)",
     "cat": "软体家具",
     "detail": "曲美家居(603818)08-13披露关联交易公告：实控人赵瑞海之子赵泽龙(抖音『泽龙Z』、公司战略顾问)"
               "过去12个月通过橱窗/直播/巨量星图付费商单为公司带货，累计关联交易32.44万元。关键在费率——"
               "公司抖音精选联盟推广费率2026年3月设为15%，自6月15日起下调至5%(平台可设最低下限)。"
               "这是家居品牌在内容电商『降费率保ROI』、并以实控人二代达人身份深度绑定自播的一个样本。",
     "url": "https://data.eastmoney.com/notices/detail/603818/AN202608121827902904.html"},
    {"date": "2026-08-13",
     "title": "江河集团H1净利+34%叠加中期分红预期，三日累涨超20%触发异动核查",
     "impact": "中",
     "source": "上交所/东方财富·江河集团临2026-037号公告(逐字核验)",
     "cat": "建材",
     "detail": "江河集团(601886)08-13披露股票交易异常波动公告：08-10/11/12连续三日收盘涨幅偏离值累计超20%，"
               "自查无未披露重大事项。催化来自08-12披露的2026H1营收108.24亿(+15.90%)、归母净利4.41亿(+34.34%)"
               "及中期利润分配方案。幕墙/建筑装饰工程端(B端)逆势高增，与地产链零售家居普跌形成鲜明分化。",
     "url": "https://data.eastmoney.com/notices/detail/601886/AN202608121827906108.html"},
  ],
  "platform": [
    {"date": "2026-08-11",
     "title": "818家具战打响：京东家具超级品类日携马頔办『新家发补会』，亿元补贴至高返50%",
     "impact": "中",
     "source": "中企资讯网(京东通稿转载，二手)",
     "cat": "软体家具",
     "detail": "京东家具超级品类日于8月11日晚8点启动(App搜『马頔新家发补会』)：五重礼合计1亿元家装补贴，"
               "含至高返50%装修补贴、国补叠加、PLUS至高再减12%、白条6期免息，活动期每晚8点『1元抢家具』；"
               "参与品牌含顾家、全友、芝华仕、喜临门、慕思、林氏、源氏木语等。二手通稿口径，费率/样品价以商家后台为准。",
     "url": "https://www.zqbao.com.cn/news/18680.html"},
    {"date": "2026-08-10",
     "title": "微信小店重构家具一级类目：8月24日起『商业办公』改名、部分类目关闭迁移",
     "impact": "中",
     "source": "微信小店成长中心·平台公告(腾讯，一手)",
     "cat": "家具",
     "detail": "微信小店公告自2026-08-24起优化一级类目【家具】：二级类目【商业办公】更名为【商业/办公家具】，"
               "存量商品逐步迁移并按新类目管理，08-24起原类目下线、不可再新增商品；并明确家具类目下暂不支持医疗器械相关类目及商家入驻。"
               "视频号/微信小店家具经营者需在08-24前完成类目切换以免影响上架。",
     "url": "https://store.weixin.qq.com/chengzhang/webdoc/wiki/9776/1da454ab33fce4d0/growth_center_platform_notice/1?bpath=%252Fnotice"},
  ],
  "policy": [
    {"date": "2026-08-10",
     "title": "地方国补白名单滚动扩容：福建三明尤溪已到第十七批，湖北武汉第六批同步公示",
     "impact": "中",
     "source": "尤溪县/武汉市商务局(一手)",
     "cat": "全屋智能",
     "detail": "福建尤溪县08-10公示第十七批家电/数码智能/智能家居购新补贴参与企业(线上，含京东家电家居)；"
               "武汉市08-07公示第六批智能家居购新补贴参与主体(线上+线下)。两地均延续『企业申报→区/市两级审核→动态白名单』机制，"
               "显示国补资格从平台级下沉到经营主体级已常态化、并向县域扩面。补贴比例/上限见各地实施细则。",
     "url": "https://www.fjyx.gov.cn/zwgk/gggs/zh/202608/t20260810_2268865.htm"},
    {"date": "2026-07-28",
     "title": "南平细化智能家居补贴口径：新增油烟机/洗碗机等5类，『智能沙发』并入按摩椅不得重复申领",
     "impact": "中",
     "source": "福建省发改委(转南平市商务局公告，一手)",
     "cat": "卫浴厨房",
     "detail": "南平市08-01前后执行的扩围公告：新增数码相机、智能吸油烟机、智能燃气灶(含集成灶)、智能洗碗机、智能干衣机5类，"
               "补贴为最终销售价15%、每人每类限1件、每件≤1500元；并把『智能沙发』并入『智能按摩椅』且不得重复申领。"
               "地方在扩品类的同时收紧执行口径，防止客厅智能家具补贴套利。",
     "url": "http://fgw.fujian.gov.cn/ztzl/dgmsbgxhxfpyjhx/jzqk/202607/t20260728_7192883.htm"},
  ],
  "macro": [
    {"date": "2026-08-13",
     "title": "7月宏观硬数据本周尚未落地：社零/规上工业/70城房价定于08-17、BHI预计08-15",
     "impact": "低",
     "source": "国家统计局发布日程/CBMCA历史节奏",
     "cat": "建材",
     "detail": "截至08-13，7月社会消费品零售总额(含家具类/建筑及装潢材料类)、规上工业增加值、70城住宅销售价格按统计局日程定于2026-08-17发布；"
               "7月全国建材家居景气指数BHI预计08-15前后。本期宏观口径仍以7月PMI、7月CPI+0.5%(居住-0.3%)/PPI+3.5%、前7个月进出口+17.3%、"
               "7月MPI 95.3为准，下期(08-15~08-17)二次补采7月消费与房价硬数据。",
     "url": "https://www.stats.gov.cn/sj/zxfb/"},
  ],
}

for grp, items in adds.items():
    for it in items:
        assert isinstance(it, dict) and set(it.keys()) == REQUIRED, ("BAD ITEM", grp, it.get("title"))
    existing = {(x["date"], x["title"]) for x in h["highlights"][grp]}
    h["highlights"][grp] = [it for it in items if (it["date"], it["title"]) not in existing] + h["highlights"][grp]

# 结构自检：四组内无非dict、7键齐全
for grp in ("macro", "platform", "policy", "merchant"):
    for it in h["highlights"][grp]:
        assert isinstance(it, dict), ("NONDICT", grp, it)
        assert set(it.keys()) == REQUIRED, ("KEYS", grp, sorted(it.keys()))

h["monthlySummary"] = (
    "8月上旬至08-13：家居建材『中报密集披露+818大促季+地方国补滚动扩容』三线并进。中报端结构性分化加剧——"
    "江河集团(建筑装饰/幕墙工程端)H1净利+34%并触发股价异动，与地产链零售家居(慕思/志邦/惠达/金牌预亏预减)形成鲜明对照，"
    "扣非与经营现金流才是真分水岭；欧派、好莱客把闲置资金转向理财/私募，龙头主动收缩资本开支。渠道端818打响家具补贴战："
    "京东家具超级品类日携马頔办『亿元补贴至高返50%』，微信小店重构家具类目(08-24生效)，快手818宠粉节(08-04~08-28)；"
    "曲美家居把抖音自播费率打到平台下限5%，折射内容电商『降费率保ROI』。政策端地方国补白名单滚动扩容(福建三明尤溪第十七批/武汉第六批)、"
    "口径细化(南平『智能沙发』并入按摩椅不得重复申领)，标准端CABEE辐射隔热涂料团标(10-01实施)、CBDA标准管理办法修订(08-11)落地。"
    "宏观硬数据(7月社零/70城房价/规上工业)定于08-17、7月BHI预计08-15，本期尚未公布，下期二次补采。"
)
save("data/v2/monthly_highlights.json", h)

# ---------- data_sources_index ----------
s = load("data/v2/data_sources_index.json")
s["asOf"] = "2026-08-13 12:00"
new_sources = [
  {"name": "微信小店成长中心·平台公告", "layer": "E", "url": "https://store.weixin.qq.com/chengzhang/notice",
   "login": "免登录(公告页)", "depth": 2, "count": "1条(家具类目调整08-24生效)", "timestamp": "2026-08-13",
   "blocker": "SPA页，商家后台明细需登录；公告正文可核。"},
  {"name": "东方财富·上市公司公告(cnotice正文API)", "layer": "A",
   "url": "https://np-cnotice-stock.eastmoney.com/api/content/ann", "login": "免登录", "depth": 3,
   "count": "本期08-13新增4家逐字核验(曲美/江河/北新/雄塑)", "timestamp": "2026-08-13",
   "blocker": "无。作为公告关键数字一手核验通道。"},
  {"name": "东方财富·datacenter中报API(RPT_LICO_FN_CPD)", "layer": "A",
   "url": "https://datacenter-web.eastmoney.com/api/data/v1/get", "login": "免登录", "depth": 3,
   "count": "2026H1(REPORTDATE=2026-06-30)watchlist匹配核验", "timestamp": "2026-08-13",
   "blocker": "无。营收/净利/毛利率/YoY一手取数。"},
  {"name": "福建省发改委/南平·尤溪·三明地方国补公告", "layer": "A",
   "url": "http://fgw.fujian.gov.cn/", "login": "免登录", "depth": 3,
   "count": "南平扩围+尤溪第十七批白名单", "timestamp": "2026-08-13",
   "blocker": "三明市商务局原文一度连接失败，已由同省南平公告佐证。"},
  {"name": "武汉市商务局·国补白名单", "layer": "A", "url": "https://sw.wuhan.gov.cn/",
   "login": "免登录", "depth": 3, "count": "第六批智能家居主体名单", "timestamp": "2026-08-13", "blocker": "无。"},
  {"name": "中国建筑节能协会CABEE/中国建筑装饰协会CBDA", "layer": "A",
   "url": "https://www.cabee.org/ ; http://www.cbda.cn/", "login": "免登录", "depth": 3,
   "count": "辐射隔热涂料团标+CBDA标准管理办法", "timestamp": "2026-08-13", "blocker": "无。"},
]
existing_names = {x["name"] for x in s["sources"]}
for ns in new_sources:
    if ns["name"] not in existing_names:
        s["sources"].append(ns)

# 重新统计summary
depth3 = sum(1 for x in s["sources"] if x.get("depth") == 3)
depth2 = sum(1 for x in s["sources"] if x.get("depth") == 2)
depth1 = sum(1 for x in s["sources"] if x.get("depth") == 1)
depth0 = sum(1 for x in s["sources"] if x.get("depth") == 0)
s["summary"]["totalSources"] = len(s["sources"])
s["summary"]["depth3"] = depth3
s["summary"]["depth2"] = depth2
s["summary"]["depth1"] = depth1
s["summary"]["depth0_blocked"] = depth0
s["summary"]["newThisRound"] = (
    "本期(2026-08-13)为08-12→08-13的1日滚动增量：新增微信小店家具类目公告(一手)、"
    "上市公司08-13公告逐字核验4家(曲美关联交易/江河异动/北新说明会/雄塑减持)、"
    "福建三明尤溪第十七批与武汉第六批国补白名单、CABEE/CBDA团标；东财公告正文API+中报datacenter API作为一手核验主通道。"
)
s["summary"]["blockedNote"] = (
    "仍阻塞：抖音/淘天/拼多多/小红书本窗口无可核验的家装818专项招商规则一手源；"
    "京麦『类目调整公告』详情页登录墙；甘肃省商务厅报道WAF拦截(HTTP 412)；三明市商务局预征集原文连接失败；"
    "内部sale-analyzer工具HTTP 504不可用；抖店罗盘见layerC说明。"
)
save("data/v2/data_sources_index.json", s)
print("sources total=%d depth3=%d depth2=%d depth1=%d depth0=%d" % (len(s["sources"]), depth3, depth2, depth1, depth0))
print("DONE refresh_v2_2026-08-13")
