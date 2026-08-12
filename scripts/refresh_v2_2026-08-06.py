# -*- coding: utf-8 -*-
"""刷新 v2 专属数据 2026-08-06：
- monthly_highlights.json -> 切换自然月至 2026年8月(08-01至今)，注入本月已核实要闻，更新 monthlySummary/monthLabel
- data_sources_index.json -> 逐源更新本周采集深度/时间戳/阻塞原因
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
ASOF = "2026-08-06"

def load(p):
    with open(os.path.join(D, p), encoding="utf-8") as f:
        return json.load(f)
def save(p, obj):
    with open(os.path.join(D, p), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    print("saved", p)

# ---------- monthly_highlights.json ----------
mh = load("v2/monthly_highlights.json")
mh["asOf"] = ASOF
mh["monthLabel"] = "2026年8月（自然月：2026-08-01 至 2026-08-06）"
mh["intro"] = ("本区块聚焦当前自然月（8月）内发生的高优先级信号，独立于近30天滚动窗口，供管理层快速把握本月最新动向。"
 "8月上旬(截至08-06)以7月月度经济/景气读数集中释放为主，头部商家正式中报将于8月中下旬密集披露，届时二次补充。"
 "共 4 个维度：宏观数据、平台大事、政策标准、头部商家。")
mh["highlights"] = {
 "macro": [
  {"date":"2026-07-31","title":"7月PMI全面回落：制造业49.2%、建筑业47.0%，需求端先行指标走弱",
   "detail":"国家统计局7月31日发布：制造业PMI 49.2%(环比-1.1pt)、非制造业商务活动49.0%(-1.2pt)、综合PMI产出49.3%(-1.3pt)，四大指数环比全部下滑并处临界点下方；与家装建材需求高度相关的建筑业商务活动指数47.0%(-2.0pt)明显走弱，预示三季度开局施工与竣工端仍承压。",
   "impact":"高","url":"https://www.stats.gov.cn/sj/zxfb/202607/t20260731_1964253.html","source":"国家统计局","cat":"建材"},
  {"date":"2026-08-03","title":"1-7月百强房企销售1.80万亿，降幅连续五个月收窄",
   "detail":"中指研究院：TOP100房企1-7月销售总额18042.1亿元，同比仍降但降幅较1-6月收窄0.6pct(连续第五个月收窄)；前五保利1500亿/中海1494.6亿/华润1306亿/招商1098.6亿/绿城1070亿；千亿房企5家、百亿房企39家(同比减10家)。房企端边际企稳有望缓慢传导至竣工与精装配套需求。",
   "impact":"中","url":"https://www.cls.cn/detail/2444122","source":"中指研究院(财联社转载)","cat":"装修"},
  {"date":"2026-08-01","title":"7月百城房价：新房环比+0.26%微涨、二手房-0.44%续跌",
   "detail":"中指研究院8月1日发布：百城新建住宅均价17229元/㎡(环比+0.26%、同比+2.09%)，杭州/成都等为上涨主力；百城二手住宅均价12584元/㎡(环比-0.44%，跌幅较上月扩大0.02pct)。新房结构性回暖对新房精装/整装是弱支撑，二手房续跌则压制二次装修与局部翻新需求。",
   "impact":"中","url":"https://finance.sina.com.cn/jjxw/2026-08-01/doc-inikumqh8984172.shtml","source":"中指研究院(新浪财经转载)","cat":"装修"},
  {"date":"2026-08-03","title":"7月建材工业景气指数MPI 95.3点，环比降6.0点续处非景气区间",
   "detail":"中国建筑材料联合会：7月MPI 95.3点(环比-6.0)，生产指数96.3(-6.2)、投资需求指数94.9、工业消费96.2、国际贸易97.1均低于临界点；投资需求今年累计同比约-10%。7月季节性回落，多数指标环比下滑但同比仍高于去年同期，建材上游景气偏弱。",
   "impact":"中","url":"http://wap.sasac.gov.cn/n16582853/n16582898/c35725911/content.html","source":"中国建筑材料联合会","cat":"建材"},
 ],
 "platform": [
  {"date":"2026-08-05","title":"京东MALL启动『冷风暖水秋季家装节』，抢占818后舒适家赛道",
   "detail":"京东MALL/京东电器城市旗舰店8月8日至9月14日开展『家气候定制·冷风暖水秋季家装节』：中央空调『999元/风口』一口价(较市场价约降30%)、3匹机型低至3699元，配『十免』增值服务(量房/设计/送货/打孔/调试等)；全屋整装套餐性价比款36999元、高端款68999元；品牌含3M/菲斯曼/海尔/松下/怡口等。京东继续以整装+舒适家系统切入家装存量翻新市场。",
   "impact":"中","url":"https://m.sohu.com/a/1059103866_121002798","source":"搜狐(IT168同步报道佐证)","cat":"装修"},
 ],
 "policy": [
  {"date":"2026-08-01","title":"8月1日起一批国家标准实施，含甲醛单位产品能耗限额GB 46029-2025",
   "detail":"新华社梳理8月1日起实施的一批国标：强制性国标《甲醛 单位产品能源消耗限额》(GB 46029-2025)规定甲醛(人造板/胶黏剂主要原料)生产能耗等级与限定值，将从上游抬高高耗能产能成本、利好合规大厂；《家用太阳能热水系统能效限定值及能效等级》(GB 26969-2025)同步实施。该批以能耗/绿色发展为主，非家具/卫浴/照明产品安全类新国标，对终端家居直接相关度有限。",
   "impact":"中","url":"https://www.news.cn/politics/20260731/b4873b5e832f4ce1b69b261bc65bdb52/c.html","source":"新华社","cat":"建材"},
 ],
 "merchant": [
  {"date":"2026-08-06","title":"头部公司2026H1正式中报8月中下旬密集披露，箭牌家居定于08-27",
   "detail":"截至08-06，17家跟踪的头部家居建材公司均未发布正式半年报，正式中报排期集中在8月中下旬(如箭牌家居001322定于2026-08-27披露)。上一期已收录的H1业绩预告(欧派预降50-60%、索菲亚预降78-85%、慕思预降44-51%、志邦预亏、红星美凯龙扭亏、箭牌预亏等)发布于07-14~16，正式财报将验证预告区间并披露分品类/渠道结构，本月要闻届时二次补充。",
   "impact":"中","url":"http://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?stockid=001322&id=12445077","source":"新浪财经(箭牌家居公告)","cat":"家具"},
 ],
}
mh["monthlySummary"] = ("8月上旬(截至08-06)看点集中在7月月度读数：7月PMI全面回落(制造业49.2%、建筑业47.0%)确认需求端先行指标走弱；"
 "中指院显示新房价格结构性微涨(百城环比+0.26%)但二手房续跌(-0.44%)、1-7月百强房企销售降幅连续五个月收窄，房企端边际企稳有望缓慢传导竣工与精装需求；"
 "建材工业景气指数7月MPI 95.3续处非景气区间。平台端京东MALL率先启动『冷风暖水秋季家装节』(08-08~09-14)抢占818后中央空调/舒适家赛道。"
 "政策端8月1日一批国标实施(甲醛能耗限额等，家居间接相关)。头部商家2026H1正式中报将于8月中下旬集中披露(箭牌08-27)，届时本月要闻二次补充。")
save("v2/monthly_highlights.json", mh)

# ---------- data_sources_index.json ----------
si = load("v2/data_sources_index.json")
si["asOf"] = "2026-08-06 11:20"
def upd(match_keys, **kw):
    for s in si["sources"]:
        name = s.get("name","")
        if any(k in name for k in match_keys):
            s.update(kw); return s
    return None
upd(["国家统计局"], depth=3, timestamp="2026-08-06",
    blocker="无。本周补采7月PMI(制造业49.2%/建筑业47.0%,07-31发布);7月社零/工业增加值/房地产投资预计08-15发布,待补。")
upd(["中指研究院","中指院"], depth=2, timestamp="2026-08-06",
    blocker="本周补采7月百城房价(新房+0.26%/二手-0.44%,08-01)与1-7月百强房企销售(18042.1亿,08-03,经财联社转载);完整月报仍需付费。")
upd(["CBMF","建材工业协会","建筑材料"], depth=2, timestamp="2026-08-06",
    blocker="本周补采7月建材工业景气指数MPI 95.3点(08-03,经国资委网转载)。")
upd(["罗盘","compass","抖店"], timestamp="2026-07-30",
    blocker="本周(2026-08-06)为非交互cron刷新,未获章鹏账号新登录态,沿用上期07-30快照;已通过小Q提醒用户按需扫码重采。")
# summary
sm = si.setdefault("summary", {})
sm["totalSources"] = len(si["sources"])
sm["newThisRound"] = ("本周(2026-08-06)以联网公开源补采7月月度增量：国家统计局7月PMI(制造业49.2/建筑业47.0,07-31)、"
 "中指院7月百城房价(08-01)与1-7月百强房企销售(08-03)、中国建材联合会7月建材工业景气指数MPI 95.3(08-03)、"
 "国家统计局7月下旬流通领域建材价格(08-04)、京东MALL秋季家装节(搜狐/IT168,08-05)、新华社8月1日实施国标梳理(07-31)。"
 "强登录源(蝉妈妈/千瓜/京准通/京麦/抖店罗盘)本周为非交互cron刷新未重采,沿用上期数据并标注日期;7月社零/工业增加值/地产投资(约08-15)、"
 "7月BHI、立邦H1、头部公司正式中报(8月中下旬,箭牌08-27)待发布后二次补采。")
# 保留原有的 depth 统计键（若存在则重算 depth0）
from collections import Counter
c = Counter(s.get("depth") for s in si["sources"])
sm["depth3"] = c.get(3,0); sm["depth2"] = c.get(2,0); sm["depth1"] = c.get(1,0); sm["depth0_blocked"] = c.get(0,0)
save("v2/data_sources_index.json", si)

print("\n--- v2 refresh done ---")
print("mh: macro=%d platform=%d policy=%d merchant=%d" % tuple(len(mh["highlights"][k]) for k in ["macro","platform","policy","merchant"]))
print("si: totalSources=%d depth3=%d depth2=%d depth1=%d depth0=%d" % (
    sm["totalSources"], sm["depth3"], sm["depth2"], sm["depth1"], sm["depth0_blocked"]))
