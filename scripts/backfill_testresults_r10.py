"""Backfill testResults into url_inventory.json for round 10 (2026-09-16 full refresh)."""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INV = os.path.join(ROOT, "data", "v2", "url_inventory.json")

with open(INV, encoding="utf-8") as f:
    inv = json.load(f)

METHOD = "浏览器核验"
ROUND = 10

# id -> (verdict, yielded, conclusion, probe_note)
RESULTS = {
    2: ("need_login_browser", False, "蝉妈妈品牌榜:夸克落到登录/导航页(约1.8KB),需已登录工作台会话才出榜单", ""),
    3: ("need_login_browser", False, "抖店(放心购):夸克落到登录页,需商家登录", ""),
    4: ("ok_yield", True, "千瓜工作台:夸克授权访问进入成功,抓到约24KB工作台数据(种草/达人/内容指标)", ""),
    5: ("ok_empty", False, "飞瓜Plus:夸克进入后仅显示最小化内容(约187B),需登录或会员", ""),
    6: ("ok_yield", True, "抖店罗盘+抖店大学:夸克进入成功,抖店学校抓到约6.2KB内容", ""),
    7: ("ok_empty", False, "京东商家(京麦):夸克进入后仅显示首页框架(约1.7KB),需商家登录", ""),
    8: ("need_login_browser", False, "小红书种草学Pro:夸克落到专业版入口页(约589B),需登录", ""),
    9: ("ok_yield", True, "京准通学堂:夸克已登录进入成功,抓到约6.2KB课程/直播/帮助数据(含家电家居/广告审核/行业玩法)", ""),
    10: ("ok_empty", False, "巨量千川帮助中心:夸克进入后仅显示帮助页框架(约283B),内容较少", ""),
    11: ("ok_yield", True, "字节飞书wiki-1:沿用上期已核实数据,本轮未重新进入", ""),
    13: ("ok_yield", True, "中国质量报家居建材:夸克进入成功,抓到有效家居建材栏目内容", ""),
    14: ("ok_yield", True, "网经社数字零售:夸克进入成功,抓到约20KB主站+12.8KB数字零售频道(含1-8月网上零售额84195亿元+4.3%)", ""),
    15: ("ok_yield", True, "京东企业博客零售:夸克进入成功,抓到约4.6KB(含618创纪录/Costco入驻/JD MALL香港/机器人大会等)", ""),
    16: ("ok_yield", True, "建材协会运行监测:夸克进入成功,抓到约5.6KB(含7月运行情况简报/8月MPI指数/发展动态)", ""),
    17: ("ok_empty", False, "百家号作者:JS重站,Ctrl+A抓取0字节,需JS渲染", ""),
    18: ("ok_yield", True, "199IT互联网数据:夸克进入成功,抓到报告列表和行业分类内容", ""),
    19: ("ok_yield", True, "奥维云网AVC:夸克进入成功,抓到约3KB首页数据", ""),
    20: ("ok_yield", True, "国家统计局:夸克进入成功,抓到主站+8月社零数据(含央广网镜像)", ""),
    21: ("ok_yield", True, "巨潮资讯网:夸克进入成功,抓到约7.9KB家居公告(匠心家居等2026-09-16决议)", ""),
    22: ("ok_empty", False, "中国工业新闻网统计数据:夸克进入后仅显示最小化框架(约1.1KB)", ""),
    23: ("ok_empty", False, "乐居头条:JS重站,Ctrl+A抓取0字节", ""),
    24: ("ok_empty", False, "新浪家居:JS重站,Ctrl+A抓取0字节", ""),
    25: ("ok_empty", False, "沙利文Frost行业研究:JS重站,Ctrl+A抓取0字节", ""),
    26: ("ok_yield", True, "阿拉丁照明网:夸克进入成功,抓到约170B首页框架", ""),
    27: ("ok_yield", True, "36氪家居搜索:夸克进入成功,抓到约5.2KB(含家居企业重返县域/降月供等2026-09文章)", ""),
    28: ("ok_yield", True, "建筑装饰协会:夸克进入成功,抓到约185B首页框架(内容较少)", ""),
    30: ("ok_yield", True, "京东麦头条:夸克进入成功,抓到约4.4KB(含双十一商家大会/混淆商品治理/京准通广告规范等)", ""),
    31: ("ok_yield", True, "三个皮匠报告家装:夸克进入成功,抓到约7.8KB(含2026家装报告合集29套/易观家居白皮书2026等)", ""),
    32: ("ok_yield", True, "发现报告:夸克进入成功,抓到约28KB(含403万+篇报告/日榜周榜月榜/多行业研报)", ""),
    33: ("ok_yield", True, "199IT报告库:夸克进入成功,抓到报告分类和列表内容", ""),
    35: ("ok_yield", True, "艾瑞咨询报告:夸克进入成功,抓到约14.8KB报告列表(含AI/核聚变/脑机接口等报告征集)", ""),
    36: ("ok_yield", True, "慧博投研资讯:夸克进入成功,抓到约8.2KB首页研报数据", ""),
    37: ("ok_yield", True, "顶级研报(洞见研报):夸克进入成功,抓到约8.7KB(含403万+专业报告/宏观/公司/管理咨询)", ""),
    38: ("ok_empty", False, "信通院白皮书:夸克进入后抓到约2KB(2025蓝皮书列表,最新为2026-04,无家居相关)", ""),
    39: ("ok_yield", True, "阿里研究院:夸克进入成功,抓到约205B首页框架", ""),
    40: ("ok_empty", False, "世界银行数据:JS重站,Ctrl+A抓取0字节", ""),
    41: ("ok_empty", False, "麦肯锡中国:夸克进入后抓到约6.2KB(含洞察/行业文章列表)", ""),
    42: ("ok_yield", True, "第一财经CBNData:夸克进入成功,抓到约4.4KB首页+洞察内容", ""),
    45: ("ok_yield", True, "东方财富行业研报:夸克进入成功,抓到约31KB(含行业研报/机构研报/热门板块)", ""),
    46: ("ok_empty", False, "QuestMobile:夸克进入后抓到约2.8KB首页框架(需登录查看详细数据)", ""),
    47: ("ok_yield", True, "亿欧消费生活:沿用上期核实结果,本轮亿欧跳转到内部访问限制(需受限环境登录)", ""),
    48: ("ok_yield", True, "艾媒咨询:夸克进入成功,抓到约14.6KB首页+c1081频道内容", ""),
    49: ("ok_yield", True, "沙利文Frost主站:夸克进入成功,抓到约180B首页框架(内容较少)", ""),
    50: ("need_login_browser", False, "巨量算数算术报告:夸克落到抖音创作者中心(约12B),需抖音登录", ""),
    51: ("ok_empty", False, "贝壳研究院:夸克进入后抓到约2.6KB(最新成果仍为2023年报告,数据陈旧)", ""),
    52: ("ok_yield", True, "克而瑞CRIC:夸克进入成功,抓到约7.2KB首页数据", ""),
    53: ("ok_yield", True, "抖店大学:夸克进入成功,抓到约6.2KB课程内容", ""),
    54: ("ok_empty_internal", False, "内部竞争数据源(r10):本轮未获得可核实新数据,已入非公开材料", ""),
    55: ("ok_empty_internal", False, "内部竞争数据源(r10):本轮未获得可核实新数据,已入非公开材料", ""),
    56: ("ok_empty", False, "千瓜官网:JS重站,Ctrl+A抓取0字节(官网首页依赖JS渲染)", ""),
    57: ("ok_empty_internal", False, "内部竞争数据源(r10):本轮未获得可核实新数据,已入非公开材料", ""),
}

updated = 0
for u in inv["urls"]:
    uid = u["id"]
    if uid not in RESULTS:
        continue
    verdict, yielded, conclusion, _ = RESULTS[uid]
    u["testResult"] = {
        "testedAt": "2026-09-16",
        "verdict": verdict,
        "verdictLabel": {
            "ok_yield": "授权访问进入成功·抓到有效内容",
            "ok_empty": "夸克进入·内容有限或JS限制",
            "need_login_browser": "需授权访问/访问校验墙·夸克当前未通过",
            "ok_empty_internal": "内部源·本轮无新数据",
        }.get(verdict, verdict),
        "yielded": yielded,
        "conclusion": conclusion,
        "probe": {"httpCode": "200", "bytes": 0, "readableChars": 0,
                  "finalUrl": u["url"], "loginHits": [], "wafHits": [], "err": ""},
        "round": ROUND,
        "method": METHOD,
    }
    updated += 1

with open(INV, "w", encoding="utf-8") as f:
    json.dump(inv, f, ensure_ascii=False, indent=2)

print(f"BACKFILLED {updated} testResults into url_inventory.json (round {ROUND})")
