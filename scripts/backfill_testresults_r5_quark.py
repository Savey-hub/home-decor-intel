# -*- coding: utf-8 -*-
"""Round-5 (2026-08-26) Quark-browser re-verification backfill.

The user required EVERY source in url_inventory.json be physically run through the
local Quark browser (夸克, SendInput+scancode), one by one. This script writes the
actual per-source outcome of that run into urls[].testResult (round=5), recomputes
auditSummary, and refreshes the round note.

Iron rule #2: intranet sources (D layer: Rune/魔镜/FBI) — conclusions contain NO
numeric values and only state reachability; their data stays in _work/internal_* only.

Backs up url_inventory.json to _work/bak_url_inventory_before_r5quark.json first.
"""
import json
import os
import shutil
import sys
from collections import Counter

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, '_work')
INV = os.path.join(ROOT, 'data', 'v2', 'url_inventory.json')

LABELS = {
    'ok_yield': '夸克登录态进入成功·抓到有效内容',
    'ok_yield_internal': '夸克进入成功·内网有数据(仅入本地内部件)',
    'ok_empty': '夸克进入成功·仅落地页/导航,无新增结构化数据',
    'ok_empty_internal': '夸克进入成功·内网SSO登录态过期未取数(仅内部件)',
    'partial': '夸克进入成功·登录墙下仅部分可见',
    'dead': '链接失效/域名拦截·已确认',
    'need_login_browser': '需已登录会话/验证码墙·夸克当前未通过',
    'noise': '噪声源·已剔除',
}

# id -> (verdict, yielded, conclusion)  —  from actual 2026-08-26 Quark grabs in _work/quark/
R = {
    1:  ('noise', False, '百度首页,噪声源,夸克抓取315B均为导航,已剔除'),
    2:  ('need_login_browser', False, '蝉妈妈品牌榜:夸克本轮落到登录/导航页(约1.8KB,含登录提示),需已登录工作台会话才出榜单'),
    3:  ('need_login_browser', False, '抖店(放心购):夸克落到登录页(约1.5KB),需商家登录'),
    4:  ('ok_yield', True, '千瓜·工作台:夸克已登录会话进入成功,抓到约24KB工作台数据(种草/达人/内容指标)'),
    5:  ('ok_empty', False, '飞瓜Plus(mktindex):夸克进入返回0B,页面未渲染可抓文本'),
    6:  ('ok_yield', True, '抖店罗盘·类目概览:夸克已登录进入成功,抓到约9.5KB类目概览数据'),
    7:  ('ok_empty', False, '京东商家(京麦):夸克进入约0.6KB,仅框架无业务数据'),
    8:  ('need_login_browser', False, '小红书种草学Pro:夸克落到登录页(约1.1KB,含登录提示)'),
    9:  ('ok_yield', True, '京准通·学堂:夸克进入成功,抓到约5.5KB学堂/投放内容'),
    10: ('ok_empty', False, '巨量千川·帮助中心:夸克进入返回0B,SPA未渲染'),
    11: ('dead', False, '字节飞书wiki-1:夸克进入0B,文档已失效/无权限'),
    12: ('dead', False, '字节飞书wiki-2:夸克进入0B,文档已失效/无权限'),
    13: ('ok_yield', True, '中国质量报·家居建材:夸克进入成功,抓到约2.5KB家居建材质量资讯'),
    14: ('ok_yield', True, '网经社·数字零售快讯:夸克进入成功,抓到约2.2KB零售快讯'),
    15: ('ok_yield', True, '京东企业博客·零售:夸克进入成功,抓到约4.8KB零售洞察'),
    16: ('ok_yield', True, '建材协会·运行监测:夸克进入成功,抓到约2.4KB行业运行监测'),
    17: ('ok_empty', False, '百家号作者-1:夸克进入仅56B,作者主页无可抓正文'),
    18: ('ok_yield', True, '199IT互联网数据资讯:夸克进入成功,抓到约3.8KB数据资讯列表'),
    19: ('ok_yield', True, '奥维云网AVC:夸克进入成功,抓到约1.2KB快讯(landing)'),
    20: ('ok_yield', True, '国家统计局:夸克进入成功,抓到约2.2KB统计条目'),
    21: ('ok_yield', True, '巨潮资讯网:夸克进入成功,抓到约5.5KB上市公司公告(含居然智家/顾家等家居标的公告)'),
    22: ('ok_empty', False, '中国工业新闻网·统计数据:夸克进入约1.1KB,仅栏目导航'),
    23: ('ok_empty', False, '乐居头条:夸克进入约1.2KB,仅栏目导航'),
    24: ('ok_empty', False, '新浪家居:夸克进入约1.2KB,仅栏目导航'),
    25: ('ok_empty', False, '沙利文Frost行业研究:夸克进入约1.6KB,会员墙landing,无正文'),
    26: ('need_login_browser', False, '阿拉丁照明网:夸克进入触发滑动验证(约17B),人机验证墙拦截'),
    27: ('ok_yield', True, '36氪·家居搜索:夸克进入成功,抓到约2.3KB家居频道近期文章(2026-08多篇)'),
    28: ('need_login_browser', False, '建筑装饰协会:夸克进入触发安全验证(约64B),验证墙拦截'),
    29: ('dead', False, '微信文档·表格:夸克进入被DLP域名拦截(约35B),企业安全策略阻断'),
    30: ('ok_yield', True, '京东麦头条(mtt):夸克进入成功,抓到约2.1KB头条内容'),
    31: ('ok_yield', True, '三个皮匠报告:夸克进入成功,抓到约4.3KB家装研报清单(含2026家装年报合集第28期/2026家居家装发展研究报告)'),
    32: ('ok_yield', True, '发现报告:夸克进入成功,抓到约7.9KB研报清单(含人形机器人/AI大模型等,2026-08多份)'),
    33: ('ok_yield', True, '199IT·报告库:夸克进入成功,抓到约2.0KB报告库条目'),
    34: ('dead', False, '百家号作者-2:夸克提示"用户信息不存在",账号失效(约7B)'),
    35: ('ok_yield', True, '艾瑞咨询报告:夸克进入成功,抓到约5.9KB研报清单(含2026消费社媒投放/企业AI转型等,2026-08)'),
    36: ('ok_yield', True, '慧博投研资讯:夸克进入成功,抓到约3.4KB研报资讯'),
    37: ('partial', True, '顶级研报:夸克进入约4.3KB研报列表但含登录提示,仅标题可见'),
    38: ('ok_empty', False, '信通院·白皮书:夸克进入约1.0KB,仅栏目导航'),
    39: ('ok_yield', True, '阿里研究院:夸克进入成功,抓到约4.4KB研究文章列表'),
    40: ('ok_empty', False, '世界银行数据:夸克进入约1.7KB,仅门户导航'),
    41: ('ok_empty', False, '麦肯锡中国:夸克进入约2.3KB,仅门户landing'),
    42: ('ok_yield', True, '第一财经数据CBNData:夸克进入成功,抓到约1.9KB数据栏目'),
    43: ('noise', False, '微软研究院:夸克进入0B,英文站与家装无关,噪声源'),
    44: ('noise', False, '英伟达数据中心:夸克进入0B,英文站与家装无关,噪声源'),
    45: ('ok_yield', True, '东方财富·行业研报:夸克进入成功,抓到约5.8KB行业研报清单'),
    46: ('ok_empty', False, 'QuestMobile:夸克进入约1.4KB,仅门户landing'),
    47: ('ok_yield', True, '亿欧·消费生活报告:夸克进入成功,抓到约4.7KB消费生活研报清单'),
    48: ('ok_yield', True, '艾媒咨询:夸克进入成功,抓到约9.2KB研报清单(含《2026-2027中国智能家居行业发展白皮书》2026-08-25)'),
    49: ('ok_yield', True, '沙利文Frost主站:夸克进入成功,抓到约4.2KB咨询内容'),
    50: ('need_login_browser', False, '巨量算数·算术报告:夸克进入触发验证/登录(约0.6KB),需已登录会话'),
    51: ('ok_empty', False, '贝壳研究院:夸克进入约1.1KB,仅门户landing'),
    52: ('dead', False, '克而瑞CRIC:夸克进入被DLP域名拦截(约35B),企业安全策略阻断'),
    53: ('ok_yield', True, '抖店大学:夸克进入成功,抓到约3.0KB学习中心内容'),
    54: ('ok_empty_internal', False, 'Rune·竞对AI:夸克进入被重定向到统一登录中心,本轮SSO登录态过期未取数;内网源仅入本地内部件'),
    55: ('ok_empty_internal', False, '魔镜·竞争管控·行业管控:夸克进入被重定向到统一登录中心,本轮SSO登录态过期未取数;内网源仅入本地内部件'),
    56: ('ok_empty', False, '千瓜官网:夸克进入约1.0KB首页,真实数据经工作台(id4)取得'),
    57: ('ok_empty_internal', False, 'FBI·报表(view 4847):夸克进入页面标题已加载但正文0B(需登录/画布渲染),本轮未取数;内网源仅入本地内部件'),
}


def main():
    bak = os.path.join(WORK, 'bak_url_inventory_before_r5quark.json')
    if not os.path.exists(bak):
        shutil.copyfile(INV, bak)

    inv = json.load(open(INV, encoding='utf-8'))
    updated = 0
    for u in inv['urls']:
        r = R.get(u['id'])
        if not r:
            continue
        verdict, yielded, concl = r
        tr = u.get('testResult') or {}
        tr['testedAt'] = '2026-08-26'
        tr['verdict'] = verdict
        tr['verdictLabel'] = LABELS.get(verdict, verdict)
        tr['yielded'] = yielded
        tr['conclusion'] = concl
        tr['round'] = 5
        tr['method'] = '本机夸克浏览器(AUMID:Quark)已登录会话,SendInput+扫描码逐个进入抓取(Ctrl+A剪贴板+滚动二次抓)'
        u['testResult'] = tr
        u['status'] = verdict
        updated += 1

    inv['auditSummary']['testedAt'] = '2026-08-26'
    inv['auditSummary']['statusCounts'] = dict(Counter(u['status'] for u in inv['urls']))
    inv['auditSummary']['yieldedCount'] = sum(
        1 for u in inv['urls'] if (u.get('testResult') or {}).get('yielded'))
    inv['auditSummary']['note'] = (
        '2026-08-26 第5轮：应要求把 url_inventory 全部 57 个数据源逐一用本机夸克浏览器'
        '(SendInput+扫描码,Ctrl+A剪贴板抓取+向下滚动二次抓)实测进入,不再用 WebSearch/WebFetch 代替。'
        '每源结论(含抓取字节量与拦截类型)见 urls[].testResult。'
        '有效抓到内容的公开源:千瓜工作台、抖店罗盘、京准通、抖店大学、中国质量报、网经社、京东企业博客、建材协会、'
        '199IT、奥维云网、国家统计局、巨潮资讯、36氪家居、京东麦头条、三个皮匠、发现报告、艾瑞咨询、慧博投研、'
        '阿里研究院、东方财富研报、亿欧、艾媒咨询、沙利文主站等;'
        '其中艾媒《2026-2027中国智能家居行业发展白皮书》(2026-08-25)为本轮新增可注入情报。'
        '登录/验证码墙未通过:蝉妈妈榜单、抖店放心购、小红书种草学、阿拉丁照明(滑动验证)、建筑装饰协会(安全验证)、巨量算数;'
        '失效或被DLP域名拦截:字节飞书wiki×2、百家号作者×2、微信文档、克而瑞CRIC;'
        '内网源(Rune/魔镜/FBI)夸克进入均被重定向统一登录中心,本轮SSO登录态过期未取数,按方案1仅沉淀本地内部件、不进公开仓。')

    json.dump(inv, open(INV, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    print('updated testResults:', updated)
    print('statusCounts:', json.dumps(inv['auditSummary']['statusCounts'], ensure_ascii=False))
    print('yieldedCount:', inv['auditSummary']['yieldedCount'])


if __name__ == '__main__':
    main()
