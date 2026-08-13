# -*- coding: utf-8 -*-
"""更新 data/v2/data_sources_index.json —— 2026-08-12 期采集源台账。"""
import json
import os
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "v2", "data_sources_index.json")

with open(P, encoding="utf-8") as f:
    si = json.load(f)

si["asOf"] = "2026-08-12 18:00"


def upsert(item):
    for i, x in enumerate(si["sources"]):
        if x["name"] == item["name"]:
            si["sources"][i] = {**x, **item}
            return False
    si["sources"].append(item)
    return True


new = 0
# 更新既有源的本期状态
upsert({
    "name": "国家统计局（社零/工业增加值/房地产/70城房价/PMI）",
    "layer": "A", "url": "https://www.stats.gov.cn/sj/zxfb/", "login": "免登录", "depth": 3,
    "count": "26项指标",
    "timestamp": "2026-08-12",
    "blocker": "无。本期补采7月CPI(+0.5%,居住-0.3%)与7月PPI(+3.5%),均08-09发布,已读CPI正文分项。"
               "7月社零/70城房价/规上工业增加值按统计局发布日程定于2026-08-17,本窗口尚未公布,已入gaps。"
})

# 本期新增源
new += upsert({
    "name": "东方财富·数据中心业绩报表API（RPT_LICO_FN_CPD）",
    "layer": "A",
    "url": "https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_LICO_FN_CPD",
    "login": "免登录",
    "depth": 3,
    "count": "2026H1(REPORTDATE=2026-06-30)家居建材产业链4家已披露公司全字段：营收/同比/归母/同比/基本EPS/扣非EPS/毛利率/每股经营现金流",
    "timestamp": "2026-08-12（现采）",
    "blocker": "无。该接口为结构化财报口径，可直接交叉验证媒体转述；本期即用扣非EPS与基本EPS的背离识别出伟星新材『归母+43.9%但主业承压』。"
})
new += upsert({
    "name": "东方财富·上市公司公告API（security/ann + content/ann）",
    "layer": "A",
    "url": "https://np-anotice-stock.eastmoney.com/api/security/ann",
    "login": "免登录",
    "depth": 3,
    "count": "11家家居建材上市公司08-07~08-12全量公告清单；其中顾家家居2026-052/053、居然智家临2026-044、"
             "惠达卫浴2026-036、箭牌家居2026-034共4份公告读取正文原文并逐字核验关键数字",
    "timestamp": "2026-08-12（现采）",
    "blocker": "无。content/ann 返回公告纯文本，是绕开PDF解析的最可靠正文源。"
               "本期即靠正文推翻了二手渠道『顾家定增致第一大股东摊薄29.44%→26.12%』的错误说法（原文为控股方增持至37.39%）。"
})
new += upsert({
    "name": "海关总署月度进出口（经央视新闻/中国日报网转载）",
    "layer": "A",
    "url": "https://cn.chinadaily.com.cn/a/202608/07/WS6a7555e4a310d709c2fc20a1.html",
    "login": "免登录",
    "depth": 2,
    "count": "1-7月进出口30.13万亿(+17.3%)、出口17.44万亿(+14%)、进口12.69万亿(+22%)；7月单月4.66万亿(+19.2%)",
    "timestamp": "2026-08-07",
    "blocker": "海关总署官网 customs.gov.cn 对应栏目返回504超时，改用央视/中国日报转载页取数，数值口径一致。"
})
new += upsert({
    "name": "中指研究院·中国房地产指数系统（周度成交监测）",
    "layer": "A",
    "url": "https://www.cih-index.com/",
    "login": "免登录",
    "depth": 2,
    "count": "第32周(08-02~08-08)重点城市二手房成交24463套(环比-10.4%/同比+7.8%)、30城新房151万㎡(环比-24.3%/同比+3.4%)、8月累计口径、一线库存环比方向",
    "timestamp": "2026-08-10",
    "blocker": "官网仅提供周度口径与月度价格指数，月度成交量报告需另购/另找入口。"
               "已主动丢弃二手渠道流传的『20城二手7月12.5万套+9.3%、100城新房环比-17%』等无出处月度数值。"
})
new += upsert({
    "name": "京东商家帮助·平台规则中心（learn-jdm.jd.com）",
    "layer": "B",
    "url": "https://learn-jdm.jd.com/knowledge/rule",
    "login": "列表页免登录可读；详情页需商家账号登录",
    "depth": 1,
    "count": "规则更新公示在架9条（含《经营类目商品阈值明细表》生效08-17、《不当使用关键词细则》生效08-19、"
             "《旗舰店商家考核规范》与《招商管理规则》生效08-07）+ 最新公告《家电家居安装、维修业务经营模式调整公告》(08-03)"
             "+ 《规则动态一览（8月3日-8月9日）》",
    "timestamp": "2026-08-12（浏览器渲染后取列表页DOM）",
    "blocker": "深度受限在1：/rule/detail 与 /rule/notice 详情页需POP商家账号登录，正文条款未取到，已记录 ruleId 待陪跑补全。"
               "站内 rule.jd.com 旧域名已301跳转至 learn-jdm.jd.com，且为JS单页应用，WebFetch取不到内容，须用浏览器渲染。"
})
new += upsert({
    "name": "深圳市商务局·政府信息公开（线上国补经营主体名单）",
    "layer": "A",
    "url": "https://commerce.sz.gov.cn/xxgk/qt/tzgg_1/content/post_12930586.html",
    "login": "免登录",
    "depth": 2,
    "count": "2026-08-10公告：公布参与2026年线上家电以旧换新、数码和智能产品购新补贴的经营主体名单，依据商办流通函2025年第469号，明确动态调整",
    "timestamp": "2026-08-10",
    "blocker": "名单明细在附件《经营主体名单.xlsx》中，正文未列具体主体数量与品类范围，附件未下载解析，标注为深度2。"
})
new += upsert({
    "name": "中国新闻网江苏（地方消费券/促消费）",
    "layer": "A",
    "url": "https://www.js.chinanews.com.cn/news/2026/0811/234840.html",
    "login": "免登录",
    "depth": 2,
    "count": "盐城盐都区400万元消费券完整结构：汽车200万/家装家居100万/家电50万/餐饮商圈50万，含面额档位、发放批次(7-20、8-3、8-17、8-31)与商户数",
    "timestamp": "2026-08-11",
    "blocker": "无。"
})

# 汇总
depth = {}
for s in si["sources"]:
    depth[s.get("depth", 0)] = depth.get(s.get("depth", 0), 0) + 1
si["summary"]["totalSources"] = len(si["sources"])
si["summary"]["depth3"] = depth.get(3, 0)
si["summary"]["depth2"] = depth.get(2, 0)
si["summary"]["depth1"] = depth.get(1, 0)
si["summary"]["depth0_blocked"] = depth.get(0, 0)
si["summary"]["publicItemsCollected"] = (
    "约79条(Layer A/B) + 抖店罗盘完整类目盘 + 本期(08-07~08-12)新增39条："
    "上市公司2026H1中报4家全字段财务、重大公告6家(顾家定增/居然智家实控人/惠达出表/箭牌激励作废/欧派现金管理/好莱客私募)、"
    "宏观3项(7月CPI含居住分项、7月PPI、1-7月进出口)、地产2项(中指第32周二手房与30城新房)、"
    "京东规则5项、地方补贴2项(深圳线上国补经营主体白名单、盐城盐都400万消费券)"
)
si["summary"]["newThisRound"] = (
    "本期(2026-08-12)为08-07~08-12的6天增量补采，方法上做了两处升级："
    "一是把上市公司数据源从『媒体转述』切换为东方财富结构化财报API+公告正文API，做到关键数字逐字核验；"
    "二是对JS单页应用(京东规则中心)改用浏览器渲染后取DOM，而非WebFetch。"
    "主动丢弃的未核实线索共4类：顾家定增摊薄比例(与公告原文矛盾)、中指20城/100城月度成交(无出处)、"
    "京东厨房配件/五金工具/浴室柜三条类目调整(详情页需登录、列表页无此标题)、"
    "淘宝天猫七夕礼遇季与88会员节招商稿(页面自标AI生成或三方招商站)。"
    "待补：7月社零/70城房价/规上工业增加值(08-17发布)、7月BHI(约08-15)、"
    "头部公司正式中报(8月中下旬密集披露，箭牌08-27)。"
)
si["summary"]["blockedNote"] = (
    "仍阻塞源：京麦(无POP商家权限)、京准通行业分析(需竞价投放广告主账号)、微信文档(公司网络DLP拦截)、"
    "千瓜行业流量大盘曲线(需更高阶数据权限)、京东规则详情页(需POP商家账号登录)。"
    "强登录源(蝉妈妈/千瓜/抖店罗盘)本期为非交互刷新未重采，沿用上期数据并标注原始日期。"
    "以上均按『阻塞透明、不臆测填充』规则标注。"
)

with open(P, "w", encoding="utf-8") as f:
    json.dump(si, f, ensure_ascii=False, indent=2)

print("sources: %d (new %d) | depth3=%d depth2=%d depth1=%d depth0=%d"
      % (len(si["sources"]), new, si["summary"]["depth3"], si["summary"]["depth2"],
         si["summary"]["depth1"], si["summary"]["depth0_blocked"]))
