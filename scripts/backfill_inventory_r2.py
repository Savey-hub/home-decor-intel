"""Backfill data/v2/url_inventory.json with 2026-08-13 per-id test results.

Merges mechanical probe data (_work/probe57_2026-08-13.json) with the
human-verified verdicts (_work/testresult_r2.json), recomputes statusCounts,
and refreshes data/v2/data_sources_index.json audit fields if present.
"""
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, '_work')
INV = os.path.join(ROOT, 'data', 'v2', 'url_inventory.json')
TESTED_AT = '2026-08-13'

VERDICT_LABEL = {
    'ok_yield': '可读并产出情报',
    'ok_empty': '可读但窗口内无新增（真实空窗）',
    'partial': '部分可读（列表可读/正文受限）',
    'need_browser': '需真实浏览器（JS 渲染或反爬）',
    'need_login_browser': '需登录态浏览器',
    'member_wall': '会员/留资墙',
    'blocked_waf': '动态 WAF 硬阻断',
    'blocked_frozen': '公开内容冻结/已停更',
    'intranet': '内网源需登录态',
    'dlp': 'DLP 管控，放弃',
    'noise': '噪声源，剔除',
}


def main():
    inv = json.load(open(INV, encoding='utf-8'))
    probe = json.load(open(os.path.join(WORK, 'probe57_2026-08-13.json'), encoding='utf-8'))
    tr = json.load(open(os.path.join(WORK, 'testresult_r2.json'), encoding='utf-8'))['results']

    bak = os.path.join(WORK, 'bak_url_inventory_before_r2.json')
    if not os.path.exists(bak):
        shutil.copyfile(INV, bak)

    missing = []
    counts = {}
    yielded = 0
    for u in inv['urls']:
        sid = str(u['id'])
        p = probe.get(sid)
        v = tr.get(sid)
        if not v:
            missing.append(sid)
            continue
        res = {
            'testedAt': TESTED_AT,
            'verdict': v['verdict'],
            'verdictLabel': VERDICT_LABEL[v['verdict']],
            'yielded': v['yielded'],
            'conclusion': v['conclusion'],
        }
        if p:
            res['probe'] = {
                'httpCode': p.get('code'),
                'bytes': p.get('bytes'),
                'readableChars': p.get('text_len'),
                'finalUrl': p.get('final'),
                'loginHits': p.get('login_hit', []),
                'wafHits': p.get('waf_hit', []),
                'err': p.get('err', ''),
            }
        u['testResult'] = res
        counts[v['verdict']] = counts.get(v['verdict'], 0) + 1
        if v['yielded']:
            yielded += 1

    if missing:
        raise SystemExit('missing verdicts for ids: %s' % missing)

    inv['auditSummary']['testedAt'] = TESTED_AT
    inv['auditSummary']['statusCounts'] = dict(sorted(counts.items(), key=lambda kv: -kv[1]))
    inv['auditSummary']['yieldedCount'] = yielded
    inv['auditSummary']['note'] = (
        '2026-08-13 全量 57 源逐一重测。实测方式：先用 curl（Chrome UA + 完整请求头，记录 http_code/'
        'size_download/可读字符数/登录与 WAF 关键词命中）建立机械可达性基线（_work/probe57_2026-08-13.json），'
        '再对可读源逐个进入正文深挖，对 JS 渲染/登录/内网源改由本机夸克浏览器执行。每源结论见 '
        'urls[].testResult。本轮成功攻破：中装协滑块（verify.php）、199IT WordPress REST、新浪财经搜索接口、'
        '东方财富 reportapi、发现报告 Next.js _next/data、QuestMobile article-list 逆向、CBNData '
        '__INITIAL_STATE__、慧博 GBK 路由与标题日期后缀、沙利文 --http1.1、亿欧 TLS（curl -k）。'
        '硬阻断：信通院（瑞数动态 JS WAF）、贝壳研究院（公开内容冻结于 2023-10-20）、慧博正文（PC 客户端墙）、'
        '沙利文与 CBNData 深度章节（留资/付费墙）。'
    )

    json.dump(inv, open(INV, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    print('url_inventory.json backfilled: %d urls' % len(inv['urls']))
    for k, n in inv['auditSummary']['statusCounts'].items():
        print('  %-20s %2d  %s' % (k, n, VERDICT_LABEL[k]))
    print('  yielded intel from %d sources' % yielded)

    # refresh data_sources_index.json audit stamp if it carries one
    idx_path = os.path.join(ROOT, 'data', 'v2', 'data_sources_index.json')
    if os.path.exists(idx_path):
        idx = json.load(open(idx_path, encoding='utf-8'))
        touched = []
        for key in ('asOf', 'lastAudit', 'testedAt', 'updatedAt'):
            if key in idx:
                idx[key] = TESTED_AT
                touched.append(key)
        if touched:
            json.dump(idx, open(idx_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print('data_sources_index.json fields refreshed: %s' % (touched or 'none'))


if __name__ == '__main__':
    main()
