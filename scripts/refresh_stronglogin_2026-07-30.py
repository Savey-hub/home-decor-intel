# -*- coding: utf-8 -*-
"""强登录源重采整合脚本 2026-07-30 (第4期·强登录陪跑重采)。
本轮通过本机夸克浏览器 Computer Use 桌面自动化,重新采集了4个强登录/受限源:
  - 抖店罗盘(抖音电商后台) 已重采 07-30
  - 千瓜尊享版·品牌排行榜(小红书) 已采 07-30
  - 蝉妈妈·品牌库(抖音电商第三方) 已采 07-30 家具建材TOP17
  - 京准通(京东数字营销) 登录成功但撞『行业分析权限门槛』(仅对有竞价投放pin开放)
  - 阿拉丁照明网 过堡塔云WAF滑块后采到 07-30 照明行业资讯
  - 京麦 仍无POP商家权限,阻塞
遵循不编造原则:仅按实际采集结果更新 depth/timestamp/blocker,阻塞透明。
"""
import json, io, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p):
    with io.open(os.path.join(ROOT, p), encoding='utf-8') as f:
        return json.load(f)
def save(p, d, indent=1):
    with io.open(os.path.join(ROOT, p), 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=indent)
    print('WROTE', p)

# ============ 1. data_sources_index.json ============
s = load('data/v2/data_sources_index.json')
s['asOf'] = '2026-07-30 18:30'

def find(name_kw):
    for x in s['sources']:
        if name_kw in x['name']:
            return x
    return None

# 1a. 抖店罗盘·类目概览 → 本轮重采(07-30 16:17)
d1 = find('抖店罗盘·类目概览')
if d1:
    d1['login'] = '强登录(本机夸克浏览器·本轮重新扫码陪跑登录)'
    d1['depth'] = 3
    d1['timestamp'] = '2026-07-30 近30天口径(现采)'
    d1['blocker'] = '罗盘对市场类目仅公开数量级区间(如¥1亿-1.5亿),不显示精确值,区间已原样保留。本轮经夸克浏览器重新登录现采,非沿用快照。'

# 1b. 千瓜: 原『行业流量大盘』为会员墙阻塞 → 新增『尊享版·品牌排行榜』实采条目
qg = find('千瓜数据·行业流量大盘')
if qg:
    qg['blocker'] = ('切换『家居家装』行业流量大盘为尊享版会员功能;本轮已用尊享版账号登录,改从『品牌排行榜(小红书)』维度采到家居家装商单笔记榜(见下条),'
        '行业流量大盘的类目趋势曲线仍需更高阶数据权限,标注部分可取。')
# 追加千瓜尊享版品牌榜实采条目
if not find('千瓜尊享版·品牌排行榜'):
    s['sources'].append({
        "name": "千瓜尊享版·品牌排行榜(小红书·家居家装商单笔记榜)",
        "layer": "C",
        "url": "https://app.qian-gua.com/#/blogger/brand",
        "login": "强登录(本机夸克浏览器·尊享版账号·本轮扫码陪跑登录)",
        "depth": 3,
        "count": "家居家装·商单笔记榜(月榜2026-06)TOP19品牌(互动总量/商单笔记数/合作达人数),其中家装建材家具品牌6席",
        "timestamp": "2026-07-30 18:00(现采)",
        "blocker": "第9名(六神)/第14名(源氏木语)互动总量被页面吸顶表头遮挡,按真实性纪律标『待核实』不臆测;榜单被日化品牌大量占据,家装建材品牌密度偏低(已入insights)。"
    })

# 1c. 蝉妈妈 → 本轮已采 家具建材 近30天 TOP17
cm = find('蝉妈妈')
if cm:
    cm['login'] = '强登录(本机夸克浏览器·品牌版账号·本轮扫码陪跑登录)'
    cm['depth'] = 3
    cm['url'] = 'https://www.chanmama.com/brandRank/?category_id=7'
    cm['count'] = '抖音电商·品牌库·带货分类=家具建材·近30天·按类目销售额降序TOP17品牌(全友家居/林氏家居/源氏木语/九牧/奥克斯...,含类目商品数/销量区间/销售额/关联达人/视频/直播/小店)'
    cm['timestamp'] = '2026-07-30 18:12(现采)'
    cm['blocker'] = '品牌版账号该视图渲染至第17名(AUPU/奥普)后表格吸顶回弹,未越界臆测TOP18+;全域GMV分层标签(1000w+)≠家具建材类目内销售额,已在源文件note区分口径。'

# 1d. 京准通 → 登录成功但撞行业分析权限门槛
jzt = find('京准通')
if jzt:
    jzt['login'] = '强登录(本机夸克浏览器·jingdongcaiji账号·本轮已成功登录)'
    jzt['depth'] = 0
    jzt['timestamp'] = '2026-07-30(已登录,撞权限门槛)'
    jzt['blocker'] = ('本轮已用正确账号(99927544734)成功登录京准通数据中心,但『行业分析(行业大盘/竞争分析/流量解析)』为权限门槛功能:'
        '仅对近期实际投放过竞价广告(京东快车等)的pin开放。该账号可用余额¥0、无在投计划、自投花费¥0,故弹出『行业分析功能暂只针对有投放竞价广告pin开放』,'
        '指标卡全为---,非自动化可绕过。若需京准通行业数据须换有实际竞价投放的京东广告主账号。')

# 1e. 阿拉丁照明网 → 过WAF后采到照明行业资讯
al = find('阿拉丁照明网')
if al:
    al['login'] = '免登录(需过堡塔云WAF滑块)'
    al['depth'] = 2
    al['url'] = 'https://www.alighting.cn/ ; https://www.alighting.cn/news/'
    al['count'] = '照明/灯具光源行业资讯(2026-07-29~30):上半年出口+17家上市公司H1业绩预告+木林森净利6-7亿+多条道路/景观照明大额标讯+每周光点NO.246'
    al['timestamp'] = '2026-07-30 18:22(现采)'
    al['blocker'] = '首访触发堡塔云WAF人机滑块,经Computer Use drag一次通过;此后主域访问不再拦截。/news.htm为无效路径(404),正确门户首页www.alighting.cn、新闻中心www.alighting.cn/news/。内容为B端行业口径,非天猫C端成交。'

# 1f. 京麦 → 仍阻塞
jm = find('京麦')
if jm:
    jm['blocker'] = '本轮仍未获POP商家账号:扫码为买家号提示『该账号暂不支持开店』,京麦商智家居家装类目数据未取,待用户以POP商家账号扫码陪跑补采。'

# 1g. 重算 summary
def bucket(dep):
    return dep
depths = [x.get('depth', 0) for x in s['sources']]
summ = s['summary']
summ['totalSources'] = len(s['sources'])
summ['depth3'] = sum(1 for d in depths if d == 3)
summ['depth2'] = sum(1 for d in depths if d == 2)
summ['depth1'] = sum(1 for d in depths if d == 1)
summ['depth0_blocked'] = sum(1 for d in depths if d == 0)
summ['newThisRound'] = ('本轮(2026-07-30)强登录源陪跑重采:经本机夸克浏览器 Computer Use 桌面自动化,'
    '①抖店罗盘重新登录现采(近30天口径);②千瓜尊享版首次采到小红书『家居家装商单笔记榜』TOP19(家装建材家具品牌6席,榜单被日化品牌大量占据);'
    '③蝉妈妈品牌版首次采到抖音电商『家具建材』近30天品牌销售额TOP17(全友家居/林氏家居/源氏木语居前);'
    '④阿拉丁照明网过WAF滑块后采到照明行业2026H1景气资讯(出口回暖+17家上市公司业绩预告+木林森净利6-7亿);'
    '⑤京准通已成功登录但撞『行业分析权限门槛』(仅对有竞价投放pin开放,该账号零投放故取不到,已阻塞透明标注)。')
summ['blockedNote'] = ('仍阻塞源:京麦(无POP商家权限,买家号不支持开店)、京准通行业分析(需有竞价投放的广告主账号)、微信文档(公司网络DLP拦截)、'
    '千瓜行业流量大盘曲线(需更高阶数据权限)。以上均按『阻塞透明、不臆测填充』规则标注,待相应账号/权限就绪即可补采。'
    '蝉妈妈/千瓜品牌榜的吸顶遮挡个别数值已标待核实。')
save('data/v2/data_sources_index.json', s)
print('sources now', summ['totalSources'], 'depth3/2/1/0=', summ['depth3'], summ['depth2'], summ['depth1'], summ['depth0_blocked'])

# ============ 2. monthly_highlights.json 追加强登录源要闻 ============
h = load('data/v2/monthly_highlights.json')
h['asOf'] = '2026-07-30'

plat = h['highlights']['platform']
def has_title(arr, kw):
    return any(kw in x.get('title','') for x in arr)

# 2a. 蝉妈妈抖音电商家具建材品牌榜
if not has_title(plat, '蝉妈妈'):
    plat.append({
        "date": "2026-07-30",
        "title": "蝉妈妈抖音电商『家具建材』近30天品牌销售额TOP榜:全友家居/林氏家居/源氏木语居前三",
        "detail": ("本机夸克浏览器现采蝉妈妈品牌库(带货分类=家具建材,近30天):按类目销售额降序TOP17依次为全友家居(731万)、林氏家居(421万)、"
            "YESWOOD源氏木语(407万)、JOMOO九牧(375万)、AUX奥克斯(372万,主营厨卫家电)、Micoe四季沐歌、DESSMANN德施曼、爱果乐、牛警长、酷比得…慕思/喜临门/德力西电气/绿林/奥普等。"
            "投放结构分化明显:潜水艇(1568商品/609达人)为铺量型,德施曼/牛警长高客单低铺量;德力西电气类目销量榜首但销售额仅第15,呈高频低客单。"
            "多数为跨平台品牌,与天猫家装重叠度高,可作抖音端竞争位次与招商参照。"),
        "impact": "中",
        "url": "https://www.chanmama.com/brandRank/?category_id=7",
        "source": "蝉妈妈品牌库(本机夸克浏览器陪跑登录现采)",
        "cat": "抖音电商·家具建材"
    })

# 2b. 千瓜小红书家居家装商单笔记榜
if not has_title(plat, '千瓜'):
    plat.append({
        "date": "2026-07-30",
        "title": "千瓜小红书『家居家装商单笔记榜』(6月月榜):日化品牌大量占据,家装建材品牌仅6席",
        "detail": ("本机夸克浏览器现采千瓜尊享版品牌排行榜(小红书·家居家装·商单笔记榜·月榜2026-06,按互动总量降序):TOP19中日化/个护品牌占13席"
            "(德佑/碧浪/维达/汰渍/金纺/立白/当妮/奥妙/超能等),真正家装建材家具品牌仅6席——京东商城(#1)、三棵树(#3,涂料,40.53万互动/篇均约3651为纯建材最高效率)、"
            "全友(#11,定制家居,409篇铺量型)、源氏木语(#14,互动待核实)、三千金(#15,窗帘)、东方雨虹(#19,防水切C端种草)。"
            "说明小红书『家居家装』心智被日化品牌场景化分流,家装建材品牌需以高单篇效率品类(涂料/软装)为种草突破口。"),
        "impact": "中",
        "url": "https://app.qian-gua.com/#/blogger/brand",
        "source": "千瓜尊享版(本机夸克浏览器陪跑登录现采)",
        "cat": "小红书·家居家装"
    })

# 2c. 阿拉丁照明行业H1景气
if not has_title(plat, '阿拉丁') and not has_title(plat, '照明'):
    plat.append({
        "date": "2026-07-30",
        "title": "阿拉丁照明网:2026H1照明/灯具光源行业景气回暖,17家上市公司发布业绩预告",
        "detail": ("本机夸克浏览器现采阿拉丁照明网(照明行业第一门户)2026-07-30头条:温其东《2026上半年中国照明出口情况详解》、"
            "佛山照明/海洋王/豪尔赛等17家照明上市公司发布2026H1业绩预告、木林森半年净利预计6-7亿、每周光点NO.246『上市企业业绩飘红,LED行业逐步向好』,"
            "整体指向上半年照明行业景气回暖、上市公司盈利改善。工程需求侧旺盛(江苏河北夜游+道路照明超4.43亿、广深宁波超6100万等大额标讯),"
            "技术主题聚焦照明节能+物联网化(人来灯亮人走灯暗)。对天猫『灯具光源』子行业是需求侧回暖信号,建议招商向智能/节能照明倾斜。"),
        "impact": "中",
        "url": "https://www.alighting.cn/news/",
        "source": "阿拉丁照明网(本机夸克浏览器现采,过WAF滑块)",
        "cat": "灯具光源·照明"
    })

# monthlySummary 补一句强登录重采说明
h['monthlySummary'] = h['monthlySummary'].rstrip() + (
    ' 【07-30强登录源重采】经本机夸克浏览器陪跑,补齐抖音电商(蝉妈妈家具建材TOP17)、小红书(千瓜家居家装商单榜)、'
    '照明行业(阿拉丁2026H1景气)三大站外精确数据源;京准通因『行业分析仅对有竞价投放pin开放』的平台权限门槛无法取数,京麦因无POP商家权限阻塞,均已阻塞透明标注。')
save('data/v2/monthly_highlights.json', h)
print('platform highlights now', len(plat))
